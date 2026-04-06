@echo off
echo ========================================
echo Running DEEN Commerce BI Auto Bug-Fixer
echo ========================================

echo.
echo [1/3] Automatically formatting code with Ruff...
ruff format .

echo.
echo [2/3] Automatically fixing linting warnings and unused imports with Ruff...
ruff check --fix --unsafe-fixes .

echo.
echo [3/3] Running tests to ensure core logic integrity...
python -m unittest discover -s tests -p "test_*.py"

echo.
echo ========================================
echo Auto Bug-Fixing Complete!
echo ========================================
pause
