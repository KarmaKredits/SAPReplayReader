#!/usr/bin/env python
"""
Test script to verify Turn Time computation from timestamps.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sapreplayreader.gui_replay_viewer import ReplayTimelineVisualization
from datetime import datetime, timedelta

def test_turn_time_computation():
    """Test that Turn Time is correctly computed from Start Turn and End Turn timestamps."""
    print("Testing Turn Time computation...")
    
    # Create a mock visualization with test data
    viz = ReplayTimelineVisualization()
    
    # Simulate actions with timestamps for Turn Time calculation
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
            "Time": (base_time + timedelta(seconds=4)).isoformat(),
            "Lives": 6,
            "BuildCount": 2,
            "Amount": None
        },
        {
            "Action Type": "BUY FOOD",
            "Turn": 1,
            "Time": (base_time + timedelta(seconds=5)).isoformat(),
            "Lives": 6,
            "BuildCount": 3,
            "Amount": 3  # Buy Food action with amount
        },
        {
            "Action Type": "END TURN",
            "Turn": 1,
            "Time": (base_time + timedelta(seconds=11)).isoformat(),
            "Lives": 6,
            "BuildCount": 6
        },
        {
            "Action Type": "START TURN",
            "Turn": 2,
            "Time": (base_time + timedelta(seconds=13)).isoformat(),
            "Lives": 5,
            "BuildCount": 7
        },
        {
            "Action Type": "END TURN",
            "Turn": 2,
            "Time": (base_time + timedelta(seconds=27)).isoformat(),
            "Lives": 5,
            "BuildCount": 10
        }
    ]
    
    viz.actions = mock_actions
    
    # Test Turn Time Y-axis computation
    x_values, y_values = viz.get_timeline_data(x_axis_mode="turns", y_axis_mode="turn time")
    
    print(f"Actions count: {len(x_values)}")
    print(f"X values (Turn numbers): {x_values}")
    print(f"Y values (Turn Time in seconds):")
    for i, (x, y) in enumerate(zip(x_values, y_values)):
        print(f"  Action {i}: Turn {x} -> {y} seconds")
    
    # Verify Turn Times are computed correctly
    # Turn 1: 11 seconds (from base_time to base_time + 11s)
    # Turn 2: 14 seconds (from base_time + 13s to base_time + 27s)
    
    # Check Turn 1 actions (indices 0-3)
    if y_values[3] == 11:  # END TURN action for Turn 1
        print("✓ Turn 1 time correctly computed: 11 seconds")
    else:
        print(f"✗ Turn 1 time incorrect: expected 11, got {y_values[3]}")
    
    # Check Turn 2 actions (indices 4-5)
    if y_values[5] == 14:  # END TURN action for Turn 2
        print("✓ Turn 2 time correctly computed: 14 seconds")
    else:
        print(f"✗ Turn 2 time incorrect: expected 14, got {y_values[5]}")
    
    # Verify excluded patterns
    y_axes = viz.get_available_y_axes()
    print(f"\nAvailable Y-axes: {y_axes}")
    
    if "Start Turn" not in y_axes and "Game Mode" not in y_axes:
        print("✓ 'Start Turn' and 'Game Mode' are correctly excluded from Y-axis options")
    else:
        print("✗ 'Start Turn' or 'Game Mode' should not appear as Y-axis options")
    
    if "Turn Time" in y_axes:
        print("✓ 'Turn Time' is available as a Y-axis option")
    else:
        print("✗ 'Turn Time' should be available as a Y-axis option")

if __name__ == "__main__":
    test_turn_time_computation()
