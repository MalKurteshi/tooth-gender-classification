#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Tooth Gender Prediction Interface
Streamlined tool for making predictions with saved model
"""

import pandas as pd
import numpy as np
import json
import joblib
import warnings
warnings.filterwarnings('ignore')

class SimpleToothGenderPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.selector = None
        self.metadata = None
        self.load_model()
    
    def load_model(self):
        """Load the saved model and preprocessing components"""
        try:
            self.model = joblib.load('best_tooth_gender_model.pkl')
            self.scaler = joblib.load('tooth_gender_scaler.pkl')
            self.selector = joblib.load('tooth_gender_selector.pkl')
            
            with open('model_metadata.json', 'r') as f:
                self.metadata = json.load(f)
            
            print("✅ Model loaded successfully!")
            print(f"📊 Model: {self.metadata['model_name']}")
            print(f"🎯 Cross-validation accuracy: {self.metadata['cv_accuracy']:.3f}")
            
        except FileNotFoundError as e:
            print(f"❌ Error loading model files: {e}")
            print("Please run main_enhanced.py first to train and save the model.")
            raise
    
    def get_required_features(self):
        """Get the original features needed for prediction"""
        # These are the 21 original features after removing highly correlated ones
        return [
            'U M2 MD (mm)', 'U M1 MD (mm)', 'U P2 MD (mm)', 'U P1 MD (mm)',
            '13 BO (mm)', '13 MD (mm)', '12MD (mm)', '11 MD (mm)',
            '22 MD (mm)', '23 MD (mm)', 'L M2 MD (mm)', 'L M1 MD (mm)',
            'L P2 MD (mm)', 'L P1 MD (mm)', '43 BO (mm)', '43 MD (mm)',
            '42MD (mm)', '41 MD (mm)', '32 MD (mm)', '33 MD (mm)',
            'Harku interkanin mandibullar'
        ]
    
    def create_full_feature_vector(self, measurements):
        """Create the complete feature vector as used in training"""
        original_features = self.get_required_features()
        
        # Create base feature vector
        base_values = []
        for feature in original_features:
            value = measurements.get(feature, 7.5)  # Default value for missing features
            base_values.append(value)
        
        # Create polynomial interaction features for top 8 features
        # This matches the feature engineering from training
        from sklearn.preprocessing import PolynomialFeatures
        
        # Use first 8 features for polynomial expansion
        top_8_values = base_values[:8]
        poly = PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)
        poly_expanded = poly.fit_transform([top_8_values])[0]
        
        # The polynomial expansion includes original features + interactions
        # We only want the interaction terms (skip first 8)
        interaction_terms = poly_expanded[8:]
        
        # Combine original features with interaction terms
        full_vector = base_values + interaction_terms.tolist()
        
        return np.array(full_vector).reshape(1, -1)
    
    def predict(self, measurements):
        """Make a prediction from measurement dictionary"""
        try:
            # Create feature vector
            X = self.create_full_feature_vector(measurements)
            
            # Apply preprocessing (same as training)
            X_scaled = self.scaler.transform(X)
            X_selected = self.selector.transform(X_scaled)
            
            # Make prediction
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
                }
            }
            
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return None
    
    def interactive_prediction(self):
        """Simple interactive interface"""
        print("\\n🦷 TOOTH GENDER PREDICTION")
        print("="*40)
        print("Enter dental measurements (in mm)")
        print("Press Enter to skip a measurement\\n")
        
        features = self.get_required_features()
        measurements = {}
        
        for i, feature in enumerate(features, 1):
            while True:
                try:
                    value_str = input(f"{i:2d}. {feature}: ")
                    if value_str.strip() == "":
                        measurements[feature] = 7.5  # Default value
                        print(f"    → Using default: 7.5mm")
                        break
                    else:
                        value = float(value_str.replace(',', '.'))  # Handle comma as decimal
                        if 0 < value < 50:
                            measurements[feature] = value
                            break
                        else:
                            print("    ⚠️  Please enter a value between 0 and 50mm")
                except ValueError:
                    print("    ⚠️  Please enter a valid number")
        
        # Make prediction
        print("\\n🔄 Making prediction...")
        result = self.predict(measurements)
        
        if result:
            print("\\n" + "="*40)
            print("🎯 PREDICTION RESULT")
            print("="*40)
            print(f"👤 Gender: {result['prediction']}")
            print(f"🎲 Confidence: {result['confidence']:.1f}%")
            print("\\n📊 Probabilities:")
            print(f"   Female: {result['probabilities']['Female']:.1f}%")
            print(f"   Male:   {result['probabilities']['Male']:.1f}%")
            
            # Confidence level
            if result['confidence'] > 80:
                print("\\n🟢 Very High Confidence")
            elif result['confidence'] > 70:
                print("\\n🔵 High Confidence")
            elif result['confidence'] > 60:
                print("\\n🟡 Moderate Confidence")
            else:
                print("\\n🔴 Low Confidence")
        else:
            print("❌ Prediction failed")
    
    def quick_example(self):
        """Show a quick example prediction"""
        print("\\n🔬 QUICK EXAMPLE PREDICTION")
        print("="*40)
        
        # Example measurements (typical values)
        example_measurements = {
            'U M2 MD (mm)': 9.2, 'U M1 MD (mm)': 10.5, 'U P2 MD (mm)': 6.8, 'U P1 MD (mm)': 7.2,
            '13 BO (mm)': 8.1, '13 MD (mm)': 7.7, '12MD (mm)': 6.4, '11 MD (mm)': 8.2,
            '22 MD (mm)': 6.1, '23 MD (mm)': 7.8, 'L M2 MD (mm)': 11.2, 'L M1 MD (mm)': 10.8,
            'L P2 MD (mm)': 7.1, 'L P1 MD (mm)': 6.9, '43 BO (mm)': 7.5, '43 MD (mm)': 6.8,
            '42MD (mm)': 6.2, '41 MD (mm)': 5.4, '32 MD (mm)': 6.1, '33 MD (mm)': 6.7,
            'Harku interkanin mandibullar': 27.5
        }
        
        print("Using example measurements:")
        for feature, value in list(example_measurements.items())[:5]:
            print(f"  {feature}: {value}mm")
        print("  ... (and 16 more features)")
        
        result = self.predict(example_measurements)
        
        if result:
            print(f"\\n➡️  Prediction: {result['prediction']} ({result['confidence']:.1f}% confidence)")
        else:
            print("❌ Example prediction failed")

def main():
    """Main function"""
    try:
        predictor = SimpleToothGenderPredictor()
        
        print("\\n" + "="*50)
        print("OPTIONS:")
        print("1. Make a prediction (interactive)")
        print("2. Show quick example")
        print("3. Show model info")
        print("4. Exit")
        
        while True:
            try:
                choice = input("\\n🎯 Select option (1-4): ").strip()
                
                if choice == '1':
                    predictor.interactive_prediction()
                    
                elif choice == '2':
                    predictor.quick_example()
                    
                elif choice == '3':
                    print("\\n📊 MODEL INFORMATION:")
                    print(f"Model: {predictor.metadata['model_name']}")
                    print(f"CV Accuracy: {predictor.metadata['cv_accuracy']:.3f}")
                    print(f"Test Accuracy: {predictor.metadata['test_accuracy']:.3f}")
                    print(f"Features: {len(predictor.get_required_features())}")
                    
                elif choice == '4':
                    print("\\n👋 Goodbye!")
                    break
                    
                else:
                    print("❌ Please select 1-4")
                    
            except KeyboardInterrupt:
                print("\\n\\n👋 Goodbye!")
                break
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()