"""节气计算 —— 八字排盘的核心（年月柱分界）。"""

from __future__ import annotations

import swisseph as swe
from dataclasses import dataclass

from .pillars import JIE_NAMES, get_month_branch_by_jie


@dataclass
class SolarTerm:
    """单个节气的数据。"""
    name: str
    year: int
    month: int
    day: int
    hour: float  # UT，小数小时
    jd: float    # Julian Day


# 八字用的十二节令（决定月柱）
# 太阳黄经度数
JIE_LONGITUDES = [
    315,  # 立春 - 寅月
    345,  # 惊蛰 - 卯月
    15,   # 清明 - 辰月
    45,   # 立夏 - 巳月
    75,   # 芒种 - 午月
    105,  # 小暑 - 未月
    135,  # 立秋 - 申月
    165,  # 白露 - 酉月
    195,  # 寒露 - 戌月
    225,  # 立冬 - 亥月
    255,  # 大雪 - 子月
    285,  # 小寒 - 丑月
]


def find_sun_longitude_jd(target_lon: float, jd_start: float, jd_end: float) -> float:
    """
    二分查找太阳到达指定黄经的 Julian Day。
    
    Args:
        target_lon: 目标黄经（0-360）
        jd_start: 开始搜索的 Julian Day
        jd_end: 结束搜索的 Julian Day
    """
    def sun_lon(jd: float) -> float:
        result, _ = swe.calc_ut(jd, swe.SUN)
        return result[0]  # 黄经（默认黄道坐标）
    
    # 归一化角度差
    def normalize_diff(lon: float, target: float) -> float:
        diff = target - lon
        while diff > 180:
            diff -= 360
        while diff < -180:
            diff += 360
        return diff
    
    # 二分查找
    lo, hi = jd_start, jd_end
    for _ in range(50):  # 足够精度
        mid = (lo + hi) / 2
        lon_mid = sun_lon(mid)
        diff_mid = normalize_diff(lon_mid, target_lon)
        if abs(diff_mid) < 1e-8:
            return mid
        # 判断方向
        lon_lo = sun_lon(lo)
        diff_lo = normalize_diff(lon_lo, target_lon)
        
        if diff_lo * diff_mid < 0:
            hi = mid
        else:
            lo = mid
    
    return (lo + hi) / 2


def get_jieqi_year(year: int) -> list[SolarTerm]:
    """
    获取指定公历年份的所有节令（八字用的十二节）。
    
    注意：八字的年份从立春开始，所以一年的节令可能跨越两个公历年。
    例如 2024 年的八字年份包含：
    - 2024年立春（2024-02-04左右）到 2025年立春前
    
    本函数返回从该年立春开始，到次年立春前的所有节令。
    """
    terms = []
    
    # 搜索范围：上年年底到本年年底
    jd_start = swe.julday(year - 1, 12, 15, 0)
    jd_end = swe.julday(year + 1, 2, 15, 0)
    
    # 找立春（确定八字年份开始）
    # 先粗略找到立春所在的 JD 范围
    # 立春大约在 2月4日左右
    approx_start = swe.julday(year, 2, 1, 0)
    approx_end = swe.julday(year, 2, 10, 0)
    lichun_jd = find_sun_longitude_jd(315, approx_start, approx_end)
    
    # 从这个立春开始，找后续所有节令
    current_jd = lichun_jd
    for i in range(12):
        jie_idx = i % 12
        target_lon = JIE_LONGITUDES[jie_idx]
        
        # 找下一个节令
        jd_start_search = current_jd
        jd_end_search = current_jd + 35  # 节令间隔约30天
        
        jd = find_sun_longitude_jd(target_lon, jd_start_search, jd_end_search)
        
        # 转换回日期
        year_out, month_out, day_out, hour_out = swe.revjul(jd)
        
        terms.append(SolarTerm(
            name=JIE_NAMES[jie_idx],
            year=int(year_out),
            month=int(month_out),
            day=int(day_out),
            hour=float(hour_out),
            jd=jd
        ))
        
        current_jd = jd
    
    return terms


def get_year_start_jd(year: int) -> float:
    """获取指定年的立春 JD（八字年份的开始）。"""
    # 立春大约在 2月4日
    jd_start = swe.julday(year, 2, 1, 0)
    jd_end = swe.julday(year, 2, 10, 0)
    return find_sun_longitude_jd(315, jd_start, jd_end)


def get_month_pillar_by_jd(jd: float, year_start_jd: float) -> tuple[int, int, SolarTerm]:
    """
    根据 JD 确定月柱。
    
    Returns:
        (月干索引, 月支索引, 当前节令信息)
    """
    # 找这个 JD 落在哪个节令之间
    # 先确定是哪个八字年
    jd_lichun = year_start_jd
    
    # 从这个立春开始，找后续的节令
    current_jd = jd_lichun
    prev_term = None
    
    for i in range(13):  # 最多找13个节令（一整年多一点）
        jie_idx = i % 12
        target_lon = JIE_LONGITUDES[jie_idx]
        
        jd_start_search = current_jd
        jd_end_search = current_jd + 35
        
        term_jd = find_sun_longitude_jd(target_lon, jd_start_search, jd_end_search)
        
        year_out, month_out, day_out, hour_out = swe.revjul(term_jd)
        term = SolarTerm(
            name=JIE_NAMES[jie_idx],
            year=int(year_out),
            month=int(month_out),
            day=int(day_out),
            hour=float(hour_out),
            jd=term_jd
        )
        
        if term_jd > jd:
            # 找到了，jd 在 prev_term 和 term 之间
            if prev_term is None:
                # 在立春之前，属于上一年
                # 需要重新计算
                pass
            
            # 确定月支
            month_branch = get_month_branch_by_jie(jie_idx)
            # 月干需要根据年干推算（年上起月法）
            # 这里返回月支，月干在外层计算
            return month_branch, term
        
        prev_term = term
        current_jd = term_jd
    
    # 如果没找到，可能是年底，返回最后一个
    month_branch = get_month_branch_by_jie(11)  # 丑月
    return month_branch, prev_term


def get_exact_month_pillar(jd: float) -> tuple[int, SolarTerm]:
    """
    根据 JD 精确计算月柱。
    
    八字月柱以节令为界，月支由节令决定：
    - 立春(0) -> 寅月(2)  惊蛰(1) -> 卯月(3)  清明(2) -> 辰月(4)  立夏(3) -> 巳月(5)
    - 芒种(4) -> 午月(6)  小暑(5) -> 未月(7)  立秋(6) -> 申月(8)  白露(7) -> 酉月(9)
    - 寒露(8) -> 戌月(10) 立冬(9) -> 亥月(11) 大雪(10) -> 子月(0) 小寒(11) -> 丑月(1)
    
    Returns:
        (月支索引, 节令信息)
    """
    year, month, day, hour = swe.revjul(jd)
    
    # 收集 jd 前后一年左右的节令
    terms = []
    
    # 搜索范围：前一年到后一年
    search_start = swe.julday(year - 1, 1, 1, 0)
    search_end = swe.julday(year + 1, 12, 31, 0)
    
    # 找所有12个节令在搜索范围内的出现
    current_jd = search_start
    for _ in range(30):  # 最多找30个节令（2年多）
        # 找下一个节令
        found = False
        for jie_idx in range(12):
            target_lon = JIE_LONGITUDES[jie_idx]
            try:
                term_jd = find_sun_longitude_jd(target_lon, current_jd, current_jd + 40)
                if term_jd > search_end:
                    break
                
                y, m, d, h = swe.revjul(term_jd)
                term = SolarTerm(
                    name=JIE_NAMES[jie_idx],
                    year=int(y), month=int(m), day=int(d),
                    hour=float(h), jd=term_jd
                )
                terms.append((jie_idx, term_jd, term))
                current_jd = term_jd
                found = True
            except:
                continue
        
        if not found:
            break
    
    # 按时间排序
    terms.sort(key=lambda x: x[1])
    
    # 找到包含 jd 的区间 [term[i], term[i+1])
    for i in range(len(terms)):
        if terms[i][1] > jd:
            # jd 在 terms[i-1] 和 terms[i] 之间
            if i > 0:
                jie_idx = terms[i-1][0]
                month_branch = get_month_branch_by_jie(jie_idx)
                return month_branch, terms[i-1][2]
            else:
                # 在第一个节令之前，用上一个节令（需要处理）
                jie_idx = (terms[i][0] - 1) % 12
                month_branch = get_month_branch_by_jie(jie_idx)
                return month_branch, terms[i][2]
        elif terms[i][1] == jd:
            # 正好在节令时刻
            jie_idx = terms[i][0]
            month_branch = get_month_branch_by_jie(jie_idx)
            return month_branch, terms[i][2]
    
    # 在所有节令之后
    if terms:
        jie_idx = terms[-1][0]
        month_branch = get_month_branch_by_jie(jie_idx)
        return month_branch, terms[-1][2]
    
    # 默认返回寅月
    return 2, SolarTerm("立春", year, 2, 4, 0, jd)


def calc_month_stem(year_stem: int, month_branch: int) -> int:
    """
    根据年干和月支推算月干（年上起月法）。
    
    口诀：
    甲己之年丙作首（甲己年，正月起丙寅）
    乙庚之岁戊为头（乙庚年，正月起戊寅）
    丙辛之岁寻庚上（丙辛年，正月起庚寅）
    丁壬壬位顺行流（丁壬年，正月起壬寅）
    若问戊癸何处起，甲寅之上好追求（戊癸年，正月起甲寅）
    
    注意：正月是寅月（索引2）
    """
    # 确定正月的月干
    if year_stem in [0, 5]:    # 甲己
        zheng_stem = 2  # 丙
    elif year_stem in [1, 6]:  # 乙庚
        zheng_stem = 4  # 戊
    elif year_stem in [2, 7]:  # 丙辛
        zheng_stem = 6  # 庚
    elif year_stem in [3, 8]:  # 丁壬
        zheng_stem = 8  # 壬
    else:                      # 戊癸
        zheng_stem = 0  # 甲
    
    # 正月是寅月（索引2）
    # 月支到正月的偏移
    offset = (month_branch - 2) % 12
    return (zheng_stem + offset) % 10
