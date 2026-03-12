"""八字核心计算 —— 四柱排盘。"""

from __future__ import annotations

import swisseph as swe
from dataclasses import dataclass, field

from ..core.ephemeris import GeoLocation
from ..core.timezone import get_timezone, local_to_ut
from .pillars import (
    TIANGAN, DIZHI, 
    hour_to_shichen, get_shichen_ganzhi,
    tg_element, dz_element, tg_yin, dz_yin,
)
from .daypillar import get_day_pillar, apply_true_solar_time
from .solarterm import (
    get_exact_month_pillar, calc_month_stem,
    get_year_start_jd, find_sun_longitude_jd, JIE_NAMES
)
from .shishen import get_shishen, get_canggan_with_shishen


@dataclass
class Pillar:
    """单个柱（年柱、月柱、日柱、时柱）。"""
    name: str           # 柱名
    stem: str           # 天干
    stem_index: int     # 天干索引
    branch: str         # 地支
    branch_index: int   # 地支索引
    ganzhi: str         # 干支组合
    
    # 附加信息
    element: str = ""           # 纳音五行（简化版用天干+地支五行）
    yin_yang: str = ""          # 阴阳
    shishen_stem: str = ""      # 天干十神（相对于日主）
    shishen_branch: str = ""    # 地支十神（相对于日主）
    canggan: list = field(default_factory=list)  # 藏干 [{qi, stem, shishen}, ...]


@dataclass
class BaZi:
    """八字命盘。"""
    # 四柱
    year_pillar: Pillar
    month_pillar: Pillar
    day_pillar: Pillar
    hour_pillar: Pillar
    
    # 日主信息
    day_master: str          # 日主天干
    day_master_index: int    # 日主索引
    day_master_element: str  # 日主五行
    day_master_yin: bool     # 日主阴阳
    
    # 出生信息
    year: int
    month: int
    day: int
    hour: float
    location: GeoLocation | None = None
    
    # 选项
    use_true_solar_time: bool = False
    use_split_zi: bool = False
    
    @property
    def pillars(self) -> list[Pillar]:
        """返回四柱列表。"""
        return [self.year_pillar, self.month_pillar, self.day_pillar, self.hour_pillar]
    
    @property
    def all_branches(self) -> list[int]:
        """返回所有地支索引。"""
        return [p.branch_index for p in self.pillars]
    
    @property
    def all_stems(self) -> list[int]:
        """返回所有天干索引。"""
        return [p.stem_index for p in self.pillars]


def calculate_bazi(
    year: int,
    month: int,
    day: int,
    hour: float,
    location: GeoLocation | None = None,
    use_true_solar_time: bool = True,
    use_split_zi: bool = False,
) -> BaZi:
    """
    计算八字四柱。
    
    Args:
        year, month, day: 公历日期
        hour: 小时（0-24，本地时间）
        location: 地理位置（用于真太阳时计算）
        use_true_solar_time: 是否使用真太阳时
        use_split_zi: 是否分早晚子时
    
    Returns:
        BaZi 对象
    """
    # 应用真太阳时
    if use_true_solar_time and location is not None:
        tz = get_timezone(location)
        # 先转 UT
        uy, um, ud, hour_ut = local_to_ut(year, month, day, hour, tz)
        # 真太阳时计算（简化版，基于经度）
        # 经度时差：每度4分钟
        longitude_offset = (location.lon - 120.0) / 15.0  # 小时
        hour_true = hour + longitude_offset
        
        # 处理日期跨越
        if hour_true >= 24:
            jd = swe.julday(year, month, day, hour)
            jd_new = jd + longitude_offset / 24.0
            y, m, d, h = swe.revjul(jd_new)
            year, month, day = int(y), int(m), int(d)
            hour = float(h)
        elif hour_true < 0:
            jd = swe.julday(year, month, day, hour)
            jd_new = jd + longitude_offset / 24.0
            y, m, d, h = swe.revjul(jd_new)
            year, month, day = int(y), int(m), int(d)
            hour = float(h)
        else:
            hour = hour_true
    
    # 计算 JD（用于日柱和节气）
    # 使用真太阳时校正后的日期时间
    jd = swe.julday(year, month, day, hour)
    
    # ========== 年柱 ==========
    # 年柱以立春为界
    # 找立春
    lichun_jd = get_year_start_jd(year)
    
    # 如果在立春之前，属于上一年
    if jd < lichun_jd:
        lichun_jd = get_year_start_jd(year - 1)
        year_gan_idx = (year - 1 - 4) % 10  # 1984甲子，(year-4)%10
        year_zhi_idx = (year - 1 - 4) % 12
    else:
        year_gan_idx = (year - 4) % 10
        year_zhi_idx = (year - 4) % 12
    
    year_gan_idx = year_gan_idx % 10
    year_zhi_idx = year_zhi_idx % 12
    
    # ========== 日柱 ==========
    day_gan_idx, day_zhi_idx = get_day_pillar(jd)
    
    # ========== 时柱 ==========
    # 判断时辰（考虑早晚子时）
    if use_split_zi and (hour >= 23 or hour < 1):
        # 早晚子时处理
        if hour >= 23:
            # 晚子时，日干不变
            shichen_name, shichen_idx = "子", 0
        else:
            # 早子时，日干已经是新的一天
            shichen_name, shichen_idx = "子", 0
    else:
        shichen_name, shichen_idx = hour_to_shichen(hour, use_split_zi)
    
    # 时干由日干推算
    hour_gan_idx, hour_zhi_idx = get_shichen_ganzhi(day_gan_idx, shichen_idx)
    
    # ========== 月柱 ==========
    # 月柱以节令为界
    month_zhi_idx, term_info = get_exact_month_pillar(jd)
    month_gan_idx = calc_month_stem(year_gan_idx, month_zhi_idx)
    
    # ========== 构建 Pillar 对象 ==========
    
    # 日主（用于十神计算）
    day_master_idx = day_gan_idx
    
    def make_pillar(name: str, stem_idx: int, branch_idx: int) -> Pillar:
        stem_shishen = get_shishen(day_master_idx, stem_idx) if name != "日柱" else "日主"
        branch_shishen = get_shishen(day_master_idx, 0)  # 简化，实际需要藏干主气
        # 获取藏干
        canggan = get_canggan_with_shishen(day_master_idx, branch_idx)
        
        return Pillar(
            name=name,
            stem=TIANGAN[stem_idx],
            stem_index=stem_idx,
            branch=DIZHI[branch_idx],
            branch_index=branch_idx,
            ganzhi=TIANGAN[stem_idx] + DIZHI[branch_idx],
            element=f"{tg_element(stem_idx)}{dz_element(branch_idx)}",
            yin_yang="阳" if tg_yin(stem_idx) else "阴",
            shishen_stem=stem_shishen,
            shishen_branch=canggan[0]["shishen"] if canggan else "",
            canggan=canggan,
        )
    
    year_pillar = make_pillar("年柱", year_gan_idx, year_zhi_idx)
    month_pillar = make_pillar("月柱", month_gan_idx, month_zhi_idx)
    day_pillar = make_pillar("日柱", day_gan_idx, day_zhi_idx)
    hour_pillar = make_pillar("时柱", hour_gan_idx, hour_zhi_idx)
    
    return BaZi(
        year_pillar=year_pillar,
        month_pillar=month_pillar,
        day_pillar=day_pillar,
        hour_pillar=hour_pillar,
        day_master=TIANGAN[day_master_idx],
        day_master_index=day_master_idx,
        day_master_element=tg_element(day_master_idx),
        day_master_yin=tg_yin(day_master_idx),
        year=year,
        month=month,
        day=day,
        hour=hour,
        location=location,
        use_true_solar_time=use_true_solar_time,
        use_split_zi=use_split_zi,
    )


def get_bazi_summary(bazi: BaZi) -> dict:
    """获取八字的摘要信息。"""
    return {
        "四柱": [p.ganzhi for p in bazi.pillars],
        "日主": bazi.day_master,
        "日主五行": bazi.day_master_element,
        "日主阴阳": "阳" if bazi.day_master_yin else "阴",
    }
