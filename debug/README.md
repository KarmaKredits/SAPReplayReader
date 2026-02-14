# Debug Files

This directory contains debug scripts used for debugging and troubleshooting during development.

## Contents

### Debug Scripts
- `debug_buy_food_request.py` - Debug script for Buy Food request processing
- `debug_turn_time.py` - Debug script for turn time computation

## Usage

To run a debug script:
```powershell
cd debug
python debug_turn_time.py
```

Or from the root directory:
```powershell
python debug/debug_turn_time.py
```

## Purpose

These scripts were created to:
- Inspect actual replay data structures
- Validate timestamp parsing
- Verify action extraction logic
- Debug computation algorithms

## Notes

- These are temporary debugging aids, not part of the production system
- Useful for development and future troubleshooting
- Can be deleted if no longer needed

## Related Documentation

- [IMPLEMENTATION_SUMMARY.md](../IMPLEMENTATION_SUMMARY.md) - Implementation details
- [PROJECT_STATUS.md](../PROJECT_STATUS.md) - Project completion status
