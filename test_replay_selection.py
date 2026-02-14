#!/usr/bin/env python
"""
Test to verify replay selection and loading works correctly.
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_replay_loading():
    """Test that replay selection and loading works."""
    print("Testing replay selection and loading...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from sapreplayreader.gui_main import SAPReplayReaderGUI
        from sapreplayreader import reader
        
        print("✓ Imports successful")
        
        # Test that a replay file exists
        test_pid = '0007f058-5586-4490-84df-9a94330024dd'
        try:
            replay_data = reader.get_replay(test_pid)
            print(f"✓ Test replay loaded: {test_pid}")
            print(f"  - Loaded {len(replay_data)} keys from JSON")
        except Exception as e:
            print(f"✗ Failed to load test replay: {e}")
            return False
        
        # Create application and window
        app = QApplication([])
        window = SAPReplayReaderGUI()
        print("✓ Main window created")
        
        # Verify tabs exist
        if window.tab_widget.count() != 2:
            print(f"✗ Expected 2 tabs, got {window.tab_widget.count()}")
            return False
        print("✓ Expected 2 tabs present (Summary, Viewer)")
        
        # Test the replay selection callback
        print(f"\nTesting replay selection callback...")
        window.show()
        app.processEvents()
        
        # Simulate replay selection
        print(f"Calling on_replay_selected({test_pid})...")
        window.on_replay_selected(test_pid)
        app.processEvents()
        
        # Check that we switched to the replay viewer tab
        current_tab_idx = window.tab_widget.currentIndex()
        if current_tab_idx != 1:  # Replay Viewer should be tab 1
            print(f"✗ Expected to be on tab 1 (Replay Viewer), but on tab {current_tab_idx}")
            return False
        print("✓ Successfully switched to Replay Viewer tab")
        
        # Verify that replay data was loaded
        if window.replay_viewer_tab.replay_data is None:
            print("✗ Replay data was not loaded")
            return False
        print(f"✓ Replay data loaded in viewer")
        print(f"  - Replay ID: {window.replay_viewer_tab.current_pid}")
        print(f"  - Data keys: {list(window.replay_viewer_tab.replay_data.keys())[:5]}...")
        
        # Check that facts are displayed
        if window.replay_viewer_tab.facts_layout.count() == 0:
            print("✗ No replay facts displayed")
            return False
        print(f"✓ Replay facts displayed ({window.replay_viewer_tab.facts_layout.count()} items)")
        
        print("\n✓ All replay loading tests passed!")
        window.close()
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_replay_loading()
    sys.exit(0 if success else 1)
