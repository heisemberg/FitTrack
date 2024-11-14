instructions = [
    'SET FOREIGN_KEY_CHECKS=0;',
    'DROP TABLE IF EXISTS todo;',
    'DROP TABLE IF EXISTS usuario;',
    'SET FOREIGN_KEY_CHECKS=1;',
    """
    CREATE TABLE usuario (
        id INT PRIMARY KEY AUTO_INCREMENT,
        usuario VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(255) UNIQUE NOT NULL,
        nombres VARCHAR(150) NOT NULL,
        apellidos VARCHAR(150) NOT NULL,
        fecha_nacimiento DATE NOT NULL,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE perfil_usuario (
        id INT PRIMARY KEY AUTO_INCREMENT,
        usuario_id INT,
        sexo TEXT CHECK (sexo IN ('M', 'F')) NOT NULL,
        peso_inicial FLOAT NOT NULL,
        estatura FLOAT NOT NULL,
        objetivo TEXT CHECK (objetivo IN ('subir', 'bajar', 'mantener')) NOT NULL,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuario(id)
    );
    """,
    """
    CREATE TABLE medidas (
        id INT PRIMARY KEY AUTO_INCREMENT,
        usuario_id INT,
        fecha_medicion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        peso FLOAT NOT NULL,
        cintura FLOAT,
        pecho FLOAT,
        cadera FLOAT,
        brazo FLOAT,
        pierna FLOAT,
        FOREIGN KEY (usuario_id) REFERENCES usuario(id)
    );
    """
]