from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'clave_secreta_biblioteca'

# Configuración MongoDB
app.config["MONGO_URI"] = "mongodb://localhost:27017/biblioteca"
mongo = PyMongo(app)

# --------------------------
# RUTAS PARA USUARIOS (CRUD)
# --------------------------
@app.route('/usuarios')
def usuarios():
    usuarios = list(mongo.db.usuarios.find())
    return render_template('usuarios/index.html', usuarios=usuarios)

@app.route('/usuarios/agregar', methods=['GET', 'POST'])
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
    return render_template('usuarios/agregar.html')

@app.route('/usuarios/editar/<id>', methods=['GET', 'POST'])
def editar_usuario(id):
    if request.method == 'POST':
        mongo.db.usuarios.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'nombre': request.form['nombre'],
                'apellido': request.form['apellido'],
                'email': request.form['email'],
                'direccion': request.form['direccion'],
                'fechaNacimiento': request.form['fechaNacimiento']
            }}
        )
        flash('Usuario actualizado correctamente')
        return redirect(url_for('usuarios'))
    usuario = mongo.db.usuarios.find_one({'_id': ObjectId(id)})
    return render_template('usuarios/editar.html', usuario=usuario)

@app.route('/usuarios/eliminar/<id>')
def eliminar_usuario(id):
    mongo.db.usuarios.delete_one({'_id': ObjectId(id)})
    flash('Usuario eliminado correctamente')
    return redirect(url_for('usuarios'))

# --------------------------
# RUTAS PARA LIBROS (CRUD)
# --------------------------
@app.route('/libros')
def libros():
    libros = list(mongo.db.libros.find())
    return render_template('libros/index.html', libros=libros)

@app.route('/libros/agregar', methods=['GET', 'POST'])
def agregar_libro():
    if request.method == 'POST':
        libro = {
            'titulo': request.form['titulo'],
            'autor': request.form['autor'],
            'isbn': request.form['isbn'],
            'categoria': request.form['categoria'],
            'ejemplares': int(request.form['ejemplares']),
            'disponibles': int(request.form['ejemplares'])  # Inicialmente todos disponibles
        }
        mongo.db.libros.insert_one(libro)
        flash('Libro agregado correctamente')
        return redirect(url_for('libros'))
    return render_template('libros/agregar.html')

# (Implementar editar y eliminar libros similar a usuarios)

# --------------------------
# RUTAS PARA PRÉSTAMOS (CRUD)
# --------------------------
@app.route('/prestamos')
def prestamos():
    prestamos = list(mongo.db.prestamos.aggregate([{
        '$lookup': {
            'from': 'usuarios',
            'localField': 'usuario_id',
            'foreignField': '_id',
            'as': 'usuario'
        }
    }, {
        '$lookup': {
            'from': 'libros',
            'localField': 'libro_id',
            'foreignField': '_id',
            'as': 'libro'
        }
    }]))
    return render_template('prestamos/index.html', prestamos=prestamos)

@app.route('/prestamos/agregar', methods=['GET', 'POST'])
def agregar_prestamo():
    if request.method == 'POST':
        fecha_prestamo = request.form['fechaPrestamo']
        prestamo = {
            'usuario_id': ObjectId(request.form['usuario_id']),
            'libro_id': ObjectId(request.form['libro_id']),
            'fechaPrestamo': fecha_prestamo,
            'fechaDevolucion': (datetime.strptime(fecha_prestamo, '%Y-%m-%d') + timedelta(days=7)).strftime('%Y-%m-%d'),
            'estado': 'Pendiente'
        }
        # Disminuir disponibilidad
        mongo.db.libros.update_one(
            {'_id': ObjectId(request.form['libro_id'])},
            {'$inc': {'disponibles': -1}}
        )
        mongo.db.prestamos.insert_one(prestamo)
        flash('Préstamo registrado correctamente')
        return redirect(url_for('prestamos'))
    
    usuarios = list(mongo.db.usuarios.find())
    libros = list(mongo.db.libros.find({'disponibles': {'$gt': 0}}))
    return render_template('prestamos/agregar.html', usuarios=usuarios, libros=libros)

# --------------------------
# RUTAS PARA RESERVAS (CRUD)
# --------------------------
@app.route('/reservas')
def reservas():
    reservas = list(mongo.db.reservas.aggregate([{
        '$lookup': {
            'from': 'usuarios',
            'localField': 'usuario_id',
            'foreignField': '_id',
            'as': 'usuario'
        }
    }, {
        '$lookup': {
            'from': 'libros',
            'localField': 'libro_id',
            'foreignField': '_id',
            'as': 'libro'
        }
    }]))
    return render_template('reservas/index.html', reservas=reservas)

@app.route('/reservas/agregar', methods=['GET', 'POST'])
def agregar_reserva():
    if request.method == 'POST':
        reserva = {
            'usuario_id': ObjectId(request.form['usuario_id']),
            'libro_id': ObjectId(request.form['libro_id']),
            'fechaReserva': request.form['fechaReserva']
        }
        mongo.db.reservas.insert_one(reserva)
        flash('Reserva registrada correctamente')
        return redirect(url_for('reservas'))
    
    usuarios = list(mongo.db.usuarios.find())
    libros = list(mongo.db.libros.find())
    return render_template('reservas/agregar.html', usuarios=usuarios, libros=libros)

if __name__ == '__main__':
    app.run(debug=True)