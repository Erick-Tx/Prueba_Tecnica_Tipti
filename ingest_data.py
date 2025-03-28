import pandas as pd
from elasticsearch import Elasticsearch, helpers

# Conectando a Elasticsearch
es = Elasticsearch("http://localhost:9200")
index_name = "productos_amazon"

# Ruta del archivo CSV
csv_file = "data/All_Electronics.csv"

# Leyendo el CSV
df = pd.read_csv(csv_file)

def clean_price(value):
    """
    Limpiando el valor de precio, removiendo símbolos de moneda y comas.
    Retornando un float.
    """
    if pd.isna(value):
        return 0.0
    cleaned = str(value).replace('₹', '').replace(',', '').strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def clean_int(value):
    """
    Limpiando el valor removiendo comas y lo convierte a entero.
    """
    if pd.isna(value):
        return 0
    cleaned = str(value).replace(',', '').strip()
    try:
        return int(cleaned)
    except ValueError:
        return 0

def clean_float(value):
    """
    Limpiando el valor y lo convierte a float.
    Si el valor no es convertible, retorna 0.0.
    """
    if pd.isna(value):
        return 0.0
    try:
        return float(value)
    except ValueError:
        return 0.0

def generate_docs(dataframe):
    for idx, row in dataframe.iterrows():
        doc = {
            "_index": index_name,
            "_id": idx,
            "_source": {
                "name": row["name"],
                "main_category": row["main_category"],
                "sub_category": row["sub_category"],
                "image": row["image"],
                "link": row["link"],
                "ratings": clean_float(row["ratings"]),
                "no_of_ratings": clean_int(row["no_of_ratings"]),
                "discount_price": clean_price(row["discount_price"]),
                "actual_price": clean_price(row["actual_price"]),
                # Como valor inicial se le asigna un vector de ceros (768 dimensiones)
                "embedding": [0.0] * 768
            }
        }
        yield doc

helpers.bulk(es, generate_docs(df))
print("Ingesta de datos completada.")
