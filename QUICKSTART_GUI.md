# GUI Application Quick Start

## Installation

The GUI application has been successfully created with all dependencies configured. To get started:

### 1. Install/Update Dependencies

```bash
pip install -r requirements.txt
```

**Required packages installed:**
- PyQt5 (GUI framework)
- matplotlib (timeline visualization)
- pandas (data handling)
- requests (API calls)
- python-dotenv (environment variables)
- pyqtgraph (optional, for future enhancements)

### 2. Launch the GUI

**Option A - Launch GUI by default:**
```bash
python -m sapreplayreader
```

**Option B - Launch GUI explicitly:**
```bash
python -m sapreplayreader --gui
```

**Option C - Direct Python execution:**
```bash
python src/sapreplayreader/gui_main.py
```

## First-Time Setup

When you first launch the GUI, follow these steps:

### Step 1: Generate Summary Data
1. Go to the **Data Processing** tab
2. Click **"Generate Summary DB"** button
3. Wait for the operation to complete (this may take a few minutes for large datasets)
4. Monitor progress in the output console

### Step 2: Browse Replays
1. Navigate to the **Replay Summary** tab
2. The summary table will automatically populate with replay data
3. Use filters to find replays of interest:
   - Filter by username, opponent, outcome, game mode, etc.
   - Toggle "Ranked Games Only" for ranked matches
   - Set minimum turns to filter longer games

### Step 3: View Replay Details
1. Select a replay from the table
2. Click **"View Selected Replay"**
3. The app will automatically switch to the **Replay Viewer** tab
4. View detailed game information and action timeline

## GUI Tabs Overview

### Data Processing Tab
Manage replay data and generate analysis files:
- **Update Process DB**: Scan for new replay files and update the database
- **Extract Opponent PIDs**: Extract opponent participation IDs from replays
- **Generate Summary DB**: Create/update the summary.csv file with all replay data
- **Check for Opponent PIDs**: Find and process missing opponent replays

Each operation shows:
- Real-time progress bar
- Console output with detailed status messages
- Error reporting if issues occur

### Replay Summary Tab
Browse and filter replays from summary.csv:
- **Filters**: Username, opponent name, outcome, game mode, ranked status, minimum turns
- **Table**: Displays key replay information (username, outcome, turn count, etc.)
- **Selection**: Click to select a replay and view detailed information
- **Quick Navigation**: Auto-switches to Replay Viewer when you view a replay

### Replay Viewer Tab
Analyze detailed replay information:
- **Left Panel**: Displays replay facts
  - Match and participation IDs
  - Player information (username, rank, pack)
  - Game outcome and mode
  - Version and timestamps
- **Right Panel**: Action timeline
  - Interactive chart showing lives over time
  - Toggle between "Turns" and "Timestamp" view
  - Action summary statistics

## File Structure

```
SAPReplayReader/
├── src/sapreplayreader/
│   ├── gui_main.py              # Main application window
│   ├── gui_data_processing.py   # Data processing tab
│   ├── gui_replay_summary.py    # Replay summary/filter tab
│   ├── gui_replay_viewer.py     # Detailed replay viewer tab
│   ├── reader.py                # Backend replay processing
│   ├── api_calls.py             # API interaction utilities
│   └── __main__.py              # Entry point
├── Replays/                     # JSON replay files
├── summary.csv                  # Generated replay summary (created by GUI)
├── pid_df.csv                   # Process tracking database
├── requirements.txt             # Python dependencies
├── GUI_README.md                # Detailed GUI documentation
└── test_gui.py                  # GUI validation tests
```

## Common Tasks

### Updating with New Replays
1. Add new JSON replay files to the `Replays/` folder
2. Go to **Data Processing** tab
3. Click **"Update Process DB"**
4. Click **"Generate Summary DB"** to regenerate summary

### Filtering for Specific Matches
1. Go to **Replay Summary** tab
2. Enter search criteria in filters:
   - Username: Your player name
   - Opponent: Specific opponent name
   - Outcome: Win/Loss/Draw
3. Filtered results update automatically
4. Click **"Clear Filters"** to reset

### Analyzing a Single Replay
1. Find the replay in the Summary tab
2. Click to select it
3. Click **"View Selected Replay"**
4. View detailed information in the Replay Viewer tab
5. Toggle the timeline between **Turns** and **Time** views

## Troubleshooting

### "summary.csv not found" Error
- Generate the summary first: Go to Data Processing → Generate Summary DB

### GUI Won't Launch
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that PyQt5 and matplotlib are properly installed
- Try running the validation test: `python test_gui.py`

### Slow Performance with Large Datasets
- Use filters in the Summary tab to narrow down replays before viewing
- Only open one replay at a time in the Viewer tab

### Missing Replay Data
1. Ensure replay JSON files are in the `Replays/` folder
2. Run **Update Process DB** from the Data Processing tab
3. Run **Generate Summary DB** to rebuild the summary file

## Advanced Features

### Processing Operations Details

**Update Process DB**: Scans the Replays folder and updates tracking database
- Identifies new replay files
- Marks processed vs unprocessed replays  
- Creates pid_df.csv if it doesn't exist

**Extract Opponent PIDs**: Finds opponent participation IDs
- Extracts from existing replay data
- Identifies replays to download
- Useful for building complete opponent history

**Generate Summary DB**: Creates comprehensive replay analysis
- Processes all replay files
- Extracts key information (winner, turns, players, etc.)
- Creates summary.csv for browsing

**Check for Opponent PIDs**: Validates and processes opponent data
- Reviews summary.csv for opponent references
- Finds missing opponent replay files
- Prepares data for download

## Support & Documentation

- **Detailed GUI Guide**: See [GUI_README.md](GUI_README.md)
- **Data Format**: Check [README.md](README.md) for project overview
- **Validation**: Run `python test_gui.py` to verify installation

## Tips for Best Experience

1. **Generate Summary First**: Always run "Generate Summary DB" after adding new replays
2. **Filter Strategically**: Use filters to narrow down results for easier browsing
3. **Monitor Progress**: Watch the output console during processing for detailed status
4. **Check for Errors**: Review the output area for any warnings or issues
5. **Star Tracking**: The "Min Turns" filter is great for finding long, strategic games

Enjoy analyzing your replays!
