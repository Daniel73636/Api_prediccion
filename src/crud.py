from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Usuario, HistorialPrestamo
from sqlalchemy.future import select

async def crear_usuario(session: AsyncSession, nombre: str, correo: str):
    usuario = Usuario(nombre=nombre, correo=correo)
    session.add(usuario)
    await session.commit()
    await session.refresh(usuario)
    return usuario

async def agregar_historial_prestamos(session: AsyncSession, user_id: int, prestamos: list[dict]):
    for p in prestamos:
        prestamo = HistorialPrestamo(user_id=user_id, **p)
        session.add(prestamo)
    await session.commit()


async def obtener_historial_usuario(session, user_id: int, n_meses: int = 3):
    result = await session.execute(
        select(HistorialPrestamo)
        .where(HistorialPrestamo.user_id == user_id)
        .order_by(HistorialPrestamo.mes.desc())
        .limit(n_meses)
    )
    prestamos = result.scalars().all()
    return list(reversed(prestamos))  # para que estén en orden cronológico


async def obtener_usuarios(db: AsyncSession):
    result = await db.execute(select(Usuario))
    return result.scalars().all()
