
# 🏛️ Sistema de Gestión Bibliotecaria

![Captura de pantalla](/img/bibliotecaSQL.jpg)

## 📌 Tabla de Contenidos
- [Descripción](#-descripción)
- [Características](#-características)
- [Tecnologías](#-tecnologías)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Estructura](#-estructura-del-proyecto)
- [Uso](#-uso)
- [Endpoints](#-endpoints)
- [Licencia](#-licencia)
- [Contribuciones](#-contribuciones)
- [Contacto](#-contacto)

## 🌟 Descripción

Sistema completo de gestión para bibliotecas desarrollado con:

- **Backend**: Python Flask
- **Base de datos**: MariaDB/MySQL
- **Frontend**: Bootstrap 5 + CSS personalizado
- **Interfaz**: Diseño responsive con tema morado

## ✨ Características

### 📚 Gestión de Libros
- Registro completo con ISBN único
- Control de ejemplares disponibles
- Categorización de materiales

### 👥 Gestión de Usuarios
- Registro con todos los datos personales
- Validación de campos obligatorios
- Historial de préstamos

### 🔄 Sistema de Préstamos
- Asignación automática de fechas (7 días)
- Estados: Pendiente/Devuelto/Atrasado
- Control de disponibilidad

### 📅 Sistema de Reservas
- Reservación por usuario
- Fechas personalizables
- Integración con préstamos

## 💻 Tecnologías

| Componente       | Tecnología          | Versión   |
|------------------|---------------------|-----------|
| Lenguaje         | Python              | 3.9+      |
| Framework Web    | Flask               | 2.0.1     |
| Base de Datos    | MariaDB/MySQL       | 10.6+     |
| Frontend         | Bootstrap           | 5.1.3     |
| Íconos           | Bootstrap Icons     | 1.8.0     |

## ⚡ Instalación

1. **Clonar repositorio**:
```bash
git clone https://github.com/tu-usuario/biblioteca-flask.git
cd biblioteca-flask
```

2. **Crear un entorno visual (recomendado)**:
```bash
python -m very venv
source venv/bin/activate # Linux/Mac
.\venv\Scripts\activate # Windows
```

3. **Instalar dependencias**:
```bash
pip install flask flask-mysqldb
```
## 🔧 Configuración

1.**Configurar la base de datos:**
```Sql
CREATE DATABASE biblioteca;
USE biblioteca;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    direccion VARCHAR(200) NOT NULL,
    fechaNacimiento DATE NOT NULL
);

-- Ejecutar resto de CREATE TABLE desde app.py
```

2.**Configurar conexión en `app.py`**
```python
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'tu_usuario'
app.config['MYSQL_PASSWORD'] = 'tu_contraseña'
app.config['MYSQL_DB'] = 'biblioteca'
app.config['SECRET_KEY'] = 'tu-clave-secreta'
```

3.**Iniciar Aplicación**:
```bash
python app.py
```

## 📂 Estructura del Proyeto

```
biblioteca-flask/
├── app.py                # Aplicación principal
├── static/               # CSS/JS personalizados
└── templates/            # Plantillas HTML
    ├── base.html         # Layout principal
    ├── index.html        # Dashboard
    ├── usuarios/         # CRUD usuarios
    │   ├── index.html
    │   ├── agregar.html
    │   └── editar.html
    ├── libros/           # CRUD libros
    │   ├── index.html
    │   ├── agregar.html
    │   └── editar.html
    ├── prestamos/        # Gestión préstamos
    │   ├── index.html
    │   ├── agregar.html
    │   └── editar.html
    └── reservas/         # Gestión reservas
        ├── index.html
        ├── agregar.html
        └── editar.html
```

## 💻 Uso

1. **Acceder al sistema**:
```
http://localhost:5000
```
2. **Credenciales iniciales**
- Crear primer usuario desde /usuario/agregar
- Registrar libros disponibles

3. **Funcionalidades clave**
- Préstamos automáticos con devolución en 7 días.
- Control de inventario en tiempo real.
- Reservas integradas con el catálogo

## 🌐Endpoints Principales


## 🌐 Endpoints API


| Módulo       | Endpoint                | Método   | Descripción                              | Parámetros (POST)                          |
|--------------|-------------------------|----------|------------------------------------------|--------------------------------------------|
| **Usuarios** | `/usuarios`             | `GET`    | Obtener listado de todos los usuarios    | -                                          |
|              | `/usuarios/agregar`     | `POST`   | Crear nuevo usuario                      | `nombre`, `apellido`, `email`, `direccion`, `fechaNacimiento` |
|              | `/usuarios/editar/<id>` | `PUT`    | Actualizar usuario existente             | Campos opcionales a actualizar             |
|              | `/usuarios/eliminar/<id>` | `DELETE` | Eliminar usuario                       | -                                          |
| **Libros**   | `/libros`               | `GET`    | Obtener listado completo de libros       | -                                          |
|              | `/libros/agregar`       | `POST`   | Agregar nuevo libro al catálogo          | `titulo`, `autor`, `isbn`, `categoria`, `ejemplares` |
|              | `/libros/editar/<id>`   | `PUT`    | Actualizar información de libro          | Campos opcionales a actualizar             |
|              | `/libros/eliminar/<id>` | `DELETE` | Eliminar libro del sistema               | -                                          |
| **Préstamos**| `/prestamos`            | `GET`    | Listar todos los préstamos activos       | -                                          |
|              | `/prestamos/agregar`    | `POST`   | Registrar nuevo préstamo                 | `usuario_id`, `libro_id`, `fechaPrestamo`  |
|              | `/prestamos/devolver/<id>` | `PUT` | Marcar préstamo como devuelto           | -                                          |
|              | `/prestamos/usuario/<id>` | `GET`  | Obtener préstamos por usuario           | -                                          |
| **Reservas** | `/reservas`             | `GET`    | Listar todas las reservas activas        | -                                          |
|              | `/reservas/agregar`     | `POST`   | Crear nueva reserva                      | `usuario_id`, `libro_id`, `fechaReserva`   |
|              | `/reservas/cancelar/<id>` | `DELETE` | Cancelar reserva                       | -                                          |
|              | `/reservas/libro/<id>`  | `GET`    | Obtener reservas por libro               | -                                          |

## 🤝Contribuciones

Sigue estos pasos:

- Has un fork al proyecto.
- Crea tu rama feature (`git checkout -b feature/NuevaFuncionalidad`)
- Has un commit de tus cambios (`git commit -m 'Agrega NuevaFuncionalidad`)
- Has push a la rama (`git push origin feature/NuevaFuncionalidad`)
- Abre el Pull Request.

## 📲 Contacto

Para soporte o consultas:

- Email: liluzikb@gmail.com