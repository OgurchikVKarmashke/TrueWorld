@echo off
chcp 65001 > nul
echo ==================================================
echo            STARTING TRUEWORLD
echo ==================================================
echo.
python -c "import colorama" >nul 2>nul || python -m pip install colorama --user
python main_loop.py
pause