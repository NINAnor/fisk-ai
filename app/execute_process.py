"""Progress bar when loading AI models."""
import re
import typing

from PyQt6.QtCore import QProcess
from PyQt6.QtWidgets import QDialog, QPlainTextEdit, QProgressBar, QVBoxLayout

from .common import Common

# A regular expression, to extract the % complete.
progress_re = re.compile(r"Total complete: (\d+)%")


class ProgressWindow(QDialog):
    """Progress window.

    Args:
        QDialog (QDialog): Inherits QDialog.
    """

    def __init__(self) -> None:
        """Initiates the Progress Window Dialog."""

        super().__init__()

        # Set default window settings
        self.dialog_layout = QVBoxLayout()
        self.setWindowTitle("Processing...")

        # Text box
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.dialog_layout.addWidget(self.text)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.dialog_layout.addWidget(self.progress)

        self.setLayout(self.dialog_layout)

        self.start_process()

    def message(self, message: str) -> None:
        """Print a message to the text box."""
        self.text.appendPlainText(message)

    def start_process(self) -> None:
        """Start the process."""

        # Start the process if it is not already running.
        if Common.process is None:
            self.message("Starting process...")
            Common.process = QProcess()

            # Connect the process signals to the appropriate slots.
            Common.process.readyReadStandardOutput.connect(self.handle_stdout)
            Common.process.readyReadStandardError.connect(self.handle_stderr)
            Common.process.stateChanged.connect(self.handle_state)
            Common.process.finished.connect(self.process_finished)

            # Start the process.
            Common.process.start("python", [Common.process_path])

    def handle_stderr(self) -> None:
        """Gets the errors and progress from the process and prints them to the text box."""
        if Common.process is not None:
            data = Common.process.readAllStandardError()
            stderr = data.data().decode("utf8")
            # Extract progress if it is in the data.
            progress = simple_percent_parser(stderr)

            # Update the progress bar.
            if progress:
                self.progress.setValue(progress)
            self.message(stderr)

    def handle_stdout(self) -> None:
        """Prints out the standard output from the process to the text box."""
        if Common.process is not None:
            data = Common.process.readAllStandardOutput()
            stdout = data.data().decode("utf8")
            self.message(stdout)

    def handle_state(self, state: typing.Any) -> None:
        """Handles the state of the process. Prints the state to the text box.

        Args:
            state (Any): The state of the process.
        """
        states = {
            QProcess.ProcessState.NotRunning: "Not running",
            QProcess.ProcessState.Starting: "Starting",
            QProcess.ProcessState.Running: "Running",
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")

    def process_finished(self) -> None:
        """Print out finsihed message and reset the process."""
        self.message("Process finished.")
        Common.process = None


def simple_percent_parser(output: typing.Any) -> int | None:
    """
    Matches lines using the progress_re regex,
    returning a single integer for the % progress.
    """

    # Search for the progress.
    match = progress_re.search(output)
    if match:
        pc_complete = match.group(1)
        return int(pc_complete)
    return None
