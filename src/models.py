from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    correo = Column(String(150), unique=True)

class HistorialPrestamo(Base):
    __tablename__ = "historial_prestamos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"))
    mes = Column(Integer)
    monto = Column(Float)
    cantidad_prestamos = Column(Integer)
    pagos_atrasados = Column(Integer)
    score_datacredito = Column(Float)
