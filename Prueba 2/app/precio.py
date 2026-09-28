import requests
from datetime import date, timedelta
import sqlite3

#Obtener precios
def obtener_precios(fecha):
    url = "https://apidatos.ree.es/es/datos/mercados/precios-mercados-tiempo-real" #https://www.ree.es/es/datos/apidatos pagina API's

    parametros = {
        "start_date": f"{fecha}T00:00",
        "end_date": f"{fecha}T23:59",
        "time_trunc": "hour",
        "geo_trunc": "electric_system",
        "geo_limit": "peninsular",
        "geo_ids": "8741"
    }

    respuesta = requests.get(url, params=parametros)

    if(respuesta.status_code != 200):
        print("Error en la consulta:", respuesta.status_code)
        return []

    datos = respuesta.json()
    valores = datos["included"][0]["attributes"]["values"]

    return valores

def ultimos_dias():
    hoy = date.today()

    fechas = []

    for i in range(7):
        fecha = hoy - timedelta(days=i)
        fechas.append(fecha.strftime("%Y-%m-%d"))

    return fechas

def cargar_ultimos_7_dias():
    fechas = ultimos_dias()

    precios = []

    for fecha in fechas:

        if comprobar_fecha(fecha):
            datos = leer_precios(fecha)

        else:
            datos = obtener_precios(fecha)

            if datos:
                guardar_precios(datos)
                datos = leer_precios(fecha)

        precios.extend(datos)

    return precios

def min_max(): 
    precios = cargar_ultimos_7_dias()

    precios_ordenados = sorted(precios, key=lambda x: x["value"])
    #Puede ser 1 unidad o un rango, ya que en el enunciado ponia minimos y maximos
    menores = precios_ordenados[:1] 
    mayores = precios_ordenados[-1:]

    return menores, mayores

#Creacion y actualizacion bbdd
def crear_base_datos(): #No implemento una funcion para borrar la base de datos por tiempo
    try:
        conexion = sqlite3.connect("datos/precios.db")
        cursor = conexion.cursor()

        cursor.execute("""CREATE TABLE IF NOT EXISTS precios (
                        fecha_hora TEXT PRIMARY KEY,
                        precio REAL NOT NULL)""")

        conexion.commit()
        conexion.close()
        return True
    
    except sqlite3.Error as error:
        print("Error al crear la base de datos:", error)
        return False


def guardar_precios(precios):
    if not precios:
        print("No hay precios para guardar.")
        return False
    try:
        conexion = sqlite3.connect("datos/precios.db")
        cursor = conexion.cursor()

        for precio in precios:
            cursor.execute("""INSERT INTO precios (fecha_hora, precio)
                            VALUES (?, ?)""", (precio["datetime"], precio["value"]))

        conexion.commit()
        conexion.close()

        return True

    except sqlite3.Error as error:
        print("Error al guardar los precios:", error)
        return False


def comprobar_fecha(fecha):
    try:
        conexion = sqlite3.connect("datos/precios.db")
        cursor = conexion.cursor()

        cursor.execute("""SELECT COUNT(*)
                        FROM precios
                        WHERE fecha_hora LIKE ?""", (f"{fecha}%",))

        cantidad = cursor.fetchone()[0]

        conexion.close()

        return cantidad > 0 #Asumimos que si se ha guardado 1 hora minimo de ese dia tenemos toda la informacion que nos puede dar la API

    except sqlite3.Error as error:
        print("Error al comprobar la fecha:", error)
        return False


def leer_precios(fecha):
    try:
        conexion = sqlite3.connect("datos/precios.db")
        cursor = conexion.cursor()

        cursor.execute("""SELECT fecha_hora, precio
                        FROM precios
                        WHERE fecha_hora LIKE ?
                        ORDER BY fecha_hora""", (f"{fecha}%",))

        resultados = cursor.fetchall()

        conexion.close()

        precios = []

        for resultado in resultados: #Lo convierto al mismo formato que la lectura de API para simplificar luego todo
            precios.append({
                "datetime": resultado[0],
                "value": resultado[1]
            }) 

        return precios

    except sqlite3.Error as error:
        print("Error al leer los precios:", error)
        return []
