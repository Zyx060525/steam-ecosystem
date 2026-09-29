# -*- coding: utf-8 -*-
"""生成项目展示 PPT 骨架。"""
import os

from pptx import Presentation
from pptx.util import Inches, Pt

BASE = os.path.dirname(os.path.abspath(__file__))
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

TITLE = prs.slide_layouts[0]  # 标题版式
CONTENT = prs.slide_layouts[1]  # 标题+内容


def add_title_slide(title, subtitle=""):
    s = prs.slides.add_slide(TITLE)
    s.shapes.title.text = title
    if subtitle:
        s.placeholders[1].text = subtitle
    return s


def add_bullet_slide(title, bullets):
    s = prs.slides.add_slide(CONTENT)
    s.shapes.title.text = title
    body = s.placeholders[1].text_frame
    body.text = bullets[0]
    for b in bullets[1:]:
        p = body.add_paragraph()
        p.text = b
        p.level = 0
    return s


# 1 封面
add_title_slide("Steam 游戏生态的多维画像", "多源多维度数据采集、融合分析与可视化\n《大数据原理与应用》中期作业 · 组员：XXX")

# 2 选题与背景
add_bullet_slide("选题与背景", [
    "Steam 是全球最大 PC 游戏平台，聚集硬件配置、在线人数、评论、元数据、更新事件等多维数据",
    "核心：用多个独立数据源观察同一真实问题，并真正关联起来",
    "覆盖 3 类数据形态：官方统计 + 行为数据 + 事件文本 + 实体映射",
])

# 3 研究问题
add_bullet_slide("3 个核心研究问题", [
    "Q1 游戏好评率能否解释其在线人气？（评论 + 在线，实体关联）",
    "Q2 玩家硬件配置是否随新一代游戏发行协同演进？（硬件 + 元数据，时间关联）",
    "Q3 更新/赛事对在线人数的冲击有多大？（新闻 + 在线，事件+时间关联）",
])

# 4 数据源
add_bullet_slide("5 个独立数据源", [
    "① Steam 硬件调查 —— 官方统计（月度，2008~2026）",
    "② Steam 在线人数 —— 公开 API 自采（分钟级）",
    "③ Steam 评论 —— Kaggle 数据集（1.28 亿条）",
    "④ 游戏元数据 —— Steam API（实体映射）",
    "⑤ 新闻/更新事件 —— Steam API（事件文本）",
])

# 5 关联图
s = prs.slides.add_slide(CONTENT)
s.shapes.title.text = "多源数据关联（实体 / 时间 / 事件）"
s.shapes.add_picture(os.path.join(BASE, "data_lineage.png"), Inches(3.9), Inches(1.2), width=Inches(5.5))

# 6 处理链
add_bullet_slide("Raw → Clean → Integrated 处理链", [
    "Raw：原始数据（含 123 行 player_count=0 异常）",
    "Clean：剔除异常、备份原始（steam_online_raw.csv）",
    "Integrated：以 appid 融合为「游戏维度」总表（8 行 × 19 列）",
])

# 7 Q1 结果
s = prs.slides.add_slide(CONTENT)
s.shapes.title.text = "Q1 口碑 vs 在线人气：几乎无关 (r=-0.068)"
s.placeholders[1].text = "PUBG 好评率最低(58.2%)但在线第三高——免费制/电竞 > 口碑"
s.shapes.add_picture(os.path.join(BASE, "visualization", "v2_reputation_vs_online.png"), Inches(4.2), Inches(2.3), width=Inches(5))

# 8 Q2 结果
s = prs.slides.add_slide(CONTENT)
s.shapes.title.text = "Q2 硬件配置协同演进（8GB→16GB, 2019-2020）"
s.placeholders[1].text = "内存代际切换与 Destiny2/Apex 等新游戏发行时间吻合"
s.shapes.add_picture(os.path.join(BASE, "visualization", "v4_hardware_evolution.png"), Inches(3.2), Inches(2.3), width=Inches(7))

# 9 Q3 结果
s = prs.slides.add_slide(CONTENT)
s.shapes.title.text = "Q3 事件冲击：电竞/活动拉动 +60% 在线"
s.placeholders[1].text = "注意剔除「日周期」混淆（凌晨下降≠事件负效应）"
s.shapes.add_picture(os.path.join(BASE, "visualization", "v3_event_impact.png"), Inches(3.4), Inches(2.3), width=Inches(6.5))

# 10 可视化总览
add_bullet_slide("5 张核心可视化（问题式标题）", [
    "v1 不同游戏在线人数如何随时间波动？（总体特征）",
    "v2 好评率能解释在线人气吗？（跨源关系）",
    "v3 更新/赛事后在线是否显著上升？（跨源关系）",
    "v4 硬件如何随游戏发行演进？（时间分析）",
    "v5 全球上线高峰在哪些时段？（时间分析）",
])

# 11 AI 使用
add_bullet_slide("AI 使用与反思", [
    "工具：Cline（Claude），全程参与采集/清洗/融合/分析/可视化",
    "核验：代码本地运行验证、数据交叉核对、结论人工判断",
    "纠正：下载内存崩溃→改 curl；文件大小误读→底层接口复核；凌晨负效应→识别为日周期混淆",
])

# 12 结论
add_bullet_slide("结论与局限", [
    "结论：①口碑≠人气 ②硬件与游戏协同演进 ③事件显著拉动在线",
    "局限：核心样本仅 8 游戏；在线为行为数据规模受限；评论占规模主导",
    "感谢提问！",
])

out = os.path.join(BASE, "项目展示PPT_Steam游戏生态.pptx")
prs.save(out)
print(f"PPT 骨架已生成: {out}")
