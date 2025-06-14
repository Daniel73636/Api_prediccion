from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import SessionLocal
from src.crud import obtener_historial_usuario, obtener_usuarios
from src.loader import cargar_modelo_y_scalers
from src.riesgo import evaluar_riesgo
from src.proyeccion import proyectar_cupo_mensual
from src.models import Usuario
from sqlalchemy.future import select

app = FastAPI(title="API de Predicción de Cupo Mensual")

# Cargar modelo y escaladores
modelo, scaler_x, scaler_y = cargar_modelo_y_scalers(
    "artifacts/modelo_proyeccion_cupo.pth",
    "artifacts/scaler_proyeccion.pkl",
    "artifacts/y_scaler_proyeccion.pkl"
)

# Dependencia DB
async def get_db():
    async with SessionLocal() as session:
        yield session

# Request body
class ProyeccionRequest(BaseModel):
    user_id: int
    meses_futuros: int = 6

@app.post(
    "/proyectar_cupo",
    summary="Proyectar cupo mensual",
    description="Devuelve la proyección del cupo estimado en los próximos meses para un usuario."
)
async def proyectar_cupo(req: ProyeccionRequest, db: AsyncSession = Depends(get_db)):
    historial = await obtener_historial_usuario(db, req.user_id)

    if len(historial) < 3:
        return {"detalle": "❌ El usuario no tiene suficiente historial (mínimo 3 meses)"}

    # Convertimos y ordenamos el historial
    historial_dicts = sorted([
        {
            "mes": h.mes,
            "prestó": int(h.cantidad_prestamos > 0),
            "monto": h.monto,
            "score_datacredito": h.score_datacredito,
            "pagos_atrasados": h.pagos_atrasados,
            "plazo": 6,
            "aliados_bancarios": 1
        }
        for h in historial
    ], key=lambda x: x["mes"])

    # Tomamos los últimos 12 meses
    entrada = historial_dicts[-12:]

    # Si hay menos de 12, rellenamos al inicio con ceros
    while len(entrada) < 12:
        entrada.insert(0, {
            "mes": 0,
            "prestó": 0,
            "monto": 0.0,
            "score_datacredito": 0.0,
            "pagos_atrasados": 0,
            "plazo": 6,
            "aliados_bancarios": 0
        })

    # Eliminamos 'mes' antes de pasarlo al modelo
    entrada_limpia = [{k: v for k, v in mes.items() if k != "mes"} for mes in entrada]

    proyeccion = proyectar_cupo_mensual(
        modelo, scaler_x, scaler_y, entrada_limpia, meses_futuros=req.meses_futuros
    )

    return {
        "proyeccion": proyeccion,
        "mensaje": "✅ Si el usuario mantiene su comportamiento actual, su capacidad de préstamo aumentará mes a mes."
    }

@app.get("/usuarios/todos", summary="Listar usuarios", description="Devuelve todos los usuarios registrados en la base de datos.")
async def listar_usuarios(db: AsyncSession = Depends(get_db)):
    usuarios = await obtener_usuarios(db)
    return [
        {"id": u.id, "nombre": u.nombre, "correo": u.correo}
        for u in usuarios
    ]

@app.get("/usuarios", summary="Listar usuarios", description="Devuelve todos los usuarios registrados en la base de datos. Puedes filtrar por usuarios con historial.")
async def listar_usuarios_disponibles(con_historial: bool = False, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Usuario))
    usuarios = result.scalars().all()

    if con_historial:
        usuarios_filtrados = []
        for u in usuarios:
            historial = await obtener_historial_usuario(db, u.id)
            if len(historial) >= 3:
                usuarios_filtrados.append(u)
        usuarios = usuarios_filtrados

    return [
        {"id": u.id, "nombre": u.nombre, "correo": u.correo}
        for u in usuarios
    ]

@app.get(
    "/historial/{user_id}",
    summary="Obtener historial de préstamos",
    description="Devuelve el historial completo de préstamos de un usuario por mes."
)
async def obtener_historial(user_id: int, db: AsyncSession = Depends(get_db)):
    historial = await obtener_historial_usuario(db, user_id)

    if not historial:
        return {"detalle": "No hay registros de préstamo para este usuario."}

    historial_ordenado = sorted(historial, key=lambda h: h.mes)

    return [
        {
            "mes": h.mes,
            "monto": h.monto,
            "cantidad_prestamos": h.cantidad_prestamos,
            "pagos_atrasados": h.pagos_atrasados,
            "score_datacredito": h.score_datacredito
        }
        for h in historial_ordenado
    ]

@app.get("/riesgo/{user_id}", summary="Evaluar riesgo", description="Analiza el comportamiento del usuario y estima su nivel de riesgo.")
async def analizar_riesgo(user_id: int, db: AsyncSession = Depends(get_db)):
    historial = await obtener_historial_usuario(db, user_id)

    if len(historial) < 3:
        return {"detalle": "❌ No hay suficiente historial para evaluar el riesgo."}

    historial_dicts = sorted([
        {
            "mes": h.mes,
            "monto": h.monto,
            "score_datacredito": h.score_datacredito,
            "pagos_atrasados": h.pagos_atrasados
        }
        for h in historial
    ], key=lambda x: x["mes"])

    nivel_riesgo = evaluar_riesgo(historial_dicts)
    return {
        "riesgo": nivel_riesgo,
        "analisis": historial_dicts[-12:]
    }
