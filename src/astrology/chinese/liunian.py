"""流年、流月、流日 —— 时间流转的干支。"""

from __future__ import annotations

import swisseph as swe
from dataclasses import dataclass

from .pillars import TIANGAN, DIZHI, cycle_to_ganzhi_v2, year_to_ganzhi


@dataclass
class LiuNian:
    """流年。"""
    year: int
    stem: str
    stem_index: int
    branch: str
    branch_index: int
    ganzhi: str


@dataclass
class LiuYue:
    """流月。"""
    year: int
    month: int
    stem: str
    stem_index: int
    branch: str
    branch_index: int
    ganzhi: str


@dataclass
class LiuRi:
    """流日。"""
    year: int
    month: int
    day: int
    stem: str
    stem_index: int
    branch: str
    branch_index: int
    ganzhi: str


# ============ 流年 ============

def get_liunian(year: int) -> LiuNian:
    """获取指定公历年的流年干支。"""
    stem, branch = year_to_ganzhi(year)
    return LiuNian(
        year=year,
        stem=TIANGAN[stem],
        stem_index=stem,
        branch=DIZHI[branch],
        branch_index=branch,
        ganzhi=TIANGAN[stem] + DIZHI[branch],
    )


def get_liunian_range(start_year: int, end_year: int) -> list[LiuNian]:
    """获取一段时间范围内的流年列表。"""
    return [get_liunian(y) for y in range(start_year, end_year + 1)]


# ============ 流月 ============

# 五虎遁月（年干起月干）
# 甲己之年丙作首（甲己年正月丙寅）
# 乙庚之岁戊为头（乙庚年正月戊寅）
# 丙辛之岁寻庚上（丙辛年正月庚寅）
# 丁壬壬位顺行流（丁壬年正月壬寅）
# 若问戊癸何处起，甲寅之上好追求（戊癸年正月甲寅）

YEAR_TO_MONTH_STEM = {
    0: 2,   # 甲年 -> 丙
    5: 2,   # 己年 -> 丙
    1: 4,   # 乙年 -> 戊
    6: 4,   # 庚年 -> 戊
    2: 6,   # 丙年 -> 庚
    7: 6,   # 辛年 -> 庚
    3: 8,   # 丁年 -> 壬
    8: 8,   # 壬年 -> 壬
    4: 0,   # 戊年 -> 甲
    9: 0,   # 癸年 -> 甲
}

# 正月建寅（寅月索引为2）
ZHENGYUE_BRANCH = 2


def get_liuyue(year: int, month: int) -> LiuYue:
    """
    获取指定年月（农历月，正月=1）的流月干支。
    
    注意：这里的 month 是农历月份（正月到腊月），不是公历月份。
    实际使用时需要根据节气转换。
    """
    # 年干
    year_stem, _ = year_to_ganzhi(year)
    
    # 正月月干
    zheng_stem = YEAR_TO_MONTH_STEM[year_stem]
    
    # 正月是寅月（索引2）
    # 目标月份的地支索引
    # 正月(1) -> 寅(2)，二月(2) -> 卯(3)，...
    target_branch = (ZHENGYUE_BRANCH + month - 1) % 12
    
    # 月干
    target_stem = (zheng_stem + month - 1) % 10
    
    return LiuYue(
        year=year,
        month=month,
        stem=TIANGAN[target_stem],
        stem_index=target_stem,
        branch=DIZHI[target_branch],
        branch_index=target_branch,
        ganzhi=TIANGAN[target_stem] + DIZHI[target_branch],
    )


def get_liuyue_year(year: int) -> list[LiuYue]:
    """获取一整年的流月列表（农历正月到腊月）。"""
    return [get_liuyue(year, m) for m in range(1, 13)]


# ============ 流日 ============

# 参考点
REF_JD_2000 = swe.julday(2000, 1, 1, 0)
# 2000年1月1日是？
# 查万年历：2000-01-01 是 己卯日
# 己=5, 卯=3
REF_DAY_CYCLE_2000 = 15  # 己卯在60甲子中的位置


def get_liuri(year: int, month: int, day: int) -> LiuRi:
    """获取指定公历日的流日干支。"""
    jd = swe.julday(year, month, day, 0)
    
    # 从参考点计算
    days_diff = int(jd - REF_JD_2000)
    cycle_idx = (REF_DAY_CYCLE_2000 + days_diff) % 60
    
    stem, branch = cycle_to_ganzhi_v2(cycle_idx)
    
    return LiuRi(
        year=year,
        month=month,
        day=day,
        stem=TIANGAN[stem],
        stem_index=stem,
        branch=DIZHI[branch],
        branch_index=branch,
        ganzhi=TIANGAN[stem] + DIZHI[branch],
    )


def get_liuri_range(year: int, month: int, start_day: int, end_day: int) -> list[LiuRi]:
    """获取一段时间范围内的流日列表。"""
    result = []
    for d in range(start_day, end_day + 1):
        try:
            result.append(get_liuri(year, month, d))
        except:
            break  # 日期越界
    return result


# ============ 综合查询 ============

def get_liunian_with_liuyue(year: int) -> tuple[LiuNian, list[LiuYue]]:
    """获取指定年的流年及其流月列表。"""
    liunian = get_liunian(year)
    liuyue_list = get_liuyue_year(year)
    return liunian, liuyue_list


def find_liuri_by_ganzhi(target_ganzhi: str, start_year: int, end_year: int) -> list[LiuRi]:
    """
    查找一段时间范围内特定干支的流日。
    用于查找特定日子（如择日）。
    """
    result = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            for day in range(1, 32):
                try:
                    liuri = get_liuri(year, month, day)
                    if liuri.ganzhi == target_ganzhi:
                        result.append(liuri)
                except:
                    continue
    return result
