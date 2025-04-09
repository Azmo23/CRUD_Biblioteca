# 📖 BibliotecaFlask - Sistema de Gestión de Biblioteca

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-lightgrey)
![MongoDB](https://img.shields.io/badge/MongoDB-5.0%2B-green)

Aplicación web completa para la gestión de usuarios, libros, préstamos y reservas en una biblioteca, con interfaz CRUD para cada módulo.

## 🌟 Características Principales

- **CRUD Completo** para 4 módulos:
  - 👥 Usuarios
  - 📚 Libros
  - 🔄 Préstamos
  - 🗓️ Reservas
- **Base de datos NoSQL** con MongoDB
- **Validación de formularios** integrada
- **Fechas automáticas** para préstamos (7 días de duración)
- **Interfaz intuitiva** con navegación por rutas

## 🛠️ Tecnologías Utilizadas

| Componente       | Tecnología           |
|------------------|---------------------|
| Backend          | Python + Flask      |
| Base de Datos    | MongoDB             |
| Frontend         | HTML5 + CSS3        |
| Forms            | Flask-WTF           |
| ORM              | PyMongo             |

## 🚀 Instalación

### Requisitos Previos
- Python 3.8+
- MongoDB local o remoto
- Pip instalado

### Pasos para Configuración

1. Clonar repositorio:
```bash
    git clone https://github.com/Azmo23/CRUD_Biblioteca.git
    cd CRUD_Biblioteca
```

2. Instalar dependencias:
```bash
    pip install flask pymongo flask-wtf
```
3. Configurar MongoDB: 
```python
    #En app.py
    app.config["MONGO_URI"] = "mongodb://localhost:27017/biblioteca"
```
4. Ejecutar aplicación:
```bash
    python app.py
```
5. Acceder en navegador:
```
  http://localhost:5000
```

## 📕Estructura del codigo.
```
biblioteca-app/
├── app.py                # Aplicación principal
├── static/               # Archivos CSS/JS (si los hay)
└── templates/            # Plantillas HTML
    ├── base.html         # Plantilla base
    ├── index.html        # Dashboard principal
    ├── usuarios/         # CRUD de usuarios
    │   ├── index.html
    │   ├── agregar.html
    │   └── editar.html
    ├── libros/           # CRUD de libros
    │   ├── index.html
    │   ├── agregar.html
    │   └── editar.html
    ├── prestamos/        # Gestión de préstamos
    │   ├── index.html
    │   ├── agregar.html
    │   └── editar.html
    └── reservas/         # Gestión de reservas
        ├── index.html
        ├── agregar.html
        └── editar.html
```
## 📊Modelo de datos
**Usuario.**
```JSON
  db.usuario.insertOne({
    "nombre" : "Carlos",
    "apellido": "Garcia",
    "email": "carlos.garcia@example.com",
    "direccion": "Calle 123, 456",
    "telefono": "6543210987",
    "fecha_nacimiento": "15-06-1990",
  })
```
**Préstamo**
```JSON
  db.prestamos.insertOne({
    "_id":"456",
    "usuario_id": ObjectID,
    "libro_id": "112",
    "fecha_prest": "20-02-2025",
    "fecha_dev": "23-02-2025",
    "estado": ["activo | devuelto"]
  });
```
## 📈Diagrama de la respectica aplicación.

![CasosDeUso](https://github.com/Azmo23/CRUD_Biblioteca/blob/main/img/CasosDeUso.png)

## 🖥Capturas de Pantalla de la aplicación.

**Vista Principal**
![VistaPrincipal] (https://github.com/Azmo23/CRUD_Biblioteca/blob/main/img/VistaPrincipal.jpg)

**Formulario Agregar Usuario**
![FormularioAggUsuario](https://github.com/Azmo23/CRUD_Biblioteca/blob/main/img/FormularioUsuario.jpg)

**CRUD de Libros**
![CRUDLibro](https://github.com/Azmo23/CRUD_Biblioteca/blob/main/img/CRUDLibros.jpg)

**Formulario para registrar prestamo**
![RegistrarPrestamo](https://github.com/Azmo23/CRUD_Biblioteca/blob/main/img/FormularioRegistroPrestamo.jpg)


## 🌐 Rutas Principales

### 👥 Módulo de Usuarios
| Ruta                     | Métodos    | Descripción                          | Acceso       |
|--------------------------|------------|--------------------------------------|-------------|
| `/usuarios`              | GET        | Lista todos los usuarios             | Público     |
| `/usuarios/crear`        | GET, POST  | Formulario de creación de usuario    | Admin       |
| `/usuarios/editar/<id>`  | GET, POST  | Editar usuario existente             | Admin       |
| `/usuarios/eliminar/<id>`| POST       | Eliminar usuario (confirmación)      | Admin       |
| `/usuarios/buscar`       | GET        | Búsqueda por nombre/apellido         | Staff       |

### 📚 Módulo de Libros
| Ruta                     | Métodos    | Descripción                          | Acceso       |
|--------------------------|------------|--------------------------------------|-------------|
| `/libros`                | GET        | Catálogo completo de libros          | Público     |
| `/libros/crear`          | GET, POST  | Añadir nuevo libro al sistema        | Bibliotecario |
| `/libros/editar/<id>`    | GET, POST  | Modificar información de libro       | Bibliotecario |
| `/libros/eliminar/<id>`  | POST       | Eliminar libro (validar ejemplares)  | Admin       |
| `/libros/buscar`         | GET        | Búsqueda por título/autor/ISBN       | Público     |

### 🔄 Módulo de Préstamos
| Ruta                          | Métodos    | Descripción                                  | Acceso       |
|-------------------------------|------------|----------------------------------------------|-------------|
| `/prestamos`                  | GET        | Listado de préstamos activos                 | Staff       |
| `/prestamos/crear`            | GET, POST  | Registrar nuevo préstamo                     | Bibliotecario |
| `/prestamos/editar/<id>`      | GET, POST  | Modificar préstamo (extender plazo)          | Bibliotecario |
| `/prestamos/devolver/<id>`     | POST       | Registrar devolución                         | Bibliotecario |
| `/prestamos/historial`        | GET        | Historial completo de préstamos              | Admin       |
| `/prestamos/vencidos`         | GET        | Lista de préstamos vencidos                  | Staff       |

### 🗓️ Módulo de Reservas
| Ruta                          | Métodos    | Descripción                                  | Acceso       |
|-------------------------------|------------|----------------------------------------------|-------------|
| `/reservas`                   | GET        | Reservas activas                             | Staff       |
| `/reservas/crear`             | GET, POST  | Crear nueva reserva                          | Usuarios    |
| `/reservas/cancelar/<id>`     | POST       | Cancelar reserva                             | Usuarios/Staff |
| `/reservas/historial`         | GET        | Historial de reservas                        | Staff       |

### 🏠 Rutas Generales
| Ruta             | Métodos    | Descripción                          |
|------------------|------------|--------------------------------------|
| `/`              | GET        | Página de inicio/dashboard           |


## 🛠 Configurar MongoDB

Edita directamente en `app.py`:

```python
  mongo = PyMongo(app, uri="mongodb://localhost:27017/biblioteca")
```

## 👨‍🔧Soporte.
  Hecho por: Simón Alzate Velasquez.
  
  Email: liluzikb@gmail.com.










