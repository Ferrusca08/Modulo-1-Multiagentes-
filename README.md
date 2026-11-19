# Robots de limpieza reactivos

Simulación multiagente (Mesa) de robots aspiradora que limpian una habitación de M x N celdas. Cada robot solo ve su propia celda: si está sucia la aspira; si no, se mueve a una celda vecina al azar.

## Archivos

| Archivo | Descripción |
|---|---|
| `model.py` | Modelo de la habitación (`Habitacion`) y del robot (`RobotLimpieza`). |
| `agent.py` | Experimentos A, B y C; guarda CSV y gráficas en `resultados/`. |
| `app.py` | Visualización interactiva en el navegador con Solara. |
| `Informe_RobotLimpieza.pdf` | Informe con el análisis de resultados. |

## Instalación

```bash
pip install "mesa[rec]" solara pandas matplotlib numpy
```

## Uso

```bash
python model.py        # una simulación de ejemplo
python agent.py        # corre los experimentos y genera las gráficas
solara run app.py      # abre la visualización en el navegador
```

## Autores

- Emiliano Díaz Ferrusca (A01748498)
- Santiago Hernández Acevedo (A01754509)
