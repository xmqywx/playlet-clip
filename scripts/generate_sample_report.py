#!/usr/bin/env python3
"""Generate a customer-facing Markdown sample report."""

import json
from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from playlet_clip.models.task import ProcessResult
from playlet_clip.reporting.sample_report import SampleReportInput, generate_sample_report


def main() -> int:
    parser = ArgumentParser(description="Generate a Playlet-Clip sample report.")
    parser.add_argument("--input-video", required=True, type=Path, help="Original input video path.")
    parser.add_argument("--output-video", required=True, type=Path, help="Generated output video path.")
    parser.add_argument("--subtitles", required=True, type=Path, help="Generated or supplied SRT path.")
    parser.add_argument("--narration-json", required=True, type=Path, help="Generated narration JSON path.")
    parser.add_argument("--duration", required=True, type=float, help="Processing duration in seconds.")
    parser.add_argument("--style", default="默认风格", help="Commercial narration style.")
    parser.add_argument("--title", default="Playlet-Clip 样片交付报告", help="Markdown report title.")
    parser.add_argument("--report-path", required=True, type=Path, help="Report output Markdown path.")
    args = parser.parse_args()

    result = ProcessResult(
        success=True,
        output_path=args.output_video,
        duration=args.duration,
        segments_count=_count_json_items(args.narration_json),
        subtitles_path=args.subtitles,
        narration_json_path=args.narration_json,
    )
    report = generate_sample_report(
        SampleReportInput(
            title=args.title,
            input_video=args.input_video,
            result=result,
            style=args.style,
        )
    )

    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(report, encoding="utf-8")
    print(f"Sample report written: {args.report_path}")
    return 0


def _count_json_items(path: Path) -> int:
    data: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return 0
    return sum(1 for item in data if isinstance(item, dict))


if __name__ == "__main__":
    raise SystemExit(main())
