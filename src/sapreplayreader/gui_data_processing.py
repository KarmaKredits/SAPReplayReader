"""
Data Processing Tab for SAP Replay Reader GUI.
Allows execution of functions from reader.py with progress tracking and output display.
"""

import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QProgressBar, QLabel, QScrollArea, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer
from PyQt5.QtGui import QFont

from sapreplayreader import reader


class ProcessingThread(QObject):
    """Worker thread for background processing."""
    
    finished = pyqtSignal()
    error = pyqtSignal(str)
    output = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, operation, *args):
        super().__init__()
        self.operation = operation
        self.args = args
    
    def run(self):
        """Run the processing operation."""
        try:
            self.output.emit(f"Starting: {self.operation}...\n")
            
            if self.operation == "Update Process DB":
                file_names = reader.read_replay_filenames()
                self.output.emit(f"Found {len(file_names)} replay files.\n")
                reader.update_process_db(file_names)
                self.output.emit("Process DB updated successfully!\n")
                
            elif self.operation == "Extract Opponent PIDs":
                self.output.emit("Extracting opponent PIDs...\n")
                new_pids = reader.extract_pids()
                self.output.emit(f"Extracted {len(new_pids)} new opponent PIDs.\n")
                reader.add_to_pid_df(new_pids)
                self.output.emit("Added new PIDs to process database.\n")
                
            elif self.operation == "Generate Summary DB":
                self.output.emit("Reading all replay files...\n")
                files = reader.read_replay_filenames()
                total_files = len(files)
                self.output.emit(f"Found {total_files} files. Generating summary...\n")
                
                summary_df = reader.get_summary(files[0])
                for idx, file in enumerate(files[1:], 1):
                    if idx % 10 == 0:
                        progress_pct = int((idx / total_files) * 100)
                        self.progress.emit(progress_pct)
                        self.output.emit(f"Processing {file} ({idx}/{total_files})...\n")
                    summary_df = __import__('pandas').concat([summary_df, reader.get_summary(file)], ignore_index=True)
                
                summary_df.to_csv('summary.csv', index=False)
                self.output.emit(f"Summary DB generated with {len(summary_df)} entries!\n")
                self.progress.emit(100)
                
            elif self.operation == "Check for Opponent PIDs":
                self.output.emit("Checking summary for opponent PIDs...\n")
                reader.check_summary_for_opp_pids()
                self.output.emit("Opponent PIDs check completed!\n")
                
            else:
                self.error.emit(f"Unknown operation: {self.operation}")
                self.finished.emit()
                return
            
            self.output.emit("\nOperation completed successfully!\n")
            self.progress.emit(100)
            
        except Exception as e:
            self.error.emit(f"Error during processing: {str(e)}")
        
        self.finished.emit()


class DataProcessingTab(QWidget):
    """Tab for data processing operations."""
    
    def __init__(self):
        super().__init__()
        self.thread = None
        self.worker = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI for the data processing tab."""
        layout = QHBoxLayout()
        
        # Left side: Buttons
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Processing Operations:"))
        left_layout.setSpacing(10)
        
        operations = [
            "Update Process DB",
            "Extract Opponent PIDs",
            "Generate Summary DB",
            "Check for Opponent PIDs"
        ]
        
        for operation in operations:
            btn = QPushButton(operation)
            btn.clicked.connect(lambda checked, op=operation: self.execute_operation(op))
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #1f618d;
                }
            """)
            left_layout.addWidget(btn)
        
        left_layout.addStretch()
        left_panel = QWidget()
        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(180)
        
        # Right side: Output and Progress
        right_layout = QVBoxLayout()
        
        # Output text area
        output_label = QLabel("Processing Output:")
        output_label.setFont(QFont("Courier", 10))
        right_layout.addWidget(output_label)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
                padding: 5px;
                font-family: Courier;
                font-size: 9pt;
            }
        """)
        right_layout.addWidget(self.output_text)
        
        # Progress bar
        progress_label = QLabel("Progress:")
        right_layout.addWidget(progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
            }
        """)
        right_layout.addWidget(self.progress_bar)
        
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        layout.addWidget(left_panel)
        layout.addLayout(right_layout, 1)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.setLayout(layout)
    
    def execute_operation(self, operation):
        """Execute a processing operation."""
        if self.worker is not None and self.thread.isRunning():
            QMessageBox.warning(self, "Operation in Progress", "Another operation is already running.")
            return
        
        self.output_text.clear()
        self.progress_bar.setValue(0)
        
        # Create and start worker thread
        self.worker = ProcessingThread(operation)
        self.thread = threading.Thread(target=self.worker.run)
        self.thread.daemon = True
        
        self.worker.output.connect(self.append_output)
        self.worker.error.connect(self.show_error)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_operation_finished)
        
        self.thread.start()
    
    def append_output(self, text):
        """Append text to output area."""
        self.output_text.append(text.rstrip())
        # Auto-scroll to bottom
        self.output_text.verticalScrollBar().setValue(
            self.output_text.verticalScrollBar().maximum()
        )
    
    def update_progress(self, value):
        """Update progress bar."""
        self.progress_bar.setValue(value)
    
    def show_error(self, error_msg):
        """Show error message."""
        self.output_text.append(f"ERROR: {error_msg}")
        QMessageBox.critical(self, "Error", error_msg)
    
    def on_operation_finished(self):
        """Called when operation completes."""
        self.output_text.append("\n" + "="*50 + "\nOperation finished!\n")
