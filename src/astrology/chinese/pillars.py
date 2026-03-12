"""天干地支数据与基础计算 —— 八字四柱的基石。"""

from __future__ import annotations

# ============ 基础数据 ============

TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 五行
def tg_element(index: int) -> str:
    """天干五行：甲乙木、丙丁火、戊己土、庚辛金、壬癸水。"""
    return ["木", "木", "火", "火", "土", "土", "金", "金", "水", "水"][index]

def dz_element(index: int) -> str:
    """地支五行：寅卯木、巳午火、申酉金、亥子水、辰戌丑未土。"""
    return ["水", "土", "木", "木", "土", "火", "火", "土", "金", "金", "土", "水"][index]

# 阴阳
def tg_yin(index: int) -> bool:
    """天干阴阳：奇数为阳，偶数为阴（0-indexed：偶阳奇阴）。"""
    return index % 2 == 0

def dz_yin(index: int) -> bool:
    """地支阴阳：同上。"""
    return index % 2 == 0

# ============ 六十甲子 ============

def get_ganzhi(stem_index: int, branch_index: int) -> str | None:
    """
    获取干支组合。阴阳相配才合法（阳干配阳支，阴干配阴支）。
    返回 None 表示不配。
    """
    if stem_index % 2 != branch_index % 2:
        return None
    return TIANGAN[stem_index] + DIZHI[branch_index]

def get_cycle_index(stem_index: int, branch_index: int) -> int | None:
    """
    获取干支在六十甲子中的序号（0-59）。
    非法组合返回 None。
    """
    if stem_index % 2 != branch_index % 2:
        return None
    # 甲子=0, 甲戌=10, 甲申=20, 甲午=30, 甲辰=40, 甲寅=50
    for i in range(6):
        if (stem_index - i * 2) % 10 == 0:  # 找到对应的甲周期
            return i * 10 + branch_index // 2
    return None

def cycle_to_ganzhi(cycle_index: int) -> tuple[int, int]:
    """六十甲子序号转干支索引。"""
    cycle_index = cycle_index % 60
    # 地支每两个进一位，天干每十个进一位
    branch_index = (cycle_index % 12) * 2 % 12
    if cycle_index >= 50:
        branch_index = 2  # 甲寅
    elif cycle_index >= 40:
        branch_index = 4  # 甲辰
    elif cycle_index >= 30:
        branch_index = 6  # 甲午
    elif cycle_index >= 20:
        branch_index = 8  # 甲申
    elif cycle_index >= 10:
        branch_index = 10  # 甲戌
    else:
        branch_index = 0  # 甲子
    
    stem_index = cycle_index % 10
    # 调整地支使其与天干同阴阳
    if stem_index % 2 != branch_index % 2:
        branch_index = (branch_index + 6) % 12
    return stem_index, branch_index

# 更简洁的算法
def cycle_to_ganzhi_v2(cycle_index: int) -> tuple[int, int]:
    """六十甲子序号转干支索引（v2，正确版本）。"""
    cycle_index = cycle_index % 60
    # 天干每10一循环
    stem_index = cycle_index % 10
    # 地支每12一循环，但要保持阴阳一致
    # 甲子(0): 子=0, 甲戌(10): 戌=10, 甲申(20): 申=8, 甲午(30): 午=6, 甲辰(40): 辰=4, 甲寅(50): 寅=2
    branch_index = (cycle_index % 12)
    # 检查阴阳是否匹配
    if stem_index % 2 != branch_index % 2:
        branch_index = (branch_index + 6) % 12
    return stem_index, branch_index

# ============ 六十甲子表（用于对照） ============

GANZHI_60 = []
for i in range(60):
    s, b = cycle_to_ganzhi_v2(i)
    GANZHI_60.append(TIANGAN[s] + DIZHI[b])

# ============ 十二时辰 ============

SHICHEN = [
    ("子", 23, 1),   # 23:00-01:00
    ("丑", 1, 3),    # 01:00-03:00
    ("寅", 3, 5),    # 03:00-05:00
    ("卯", 5, 7),    # 05:00-07:00
    ("辰", 7, 9),    # 07:00-09:00
    ("巳", 9, 11),   # 09:00-11:00
    ("午", 11, 13),  # 11:00-13:00
    ("未", 13, 15),  # 13:00-15:00
    ("申", 15, 17),  # 15:00-17:00
    ("酉", 17, 19),  # 17:00-19:00
    ("戌", 19, 21),  # 19:00-21:00
    ("亥", 21, 23),  # 21:00-23:00
]

def hour_to_shichen(hour: float, use_split_zi: bool = False) -> tuple[str, int]:
    """
    将小时（0-24）转换为时辰。
    
    Args:
        hour: 小时数（如 23.5 表示 23:30）
        use_split_zi: 是否分早晚子时。True 时 0-1 点为早子时，23-24 点为晚子时（都为子时但日干不同）
    
    Returns:
        (时辰名, 时辰索引 0-11)
    """
    h = int(hour)
    for i, (name, start, end) in enumerate(SHICHEN):
        if start < end:  # 正常时段
            if start <= h < end:
                return name, i
        else:  # 跨午夜（子时）
            if h >= start or h < end:
                return name, i
    return "子", 0  # fallback

def get_shichen_ganzhi(day_stem: int, shichen_index: int) -> tuple[int, int]:
    """
    根据日干和时辰索引推算时柱干支。
    
    口诀：
    甲己还加甲（甲己日从甲子起）
    乙庚丙作初（乙庚日从丙子起）
    丙辛从戊起（丙辛日从戊子起）
    丁壬庚子居（丁壬日从庚子起）
    戊癸何方发，壬子是真途（戊癸日从壬子起）
    """
    # 确定子时天干
    if day_stem in [0, 5]:    # 甲己
        zi_stem = 0  # 甲
    elif day_stem in [1, 6]:  # 乙庚
        zi_stem = 2  # 丙
    elif day_stem in [2, 7]:  # 丙辛
        zi_stem = 4  # 戊
    elif day_stem in [3, 8]:  # 丁壬
        zi_stem = 6  # 庚
    else:                      # 戊癸
        zi_stem = 8  # 壬
    
    # 时辰天干 = 子时天干 + 时辰索引
    hour_stem = (zi_stem + shichen_index) % 10
    hour_branch = shichen_index
    return hour_stem, hour_branch

# ============ 节气数据 ============

JIEQI_LONGITUDES = [
    315,  # 立春
    330,  # 惊蛰（实际上是345，但传统八字月柱用"节"）
    345,  # 惊蛰
    0,    # 清明（实际上是15）
    15,   # 清明
    30,   # 立夏
    45,   # 芒种
    60,   # 小暑
    75,   # 立秋
    90,   # 白露
    105,  # 寒露
    120,  # 立冬
    135,  # 大雪
    150,  # 小寒
]

# 八字用十二节令（决定月柱）
# 正月寅：立春
# 二月卯：惊蛰
# 三月辰：清明
# 四月巳：立夏
# 五月午：芒种
# 六月未：小暑
# 七月申：立秋
# 八月酉：白露
# 九月戌：寒露
# 十月亥：立冬
# 十一月子：大雪
# 十二月丑：小寒

JIE_NAMES = ["立春", "惊蛰", "清明", "立夏", "芒种", "小暑", 
             "立秋", "白露", "寒露", "立冬", "大雪", "小寒"]

# 地支对应的月份（正月建寅）
DZ_MONTH = [11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # 子丑寅卯辰巳午未申酉戌亥 -> 月支索引

def get_month_branch_by_jie(jie_index: int) -> int:
    """
    根据节令索引获取月支。
    立春(0)->寅(2), 惊蛰(1)->卯(3), ...
    """
    # 正月建寅，所以立春是寅月
    return (jie_index + 2) % 12

# ============ 年份对应年干（快速计算） ============

def year_to_ganzhi(year: int) -> tuple[int, int]:
    """
    年份转干支索引。
    以 1984 年（甲子年）为参考点。
    """
    # 1984 是甲子（0）
    cycle = (year - 1984) % 60
    return cycle_to_ganzhi_v2(cycle)
