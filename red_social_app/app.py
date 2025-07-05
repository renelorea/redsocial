from flask import Flask, render_template,jsonify,request, redirect, session, flash, get_flashed_messages

import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import mysql.connector
from datetime import date
from mysql.connector import Error
import heapq
import os
from collections import deque
from itertools import cycle
import matplotlib.colors as mcolors

# ✅ Prueba de conexión inicial a la base de datos
def probar_conexion():
    try:
        conexion = mysql.connector.connect(
            host='srv563.hstgr.io',
            user='u271403909_rene',
            password='c*EX$3M7F^6',
            database='u271403909_redsocial'
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

# Flask inicial
app = Flask(__name__)
plt.switch_backend('Agg')  # Desactiva GUI de matplotlib (para backend web)

# 🔧 Carga grafo desde la base de datos
def construir_grafo_desde_bd():
    conn = get_db()
    cursor = conn.cursor()

    # Recupera nombres de personas
    cursor.execute("SELECT id, nombre FROM personas")
    nombres = dict(cursor.fetchall())

    # Recupera relaciones y pesos entre personas
    cursor.execute("SELECT persona1_id, persona2_id, peso FROM cosas_en_comun")
    relaciones = cursor.fetchall()
    conn.close()

    G = nx.Graph()
    for p1, p2, peso in relaciones:
        G.add_edge(p1, p2, weight=peso)

    return G, nombres

# Recorrido DFS en preorden
def dfs_recorrido(grafo, origen):
    return list(nx.dfs_preorder_nodes(grafo, source=origen))

# 🔢 Algoritmo de Dijkstra clásico
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

# 🌀 BFS clásico con impresión de recorrido
def bfs(grafo, inicio):
    visitado = set()
    cola = deque([inicio])
    
    while cola:
        nodo = cola.popleft()
        if nodo not in visitado:
            print(f"🔍 Visitando: {nodo}")
            visitado.add(nodo)
            cola.extend([vecino for vecino in grafo[nodo] if vecino not in visitado])

# DFS recursivo simple
def dfs(grafo, nodo, visitado=None):
    if visitado is None:
        visitado = set()
    print(f"🔍 Visitando: {nodo}")
    visitado.add(nodo)
    for vecino in grafo[nodo]:
        if vecino not in visitado:
            dfs(grafo, vecino, visitado)

# 🔄 Crea una conexión DB nueva
def get_db():
    return mysql.connector.connect(
        host='srv563.hstgr.io',
        user='u271403909_rene',
        password='c*EX$3M7F^6',
        database='u271403909_redsocial'
    )

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
    cursor.execute("""
                   SELECT p.id,p.id_autor,l.id_usuario, COUNT(l.id) as peso FROM publicaciones p, interacciones l where p.id=l.publicacion_id group by 1,3 
                   """)
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
    print(f"autor: {idAutor} usuario:{idUsuario} peso: {peso}")
    conexion = get_db()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO cosas_en_comun (persona1_id, persona2_id, peso) VALUES (%s, %s, %s)", (idAutor, idUsuario,peso))
    conexion.commit()
    conexion.close()

# --- FUNCIONES AUXILIARES PARA MANEJO DE LISTAS DE OBJETOS ---

# 🔍 Busca objetos dentro de una lista (diccionarios o instancias) con base en un criterio y valor
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
# ✏️ Actualiza atributos o claves de objetos en una lista según coincidencia
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

# 📍 Ruta para ejecutar DFS desde un nodo específico
@app.route('/dfs/<int:origen>')
def ejecutar_dfs(origen):
    G, nombres = construir_grafo_desde_bd()

    # ⚠️ Validación: si el nodo no existe, retorna error 404
    if origen not in G:
        return jsonify({"error": f"🚫 El nodo {origen} no existe en el grafo"}), 404

    recorrido = list(nx.dfs_preorder_nodes(G, source=origen))

    # ⚠️ Si el recorrido está vacío, se notifica al cliente
    if not recorrido:
        return jsonify({"error": "⚠️ No se encontró ningún recorrido DFS desde este nodo"}), 404

    return jsonify({"recorrido": recorrido, "nombres": nombres})

# 📊 Ruta para construir y mostrar visualmente el grafo como una red

# ➕ Ruta para agregar una nueva persona al sistema
@app.route('/agregar_persona', methods=['GET', 'POST'])
def agregar_persona():
    if request.method == 'POST':
        # 📝 Recolecta datos del formulario
        nombre = request.form['nombre']
        edad = request.form['edad']
        ciudad = request.form['ciudad']
        usuario = request.form['usuario']
        password = request.form['password']

        # 📥 Inserta en la base de datos
        conexion = get_db()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO personas (nombre, edad, ciudad, usuario, password) VALUES (%s, %s, %s, %s, %s)",
            (nombre, edad, ciudad, usuario, password)
        )
        conexion.commit()
        conexion.close()
        return redirect('/')
    return render_template('agregar_persona.html')

@app.route('/red')
def red():
    import networkx as nx
    import plotly.graph_objects as go
    import os
    from itertools import cycle
    from flask import redirect, url_for

    # 🎨 Paleta compatible con Plotly
    css_colors = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
        '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
        '#bcbd22', '#17becf'
    ]
    paleta = cycle(css_colors)

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # 🔄 Datos desde la base
    cursor.execute("SELECT * FROM personas")
    personas = cursor.fetchall()
    cursor.execute("SELECT * FROM cosas_en_comun")
    enlaces = cursor.fetchall()

    # 🧠 Construcción del grafo
    G = nx.Graph()
    for p in personas:
        G.add_node(p["id"], label=p["nombre"])
    for e in enlaces:
        G.add_edge(e["persona1_id"], e["persona2_id"], peso=e["peso"])

    # 📍 Posiciones
    pos = nx.spring_layout(G, seed=42)

    # 🔷 Aristas
    edge_x, edge_y = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        mode='lines',
        hoverinfo='none'
    )

    # 🧩 Comunidades
    comunidades = list(nx.connected_components(G))
    colores = {}
    for color, grupo in zip(paleta, comunidades):
        for nodo in grupo:
            colores[nodo] = color

    # 🔝 Nodos con tamaño proporcional al grado
    nodos_coloreados = []
    for color in set(colores.values()):
        nodos = [n for n in G.nodes() if colores[n] == color]
        x, y = zip(*[pos[n] for n in nodos])
        texto = [G.nodes[n]["label"] for n in nodos]
        grados = [G.degree[n] for n in nodos]  # Tamaño dinámico

        nodos_coloreados.append(go.Scatter(
            x=x, y=y,
            mode='markers+text',
            marker=dict(
                size=[8 + g * 4 for g in grados],  # Personaliza el escalado
                color=color,
                line=dict(width=1, color='black')
            ),
            text=texto,
            textposition='top center',
            hoverinfo='text'
        ))

    # 📊 Figura final
    fig = go.Figure(data=[edge_trace] + nodos_coloreados)
    fig.update_layout(
        title='Red Social por Intereses (Tamaño ∝ Conectividad)',
        showlegend=False,
        hovermode='closest',
        margin=dict(l=20, r=20, t=40, b=20)
    )

    # 💾 HTML interactivo
    html_path = os.path.join('static', 'red_interactiva.html')
    fig.write_html(html_path)

    return redirect(url_for('static', filename='red_interactiva.html'))


# 📝 Ruta para agregar una nueva publicación
@app.route('/agregar_publicacion', methods=['GET', 'POST'])
def agregar_publicacion():
    if request.method == 'POST':
        persona_id = request.form['persona_id']
        contenido = request.form['contenido']
        hoy = date.today()
        formateada = hoy.strftime("%Y-%m-%d")

        conexion = get_db()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO publicaciones (id_autor, contenido, fecha) VALUES (%s, %s, %s)",
            (persona_id, contenido, formateada)
        )
        conexion.commit()
        conexion.close()
        return redirect('/publicaciones')
    return render_template('agregar_publicacion.html')

# 📄 Ruta para ver todas las publicaciones
@app.route('/publicaciones')
def publicaciones():
    conexion = get_db()
    cursor = conexion.cursor(dictionary=True)

    # 📥 Consulta publicaciones con nombre del autor + conteo de likes y dislikes
    cursor.execute("""
        SELECT p.id, p.contenido, p.id_autor, per.nombre AS autor, p.fecha,
               (SELECT COUNT(*) FROM interacciones WHERE publicacion_id = p.id and tipo=1) AS likes,
               (SELECT COUNT(*) FROM interacciones WHERE publicacion_id = p.id and tipo=2) AS dislikes
        FROM publicaciones p
        JOIN personas per ON p.id_autor = per.id
        ORDER BY p.fecha DESC
    """)
    posts = cursor.fetchall()

    # ✅ Impresión para depuración (opcional)
    if posts:
        print(f"✅ Se encontraron {len(posts)} publicaciones.")
        for fila in posts:
            print(f"{fila['autor']}: {fila['contenido']}")

    conexion.close()
    return render_template('publicaciones.html', publicaciones=posts)

# 👍 Ruta para registrar un "like" desde un usuario a una publicación
@app.route('/like/<int:publicacion_id>&<int:id_usuario>', methods=['POST'])
def dar_like(publicacion_id, id_usuario):
    conexion = get_db()
    cursor = conexion.cursor()
    l=1
    d=2

    # 🔘 Inserta registro en tabla "likes"
    cursor.execute("INSERT INTO interacciones (publicacion_id, id_usuario,tipo) VALUES (%s, %s, %s)", (publicacion_id, id_usuario, l))
    conexion.commit()

    # 🔢 Obtiene nuevo total de likes para esa publicación
    cursor.execute("SELECT COUNT(*) FROM interacciones WHERE publicacion_id = %s", (publicacion_id,))
    total = cursor.fetchone()[0]
    conexion.close()

    return jsonify({"likes": total})


# 👎 Ruta para registrar un "dislike" desde un usuario a una publicación
@app.route('/dislike/<int:publicacion_id>&<int:id_usuario>', methods=['POST'])
def dar_dislike(publicacion_id, id_usuario):
    conexion = get_db()
    cursor = conexion.cursor()
    d=2

    # 🔘 Inserta registro en tabla "dislikes"
    cursor.execute("INSERT INTO interacciones (publicacion_id, id_usuario,tipo) VALUES (%s, %s, %s)", (publicacion_id, id_usuario, d))
    conexion.commit()

    # 🔢 Obtiene nuevo total de dislikes para esa publicación
    cursor.execute("SELECT COUNT(*) FROM interacciones WHERE publicacion_id = %s", (publicacion_id,))
    total = cursor.fetchone()[0]
    conexion.close()

    return jsonify({"dislikes": total})

app.secret_key = 'supersecreto'


# 🔐 Ruta principal para iniciar sesión
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # 🔍 Verifica usuario en la base de datos
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM personas WHERE usuario=%s AND password=%s", (email, password))
        usuario = cursor.fetchone()
        db.close()

        if usuario:
            if usuario['usuario'] == "admin":
                return redirect('/admin')  # Redirección especial para admin
            else:
                # 🧠 Se guarda sesión de usuario normal
                session['usuario_id'] = usuario['id']
                session['nombre'] = usuario['nombre']
                return redirect('/publicaciones')
        else:
            # ⚠️ Usuario no encontrado: muestra mensaje de advertencia
            flash("¡El usuario no existe o la contraseña es incorrecta!", "warning")
            return redirect('/')

    return render_template('login.html')


# 🧾 Ruta para registrar un nuevo usuario (registro)
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']

        # 📥 Inserta nuevo usuario en la tabla "usuarios"
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)", (nombre, email, password))
        db.commit()
        db.close()

        return redirect('/')
    return render_template('registro.html')

# 🔓 Ruta para cerrar sesión del usuario
@app.route('/logout')
def logout():
    session.clear()  # 🧹 Limpia la sesión del usuario actual
    return redirect('/')




if __name__ == '__main__':
    app.run(debug=True)

