"""Generate customer-facing sample processing reports."""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from playlet_clip.models.subtitle import SubtitleFile
from playlet_clip.models.task import ProcessResult


@dataclass(frozen=True)
class SampleReportInput:
    """Inputs required to render a sample report."""

    title: str
    input_video: Path
    result: ProcessResult
    style: str | None = None
    generated_at: datetime | None = None


def generate_sample_report(report_input: SampleReportInput) -> str:
    """Render a Markdown report from a pipeline result."""
    result = report_input.result
    generated_at = report_input.generated_at or datetime.now()
    subtitles_count = _count_subtitles(result.subtitles_path)
    narration_items = _load_narration_items(result.narration_json_path)
    narration_count = sum(1 for item in narration_items if item.get("type") == "解说")
    video_count = sum(1 for item in narration_items if item.get("type") == "video")
    sample_lines = _render_narration_preview(narration_items)

    status = "成功" if result.success else "失败"
    style = report_input.style or "默认风格"
    output_path = str(result.output_path) if result.output_path else "未生成"
    error_message = result.error_message or "无"

    lines = [
        f"# {report_input.title}",
        "",
        "## 交付摘要",
        "",
        "| 项目 | 结果 |",
        "| --- | --- |",
        f"| 处理状态 | {status} |",
        f"| 商业风格 | {style} |",
        f"| 输入视频 | {report_input.input_video.name} |",
        f"| 字幕条数 | {subtitles_count} |",
        f"| 解说段数 | {narration_count} |",
        f"| 视频保留段数 | {video_count} |",
        f"| 总片段数 | {result.segments_count} |",
        f"| 处理耗时 | {_format_duration(result.duration)} |",
        f"| 输出视频 | {output_path} |",
        f"| 报告时间 | {generated_at.strftime('%Y-%m-%d %H:%M:%S')} |",
        "",
        "## 客户可见结论",
        "",
        "- 已完成原片解析、字幕统计、解说脚本生成和成片输出路径归档。",
        "- 可用本报告快速确认样片处理量、剪辑结构和最终交付文件。",
    ]

    if not result.success:
        lines.extend(["", "## 异常信息", "", error_message])

    if sample_lines:
        lines.extend(["", "## 解说预览", "", *sample_lines])

    lines.extend(
        [
            "",
            "## 交付文件",
            "",
            f"- 输入视频：`{report_input.input_video}`",
            f"- 字幕文件：`{result.subtitles_path or '未生成'}`",
            f"- 解说 JSON：`{result.narration_json_path or '未生成'}`",
            f"- 输出视频：`{output_path}`",
            "",
        ]
    )
    return "\n".join(lines)


def _count_subtitles(path: Path | None) -> int:
    if path is None or not path.exists():
        return 0
    content = path.read_text(encoding="utf-8")
    return len(SubtitleFile.from_srt(content).segments)


def _load_narration_items(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def _render_narration_preview(items: list[dict[str, Any]], limit: int = 5) -> list[str]:
    lines = []
    narration_items = [item for item in items if item.get("type") == "解说"]
    for index, item in enumerate(narration_items[:limit], start=1):
        time_range = item.get("time") or "未标注时间"
        content = item.get("content") or ""
        lines.append(f"{index}. `{time_range}` {content}")
    return lines


def _format_duration(seconds: float) -> str:
    total_seconds = max(0, int(round(seconds)))
    minutes, secs = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}小时{minutes}分{secs}秒"
    if minutes:
        return f"{minutes}分{secs}秒"
    return f"{secs}秒"
