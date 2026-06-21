import pandas as pd 
import openai 
import os 
import json 
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent  # sube desde src/ hasta expense-analyzer/
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"

load_dotenv()

client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key= os.getenv("OPEN_ROUTER_KEY") 
)


def leer_datos(ruta):
    if ruta.suffix == ".csv": # .suffix es un atributo de path que devuelve la extención del archivo
        return pd.read_csv(ruta)
    elif ruta.suffix == ".xlsx":
        return pd.read_excel(ruta)
    else: 
        raise ValueError(f"Formato no soportado{ruta.suffix}")

def clasifica(df):
    movimientos_texto = df[["concepto", "importe"]].to_string()
    respuesta = client.chat.completions.create ( 
    model="openai/gpt-oss-120b:free",
    messages=[
        {"role": "system", "content": "Clasifica segun el concepto si es  alguna de estas clasificaciones ingresos, gasto_fijo, gasto_variable, ocio, inversion, salud, suscripciones. Devuelve solo JSON"},
        {"role": "user", "content": movimientos_texto}
    ]
    )
    
    if not respuesta.choices:
        raise ValueError(f"La API no devolvio respuesta: {respuesta.error}")
    
    texto = respuesta.choices[0].message.content
    return texto 

def limpiar_respuesta(texto, df):
    # limpiar
    texto = texto.replace("```json", "").replace("```", "").strip()
    
    # parsear
    categorias_raw = json.loads(texto)
    
    # extraer lista
    categorias = [item["clasificacion"] for item in categorias_raw]
    
    # rellenar si faltan items
    if len(categorias) < len(df):
        n = len(df) - len(categorias)
        categorias = categorias + ["otros"] * n
    
    return categorias

def analizar(df):
    gastos = df[df["importe"] < 0]
    ingresos = df[df["importe"] > 0]

    resumen_gastos = gastos.groupby("categoria")["importe"].sum()
    resumen_ingresos = ingresos.groupby("categoria")["importe"].sum() 
    balance = resumen_ingresos.sum() + resumen_gastos.sum()

    print(f"Gastos totales por categoría: {resumen_gastos.abs()} \n Ingresos totales por categoría: {resumen_ingresos}") # El .abs() es para que los números negativos salgan en positivo, con tal de que sea mas legible en un informe
    print(f"Balance neto {balance: .2f}€") # El .2f formatea el número en dos decimales.


def resultado(df):
    salida = OUTPUT_DIR/"movimientos_clasificados.xlsx"
    df.to_excel(salida, index=False ) 

if __name__ == "__main__":
    datos = DATA_DIR/"movimientos.csv"
    df = leer_datos(datos)


    clasificacion = clasifica(df)

    print("Respuesta IA:", clasificacion)
    df["categoria"] = limpiar_respuesta(clasificacion, df)

    
    analizar(df)
    resultado(df)
