from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

#CONFIGURACIÓN DE MariaDB
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'biblioteca')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'Simon2306')
mysql = MySQL(app)

#CONFIGURACIÓN DE MENSAJES FLASH
app.secret_key = 'Simon2306'

# Crear tablas si no existen
def create_tables():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        # Tabla usuarios
        cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            apellido VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            direccion VARCHAR(200) NOT NULL,
            fechaNacimiento DATE NOT NULL
        )
        """)
        
        # Tabla libros
        cur.execute("""
        CREATE TABLE IF NOT EXISTS libros (
            id INT AUTO_INCREMENT PRIMARY KEY,
            titulo VARCHAR(200) NOT NULL,
            autor VARCHAR(200) NOT NULL,
            isbn VARCHAR(20) NOT NULL UNIQUE,
            categoria VARCHAR(100) NOT NULL,
            ejemplares INT NOT NULL
        )
        """)
        
        # Tabla prestamos
        cur.execute("""
        CREATE TABLE IF NOT EXISTS prestamos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL,
            libro_id INT NOT NULL,
            fechaPrestamo DATE NOT NULL,
            fechaDevolucion DATE NOT NULL,
            estado VARCHAR(20) NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (libro_id) REFERENCES libros(id)
        )
        """)
        
        # Tabla reservas
        cur.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL,
            libro_id INT NOT NULL,
            fechaReserva DATE NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (libro_id) REFERENCES libros(id)
        )
        """)
        
        mysql.connection.commit()
        cur.close()

create_tables()

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    
    # Obtener estadísticas
    cur.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM libros")
    total_libros = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM prestamos WHERE estado = 'Pendiente'")
    prestamos_pendientes = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM reservas")
    total_reservas = cur.fetchone()[0]
    
    # Obtener últimos préstamos
    cur.execute("""
        SELECT p.id, u.nombre, u.apellido, l.titulo, p.fechaPrestamo, p.fechaDevolucion, p.estado
        FROM prestamos p
        JOIN usuarios u ON p.usuario_id = u.id
        JOIN libros l ON p.libro_id = l.id
        ORDER BY p.fechaPrestamo DESC
        LIMIT 5
    """)
    ultimos_prestamos = cur.fetchall()
    
    # Obtener últimos libros agregados
    cur.execute("SELECT * FROM libros ORDER BY id DESC LIMIT 5")
    ultimos_libros = cur.fetchall()
    
    cur.close()
    
    return render_template('index.html', 
                        total_usuarios=total_usuarios,
                        total_libros=total_libros,
                        prestamos_pendientes=prestamos_pendientes,
                        total_reservas=total_reservas,
                        ultimos_prestamos=ultimos_prestamos,
                        ultimos_libros=ultimos_libros)
# Rutas para Usuarios

#RUTA PARA VER USUARIOS.
@app.route('/usuarios')
def usuarios():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios ORDER BY nombre ASC")
    data = cur.fetchall()
    cur.close()
    return render_template('usuarios/index.html', usuarios=data)

#RUTA PARA AGREGAR USUARIO.
@app.route('/usuarios/agregar', methods=['GET', 'POST'])
def agregar_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        direccion = request.form['direccion']
        fechaNacimiento = request.form['fechaNacimiento']
        
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO usuarios (nombre, apellido, email, direccion, fechaNacimiento)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, apellido, email, direccion, fechaNacimiento))
        mysql.connection.commit()
        cur.close()
        
        flash('Usuario agregado correctamente')
        return redirect(url_for('usuarios'))
    
    return render_template('usuarios/agregar.html')

#RUTA PARA EDITAR USUARIO.
@app.route('/usuarios/editar/<id>', methods=['GET', 'POST'])
def editar_usuario(id):
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        direccion = request.form['direccion']
        fechaNacimiento = request.form['fechaNacimiento']
        
        cur.execute("""
            UPDATE usuarios
            SET nombre = %s,
                apellido = %s,
                email = %s,
                direccion = %s,
                fechaNacimiento = %s
            WHERE id = %s
        """, (nombre, apellido, email, direccion, fechaNacimiento, id))
        mysql.connection.commit()
        cur.close()
        
        flash('Usuario actualizado correctamente')
        return redirect(url_for('usuarios'))
    
    cur.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    data = cur.fetchone()
    cur.close()
    return render_template('usuarios/editar.html', usuario=data)

#RUTA PARA ELIMINAR USUARIO.
@app.route('/usuarios/eliminar/<id>')
def eliminar_usuario(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Usuario eliminado correctamente')
    return redirect(url_for('usuarios'))

# Rutas para Libros

#RUTA PARA VER LIBROS.
@app.route('/libros')
def libros():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM libros")
    data = cur.fetchall()
    cur.close()
    return render_template('libros/index.html', libros=data)

#RUTA PARA AGREGAR LIBRO.
@app.route('/libros/agregar', methods=['GET', 'POST'])
def agregar_libro():
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        isbn = request.form['isbn']
        categoria = request.form['categoria']
        ejemplares = request.form['ejemplares']
        
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO libros (titulo, autor, isbn, categoria, ejemplares)
            VALUES (%s, %s, %s, %s, %s)
        """, (titulo, autor, isbn, categoria, ejemplares))
        mysql.connection.commit()
        cur.close()
        
        flash('Libro agregado correctamente')
        return redirect(url_for('libros'))
    
    return render_template('libros/agregar.html')

#RUTA PARA EDITAR LIBROS.
@app.route('/libros/editar/<id>', methods=['GET', 'POST'])
def editar_libro(id):
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        isbn = request.form['isbn']
        categoria = request.form['categoria']
        ejemplares = request.form['ejemplares']
        
        cur.execute("""
            UPDATE libros
            SET titulo = %s,
                autor = %s,
                isbn = %s,
                categoria = %s,
                ejemplares = %s
            WHERE id = %s
        """, (titulo, autor, isbn, categoria, ejemplares, id))
        mysql.connection.commit()
        cur.close()
        
        flash('Libro actualizado correctamente')
        return redirect(url_for('libros'))
    
    cur.execute("SELECT * FROM libros WHERE id = %s", (id,))
    data = cur.fetchone()
    cur.close()
    return render_template('libros/editar.html', libro=data)

#RUTA PARA ELIMINAR LIBRO.
@app.route('/libros/eliminar/<id>')
def eliminar_libro(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM libros WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Libro eliminado correctamente')
    return redirect(url_for('libros'))

# Rutas para Prestamos
@app.route('/prestamos')
def prestamos():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.id, u.nombre, u.apellido, l.titulo, p.fechaPrestamo, p.fechaDevolucion, p.estado
        FROM prestamos p
        JOIN usuarios u ON p.usuario_id = u.id
        JOIN libros l ON p.libro_id = l.id
    """)
    data = cur.fetchall()
    cur.close()
    return render_template('prestamos/index.html', prestamos=data)

#RUTA PARA AGREGAR PRESTAMO
@app.route('/prestamos/agregar', methods=['GET', 'POST'])
def agregar_prestamo():
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        usuario_id = request.form['usuario_id']
        libro_id = request.form['libro_id']
        fechaPrestamo = request.form['fechaPrestamo']
        fechaDevolucion = (datetime.strptime(fechaPrestamo, '%Y-%m-%d') + timedelta(days=7)).strftime('%Y-%m-%d')
        estado = 'Pendiente'
        
        # Verificar disponibilidad del libro
        cur.execute("SELECT ejemplares FROM libros WHERE id = %s", (libro_id,))
        ejemplares = cur.fetchone()[0]
        
        if ejemplares > 0:
            # Actualizar ejemplares disponibles
            cur.execute("UPDATE libros SET ejemplares = ejemplares - 1 WHERE id = %s", (libro_id,))
            
            # Crear préstamo
            cur.execute("""
                INSERT INTO prestamos (usuario_id, libro_id, fechaPrestamo, fechaDevolucion, estado)
                VALUES (%s, %s, %s, %s, %s)
            """, (usuario_id, libro_id, fechaPrestamo, fechaDevolucion, estado))
            
            mysql.connection.commit()
            flash('Préstamo registrado correctamente')
        else:
            flash('No hay ejemplares disponibles de este libro', 'error')
        
        cur.close()
        return redirect(url_for('prestamos'))
    
    # Obtener usuarios y libros para el formulario
    cur.execute("SELECT id, nombre, apellido FROM usuarios")
    usuarios = cur.fetchall()
    
    cur.execute("SELECT id, titulo FROM libros WHERE ejemplares > 0")
    libros = cur.fetchall()
    
    cur.close()
    return render_template('prestamos/agregar.html', usuarios=usuarios, libros=libros)

#RUTA PARA EDITAR PRESTAMOS.
@app.route('/prestamos/editar/<id>', methods=['GET', 'POST'])
def editar_prestamo(id):
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        usuario_id = request.form['usuario_id']
        libro_id = request.form['libro_id']
        fechaPrestamo = request.form['fechaPrestamo']
        fechaDevolucion = request.form['fechaDevolucion']
        estado = request.form['estado']
        
        cur.execute("""
            UPDATE prestamos
            SET usuario_id = %s,
                libro_id = %s,
                fechaPrestamo = %s,
                fechaDevolucion = %s,
                estado = %s
            WHERE id = %s
        """, (usuario_id, libro_id, fechaPrestamo, fechaDevolucion, estado, id))
        mysql.connection.commit()
        cur.close()
        
        flash('Préstamo actualizado correctamente')
        return redirect(url_for('prestamos'))
    
    # Obtener datos del préstamo
    cur.execute("SELECT * FROM prestamos WHERE id = %s", (id,))
    prestamo = cur.fetchone()
    
    # Obtener usuarios y libros para el formulario
    cur.execute("SELECT id, nombre, apellido FROM usuarios")
    usuarios = cur.fetchall()
    
    cur.execute("SELECT id, titulo FROM libros")
    libros = cur.fetchall()
    
    cur.close()
    return render_template('prestamos/editar.html', prestamo=prestamo, usuarios=usuarios, libros=libros)

#RUTA PARA ELIMINAR PRESTAMO.
@app.route('/prestamos/eliminar/<id>')
def eliminar_prestamo(id):
    cur = mysql.connection.cursor()
    
    # Obtener libro_id para actualizar ejemplares
    cur.execute("SELECT libro_id FROM prestamos WHERE id = %s", (id,))
    libro_id = cur.fetchone()[0]
    
    # Eliminar préstamo
    cur.execute("DELETE FROM prestamos WHERE id = %s", (id,))
    
    # Actualizar ejemplares disponibles
    cur.execute("UPDATE libros SET ejemplares = ejemplares + 1 WHERE id = %s", (libro_id,))
    
    mysql.connection.commit()
    cur.close()
    
    flash('Préstamo eliminado correctamente')
    return redirect(url_for('prestamos'))

# Rutas para Reservas
@app.route('/reservas')
def reservas():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT r.id, u.nombre, u.apellido, l.titulo, r.fechaReserva
        FROM reservas r
        JOIN usuarios u ON r.usuario_id = u.id
        JOIN libros l ON r.libro_id = l.id
    """)
    data = cur.fetchall()
    cur.close()
    return render_template('reservas/index.html', reservas=data)

#RUTA PARA AGREGAR RESERVA.
@app.route('/reservas/agregar', methods=['GET', 'POST'])
def agregar_reserva():
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        usuario_id = request.form['usuario_id']
        libro_id = request.form['libro_id']
        fechaReserva = request.form['fechaReserva']
        
        cur.execute("""
            INSERT INTO reservas (usuario_id, libro_id, fechaReserva)
            VALUES (%s, %s, %s)
        """, (usuario_id, libro_id, fechaReserva))
        mysql.connection.commit()
        cur.close()
        
        flash('Reserva registrada correctamente')
        return redirect(url_for('reservas'))
    
    # Obtener usuarios y libros para el formulario
    cur.execute("SELECT id, nombre, apellido FROM usuarios")
    usuarios = cur.fetchall()
    
    cur.execute("SELECT id, titulo FROM libros")
    libros = cur.fetchall()
    
    cur.close()
    return render_template('reservas/agregar.html', usuarios=usuarios, libros=libros)

#RUTA PARA EDITAR RESERVA.
@app.route('/reservas/editar/<id>', methods=['GET', 'POST'])
def editar_reserva(id):
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        usuario_id = request.form['usuario_id']
        libro_id = request.form['libro_id']
        fechaReserva = request.form['fechaReserva']
        
        cur.execute("""
            UPDATE reservas
            SET usuario_id = %s,
                libro_id = %s,
                fechaReserva = %s
            WHERE id = %s
        """, (usuario_id, libro_id, fechaReserva, id))
        mysql.connection.commit()
        cur.close()
        
        flash('Reserva actualizada correctamente')
        return redirect(url_for('reservas'))
    
    # Obtener datos de la reserva
    cur.execute("SELECT * FROM reservas WHERE id = %s", (id,))
    reserva = cur.fetchone()
    
    # Obtener usuarios y libros para el formulario
    cur.execute("SELECT id, nombre, apellido FROM usuarios")
    usuarios = cur.fetchall()
    
    cur.execute("SELECT id, titulo FROM libros")
    libros = cur.fetchall()
    
    cur.close()
    return render_template('reservas/editar.html', reserva=reserva, usuarios=usuarios, libros=libros)

#RUTA PARA ELIMINAR RESERVA.
@app.route('/reservas/eliminar/<id>')
def eliminar_reserva(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM reservas WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Reserva eliminada correctamente')
    return redirect(url_for('reservas'))

# Ruta principal

def index():
    return render_template('base.html')

if __name__ == '__main__':
    app.run(debug=True)
