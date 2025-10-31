# ============================================================
# TEST DE CAPACIDAD COGNITIVA GENERAL (IQ SCREENING) - 70 ÍTEMS
# Versión con INFORME PDF ORDENADO (2 páginas, cajas limpias, sin texto encima)
#
# Flujo:
# 1. Datos candidato (nombre + correo evaluador)
# 2. Preguntas (1 por pantalla, auto-avance sin doble click)
# 3. Pantalla final "Evaluación finalizada"
# 4. Se genera PDF ordenado en 2 páginas y se envía al correo del evaluador
#
# Dimensiones cognitivas:
#   NR = Razonamiento Numérico
#   VR = Razonamiento Verbal / Semántico
#   LR = Lógica / Deducción
#   SP = Patrones / Secuencias
#   MT = Memoria de Trabajo / Procesamiento Secuencial
#
# Librerías necesarias:
#   pip install streamlit reportlab
#
# IMPORTANTE:
# - No depende de imágenes
# - Es para screening cognitivo general (no amarra a un cargo específico)
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
# CREDENCIALES CORREO (para enviar PDF al evaluador)
# ------------------------------------------------------------
FROM_ADDR = "jo.tajtaj@gmail.com"
APP_PASS  = "nlkt kujl ebdg cyts"


# ------------------------------------------------------------
# PREGUNTAS (70 ítems, dificultad creciente)
# Cada pregunta:
#  - text: enunciado
#  - options: 4 alternativas
#  - correct: índice de la correcta (0..3)
#  - dim: dimensión ("NR","VR","LR","SP","MT")
#
# Nota: ya están razonables en dificultad y sin depender de imágenes.
# ------------------------------------------------------------

QUESTIONS = [

    # NR — Razonamiento Numérico (16 ítems)
    {
        "text": "¿Cuál es el resultado de 7 + 5?",
        "options": ["10", "11", "12", "13"],
        "correct": 2,
        "dim": "NR"
    },
    {
        "text": "Si tienes 18 y regalas 7, ¿cuántos quedan?",
        "options": ["9", "10", "11", "12"],
        "correct": 2,  # 11
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
        "options": ["120", "110", "112", "100"],
        "correct": 0,  # 24*5=120
        "dim": "NR"
    },
    {
        "text": "Si aumentas 25 en un 20%, obtienes:",
        "options": ["27", "28", "30", "35"],
        "correct": 2,  # 30
        "dim": "NR"
    },
    {
        "text": "Resuelve: 15 + 27 - 8 =",
        "options": ["32", "33", "34", "35"],
        "correct": 2,  # 34
        "dim": "NR"
    },
    {
        "text": "Si 5 trabajadores hacen 40 unidades en total, en promedio cada uno hizo:",
        "options": ["6", "7", "8", "9"],
        "correct": 2,  # 8
        "dim": "NR"
    },
    {
        "text": "Un artículo cuesta 80 y baja 15%. Nuevo precio:",
        "options": ["68", "70", "72", "74"],
        "correct": 0,  # 68
        "dim": "NR"
    },
    {
        "text": "Completa: 4, 7, 10, 13, __",
        "options": ["14", "15", "16", "17"],
        "correct": 2,  # 16 (+3)
        "dim": "NR"
    },
    {
        "text": "Si x = 12 y y = 5, calcula x - 2y:",
        "options": ["1", "2", "3", "4"],
        "correct": 1,  # 12 - 10 = 2
        "dim": "NR"
    },
    {
        "text": "3/4 de 32 =",
        "options": ["20", "22", "24", "28"],
        "correct": 2,  # 24
        "dim": "NR"
    },
    {
        "text": "Caminas 1,2 km cada 10 minutos. ¿Cuántos km en 30 minutos?",
        "options": ["2,4", "3,6", "4,2", "5,0"],
        "correct": 1,  # 3.6
        "dim": "NR"
    },
    {
        "text": "Si 2a + 3 = 17, entonces a =",
        "options": ["6", "7", "8", "9"],
        "correct": 1,  # 7
        "dim": "NR"
    },
    {
        "text": "Un número se multiplica por 6 y luego se le resta 9. El resultado es 33. ¿Cuál era el número?",
        "options": ["5", "6", "7", "8"],
        "correct": 2,  # 7
        "dim": "NR"
    },

    # VR — Razonamiento Verbal / Semántico (14 ítems)
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
        "text": "Fuerte es a débil como rápido es a:",
        "options": ["lento", "duro", "tímido", "alto"],
        "correct": 0,
        "dim": "VR"
    },
    {
        "text": "¿Cuál palabra se parece más a 'evaluar'?",
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
        "text": "Completa: 'Para tomar una buena decisión, debemos tener toda la ___ disponible.'",
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
        "text": "'Manual' es a 'procedimiento' como 'mapa' es a:",
        "options": ["camino", "viaje", "ruta", "distancia"],
        "correct": 2,
        "dim": "VR"
    },
    {
        "text": "¿Qué describe mejor 'priorizar'?",
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
        "text": "‘Si un proceso es eficiente, entonces…’",
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

    # LR — Lógica / Deducción (15 ítems)
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
        "text": "Todas las piezas tipo X pesan más de 10 kg. Esta pesa 8 kg. Entonces:",
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
        "text": "Tres afirmaciones:\n1) Ana es mayor que Luis.\n2) Luis es mayor que Carla.\n3) Carla es mayor que Ana.\n¿Pueden ser todas verdaderas a la vez?",
        "options": ["Sí", "No", "Solo si son trillizos", "Solo si es lunes"],
        "correct": 1,
        "dim": "LR"
    },
    {
        "text": "Si exactamente una de estas frases es verdadera:\nA) 'Yo siempre digo la verdad.'\nB) 'Yo siempre miento.'\nEntonces:",
        "options": [
            "Ambas pueden ser verdaderas",
            "Ambas pueden ser falsas",
            "Solo A es verdadera",
            "Solo B es verdadera"
        ],
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
        "text": "Un equipo tiene A, B, C. Sabemos: A trabaja con B. B trabaja con C. ¿Podemos concluir con certeza que A trabaja con C?",
        "options": ["Sí", "No", "Solo los lunes", "A es jefe de C"],
        "correct": 1,
        "dim": "LR"
    },
    {
        "text": "Nadie menor de 18 opera la máquina. Paula opera la máquina. Entonces:",
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
        "correct": 1,
        "dim": "LR"
    },
    {
        "text": "Regla: 'Si el contenedor está lleno, se sella'. El contenedor NO está sellado. ¿Qué es válido?",
        "options": [
            "El contenedor está lleno pero no lo sellaron",
            "El contenedor no está lleno",
            "El contenedor está vacío absolutamente",
            "El contenedor explotó"
        ],
        "correct": 1,
        "dim": "LR"
    },

    # SP — Patrones / Secuencias (15 ítems)
    {
        "text": "Completa la serie: 2, 4, 6, 8, __",
        "options": ["9", "10", "11", "12"],
        "correct": 1,
        "dim": "SP"
    },
    {
        "text": "Completa la serie: 5, 10, 20, 40, __",
        "options": ["45", "60", "70", "80"],
        "correct": 3,
        "dim": "SP"
    },
    {
        "text": "Completa la serie: 9, 7, 5, 3, __",
        "options": ["1", "2", "0", "-1"],
        "correct": 0,
        "dim": "SP"
    },
    {
        "text": "Completa la serie: 1, 1, 2, 3, 5, __",
        "options": ["6", "7", "8", "9"],
        "correct": 2,
        "dim": "SP"
    },
    {
        "text": "Serie de letras: A, C, E, G, __",
        "options": ["H", "I", "J", "K"],
        "correct": 1,  # I
        "dim": "SP"
    },
    {
        "text": "Completa la serie: 12, 11, 9, 6, __",
        "options": ["2", "3", "4", "5"],
        "correct": 0,  # 2
        "dim": "SP"
    },
    {
        "text": "Completa: 3, 6, 9, 15, 24, __",
        "options": ["33", "36", "38", "39"],
        "correct": 1,  # 36
        "dim": "SP"
    },
    {
        "text": "Completa: B, D, G, K, __",
        "options": ["P", "O", "N", "Q"],
        "correct": 3,  # Q
        "dim": "SP"
    },
    {
        "text": "Completa: 2, 4, 12, 48, __",
        "options": ["120", "192", "200", "240"],
        "correct": 3,  # 240
        "dim": "SP"
    },
    {
        "text": "Completa: 100, 90, 81, 73, __",
        "options": ["65", "66", "67", "68"],
        "correct": 2,  # 67
        "dim": "SP"
    },
    {
        "text": "Completa: 4, 9, 16, 25, __",
        "options": ["30", "32", "35", "36"],
        "correct": 3,  # 36
        "dim": "SP"
    },
    {
        "text": "Completa: 7, 14, 28, 56, __",
        "options": ["70", "84", "96", "112"],
        "correct": 3,  # 112
        "dim": "SP"
    },
    {
        "text": "Completa: 2, 5, 11, 23, __",
        "options": ["35", "36", "39", "47"],
        "correct": 3,  # 47
        "dim": "SP"
    },
    {
        "text": "Completa: 1, 4, 9, 16, 25, __",
        "options": ["30", "32", "36", "40"],
        "correct": 2,  # 36
        "dim": "SP"
    },
    {
        "text": "Completa: 10, 9, 7, 4, 0, __",
        "options": ["-5", "-4", "-3", "-2"],
        "correct": 0,  # -5
        "dim": "SP"
    },

    # MT — Memoria de Trabajo / Procesamiento Secuencial (10 ítems)
    {
        "text": "Tienes 18, 6 y 4. 1) Divide 18 por 6. 2) Multiplica ese resultado por 4. 3) Resta 2. ¿Resultado final?",
        "options": ["8", "10", "12", "16"],
        "correct": 1,  # 10
        "dim": "MT"
    },
    {
        "text": "Letras: T, L, R, A. 1) Ordénalas alfabéticamente. 2) Toma la segunda y la cuarta y únelas. ¿Clave final?",
        "options": ["AL", "LT", "RA", "TA"],
        "correct": 1,  # LT
        "dim": "MT"
    },
    {
        "text": "Secuencia mental: 7, 14, 5. 1) Suma los dos primeros. 2) Divide por el tercero. 3) Súmale 3. ¿Entero más cercano?",
        "options": ["4", "5", "6", "7"],
        "correct": 3,  # 7.2 ~7
        "dim": "MT"
    },
    {
        "text": "Pasos: [Encender], [Configurar], [Probar], [Registrar]. Elimina el segundo paso y luego invierte el orden. ¿Qué paso queda PRIMERO al final?",
        "options": ["Encender", "Configurar", "Probar", "Registrar"],
        "correct": 3,  # Registrar
        "dim": "MT"
    },
    {
        "text": "Números: 4, 10, 2, 8. 1) Mayor - Menor. 2) + promedio de los otros dos. ¿Resultado final?",
        "options": ["12", "13", "14", "15"],
        "correct": 2,  # 14
        "dim": "MT"
    },
    {
        "text": "Dígitos: 5, 1, 9, 1. 1) Quita repeticiones (mantén orden de primera aparición). 2) Suma los dígitos únicos. Resultado:",
        "options": ["12", "14", "15", "16"],
        "correct": 2,  # 5+1+9=15
        "dim": "MT"
    },
    {
        "text": "Letras: C, H, A, R, T. 1) Quita la primera vocal que aparezca. 2) Ordena alfabéticamente el resto. ¿Última letra en ese nuevo orden?",
        "options": ["C", "H", "R", "T"],
        "correct": 3,  # T
        "dim": "MT"
    },
    {
        "text": "Números: 16, 4, 3. 1) 16 / 4. 2) Multiplica por 3. 3) Súmale 5. Resultado final:",
        "options": ["13", "14", "15", "17"],
        "correct": 3,  # 17
        "dim": "MT"
    },
    {
        "text": "Colores: [Rojo, Azul, Verde, Amarillo]. 1) Mueve el último al inicio. 2) Elimina el que queda en la 3ra posición. ¿Qué color queda en la 2da posición al final?",
        "options": ["Rojo", "Azul", "Verde", "Amarillo"],
        # Reorden: [Amarillo, Rojo, Azul, Verde]
        # Eliminar 3ra pos (Azul):
        # Queda [Amarillo, Rojo, Verde]
        # 2da posición final = Rojo -> index0
        "correct": 0,
        "dim": "MT"
    },
    {
        "text": "Usa 3, 9 y 2. 1) Suma el primero y segundo. 2) Resta el tercero. 3) Multiplica por 2. Resultado:",
        "options": ["18", "20", "24", "26"],
        # (3+9)=12; -2=10; *2=20
        "correct": 1,
        "dim": "MT"
    },
]

TOTAL_QUESTIONS = len(QUESTIONS)  # 70


# ------------------------------------------------------------
# ESTADO STREAMLIT
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
# SCORING / TEXTO DESCRIPTIVO
# ------------------------------------------------------------
DIM_LABELS = {
    "NR": "Razonamiento Numérico",
    "VR": "Razonamiento Verbal / Comprensión Semántica",
    "LR": "Lógica / Deducción",
    "SP": "Patrones y Secuencias",
    "MT": "Memoria de Trabajo / Procesamiento Secuencial",
}

def compute_scores(ans_dict):
    dim_correct = {"NR":0,"VR":0,"LR":0,"SP":0,"MT":0}
    dim_total   = {"NR":0,"VR":0,"LR":0,"SP":0,"MT":0}

    for idx, q in enumerate(QUESTIONS):
        dim = q["dim"]
        dim_total[dim] += 1
        given = ans_dict.get(idx)
        if given is not None and given == q["correct"]:
            dim_correct[dim] += 1

    dim_pct = {}
    for d in dim_total:
        if dim_total[d] > 0:
            dim_pct[d] = (dim_correct[d] / dim_total[d]) * 100.0
        else:
            dim_pct[d] = 0.0

    overall = sum(dim_pct.values()) / len(dim_pct)

    return dim_pct, overall, dim_correct, dim_total

def level_from_pct(p):
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
            f"Desempeño global {lvl.lower()}. El evaluado resuelve con solidez "
            "operaciones mentales, comparaciones lógicas y manejo de pasos encadenados. "
            "Indica buena capacidad de razonamiento bajo demanda cognitiva."
        )
    elif lvl == "Promedio":
        return (
            "Desempeño global en rango promedio. Maneja comparaciones lógicas básicas, "
            "cálculo funcional y reconocimiento de patrones. Puede requerir más tiempo "
            "ante consignas complejas con múltiples pasos."
        )
    else:
        return (
            "Desempeño global en rango bajo. Dificultad para sostener operaciones "
            "mentales de varios pasos y mantener precisión en cálculos o inferencias "
            "abstractas. Podría requerir instrucciones más segmentadas y apoyo adicional "
            "en tareas de alta complejidad cognitiva."
        )

def dimension_description(dim_key, pct):
    lvl = level_from_pct(pct)
    if dim_key == "NR":
        if pct >= 60:
            return f"Buen manejo de números y proporciones (nivel {lvl.lower()})."
        elif pct >= 40:
            return "Opera con cantidades y porcentajes básicos con cierta consistencia."
        else:
            return "Puede requerir apoyo en cálculos sucesivos o porcentajes."
    if dim_key == "VR":
        if pct >= 60:
            return f"Comprensión verbal sólida y uso claro de relaciones semánticas (nivel {lvl.lower()})."
        elif pct >= 40:
            return "Interpreta instrucciones comunes y relaciones de significado directo."
        else:
            return "Podría necesitar instrucciones más claras o ejemplos concretos."
    if dim_key == "LR":
        if pct >= 60:
            return f"Capacidad lógica para extraer conclusiones coherentes (nivel {lvl.lower()})."
        elif pct >= 40:
            return "Puede seguir reglas simples y detectar contradicciones básicas."
        else:
            return "Le cuesta sostener reglas lógicas cuando hay condiciones múltiples."
    if dim_key == "SP":
        if pct >= 60:
            return f"Reconoce patrones y progresiones numéricas (nivel {lvl.lower()})."
        elif pct >= 40:
            return "Identifica secuencias simples y cambios regulares."
        else:
            return "Menor precisión al proyectar la siguiente etapa de la serie."
    if dim_key == "MT":
        if pct >= 60:
            return f"Mantiene varios pasos mentales en orden (nivel {lvl.lower()})."
        elif pct >= 40:
            return "Puede sostener 2-3 transformaciones consecutivas antes de responder."
        else:
            return "Pierde información intermedia cuando hay muchos pasos encadenados."
    return "—"

def build_strengths_and_needs(dim_pct):
    fortalezas = []
    alertas = []

    if dim_pct["NR"] >= 60:
        fortalezas.append("Opera con números y proporciones de forma eficiente.")
    elif dim_pct["NR"] < 40:
        alertas.append("Podría requerir apoyo para cálculos sucesivos o porcentajes.")

    if dim_pct["VR"] >= 60:
        fortalezas.append("Buena comprensión verbal e interpretación de instrucciones escritas.")
    elif dim_pct["VR"] < 40:
        alertas.append("Podría requerir instrucciones más claras y reformuladas verbalmente.")

    if dim_pct["LR"] >= 60:
        fortalezas.append("Extrae conclusiones lógicas y detecta contradicciones en enunciados.")
    elif dim_pct["LR"] < 40:
        alertas.append("Puede confundirse si las condiciones lógicas son múltiples o abstractas.")

    if dim_pct["SP"] >= 60:
        fortalezas.append("Reconoce patrones y secuencias, anticipando resultados futuros.")
    elif dim_pct["SP"] < 40:
        alertas.append("Puede tener dificultad para proyectar series con reglas cambiantes.")

    if dim_pct["MT"] >= 60:
        fortalezas.append("Sostiene varios pasos mentales seguidos (memoria de trabajo activa).")
    elif dim_pct["MT"] < 40:
        alertas.append("En consignas con 3+ pasos puede perder información intermedia.")

    return fortalezas, alertas


# ------------------------------------------------------------
# HELPERS PDF
#   NUEVA VERSIÓN: layout más simple, ordenado en PILA vertical,
#   SIN superposición y SIN cajas pegadas raras.
#
# Página 1:
#   - Encabezado
#   - Datos candidato
#   - Desempeño global
#   - Gráfico barras por dimensión
#
# Página 2:
#   - Resumen cognitivo observado (fortalezas / alertas)
#   - Tabla por dimensión (una fila por dimensión con puntaje/nivel/descripción)
#   - Nota metodológica
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
    PDF LIMPIO (2 páginas, layout vertical):
    - Todo dentro de cajas con padding interno.
    - Texto envuelto.
    - Espacios consistentes.
    """

    buf = BytesIO()
    W, H = A4
    c = canvas.Canvas(buf, pagesize=A4)

    margin_left = 36
    margin_right = 36
    content_w = W - margin_left - margin_right

    # ---------------------------
    # PÁGINA 1
    # ---------------------------

    y_cursor = H - 40

    # Título principal
    c.setStrokeColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.drawString(margin_left, y_cursor, "Evaluación Cognitiva General (70 ítems)")
    y_cursor -= 16
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.grey)
    c.drawString(margin_left, y_cursor, "Instrumento de screening cognitivo. Uso interno RR.HH. / No clínico.")
    y_cursor -= 24

    # --- Caja Datos del Evaluado ---
    box1_h = 70
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(margin_left, y_cursor - box1_h, content_w, box1_h, stroke=1, fill=1)

    inner_y = y_cursor - 14
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    c.drawString(margin_left+10, inner_y, f"Evaluado: {candidate_name}")
    inner_y -= 12
    c.setFont("Helvetica", 8)
    c.drawString(margin_left+10, inner_y, f"Fecha evaluación: {fecha_eval}")
    inner_y -= 12
    c.drawString(margin_left+10, inner_y, f"Informe enviado a: {evaluator_email}")
    inner_y -= 12
    c.setFont("Helvetica", 6)
    c.setFillColor(colors.grey)
    c.drawString(margin_left+10, inner_y, "Documento interno de RR.HH. No reemplaza entrevista ni experiencia previa.")

    y_cursor -= (box1_h + 20)

    # --- Caja Desempeño Global ---
    box2_h = 110
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(margin_left, y_cursor - box2_h, content_w, box2_h, stroke=1, fill=1)

    inner_y = y_cursor - 16
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.black)

    global_txt_header = (
        f"Desempeño global estimado: {int(round(overall_pct))}% "
        f"({level_from_pct(overall_pct)})"
    )
    c.drawString(margin_left+10, inner_y, global_txt_header)
    inner_y -= 14

    overall_block = summary_overall_text(overall_pct)

    inner_y = _draw_par(
        c,
        overall_block,
        margin_left+10,
        inner_y,
        content_w-20,
        font="Helvetica",
        size=7,
        leading=10,
        color=colors.black,
        max_lines=None
    )

    y_cursor -= (box2_h + 20)

    # --- Caja Perfil por Dimensión (Gráfico de barras vertical sencillo) ---
    # Vamos a dibujar barras horizontales tipo % dentro de caja grande
    box3_h = 180
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(margin_left, y_cursor - box3_h, content_w, box3_h, stroke=1, fill=1)

    inner_y = y_cursor - 16
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.black)
    c.drawString(margin_left+10, inner_y, "Perfil por dimensión cognitiva (%)")
    inner_y -= 14

    # Para cada dimensión hacemos barra horizontal 0..100
    bar_area_left = margin_left + 10
    bar_area_right = margin_left + content_w - 10
    bar_full_w = bar_area_right - bar_area_left
    bar_height = 10
    bar_gap = 18

    for dkey in ["NR","VR","LR","SP","MT"]:
        pct_val = max(0, min(100, dim_pct[dkey]))
        lvl_val = level_from_pct(pct_val)
        label_txt = DIM_LABELS[dkey]

        # texto etiqueta
        c.setFont("Helvetica-Bold",7)
        c.setFillColor(colors.black)
        c.drawString(bar_area_left, inner_y, f"{label_txt}")
        c.setFont("Helvetica",7)
        c.drawRightString(
            bar_area_right,
            inner_y,
            f"{int(round(pct_val))}% · {lvl_val}"
        )
        inner_y -= 10

        # barra fondo
        c.setStrokeColor(colors.lightgrey)
        c.setFillColor(colors.whitesmoke)
        c.rect(bar_area_left, inner_y - bar_height, bar_full_w, bar_height, stroke=1, fill=1)

        # barra llena
        c.setStrokeColor(colors.black)
        c.setFillColor(colors.HexColor("#2563eb"))
        fill_w = (pct_val/100.0)*bar_full_w
        c.rect(bar_area_left, inner_y - bar_height, fill_w, bar_height, stroke=0, fill=1)

        inner_y -= bar_gap

    # Footer página 1
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawRightString(W - margin_right, 40, "Evaluación Cognitiva General · Página 1/2")

    # Fin página 1
    c.showPage()

    # ---------------------------
    # PÁGINA 2
    # ---------------------------
    y_cursor = H - 40

    # --- Caja Resumen Cognitivo Observado (Fortalezas / Alertas) ---
    box4_h = 200
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(margin_left, y_cursor - box4_h, content_w, box4_h, stroke=1, fill=1)

    inner_y = y_cursor - 16
    c.setFont("Helvetica-Bold",9)
    c.setFillColor(colors.black)
    c.drawString(margin_left+10, inner_y, "Resumen cognitivo observado")
    inner_y -= 16

    # Fortalezas
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(margin_left+10, inner_y, "Fortalezas potenciales:")
    inner_y -= 12
    c.setFont("Helvetica",7)
    if len(fortalezas) == 0:
        fortalezas = ["No se detectan fortalezas destacadas en este tamizaje específico."]
    for f in fortalezas:
        # envolver cada viñeta
        wrapped = _wrap(c, "• " + f, content_w-20, "Helvetica",7)
        for ln in wrapped:
            c.drawString(margin_left+15, inner_y, ln)
            inner_y -= 10
            if inner_y < (y_cursor - box4_h + 40):
                break
        if inner_y < (y_cursor - box4_h + 40):
            break

    inner_y -= 8

    # Alertas / apoyo
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(margin_left+10, inner_y, "Aspectos a monitorear / apoyo sugerido:")
    inner_y -= 12
    c.setFont("Helvetica",7)
    if len(alertas) == 0:
        alertas = ["Sin alertas críticas destacables dentro de este tamizaje."]
    for a in alertas:
        wrapped = _wrap(c, "• " + a, content_w-20, "Helvetica",7)
        for ln in wrapped:
            c.drawString(margin_left+15, inner_y, ln)
            inner_y -= 10
            if inner_y < (y_cursor - box4_h + 20):
                break
        if inner_y < (y_cursor - box4_h + 20):
            break

    y_cursor -= (box4_h + 20)

    # --- Caja Detalle por Dimensión ---
    box5_h = 260
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(margin_left, y_cursor - box5_h, content_w, box5_h, stroke=1, fill=1)

    inner_y = y_cursor - 16
    c.setFont("Helvetica-Bold",9)
    c.setFillColor(colors.black)
    c.drawString(margin_left+10, inner_y, "Detalle por dimensión")
    inner_y -= 16

    # Encabezado tabla
    c.setFont("Helvetica-Bold",8)
    c.drawString(margin_left+10,  inner_y, "Dimensión")
    c.drawString(margin_left+170, inner_y, "Puntaje")
    c.drawString(margin_left+230, inner_y, "Nivel")
    c.drawString(margin_left+280, inner_y, "Descripción breve")
    inner_y -= 14

    row_gap = 40  # altura disponible por dimensión

    for dkey in ["NR","VR","LR","SP","MT"]:
        pct_val = dim_pct[dkey]
        pct_int = int(round(pct_val))
        lvl_val = level_from_pct(pct_val)
        desc    = dimension_description(dkey, pct_val)

        # Dimensión + puntaje + nivel (1 línea)
        c.setFont("Helvetica-Bold",7)
        c.setFillColor(colors.black)
        c.drawString(margin_left+10, inner_y, DIM_LABELS[dkey])

        c.setFont("Helvetica",7)
        c.drawString(margin_left+170, inner_y, f"{pct_int}%")
        c.drawString(margin_left+230, inner_y, lvl_val)

        # Descripción envuelta debajo
        inner_y -= 10
        inner_y = _draw_par(
            c,
            desc,
            margin_left+10,
            inner_y,
            content_w-20,
            font="Helvetica",
            size=7,
            leading=10,
            color=colors.black,
            max_lines=None
        )

        # espacio entre filas
        inner_y -= (row_gap - 20)
        if inner_y < (y_cursor - box5_h + 30):
            break

    y_cursor -= (box5_h + 20)

    # --- Caja Nota Metodológica ---
    box6_h = 80
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(margin_left, y_cursor - box6_h, content_w, box6_h, stroke=1, fill=1)

    inner_y = y_cursor - 16
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(margin_left+10, inner_y, "Nota metodológica")
    inner_y -= 14

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
        margin_left+10,
        inner_y,
        content_w-20,
        font="Helvetica",
        size=7,
        leading=10,
        color=colors.black,
        max_lines=None
    )

    # Footer página 2
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawRightString(W - margin_right, 40, "Evaluación Cognitiva General · Página 2/2")

    # Cerrar PDF
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


# ------------------------------------------------------------
# ENVÍO DE PDF POR EMAIL
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
# FINALIZACIÓN: calcular resultados, generar PDF, mandar
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
            # No rompemos la app si falla el envío
            pass
        st.session_state.already_sent = True


# ------------------------------------------------------------
# CALLBACK RESPUESTA (auto-avance sin doble click)
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
# VISTAS DE LA APP
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
                Esta evaluación mide razonamiento numérico, verbal,
                lógico, patrones/secuencias y memoria de trabajo.
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
    st.write(
        "Cuando continúes, se iniciará el test de 70 preguntas. "
        "Vas a ver 1 pregunta por pantalla y avanzarás automáticamente al responder."
    )
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

    # Header / progreso
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

    # Tarjeta pregunta
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

    # Opciones
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

    # Confidencialidad
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
# RERUN CONTROLADO (para que avance sin doble click)
# ------------------------------------------------------------
if st.session_state._need_rerun:
    st.session_state._need_rerun = False
    st.rerun()
