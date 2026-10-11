import os
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuración de la aplicación
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "clave-local-solo-para-desarrollo"
)

# Ruta de la base de datos local
BASE_DIR = Path(__file__).resolve().parent

# Leer la dirección de PostgreSQL desde Render.
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Adaptar las direcciones de conexión de Render
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgres://",
            "postgresql+psycopg://",
            1
        )
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL

else:
    # Si no existe DATABASE_URL, usar SQLite local.
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"sqlite:///{BASE_DIR / 'biblioteca.db'}"
    )

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Modelo que representa cada libro
class Libro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    estado = db.Column(
        db.String(20),
        nullable=False,
        default="Disponible"
    )


# Página principal: mostrar todos los libros
@app.route("/")
def index():
    libros = Libro.query.order_by(Libro.id.desc()).all()
    return render_template("index.html", libros=libros)


# Agregar un libro
@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        autor = request.form.get("autor", "").strip()

        if not titulo or not autor:
            flash("Escribe el título y el autor.", "error")
            return render_template("agregar.html")

        nuevo_libro = Libro(
            titulo=titulo,
            autor=autor,
            estado="Disponible"
        )

        db.session.add(nuevo_libro)
        db.session.commit()

        flash("Libro agregado correctamente.", "success")
        return redirect(url_for("index"))

    return render_template("agregar.html")


# Prestar un libro
@app.route("/prestar/<int:id>")
def prestar(id):
    libro = db.get_or_404(Libro, id)

    if libro.estado == "Disponible":
        libro.estado = "Prestado"
        db.session.commit()
        flash("El libro se marcó como prestado.", "success")
    else:
        flash("El libro ya está prestado.", "error")

    return redirect(url_for("index"))


# Devolver un libro
@app.route("/devolver/<int:id>")
def devolver(id):
    libro = db.get_or_404(Libro, id)

    libro.estado = "Disponible"
    db.session.commit()

    flash("El libro está disponible nuevamente.", "success")
    return redirect(url_for("index"))


# Eliminar un libro
@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    libro = db.get_or_404(Libro, id)

    db.session.delete(libro)
    db.session.commit()

    flash("Libro eliminado correctamente.", "success")
    return redirect(url_for("index"))


# Crear las tablas e iniciar la aplicación local

# Crear las tablas al iniciar la aplicación
with app.app_context():
    db.create_all()


# Iniciar el servidor local
if __name__ == "__main__":
    app.run(debug=True)
