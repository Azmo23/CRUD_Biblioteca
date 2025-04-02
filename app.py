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

# Editar Libro - GET (Formulario) / POST (Procesar)
@app.route('/libros/editar/<id>', methods=['GET', 'POST'])
def editar_libro(id):
    if request.method == 'POST':
        mongo.db.libros.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'titulo': request.form['titulo'],
                'autor': request.form['autor'],
                'isbn': request.form['isbn'],
                'categoria': request.form['categoria'],
                'ejemplares': int(request.form['ejemplares']),
                'disponibles': int(request.form['ejemplares']) - 
                    (mongo.db.libros.find_one({'_id': ObjectId(id)})['ejemplares'] - 
                    mongo.db.libros.find_one({'_id': ObjectId(id)})['disponibles'])
            }}
        )
        flash('Libro actualizado correctamente')
        return redirect(url_for('libros'))
    
    libro = mongo.db.libros.find_one({'_id': ObjectId(id)})
    return render_template('libros/editar.html', libro=libro)

# Eliminar Libro
@app.route('/libros/eliminar/<id>')
def eliminar_libro(id):
    # Verificar si el libro está en préstamos/reservas activas
    if mongo.db.prestamos.count_documents({'libro_id': ObjectId(id), 'estado': 'Pendiente'}) > 0:
        flash('No se puede eliminar: El libro tiene préstamos pendientes', 'error')
    else:
        mongo.db.libros.delete_one({'_id': ObjectId(id)})
        flash('Libro eliminado correctamente')
    return redirect(url_for('libros'))

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

# Editar Préstamo
@app.route('/prestamos/editar/<id>', methods=['GET', 'POST'])
def editar_prestamo(id):
    if request.method == 'POST':
        mongo.db.prestamos.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'usuario_id': ObjectId(request.form['usuario_id']),
                'libro_id': ObjectId(request.form['libro_id']),
                'fechaPrestamo': request.form['fechaPrestamo'],
                'fechaDevolucion': request.form['fechaDevolucion'],
                'estado': request.form['estado']
            }}
        )
        flash('Préstamo actualizado correctamente')
        return redirect(url_for('prestamos'))
    
    prestamo = mongo.db.prestamos.find_one({'_id': ObjectId(id)})
    usuarios = list(mongo.db.usuarios.find())
    libros = list(mongo.db.libros.find())
    return render_template('prestamos/editar.html', 
                        prestamo=prestamo,
                        usuarios=usuarios,
                        libros=libros)

# Eliminar Préstamo
@app.route('/prestamos/eliminar/<id>')
def eliminar_prestamo(id):
    prestamo = mongo.db.prestamos.find_one({'_id': ObjectId(id)})
    # Incrementar disponibilidad al eliminar
    mongo.db.libros.update_one(
        {'_id': prestamo['libro_id']},
        {'$inc': {'disponibles': 1}}
    )
    mongo.db.prestamos.delete_one({'_id': ObjectId(id)})
    flash('Préstamo eliminado correctamente')
    return redirect(url_for('prestamos'))

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

# Editar Reserva
@app.route('/reservas/editar/<id>', methods=['GET', 'POST'])
def editar_reserva(id):
    if request.method == 'POST':
        mongo.db.reservas.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'usuario_id': ObjectId(request.form['usuario_id']),
                'libro_id': ObjectId(request.form['libro_id']),
                'fechaReserva': request.form['fechaReserva']
            }}
        )
        flash('Reserva actualizada correctamente')
        return redirect(url_for('reservas'))
    
    reserva = mongo.db.reservas.find_one({'_id': ObjectId(id)})
    usuarios = list(mongo.db.usuarios.find())
    libros = list(mongo.db.libros.find())
    return render_template('reservas/editar.html', 
                        reserva=reserva,
                        usuarios=usuarios,
                        libros=libros)

# Eliminar Reserva
@app.route('/reservas/eliminar/<id>')
def eliminar_reserva(id):
    mongo.db.reservas.delete_one({'_id': ObjectId(id)})
    flash('Reserva eliminada correctamente')
    return redirect(url_for('reservas'))


if __name__ == '__main__':
    app.run(debug=True)