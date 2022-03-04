import data
from models import Barbeiro, Hora_Marcada


print(" criando database")

data.Base.metadata.create_all(data.engine)