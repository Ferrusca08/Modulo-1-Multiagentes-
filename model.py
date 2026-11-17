# Simulacion de robots de limpieza reactivos.
# Basicamente tenemos una habitacion de M x N celdas donde un grupo
# de robots aspiradora se dedican a limpiar las celdas sucias. Cada
# robot solo puede ver su propia celda: si esta sucia la aspira, y si
# no, se mueve a una celda vecina al azar. Nada mas.
# Autores: Emiliano Diaz Ferrusca (A01748498)
#          Santiago Hernandez Acevedo (A01754509)
# Fecha de creacion: 11 de noviembre de 2026
# Fecha de modificacion: 16 de noviembre de 2026

import mesa
import numpy as np
from mesa.space import MultiGrid

# Las 8 direcciones posibles a las que se puede mover un robot.
DIRECCIONES = [
	(-1, -1), (0, -1), (1, -1),
	(-1, 0), (1, 0),
	(-1, 1), (0, 1), (1, 1),
]

# La celda [1,1] del enunciado es (0, 0) en Mesa porque empieza
# a contar desde cero.
CELDA_INICIAL = (0, 0)


# Cada robot es un agente reactivo: no tiene memoria ni se coordina
# con los demas, solo revisa si su celda esta sucia o no.
# Atributos:
#   movimientos: cuantas veces logro moverse a otra celda.
#   intentosBloqueados: cuantas veces intento salirse de la habitacion.
class RobotLimpieza(mesa.Agent):

	# Crea un robot nuevo, sin historial de nada.
	# Parametros:
	#   model: la habitacion donde va a vivir el robot.
	# Regresa: nada.
	def __init__(self, model):
		super().__init__(model)
		self.movimientos = 0
		self.intentosBloqueados = 0

	# Lo que hace el robot en cada paso: si su celda esta sucia la
	# aspira, y si esta limpia intenta moverse a otro lado.
	# Parametros: ninguno.
	# Regresa: nada.
	def step(self):
		if self.model.estaSucia(self.pos):
			self.aspirar()
		else:
			self.mover()

	# Limpia la celda donde esta parado el robot.
	# Parametros: ninguno.
	# Regresa: nada.
	def aspirar(self):
		self.model.limpiar(self.pos)

	# Escoge una direccion al azar y trata de moverse. Si la celda
	# destino esta fuera de la habitacion, se queda donde esta.
	# Parametros: ninguno.
	# Regresa: nada.
	def mover(self):
		dx, dy = self.random.choice(DIRECCIONES)
		destino = (self.pos[0] + dx, self.pos[1] + dy)
		if self.model.grid.out_of_bounds(destino):
			self.intentosBloqueados += 1
		else:
			self.model.grid.move_agent(self, destino)
			self.movimientos += 1


# La habitacion es el modelo completo: tiene el grid, la suciedad
# y los robots. Controla cuando empieza y cuando termina todo.
# Atributos:
#   grid: el espacio donde se mueven los robots.
#   suciedad: una matriz que dice cuales celdas estan sucias.
#   tiempoMaximo: el limite de pasos que puede durar la simulacion.
#   tiempo: cuantos pasos han pasado.
#   running: se pone en False cuando ya se acabo.
class Habitacion(mesa.Model):

	# Arma la habitacion: crea el grid, ensucia celdas al azar y
	# pone todos los robots en la esquina.
	# Parametros:
	#   ancho: columnas de la habitacion.
	#   alto: filas de la habitacion.
	#   numAgentes: cuantos robots queremos.
	#   porcentajeSucias: que porcentaje de celdas empieza sucio (0-100).
	#   tiempoMaximo: limite de pasos.
	#   semilla: para que se pueda repetir exactamente la simulacion.
	# Regresa: nada.
	def __init__(
		self, ancho, alto, numAgentes, porcentajeSucias, tiempoMaximo,
		semilla = None
	):
		super().__init__(rng = semilla)
		self.ancho = ancho
		self.alto = alto
		self.tiempoMaximo = tiempoMaximo
		self.tiempo = 0
		self.grid = MultiGrid(ancho, alto, torus = False)
		self.suciedad = np.zeros((ancho, alto), dtype = bool)

		self.ensuciar(porcentajeSucias)
		self.colocarRobots(numAgentes)
		self.running = self.contarSucias() > 0 and tiempoMaximo > 0

	# Escoge celdas al azar y las marca como sucias.
	# Parametros:
	#   porcentajeSucias: que porcentaje del total se ensucia.
	# Regresa: nada.
	def ensuciar(self, porcentajeSucias):
		total = self.ancho * self.alto
		cantidad = round(total * porcentajeSucias / 100)
		celdas = [(x, y) for x in range(self.ancho) for y in range(self.alto)]
		for x, y in self.random.sample(celdas, cantidad):
			self.suciedad[x, y] = True

	# Pone todos los robots en la celda inicial.
	# Parametros:
	#   numAgentes: cuantos robots crear.
	# Regresa: nada.
	def colocarRobots(self, numAgentes):
		for indice in range(numAgentes):
			robot = RobotLimpieza(self)
			self.grid.place_agent(robot, CELDA_INICIAL)

	# Revisa si una celda esta sucia.
	# Parametros:
	#   pos: coordenadas (x, y) de la celda.
	# Regresa: True si esta sucia, False si no.
	def estaSucia(self, pos):
		return bool(self.suciedad[pos])

	# Marca una celda como limpia.
	# Parametros:
	#   pos: coordenadas (x, y) de la celda.
	# Regresa: nada.
	def limpiar(self, pos):
		self.suciedad[pos] = False

	# Cuenta cuantas celdas siguen sucias.
	# Parametros: ninguno.
	# Regresa: el numero de celdas sucias.
	def contarSucias(self):
		return int(self.suciedad.sum())

	# Calcula que porcentaje de la habitacion esta limpio.
	# Parametros: ninguno.
	# Regresa: porcentaje de celdas limpias (0 a 100).
	def calcularPorcentajeLimpias(self):
		total = self.ancho * self.alto
		return 100 * (total - self.contarSucias()) / total

	# Suma todos los movimientos que hicieron los robots.
	# Parametros: ninguno.
	# Regresa: total de movimientos.
	def contarMovimientos(self):
		return sum(robot.movimientos for robot in self.agents)

	# Suma todas las veces que un robot intento salirse.
	# Parametros: ninguno.
	# Regresa: total de intentos bloqueados.
	def contarBloqueados(self):
		return sum(robot.intentosBloqueados for robot in self.agents)

	# Avanza un paso: todos los robots actuan en orden aleatorio.
	# Si ya no hay celdas sucias o se acabo el tiempo, para.
	# Parametros: ninguno.
	# Regresa: nada.
	def step(self):
		self.agents.shuffle_do("step")
		self.tiempo += 1
		if self.contarSucias() == 0 or self.tiempo >= self.tiempoMaximo:
			self.running = False

	# Corre toda la simulacion de principio a fin.
	# Parametros: ninguno.
	# Regresa: un diccionario con las estadisticas finales.
	def ejecutar(self):
		while self.running:
			self.step()
		return {
			"tiempo": self.tiempo,
			"limpiezaCompleta": self.contarSucias() == 0,
			"porcentajeLimpias": self.calcularPorcentajeLimpias(),
			"movimientos": self.contarMovimientos(),
			"intentosBloqueados": self.contarBloqueados(),
		}


# Corre una simulacion rapida de ejemplo para verificar que todo jale.
# Parametros: ninguno.
# Regresa: nada.
def main():
	modelo = Habitacion(
		ancho = 20, alto = 20, numAgentes = 10, porcentajeSucias = 40,
		tiempoMaximo = 5000, semilla = 42
	)
	resultado = modelo.ejecutar()
	print(f"Tiempo empleado (pasos): {resultado['tiempo']}")
	print(f"Limpieza completa: {resultado['limpiezaCompleta']}")
	print(f"Celdas limpias: {resultado['porcentajeLimpias']:.1f} %")
	print(f"Movimientos totales: {resultado['movimientos']}")


if __name__ == "__main__":
	main()
