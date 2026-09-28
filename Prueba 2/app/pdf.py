from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

#Esto tambien, nunca habia autogenerado un archivo pdf, por lo que tambien es en gran parte uso de IA

def generar_pdf(fecha, precios):
    nombre_archivo = f"datos/pdfs/precio_pvpc_{fecha}.pdf"

    documento = SimpleDocTemplate(
        nombre_archivo,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    estilos = getSampleStyleSheet()

    elementos = []

    titulo = Paragraph(
        "Precio de la electricidad - PVPC",
        estilos["Title"]
    )

    elementos.append(titulo)

    fecha_texto = Paragraph(
        f"Fecha: {fecha}",
        estilos["Normal"]
    )

    elementos.append(fecha_texto)

    datos_tabla = [["Hora", "Precio (€/MWh)"]]

    for precio in precios:
        hora = precio["datetime"][11:16]
        valor = precio["value"]

        datos_tabla.append([
            hora,
            f"{valor:.2f}"
        ])

    tabla = Table(datos_tabla)

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))

    elementos.append(tabla)

    generar_grafico(precios)
    grafica = Image("datos/pdfs/grafica/grafica.png", width=500, height=200)

    elementos.append(grafica)
    documento.build(elementos)

    return nombre_archivo

def generar_grafico(precios):
    x = (list(range(24)))
    y = []
    for precio in precios:
        y.append(precio["value"])

    plt.plot(x, y)
    plt.savefig("datos/pdfs/grafica/grafica.png")
    plt.close()  
    
