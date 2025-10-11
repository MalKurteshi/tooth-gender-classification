#!/usr/bin/env python3
"""
Tooth Gender Classification - Simple Launcher
A user-friendly launcher that detects the system and starts the appropriate interface

This script provides an easy way for users to launch the application regardless of their
technical expertise or platform.
"""

import os
import sys
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox

def show_launcher_gui():
    """Show a simple GUI launcher if possible"""
    try:
        root = tk.Tk()
        root.title("Tooth Gender Classification - Launcher")
        root.geometry("400x300")
        root.resizable(False, False)
        
        # Center the window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")
        
        # Title
        title_label = tk.Label(root, text="🦷 Tooth Gender Classification", 
                              font=('Arial', 16, 'bold'))
        title_label.pack(pady=20)
        
        # Description
        desc_text = """Welcome to the Tooth Gender Classification application.
Choose how you would like to proceed:"""
        desc_label = tk.Label(root, text=desc_text, justify=tk.CENTER)
        desc_label.pack(pady=10)
        
        # Buttons frame
        button_frame = tk.Frame(root)
        button_frame.pack(pady=30)
        
        def launch_gui():
            root.destroy()
            launch_application("gui")
        
        def launch_cli():
            root.destroy()
            launch_application("cli")
        
        def run_setup():
            root.destroy()
            run_setup_script()
        
        # Main buttons
        tk.Button(button_frame, text="🖥️ Launch GUI Application", 
                 command=launch_gui, width=25, pady=5).pack(pady=5)
        tk.Button(button_frame, text="💻 Launch Command Line", 
                 command=launch_cli, width=25, pady=5).pack(pady=5)
        tk.Button(button_frame, text="⚙️ Run Setup/Install", 
                 command=run_setup, width=25, pady=5).pack(pady=5)
        
        # Status info
        status_text = f"System: {platform.system()} {platform.release()}"
        tk.Label(root, text=status_text, font=('Arial', 9), 
                foreground='gray').pack(side=tk.BOTTOM, pady=10)
        
        root.mainloop()
        
    except Exception as e:
        print(f"GUI launcher failed: {e}")
        show_text_launcher()

def show_text_launcher():
    """Show text-based launcher for systems without GUI"""
    print("=" * 50)
    print("🦷 Tooth Gender Classification - Launcher")
    print("=" * 50)
    print(f"System: {platform.system()} {platform.release()}")
    print()
    
    print("Choose an option:")
    print("1. Launch GUI Application")
    print("2. Launch Command Line Interface")
    print("3. Run Setup/Install Dependencies")
    print("4. Exit")
    print()
    
    try:
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            launch_application("gui")
        elif choice == "2":
            launch_application("cli")
        elif choice == "3":
            run_setup_script()
        elif choice == "4":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")
            show_text_launcher()
            
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)

def check_environment():
    """Check if the environment is properly set up"""
    issues = []
    
    # Check if we're in the right directory
    if not os.path.exists('src'):
        issues.append("Not running from the correct directory (missing 'src' folder)")
    
    if not os.path.exists('models'):
        issues.append("Missing 'models' directory")
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append(f"Python version {sys.version_info[0]}.{sys.version_info[1]} is too old (need 3.8+)")
    
    # Try to import key dependencies
    try:
        import pandas
        import numpy
        import sklearn
    except ImportError as e:
        issues.append(f"Missing required Python packages: {e}")
    
    return issues

def launch_application(app_type="gui"):
    """Launch the specified application type"""
    print(f"\n🚀 Starting {app_type.upper()} application...")
    
    # Check environment first
    issues = check_environment()
    if issues:
        print("❌ Environment issues detected:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nPlease run the setup script first or check the installation.")
        
        # Ask if user wants to run setup
        try:
            response = input("\nWould you like to run the setup script now? (y/n): ").lower()
            if response.startswith('y'):
                run_setup_script()
                return
        except:
            pass
        
        sys.exit(1)
    
    # Determine the script to run
    if app_type == "gui":
        script_path = os.path.join("src", "gui_app.py")
        if not os.path.exists(script_path):
            print("❌ GUI application not found. Please check installation.")
            sys.exit(1)
    else:
        script_path = os.path.join("src", "predict_working.py")
        if not os.path.exists(script_path):
            print("❌ Command line application not found. Please check installation.")
            sys.exit(1)
    
    try:
        # Change to the project directory to ensure proper imports
        project_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_dir)
        
        # Launch the application
        subprocess.run([sys.executable, script_path], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start application (exit code {e.returncode})")
        print("Please check the error messages above.")
    except KeyboardInterrupt:
        print("\n✋ Application interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def run_setup_script():
    """Run the appropriate setup script for the platform"""
    print("\n⚙️ Running setup script...")
    
    system = platform.system().lower()
    
    if system == "windows":
        script_name = "setup_windows.bat"
        if os.path.exists(script_name):
            try:
                subprocess.run([script_name], shell=True, check=True)
            except subprocess.CalledProcessError:
                print("❌ Setup script failed. Please run it manually.")
        else:
            print(f"❌ Setup script '{script_name}' not found.")
    else:
        script_name = "setup_unix.sh"
        if os.path.exists(script_name):
            try:
                # Make sure it's executable
                os.chmod(script_name, 0o755)
                subprocess.run([f"./{script_name}"], shell=True, check=True)
            except subprocess.CalledProcessError:
                print("❌ Setup script failed. Please run it manually.")
        else:
            print(f"❌ Setup script '{script_name}' not found.")

def main():
    """Main launcher entry point"""
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["gui", "g", "--gui"]:
            launch_application("gui")
        elif arg in ["cli", "c", "--cli"]:
            launch_application("cli")
        elif arg in ["setup", "s", "--setup"]:
            run_setup_script()
        else:
            print(f"Unknown argument: {arg}")
            print("Usage: python launch.py [gui|cli|setup]")
            sys.exit(1)
    else:
        # No arguments - show interactive launcher
        try:
            # Try GUI launcher first
            show_launcher_gui()
        except:
            # Fall back to text launcher
            show_text_launcher()

if __name__ == "__main__":
    main()