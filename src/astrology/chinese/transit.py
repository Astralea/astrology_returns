"""行运分析 —— 大运、流年、流月与原局的关系。"""

from __future__ import annotations

import swisseph as swe
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .pillars import TIANGAN, DIZHI, tg_element, dz_element
from .shishen import get_shishen
from .relations import analyze_relations, is_chong, is_liuhe, get_sanhe, get_xing
from .liunian import get_liunian, get_liuyue
from .dayun import DaYun

if TYPE_CHECKING:
    from .bazi import BaZi


@dataclass
class TransitPillar:
    """行运柱（大运/流年/流月/流日）。"""
    name: str           # 名称（如"大运"、"流年"）
    ganzhi: str         # 干支
    stem_index: int     # 天干索引
    branch_index: int   # 地支索引
    shishen: str = ""   # 天干十神（相对于日主）
    relations: list = field(default_factory=list)  # 与原局的关系


@dataclass
class PeriodAnalysis:
    """行运周期分析结果。"""
    # 原局
    natal: BaZi
    
    # 当前大运
    dayun: DaYun | None = None
    
    # 流年
    liunian: TransitPillar | None = None
    
    # 流月
    liuyue: TransitPillar | None = None
    
    # 流日（可选）
    liuri: TransitPillar | None = None
    
    # 综合分析
    summary: str = ""


def find_current_dayun(bazi: BaZi, dayun_list: list[DaYun], target_year: int) -> DaYun | None:
    """找到目标年份所在的大运。"""
    for dy in dayun_list:
        if dy.year_start <= target_year <= dy.year_end:
            return dy
    return None


def analyze_transit_relations(
    natal_branches: list[int],
    transit_branch: int,
    transit_name: str
) -> list[str]:
    """分析行运地支与原局的关系。"""
    relations = []
    dz_names = DIZHI
    
    # 检查与原局四柱地支的关系
    pillar_names = ["年支", "月支", "日支", "时支"]
    for i, natal_b in enumerate(natal_branches):
        # 冲
        if is_chong(natal_b, transit_branch):
            relations.append(f"冲{pillar_names[i]}({dz_names[natal_b]})")
        # 合
        from .relations import LIUHE
        if LIUHE.get(natal_b) == transit_branch:
            relations.append(f"合{pillar_names[i]}({dz_names[natal_b]})")
        # 刑
        xing = get_xing(natal_b, transit_branch)
        if xing:
            relations.append(f"刑{pillar_names[i]}({dz_names[natal_b]})")
    
    # 检查三合局
    all_branches = natal_branches + [transit_branch]
    has_sanhe, sanhe_elem = get_sanhe(all_branches)
    if has_sanhe:
        relations.append(f"三合{sanhe_elem}局")
    
    return relations


def analyze_period(
    bazi: BaZi,
    year: int,
    month: int | None = None,
    day: int | None = None,
    dayun_list: list[DaYun] | None = None,
) -> PeriodAnalysis:
    """
    分析指定时间的行运。
    
    Args:
        bazi: 原局八字
        year: 目标年份
        month: 目标月份（可选，默认当前月）
        day: 目标日期（可选，默认当前日）
        dayun_list: 预计算的大运列表（可选）
    """
    from .liunian import LiuNian, LiuYue
    
    result = PeriodAnalysis(natal=bazi)
    day_master = bazi.day_master_index
    natal_branches = bazi.all_branches
    
    # ========== 大运 ==========
    if dayun_list is None:
        from .dayun import calculate_dayun_simple
        import swisseph as swe
        jd = swe.julday(bazi.year, bazi.month, bazi.day, bazi.hour)
        is_male = True  # 默认，应该传入
        dayun_list = calculate_dayun_simple(
            jd,
            bazi.year_pillar.stem_index,
            bazi.month_pillar.stem_index,
            bazi.month_pillar.branch_index,
            is_male=is_male,
        )
    
    current_dayun = find_current_dayun(bazi, dayun_list, year)
    result.dayun = current_dayun
    
    # ========== 流年 ==========
    ln = get_liunian(year)
    ln_shishen = get_shishen(day_master, ln.stem_index)
    ln_relations = analyze_transit_relations(natal_branches, ln.branch_index, "流年")
    
    result.liunian = TransitPillar(
        name="流年",
        ganzhi=ln.ganzhi,
        stem_index=ln.stem_index,
        branch_index=ln.branch_index,
        shishen=ln_shishen,
        relations=ln_relations,
    )
    
    # ========== 流月 ==========
    if month is not None:
        # 转换为农历月份（简化处理，实际应该按节气）
        ly = get_liuyue(year, month)
        ly_shishen = get_shishen(day_master, ly.stem_index)
        ly_relations = analyze_transit_relations(natal_branches, ly.branch_index, "流月")
        
        result.liuyue = TransitPillar(
            name="流月",
            ganzhi=ly.ganzhi,
            stem_index=ly.stem_index,
            branch_index=ly.branch_index,
            shishen=ly_shishen,
            relations=ly_relations,
        )
    
    # ========== 流日 ==========
    if day is not None and month is not None:
        from .liunian import get_liuri
        lr = get_liuri(year, month, day)
        lr_shishen = get_shishen(day_master, lr.stem_index)
        lr_relations = analyze_transit_relations(natal_branches, lr.branch_index, "流日")
        
        result.liuri = TransitPillar(
            name="流日",
            ganzhi=lr.ganzhi,
            stem_index=lr.stem_index,
            branch_index=lr.branch_index,
            shishen=lr_shishen,
            relations=lr_relations,
        )
    
    # ========== 生成摘要 ==========
    result.summary = _generate_summary(result)
    
    return result


def _generate_summary(period: PeriodAnalysis) -> str:
    """生成行运摘要。"""
    parts = []
    
    if period.dayun:
        parts.append(f"行{period.dayun.ganzhi}大运({period.dayun.year_start}-{period.dayun.year_end})")
    
    if period.liunian:
        parts.append(f"遇{period.liunian.ganzhi}流年")
        if period.liunian.relations:
            parts.append(f"流年{', '.join(period.liunian.relations[:3])}")  # 最多显示3个
    
    return "；".join(parts) if parts else "暂无行运信息"


def format_period(period: PeriodAnalysis, show_detail: bool = True) -> str:
    """格式化行运分析。"""
    lines = []
    
    # 标题
    lines.append("=" * 50)
    lines.append("行运分析")
    lines.append("=" * 50)
    
    # 原局日主
    lines.append(f"\n原局日主: {period.natal.day_master} ({period.natal.day_master_element})")
    lines.append(f"原局四柱: {' '.join([p.ganzhi for p in period.natal.pillars])}")
    
    # 大运
    if period.dayun:
        lines.append(f"\n【大运】{period.dayun.ganzhi}")
        lines.append(f"  时间段: {period.dayun.year_start}-{period.dayun.year_end}年")
        lines.append(f"  年龄段: {period.dayun.age_start:.1f}-{period.dayun.age_end:.1f}岁")
        dy_shishen = get_shishen(period.natal.day_master_index, period.dayun.stem_index)
        lines.append(f"  天干十神: {dy_shishen}")
    
    # 流年
    if period.liunian:
        lines.append(f"\n【流年】{period.liunian.ganzhi}")
        lines.append(f"  天干十神: {period.liunian.shishen}")
        if period.liunian.relations:
            lines.append(f"  地支关系: {'，'.join(period.liunian.relations)}")
    
    # 流月
    if period.liuyue:
        lines.append(f"\n【流月】{period.liuyue.ganzhi}")
        lines.append(f"  天干十神: {period.liuyue.shishen}")
        if period.liuyue.relations:
            lines.append(f"  地支关系: {'，'.join(period.liuyue.relations)}")
    
    # 流日
    if period.liuri:
        lines.append(f"\n【流日】{period.liuri.ganzhi}")
        lines.append(f"  天干十神: {period.liuri.shishen}")
        if period.liuri.relations:
            lines.append(f"  地支关系: {'，'.join(period.liuri.relations)}")
    
    # 综合提示
    if period.summary:
        lines.append(f"\n【运势提示】")
        lines.append(f"  {period.summary}")
    
    return "\n".join(lines)


def format_period_compact(period: PeriodAnalysis) -> str:
    """紧凑格式输出。"""
    parts = []
    
    if period.dayun:
        parts.append(f"大运{period.dayun.ganzhi}")
    
    if period.liunian:
        rel_str = f"({','.join(period.liunian.relations[:2])})" if period.liunian.relations else ""
        parts.append(f"流年{period.liunian.ganzhi}{rel_str}")
    
    if period.liuyue:
        parts.append(f"流月{period.liuyue.ganzhi}")
    
    return " | ".join(parts)
