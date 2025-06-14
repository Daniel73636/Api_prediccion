import torch
import joblib
from src.model import ModeloProyeccionCupo

def cargar_modelo_y_scalers(model_path, x_scaler_path, y_scaler_path):
    model = ModeloProyeccionCupo(input_dim=6 * 12)
    model.load_state_dict(torch.load(model_path))
    model.eval()

    x_scaler = joblib.load(x_scaler_path)
    y_scaler = joblib.load(y_scaler_path)

    return model, x_scaler, y_scaler
