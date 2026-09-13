"""ConcreteAI - Deterministic ACI 211.1 mix design tool (hackathon prototype).
Absolute volume method. Units: psi, kg/m3, cft. Code basis: ACI 211.1 / ACI 318 / PBC 2021."""

WATER_KG = 193.0            # ACI 211.1 Table 6.3.3 (20mm agg, 75-100mm slump)
AIR_PCT = 2.0
CEMENT_SG, WATER_SG, SAND_SG, AGG_SG = 3.15, 1.0, 2.62, 2.68
DRY_RODDED_KG_M3 = 1600     # dry-rodded unit weight of coarse aggregate
COARSE_VOL_FACTOR = 0.62    # ACI 211.1 Table 6.3.6 (20mm agg, FM 2.8 sand)
M3_TO_CFT = 35.3147

STRENGTH_WC = [(5000, 0.38), (4000, 0.45), (3000, 0.55), (2500, 0.62), (2000, 0.70)]

EXPOSURE_RULES = {
    "mild":     {"min_psi": 2500, "max_wc": 0.60, "label": "Mild"},
    "moderate": {"min_psi": 3000, "max_wc": 0.50, "label": "Moderate"},
    "severe":   {"min_psi": 3500, "max_wc": 0.45, "label": "Severe"},
    "coastal":  {"min_psi": 4000, "max_wc": 0.40, "label": "Very severe / coastal & sulfate"},
}

def _wc_for_strength(psi):
    for target, wc in STRENGTH_WC:
        if psi >= target:
            return wc
    return 0.70

def calculate_mix_design(target_strength_psi: int, exposure: str) -> dict:
    exposure = (exposure or "mild").strip().lower()
    if exposure not in EXPOSURE_RULES:
        exposure = "mild"
    rule = EXPOSURE_RULES[exposure]
    warnings, final_psi = [], int(target_strength_psi)

    if final_psi < rule["min_psi"]:
        warnings.append(f"CODE OVERRIDE (ACI 318 / PBC 2021): {rule['label']} exposure requires "
                        f"minimum {rule['min_psi']} psi. Requested {final_psi} psi upgraded to {rule['min_psi']} psi.")
        final_psi = rule["min_psi"]

    wc_strength = _wc_for_strength(final_psi)
    wc = min(wc_strength, rule["max_wc"])
    if wc < wc_strength:
        warnings.append(f"DURABILITY GOVERNS: w/c capped at {wc:.2f} for {rule['label']} exposure "
                        f"(strength alone would allow {wc_strength:.2f}).")

    water = WATER_KG
    cement = water / wc
    coarse = COARSE_VOL_FACTOR * DRY_RODDED_KG_M3
    vol = cement/(CEMENT_SG*1000) + water/(WATER_SG*1000) + AIR_PCT/100 + coarse/(AGG_SG*1000)
    sand = (1.0 - vol) * SAND_SG * 1000

    bags = cement / 50.0
    sand_cft = sand / (SAND_SG * 1000) * M3_TO_CFT
    agg_cft = coarse / (AGG_SG * 1000) * M3_TO_CFT

    return {
        "requested_psi": int(target_strength_psi),
        "final_psi": final_psi,
        "exposure": rule["label"],
        "wc_ratio": round(wc, 2),
        "water_kg_m3": round(water),
        "cement_kg_m3": round(cement),
        "sand_kg_m3": round(sand),
        "coarse_agg_kg_m3": round(coarse),
        "cement_bags_50kg": round(bags, 1),
        "sand_cft_m3": round(sand_cft, 1),
        "coarse_agg_cft_m3": round(agg_cft, 1),
        "site_ratio_per_bag": f"1 bag : {round(sand_cft / bags, 1)} cft sand : {round(agg_cft / bags, 1)} cft crush",
        "warnings": warnings,
    }
