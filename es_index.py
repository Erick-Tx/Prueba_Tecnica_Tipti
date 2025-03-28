from elasticsearch import Elasticsearch

# Conectando a Elasticsearch
es = Elasticsearch("http://localhost:9200")
index_name = "productos_amazon"

mapping = {
    "mappings": {
        "properties": {
            "name": {"type": "text"},
            "main_category": {"type": "keyword"},
            "sub_category": {"type": "keyword"},
            "image": {"type": "keyword"},
            "link": {"type": "keyword"},
            "ratings": {"type": "float"},
            "no_of_ratings": {"type": "integer"},
            "discount_price": {"type": "float"},
            "actual_price": {"type": "float"},
            "embedding": {"type": "dense_vector", "dims": 768} #768 dimensiones
        }
    }
}

# Si el índice ya existe, se recomienda eliminarlo (para pruebas) y volver a crearlo.
if es.indices.exists(index=index_name):
    print(f"El índice {index_name} ya existe, eliminándolo para recrearlo.")
    es.indices.delete(index=index_name)

# Creando el índice usando el mapping (usando el parámetro 'mappings' para evitar warnings)
es.indices.create(index=index_name, mappings=mapping["mappings"])
print(f"Índice {index_name} creado correctamente.")
