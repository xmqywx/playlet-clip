"""Build customer-facing demo packages."""

from dataclasses import dataclass
from pathlib import Path
from shutil import copy2


@dataclass(frozen=True)
class DemoPackageInput:
    """Inputs required to assemble a demo package."""

    output_dir: Path
    sample_report: Path
    screenshots: list[Path]
    offer_name: str
    offer_price: str
    contact_note: str = "可先免费跑 1 条样片，满意后再聊部署或代剪。"


@dataclass(frozen=True)
class DemoPackage:
    """Generated demo package paths."""

    output_dir: Path
    copied_screenshots: list[Path]


def build_demo_package(package_input: DemoPackageInput) -> DemoPackage:
    """Create a small folder that can be sent to a sales prospect."""
    output_dir = package_input.output_dir
    screenshots_dir = output_dir / "screenshots"
    output_dir.mkdir(parents=True, exist_ok=True)
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    report_dest = output_dir / "sample-report.md"
    copy2(package_input.sample_report, report_dest)

    copied_screenshots = []
    for screenshot in package_input.screenshots:
        if screenshot.exists():
            dest = screenshots_dir / screenshot.name
            copy2(screenshot, dest)
            copied_screenshots.append(dest)

    (output_dir / "README.md").write_text(
        _render_readme(package_input, copied_screenshots),
        encoding="utf-8",
    )
    (output_dir / "outreach-message.md").write_text(
        _render_outreach(package_input),
        encoding="utf-8",
    )
    return DemoPackage(output_dir=output_dir, copied_screenshots=copied_screenshots)


def _render_readme(package_input: DemoPackageInput, screenshots: list[Path]) -> str:
    screenshot_lines = (
        "\n".join(f"- screenshots/{path.name}" for path in screenshots) if screenshots else "- 暂无截图"
    )
    return "\n".join(
        [
            "# Playlet-Clip 客户演示包",
            "",
            "## 交付内容",
            "",
            "- `sample-report.md`：样片处理统计和交付路径",
            "- `outreach-message.md`：可直接发送给客户的私信文案",
            "- `screenshots/`：Web UI 或样片流程截图",
            "",
            "## 当前报价",
            "",
            f"- 套餐：{package_input.offer_name}",
            f"- 价格：{package_input.offer_price}",
            f"- 备注：{package_input.contact_note}",
            "",
            "## 截图清单",
            "",
            screenshot_lines,
            "",
        ]
    )


def _render_outreach(package_input: DemoPackageInput) -> str:
    return "\n".join(
        [
            "# 客户私信文案",
            "",
            "你好，我做了一个短剧自动解说剪辑工具，可以把原视频自动转成“字幕识别 + 解说文案 + AI 配音 + 成片”的二创素材。",
            "",
            f"目前主推 `{package_input.offer_name}`，参考价格 `{package_input.offer_price}`。",
            package_input.contact_note,
            "",
            "如果你现在有短剧素材，可以先发 1 条，我用这个流程生成样片和处理报告，你看效果后再决定是否部署。",
            "",
        ]
    )
