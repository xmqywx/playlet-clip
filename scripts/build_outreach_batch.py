#!/usr/bin/env python3
"""Build a sales outreach batch from a JSON prospect list."""

from argparse import ArgumentParser
from pathlib import Path

from playlet_clip.reporting.outreach_batch import build_outreach_batch


def main() -> int:
    parser = ArgumentParser(description="Build a Playlet-Clip outreach batch.")
    parser.add_argument("--prospects", required=True, type=Path, help="Prospect JSON file path.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Batch output directory.")
    parser.add_argument("--batch-name", default="Playlet-Clip 今日外联批次", help="Batch title.")
    parser.add_argument("--free-sample-slots", default=3, type=int, help="Free sample slots to offer.")
    parser.add_argument(
        "--package-path",
        default=Path("output/playlet-clip-demo/customer-package"),
        type=Path,
        help="Customer demo package path to reference.",
    )
    args = parser.parse_args()

    batch = build_outreach_batch(
        prospects=args.prospects,
        output_dir=args.output_dir,
        batch_name=args.batch_name,
        free_sample_slots=args.free_sample_slots,
        package_path=args.package_path,
    )
    print(f"Outreach tracker written: {batch.csv_path}")
    print(f"Today batch written: {batch.markdown_path}")
    print(f"Messages written: {len(batch.message_paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
