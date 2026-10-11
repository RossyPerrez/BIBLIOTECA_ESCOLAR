from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

app = Flask(__name__)

# Configuración de la aplicación
app.config["SECRET_KEY"] = "cambia-esta-clave-para-tu-proyecto"

# Ruta de la base de datos SQLite
BASE_DIR = Path(__file__).resolve().parent
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


# Crear las tablas e iniciar la aplicación
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)