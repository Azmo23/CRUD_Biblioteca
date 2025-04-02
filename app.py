from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from datetime import datetime, timedelta
from bson.objectid import ObjectId

app = Flask(__name__)

# Configuración de MongoDB (reemplaza con tus datos)
app.config["MONGO_URI"] = "mongodb://localhost:27017/biblioteca"
mongo = PyMongo(app)

# No necesitamos crear tablas, MongoDB crea colecciones automáticamente

# Ruta principal
@app.route('/')
def index():
    stats = {
        'total_usuarios': mongo.db.usuarios.count_documents({}),
        'total_libros': mongo.db.libros.count_documents({}),
        'prestamos_pendientes': mongo.db.prestamos.count_documents({'estado': 'Pendiente'}),
        'total_reservas': mongo.db.reservas.count_documents({})
    }
    return render_template('index.html', stats=stats)

# CRUD Usuarios (Ejemplo adaptado)
@app.route('/usuarios')
def usuarios():
    usuarios = list(mongo.db.usuarios.find())
    return render_template('usuarios/index.html', usuarios=usuarios)

@app.route('/usuarios/agregar', methods=['POST'])
def agregar_usuario():
    if request.method == 'POST':
        usuario = {
            'nombre': request.form['nombre'],
            'apellido': request.form['apellido'],
            'email': request.form['email'],
            'direccion': request.form['direccion'],
            'fechaNacimiento': request.form['fechaNacimiento']
        }
        mongo.db.usuarios.insert_one(usuario)
        flash('Usuario agregado correctamente')
    return redirect(url_for('usuarios'))

# CRUD Libros (Ejemplo adaptado)
@app.route('/libros/agregar', methods=['POST'])
def agregar_libro():
    if request.method == 'POST':
        libro = {
            'titulo': request.form['titulo'],
            'autor': request.form['autor'],
            'isbn': request.form['isbn'],
            'categoria': request.form['categoria'],
            'ejemplares': int(request.form['ejemplares']),
            'disponibles': int(request.form['ejemplares'])  # Nuevo campo para control
        }
        mongo.db.libros.insert_one(libro)
        flash('Libro agregado correctamente')
    return redirect(url_for('libros'))

# CRUD Préstamos (Ejemplo adaptado)
@app.route('/prestamos/agregar', methods=['POST'])
def agregar_prestamo():
    if request.method == 'POST':
        libro_id = request.form['libro_id']
        # Disminuir disponibles
        mongo.db.libros.update_one(
            {'_id': ObjectId(libro_id)},
            {'$inc': {'disponibles': -1}}
        )
        
        prestamo = {
            'usuario_id': ObjectId(request.form['usuario_id']),
            'libro_id': ObjectId(libro_id),
            'fechaPrestamo': request.form['fechaPrestamo'],
            'fechaDevolucion': (datetime.strptime(request.form['fechaPrestamo'], '%Y-%m-%d') + timedelta(days=7)).strftime('%Y-%m-%d'),
            'estado': 'Pendiente'
        }
        mongo.db.prestamos.insert_one(prestamo)
        flash('Préstamo registrado correctamente')
    return redirect(url_for('prestamos'))

if __name__ == '__main__':
    app.secret_key = 'tu_clave_secreta_aqui'
    app.run(debug=True)