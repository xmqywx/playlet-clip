"""Demo package generation tests."""

from pathlib import Path

from playlet_clip.reporting.demo_package import DemoPackageInput, build_demo_package


def test_build_demo_package_writes_customer_ready_files(temp_dir: Path):
    report_path = temp_dir / "sample-report.md"
    screenshot_path = temp_dir / "web-ui.png"
    output_dir = temp_dir / "demo-package"

    report_path.write_text("# 样片报告\n\n| 字幕条数 | 2 |", encoding="utf-8")
    screenshot_path.write_bytes(b"fake image")

    package = build_demo_package(
        DemoPackageInput(
            output_dir=output_dir,
            sample_report=report_path,
            screenshots=[screenshot_path],
            offer_name="样片启动包",
            offer_price="1999-3999 元",
            contact_note="可先免费跑 1 条样片，满意后再部署。",
        )
    )

    assert package.output_dir == output_dir
    assert (output_dir / "README.md").exists()
    assert (output_dir / "sample-report.md").read_text(encoding="utf-8") == report_path.read_text(
        encoding="utf-8"
    )
    assert (output_dir / "screenshots" / "web-ui.png").read_bytes() == b"fake image"
    outreach = (output_dir / "outreach-message.md").read_text(encoding="utf-8")
    assert "样片启动包" in outreach
    assert "1999-3999 元" in outreach
    assert "可先免费跑 1 条样片" in outreach


def test_build_demo_package_skips_missing_screenshots(temp_dir: Path):
    report_path = temp_dir / "sample-report.md"
    output_dir = temp_dir / "demo-package"
    report_path.write_text("# 样片报告", encoding="utf-8")

    package = build_demo_package(
        DemoPackageInput(
            output_dir=output_dir,
            sample_report=report_path,
            screenshots=[temp_dir / "missing.png"],
            offer_name="本地部署包",
            offer_price="999-1999 元",
        )
    )

    assert package.copied_screenshots == []
    assert "暂无截图" in (output_dir / "README.md").read_text(encoding="utf-8")
