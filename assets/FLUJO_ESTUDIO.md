# Flujo de estudio de SHIFTPLANGA

## Paso 1. Entrada de datos

El sistema recibe:

- empleados
- demanda semanal
- pesos de optimizacion
- configuracion del AG

Los datos entran por JSON o CSV.

## Paso 2. Semilla

La `semilla` fija el azar del algoritmo.
Si repites los mismos datos, la misma semilla y la misma configuracion, obtienes resultados repetibles.

### En el ejemplo AG adjunto

- `main.py` tiene `#random.seed(42)` comentado, asi que la semilla no esta activa.
- Por eso el ejemplo puede cambiar de una ejecucion a otra.

## Paso 3. Tipos de cada fase en tu proyecto

### Inicializacion

- `aleatoria`: crea diversidad desde el inicio.
- `sesgada_preferencias`: inicia mas cerca de lo que prefieren los empleados.

### Emparejamiento / Seleccion

- `torneo`: elige el mejor dentro de un grupo pequeno.
- `emparejamiento_ranking`: ordena por aptitud y empareja por ranking.
- `emparejamiento_mitad_ordenada`: divide la poblacion en dos mitades y empareja el primero de la primera mitad con el primero de la segunda, el segundo con el segundo, etc.

### Cruza

- `dos_puntos`: conserva bloques continuos de dias.
- `multipunto`: mezcla mas de un bloque y aumenta recombinacion.
- `uniforme`: decide gen por gen de que padre heredar.

### Mutacion

- `puntual`: cambia un turno puntual respetando disponibilidad.
- `hibrida`: combina cambio puntual con reinicio local o intercambio.
- `intercambio`: permuta dos dias del mismo empleado.

### Poda

- `elitismo`: conserva los mejores individuos para no perder buena solucion.
- `reemplazo_generacional`: reemplaza toda la poblacion y fuerza renovacion.

## Paso 4. Evaluacion

Cada individuo se puntua por:

- deficit de cobertura
- horas extra
- insatisfaccion
- violaciones legales

Menor penalizacion significa mejor aptitud.

## Paso 5. Salida

El backend devuelve:

- perfiles A, B y C
- grafica de evolucion
- ranking de individuos
- horario final por empleado

## Paso 6. Configuracion recomendada para estudiar

### Opcion estable

- inicializacion: `sesgada_preferencias`
- emparejamiento: `emparejamiento_mitad_ordenada`
- cruza: `dos_puntos`
- mutacion: `puntual`
- poda: `elitismo`

### Opcion mas exploratoria

- inicializacion: `aleatoria`
- emparejamiento: `torneo`
- cruza: `multipunto` o `uniforme`
- mutacion: `hibrida` o `intercambio`
- poda: `reemplazo_generacional`

## Paso 7. Idea para explicarlo

Este proyecto no usa un AG unico e inamovible.
Usa varias estrategias configurables para justificar, con evidencia, cual conviene segun el objetivo: estabilidad, exploracion o balance entre ambas.
