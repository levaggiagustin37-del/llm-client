import math


def intervalo_wilson(exitos, total, z=1.96):
    if total == 0:
        return (0.0, 0.0)
    p = exitos / total
    denominador = 1 + z**2 / total
    centro = (p + z**2 / (2 * total)) / denominador
    margen = z * math.sqrt(p * (1 - p) / total + z**2 / (4 * total**2)) / denominador
    return (max(0.0, centro - margen), min(1.0, centro + margen))