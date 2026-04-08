# SHIFTPLANGA

Sistema de optimizacion de horarios laborales con Algoritmos Geneticos (AG), con backend en FastAPI y frontend en React.

## 1) Objetivo del proyecto

Construir horarios semanales por empleado maximizando aptitud global con 4 criterios:

- cobertura de demanda
- horas extra
- insatisfaccion
- violaciones legales

La aptitud se combina como producto ponderado:

$$
aptitud = \left(\frac{1}{1+deficit}\right)^{w_1}
\cdot
\left(\frac{1}{1+horas\_extra}\right)^{w_2}
\cdot
\left(\frac{1}{1+insatisfaccion}\right)^{w_3}
\cdot
\left(\frac{1}{1+violaciones\_legales}\right)^{w_4}
$$

## 2) Arquitectura

- Backend: `233361-AG/app/main.py`
- Configuracion AG: `233361-AG/app/config.py`
- Inicializacion: `233361-AG/app/ga_core/population.py`
- Aptitud/restricciones: `233361-AG/app/ga_core/fitness.py`
- Operadores AG: `233361-AG/app/ga_core/operators.py`
- Motor evolutivo: `233361-AG/app/ga_core/engine.py`
- Frontend principal: `233361-FRONT-AG/src/App.jsx`

## 3) Configuracion disponible y justificacion

### 3.1 Inicializacion

Parametro: `metodo_inicializacion`

Opciones:

- `aleatoria`
- `sesgada_preferencias`

Justificacion:

- `aleatoria`: maximiza diversidad inicial y evita sesgo temprano. Conviene cuando no conoces el patron de la solucion o cuando quieres explorar mas espacio de busqueda.
- `sesgada_preferencias`: arranca con individuos mas cercanos a preferencias de empleados, acelerando convergencia inicial. Conviene cuando las preferencias son confiables y quieres resultados utiles rapido.

Parametro de ajuste:

- `fraccion_sesgo_preferencias` en [0, 1]: probabilidad de elegir el turno mas preferido dentro de la disponibilidad.

### 3.2 Seleccion / Emparejamiento de padres

Parametro: `metodo_seleccion`

Opciones:

- `torneo`
- `emparejamiento_ranking`
- `emparejamiento_mitad_ordenada`

Justificacion:

- `torneo`: estable, simple, robusto con ruido; controla presion selectiva via `tamano_torneo`.
- `emparejamiento_ranking`: ordena por aptitud, divide en dos bloques y mezcla el bloque inferior para evitar apareamientos siempre identicos.
- `emparejamiento_mitad_ordenada`: divide poblacion ordenada en dos mitades y empareja primero con primero, segundo con segundo, etc. Esto implementa exactamente la logica "partir por la mitad y emparejar primeros con primeros".

Cuando usar cada uno:

- usa `torneo` si ves estancamiento o necesitas mas exploracion controlada.
- usa `emparejamiento_ranking` para buen balance entre explotacion y diversidad.
- usa `emparejamiento_mitad_ordenada` cuando quieres presion selectiva mas determinista y trazable para analisis academico.

### 3.3 Cruza

Parametro: `metodo_cruce`

Opciones:

- `dos_puntos`
- `multipunto`
- `uniforme`

Justificacion:

- `dos_puntos`: preserva bloques contiguos de dias; util cuando patrones semanales continuos importan.
- `multipunto`: recombina mas agresivamente; util para escapar de optimos locales.
- `uniforme`: decide gen por gen de que padre heredar; aumenta mezcla genetica.

Ajustes relevantes:

- `cortes_minimos_multipunto`
- `cortes_maximos_multipunto`

### 3.4 Mutacion

Parametro: `metodo_mutacion`

Opciones:

- `puntual`
- `hibrida`
- `intercambio`

Justificacion:

- `puntual`: cambia turnos de forma local respetando disponibilidad; buena base general.
- `hibrida`: combina reinicio local y swap, util cuando necesitas mezclar refinamiento y sacudidas ocasionales.
- `intercambio`: intercambia dos dias del mismo empleado; conserva cantidad de turnos y cambia distribucion temporal.

Ajuste relevante:

- `probabilidad_reinicio_hibrida` (solo `hibrida`).

### 3.5 Poda / Reemplazo

Parametro: `metodo_poda`

Opciones:

- `elitismo`
- `reemplazo_generacional`

Justificacion:

- `elitismo`: preserva los mejores individuos entre generaciones; reduce riesgo de perder soluciones de alta aptitud.
- `reemplazo_generacional`: no conserva elite fija; fuerza renovacion completa y puede aumentar exploracion.

Ajuste relevante:

- `probabilidad_elitismo` (solo cuando `metodo_poda = elitismo`).

## 4) Recomendaciones de configuracion (guia rapida)

### Escenario A: Convergencia rapida

- `metodo_inicializacion`: `sesgada_preferencias`
- `metodo_seleccion`: `emparejamiento_mitad_ordenada`
- `metodo_cruce`: `dos_puntos`
- `metodo_mutacion`: `puntual`
- `metodo_poda`: `elitismo`

### Escenario B: Evitar estancamiento

- `metodo_inicializacion`: `aleatoria`
- `metodo_seleccion`: `torneo`
- `metodo_cruce`: `multipunto` o `uniforme`
- `metodo_mutacion`: `hibrida` o `intercambio`
- `metodo_poda`: `reemplazo_generacional`

### Escenario C: Balance exploracion/explotacion

- `metodo_inicializacion`: `aleatoria`
- `metodo_seleccion`: `emparejamiento_ranking`
- `metodo_cruce`: `dos_puntos`
- `metodo_mutacion`: `hibrida`
- `metodo_poda`: `elitismo`

## 5) Ejemplo de configuracion JSON

```json
{
  "poblacion": 80,
  "generations": 100,
  "probabilidad_cruce": 0.85,
  "probabilidad_mutacion": 0.08,
  "probabilidad_elitismo": 0.15,
  "tamano_torneo": 3,
  "semilla": 42,
  "metodo_inicializacion": "sesgada_preferencias",
  "fraccion_sesgo_preferencias": 0.70,
  "metodo_seleccion": "emparejamiento_mitad_ordenada",
  "metodo_cruce": "uniforme",
  "metodo_mutacion": "hibrida",
  "probabilidad_reinicio_hibrida": 0.70,
  "metodo_poda": "elitismo",
  "cortes_minimos_multipunto": 1,
  "cortes_maximos_multipunto": 3
}
```

## 6) API

### `GET /api/config-template`

Devuelve:

- `defaults`: valores por defecto
- `choices`: opciones disponibles por estrategia

### `POST /api/optimize`

Entrada:

- `empleados`
- `demanda`
- `pesos`
- `configuracion`

Salida:

- `perfiles` (A, B, C)
- `titulo_grafica`
- `titulo_ranking`
- `configuracion_usada`

## 7) Ejecucion

### Backend

```bash
cd 233361-AG
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd 233361-FRONT-AG
npm install
npm run dev
```

## 8) Nota metodologica

No existe una unica configuracion "mejor" para todos los casos. La combinacion correcta depende de:

- calidad y consistencia de preferencias
- nivel de conflicto en demanda vs disponibilidad
- prioridad del curso/proyecto (cobertura, satisfaccion, legalidad)
- tiempo disponible de computo

Por eso se exponen metodos intercambiables y parametros de ajuste: para que puedas justificar experimentalmente por que una combinacion supera a otra en tu escenario.

# Algoritmo-Gen-tico--Generador-de-Horarios
