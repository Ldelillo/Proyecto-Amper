#En general a lo largo de la carrera no he realizado interfaces por lo que esto es en gran parte uso de IA
from flask import Flask, render_template, request

from precio import (
    crear_base_datos,
    comprobar_fecha,
    leer_precios,
    obtener_precios,
    guardar_precios,
    min_max
)

app = Flask(__name__)

if not crear_base_datos():
    raise SystemExit("No se ha podido inicializar la base de datos.")


@app.route("/", methods=["GET", "POST"])
def inicio():
    precios = []
    fecha = None

    if request.method == "POST":
        fecha = request.form["fecha"]

        if comprobar_fecha(fecha):
            precios = leer_precios(fecha)
        else:
            precios = obtener_precios(fecha)

            if precios:
                guardar_precios(precios)

    minimo, maximo = min_max()

    return render_template(
        "index.html",
        precios=precios,
        fecha=fecha,
        minimo=minimo,
        maximo=maximo
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)