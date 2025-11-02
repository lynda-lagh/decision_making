@echo off
echo ========================================
echo Setting up Predictive Maintenance Project
echo ========================================
echo.

echo Step 1: Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    echo Please ensure Python 3.9+ is installed
    pause
    exit /b 1
)
echo ✓ Virtual environment created
echo.

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated
echo.

echo Step 3: Upgrading pip...
python -m pip install --upgrade pip
echo ✓ Pip upgraded
echo.

echo Step 4: Installing dependencies...
echo This may take 5-10 minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some packages may have failed to install
    echo You can continue, but some features may not work
)
echo ✓ Dependencies installed
echo.

echo Step 5: Verifying installation...
python -c "import pandas, numpy, sklearn; print('✓ Core packages verified')"
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Keep this terminal open (virtual environment is active)
echo 2. Or activate later with: venv\Scripts\activate
echo 3. Start Jupyter: jupyter notebook
echo 4. Read SETUP_GUIDE.md for more information
echo.
echo Ready to begin Phase 2: Data Strategy!
echo.
pause
