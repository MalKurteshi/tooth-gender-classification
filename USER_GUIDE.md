# Tooth Gender Classification - User Guide

🦷 **A Desktop Application for Gender Classification Based on Dental Measurements**

## Table of Contents
- [Quick Start](#quick-start)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Using the Application](#using-the-application)
- [Troubleshooting](#troubleshooting)
- [Frequently Asked Questions](#frequently-asked-questions)
- [Support](#support)

## Quick Start

### For Beginners (Recommended)
1. **Download** the setup script for your operating system
2. **Double-click** to run the automatic installer
3. **Launch** the desktop application
4. **Enter** dental measurements and get predictions

### For Advanced Users
- Use the standalone executable files directly
- Run from command line for batch processing
- Integrate with existing workflows

## System Requirements

### Minimum Requirements
- **Operating System:** Windows 10, macOS 10.14, or Ubuntu 18.04 (or newer)
- **RAM:** 4 GB minimum, 8 GB recommended
- **Storage:** 1 GB free disk space
- **Display:** 1024x768 resolution minimum

### Recommended Requirements
- **Operating System:** Windows 11, macOS 12+, or Ubuntu 20.04+
- **RAM:** 8 GB or more
- **Storage:** 2 GB free disk space
- **Display:** 1920x1080 resolution or higher

## Installation

### 🪟 Windows Installation

#### Method 1: Automatic Setup (Recommended)
1. Download `setup_windows.bat`
2. Right-click and select "Run as administrator"
3. Follow the on-screen instructions
4. The application will be installed automatically

#### Method 2: Manual Installation
1. Ensure Python 3.8+ is installed from [python.org](https://www.python.org/downloads/)
2. Download the project files
3. Double-click `setup_windows.bat`

### 🍎 macOS Installation

#### Method 1: Automatic Setup (Recommended)
1. Download `setup_unix.sh`
2. Open Terminal and navigate to the download folder
3. Run: `chmod +x setup_unix.sh && ./setup_unix.sh`
4. Follow the on-screen instructions

#### Method 2: Using Homebrew (Advanced)
```bash
# Install Python if not already installed
brew install python

# Run the setup script
./setup_unix.sh
```

### 🐧 Linux Installation

#### Ubuntu/Debian
```bash
# Install Python and dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Run setup script
chmod +x setup_unix.sh
./setup_unix.sh
```

#### CentOS/RHEL/Fedora
```bash
# Install Python and dependencies
sudo yum install python3 python3-pip  # CentOS/RHEL
sudo dnf install python3 python3-pip  # Fedora

# Run setup script
chmod +x setup_unix.sh
./setup_unix.sh
```

## Using the Application

### 🖥️ Desktop GUI Application

#### Getting Started
1. **Launch the application**
   - Windows: Double-click the desktop shortcut or find it in Start Menu
   - macOS: Look in Applications folder or Launchpad
   - Linux: Find in your application menu or run `tooth-gender-gui`

2. **Main Interface**
   - The application opens with a tabbed interface
   - Three main tabs: Prediction, Add Data, Settings

#### Making Predictions

1. **Go to the "Prediction" tab**
2. **Enter dental measurements**
   - Fill in as many measurements as possible (in millimeters)
   - At least 11 measurements are required for accurate results
   - Leave empty fields blank - the system will handle missing data

3. **Click "Predict Gender"**
   - Results appear in the bottom panel
   - Shows predicted gender and confidence level

#### Understanding Results

**Prediction Results:**
- **Gender:** Male or Female
- **Confidence:** Percentage (0-100%)

**Confidence Levels:**
- **90%+:** Very High - Highly reliable
- **80-89%:** High - Reliable for most purposes  
- **70-79%:** Moderate - Generally reliable
- **60-69%:** Low - Use with caution
- **<60%:** Very Low - May not be reliable

#### Input Methods

1. **Manual Entry**
   - Type measurements directly into fields
   - Use decimal points (e.g., 7.5, 8.2)
   - Both comma (7,5) and period (7.5) are accepted

2. **Load from CSV File**
   - Click "Load from CSV" button
   - Select a CSV file with measurement data
   - First row of data will be loaded automatically

3. **Clear All Fields**
   - Click "Clear All" to reset all inputs

### 📊 Adding Training Data

1. **Go to the "Add Data" tab**
2. **Click "Add New Training Data"**
3. **Enter measurements and actual gender**
4. **Data is saved for future model improvements**

*Note: This feature helps improve the model over time with new data*

### ⚙️ Settings and Information

1. **Go to the "Settings" tab**
2. **View system information**
   - Operating system details
   - Python version
   - Dependency status

3. **Available actions:**
   - **Check Dependencies:** Verify all required packages
   - **View Model Info:** See model performance statistics
   - **Generate Report:** Create analysis report

### 💻 Command Line Interface

For advanced users who prefer command line:

```bash
# Windows
python src\predict_working.py

# macOS/Linux  
python src/predict_working.py
```

**Command Line Features:**
- Interactive measurement entry
- Batch processing of multiple cases
- CSV file import/export
- Model retraining capabilities

## Troubleshooting

### Common Issues

#### "Dependencies Missing" Error
**Problem:** Required Python packages are not installed
**Solution:**
1. Re-run the setup script
2. Check internet connection during installation
3. Try running: `pip install pandas numpy scikit-learn`

#### "Model Files Not Found" Error
**Problem:** AI model files are missing
**Solution:**
1. Ensure you have the complete project folder
2. Check that `models/current/` directory contains `.pkl` files
3. You may need to train the model first

#### Application Won't Start
**Problem:** Application crashes or won't open
**Solution:**
1. Check system requirements
2. Try running from command line to see error messages
3. Re-run the setup script
4. On Windows, try "Run as administrator"

#### Prediction Takes Too Long
**Problem:** Slow prediction performance
**Solution:**
1. Check available RAM (close other applications)
2. Ensure SSD storage if possible
3. Update to latest version

### Platform-Specific Issues

#### Windows
- **Python not found:** Install from [python.org](https://www.python.org/downloads/) and check "Add to PATH"
- **Permission errors:** Run as administrator
- **Antivirus blocking:** Add application to antivirus whitelist

#### macOS
- **"App can't be opened" error:** Right-click app and select "Open"
- **Python version issues:** Use Homebrew: `brew install python`
- **Gatekeeper warnings:** Go to System Preferences > Security & Privacy

#### Linux
- **Missing tkinter:** Install with `sudo apt install python3-tk`
- **Permission issues:** Check file permissions with `ls -la`
- **Display issues:** Ensure X11 forwarding if using SSH

## Frequently Asked Questions

### General Questions

**Q: Is this application free to use?**
A: Yes, this is open-source software available for free.

**Q: Do I need internet connection to use the application?**
A: No, once installed, the application works completely offline.

**Q: How accurate are the predictions?**
A: Accuracy varies based on the quality and completeness of measurements. The confidence score indicates reliability.

### Technical Questions

**Q: What dental measurements are used?**
A: The system uses 21 different dental measurements including mesiodistal widths, buccolingual dimensions, and intercanine width.

**Q: Can I use this for clinical diagnosis?**
A: This tool is for research and educational purposes only. It should not replace professional medical assessment.

**Q: How is my data handled?**
A: All processing happens locally on your computer. No data is sent to external servers.

### Usage Questions

**Q: What if I don't have all measurements?**
A: The system can work with partial data, but needs at least 11 measurements for reliable results.

**Q: Can I process multiple cases at once?**
A: Yes, use the command line interface for batch processing or CSV import.

**Q: How do I update the application?**
A: Download the latest version and run the setup script again.

## Support

### Getting Help

1. **Check this user guide** for common solutions
2. **Run the dependency check** in the Settings tab
3. **Check system requirements** are met
4. **Look for error messages** in command line output

### Documentation

- **User Guide:** This document
- **Technical Documentation:** See `README.md` for developers
- **Code Documentation:** See source code comments

### Reporting Issues

If you encounter problems:

1. **Collect information:**
   - Operating system and version
   - Python version
   - Error messages (copy exact text)
   - Steps to reproduce the problem

2. **Check known issues** in project documentation

3. **Contact support** with detailed information

### Performance Tips

**For Better Performance:**
- Close unnecessary applications
- Ensure adequate free RAM (4GB+)
- Use SSD storage when possible
- Keep system updated

**For Large Datasets:**
- Use command line interface for batch processing
- Consider processing in smaller chunks
- Monitor system resources

---

## Quick Reference Card

### Essential Shortcuts
- **Start GUI:** Double-click application icon
- **Start CLI:** Run `python src/predict_working.py`
- **Clear inputs:** Click "Clear All" button
- **Load CSV:** Click "Load from CSV" button

### Minimum Input Requirements
- **At least 11 measurements** for reliable prediction
- **Decimal format:** Use periods (.) for decimals
- **Units:** All measurements in millimeters (mm)

### File Locations
- **Windows:** `C:\Program Files\ToothGenderClassification\`
- **macOS:** `/Applications/ToothGenderClassification.app`
- **Linux:** `~/.local/share/ToothGenderClassification/`

---

*This guide covers the basic usage of the Tooth Gender Classification application. For technical details and development information, see the README.md file.*