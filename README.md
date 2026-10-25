# gradecard-core

面向机械工程师的**纯 Python 工程计算库**。零第三方依赖（只用标准库），可直接嵌入 CAD 插件、MES、报价系统或任何后端。

来自 [GradeCard 材料选型助手](https://gradecard.online) 的生产内核，v2.1–v4.5 在线上环境打磨过。

## 能力一览

| 模块 | 功能 | 依据 |
|---|---|---|
| `tolerance` | ISO 286 标准公差 IT01–IT16（0–3150mm）、孔/轴偏差、任意配合计算、常用配合速查、**反向选配**（给间隙范围→推荐公差带）、装配良率估计、过盈压装力/传扭/热装温差、螺纹 M3–M64 公差速查、GD&T、粗糙度↔工艺对照 | GB/T 1800 / ISO 286 / ISO 965 / GB/T 1184 |
| `engineering` | 硬度换算 HB↔HV↔HRC↔HRA、14 组工程单位换算、轴强度刚度校核、梁校核（4 种载荷工况 × 3 种截面）、螺栓预紧力与拧紧扭矩、齿轮/轴承配合推荐 | GB/T 1172 / ASTM E140 / VDI 2230 / GB/T 275 |
| `process_kb` | 材料牌号 → 热处理/成型工艺知识库（碳钢、合金钢、不锈钢、铸铁、铝合金、钛合金、高温合金、塑料、橡胶、陶瓷等） | 机械设计手册典型值 |

所有结果都带 `basis`（标准依据）和 `notes`（使用提醒），可直接进报告。

## 快速上手

```bash
pip install gradecard-core
```

```python
from gradecard_core import compute_fit, reverse_compute, hardness_convert, bolt_preload

# ① 配合计算：Φ50 H7/g6
r = compute_fit(50, "H7", "g6")
# {'max_clearance': 39.0, 'min_clearance': 9.0, 'fit_type': '间隙', ...}

# ② 反向选配：Φ40 希望间隙 0~50µm，按成本排序
for fit in reverse_compute(40, 0, 50, sort="cost"):
    print(fit["hole"], fit["shaft"], fit["min_clearance"], fit["max_clearance"])

# ③ 硬度换算：300 HBW → HV/HRC
hardness_convert(300, "HBW")

# ④ M12-8.8 螺栓，摩擦系数 0.2：目标预紧力与扭矩
bolt_preload(diameter_mm=12, grade="8.8", friction_k=0.2)

# ⑤ 工艺推荐：45Cr 传动轴，要求耐磨
from gradecard_core import recommend_process
recommend_process("45", {"application": "耐磨传动轴"})
```

## API 摘要

### tolerance
- `standard_tolerance(size, grade)` — 标准公差值 (µm)
- `band_deviations(size, band)` — 公差带上下偏差（H7/g6/JS9/K8…）
- `compute_fit(size, hole, shaft)` — 配合：间隙/过盈 + 类型
- `enhance_fit_result(size, hole, shaft)` — 配合 + 工艺方法 + 粗糙度 + 良率
- `reverse_compute(size, gap_min, gap_max, sort="precision"|"cost")` — 反向选配
- `assembly_yield(size, hole, shaft, sigma=6)` — 正态近似装配良率
- `press_fit(...)` — 过盈压装力 / 可传扭矩 / 热装冷装温差
- `thread_quickref(nominal, ext_class, int_class)` — 粗牙螺纹公差 + 底孔建议
- `process_for_grade(grade)` / `cost_for_grade(grade)` — IT 等级 → 加工方法与成本档
- `suggest_fit(scene)` / `COMMON_FITS` / `SCENARIOS` — 场景化速查

### engineering
- `hardness_convert(value, scale)` — HB/HBW/HV/HRC/HRA 互算（含适用范围守卫）
- `unit_convert(group, value, from_unit, to_unit)` / `unit_groups()` — 力/应力/扭矩/功率/导热率… 14 组
- `shaft_check(diameter_mm, power_kw, speed_rpm, ...)` — 扭转/弯扭合成/最小轴径/挠度
- `beam_check(case, length_mm, section, dims, ...)` — 弯矩/应力/挠度校核
- `bolt_preload(diameter_mm, grade, friction_k, method="torque"|"angle", ...)`
- `gear_fit(...)` / `bearing_fit(...)` — 齿轮、滚动轴承配合推荐

### process_kb
- `recommend_process(grade, cond)` — cond: `{hardness, load, application, keep_tough, category}`；纯内存匹配，无数据库依赖

## 免责说明

数值为工程参考级（标准表格 + 手册典型值 + 线性插值）。正式设计请按标准原文与实物试验验证——每个函数返回的 `notes` 里都写明了适用边界。

## License

MIT
