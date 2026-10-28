# Preparing a desktop release

Install Python 3.13 with Tcl/Tk support and the libraries in `requirements-build.txt`. Build on the operating system you are targeting with `python build_executable.py --gui`. Windows requires Inno Setup 6; macOS requires Xcode command line tools. The output installer is in `dist/`.

The build bundles the application, Python runtime, required libraries, saved model, and seed dataset. Version 2.2.0 bundles `data/raw/Per_ANN_v1.xlsx` and its 31-feature model. The schema, source-workbook SHA-256, and scikit-learn version are checked before packaging, preventing a stale model from being shipped with changed data. Normal builds use the included model without changing it. Use `--retrain-model` only when deliberately regenerating the bundled model. Client-specific Excel import and retraining are available inside the application.

The GitHub workflow builds Windows, Apple Silicon macOS, and Intel macOS installers on pull requests, version tags, or manual runs. Download the corresponding workflow artifact to obtain an installer. The workflow does not publish releases automatically.

## Signing and distribution

For Windows releases, sign the executable and Setup.exe with the publisher's Authenticode certificate using Windows SDK SignTool.

For macOS releases, sign the application and its native dependencies with a Developer ID Application identity and the appropriate hardened-runtime settings. Sign the installer with a Developer ID Installer identity, submit it to Apple's notarization service, and staple the notarization ticket. These steps require the publisher's Apple Developer certificates and credentials.

Verify installation and desktop shortcuts on clean target computers without Python installed before distributing. Confirm prediction, Excel import, retraining, reopening with the saved model, report export, upgrades, and uninstall. Record the operating system versions and processor architectures supported by the release.

Only distribute the installer to clients; the repository, virtual environment, intermediate build files, and source code are not needed to use the application.

## v1 model and storage

The seed workbook has 100 samples, with 50 labels of each class. The identifier `Nr.` is excluded. The pipeline fits all 31 input features using median imputation, robust scaling, and logistic regression, with SMOTE inside the training pipeline. All preprocessing is fitted independently within each cross-validation fold. Five-fold stratified validation reports accuracy 75.0% ± 7.1 percentage points. No independent test-set performance is claimed. Model metadata stores input order, schema version, training class counts, workbook SHA-256, and training time.

The shared `src/schema.py` defines the 31 workbook headers, minimum 16 provided prediction values, seed filename, schema identifier, and application version. Do not change feature order without retraining the model. Index values retain the workbook scale. Import accepts standard or second-row headers and trims whitespace.

Client data is isolated under `dataset-v1` within the existing application-data folder. Earlier models and Excel data are retained in the parent folder and never silently loaded against v1 inputs. Successful Excel imports activate a complete dataset/model pair atomically; failure leaves the prior v1 model active. Existing v1 user models take precedence over the bundled model after reopening.

## Verification for 2.2.0

The local checks verified the workbook's 31 headers and 100 samples, the model's input count and source hash, prediction validation, Excel template export, changed predictions after retraining, saved-model reload, rollback on activation failure, later data entry/retraining, and preservation of legacy client files. The GUI was exercised with all 31 fields and its background Excel import flow. The rebuilt macOS app opened successfully; its packaged workbook and model match the source. No test-case files or diagnostic application modes are included in the repository. Windows and Intel macOS builds and publisher signing still require the release environment.

## Application icon

`assets/tooth_icon.svg` is the editable tooth artwork. Pre-generated PNG, ICO, and ICNS files are included so installer builds need no image-conversion libraries. The Windows executable and installer embed the ICO, and Desktop/Start menu shortcuts use the executable's icon. The macOS bundle embeds the ICNS for Finder, Dock, and its desktop shortcut. Tkinter uses the platform-appropriate runtime icon. Rebuild and reinstall to update an existing installation.
