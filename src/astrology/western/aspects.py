"""Planetary aspect calculations."""

from __future__ import annotations

from dataclasses import dataclass

# Major aspects with standard orbs
ASPECTS = {
    "Conjunction": (0, "☌"),
    "Sextile": (60, "⚹"),
    "Square": (90, "□"),
    "Trine": (120, "△"),
    "Opposition": (180, "☍"),
}

# Default orbs per planet (wider for luminaries)
PLANET_ORBS = {
    "Sun": 15.0,
    "Moon": 12.0,
    "Mercury": 7.0,
    "Venus": 7.0,
    "Mars": 8.0,
    "Jupiter": 9.0,
    "Saturn": 9.0,
    "Uranus": 5.0,
    "Neptune": 5.0,
    "Pluto": 5.0,
    "North Node": 3.0,
    "Chiron": 5.0,
}


@dataclass
class AspectData:
    planet_a: str
    planet_b: str
    aspect_name: str
    aspect_angle: int
    orb: float  # actual orb in degrees
    applying: bool  # True if applying, False if separating
    symbol: str


def calculate_aspects(
    planets: dict[str, float],
    speeds: dict[str, float] | None = None,
) -> list[AspectData]:
    """
    Calculate all aspects between planets.

    Args:
        planets: dict of planet_name -> longitude
        speeds: optional dict of planet_name -> speed (degrees/day) for applying/separating

    Returns:
        List of AspectData sorted by tightness of orb.
    """
    results = []
    planet_names = list(planets.keys())

    for i, pa in enumerate(planet_names):
        for pb in planet_names[i + 1:]:
            lon_a = planets[pa]
            lon_b = planets[pb]

            diff = abs(lon_a - lon_b)
            if diff > 180:
                diff = 360 - diff

            # Check each aspect type
            for asp_name, (angle, symbol) in ASPECTS.items():
                # Use the average of both planets' orbs
                orb_a = PLANET_ORBS.get(pa, 7.0)
                orb_b = PLANET_ORBS.get(pb, 7.0)
                max_orb = (orb_a + orb_b) / 2.0

                actual_orb = abs(diff - angle)
                if actual_orb <= max_orb:
                    # Determine applying/separating
                    applying = False
                    if speeds:
                        spd_a = speeds.get(pa, 0.0)
                        spd_b = speeds.get(pb, 0.0)
                        # Relative speed — if closing, applying
                        relative = spd_a - spd_b
                        signed_diff = lon_a - lon_b
                        if signed_diff > 180:
                            signed_diff -= 360
                        elif signed_diff < -180:
                            signed_diff += 360
                        # Applying if the aspect is getting tighter
                        if angle == 0:
                            applying = (signed_diff > 0 and relative < 0) or (signed_diff < 0 and relative > 0)
                        else:
                            applying = abs(diff) > angle and relative != 0
                            # More precise: applying if orb is decreasing
                            applying = (diff > angle and (
                                (signed_diff > 0 and relative < 0) or
                                (signed_diff < 0 and relative > 0)
                            )) or (diff < angle and (
                                (signed_diff > 0 and relative > 0) or
                                (signed_diff < 0 and relative < 0)
                            ))

                    results.append(AspectData(
                        planet_a=pa,
                        planet_b=pb,
                        aspect_name=asp_name,
                        aspect_angle=angle,
                        orb=actual_orb,
                        applying=applying,
                        symbol=symbol,
                    ))

    results.sort(key=lambda a: a.orb)
    return results


# Traditional planets for VOC check
_TRADITIONAL = {"Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"}
_MAJOR_ANGLES = [0, 60, 90, 120, 180]


def is_moon_void_of_course(
    planets: dict[str, float],
    speeds: dict[str, float],
) -> tuple[bool, float]:
    """
    Check if the Moon is void of course (no applying major aspects
    to traditional planets before leaving its current sign).

    Returns:
        (is_voc, degrees_remaining_in_sign)
    """
    moon_lon = planets.get("Moon")
    moon_speed = speeds.get("Moon")
    if moon_lon is None or moon_speed is None:
        return False, 0.0

    sign_end = ((moon_lon // 30) + 1) * 30
    degrees_remaining = sign_end - moon_lon

    if moon_speed <= 0:
        # Lunar retrograde is extremely rare; skip VOC check
        return False, degrees_remaining

    time_to_leave = degrees_remaining / moon_speed  # days

    for name, lon in planets.items():
        if name == "Moon" or name not in _TRADITIONAL:
            continue

        planet_speed = speeds.get(name, 0.0)
        relative_speed = moon_speed - planet_speed
        if abs(relative_speed) < 1e-10:
            continue

        # Current angular separation (Moon - planet), normalized to [0, 360)
        current_sep = (moon_lon - lon) % 360

        for angle in _MAJOR_ANGLES:
            # Aspect is exact when separation = angle or 360-angle
            targets = [angle]
            if 0 < angle < 180:
                targets.append(360 - angle)

            for target in targets:
                diff = target - current_sep
                # Find smallest positive t where current_sep + relative_speed * t ≡ target (mod 360)
                best_t = None
                for k in range(-2, 3):
                    t = (diff + 360 * k) / relative_speed
                    if t > 1e-10 and (best_t is None or t < best_t):
                        best_t = t

                if best_t is not None and best_t < time_to_leave:
                    return False, degrees_remaining

    return True, degrees_remaining
