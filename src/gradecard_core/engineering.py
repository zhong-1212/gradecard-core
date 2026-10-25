# -*- coding: utf-8 -*-
"""工程师向计算内核（v2.8）：硬度换算、单位换算、轴/梁强度校核、螺栓预紧力、齿轮/轴承配合。

设计约定：
1. 所有函数只做纯计算，不访问数据库、不抛 HTTP 异常，返回 dict（含 conclusion / notes / basis）。
2. 每个结果都带 basis（依据标准）与 notes（使用提示），便于前端与导出报告直接引用。
3. 结果仅供初步设计参考，正式设计须按标准原文与实物试验验证。
"""
from __future__ import annotations

import math

# ---------------------------------------------------------------------------
# 硬度换算
# ---------------------------------------------------------------------------

# 常用近似换算表（非奥氏体钢）：(HV, HBW, HRC)，HRC 为 None 表示该区间不适用 C 标尺。
# 依据 GB/T 1172 / ASTM E140 常用对照表整理，线性插值取近似值，仲裁须按标准实测。
_HARDNESS_ROWS = [
    (100, 100, None), (105, 105, None), (110, 110, None), (115, 115, None),
    (120, 120, None), (125, 125, None), (130, 130, None), (135, 135, None),
    (140, 140, None), (145, 145, None), (150, 150, None), (155, 155, None),
    (160, 160, None), (165, 165, None), (170, 170, None), (175, 175, None),
    (180, 180, None), (185, 185, None), (190, 190, None), (195, 195, None),
    (200, 200, None), (206, 205, None), (212, 210, None), (218, 215, None),
    (224, 220, None),
    (238, 226, 20), (243, 231, 21), (247, 235, 22), (252, 240, 23),
    (258, 245, 24), (264, 251, 25), (270, 257, 26), (276, 263, 27),
    (282, 269, 28), (288, 275, 29), (295, 283, 30), (302, 289, 31),
    (309, 296, 32), (316, 304, 33), (323, 311, 34), (331, 319, 35),
    (339, 327, 36), (347, 336, 37), (355, 345, 38), (364, 354, 39),
    (373, 363, 40), (382, 373, 41), (392, 382, 42), (402, 392, 43),
    (412, 402, 44), (421, 413, 45), (432, 424, 46), (442, 434, 47),
    (453, 446, 48), (464, 458, 49), (474, 471, 50), (486, 484, 51),
    (498, 496, 52), (509, 509, 53), (520, 522, 54), (532, 535, 55),
    (544, 548, 56), (556, 561, 57), (569, 575, 58), (581, 589, 59),
    (594, 603, 60), (607, 618, 61), (620, 633, 62), (634, 649, 63),
    (647, 665, 64), (661, 682, 65), (675, 700, 66), (690, 720, 67),
]

HARDNESS_SCALES = {
    "HB": "布氏硬度 HBW（10mm 球 / 3000kgf）",
    "HBW": "布氏硬度 HBW（硬质合金球）",
    "HBS": "布氏硬度 HBS（淬火钢球，旧标）",
    "HV": "维氏硬度 HV",
    "HRC": "洛氏硬度 HRC（C 标尺）",
    "HRB": "洛氏硬度 HRB（B 标尺，软材料）",
    "HRA": "洛氏硬度 HRA（硬质合金 / 薄硬化层）",
}

_HARDNESS_BASIS = "GB/T 1172 / ASTM E140 常用近似对照表（非奥氏体钢）"


def _interp(x, x0, x1, y0, y1):
    if x1 == x0:
        return float(y0)
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def _to_hv(scale, value):
    """把任意标尺折算为 HV 近似值。返回 (hv, hrc_hint, error)。"""
    scale = (scale or "").strip().upper()
    if scale in ("HB", "HBW", "HBS"):
        if value < 80 or value > 720:
            return None, None, "布氏硬度超出换算表覆盖范围（80~720 HBW）"
        for i in range(len(_HARDNESS_ROWS) - 1):
            a, b = _HARDNESS_ROWS[i], _HARDNESS_ROWS[i + 1]
            if a[1] <= value <= b[1]:
                return _interp(value, a[1], b[1], a[0], b[0]), None, None
        return None, None, "布氏硬度超出换算表覆盖范围"
    if scale == "HV":
        if value < 100 or value > 690:
            return None, None, "维氏硬度超出换算表覆盖范围（100~690 HV）"
        return float(value), None, None
    if scale == "HRC":
        if value < 20 or value > 67:
            return None, None, "洛氏 C 标尺超出换算表覆盖范围（20~67 HRC），低于 20 HRC 请改用 HRB 或 HV/HBW"
        for i in range(len(_HARDNESS_ROWS) - 1):
            a, b = _HARDNESS_ROWS[i], _HARDNESS_ROWS[i + 1]
            if a[2] is not None and b[2] is not None and a[2] <= value <= b[2]:
                return _interp(value, a[2], b[2], a[0], b[0]), None, None
        return None, None, "洛氏 C 标尺超出换算表覆盖范围"
    if scale == "HRA":
        hrc = value - 8.0
        if hrc < 20 or hrc > 67:
            return None, None, "HRA 超出可换算范围（需 HRA 60 以上）"
        hv, _, err = _to_hv("HRC", hrc)
        return hv, hrc, err
    if scale == "HRB":
        return None, None, "HRB 为软材料标尺，与 HBW/HV 无可靠近似换算，请直接使用 HBW 或 HV 实测"
    return None, None, "不支持的硬度标尺：%s" % scale


def hardness_convert(value, scale):
    """硬度换算：输入任一标尺，输出 HV / HBW / HRC 近似值。"""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return {"ok": False, "error": "硬度值必须是数字"}
    scale = (scale or "").strip().upper() or "HRC"
    hv, hrc_hint, err = _to_hv(scale, value)
    if hv is None:
        return {"ok": False, "error": err or "无法换算"}

    hbw = None
    hrc = None if hrc_hint is None else round(hrc_hint, 1)
    for i in range(len(_HARDNESS_ROWS) - 1):
        a, b = _HARDNESS_ROWS[i], _HARDNESS_ROWS[i + 1]
        if a[0] <= hv <= b[0]:
            hbw = _interp(hv, a[0], b[0], a[1], b[1])
            if hrc_hint is None and a[2] is not None and b[2] is not None:
                hrc = _interp(hv, a[0], b[0], a[2], b[2])
            break

    rows = [
        {"scale": "HV", "value": round(hv, 1)},
        {"scale": "HBW", "value": round(hbw, 1) if hbw is not None else None},
        {"scale": "HRC", "value": round(hrc, 1) if hrc is not None else None},
    ]
    notes = [
        "换算为经验近似值，不同标准（GB/T 1172、ASTM E140、DIN 50150）结果存在 2%~5% 差异。",
        "仲裁、验收与图纸标注必须使用标准规定的实测方法，不得以换算值代替。",
    ]
    if hbw is not None and hbw < 226:
        notes.append("HBW 低于 226 时洛氏 C 标尺不适用，建议改用 HRB 或直接标注 HBW/HV。")
    if hv > 650:
        notes.append("高硬度区（HRC>60）换算偏差明显增大，建议直接标注 HV。")
    return {
        "ok": True,
        "input": {"value": value, "scale": scale},
        "results": rows,
        "notes": notes,
        "basis": _HARDNESS_BASIS,
    }

# ---------------------------------------------------------------------------
# 单位换算
# ---------------------------------------------------------------------------

# 每组：单位 -> 相对该组基准单位的倍率
_UNIT_LINEAR = {
    "力": {"N": 1.0, "kN": 1000.0, "gf": 0.00980665, "kgf": 9.80665, "tf": 9806.65,
           "lbf": 4.4482216152605, "kip": 4448.2216152605},
    "应力/压力": {"MPa": 1.0, "N/mm2": 1.0, "kPa": 0.001, "Pa": 1e-06, "GPa": 1000.0,
              "bar": 0.1, "kgf/mm2": 9.80665, "kgf/cm2": 0.0980665, "psi": 0.006894757293,
              "ksi": 6.894757293, "atm": 0.101325},
    "长度": {"mm": 1.0, "um": 0.001, "cm": 10.0, "m": 1000.0,
           "in": 25.4, "ft": 304.8, "mil": 0.0254},
    "面积": {"mm2": 1.0, "cm2": 100.0, "m2": 1000000.0, "in2": 645.16},
    "体积": {"L": 1.0, "mL": 0.001, "m3": 1000.0, "cm3": 0.001, "in3": 0.016387064,
           "gal(US)": 3.785411784},
    "质量": {"kg": 1.0, "g": 0.001, "mg": 1e-06, "t": 1000.0, "lb": 0.45359237,
           "oz": 0.028349523125},
    "扭矩": {"N·m": 1.0, "N·mm": 0.001, "kgf·m": 9.80665, "kgf·cm": 0.0980665,
           "lbf·ft": 1.3558179483314, "lbf·in": 0.1129848290276},
    "功/能量": {"J": 1.0, "kJ": 1000.0, "cal": 4.184, "kcal": 4184.0,
             "kW·h": 3600000.0, "N·m": 1.0},
    "功率": {"W": 1.0, "kW": 1000.0, "MW": 1000000.0, "PS(公制马力)": 735.49875,
           "hp(英制马力)": 745.6998716},
    "导热率": {"W/(m·K)": 1.0, "kcal/(m·h·℃)": 1.163, "cal/(cm·s·℃)": 418.68,
            "Btu·in/(ft2·h·℉)": 0.1442279, "Btu/(ft·h·℉)": 1.7307347},
    "线膨胀系数": {"1e-6/K": 1.0, "1e-6/℃": 1.0, "1e-6/℉": 1.8},
    "密度": {"g/cm3": 1.0, "kg/m3": 0.001, "t/m3": 1.0, "lb/in3": 27.6799047},
    "导电率": {"%IACS": 1.0, "MS/m": 1.72413793, "S/m": 1.72413793e-06},
}

_UNIT_TEMPERATURE = {"℃": 1.0, "°C": 1.0, "K": 1.0, "℉": 1.0, "°F": 1.0}

_UNIT_BASIS = "GB/T 3102 法定计量单位与常用工程单位换算关系（换算系数为定义值）"


def unit_groups():
    """返回所有可换算的物理量分组及单位列表。"""
    out = []
    for name, units in _UNIT_LINEAR.items():
        out.append({"group": name, "units": list(units.keys())})
    out.append({"group": "温度", "units": ["℃", "K", "℉"]})
    return out


def _is_temp(u):
    return (u or "").strip() in _UNIT_TEMPERATURE


def unit_convert(group, value, from_unit, to_unit):
    """单位换算：同一物理量分组内任意单位互换（温度支持零点偏移）。"""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return {"ok": False, "error": "数值必须是数字"}
    group = (group or "").strip()
    from_unit = (from_unit or "").strip()
    to_unit = (to_unit or "").strip()
    if not from_unit or not to_unit:
        return {"ok": False, "error": "请选择源单位与目标单位"}

    if group == "温度" or (_is_temp(from_unit) and _is_temp(to_unit)):
        if not (_is_temp(from_unit) and _is_temp(to_unit)):
            return {"ok": False, "error": "温度单位仅支持 ℃ / K / ℉"}
        celsius = {"℃": value, "°C": value, "K": value - 273.15,
                   "℉": (value - 32.0) * 5.0 / 9.0, "°F": (value - 32.0) * 5.0 / 9.0}[from_unit]
        out = {"℃": celsius, "°C": celsius, "K": celsius + 273.15,
               "℉": celsius * 9.0 / 5.0 + 32.0, "°F": celsius * 9.0 / 5.0 + 32.0}[to_unit]
        return {
            "ok": True, "group": "温度", "value": value, "from_unit": from_unit,
            "result": round(out, 6), "to_unit": to_unit,
            "basis": "热力学温度定义（0 ℃ = 273.15 K）",
            "notes": ["温度换算含零点偏移，与倍率换算不同，请勿套用比例关系。"],
        }

    units = _UNIT_LINEAR.get(group)
    if not units:
        return {"ok": False, "error": "不支持的物理量分组：%s" % group}
    if from_unit not in units:
        return {"ok": False, "error": "分组「%s」不支持源单位 %s" % (group, from_unit)}
    if to_unit not in units:
        return {"ok": False, "error": "分组「%s」不支持目标单位 %s" % (group, to_unit)}
    base = value * units[from_unit]
    out = base / units[to_unit]
    notes = []
    if group == "导电率":
        notes.append("按 100%IACS = 58 MS/m（国际退火铜标准）换算；铜合金导电率常以 %IACS 标注。")
    if group == "导热率":
        notes.append("1 W/(m·K) = 0.8598 kcal/(m·h·℃)，工程手册常混用，选材对比时务必统一单位。")
    return {
        "ok": True, "group": group, "value": value, "from_unit": from_unit,
        "result": round(out, 8), "to_unit": to_unit,
        "basis": _UNIT_BASIS,
        "notes": notes or ["换算系数为标准定义值，结果可直接用于图纸与技术文件。"],
    }

# ---------------------------------------------------------------------------
# 轴强度 / 刚度校核
# ---------------------------------------------------------------------------

_SHAFT_MATERIALS = {
    "45钢(正火)": {"torsion": 30.0, "bending": 95.0, "E": 206.0},
    "45钢(调质)": {"torsion": 40.0, "bending": 135.0, "E": 206.0},
    "40Cr(调质)": {"torsion": 52.0, "bending": 165.0, "E": 206.0},
    "42CrMo(调质)": {"torsion": 60.0, "bending": 190.0, "E": 206.0},
    "20CrMnTi(渗碳淬火)": {"torsion": 55.0, "bending": 175.0, "E": 206.0},
    "Q235(正火)": {"torsion": 25.0, "bending": 80.0, "E": 200.0},
    "1Cr18Ni9Ti(固溶)": {"torsion": 35.0, "bending": 120.0, "E": 193.0},
    "HT200(铸铁)": {"torsion": 20.0, "bending": 55.0, "E": 120.0},
}


def shaft_materials():
    return [{"name": k, "torsion": v["torsion"], "bending": v["bending"], "E": v["E"]}
            for k, v in _SHAFT_MATERIALS.items()]


def _pick_shaft_material(material):
    m = (material or "").strip()
    if m in _SHAFT_MATERIALS:
        return m, dict(_SHAFT_MATERIALS[m])
    for k, v in _SHAFT_MATERIALS.items():
        if m and (m in k or k.startswith(m)):
            return k, dict(v)
    return "45钢(调质)", dict(_SHAFT_MATERIALS["45钢(调质)"])


def _fnum(v, default=None):
    if v in (None, ""):
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def shaft_check(diameter_mm, power_kw=None, speed_rpm=None, torque_nm=None,
                bending_moment_nm=0.0, material="45钢(调质)", torsion_allow_mpa=None,
                bending_allow_mpa=None, alpha=0.6, length_mm=None, load_type="center"):
    """轴强度与刚度校核：扭转剪应力、弯扭合成应力、最小轴径、挠度估算。

    alpha：扭转剪应力循环特性折算系数，静应力 0.3，脉动循环 0.6，对称循环 1.0。
    """
    try:
        d = float(diameter_mm)
    except (TypeError, ValueError):
        return {"ok": False, "error": "轴径必须是数字"}
    if d <= 0:
        return {"ok": False, "error": "轴径必须大于 0"}
    name, mat = _pick_shaft_material(material)
    ta = _fnum(torsion_allow_mpa) or mat["torsion"]
    ba = _fnum(bending_allow_mpa) or mat["bending"]
    alpha = _fnum(alpha, 0.6)
    e_mod = mat["E"] * 1000.0

    torque = _fnum(torque_nm)
    if torque is None:
        p, n = _fnum(power_kw), _fnum(speed_rpm)
        if p is None or n is None:
            return {"ok": False, "error": "请提供「功率 + 转速」或直接提供扭矩"}
        if n <= 0:
            return {"ok": False, "error": "转速必须大于 0"}
        torque = 9550.0 * p / n

    wt = math.pi * d ** 3 / 16.0
    w = math.pi * d ** 3 / 32.0
    i = math.pi * d ** 4 / 64.0
    area = math.pi * d ** 2 / 4.0

    t_nmm = torque * 1000.0
    tau = t_nmm / wt
    bending = (_fnum(bending_moment_nm, 0.0) or 0.0) * 1000.0
    sigma = bending / w if bending else 0.0
    sigma_eq = math.sqrt(sigma ** 2 + 4.0 * (alpha * tau) ** 2)

    d_min = (t_nmm / (0.2 * ta)) ** (1.0 / 3.0) if ta > 0 else None
    d_min_key = d_min * 1.05 if d_min else None

    items = [
        {"k": "传递扭矩 T", "v": "%.1f N·m" % torque},
        {"k": "抗扭截面系数 Wt", "v": "%.1f mm3" % wt},
        {"k": "扭转剪应力 τ", "v": "%.1f MPa" % tau},
        {"k": "许用扭转剪应力 [τ]", "v": "%.0f MPa" % ta},
    ]
    if bending:
        items.append({"k": "弯曲应力 σ", "v": "%.1f MPa" % sigma})
        items.append({"k": "许用弯曲应力 [σ]", "v": "%.0f MPa" % ba})
        items.append({"k": "弯扭合成应力 σca", "v": "%.1f MPa（α=%.2f）" % (sigma_eq, alpha)})
    items.append({"k": "安全系数（扭转）", "v": ("%.2f" % (ta / tau)) if tau else "—"})
    if d_min:
        items.append({"k": "理论最小轴径", "v": "%.1f mm；单键槽按 5%% 削弱取 %.1f mm" % (d_min, d_min_key)})
    items.append({"k": "截面积 A", "v": "%.1f mm2" % area})
    items.append({"k": "惯性矩 I", "v": "%.0f mm4" % i})

    L = _fnum(length_mm)
    if L and L > 0:
        force = 2.0 * bending / L if bending else 0.0
        if force:
            if (load_type or "center") == "cantilever":
                defl = force * L ** 3 / (3.0 * e_mod * i)
                label = "悬臂梁端部集中力挠度"
            else:
                defl = force * L ** 3 / (48.0 * e_mod * i)
                label = "简支梁跨中集中力挠度"
            items.append({"k": label, "v": "%.3f mm（跨距 %.0f mm，当量集中力 %.0f N）" % (defl, L, force)})
            items.append({"k": "挠度限值参考", "v": "一般传动轴 ≤ (0.0003~0.0005)L = %.3f~%.3f mm"
                          % (0.0003 * L, 0.0005 * L)})

    torsion_ok = tau <= ta
    strength_ok = sigma_eq <= (ba if bending else ta)
    d_ok = (d >= d_min) if d_min else True
    ok = bool(torsion_ok and strength_ok and d_ok)
    if ok:
        conclusion = "通过：当前轴径满足扭转与弯曲强度要求。"
    else:
        reasons = []
        if not torsion_ok:
            reasons.append("扭转剪应力超过许用值")
        if not strength_ok:
            reasons.append("弯扭合成应力超过许用值")
        if not d_ok:
            reasons.append("轴径小于理论最小轴径")
        conclusion = "不通过：" + "；".join(reasons) + "。建议加大轴径或选用更高强度材料。"

    return {
        "ok": True, "pass": ok, "conclusion": conclusion, "material": name,
        "items": items,
        "basis": "材料力学圆轴扭转/弯曲公式；许用应力参照《机械设计手册》常用轴用材料推荐值",
        "notes": [
            "许用应力已含常规安全裕度，高速、重载、冲击轴建议单独做疲劳强度校核。",
            "轴上开键槽、花键、螺纹时截面被削弱，需按实际有效截面重新核算。",
            "挠度估算按等直径光轴，阶梯轴应按当量直径折算。",
        ],
    }

# ---------------------------------------------------------------------------
# 梁 / 支架强度校核
# ---------------------------------------------------------------------------

BEAM_CASES = {
    "simply_center": "简支梁 · 跨中集中力",
    "simply_uniform": "简支梁 · 均布载荷",
    "cantilever_end": "悬臂梁 · 端部集中力",
    "cantilever_uniform": "悬臂梁 · 均布载荷",
}

SECTION_TYPES = {"circle": "实心圆", "tube": "圆管", "rect": "矩形"}


def _section_props(kind, dims):
    """返回 (面积 mm2, 惯性矩 I mm4, 抗弯截面系数 W mm3, 说明)。"""
    kind = (kind or "circle").strip()
    if kind == "circle":
        d = _fnum((dims or {}).get("d")) or 0.0
        if d <= 0:
            raise ValueError("圆截面直径必须大于 0")
        return (math.pi * d ** 2 / 4, math.pi * d ** 4 / 64, math.pi * d ** 3 / 32,
                "实心圆 d=%.1f mm" % d)
    if kind == "tube":
        D = _fnum((dims or {}).get("D")) or 0.0
        d = _fnum((dims or {}).get("d")) or 0.0
        if D <= 0 or d <= 0 or d >= D:
            raise ValueError("圆管外径必须大于内径，且均大于 0")
        return (math.pi * (D ** 2 - d ** 2) / 4, math.pi * (D ** 4 - d ** 4) / 64,
                math.pi * (D ** 4 - d ** 4) / (32 * D), "圆管 D=%.1f / d=%.1f mm" % (D, d))
    if kind == "rect":
        b = _fnum((dims or {}).get("b")) or 0.0
        h = _fnum((dims or {}).get("h")) or 0.0
        if b <= 0 or h <= 0:
            raise ValueError("矩形宽高必须大于 0")
        return (b * h, b * h ** 3 / 12, b * h ** 2 / 6,
                "矩形 b=%.1f × h=%.1f mm（h 为受力方向高度）" % (b, h))
    raise ValueError("不支持的截面类型")


def beam_check(case="simply_center", length_mm=None, section="circle", dims=None,
               force_n=0.0, load_n_per_mm=0.0, elastic_modulus_gpa=206.0,
               allowable_bending_mpa=135.0, deflection_limit_ratio=0.0005):
    """梁/支架强度与刚度校核：最大弯矩、最大弯曲应力、最大挠度。"""
    case = (case or "simply_center").strip()
    if case not in BEAM_CASES:
        return {"ok": False, "error": "不支持的梁型"}
    L = _fnum(length_mm)
    if L is None or L <= 0:
        return {"ok": False, "error": "跨度必须大于 0"}
    F = _fnum(force_n, 0.0) or 0.0
    q = _fnum(load_n_per_mm, 0.0) or 0.0
    try:
        area, I, W, sec_desc = _section_props(section, dims or {})
    except (ValueError, TypeError) as exc:
        return {"ok": False, "error": str(exc)}
    if I <= 0:
        return {"ok": False, "error": "截面惯性矩必须大于 0"}
    if case in ("simply_center", "cantilever_end") and F <= 0:
        return {"ok": False, "error": "集中力必须大于 0"}
    if case in ("simply_uniform", "cantilever_uniform") and q <= 0:
        return {"ok": False, "error": "均布载荷必须大于 0"}

    e_mod = (_fnum(elastic_modulus_gpa, 206.0) or 206.0) * 1000.0
    if case == "simply_center":
        mmax = F * L / 4.0
        ymax = F * L ** 3 / (48.0 * e_mod * I)
        total_load = F
    elif case == "simply_uniform":
        mmax = q * L ** 2 / 8.0
        ymax = 5.0 * q * L ** 4 / (384.0 * e_mod * I)
        total_load = q * L
    elif case == "cantilever_end":
        mmax = F * L
        ymax = F * L ** 3 / (3.0 * e_mod * I)
        total_load = F
    else:
        mmax = q * L ** 2 / 2.0
        ymax = q * L ** 4 / (8.0 * e_mod * I)
        total_load = q * L

    sigma = mmax / W
    ab = _fnum(allowable_bending_mpa, 135.0) or 135.0
    ratio = _fnum(deflection_limit_ratio, 0.0005) or 0.0005
    limit = ratio * L
    strength_ok = sigma <= ab
    stiff_ok = ymax <= limit
    ok = bool(strength_ok and stiff_ok)
    if ok:
        conclusion = "通过：弯曲强度与挠度均在允许范围内。"
    else:
        reasons = []
        if not strength_ok:
            reasons.append("弯曲应力 %.1f MPa 超过许用 %.0f MPa" % (sigma, ab))
        if not stiff_ok:
            reasons.append("挠度 %.3f mm 超过限值 %.3f mm" % (ymax, limit))
        conclusion = "不通过：" + "；".join(reasons) + "。建议加大截面、缩短跨度或改选高模量材料。"

    return {
        "ok": True, "pass": ok, "conclusion": conclusion,
        "case": case, "case_label": BEAM_CASES[case],
        "items": [
            {"k": "梁型", "v": BEAM_CASES[case]},
            {"k": "截面", "v": sec_desc},
            {"k": "跨度 L", "v": "%.1f mm" % L},
            {"k": "总载荷", "v": "%.0f N" % total_load},
            {"k": "最大弯矩 Mmax", "v": "%.0f N·mm" % mmax},
            {"k": "抗弯截面系数 W", "v": "%.1f mm3" % W},
            {"k": "最大弯曲应力 σ", "v": "%.1f MPa" % sigma},
            {"k": "许用弯曲应力 [σ]", "v": "%.0f MPa" % ab},
            {"k": "最大挠度 ymax", "v": "%.4f mm" % ymax},
            {"k": "挠度限值", "v": "%.4f mm（L/%.0f）" % (limit, 1.0 / ratio)},
            {"k": "截面积 A", "v": "%.1f mm2" % area},
        ],
        "basis": "材料力学梁弯曲公式；挠度限值参照《机械设计手册》一般机械 L/2000~L/3000",
        "notes": [
            "计算假定材料线弹性、小变形，不含应力集中与动载系数。",
            "冲击、交变载荷工况需乘以动载系数并做疲劳校核。",
            "焊接件应另行核算焊缝强度。",
        ],
    }

# ---------------------------------------------------------------------------
# 螺栓预紧力与拧紧扭矩
# ---------------------------------------------------------------------------

# GB/T 3098.1 紧固件机械性能：抗拉强度最小值 / 屈服强度最小值（MPa）
BOLT_GRADES = {
    "4.8": {"rm": 400, "rp": 320},
    "5.6": {"rm": 500, "rp": 300},
    "5.8": {"rm": 500, "rp": 400},
    "6.8": {"rm": 600, "rp": 480},
    "8.8": {"rm": 800, "rp": 640},
    "10.9": {"rm": 1040, "rp": 940},
    "12.9": {"rm": 1220, "rp": 1100},
}

# ISO 724 / GB/T 196 粗牙螺纹标准螺距
METRIC_PITCH = {
    3: 0.5, 4: 0.7, 5: 0.8, 6: 1.0, 8: 1.25, 10: 1.5, 12: 1.75, 14: 2.0,
    16: 2.0, 18: 2.5, 20: 2.5, 22: 2.5, 24: 3.0, 27: 3.0, 30: 3.5, 33: 3.5,
    36: 4.0, 39: 4.0, 42: 4.5, 45: 4.5, 48: 5.0, 52: 5.0, 56: 5.5, 60: 5.5,
    64: 6.0,
}

FRICTION_K = {
    "0.10 无润滑发黑": 0.10,
    "0.14 磷化/镀锌+润滑": 0.14,
    "0.16 镀锌未润滑": 0.16,
    "0.20 一般干态钢-钢": 0.20,
    "0.24 不锈钢干态": 0.24,
    "0.30 严重锈蚀/粗糙": 0.30,
}


def _stress_area(d, p):
    """螺纹应力截面积 As（ISO 724 / GB/T 196）：As = π/4 · (d - 0.9382P)²。"""
    return math.pi / 4.0 * (d - 0.9382 * p) ** 2


def bolt_metrics():
    out = []
    for d, p in sorted(METRIC_PITCH.items()):
        out.append({"spec": "M%d" % d, "d": d, "pitch": p, "as": round(_stress_area(d, p), 1)})
    return out


def bolt_preload(diameter_mm=None, pitch=None, grade="8.8", friction_k=0.2,
                 method="torque", given_torque_nm=None, given_force_n=None,
                 preload_ratio=None):
    """螺栓预紧力 / 拧紧扭矩计算与校核。

    method：torque（扭矩法，预紧力取 0.7·ReL·As）/ angle（转角法，取 0.9·ReL·As）
    """
    d = _fnum(diameter_mm)
    if d is None:
        return {"ok": False, "error": "请选择或输入螺纹公称直径"}
    if d <= 0:
        return {"ok": False, "error": "螺纹公称直径必须大于 0"}
    p = _fnum(pitch)
    standard_p = METRIC_PITCH.get(int(d)) if d == int(d) else None
    if not p:
        p = standard_p
    if not p or p <= 0 or p >= d:
        return {"ok": False, "error": "螺距无效，请检查输入"}

    g = str(grade or "8.8").strip()
    if g not in BOLT_GRADES:
        return {"ok": False, "error": "不支持的强度等级，可选：%s" % "、".join(BOLT_GRADES.keys())}
    rp = BOLT_GRADES[g]["rp"]
    rm = BOLT_GRADES[g]["rm"]
    as_area = _stress_area(d, p)
    k = _fnum(friction_k, 0.2) or 0.2
    ratio = 0.9 if (method or "").strip() == "angle" else 0.7
    pr = _fnum(preload_ratio)
    if pr:
        ratio = pr

    force = ratio * rp * as_area
    torque = k * force * d / 1000.0
    spec_txt = "M%g × %g" % (d, p)
    if standard_p and abs(p - standard_p) < 1e-9:
        spec_txt += "（粗牙）"
    else:
        spec_txt += "（细牙/自定义）"

    items = [
        {"k": "螺纹规格", "v": spec_txt},
        {"k": "应力截面积 As", "v": "%.1f mm2" % as_area},
        {"k": "强度等级", "v": "%s（Rm ≥ %d MPa，ReL ≥ %d MPa）" % (g, rm, rp)},
        {"k": "预紧力系数", "v": "%.2f × ReL × As（%s）" % (ratio, "转角法" if method == "angle" else "扭矩法")},
        {"k": "目标预紧力 F", "v": "%.0f N（%.1f kN）" % (force, force / 1000.0)},
        {"k": "拧紧扭矩 T", "v": "%.1f N·m" % torque},
        {"k": "摩擦系数 K", "v": "%.2f" % k},
    ]

    warn = []
    tg = _fnum(given_torque_nm)
    if tg:
        fg = tg * 1000.0 / (k * d)
        items.append({"k": "按给定扭矩反算预紧力", "v": "%.0f N（%.1f kN）" % (fg, fg / 1000.0)})
        if fg > 0.9 * rp * as_area:
            warn.append("给定扭矩对应预紧力已接近屈服极限，存在螺栓屈服或螺纹脱扣风险。")
    f0 = _fnum(given_force_n)
    if f0:
        items.append({"k": "按给定预紧力所需扭矩", "v": "%.1f N·m" % (k * f0 * d / 1000.0)})
        if f0 > 0.9 * rp * as_area:
            warn.append("给定预紧力超过 0.9·ReL·As，超出常规拧紧控制范围。")

    return {
        "ok": True, "pass": not warn, "warnings": warn,
        "conclusion": "计算完成：目标预紧力 %.1f kN，建议拧紧扭矩 %.1f N·m。" % (force / 1000.0, torque),
        "items": items,
        "basis": "VDI 2230 / GB/T 16823.2 拧紧扭矩 T = K·F·d；应力截面积按 ISO 724 公式；强度等级按 GB/T 3098.1",
        "notes": [
            "摩擦系数 K 离散性极大（0.08~0.35），扭矩法预紧力误差可达 ±30%，重要连接请在试件上标定。",
            "同一法兰上的螺栓应按对角/星形分 2~3 次拧紧至目标扭矩。",
            "疲劳、受剪、振动工况需另做防松与强度校核。",
        ],
    }

# ---------------------------------------------------------------------------
# 齿轮配合推荐
# ---------------------------------------------------------------------------

GEAR_PRECISION = ["5级", "6级", "7级", "8级", "9级"]
GEAR_DUTY = {
    "light": "轻载 / 无冲击",
    "normal": "一般载荷",
    "heavy": "重载 / 冲击",
    "precision": "精密传动（低噪声、高精度）",
}


def gear_fit(precision="7级", pitch_diameter_mm=100.0, speed_mps=5.0,
             duty="normal", removable=True):
    """齿轮与轴（齿轮孔 / 轴颈）配合推荐。"""
    d = _fnum(pitch_diameter_mm)
    v = _fnum(speed_mps, 0.0) or 0.0
    if d is None or d <= 0:
        return {"ok": False, "error": "分度圆直径必须大于 0"}
    prec = (precision or "7级").strip()
    if prec not in GEAR_PRECISION:
        return {"ok": False, "error": "精度等级可选：%s" % "、".join(GEAR_PRECISION)}
    duty = (duty or "normal").strip()
    if duty not in GEAR_DUTY:
        return {"ok": False, "error": "工作性质可选：%s" % "、".join(GEAR_DUTY.keys())}

    level = GEAR_PRECISION.index(prec)
    if duty == "precision" or level <= 1:
        base = ["H6/js5", "H6/h5"]
        detail = "高精度传动需控制配合间隙与偏心，优先 H6/js5（可拆）或 H6/h5（轻敲装配）。"
    elif duty == "heavy" or level >= 3:
        base = ["H7/k6", "H7/m6", "H7/n6"]
        detail = "重载或冲击载荷优先过渡/小过盈配合，避免微动磨损造成键槽松动。"
    else:
        base = ["H7/js6", "H7/k6", "H7/h6"]
        detail = "一般传动推荐 H7/js6（需拆卸）或 H7/k6（定位可靠）。"

    if removable is False:
        filtered = [b for b in base if not b.endswith("h6") and not b.endswith("h5")]
        base = filtered or ["H7/n6", "H7/p6"]
        detail += " 不常拆卸时应选小过盈配合以防松动。"

    extra = []
    if v > 15:
        extra.append("圆周速度 %.1f m/s 属高速传动，建议提高齿轮精度至 6 级并做动平衡。" % v)
    if d > 400:
        extra.append("分度圆直径较大（%.0f mm），应核算悬臂安装时的轴挠度与齿向偏斜。" % d)

    return {
        "ok": True,
        "conclusion": "推荐配合：%s" % " / ".join(base),
        "recommend": base,
        "detail": detail,
        "items": [
            {"k": "齿轮精度等级", "v": prec},
            {"k": "分度圆直径", "v": "%.1f mm" % d},
            {"k": "圆周速度", "v": "%.1f m/s" % v},
            {"k": "工作性质", "v": GEAR_DUTY[duty]},
            {"k": "推荐孔/轴配合", "v": " / ".join(base)},
            {"k": "配合性质", "v": "过渡配合（定位可靠，需辅助键/销传递扭矩）"},
            {"k": "键联接推荐", "v": "普通平键 GB/T 1096，键宽按轴径查表，正常联接取 H9/h9"},
        ],
        "extra": extra,
        "basis": "GB/T 10095 齿轮精度；GB/T 1800.2 极限与配合；《机械设计手册》齿轮与轴配合推荐",
        "notes": [
            "齿轮孔与轴的配合必须与键/花键联接方式、装配工艺一起确定，单独看配合值易出错。",
            "过盈配合装配需校核压装力或加热温度，避免齿面退火。",
            "推荐公差带可配合本库 tolerance.compute_fit() 验算间隙/过盈量。",
        ],
    }


# ---------------------------------------------------------------------------
# 轴承配合推荐
# ---------------------------------------------------------------------------

BEARING_LOAD = {
    "light": "轻载荷 P ≤ 0.07C",
    "normal": "正常载荷 0.07C < P ≤ 0.15C",
    "heavy": "重载荷 P > 0.15C",
}
BEARING_ROTATION = {
    "inner": "内圈旋转（轴旋转、载荷方向固定）",
    "outer": "外圈旋转（外壳旋转、载荷方向相对套圈旋转）",
    "static": "内外圈均静止（定向载荷）",
}


def bearing_fit(rotation="inner", load="normal", diameter_mm=50.0,
                split_housing=False, need_disassembly=True):
    """滚动轴承与轴 / 外壳孔配合推荐（GB/T 275 参考）。"""
    rotation = (rotation or "inner").strip()
    load = (load or "normal").strip()
    if rotation not in BEARING_ROTATION:
        return {"ok": False, "error": "旋转状态可选：%s" % "、".join(BEARING_ROTATION.keys())}
    if load not in BEARING_LOAD:
        return {"ok": False, "error": "载荷状态可选：%s" % "、".join(BEARING_LOAD.keys())}
    d = _fnum(diameter_mm)
    if d is None or d <= 0:
        return {"ok": False, "error": "轴承内径必须大于 0"}

    if rotation == "inner":
        shaft = {"light": "j5", "normal": "k5", "heavy": "m5"}[load]
        shaft_desc = "内圈承受旋转载荷，须保证内圈与轴不产生相对爬行，采用过渡/小过盈配合。"
    else:
        shaft = {"light": "g6", "normal": "h6", "heavy": "js6"}[load]
        shaft_desc = ("内圈相对载荷静止，配合可松，便于装配。" if rotation == "outer"
                      else "定向载荷，内圈配合按载荷大小选取即可。")

    if rotation == "outer":
        housing = {"light": "K7", "normal": "M7", "heavy": "N7"}[load]
        housing_desc = "外圈承受旋转载荷，外壳孔需过渡/过盈配合，防止外圈爬行。"
    elif rotation == "inner":
        housing = {"light": "H7", "normal": "JS7", "heavy": "H7"}[load]
        housing_desc = "外圈相对载荷静止，通常取 H7 或 JS7，轴向需另设定位。"
    else:
        housing = "J7"
        housing_desc = "定向载荷，外壳孔取 J7，兼顾定位与装配。"

    extra = []
    if split_housing:
        housing = {"light": "H7", "normal": "H7", "heavy": "H8"}[load]
        extra.append("剖分式外壳无法形成过盈，外圈易爬行，应改用整体式外壳或加装外圈端盖/挡圈。")
    if need_disassembly:
        extra.append("频繁拆卸场合过盈量不宜过大，建议选用可分离型轴承或加装紧定套。")
    if load == "heavy" and rotation == "inner":
        extra.append("重载内圈配合建议加热装配（80~100 ℃ 油浴），避免敲击损伤滚道。")
    extra.append("配合松紧会改变轴承游隙：过盈越大游隙越小，精密轴承必须复核安装后游隙。")

    return {
        "ok": True,
        "conclusion": "轴公差带 %s / 外壳孔公差带 %s" % (shaft, housing),
        "shaft": shaft, "housing": housing,
        "items": [
            {"k": "轴承内径", "v": "%.1f mm" % d},
            {"k": "旋转状态", "v": BEARING_ROTATION[rotation]},
            {"k": "载荷状态", "v": BEARING_LOAD[load]},
            {"k": "轴公差带", "v": "%s —— %s" % (shaft, shaft_desc)},
            {"k": "外壳孔公差带", "v": "%s —— %s" % (housing, housing_desc)},
            {"k": "轴颈粗糙度", "v": "Ra ≤ 0.8 μm（普通轴承）/ Ra ≤ 0.4 μm（精密轴承）"},
            {"k": "外壳孔粗糙度", "v": "Ra ≤ 1.6 μm"},
            {"k": "轴颈圆柱度", "v": "≤ 公称直径的 IT5~IT6 级"},
        ],
        "extra": extra,
        "basis": "GB/T 275 滚动轴承 配合；ISO 492 轴承公差；《机械设计手册》轴承配合推荐",
        "notes": [
            "配合选择的核心是判断「载荷方向相对套圈是否旋转」，判错会导致跑圈或装配困难。",
            "表中数值适用于实心轴与钢/铸铁整体外壳，空心轴与轻合金外壳需适当加大过盈。",
            "推荐公差带可配合本库 tolerance.compute_fit() 验算间隙/过盈量。",
        ],
    }