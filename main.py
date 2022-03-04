import datetime
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from database.data import SessionLocal
from database.models import Barbeiro, Hora_Marcada


app = FastAPI()

class Barbeiros(BaseModel):
    id: Optional[int]= None
    nome: str
    horario_de_entrada: datetime.time
    horario_de_saida: datetime.time
    ativo: bool = True
    
    class Config:
        orm_mode = True
    

class Horario_Marcado(BaseModel):
    id: Optional[int] = None
    barbeiro: int
    cliente: str
    horario: datetime.datetime
    
    class Config:
        orm_mode = True
        
db= SessionLocal()
    
    
@app.post('/barbeiro', response_model=Barbeiros, status_code=status.HTTP_201_CREATED)
def cria_barbeiro(barbeiro:Barbeiros):
    barbeiro = Barbeiro(
        nome=barbeiro.nome,
        horario_de_entrada=barbeiro.horario_de_entrada,
        horario_de_saida=barbeiro.horario_de_saida,
        ativo=barbeiro.ativo
    )
    db.add(barbeiro)
    db.commit()
    return barbeiro

@app.post('/hora_marcada', response_model=Horario_Marcado, status_code=status.HTTP_201_CREATED)
def cria_horario(hora_marcada:Horario_Marcado):
    hora_marcada = Hora_Marcada(
        cliente = hora_marcada.cliente,
        horario = hora_marcada.horario,
        barbeiro = hora_marcada.barbeiro
    )
    db.add(hora_marcada)
    db.commit()
    return hora_marcada