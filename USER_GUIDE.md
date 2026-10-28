# Desktop user guide

Install the Windows Setup.exe or the macOS .pkg matching your processor. Windows creates Desktop and Start menu shortcuts; macOS installs the application in Applications and creates a desktop shortcut for the signed-in user. Open that icon on subsequent visits. You do not need Python, a terminal, or an internet connection to make predictions.

## Make a prediction

Enter the 31 parameters shown in the Prediction tab, matching `Per_ANN_v1.xlsx`. Tooth columns marked `(mm)` use millimeters; enter the two indices on their original workbook scale without conversion. Commas and dots are accepted as decimal separators. At least 16 parameter values are required; missing measurements use medians learned from training data. Values must be finite positive numbers. Click Predict Gender to see the predicted label and model probabilities.

CSV import reads the first row, using the 31 parameter names listed in the Prediction tab as column headers. Import clears previous inputs so old values cannot silently remain.

## Import an Excel workbook and train a model

Open Training Data → Save Excel Template. Fill the template with your samples, including the `Gjinia` label (0/F/Female or 1/M/Male). Include at least four samples for each class. Keep all 31 parameter column headers. Empty measurement cells are allowed, but every measurement column must contain some data. Supplied measurements must be positive numbers. Missing or invalid labels are rejected.

Choose Import Excel and Retrain, select your `.xlsx` file, and confirm. The first worksheet is used. A `Gender` label header is also accepted. The original workbook is never modified. Import replaces the active dataset rather than appending to it.

Wait for the success message. The new model is immediately used for predictions and is loaded again after you close and reopen the application. The previous prediction is cleared to avoid confusing it with a result from the new model. The previous dataset and model are retained in your application-data folder. If validation or training fails, your previous model remains active.

## Add data and retrain

Complete all 31 parameters in the Prediction tab. Go to Training Data, click Add New Training Data, then Enter Data. Provide F or M for the known label. A backup is made before the user dataset is changed.

Click Retrain Model to train and validate against your saved dataset. Wait until the completion dialog appears. A successful retrain saves a complete pipeline for future sessions. Failed training leaves the previously saved model available. The shipped dataset and model remain unchanged.

## Upgrading from the 21-feature application

Version 2.2.0 starts with the new model trained on 100 samples and all 31 v1 features. Older user-trained models cannot accept the expanded inputs, so they are preserved in their old storage folder and are not loaded. New v1 data and models live in the `dataset-v1` subfolder. To reuse old samples, save the new template, supply all new parameter columns, and import it. A v1 model you subsequently train remains active after reopening and future v1 updates.

## Model reports

Settings → View Model Info shows the active model's metadata. Generate Report exports an HTML report to a location you choose. Open it in a browser to read or print it. Report generation does not train another model.

## Troubleshooting

If startup or another action fails, the error identifies the application log. User files live at:

- Windows: `%LOCALAPPDATA%\ToothGenderClassification\dataset-v1`
- macOS: `~/Library/Application Support/ToothGenderClassification/dataset-v1`

Include `application.log` when reporting a problem. Updates preserve this folder; back it up before changing computers. On Windows uninstall through Installed Apps. On macOS remove the application from Applications and its desktop shortcut. User data is retained until you explicitly remove its application-data folder.

Use only installers supplied by your publisher. Unsigned development builds can trigger operating-system security checks. The application is a research tool; its model probabilities do not establish clinical reliability.
