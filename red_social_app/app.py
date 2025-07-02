from flask import Flask, render_template,jsonify,request, redirect, session, flash, get_flashed_messages

import networkx as nx
import matplotlib.pyplot as plt
import mysql.connector
from datetime import date
from mysql.connector import Error
import heapq
from collections import deque

def probar_conexion():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='usercon',
            password='Admin2025',
            database='redsocial'
        )
        if conexion.is_connected():
            print("✅ Conexión exitosa a la base de datos")
            print("Base de datos:", conexion.database)
    except Error as e:
        print("❌ Error al conectar:", e)
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            conexion.close()
            print("🔌 Conexión cerrada")

probar_conexion()

app = Flask(__name__)

plt.switch_backend('Agg') 



def construir_grafo_desde_bd():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, nombre FROM personas")
    nombres = dict(cursor.fetchall())

    cursor.execute("SELECT persona1_id, persona2_id, peso FROM cosas_en_comun")
    relaciones = cursor.fetchall()
    conn.close()

    G = nx.Graph()
    for p1, p2, peso in relaciones:
        G.add_edge(p1, p2, weight=peso)

    return G, nombres


def dfs_recorrido(grafo, origen):
    return list(nx.dfs_preorder_nodes(grafo, source=origen))




def dijkstra(grafo, inicio):
    dist = {nodo: float('inf') for nodo in grafo}
    dist[inicio] = 0
    cola = [(0, inicio)]

    while cola:
        actual_dist, actual_nodo = heapq.heappop(cola)

        for vecino, peso in grafo[actual_nodo]:
            nueva_dist = actual_dist + peso
            if nueva_dist < dist[vecino]:
                dist[vecino] = nueva_dist
                heapq.heappush(cola, (nueva_dist, vecino))

    return dist



def bfs(grafo, inicio):
    visitado = set()
    cola = deque([inicio])
    
    while cola:
        nodo = cola.popleft()
        if nodo not in visitado:
            print(f"🔍 Visitando: {nodo}")
            visitado.add(nodo)
            cola.extend([vecino for vecino in grafo[nodo] if vecino not in visitado])
            
def dfs(grafo, nodo, visitado=None):
    if visitado is None:
        visitado = set()
    print(f"🔍 Visitando: {nodo}")
    visitado.add(nodo)
    for vecino in grafo[nodo]:
        if vecino not in visitado:
            dfs(grafo, vecino, visitado)



def get_db():
    conn = mysql.connector.connect(
        host='localhost',
        user='usercon',
        password='Admin2025',
        database='redsocial'
    )
    return conn

@app.route('/comparador')
def comparador():
    return render_template('comparador.html')


@app.route('/bfs/<int:origen>')
def ejecutar_bfs(origen):
    G, nombres = construir_grafo_desde_bd()
    recorrido = list(nx.dfs_preorder_nodes(G, source=origen))
    return jsonify({"recorrido": recorrido, "nombres": nombres})


@app.route('/bfs')
def ver_bfs():
    return render_template('bfs.html')

@app.route('/dfs')
def ver_dfs():
    return render_template('dfs.html')

@app.route('/dijkstra/<int:origen>/<int:destino>')
def ejecutar_dijkstra(origen, destino):
    G, nombres = construir_grafo_desde_bd()
    try:
        camino = nx.dijkstra_path(G, source=origen, target=destino, weight='weight')
        distancia_total = nx.dijkstra_path_length(G, source=origen, target=destino, weight='weight')
        return jsonify({
            "camino": camino,
            "nombres": nombres,
            "costo": distancia_total
        })
    except nx.NetworkXNoPath:
        return jsonify({"error": "🚫 No hay camino entre esos nodos"}), 404

@app.route('/dijkstra')
def ver_dijkstra():
    return render_template('dijkstra.html')



@app.route('/admin')
def index():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM personas")
    personas = cursor.fetchall()
    if personas:
        print(f"✅ Se encontraron {len(personas)} registros.")
        for fila in personas:
            print(fila)
    cursor.execute("SELECT * FROM publicaciones ORDER BY fecha DESC")
    publicaciones = cursor.fetchall()
    if publicaciones:
        print(f"✅ Se encontraron {len(publicaciones)} registros.")
    return render_template('index.html', personas=personas, publicaciones=publicaciones)

@app.route('/updatecomun')
def updatecomun():
    lista=[]
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT p.id,p.id_autor,l.id_usuario, COUNT(l.id) as peso FROM publicaciones p, likes l where p.id=l.publicacion_id group by 1 "+
                   " UNION ALL "+
                   "SELECT p.id,p.id_autor,d.id_usuario, COUNT(d.id) as peso FROM  publicaciones p, dislikes d where p.id=d.publicacion_id group by 1")
    comunes = cursor.fetchall()
    acum=0
    if comunes:
        print(f"✅ Se encontraron {len(comunes)} registros.")
        id=0
        p1=0
        p2=0
        acum=0
        for fila in comunes:
            
            acum+=fila["peso"]
            id=fila["id"]
            p1=fila["id_autor"]
            p2=fila["id_usuario"]
                    
            resultado = buscar_objetos_en_lista(lista,"id",id)

            if resultado:
                numerodatos=actualizar_objetos_en_lista(lista,"id", id, "peso", acum) 
                print(f"valores actualizados: {numerodatos}")
            else:
                print("No se encontró el diccionario.")
                acum=fila["peso"]
                comun=Comun(fila["id"],fila["id_autor"],fila["id_usuario"],acum)
                lista.append(comun)
                    
                    
            
        borrarCosasEnComun()
        for comun in lista:
            print(f"id= {comun.id} id_autor= {comun.idAutor} id_usuario= {comun.idUsuario} peso= {comun.peso}")
            crearCosasEnComun(comun.idAutor,comun.idUsuario,comun.peso)
                  
    return render_template('actualiza.html')

class Comun:
    def __init__(self, id,idAutor,idUsuario,peso):
        self.id=id
        self.idAutor = idAutor
        self.idUsuario=idUsuario
        self.peso=peso

def borrarCosasEnComun():
    conexion = get_db()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM cosas_en_comun")
    conexion.commit()
    conexion.close()

def crearCosasEnComun(idAutor,idUsuario,peso):
    conexion = get_db()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO cosas_en_comun (persona1_id, persona2_id, peso) VALUES (%s, %s, %s)", (idAutor, idUsuario,peso))
    conexion.commit()
    conexion.close()

def buscar_objetos_en_lista(lista, criterio_busqueda, valor_busqueda, buscar_todos=False):
    """
    Busca objetos en una lista basándose en un criterio y un valor.

    Args:
        lista (list): La lista de objetos (instancias de clase o diccionarios).
        criterio_busqueda (str): El nombre del atributo (para objetos) o la clave (para diccionarios) por el cual buscar.
        valor_busqueda: El valor a comparar en el criterio de búsqueda.
        buscar_todos (bool): Si es True, devuelve una lista de todas las coincidencias.
                             Si es False (por defecto), devuelve la primera coincidencia encontrada.

    Returns:
        list o object o None: Si buscar_todos es True, devuelve una lista de objetos que coinciden.
                               Si buscar_todos es False, devuelve el primer objeto que coincide o None si no se encuentra.
    """
    resultados = []
    for item in lista:
        if isinstance(item, dict): # Si el elemento es un diccionario
            if criterio_busqueda in item and item[criterio_busqueda] == valor_busqueda:
                if not buscar_todos:
                    return item
                resultados.append(item)
        else: # Si el elemento es una instancia de una clase
            if hasattr(item, criterio_busqueda) and getattr(item, criterio_busqueda) == valor_busqueda:
                if not buscar_todos:
                    return item
                resultados.append(item)

    return resultados if buscar_todos else None

# --- Función para Actualizar Objetos en una Lista ---

def actualizar_objetos_en_lista(lista, criterio_busqueda, valor_busqueda, atributo_a_actualizar, nuevo_valor, actualizar_todos=False):
    """
    Busca y actualiza objetos en una lista basándose en un criterio.

    Args:
        lista (list): La lista de objetos (instancias de clase o diccionarios).
        criterio_busqueda (str): El nombre del atributo (para objetos) o la clave (para diccionarios) por el cual buscar.
        valor_busqueda: El valor a comparar en el criterio de búsqueda.
        atributo_a_actualizar (str): El nombre del atributo (para objetos) o la clave (para diccionarios) a modificar.
        nuevo_valor: El nuevo valor que se asignará al atributo/clave.
        actualizar_todos (bool): Si es True, actualiza todas las coincidencias.
                                Si es False (por defecto), actualiza solo la primera coincidencia encontrada.

    Returns:
        int: El número de objetos actualizados.
    """
    contador_actualizados = 0
    for item in lista:
        coincide = False
        if isinstance(item, dict):
            if criterio_busqueda in item and item[criterio_busqueda] == valor_busqueda:
                coincide = True
        else:
            if hasattr(item, criterio_busqueda) and getattr(item, criterio_busqueda) == valor_busqueda:
                coincide = True

        if coincide:
            if isinstance(item, dict):
                item[atributo_a_actualizar] = nuevo_valor
            else:
                setattr(item, atributo_a_actualizar, nuevo_valor)
            contador_actualizados += 1
            if not actualizar_todos:
                break # Si solo se debe actualizar el primero

    return contador_actualizados
@app.route('/dfs/<int:origen>')
def ejecutar_dfs(origen):
    G, nombres = construir_grafo_desde_bd()
    recorrido = list(nx.dfs_preorder_nodes(G, source=origen))
    return jsonify({"recorrido": recorrido, "nombres": nombres})

@app.route('/red')
def red():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM personas")
    personas = cursor.fetchall()
    cursor.execute("SELECT * FROM cosas_en_comun")
    enlaces = cursor.fetchall()
    
    if personas:
        print(f"✅ Se encontraron {len(personas)} registros.")
        for fila in personas:
            print(fila)

    G = nx.Graph()
    for p in personas:
        G.add_node(p["id"], label=p["nombre"])
    for e in enlaces:
        G.add_edge(e["persona1_id"], e["persona2_id"], interes=e["interes"])

    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(6, 5))
    nx.draw(G, pos, with_labels=True, labels=nx.get_node_attributes(G, 'label'),
            node_color='skyblue', node_size=800, font_size=10)
    plt.title("Red Social por Intereses")
    plt.savefig("static/red.png")
    plt.close()

    return render_template('red.html', imagen="static/red.png")


@app.route('/agregar_persona', methods=['GET', 'POST'])
def agregar_persona():
    if request.method == 'POST':
        nombre = request.form['nombre']
        edad = request.form['edad']
        ciudad = request.form['ciudad']
        usuario = request.form['usuario']
        password = request.form['password']
        conexion = get_db()
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO personas (nombre, edad,ciudad,usuario,password) VALUES (%s, %s,%s, %s,%s)", (nombre, edad,ciudad,usuario,password))
        conexion.commit()
        conexion.close()
        return redirect('/')
    return render_template('agregar_persona.html')

@app.route('/agregar_publicacion', methods=['GET', 'POST'])
def agregar_publicacion():
    if request.method == 'POST':
        persona_id = request.form['persona_id']
        contenido = request.form['contenido']
        conexion = get_db()
        cursor = conexion.cursor()
        hoy = date.today()
        formateada = hoy.strftime("%Y-%m-%d")
        cursor.execute("INSERT INTO publicaciones (id_autor, contenido,fecha) VALUES (%s, %s, %s)", (persona_id, contenido,formateada))
        conexion.commit()
        conexion.close()
        return redirect('/publicaciones')
    return render_template('agregar_publicacion.html')

@app.route('/publicaciones')
def publicaciones():
    conexion = get_db()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id, p.contenido, p.id_autor, p.fecha,
                (SELECT COUNT(*) FROM likes WHERE publicacion_id = p.id) AS likes,
           (SELECT COUNT(*) FROM dislikes WHERE publicacion_id = p.id) AS dislikes
        FROM publicaciones p
        ORDER BY p.fecha DESC
    """)
    posts = cursor.fetchall()
    if posts:
        print(f"✅ Se encontraron {len(posts)} registros.")
        for fila in posts:
            print(fila)
    conexion.close()
    return render_template('publicaciones.html', publicaciones=posts)

@app.route('/like/<int:publicacion_id>&<int:id_usuario>', methods=['POST'])
def dar_like(publicacion_id,id_usuario):
    conexion = get_db()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO likes (publicacion_id,id_usuario) VALUES (%s,%s)", (publicacion_id,id_usuario))
    conexion.commit()
    cursor.execute("SELECT COUNT(*) FROM likes WHERE publicacion_id = %s", (publicacion_id,))
    total = cursor.fetchone()[0]
    conexion.close()
    return jsonify({"likes": total})

@app.route('/dislike/<int:publicacion_id>&<int:id_usuario>', methods=['POST'])
def dar_dislike(publicacion_id,id_usuario):
    conexion = get_db()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO dislikes (publicacion_id,id_usuario) VALUES (%s,%s)", (publicacion_id,id_usuario))
    conexion.commit()
    cursor.execute("SELECT COUNT(*) FROM dislikes WHERE publicacion_id = %s", (publicacion_id,))
    total = cursor.fetchone()[0]
    conexion.close()
    return jsonify({"dislikes": total})

app.secret_key = 'supersecreto'


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM personas WHERE usuario=%s AND password=%s", (email, password))
        usuario = cursor.fetchone()
        db.close()
        if usuario:
            if usuario['usuario']=="admin":
                return redirect('/admin')
            else:
                session['usuario_id'] = usuario['id']
                session['nombre'] = usuario['nombre']
                return redirect('/publicaciones')
        else:
            # insertar usuario
            flash("¡El usuario no existe o la contraseña es incorrecta!", "warning")
            return redirect('/')
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)", (nombre, email, password))
        db.commit()
        db.close()
        return redirect('/')
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')




if __name__ == '__main__':
    app.run(debug=True)

