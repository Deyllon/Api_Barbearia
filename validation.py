from fastapi import HTTPException, status

from database.data import SessionLocal



def valida_barbeiro(barbeiro):
    if barbeiro is  None:
        raise HTTPException(status_code=400, detail="O barbeiro não existe")

def valida_horario(barbeiro, hora_marcada):
    horario = hora_marcada.horario[11:18]
    db_horario_entrada = barbeiro.horario_de_entrada
    db_horario_saida = barbeiro.horario_de_saida
    if not str(db_horario_entrada) <= horario <= str(db_horario_saida):
        raise HTTPException(status_code=400, detail="Esse Horario não é valido")
    
def valida_hora_marcada(db_hora_marcada):
    if db_hora_marcada is not None:
        raise HTTPException(status_code=400, detail="O Barbeiro Já tem um corte para esse horario")
    
def valida_horario_do_cliente(horario_do_cliente):
    if not horario_do_cliente:
        raise HTTPException(status_code=400, detail='O cliente não tem nenhum horario marcado') 

def valida_horario_do_barbeiro(horario_do_barbeiro):
    if not horario_do_barbeiro:
        raise HTTPException(status_code=400, detail='O barbeiro não tem nenhum horario')
    
def validar_barbeiro_a_deletar(barbeiro_a_deletar):
    if barbeiro_a_deletar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Barbeiro não encontrado")
    
def valida_criacao_barbeiro(db_barbeiro):
    if db_barbeiro is not None:
        raise HTTPException(status_code=400, detail="Barbeiro já existe")
    
def valida_atualizacao_barbeiro(barbeiro_a_atualizar):
    if barbeiro_a_atualizar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Barbeiro não encontrado')

def barbeiro_existe(barbeiros):
    if not barbeiros:
        raise HTTPException(status_code=400, detail='Nenhum Barbeiro encontrado')

def horario_existe(horarios):
    if not horarios:
        raise HTTPException(status_code=400, detail='Nenhum horario encontrado')

def validar_horario_a_deletar(horario_a_deletar):
    if horario_a_deletar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Horario não encontrado')

def apagar_horarios(horario_do_barbeiro):
    db= SessionLocal()
    for horario in horario_do_barbeiro:
        db.delete(horario)
        db.commit()
        
def usuario_existe(db_usuario):
    return db_usuario
           
def verificar_senha(db_usuario, senha):
    return db_usuario.vericar_senha(senha)
           
def encontra_usuario(usuario):
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario não encontrado')
    
def encontrou_usuario(db_usuario):
    if not db_usuario is None:
        raise HTTPException(status_code=400, detail='Usuario já existe')