import datetime
from time import strftime
from fastapi import FastAPI, status, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from database.data import SessionLocal
from database.models import Barbeiro, Hora_Marcada, Usuario_Model
from validation import apagar_horarios, horario_existe, valida_horario,valida_barbeiro, valida_hora_marcada, valida_horario_do_cliente,valida_horario_do_barbeiro, validar_barbeiro_a_deletar, valida_criacao_barbeiro, valida_atualizacao_barbeiro, barbeiro_existe, validar_horario_a_deletar
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm



app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

class Usuario(BaseModel):
    id: Optional[int] = None
    usuario : str
    senha : str
    
    def vericar_senha(self, senha):
        return self.senha == senha
    class Config:
        orm_mode = True

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
    
def autenticar_usuario(usuario: str, senha: str):
    db_usuario = db.query(Usuario_Model).filter(Usuario_Model.usuario == usuario).first()
    if not db_usuario:
        return False
    if not db_usuario.vericar_senha(senha):
        return False
    return db_usuario


@app.post('/token')
def gerar_token(formulario: OAuth2PasswordRequestForm = Depends()):
    usuario = autenticar_usuario(formulario.username, formulario.password)
    
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario não encontrado')
    
    token = usuario
    return {"token_de_acesso": token, 'tipo_do_token': 'bearer'}
 
#Metodo HTTP para o modelo Usuario
    
@app.post('/cria_usuario', response_model=Usuario)
def cria_usuario(usuario: Usuario):
    db_usuario = db.query(Usuario_Model).filter(Usuario_Model.usuario == usuario.usuario).first()
    if not db_usuario is None:
        raise HTTPException(status_code=400, detail='Usuario já existe')
    usuario = Usuario_Model(
        usuario = usuario.usuario,
        senha = usuario.senha
    )
    db.add(usuario)
    db.commit()
    return usuario
  
#Metodos HTTP para o modelo Barbeiro
    
@app.post('/cria_barbeiro', response_model=Barbeiros, status_code=status.HTTP_201_CREATED)
def cria_barbeiro(barbeiro:Barbeiros, usuario= Depends(oauth2_scheme)):
    db_barbeiro = db.query(Barbeiro).filter(Barbeiro.nome== barbeiro.nome).first()
    
    valida_criacao_barbeiro(db_barbeiro)
    
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
def barbeiros(usuario= Depends(oauth2_scheme)):
    barbeiros = db.query(Barbeiro).all()
    
    barbeiro_existe(barbeiros)
    
    return barbeiros

@app.get('/barbeiro/{barbeiro_nome}', response_model=Barbeiros, status_code=status.HTTP_200_OK)
def barbeiro(barbeiro_nome: str, usuario= Depends(oauth2_scheme)):
    barbeiro = db.query(Barbeiro).filter(Barbeiro.nome ==  barbeiro_nome).first()
    
    valida_barbeiro(barbeiro)
    
    return barbeiro

@app.put('/atualiza_barbeiro/{barbeiro_nome}', response_model=Barbeiros, status_code=status.HTTP_200_OK)
def atualizar_barbeiro(barbeiro_nome: str, barbeiro:Barbeiros, usuario= Depends(oauth2_scheme)):
    barbeiro_a_atualizar = db.query(Barbeiro).filter(Barbeiro.nome == barbeiro_nome).first()
    
    valida_atualizacao_barbeiro(barbeiro_a_atualizar)
    
    barbeiro_a_atualizar.horario_de_entrada = barbeiro.horario_de_entrada
    barbeiro_a_atualizar.horario_de_saida = barbeiro.horario_de_saida
    barbeiro_a_atualizar.ativo = barbeiro.ativo
    
    db.commit()
    
    return barbeiro_a_atualizar

@app.delete('/deleta_barbeiro/{barbeiro_nome}', response_model=Barbeiros, status_code=status.HTTP_200_OK)
def deleta_barbeiro(barbeiro_nome: str, usuario= Depends(oauth2_scheme)):
    barbeiro_a_deletar = db.query(Barbeiro).filter(Barbeiro.nome == barbeiro_nome).first()
    
    validar_barbeiro_a_deletar(barbeiro_a_deletar)
    
    horario_do_barbeiro = db.query(Hora_Marcada).filter(Hora_Marcada.barbeiro == barbeiro_a_deletar.id).all()
    
    apagar_horarios(horario_do_barbeiro)
    
    db.delete(barbeiro_a_deletar)
    db.commit()
    
    return barbeiro_a_deletar

#Metodos HTTP para o model Hora_Marcada

@app.post('/cria_hora_marcada', response_model=Horario_Marcado, status_code=status.HTTP_201_CREATED)
def cria_horario(hora_marcada:Horario_Marcado, usuario= Depends(oauth2_scheme)):
    hora_marcada = Hora_Marcada(
        cliente = hora_marcada.cliente,
        horario = hora_marcada.horario.strftime('%Y-%m-%d %H:%M'),
        barbeiro = hora_marcada.barbeiro
    
    )
    barbeiro_id = hora_marcada.barbeiro
    barbeiro = db.query(Barbeiro).filter(Barbeiro.id == barbeiro_id).first()
    
    valida_barbeiro(barbeiro)
    valida_horario(barbeiro, hora_marcada)
    
    db_hora_marcada = db.query(Hora_Marcada).filter(Hora_Marcada.barbeiro == hora_marcada.barbeiro, Hora_Marcada.horario == (datetime.datetime.strptime(str(hora_marcada.horario),'%Y-%m-%d %H:%M'))).first()
    
    valida_hora_marcada(db_hora_marcada)
    
    db.add(hora_marcada)
    db.commit()
    
    return hora_marcada

@app.get('/hora_marcada', response_model=List[Horario_Marcado], status_code=status.HTTP_200_OK)
def ver_horas_marcadas(usuario= Depends(oauth2_scheme)):
    horarios = db.query(Hora_Marcada).order_by(Hora_Marcada.horario.desc()).all()
    
    horario_existe(horarios)
    
    return horarios

@app.get('/hora_marcada/{cliente_nome}', response_model=List[Horario_Marcado], status_code=status.HTTP_200_OK)
def ver_hora_marcada_do_cliente(cliente_nome: str, usuario= Depends(oauth2_scheme)):
    horario_do_cliente = db.query(Hora_Marcada).order_by(Hora_Marcada.horario.desc()).filter(Hora_Marcada.cliente == cliente_nome).all()
    
    valida_horario_do_cliente(horario_do_cliente)
    
    return horario_do_cliente


@app.get('/hora_marcada_barbeiro/{barbeiro_nome}', response_model=List[Horario_Marcado], status_code=status.HTTP_200_OK)
def ver_hora_marcado_do_barbeiro(barbeiro_nome: str, usuario= Depends(oauth2_scheme)):
    barbeiro = db.query(Barbeiro).filter(Barbeiro.nome == barbeiro_nome).first()
    
    valida_barbeiro(barbeiro)
    
    horario_do_barbeiro = db.query(Hora_Marcada).order_by(Hora_Marcada.horario.desc()).filter(Hora_Marcada.barbeiro == barbeiro.id).all()
    
    valida_horario_do_barbeiro(horario_do_barbeiro)
    
    return horario_do_barbeiro

@app.put('/atualiza_horario/{cliente_nome}', response_model=Horario_Marcado, status_code=status.HTTP_200_OK)
def atualizar_horario(cliente_nome: str,horario_marcado:Horario_Marcado, usuario= Depends(oauth2_scheme)):
    horario_a_atualizar = db.query(Hora_Marcada).order_by(Hora_Marcada.horario.desc()).filter(Hora_Marcada.cliente == cliente_nome).first()
    
    horario_existe(horario_a_atualizar)
    
    horario_a_atualizar.horario = horario_marcado.horario.strftime('%Y-%m-%d %H:%M')
    horario_a_atualizar.barbeiro = horario_marcado.barbeiro
    
    barbeiro = db.query(Barbeiro).filter(Barbeiro.id == horario_a_atualizar.barbeiro).first()
    
    valida_barbeiro(horario_a_atualizar.barbeiro)
    valida_horario(barbeiro,horario_a_atualizar)
    
    db_horario_barbeiro = db.query(Hora_Marcada).filter(Hora_Marcada.barbeiro == barbeiro.id, Hora_Marcada.horario == (datetime.datetime.strptime(str(horario_a_atualizar.horario),'%Y-%m-%d %H:%M'))).first()
    
    valida_hora_marcada(db_horario_barbeiro)
    
    db.commit()
    
    return horario_a_atualizar

@app.delete('/deletar_horario/{cliente_nome}/{horario}', response_model=Horario_Marcado, status_code=status.HTTP_200_OK)
def deletar_horario(cliente_nome: str, horario: str, usuario= Depends(oauth2_scheme)):
    horario_a_deletar = db.query(Hora_Marcada).filter(Hora_Marcada.cliente == cliente_nome, Hora_Marcada.horario == horario ).first()
    
    validar_horario_a_deletar(horario_a_deletar)
    
    db.delete(horario_a_deletar)
    db.commit()
    
    return horario_a_deletar