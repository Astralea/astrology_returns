"""日柱计算 —— 干支纪日（60日周期）。"""

from __future__ import annotations

import swisseph as swe

from .pillars import cycle_to_ganzhi_v2, TIANGAN, DIZHI


# 参考点：1900-01-01 是甲戌日（cycle index 10）
# 查证来源：万年历数据
REF_JD = swe.julday(1900, 1, 1, 0)  # 1900年1月1日 0h UT
REF_CYCLE = 10  # 甲戌


def get_day_pillar(jd: float) -> tuple[int, int]:
    """
    根据 Julian Day 计算日柱。
    
    Returns:
        (日干索引, 日支索引)
    """
    # 计算距离参考点的天数
    days_diff = int(jd - REF_JD)
    cycle_index = (REF_CYCLE + days_diff) % 60
    return cycle_to_ganzhi_v2(cycle_index)


def get_day_pillar_for_datetime(year: int, month: int, day: int, hour_ut: float) -> tuple[int, int]:
    """
    根据日期时间计算日柱。
    
    注意：八字日柱以子时为界（23:00），但日干在子时更换。
    """
    jd = swe.julday(year, month, day, hour_ut)
    return get_day_pillar(jd)


# ============ 真太阳时 ============

def get_true_solar_time_offset(longitude: float, timezone_offset: float) -> float:
    """
    计算真太阳时与平太阳时的差值（小时）。
    
    真太阳时 = 平太阳时 + 经度时差 + 均时差
    
    Args:
        longitude: 经度（东经为正）
        timezone_offset: 时区偏移（小时，如东八区为 8）
    
    Returns:
        偏移小时数（需要加到平太阳时上）
    """
    # 经度时差：每度4分钟（240秒）
    # 东经120度是东八区中央经线
    longitude_offset_hours = (longitude - 120.0) / 15.0  # 小时
    
    return longitude_offset_hours


def get_equation_of_time(jd: float) -> float:
    """
    计算均时差（Equation of Time）。
    
    由于地球轨道是椭圆，真太阳时和平太阳时有差异。
    公式简化版，误差在几秒以内。
    
    Returns:
        均时差（小时），真太阳比平太阳快时为正
    """
    import math
    
    # 计算太阳黄经
    result, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_EQUATORIAL)
    sun_lon = result[0]  # 黄经
    
    # 计算太阳平黄经（近似）
    # JD 2451545.0 是 2000-01-01 12:00 UT（J2000）
    n = jd - 2451545.0
    # 太阳平黄经
    L0 = (280.46061837 + 0.98564736629 * n) % 360
    
    # 均时差近似公式（度转小时）
    eot_deg = sun_lon - L0
    # 归一化到 -180 到 180
    while eot_deg > 180:
        eot_deg -= 360
    while eot_deg < -180:
        eot_deg += 360
    
    eot_hours = eot_deg / 15.0  # 度转小时（每小时15度）
    
    return eot_hours


def apply_true_solar_time(
    year: int, month: int, day: int, hour: float,
    longitude: float, timezone_offset: float
) -> tuple[int, int, int, float]:
    """
    将平太阳时转换为真太阳时。
    
    Args:
        year, month, day: 日期
        hour: 小时（平太阳时）
        longitude: 经度（东经为正）
        timezone_offset: 时区偏移（小时）
    
    Returns:
        (年, 月, 日, 真太阳时小时)
    """
    jd = swe.julday(year, month, day, hour)
    
    # 经度时差
    longitude_offset = (longitude - 120.0) / 15.0
    
    # 均时差
    eot = get_equation_of_time(jd)
    
    # 总偏移
    total_offset = longitude_offset + eot
    
    # 应用偏移
    true_hour = hour + total_offset
    
    # 处理日期跨越
    if true_hour >= 24:
        # 加一天
        jd_new = jd + (true_hour - hour) / 24.0
        y, m, d, h = swe.revjul(jd_new)
        return int(y), int(m), int(d), float(h)
    elif true_hour < 0:
        # 减一天
        jd_new = jd + (true_hour - hour) / 24.0
        y, m, d, h = swe.revjul(jd_new)
        return int(y), int(m), int(d), float(h)
    
    return year, month, day, true_hour


# ============ 完整日柱信息 ============

def get_full_day_pillar_info(jd: float) -> dict:
    """获取日柱的完整信息。"""
    stem, branch = get_day_pillar(jd)
    
    from .pillars import tg_element, dz_element, tg_yin, dz_yin
    
    return {
        "ganzhi": TIANGAN[stem] + DIZHI[branch],
        "stem": TIANGAN[stem],
        "stem_index": stem,
        "branch": DIZHI[branch],
        "branch_index": branch,
        "stem_element": tg_element(stem),
        "branch_element": dz_element(branch),
        "stem_yin": tg_yin(stem),
        "branch_yin": dz_yin(branch),
    }
