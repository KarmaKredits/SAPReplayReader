# Data Files

This directory contains test and reference data files used during development and testing.

## Contents

### CSV Files (Test Data)
- `action_test.csv` - Test dataset for action processing
- `pid_df.csv` - Replay ID dataframe
- `summary.csv` - Summary statistics
- `summary copy.csv` - Summary statistics backup

### Text Files
- `pids_full.txt` - List of replay IDs

## Purpose

These files contain:
- Test data for validating data processing
- Reference datasets for debugging
- Summary statistics from replay data
- Lists of replay IDs for testing

## Usage

To use these files in your scripts:
```python
import pandas as pd

# Read CSV data
df = pd.read_csv('data/action_test.csv')

# Read text file
with open('data/pids_full.txt', 'r') as f:
    pids = f.read().splitlines()
```

## Notes

- These are informal data files created during development
- Use with caution - may contain incomplete or outdated data
- For actual replay data, see [Replays/](../Replays/) directory
- Test CSV files may not represent final replay data format

## Related Documentation

- [README.md](../README.md) - Main project README
- [IMPLEMENTATION_SUMMARY.md](../IMPLEMENTATION_SUMMARY.md) - Data processing details
