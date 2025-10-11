"""
Setup configuration for Tooth Gender Classification package
"""

from setuptools import setup, find_packages

setup(
    name="tooth-gender-classification",
    version="2.0.0",
    description="Machine learning model for gender prediction based on dental measurements",
    author="Mal Kurteshi", 
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.20.0", 
        "scikit-learn>=1.0.0",
        "imbalanced-learn>=0.8.0",
        "xgboost>=1.5.0",
        "lightgbm>=3.2.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "openpyxl>=3.0.0",
        "joblib>=1.1.0",
    ],
    extras_require={
        "dev": ["pytest>=6.0.0", "jupyter>=1.0.0"],
        "reports": ["reportlab>=3.6.0"],
    },
    entry_points={
        "console_scripts": [
            "tooth-predict=src.predict:main",
        ],
    },
)
