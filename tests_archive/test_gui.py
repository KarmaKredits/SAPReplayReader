#!/usr/bin/env python
"""
Test script to verify GUI application structure and imports.
This script validates that all GUI components are properly configured.
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all GUI modules can be imported."""
    print("Testing imports...")
    try:
        from sapreplayreader import reader
        print("✓ reader module imported")
    except ImportError as e:
        print(f"✗ Failed to import reader: {e}")
        return False
    
    try:
        from sapreplayreader.gui_main import SAPReplayReaderGUI
        print("✓ gui_main module imported")
    except ImportError as e:
        print(f"✗ Failed to import gui_main: {e}")
        return False
    
    try:
        from sapreplayreader.gui_data_processing import DataProcessingTab
        print("✓ gui_data_processing module imported")
    except ImportError as e:
        print(f"✗ Failed to import gui_data_processing: {e}")
        return False
    
    try:
        from sapreplayreader.gui_replay_summary import ReplaySummaryTab
        print("✓ gui_replay_summary module imported")
    except ImportError as e:
        print(f"✗ Failed to import gui_replay_summary: {e}")
        return False
    
    try:
        from sapreplayreader.gui_replay_viewer import ReplayViewerTab, ReplayTimelineVisualization
        print("✓ gui_replay_viewer module imported")
    except ImportError as e:
        print(f"✗ Failed to import gui_replay_viewer: {e}")
        return False
    
    return True

def test_file_structure():
    """Test that required data files exist."""
    print("\nTesting file structure...")
    
    required_dirs = ["Replays", "src/sapreplayreader"]
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"✓ Directory exists: {dir_path}")
        else:
            print(f"✗ Directory missing: {dir_path}")
            return False
    
    required_files = ["summary.csv"]
    for file_path in required_files:
        if os.path.isfile(file_path):
            print(f"✓ File exists: {file_path}")
        else:
            print(f"⚠ Optional file missing: {file_path}")
    
    return True

def test_gui_initialization():
    """Test that GUI components can be instantiated."""
    print("\nTesting GUI component initialization...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from sapreplayreader.gui_data_processing import DataProcessingTab
        from sapreplayreader.gui_replay_summary import ReplaySummaryTab
        from sapreplayreader.gui_replay_viewer import ReplayViewerTab, TimelineChartView
        
        # Create a minimal QApplication for testing
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Test tab creation
        data_tab = DataProcessingTab()
        print("✓ DataProcessingTab instantiated")
        
        summary_tab = ReplaySummaryTab()
        print("✓ ReplaySummaryTab instantiated")
        
        viewer_tab = ReplayViewerTab()
        print("✓ ReplayViewerTab instantiated")
        
        timeline_view = TimelineChartView()
        print("✓ TimelineChartView instantiated")
        
        return True
    except Exception as e:
        print(f"✗ Failed to instantiate GUI components: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("SAP Replay Reader GUI - Validation Tests")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("File Structure", test_file_structure),
        ("GUI Initialization", test_gui_initialization),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
        all_passed = all_passed and result
    
    print("=" * 50)
    if all_passed:
        print("All tests passed! ✓")
        print("You can now run: python -m sapreplayreader --gui")
        return 0
    else:
        print("Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
