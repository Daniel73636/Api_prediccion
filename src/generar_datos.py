import pandas as pd
import numpy as np
import os

def generar_historial_sintetico(num_usuarios=100, meses_por_usuario=15, output_path="data/historial_entrenamiento.csv"):
    np.random.seed(42)
    registros = []

    for user_id in range(1, num_usuarios + 1):
        score_base = np.random.randint(600, 750)

        for mes in range(1, meses_por_usuario + 1):
            monto = np.random.choice(
                [0, 50000, 100000, 150000, 200000, 300000, 400000, 500000],
                p=[0.1, 0.15, 0.15, 0.2, 0.2, 0.1, 0.05, 0.05]
            )
            cantidad = np.random.choice([0, 1, 2, 3], p=[0.1, 0.4, 0.3, 0.2]) if monto > 0 else 0
            atrasos = 0 if monto == 0 else np.random.choice([0, 1], p=[0.85, 0.15])
            score = score_base + np.random.randint(-30, 20)
            prestó = 1 if monto > 0 else 0
            plazo = np.random.choice([3, 6, 9, 12])
            aliados = np.random.choice([0, 1], p=[0.3, 0.7])

            registros.append({
                "user_id": user_id,
                "mes": mes,
                "monto": monto,
                "cantidad_prestamos": cantidad,
                "pagos_atrasados": atrasos,
                "score_datacredito": max(550, min(score, 850)),
                "prestó": prestó,
                "plazo": plazo,
                "aliados_bancarios": aliados
            })

    df = pd.DataFrame(registros)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✅ Historial generado: {len(df)} filas → {output_path}")

if __name__ == "__main__":
    generar_historial_sintetico()
