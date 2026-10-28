"""Shared desktop/CLI backend. Training is explicit; prediction only loads artifacts."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import uuid

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.preprocessing import RobustScaler
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline

try:
    from .app_paths import dataset_path, user_dir, model_path
except ImportError:
    from app_paths import dataset_path, user_dir, model_path

try:
    from .schema import FEATURES, MIN_MEASUREMENTS, SCHEMA_VERSION, SEED_FILENAME
except ImportError:
    from schema import FEATURES, MIN_MEASUREMENTS, SCHEMA_VERSION, SEED_FILENAME


def validate_measurements(measurements, complete=False):
    result = {}
    for feature in FEATURES:
        raw = measurements.get(feature, "")
        if raw is None or str(raw).strip() == "":
            if complete:
                raise ValueError(f"Missing measurement: {feature}")
            continue
        value = float(str(raw).replace(",", "."))
        if not np.isfinite(value) or value <= 0:
            raise ValueError(f"{feature} must be a finite positive number.")
        result[feature] = value
    if not complete and len(result) < MIN_MEASUREMENTS:
        raise ValueError(
            f"Please provide at least {MIN_MEASUREMENTS} of the {len(FEATURES)} parameters."
        )
    return result


def read_dataset(path):
    frame = pd.read_excel(path, engine="openpyxl").dropna(how="all")
    if frame.empty:
        raise ValueError("The Excel file contains no training samples.")
    frame.columns = [str(col).strip() for col in frame.columns]
    if not {"Gjinia", "Gender"}.intersection(frame.columns):
        frame.columns = [str(col).strip() for col in frame.iloc[0]]
        frame = frame.iloc[1:].reset_index(drop=True)
    if "Gjinia" not in frame.columns and "Gender" in frame.columns:
        frame = frame.rename(columns={"Gender": "Gjinia"})
    if frame.columns.duplicated().any():
        raise ValueError("The Excel file contains duplicate column names.")
    missing = set(FEATURES + ["Gjinia"]) - set(frame.columns)
    if missing:
        raise ValueError(f"Dataset columns missing: {sorted(missing)}")
    frame = frame[FEATURES + ["Gjinia"]].dropna(how="all").copy()
    if frame.empty:
        raise ValueError("The Excel file contains no training samples.")
    labels = frame["Gjinia"].astype(str).str.strip().str.lower()
    labels = labels.replace({"female": "0", "f": "0", "male": "1", "m": "1"})
    frame["Gjinia"] = pd.to_numeric(labels, errors="coerce")
    if not frame["Gjinia"].isin([0, 1]).all():
        raise ValueError("Every training sample needs a gender: 0/F/Female or 1/M/Male.")
    for column in FEATURES:
        raw = frame[column].astype("string").str.strip().str.replace(",", ".", regex=False)
        values = pd.to_numeric(raw.replace("", pd.NA), errors="coerce")
        supplied = raw.notna() & raw.ne("")
        invalid = supplied & (values.isna() | ~np.isfinite(values) | (values <= 0))
        if invalid.any():
            raise ValueError(
                f"Invalid measurement in {column}. Use positive numbers or leave the cell empty."
            )
        frame[column] = values.astype(float)
    if (frame[FEATURES].count() == 0).any():
        raise ValueError("Every measurement column needs at least one value.")
    return frame.reset_index(drop=True)


def atomic_dump(value, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        joblib.dump(value, temporary)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def train_artifact(data_path, output):
    frame = read_dataset(data_path)
    X, y = frame[FEATURES], frame["Gjinia"].astype(int)
    counts = y.value_counts()
    if len(counts) != 2 or counts.min() < 4:
        raise ValueError("Training requires at least four samples of each class.")
    folds = min(5, int(counts.min()))
    # A single neighbor remains valid in the smallest supported CV training fold.
    pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
            ("smote", SMOTE(random_state=42, k_neighbors=1)),
            ("scaler", RobustScaler()),
            (
                "model",
                LogisticRegression(
                    random_state=42, max_iter=1000, class_weight="balanced", solver="liblinear"
                ),
            ),
        ]
    )
    scores = cross_validate(
        pipeline,
        X,
        y,
        cv=StratifiedKFold(folds, shuffle=True, random_state=42),
        scoring={"accuracy": "accuracy", "balanced_accuracy": "balanced_accuracy"},
        error_score="raise",
    )
    pipeline.fit(X, y)
    metadata = dict(
        model_name="Logistic Regression",
        cv_accuracy=float(scores["test_accuracy"].mean()),
        cv_std=float(scores["test_accuracy"].std()),
        cv_balanced_accuracy=float(scores["test_balanced_accuracy"].mean()),
        cv_folds=folds,
        schema_version=SCHEMA_VERSION,
        training_file=Path(data_path).name,
        training_sha256=hashlib.sha256(Path(data_path).read_bytes()).hexdigest(),
        class_counts={"Female": int(counts.loc[0]), "Male": int(counts.loc[1])},
        feature_names=FEATURES,
        selected_features=FEATURES,
        target_classes=["Female", "Male"],
        samples=len(frame),
        sklearn_version=sklearn.__version__,
        trained_at=datetime.now(timezone.utc).isoformat(),
        test_accuracy=None,
        preprocessing_steps=[
            "Median imputation",
            "SMOTE (1 neighbor)",
            "RobustScaler",
        ],
    )
    artifact = dict(format_version=1, pipeline=pipeline, metadata=metadata)
    atomic_dump(artifact, output)
    return artifact


class WorkingToothGenderPredictor:
    def __init__(self):
        self.reload()

    def reload(self):
        path = model_path()
        artifact = joblib.load(path)
        if artifact.get("format_version") != 1:
            raise ValueError("Unsupported model format.")
        metadata = artifact["metadata"]
        if (
            metadata.get("schema_version") != SCHEMA_VERSION
            or metadata.get("feature_names") != FEATURES
        ):
            raise ValueError(
                "The saved model uses a different input schema. Import a v1 workbook and retrain."
            )
        if artifact["pipeline"].n_features_in_ != len(FEATURES):
            raise ValueError("The model input count does not match the v1 parameters.")
        if metadata["sklearn_version"] != sklearn.__version__:
            raise ValueError(
                "Model and scikit-learn versions differ. Rebuild the application/model together."
            )
        self.metadata = metadata
        self.model_pipeline = artifact["pipeline"]
        self.original_features = FEATURES

    def predict_gender(self, measurements):
        values = validate_measurements(measurements)
        X = pd.DataFrame([[values.get(f, np.nan) for f in FEATURES]], columns=FEATURES)
        probabilities = self.model_pipeline.predict_proba(X)[0]
        classes = self.model_pipeline.classes_
        labels = {0: "Female", 1: "Male"}
        best = int(np.argmax(probabilities))
        return dict(
            prediction=labels[int(classes[best])],
            confidence=float(probabilities[best] * 100),
            probabilities={labels[int(c)]: float(p * 100) for c, p in zip(classes, probabilities)},
        )

    def add_training_sample(self, measurements, gender):
        values = validate_measurements(measurements, complete=True)
        if gender not in (0, 1):
            raise ValueError("Choose Female or Male.")
        path = dataset_path()
        frame = read_dataset(path)
        backup = user_dir() / "backups"
        backup.mkdir(exist_ok=True)
        shutil.copy2(path, backup / f"dataset-{uuid.uuid4().hex}.xlsx")
        frame = pd.concat([frame, pd.DataFrame([{**values, "Gjinia": gender}])], ignore_index=True)
        temporary = path.with_name(f"dataset-{uuid.uuid4().hex}.xlsx")
        try:
            frame.to_excel(temporary, index=False)
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)
        return len(frame)

    def retrain(self):
        current = model_path()
        path = current if current.is_relative_to(user_dir()) else user_dir() / "pipeline.joblib"
        if path.exists():
            backup = user_dir() / "backups"
            backup.mkdir(exist_ok=True)
            shutil.copy2(path, backup / f"pipeline-{uuid.uuid4().hex}.joblib")
        artifact = train_artifact(dataset_path(), path)
        self.reload()
        return artifact["metadata"]

    def import_and_retrain(self, excel_path):
        """Stage a complete dataset/model pair, then activate both with one atomic pointer."""
        source = Path(excel_path)
        if source.suffix.lower() != ".xlsx":
            raise ValueError("Choose an Excel .xlsx file.")
        frame = read_dataset(source)
        generation = uuid.uuid4().hex
        folder = user_dir() / "generations" / generation
        folder.mkdir(parents=True)
        pointer = user_dir() / "active-model.json"
        temporary = pointer.with_name(f"active-{generation}.tmp")
        activated = False
        try:
            shutil.copy2(model_path(), folder / "previous-pipeline.joblib")
            shutil.copy2(dataset_path(), folder / ("previous-" + SEED_FILENAME))
            frame.to_excel(folder / SEED_FILENAME, index=False)
            artifact = train_artifact(folder / SEED_FILENAME, folder / "pipeline.joblib")
            temporary.write_text(json.dumps({"generation": generation}), encoding="utf-8")
            os.replace(temporary, pointer)
            activated = True
            self.metadata = artifact["metadata"]
            self.model_pipeline = artifact["pipeline"]
            self.original_features = FEATURES
            return self.metadata
        finally:
            temporary.unlink(missing_ok=True)
            if not activated:
                shutil.rmtree(folder)

    @staticmethod
    def export_training_template(path):
        pd.DataFrame(columns=FEATURES + ["Gjinia"]).to_excel(path, index=False)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Predict the first row of a measurement CSV.")
    parser.add_argument("csv", type=Path)
    args = parser.parse_args()
    try:
        frame = pd.read_csv(args.csv)
        if frame.empty:
            raise ValueError("CSV contains no data.")
        print(
            json.dumps(
                WorkingToothGenderPredictor().predict_gender(frame.iloc[0].dropna().to_dict()),
                indent=2,
            )
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
