DROP TABLE personas;
DROP TABLE cosas_en_comun;
DROP TABLE publicaciones;


CREATE TABLE personas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    edad INTEGER,
    ciudad TEXT
);

CREATE TABLE cosas_en_comun (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    persona1_id INTEGER,
    persona2_id INTEGER,
    interes TEXT
);

CREATE TABLE publicaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_autor INTEGER,
    contenido TEXT,
    fecha TEXT
);
