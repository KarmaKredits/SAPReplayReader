#!/usr/bin/env python
"""
Simple test to verify GUI displays and captures any initialization errors.
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_gui_display():
    """Test that GUI creates and displays properly."""
    print("Testing GUI display...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from sapreplayreader.gui_main import SAPReplayReaderGUI
        
        print("✓ Imports successful")
        
        # Create application
        app = QApplication([])
        print("✓ QApplication created")
        
        # Create main window
        try:
            window = SAPReplayReaderGUI()
            print("✓ Main window created")
        except Exception as e:
            print(f"✗ Error creating main window: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Check that components exist
        if not hasattr(window, 'tab_widget'):
            print("✗ tab_widget not found")
            return False
        print("✓ tab_widget found")
        
        if not hasattr(window, 'data_processing_tab'):
            print("⏭ data_processing_tab removed (intentional)")
        
        if not hasattr(window, 'replay_summary_tab'):
            print("✗ replay_summary_tab not found")
            return False
        print("✓ replay_summary_tab found")
        
        if not hasattr(window, 'replay_viewer_tab'):
            print("✗ replay_viewer_tab not found")
            return False
        print("✓ replay_viewer_tab found")
        
        # Check window properties
        print(f"✓ Window size: {window.geometry()}")
        print(f"✓ Window title: {window.windowTitle()}")
        print(f"✓ Tab count: {window.tab_widget.count()} (2 tabs: Summary, Viewer)")
        
        # Show window to test rendering
        print("Attempting to show window...")
        window.show()
        print("✓ Window shown")
        
        # Process events to let widgets render
        app.processEvents()
        print("✓ Events processed")
        
        print("\n✓ GUI display test passed!")
        
        # Close the window
        window.close()
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gui_display()
    sys.exit(0 if success else 1)
