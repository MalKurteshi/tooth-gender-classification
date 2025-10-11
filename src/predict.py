#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Working Tooth Gender Prediction Interface
Uses the exact same preprocessing as the training pipeline
"""

import os
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import RobustScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbalancedPipeline
from datetime import datetime
import shutil
import warnings
warnings.filterwarnings('ignore')
import warnings
warnings.filterwarnings('ignore')

class WorkingToothGenderPredictor:
    def __init__(self):
        """Initialize predictor with model training pipeline"""
        self.model_pipeline = None
        self.original_features = None
        self.load_data_and_model()
    
    def load_data_and_model(self):
        """Load data and recreate the exact training pipeline"""
        try:
            print("🔄 Loading training data and recreating model pipeline...")
            
            # Load and process data exactly like training
            data_path = os.path.join('data/raw', 'Per_ANN.xlsx')
            df = pd.read_excel(data_path)
            
            # Data preprocessing (exact same as training)
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)
            df = df.drop(columns=['Nr.'], errors='ignore')
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            df = df.replace(',', '.', regex=True)
            
            # Process target variable
            df['Gjinia'] = df['Gjinia'].astype(str).str.strip()
            df['Gjinia'] = df['Gjinia'].replace(['', 'nan', 'NaN', None], pd.NA)
            df = df.dropna(subset=["Gjinia"])
            df['Gjinia'] = pd.to_numeric(df['Gjinia'], errors='coerce')
            df['Gjinia'] = df['Gjinia'].fillna(0).astype(int).astype(bool)
            
            # Convert features to numeric
            for col in df.columns:
                if col != 'Gjinia':
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Separate features and target
            X = df.drop(columns=['Gjinia'])
            y = df['Gjinia']
            
            # Remove highly correlated features (same as training)
            correlation_matrix = X.corr().abs()
            upper_triangle = correlation_matrix.where(
                np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool)
            )
            high_corr_features = [
                column for column in upper_triangle.columns 
                if any(upper_triangle[column] > 0.95)
            ]
            if high_corr_features:
                X = X.drop(columns=high_corr_features)
            
            # Store original features for user input
            self.original_features = X.columns.tolist()
            
            # Create the exact pipeline from main_final.py
            def create_robust_pipeline(model, k_features=12):
                steps = [
                    ('smote', SMOTE(random_state=42)),
                    ('scaler', RobustScaler()),
                    ('selector', SelectKBest(f_classif, k=min(k_features, X.shape[1]))),
                    ('model', model)
                ]
                return ImbalancedPipeline(steps)
            
            # Create and train the model (using best model from main_final: Logistic Regression)
            self.model_pipeline = create_robust_pipeline(
                LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced'),
                k_features=12
            )
            
            # Train the pipeline
            print("🏋️ Training model pipeline...")
            self.model_pipeline.fit(X, y)
            
            print("✅ Model pipeline ready!")
            print(f"📊 Features available: {len(self.original_features)}")
            
        except Exception as e:
            print(f"❌ Error setting up model: {e}")
            raise
    
    def predict_gender(self, measurements):
        """Make prediction using the working pipeline"""
        try:
            # Create feature vector from measurements
            feature_values = []
            for feature in self.original_features:
                value = measurements.get(feature, 7.5)  # Default value
                feature_values.append(float(value))
            
            # Create DataFrame
            X_input = pd.DataFrame([feature_values], columns=self.original_features)
            
            # Make prediction using the pipeline
            prediction = self.model_pipeline.predict(X_input)[0]
            probabilities = self.model_pipeline.predict_proba(X_input)[0]
            
            # Format results
            gender = "Male" if prediction else "Female"
            confidence = max(probabilities) * 100
            
            return {
                'prediction': gender,
                'confidence': confidence,
                'probabilities': {
                    'Female': probabilities[0] * 100,
                    'Male': probabilities[1] * 100
                }
            }
            
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return None
    
    def interactive_prediction(self):
        """Interactive prediction interface"""
        print("\\n🦷 TOOTH GENDER PREDICTION")
        print("="*40)
        print("Enter dental measurements (mm)")
        print("Press Enter for default (7.5mm)\\n")
        
        while True:
            try:
                measurements = {}
                
                print("📏 Enter measurements:")
                print("-" * 25)
                
                for i, feature in enumerate(self.original_features, 1):
                    while True:
                        try:
                            value_str = input(f"{i:2d}. {feature}: ")
                            
                            if value_str.strip() == "":
                                measurements[feature] = 7.5
                                print(f"    → Default: 7.5mm")
                                break
                            else:
                                value = float(value_str.replace(',', '.'))
                                if 0.1 <= value <= 50.0:
                                    measurements[feature] = value
                                    break
                                else:
                                    print("    ⚠️  Value should be 0.1-50.0mm")
                        except ValueError:
                            print("    ⚠️  Enter valid number or press Enter")
                
                # Make prediction
                print("\\n🔄 Predicting...")
                result = self.predict_gender(measurements)
                
                if result:
                    print("\\n" + "="*40)
                    print("🎯 RESULT")
                    print("="*40)
                    print(f"👤 Gender: {result['prediction']}")
                    print(f"🎲 Confidence: {result['confidence']:.1f}%")
                    print("\\n📊 Probabilities:")
                    print(f"   Female: {result['probabilities']['Female']:.1f}%")
                    print(f"   Male:   {result['probabilities']['Male']:.1f}%")
                    
                    # Confidence level
                    conf = result['confidence']
                    if conf >= 85:
                        print("\\n🟢 High Confidence")
                    elif conf >= 70:
                        print("\\n🔵 Good Confidence")
                    elif conf >= 60:
                        print("\\n🟡 Moderate Confidence")
                    else:
                        print("\\n🔴 Low Confidence")
                else:
                    print("❌ Prediction failed")
                
                # Continue?
                print("\\n" + "-"*40)
                again = input("\\n🔄 Another prediction? (y/n): ").lower().strip()
                if again not in ['y', 'yes']:
                    break
                    
            except KeyboardInterrupt:
                print("\\n\\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\\n❌ Error: {e}")
                
    def quick_test(self):
        """Quick test with example data"""
        print("\\n🧪 QUICK TEST")
        print("="*20)
        
        # Test with average values
        test_data = {feature: 7.5 for feature in self.original_features}
        test_data.update({
            'U M1 MD (mm)': 10.5,  # Larger values more likely male
            'L M1 MD (mm)': 11.0,
            '43 MD (mm)': 7.2,
            '33 MD (mm)': 6.8,
            'Harku interkanin mandibullar': 27.0
        })
        
        print("Using test measurements...")
        result = self.predict_gender(test_data)
        
        if result:
            print(f"➡️  Result: {result['prediction']} ({result['confidence']:.1f}% confidence)")
        else:
            print("❌ Test failed")
    
    def add_data_to_excel(self):
        """Add new data entry to the Per ANN.xlsx file"""
        print("\\n📝 ADD NEW DATA TO DATASET")
        print("="*35)
        print("Enter new dental measurement data to add to the training dataset")
        print("This will be saved to Per ANN.xlsx for future model training\\n")
        
        try:
            # Collect measurements
            measurements = {}
            print("📏 Enter measurements for new sample:")
            print("-" * 40)
            
            # Get all dental measurements
            for i, feature in enumerate(self.original_features, 1):
                while True:
                    try:
                        value_str = input(f"{i:2d}. {feature}: ")
                        if value_str.strip() == "":
                            print("    ⚠️  This field is required for dataset entry")
                            continue
                        else:
                            value = float(value_str.replace(',', '.'))
                            if 0.1 <= value <= 50.0:
                                measurements[feature] = value
                                break
                            else:
                                print("    ⚠️  Value should be 0.1-50.0mm")
                    except ValueError:
                        print("    ⚠️  Enter a valid number")
            
            # Get the ground truth gender
            while True:
                gender_input = input("\\n👤 Actual Gender (M/F): ").strip().upper()
                if gender_input in ['M', 'MALE', '1']:
                    measurements['Gjinia'] = 1  # Male = True = 1
                    gender_label = "Male"
                    break
                elif gender_input in ['F', 'FEMALE', '0']:
                    measurements['Gjinia'] = 0  # Female = False = 0
                    gender_label = "Female"
                    break
                else:
                    print("    ⚠️  Enter M for Male or F for Female")
            
            # Load existing Excel file
            data_path = os.path.join('data/raw', 'Per_ANN.xlsx')
            
            try:
                # Read the existing data
                df_existing = pd.read_excel(data_path)
                
                # Get the structure (first row should be headers after processing)
                headers = df_existing.iloc[0].tolist()
                
                # Create new row data matching the Excel structure
                new_row = []
                
                # Add a sequential number (Nr.)
                new_row.append(len(df_existing))  # This will be the new row number
                
                # Add measurements in the same order as headers
                for header in headers[1:]:  # Skip first column (Nr.)
                    if header in measurements:
                        new_row.append(measurements[header])
                    else:
                        # If header not found, use default or empty
                        new_row.append('')
                
                # Add the new row to DataFrame
                new_df = pd.DataFrame([new_row], columns=headers)
                updated_df = pd.concat([df_existing, new_df], ignore_index=True)
                
                # Create backup before modifying
                backup_path = f"data/Per ANN_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                df_existing.to_excel(backup_path, index=False)
                print(f"\\n💾 Backup created: {backup_path}")
                
                # Save updated data
                updated_df.to_excel(data_path, index=False)
                
                print(f"\\n✅ Successfully added new {gender_label} sample to dataset!")
                print(f"📊 Dataset now contains {len(updated_df)} samples")
                print("\\n🔄 Recommendation: Retrain the model to include this new data")
                
            except Exception as e:
                print(f"\\n❌ Error updating Excel file: {e}")
                print("Please check file permissions and try again.")
                
        except KeyboardInterrupt:
            print("\\n\\n⏹️  Data entry cancelled by user")
        except Exception as e:
            print(f"\\n❌ Error during data entry: {e}")
    
    def retrain_model(self):
        """Retrain the model with updated dataset"""
        print("\\n🔄 RETRAIN MODEL")
        print("="*25)
        print("This will retrain the model using the current dataset")
        print("Including any newly added data entries\\n")
        
        # Ask for confirmation
        confirm = input("⚠️  This will replace the current model. Continue? (y/n): ").lower().strip()
        if confirm not in ['y', 'yes']:
            print("❌ Model retraining cancelled")
            return
        
        try:
            print("\\n🏗️  Starting model retraining process...")
            
            # Load and process data (same as initialization)
            data_path = os.path.join('data/raw', 'Per_ANN.xlsx')
            df = pd.read_excel(data_path)
            
            print("📊 Loading dataset...")
            
            # Data preprocessing (exact same as training)
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)
            df = df.drop(columns=['Nr.'], errors='ignore')
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            df = df.replace(',', '.', regex=True)
            
            # Process target variable
            df['Gjinia'] = df['Gjinia'].astype(str).str.strip()
            df['Gjinia'] = df['Gjinia'].replace(['', 'nan', 'NaN', None], pd.NA)
            df = df.dropna(subset=["Gjinia"])
            df['Gjinia'] = pd.to_numeric(df['Gjinia'], errors='coerce')
            df['Gjinia'] = df['Gjinia'].fillna(0).astype(int).astype(bool)
            
            # Convert features to numeric
            for col in df.columns:
                if col != 'Gjinia':
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            print(f"✅ Loaded {len(df)} samples")
            
            # Check class distribution
            class_counts = df['Gjinia'].value_counts()
            print(f"📊 Class distribution: {class_counts[False]} Female, {class_counts[True]} Male")
            
            # Separate features and target
            X = df.drop(columns=['Gjinia'])
            y = df['Gjinia']
            
            # Remove highly correlated features (same as training)
            correlation_matrix = X.corr().abs()
            upper_triangle = correlation_matrix.where(
                np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool)
            )
            high_corr_features = [
                column for column in upper_triangle.columns 
                if any(upper_triangle[column] > 0.95)
            ]
            if high_corr_features:
                X = X.drop(columns=high_corr_features)
                print(f"🧹 Removed {len(high_corr_features)} highly correlated features")
            
            print("\\n🔧 Building new model pipeline...")
            
            # Create the pipeline
            def create_robust_pipeline(model, k_features=12):
                steps = [
                    ('smote', SMOTE(random_state=42)),
                    ('scaler', RobustScaler()),
                    ('selector', SelectKBest(f_classif, k=min(k_features, X.shape[1]))),
                    ('model', model)
                ]
                return ImbalancedPipeline(steps)
            
            # Create and train the model
            new_pipeline = create_robust_pipeline(
                LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced'),
                k_features=12
            )
            
            print("🏋️  Training new model...")
            new_pipeline.fit(X, y)
            
            # Quick validation
            if len(df) >= 5:  # Need at least 5 samples for 5-fold CV
                cv_scores = cross_val_score(new_pipeline, X, y, cv=StratifiedKFold(n_splits=min(5, len(df)), shuffle=True, random_state=42))
                print(f"\\n📈 New model performance:")
                print(f"   Cross-validation accuracy: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
            else:
                print(f"\\n⚠️  Dataset too small for cross-validation ({len(df)} samples)")
                # Simple train accuracy
                train_accuracy = new_pipeline.score(X, y)
                print(f"   Training accuracy: {train_accuracy:.3f}")
            
            # Create backup of old model
            backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if hasattr(self, 'model_pipeline') and self.model_pipeline is not None:
                backup_model_path = f'model_backup_{backup_timestamp}.pkl'
                joblib.dump(self.model_pipeline, backup_model_path)
                print(f"💾 Old model backed up to: {backup_model_path}")
            
            # Update the current model
            self.model_pipeline = new_pipeline
            self.original_features = X.columns.tolist()
            
            # Save the new model (optional - update the main model files)
            save_new = input("\\n💾 Save as new main model files? (y/n): ").lower().strip()
            if save_new in ['y', 'yes']:
                try:
                    # Create timestamped backups of current model files
                    if os.path.exists('models/current/model.pkl'):
                        shutil.copy('models/current/model.pkl', f'best_tooth_gender_model_backup_{backup_timestamp}.pkl')
                    
                    # Save new model components (simplified - just the pipeline)
                    joblib.dump(new_pipeline, 'best_tooth_gender_model_new.pkl')
                    print("✅ New model saved as 'best_tooth_gender_model_new.pkl'")
                    print("📝 Note: Old model files backed up with timestamp")
                except Exception as e:
                    print(f"⚠️  Could not save model files: {e}")
            
            print(f"\\n🎉 Model retraining completed successfully!")
            print(f"📊 Model trained on {len(X)} samples with {len(X.columns)} features")
            print(f"🎯 Ready for predictions with updated model")
            
        except Exception as e:
            print(f"\\n❌ Error during model retraining: {e}")
            print("Please check the dataset and try again.")

def main():
    """Main function"""
    print("🦷 WORKING TOOTH GENDER CLASSIFIER")
    print("="*35)
    
    try:
        predictor = WorkingToothGenderPredictor()
        
        print("\\n🎯 OPTIONS:")
        print("1. Make prediction")
        print("2. Quick test")
        print("3. Add new data to dataset")
        print("4. Retrain model")
        print("5. Exit")
        
        while True:
            try:
                choice = input("\\n⚡ Choose (1-5): ").strip()
                
                if choice == '1':
                    predictor.interactive_prediction()
                elif choice == '2':
                    predictor.quick_test()
                elif choice == '3':
                    predictor.add_data_to_excel()
                elif choice == '4':
                    predictor.retrain_model()
                elif choice == '5':
                    print("\\n👋 Goodbye!")
                    break
                else:
                    print("❌ Choose 1, 2, 3, 4, or 5")
                    
            except KeyboardInterrupt:
                print("\\n\\n👋 Goodbye!")
                break
                
    except Exception as e:
        print(f"\\n❌ Setup failed: {e}")

if __name__ == "__main__":
    main()