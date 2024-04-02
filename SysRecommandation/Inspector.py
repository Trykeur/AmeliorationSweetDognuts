import pandas as pd
import sqlalchemy as sql
import matplotlib.pyplot as plt

# TODO : utiliser le fichier de connexion
username='postgres'
password='admin'
host='localhost'
database= 'Sae'
schema = ""

# Connexion
engine = sql.create_engine(f'postgresql://{username}:{password}@{host}/{database}')

inspector = sql.inspect(engine)
schemas = inspector.get_schema_names()

for schema in schemas:
    print("schema: %s" % schema)
    for table_name in inspector.get_table_names(schema=schema):
        print("\ttable_name: %s" % table_name)



