"""
Main GUI Application for SAP Replay Reader.
This module provides the main window and tab management interface.
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTabWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from sapreplayreader.gui_replay_summary import ReplaySummaryTab
from sapreplayreader.gui_replay_viewer import ReplayViewerTab


class SAPReplayReaderGUI(QMainWindow):
    """Main application window for SAP Replay Reader."""

    def __init__(self):
        super().__init__()
        self.selected_replay_pid = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("SAP Replay Reader")
        self.setGeometry(100, 100, 1400, 900)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create the main layout (vertical)
        layout = QVBoxLayout()

        # Create tab widget
        self.tab_widget = QTabWidget()

        # Create tabs
        self.replay_summary_tab = ReplaySummaryTab(self.on_replay_selected)
        self.replay_viewer_tab = ReplayViewerTab()

        # Add tabs to tab widget
        self.tab_widget.addTab(self.replay_summary_tab, "Replay Summary")
        self.tab_widget.addTab(self.replay_viewer_tab, "Replay Viewer")

        # Add tab widget
        layout.addWidget(self.tab_widget)

        central_widget.setLayout(layout)

        # Apply stylesheet
        self.apply_stylesheet()

    def apply_stylesheet(self):
        """Apply application-wide stylesheet."""
        stylesheet = """
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                color: #333333;
                padding: 5px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #000000;
            }
        """
        self.setStyleSheet(stylesheet)

    def on_replay_selected(self, pid: str):
        """Handle replay selection from summary tab."""
        self.selected_replay_pid = pid
        self.replay_viewer_tab.load_replay(pid)
        self.tab_widget.setCurrentWidget(self.replay_viewer_tab)


def main():
    """Entry point for the GUI application."""
    app = QApplication(sys.argv)
    window = SAPReplayReaderGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
