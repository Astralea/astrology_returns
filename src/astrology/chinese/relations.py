"""地支关系 —— 刑、冲、合、害、破、三合、六合等。"""

from __future__ import annotations

from .pillars import DIZHI


# ============ 六合 ============
# 子丑合土，寅亥合木，卯戌合火，辰酉合金，巳申合水，午未合土
LIUHE = {
    0: 1,   # 子合丑
    1: 0,   # 丑合子
    2: 11,  # 寅合亥
    3: 10,  # 卯合戌
    4: 9,   # 辰合酉
    5: 8,   # 巳合申
    6: 7,   # 午合未
    7: 6,   # 未合午
    8: 5,   # 申合巳
    9: 4,   # 酉合辰
    10: 3,  # 戌合卯
    11: 2,  # 亥合寅
}

LIUHE_ELEMENT = {
    (0, 1): "土",   # 子丑
    (2, 11): "木",  # 寅亥
    (3, 10): "火",  # 卯戌
    (4, 9): "金",   # 辰酉
    (5, 8): "水",   # 巳申
    (6, 7): "土",   # 午未
}

def get_liuhe(branch: int) -> int | None:
    """获取地支的六合对象。"""
    return LIUHE.get(branch)

def is_liuhe(b1: int, b2: int) -> bool:
    """判断两个地支是否相合。"""
    return LIUHE.get(b1) == b2

def get_liuhe_element(b1: int, b2: int) -> str | None:
    """获取六合的五行属性。"""
    if b1 > b2:
        b1, b2 = b2, b1
    return LIUHE_ELEMENT.get((b1, b2))


# ============ 六冲 ============
# 子午冲，丑未冲，寅申冲，卯酉冲，辰戌冲，巳亥冲
LIUCHONG = {
    0: 6,   # 子冲午
    6: 0,   # 午冲子
    1: 7,   # 丑冲未
    7: 1,   # 未冲丑
    2: 8,   # 寅冲申
    8: 2,   # 申冲寅
    3: 9,   # 卯冲酉
    9: 3,   # 酉冲卯
    4: 10,  # 辰冲戌
    10: 4,  # 戌冲辰
    5: 11,  # 巳冲亥
    11: 5,  # 亥冲巳
}

def get_chong(branch: int) -> int:
    """获取地支的六冲对象（正对面）。"""
    return (branch + 6) % 12

def is_chong(b1: int, b2: int) -> bool:
    """判断两个地支是否相冲。"""
    return abs(b1 - b2) == 6 or abs(b1 - b2) == 6


# ============ 三合 ============
# 申子辰合水局，寅午戌合火局，巳酉丑合金局，亥卯未合木局
SANHE_GROUPS = [
    (8, 0, 4, "水"),   # 申子辰
    (2, 6, 10, "火"),  # 寅午戌
    (5, 9, 1, "金"),   # 巳酉丑
    (11, 3, 7, "木"),  # 亥卯未
]

def get_sanhe(branches: list[int]) -> tuple[bool, str | None]:
    """
    判断地支列表中是否有三合局。
    
    Returns:
        (是否成局, 局的五行)
    """
    branch_set = set(branches)
    for b1, b2, b3, element in SANHE_GROUPS:
        if b1 in branch_set and b2 in branch_set and b3 in branch_set:
            return True, element
    return False, None

def is_sanhe_partial(branches: list[int]) -> list[tuple[int, int, str]]:
    """
    判断地支列表中的半合局。
    
    Returns:
        [(地支1, 地支2, 局的五行), ...]
    """
    result = []
    branch_set = set(branches)
    # 半合：两个地支属于同一三合局
    for b1, b2, b3, element in SANHE_GROUPS:
        # 检查任意两个
        pairs = [(b1, b2), (b2, b3), (b1, b3)]
        for p1, p2 in pairs:
            if p1 in branch_set and p2 in branch_set:
                result.append((p1, p2, element))
    return result


# ============ 三会 ============
# 寅卯辰会东方木，巳午未会南方火，申酉戌会西方金，亥子丑会北方水
SANHUI_GROUPS = [
    (2, 3, 4, "木"),    # 寅卯辰
    (5, 6, 7, "火"),    # 巳午未
    (8, 9, 10, "金"),   # 申酉戌
    (11, 0, 1, "水"),   # 亥子丑
]

def get_sanhui(branches: list[int]) -> tuple[bool, str | None]:
    """判断地支列表中是否有三会局。"""
    branch_set = set(branches)
    for b1, b2, b3, element in SANHUI_GROUPS:
        if b1 in branch_set and b2 in branch_set and b3 in branch_set:
            return True, element
    return False, None


# ============ 相刑 ============
# 子卯相刑（无礼之刑），寅巳申相刑（无恩之刑）
# 丑戌未相刑（恃势之刑），辰午酉亥自刑
XING_RELATIONS = {
    # 无礼之刑
    (0, 3): "无礼之刑",  # 子刑卯
    (3, 0): "无礼之刑",  # 卯刑子
    # 无恩之刑
    (2, 5): "无恩之刑",  # 寅刑巳
    (5, 2): "无恩之刑",  # 巳刑寅
    (2, 8): "无恩之刑",  # 寅刑申
    (8, 2): "无恩之刑",  # 申刑寅
    (5, 8): "无恩之刑",  # 巳刑申
    (8, 5): "无恩之刑",  # 申刑巳
    # 恃势之刑
    (1, 4): "恃势之刑",  # 丑刑戌
    (4, 1): "恃势之刑",  # 戌刑丑
    (1, 7): "恃势之刑",  # 丑刑未
    (7, 1): "恃势之刑",  # 未刑丑
    (4, 7): "恃势之刑",  # 戌刑未
    (7, 4): "恃势之刑",  # 未刑戌
    # 自刑
    (4, 4): "自刑",      # 辰自刑
    (6, 6): "自刑",      # 午自刑
    (9, 9): "自刑",      # 酉自刑
    (11, 11): "自刑",    # 亥自刑
}

def get_xing(b1: int, b2: int) -> str | None:
    """获取两个地支之间的刑关系。"""
    return XING_RELATIONS.get((b1, b2))

def has_xing(b1: int, b2: int) -> bool:
    """判断两个地支是否有刑关系。"""
    return (b1, b2) in XING_RELATIONS


# ============ 六害 ============
# 子未害，丑午害，寅巳害，卯辰害，申亥害，酉戌害
LIUHAI = {
    0: 7,   # 子害未
    7: 0,   # 未害子
    1: 6,   # 丑害午
    6: 1,   # 午害丑
    2: 5,   # 寅害巳
    5: 2,   # 巳害寅
    3: 4,   # 卯害辰
    4: 3,   # 辰害卯
    8: 11,  # 申害亥
    11: 8,  # 亥害申
    9: 10,  # 酉害戌
    10: 9,  # 戌害酉
}

def get_hai(branch: int) -> int | None:
    """获取地支的六害对象。"""
    return LIUHAI.get(branch)

def is_hai(b1: int, b2: int) -> bool:
    """判断两个地支是否相害。"""
    return LIUHAI.get(b1) == b2


# ============ 相破 ============
# 子酉破，卯午破，辰丑破，戌未破，寅亥破，巳申破
PO_RELATIONS = {
    (0, 9): True,   # 子破酉
    (9, 0): True,   # 酉破子
    (3, 6): True,   # 卯破午
    (6, 3): True,   # 午破卯
    (4, 1): True,   # 辰破丑
    (1, 4): True,   # 丑破辰
    (10, 7): True,  # 戌破未
    (7, 10): True,  # 未破戌
    (2, 11): True,  # 寅破亥
    (11, 2): True,  # 亥破寅
    (5, 8): True,   # 巳破申
    (8, 5): True,   # 申破巳
}

def is_po(b1: int, b2: int) -> bool:
    """判断两个地支是否相破。"""
    return (b1, b2) in PO_RELATIONS


# ============ 关系汇总 ============

def analyze_relations(branches: list[int]) -> dict:
    """
    分析一组地支之间的所有关系。
    
    Returns:
        {
            "liuhe": [(b1, b2, element), ...],  # 六合
            "chong": [(b1, b2), ...],           # 六冲
            "sanhe": [(b1, b2, b3, element), ...], # 三合
            "sanhe_partial": [(b1, b2, element), ...], # 半合
            "sanhui": [(b1, b2, b3, element), ...],    # 三会
            "xing": [(b1, b2, type), ...],      # 相刑
            "hai": [(b1, b2), ...],             # 六害
            "po": [(b1, b2), ...],              # 相破
        }
    """
    result = {
        "liuhe": [],
        "chong": [],
        "sanhe": [],
        "sanhe_partial": [],
        "sanhui": [],
        "xing": [],
        "hai": [],
        "po": [],
    }
    
    n = len(branches)
    checked_pairs = set()
    
    # 两两关系
    for i in range(n):
        for j in range(i + 1, n):
            b1, b2 = branches[i], branches[j]
            if (b1, b2) in checked_pairs:
                continue
            checked_pairs.add((b1, b2))
            checked_pairs.add((b2, b1))
            
            # 六合
            if is_liuhe(b1, b2):
                elem = get_liuhe_element(b1, b2)
                result["liuhe"].append((b1, b2, elem))
            
            # 六冲
            if is_chong(b1, b2):
                result["chong"].append((b1, b2))
            
            # 相刑
            xing_type = get_xing(b1, b2)
            if xing_type:
                result["xing"].append((b1, b2, xing_type))
            
            # 六害
            if is_hai(b1, b2):
                result["hai"].append((b1, b2))
            
            # 相破
            if is_po(b1, b2):
                result["po"].append((b1, b2))
    
    # 三合局
    has_sanhe, sanhe_elem = get_sanhe(branches)
    if has_sanhe and sanhe_elem:
        for b1, b2, b3, elem in SANHE_GROUPS:
            if elem == sanhe_elem:
                result["sanhe"].append((b1, b2, b3, elem))
                break
    
    # 半合
    partial = is_sanhe_partial(branches)
    result["sanhe_partial"] = partial
    
    # 三会局
    has_sanhui, sanhui_elem = get_sanhui(branches)
    if has_sanhui and sanhui_elem:
        for b1, b2, b3, elem in SANHUI_GROUPS:
            if elem == sanhui_elem:
                result["sanhui"].append((b1, b2, b3, elem))
                break
    
    return result


def format_relation(b1: int, b2: int, relation_type: str, detail: str = "") -> str:
    """格式化关系描述。"""
    b1_name = DIZHI[b1]
    b2_name = DIZHI[b2]
    
    if detail:
        return f"{b1_name}{b2_name}{relation_type}({detail})"
    return f"{b1_name}{b2_name}{relation_type}"
