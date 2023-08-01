import pandas as pd 
import psycopg2 
import sqlalchemy
from sqlalchemy import create_engine
engine = create_engine("postgresql://postgres:admin@localhost:5432/postgres")

df = pd.read_csv("vgsales.csv", index_col=0)
df = df.dropna()# drop N/A to handle later 
df.to_sql("vgsales", con=engine, if_exists="replace")