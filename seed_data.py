import asyncio
from src.database import SessionLocal
from src.crud import crear_usuario, agregar_historial_prestamos

async def poblar():
    async with SessionLocal() as session:
        # Crear usuario
        usuario = await crear_usuario(session, "Daniel Montiel", "daniel@example.com")

        # Agregar historial desde enero hasta mayo
        historial = [
            {"mes": 1, "monto": 200000, "cantidad_prestamos": 3, "pagos_atrasados": 0, "score_datacredito": 670},
            {"mes": 2, "monto": 0, "cantidad_prestamos": 0, "pagos_atrasados": 0, "score_datacredito": 675},
            {"mes": 3, "monto": 700000, "cantidad_prestamos": 3, "pagos_atrasados": 1, "score_datacredito": 665},
            {"mes": 4, "monto": 500000, "cantidad_prestamos": 2, "pagos_atrasados": 0, "score_datacredito": 680},
            {"mes": 5, "monto": 650000, "cantidad_prestamos": 3, "pagos_atrasados": 0, "score_datacredito": 690},
        ]

        await agregar_historial_prestamos(session, usuario.id, historial)

asyncio.run(poblar())
