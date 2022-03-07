import data
from models import Barbeiro, Hora_Marcada


data.Base.metadata.create_all(data.engine)