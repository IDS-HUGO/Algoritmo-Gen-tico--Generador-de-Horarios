def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    total = sum(max(value, 0.0) for value in weights.values())
    if total <= 0:
        return {key: 0.25 for key in weights}
    return {key: max(value, 0.0) / total for key, value in weights.items()}


def blend_profile_weights(base_weights: dict[str, float], profile_weights: dict[str, float]) -> dict[str, float]:
    return {
        "cobertura": base_weights["cobertura"] * profile_weights["cobertura"],
        "horas_extra": base_weights["horas_extra"] * profile_weights["horas_extra"],
        "insatisfaccion": base_weights["insatisfaccion"] * profile_weights["insatisfaccion"],
        "legal": base_weights["legal"] * profile_weights["legal"],
    }


def default_profiles() -> dict[str, dict[str, float]]:
    return {
        "A": {"cobertura": 0.45, "horas_extra": 0.30, "insatisfaccion": 0.15, "legal": 0.10},
        "B": {"cobertura": 0.20, "horas_extra": 0.15, "insatisfaccion": 0.50, "legal": 0.15},
        "C": {"cobertura": 0.20, "horas_extra": 0.10, "insatisfaccion": 0.10, "legal": 0.60},
    }
