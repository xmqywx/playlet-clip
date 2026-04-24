"""Sample report generation tests."""

import json
import subprocess
import sys
from pathlib import Path

from playlet_clip.models.task import ProcessResult
from playlet_clip.reporting.sample_report import SampleReportInput, generate_sample_report


def _write_sample_files(temp_dir: Path) -> tuple[Path, Path, Path, Path]:
    video_path = temp_dir / "demo.mp4"
    output_path = temp_dir / "demo_output.mp4"
    srt_path = temp_dir / "subtitles.srt"
    narration_path = temp_dir / "narration.json"

    video_path.write_bytes(b"fake video")
    output_path.write_bytes(b"fake output")
    srt_path.write_text(
        """1
00:00:00,000 --> 00:00:02,000
第一句台词

2
00:00:02,000 --> 00:00:04,000
第二句台词
""",
        encoding="utf-8",
    )
    narration_path.write_text(
        json.dumps(
            [
                {"type": "解说", "content": "她终于发现真相。", "time": "00:00:00,000 --> 00:00:01,500"},
                {"type": "video", "content": None, "time": "00:00:01,500 --> 00:00:02,500"},
                {"type": "解说", "content": "下一秒，全场安静。", "time": "00:00:02,500 --> 00:00:04,000"},
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return video_path, output_path, srt_path, narration_path


def test_generate_sample_report_summarizes_pipeline_result(temp_dir: Path):
    video_path, output_path, srt_path, narration_path = _write_sample_files(temp_dir)
    result = ProcessResult(
        success=True,
        output_path=output_path,
        duration=87.4,
        segments_count=3,
        subtitles_path=srt_path,
        narration_json_path=narration_path,
    )

    report = generate_sample_report(
        SampleReportInput(
            title="客户样片交付报告",
            input_video=video_path,
            result=result,
            style="反转悬疑",
        )
    )

    assert "# 客户样片交付报告" in report
    assert "| 处理状态 | 成功 |" in report
    assert "| 输入视频 | demo.mp4 |" in report
    assert "| 字幕条数 | 2 |" in report
    assert "| 解说段数 | 2 |" in report
    assert "| 视频保留段数 | 1 |" in report
    assert "| 处理耗时 | 1分27秒 |" in report
    assert str(output_path) in report
    assert "她终于发现真相。" in report


def test_sample_report_cli_writes_markdown_file(temp_dir: Path):
    video_path, output_path, srt_path, narration_path = _write_sample_files(temp_dir)
    report_path = temp_dir / "report.md"

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/generate_sample_report.py",
            "--input-video",
            str(video_path),
            "--output-video",
            str(output_path),
            "--subtitles",
            str(srt_path),
            "--narration-json",
            str(narration_path),
            "--duration",
            "12.2",
            "--style",
            "狗血吐槽",
            "--report-path",
            str(report_path),
        ],
        cwd=Path(__file__).parent.parent,
        check=False,
        text=True,
        capture_output=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8")
    assert "| 商业风格 | 狗血吐槽 |" in content
    assert "| 字幕条数 | 2 |" in content
    assert "| 解说段数 | 2 |" in content
    assert "| 总片段数 | 3 |" in content
    assert str(report_path) in completed.stdout
