import sqlalchemy as sql

username='postgres'
password='Trykeur_450'
host='localhost'
database= 'SAE'
port = "5433"
schema = ""

engine = sql.create_engine(f'postgresql://{username}:{password}@{host}:{port}/{database}')

with engine.connect() as connection :
    print("bravo")