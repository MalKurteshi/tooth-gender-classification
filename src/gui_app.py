#!/usr/bin/env python3
"""
Tooth Gender Classification - Desktop GUI Application
Cross-platform desktop interface for non-technical users

Supports: Windows, macOS, Linux
Requirements: Python 3.8+ with tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import sys
import platform
import subprocess
import threading
from datetime import datetime
import json

# Add the src directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class ToothGenderGUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.check_dependencies()
        self.create_widgets()
        
    def setup_window(self):
        """Setup the main window"""
        self.root.title("Tooth Gender Classification - Desktop App")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Set window icon (if available)
        try:
            if platform.system() == "Windows":
                self.root.iconbitmap("assets/tooth_icon.ico")
            else:
                # For macOS and Linux
                icon_path = "assets/tooth_icon.png"
                if os.path.exists(icon_path):
                    self.root.iconphoto(True, tk.PhotoImage(file=icon_path))
        except:
            pass  # Icon not available
        
        # Configure style
        self.style = ttk.Style()
        if platform.system() == "Darwin":  # macOS
            self.style.theme_use('aqua')
        elif platform.system() == "Windows":
            self.style.theme_use('vista')
        else:  # Linux
            self.style.theme_use('clam')
            
    def setup_variables(self):
        """Setup tkinter variables"""
        self.feature_vars = {}
        self.features = [
            'U M2 MD (mm)', 'U M1 MD (mm)', 'U P2 MD (mm)', 'U P1 MD (mm)',
            '13 BO (mm)', '13 MD (mm)', '12MD (mm)', '11 MD (mm)',
            '22 MD (mm)', '23 MD (mm)', 'L M2 MD (mm)', 'L M1 MD (mm)',
            'L P2 MD (mm)', 'L P1 MD (mm)', '43 BO (mm)', '43 MD (mm)',
            '42MD (mm)', '41 MD (mm)', '32 MD (mm)', '33 MD (mm)',
            'Harku interkanin mandibullar'
        ]
        
        # Create StringVar for each feature
        for feature in self.features:
            self.feature_vars[feature] = tk.StringVar()
            
        self.result_var = tk.StringVar()
        self.confidence_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        
    def check_dependencies(self):
        """Check if required dependencies are available"""
        self.dependencies_ok = False
        try:
            # Try importing required modules
            import pandas
            import numpy 
            import sklearn
            import joblib
            
            # Check if model files exist
            model_path = os.path.join('models', 'current', 'model.pkl')
            if os.path.exists(model_path):
                self.dependencies_ok = True
            else:
                self.show_error("Model files not found", 
                               "Please ensure the model files are in the 'models/current/' directory.")
                
        except ImportError as e:
            self.show_error("Dependencies Missing", 
                           f"Required Python packages are missing: {e}")
            
    def create_widgets(self):
        """Create and arrange GUI widgets"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🦷 Tooth Gender Classification", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, padx=(0, 5))
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                                foreground="green" if self.dependencies_ok else "red")
        status_label.grid(row=0, column=1, sticky=tk.W)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(2, weight=1)
        
        # Tab 1: Prediction
        self.create_prediction_tab(notebook)
        
        # Tab 2: Data Entry
        self.create_data_entry_tab(notebook)
        
        # Tab 3: Settings
        self.create_settings_tab(notebook)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        results_frame.columnconfigure(1, weight=1)
        
        ttk.Label(results_frame, text="Predicted Gender:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        result_label = ttk.Label(results_frame, textvariable=self.result_var, 
                                font=('Arial', 12, 'bold'), foreground="blue")
        result_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(results_frame, text="Confidence:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        confidence_label = ttk.Label(results_frame, textvariable=self.confidence_var, 
                                    font=('Arial', 12, 'bold'), foreground="green")
        confidence_label.grid(row=1, column=1, sticky=tk.W)
        
    def create_prediction_tab(self, parent):
        """Create the prediction input tab"""
        pred_frame = ttk.Frame(parent, padding="10")
        parent.add(pred_frame, text="🎯 Make Prediction")
        
        # Create scrollable frame for inputs
        canvas = tk.Canvas(pred_frame)
        scrollbar = ttk.Scrollbar(pred_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Arrange canvas and scrollbar
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        pred_frame.columnconfigure(0, weight=1)
        pred_frame.rowconfigure(0, weight=1)
        
        # Add input fields
        ttk.Label(scrollable_frame, text="Enter dental measurements (in mm):", 
                 font=('Arial', 11, 'bold')).grid(row=0, column=0, columnspan=2, 
                                                  pady=(0, 15), sticky=tk.W)
        
        # Create input fields in two columns
        for i, feature in enumerate(self.features):
            row = (i // 2) + 1
            col = (i % 2) * 2
            
            ttk.Label(scrollable_frame, text=f"{feature}:").grid(
                row=row, column=col, sticky=tk.W, padx=(0, 5), pady=2)
            
            entry = ttk.Entry(scrollable_frame, textvariable=self.feature_vars[feature], width=12)
            entry.grid(row=row, column=col+1, padx=(0, 20), pady=2, sticky=tk.W)
            
        # Buttons frame
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=len(self.features)//2 + 2, column=0, columnspan=4, pady=(20, 10))
        
        ttk.Button(button_frame, text="🎯 Predict Gender", 
                  command=self.make_prediction).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🔄 Clear All", 
                  command=self.clear_inputs).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📁 Load from CSV", 
                  command=self.load_from_csv).pack(side=tk.LEFT)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)  # Windows
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux
        
    def create_data_entry_tab(self, parent):
        """Create the data entry tab"""
        data_frame = ttk.Frame(parent, padding="10")
        parent.add(data_frame, text="📝 Add Data")
        
        ttk.Label(data_frame, text="Add New Training Data", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        info_text = """This feature allows you to add new dental measurements to the training dataset.
After entering measurements and the actual gender, the data will be saved for future model improvements."""
        
        ttk.Label(data_frame, text=info_text, wraplength=600, 
                 justify=tk.LEFT).pack(pady=(0, 20))
        
        ttk.Button(data_frame, text="📝 Add New Training Data", 
                  command=self.add_training_data).pack(pady=10)
        
        ttk.Button(data_frame, text="🔄 Retrain Model", 
                  command=self.retrain_model).pack(pady=10)
        
    def create_settings_tab(self, parent):
        """Create the settings tab"""
        settings_frame = ttk.Frame(parent, padding="10")
        parent.add(settings_frame, text="⚙️ Settings")
        
        ttk.Label(settings_frame, text="Application Settings", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # System information
        info_frame = ttk.LabelFrame(settings_frame, text="System Information", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        system_info = f"""Operating System: {platform.system()} {platform.release()}
Python Version: {sys.version.split()[0]}
Platform: {platform.platform()}
Dependencies: {"✅ Available" if self.dependencies_ok else "❌ Missing"}"""
        
        ttk.Label(info_frame, text=system_info, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Action buttons
        ttk.Button(settings_frame, text="🔧 Check Dependencies", 
                  command=self.check_dependencies_detailed).pack(pady=5)
        ttk.Button(settings_frame, text="📋 View Model Info", 
                  command=self.show_model_info).pack(pady=5)
        ttk.Button(settings_frame, text="📊 Generate Report", 
                  command=self.generate_report).pack(pady=5)
        
    def make_prediction(self):
        """Make a gender prediction"""
        if not self.dependencies_ok:
            self.show_error("Dependencies Missing", 
                           "Please install required dependencies first.")
            return
            
        try:
            # Collect measurements
            measurements = {}
            missing_fields = []
            
            for feature in self.features:
                value = self.feature_vars[feature].get().strip()
                if value:
                    try:
                        measurements[feature] = float(value.replace(',', '.'))
                    except ValueError:
                        self.show_error("Invalid Input", 
                                       f"'{value}' is not a valid number for {feature}")
                        return
                else:
                    missing_fields.append(feature)
            
            # Check if too many fields are missing
            if len(missing_fields) > 10:
                self.show_error("Insufficient Data", 
                               "Please provide at least 11 measurements for accurate prediction.")
                return
            
            # Fill missing values with default
            for field in missing_fields:
                measurements[field] = 7.5
                
            self.status_var.set("Making prediction...")
            self.root.update()
            
            # Make prediction using the backend
            result = self.predict_using_backend(measurements)
            
            if result:
                self.result_var.set(result['prediction'])
                self.confidence_var.set(f"{result['confidence']:.1f}%")
                self.status_var.set("Prediction completed")
                
                # Show detailed results
                self.show_detailed_results(result)
            else:
                self.result_var.set("Error")
                self.confidence_var.set("N/A")
                self.status_var.set("Prediction failed")
                
        except Exception as e:
            self.show_error("Prediction Error", f"An error occurred: {str(e)}")
            
    def predict_using_backend(self, measurements):
        """Use the backend prediction logic"""
        try:
            # Import and use the existing prediction logic
            from predict import WorkingToothGenderPredictor
            
            predictor = WorkingToothGenderPredictor()
            result = predictor.predict_gender(measurements)
            return result
            
        except Exception as e:
            print(f"Backend prediction error: {e}")
            return None
            
    def clear_inputs(self):
        """Clear all input fields"""
        for var in self.feature_vars.values():
            var.set("")
        self.result_var.set("")
        self.confidence_var.set("")
        self.status_var.set("Inputs cleared")
        
    def load_from_csv(self):
        """Load measurements from CSV file"""
        try:
            file_path = filedialog.askopenfilename(
                title="Select CSV file",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if file_path:
                import pandas as pd
                df = pd.read_csv(file_path)
                
                # Load first row of data
                if len(df) > 0:
                    row = df.iloc[0]
                    loaded_count = 0
                    
                    for feature in self.features:
                        if feature in row and pd.notna(row[feature]):
                            self.feature_vars[feature].set(str(row[feature]))
                            loaded_count += 1
                    
                    self.status_var.set(f"Loaded {loaded_count} measurements from CSV")
                else:
                    self.show_error("Empty File", "The CSV file contains no data.")
                    
        except Exception as e:
            self.show_error("File Load Error", f"Could not load CSV file: {str(e)}")
            
    def add_training_data(self):
        """Open data entry dialog"""
        DataEntryDialog(self.root, self)
        
    def retrain_model(self):
        """Retrain the model"""
        if not self.dependencies_ok:
            self.show_error("Dependencies Missing", 
                           "Please install required dependencies first.")
            return
            
        response = messagebox.askyesno(
            "Retrain Model",
            "This will retrain the model with the current dataset. This may take a few minutes. Continue?"
        )
        
        if response:
            RetrainDialog(self.root, self)
            
    def check_dependencies_detailed(self):
        """Show detailed dependency information"""
        DependencyDialog(self.root)
        
    def show_model_info(self):
        """Show model information"""
        try:
            metadata_path = os.path.join('models', 'current', 'metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                info = f"""Model Information:

Model Type: {metadata.get('model_name', 'N/A')}
Cross-validation Accuracy: {metadata.get('cv_accuracy', 'N/A')}
Test Accuracy: {metadata.get('test_accuracy', 'N/A')}
AUC Score: {metadata.get('auc_score', 'N/A')}
Number of Features: {len(metadata.get('feature_names', []))}
Selected Features: {len(metadata.get('selected_features', []))}

Target Classes: {', '.join(metadata.get('target_classes', []))}
"""
                messagebox.showinfo("Model Information", info)
            else:
                messagebox.showerror("Error", "Model metadata not found.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not load model information: {str(e)}")
            
    def generate_report(self):
        """Generate analysis report"""
        try:
            self.status_var.set("Generating report...")
            self.root.update()
            
            # Run the report generation script
            subprocess.run([sys.executable, "scripts/generate_report.py"], 
                          cwd=os.path.dirname(os.path.dirname(__file__)))
            
            self.status_var.set("Report generated successfully")
            messagebox.showinfo("Success", "Analysis report generated successfully!")
            
        except Exception as e:
            self.status_var.set("Report generation failed")
            messagebox.showerror("Error", f"Could not generate report: {str(e)}")
            
    def show_detailed_results(self, result):
        """Show detailed prediction results"""
        details = f"""Prediction Results:

Predicted Gender: {result['prediction']}
Confidence: {result['confidence']:.1f}%

Probability Breakdown:
• Female: {result['probabilities']['Female']:.1f}%
• Male: {result['probabilities']['Male']:.1f}%

Confidence Level: {self.get_confidence_level(result['confidence'])}
"""
        messagebox.showinfo("Prediction Results", details)
        
    def get_confidence_level(self, confidence):
        """Get confidence level description"""
        if confidence >= 90:
            return "Very High"
        elif confidence >= 80:
            return "High"
        elif confidence >= 70:
            return "Moderate"
        elif confidence >= 60:
            return "Low"
        else:
            return "Very Low"
            
    def show_error(self, title, message):
        """Show error message"""
        messagebox.showerror(title, message)
        self.status_var.set(f"Error: {title}")

class DataEntryDialog:
    """Dialog for entering training data"""
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.create_dialog()
        
    def create_dialog(self):
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Add Training Data")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        ttk.Label(self.dialog, text="Add New Training Data", 
                 font=('Arial', 14, 'bold')).pack(pady=20)
        
        info_text = """To add training data, you need to provide:
1. Complete dental measurements
2. The actual gender (ground truth)

This data will be added to the training dataset
for future model improvements."""
        
        ttk.Label(self.dialog, text=info_text, wraplength=350, 
                 justify=tk.LEFT).pack(pady=20)
        
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="📝 Enter Data", 
                  command=self.enter_data).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="❌ Cancel", 
                  command=self.dialog.destroy).pack(side=tk.LEFT, padx=10)
                  
    def enter_data(self):
        """Enter training data"""
        messagebox.showinfo("Info", "Training data entry feature would open here.\nFor now, please use the command line interface.")
        self.dialog.destroy()

class RetrainDialog:
    """Dialog for retraining the model"""
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.create_dialog()
        
    def create_dialog(self):
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Retrain Model")
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        ttk.Label(self.dialog, text="Model Retraining", 
                 font=('Arial', 14, 'bold')).pack(pady=20)
        
        ttk.Label(self.dialog, text="Model retraining will start...\nThis may take several minutes.", 
                 justify=tk.CENTER).pack(pady=20)
        
        self.progress = ttk.Progressbar(self.dialog, mode='indeterminate')
        self.progress.pack(pady=20, padx=40, fill=tk.X)
        
        self.progress.start()
        
        # Start retraining in background thread
        threading.Thread(target=self.retrain_worker, daemon=True).start()
        
    def retrain_worker(self):
        """Background worker for retraining"""
        try:
            # Simulate retraining process
            messagebox.showinfo("Info", "Model retraining would start here.\nFor now, please use the command line interface.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Retraining failed: {str(e)}")
        finally:
            self.progress.stop()
            self.dialog.destroy()

class DependencyDialog:
    """Dialog showing dependency information"""
    def __init__(self, parent):
        self.parent = parent
        self.create_dialog()
        
    def create_dialog(self):
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Dependency Check")
        self.dialog.geometry("500x400")
        self.dialog.resizable(True, True)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        ttk.Label(self.dialog, text="Dependency Status", 
                 font=('Arial', 14, 'bold')).pack(pady=(10, 20))
        
        # Create scrolled text widget
        text_frame = ttk.Frame(self.dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD)
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Check dependencies
        self.check_dependencies()
        
        ttk.Button(self.dialog, text="Close", 
                  command=self.dialog.destroy).pack(pady=10)
                  
    def check_dependencies(self):
        """Check and display dependency status"""
        dependencies = [
            'pandas', 'numpy', 'scikit-learn', 'imbalanced-learn',
            'xgboost', 'lightgbm', 'matplotlib', 'seaborn', 'joblib', 'openpyxl'
        ]
        
        self.text_widget.insert(tk.END, "Checking Python packages...\n\n")
        
        for dep in dependencies:
            try:
                __import__(dep.replace('-', '_'))
                self.text_widget.insert(tk.END, f"✅ {dep}: Available\n")
            except ImportError:
                self.text_widget.insert(tk.END, f"❌ {dep}: Missing\n")
        
        self.text_widget.insert(tk.END, "\n" + "="*40 + "\n")
        self.text_widget.insert(tk.END, "Checking model files...\n\n")
        
        model_files = [
            'models/current/model.pkl',
            'models/current/scaler.pkl', 
            'models/current/selector.pkl',
            'models/current/metadata.json'
        ]
        
        for file_path in model_files:
            if os.path.exists(file_path):
                self.text_widget.insert(tk.END, f"✅ {file_path}: Found\n")
            else:
                self.text_widget.insert(tk.END, f"❌ {file_path}: Missing\n")

def main():
    """Main application entry point"""
    # Check if running from correct directory
    if not os.path.exists('src') or not os.path.exists('models'):
        messagebox.showerror(
            "Wrong Directory", 
            "Please run this application from the tooth-gender-classification root directory."
        )
        return
        
    root = tk.Tk()
    app = ToothGenderGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.destroy()

if __name__ == "__main__":
    main()