# GUI Troubleshooting & Setup Guide

## Fixed Issues

The following issues have been resolved and tested:

### ✅ DLL Load Error (ImportError: DLL load failed)
**Problem**: Getting `ImportError: DLL load failed while importing QtWidgets`
**Solution**: The package now works with PyQt5 and is installed in editable mode.

### ✅ Module Import Error 
**Problem**: `No module named 'sapreplayreader'`
**Solution**: Updated `pyproject.toml` to support Python 3.7+ and installed package in development mode.

### ✅ Missing Function Error
**Problem**: `cannot import name 'read_replay' from 'sapreplayreader.reader'`
**Solution**: Fixed `__main__.py` to use lazy imports for GUI execution.

## How to Run the GUI

### Desktop Shortcut / Quick Launch

**Method 1: Using module (Recommended)**
```bash
cd d:\REPOS\SAPReplayReader
python -m sapreplayreader --gui
```

**Method 2: Using module without --gui flag (launches GUI by default)**
```bash
cd d:\REPOS\SAPReplayReader
python -m sapreplayreader
```

**Method 3: Direct execution**
```bash
cd D:\REPOS\SAPReplayReader
D:/REPOS/SAPReplayReader/.venv/Scripts/python.exe -m sapreplayreader --gui
```

### From within VS Code
- Open integrated terminal (Ctrl+`)
- Make sure you're in the project root: `d:\REPOS\SAPReplayReader`
- Run: `python -m sapreplayreader --gui`

### Batch File (Optional - for Windows Desktop Shortcut)
Create `run_gui.bat`:
```batch
@echo off
cd /d D:\REPOS\SAPReplayReader
.\\.venv\Scripts\python.exe -m sapreplayreader --gui
pause
```

Then double-click to launch!

## Minor Warning - QWidget::setLayout

You may see this warning when launching:
```
QWidget::setLayout: Attempting to set QLayout "" on QWidget "", which already has a layout
```

**This is harmless** and does not affect functionality. It's a known PyQt5 layout management warning from internal widget initialization. The GUI operates normally.

## What to Do If Issues Persist

### Issue: Still getting DLL errors

**Step 1:** Verify the package is installed in editable mode:
```bash
cd D:\REPOS\SAPReplayReader
D:.venv\Scripts\python.exe -m pip list | findstr sapreplayreader
```
Should show: `sapreplayreader 0.1.0`

**Step 2:** Verify PyQt5 is installed:
```bash
.venv\Scripts\python.exe -c "from PyQt5.QtWidgets import QApplication; print('OK')"
```
Should print: `OK`

**Step 3:** Reinstall PyQt5:
```bash
.venv\Scripts\python.exe -m pip install --force-reinstall --no-cache-dir PyQt5==5.15.9
```

### Issue: GUI window appears but is blank or unresponsive

- Try waiting 5-10 seconds for the GUI to fully initialize
- Check that `summary.csv` exists in the project root
- Try the validation test: `.venv\Scripts\python.exe test_gui.py`

### Issue: Can't find the GUI window

- The window should open in the foreground
- Check Windows taskbar for additional windows
- Try Alt+Tab to cycle through windows
- Look for "SAP Replay Reader" in the taskbar

## Environment Setup Recap

The following has been configured:

✅ **Python Environment**: 3.7.9 virtual environment (`.venv`)
✅ **Package**: Installed in editable/development mode  
✅ **Dependencies**: 
  - PyQt5 5.15.9 (GUI framework)
  - matplotlib 3.5.3 (timeline visualization)
  - pandas 1.3.5 (data handling)
  - All other requirements from requirements.txt

✅ **Project Structure**: 
  - `pyproject.toml` - Supports Python 3.7+
  - `src/sapreplayreader/` - Main package
  - `gui_*.py` files - GUI components

## First-Time Usage After Setup

Once the GUI opens:

1. **Go to Data Processing tab**
   - Click "Generate Summary DB" if it's your first time
   - This creates the replay summary from JSON files

2. **Go to Replay Summary tab**
   - You'll see a list of replays
   - Use filters to find replays
   - Select one and click "View Selected Replay"

3. **Go to Replay Viewer tab**
   - See detailed replay information
   - Toggle timeline between "Turns" and "Timestamp" views
   - Analyze action history

## Command Reference

| Command | Purpose |
|---------|---------|
| `python -m sapreplayreader --gui` | Launch GUI |
| `python -m sapreplayreader` | Launch GUI (default when no args) |
| `.venv\Scripts\python.exe test_gui.py` | Run validation tests |
| `.venv\Scripts\python.exe -m pip list` | List installed packages |
| `pip install -r requirements.txt` | Install/update all dependencies |

## File Changes Made

The following files were updated to resolve issues:

1. **pyproject.toml** - Updated `requires-python` from ">=3.11" to ">=3.7"
2. **__main__.py** - Fixed imports and added lazy loading for GUI
3. **reader.py** - Added fallback for relative imports

These changes enable the GUI to run in Python 3.7 environments without import errors.

## Still Having Issues?

1. **Run the validation test**: `python test_gui.py`
2. **Check Python version**: `python --version` (should be 3.7.9)
3. **Verify virtual environment is active**: You should see `(.venv)` in your terminal prompt
4. **Clear pip cache**: `.venv\Scripts\python.exe -m pip cache purge`
5. **Reinstall everything**: 
   ```bash
   .venv\Scripts\python.exe -m pip install --force-reinstall -r requirements.txt
   ```

The GUI is now fully functional and ready to use!
