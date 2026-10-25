# -*- coding: utf-8 -*-
"""gradecard-core：面向机械工程师的纯 Python 工程计算库。

零第三方依赖，仅标准库。包含三个模块：
- tolerance   ISO 286 公差配合（0–3150mm）、反向选配、压装、螺纹、GD&T、粗糙度
- engineering 硬度换算、单位换算、轴/梁校核、螺栓预紧力、齿轮/轴承配合推荐
- process_kb  材料牌号 → 热处理/成型工艺知识库（碳钢、不锈钢、铝合金、塑料等）
"""
from . import engineering, process_kb, tolerance
from .engineering import (
    bearing_fit,
    beam_check,
    bolt_preload,
    gear_fit,
    hardness_convert,
    shaft_check,
    unit_convert,
)
from .process_kb import recommend_process
from .tolerance import (
    assembly_yield,
    band_deviations,
    compute_fit,
    press_fit,
    process_for_grade,
    reverse_compute,
    standard_tolerance,
    suggest_fit,
    thread_quickref,
)

__version__ = "0.1.0"

__all__ = [
    "tolerance", "engineering", "process_kb",
    "standard_tolerance", "band_deviations", "compute_fit", "suggest_fit",
    "reverse_compute", "assembly_yield", "press_fit", "thread_quickref",
    "process_for_grade",
    "hardness_convert", "unit_convert", "shaft_check", "beam_check",
    "bolt_preload", "gear_fit", "bearing_fit", "recommend_process",
    "__version__",
]
