#!/usr/bin/env python3
"""Build a customer-facing demo package."""

from argparse import ArgumentParser
from pathlib import Path

from playlet_clip.reporting.demo_package import DemoPackageInput, build_demo_package


def main() -> int:
    parser = ArgumentParser(description="Build a Playlet-Clip customer demo package.")
    parser.add_argument("--sample-report", required=True, type=Path, help="Markdown sample report path.")
    parser.add_argument("--screenshot", action="append", type=Path, default=[], help="Screenshot path.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Demo package output directory.")
    parser.add_argument("--offer-name", default="样片启动包", help="Commercial offer name.")
    parser.add_argument("--offer-price", default="1999-3999 元", help="Commercial offer price.")
    parser.add_argument(
        "--contact-note",
        default="可先免费跑 1 条样片，满意后再聊部署或代剪。",
        help="Short promise or next step for the prospect.",
    )
    args = parser.parse_args()

    package = build_demo_package(
        DemoPackageInput(
            output_dir=args.output_dir,
            sample_report=args.sample_report,
            screenshots=args.screenshot,
            offer_name=args.offer_name,
            offer_price=args.offer_price,
            contact_note=args.contact_note,
        )
    )
    print(f"Demo package written: {package.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
