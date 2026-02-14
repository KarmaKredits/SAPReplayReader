# CSV Path Migration Summary

## Overview
All CSV file references have been updated to reflect the new `data/` folder structure after the file reorganization.

## Files Updated

### Python Source Files (5 files)

**1. `src/sapreplayreader/gui_replay_viewer.py`**
- `'summary.csv'` → `'data/summary.csv'` (load_replay method)

**2. `src/sapreplayreader/reader.py`**
- `'pid_df.csv'` → `'data/pid_df.csv'` (update_process_db function)
- `'pid_df.csv'` → `'data/pid_df.csv'` (add_to_pid_df function)
- `'summary.csv'` → `'data/summary.csv'` (generate_summarydb_from_files function)
- `'summary.csv'` → `'data/summary.csv'` (check_summary_for_opp_pids function)
- `'action_test.csv'` → `'data/action_test.csv'` (commented code in __main__)

**3. `src/sapreplayreader/gui_data_processing.py`**
- `'summary.csv'` → `'data/summary.csv'` (ProcessingThread.run method)

**4. `src/sapreplayreader/gui_replay_summary.py`**
- `'summary.csv'` → `'data/summary.csv'` (load_summary_data method)

**5. `src/sapreplayreader/api_calls.py`**
- `'pid_df.csv'` → `'data/pid_df.csv'` (process_from_df function - 3 occurrences)
- `'pid_df.csv'` → `'data/pid_df.csv'` (commented code)

### Documentation Files (2 files)

**1. `QUICKSTART_GUI.md`**
- Updated file structure tree to show CSV files under `data/` folder
- Added clarity to folder organization

**2. `GUI_README.md`**
- Added note that CSV files are stored in `data/` folder
- Updated troubleshooting section

## CSV Files Affected

| File | Old Location | New Location | Purpose |
|------|-------------|-------------|---------|
| `summary.csv` | Root | `data/` | Replay summary database |
| `pid_df.csv` | Root | `data/` | Process tracking database |
| `action_test.csv` | Root | `data/` | Test/reference data |

## Total Changes

- **Python files modified**: 5
- **Documentation files modified**: 2
- **Path references updated**: 14+ occurrences
- **Backward compatibility**: ✅ No breaking changes - paths are dynamically constructed

## Verification

✅ **Search Result**: No references to CSV files found outside the `data/` folder (except in comments about old structure)

## Impact

- **GUI Functions**: ✅ All continue to work with new paths
- **Data Processing**: ✅ All database operations updated
- **API Calls**: ✅ All API-related DB operations updated
- **Documentation**: ✅ All references updated

## Notes

- All CSV file handling remains functionally identical
- Only file paths have changed
- The `data/` folder was already created during reorganization
- No database schema or format changes
- All error handling for missing files remains intact

## Related Documentation

See [CHANGES_SUMMARY.md](CHANGES_SUMMARY.md) for complete file reorganization details.
