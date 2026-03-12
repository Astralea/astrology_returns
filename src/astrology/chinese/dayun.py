"""大运排法 —— 十年一大运，预测人生起伏。"""

from __future__ import annotations

import swisseph as swe
from dataclasses import dataclass

from .pillars import TIANGAN, DIZHI, cycle_to_ganzhi_v2
from .solarterm import get_year_start_jd, find_sun_longitude_jd, JIE_LONGITUDES


@dataclass
class DaYun:
    """大运柱。"""
    index: int           # 第几运（0起）
    age_start: float     # 起运年龄
    age_end: float       # 结束年龄
    year_start: int      # 开始年份
    year_end: int        # 结束年份
    stem: str            # 天干
    stem_index: int      # 天干索引
    branch: str          # 地支
    branch_index: int    # 地支索引
    ganzhi: str          # 干支
    is_forward: bool     # 顺行还是逆行


def calculate_dayun_start(
    birth_jd: float,
    year_stem: int,
    is_male: bool = True,
) -> tuple[bool, float, float]:
    """
    计算起运方向、起运岁数、起运 JD。
    
    规则：
    - 阳年（甲丙戊庚壬）男命顺行，女命逆行
    - 阴年（乙丁己辛癸）男命逆行，女命顺行
    
    Returns:
        (是否顺行, 起运年龄, 起运 JD)
    """
    # 判断年干阴阳（甲丙戊庚壬为阳 0,2,4,6,8）
    is_yang_year = year_stem % 2 == 0
    
    # 确定顺逆
    if is_yang_year:
        is_forward = is_male
    else:
        is_forward = not is_male
    
    # 计算起运时间
    # 找最近的节令
    year, month, day, hour = swe.revjul(birth_jd)
    
    # 找出生年立春
    lichun_jd = get_year_start_jd(int(year))
    
    # 确定从出生到下一个节令（或上一个节令）的时间
    if is_forward:
        # 顺行：从出生到下一个节令
        # 找下一个节令
        current_jd = birth_jd
        next_jie_jd = None
        
        # 从出生日开始往后找节令
        for days in range(1, 60):  # 最多找60天
            check_jd = birth_jd + days
            # 检查是否过了节令
            # 简化：计算太阳黄经，看是否跨越了节令点
            result, _ = swe.calc_ut(check_jd, swe.SUN, swe.FLG_EQUATORIAL)
            lon = result[0]
            
            # 检查是否跨过某个节令点
            for jie_lon in JIE_LONGITUDES:
                result_prev, _ = swe.calc_ut(check_jd - 1, swe.SUN, swe.FLG_EQUATORIAL)
                prev_lon = result_prev[0]
                
                # 归一化角度
                diff_prev = (prev_lon - jie_lon + 360) % 360
                diff_curr = (lon - jie_lon + 360) % 360
                
                if diff_prev > diff_curr and diff_curr < 1:  # 跨过节令点
                    next_jie_jd = check_jd
                    break
            
            if next_jie_jd:
                break
        
        if next_jie_jd is None:
            next_jie_jd = birth_jd + 30  # fallback
        
        # 起运时间 = 出生时间 + (到节令的时间差 * 3)
        # 三天折合一岁，一天折合四个月，一个时辰（2小时）折合十天
        days_to_jie = next_jie_jd - birth_jd
        years_to_start = days_to_jie / 3.0  # 三天一岁
        
        start_age = years_to_start
        start_jd = birth_jd + days_to_jie * 3  # 起运 JD
        
    else:
        # 逆行：从出生到上一个节令
        prev_jie_jd = None
        
        for days in range(1, 60):
            check_jd = birth_jd - days
            result, _ = swe.calc_ut(check_jd, swe.SUN, swe.FLG_EQUATORIAL)
            lon = result[0]
            
            for jie_lon in JIE_LONGITUDES:
                result_next, _ = swe.calc_ut(check_jd + 1, swe.SUN, swe.FLG_EQUATORIAL)
                next_lon = result_next[0]
                
                diff_next = (next_lon - jie_lon + 360) % 360
                diff_curr = (lon - jie_lon + 360) % 360
                
                if diff_next > diff_curr and diff_curr < 1:
                    prev_jie_jd = check_jd
                    break
            
            if prev_jie_jd:
                break
        
        if prev_jie_jd is None:
            prev_jie_jd = birth_jd - 30
        
        days_from_jie = birth_jd - prev_jie_jd
        years_to_start = days_from_jie / 3.0
        
        start_age = years_to_start
        start_jd = birth_jd + days_from_jie * 3
    
    return is_forward, start_age, start_jd


def calculate_dayun(
    birth_jd: float,
    year_stem: int,
    year_branch: int,
    month_stem: int,
    month_branch: int,
    is_male: bool = True,
    num_yun: int = 8,
) -> list[DaYun]:
    """
    计算大运。
    
    Args:
        birth_jd: 出生时间的 Julian Day
        year_stem: 年干索引
        year_branch: 年支索引
        month_stem: 月干索引
        month_branch: 月支索引
        is_male: 是否男性
        num_yun: 计算多少步大运（默认8步，80年）
    
    Returns:
        大运列表
    """
    is_forward, start_age, start_jd = calculate_dayun_start(birth_jd, year_stem, is_male)
    
    # 大运从月柱开始顺排或逆排
    # 第一步大运的干支 = 月柱顺推或逆推一位
    
    dayun_list = []
    
    for i in range(num_yun):
        if is_forward:
            # 顺行：月柱 + i + 1
            cycle_idx = (month_stem + i + 1) % 10  # 这不完全对，需要整体60甲子推进
            # 更准确的算法
            from .pillars import get_cycle_index
            month_cycle = get_cycle_index(month_stem, month_branch)
            if month_cycle is None:
                month_cycle = 0
            new_cycle = (month_cycle + i + 1) % 60
            stem, branch = cycle_to_ganzhi_v2(new_cycle)
        else:
            # 逆行：月柱 - i - 1
            from .pillars import get_cycle_index
            month_cycle = get_cycle_index(month_stem, month_branch)
            if month_cycle is None:
                month_cycle = 0
            new_cycle = (month_cycle - i - 1) % 60
            stem, branch = cycle_to_ganzhi_v2(new_cycle)
        
        # 计算时间范围
        yun_start_age = start_age + i * 10
        yun_end_age = yun_start_age + 10
        
        # 计算年份
        birth_year, _, _, _ = swe.revjul(birth_jd)
        year_start = int(birth_year + yun_start_age)
        year_end = int(birth_year + yun_end_age)
        
        dayun_list.append(DaYun(
            index=i,
            age_start=yun_start_age,
            age_end=yun_end_age,
            year_start=year_start,
            year_end=year_end,
            stem=TIANGAN[stem],
            stem_index=stem,
            branch=DIZHI[branch],
            branch_index=branch,
            ganzhi=TIANGAN[stem] + DIZHI[branch],
            is_forward=is_forward,
        ))
    
    return dayun_list


# ============ 简化版大运计算 ============

def calculate_dayun_simple(
    birth_jd: float,
    year_stem: int,
    month_stem: int,
    month_branch: int,
    is_male: bool = True,
    num_yun: int = 8,
) -> list[DaYun]:
    """
    简化版大运计算（更稳定的实现）。
    """
    # 判断顺逆
    is_yang_year = year_stem % 2 == 0
    is_forward = is_yang_year if is_male else not is_yang_year
    
    # 简化的起运岁数（示例值，实际需要精确计算）
    start_age = 3.0  # 默认3岁起运
    
    dayun_list = []
    
    for i in range(num_yun):
        if is_forward:
            new_stem = (month_stem + i + 1) % 10
            new_branch = (month_branch + i + 1) % 12
        else:
            new_stem = (month_stem - i - 1) % 10
            new_branch = (month_branch - i - 1) % 12
        
        # 修正阴阳匹配
        if new_stem % 2 != new_branch % 2:
            new_branch = (new_branch + 6) % 12
        
        yun_start_age = start_age + i * 10
        yun_end_age = yun_start_age + 10
        
        birth_year, _, _, _ = swe.revjul(birth_jd)
        year_start = int(birth_year + yun_start_age)
        year_end = int(birth_year + yun_end_age)
        
        dayun_list.append(DaYun(
            index=i,
            age_start=yun_start_age,
            age_end=yun_end_age,
            year_start=year_start,
            year_end=year_end,
            stem=TIANGAN[new_stem],
            stem_index=new_stem,
            branch=DIZHI[new_branch],
            branch_index=new_branch,
            ganzhi=TIANGAN[new_stem] + DIZHI[new_branch],
            is_forward=is_forward,
        ))
    
    return dayun_list
