#!/usr/bin/env python
"""
Test to verify plot_timeline sets Y-axis minimum to 0.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sapreplayreader.gui_replay_viewer import ReplayTimelineVisualization, TimelineChartView
from datetime import datetime, timedelta

def test_plot_y_axis_minimum():
    """Test that plot_timeline sets Y-axis minimum to 0."""
    print("Testing plot_timeline Y-axis minimum setting...\n")
    
    # Create chart view
    chart_view = TimelineChartView()
    
    # Test 1: Buy Pet data (should have minimum 0)
    print("Test 1: Buy Pet Y-axis")
    print("-" * 60)
    x_values = [1, 1, 1, 2, 2, 2, 3, 3, 3]
    y_values = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    
    chart_view.plot_timeline(x_values, y_values, x_label="Turns", y_label="BUY PET Count", title="Buy Pet Count Over Time")
    
    # Check Y-axis limits
    y_min, y_max = chart_view.ax.get_ylim()
    print(f"Y-axis limits: ({y_min}, {y_max})")
    print(f"Y-axis minimum: {y_min}")
    
    if y_min == 0:
        print("✓ Y-axis minimum is 0")
    else:
        print(f"✗ Y-axis minimum should be 0, but got {y_min}")
        return False
    
    print()
    
    # Test 2: Lives data with negative potential
    print("Test 2: Lives Y-axis (non-zero minimum)")
    print("-" * 60)
    x_values = [1, 2, 3, 4, 5]
    y_values = [5, 4, 3, 2, 1]
    
    chart_view.plot_timeline(x_values, y_values, x_label="Turns", y_label="Lives", title="Lives Over Time")
    
    y_min, y_max = chart_view.ax.get_ylim()
    print(f"Y-axis limits: ({y_min}, {y_max})")
    print(f"Y-axis minimum: {y_min}")
    
    if y_min == 0:
        print("✓ Y-axis minimum is 0 (even for negative values)")
    else:
        print(f"✗ Y-axis minimum should be 0, but got {y_min}")
        return False
    
    print()
    
    # Test 3: Turn Time data
    print("Test 3: Turn Time Y-axis")
    print("-" * 60)
    x_values = [1, 2, 3, 4, 5]
    y_values = [24, 25, 27, 35, 30]
    
    chart_view.plot_timeline(x_values, y_values, x_label="Turns", y_label="Turn Time (seconds)", title="Turn Time Over Time")
    
    y_min, y_max = chart_view.ax.get_ylim()
    print(f"Y-axis limits: ({y_min}, {y_max})")
    print(f"Y-axis minimum: {y_min}")
    
    if y_min == 0:
        print("✓ Y-axis minimum is 0")
    else:
        print(f"✗ Y-axis minimum should be 0, but got {y_min}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_plot_y_axis_minimum()
    
    print("\n" + "="*60)
    if success:
        print("✓ All plot Y-axis tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)
