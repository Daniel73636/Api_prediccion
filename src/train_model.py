import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from model import ModeloProyeccionCupo
import joblib
import os


def entrenar_modelo(historial_csv="data/historial_entrenamiento.csv", epochs=50):
    df = pd.read_csv(historial_csv)
    df.sort_values(["user_id", "mes"], inplace=True)

    # Variables para predicción
    features = ["prestó", "monto", "score_datacredito", "pagos_atrasados", "plazo", "aliados_bancarios"]

    secuencias = []
    targets = []

    ventana = 12
    for user_id, group in df.groupby("user_id"):
        group = group.reset_index(drop=True)
        for i in range(len(group) - ventana - 1):
            entrada = group.loc[i:i+ventana-1, features].values.flatten()
            salida = group.loc[i+ventana, "monto"]
            secuencias.append(entrada)
            targets.append(salida)

    # ✅ Verificación importante
    if len(secuencias) == 0:
        raise ValueError(
            "❌ No se generaron secuencias para entrenar. "
            "Asegúrate de que los usuarios tengan al menos 13 meses de historial."
        )

    # Escalar X e y
    X = np.array(secuencias)
    y = np.array(targets).reshape(-1, 1)

    x_scaler = StandardScaler()
    y_scaler = StandardScaler()
    X_scaled = x_scaler.fit_transform(X)
    y_scaled = y_scaler.fit_transform(y)

    X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
    y_tensor = torch.tensor(y_scaled, dtype=torch.float32)

    dataset = TensorDataset(X_tensor, y_tensor)
    train_ds, val_ds = train_test_split(dataset, test_size=0.2)

    model = ModeloProyeccionCupo(input_dim=X.shape[1])
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.MSELoss()

    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=32)

    print("📊 Entrenando modelo...")
    for epoch in range(epochs):
        model.train()
        train_loss = 0
        for Xb, yb in train_loader:
            pred = model(Xb)
            loss = loss_fn(pred, yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        model.eval()
        val_loss = sum(loss_fn(model(Xv), yv).item() for Xv, yv in val_loader)
        print(f"Epoch {epoch+1:02d} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")

    os.makedirs("artifacts", exist_ok=True)
    torch.save(model.state_dict(), "artifacts/modelo_proyeccion_cupo.pth")
    joblib.dump(x_scaler, "artifacts/scaler_proyeccion.pkl")
    joblib.dump(y_scaler, "artifacts/y_scaler_proyeccion.pkl")

    print("✅ Modelo y escaladores guardados en carpeta 'artifacts/'")

if __name__ == "__main__":
    entrenar_modelo()
