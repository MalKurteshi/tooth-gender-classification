#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tooth Gender Prediction Interface
Interactive tool for predicting gender based on dental measurements
"""

import os
import pandas as pd
import numpy as np
import json
import joblib
from sklearn.preprocessing import PolynomialFeatures
import warnings
warnings.filterwarnings('ignore')

class ToothGenderPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.selector = None
        self.metadata = None
        self.feature_names = None
        self.original_features = None
        self.load_model()
    
    def load_model(self):
        """Load the saved model and preprocessing components"""
        try:
            # Load model components
            self.model = joblib.load('best_tooth_gender_model.pkl')
            self.scaler = joblib.load('tooth_gender_scaler.pkl')
            self.selector = joblib.load('tooth_gender_selector.pkl')
            
            # Load metadata
            with open('model_metadata.json', 'r') as f:
                self.metadata = json.load(f)
            
            print("✅ Model loaded successfully!")
            print(f"📊 Model: {self.metadata['model_name']}")
            print(f"🎯 Cross-validation accuracy: {self.metadata['cv_accuracy']:.3f}")
            print(f"🧪 Test accuracy: {self.metadata['test_accuracy']:.3f}")
            
            # Get the original feature names (before feature engineering)
            self.get_original_features()
            
        except FileNotFoundError as e:
            print(f"❌ Error loading model files: {e}")
            print("Please run main_enhanced.py first to train and save the model.")
            raise
    
    def get_original_features(self):
        """Get the original feature names from the dataset"""
        try:
            # Load and process data to get original features
            data_path = os.path.join('data', 'Per ANN.xlsx')
            df = pd.read_excel(data_path)
            
            # Apply same preprocessing as training
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)
            df = df.drop(columns=['Nr.'], errors='ignore')
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            
            # Remove target column
            features = [col for col in df.columns if col != 'Gjinia']
            
            # Remove highly correlated features (same as training)
            X = df[features]
            for col in X.columns:
                X[col] = pd.to_numeric(X[col], errors='coerce')
                
            correlation_matrix = X.corr().abs()
            upper_triangle = correlation_matrix.where(
                np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool)
            )
            high_corr_features = [
                column for column in upper_triangle.columns 
                if any(upper_triangle[column] > 0.95)
            ]
            
            # Final original features
            self.original_features = [f for f in features if f not in high_corr_features]
            
        except Exception as e:
            print(f"Warning: Could not load original features: {e}")
            self.original_features = []
    
    def get_feature_info(self):
        """Display information about required features"""
        print("\\n📋 FEATURE REQUIREMENTS:")
        print("="*60)
        print("Please provide values for the following dental measurements:")
        print("(All measurements should be in millimeters)")
        print()
        
        if self.original_features:
            for i, feature in enumerate(self.original_features, 1):
                print(f"{i:2d}. {feature}")
        else:
            print("Features will be requested during prediction.")
        
        print("\\n💡 Tips:")
        print("• MD = Mesio-Distal (length)")
        print("• BO = Bucco-Oral (width)")
        print("• Numbers refer to tooth positions")
        print("• Typical range: 5-15mm for most measurements")
    
    def create_feature_vector(self, measurements):
        """Create feature vector matching the exact training process"""
        # Convert to DataFrame
        df_input = pd.DataFrame([measurements], columns=self.original_features)
        
        # Use the stored feature names from training to ensure consistency
        all_feature_names = self.metadata['feature_names']
        
        # Create a vector with all expected features, filling missing ones with 0
        feature_vector = []
        for feature_name in all_feature_names:
            if feature_name in measurements:
                feature_vector.append(measurements[feature_name])
            elif feature_name.startswith('poly_'):
                # Polynomial features will be 0 for now - we'll compute them properly
                feature_vector.append(0.0)
            else:
                # Use default value for missing original features
                feature_vector.append(7.5)
        
        # Convert to DataFrame with correct column names
        X_input = pd.DataFrame([feature_vector], columns=all_feature_names)
        
        # For polynomial features, we need to recreate them properly
        # Use original features to compute polynomial interactions
        original_values = [measurements.get(feat, 7.5) for feat in self.original_features]
        
        # Create polynomial features for first 8 features (matching training)
        poly_features = PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)
        first_8_features = original_values[:8]
        X_poly = poly_features.fit_transform([first_8_features])
        
        # Update polynomial feature columns
        poly_start_idx = len(self.original_features)
        poly_values = X_poly[0][8:]  # Skip the original 8 features
        
        for i, poly_val in enumerate(poly_values):
            if poly_start_idx + i < len(all_feature_names):
                X_input.iloc[0, poly_start_idx + i] = poly_val
        
        return X_input
    
    def predict_single(self, measurements):
        """Make a single prediction"""
        try:
            # Create feature vector
            X_input = self.create_feature_vector(measurements)
            
            # Apply preprocessing pipeline
            X_scaled = self.scaler.transform(X_input)
            X_selected = self.selector.transform(X_scaled)
            
            # Make prediction
            prediction = self.model.predict(X_selected)[0]
            probability = self.model.predict_proba(X_selected)[0]
            
            # Convert prediction to readable format
            gender = "Male" if prediction else "Female"
            confidence = max(probability) * 100
            
            return {
                'prediction': gender,
                'confidence': confidence,
                'probabilities': {
                    'Female': probability[0] * 100,
                    'Male': probability[1] * 100
                }
            }
            
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return None
    
    def interactive_prediction(self):
        """Interactive prediction interface"""
        print("\\n🦷 TOOTH GENDER PREDICTION INTERFACE")
        print("="*50)
        
        while True:
            try:
                measurements = {}
                
                print("\\nPlease enter dental measurements (in mm):")
                print("(Press Enter for missing values - they'll be handled automatically)")
                
                for i, feature in enumerate(self.original_features, 1):
                    while True:
                        try:
                            value_input = input(f"{i:2d}. {feature}: ")
                            if value_input.strip() == "":
                                # Use average value for missing measurements
                                measurements[feature] = 7.5  # Reasonable average
                                print(f"    → Using default value: 7.5mm")
                                break
                            else:
                                value = float(value_input)
                                if 0 < value < 50:  # Reasonable range check
                                    measurements[feature] = value
                                    break
                                else:
                                    print("    ⚠️  Please enter a value between 0 and 50mm")
                        except ValueError:
                            print("    ⚠️  Please enter a valid number")
                
                # Make prediction
                print("\\n🔄 Processing...")
                result = self.predict_single(measurements)
                
                if result:
                    print("\\n" + "="*50)
                    print("🎯 PREDICTION RESULTS")
                    print("="*50)
                    print(f"👤 Predicted Gender: {result['prediction']}")
                    print(f"🎲 Confidence: {result['confidence']:.1f}%")
                    print("\\n📊 Probability Breakdown:")
                    print(f"   Female: {result['probabilities']['Female']:.1f}%")
                    print(f"   Male:   {result['probabilities']['Male']:.1f}%")
                    
                    # Confidence interpretation
                    if result['confidence'] > 80:
                        confidence_level = "Very High"
                        emoji = "🟢"
                    elif result['confidence'] > 70:
                        confidence_level = "High"
                        emoji = "🔵"
                    elif result['confidence'] > 60:
                        confidence_level = "Moderate"
                        emoji = "🟡"
                    else:
                        confidence_level = "Low"
                        emoji = "🔴"
                    
                    print(f"\\n{emoji} Confidence Level: {confidence_level}")
                    
                else:
                    print("❌ Prediction failed. Please try again.")
                
                # Ask for another prediction
                print("\\n" + "-"*50)
                another = input("\\n🔄 Make another prediction? (y/n): ").lower().strip()
                if another not in ['y', 'yes']:
                    break
                    
            except KeyboardInterrupt:
                print("\\n\\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\\n❌ Error: {e}")
                print("Please try again.")
    
    def batch_prediction(self, csv_file):
        """Make predictions for a CSV file"""
        try:
            df = pd.read_csv(csv_file)
            results = []
            
            print(f"\\n📁 Processing {len(df)} samples from {csv_file}")
            
            for idx, row in df.iterrows():
                measurements = {}
                for feature in self.original_features:
                    measurements[feature] = row.get(feature, 7.5)  # Default value for missing
                
                result = self.predict_single(measurements)
                if result:
                    results.append({
                        'Sample': idx + 1,
                        'Predicted_Gender': result['prediction'],
                        'Confidence': result['confidence'],
                        'Female_Probability': result['probabilities']['Female'],
                        'Male_Probability': result['probabilities']['Male']
                    })
            
            # Save results
            results_df = pd.DataFrame(results)
            output_file = csv_file.replace('.csv', '_predictions.csv')
            results_df.to_csv(output_file, index=False)
            
            print(f"✅ Predictions saved to: {output_file}")
            return results_df
            
        except Exception as e:
            print(f"❌ Batch prediction error: {e}")
            return None

def main():
    """Main function"""
    try:
        # Initialize predictor
        predictor = ToothGenderPredictor()
        
        # Show feature information
        predictor.get_feature_info()
        
        print("\\n" + "="*60)
        print("PREDICTION OPTIONS:")
        print("1. Interactive prediction (manual input)")
        print("2. Batch prediction (from CSV file)")
        print("3. Show model information")
        print("4. Exit")
        
        while True:
            try:
                choice = input("\\n🎯 Select option (1-4): ").strip()
                
                if choice == '1':
                    predictor.interactive_prediction()
                    
                elif choice == '2':
                    csv_file = input("\\n📁 Enter CSV file path: ").strip()
                    if os.path.exists(csv_file):
                        predictor.batch_prediction(csv_file)
                    else:
                        print("❌ File not found!")
                        
                elif choice == '3':
                    print("\\n📊 MODEL INFORMATION:")
                    print("="*40)
                    for key, value in predictor.metadata.items():
                        if key != 'preprocessing_steps':
                            print(f"{key.replace('_', ' ').title()}: {value}")
                    
                    print("\\n🔧 Preprocessing Steps:")
                    for step in predictor.metadata['preprocessing_steps']:
                        print(f"  • {step}")
                        
                elif choice == '4':
                    print("\\n👋 Goodbye!")
                    break
                    
                else:
                    print("❌ Invalid option. Please select 1-4.")
                    
            except KeyboardInterrupt:
                print("\\n\\n👋 Goodbye!")
                break
                
    except Exception as e:
        print(f"❌ Error initializing predictor: {e}")

if __name__ == "__main__":
    main()