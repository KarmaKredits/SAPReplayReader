#!/usr/bin/env python
"""
Test script to verify the updated turn time computation with proper timestamp parsing.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sapreplayreader.gui_replay_viewer import ReplayTimelineVisualization
from sapreplayreader import reader
from datetime import datetime

def test_turn_time_from_replay():
    """Test turn time computation from actual replay data."""
    print("Testing Turn Time computation from actual replay...\n")
    
    viz = ReplayTimelineVisualization()
    pid = "0a3a16f1-43e3-4fb7-ba74-e9806a5d9f6b"
    
    # Load actions from the replay
    if not viz.load_actions(pid):
        print("Failed to load actions")
        return False
    
    print(f"Loaded {len(viz.actions)} actions\n")
    
    # Get turn time data
    x_values, y_values = viz.get_timeline_data(x_axis_mode="turns", y_axis_mode="turn time")
    
    print("Turn Time Data (Y-axis values):")
    print("-" * 60)
    
    # Group by turn and show turn time
    turn_times = {}
    for x, y in zip(x_values, y_values):
        if x not in turn_times:
            turn_times[x] = y
    
    for turn_num in sorted(turn_times.keys())[:15]:  # Show first 15 turns
        duration = turn_times[turn_num]
        print(f"Turn {turn_num:2d}: {duration:6.1f} seconds")
    
    # Verify no 0-second turns
    zero_turn_count = sum(1 for duration in turn_times.values() if duration == 0)
    if zero_turn_count > 0:
        print(f"\n⚠ WARNING: {zero_turn_count} turns have 0 seconds duration")
        return False
    else:
        print(f"\n✓ All {len(turn_times)} turns have non-zero duration")
    
    # Check that Turn Time is in available Y-axes
    y_axes = viz.get_available_y_axes()
    if "Turn Time" in y_axes:
        print("✓ 'Turn Time' is available in Y-axis options")
    else:
        print("✗ 'Turn Time' should be available in Y-axis options")
        return False
    
    # Verify Start Turn and Game Mode are not in Y-axes
    excluded = ["Start Turn", "Game Mode", "START TURN", "GAME MODE"]
    found_excluded = [name for name in excluded if name in y_axes]
    if found_excluded:
        print(f"✗ These should not be in Y-axes: {found_excluded}")
        return False
    else:
        print("✓ 'Start Turn' and 'Game Mode' are correctly excluded")
    
    return True

if __name__ == "__main__":
    success = test_turn_time_from_replay()
    sys.exit(0 if success else 1)
