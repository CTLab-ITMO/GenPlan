import math
from typing import Dict, List

from dto.rect import Rect


def calculate_endurance_wall(
        height: float,
        walls: List[Rect],
        beam_radius: float,
) -> Dict[str, bool]:
    final_m = None
    for w in walls:
        m = calculate_endurance(
            height=height,
            width=w.max_size,
            thickness=w.min_size,
            beam_radius=beam_radius
        )
        print(m)
        if final_m is None:
            final_m = m
        else:
            for key in final_m:
                final_m[key] = final_m[key] and m[key]
    return final_m


"""
    Args:
        height (float): Height of wall, m.
        width (float): Width of wall, m.
        thickness (float): Thickness of wall, m.
        beam_square (float): Radius of beam, m.
"""


def calculate_endurance(
        height: float,
        width: float,
        thickness: float,
        beam_radius: float,
) -> Dict[str, bool]:
    concrete_resistance = 11.5  # расчётное сопротивление бетона, МПа
    beam_resistance = 365  # расчётное сопротивление арматуры, МПа
    concrete_stretch = 0.91  # сопротивление бетона на растяжение, МПа
    phi = 0.9  # коэффициент устойчивости
    p = 2500  # плотность бетонв кг/м³
    q = 1.5  # ветровая нагрузка (зависит от региона)
    g = 9.8  # ускорение свободного падения м/с²

    beam_square = math.pi * beam_radius ** 2
    wall_weight = p * height * width * thickness * g
    wall_square = width * thickness
    thickness_real = thickness - beam_radius

    transverse_force = p * q * height  # Ветровая нагрузка/Поперечная сила, кН
    bending_moment = transverse_force * height / 2  # Изгибающий момент, кН·м
    inertia_radius = thickness / (12 ** 0.5)  # Радиус инерции, м

    # Endurance
    wall_endurance = wall_weight / wall_square
    wall_endurance_max = concrete_resistance * phi

    # Bend
    wall_moment = (width * height ** 2) / 6  # Момент сопротивления бетона
    beam_moment = (beam_square * height) / 6  # Момент сопротивления арматуры
    construction_moment = concrete_resistance * wall_moment + beam_resistance * beam_moment
    construction_moment_min = bending_moment

    # Shift
    shift = concrete_stretch * width * thickness_real * 1e3
    shift_min = transverse_force

    # Flexibility
    wall_flexibility = height / inertia_radius
    wall_flexibility_max = 25

    return {
        "Endurance": wall_endurance <= wall_endurance_max,
        "Bend": construction_moment_min <= construction_moment,
        "Shift": shift_min <= shift,
        "Flexibility": wall_flexibility <= wall_flexibility_max,
    }
