"""十神系统 —— 八字论命的核心。"""

from __future__ import annotations

from .pillars import TIANGAN, DIZHI, tg_element, tg_yin


# 十神名称
SHISHEN_NAMES = ["比肩", "劫财", "食神", "伤官", "偏财", "正财", "七杀", "正官", "偏印", "正印"]

# 五行生克关系
# 木火土金水 01234
ELEMENT_INDEX = {"木": 0, "火": 1, "土": 2, "金": 3, "水": 4}


def get_element_index(element: str) -> int:
    """获取五行索引。"""
    return ELEMENT_INDEX.get(element, -1)


def is_generates(element1: str, element2: str) -> bool:
    """
    判断 element1 是否生 element2。
    五行相生：木(0)->火(1)->土(2)->金(3)->水(4)->木(0)
    """
    e1 = get_element_index(element1)
    e2 = get_element_index(element2)
    if e1 == -1 or e2 == -1:
        return False
    return (e1 + 1) % 5 == e2


def is_overcomes(element1: str, element2: str) -> bool:
    """
    判断 element1 是否克 element2。
    五行相克：木(0)->土(2)->水(4)->火(1)->金(3)->木(0)
    """
    e1 = get_element_index(element1)
    e2 = get_element_index(element2)
    if e1 == -1 or e2 == -1:
        return False
    # 木克土(0->2), 土克水(2->4), 水克火(4->1), 火克金(1->3), 金克木(3->0)
    mapping = {0: 2, 2: 4, 4: 1, 1: 3, 3: 0}
    return mapping.get(e1, -1) == e2


def get_shishen(day_stem: int, target_stem: int) -> str:
    """
    根据日干和目标天干确定十神。
    
    Args:
        day_stem: 日干索引（0-9）
        target_stem: 目标天干索引（0-9）
    
    Returns:
        十神名称
    """
    if day_stem == target_stem:
        return "比肩"
    
    day_element = tg_element(day_stem)
    day_yin = tg_yin(day_stem)
    target_element = tg_element(target_stem)
    target_yin = tg_yin(target_stem)
    
    same_yin = (day_yin == target_yin)
    
    # 生我者为印（同阴阳为偏印/枭神，异阴阳为正印）
    if is_generates(target_element, day_element):
        return "偏印" if same_yin else "正印"
    
    # 我生者为食伤（同阴阳为食神，异阴阳为伤官）
    if is_generates(day_element, target_element):
        return "食神" if same_yin else "伤官"
    
    # 克我者为官杀（同阴阳为七杀/偏官，异阴阳为正官）
    if is_overcomes(target_element, day_element):
        return "七杀" if same_yin else "正官"
    
    # 我克者为财（同阴阳为偏财，异阴阳为正财）
    if is_overcomes(day_element, target_element):
        return "偏财" if same_yin else "正财"
    
    # 同我者为比劫（同阴阳为比肩，异阴阳为劫财）
    if target_element == day_element:
        return "劫财" if same_yin else "比肩"
    
    return "未知"


def get_shishen_for_ganzhi(day_stem: int, target_stem: int, target_branch: int) -> tuple[str, str]:
    """
    获取干支的十神。
    
    Returns:
        (天干十神, 地支十神)
    """
    from .pillars import dz_element
    
    # 天干十神
    stem_shishen = get_shishen(day_stem, target_stem)
    
    # 地支十神（以地支藏干的主气来定，简化版直接用本气）
    # 地支藏干比较复杂，这里先简化
    branch_element = dz_element(target_branch)
    # 需要找一个具有该五行的天干来确定十神
    # 简化：地支的十神按其本气的五行来推算
    # 实际应该看藏干的主气
    
    # 地支藏干主气（本气）
    # 子(癸水), 丑(己土), 寅(甲木), 卯(乙木), 辰(戊土), 巳(丙火)
    # 午(丁火), 未(己土), 申(庚金), 酉(辛金), 戌(戊土), 亥(壬水)
    zhuqi = [9, 5, 0, 1, 4, 2, 3, 5, 6, 7, 4, 8]  # 对应天干索引
    
    branch_stem = zhuqi[target_branch]
    branch_shishen = get_shishen(day_stem, branch_stem)
    
    return stem_shishen, branch_shishen


def get_shishen_index(shishen: str) -> int:
    """获取十神索引。"""
    mapping = {
        "比肩": 0, "劫财": 1,
        "食神": 2, "伤官": 3,
        "偏财": 4, "正财": 5,
        "七杀": 6, "正官": 7,
        "偏印": 8, "正印": 9,
        "枭神": 8,  # 偏印别名
    }
    return mapping.get(shishen, -1)


# ============ 藏干 ============

# 地支藏干表（主气、中气、余气）
DZ_CANGGAN = {
    0: [9, 0, 0],   # 子：癸、无、无
    1: [5, 7, 9],   # 丑：己、辛、癸
    2: [0, 2, 4],   # 寅：甲、丙、戊
    3: [1, 0, 0],   # 卯：乙
    4: [4, 1, 9],   # 辰：戊、乙、癸
    5: [2, 6, 4],   # 巳：丙、庚、戊
    6: [3, 5, 0],   # 午：丁、己、无
    7: [5, 3, 1],   # 未：己、丁、乙
    8: [6, 8, 4],   # 申：庚、壬、戊
    9: [7, 0, 0],   # 酉：辛
    10: [4, 3, 7],  # 戌：戊、辛、丁
    11: [8, 0, 0],  # 亥：壬
}


def get_canggan(branch_index: int) -> list[tuple[int, str]]:
    """
    获取地支藏干及其十神描述。
    
    Returns:
        [(天干索引, 十神描述), ...]
    """
    stems = DZ_CANGGAN.get(branch_index, [])
    result = []
    for stem in stems:
        if stem > 0:
            result.append((stem, TIANGAN[stem]))
    return result


def get_canggan_with_shishen(day_stem: int, branch_index: int) -> list[dict]:
    """
    获取地支藏干及其十神。
    
    Returns:
        [{"stem": 天干, "shishen": 十神}, ...]
    """
    stems = DZ_CANGGAN.get(branch_index, [])
    result = []
    qi_names = ["本气", "中气", "余气"]
    
    for i, stem in enumerate(stems):
        if stem > 0 or i == 0:  # 至少要有主气
            ss = get_shishen(day_stem, stem) if stem > 0 else "未知"
            result.append({
                "qi": qi_names[i] if i < 3 else "杂气",
                "stem_index": stem,
                "stem": TIANGAN[stem] if stem >= 0 else "?",
                "shishen": ss
            })
    
    return result
