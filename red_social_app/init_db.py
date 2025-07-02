import sqlite3

conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()

with open('schemas.sql') as f:
    c.executescript(f.read())
    
c.executescript("DELETE FROM personas")
conn.commit()
c.executescript("DELETE FROM cosas_en_comun")
conn.commit()
c.executescript("DELETE FROM publicaciones")
conn.commit()

# Datos de ejemplo
personas = [
    ("Ana", 25, "CDMX"), ("Luis", 30, "CDMX"), ("Sofía", 28, "CDMX"),
    ("Carlos", 35, "CDMX"), ("Elena", 22, "CDMX"), ("Diego", 27, "CDMX"),
    ("Valeria", 29, "CDMX")
]
c.executemany("INSERT INTO personas (nombre, edad, ciudad) VALUES (?, ?, ?)", personas)

cosas = [
    (1, 2, "fútbol"), (1, 3, "fútbol"), (2, 4, "música"),
    (3, 4, "viajes"), (5, 6, "anime"), (6, 7, "videojuegos"),
    (1, 7, "lectura")
]
c.executemany("INSERT INTO cosas_en_comun (persona1_id, persona2_id, interes) VALUES (?, ?, ?)", cosas)

publicaciones = [
    (1, "¡Me encanta el cine!", "2025-06-01"),
    (3, "¿Quién quiere viajar a Oaxaca?", "2025-06-05"),
    (6, "Nuevo torneo de videojuegos 🎮", "2025-06-10"),
    (7, "Recomiendo este libro 📚", "2025-06-12")
]
c.executemany("INSERT INTO publicaciones (id_autor, contenido, fecha) VALUES (?, ?, ?)", publicaciones)

conn.commit()
conn.close()
