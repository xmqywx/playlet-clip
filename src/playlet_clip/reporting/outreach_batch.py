"""Generate sales outreach batches for customer validation."""

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class Prospect:
    """A sales prospect to contact."""

    name: str
    channel: str
    prospect_type: str
    entry: str
    pain_point: str
    priority: str


@dataclass(frozen=True)
class OutreachBatch:
    """Generated outreach batch files."""

    output_dir: Path
    csv_path: Path
    markdown_path: Path
    message_paths: list[Path]
    followup_paths: list[Path]


def build_outreach_batch(
    prospects: Sequence[Prospect] | Path,
    output_dir: Path,
    batch_name: str,
    free_sample_slots: int,
    package_path: Path,
) -> OutreachBatch:
    """Create a CSV tracker and copy-ready outreach messages."""
    prospect_items = _load_prospects(prospects)
    messages_dir = output_dir / "messages"
    followups_dir = output_dir / "followups"
    output_dir.mkdir(parents=True, exist_ok=True)
    messages_dir.mkdir(parents=True, exist_ok=True)
    followups_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "outreach-tracker.csv"
    _write_tracker(csv_path, prospect_items)

    markdown_path = output_dir / "today-batch.md"
    markdown_path.write_text(
        _render_batch_markdown(batch_name, free_sample_slots, package_path, prospect_items),
        encoding="utf-8",
    )

    message_paths = []
    followup_paths = []
    for index, prospect in enumerate(prospect_items, start=1):
        filename = f"{index:02d}-{_slugify(prospect.name)}.md"
        message_path = messages_dir / filename
        message_path.write_text(_render_message(prospect, package_path), encoding="utf-8")
        message_paths.append(message_path)
        followup_path = followups_dir / filename
        followup_path.write_text(_render_followup(prospect), encoding="utf-8")
        followup_paths.append(followup_path)

    return OutreachBatch(
        output_dir=output_dir,
        csv_path=csv_path,
        markdown_path=markdown_path,
        message_paths=message_paths,
        followup_paths=followup_paths,
    )


def _load_prospects(prospects: Sequence[Prospect] | Path) -> list[Prospect]:
    if isinstance(prospects, Path):
        raw_items = json.loads(prospects.read_text(encoding="utf-8"))
        return [Prospect(**item) for item in raw_items]
    return list(prospects)


def _write_tracker(path: Path, prospects: Sequence[Prospect]) -> None:
    fieldnames = [
        "目标名称",
        "渠道",
        "类型",
        "入口",
        "痛点",
        "优先级",
        "状态",
        "下一步",
        "免费样片状态",
        "报价阶段",
        "预计金额",
        "跟进日期",
        "备注",
    ]
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for prospect in prospects:
            writer.writerow(
                {
                    "目标名称": prospect.name,
                    "渠道": prospect.channel,
                    "类型": prospect.prospect_type,
                    "入口": prospect.entry,
                    "痛点": prospect.pain_point,
                    "优先级": prospect.priority,
                    "状态": "待发送",
                    "下一步": "发送首条私信，索要 30-90 秒真实素材",
                    "免费样片状态": "未邀约",
                    "报价阶段": "未报价",
                    "预计金额": "",
                    "跟进日期": "",
                    "备注": "",
                }
            )


def _render_batch_markdown(
    batch_name: str,
    free_sample_slots: int,
    package_path: Path,
    prospects: Sequence[Prospect],
) -> str:
    lines = [
        f"# {batch_name}",
        "",
        f"- 免费样片名额：{free_sample_slots}",
        f"- 演示包路径：`{package_path}`",
        "- 首轮目标：拿到 1 条真实素材并跑出客户样片",
        "- 筛选标准：已有短剧素材、正在接单或推广、愿意看样片",
        "",
        "## 今日触达列表",
        "",
        "| # | 目标 | 渠道 | 痛点 | 优先级 |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for index, prospect in enumerate(prospects, start=1):
        lines.append(
            f"| {index} | {prospect.name} | {prospect.channel} | "
            f"{prospect.pain_point} | {prospect.priority} |"
        )
    lines.extend(
        [
            "",
            "## 执行规则",
            "",
            "1. 先发私信，不解释技术细节。",
            "2. 对方愿意试样片后，只要 30-90 秒竖屏原片。",
            "3. 不承诺流量、爆单或绕平台风控。",
            "4. 有真实素材后，优先生成样片报告再谈收费。",
            "",
        ]
    )
    return "\n".join(lines)


def _render_message(prospect: Prospect, package_path: Path) -> str:
    return "\n".join(
        [
            f"# {prospect.name} 首条私信",
            "",
            f"渠道：{prospect.channel}",
            f"切入点：{prospect.pain_point}",
            "",
            "## 可复制版本",
            "",
            f"你好，看到你这边在做{prospect.channel}相关的短剧/推剧业务。",
            "",
            "我这边有一个短剧自动解说剪辑工具，可以把原视频自动处理成“字幕识别 + 解说文案 + AI 配音 + 成片”的二创素材。",
            f"你们这种情况通常是{prospect.pain_point}，所以我想先免费给你跑 1 条真实样片。",
            "",
            "如果你方便，可以发一段 30-90 秒竖屏短剧原片。我会给你一版成片和处理报告，满意后再聊部署、代跑或批量样片，不满意不收费。",
            "",
            f"演示包路径：`{package_path}`",
            "",
        ]
    )


def _render_followup(prospect: Prospect) -> str:
    return "\n".join(
        [
            f"# {prospect.name} 跟进话术",
            "",
            "## 素材追问",
            "",
            f"你好，昨天提到的短剧样片我这边还可以给你留一个名额。你们现在的主要痛点是{prospect.pain_point}，先发一段 30-90 秒竖屏原片就行，我只做一版样片和处理报告，不需要你先改流程。",
            "",
            "## 样片交付后",
            "",
            "这条样片已经跑完，报告里有字幕数、解说段数和输出路径。你可以先看节奏和文案方向，如果要继续测，我建议先做 3 条不同风格，比单条更容易判断能不能稳定出素材。",
            "",
            "## 报价跟进",
            "",
            "如果只是你自己用，我建议先走本地部署包，999-1999 元区间，交付部署、API 配置和基础培训。如果你们是团队批量测素材，可以走样片启动包或工作室自动化包，把风格模板和批量处理一起交付。",
            "",
        ]
    )


def _slugify(value: str) -> str:
    tokens = []
    for char in value:
        mapped = _PINYIN_MAP.get(char)
        if mapped:
            tokens.append(f"-{mapped}-")
        else:
            tokens.append(char)
    mapped = "".join(tokens)
    normalized = re.sub(r"[^A-Za-z0-9]+", "-", mapped).strip("-").lower()
    return normalized or "prospect"


_PINYIN_MAP = {
    "闲": "xian",
    "鱼": "yu",
    "短": "duan",
    "剧": "ju",
    "视": "shi",
    "频": "pin",
    "号": "hao",
    "推": "tui",
    "广": "guang",
    "团": "tuan",
    "队": "dui",
    "剪": "jian",
    "辑": "ji",
    "服": "fu",
    "务": "wu",
    "商": "shang",
    "巨": "ju",
    "量": "liang",
    "星": "xing",
    "图": "tu",
    "达": "da",
    "人": "ren",
    "联": "lian",
    "盟": "meng",
    "渠": "qu",
    "道": "dao",
    "分": "fen",
    "销": "xiao",
    "平": "ping",
    "台": "tai",
}
