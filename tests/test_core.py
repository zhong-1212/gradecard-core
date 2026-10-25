# -*- coding: utf-8 -*-
"""数值正确性测试：以 ISO 286 / GB/T 1800.2 标准表格值与材料力学公式手算值为基准。"""
import math

import pytest

from gradecard_core import tolerance as T
from gradecard_core import engineering as E
from gradecard_core import process_kb as P


# ---------------- tolerance ----------------

class TestStandardTolerance:
    @pytest.mark.parametrize("size,grade,want_um", [
        (50, "IT7", 25),    # 30-50 段 IT7
        (50, "IT6", 16),
        (25, "IT7", 21),    # 18-30 段
        (100, "IT7", 35),   # 80-120 段
        (10, "IT8", 22),
        (650, "IT7", 80),   # >500mm 大尺寸段
    ])
    def test_table_values(self, size, grade, want_um):
        assert T.standard_tolerance(size, grade) == want_um

    def test_it01_undefined_above_500(self):
        with pytest.raises(ValueError):
            T.standard_tolerance(650, "IT01")

    def test_bad_grade(self):
        with pytest.raises(ValueError):
            T.standard_tolerance(50, "IT17")
        with pytest.raises(ValueError):
            T.standard_tolerance(0, "IT7")
        with pytest.raises(ValueError):
            T.standard_tolerance(4000, "IT7")


class TestBandDeviations:
    def test_h7_hole(self):
        d = T.band_deviations(50, "H7")
        assert d == {"ES": 25, "EI": 0}

    def test_g6_shaft(self):
        d = T.band_deviations(50, "g6")
        assert d["es"] == -9          # 30-50 段 g 基本偏差
        assert d["ei"] == -9 - 16     # es - IT6

    def test_js_symmetry(self):
        for band in ("JS9", "js9"):
            d = T.band_deviations(50, band)
            half = T.standard_tolerance(50, "IT9") / 2
            assert abs(d.get("ES", d.get("es")) - half) < 1e-9
            lo = d.get("EI", d.get("ei"))
            assert abs(lo + half) < 1e-9

    def test_parse_band(self):
        assert T.parse_tolerance_band("H7") == ("H", "IT7")
        assert T.parse_tolerance_band("js6") == ("js", "IT6")
        with pytest.raises(ValueError):
            T.parse_tolerance_band("H")


class TestComputeFit:
    def test_phi50_H7g6(self):
        r = T.compute_fit(50, "H7", "g6")
        assert r["max_clearance"] == 25 - (-25)  # ES - ei
        assert r["min_clearance"] == 0 - (-9)
        assert r["fit_type"] == "间隙"

    def test_phi50_H7s6_interference(self):
        r = T.compute_fit(50, "H7", "s6")
        assert r["fit_type"] == "过盈"
        assert r["max_clearance"] <= 0 or r["min_clearance"] < 0

    def test_batch_errors_are_isolated(self):
        rows = T.compute_batch([{"size": 50, "hole": "H7", "shaft": "g6"},
                                {"size": 0, "hole": "X9", "shaft": "?"}])
        assert rows[0]["error"] is None
        assert rows[1]["error"] is not None


class TestReverseCompute:
    def test_finds_valid_combos(self):
        hits = T.reverse_compute(40, 0, 50, limit=5)
        assert hits
        for h in hits:
            assert 0 <= h["min_clearance"] and h["max_clearance"] <= 50

    def test_cost_sort_not_worse_than_precision_on_cost(self):
        a = T.reverse_compute(40, 0, 50, limit=1, sort="cost")[0]
        b = T.reverse_compute(40, 0, 50, limit=1, sort="precision")[0]
        assert a["cost_level"] <= b["cost_level"]


class TestPressFit:
    def test_hand_case(self):
        # Φ50, 过盈 50µm, L=60, 钢-钢 f=0.12, 轮毂外径默认 2d
        r = T.press_fit(50, 50, 60)
        # 厚壁圆筒：C_h=(4d²+d²)/(4d²-d²)+0.3=5/3+0.3; p=δ/(d*(Ch/E+Cs/E))
        ch = (100 ** 2 + 50 ** 2) / (100 ** 2 - 50 ** 2) + 0.30
        cs = 1 - 0.30
        p = 0.05 / (50 * (ch / 206000 + cs / 206000))
        assert abs(r["pressure_mpa"] - round(p, 2)) < 0.02
        f = 0.12 * p * math.pi * 50 * 60
        assert abs(r["press_force_kn"] - round(f / 1000, 2)) < 0.5

    def test_range_guard(self):
        with pytest.raises(ValueError):
            T.press_fit(600, 50, 60)


class TestThread:
    def test_m10_6g6h(self):
        r = T.thread_quickref(10)
        assert r["nominal"] == "M10"
        assert r["pitch"] == 1.5
        assert r["d2"] == 9.026
        assert r["external"]["major_max"] < 10  # 6g 有负偏差
        assert r["tap_hole"]["韧性材料"] == 8.5

    def test_unknown_size(self):
        with pytest.raises(ValueError):
            T.thread_quickref(7)


def test_process_for_grade():
    # 实测映射（PROCESS_TABLE/RA_TABLE 内部序 IT01→0, IT0→1, ITn→n+1）：
    # order[4-5](IT03-IT04)→Ra0.1, [6](IT05)→0.2, [7](IT6)→0.4, [8](IT7)→0.8, [9](IT8)→1.6
    assert T.process_for_grade("IT6")["ra_um"] == 0.4
    assert T.process_for_grade("IT7")["ra_um"] == 0.8
    assert T.process_for_grade("IT8")["ra_um"] == 1.6
    assert T.process_for_grade("IT01")["process"] == "研磨 / 珩磨"


# ---------------- engineering ----------------

class TestHardness:
    def test_roundtrip_hb_hv(self):
        r = E.hardness_convert(300, "HBW")
        assert r["ok"]
        hv = {x["scale"]: x["value"] for x in r["results"]}["HV"]
        assert 280 < hv < 320  # HB≈HV（布氏维氏在中段近似相等）

    def test_hrc_out_of_range(self):
        r = E.hardness_convert(10, "HRC")
        assert not r["ok"] and "20~67" in r["error"]

    def test_hrb_refuses(self):
        assert not E.hardness_convert(80, "HRB")["ok"]


class TestUnits:
    @pytest.mark.parametrize("group,v,f,t,want", [
        ("力", 1, "kN", "N", 1000.0),
        ("应力/压力", 1, "psi", "MPa", 0.006894757293),
        ("扭矩", 1, "N·m", "kgf·m", 0.10197162),
        ("长度", 1, "in", "mm", 25.4),
    ])
    def test_linear(self, group, v, f, t, want):
        r = E.unit_convert(group, v, f, t)
        assert r["ok"]
        assert abs(r["result"] - want) < 1e-6

    def test_temperature_offset(self):
        assert E.unit_convert("温度", 100, "℃", "℉")["result"] == 212.0
        assert E.unit_convert("温度", 0, "℃", "K")["result"] == 273.15

    def test_group_guard(self):
        assert not E.unit_convert("硬度", 1, "HB", "HV")["ok"]


class TestShaftCheck:
    def test_power_speed_torque(self):
        # P=10kW, n=1000rpm → T=95.5 N·m；Φ40 45钢调质 τ≈3.0 MPa << 40
        r = E.shaft_check(40, power_kw=10, speed_rpm=1000)
        assert r["ok"] and r["pass"]
        torques = [i for i in r["items"] if i["k"] == "传递扭矩 T"][0]
        assert "95.5" in torques["v"]

    def test_fail_case(self):
        r = E.shaft_check(5, torque_nm=5000)
        assert r["ok"] and not r["pass"]

    def test_missing_inputs(self):
        assert not E.shaft_check(40)["ok"]


class TestBeamCheck:
    def test_simply_center_hand(self):
        # F=1000N, L=100mm, 实心圆 d=20: M=FL/4=25000 N·mm, W=πd³/32=1570.8
        r = E.beam_check(case="simply_center", length_mm=100, section="circle",
                         dims={"d": 20}, force_n=1000)
        assert r["ok"]
        sigma = 25000 / (math.pi * 20 ** 3 / 32)
        assert any(abs(float(i["v"].split()[0]) - sigma) < 1
                   for i in r["items"] if i["k"] == "最大弯曲应力 σ")

    def test_cantilever_uniform(self):
        r = E.beam_check(case="cantilever_uniform", length_mm=200, section="rect",
                         dims={"b": 30, "h": 50}, load_n_per_mm=10)
        assert r["ok"]  # M=qL²/2=200000, W=bh²/6=12500 → σ=16 MPa 通过


class TestBolt:
    def test_m12_88(self):
        r = E.bolt_preload(diameter_mm=12, grade="8.8", friction_k=0.2)
        assert r["ok"]
        # As=π/4*(12-0.9382*1.75)²≈84.3 mm²; F=0.7*640*84.3≈37.8kN; T=0.2*F*d≈90.7N·m
        items = {i["k"]: i["v"] for i in r["items"]}
        assert "84.3" in items["应力截面积 As"]
        assert "37.8" in items["目标预紧力 F"]

    def test_over_yield_warns(self):
        r = E.bolt_preload(diameter_mm=12, grade="8.8", given_torque_nm=300)
        assert r["warnings"]


class TestGearBearing:
    def test_gear_recommendations_are_valid_bands(self):
        r = E.gear_fit(precision="7级", duty="normal")
        assert r["ok"]
        for band in r["recommend"]:
            hole, shaft = band.split("/")
            T.band_deviations(50, hole)
            T.band_deviations(50, shaft)

    def test_bearing_inner_normal(self):
        r = E.bearing_fit(rotation="inner", load="normal", diameter_mm=50)
        assert r["shaft"] == "k5" and r["housing"] == "JS7"


# ---------------- process_kb ----------------

class TestProcessKb:
    def test_45_steel(self):
        r = P.recommend_process("45#", {"application": "综合力学性能"})
        assert r and "调质" in r["recommended"]

    def test_category_fallback_no_db(self):
        # 未知牌号 + category 提示 → 走类别表，全程无数据库依赖
        r = P.recommend_process("XX999", {"category": "灰铸铁"})
        assert r and "时效" in r["recommended"]

    def test_unknown_returns_none(self):
        assert P.recommend_process("", {}) is None
        assert P.recommend_process("不存在牌号ZZZ", {}) is None
