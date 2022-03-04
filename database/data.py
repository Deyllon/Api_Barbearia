from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from decouple import config

senha = config('senha')

engine= create_engine(f"postgresql://postgres:{senha}@localhost:5432/barbearia")

Base= declarative_base()
SessionLocal = sessionmaker(bind=engine)