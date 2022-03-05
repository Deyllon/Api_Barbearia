import datetime
from time import strftime
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
    
    
@app.post('/cria_barbeiro', response_model=Barbeiros, status_code=status.HTTP_201_CREATED)
def cria_barbeiro(barbeiro:Barbeiros):
    db_barbeiro = db.query(Barbeiro).filter(Barbeiro.nome== barbeiro.nome).first()
    if db_barbeiro is not None:
        raise HTTPException(status_code=400, detail="Barbeiro já existe")
    barbeiro = Barbeiro(
        nome=barbeiro.nome,
        horario_de_entrada=barbeiro.horario_de_entrada,
        horario_de_saida=barbeiro.horario_de_saida,
        ativo=barbeiro.ativo
    )
    db.add(barbeiro)
    db.commit()
    return barbeiro

@app.get('/barbeiro', response_model=List[Barbeiros], status_code=status.HTTP_200_OK)
def barbeiros():
    barbeiros = db.query(Barbeiro).all()
    return barbeiros

@app.get('/barbeiro/{barbeiro_nome}', response_model=Barbeiros, status_code=status.HTTP_200_OK)
def barbeiro(barbeiro_nome: str):
    barbeiro = db.query(Barbeiro).filter(Barbeiro.nome ==  barbeiro_nome).first()
    return barbeiro

@app.put('/atualiza_barbeiro/{barbeiro_nome}', response_model=Barbeiros, status_code=status.HTTP_200_OK)
def atualizar_barbeiro(barbeiro_nome: str, barbeiro:Barbeiros):
    pass


@app.post('/cria_hora_marcada', response_model=Horario_Marcado, status_code=status.HTTP_201_CREATED)
def cria_horario(hora_marcada:Horario_Marcado):
    hora_marcada = Hora_Marcada(
        cliente = hora_marcada.cliente,
        horario = hora_marcada.horario.strftime('%Y-%m-%d %H:%M'),
        barbeiro = hora_marcada.barbeiro
    )
    barbeiro_id = hora_marcada.barbeiro
    barbeiro = db.query(Barbeiro).filter(Barbeiro.id == barbeiro_id).first()
    if barbeiro is  None:
        raise HTTPException(status_code=400, detail="O barbeiro não existe")
    horario = hora_marcada.horario[11:18]
    db_horario_entrada = barbeiro.horario_de_entrada
    db_horario_saida = barbeiro.horario_de_saida
    if not str(db_horario_entrada) <= horario <= str(db_horario_saida):
        raise HTTPException(status_code=400, detail="Esse Horario não é valido")
    db_hora_marcada = db.query(Hora_Marcada).filter(Hora_Marcada.barbeiro == hora_marcada.barbeiro, Hora_Marcada.horario == (datetime.datetime.strptime(str(hora_marcada.horario),'%Y-%m-%d %H:%M'))).first()
    if db_hora_marcada is not None:
        raise HTTPException(status_code=400, detail="O Barbeiro Já tem um corte para esse horario")
    db.add(hora_marcada)
    db.commit()
    return hora_marcada
