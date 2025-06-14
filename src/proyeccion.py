import torch
import pandas as pd
from calendar import month_name
from datetime import datetime

def predecir_cupo_futuro(model, x_scaler, y_scaler, historial):
    columnas = ["prestó", "monto", "score_datacredito", "pagos_atrasados", "plazo", "aliados_bancarios"]

    # Rellenar con ceros al principio si hay menos de 12 meses
    while len(historial) < 12:
        historial.insert(0, {
            "prestó": 0,
            "monto": 0.0,
            "score_datacredito": 0.0,
            "pagos_atrasados": 0,
            "plazo": 6,
            "aliados_bancarios": 0
        })

    # Solo conservar las últimas 12 entradas
    historial = historial[-12:]

    df = pd.DataFrame(historial)
    entrada = df[columnas].values.flatten().reshape(1, -1)

    entrada_scaled = x_scaler.transform(entrada)
    X_tensor = torch.tensor(entrada_scaled, dtype=torch.float32)

    with torch.no_grad():
        pred_scaled = model(X_tensor).item()
        pred_real = y_scaler.inverse_transform([[pred_scaled]])[0][0]

    return round(pred_real, 2)

def proyectar_cupo_mensual(model, x_scaler, y_scaler, historial_inicial, meses_futuros=6):
    historial = historial_inicial.copy()
    proyecciones = []
    mes_actual = datetime.now().month

    for i in range(meses_futuros):
        cupo = predecir_cupo_futuro(model, x_scaler, y_scaler, historial)
        mes_nombre = month_name[(mes_actual + i - 1) % 12 + 1]
        proyecciones.append({"mes": mes_nombre, "cupo_estimado": cupo})

        nuevo_mes = historial[-1].copy()
        nuevo_mes["monto"] = cupo
        historial = historial[1:] + [nuevo_mes]

    return proyecciones
