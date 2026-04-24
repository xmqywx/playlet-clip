"""Outreach batch generation tests."""

import csv
import json
from pathlib import Path

from playlet_clip.reporting.outreach_batch import Prospect, build_outreach_batch


def test_build_outreach_batch_writes_tracker_and_messages(temp_dir: Path):
    output_dir = temp_dir / "outreach"
    prospects = [
        Prospect(
            name="闲鱼短剧剪辑服务商 A",
            channel="闲鱼",
            prospect_type="服务商",
            entry="闲鱼搜索：短剧剪辑",
            pain_point="已经在卖短剧剪辑服务，需要更快交付更多素材",
            priority="高",
        ),
        Prospect(
            name="巨量星图短剧达人 B",
            channel="巨量星图",
            prospect_type="达人/MCN",
            entry="巨量星图搜索：短剧 CPS",
            pain_point="有推剧账号，需要多风格样片测试",
            priority="高",
        ),
    ]

    batch = build_outreach_batch(
        prospects=prospects,
        output_dir=output_dir,
        batch_name="第一批高意向触达",
        free_sample_slots=3,
        package_path=Path("output/playlet-clip-demo/customer-package"),
    )

    assert batch.output_dir == output_dir
    assert batch.csv_path == output_dir / "outreach-tracker.csv"
    assert batch.markdown_path == output_dir / "today-batch.md"
    assert len(batch.message_paths) == 2
    assert len(batch.intake_paths) == 2
    assert batch.reply_router_path == output_dir / "reply-router.md"
    assert batch.send_queue_path == output_dir / "send-queue.md"
    assert batch.send_console_path == output_dir / "send-console.html"

    rows = list(csv.DictReader(batch.csv_path.open(encoding="utf-8")))
    assert rows[0]["目标名称"] == "闲鱼短剧剪辑服务商 A"
    assert rows[0]["状态"] == "待发送"
    assert rows[0]["下一步"] == "发送首条私信，索要 30-90 秒真实素材"
    assert rows[0]["免费样片状态"] == "未邀约"
    assert rows[0]["报价阶段"] == "未报价"
    assert rows[0]["预计金额"] == ""
    assert rows[0]["跟进日期"] == ""
    assert rows[1]["渠道"] == "巨量星图"

    markdown = batch.markdown_path.read_text(encoding="utf-8")
    assert "第一批高意向触达" in markdown
    assert "免费样片名额：3" in markdown
    assert "output/playlet-clip-demo/customer-package" in markdown

    xianyu_message = (output_dir / "messages" / "01-xian-yu-duan-ju-jian-ji-fu-wu-shang-a.md").read_text(
        encoding="utf-8"
    )
    assert "闲鱼短剧剪辑服务商 A" in xianyu_message
    assert "已经在卖短剧剪辑服务" in xianyu_message
    assert "30-90 秒" in xianyu_message
    assert "不满意不收费" in xianyu_message

    followup = (output_dir / "followups" / "01-xian-yu-duan-ju-jian-ji-fu-wu-shang-a.md").read_text(
        encoding="utf-8"
    )
    assert "素材追问" in followup
    assert "报价跟进" in followup
    assert "999-1999 元" in followup

    intake = (output_dir / "intake" / "01-xian-yu-duan-ju-jian-ji-fu-wu-shang-a.md").read_text(
        encoding="utf-8"
    )
    assert "素材提交要求" in intake
    assert "30-90 秒竖屏原片" in intake
    assert "已授权" in intake
    assert "不承诺流量" in intake

    reply_router = batch.reply_router_path.read_text(encoding="utf-8")
    assert "回复分流" in reply_router
    assert "可以试" in reply_router
    assert "直接索要素材" in reply_router

    send_queue = batch.send_queue_path.read_text(encoding="utf-8")
    assert "发送队列" in send_queue
    assert "闲鱼搜索：短剧剪辑" in send_queue
    assert "复制首条私信" in send_queue
    assert "outreach-tracker.csv" in send_queue
    assert "01-xian-yu-duan-ju-jian-ji-fu-wu-shang-a.md" in send_queue

    send_console = batch.send_console_path.read_text(encoding="utf-8")
    assert "Playlet-Clip 外联发送控制台" in send_console
    assert "copyText" in send_console
    assert "闲鱼短剧剪辑服务商 A" in send_console
    assert "首条私信" in send_console
    assert "素材收集" in send_console
    assert "跟进话术" in send_console
    assert "outreach-tracker.csv" in send_console
    assert "copyText('p1-message')" in send_console
    assert "copyText('p1-intake')" in send_console
    assert "copyText('p1-followup')" in send_console


def test_build_outreach_batch_loads_prospects_from_json_file(temp_dir: Path):
    prospects_path = temp_dir / "prospects.json"
    prospects_path.write_text(
        json.dumps(
            [
                {
                    "name": "短剧联盟渠道",
                    "channel": "短剧联盟",
                    "prospect_type": "短剧授权分销平台",
                    "entry": "https://example.test",
                    "pain_point": "旗下达人需要批量素材",
                    "priority": "高",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    batch = build_outreach_batch(
        prospects=prospects_path,
        output_dir=temp_dir / "batch",
        batch_name="渠道批次",
        free_sample_slots=1,
        package_path=Path("demo-package"),
    )

    rows = list(csv.DictReader(batch.csv_path.open(encoding="utf-8")))
    assert rows[0]["目标名称"] == "短剧联盟渠道"
    assert rows[0]["优先级"] == "高"
    assert (batch.output_dir / "messages" / "01-duan-ju-lian-meng-qu-dao.md").exists()
    assert (batch.output_dir / "followups" / "01-duan-ju-lian-meng-qu-dao.md").exists()
    assert (batch.output_dir / "intake" / "01-duan-ju-lian-meng-qu-dao.md").exists()
    assert (batch.output_dir / "reply-router.md").exists()
    assert (batch.output_dir / "send-queue.md").exists()
    assert (batch.output_dir / "send-console.html").exists()
