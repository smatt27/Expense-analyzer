import pandas as pd 
import openai 
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent  # sube desde src/ hasta expense-analyzer/
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"


def leer_datos(ruta):
    if ruta.suffix == ".csv": # .suffix es un atributo de path que devuelve la extención del archivo
        return pd.read_csv(ruta)
    elif ruta.suffix == ".xlsx":
        return pd.read_excel(ruta)
    else: 
        raise ValueError(f"Formato no soportado{ruta.suffix}")

def clasifica(df):
    pass

def resultado(df, ruta):
    pass 

if __name__ == "__main__":
    datos = DATA_DIR/"movimientos.csv"
    df = leer_datos(datos)
    clasifica(df)
    resultado(df, datos)