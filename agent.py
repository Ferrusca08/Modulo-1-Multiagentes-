# Experimentos para analizar como se comportan los robots de limpieza
# cuando vamos cambiando la cantidad de agentes.
# Basicamente corremos la simulacion muchas veces con distintas
# configuraciones y guardamos los resultados en CSV para despues
# generar las graficas del informe.
# Tenemos tres experimentos:
#   A: con tiempo de sobra, para ver cuanto tardan en limpiar todo.
#   B: con poco tiempo, para ver que porcentaje logran limpiar.
#   C: barrido fino de 1 a 30 agentes, para mostrar como las corridas
#      individuales oscilan bastante comparadas con el promedio.
# Autores: Emiliano Diaz Ferrusca (A01748498)
#          Santiago Hernandez Acevedo (A01754509)
# Fecha de creacion: 11 de noviembre de 2026
# Fecha de modificacion: 16 de noviembre de 2026

import os

import matplotlib.pyplot as plt
import pandas as pd

from model import Habitacion

ANCHO = 20
ALTO = 20
PORCENTAJE_SUCIAS = 40
CANTIDADES_AGENTES = [1, 2, 5, 10, 20, 50, 100]
CANTIDADES_BARRIDO = list(range(1, 31))
REPETICIONES = 30
CORRIDAS_INDIVIDUALES = [0, 1, 2]
TIEMPO_MAXIMO_HOLGADO = 30000
TIEMPO_MAXIMO_CORTO = 200
CARPETA_RESULTADOS = "resultados"
COLOR = "#2a6f97"
COLORES_CORRIDAS = ["#e07a5f", "#81b29a", "#b08bbf"]


# Corre 30 simulaciones por cada cantidad de agentes que le pasemos.
# Parametros:
#   tiempoMaximo: limite de pasos para cada simulacion.
#   cantidades: lista con las cantidades de agentes a probar.
# Regresa: un DataFrame con una fila por simulacion y sus datos.
def correrExperimento(tiempoMaximo, cantidades):
	filas = []
	for numAgentes in cantidades:
		for repeticion in range(REPETICIONES):
			modelo = Habitacion(
				ANCHO, ALTO, numAgentes, PORCENTAJE_SUCIAS, tiempoMaximo,
				semilla = repeticion
			)
			resultado = modelo.ejecutar()
			resultado["agentes"] = numAgentes
			resultado["repeticion"] = repeticion
			filas.append(resultado)
	return pd.DataFrame(filas)


# Saca promedios y desviaciones estandar agrupados por cantidad
# de agentes. Asi podemos comparar las configuraciones.
# Parametros:
#   datos: el DataFrame que sale de correrExperimento.
# Regresa: un DataFrame resumen indexado por numero de agentes.
def resumir(datos):
	return datos.groupby("agentes").agg(
		tiempoMedio = ("tiempo", "mean"),
		tiempoDesv = ("tiempo", "std"),
		limpiasMedio = ("porcentajeLimpias", "mean"),
		limpiasDesv = ("porcentajeLimpias", "std"),
		movimientosMedio = ("movimientos", "mean"),
		movimientosDesv = ("movimientos", "std"),
		completas = ("limpiezaCompleta", "sum"),
	)


# Arma la ruta completa de un archivo en la carpeta de resultados.
# Parametros:
#   archivo: nombre del archivo.
# Regresa: la ruta completa.
def obtenerRuta(archivo):
	return os.path.join(CARPETA_RESULTADOS, archivo)


# Le pone etiquetas y formato bonito a una grafica.
# Parametros:
#   eje: los ejes de matplotlib.
#   etiqueta: lo que va en el eje Y.
#   titulo: titulo de la grafica.
# Regresa: nada.
def darFormato(eje, etiqueta, titulo):
	eje.set_xlabel("Numero de agentes")
	eje.set_ylabel(etiqueta)
	eje.set_title(titulo)
	eje.grid(True, which = "major", alpha = 0.3)
	for lado in ["top", "right"]:
		eje.spines[lado].set_visible(False)


# Genera una grafica con barras de error mostrando una metrica
# contra el numero de agentes.
# Parametros:
#   resumen: DataFrame que sale de resumir.
#   columna: la columna con el promedio.
#   desviacion: la columna con la desviacion estandar.
#   etiqueta: texto para el eje Y.
#   titulo: titulo de la grafica.
#   archivo: nombre del PNG que se guarda.
#   esLogaritmica: si el eje Y va en escala logaritmica.
# Regresa: nada.
def graficar(
	resumen, columna, desviacion, etiqueta, titulo, archivo, esLogaritmica
):
	figura, eje = plt.subplots(figsize = (6.5, 3.8))
	eje.errorbar(
		resumen.index, resumen[columna], yerr = resumen[desviacion],
		marker = "o", color = COLOR, capsize = 3, linewidth = 1.8
	)
	eje.set_xscale("log")
	if esLogaritmica:
		eje.set_yscale("log")
	eje.set_xticks(CANTIDADES_AGENTES)
	eje.set_xticklabels(CANTIDADES_AGENTES)
	darFormato(eje, etiqueta, titulo)
	figura.tight_layout()
	figura.savefig(obtenerRuta(archivo), dpi = 200)
	plt.close(figura)


# Grafica corridas individuales vs el promedio para que se vea
# como oscilan. Sirve para el analisis del comportamiento caotico.
# Parametros:
#   datos: DataFrame del barrido fino.
#   columna: que metrica graficar.
#   etiqueta: texto para el eje Y.
#   titulo: titulo de la grafica.
#   archivo: nombre del PNG de salida.
# Regresa: nada.
def graficarOscilacion(datos, columna, etiqueta, titulo, archivo):
	figura, eje = plt.subplots(figsize = (6.5, 3.8))
	for repeticion, color in zip(CORRIDAS_INDIVIDUALES, COLORES_CORRIDAS):
		corrida = datos[datos["repeticion"] == repeticion]
		eje.plot(
			corrida["agentes"], corrida[columna], color = color,
			linewidth = 1, marker = ".",
			label = f"Corrida individual (semilla {repeticion})"
		)
	promedio = datos.groupby("agentes")[columna].mean()
	eje.plot(
		promedio.index, promedio, color = COLOR, linewidth = 2.4,
		label = f"Promedio de {REPETICIONES} corridas"
	)
	eje.set_yscale("log")
	eje.legend(fontsize = 8, frameon = False)
	darFormato(eje, etiqueta, titulo)
	figura.tight_layout()
	figura.savefig(obtenerRuta(archivo), dpi = 200)
	plt.close(figura)


# Corre un experimento completo y guarda tanto los datos crudos
# como el resumen en archivos CSV.
# Parametros:
#   nombre: letra del experimento (a o b).
#   tiempoMaximo: limite de pasos.
# Regresa: el DataFrame de resumen.
def correrYGuardar(nombre, tiempoMaximo):
	datos = correrExperimento(tiempoMaximo, CANTIDADES_AGENTES)
	resumen = resumir(datos)
	datos.to_csv(obtenerRuta(f"experimento_{nombre}.csv"), index = False)
	resumen.to_csv(obtenerRuta(f"resumen_{nombre}.csv"))
	return resumen


# Genera las tres graficas principales de los experimentos A y B.
# Parametros:
#   resumenA: resumen del experimento con mucho tiempo.
#   resumenB: resumen del experimento con poco tiempo.
# Regresa: nada.
def graficarResumenes(resumenA, resumenB):
	graficar(
		resumenA, "tiempoMedio", "tiempoDesv", "Pasos hasta limpiar todo",
		"Tiempo de limpieza segun el numero de agentes", "tiempo.png", True
	)
	graficar(
		resumenA, "movimientosMedio", "movimientosDesv",
		"Movimientos totales",
		"Movimientos totales segun el numero de agentes",
		"movimientos.png", True
	)
	graficar(
		resumenB, "limpiasMedio", "limpiasDesv",
		"Celdas limpias al final (%)",
		f"Limpieza con tiempo maximo de {TIEMPO_MAXIMO_CORTO} pasos",
		"limpias.png", False
	)


# Corre el barrido fino (de 1 a 30 agentes) y hace las graficas
# de oscilacion donde se ve el comportamiento caotico.
# Parametros: ninguno.
# Regresa: nada.
def correrBarrido():
	datos = correrExperimento(TIEMPO_MAXIMO_HOLGADO, CANTIDADES_BARRIDO)
	datos.to_csv(obtenerRuta("experimento_c.csv"), index = False)
	graficarOscilacion(
		datos, "tiempo", "Pasos hasta limpiar todo",
		"Tiempo: corridas individuales y promedio", "oscilacion_tiempo.png"
	)
	graficarOscilacion(
		datos, "movimientos", "Movimientos totales",
		"Movimientos: corridas individuales y promedio",
		"oscilacion_movimientos.png"
	)


# Punto de entrada: corre todo y muestra los resumenes en consola.
# Parametros: ninguno.
# Regresa: nada.
def main():
	plt.switch_backend("Agg")
	os.makedirs(CARPETA_RESULTADOS, exist_ok = True)

	resumenA = correrYGuardar("a", TIEMPO_MAXIMO_HOLGADO)
	resumenB = correrYGuardar("b", TIEMPO_MAXIMO_CORTO)
	graficarResumenes(resumenA, resumenB)
	correrBarrido()

	pd.set_option("display.width", 200)
	print("Experimento A (tiempo holgado)")
	print(resumenA.round(1))
	print("\nExperimento B (tiempo corto)")
	print(resumenB.round(1))


if __name__ == "__main__":
	main()
