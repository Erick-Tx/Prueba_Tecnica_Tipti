from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import json

app = Flask(__name__)

# Conectando a Elasticsearch
es = Elasticsearch("http://localhost:9200")
index_name = "productos_amazon"

# Cargar la plantilla Mustache para búsquedas desde el archivo JSON
with open("templates/search_template.json", "r") as f:
    search_template = json.load(f)

# Cargando el mismo modelo para generar embeddings en el endpoint /similar_products
model = SentenceTransformer('all-mpnet-base-v2')


@app.route("/search", methods=["GET"])
def search():
    """
    Endpoint /search:
    Realizando una búsqueda por nombre y filtra por la categoría principal.
    Parámetros:
      - search_box: Texto a buscar en 'name'
      - main_category: Valor exacto para filtrar 'main_category'
    """
    search_box = request.args.get("search_box", "")
    main_category = request.args.get("main_category", "")

    # Construcción de la consulta (usando un match para 'name' y un filtro term para 'main_category')
    query_body = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"name": search_box}}
                ],
                "filter": [
                    {"term": {"main_category": main_category}} if main_category else {}
                ]
            }
        },
        "sort": [
            {"ratings": {"order": "desc"}}
        ]
    }
    # Si main_category está vacío, quitamos el filtro
    if not main_category:
        del query_body["query"]["bool"]["filter"]

    try:
        res = es.search(index=index_name, body=query_body)
        return jsonify(res["hits"]["hits"])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/similar_products", methods=["GET"])
def similar_products():
    """
    Endpoint /similar_products:
    Calculando el embedding del producto consultado y devuelve los 5 productos más similares.
    Parámetro:
      - product_name: Nombre del producto para calcular el embedding
    """
    product_name = request.args.get("product_name", "")
    if not product_name:
        return jsonify({"error": "El parámetro product_name es obligatorio."}), 400

    query_embedding = model.encode(product_name).tolist()

    # Consulta utilizando script_score para calcular similitud por cosineSimilarity
    query_body = {
        "size": 5,
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": query_embedding}
                }
            }
        }
    }
    try:
        res = es.search(index=index_name, body=query_body)
        return jsonify(res["hits"]["hits"])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/top_products", methods=["GET"])
def top_products():
    """
    Endpoint /top_products:
    Devuelviendo los productos mejor valorados, con opción de filtrar por categoría.
    Parámetros opcionales:
      - limit: Cantidad de productos a devolver (por defecto 10)
      - main_category: Si se especifica, filtra por esa categoría exacta.
    """
    try:
        limit = int(request.args.get("limit", 10))
    except ValueError:
        return jsonify({"error": "El parámetro 'limit' debe ser un número entero."}), 400

    main_category = request.args.get("main_category", "")

    # Construir la consulta
    query_body = {
        "size": limit,
        "query": {
            "match_all": {}
        },
        "sort": [
            {"ratings": {"order": "desc"}}
        ]
    }
    # Si se especifica la categoría, se añade un filtro exacto
    if main_category:
        query_body["query"] = {
            "bool": {
                "must": [{"match_all": {}}],
                "filter": [{"term": {"main_category": main_category}}]
            }
        }

    try:
        res = es.search(index=index_name, body=query_body)
        return jsonify(res["hits"]["hits"])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
