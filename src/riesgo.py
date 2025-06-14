def evaluar_riesgo(historial: list[dict]) -> str:
    """
    Evalúa el riesgo crediticio de un usuario basándose en su historial reciente.

    Parámetros:
    - historial: lista de diccionarios con claves: monto, score_datacredito, pagos_atrasados

    Retorna:
    - Una cadena indicando el nivel de riesgo.
    """
    if len(historial) < 3:
        return "❌ Historial insuficiente para evaluar el riesgo"

    recientes = historial[-3:]  # Últimos 3 meses

    score_bajo = any(h["score_datacredito"] < 600 for h in recientes)
    atrasos_frecuentes = sum(h["pagos_atrasados"] for h in recientes) > 1
    inactividad = all(h["monto"] == 0 for h in recientes)

    # Ver si la tendencia del monto va en caída
    tendencia_negativa = False
    montos = [h["monto"] for h in recientes if h["monto"] > 0]
    if len(montos) >= 2 and montos[-1] < montos[0]:
        tendencia_negativa = True

    if score_bajo or atrasos_frecuentes or inactividad or tendencia_negativa:
        return "⚠️ Riesgo alto"
    else:
        return "✅ Riesgo bajo"
