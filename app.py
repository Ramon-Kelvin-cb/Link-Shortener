import os
import random
import string

from flask import Flask, jsonify, redirect, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

uri_banco = os.getenv("DATABASE_URL", "sqlite:///local.db")
if uri_banco and uri_banco.startswith("postgres://"):
    uri_banco = uri_banco.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = uri_banco
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo_curto = db.Column(db.String(10), unique=True, nullable=False, index=True)
    url_original = db.Column(db.String(2048), nullable=False)

    def __repr__(self):
        return f"<Link {self.codigo_curto}>"


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

    for _ in range(5):
        codigo = gerar_codigo()
        # Verifica se já existe usando o ORM
        if not Link.query.filter_by(codigo_curto=codigo).first():
            novo_link = Link(codigo_curto=codigo, url_original=url_original)
            db.session.add(novo_link)
            db.session.commit()

            return jsonify(
                {
                    "url_original": url_original,
                    "url_curta": f"{request.host_url}{codigo}",
                    "codigo": codigo,
                }
            ), 201

    return jsonify(
        {"erro": "Não foi possível gerar um código único, tente novamente."}
    ), 500


@app.route("/<codigo>", methods=["GET"])
def redirecionar(codigo):
    link = Link.query.filter_by(codigo_curto=codigo).first()

    if link:
        return redirect(link.url_original)
    else:
        return jsonify({"erro": "URL curta não encontrada"}), 404


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
