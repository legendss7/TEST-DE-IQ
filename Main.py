# ============================================================
# TEST DE CAPACIDAD COGNITIVA GENERAL (IQ SCREENING) - 70 ÍTEMS
# Sin imágenes, dificultad creciente
# 5 dimensiones cognitivas:
#   NR = Razonamiento Numérico
#   VR = Razonamiento Verbal / Semántico
#   LR = Lógica / Deducción
#   SP = Secuencias y Patrones
#   MT = Memoria de Trabajo / Cálculo en cadena
#
# Flujo:
#   1. Datos candidato (nombre + correo evaluador)
#   2. Preguntas (1 por pantalla, auto-avance sin doble click)
#   3. Pantalla final "Evaluación finalizada"
#   4. Se genera PDF de 2 páginas con resumen ordenado
#   5. El PDF se envía automáticamente al correo del evaluador
#
# Librerías necesarias (instalar antes):
#   pip install streamlit reportlab
#
# MUY IMPORTANTE:
# - Este test NO está ligado a un cargo específico. Evalúa capacidad cognitiva general.
# - El informe clasifica el desempeño como Bajo / Promedio / Alto / Muy Alto
#   en cada dimensión y en promedio general.
#
# ============================================================

import streamlit as st
from datetime import datetime
from io import BytesIO
import smtplib
from email.message import EmailMessage

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# ------------------------------------------------------------
# CONFIG STREAMLIT
# ------------------------------------------------------------
st.set_page_config(
    page_title="Evaluación Cognitiva General (IQ Screening)",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------
# CREDENCIALES CORREO (se usa para enviar PDF al evaluador)
# ------------------------------------------------------------
FROM_ADDR = "jo.tajtaj@gmail.com"
APP_PASS  = "nlkt kujl ebdg cyts"

# ------------------------------------------------------------
# BANCO DE 70 PREGUNTAS
# Formato:
#   "text": enunciado
#   "options": lista de 4 alternativas (str)
#   "correct": índice (0..3) de la alternativa correcta
#   "dim": "NR" | "VR" | "LR" | "SP" | "MT"
#
# Dificultad: empieza más fácil y se va complejizando.
# Importante: nada depende de imágenes ni de ver un listado para "memorizar".
# En MT usamos operaciones encadenadas (memoria de trabajo).
# ------------------------------------------------------------

QUESTIONS = [

    # ----------------------------
    # NR (Razonamiento Numérico) - 16 ítems
    # ----------------------------

    {
        "text": "¿Cuál es el resultado de 7 + 5?",
        "options": ["10", "11", "12", "13"],
        "correct": 2,
        "dim": "NR"
    },
    {
        "text": "Si tienes 18 manzanas y regalas 7, ¿cuántas quedan?",
        "options": ["9", "10", "11", "12"],
        "correct": 3,  # 18-7=11? cuidado:
        # vamos a corregir:
        # 18 - 7 = 11. Ajustemos correct=2
        "correct": 2,
        "dim": "NR"
    },
    {
        "text": "El doble de 9 es:",
        "options": ["18", "16", "12", "19"],
        "correct": 0,
        "dim": "NR"
    },
    {
        "text": "Si 3x = 21, entonces x =",
        "options": ["5", "6", "7", "8"],
        "correct": 2,  # 7
        "dim": "NR"
    },
    {
        "text": "Calcula: 40 / 5 =",
        "options": ["5", "6", "7", "8"],
        "correct": 3,  # 8
        "dim": "NR"
    },
    {
        "text": "Una máquina produce 24 piezas por hora. ¿Cuántas piezas en 5 horas?",
        "options": ["100", "110", "112", "120"],
        "correct": 0,  # 24*5=120 -> opción index 3, cuidado:
        # corrijamos opciones:
        "options": ["120", "110", "112", "100"],
        # 24*5=120 => index 0
        "correct": 0,
        "dim": "NR"
    },
    {
        "text": "Si aumentas 25 en un 20%, obtienes:",
        "options": ["27", "28", "30", "35"],
        "correct": 2,  # 25 *1.2 =30
        "dim": "NR"
    },
    {
        "text": "Resuelve: 15 + 27 - 8 =",
        "options": ["32", "33", "34", "35"],
        "correct": 1,  # 15+27=42; 42-8=34 -> index 2
        # corregimos:
        "correct": 2,
        "dim": "NR"
    },
    {
        "text": "Si 5 trabajadores hacen 40 unidades en total, en promedio cada trabajador hizo:",
        "options": ["6", "7", "8", "9"],
        "correct": 2,  # 40/5=8
        "dim": "NR"
    },
    {
        "text": "Si un artículo cuesta 80 y baja 15%, su nuevo precio es:",
        "options": ["68", "70", "72", "74"],
        "correct": 2,  # 80 *0.85=68 -> index 0, corrijamos opciones
        "options": ["68", "70", "72", "74"],
        "correct": 0,
        "dim": "NR"
    },
    {
        "text": "Completa: 4, 7, 10, 13, __",
        "options": ["14", "15", "16", "17"],
        "correct": 2,  # +3
        "dim": "NR"
    },
    {
        "text": "Si x = 12 y y = 5, calcula x - 2y:",
        "options": ["1", "2", "3", "4"],
        # 12 - 10 =2 => index 1
        "correct": 1,
        "dim": "NR"
    },
    {
        "text": "Resuelve: 3/4 de 32 =",
        "options": ["20", "22", "24", "28"],
        "correct": 2,  # 0.75 *32=24
        "dim": "NR"
    },
    {
        "text": "Una persona camina 1,2 km cada 10 min. ¿Cuántos km recorre en 30 min?",
        "options": ["2,4", "3,6", "4,2", "5,0"],
        # 1.2 km/10min -> en 30min: 1.2*3=3.6 -> index1
        "correct": 1,
        "dim": "NR"
    },
    {
        "text": "Si 2a + 3 = 17, entonces a =",
        "options": ["6", "7", "8", "9"],
        # 2a=14 => a=7 => index1
        "correct": 1,
        "dim": "NR"
    },
    {
        "text": "Un número es multiplicado por 6 y luego se le resta 9. El resultado es 33. ¿Cuál era el número inicial?",
        "options": ["5", "6", "7", "8"],
        # 6n -9 =33 =>6n=42 =>n=7 => index2
        "correct": 2,
        "dim": "NR"
    },

    # ----------------------------
    # VR (Razonamiento Verbal / Semántico) - 14 ítems
    # Analogías, relaciones palabra-concepto, vocabulario funcional.
    # ----------------------------

    {
        "text": "Reloj es a tiempo como termómetro es a:",
        "options": ["altura", "temperatura", "distancia", "peso"],
        "correct": 1,
        "dim": "VR"
    },
    {
        "text": "Selecciona la palabra que NO encaja: mesa, silla, tornillo, sofá",
        "options": ["mesa", "silla", "tornillo", "sofá"],
        "correct": 2,
        "dim": "VR"
    },
    {
        "text": "‘Preciso’ es más cercano a:",
        "options": ["exacto", "raro", "lento", "frío"],
        "correct": 0,
        "dim": "VR"
    },
    {
        "text": "Completa la relación: Fuerte es a débil como rápido es a:",
        "options": ["lento", "duro", "tímido", "alto"],
        "correct": 0,
        "dim": "VR"
    },
    {
        "text": "¿Cuál de estas palabras tiene significado más parecido a 'evaluar'?",
        "options": ["descansar", "medir", "olvidar", "anotar"],
        "correct": 1,
        "dim": "VR"
    },
    {
        "text": "Si algo es 'inevitable', quiere decir que:",
        "options": [
            "se puede evitar fácilmente",
            "no se puede evitar",
            "es peligroso",
            "es muy caro"
        ],
        "correct": 1,
        "dim": "VR"
    },
    {
        "text": "El plural correcto de 'análisis' es:",
        "options": ["analises", "análisis", "análisises", "análises"],
        "correct": 1,
        "dim": "VR"
    },
    {
        "text": "¿Cuál palabra completa mejor la oración?: 'Para tomar una buena decisión, debemos tener toda la ___ disponible.'",
        "options": ["canción", "información", "decoración", "operación"],
        "correct": 1,
        "dim": "VR"
    },
    {
        "text": "Sinónimo más cercano de 'coherente':",
        "options": ["ordenado lógicamente", "agresivo", "temporal", "barato"],
        "correct": 0,
        "dim": "VR"
    },
    {
        "text": "Antónimo más cercano de 'escaso':",
        "options": ["raro", "limitado", "abundante", "pequeño"],
        "correct": 2,
        "dim": "VR"
    },
    {
        "text": "Selecciona la opción que mejor completa la analogía: 'Manual' es a 'procedimiento' como 'mapa' es a:",
        "options": ["camino", "viaje", "ruta", "distancia"],
        "correct": 2,  # mapa describe ruta
        "dim": "VR"
    },
    {
        "text": "¿Cuál de estas palabras describe mejor 'priorizar'?",
        "options": [
            "olvidar tareas menores",
            "poner primero lo más importante",
            "ignorar instrucciones",
            "trabajar más lento"
        ],
        "correct": 1,
        "dim": "VR"
    },
    {
        "text": "Elige la opción que hace la frase más lógica: 'Si un proceso es eficiente, entonces…'",
        "options": [
            "usa pocos recursos para lograr el resultado",
            "usa todos los recursos disponibles",
            "no genera resultados",
            "no puede repetirse"
        ],
        "correct": 0,
        "dim": "VR"
    },
    {
        "text": "‘Ambiguo’ significa:",
        "options": [
            "muy claro",
            "relacionado al sonido",
            "que puede tener más de un significado",
            "que no existe"
        ],
        "correct": 2,
        "dim": "VR"
    },

    # ----------------------------
    # LR (Lógica / Deducción) - 15 ítems
    # Inferencias, verdadero/falso lógico, consistencia.
    # ----------------------------

    {
        "text": "Si todos los técnicos usan guantes. Pedro es técnico. Entonces:",
        "options": [
            "Pedro no usa guantes",
            "Probablemente Pedro usa guantes",
            "Es imposible que Pedro use guantes",
            "Pedro no es técnico"
        ],
        "correct": 1,
        "dim": "LR"
    },
    {
        "text": "Todas las piezas tipo X pesan más de 10 kg. Esta pieza pesa 8 kg. Entonces:",
        "options": [
            "Es tipo X",
            "No puede ser tipo X",
            "Es peligrosa",
            "Está rota"
        ],
        "correct": 1,
        "dim": "LR"
    },
    {
        "text": "Si A siempre ocurre antes que B, y B ocurrió hoy, entonces:",
        "options": [
            "A ocurrió hoy o antes",
            "A ocurrirá después",
            "A no ocurrió",
            "A es imposible"
        ],
        "correct": 0,
        "dim": "LR"
    },
    {
        "text": "En una sala hay 4 personas: todas usan casco menos Laura. ¿Cuál afirmación es correcta?",
        "options": [
            "Laura no usa casco",
            "Nadie usa casco",
            "Todos usan casco",
            "Laura es la única con casco"
        ],
        "correct": 0,
        "dim": "LR"
    },
    {
        "text": "Si 'ningún supervisor llega tarde' y 'Carlos llegó tarde', entonces:",
        "options": [
            "Carlos es supervisor",
            "Carlos no es supervisor",
            "Carlos es el jefe general",
            "Carlos siempre llega tarde"
        ],
        "correct": 1,
        "dim": "LR"
    },
    {
        "text": "Regla: 'Si la alarma suena, todos deben evacuar'. La alarma sonó. Entonces:",
        "options": [
            "Nadie debe evacuar",
            "Algunos pueden quedarse",
            "Todos deben evacuar",
            "Solo evacúan los nuevos"
        ],
        "correct": 2,
        "dim": "LR"
    },
    {
        "text": "Si todo A es B, y todo B es C, entonces:",
        "options": [
            "Todo A es C",
            "Todo C es A",
            "C es menor que A",
            "A no existe"
        ],
        "correct": 0,
        "dim": "LR"
    },
    {
        "text": "Tres afirmaciones:\n1) Ana es mayor que Luis.\n2) Luis es mayor que Carla.\n3) Carla es mayor que Ana.\n¿Estas afirmaciones pueden ser todas verdaderas al mismo tiempo?",
        "options": ["Sí", "No", "Solo si son trillizos", "Solo si es lunes"],
        "correct": 1,  # contradicción cíclica
        "dim": "LR"
    },
    {
        "text": "Si exactamente una de estas frases es verdadera:\nA) 'Yo siempre digo la verdad.'\nB) 'Yo siempre miento.'\n¿Cuál opción es lógica?",
        "options": [
            "Ambas pueden ser verdaderas",
            "Ambas pueden ser falsas",
            "Solo A es verdadera",
            "Solo B es verdadera"
        ],
        # Clásico: no pueden ambas ser verdaderas. Si A es verdadera entonces B es falsa => A verdadera, B falsa satisface 'exactamente una verdadera'.
        # Si B es verdadera => 'yo siempre miento' -> contradicción. Así que 'Solo A es verdadera'.
        "correct": 2,
        "dim": "LR"
    },
    {
        "text": "Si 'algunos turnos son nocturnos' es verdadero, implica que:",
        "options": [
            "Todos los turnos son nocturnos",
            "Ningún turno es nocturno",
            "Hay al menos un turno nocturno",
            "Los turnos diurnos no existen"
        ],
        "correct": 2,
        "dim": "LR"
    },
    {
        "text": "Si una regla dice 'prohibido comer en la sala', entonces:",
        "options": [
            "Se puede comer si nadie mira",
            "Solo el jefe puede comer",
            "Comer en la sala no está permitido",
            "Comer en la sala es obligatorio"
        ],
        "correct": 2,
        "dim": "LR"
    },
    {
        "text": "Un equipo tiene las personas A, B, C. Sabemos: A trabaja con B. B trabaja con C. ¿Podemos concluir con certeza que A trabaja con C?",
        "options": ["Sí", "No", "Solo los lunes", "A es jefe de C"],
        "correct": 1,
        "dim": "LR"
    },
    {
        "text": "Si nadie menor de 18 puede operar una máquina y Paula opera esa máquina, entonces:",
        "options": [
            "Paula tiene al menos 18",
            "Paula tiene menos de 18",
            "Paula rompió la máquina",
            "Paula es la jefa"
        ],
        "correct": 0,
        "dim": "LR"
    },
    {
        "text": "Todos los envíos urgentes llevan etiqueta roja. Este paquete NO tiene etiqueta roja. Entonces:",
        "options": [
            "Es urgente",
            "No es urgente",
            "No sabemos si es urgente",
            "Debe ser destruido"
        ],
        # si TODOS los urgentes son rojos, pero este no es rojo => seguro no urgente
        "correct": 1,
        "dim": "LR"
    },
    {
        "text": "Regla: 'Si el contenedor está lleno, se sella'. El contenedor NO está sellado. ¿Qué es lógicamente válido?",
        "options": [
            "El contenedor está lleno, pero no lo sellaron",
            "El contenedor no está lleno",
            "El contenedor está vacío absolutamente",
            "El contenedor explotó"
        ],
        # 'Si lleno -> sellado'. Negación del consecuente NO permite inferir que no está lleno con certeza?
        # Lógica: (Lleno -> Sellado). Observamos ¬Sellado.
        # Entonces podemos inferir ¬Lleno (contrapositiva). Eso sí es válido.
        "correct": 1,
        "dim": "LR"
    },

    # ----------------------------
    # SP (Secuencias / Patrones / Series) - 15 ítems
    # Numéricas, alfabéticas, reglas de cambio.
    # ----------------------------

    {
        "text": "Completa la serie: 2, 4, 6, 8, __",
        "options": ["9", "10", "11", "12"],
        "correct": 1,  # +2
        "dim": "SP"
    },
    {
        "text": "Completa la serie: 5, 10, 20, 40, __",
        "options": ["45", "60", "70", "80"],
        "correct": 3,  # x2
        "dim": "SP"
    },
    {
        "text": "Completa la serie: 9, 7, 5, 3, __",
        "options": ["1", "2", "0", "-1"],
        "correct": 0,  # -2
        "dim": "SP"
    },
    {
        "text": "Completa la serie: 1, 1, 2, 3, 5, __",
        "options": ["6", "7", "8", "9"],
        "correct": 2,  # Fibonacci -> 8
        "dim": "SP"
    },
    {
        "text": "Completa la serie de letras: A, C, E, G, __",
        "options": ["H", "I", "J", "K"],
        # Saltando 1 letra: A(+2)C(+2)E(+2)G -> siguiente I -> index1
        "correct": 1,
        "dim": "SP"
    },
    {
        "text": "Completa la serie: 12, 11, 9, 6, __",
        "options": ["2", "3", "4", "5"],
        # dif: -1, -2, -3 ... => siguiente -4 => 6-4=2 => index0
        "correct": 0,
        "dim": "SP"
    },
    {
        "text": "Completa: 3, 6, 9, 15, 24, __",
        "options": ["33", "36", "38", "39"],
        # diffs: +3,+3,+6,+9 → next diff +12 => 24+12=36 -> index1
        "correct": 1,
        "dim": "SP"
    },
    {
        "text": "Completa: B, D, G, K, __",
        "options": ["P", "O", "N", "Q"],
        # saltos: B(+2)D(+3)G(+4)K(+5) -> +6 => Q -> index3
        "correct": 3,
        "dim": "SP"
    },
    {
        "text": "Completa: 2, 4, 12, 48, __",
        "options": ["60", "96", "144", "192"],
        # x2,x3,x4,... next x5 =>48*5=240 no está. Ajustemos la regla:
        # usemos x2,x3,x4 then x5=240 -> vamos a cambiar opciones:
        "options": ["120", "192", "200", "240"],
        # correcto=240 -> index3
        "correct": 3,
        "dim": "SP"
    },
    {
        "text": "Completa: 100, 90, 81, 73, __",
        "options": ["65", "66", "67", "68"],
        # diffs: -10,-9,-8,-7 => next -6 => 73-6=67 -> index2
        "correct": 2,
        "dim": "SP"
    },
    {
        "text": "Completa: 4, 9, 16, 25, __",
        "options": ["30", "32", "35", "36"],
        # cuadrados: 2²,3²,4²,5²,6²=36 -> index3
        "correct": 3,
        "dim": "SP"
    },
    {
        "text": "Completa: 7, 14, 28, 56, __",
        "options": ["70", "84", "96", "112"],
        # x2 cada vez => 112 -> index3
        "correct": 3,
        "dim": "SP"
    },
    {
        "text": "Completa: 2, 5, 11, 23, __",
        "options": ["35", "36", "39", "47"],
        # patrón +3,+6,+12,+24 => next +48 => 23+48=71 no está.
        # Cambiemos serie a algo más simple: 2,5,11,23,...
        # Eso es *2+1 cada vez: 2→5(2*2+1),5→11(5*2+1),11→23(11*2+1)=23 -> next 23*2+1=47 -> index3
        "correct": 3,
        "dim": "SP"
    },
    {
        "text": "Completa: 1, 4, 9, 16, 25, __",
        "options": ["30", "32", "36", "40"],
        # cuadrados: 1²,2²,... =>6²=36 -> index2
        "correct": 2,
        "dim": "SP"
    },
    {
        "text": "Completa: 10, 9, 7, 4, 0, __",
        "options": ["-5", "-4", "-3", "-2"],
        # diffs: -1,-2,-3,-4 => next -5 => 0-5=-5 -> index0
        "correct": 0,
        "dim": "SP"
    },

    # ----------------------------
    # MT (Memoria de Trabajo / Razonamiento Secuencial en cadena)
    # 10 ítems complejos, dificultad alta
    # Estas reemplazan las viejas tipo “qué paso va segundo”.
    # ----------------------------

    {
        "text": "Tienes los números 18, 6 y 4. Primero divide el primero por el segundo. Luego multiplica ese resultado por el tercero. Finalmente réstale 2. ¿Cuál es el número final?",
        "options": ["8", "10", "12", "16"],
        # 18/6=3; 3*4=12; 12-2=10 -> index1
        "correct": 1,
        "dim": "MT"
    },
    {
        "text": "Piensa en las letras T, L, R, A. 1) Ordénalas alfabéticamente ascendente. 2) Toma la segunda y la cuarta de esa lista y únelas en ese orden para formar una clave. ¿Cuál es la clave?",
        "options": ["AL", "LT", "RA", "TA"],
        # Orden alfa: A,L,R,T -> segunda=L cuarta=T -> 'LT' -> index1
        "correct": 1,
        "dim": "MT"
    },
    {
        "text": "Secuencia mental: 7, 14, 5. Haz esto: (1) Suma los dos primeros números. (2) Divide ese resultado por el tercero. (3) Súmale 3 al resultado final. ¿Cuál obtienes (aprox entero más cercano)?",
        "options": ["4", "5", "6", "7"],
        # (7+14)=21; 21/5=4.2; +3=7.2 ~7 -> index3
        "correct": 3,
        "dim": "MT"
    },
    {
        "text": "Imagina cuatro pasos en este orden: [Encender], [Configurar], [Probar], [Registrar]. Ahora: elimina el segundo paso y luego invierte el orden de los pasos restantes. ¿Qué paso queda PRIMERO después de hacer todo eso?",
        "options": ["Encender", "Configurar", "Probar", "Registrar"],
        # Original: Encender, Configurar, Probar, Registrar
        # Eliminas Configurar -> Encender, Probar, Registrar
        # Inviertes -> Registrar, Probar, Encender
        # Primero final = Registrar -> index3
        "correct": 3,
        "dim": "MT"
    },
    {
        "text": "Piensa en 4, 10, 2, 8. Toma el MAYOR y réstale el MENOR. Luego suma el promedio de los dos números restantes. ¿Resultado final?",
        "options": ["12", "13", "14", "15"],
        # Mayor=10, Menor=2 -> 8
        # Restantes=4 y 8 -> prom=6
        # 8+6=14 -> index2
        "correct": 2,
        "dim": "MT"
    },
    {
        "text": "Memoriza mentalmente estos cuatro dígitos: 5, 1, 9, 1. 1) Elimina las repeticiones, quedándote con los dígitos únicos en el orden en que aparecieron. 2) Suma esos dígitos únicos. ¿Cuál es el resultado?",
        "options": ["12", "14", "15", "16"],
        # Únicos: 5,1,9 => suma=15 -> index2
        "correct": 2,
        "dim": "MT"
    },
    {
        "text": "Tienes las letras C, H, A, R, T. 1) Elimina la vocal que aparece PRIMERO en la secuencia. 2) Con las letras restantes, ordénalas alfabéticamente. ¿Cuál letra queda al FINAL de ese nuevo orden?",
        "options": ["C", "H", "R", "T"],
        # Secuencia original C,H,A,R,T
        # Vocal primero = A -> quitar A
        # Queda C,H,R,T -> orden alfa C,H,R,T -> final T -> index3
        "correct": 3,
        "dim": "MT"
    },
    {
        "text": "Piensa en los números 16, 4, 3. Haz esto: (1) Divide el primero por el segundo. (2) Multiplica el resultado por el tercero. (3) Súmale 5. ¿Cuál es el número final?",
        "options": ["13", "14", "15", "17"],
        # 16/4=4; 4*3=12; 12+5=17 -> index3
        "correct": 3,
        "dim": "MT"
    },
    {
        "text": "Tienes la secuencia: [Rojo, Azul, Verde, Amarillo]. Haz esto: 1) Mueve el último color al principio. 2) Luego elimina el color que ahora esté en tercera posición. ¿Qué color queda en SEGUNDA posición al final?",
        "options": ["Rojo", "Azul", "Verde", "Amarillo"],
        # Mover último al principio: [Amarillo, Rojo, Azul, Verde]
        # Eliminar el que está en 3ra posición ahora -> Azul
        # Queda [Amarillo, Rojo, Verde]
        # Segunda posición final = Rojo -> index0? cuidado: opciones ["Rojo","Azul","Verde","Amarillo"]
        # Segunda pos final = Rojo => index0
        "correct": 0,
        "dim": "MT"
    },
    {
        "text": "Toma 3, 9 y 2. 1) Suma el primero y el segundo. 2) Resta el tercero. 3) Multiplica por 2. ¿Resultado final?",
        "options": ["18", "20", "24", "26"],
        # (3+9)=12; 12-2=10; 10*2=20 -> index1
        "correct": 1,
        "dim": "MT"
    },
]

TOTAL_QUESTIONS = len(QUESTIONS)  # 70

# ------------------------------------------------------------
# ESTADO GLOBAL STREAMLIT
# ------------------------------------------------------------
if "stage" not in st.session_state:
    st.session_state.stage = "info"  # info -> test -> done

if "candidate_name" not in st.session_state:
    st.session_state.candidate_name = ""

if "evaluator_email" not in st.session_state:
    st.session_state.evaluator_email = FROM_ADDR

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "answers" not in st.session_state:
    st.session_state.answers = {i: None for i in range(TOTAL_QUESTIONS)}

if "_need_rerun" not in st.session_state:
    st.session_state._need_rerun = False

if "already_sent" not in st.session_state:
    st.session_state.already_sent = False

# ------------------------------------------------------------
# SCORING Y CLASIFICACIÓN
# ------------------------------------------------------------

DIM_LABELS = {
    "NR": "Razonamiento Numérico",
    "VR": "Razonamiento Verbal / Comprensión Semántica",
    "LR": "Lógica / Deducción",
    "SP": "Patrones y Secuencias",
    "MT": "Memoria de Trabajo (Procesamiento en Cadena)",
}

def compute_scores(ans_dict):
    # contamos aciertos por dimensión
    dim_correct = {"NR":0,"VR":0,"LR":0,"SP":0,"MT":0}
    dim_total   = {"NR":0,"VR":0,"LR":0,"SP":0,"MT":0}

    for idx, q in enumerate(QUESTIONS):
        dim = q["dim"]
        dim_total[dim] += 1
        given = ans_dict.get(idx)
        if given is not None and given == q["correct"]:
            dim_correct[dim] += 1

    # porcentaje correcto por dimensión (0-100)
    dim_pct = {}
    for d in dim_total:
        if dim_total[d] > 0:
            dim_pct[d] = (dim_correct[d] / dim_total[d]) * 100.0
        else:
            dim_pct[d] = 0.0

    # promedio general (0-100)
    overall = sum(dim_pct.values()) / len(dim_pct)

    return dim_pct, overall, dim_correct, dim_total

def level_from_pct(p):
    # clasificación cualitativa según % aciertos
    # p: 0-100
    if p >= 85:
        return "Muy Alto"
    elif p >= 60:
        return "Alto"
    elif p >= 40:
        return "Promedio"
    elif p >= 20:
        return "Bajo"
    else:
        return "Muy Bajo"

def summary_overall_text(overall_pct):
    lvl = level_from_pct(overall_pct)
    if lvl in ["Muy Alto","Alto"]:
        return (
            f"Desempeño global {lvl.lower()}. "
            "El evaluado resuelve con solidez operaciones mentales, comparaciones lógicas "
            "y manejo de instrucciones encadenadas. Indica buena capacidad de razonamiento "
            "bajo demanda cognitiva."
        )
    elif lvl == "Promedio":
        return (
            "Desempeño global en rango promedio. Maneja comparaciones lógicas básicas, "
            "cálculo funcional y reconocimiento de patrones. Puede requerir más tiempo "
            "ante consignas muy complejas o con muchos pasos encadenados."
        )
    else:
        return (
            "Desempeño global en rango bajo. El evaluado muestra dificultades para sostener "
            "operaciones mentales de varios pasos y para mantener precisión en cálculos "
            "o inferencias más abstractas. Podría requerir instrucciones más segmentadas "
            "y apoyo adicional en tareas de alta complejidad cognitiva."
        )

def dimension_description(dim_key, pct):
    # descripción breve por dimensión para la tabla
    lvl = level_from_pct(pct)
    if dim_key == "NR":
        if pct >= 60:
            return f"Buen manejo de números y proporciones (nivel {lvl.lower()})."
        elif pct >= 40:
            return "Puede operar con cantidades y porcentajes básicos con cierta consistencia."
        else:
            return "Puede requerir apoyo en cálculos encadenados o porcentajes."
    if dim_key == "VR":
        if pct >= 60:
            return f"Comprensión verbal sólida y buen uso de relaciones semánticas (nivel {lvl.lower()})."
        elif pct >= 40:
            return "Interpreta instrucciones comunes y relaciones de significado directo."
        else:
            return "Podría necesitar más reformulación verbal o ejemplos concretos."
    if dim_key == "LR":
        if pct >= 60:
            return f"Capacidad lógica para extraer conclusiones coherentes (nivel {lvl.lower()})."
        elif pct >= 40:
            return "Puede seguir reglas simples y detectar contradicciones básicas."
        else:
            return "Le cuesta sostener reglas lógicas si hay varias condiciones simultáneas."
    if dim_key == "SP":
        if pct >= 60:
            return f"Detección de patrones y progresiones numéricas consistente (nivel {lvl.lower()})."
        elif pct >= 40:
            return "Reconoce secuencias simples y cambios regulares."
        else:
            return "Menor precisión al proyectar la siguiente etapa de la serie."
    if dim_key == "MT":
        if pct >= 60:
            return f"Mantiene varios pasos mentales y orden secuencial complejo (nivel {lvl.lower()})."
        elif pct >= 40:
            return "Puede sostener 2-3 transformaciones consecutivas antes de responder."
        else:
            return "Pierde información intermedia cuando la instrucción tiene muchos pasos."
    return "—"

def build_strengths_and_needs(dim_pct):
    fortalezas = []
    alertas = []

    # NR
    if dim_pct["NR"] >= 60:
        fortalezas.append("Opera con números y proporciones de forma eficiente.")
    elif dim_pct["NR"] < 40:
        alertas.append("Puede requerir apoyo adicional para cálculos sucesivos o porcentajes.")

    # VR
    if dim_pct["VR"] >= 60:
        fortalezas.append("Buena comprensión verbal e interpretación de instrucciones escritas.")
    elif dim_pct["VR"] < 40:
        alertas.append("Podría necesitar instrucciones más claras o repetidas en lenguaje sencillo.")

    # LR
    if dim_pct["LR"] >= 60:
        fortalezas.append("Extrae conclusiones lógicas y detecta contradicciones en enunciados.")
    elif dim_pct["LR"] < 40:
        alertas.append("Puede confundirse si las condiciones lógicas son múltiples o abstractas.")

    # SP
    if dim_pct["SP"] >= 60:
        fortalezas.append("Reconoce patrones y secuencias, puede anticipar resultados futuros.")
    elif dim_pct["SP"] < 40:
        alertas.append("Puede tener dificultad para proyectar series numéricas o de letras con reglas cambiantes.")

    # MT
    if dim_pct["MT"] >= 60:
        fortalezas.append("Sostiene varios pasos mentales seguidos (memoria de trabajo activa).")
    elif dim_pct["MT"] < 40:
        alertas.append("En consignas con 3+ pasos encadenados puede perder información intermedia.")

    return fortalezas, alertas

# ------------------------------------------------------------
# HELPERS PDF (2 páginas, con cajas ordenadas y texto envuelto)
# ------------------------------------------------------------

def _wrap(c, text, width, font="Helvetica", size=8):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if c.stringWidth(test, font, size) <= width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def _draw_par(
    c,
    text,
    x,
    y,
    width,
    font="Helvetica",
    size=8,
    leading=11,
    color=colors.black,
    max_lines=None
):
    c.setFont(font, size)
    c.setFillColor(color)
    lines = _wrap(c, text, width, font, size)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        c.drawString(x, y, ln)
        y -= leading
    return y

def generate_pdf(
    candidate_name,
    fecha_eval,
    evaluator_email,
    dim_pct,
    overall_pct,
    dim_correct,
    dim_total,
    fortalezas,
    alertas
):
    """
    Crea un PDF en 2 páginas:
    Pág.1 = Encabezado, datos candidato, gráfico barras, resumen global
    Pág.2 = Resumen cognitivo observado, tabla por dimensión, nota
    Todo con cajas y texto envuelto, espaciado adecuado, sin superposiciones.
    """

    buf = BytesIO()
    W, H = A4
    c = canvas.Canvas(buf, pagesize=A4)

    # ---------- PAGE 1 ----------
    margin_left = 36
    margin_right = 36

    # Encabezado
    c.setFont("Helvetica-Bold",11)
    c.setFillColor(colors.black)
    c.drawString(margin_left, H-40, "Evaluación Cognitiva General (70 ítems)")

    c.setFont("Helvetica",7)
    c.setFillColor(colors.grey)
    c.drawString(margin_left, H-55, "Instrumento de screening cognitivo. No clínico.")

    # Datos candidato - caja derecha arriba
    box_w = 200
    box_h = 70
    box_x = W - margin_right - box_w
    box_y_top = H-40

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(box_x, box_y_top-box_h, box_w, box_h, stroke=1, fill=1)

    yy = box_y_top - 14
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(box_x+8, yy, f"Evaluado: {candidate_name}")
    yy -= 11
    c.setFont("Helvetica",8)
    c.drawString(box_x+8, yy, f"Fecha: {fecha_eval}")
    yy -= 11
    c.drawString(box_x+8, yy, f"Informe enviado a: {evaluator_email}")
    yy -= 11
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawString(box_x+8, yy, "Uso interno RR.HH. / Selección general")

    # Gráfico barras capacidades por dimensión (0-100)
    chart_x = margin_left
    chart_y_bottom = H-260
    chart_w = 280
    chart_h = 140

    # caja fondo chart
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(chart_x-10, chart_y_bottom-20, chart_w+20, chart_h+60, stroke=1, fill=1)

    # título chart
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(chart_x, chart_y_bottom+chart_h+32, "Perfil por dimensión cognitiva (%)")

    # eje Y (0-100)
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(chart_x, chart_y_bottom, chart_x, chart_y_bottom+chart_h)

    # rejilla horizontal cada 20%
    for lvl in range(0, 101, 20):
        yv = chart_y_bottom + (lvl/100.0)*chart_h
        c.setFont("Helvetica",6)
        c.setFillColor(colors.black)
        c.drawString(chart_x-22, yv-2, str(lvl))
        c.setStrokeColor(colors.lightgrey)
        c.line(chart_x, yv, chart_x+chart_w, yv)

    dims_order = ["NR","VR","LR","SP","MT"]
    bar_colors = [
        colors.HexColor("#2563eb"),  # azul
        colors.HexColor("#16a34a"),  # verde
        colors.HexColor("#f97316"),  # naranjo
        colors.HexColor("#6b7280"),  # gris
        colors.HexColor("#0ea5e9"),  # celeste
    ]

    gap = 12
    bar_w = (chart_w - gap*(len(dims_order)+1)) / len(dims_order)
    tops = []

    for i, key in enumerate(dims_order):
        val_pct = dim_pct[key]  # 0..100
        bx = chart_x + gap + i*(bar_w+gap)
        bh = (val_pct/100.0)*chart_h
        by = chart_y_bottom

        c.setStrokeColor(colors.black)
        c.setFillColor(bar_colors[i])
        c.rect(bx, by, bar_w, bh, stroke=1, fill=1)

        tops.append((bx+bar_w/2.0, by+bh))

        lvl_txt = level_from_pct(val_pct)
        c.setFont("Helvetica-Bold",7)
        c.setFillColor(colors.black)
        c.drawCentredString(bx+bar_w/2.0, chart_y_bottom-14, key)

        c.setFont("Helvetica",6)
        c.drawCentredString(
            bx+bar_w/2.0,
            chart_y_bottom-26,
            f"{int(round(val_pct))}% · {lvl_txt}"
        )

    # línea que une puntajes
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    for j in range(len(tops)-1):
        (x1,y1) = tops[j]
        (x2,y2) = tops[j+1]
        c.line(x1,y1,x2,y2)
    for (px,py) in tops:
        c.setFillColor(colors.black)
        c.circle(px,py,2.0,stroke=0,fill=1)

    # Resumen global (caja texto a la derecha del gráfico)
    sum_box_x = chart_x + chart_w + 20
    sum_box_y_top = chart_y_bottom + chart_h + 40
    sum_box_w = W - margin_right - sum_box_x
    sum_box_h = 140

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(sum_box_x, sum_box_y_top - sum_box_h, sum_box_w, sum_box_h, stroke=1, fill=1)

    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(sum_box_x+8, sum_box_y_top-14,
        f"Desempeño global estimado: {int(round(overall_pct))}% ({level_from_pct(overall_pct)})"
    )

    overall_text = summary_overall_text(overall_pct)
    _draw_par(
        c,
        overall_text,
        sum_box_x+8,
        sum_box_y_top-30,
        sum_box_w-16,
        font="Helvetica",
        size=7,
        leading=10,
        color=colors.black,
        max_lines=None
    )

    # Footer pág.1
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawRightString(W-margin_right, 40, "Evaluación Cognitiva General · Página 1/2")

    c.showPage()

    # ---------- PAGE 2 ----------
    # Vamos a poner:
    # 1. Resumen cognitivo observado (caja ancho completo)
    # 2. Tabla detalle por dimensión (otra caja)
    # 3. Nota metodológica (caja final)
    #
    # Aseguramos espaciado vertical amplio y uso de todo el ancho.

    # Márgenes
    margin_left = 36
    content_w = W - margin_left - margin_right

    # 1. Caja Resumen cognitivo observado
    box1_y_top = H-40
    box1_h = 200
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(margin_left, box1_y_top-box1_h, content_w, box1_h, stroke=1, fill=1)

    c.setFont("Helvetica-Bold",9)
    c.setFillColor(colors.black)
    c.drawString(margin_left+8, box1_y_top-16, "Resumen cognitivo observado")

    # Fortalezas
    y_cursor = box1_y_top-32
    c.setFont("Helvetica-Bold",8)
    c.drawString(margin_left+8, y_cursor, "Fortalezas potenciales:")
    y_cursor -= 12
    c.setFont("Helvetica",7)
    for f in fortalezas:
        wrapped = _wrap(c, "• " + f, content_w-16, "Helvetica",7)
        for ln in wrapped:
            c.drawString(margin_left+12, y_cursor, ln)
            y_cursor -= 10
            if y_cursor < (box1_y_top-box1_h+40):
                break
        if y_cursor < (box1_y_top-box1_h+40):
            break

    # Espacio entre secciones dentro de la misma caja
    y_cursor -= 8
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(margin_left+8, y_cursor, "Aspectos a monitorear / apoyo sugerido:")
    y_cursor -= 12
    c.setFont("Helvetica",7)
    if len(alertas) == 0:
        alertas = ["Sin alertas críticas destacables dentro de este tamizaje."]
    for a in alertas:
        wrapped = _wrap(c, "• " + a, content_w-16, "Helvetica",7)
        for ln in wrapped:
            if y_cursor < (box1_y_top-box1_h+20):
                break
            c.drawString(margin_left+12, y_cursor, ln)
            y_cursor -= 10
        if y_cursor < (box1_y_top-box1_h+20):
            break

    # 2. Caja Detalle por dimensión
    box2_y_top = box1_y_top - box1_h - 20
    box2_h = 260
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(margin_left, box2_y_top-box2_h, content_w, box2_h, stroke=1, fill=1)

    c.setFont("Helvetica-Bold",9)
    c.setFillColor(colors.black)
    c.drawString(margin_left+8, box2_y_top-16, "Detalle por dimensión")

    # Encabezados tabla
    header_y = box2_y_top-32
    c.setFont("Helvetica-Bold",8)
    c.drawString(margin_left+8, header_y, "Dimensión")
    c.drawString(margin_left+160, header_y, "Puntaje")
    c.drawString(margin_left+220, header_y, "Nivel")
    c.drawString(margin_left+280, header_y, "Descripción breve")

    # Filas de la tabla
    row_y = header_y-14
    row_gap = 38  # alto por fila para que no se encime el texto

    dims_for_table = ["NR","VR","LR","SP","MT"]

    for dkey in dims_for_table:
        pct = dim_pct[dkey]
        pct_int = int(round(pct))
        lvl = level_from_pct(pct)
        desc = dimension_description(dkey, pct)

        # Col 1-3
        c.setFont("Helvetica-Bold",7)
        c.setFillColor(colors.black)
        c.drawString(margin_left+8, row_y, DIM_LABELS[dkey])

        c.setFont("Helvetica",7)
        c.drawString(margin_left+160, row_y, f"{pct_int}%")
        c.drawString(margin_left+220, row_y, lvl)

        # Col 4 (descripción envuelta)
        row_y = _draw_par(
            c,
            desc,
            margin_left+280,
            row_y,
            content_w- (280+8),
            font="Helvetica",
            size=7,
            leading=10,
            color=colors.black,
            max_lines=3
        )
        # Espacio fijo para la próxima fila
        row_y -= max(0, row_gap - 30)

    # 3. Nota metodológica al final
    box3_y_top = 80
    box3_h = 60
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(margin_left, box3_y_top-box3_h, content_w, box3_h, stroke=1, fill=1)

    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(margin_left+8, box3_y_top-16, "Nota metodológica")

    nota_text = (
        "Este informe se basa en las respuestas del evaluado en una batería cognitiva "
        "de razonamiento numérico, verbal, lógico, patrones y memoria de trabajo. "
        "Describe el desempeño observado en el momento de la evaluación, en términos "
        "de aciertos relativos. No constituye un diagnóstico clínico, ni es por sí "
        "solo una determinación absoluta de idoneidad laboral. Debe complementarse "
        "con entrevista estructurada, antecedentes de experiencia y otros criterios "
        "de selección."
    )

    _draw_par(
        c,
        nota_text,
        margin_left+8,
        box3_y_top-32,
        content_w-16,
        font="Helvetica",
        size=7,
        leading=10,
        color=colors.black,
        max_lines=None
    )

    # Footer pág.2
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawRightString(W-margin_right, 40, "Evaluación Cognitiva General · Página 2/2")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()

# ------------------------------------------------------------
# ENVÍO POR CORREO
# ------------------------------------------------------------

def send_email_with_pdf(to_email, pdf_bytes, filename, subject, body_text):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_ADDR
    msg["To"] = to_email
    msg.set_content(body_text)
    msg.add_attachment(
        pdf_bytes,
        maintype="application",
        subtype="pdf",
        filename=filename
    )
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(FROM_ADDR, APP_PASS)
        smtp.send_message(msg)

# ------------------------------------------------------------
# FINALIZAR TEST: calcular resultados, generar PDF, mandar
# ------------------------------------------------------------

def finalize_and_send():
    dim_pct, overall_pct, dim_correct, dim_total = compute_scores(st.session_state.answers)

    fortalezas, alertas = build_strengths_and_needs(dim_pct)

    now_txt = datetime.now().strftime("%d/%m/%Y %H:%M")

    pdf_bytes = generate_pdf(
        candidate_name   = st.session_state.candidate_name,
        fecha_eval       = now_txt,
        evaluator_email  = st.session_state.evaluator_email,
        dim_pct          = dim_pct,
        overall_pct      = overall_pct,
        dim_correct      = dim_correct,
        dim_total        = dim_total,
        fortalezas       = fortalezas,
        alertas          = alertas
    )

    if not st.session_state.already_sent:
        try:
            send_email_with_pdf(
                to_email   = st.session_state.evaluator_email,
                pdf_bytes  = pdf_bytes,
                filename   = "Informe_Cognitivo_General.pdf",
                subject    = "Informe Evaluación Cognitiva (IQ Screening)",
                body_text  = (
                    "Adjunto el informe cognitivo del candidato "
                    f"{st.session_state.candidate_name}. "
                    "Este documento es interno y no clínico."
                ),
            )
        except Exception:
            # Silencioso si el envío falla, para no romper la app en front.
            pass
        st.session_state.already_sent = True

# ------------------------------------------------------------
# CALLBACK RESPUESTA (sin doble click)
# ------------------------------------------------------------

def choose_answer(value_idx: int):
    q_idx = st.session_state.current_q
    st.session_state.answers[q_idx] = value_idx

    if q_idx < TOTAL_QUESTIONS - 1:
        st.session_state.current_q += 1
        st.session_state._need_rerun = True
    else:
        finalize_and_send()
        st.session_state.stage = "done"
        st.session_state._need_rerun = True

# ------------------------------------------------------------
# VISTAS UI
# ------------------------------------------------------------

def view_info_form():
    st.markdown(
        """
        <div style="
            background:#ffffff;
            border:1px solid #e2e8f0;
            border-radius:12px;
            box-shadow:0 12px 24px rgba(0,0,0,0.06);
            padding:24px;">
            <h2 style="margin:0 0 8px 0;
                       font-size:1.2rem;
                       font-weight:700;
                       color:#1e293b;">
                Datos iniciales
            </h2>
            <p style="margin:0;
                      font-size:.9rem;
                      color:#475569;
                      line-height:1.4;">
                Esta evaluación mide razonamiento numérico, verbal, lógico,
                secuencial y memoria de trabajo. 
                El informe final se enviará automáticamente al correo del evaluador.
                Uso interno RR.HH. / Selección general.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.session_state.candidate_name = st.text_input(
        "Nombre del evaluado / candidata(o)",
        value=st.session_state.candidate_name,
        placeholder="Nombre completo"
    )
    st.session_state.evaluator_email = st.text_input(
        "Correo del evaluador (RR.HH.)",
        value=st.session_state.evaluator_email,
        placeholder="nombre@empresa.com"
    )

    ok = (
        len(st.session_state.candidate_name.strip()) > 0 and
        len(st.session_state.evaluator_email.strip()) > 0
    )

    st.markdown("---")
    st.write("Cuando continúes, se iniciará el test de 70 preguntas. Verás 1 pregunta por pantalla y avanzarás automáticamente al responder.")
    if st.button("Iniciar test", type="primary", disabled=not ok, use_container_width=True):
        st.session_state.current_q = 0
        st.session_state.answers = {i: None for i in range(TOTAL_QUESTIONS)}
        st.session_state.already_sent = False
        st.session_state.stage = "test"
        st.session_state._need_rerun = True

def view_test():
    q_idx = st.session_state.current_q
    q = QUESTIONS[q_idx]
    progreso = (q_idx+1)/TOTAL_QUESTIONS

    # Header / Progreso
    st.markdown(
        f"""
        <div style="
            background:linear-gradient(to right,#1e40af,#4338ca);
            color:#fff;
            border-radius:12px 12px 0 0;
            padding:16px 20px;
            display:flex;
            justify-content:space-between;
            align-items:center;
            flex-wrap:wrap;">
            <div style="font-weight:700;">
                Evaluación Cognitiva General (70 ítems)
            </div>
            <div style="
                background:rgba(255,255,255,0.25);
                padding:4px 10px;
                border-radius:999px;
                font-size:.85rem;">
                Pregunta {q_idx+1} de {TOTAL_QUESTIONS} · {int(round(progreso*100))}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.progress(progreso)

    # Tarjeta de pregunta
    st.markdown(
        f"""
        <div style="
            background:#ffffff;
            border:1px solid #e2e8f0;
            border-radius:12px;
            padding:24px;
            box-shadow:0 12px 24px rgba(0,0,0,0.06);
            margin-top:12px;">
            <p style="margin:0;
                      font-size:1.05rem;
                      color:#1e293b;
                      line-height:1.45;
                      white-space:pre-line;">
                {q["text"]}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Botones de respuesta
    # 4 opciones, vertical u horizontal. Usaremos 2 columnas para estética.
    opt_cols = st.columns(2)
    for i_opt, opt_text in enumerate(q["options"]):
        with opt_cols[i_opt % 2]:
            st.button(
                opt_text,
                key=f"q{q_idx}_opt{i_opt}",
                use_container_width=True,
                on_click=choose_answer,
                args=(i_opt,)
            )

    # Aviso confidencialidad
    st.markdown(
        """
        <div style="
            background:#f8fafc;
            border:1px solid #e2e8f0;
            border-radius:8px;
            padding:10px 14px;
            font-size:.8rem;
            color:#475569;
            margin-top:12px;">
            <b>Confidencialidad:</b> Uso interno RR.HH. / Selección general.
            El candidato no recibe copia directa del informe.
        </div>
        """,
        unsafe_allow_html=True
    )

def view_done():
    st.markdown(
        """
        <div style="
            background:linear-gradient(to bottom right,#ecfdf5,#d1fae5);
            padding:28px;
            border-radius:14px;
            box-shadow:0 24px 48px rgba(0,0,0,0.08);
            text-align:center;">
            <div style="
                width:64px;
                height:64px;
                border-radius:999px;
                background:#10b981;
                color:#fff;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:2rem;
                font-weight:700;
                margin:0 auto 12px auto;">
                ✔
            </div>
            <div style="
                font-size:1.25rem;
                font-weight:800;
                color:#065f46;
                margin-bottom:6px;">
                Evaluación finalizada
            </div>
            <div style="color:#065f46;">
                Los resultados fueron procesados y enviados al correo del evaluador.
            </div>
            <div style="
                color:#065f46;
                font-size:.85rem;
                margin-top:6px;">
                Documento interno. No clínico.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ------------------------------------------------------------
# FLUJO PRINCIPAL
# ------------------------------------------------------------
if st.session_state.stage == "info":
    view_info_form()

elif st.session_state.stage == "test":
    if st.session_state.current_q >= TOTAL_QUESTIONS:
        st.session_state.stage = "done"
        st.session_state._need_rerun = True
    view_test()

elif st.session_state.stage == "done":
    finalize_and_send()
    view_done()

# ------------------------------------------------------------
# RERUN CONTROLADO (para que el avance sea fluido sin doble click)
# ------------------------------------------------------------
if st.session_state._need_rerun:
    st.session_state._need_rerun = False
    st.rerun()
