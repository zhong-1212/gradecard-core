# -*- coding: utf-8 -*-
"""2.3 工艺推荐知识库：牌号 × 工况 → 推荐热处理/表面工艺（规则引擎）。"""

# 单牌号工艺条目：processes 中 recommended=True 的为默认推荐
PROCESS_KB = {
    "45": {
        "name": "45 号钢（优质碳素结构钢）",
        "processes": [
            {"name": "正火", "params": "加热 830-860℃ 空冷", "after_hardness": "170-217HB",
             "use": "改善切削加工性、消除锻造/焊接应力", "recommended": False},
            {"name": "调质（淬火+高温回火）", "params": "淬火 820-840℃ 水冷/PAG，回火 520-580℃ 空冷",
             "after_hardness": "220-280HB", "use": "综合力学性能优良，适合轴、齿轮、连杆、法兰", "recommended": True},
            {"name": "表面感应淬火（中频）", "params": "感应加热 860-900℃，水/PAG 冷却，低温回火 180-200℃",
             "after_hardness": "表层 45-52HRC", "use": "轴颈、花键、导轨等要求耐磨部位（先调质）", "recommended": False},
        ],
        "tips": ["45# 淬透性一般，截面大于 60mm 后心部性能下降，重载大件建议换 40Cr/42CrMo",
                 "表面淬火前必须先调质，保证心部综合性能"],
    },
    "40CR": {
        "name": "40Cr（合金结构钢）",
        "processes": [
            {"name": "调质（淬火+高温回火）", "params": "淬火 850℃ 油冷，回火 520-620℃",
             "after_hardness": "240-320HB", "use": "轴、齿轮、连杆、螺栓等中等截面承力件", "recommended": True},
            {"name": "表面感应淬火（中频）", "params": "感应加热 900℃，PAG/水冷却，低温回火 180-220℃",
             "after_hardness": "表层 48-55HRC", "use": "花键、曲轴轴颈等耐磨部位（先调质）", "recommended": False},
            {"name": "氮化（离子/气体）", "params": "调质后 500-560℃ 氮化 20-60h",
             "after_hardness": "表面 850-1000HV", "use": "高耐磨、高疲劳寿命场合", "recommended": False},
        ],
        "tips": ["40Cr 油淬临界直径约 40mm，更大截面用 42CrMo"],
    },
    "42CRMO": {
        "name": "42CrMo（合金结构钢）",
        "processes": [
            {"name": "调质（淬火+高温回火）", "params": "淬火 840-860℃ 油冷，回火 560-640℃",
             "after_hardness": "260-340HB", "use": "大截面重载轴、齿轮、曲轴、高强度螺栓", "recommended": True},
            {"name": "淬火+低温回火", "params": "淬火 850℃ 油冷，回火 200-250℃",
             "after_hardness": "42-50HRC", "use": "要求高强度的结构件", "recommended": False},
            {"name": "氮化", "params": "调质后 510-560℃ 氮化 40-80h",
             "after_hardness": "表面 900-1100HV", "use": "重载耐磨传动件", "recommended": False},
        ],
        "tips": ["42CrMo 淬透性好，适合大截面重载件"],
    },
    "35CRMO": {
        "name": "35CrMo（合金结构钢）",
        "processes": [
            {"name": "调质（淬火+高温回火）", "params": "淬火 850℃ 油冷，回火 540-600℃",
             "after_hardness": "240-300HB", "use": "重要轴、齿轮、高压紧固件", "recommended": True},
            {"name": "淬火+中温回火", "params": "淬火 850℃ 油冷，回火 400-450℃",
             "after_hardness": "35-42HRC", "use": "要求弹塑性兼备的连接件", "recommended": False},
        ],
        "tips": [],
    },
    "20CRMNTI": {
        "name": "20CrMnTi（渗碳钢）",
        "processes": [
            {"name": "渗碳淬火（渗碳+淬火+低温回火）", "params": "渗碳 920-940℃ 8-16h，直接淬火/二次淬火，回火 180-200℃",
             "after_hardness": "表面 58-62HRC，心部 30-45HRC", "use": "齿轮、轴类等要求表硬心韧的耐磨传动件", "recommended": True},
            {"name": "调质（淬火+高温回火）", "params": "淬火 860℃ 油冷，回火 520-580℃",
             "after_hardness": "220-280HB", "use": "不需表面高硬度的普通结构件", "recommended": False},
        ],
        "tips": ["20CrMnTi 为渗碳钢，核心优势是表面高硬 + 心部高韧，传动齿轮首选"],
    },
    "38CRMOAL": {
        "name": "38CrMoAl（氮化钢）",
        "processes": [
            {"name": "调质（淬火+高温回火）", "params": "淬火 930-950℃ 油冷，回火 600-680℃",
             "after_hardness": "240-300HB", "use": "氮化前的预备热处理", "recommended": False},
            {"name": "氮化（气体/离子）", "params": "调质后 500-560℃ 氮化 30-70h",
             "after_hardness": "表面 950-1150HV", "use": "精密主轴、镗杆、齿轮等高耐磨高精度件", "recommended": True},
        ],
        "tips": ["38CrMoAl 氮化后变形极小，适合精密耐磨件；氮化层薄，不适合冲击载荷"],
    },
    "20": {
        "name": "20 号钢（优质碳素结构钢）",
        "processes": [
            {"name": "正火", "params": "加热 900-930℃ 空冷", "after_hardness": "130-170HB",
             "use": "一般结构件、焊接件", "recommended": True},
            {"name": "渗碳淬火", "params": "渗碳 920℃，淬火 780-800℃ 水冷，低温回火",
             "after_hardness": "表面 56-62HRC", "use": "要求耐磨的轻载零件（如拨叉、销）", "recommended": False},
        ],
        "tips": [],
    },
    "Q235": {
        "name": "Q235（碳素结构钢）",
        "processes": [
            {"name": "热轧/正火", "params": "热轧态直接使用，或 900-920℃ 正火",
             "after_hardness": "约 130-160HB", "use": "一般结构件、支架、焊接件，不做强化处理", "recommended": True},
        ],
        "tips": ["Q235 为低碳普通结构钢，一般不进行调质；需强度时选用 Q355/45#"],
    },
    "Q355": {
        "name": "Q355（低合金高强度结构钢）",
        "processes": [
            {"name": "热轧/正火", "params": "热轧态使用，或 900-940℃ 正火", "after_hardness": "150-200HB",
             "use": "桥梁、建筑、工程机械结构件", "recommended": True},
        ],
        "tips": [],
    },
    "65MN": {
        "name": "65Mn（弹簧钢）",
        "processes": [
            {"name": "淬火+中温回火", "params": "淬火 810-830℃ 油冷，回火 380-480℃",
             "after_hardness": "38-48HRC", "use": "弹簧、发条、锯条等弹性零件", "recommended": True},
        ],
        "tips": ["65Mn 弹性极限高但淬透性有限，大截面弹簧用 60Si2Mn"],
    },
    "60SI2MN": {
        "name": "60Si2Mn（弹簧钢）",
        "processes": [
            {"name": "淬火+中温回火", "params": "淬火 860-880℃ 油冷，回火 430-480℃",
             "after_hardness": "40-48HRC", "use": "汽车板簧、螺旋弹簧、弹性元件", "recommended": True},
        ],
        "tips": ["60Si2Mn 淬透性好、弹性高，适合截面较大的弹簧"],
    },
    "GCR15": {
        "name": "GCr15（轴承钢）",
        "processes": [
            {"name": "球化退火", "params": "加热 780-810℃ 炉冷至 650℃ 以下", "after_hardness": "179-207HB",
             "use": "冷加工前软化，改善切削性", "recommended": False},
            {"name": "淬火+低温回火", "params": "淬火 830-850℃ 油冷，回火 150-170℃",
             "after_hardness": "60-65HRC", "use": "轴承套圈、滚动体、精密量具", "recommended": True},
        ],
        "tips": ["GCr15 淬火后必须及时低温回火，防止开裂"],
    },
    "T8": {
        "name": "T8（碳素工具钢）",
        "processes": [
            {"name": "球化退火", "params": "加热 740-760℃ 保温后炉冷", "after_hardness": "≤187HB",
             "use": "冷加工前预备处理", "recommended": False},
            {"name": "淬火+低温回火", "params": "淬火 780-800℃ 水冷/油冷，回火 160-200℃",
             "after_hardness": "58-62HRC", "use": "冲头、刀具、量具等耐磨工具", "recommended": True},
        ],
        "tips": [],
    },
    "T10": {
        "name": "T10（碳素工具钢）",
        "processes": [
            {"name": "淬火+低温回火", "params": "淬火 770-790℃ 水冷/油冷，回火 160-200℃",
             "after_hardness": "60-64HRC", "use": "耐磨工具、冲模、量规", "recommended": True},
        ],
        "tips": [],
    },
    "CR12MOV": {
        "name": "Cr12MoV（冷作模具钢）",
        "processes": [
            {"name": "淬火+回火", "params": "预热 850℃，淬火 1020-1040℃ 油冷，回火 180-220℃ 两次",
             "after_hardness": "60-63HRC", "use": "冷冲模、冷镦模、切边模", "recommended": True},
            {"name": "真空淬火+回火", "params": "真空炉 1020℃ 淬火，回火 180-200℃",
             "after_hardness": "58-62HRC", "use": "精密模具，变形小", "recommended": False},
        ],
        "tips": ["Cr12MoV 高碳高铬，淬火变形小，耐磨性好"],
    },
    "5CRNIMO": {
        "name": "5CrNiMo（热作模具钢）",
        "processes": [
            {"name": "淬火+回火", "params": "预热 650℃，淬火 830-860℃ 油冷，回火 490-540℃",
             "after_hardness": "39-47HRC", "use": "锤锻模、热锻模", "recommended": True},
        ],
        "tips": ["热作模具钢回火要充分，防止早期热疲劳开裂"],
    },
    "W6MO5CR4V2": {
        "name": "W6Mo5Cr4V2（高速钢）",
        "processes": [
            {"name": "淬火+回火", "params": "预热 850/1050℃，淬火 1210-1240℃ 油冷，回火 540-560℃ 三次",
             "after_hardness": "63-66HRC", "use": "高速切削刀具、钻头、铣刀", "recommended": True},
        ],
        "tips": ["高速钢必须三次回火，消除残余奥氏体"],
    },
    "304": {
        "name": "304（SUS304，奥氏体不锈钢）",
        "processes": [
            {"name": "固溶处理", "params": "加热 1010-1120℃ 水冷/快速冷却", "after_hardness": "≤187HB",
             "use": "消除加工硬化与晶界析出，恢复耐蚀性", "recommended": True},
            {"name": "冷作硬化", "params": "冷轧/冷拉变形 20-40%", "after_hardness": "可达 300-400HV",
             "use": "弹簧、弹片等利用冷作强化的零件", "recommended": False},
        ],
        "tips": ["304 不能通过淬火强化，只能固溶+冷作硬化", "避免 450-850℃ 敏化温度区间，防止晶间腐蚀"],
    },
    "316": {
        "name": "316（SUS316，奥氏体不锈钢）",
        "processes": [
            {"name": "固溶处理", "params": "加热 1010-1150℃ 水冷", "after_hardness": "≤187HB",
             "use": "耐氯离子腐蚀设备、化工部件", "recommended": True},
        ],
        "tips": ["316 含 Mo，耐点蚀性能优于 304"],
    },
    "174PH": {
        "name": "17-4PH（沉淀硬化不锈钢）",
        "processes": [
            {"name": "固溶+时效", "params": "固溶 1040℃ 空冷，时效 480℃ 4h 或 550℃ 4h",
             "after_hardness": "38-44HRC（H1025）", "use": "高强度耐蚀结构件、轴、阀杆", "recommended": True},
        ],
        "tips": [],
    },
    "6061": {
        "name": "6061 铝合金",
        "processes": [
            {"name": "固溶+时效（T6）", "params": "固溶 530℃ 水淬，时效 175℃ 8h",
             "after_hardness": "约 95HB", "use": "结构件、型材、机架", "recommended": True},
        ],
        "tips": ["6061 时效后强度中等、耐蚀与焊接性好"],
    },
    "6063": {
        "name": "6063 铝合金",
        "processes": [
            {"name": "固溶+时效（T5/T6）", "params": "固溶 520℃ 水淬，时效 175℃ 6-8h",
             "after_hardness": "约 73-90HB", "use": "门窗、散热器、装饰型材", "recommended": True},
        ],
        "tips": [],
    },
    "7075": {
        "name": "7075 铝合金",
        "processes": [
            {"name": "固溶+时效（T6/T73）", "params": "固溶 470℃ 水淬，时效 120℃ 24h（T6）",
             "after_hardness": "约 150-160HB", "use": "航空结构件、高强轻量化零件", "recommended": True},
        ],
        "tips": ["7075 强度高但应力腐蚀敏感，必要时选 T73 过时效"],
    },
    "2A12": {
        "name": "2A12（LY12）铝合金",
        "processes": [
            {"name": "固溶+时效（T4）", "params": "固溶 495℃ 水淬，自然时效 4 天以上",
             "after_hardness": "约 120HB", "use": "飞机蒙皮、铆钉、结构件", "recommended": True},
        ],
        "tips": [],
    },
    "T2": {
        "name": "T2（紫铜）",
        "processes": [
            {"name": "退火", "params": "加热 500-700℃ 水冷", "after_hardness": "约 40-50HB",
             "use": "消除冷加工硬化，提高导电性", "recommended": True},
            {"name": "冷作硬化", "params": "冷轧/冷拉变形", "after_hardness": "可达 100HV 以上",
             "use": "导电弹性元件、接触件", "recommended": False},
        ],
        "tips": ["T2 导电导热性能优良，强度靠冷作硬化获得"],
    },
    "H62": {
        "name": "H62（黄铜）",
        "processes": [
            {"name": "退火", "params": "加热 600-700℃ 空冷", "after_hardness": "约 50-60HB",
             "use": "冷加工中间软化", "recommended": True},
            {"name": "冷作硬化", "params": "冷轧/冷拉", "after_hardness": "可达 150HV",
             "use": "弹簧、接插件、耐磨件", "recommended": False},
        ],
        "tips": [],
    },
    "QSN65-0.1": {
        "name": "QSn6.5-0.1（锡磷青铜）",
        "processes": [
            {"name": "退火", "params": "加热 600-650℃ 空冷", "after_hardness": "约 70-90HB",
             "use": "中间软化", "recommended": False},
            {"name": "冷作硬化", "params": "冷轧变形 20-50%", "after_hardness": "180-220HV",
             "use": "弹簧、导电耐磨件、轴瓦", "recommended": True},
        ],
        "tips": ["锡磷青铜弹性和耐磨性优良，适合做弹性接触件"],
    },
    "TC4": {
        "name": "TC4（Ti-6Al-4V）钛合金",
        "processes": [
            {"name": "固溶+时效", "params": "固溶 940-960℃ 水淬，时效 500-580℃ 4-8h",
             "after_hardness": "约 36-40HRC", "use": "航空结构件、高强度轻量化件", "recommended": True},
        ],
        "tips": ["钛合金加热要注意气氛保护，避免吸氢"],
    },
    "GH4169": {
        "name": "GH4169（Inconel 718）高温合金",
        "processes": [
            {"name": "固溶+时效", "params": "固溶 950-980℃ 空冷，时效 720℃ 8h + 620℃ 8h",
             "after_hardness": "约 40-45HRC", "use": "高温涡轮盘、紧固件（650℃ 以下）", "recommended": True},
        ],
        "tips": [],
    },
}

def _nonmetal_entry(name: str, main_proc: str, use: str, extra: str = ""):
    """构造非金属类别工艺回退条目（不适用金属热处理）。"""
    entry = {
        "name": name,
        "processes": [
            {"name": main_proc, "params": "按牌号与模具/设备参数设定", "after_hardness": "",
             "use": use, "recommended": True},
            {"name": "挤出成型", "params": "板材/棒材/型材连续成型", "after_hardness": "",
             "use": "板棒管等连续截面制品", "recommended": False},
            {"name": "CNC 机加工", "params": "三轴/五轴铣削加工", "after_hardness": "",
             "use": "精度要求高的成品件", "recommended": False},
            {"name": "激光切割", "params": "板材下料", "after_hardness": "",
             "use": "板类零件下料", "recommended": False},
            {"name": "粘接/热焊接", "params": "结构胶粘接或热板焊", "after_hardness": "",
             "use": "组装成型件", "recommended": False},
        ],
        "tips": ["塑料/橡胶/陶瓷等非金属不适用淬火、调质、渗碳、氮化等金属热处理",
                 "成型与机加工是主要工艺路径，热塑性可多次成型，热固性一次成型后不可重塑"],
    }
    if extra:
        entry["tips"].append(extra)
    return entry


# 材料大类回退工艺（未收录单牌号时按类别推荐）
CATEGORY_PROCESS = {
    "碳素结构钢": {
        "name": "碳素结构钢（Q 系列）",
        "processes": [
            {"name": "热轧/正火", "params": "热轧态使用或 900-940℃ 正火", "after_hardness": "130-180HB",
             "use": "一般结构件，不做强化", "recommended": True},
        ],
        "tips": ["普通碳素结构钢一般不调质，承力件建议选 45#/Q355"],
    },
    "优质碳素结构钢": {
        "name": "优质碳素结构钢",
        "processes": [
            {"name": "正火", "params": "按含碳量加热 830-930℃ 空冷", "after_hardness": "150-220HB",
             "use": "改善组织与切削性", "recommended": False},
            {"name": "调质（淬火+高温回火）", "params": "淬火水冷/油冷 + 520-620℃ 回火", "after_hardness": "220-320HB",
             "use": "轴、齿轮、连杆等承力件", "recommended": True},
        ],
        "tips": [],
    },
    "合金结构钢": {
        "name": "合金结构钢",
        "processes": [
            {"name": "调质（淬火+高温回火）", "params": "淬火油冷 + 520-640℃ 回火", "after_hardness": "240-340HB",
             "use": "中高强度承力件", "recommended": True},
            {"name": "渗碳淬火（低碳合金钢）", "params": "渗碳 920-940℃ + 淬火 + 低温回火", "after_hardness": "表面 58-62HRC",
             "use": "耐磨传动件", "recommended": False},
            {"name": "氮化", "params": "调质后 500-560℃ 氮化", "after_hardness": "表面 850-1100HV",
             "use": "高耐磨高精度件", "recommended": False},
        ],
        "tips": [],
    },
    "弹簧钢": {
        "name": "弹簧钢",
        "processes": [
            {"name": "淬火+中温回火", "params": "淬火油冷，回火 380-480℃", "after_hardness": "38-48HRC",
             "use": "弹性元件", "recommended": True},
        ],
        "tips": [],
    },
    "轴承钢": {
        "name": "轴承钢",
        "processes": [
            {"name": "球化退火 + 淬火+低温回火", "params": "球化退火后 830-850℃ 油淬，150-170℃ 回火",
             "after_hardness": "60-65HRC", "use": "轴承与精密耐磨件", "recommended": True},
        ],
        "tips": [],
    },
    "碳素工具钢": {
        "name": "碳素工具钢",
        "processes": [
            {"name": "淬火+低温回火", "params": "淬火水冷/油冷，回火 160-200℃", "after_hardness": "58-64HRC",
             "use": "刀具、量具、耐磨件", "recommended": True},
        ],
        "tips": [],
    },
    "合金工具钢": {
        "name": "合金工具钢/模具钢",
        "processes": [
            {"name": "淬火+回火", "params": "按钢种 980-1080℃ 淬火，180-250℃ 回火两次", "after_hardness": "58-63HRC",
             "use": "冷作模具、耐磨工具", "recommended": True},
        ],
        "tips": [],
    },
    "热作模具钢": {
        "name": "热作模具钢",
        "processes": [
            {"name": "淬火+高温回火", "params": "预热后 1020-1060℃ 淬火，540-600℃ 回火两次", "after_hardness": "42-52HRC",
             "use": "压铸模、热锻模", "recommended": True},
        ],
        "tips": [],
    },
    "冷作模具钢": {
        "name": "冷作模具钢",
        "processes": [
            {"name": "淬火+回火", "params": "预热后 950-1030℃ 淬火，180-260℃ 回火", "after_hardness": "58-63HRC",
             "use": "冷冲模、冷镦模", "recommended": True},
        ],
        "tips": [],
    },
    "塑料模具钢": {
        "name": "塑料模具钢",
        "processes": [
            {"name": "预硬处理", "params": "调质至 28-38HRC 交货，直接加工", "after_hardness": "28-38HRC",
             "use": "注塑模、压铸模镶件", "recommended": True},
        ],
        "tips": [],
    },
    "高速工具钢": {
        "name": "高速工具钢",
        "processes": [
            {"name": "淬火+三次回火", "params": "1200-1240℃ 油淬，540-560℃ 回火 3 次", "after_hardness": "63-66HRC",
             "use": "高速切削刀具", "recommended": True},
        ],
        "tips": [],
    },
    "奥氏体不锈钢": {
        "name": "奥氏体不锈钢",
        "processes": [
            {"name": "固溶处理", "params": "加热 1010-1150℃ 快速冷却", "after_hardness": "≤200HB",
             "use": "恢复耐蚀性、消除加工硬化", "recommended": True},
            {"name": "冷作硬化", "params": "冷轧/冷拉变形", "after_hardness": "300-400HV",
             "use": "弹性件、高强度紧固件", "recommended": False},
        ],
        "tips": ["奥氏体不锈钢不能淬火强化"],
    },
    "马氏体不锈钢": {
        "name": "马氏体不锈钢",
        "processes": [
            {"name": "调质（淬火+回火）", "params": "淬火 980-1060℃ 油冷/空冷，回火 600-700℃",
             "after_hardness": "220-320HB", "use": "汽轮机叶片、阀杆、刀具", "recommended": True},
        ],
        "tips": [],
    },
    "铁素体不锈钢": {
        "name": "铁素体不锈钢",
        "processes": [
            {"name": "退火", "params": "加热 780-850℃ 空冷", "after_hardness": "≤183HB",
             "use": "消除冷加工应力", "recommended": True},
        ],
        "tips": ["铁素体不锈钢不能通过热处理强化"],
    },
    "沉淀硬化不锈钢": {
        "name": "沉淀硬化不锈钢",
        "processes": [
            {"name": "固溶+时效", "params": "固溶 1020-1060℃ + 480-620℃ 时效 4h", "after_hardness": "32-46HRC",
             "use": "高强度耐蚀件", "recommended": True},
        ],
        "tips": [],
    },
    "双相不锈钢": {
        "name": "双相不锈钢",
        "processes": [
            {"name": "固溶处理", "params": "加热 1020-1100℃ 水冷", "after_hardness": "约 290HB",
             "use": "耐应力腐蚀的化工/海工件", "recommended": True},
        ],
        "tips": [],
    },
    "铝合金": {
        "name": "变形/铸造铝合金",
        "processes": [
            {"name": "固溶+时效（T6）", "params": "固溶 470-535℃ 水淬 + 160-180℃ 时效 6-12h",
             "after_hardness": "90-160HB", "use": "结构件、机架、轻量化件", "recommended": True},
        ],
        "tips": [],
    },
    "铜合金": {
        "name": "铜及铜合金",
        "processes": [
            {"name": "退火", "params": "加热 500-700℃ 空冷/水冷", "after_hardness": "40-90HB",
             "use": "中间软化、消除应力", "recommended": False},
            {"name": "冷作硬化", "params": "冷轧/冷拉变形 20-50%", "after_hardness": "100-220HV",
             "use": "弹性与导电耐磨件", "recommended": True},
        ],
        "tips": [],
    },
    "钛合金": {
        "name": "钛及钛合金",
        "processes": [
            {"name": "固溶+时效", "params": "α+β 型 940-960℃ 固溶 + 500-580℃ 时效 4-8h", "after_hardness": "32-42HRC",
             "use": "高强度轻量化结构件", "recommended": True},
        ],
        "tips": [],
    },
    "高温合金": {
        "name": "镍基/高温合金",
        "processes": [
            {"name": "固溶+时效", "params": "固溶 950-1080℃ + 720-780℃/620℃ 双级时效", "after_hardness": "32-46HRC",
             "use": "高温承力件、涡轮件", "recommended": True},
        ],
        "tips": [],
    },
    "球墨铸铁": {
        "name": "球墨铸铁",
        "processes": [
            {"name": "正火", "params": "加热 880-920℃ 空冷，去应力退火", "after_hardness": "200-280HB",
             "use": "提高强度与耐磨性的铸件", "recommended": True},
            {"name": "等温淬火（ADI）", "params": "奥氏体化 850-900℃ 后 250-400℃ 盐浴等温", "after_hardness": "269-400HB",
             "use": "高强耐磨齿轮、凸轮", "recommended": False},
        ],
        "tips": [],
    },
    "灰铸铁": {
        "name": "灰铸铁",
        "processes": [
            {"name": "时效处理（去应力退火）", "params": "加热 500-550℃ 保温后缓冷", "after_hardness": "160-240HB",
             "use": "消除铸造应力，稳定尺寸", "recommended": True},
        ],
        "tips": ["灰铸铁只能去应力，不能强化"],
    },
    "可锻铸铁": {
        "name": "可锻铸铁",
        "processes": [
            {"name": "石墨化退火", "params": "加热 900-960℃ 长时间退火", "after_hardness": "120-269HB",
             "use": "韧性较好的薄壁铸件", "recommended": True},
        ],
        "tips": [],
    },
    "塑料-通用": _nonmetal_entry("通用塑料", "注塑成型", "家电/日用品/一般结构件"),
    "塑料-工程": _nonmetal_entry("工程塑料", "注塑成型", "结构件/齿轮/轴套等承载件"),
    "塑料-特种": _nonmetal_entry("特种工程塑料", "注塑成型", "高温/耐蚀/高强工况件"),
    "热固性塑料": _nonmetal_entry("热固性塑料", "模压成型", "绝缘件/耐热件/电器结构件", extra="热固性不能二次熔融回收，边角料难以重新注塑"),
    "橡胶": _nonmetal_entry("橡胶弹性体", "模压硫化", "密封圈/减震件/软管", extra="橡胶以模压/注射硫化成型，注意硫化温度与时间"),
    "复合材料": _nonmetal_entry("复合材料", "模压/拉挤/缠绕成型", "轻量化结构/耐蚀壳体/板材", extra="碳纤/玻纤复合注意铺层方向与模具成本"),
    "玻璃": _nonmetal_entry("玻璃", "成型+钢化/退火", "视窗/器皿/隔断", extra="深加工需热弯、钢化或夹胶工艺"),
    "陶瓷": _nonmetal_entry("陶瓷", "干压/等静压成型+烧结", "耐磨/绝缘/耐高温件", extra="烧结后尺寸收缩，通常需磨削精加工"),
    "木材": _nonmetal_entry("木材", "锯切/刨削/CNC加工", "家具/结构/包装", extra="注意含水率与防潮防腐处理"),
    "泡沫": _nonmetal_entry("泡沫", "发泡成型", "保温/缓冲/填充", extra="泡沫件常用模塑发泡或切割成型"),
    "保温材料": _nonmetal_entry("保温材料", "切割/贴敷/浇注", "设备管道保温/隔音", extra="施工后需防潮层保护，注意防火等级"),
}


def recommend_process(grade: str, cond: dict):
    """按牌号与工况返回工艺推荐。cond: hardness/load/application/keep_tough。"""
    g = (grade or "").strip().upper().replace("#", "")
    if not g:
        return None
    entry = PROCESS_KB.get(g)
    if not entry:
        for key, e in PROCESS_KB.items():
            if g.startswith(key) or key.startswith(g):
                entry = e
                break
    category = ""
    if not entry:
        # 可选类别提示：调用方传入 cond["category"]（如「碳钢」「塑料-工程」）时，
        # 按材料类别给出通用工艺推荐；不传则保持纯知识库匹配，无外部依赖。
        category = str(cond.get("category") or "").strip()
        if category:
            entry = CATEGORY_PROCESS.get(category)
    if not entry:
        return None
    procs = entry.get("processes") or []
    if not procs:
        return None
    recs = [p for p in procs if p.get("recommended")]
    chosen = recs[0] if recs else procs[0]
    application = cond.get("application") or ""
    hardness = cond.get("hardness") or ""
    keep_tough = cond.get("keep_tough")
    if "耐磨" in application or "硬度" in application or "表面" in application:
        surf = next((p for p in procs if ("表面" in p["name"] or "渗碳" in p["name"] or "氮化" in p["name"])), None)
        if surf:
            chosen = surf
    elif "弹簧" in application:
        spr = next((p for p in procs if "中温回火" in p["name"]), None)
        if spr:
            chosen = spr
    elif keep_tough or "综合" in application:
        tq = next((p for p in procs if "调质" in p["name"]), None)
        if tq:
            chosen = tq
    elif "HRC" in hardness:
        try:
            hv = float(hardness.replace("HRC", "").strip().split("-")[-1])
            if hv >= 48:
                surf2 = next((p for p in procs if ("表面" in p["name"] or "渗碳" in p["name"] or "氮化" in p["name"])), None)
                if surf2:
                    chosen = surf2
        except (TypeError, ValueError):
            pass
    return {
        "grade": grade.strip(),
        "name": entry.get("name", ""),
        "category": category or entry.get("category", ""),
        "recommended": chosen.get("name", ""),
        "processes": procs,
        "tips": entry.get("tips", []),
        "note": "工艺参数为标准手册典型值，实际需结合零件截面尺寸与设备调整",
    }