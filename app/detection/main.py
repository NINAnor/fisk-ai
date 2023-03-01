"""Main module for detection."""
import argparse
import sys
from pathlib import Path

from .detection import process_video
from .batch_yolov8 import BatchYolov8


def main() -> int:
    """The main function.

    Returns:
        int: The exit code
    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--video_path",
        type=str,
        required=True,
        help="The path to the video to process",
    )
    parser.add_argument(
        "--weights_path",
        type=str,
        required=True,
        help="The path to the weights to use",
    )

    parser.add_argument(
        "--device",
        type=str,
        required=False,
        default="cuda:0",
        help="The device to use. Defaults to cuda:0",
    )

    parser.add_argument(
        "--batch_size",
        type=int,
        required=False,
        default=32,
        help="The batch size to use. Defaults to 32",
    )

    parser.add_argument(
        "--max_batches_to_queue",
        type=int,
        required=False,
        default=4,
        help="Max number of batches to queue. Defaults to 4",
    )

    parser.add_argument(
        "--output_path",
        type=str,
        required=False,
        default=None,
        help="Output video path.",
    )

    args = parser.parse_args()

    try:
        model = BatchYolov8(Path(args.weights_path), args.device)
    except RuntimeError as err:
        print("Failed to initialize detector", err)
        return 1

    frames_with_fish = process_video(
        model,
        Path(args.video_path),
        args.batch_size,
        args.max_batches_to_queue,
        Path(args.output_path) if args.output_path is not None else None,
    )

    print(f"Found {len(frames_with_fish)} frames with fish")

    return 0


if __name__ == "__main__":
    sys.exit(main())
