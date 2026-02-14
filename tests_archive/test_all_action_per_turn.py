#!/usr/bin/env python
"""
Comprehensive test for per-turn action counts with all action types.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sapreplayreader.gui_replay_viewer import ReplayTimelineVisualization

def test_all_action_types():
    """Test per-turn counts for all action types."""
    print("=" * 70)
    print("COMPREHENSIVE TEST: Per-Turn Action Counts")
    print("=" * 70)
    print()
    
    viz = ReplayTimelineVisualization()
    pid = "0a3a16f1-43e3-4fb7-ba74-e9806a5d9f6b"
    
    if not viz.load_actions(pid):
        print("✗ Failed to load actions")
        return False
    
    # Get available Y-axes
    y_axes = viz.get_available_y_axes()
    print(f"Available Y-axes: {y_axes}\n")
    
    # Test each non-Lives, non-Turn Time axis
    action_axes = [ax for ax in y_axes if ax not in ["Lives", "Turn Time"]]
    
    print(f"Testing per-turn counts for action types: {action_axes}\n")
    
    results = {}
    
    for action_type_label in action_axes:
        x_values, y_values = viz.get_timeline_data(x_axis_mode="turns", y_axis_mode=action_type_label)
        
        # Group by turn and find max value per turn
        turn_max = {}
        for i, action in enumerate(viz.actions):
            turn = action.get("Turn", 0)
            y_val = y_values[i]
            
            if turn not in turn_max:
                turn_max[turn] = y_val
            else:
                turn_max[turn] = max(turn_max[turn], y_val)
        
        # Count actions per turn
        action_per_turn = {}
        for action in viz.actions:
            if action.get("Action Type").upper() == action_type_label.upper():
                turn = action.get("Turn", 0)
                action_per_turn[turn] = action_per_turn.get(turn, 0) + 1
        
        # Verify all turns with this action type have matching counts
        all_match = True
        for turn in sorted(action_per_turn.keys()):
            expected_max = action_per_turn[turn]
            actual_max = turn_max[turn]
            if expected_max != actual_max:
                all_match = False
                break
        
        results[action_type_label] = all_match
        status = "✓" if all_match else "✗"
        print(f"{status} {action_type_label:15s}: Per-turn max values match action counts")
    
    print()
    print("=" * 70)
    
    if all(results.values()):
        print("✓ All action types have correct per-turn counts")
        print("  - Counts reset at start of each turn")
        print("  - Max value matches number of actions in that turn")
        return True
    else:
        print("✗ Some action types have incorrect per-turn counts")
        for action_type, match in results.items():
            if not match:
                print(f"  - {action_type}: FAILED")
        return False

if __name__ == "__main__":
    success = test_all_action_types()
    sys.exit(0 if success else 1)
