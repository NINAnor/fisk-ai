"""Detection window widget."""
import io
import os
import sys
from contextlib import redirect_stdout
from pathlib import Path
from typing import Dict, List, Tuple

import cv2
import torch
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app import settings
from app.data_manager.data_manager import DataManager
from app.detection import detection
from app.detection.batch_yolov8 import BatchYolov8
from app.report_manager.report_manager import ReportManager
from app.video_processor import Detection, video_processor

# TODO: test all these file types
ALLOWED_EXTENSIONS = (".mp4", ".m4a", ".avi", ".mkv", ".mov", ".wmv")


class DetectionWorker(QThread):
    """Detection worker thread."""

    update_progress = pyqtSignal(int)
    add_log = pyqtSignal(str)
    input_folder_path: Path
    output_folder_path: Path
    model: BatchYolov8 | None

    def __init__(self, folder_path: Path, output_folder_path: Path) -> None:
        super().__init__()

        self.input_folder_path = folder_path
        self.output_folder_path = output_folder_path
        self.model = None

    def run(self) -> None:
        """Run the detection."""

        if self.model is None:
            self.log("Initializing the model...")
            self.model = BatchYolov8(
                Path(r"data/models/v8s-640-binary.pt"),
                "cuda:0",
            )
        stream_target = io.StringIO()
        with redirect_stdout(stream_target):
            self.process_folder()
        # self.log(stream_target.getvalue())

    def log(self, text: str) -> None:
        """Log text to the console."""
        self.add_log.emit(text)

    def process_folder(self) -> None:
        """Process a folder of videos."""
        if self.input_folder_path is None:
            return

        with DataManager() as data_manager:
            report_manager = ReportManager(
                self.output_folder_path,
                data_manager,
            )

            try:
                report_manager.check_can_write_report()
            except PermissionError:
                self.log("Please close the report file.")
                return

            videos = [
                filename
                for filename in os.listdir(self.input_folder_path)
                if filename.lower().endswith(ALLOWED_EXTENSIONS)
            ]

            if len(videos) == 0:
                self.log("No videos found in the input folder")
                return

            for i, video in enumerate(videos):
                self.log(f"Processing {i + 1}/{len(videos)} ({video})")
                video_path = self.input_folder_path / video
                self.process_video(video_path, data_manager)
                data_manager.add_video_data(video_path, video, self.output_folder_path)

                # Delete the original video if the user has selected to do so
                if not settings.keep_original:
                    video_path.unlink()

            if settings.get_report:
                try:
                    report_manager.write_report(videos)
                except PermissionError:
                    self.log("Could not write report. Please close the report file.")

    def tensors_to_predictions(
        self, tensors: List[torch.Tensor]
    ) -> Dict[int, List[Detection]]:
        """Convert the tensors to a dictionary of frame number to detections."""
        detections: Dict[int, List[Detection]] = {}
        for frame, tensor in enumerate(tensors):
            # annotator.text((32, 32), text, txt_color=(0, 255, 255))
            detections[frame] = []
            for pred in tensor:
                bndbox = pred["bndbox"]
                detections[frame].append(
                    Detection(
                        label=str(pred["name"]),
                        confidence=float(pred["conf"]),
                        xmin=int(bndbox["xmin"]),
                        ymin=int(bndbox["ymin"]),
                        xmax=int(bndbox["xmax"]),
                        ymax=int(bndbox["ymax"]),
                    )
                )
        return detections

    def __add_buffer_to_ranges(
        self, frame_ranges: List[Tuple[int, int]], video_path: Path
    ) -> List[Tuple[int, int]]:
        """Add buffer time before and after each frame range and merge overlapping ranges"""

        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Add buffer time to each frame range
        frame_ranges_with_buffer = [
            (
                max(0, start_frame - int(fps * settings.buffer_before)),
                min(video_length, end_frame + int(fps * settings.buffer_after)),
            )
            for (start_frame, end_frame) in frame_ranges
        ]

        # Merge overlapping frame ranges
        merged_ranges: List[Tuple[int, int]] = []
        for start_frame, end_frame in frame_ranges_with_buffer:
            if not merged_ranges or start_frame > merged_ranges[-1][1]:
                merged_ranges.append((start_frame, end_frame))
            else:
                merged_ranges[-1] = (
                    merged_ranges[-1][0],
                    max(merged_ranges[-1][1], end_frame),
                )

        return merged_ranges

    def process_video(self, video_path: Path, data_manager: DataManager) -> None:
        """
        Process a video and save the processed video to the same folder as the original video.
        """
        if self.model is None or self.output_folder_path is None:
            return

        # self.add_text.emit(f"Processing {video_path}")

        # Update threshold
        self.model.conf_thres = settings.prediction_threshold / 100

        frames_with_fish, tensors = detection.process_video(
            model=self.model,
            video_path=video_path,
            batch_size=settings.batch_size,
            max_batches_to_queue=4,
            output_path=None,
            notify_progress=lambda progress: self.update_progress.emit(int(progress)),
        )

        print(f"Found {len(frames_with_fish)} frames with fish")

        self.add_log.emit(f"Found {len(frames_with_fish)} frames with fish")

        # Convert the detected frames to frame ranges to cut the video
        frame_ranges = detection.detected_frames_to_ranges(
            frames_with_fish, frame_buffer=31
        )
        print(f"Found {len(frame_ranges)} frame ranges with fish")
        self.add_log.emit(f"Found {len(frame_ranges)} frame ranges with fish")

        frame_ranges = self.__add_buffer_to_ranges(frame_ranges, video_path)

        if len(frame_ranges) == 0:
            print("No fish detected, skipping video")
            return

        vid_path = Path(video_path)
        out_path = self.output_folder_path / f"{vid_path.stem}_processed.mp4"

        dets = None
        if settings.box_around_fish:
            dets = self.tensors_to_predictions(tensors)

        # Cut the video to the detected frames
        video_processor.cut_video(video_path, out_path, frame_ranges, dets)
        self.log(f"Saved processed video to {out_path}")

        self.update_progress.emit(100)
        data_manager.add_detection_data(video_path, frame_ranges)


class DetectionWindow(QDialog):  # pylint: disable=too-few-public-methods
    """Detection window widget."""

    def __init__(
        self,
        input_folder_path: Path,
        output_folder_path: Path,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.dialog_layout = QVBoxLayout()

        # Add the main output textbox.
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setSizeAdjustPolicy(
            QPlainTextEdit.SizeAdjustPolicy.AdjustToContents
        )
        self.dialog_layout.addWidget(self.output)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.setMinimumSize(600, 300)

        # Add the progress bar.
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.dialog_layout.addWidget(self.progress_bar)

        self.setLayout(self.dialog_layout)

        self.worker = DetectionWorker(input_folder_path, output_folder_path)
        self.worker.update_progress.connect(self.progress_bar.setValue)
        self.worker.add_log.connect(self.output.appendPlainText)
        self.worker.finished.connect(self.worker_finished)
        self.worker.start()

        # Stop worker when window is closed
        self.finished.connect(self.worker.terminate)

        self.close_button = QPushButton("Close")
        self.close_button.hide()

        # This is needed because self.close returns a bool
        def on_close() -> None:
            self.close()

        self.close_button.clicked.connect(on_close)
        self.dialog_layout.addWidget(self.close_button)

        self.open_output_dir_button = QPushButton("Open output directory")
        self.open_output_dir_button.hide()

        def on_open_output_dir() -> None:
            if sys.platform == "win32":
                os.startfile(str(output_folder_path))  # pylint: disable=no-member
            elif sys.platform == "linux":
                os.system(f"xdg-open '{output_folder_path}'")
            else:
                raise OSError("Unsupported operating system")

        self.open_output_dir_button.clicked.connect(on_open_output_dir)

        self.dialog_layout.addWidget(self.open_output_dir_button)

    def worker_finished(self) -> None:
        """Called when the worker has finished."""
        # Show button to close window now that the worker has finished
        self.close_button.show()
        self.open_output_dir_button.show()
