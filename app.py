from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'  # Necesario para usar Flask Flash

# Conexión a MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['biblioteca']

# Colecciones
usuarios = db['usuarios']
libros = db['libros']
reservas = db['reservas']
prestamos = db['prestamos']

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para registrar usuarios
@app.route('/registrar_usuario', methods=['GET', 'POST'])
def registrar_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        
        usuarios.insert_one({
            "nombre": nombre,
            "email": email,
            "telefono": telefono,
            "direccion": direccion
        })
        flash('Usuario registrado correctamente', 'success')
        return redirect(url_for('index'))
    return render_template('registrar_usuario.html')

# Ruta para ver usuarios
@app.route('/ver_usuarios')
def ver_usuarios():
    usuarios_lista = list(usuarios.find())
    return render_template('ver_usuarios.html', usuarios=usuarios_lista)

# Ruta para editar un usuario
@app.route('/editar_usuario/<usuario_id>', methods=['GET', 'POST'])
def editar_usuario(usuario_id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        usuarios.update_one(
            {"_id": ObjectId(usuario_id)},
            {"$set": {
                "nombre": nombre,
                "email": email,
                "telefono": telefono,
                "direccion": direccion
            }}
        )
        flash('Usuario actualizado correctamente', 'success')
        return redirect(url_for('ver_usuarios'))
    else:
        usuario = usuarios.find_one({"_id": ObjectId(usuario_id)})
        return render_template('editar_usuario.html', usuario=usuario)

# Ruta para eliminar un usuario
@app.route('/eliminar_usuario/<usuario_id>')
def eliminar_usuario(usuario_id):
    usuarios.delete_one({"_id": ObjectId(usuario_id)})
    flash('Usuario eliminado correctamente', 'success')
    return redirect(url_for('ver_usuarios'))

# Ruta para ingresar libros
@app.route('/ingresar_libro', methods=['GET', 'POST'])
def ingresar_libro():
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        isbn = request.form['isbn']
        genero = request.form['genero']
        yearPub = request.form['yearPub']
        ejemplares = int(request.form['ejemplares'])
        libros.insert_one({
            "titulo": titulo,
            "autor": autor,
            "ejemplares": ejemplares,
            "isbn": isbn,
            "genero": genero,
            "yearPub": yearPub
        })
        flash('Libro ingresado correctamente', 'success')
        return redirect(url_for('index'))
    return render_template('ingresar_libro.html')

# Ruta para editar un libro
@app.route('/editar_libro/<libro_id>', methods=['GET', 'POST'])
def editar_libro(libro_id):
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        isbn = request.form['isbn']
        genero = request.form['genero']
        yearPub = request.form['yearPub']
        ejemplares = int(request.form['ejemplares'])
        libros.update_one(
            {"_id": ObjectId(libro_id)},
            {"$set": {
                "titulo": titulo,
                "autor": autor,
                "ejemplares": ejemplares,
                "isbn": isbn,
                "genero": genero,
                "yearPub": yearPub
            }}
        )
        flash('Libro actualizado correctamente', 'success')
        return redirect(url_for('consultar_libros'))
    else:
        libro = libros.find_one({"_id": ObjectId(libro_id)})
        return render_template('editar_libro.html', libro=libro)

# Ruta para eliminar un libro
@app.route('/eliminar_libro/<libro_id>')
def eliminar_libro(libro_id):
    libros.delete_one({"_id": ObjectId(libro_id)})
    flash('Libro eliminado correctamente', 'success')
    return redirect(url_for('consultar_libros'))

# Ruta para consultar libros
@app.route('/consultar_libros')
def consultar_libros():
    libros_lista = list(libros.find())
    return render_template('consultar_libros.html', libros=libros_lista)

# Ruta para agregar reservas
@app.route('/agregar_reserva', methods=['GET', 'POST'])
def agregar_reserva():
    if request.method == 'POST':
        usuario_id = request.form['usuario_id']
        libro_id = request.form['libro_id']
        fecha_reserva = request.form['fecha_reserva']
        
        reservas.insert_one({
            "usuario_id": ObjectId(usuario_id),
            "libro_id": ObjectId(libro_id),
            "fecha_reserva": fecha_reserva,

        })
        flash('Reserva agregada correctamente', 'success')
        return redirect(url_for('ver_reservas'))
    return render_template('agregar_reserva.html', usuarios=usuarios.find(), libros=libros.find())

# Ruta para ver reservas
@app.route('/ver_reservas')
def ver_reservas():
    reservas_lista = list(reservas.find())
    return render_template('ver_reservas.html', reservas=reservas_lista, usuarios=usuarios, libros=libros)

# Ruta para editar reservas
@app.route('/editar_reserva/<reserva_id>', methods=['GET', 'POST'])
def editar_reserva(reserva_id):
    if request.method == 'POST':
        usuario_id = request.form['usuario_id']
        libro_id = request.form['libro_id']
        fecha_reserva = request.form['fecha_reserva']

        reservas.update_one(
            {"_id": ObjectId(reserva_id)},
            {"$set": {
                "usuario_id": ObjectId(usuario_id),
                "libro_id": ObjectId(libro_id),
                "fecha_reserva": fecha_reserva,

            }}
        )
        flash('Reserva actualizada correctamente', 'success')
        return redirect(url_for('ver_reservas'))
    else:
        reserva = reservas.find_one({"_id": ObjectId(reserva_id)})
        return render_template('editar_reserva.html', reserva=reserva, usuarios=usuarios.find(), libros=libros.find())

# Ruta para eliminar reservas
@app.route('/eliminar_reserva/<reserva_id>')
def eliminar_reserva(reserva_id):
    reservas.delete_one({"_id": ObjectId(reserva_id)})
    flash('Reserva eliminada correctamente', 'success')
    return redirect(url_for('ver_reservas'))

# Ruta para agregar préstamos
@app.route('/agregar_prestamo', methods=['GET', 'POST'])
def agregar_prestamo():
    if request.method == 'POST':
        usuario_id = request.form['usuario_id']
        libro_id = request.form['libro_id']
        fecha_prestamo = request.form['fecha_prestamo']
        fecha_devolucion = request.form['fecha_devolucion']
        estado = request.form['estado']
        prestamos.insert_one({
            "usuario_id": ObjectId(usuario_id),
            "libro_id": ObjectId(libro_id),
            "fecha_prestamo": fecha_prestamo,
            "fecha_devolucion": fecha_devolucion,
            "estado": estado
        })
        flash('Préstamo agregado correctamente', 'success')
        return redirect(url_for('ver_prestamos'))
    return render_template('agregar_prestamo.html', usuarios=usuarios.find(), libros=libros.find())

# Ruta para ver préstamos
@app.route('/ver_prestamos')
def ver_prestamos():
    prestamos_lista = list(prestamos.find())
    return render_template('ver_prestamos.html', prestamos=prestamos_lista, usuarios=usuarios, libros=libros)

# Ruta para editar préstamos
@app.route('/editar_prestamo/<prestamo_id>', methods=['GET', 'POST'])
def editar_prestamo(prestamo_id):
    if request.method == 'POST':
        usuario_id = request.form['usuario_id']
        libro_id = request.form['libro_id']
        fecha_prestamo = request.form['fecha_prestamo']
        fecha_devolucion = request.form['fecha_devolucion']
        estado = request.form['estado']
        prestamos.update_one(
            {"_id": ObjectId(prestamo_id)},
            {"$set": {
                "usuario_id": ObjectId(usuario_id),
                "libro_id": ObjectId(libro_id),
                "fecha_prestamo": fecha_prestamo,
                "fecha_devolucion": fecha_devolucion,
                "estado": estado
            }}
        )
        flash('Préstamo actualizado correctamente', 'success')
        return redirect(url_for('ver_prestamos'))
    else:
        prestamo = prestamos.find_one({"_id": ObjectId(prestamo_id)})
        return render_template('editar_prestamo.html', prestamo=prestamo, usuarios=usuarios.find(), libros=libros.find())

# Ruta para eliminar préstamos
@app.route('/eliminar_prestamo/<prestamo_id>')
def eliminar_prestamo(prestamo_id):
    prestamos.delete_one({"_id": ObjectId(prestamo_id)})
    flash('Préstamo eliminado correctamente', 'success')
    return redirect(url_for('ver_prestamos'))

if __name__ == '__main__':
    app.run(debug=True)