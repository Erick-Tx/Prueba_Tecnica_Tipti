import pandas as pd
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

# Conectando a Elasticsearch
es = Elasticsearch("http://localhost:9200")
index_name = "productos_amazon"

# Ruta del archivo CSV
csv_file = "data/All_Electronics.csv"

# Leyendo el archivo CSV
df = pd.read_csv(csv_file)

# Cargando el modelo "all-mpnet-base-v2" para generar embeddings de 768 dimensiones
model = SentenceTransformer('all-mpnet-base-v2')

def update_embedding_for_document(doc_id, product_name):
    """
    Calculando el embedding del nombre del producto y actualizando el documento en Elasticsearch.
    Se utiliza el parámetro 'doc' directamente para evitar el warning del parámetro 'body'.
    """
    embedding = model.encode(product_name).tolist()
    es.update(
        index=index_name,
        id=doc_id,
        doc={"embedding": embedding},
        doc_as_upsert=True
    )

# Depuración: Contador de documentos procesados
total = 0
for idx, row in df.iterrows():
    update_embedding_for_document(idx, row["name"])
    total += 1
    if total % 100 == 0:
        print(f"Actualizados {total} documentos.")

print(f"Actualización de embeddings completada. Total documentos procesados: {total}")
