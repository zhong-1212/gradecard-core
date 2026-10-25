# -*- coding: utf-8 -*-
"""ISO 286 公差配合计算：尺寸段 × IT 等级 → 标准公差；字母偏差 → 上下偏差。
支持常用配合（H7/g6、H7/k6、H7/s6、F8/h6 等）与任意"基本尺寸+公差带"组合。
"""
import json

# 尺寸段（mm）：每段取上限
SIZE_RANGES = [
    (0, 3), (3, 6), (6, 10), (10, 18), (18, 30), (30, 50), (50, 80),
    (80, 120), (120, 180), (180, 250), (250, 315), (315, 400), (400, 500),
    (500, 630), (630, 800), (800, 1000), (1000, 1250), (1250, 1600),
    (1600, 2000), (2000, 2500), (2500, 3150),
]

IT_GRADES = ["IT01", "IT0", "IT1", "IT2", "IT3", "IT4", "IT5", "IT6", "IT7",
             "IT8", "IT9", "IT10", "IT11", "IT12", "IT13", "IT14", "IT15", "IT16"]

# 标准公差数值（µm）
IT_VALUES = [
    [0.3, 0.5, 0.8, 1.2, 2, 3, 4, 6, 10, 14, 25, 40, 60, 100, 140, 250, 400, 600],
    [0.4, 0.6, 1.0, 1.5, 2.5, 4, 5, 8, 12, 18, 30, 48, 75, 120, 180, 300, 480, 750],
    [0.4, 0.6, 1.0, 1.5, 2.5, 4, 6, 9, 15, 22, 36, 58, 90, 150, 220, 360, 580, 900],
    [0.5, 0.8, 1.2, 2, 3, 5, 8, 11, 18, 27, 43, 70, 110, 180, 270, 430, 700, 1100],
    [0.6, 1.0, 1.5, 2.5, 4, 6, 9, 13, 21, 33, 52, 84, 130, 210, 330, 520, 840, 1300],
    [0.6, 1.0, 1.5, 2.5, 4, 7, 11, 16, 25, 39, 62, 100, 160, 250, 390, 620, 1000, 1600],
    [0.8, 1.2, 2.0, 3, 5, 8, 13, 19, 30, 46, 74, 120, 190, 300, 460, 740, 1200, 1900],
    [1.0, 1.5, 2.5, 4, 6, 10, 15, 22, 35, 54, 87, 140, 220, 350, 540, 870, 1400, 2200],
    [1.2, 2.0, 3.5, 5, 8, 12, 18, 25, 40, 63, 100, 160, 250, 400, 630, 1000, 1600, 2500],
    [2.0, 3.0, 4.5, 7, 10, 14, 20, 29, 46, 72, 115, 185, 290, 460, 720, 1150, 1850, 2900],
    [2.5, 4.0, 6.0, 8, 12, 16, 23, 32, 52, 81, 130, 210, 320, 520, 810, 1300, 2100, 3200],
    [3.0, 5.0, 7.0, 9, 13, 18, 25, 36, 57, 89, 140, 230, 360, 570, 890, 1400, 2300, 3600],
    [4.0, 6.0, 8.0, 10, 15, 20, 27, 40, 63, 97, 155, 250, 400, 630, 970, 1550, 2500, 4000],
    # ISO 286-1 大尺寸段（500-3150mm）：IT01-IT5 无定义（None）
    [None, None, None, None, None, None, None, 44, 70, 110, 175, 280, 440, 700, 1100, 1750, 2800, 4400],
    [None, None, None, None, None, None, None, 50, 80, 125, 200, 320, 500, 800, 1250, 2000, 3200, 5000],
    [None, None, None, None, None, None, None, 56, 90, 140, 230, 360, 560, 900, 1400, 2300, 3600, 5600],
    [None, None, None, None, None, None, None, 66, 105, 165, 260, 420, 660, 1050, 1650, 2600, 4200, 6600],
    [None, None, None, None, None, None, None, 78, 125, 195, 310, 500, 780, 1250, 1950, 3100, 5000, 7800],
    [None, None, None, None, None, None, None, 92, 150, 230, 370, 600, 920, 1500, 2300, 3700, 6000, 9200],
    [None, None, None, None, None, None, None, 110, 175, 280, 440, 700, 1100, 1750, 2800, 4400, 7000, 11000],
    [None, None, None, None, None, None, None, 130, 210, 330, 540, 860, 1300, 2100, 3300, 5400, 8600, 13000],
]

# 轴的基本偏差 es（µm），字母 -> 各尺寸段的值
SHAFT_DEVIATION = {
    "a":  [-270, -270, -280, -290, -300, -310, -320, -340, -380, -410, -460, -520, -580],
    "b":  [-140, -140, -150, -150, -160, -170, -180, -200, -240, -260, -300, -330, -360],
    "c":  [-60, -70, -80, -95, -110, -120, -130, -150, -180, -200, -240, -270, -300, -330, -360, -400, -450, -500, -560, -620, -680],
    "d":  [-20, -30, -40, -50, -65, -80, -100, -120, -145, -170, -190, -210, -230, -260, -290, -320, -350, -400, -450, -500, -560],
    "e":  [-14, -20, -25, -32, -40, -50, -60, -72, -85, -100, -110, -125, -135, -145, -160, -170, -195, -220, -240, -260, -290],
    "f":  [-6, -10, -13, -16, -20, -25, -30, -36, -43, -50, -56, -62, -68, -76, -80, -86, -98, -110, -120, -130, -145],
    "g":  [-2, -4, -5, -6, -7, -9, -10, -12, -14, -15, -17, -18, -20, -22, -24, -26, -28, -30, -32, -34, -38],
    "h":  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "k":  [0, 1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 7, 8, 8, 9],
    "m":  [4, 8, 10, 12, 15, 17, 20, 24, 28, 33, 36, 40, 45, 50, 55, 60, 66, 78, 92, 110, 135],
    "n":  [6, 12, 15, 18, 22, 26, 32, 38, 43, 50, 56, 68, 78, 88, 100, 112, 130, 155, 180, 210, 250],
    "p":  [10, 15, 19, 23, 28, 34, 41, 51, 63, 80, 94, 108, 126, 150, 170, 190, 220, 260, 300, 340, 400],
    "r":  [14, 19, 23, 28, 35, 43, 54, 73, 92, 122, 158, 226, 294, 340, 380, 420, 480, 540, 600, 660, 740],
    "s":  [16, 23, 28, 34, 41, 53, 66, 86, 106, 146, 190, 272, 350, 380, 420, 470, 540, 600, 660, 730, 820],
    "t":  [18, 23, 28, 33, 48, 60, 79, 106, 132, 180, 226, 336, 434, 430, 480, 540, 620, 700, 780, 880, 1000],
    "u":  [20, 23, 28, 40, 63, 75, 102, 144, 200, 280, 330, 450, 520, 540, 600, 660, 760, 850, 950, 1050, 1200],
    "v":  [0, 0, 0, 0, 41, 51, 61, 91, 122, 160, 187, 262, 342],
    "x":  [20, 28, 34, 40, 47, 57, 70, 104, 144, 196, 228, 320, 400],
    "y":  [0, 0, 0, 0, 54, 64, 87, 123, 170, 228, 266, 382, 468],
    "z":  [26, 32, 41, 50, 63, 75, 102, 144, 200, 280, 330, 450, 520],
}

# 孔 K/M/N/P-ZC 的修正量 Δ（µm）：键为 IT 等级字符串，值随尺寸段
DELTA = {  # 每个尺寸段一行
    "KMN": [
        {"IT4": 0, "IT5": 0, "IT6": 0, "IT7": 0, "IT8": 0},
        {"IT4": 0, "IT5": 0, "IT6": 0, "IT7": 0, "IT8": 0},
        {"IT4": 0, "IT5": 0, "IT6": 0, "IT7": 0, "IT8": 0},
        {"IT4": 1, "IT5": 1, "IT6": 0, "IT7": 0, "IT8": 0},
        {"IT4": 2, "IT5": 2, "IT6": 0, "IT7": 0, "IT8": 0},
        {"IT4": 3, "IT5": 3, "IT6": 0, "IT7": 0, "IT8": 0},
        {"IT4": 5, "IT5": 5, "IT6": 0, "IT7": 0, "IT8": 0},
        {"IT4": 7, "IT5": 7, "IT6": 0, "IT7": 0, "IT8": 0},
        {"IT4": 10, "IT5": 10, "IT6": 0, "IT7": 0, "IT8": 0},
        {"IT4": 15, "IT5": 15, "IT6": 0, "IT7": 0, "IT8": 0},
        {"IT4": 20, "IT5": 20, "IT6": 0, "IT7": 0, "IT8": 0},
        {"IT4": 25, "IT5": 25, "IT6": 0, "IT7": 0, "IT8": 0},
        {"IT4": 30, "IT5": 30, "IT6": 0, "IT7": 0, "IT8": 0},        {"IT4": 0, "IT5": 0, "IT6": 0, "IT7": 0, "IT8": 0},
        {"IT4": 0, "IT5": 0, "IT6": 0, "IT7": 0, "IT8": 0},
        {"IT4": 0, "IT5": 0, "IT6": 0, "IT7": 0, "IT8": 0},
        {"IT4": 0, "IT5": 0, "IT6": 0, "IT7": 0, "IT8": 0},
        {"IT4": 0, "IT5": 0, "IT6": 0, "IT7": 0, "IT8": 0},
        {"IT4": 0, "IT5": 0, "IT6": 0, "IT7": 0, "IT8": 0},
        {"IT4": 0, "IT5": 0, "IT6": 0, "IT7": 0, "IT8": 0},
        {"IT4": 0, "IT5": 0, "IT6": 0, "IT7": 0, "IT8": 0},

    ],
    "PZC": [
        {"IT4": 0, "IT5": 0, "IT6": 0, "IT7": 0},
        {"IT4": 0, "IT5": 0, "IT6": 0, "IT7": 0},
        {"IT4": 0, "IT5": 0, "IT6": 0, "IT7": 0},
        {"IT4": 1, "IT5": 1, "IT6": 0, "IT7": 0},
        {"IT4": 2, "IT5": 2, "IT6": 0, "IT7": 0},
        {"IT4": 3, "IT5": 3, "IT6": 0, "IT7": 0},
        {"IT4": 5, "IT5": 5, "IT6": 0, "IT7": 0},
        {"IT4": 7, "IT5": 7, "IT6": 0, "IT7": 0},
        {"IT4": 10, "IT5": 10, "IT6": 0, "IT7": 0},
        {"IT4": 15, "IT5": 15, "IT6": 0, "IT7": 0},
        {"IT4": 20, "IT5": 20, "IT6": 0, "IT7": 0},
        {"IT4": 25, "IT5": 25, "IT6": 0, "IT7": 0},
        {"IT4": 30, "IT5": 30, "IT6": 0, "IT7": 0},        {"IT4": 0, "IT5": 0, "IT6": 0, "IT7": 0},
        {"IT4": 0, "IT5": 0, "IT6": 0, "IT7": 0},
        {"IT4": 0, "IT5": 0, "IT6": 0, "IT7": 0},
        {"IT4": 0, "IT5": 0, "IT6": 0, "IT7": 0},
        {"IT4": 0, "IT5": 0, "IT6": 0, "IT7": 0},
        {"IT4": 0, "IT5": 0, "IT6": 0, "IT7": 0},
        {"IT4": 0, "IT5": 0, "IT6": 0, "IT7": 0},
        {"IT4": 0, "IT5": 0, "IT6": 0, "IT7": 0},

    ],
}

# 孔/轴字母映射：大写孔用对应小写轴的偏差
HOLE_LETTERS = "ABCDEFGHJKMNP RSTUVXYZ".replace(" ", "")


def _range_index(size: float) -> int:
    """返回尺寸所在尺寸段下标；超范围抛错。"""
    size = float(size)
    if size <= 0:
        raise ValueError("基本尺寸必须大于 0")
    if size > 3150:
        raise ValueError("暂支持 ≤3150mm 尺寸段（2500-3150mm）")
    for i, (lo, hi) in enumerate(SIZE_RANGES):
        if size <= hi:
            return i
    return len(SIZE_RANGES) - 1



def _shaft_dev(letter: str, ri: int) -> float:
    """取轴基本偏差；未覆盖大尺寸段的字母给出友好报错。"""
    vals = SHAFT_DEVIATION[letter]
    if isinstance(vals, list) and ri >= len(vals):
        raise ValueError(f"公差带字母 {letter.upper()} 暂不支持 ≥500mm 尺寸段")
    return vals[ri] if isinstance(vals, list) else vals


def standard_tolerance(size: float, grade: str) -> float:
    """返回标准公差值（µm）。grade 形如 IT7。"""
    g = grade.strip().upper()
    if not g.startswith("IT") or g not in IT_GRADES:
        raise ValueError(f"公差等级需为 IT01-IT16，当前: {grade}")
    v = IT_VALUES[_range_index(size)][IT_GRADES.index(g)]
    if v is None:
        raise ValueError(f"{g} 在 >500mm 尺寸段无标准定义，请改用 IT6-IT16")
    return v


def parse_tolerance_band(band: str):
    """解析形如 H7 / g6 / JS9 / K8 的公差带，返回 (letter, grade)。"""
    band = (band or "").strip()
    if not band:
        raise ValueError("请输入公差带，如 H7 或 g6")
    m = None
    for i, ch in enumerate(band):
        if ch.isdigit():
            m = (band[:i], band[i:])
            break
    if not m:
        raise ValueError("公差带需含等级数字，如 H7 / g6")
    letter, grade_str = m
    grade = "IT" + grade_str
    if grade not in IT_GRADES:
        raise ValueError(f"公差等级需为 IT01-IT16，当前: {grade_str}")
    return letter, grade


def band_deviations(size: float, band: str) -> dict:
    """计算某个公差带的上下偏差（µm），返回 {es, ei} 或 {ES, EI}。"""
    letter, grade = parse_tolerance_band(band)
    ri = _range_index(size)
    it = IT_VALUES[ri][IT_GRADES.index(grade)]
    if it is None:
        raise ValueError(f"{grade} 在 >500mm 尺寸段无标准定义，请改用 IT6-IT16")
    lower = letter.islower()
    base = letter.upper()

    if base == "J" or base == "JS":
        # JS/js：对称偏差
        half = it / 2.0
        return {"es": half, "ei": -half} if lower else {"ES": half, "EI": -half}

    if lower:
        es = _shaft_dev(base.lower(), ri)
        return {"es": es, "ei": es - it}

    # 孔
    if base == "H":
        return {"ES": it, "EI": 0}
    if base in "ABCDEFG":
        es = _shaft_dev(base.lower(), ri)
        return {"ES": -es + it, "EI": -es}
    if base in "KMN":
        delta = DELTA["KMN"][ri].get(grade, 0)
        es = _shaft_dev(base.lower(), ri)
        return {"ES": -es + delta, "EI": -es + delta - it}
    if base in "PQRSTUVXYZ":
        delta = DELTA["PZC"][ri].get(grade, 0)
        es = _shaft_dev(base.lower(), ri)
        return {"ES": -es + delta, "EI": -es + delta - it}
    raise ValueError(f"暂不支持该公差带字母: {letter}")


FIT_TYPE = {
    ("H", "a"): "间隙", ("H", "b"): "间隙", ("H", "c"): "间隙", ("H", "d"): "间隙",
    ("H", "e"): "间隙", ("H", "f"): "间隙", ("H", "g"): "间隙", ("H", "h"): "间隙",
    ("H", "js"): "过渡", ("H", "k"): "过渡", ("H", "m"): "过渡", ("H", "n"): "过渡",
    ("H", "p"): "过盈", ("H", "r"): "过盈", ("H", "s"): "过盈", ("H", "t"): "过盈",
    ("H", "u"): "过盈", ("H", "v"): "过盈", ("H", "x"): "过盈", ("H", "y"): "过盈", ("H", "z"): "过盈",
    ("F", "h"): "间隙", ("G", "h"): "间隙", ("D", "h"): "间隙", ("E", "h"): "间隙", ("C", "h"): "间隙",
}


def compute_fit(size: float, hole: str, shaft: str) -> dict:
    """计算配合：返回孔/轴偏差、间隙或过盈、配合类型。"""
    hd = band_deviations(size, hole)
    sd = band_deviations(size, shaft)
    hole_es, hole_ei = hd.get("ES", 0), hd.get("EI", 0)
    shaft_es, shaft_ei = sd.get("es", 0), sd.get("ei", 0)
    max_gap = hole_es - shaft_ei
    min_gap = hole_ei - shaft_es
    hletter = hole[0].upper()
    sletter = "js" if shaft[:2].lower() == "js" else shaft[0].lower()
    ftype = FIT_TYPE.get((hletter, sletter), "过渡")
    if min_gap >= 0:
        ftype = "间隙"
    elif max_gap <= 0:
        ftype = "过盈"
    return {
        "size": float(size),
        "hole": {"band": hole, "ES": hole_es, "EI": hole_ei},
        "shaft": {"band": shaft, "es": shaft_es, "ei": shaft_ei},
        "max_clearance": max_gap,
        "min_clearance": min_gap,
        "fit_type": ftype,
    }


# 常用配合速查
COMMON_FITS = [
    {"fit": "H7/g6", "type": "间隙", "use": "滑动配合（精密导套、齿轮与轴滑动）"},
    {"fit": "H7/h6", "type": "间隙", "use": "可自由装拆的定位配合（皮带轮、手轮）"},
    {"fit": "H7/js6", "type": "过渡", "use": "略有过盈的定位（联轴器、轻型齿轮）"},
    {"fit": "H7/k6", "type": "过渡", "use": "精密定位、可敲入（齿轮、轴承内圈）"},
    {"fit": "H7/m6", "type": "过渡", "use": "需加压装入（重型齿轮、联轴器）"},
    {"fit": "H7/n6", "type": "过渡", "use": "压入后不可拆（轴承套、衬套）"},
    {"fit": "H7/p6", "type": "过盈", "use": "轻过盈（蜗轮轮缘、齿轮轮毂）"},
    {"fit": "H7/s6", "type": "过盈", "use": "中过盈（重载齿轮、轴承座）"},
    {"fit": "H7/u6", "type": "过盈", "use": "大过盈（重载压装、键替代）"},
    {"fit": "H8/f7", "type": "间隙", "use": "中等间隙（轴承座孔、滑动轴承）"},
    {"fit": "H8/h8", "type": "间隙", "use": "一般定位"},
    {"fit": "H11/c11", "type": "间隙", "use": "大间隙（粗糙铰链、轴销）"},
    {"fit": "F8/h6", "type": "间隙", "use": "精密滑动（液压阀芯）"},
    {"fit": "G7/h6", "type": "间隙", "use": "精密滑动（导轨）"},
    {"fit": "H7/r6", "type": "过盈", "use": "半永久装配（定位销）"},
]


def suggest_fit(scene: str) -> str:
    """按使用场景推荐配合。scene: 间隙/过渡/过盈/滑动/定位/传动/压装。"""
    s = (scene or "").strip()
    table = [
        ("滑动", "H7/g6", "精密滑动、导向配合"),
        ("间隙", "H8/f7", "一般间隙配合、滑动轴承"),
        ("定位", "H7/k6", "可拆卸定位、齿轮与轴"),
        ("过渡", "H7/n6", "不可随意拆卸的定位"),
        ("传动", "H7/m6", "需传递扭矩的静配合"),
        ("过盈", "H7/s6", "重载过盈、压装"),
        ("压装", "H7/u6", "大过盈压装、可替代键"),
    ]
    for key, fit, note in table:
        if key in s:
            return fit
    return "H7/k6"


def band_json(size, band):
    d = band_deviations(size, band)
    return {"band": band, "size": size, "it": standard_tolerance(size, band[1:] if band[0].isdigit() else _grade_of(band)), **d}


def _grade_of(band):
    letter, grade = parse_tolerance_band(band)
    return grade


# ============ v2.4 工程师工具扩展 ============

def _grade_order(grade: str) -> int:
    """IT 等级转为内部顺序：IT01=0, IT0=1, IT1=2 ... IT16=17。"""
    s = grade.strip().upper()
    if not s.startswith("IT"):
        raise ValueError(f"公差等级需为 IT01-IT16，当前: {grade}")
    body = s[2:]
    if body == "01":
        return 0
    if body == "0":
        return 1
    return int(body) + 1


# IT 等级范围 -> 典型加工方法（参考值，供工艺选配）
PROCESS_TABLE = [
    (0, 3, "研磨 / 珩磨"),
    (4, 5, "精密研磨 / 珩磨 / 精车·精镗"),
    (6, 6, "精磨 / 珩磨"),
    (7, 7, "精磨 / 精车·精镗 / 拉削"),
    (8, 8, "精车·精镗 / 精铣 / 铰孔 / 磨削"),
    (9, 9, "车·镗 / 铣 / 铰孔 / 磨削"),
    (10, 10, "车·铣·镗 / 铰孔"),
    (11, 12, "普通车·铣·镗 / 钻孔后铰"),
    (13, 14, "粗车·粗铣·粗镗 / 钻孔"),
    (15, 17, "粗加工 / 冲压·铸造·锻造"),
]

# IT 等级范围 -> 建议表面粗糙度 Ra(µm)（参考值）
RA_TABLE = [
    (0, 3, 0.05), (4, 5, 0.1), (6, 6, 0.2), (7, 7, 0.4), (8, 8, 0.8),
    (9, 9, 1.6), (10, 10, 3.2), (11, 12, 6.3), (13, 14, 12.5), (15, 17, 25),
]


def process_for_grade(grade: str) -> dict:
    """IT 等级 -> 加工方法 + 建议粗糙度。"""
    g = grade.strip().upper()
    if g not in IT_GRADES:
        raise ValueError(f"公差等级需为 IT01-IT16，当前: {grade}")
    order = _grade_order(g)
    for lo, hi, proc in PROCESS_TABLE:
        if lo <= order <= hi:
            break
    else:
        proc = "—"
    for lo, hi, ra in RA_TABLE:
        if lo <= order <= hi:
            break
    else:
        ra = None
    return {"grade": g, "process": proc, "ra_um": ra}


# IT 等级 -> 加工成本估算（1=最低 ... 5=最高，参考值，用于按成本排序）
COST_TABLE = [
    (0, 4, 5), (5, 6, 4), (7, 8, 3), (9, 10, 2), (11, 17, 1),
]


def cost_for_grade(grade: str) -> dict:
    """IT 等级 -> 加工成本等级（1-5，数字越小越便宜）。"""
    g = grade.strip().upper()
    try:
        order = _grade_order(_grade_of(g))
    except ValueError:
        return {"grade": g, "cost_level": 3}
    for lo, hi, lv in COST_TABLE:
        if lo <= order <= hi:
            return {"grade": g, "cost_level": lv}
    return {"grade": g, "cost_level": 3}


# 典型应用模板（孔/轴角色 + 推荐配合 + 说明）
SCENARIOS = [
    {"key": "bearing_shaft", "name": "滚动轴承内圈与轴", "desc": "深沟球轴承内圈与轴的配合",
     "hole": "J6", "shaft": "k6", "size": 40, "note": "一般载荷选 k6；较重/冲击载荷选 m6"},
    {"key": "bearing_housing", "name": "轴承外圈与箱体孔", "desc": "轴承外圈装入轴承座孔的配合",
     "hole": "H7", "shaft": "h6", "size": 80, "note": "常用 H7；需外圈轴向游动时可用 J7"},
    {"key": "keyway", "name": "平键键槽", "desc": "平键与轴槽/毂槽（GB/T 1095-1096）",
     "hole": "P9", "shaft": "N9", "size": 50, "note": "键宽 h9；轴槽 N9、毂槽 P9，需导向时毂槽 JS9/D10"},
    {"key": "gear_shaft", "name": "齿轮孔与轴", "desc": "齿轮内孔与传动轴的配合",
     "hole": "H7", "shaft": "k6", "size": 50, "note": "轻载可拆 H7/g6；传递扭矩 H7/m6·n6"},
    {"key": "bushing", "name": "滑动轴承衬套", "desc": "衬套孔与轴颈的滑动配合",
     "hole": "H8", "shaft": "f7", "size": 60, "note": "低速重载 H9/e8；高速轻载 H7/g6"},
    {"key": "pin", "name": "定位销与孔", "desc": "圆柱定位销压入定位孔",
     "hole": "H7", "shaft": "r6", "size": 10, "note": "可拆卸定位用 H7/n6·m6"},
    {"key": "coupling", "name": "联轴器与轴", "desc": "联轴器毂孔与轴的配合",
     "hole": "H7", "shaft": "js6", "size": 45, "note": "轻载无键 H7/h6；需定心传扭 js6/k6"},
]


PREFERRED_HOLE_LETTERS = ("H", "F", "G")


def reverse_compute(size: float, gap_min: float, gap_max: float, limit: int = 12,
                    sort: str = "precision") -> list:
    """反向选配：给定基本尺寸与期望间隙/过盈范围(µm，负值为过盈)，推荐孔/轴公差带组合。

    sort="precision" 按精度排序（公差带宽度 → 与目标中点偏差 → H/F/G 优先）；
    sort="cost" 按加工成本排序（IT 等级估算 1-5，低者在先）。
    """
    size = float(size)
    gap_min = float(gap_min)
    gap_max = float(gap_max)
    if gap_max < gap_min:
        raise ValueError("范围上限需 ≥ 下限")
    if abs(gap_max) > 5000 or abs(gap_min) > 5000:
        raise ValueError("间隙/过盈范围建议在 ±5000µm 内")
    hole_letters = ["H", "G", "F", "E", "D", "C", "JS", "K", "M", "N", "P", "R", "S"]
    shaft_letters = ["a", "b", "c", "d", "e", "f", "g", "h", "js", "k", "m", "n", "p", "r", "s", "t", "u"]
    hole_grades = [5, 6, 7, 8, 9, 10, 11]
    shaft_grades = [4, 5, 6, 7, 8, 9]
    mid = (gap_min + gap_max) / 2.0
    results = []
    for hl in hole_letters:
        for hg in hole_grades:
            for sl in shaft_letters:
                for sg in shaft_grades:
                    try:
                        r = compute_fit(size, f"{hl}{hg}", f"{sl}{sg}")
                    except ValueError:
                        continue
                    lo = min(r["min_clearance"], r["max_clearance"])
                    hi = max(r["min_clearance"], r["max_clearance"])
                    if lo < gap_min or hi > gap_max:
                        continue
                    hole_g = f"{hl}{hg}"
                    shaft_g = f"{sl}{sg}"
                    try:
                        hp = process_for_grade(f"IT{hg}")
                        sp = process_for_grade(f"IT{sg}")
                    except ValueError:
                        hp = sp = {"process": None, "ra_um": None}
                    cost_level = max(cost_for_grade(hole_g)["cost_level"],
                                     cost_for_grade(shaft_g)["cost_level"])
                    results.append((
                        0 if hl in PREFERRED_HOLE_LETTERS else 1,
                        round(hi - lo, 3),
                        abs(((lo + hi) / 2.0) - mid),
                        cost_level,
                        {
                            "hole": hole_g,
                            "shaft": shaft_g,
                            "min_clearance": round(lo, 3),
                            "max_clearance": round(hi, 3),
                            "fit_type": r["fit_type"],
                            "cost_level": cost_level,
                            "process": hp["process"],
                            "ra_um": hp["ra_um"],
                            "shaft_process": sp["process"],
                            "shaft_ra_um": sp["ra_um"],
                        },
                    ))
    if sort not in ("precision", "cost"):
        sort = "precision"
    if sort == "cost":
        results.sort(key=lambda x: (x[3],) + x[:3])
    else:
        results.sort(key=lambda x: x[:3])
    return [item for *_, item in results[:limit]]


import math


def assembly_yield(size: float, hole: str, shaft: str, sigma: int = 6) -> dict:
    """装配良率估计（正态近似）：假设孔/轴尺寸波动覆盖 ±sigma 个标准差。
    返回出现合格间隙/过盈的比例估计，仅供设计参考。"""
    r = compute_fit(size, hole, shaft)
    th = abs(r["hole"]["ES"] - r["hole"]["EI"])
    ts = abs(r["shaft"]["es"] - r["shaft"]["ei"])
    mu = (r["min_clearance"] + r["max_clearance"]) / 2.0
    sdev = max(math.sqrt(th ** 2 + ts ** 2) / float(sigma), 1e-9)
    z = mu / sdev
    p_pos = 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
    if r["fit_type"] == "过盈":
        p_ok = 1.0 - p_pos  # 保持过盈才算合格
    else:
        p_ok = p_pos
    return {
        "fit_type": r["fit_type"],
        "mu_gap_um": round(mu, 3),
        "sigma_gap_um": round(sdev, 3),
        "yield_pct": round(p_ok * 100.0, 2),
        "sigma_level": sigma,
        "note": "正态近似估计，实际良率受工艺能力影响",
    }


def compute_batch(items: list) -> list:
    """批量计算：items = [{"size": 50, "hole": "H7", "shaft": "g6"}, ...]。"""
    rows = []
    for it in items or []:
        try:
            size = float(it.get("size", 0))
        except (TypeError, ValueError):
            size = 0
        hole = str(it.get("hole", "")).strip()
        shaft = str(it.get("shaft", "")).strip()
        try:
            r = compute_fit(size, hole, shaft)
            rows.append({
                "size": r["size"], "hole": hole, "shaft": shaft,
                "min_clearance": r["min_clearance"], "max_clearance": r["max_clearance"],
                "fit_type": r["fit_type"], "error": None,
            })
        except ValueError as e:
            rows.append({
                "size": size, "hole": hole, "shaft": shaft,
                "min_clearance": None, "max_clearance": None,
                "fit_type": None, "error": str(e),
            })
    return rows


def enhance_fit_result(size: float, hole: str, shaft: str) -> dict:
    """计算配合 + 附加工程信息（加工方法、粗糙度、装配良率）。"""
    r = compute_fit(size, hole, shaft)
    hp = process_for_grade(_grade_of(hole))
    sp = process_for_grade(_grade_of(shaft))
    y = assembly_yield(size, hole, shaft)
    r["hole"].update({"process": hp["process"], "ra_um": hp["ra_um"]})
    r["shaft"].update({"process": sp["process"], "ra_um": sp["ra_um"]})
    r["assembly"] = y
    return r

# ================= v2.5 公差深化：过盈压装 / 螺纹 / GD&T / 粗糙度 =================

# 常用工程材料力学性能（过盈压装计算用）
PRESS_MATERIALS = {
    "碳钢/合金钢": {"E": 206000, "nu": 0.30, "alpha": 12.0e-6},
    "不锈钢":     {"E": 193000, "nu": 0.30, "alpha": 16.5e-6},
    "铸铁":       {"E": 105000, "nu": 0.25, "alpha": 10.5e-6},
    "铝合金":     {"E": 70000,  "nu": 0.33, "alpha": 23.0e-6},
    "铜合金":     {"E": 110000, "nu": 0.34, "alpha": 17.0e-6},
    "钛合金":     {"E": 110000, "nu": 0.34, "alpha": 9.0e-6},
}

# 摩擦系数（配对，取中值）
PRESS_FRICTION = {
    ("碳钢/合金钢", "碳钢/合金钢"): 0.12,
    ("碳钢/合金钢", "不锈钢"): 0.12,
    ("碳钢/合金钢", "铸铁"): 0.12,
    ("碳钢/合金钢", "铝合金"): 0.15,
    ("碳钢/合金钢", "铜合金"): 0.10,
    ("铸铁", "铸铁"): 0.15,
    ("不锈钢", "不锈钢"): 0.12,
}


def press_fit(size: float, interference_um: float, length: float,
              hub_material: str = "碳钢/合金钢", shaft_material: str = "碳钢/合金钢",
              friction: float | None = None, outer_d: float | None = None,
              cool_assembly: bool = False) -> dict:
    """过盈配合压装力 / 可传递扭矩 / 热装冷装温差计算（厚壁圆筒公式，工程参考）。"""
    import math
    size = float(size)
    interference_um = float(interference_um)
    length = float(length)
    if not (1 <= size <= 500):
        raise ValueError("基本尺寸需在 1-500mm 之间")
    if not (0 < interference_um <= 2000):
        raise ValueError("过盈量建议在 1-2000µm 之间")
    if not (1 <= length <= 1000):
        raise ValueError("配合长度需在 1-1000mm 之间")
    if hub_material not in PRESS_MATERIALS or shaft_material not in PRESS_MATERIALS:
        raise ValueError("暂支持的材料：" + "/".join(PRESS_MATERIALS))
    if friction is None:
        friction = PRESS_FRICTION.get((hub_material, shaft_material), 0.12)
    fric_key = (hub_material, shaft_material)
    if fric_key not in PRESS_FRICTION:
        fric_key = (shaft_material, hub_material)
    friction = friction or PRESS_FRICTION.get(fric_key, 0.12)

    hub = PRESS_MATERIALS[hub_material]
    shaft = PRESS_MATERIALS[shaft_material]
    d_outer = outer_d if outer_d and outer_d > size else size * 2.0  # 轮毂外径默认 2d

    delta = interference_um / 1000.0  # mm
    # 轮毂系数 C_h = (Do^2+d^2)/(Do^2-d^2) + nu
    ch = (d_outer ** 2 + size ** 2) / (d_outer ** 2 - size ** 2) + hub["nu"]
    cs = 1.0 - shaft["nu"]  # 实心轴
    # 结合面压强 p (MPa)
    p = delta / (size * (ch / hub["E"] + cs / shaft["E"]))
    p = max(p, 0.0)
    # 压入力 F = f * p * pi * d * L  (N)
    press_force = friction * p * math.pi * size * length
    # 可传递扭矩 T = f * p * pi * d^2 * L / 2  (N*m)
    torque = friction * p * math.pi * (size ** 2) * length / 2.0 / 1000.0
    # 热装：加热轮毂 / 冷装：冷却轴；同时用温差可减半
    dt_hub = delta / (hub["alpha"] * size)
    dt_shaft = delta / (shaft["alpha"] * size)
    dt_both = delta / ((hub["alpha"] + shaft["alpha"]) * size)
    if cool_assembly:
        dt_req = dt_shaft
        method = "冷装（冷却轴）"
    else:
        dt_req = dt_hub
        method = "热装（加热轮毂）"

    notes = []
    notes.append("按厚壁圆筒弹性公式估算，未计应力集中；正式设计需按 GB/T 5371 校核接触应力与材料屈服。")
    if p > 120:
        notes.append("估算结合面压强偏高，注意校核轮毂/轴材料屈服强度。")
    if press_force > 200000:
        notes.append("压入力较大，建议优先采用热装/冷装装配。")
    return {
        "size": size,
        "interference_um": interference_um,
        "length": length,
        "hub_material": hub_material,
        "shaft_material": shaft_material,
        "friction": round(friction, 3),
        "pressure_mpa": round(p, 2),
        "press_force_kn": round(press_force / 1000.0, 2),
        "torque_nm": round(torque, 2),
        "method": method,
        "heat_dt_k": round(dt_hub, 1),
        "cool_dt_k": round(dt_shaft, 1),
        "dt_recommend_k": round(dt_req * 1.2, 1),
        "notes": notes,
    }


# 粗牙普通螺纹 M3-M64 速查（ISO 965-1，参考值）
# 字段：d 公称, P 螺距, d2 基本中径, es_6g 外螺纹6g基本偏差(µm), Td2_6 外6级中径公差(µm),
#       TD2_6 内6级中径公差(µm), Td_6 外6级大径公差(µm), TD1_6 内6级小径公差(µm)
THREAD_TABLE = [
    (3, 0.5, 2.675, -32, 71, 100, 180, 180),
    (4, 0.7, 3.545, -38, 85, 118, 236, 236),
    (5, 0.8, 4.480, -38, 90, 125, 265, 265),
    (6, 1.0, 5.350, -40, 95, 132, 300, 300),
    (8, 1.25, 7.188, -42, 112, 150, 355, 375),
    (10, 1.5, 9.026, -45, 132, 180, 400, 450),
    (12, 1.75, 10.863, -48, 150, 200, 450, 475),
    (16, 2.0, 14.701, -52, 180, 236, 500, 530),
    (20, 2.5, 18.376, -58, 212, 280, 600, 600),
    (24, 3.0, 22.051, -63, 236, 315, 710, 710),
    (30, 3.5, 27.727, -70, 265, 355, 800, 800),
    (36, 4.0, 33.402, -75, 300, 400, 900, 900),
    (42, 4.5, 39.077, -80, 315, 425, 950, 950),
    (48, 5.0, 44.752, -85, 335, 450, 1060, 1060),
    (56, 5.5, 52.428, -95, 375, 500, 1180, 1180),
    (64, 6.0, 60.103, -100, 400, 530, 1250, 1250),
]

# 内螺纹公差等级缩放（相对 6 级）
INT_THREAD_FACTOR = {"4H": 0.63, "5H": 0.85, "6H": 1.0, "7H": 1.25}
# 外螺纹公差等级缩放（相对 6 级）+ 基本偏差模式（h=0, g=6g）
EXT_THREAD_FACTOR = {"4h": 0.63, "6h": 1.0, "6g": 1.0, "8g": 1.6}


def thread_quickref(nominal: float, ext_class: str = "6g", int_class: str = "6H") -> dict:
    """普通粗牙螺纹 M3-M64 公差速查（参考值）。返回大径/中径/小径上下限与底孔建议。"""
    nominal = float(nominal)
    row = None
    for r in THREAD_TABLE:
        if int(r[0]) == int(nominal):
            row = r
            break
    if not row:
        raise ValueError("暂支持 M3/M4/M5/M6/M8/M10/M12/M16/M20/M24/M30/M36/M42/M48/M56/M64 粗牙螺纹")
    d, p, d2, es_6g, td2_6, td2_6_int, td_6, td1_6 = row
    ext = ext_class.strip().lower()
    intc = int_class.strip().upper()
    if intc not in INT_THREAD_FACTOR:
        raise ValueError("内螺纹等级需为 4H/5H/6H/7H")
    if ext not in EXT_THREAD_FACTOR:
        raise ValueError("外螺纹等级需为 4h/6h/6g/8g")

    # 基本偏差 es（µm，负值）
    es = es_6g if ext in ("6g", "8g") else 0
    f_ext = EXT_THREAD_FACTOR[ext]
    f_int = INT_THREAD_FACTOR[intc]
    td2 = round(td2_6 * f_ext)
    TD2 = round(td2_6_int * f_int)
    Td = round(td_6 * f_ext)
    TD1 = round(td1_6 * f_int)

    # 外螺纹（µm→mm）
    d_max = d + es / 1000.0
    d_min = d_max - Td / 1000.0
    d2_max = d2 + es / 1000.0
    d2_min = d2_max - td2 / 1000.0
    d3 = d - 1.2269 * p  # 基本小径
    d3_max = d3 + es / 1000.0

    # 内螺纹
    D2_min = d2
    D2_max = d2 + TD2 / 1000.0
    D1 = d - 1.0825 * p  # 基本小径
    D1_min = D1
    D1_max = D1 + TD1 / 1000.0

    return {
        "nominal": "M%d" % int(d),
        "pitch": p,
        "d": d,
        "d2": d2,
        "ext_class": ext,
        "int_class": intc,
        "external": {
            "major_max": round(d_max, 3), "major_min": round(d_min, 3),
            "pitch_max": round(d2_max, 3), "pitch_min": round(d2_min, 3),
            "minor_max": round(d3_max, 3), "minor_min": round(d3_max - td2 / 1000.0, 3),
        },
        "internal": {
            "major_min": d, "major_max": d + TD1 / 1000.0,
            "pitch_min": round(D2_min, 3), "pitch_max": round(D2_max, 3),
            "minor_min": round(D1_min, 3), "minor_max": round(D1_max, 3),
        },
        "tap_hole": {
            "韧性材料": round(d - p, 2),
            "脆性材料": round(d - 1.1 * p, 2),
        },
        "note": "ISO 965-1 参考值（按 6g/6H 表近似换算），正式图纸请查标准原文。",
    }


# 几何公差（GD&T）速查
GDT_ITEMS = [
    {"name": "直线度", "symbol": "⏤", "cat": "形状公差", "desc": "被测要素的轮廓线在公差带内为直线", "use": "轴、导轨母线"},
    {"name": "平面度", "symbol": "⏥", "cat": "形状公差", "desc": "被测表面在公差带内为平面", "use": "安装面、基准面"},
    {"name": "圆度", "symbol": "◯", "cat": "形状公差", "desc": "同一正截面上圆要素在公差带内为圆", "use": "轴颈、孔、轴承位"},
    {"name": "圆柱度", "symbol": "⌭", "cat": "形状公差", "desc": "圆柱面在公差带内为理想圆柱", "use": "精密轴颈、缸孔"},
    {"name": "线轮廓度", "symbol": "⌒", "cat": "形状/位置", "desc": "任意截面轮廓相对理论轮廓的偏差", "use": "曲面型线、凸轮"},
    {"name": "面轮廓度", "symbol": "⌓", "cat": "形状/位置", "desc": "曲面相对理论曲面的偏差", "use": "叶片、流道面"},
    {"name": "平行度", "symbol": "∥", "cat": "位置公差", "desc": "被测要素相对基准平行", "use": "两孔轴线、平面间距"},
    {"name": "垂直度", "symbol": "⊥", "cat": "位置公差", "desc": "被测要素相对基准垂直", "use": "端面与轴线、安装孔"},
    {"name": "倾斜度", "symbol": "∠", "cat": "位置公差", "desc": "被测要素相对基准成给定角度", "use": "斜孔、斜面"},
    {"name": "位置度", "symbol": "⊕", "cat": "位置公差", "desc": "点/线/面相对理论位置的偏差", "use": "孔组、安装孔位"},
    {"name": "同轴度", "symbol": "◎", "cat": "位置公差", "desc": "被测轴线相对基准轴线的偏差", "use": "阶梯轴、齿轮内孔"},
    {"name": "对称度", "symbol": "⌯", "cat": "位置公差", "desc": "被测要素相对基准对称面/线的偏差", "use": "键槽、对称孔"},
    {"name": "圆跳动", "symbol": "↗", "cat": "跳动公差", "desc": "被测要素绕基准轴线回转时的跳动量", "use": "轴颈、端面"},
    {"name": "全跳动", "symbol": "↗↗", "cat": "跳动公差", "desc": "被测要素连续回转+轴向移动的全跳动量", "use": "整体圆柱面"},
]

# 位置度/同轴度等公差值参考（按尺寸段 ≤30mm，µm，参考 GB/T 1184）
GDT_GRADE_TABLE = [
    {"grade": "4", "value_um": 4},
    {"grade": "5", "value_um": 6},
    {"grade": "6", "value_um": 10},
    {"grade": "7", "value_um": 16},
    {"grade": "8", "value_um": 25},
    {"grade": "9", "value_um": 40},
    {"grade": "10", "value_um": 63},
    {"grade": "11", "value_um": 100},
    {"grade": "12", "value_um": 160},
]


def gdt_quickref() -> dict:
    return {"items": GDT_ITEMS, "grade_table": GDT_GRADE_TABLE,
            "note": "公差等级 K 级典型值参考（尺寸段 ≤30mm），具体标注以 GB/T 1184 为准。"}


# 表面粗糙度 Ra ↔ 加工方法对照（Ra µm）
RA_PROCESS_MAP = [
    {"ra_min": 0.012, "ra_max": 0.025, "process": "超精磨 / 研磨", "use": "镜面、量具工作面"},
    {"ra_min": 0.025, "ra_max": 0.05, "process": "研磨 / 珩磨", "use": "精密量仪、液压阀芯"},
    {"ra_min": 0.05, "ra_max": 0.1, "process": "精磨 / 珩磨 / 超精车", "use": "高精度配合面、轴承滚道"},
    {"ra_min": 0.1, "ra_max": 0.2, "process": "精磨 / 精铰", "use": "精密配合面（IT5-IT6）"},
    {"ra_min": 0.2, "ra_max": 0.4, "process": "磨削 / 精车 / 精镗", "use": "精密配合面（IT6-IT7）"},
    {"ra_min": 0.4, "ra_max": 0.8, "process": "精车 / 精铣 / 铰孔 / 磨削", "use": "一般配合面（IT7）"},
    {"ra_min": 0.8, "ra_max": 1.6, "process": "车 / 铣 / 镗 / 铰", "use": "一般加工面（IT8-IT9）"},
    {"ra_min": 1.6, "ra_max": 3.2, "process": "粗车 / 粗铣 / 钻孔", "use": "非配合面（IT10-IT11）"},
    {"ra_min": 3.2, "ra_max": 6.3, "process": "粗加工", "use": "自由表面（IT12 以下）"},
    {"ra_min": 6.3, "ra_max": 12.5, "process": "铸造 / 锻造 / 气割", "use": "毛坯面"},
    {"ra_min": 12.5, "ra_max": 25, "process": "铸造 / 锻后", "use": "粗糙毛坯面"},
]

# 常用标注 Ra 值（标准优先系列）
RA_COMMON = [
    {"ra": 0.05, "process": "研磨 / 超精磨", "use": "精密量具、高精度滑动面"},
    {"ra": 0.1, "process": "研磨 / 珩磨", "use": "精密配合面"},
    {"ra": 0.2, "process": "精磨", "use": "精密配合面、密封面"},
    {"ra": 0.4, "process": "磨削 / 精车", "use": "配合面、轴承位"},
    {"ra": 0.8, "process": "精车 / 铰孔 / 磨削", "use": "一般配合面"},
    {"ra": 1.6, "process": "车 / 铣 / 镗", "use": "一般加工面"},
    {"ra": 3.2, "process": "粗车 / 粗铣 / 钻孔", "use": "非配合面"},
    {"ra": 6.3, "process": "粗加工", "use": "自由表面"},
    {"ra": 12.5, "process": "铸造 / 锻后", "use": "毛坯面"},
]


def ra_quickref() -> dict:
    return {"map": RA_PROCESS_MAP, "common": RA_COMMON,
            "note": "参考 GB/T 1031、GB/T 131；同一种 Ra 可能有多种加工方法，需结合尺寸、材料与设备。"}
