# API Documentation

## src.predict module

### ToothGenderPredictor class

Main class for making gender predictions from dental measurements.

#### Methods

- `predict_gender(measurements: dict) -> dict`: Make prediction from measurements
- `interactive_prediction() -> None`: Run interactive prediction session  
- `add_data_to_excel() -> None`: Add new training data to dataset
- `retrain_model() -> None`: Retrain model with updated data

#### Example Usage

```python
from src.predict import WorkingToothGenderPredictor

predictor = WorkingToothGenderPredictor()

# Make prediction
measurements = {
    'U M1 MD (mm)': 10.5,
    'L M1 MD (mm)': 11.0,
    # ... other measurements
}
result = predictor.predict_gender(measurements)
print(f"Prediction: {result['prediction']} ({result['confidence']:.1f}%)")
```

## Configuration

Model and data paths can be configured in src/config.py
