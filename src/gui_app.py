#!/usr/bin/env python3
"""
Tooth Gender Classification - Desktop GUI Application
Cross-platform desktop interface for non-technical users

Supports: Windows, macOS, Linux
Requirements: Python 3.11–3.13 with tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import sys
import platform
import logging
import queue
import threading
from pathlib import Path

try:
    from .app_paths import resource_path, user_dir, configure_logging
    from .schema import FEATURES, MIN_MEASUREMENTS, APP_VERSION
    from .reporting import generate_report
except ImportError:
    from app_paths import resource_path, user_dir, configure_logging
    from schema import FEATURES, MIN_MEASUREMENTS, APP_VERSION
    from reporting import generate_report


class ToothGenderGUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.check_dependencies()
        self.create_widgets()

    def setup_window(self):
        """Setup the main window"""
        self.root.title(f"Tooth Gender Classification {APP_VERSION}")
        self.root.geometry("900x760")
        self.root.minsize(700, 600)
        self.root.resizable(True, True)

        # Set window icon (if available)
        try:
            if platform.system() == "Windows":
                self.root.iconbitmap(str(resource_path("assets", "tooth_icon.ico")))
            else:
                # For macOS and Linux
                icon_path = resource_path("assets", "tooth_icon.png")
                if os.path.exists(icon_path):
                    self.window_icon = tk.PhotoImage(file=icon_path)
                    self.root.iconphoto(True, self.window_icon)
        except (tk.TclError, OSError):
            logging.debug("Optional application icon unavailable", exc_info=True)

        # Configure style
        self.style = ttk.Style()
        theme = {"Darwin": "aqua", "Windows": "vista"}.get(platform.system(), "clam")
        if theme in self.style.theme_names():
            self.style.theme_use(theme)

    def setup_variables(self):
        """Setup tkinter variables"""
        self.feature_vars = {}
        self.features = FEATURES

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
            if __package__:
                from . import predict as backend
            else:
                import predict as backend
            self.validate_measurements = backend.validate_measurements
            self.predictor = backend.WorkingToothGenderPredictor()
            self.dependencies_ok = True
        except Exception as exc:
            logging.exception("Model initialization failed")
            self.show_error(
                "Application could not load", f"{exc}\nLog: {user_dir() / 'application.log'}"
            )

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
        title_label = ttk.Label(
            main_frame, text="🦷 Tooth Gender Classification", font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)

        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, padx=(0, 5))
        status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            foreground="green" if self.dependencies_ok else "red",
        )
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

        ttk.Label(results_frame, text="Predicted Gender:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        result_label = ttk.Label(
            results_frame,
            textvariable=self.result_var,
            font=("Arial", 12, "bold"),
            foreground="blue",
        )
        result_label.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(results_frame, text="Confidence:").grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10)
        )
        confidence_label = ttk.Label(
            results_frame,
            textvariable=self.confidence_var,
            font=("Arial", 12, "bold"),
            foreground="green",
        )
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
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Arrange canvas and scrollbar
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        pred_frame.columnconfigure(0, weight=1)
        pred_frame.rowconfigure(0, weight=1)

        # Add input fields
        ttk.Label(
            scrollable_frame,
            text=f"Enter the {len(FEATURES)} v1 parameters (at least {MIN_MEASUREMENTS} required).\nKeep the two indices on the same scale as your workbook.",
            font=("Arial", 11, "bold"),
            wraplength=620,
        ).grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky=tk.W)

        # Keep long workbook labels readable, including the new index/dimension fields.
        for i, feature in enumerate(self.features):
            row = i + 1
            col = 0

            ttk.Label(scrollable_frame, text=f"{feature}:").grid(
                row=row, column=col, sticky=tk.W, padx=(0, 5), pady=2
            )

            entry = ttk.Entry(scrollable_frame, textvariable=self.feature_vars[feature], width=12)
            entry.grid(row=row, column=col + 1, padx=(0, 20), pady=2, sticky=tk.W)

        # Buttons frame
        button_frame = ttk.Frame(pred_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky=tk.W)

        ttk.Button(button_frame, text="🎯 Predict Gender", command=self.make_prediction).pack(
            side=tk.LEFT, padx=(0, 10)
        )
        ttk.Button(button_frame, text="🔄 Clear All", command=self.clear_inputs).pack(
            side=tk.LEFT, padx=(0, 10)
        )
        ttk.Button(button_frame, text="📁 Load from CSV", command=self.load_from_csv).pack(
            side=tk.LEFT
        )

        # Mouse wheel scrolling
        def on_mousewheel(event):
            delta = event.delta if platform.system() == "Darwin" else event.delta / 120
            if delta:
                canvas.yview_scroll(
                    -int(delta) if abs(delta) >= 1 else (-1 if delta > 0 else 1), "units"
                )

        canvas.bind_all("<MouseWheel>", on_mousewheel)  # Windows
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))  # Linux

    def create_data_entry_tab(self, parent):
        """Create the data entry tab"""
        data_frame = ttk.Frame(parent, padding="10")
        parent.add(data_frame, text="Training Data")

        ttk.Label(data_frame, text="Training Data", font=("Arial", 14, "bold")).pack(pady=(0, 20))

        info_text = """This feature allows you to add new dental measurements to the training dataset.
After entering measurements and the actual gender, the data will be saved for future model improvements."""

        ttk.Label(data_frame, text=info_text, wraplength=600, justify=tk.LEFT).pack(pady=(0, 20))

        ttk.Button(
            data_frame, text="📝 Add New Training Data", command=self.add_training_data
        ).pack(pady=10)

        ttk.Button(
            data_frame, text="Import Excel and Retrain", command=self.import_training_excel
        ).pack(pady=10)
        ttk.Button(
            data_frame, text="Save Excel Template", command=self.save_training_template
        ).pack(pady=5)

        ttk.Button(data_frame, text="🔄 Retrain Model", command=self.retrain_model).pack(pady=10)

    def create_settings_tab(self, parent):
        """Create the settings tab"""
        settings_frame = ttk.Frame(parent, padding="10")
        parent.add(settings_frame, text="⚙️ Settings")

        ttk.Label(settings_frame, text="Application Settings", font=("Arial", 14, "bold")).pack(
            pady=(0, 20)
        )

        # System information
        info_frame = ttk.LabelFrame(settings_frame, text="System Information", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 20))

        system_info = f"""Operating System: {platform.system()} {platform.release()}
Python Version: {sys.version.split()[0]}
Platform: {platform.platform()}
Dependencies: {"✅ Available" if self.dependencies_ok else "❌ Missing"}"""

        ttk.Label(info_frame, text=system_info, justify=tk.LEFT).pack(anchor=tk.W)

        # Action buttons
        ttk.Button(
            settings_frame, text="🔧 Check Dependencies", command=self.check_dependencies_detailed
        ).pack(pady=5)
        ttk.Button(settings_frame, text="📋 View Model Info", command=self.show_model_info).pack(
            pady=5
        )
        ttk.Button(settings_frame, text="📊 Generate Report", command=self.generate_report).pack(
            pady=5
        )

    def make_prediction(self):
        """Make a gender prediction"""
        if not self.dependencies_ok:
            self.show_error(
                "Dependencies Missing",
                "The application could not load its model. See the startup error and application log.",
            )
            return

        try:
            measurements = self.validate_measurements(
                {f: v.get() for f, v in self.feature_vars.items()}
            )
            self.status_var.set("Making prediction...")
            self.root.update()

            # Make prediction using the backend
            result = self.predict_using_backend(measurements)

            if result:
                self.result_var.set(result["prediction"])
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
        return self.predictor.predict_gender(measurements)

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
                title="Select CSV file", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )

            if file_path:
                import pandas as pd

                df = pd.read_csv(file_path)
                df.columns = df.columns.str.strip()

                # Load first row of data
                if len(df) > 0:
                    self.clear_inputs()
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
            self.show_error(
                "Dependencies Missing",
                "The application could not load its model. See the startup error and application log.",
            )
            return

        response = messagebox.askyesno(
            "Retrain Model",
            "This will retrain the model with the current dataset. This may take a few minutes. Continue?",
        )

        if response:
            RetrainDialog(self.root, self)

    def import_training_excel(self):
        if not self.dependencies_ok:
            self.show_error(
                "Model unavailable", "The model could not load. See the application log."
            )
            return
        path = filedialog.askopenfilename(
            title="Select training data", filetypes=[("Excel workbook", "*.xlsx")]
        )
        if not path:
            return
        if messagebox.askyesno(
            "Import Excel and Retrain",
            "Use this workbook as the training dataset? After successful training, "
            "the new model will be used for predictions, including after reopening the app. "
            "Your previous dataset and model will be kept.",
        ):
            RetrainDialog(self.root, self, excel_path=Path(path))

    def save_training_template(self):
        path = filedialog.asksaveasfilename(
            title="Save training template",
            defaultextension=".xlsx",
            filetypes=[("Excel workbook", "*.xlsx")],
        )
        if path:
            try:
                self.predictor.export_training_template(path)
                messagebox.showinfo(
                    "Template saved",
                    f"Enter all {len(FEATURES)} v1 parameters and Gjinia labels: 0/F/Female or 1/M/Male. "
                    "Include at least four samples of each class.",
                )
            except Exception as exc:
                self.show_error("Could not save template", str(exc))

    def check_dependencies_detailed(self):
        """Show detailed dependency information"""
        DependencyDialog(self.root)

    def show_model_info(self):
        """Show model information"""
        try:
            metadata = self.predictor.metadata
            if metadata:
                info = f"""Model Information:

Model Type: {metadata.get("model_name", "N/A")}
Schema: {metadata.get("schema_version", "N/A")}
Training Samples: {metadata.get("samples", "N/A")}
Trained At: {metadata.get("trained_at", "N/A")}
Cross-validation Accuracy: {metadata["cv_accuracy"]:.1%}
Input Parameters: {len(metadata.get("feature_names", []))}

No independent test accuracy is available.

Target Classes: {", ".join(metadata.get("target_classes", []))}
"""
                messagebox.showinfo("Model Information", info)
            else:
                messagebox.showerror("Error", "Model metadata not found.")

        except Exception as e:
            messagebox.showerror("Error", f"Could not load model information: {str(e)}")

    def generate_report(self):
        try:
            path = filedialog.asksaveasfilename(
                title="Save model report",
                defaultextension=".html",
                filetypes=[("HTML report", "*.html")],
            )
            if not path:
                return
            generate_report(self.predictor, Path(path))
            self.status_var.set("Report saved")
            messagebox.showinfo("Report saved", str(path))
        except Exception as exc:
            logging.exception("Report generation failed")
            self.show_error("Report generation failed", str(exc))

    def show_detailed_results(self, result):
        """Show detailed prediction results"""
        details = f"""Prediction Results:

Predicted Gender: {result["prediction"]}
Confidence: {result["confidence"]:.1f}%

Probability Breakdown:
• Female: {result["probabilities"]["Female"]:.1f}%
• Male: {result["probabilities"]["Male"]:.1f}%

Confidence Level: {self.get_confidence_level(result["confidence"])}
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
        logging.error("%s: %s", title, message)
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

        ttk.Label(self.dialog, text="Add New Training Data", font=("Arial", 14, "bold")).pack(
            pady=20
        )

        info_text = """To add training data, you need to provide:
1. Complete dental measurements in the Prediction tab
2. The actual gender (ground truth)

This data will be added to the training dataset
for future model improvements."""

        ttk.Label(self.dialog, text=info_text, wraplength=350, justify=tk.LEFT).pack(pady=20)

        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="📝 Enter Data", command=self.enter_data).pack(
            side=tk.LEFT, padx=10
        )
        ttk.Button(button_frame, text="❌ Cancel", command=self.dialog.destroy).pack(
            side=tk.LEFT, padx=10
        )

    def enter_data(self):
        from tkinter import simpledialog

        try:
            values = self.main_app.validate_measurements(
                {f: v.get() for f, v in self.main_app.feature_vars.items()}, complete=True
            )
            gender = simpledialog.askstring(
                "Actual gender", "Enter F for Female or M for Male", parent=self.dialog
            )
            if gender is None:
                return
            if gender.strip().upper() not in ("F", "M"):
                raise ValueError("Enter F or M.")
            count = self.main_app.predictor.add_training_sample(
                values, int(gender.strip().upper() == "M")
            )
            messagebox.showinfo(
                "Data saved",
                f"Dataset now contains {count} samples. Retrain to use the new sample.",
                parent=self.dialog,
            )
            self.dialog.destroy()
        except Exception as exc:
            logging.exception("Data entry failed")
            messagebox.showerror("Could not save data", str(exc), parent=self.dialog)


class RetrainDialog:
    """Run computation in a worker; all Tk calls stay on the UI thread."""

    def __init__(self, parent, main_app, excel_path=None):
        self.main_app = main_app
        self.excel_path = excel_path
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Retraining model")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        ttk.Label(self.dialog, text="Training and validating the model. Please wait...").pack(
            padx=30, pady=20
        )
        self.progress = ttk.Progressbar(self.dialog, mode="indeterminate")
        self.progress.pack(padx=30, pady=20, fill=tk.X)
        self.progress.start()
        self.results = queue.Queue()
        threading.Thread(target=self.retrain_worker, daemon=True).start()
        self.dialog.after(100, self.poll)

    def retrain_worker(self):
        try:
            predictor = self.main_app.predictor
            metadata = (
                predictor.import_and_retrain(self.excel_path)
                if self.excel_path
                else predictor.retrain()
            )
            self.results.put((True, metadata))
        except Exception as exc:
            logging.exception("Retraining failed")
            self.results.put((False, str(exc)))

    def poll(self):
        try:
            success, result = self.results.get_nowait()
        except queue.Empty:
            self.dialog.after(100, self.poll)
            return
        self.progress.stop()
        self.dialog.destroy()
        if success:
            self.main_app.result_var.set("")
            self.main_app.confidence_var.set("")
            self.main_app.status_var.set("New model active and saved for future sessions")
            messagebox.showinfo(
                "Model saved",
                f"The new model is now active for predictions.\nTraining samples: {result['samples']}\nCross-validation accuracy: {result['cv_accuracy']:.1%}",
            )
        else:
            self.main_app.show_error("Retraining failed", result)


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

        ttk.Label(self.dialog, text="Dependency Status", font=("Arial", 14, "bold")).pack(
            pady=(10, 20)
        )

        # Create scrolled text widget
        text_frame = ttk.Frame(self.dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD)
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        # Check dependencies
        self.check_dependencies()

        ttk.Button(self.dialog, text="Close", command=self.dialog.destroy).pack(pady=10)

    def check_dependencies(self):
        """Check and display dependency status"""
        dependencies = ["pandas", "numpy", "sklearn", "imblearn", "joblib", "openpyxl"]

        self.text_widget.insert(tk.END, "Checking Python packages...\n\n")

        for dep in dependencies:
            try:
                __import__(dep.replace("-", "_"))
                self.text_widget.insert(tk.END, f"✅ {dep}: Available\n")
            except ImportError:
                self.text_widget.insert(tk.END, f"❌ {dep}: Missing\n")

        self.text_widget.insert(tk.END, "\n" + "=" * 40 + "\n")
        self.text_widget.insert(tk.END, "Checking model files...\n\n")

        model_files = [str(resource_path("models", "current", "pipeline.joblib"))]

        for file_path in model_files:
            if os.path.exists(file_path):
                self.text_widget.insert(tk.END, f"✅ {file_path}: Found\n")
            else:
                self.text_widget.insert(tk.END, f"❌ {file_path}: Missing\n")


def main():
    root = None
    try:
        log_path = configure_logging()
        root = tk.Tk()

        def callback_error(exc_type, exc, traceback):
            logging.error("UI action failed", exc_info=(exc_type, exc, traceback))
            messagebox.showerror("Application error", f"{exc}\nLog: {log_path}", parent=root)

        root.report_callback_exception = callback_error
        root.app = ToothGenderGUI(root)
        root.mainloop()
        return 0
    except Exception as exc:
        logging.exception("Startup failed")
        messagebox.showerror("Startup failed", f"{exc}\nApplication data: {user_dir()}")
        return 1
    finally:
        if root is not None:
            try:
                root.destroy()
            except tk.TclError:
                pass


if __name__ == "__main__":
    sys.exit(main())
