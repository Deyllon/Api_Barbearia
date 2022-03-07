from tkinter import CASCADE
from .data import Base
from sqlalchemy import ForeignKey, Integer, String, Boolean, Column, DateTime, Time 



class Barbeiro(Base):
    __tablename__ = 'barbeiro'
    id= Column(Integer,primary_key=True )
    nome = Column(String(255),nullable=False)
    horario_de_entrada = Column(Time, nullable=False)
    horario_de_saida = Column(Time, nullable=False)
    ativo = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"Barbeiro:{self.nome}"
    
    
class Hora_Marcada(Base):
    __tablename__ = 'hora_marcada'
    id= Column(Integer, primary_key=True)
    cliente = Column(String(255), nullable=False)
    horario = Column(DateTime)
    barbeiro = Column(ForeignKey('barbeiro.id'), autoincrement=False)
    
    def __repr__(self):
        return f"Cliente:{self.cliente}, barbeiro:{self.barbeiro}, horario:{self.horario}"