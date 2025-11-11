import random
import string

from flask import Flask, jsonify, redirect, request

app = Flask(__name__)
url_db = {}


def gerar_codigo(tamanho=6):
    character = string.ascii_letters + string.digits
    return "".join(random.choice(character) for _ in range(tamanho))


@app.route("/api/encurtar", methods=["POST"])
def encurtar():
    dados = request.get_json()

    if not dados or "url" not in dados:
        return jsonify(
            {"erro": 'Por favor, forneça uma URL no formato JSON: {"url": "..."}'}
        ), 400

    url_original = dados["url"]
    codigo = gerar_codigo()

    while codigo in url_db:
        codigo = gerar_codigo()

    url_db[codigo] = url_original

    url_curta = f"{request.host_url}{codigo}"
    return jsonify(
        {"url_original": url_original, "url_curta": url_curta, "codigo": codigo}
    ), 201


if __name__ == "__main__":
    app.run(debug=True)
