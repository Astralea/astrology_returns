"""八字格式化输出 —— 美观的文本展示。"""

from __future__ import annotations

from .bazi import BaZi, Pillar
from .shishen import SHISHEN_NAMES
from .pillars import TIANGAN, DIZHI


def format_pillar(p: Pillar, show_shishen: bool = True) -> str:
    """格式化单个柱。"""
    lines = []
    
    # 干支
    lines.append(f"{p.name}: {p.ganzhi}")
    
    # 十神
    if show_shishen:
        lines.append(f"  天干十神: {p.shishen_stem}")
        lines.append(f"  地支十神: {p.shishen_branch}")
        
        # 藏干
        if p.canggan:
            canggan_str = " | ".join([
                f"{c['qi']}{c['stem']}({c['shishen']})" 
                for c in p.canggan
            ])
            lines.append(f"  藏干: {canggan_str}")
    
    return "\n".join(lines)


def format_bazi(bazi: BaZi, show_detail: bool = True) -> str:
    """格式化八字命盘。"""
    lines = []
    
    # 标题
    lines.append("=" * 40)
    lines.append("八字命盘")
    lines.append("=" * 40)
    
    # 基本信息
    time_str = f"{bazi.year:04d}-{bazi.month:02d}-{bazi.day:02d} {int(bazi.hour):02d}:{int((bazi.hour % 1) * 60):02d}"
    lines.append(f"出生时间: {time_str}")
    if bazi.location:
        lines.append(f"出生地点: {bazi.location}")
    if bazi.use_true_solar_time:
        lines.append("注: 已使用真太阳时校正")
    lines.append("")
    
    # 四柱表格
    lines.append("-" * 40)
    lines.append(f"{'':8} {'天干':6} {'地支':6} {'十神':8}")
    lines.append("-" * 40)
    
    for p in bazi.pillars:
        shishen_str = p.shishen_stem if p.name != "日柱" else "日主"
        lines.append(f"{p.name:6} {p.stem:6} {p.branch:6} {shishen_str:8}")
    
    lines.append("-" * 40)
    lines.append("")
    
    # 日主信息
    lines.append(f"日主: {bazi.day_master} ({bazi.day_master_element}，{'阳' if bazi.day_master_yin else '阴'})")
    lines.append("")
    
    # 详细藏干
    if show_detail:
        lines.append("=" * 40)
        lines.append("藏干详情")
        lines.append("=" * 40)
        
        for p in bazi.pillars:
            lines.append(f"\n{p.name} {p.ganzhi}:")
            if p.canggan:
                for c in p.canggan:
                    lines.append(f"  {c['qi']:2} {c['stem']} → {c['shishen']}")
            else:
                lines.append("  无藏干信息")
        
        lines.append("")
    
    return "\n".join(lines)


def format_bazi_compact(bazi: BaZi) -> str:
    """紧凑格式输出八字。"""
    pillars = [p.ganzhi for p in bazi.pillars]
    return f"{' '.join(pillars)} | 日主{bazi.day_master}({bazi.day_master_element})"


def format_shishen_distribution(bazi: BaZi) -> str:
    """格式化十神分布统计。"""
    from collections import Counter
    
    # 统计所有十神
    all_shishen = []
    for p in bazi.pillars:
        all_shishen.append(p.shishen_stem)
        for c in p.canggan:
            all_shishen.append(c['shishen'])
    
    counter = Counter(all_shishen)
    
    lines = []
    lines.append("十神分布:")
    for name in SHISHEN_NAMES:
        count = counter.get(name, 0)
        if count > 0:
            bar = "█" * count
            lines.append(f"  {name:4}: {bar} ({count})")
    
    return "\n".join(lines)


def format_relations_analysis(bazi: BaZi) -> str:
    """格式化地支关系分析。"""
    from .relations import analyze_relations, format_relation
    
    branches = bazi.all_branches
    relations = analyze_relations(branches)
    
    lines = []
    lines.append("=" * 40)
    lines.append("地支关系")
    lines.append("=" * 40)
    
    has_relation = False
    
    # 六合
    if relations["liuhe"]:
        has_relation = True
        lines.append("\n【六合】")
        for b1, b2, elem in relations["liuhe"]:
            lines.append(f"  {format_relation(b1, b2, '合', f'化{elem}' if elem else '')}")
    
    # 六冲
    if relations["chong"]:
        has_relation = True
        lines.append("\n【六冲】")
        for b1, b2 in relations["chong"]:
            lines.append(f"  {format_relation(b1, b2, '冲')}")
    
    # 三合
    if relations["sanhe"]:
        has_relation = True
        lines.append("\n【三合局】")
        for b1, b2, b3, elem in relations["sanhe"]:
            ganzhi = DIZHI[b1] + DIZHI[b2] + DIZHI[b3]
            lines.append(f"  {ganzhi} {elem}局")
    
    # 半合
    if relations["sanhe_partial"]:
        has_relation = True
        lines.append("\n【半合局】")
        for b1, b2, elem in relations["sanhe_partial"]:
            lines.append(f"  {format_relation(b1, b2, '半合', elem + '局')}")
    
    # 三会
    if relations["sanhui"]:
        has_relation = True
        lines.append("\n【三会局】")
        for b1, b2, b3, elem in relations["sanhui"]:
            ganzhi = DIZHI[b1] + DIZHI[b2] + DIZHI[b3]
            lines.append(f"  {ganzhi} {elem}局")
    
    # 相刑
    if relations["xing"]:
        has_relation = True
        lines.append("\n【相刑】")
        for b1, b2, xing_type in relations["xing"]:
            lines.append(f"  {format_relation(b1, b2, '刑', xing_type)}")
    
    # 六害
    if relations["hai"]:
        has_relation = True
        lines.append("\n【六害】")
        for b1, b2 in relations["hai"]:
            lines.append(f"  {format_relation(b1, b2, '害')}")
    
    # 相破
    if relations["po"]:
        has_relation = True
        lines.append("\n【相破】")
        for b1, b2 in relations["po"]:
            lines.append(f"  {format_relation(b1, b2, '破')}")
    
    if not has_relation:
        lines.append("\n  无特殊地支关系")
    
    return "\n".join(lines)


def format_dayun(dayun_list: list) -> str:
    """格式化大运列表。"""
    lines = []
    lines.append("=" * 50)
    lines.append("大运")
    lines.append("=" * 50)
    lines.append(f"{'运数':6} {'年龄':12} {'公历年份':12} {'干支':8} {'方向':4}")
    lines.append("-" * 50)
    
    for dy in dayun_list:
        age_range = f"{dy.age_start:.1f}-{dy.age_end:.1f}岁"
        year_range = f"{dy.year_start}-{dy.year_end}"
        direction = "顺" if dy.is_forward else "逆"
        lines.append(f"{dy.index+1:3}   {age_range:12} {year_range:12} {dy.ganzhi:8} {direction:4}")
    
    return "\n".join(lines)


def format_liunian(liunian_list: list) -> str:
    """格式化流年列表。"""
    lines = []
    lines.append("流年:")
    
    for ln in liunian_list:
        lines.append(f"  {ln.year}: {ln.ganzhi}")
    
    return "\n".join(lines)


def format_full_report(bazi: BaZi, dayun_list: list = None, liunian_list: list = None) -> str:
    """生成完整报告。"""
    sections = []
    
    # 八字
    sections.append(format_bazi(bazi))
    
    # 十神分布
    sections.append(format_shishen_distribution(bazi))
    sections.append("")
    
    # 地支关系
    sections.append(format_relations_analysis(bazi))
    sections.append("")
    
    # 大运
    if dayun_list:
        sections.append(format_dayun(dayun_list))
        sections.append("")
    
    # 流年
    if liunian_list:
        sections.append(format_liunian(liunian_list))
    
    return "\n".join(sections)
