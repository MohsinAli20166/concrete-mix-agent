"""Educational absolute-volume estimate; not a verified code compliance engine."""
import math

M3_TO_CFT = 35.3146667
WATER_KG = 193.0
AIR_PCT = 2.0
CEMENT_SG, SAND_SG, AGG_SG = 3.15, 2.62, 2.68
DRY_RODDED_KG_M3 = 1600.0
COARSE_VOL_FACTOR = 0.62
# Inherited demo presets, NOT ACI 318 exposure classifications or requirements.
EXPOSURE_RULES = {
    "mild": {"min_psi": 2500, "max_wc": .60},
    "moderate": {"min_psi": 3000, "max_wc": .50},
    "severe": {"min_psi": 3500, "max_wc": .45},
    "coastal": {"min_psi": 4000, "max_wc": .40},
}
STRENGTH_WC = [(2000, .70), (2500, .62), (3000, .55), (4000, .45), (5000, .38)]


def number(value, name, minimum=0, maximum=None):
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a number.")
    try:
        v = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a number.") from None
    if not math.isfinite(v) or v < minimum or (maximum is not None and v > maximum):
        raise ValueError(f"{name} must be finite and between {minimum} and {maximum or 'the supported maximum'}.")
    return v


def _wc_for_strength(psi):
    psi = number(psi, "Strength", 2000, 5000)
    for (lo, a), (hi, b) in zip(STRENGTH_WC, STRENGTH_WC[1:]):
        if lo <= psi <= hi:
            return a + (b-a) * (psi-lo) / (hi-lo)
    return STRENGTH_WC[-1][1]


def calculate_mix_design(target_strength_psi, exposure):
    psi = number(target_strength_psi, "Strength", 2000, 5000)
    if exposure not in EXPOSURE_RULES:
        raise ValueError("Select a supported demo exposure preset.")
    rule = EXPOSURE_RULES[exposure]
    final = max(psi, rule['min_psi'])
    wc = min(_wc_for_strength(final), rule['max_wc'])
    cement = WATER_KG / wc
    coarse = COARSE_VOL_FACTOR * DRY_RODDED_KG_M3
    sand = (1 - cement/(CEMENT_SG*1000) - WATER_KG/1000 - AIR_PCT/100
            - coarse/(AGG_SG*1000)) * SAND_SG * 1000
    warnings = ["Demo material properties and exposure presets are unverified assumptions, not code requirements.",
                "Lab trials, aggregate moisture/absorption corrections and engineering review are required."]
    if final != psi:
        warnings.append(f"Demo preset raised the calculation basis from {psi:g} to {final:g} psi; this does not prove achieved strength.")
    return dict(requested_psi=psi, final_psi=final, exposure=exposure, wc_ratio=wc,
                cement_kg_m3=cement, sand_kg_m3=sand, coarse_agg_kg_m3=coarse,
                water_kg_m3=WATER_KG, warnings=warnings,
                basis="Educational absolute-volume estimate with fixed material assumptions")
