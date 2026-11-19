# Visualizacion interactiva de la simulacion de robots de limpieza.
# Muestra la habitacion en el navegador: las celdas sucias en cafe,
# las limpias en blanco y los robots como circulos azules (el numero
# indica cuantos robots hay en la misma celda). Tambien muestra una
# grafica del porcentaje de celdas limpias conforme avanza el tiempo.
# Para correrla: solara run app.py
# Autores: Emiliano Diaz Ferrusca (A01748498)
#          Santiago Hernandez Acevedo (A01754509)
# Fecha de creacion: 18 de noviembre de 2026
# Fecha de modificacion: 18 de noviembre de 2026

from collections import Counter

import solara
from matplotlib.colors import ListedColormap
from matplotlib.figure import Figure
from mesa.visualization import SolaraViz
from mesa.visualization.utils import update_counter

from model import Habitacion

COLOR_ROBOT = "#2a6f97"
COLORES_CELDAS = ListedColormap(["#ffffff", "#a47148"])


# Dibuja la habitacion con la suciedad y los robots.
# Parametros:
#   model: la habitacion que se esta simulando.
# Regresa: el componente de Solara con la figura.
@solara.component
def VistaHabitacion(model):
	update_counter.get()
	figura = Figure(figsize = (6, 6))
	eje = figura.subplots()
	eje.imshow(
		model.suciedad.T, origin = "lower", cmap = COLORES_CELDAS,
		vmin = 0, vmax = 1,
		extent = (-0.5, model.ancho - 0.5, -0.5, model.alto - 0.5)
	)
	conteo = Counter(robot.pos for robot in model.agents)
	if conteo:
		xs, ys = zip(*conteo.keys())
		eje.scatter(xs, ys, s = 120, color = COLOR_ROBOT, zorder = 3)
		for (x, y), cantidad in conteo.items():
			if cantidad > 1:
				eje.text(
					x, y, str(cantidad), color = "white", fontsize = 6,
					ha = "center", va = "center", zorder = 4
				)
	eje.set_xticks([x - 0.5 for x in range(model.ancho + 1)], minor = True)
	eje.set_yticks([y - 0.5 for y in range(model.alto + 1)], minor = True)
	eje.grid(which = "minor", color = "#dddddd", linewidth = 0.5)
	eje.tick_params(which = "both", length = 0, labelbottom = False,
		labelleft = False)
	eje.set_aspect("equal")
	solara.FigureMatplotlib(figura)


# Muestra las estadisticas actuales y una grafica del porcentaje de
# celdas limpias a lo largo del tiempo.
# Parametros:
#   model: la habitacion que se esta simulando.
# Regresa: el componente de Solara con los datos.
@solara.component
def Estadisticas(model):
	update_counter.get()
	if not hasattr(model, "historial"):
		model.historial = {}
	model.historial[model.tiempo] = model.calcularPorcentajeLimpias()

	estado = "Terminada" if not model.running else "En curso"
	solara.Markdown(
		f"**Paso:** {model.tiempo} / {model.tiempoMaximo}  \n"
		f"**Celdas sucias:** {model.contarSucias()}  \n"
		f"**Celdas limpias:** {model.calcularPorcentajeLimpias():.1f} %  \n"
		f"**Movimientos totales:** {model.contarMovimientos()}  \n"
		f"**Estado:** {estado}"
	)
	figura = Figure(figsize = (6, 3))
	eje = figura.subplots()
	pasos = sorted(model.historial)
	eje.plot(pasos, [model.historial[p] for p in pasos], color = COLOR_ROBOT)
	eje.set_xlabel("Paso")
	eje.set_ylabel("Celdas limpias (%)")
	eje.set_ylim(0, 100)
	eje.grid(True, alpha = 0.3)
	figura.tight_layout()
	solara.FigureMatplotlib(figura)


parametrosModelo = {
	"ancho": {
		"type": "SliderInt", "value": 20, "label": "Ancho",
		"min": 5, "max": 50, "step": 1,
	},
	"alto": {
		"type": "SliderInt", "value": 20, "label": "Alto",
		"min": 5, "max": 50, "step": 1,
	},
	"numAgentes": {
		"type": "SliderInt", "value": 10, "label": "Numero de robots",
		"min": 1, "max": 100, "step": 1,
	},
	"porcentajeSucias": {
		"type": "SliderInt", "value": 40, "label": "Celdas sucias (%)",
		"min": 0, "max": 100, "step": 1,
	},
	"tiempoMaximo": {
		"type": "SliderInt", "value": 5000, "label": "Tiempo maximo",
		"min": 50, "max": 30000, "step": 50,
	},
	"semilla": {
		"type": "SliderInt", "value": 42, "label": "Semilla",
		"min": 0, "max": 1000, "step": 1,
	},
}

modeloInicial = Habitacion(20, 20, 10, 40, 5000, semilla = 42)

page = SolaraViz(
	modeloInicial,
	components = [VistaHabitacion, Estadisticas],
	model_params = parametrosModelo,
	name = "Robots de limpieza",
)
page  # noqa
