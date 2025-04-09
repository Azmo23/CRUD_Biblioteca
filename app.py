from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'secret_key_biblioteca')

# Configuración MongoDB
app.config["MONGO_URI"] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/biblioteca')
mongo = PyMongo(app)

# --------------------------------------------
# RUTAS PRINCIPALES
# --------------------------------------------

@app.route('/')
def index():
    # Estadísticas
    stats = {
        'total_usuarios': mongo.db.usuarios.count_documents({}),
        'total_libros': mongo.db.libros.count_documents({}),
        'prestamos_pendientes': mongo.db.prestamos.count_documents({'estado': 'Pendiente'}),
        'total_reservas': mongo.db.reservas.count_documents({})
    }
    
    # Últimos préstamos con datos de usuarios y libros
    ultimos_prestamos = list(mongo.db.prestamos.aggregate([
        {
            '$lookup': {
                'from': 'usuarios',
                'localField': 'usuario_id',
                'foreignField': '_id',
                'as': 'usuario'
            }
        },
        {
            '$lookup': {
                'from': 'libros',
                'localField': 'libro_id',
                'foreignField': '_id',
                'as': 'libro'
            }
        },
        {'$sort': {'fechaPrestamo': -1}},
        {'$limit': 5}
    ]))
    
    # Últimos libros agregados
    ultimos_libros = list(mongo.db.libros.find().sort('_id', -1).limit(5))
    
    return render_template(
        'index.html',
        stats=stats,
        ultimos_prestamos=ultimos_prestamos,
        ultimos_libros=ultimos_libros,
        hoy=datetime.now().strftime('%Y-%m-%d')
    )

# --------------------------------------------
# CRUD USUARIOS
# --------------------------------------------

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
        flash('Usuario agregado correctamente', 'success')
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
        flash('Usuario actualizado correctamente', 'success')
        return redirect(url_for('usuarios'))
    
    usuario = mongo.db.usuarios.find_one({'_id': ObjectId(id)})
    return render_template('usuarios/editar.html', usuario=usuario)

@app.route('/usuarios/eliminar/<id>')
def eliminar_usuario(id):
    # Verificar si el usuario tiene préstamos/reservas activas
    if mongo.db.prestamos.count_documents({'usuario_id': ObjectId(id), 'estado': 'Pendiente'}) > 0:
        flash('No se puede eliminar: El usuario tiene préstamos pendientes', 'danger')
    else:
        mongo.db.usuarios.delete_one({'_id': ObjectId(id)})
        flash('Usuario eliminado correctamente', 'success')
    return redirect(url_for('usuarios'))

# --------------------------------------------
# CRUD LIBROS
# --------------------------------------------

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
        flash('Libro agregado correctamente', 'success')
        return redirect(url_for('libros'))
    return render_template('libros/agregar.html')

@app.route('/libros/editar/<id>', methods=['GET', 'POST'])
def editar_libro(id):
    if request.method == 'POST':
        libro_actual = mongo.db.libros.find_one({'_id': ObjectId(id)})
        nuevos_ejemplares = int(request.form['ejemplares'])
        
        mongo.db.libros.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'titulo': request.form['titulo'],
                'autor': request.form['autor'],
                'isbn': request.form['isbn'],
                'categoria': request.form['categoria'],
                'ejemplares': nuevos_ejemplares,
                'disponibles': max(0, libro_actual['disponibles'] + (nuevos_ejemplares - libro_actual['ejemplares']))
            }}
        )
        flash('Libro actualizado correctamente', 'success')
        return redirect(url_for('libros'))
    
    libro = mongo.db.libros.find_one({'_id': ObjectId(id)})
    return render_template('libros/editar.html', libro=libro)

@app.route('/libros/eliminar/<id>')
def eliminar_libro(id):
    # Verificar si el libro está en préstamos/reservas activas
    if mongo.db.prestamos.count_documents({'libro_id': ObjectId(id), 'estado': 'Pendiente'}) > 0:
        flash('No se puede eliminar: El libro tiene préstamos pendientes', 'danger')
    else:
        mongo.db.libros.delete_one({'_id': ObjectId(id)})
        flash('Libro eliminado correctamente', 'success')
    return redirect(url_for('libros'))

# --------------------------------------------
# CRUD PRÉSTAMOS
# --------------------------------------------

@app.route('/prestamos')
def prestamos():
    prestamos = list(mongo.db.prestamos.aggregate([
        {
            '$lookup': {
                'from': 'usuarios',
                'localField': 'usuario_id',
                'foreignField': '_id',
                'as': 'usuario'
            }
        },
        {
            '$lookup': {
                'from': 'libros',
                'localField': 'libro_id',
                'foreignField': '_id',
                'as': 'libro'
            }
        },
        {'$sort': {'fechaPrestamo': -1}}
    ]))
    return render_template('prestamos/index.html', prestamos=prestamos)

@app.route('/prestamos/agregar', methods=['GET', 'POST'])
def agregar_prestamo():
    if request.method == 'POST':
        libro_id = ObjectId(request.form['libro_id'])
        fecha_prestamo = request.form['fechaPrestamo']
        
        # Verificar disponibilidad
        libro = mongo.db.libros.find_one({'_id': libro_id})
        if libro['disponibles'] <= 0:
            flash('No hay ejemplares disponibles de este libro', 'danger')
            return redirect(url_for('prestamos'))
        
        # Registrar préstamo
        prestamo = {
            'usuario_id': ObjectId(request.form['usuario_id']),
            'libro_id': libro_id,
            'fechaPrestamo': fecha_prestamo,
            'fechaDevolucion': (datetime.strptime(fecha_prestamo, '%Y-%m-%d') + timedelta(days=7)).strftime('%Y-%m-%d'),
            'estado': 'Pendiente'
        }
        mongo.db.prestamos.insert_one(prestamo)
        
        # Actualizar disponibilidad
        mongo.db.libros.update_one(
            {'_id': libro_id},
            {'$inc': {'disponibles': -1}}
        )
        
        flash('Préstamo registrado correctamente', 'success')
        return redirect(url_for('prestamos'))
    
    usuarios = list(mongo.db.usuarios.find())
    libros = list(mongo.db.libros.find({'disponibles': {'$gt': 0}}))
    return render_template('prestamos/agregar.html', usuarios=usuarios, libros=libros)

@app.route('/prestamos/editar/<id>', methods=['GET', 'POST'])
def editar_prestamo(id):
    if request.method == 'POST':
        prestamo_actual = mongo.db.prestamos.find_one({'_id': ObjectId(id)})
        nuevo_estado = request.form['estado']
        
        # Si cambia de Pendiente a Devuelto, aumentar disponibilidad
        if prestamo_actual['estado'] == 'Pendiente' and nuevo_estado == 'Devuelto':
            mongo.db.libros.update_one(
                {'_id': prestamo_actual['libro_id']},
                {'$inc': {'disponibles': 1}}
            )
        
        mongo.db.prestamos.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'usuario_id': ObjectId(request.form['usuario_id']),
                'libro_id': ObjectId(request.form['libro_id']),
                'fechaPrestamo': request.form['fechaPrestamo'],
                'fechaDevolucion': request.form['fechaDevolucion'],
                'estado': nuevo_estado
            }}
        )
        flash('Préstamo actualizado correctamente', 'success')
        return redirect(url_for('prestamos'))
    
    prestamo = mongo.db.prestamos.find_one({'_id': ObjectId(id)})
    usuarios = list(mongo.db.usuarios.find())
    libros = list(mongo.db.libros.find())
    return render_template('prestamos/editar.html', prestamo=prestamo, usuarios=usuarios, libros=libros)

@app.route('/prestamos/eliminar/<id>')
def eliminar_prestamo(id):
    prestamo = mongo.db.prestamos.find_one({'_id': ObjectId(id)})
    
    # Si el préstamo estaba pendiente, aumentar disponibilidad
    if prestamo['estado'] == 'Pendiente':
        mongo.db.libros.update_one(
            {'_id': prestamo['libro_id']},
            {'$inc': {'disponibles': 1}}
        )
    
    mongo.db.prestamos.delete_one({'_id': ObjectId(id)})
    flash('Préstamo eliminado correctamente', 'success')
    return redirect(url_for('prestamos'))

# --------------------------------------------
# CRUD RESERVAS
# --------------------------------------------

@app.route('/reservas')
def reservas():
    reservas = list(mongo.db.reservas.aggregate([
        {
            '$lookup': {
                'from': 'usuarios',
                'localField': 'usuario_id',
                'foreignField': '_id',
                'as': 'usuario'
            }
        },
        {
            '$lookup': {
                'from': 'libros',
                'localField': 'libro_id',
                'foreignField': '_id',
                'as': 'libro'
            }
        },
        {'$sort': {'fechaReserva': -1}}
    ]))
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
        flash('Reserva registrada correctamente', 'success')
        return redirect(url_for('reservas'))
    
    usuarios = list(mongo.db.usuarios.find())
    libros = list(mongo.db.libros.find())
    return render_template('reservas/agregar.html', usuarios=usuarios, libros=libros)

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
        flash('Reserva actualizada correctamente', 'success')
        return redirect(url_for('reservas'))
    
    reserva = mongo.db.reservas.find_one({'_id': ObjectId(id)})
    usuarios = list(mongo.db.usuarios.find())
    libros = list(mongo.db.libros.find())
    return render_template('reservas/editar.html', reserva=reserva, usuarios=usuarios, libros=libros)

@app.route('/reservas/eliminar/<id>')
def eliminar_reserva(id):
    mongo.db.reservas.delete_one({'_id': ObjectId(id)})
    flash('Reserva eliminada correctamente', 'success')
    return redirect(url_for('reservas'))

# --------------------------------------------
# INICIO DE LA APLICACIÓN
# --------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)