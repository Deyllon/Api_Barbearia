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
    barbeiro_a_atualizar = db.query(Barbeiro).filter(Barbeiro.nome == barbeiro_nome).first()
    if barbeiro_a_atualizar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Barbeiro não encontrado')
    barbeiro_a_atualizar.horario_de_entrada = barbeiro.horario_de_entrada
    barbeiro_a_atualizar.horario_de_saida = barbeiro.horario_de_saida
    barbeiro_a_atualizar.ativo = barbeiro.ativo
    db.commit()
    return barbeiro_a_atualizar

@app.delete('/deleta_barbeiro/{barbeiro_nome}', response_model=Barbeiros, status_code=status.HTTP_200_OK)
def deleta_barbeiro(barbeiro_nome: str):
    barbeiro_a_deletar = db.query(Barbeiro).filter(Barbeiro.nome == barbeiro_nome).first()
    if barbeiro_a_deletar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Barbeiro não encontrado")
    db.delete(barbeiro_a_deletar)
    db.commit()
    return barbeiro_a_deletar


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

@app.get('/hora_marcada', response_model=List[Horario_Marcado], status_code=status.HTTP_200_OK)
def ver_horas_marcadas():
    horarios = db.query(Hora_Marcada).order_by(Hora_Marcada.horario.desc()).all()
    return horarios

@app.get('/hora_marcada/{cliente_nome}', response_model=List[Horario_Marcado], status_code=status.HTTP_200_OK)
def ver_hora_marcada_do_cliente(cliente_nome: str):
    horario_do_cliente = db.query(Hora_Marcada).order_by(Hora_Marcada.horario.desc()).filter(Hora_Marcada.cliente == cliente_nome).all()
    if not horario_do_cliente:
        raise HTTPException(status_code=400, detail='O cliente não tem nenhum horario marcado') 
    return horario_do_cliente


@app.get('/hora_marcada_barbeiro/{barbeiro_nome}', response_model=List[Horario_Marcado], status_code=status.HTTP_200_OK)
def ver_hora_marcado_do_barbeiro(barbeiro_nome: str):
    barbeiro = db.query(Barbeiro).filter(Barbeiro.nome == barbeiro_nome).first()
    horario_do_barbeiro = db.query(Hora_Marcada).order_by(Hora_Marcada.horario.desc()).filter(Hora_Marcada.barbeiro == barbeiro.id).all()
    if not horario_do_barbeiro:
        raise HTTPException(status_code=400, detail='O barbeiro não tem nenhum horario')
    return horario_do_barbeiro

@app.put('/atualiza_horario/{cliente_nome}', response_model=Horario_Marcado, status_code=status.HTTP_200_OK)
def atualizar_horario(cliente_nome: str,horario_marcado:Horario_Marcado):
    horario_a_atualizar = db.query(Hora_Marcada).order_by(Hora_Marcada.horario.desc()).filter(Hora_Marcada.cliente == cliente_nome).first()
    print(horario_a_atualizar)
    horario_a_atualizar.horario = horario_marcado.horario.strftime('%Y-%m-%d %H:%M')
    horario_a_atualizar.barbeiro = horario_marcado.barbeiro
    db.commit()
    return horario_a_atualizar

@app.delete('/deletar_horario/{cliente_nome}/{horario}', response_model=Horario_Marcado, status_code=status.HTTP_200_OK)
def deletar_horario(cliente_nome: str, horario: str):
    horario_a_deletar = db.query(Hora_Marcada).filter(Hora_Marcada.cliente == cliente_nome, Hora_Marcada.horario == horario ).first()
    db.delete(horario_a_deletar)
    db.commit()
    return horario_a_deletar