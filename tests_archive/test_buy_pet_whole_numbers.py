#!/usr/bin/env python
"""
Test to verify Buy Pet Y-axis shows only whole numbers and minimum is 0.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sapreplayreader.gui_replay_viewer import ReplayTimelineVisualization
from datetime import datetime, timedelta

def test_buy_pet_whole_numbers():
    """Test Buy Pet Y-axis returns only integers."""
    print("Testing Buy Pet Y-axis for whole numbers...\n")
    
    viz = ReplayTimelineVisualization()
    
    # Create mock actions
    base_time = datetime.fromisoformat("2025-10-26T06:57:39.625806+00:00")
    
    mock_actions = [
        {
            "Action Type": "START TURN",
            "Turn": 1,
            "Time": base_time.isoformat(),
            "Lives": 6,
            "BuildCount": 1
        },
        {
            "Action Type": "BUY PET",
            "Turn": 1,
            "Time": (base_time + timedelta(seconds=1)).isoformat(),
            "Lives": 6,
            "BuildCount": 2
        },
        {
            "Action Type": "ROLL",
            "Turn": 1,
            "Time": (base_time + timedelta(seconds=2)).isoformat(),
            "Lives": 6,
            "BuildCount": 3
        },
        {
            "Action Type": "BUY PET",
            "Turn": 1,
            "Time": (base_time + timedelta(seconds=3)).isoformat(),
            "Lives": 6,
            "BuildCount": 4
        },
        {
            "Action Type": "END TURN",
            "Turn": 1,
            "Time": (base_time + timedelta(seconds=4)).isoformat(),
            "Lives": 6,
            "BuildCount": 5
        }
    ]
    
    viz.actions = mock_actions
    
    # Get Buy Pet Y-axis data
    x_values, y_values = viz.get_timeline_data(x_axis_mode="turns", y_axis_mode="buy pet")
    
    print(f"Action sequence and Buy Pet Y-values:")
    print("-" * 60)
    for i, action in enumerate(mock_actions):
        y_val = y_values[i]
        is_int = isinstance(y_val, int) or (isinstance(y_val, float) and y_val.is_integer())
        action_type = action["Action Type"]
        print(f"Action {i}: {action_type:15s} -> Y={y_val:6.1f} (int: {is_int})")
    
    print()
    
    # Verify all values are integers
    all_integers = all(isinstance(y, int) or (isinstance(y, float) and y.is_integer()) for y in y_values)
    
    if all_integers:
        print("✓ All Buy Pet Y-values are whole numbers (integers)")
    else:
        print("✗ Some Buy Pet Y-values have decimal portions")
        return False
    
    # Verify minimum value is 0
    min_y = min(y_values)
    if min_y == 0:
        print("✓ Minimum Y-value is 0")
    else:
        print(f"✗ Minimum Y-value should be 0, but got {min_y}")
        return False
    
    # Verify sequence starts at 0
    if y_values[0] == 0:
        print("✓ First Y-value is 0 (starting point)")
    else:
        print(f"✗ First Y-value should be 0, but got {y_values[0]}")
        return False
    
    return True

def test_buy_pet_with_replay():
    """Test Buy Pet with actual replay data."""
    print("\n" + "="*60)
    print("Testing Buy Pet Y-axis with actual replay data...\n")
    
    viz = ReplayTimelineVisualization()
    pid = "0a3a16f1-43e3-4fb7-ba74-e9806a5d9f6b"
    
    if not viz.load_actions(pid):
        print("Failed to load actions")
        return False
    
    x_values, y_values = viz.get_timeline_data(x_axis_mode="turns", y_axis_mode="buy pet")
    
    # Filter to Buy Pet Y-values only
    buy_pet_y_values = [y_values[i] for i, action in enumerate(viz.actions) if action.get("Action Type") == "BUY PET"]
    
    print(f"Buy Pet Y-axis values from {len(buy_pet_y_values)} Buy Pet actions:")
    print(f"{buy_pet_y_values[:15]}")  # Show first 15
    print()
    
    # Check that all are integers
    all_integers = all(isinstance(y, int) or (isinstance(y, float) and y.is_integer()) for y in buy_pet_y_values)
    
    if all_integers:
        print(f"✓ All {len(buy_pet_y_values)} Buy Pet Y-values are whole numbers")
    else:
        print(f"✗ Some Buy Pet Y-values have decimals")
        return False
    
    # Check minimum is 0
    all_y_values = y_values
    if min(all_y_values) == 0:
        print("✓ Minimum Y-value across all actions is 0")
    else:
        print(f"✗ Minimum Y-value should be 0, but got {min(all_y_values)}")
        return False
    
    return True

if __name__ == "__main__":
    test1_pass = test_buy_pet_whole_numbers()
    test2_pass = test_buy_pet_with_replay()
    
    print("\n" + "="*60)
    if test1_pass and test2_pass:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)
