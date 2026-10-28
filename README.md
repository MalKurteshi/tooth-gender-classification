# Tooth Gender Classification

A Python/Tkinter desktop application for predicting Female/Male labels from 31 dental measurements and indices. Windows and macOS installers bundle Python, libraries, a saved prediction pipeline, and the seed dataset. Users do not install Python or run setup scripts.

## End-user installation

Get the installer for your computer from the person or team providing the application. Downloading the repository as a ZIP does not install the desktop application. Python, Conda, and developer tools are not required when using the installer.

### Windows

1. Download `ToothGenderClassification-Setup-2.2.0.exe` (or the installer for the latest version provided to you). If it arrives inside a ZIP file, extract it first.
2. Open your Downloads folder and double-click the installer.
3. Follow the installation wizard and click **Install**. The application installs for your Windows account; administrator access is not normally required.
4. Leave **Open Tooth Gender Classification** selected if you want to start immediately, then click **Finish**.
5. For future use, double-click **Tooth Gender Classification** on your desktop, or search for it in the Start menu. You do not need to run the installer again.

To uninstall, search for **Tooth Gender Classification** in Windows Settings → Apps and choose **Uninstall**. Your saved training data, models, and backups are retained separately in the user-data folder listed below.

### macOS

1. Check your Mac's processor in the Apple menu → **About This Mac**. Choose the **Apple Silicon** download for a Mac with an Apple M-series chip, or the **Intel** download for a Mac showing an Intel processor.
2. Download the matching installer. Its filename is `ToothGenderClassification-2.2.0.pkg` (or the version provided to you). The Intel and Apple Silicon packages may share the same filename, so select the correct download before opening it. If it arrives inside a ZIP file, extract it first.
3. Double-click the `.pkg` file in Downloads to open the installation wizard.
4. Follow the wizard, click **Install**, and enter your Mac administrator credentials if requested. Click **Close** when installation finishes.
5. Open Finder → **Applications** and double-click **ToothGenderClassification**. The installer also creates a **Tooth Gender Classification** desktop shortcut for the user signed in during installation, when their Desktop folder is available.
6. For future use, open the desktop shortcut or the application in Applications. You do not need to run the installer again.

To uninstall, quit the application, move **ToothGenderClassification** from Applications to the Trash, and remove its desktop shortcut. Your saved training data, models, and backups are retained separately in the user-data folder listed below.

### Updates and installation help

- To update, close the application and run the newer installer for your operating system and processor. Your saved data and retrained models are preserved; back up the user-data folder before updating. See the v1 migration note below for older 21-feature models.
- If an installer is blocked, fails to open, or reports an error, send the exact message to the team that supplied it so they can provide the appropriate installer.
- After installation, see the [user guide](USER_GUIDE.md) for predictions, Excel import, and model retraining.

**Release status:** installers still require native OS acceptance testing and publisher signing before general distribution. Current workflow artifacts are unsigned development builds; the workflow does not publish releases automatically.

## Building the installers

These steps are for the person preparing releases. End users should follow the installation instructions above.

Install Python 3.13 with Tcl/Tk support, then run the following commands from the repository folder:

```sh
python -m venv .venv
# Windows:
.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.venv\Scripts\python.exe build_executable.py --gui
# macOS:
.venv/bin/python -m pip install -r requirements-build.txt
.venv/bin/python build_executable.py --gui
```

Build on the target operating system. Windows requires Inno Setup 6; macOS requires Xcode command line tools. Installers are written to `dist/`. The build uses the included saved model. Use `--retrain-model` only when deliberately replacing that bundled model. Users can train their own model through the application's Training Data tab.

Run `python launch.py` to open the application from source with the required libraries installed. The GitHub build workflow also produces Windows, Apple Silicon, and Intel installers. See [release instructions](docs/DESKTOP_RELEASE.md) for signing and distribution.

## Prediction and data

Prediction loads one saved pipeline at startup. It does not train on each click or require a writable installation. The pipeline contains median imputation, SMOTE, robust scaling, and logistic regression using all 31 features. Model information and HTML reports use metadata embedded in that same artifact.

The bundled model is trained on `data/raw/Per_ANN_v1.xlsx`: 100 samples (50 Female, 50 Male). `Nr.` is an identifier and is excluded from training; `Gjinia` is the target (0 = Female, 1 = Male). Five-fold internal cross-validation accuracy is 75.0% (standard deviation 7.1 percentage points); this is not independent test accuracy.

Use Training Data → Save Excel Template to create a workbook, then Import Excel and Retrain to train from your own `.xlsx`. The first sheet must include all 31 parameter columns and `Gjinia` (or `Gender`), using 0/F/Female or 1/M/Male labels and at least four samples of each class. Both standard headers and the legacy second-row headers are supported. A successful import replaces the active training dataset; the new model is used immediately and after reopening. Failed imports preserve the previous model and dataset.

Enter at least 16 finite positive parameter values; omitted measurements use the training medians. To add training data, complete all 31 fields in the Prediction tab and use Add Data to provide the actual Female/Male label. Retrain explicitly to update the saved user model. The original dataset and shipped model are preserved. This version replaces the previous inconsistent runtime/metadata combination; predictions and validation scores can differ from older versions. Historical validation scores do not apply to this model. Model scores are internal cross-validation estimates, not independent clinical validation.

User files (dataset, retrained model, backups, logs) are stored in:

- Windows: `%LOCALAPPDATA%\ToothGenderClassification\dataset-v1`
- macOS: `~/Library/Application Support/ToothGenderClassification/dataset-v1`
- Linux: `$XDG_DATA_HOME/ToothGenderClassification/dataset-v1` or `~/.local/share/ToothGenderClassification/dataset-v1`

`TOOTH_APP_DATA_DIR` overrides the parent storage folder; v1 files go inside its `dataset-v1` subfolder. Updates preserve user files. Back up this folder before moving computers. Only load model artifacts produced by this application or trusted builds (joblib deserialization executes Python code).

Earlier 21-feature models and user datasets are kept in their original parent folder but are not loaded by this version. The first v1 launch uses the new bundled model. To reuse older samples, add the missing parameters using the new Excel template and import that workbook; old templates are not sufficient for v1 retraining. Subsequent updates within v1 preserve the active v1 user model.

The desktop report exports the active model’s information as HTML, printable from a browser.

## v1 parameters

Use the exact column names from the generated Excel template. Header whitespace is trimmed. The two index values must stay on the same numeric scale as the source workbook; the app does not convert indices into millimeters or calculate them from other fields.

| Group | Parameters |
| --- | --- |
| Upper teeth | `UM2 MD (mm)`, `UM1 MD (mm)`, `UP2 MD (mm)`, `UP1 MD (mm)`, `13 BO (mm)`, `13 MD (mm)`, `12MD (mm)`, `11 MD (mm)`, `21 MD (mm)`, `22 MD (mm)`, `23 MD (mm)`, `23 BO (mm)` |
| Lower teeth | `LM2 MD (mm)`, `LM1 MD (mm)`, `LP2 MD (mm)`, `LP1 MD (mm)`, `43 BO (mm)`, `43 MD (mm)`, `42MD (mm)`, `41 MD (mm)`, `31 MD (mm)`, `32 MD (mm)`, `33 MD (mm)`, `33 BO (mm)` |
| Arch and indices | `Harku interkanin mandibullar`, `Indeksi i kaninëve`, `Indeksi i incizivëve Maksillar` |
| Mandibular dimensions | `Gjatesia e ramusit`, `Gonion:Gnathion`, `Gjeresia minimale e ramusit`, `Gjeresia bigoniale` |

## Repository

`src/gui_app.py` is the desktop interface; `src/predict.py` is the shared backend; `src/app_paths.py` handles resources and user storage; `build_executable.py` and `packaging/` define native distribution; `.github/workflows/desktop.yml` builds Windows, Apple Silicon, and Intel artifacts on pull requests, on demand, or for version tags.

MIT License. Author: Mal Kurteshi.
