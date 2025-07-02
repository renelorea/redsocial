import mysql.connector
from mysql.connector import Error

def validar_query():
    conexion = mysql.connector.connect(
         host='localhost',
            user='usercon',
            password='Admin2025',
            database='redsocial'
    )

    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM personas WHERE edad > 30")  # Ajusta tu consulta

    resultados = cursor.fetchall()

    if resultados:
        print(f"✅ Se encontraron {len(resultados)} registros.")
        for fila in resultados:
            print(fila)
    else:
        print("❌ La consulta no devolvió ningún resultado.")

    cursor.close()
    conexion.close()
    
validar_query()