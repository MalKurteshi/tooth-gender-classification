#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tooth Gender Classification - Final Prediction Interface
Working tool for making predictions with the trained model
"""

import pandas as pd
import numpy as np
import json
import joblib
from sklearn.preprocessing import PolynomialFeatures
import warnings
warnings.filterwarnings('ignore')

class ToothGenderPredictor:
    def __init__(self):
        """Initialize the predictor by loading the saved model"""
        self.model = None
        self.scaler = None
        self.selector = None
        self.metadata = None
        self.load_model_components()
    
    def load_model_components(self):
        """Load all saved model components"""
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
            print(f"📝 Selected features: {len(self.metadata['selected_features'])}")
            
        except FileNotFoundError as e:
            print(f"❌ Error loading model files: {e}")
            print("Please run main_enhanced.py first to train and save the model.")
            raise
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise
    
    def get_original_features(self):
        """Return the list of original dental measurement features"""
        return [
            'U M2 MD (mm)', 'U M1 MD (mm)', 'U P2 MD (mm)', 'U P1 MD (mm)',
            '13 BO (mm)', '13 MD (mm)', '12MD (mm)', '11 MD (mm)',
            '22 MD (mm)', '23 MD (mm)', 'L M2 MD (mm)', 'L M1 MD (mm)',
            'L P2 MD (mm)', 'L P1 MD (mm)', '43 BO (mm)', '43 MD (mm)',
            '42MD (mm)', '41 MD (mm)', '32 MD (mm)', '33 MD (mm)',
            'Harku interkanin mandibullar'
        ]
    
    def preprocess_features(self, measurements):
        """Preprocess the input measurements to match training pipeline"""
        try:
            # Step 1: Get original features
            original_features = self.get_original_features()
            
            # Step 2: Create base feature vector (with defaults for missing values)
            base_values = []
            for feature in original_features:
                value = measurements.get(feature, 7.5)  # Use 7.5 as default
                base_values.append(float(value))
            
            # Step 3: Create polynomial features for first 8 features
            # This replicates the exact feature engineering from training
            poly_features = PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)
            first_8_features = np.array(base_values[:8]).reshape(1, -1)
            poly_expanded = poly_features.fit_transform(first_8_features)
            
            # Extract only the interaction terms (skip first 8 original features)
            interaction_terms = poly_expanded[0][8:]
            
            # Step 4: Combine original features with polynomial features
            all_features = base_values + interaction_terms.tolist()
            
            # Step 5: Create DataFrame with correct column names
            feature_names = self.metadata['feature_names']
            X = pd.DataFrame([all_features], columns=feature_names)
            
            return X
            
        except Exception as e:
            print(f"❌ Preprocessing error: {e}")
            return None
    
    def predict_gender(self, measurements):
        """Make a gender prediction from dental measurements"""
        try:
            # Preprocess the measurements
            X = self.preprocess_features(measurements)
            if X is None:
                return None
            
            # Apply the same preprocessing pipeline as training
            # 1. Scale the features
            X_scaled = self.scaler.transform(X)
            
            # 2. Select the best features
            X_selected = self.selector.transform(X_scaled)
            
            # 3. Make the prediction
            prediction = self.model.predict(X_selected)[0]
            probabilities = self.model.predict_proba(X_selected)[0]
            
            # Convert to readable format
            gender = "Male" if prediction else "Female"
            confidence = max(probabilities) * 100
            
            return {
                'prediction': gender,
                'confidence': confidence,
                'probabilities': {
                    'Female': probabilities[0] * 100,
                    'Male': probabilities[1] * 100
                },
                'raw_prediction': int(prediction),
                'raw_probabilities': probabilities.tolist()
            }
            
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return None
    
    def interactive_session(self):
        """Run an interactive prediction session"""
        print("\\n🦷 INTERACTIVE TOOTH GENDER PREDICTION")
        print("="*45)
        print("Enter dental measurements in millimeters")
        print("Press Enter to use default value (7.5mm)\\n")
        
        original_features = self.get_original_features()
        
        while True:
            try:
                measurements = {}
                print("📏 Enter measurements:")
                print("-" * 30)
                
                # Collect all measurements
                for i, feature in enumerate(original_features, 1):
                    while True:
                        try:
                            user_input = input(f"{i:2d}. {feature}: ")
                            
                            if user_input.strip() == "":
                                measurements[feature] = 7.5
                                print(f"    → Using default: 7.5mm")
                                break
                            else:
                                # Handle comma as decimal separator
                                value = float(user_input.replace(',', '.'))
                                if 0.1 <= value <= 50.0:  # Reasonable range
                                    measurements[feature] = value
                                    break
                                else:
                                    print("    ⚠️  Please enter a value between 0.1 and 50.0mm")
                        except ValueError:
                            print("    ⚠️  Please enter a valid number or press Enter for default")
                
                # Make prediction
                print("\\n🔄 Processing...")
                result = self.predict_gender(measurements)
                
                # Display results
                if result:
                    print("\\n" + "="*45)
                    print("🎯 PREDICTION RESULTS")
                    print("="*45)
                    print(f"👤 Predicted Gender: {result['prediction']}")
                    print(f"🎲 Confidence Level: {result['confidence']:.1f}%")
                    
                    print("\\n📊 Detailed Probabilities:")
                    print(f"   Female: {result['probabilities']['Female']:.2f}%")
                    print(f"   Male:   {result['probabilities']['Male']:.2f}%")
                    
                    # Confidence interpretation
                    conf = result['confidence']
                    if conf >= 90:
                        print("\\n🟢 Very High Confidence - Excellent prediction")
                    elif conf >= 80:
                        print("\\n🔵 High Confidence - Good prediction")
                    elif conf >= 70:
                        print("\\n🟡 Moderate Confidence - Fair prediction")
                    elif conf >= 60:
                        print("\\n🟠 Low Confidence - Uncertain prediction")
                    else:
                        print("\\n🔴 Very Low Confidence - Unreliable prediction")
                    
                else:
                    print("❌ Prediction failed. Please check your inputs.")
                
                # Ask for another prediction
                print("\\n" + "-"*45)
                another = input("\\n🔄 Make another prediction? (y/n): ").lower().strip()
                if another not in ['y', 'yes', 'да']:
                    break
                    
            except KeyboardInterrupt:
                print("\\n\\n👋 Session ended by user")
                break
            except Exception as e:
                print(f"\\n❌ Session error: {e}")
                print("Please try again.")
    
    def quick_demo(self):
        """Show a quick demonstration"""
        print("\\n🔬 QUICK DEMONSTRATION")
        print("="*30)
        
        # Example with typical male measurements (larger values)
        male_example = {
            'U M2 MD (mm)': 10.2, 'U M1 MD (mm)': 11.1, 'U P2 MD (mm)': 7.8, 'U P1 MD (mm)': 8.1,
            '13 BO (mm)': 8.9, '13 MD (mm)': 8.2, '12MD (mm)': 7.1, '11 MD (mm)': 8.8,
            '22 MD (mm)': 6.9, '23 MD (mm)': 8.5, 'L M2 MD (mm)': 12.1, 'L M1 MD (mm)': 11.8,
            'L P2 MD (mm)': 7.9, 'L P1 MD (mm)': 7.6, '43 BO (mm)': 8.1, '43 MD (mm)': 7.8,
            '42MD (mm)': 6.9, '41 MD (mm)': 6.2, '32 MD (mm)': 6.8, '33 MD (mm)': 7.2,
            'Harku interkanin mandibullar': 29.5
        }
        
        # Example with typical female measurements (smaller values)
        female_example = {
            'U M2 MD (mm)': 8.9, 'U M1 MD (mm)': 9.8, 'U P2 MD (mm)': 6.2, 'U P1 MD (mm)': 6.8,
            '13 BO (mm)': 7.1, '13 MD (mm)': 6.9, '12MD (mm)': 5.8, '11 MD (mm)': 7.2,
            '22 MD (mm)': 5.5, '23 MD (mm)': 6.8, 'L M2 MD (mm)': 10.1, 'L M1 MD (mm)': 9.7,
            'L P2 MD (mm)': 6.8, 'L P1 MD (mm)': 6.2, '43 BO (mm)': 6.8, '43 MD (mm)': 6.1,
            '42MD (mm)': 5.7, '41 MD (mm)': 5.1, '32 MD (mm)': 5.6, '33 MD (mm)': 6.0,
            'Harku interkanin mandibullar': 24.8
        }
        
        examples = [("Typical Male Pattern", male_example), ("Typical Female Pattern", female_example)]
        
        for name, example in examples:
            print(f"\\n📋 {name}:")
            print("Sample measurements:")
            for feature, value in list(example.items())[:4]:
                print(f"  {feature}: {value}mm")
            print("  ... (and 17 more)")
            
            result = self.predict_gender(example)
            if result:
                print(f"➡️  Prediction: {result['prediction']} ({result['confidence']:.1f}% confidence)")
            else:
                print("❌ Demo prediction failed")
    
    def show_model_info(self):
        """Display detailed model information"""
        print("\\n📊 MODEL INFORMATION")
        print("="*30)
        print(f"Algorithm: {self.metadata['model_name']}")
        print(f"Cross-validation Accuracy: {self.metadata['cv_accuracy']:.3f}")
        print(f"Test Set Accuracy: {self.metadata['test_accuracy']:.3f}")
        if self.metadata.get('auc_score'):
            print(f"AUC Score: {self.metadata['auc_score']:.3f}")
        
        print(f"\\n🔧 Features Used:")
        print(f"Total features after engineering: {len(self.metadata['feature_names'])}")
        print(f"Selected by algorithm: {len(self.metadata['selected_features'])}")
        
        print(f"\\n📝 Top Selected Features:")
        for i, feature in enumerate(self.metadata['selected_features'][:10], 1):
            print(f"  {i:2d}. {feature}")
        
        print(f"\\n⚙️  Preprocessing Pipeline:")
        for step in self.metadata['preprocessing_steps']:
            print(f"  • {step}")

def main():
    """Main application entry point"""
    print("🦷 TOOTH GENDER CLASSIFICATION SYSTEM")
    print("="*40)
    
    try:
        # Initialize the predictor
        predictor = ToothGenderPredictor()
        
        print("\\n🎯 AVAILABLE OPTIONS:")
        print("1. Interactive Prediction")
        print("2. Quick Demo")
        print("3. Model Information") 
        print("4. Exit")
        
        while True:
            try:
                choice = input("\\n⚡ Select option (1-4): ").strip()
                
                if choice == '1':
                    predictor.interactive_session()
                    
                elif choice == '2':
                    predictor.quick_demo()
                    
                elif choice == '3':
                    predictor.show_model_info()
                    
                elif choice == '4':
                    print("\\n👋 Thank you for using the Tooth Gender Classification System!")
                    break
                    
                else:
                    print("❌ Please select a number from 1-4")
                    
            except KeyboardInterrupt:
                print("\\n\\n👋 System terminated by user")
                break
            except Exception as e:
                print(f"\\n❌ Error: {e}")
                print("Please try again or contact support.")
                
    except Exception as e:
        print(f"\\n❌ Failed to initialize system: {e}")
        print("Make sure all model files are present and try again.")

if __name__ == "__main__":
    main()