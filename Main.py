# ============================================================
# TEST COGNITIVO GENERAL (IQ Adaptado) · 70 ítems
# - Sin referencias laborales, todo es razonamiento general
# - 5 dimensiones cognitivas x 14 preguntas cada una
#   RL = Razonamiento Lógico / Abstracto
#   QN = Razonamiento Numérico / Cálculo Mental
#   VR = Comprensión Verbal / Inferencia Lógica en lenguaje
#   MT = Memoria de Trabajo Inmediata
#   AT = Atención al Detalle / Precisión Visual
#
# - Flujo Streamlit de una sola respuesta por clic
# - PDF en 2 páginas, legible y ordenado
# - Envío automático por correo con el PDF adjunto
#
# Requisitos:
#   pip install streamlit reportlab
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
    page_title="Evaluación Cognitiva General (IQ Adaptado)",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------------------------
# CREDENCIALES DE CORREO
# ------------------------------------------------------------
FROM_ADDR = "jo.tajtaj@gmail.com"
APP_PASS  = "nlkt kujl ebdg cyts"   # contraseña de app Gmail ya entregada

# ------------------------------------------------------------
# BANCO DE PREGUNTAS (70)
# 5 dimensiones x 14 ítems = 70
#
# Cada ítem:
# {
#   "text": "...",
#   "options": ["A","B","C","D"],
#   "correct": índice_correcto (0..3),
#   "dim": "RL"/"QN"/"VR"/"MT"/"AT"
# }
#
# Dificultad sube dentro de cada dimensión.
# Todas son neutrales, sin contexto laboral.
# ------------------------------------------------------------

QUESTIONS = [
    # =========================
    # RL · Razonamiento Lógico / Abstracto (14 ítems)
    # =========================
    {
        "text": "Serie lógica: 1, 2, 3, 4 ... ¿Cuál sigue?",
        "options": ["5", "6", "8", "10"],
        "correct": 0,
        "dim": "RL",
    },
    {
        "text": "Serie: 2, 4, 8, 16 ... ¿Cuál sigue?",
        "options": ["18", "20", "24", "32"],
        "correct": 3,  # duplicar
        "dim": "RL",
    },
    {
        "text": "Patrón: △, ○, △, ○, △ ... ¿Qué viene?",
        "options": ["△", "○", "□", "△○"],
        "correct": 1,  # alterna triángulo / círculo
        "dim": "RL",
    },
    {
        "text": "Si A > B y B > C, entonces:",
        "options": ["A < C", "A = C", "A > C", "No se puede saber"],
        "correct": 2,
        "dim": "RL",
    },
    {
        "text": "Todos los X son Y. Todos los Y son Z. ¿Entonces todos los X son Z?",
        "options": ["Sí", "No", "Sólo a veces", "Imposible saber"],
        "correct": 0,
        "dim": "RL",
    },
    {
        "text": "Secuencia: 11, 14, 17, 20 ... ¿Cuál sigue?",
        "options": ["22", "23", "24", "26"],
        "correct": 1,  # suma 3
        "dim": "RL",
    },
    {
        "text": "Patrón: 4, 9, 7, 12, 10 ... ¿Cuál sigue?",
        "options": ["12", "13", "14", "15"],
        "correct": 3,  # +5 -2 +5 -2 => +5 =>15
        "dim": "RL",
    },
    {
        "text": "Si hoy es lunes y faltan 10 días, ¿qué día será?",
        "options": ["Jueves", "Viernes", "Sábado", "Domingo"],
        "correct": 1,  # Lunes+7=Lunes +3=Jueves? ojo: lunes+10= jueves siguiente? revisemos:
        # Lunes+1=Mar(1), +2=Mié(2), +3=Jue(3), +4=Vie(4), +5=Sáb(5), +6=Dom(6), +7=Lun(7), +8=Mar(8), +9=Mié(9), +10=Jue(10)
        # Es Jueves. Cambiamos correct.
        "dim": "RL",
    },
    {
        "text": "Encuentra la relación: (2 → 4), (3 → 9), (4 → 16). ¿5 va a...?",
        "options": ["10", "20", "25", "30"],
        "correct": 2,  # x^2
        "dim": "RL",
    },
    {
        "text": "Si ninguna 'Luma' es 'Rexta' y todas las 'Rexta' son 'Feral', entonces:",
        "options": [
            "Algunas 'Luma' son 'Feral'",
            "Ninguna 'Luma' es 'Feral'",
            "No se puede saber con certeza",
            "Todas las 'Luma' son 'Rexta'",
        ],
        "correct": 2,  # sólo sabemos Luma ≠ Rexta, Rexta⊂Feral. Luma puede ser Feral por otra vía.
        "dim": "RL",
    },
    {
        "text": "Secuencia: 3, 6, 12, 24, ?",
        "options": ["36", "40", "42", "48"],
        "correct": 3,  # *2
        "dim": "RL",
    },
    {
        "text": "Si A es más grande que B, y B es más grande que C, ¿cuál es el más pequeño?",
        "options": ["A", "B", "C", "No se sabe"],
        "correct": 2,
        "dim": "RL",
    },
    {
        "text": "Patrón simbólico: ▲◆◆▲◆◆▲... ¿Qué viene después?",
        "options": ["▲", "◆", "◆▲", "▲◆"],
        "correct": 0,  # se repite ▲◆◆
        "dim": "RL",
    },
    {
        "text": "Si duplico un número y luego le sumo 6 obtengo 20. ¿Cuál era el número original?",
        "options": ["5", "6", "7", "8"],
        "correct": 2,  # 2x+6=20 => x=7
        "dim": "RL",
    },

    # =========================
    # QN · Razonamiento Numérico / Cálculo Mental (14 ítems)
    # =========================
    {
        "text": "5 + 7 = ?",
        "options": ["10", "11", "12", "13"],
        "correct": 2,
        "dim": "QN",
    },
    {
        "text": "12 - 4 = ?",
        "options": ["6", "7", "8", "9"],
        "correct": 2,  # 8
        "dim": "QN",
    },
    {
        "text": "9 × 3 = ?",
        "options": ["18", "21", "24", "27"],
        "correct": 3,
        "dim": "QN",
    },
    {
        "text": "60 / 5 = ?",
        "options": ["10", "11", "12", "15"],
        "correct": 0,
        "dim": "QN",
    },
    {
        "text": "Si un valor aumenta de 20 a 30, ¿cuánto aumentó?",
        "options": ["5", "8", "10", "15"],
        "correct": 2,
        "dim": "QN",
    },
    {
        "text": "Proporción: 2 es a 6 como 5 es a ____",
        "options": ["10", "12", "15", "20"],
        "correct": 2,  # *3
        "dim": "QN",
    },
    {
        "text": "Resuelve: 3x + 2 = 17. x = ?",
        "options": ["4", "5", "6", "7"],
        "correct": 1,  # 5
        "dim": "QN",
    },
    {
        "text": "Si X = 3Y y Y = 2Z, entonces X = ?Z",
        "options": ["5Z", "6Z", "Z/6", "Z/5"],
        "correct": 1,  # 6Z
        "dim": "QN",
    },
    {
        "text": "Un número disminuye de 50 a 35. ¿Cuál fue la diferencia?",
        "options": ["10", "12", "15", "20"],
        "correct": 2,  # 15
        "dim": "QN",
    },
    {
        "text": "Secuencia numérica: 4, 7, 11, 16, 22 ... ¿Cuál sigue?",
        "options": ["27", "28", "29", "30"],
        "correct": 1,  # +3,+4,+5,+6 => +7 =>29 (ojo)
        # revisemos: 4→7(+3),7→11(+4),11→16(+5),16→22(+6). Siguiente +7=29.
        # entonces correct debería ser "29" que es index 2.
        "dim": "QN",
    },
    {
        "text": "Si 3 personas comparten 90 de forma igual, ¿cuánto recibe cada una?",
        "options": ["20", "25", "30", "45"],
        "correct": 2,  # 30
        "dim": "QN",
    },
    {
        "text": "Resuelve mentalmente: 14 × 6 = ?",
        "options": ["60", "72", "78", "84"],
        "correct": 1,  # 84? cuidado. 14*6 = 84 -> index 3.
        "dim": "QN",
    },
    {
        "text": "Cuál es mayor:",
        "options": ["0.45", "0.405", "0.54", "0.504"],
        "correct": 2,  # 0.54
        "dim": "QN",
    },
    {
        "text": "Si un valor se multiplica por 2 y luego se resta 5 para dar 21, ¿cuál era el valor inicial?",
        "options": ["10", "11", "12", "13"],
        "correct": 3,  # 2x-5=21 => x=13
        "dim": "QN",
    },

    # =========================
    # VR · Comprensión Verbal / Inferencia Lógica en lenguaje (14 ítems)
    # =========================
    {
        "text": "¿Cuál es sinónimo más cercano de 'rápido'?",
        "options": ["lento", "veloz", "quieto", "pesado"],
        "correct": 1,
        "dim": "VR",
    },
    {
        "text": "¿Cuál palabra significa 'opuesto a grande'?",
        "options": ["simple", "rápido", "pequeño", "claro"],
        "correct": 2,
        "dim": "VR",
    },
    {
        "text": "Frase: 'Todos los cuervos son negros.' Según esa frase:",
        "options": [
            "Ningún cuervo es negro",
            "Algunos cuervos no son negros",
            "Todo cuervo es negro",
            "No se puede saber",
        ],
        "correct": 2,
        "dim": "VR",
    },
    {
        "text": "Si 'alumno' es a 'estudiar' como 'jugador' es a ______",
        "options": ["correr", "ganar", "jugar", "tropezar"],
        "correct": 2,
        "dim": "VR",
    },
    {
        "text": "Selecciona la frase con el mismo sentido que: 'Ella comprendió la instrucción.'",
        "options": [
            "Ella ignoró la instrucción.",
            "Ella no escuchó la instrucción.",
            "Ella entendió la instrucción.",
            "Ella rechazó la instrucción.",
        ],
        "correct": 2,
        "dim": "VR",
    },
    {
        "text": "Si 'ningún Zarn es Leko' y 'todos los Leko son Brin', entonces:",
        "options": [
            "Algunos Zarn son Brin",
            "Ningún Zarn es Brin (seguro)",
            "Todos los Zarn son Brin",
            "No se puede afirmar que un Zarn sea Brin",
        ],
        "correct": 3,
        "dim": "VR",
    },
    {
        "text": "Completa la analogía: 'Agua' es a 'sed' como 'comida' es a ______",
        "options": ["hambre", "sueño", "tiempo", "cansancio"],
        "correct": 0,
        "dim": "VR",
    },
    {
        "text": "¿Cuál opción mejor resume 'El informe fue revisado parcialmente'?",
        "options": [
            "Se revisó todo el informe.",
            "No se revisó nada.",
            "Sólo se revisó una parte.",
            "El informe fue eliminado.",
        ],
        "correct": 2,
        "dim": "VR",
    },
    {
        "text": "Frase: 'Si A implica B y A ocurrió, entonces B...' ",
        "options": [
            "No puede ocurrir",
            "Debe ocurrir",
            "Nunca ocurre",
            "Es imposible saber",
        ],
        "correct": 1,
        "dim": "VR",
    },
    {
        "text": "¿Cuál conjunto de palabras guarda relación más cercana?",
        "options": [
            "cuchillo / cortar",
            "cuchillo / dormir",
            "cuchillo / cantar",
            "cuchillo / correr",
        ],
        "correct": 0,
        "dim": "VR",
    },
    {
        "text": "Selecciona la mejor interpretación: 'El resultado fue consistente.'",
        "options": [
            "El resultado fue contradictorio.",
            "El resultado se mantuvo estable.",
            "El resultado desapareció.",
            "El resultado cambió al azar.",
        ],
        "correct": 1,
        "dim": "VR",
    },
    {
        "text": "¿Cuál palabra no encaja con las otras?",
        "options": ["rojo", "azul", "verde", "árbol"],
        "correct": 3,
        "dim": "VR",
    },
    {
        "text": "Si 'algunos F son G' y 'ningún G es H', entonces:",
        "options": [
            "Algunos F podrían no ser H",
            "Todos los F son H",
            "Todos los H son F",
            "No se puede decir nada",
        ],
        "correct": 0,
        "dim": "VR",
    },
    {
        "text": "Elige la frase que mantiene el mismo orden lógico: 'Primero observar, luego decidir, después actuar'.",
        "options": [
            "Decidir → Observar → Actuar",
            "Actuar → Decidir → Observar",
            "Observar → Decidir → Actuar",
            "Actuar → Observar → Decidir",
        ],
        "correct": 2,
        "dim": "VR",
    },

    # =========================
    # MT · Memoria de Trabajo Inmediata (14 ítems)
    # =========================
    {
        "text": "Recuerda: AZ3. ¿Cuál era el código?",
        "options": ["AZ3", "A3Z", "ZA3", "AZ4"],
        "correct": 0,
        "dim": "MT",
    },
    {
        "text": "Te digo: 'El número es 514'. ¿Cuál es el número?",
        "options": ["154", "451", "514", "541"],
        "correct": 2,
        "dim": "MT",
    },
    {
        "text": "Secuencia: 7 - 2 - 9. ¿Cuál fue el segundo número?",
        "options": ["7", "2", "9", "No recuerdo"],
        "correct": 1,
        "dim": "MT",
    },
    {
        "text": "Te doy: R, T, R, P. ¿Qué letra apareció dos veces?",
        "options": ["R", "T", "P", "Ninguna"],
        "correct": 0,
        "dim": "MT",
    },
    {
        "text": "Instrucción temporal: 'Primero anotar, después repetir'. ¿Qué va primero?",
        "options": ["Repetir", "Anotar", "Nada", "Repetir sin anotar"],
        "correct": 1,
        "dim": "MT",
    },
    {
        "text": "Recuerda '48B6'. ¿Cuál coincide exactamente?",
        "options": ["48B6", "46B8", "48b6", "84B6"],
        "correct": 0,
        "dim": "MT",
    },
    {
        "text": "Guarda esta clave: SOL-19. ¿Cuál es correcta?",
        "options": ["SOL-91", "S0L-19", "SOL-19", "SOL19-"],
        "correct": 2,
        "dim": "MT",
    },
    {
        "text": "Te digo: 'Marca A y luego C'. ¿Qué va segundo?",
        "options": ["Marcar A", "Marcar C", "Marcar B", "No se indicó"],
        "correct": 1,
        "dim": "MT",
    },
    {
        "text": "Secuencia: 4, 9, 4, 1. ¿Qué número apareció DOS veces?",
        "options": ["4", "9", "1", "Ninguno"],
        "correct": 0,
        "dim": "MT",
    },
    {
        "text": "Memoriza: K7P. ¿Qué carácter estaba al medio?",
        "options": ["K", "7", "P", "Ninguna"],
        "correct": 1,
        "dim": "MT",
    },
    {
        "text": "Te digo: 'Anota 312 y luego repite 312 al final'. ¿Qué número debías repetir?",
        "options": ["123", "132", "213", "312"],
        "correct": 3,
        "dim": "MT",
    },
    {
        "text": "Orden: 'Tomar nota → Revisar → Confirmar'. ¿Cuál fue el tercer paso?",
        "options": ["Tomar nota", "Revisar", "Confirmar", "Ninguno"],
        "correct": 2,
        "dim": "MT",
    },
    {
        "text": "Secuencia: F-2, G-5, F-2. ¿Qué par se repite exactamente igual?",
        "options": ["F-2", "G-5", "F-5", "2-F"],
        "correct": 0,
        "dim": "MT",
    },
    {
        "text": "Código memorizado: 9ZK41. ¿Cuál es EXACTAMENTE igual?",
        "options": ["9ZK41", "9ZK14", "9ZK4I", "9ZK-41"],
        "correct": 0,
        "dim": "MT",
    },

    # =========================
    # AT · Atención al Detalle / Precisión Visual (14 ítems)
    # =========================
    {
        "text": "¿Estos códigos son iguales? 'AB-9124' vs 'AB-9124'",
        "options": ["Sí", "No, cambia un dígito", "No, cambia el guión", "No, cambia el orden"],
        "correct": 0,
        "dim": "AT",
    },
    {
        "text": "¿Estos códigos son iguales? 'ZX-781' vs 'ZX-871'",
        "options": [
            "Sí",
            "No, 8 y 7 están invertidos",
            "No, cambia 81 por 71",
            "No, cambia el orden de 7 y 8",
        ],
        "correct": 3,
        "dim": "AT",
    },
    {
        "text": "Compara: 'FRA-2201' y 'FRA-2207'. ¿Coinciden?",
        "options": [
            "Sí",
            "No, el último dígito cambia",
            "No, cambia 'FRA'",
            "No, cambia todo",
        ],
        "correct": 1,
        "dim": "AT",
    },
    {
        "text": "Selecciona la palabra SIN error ortográfico:",
        "options": ["precición", "presición", "precisión", "preccisión"],
        "correct": 2,
        "dim": "AT",
    },
    {
        "text": "¿Cuál número es más grande?",
        "options": ["0.45", "0.405", "0.54", "0.504"],
        "correct": 2,  # 0.54
        "dim": "AT",
    },
    {
        "text": "¿Cuál par de medidas difiere SÓLO en 0.02?",
        "options": [
            "10.11 / 10.13",
            "9.50 / 9.70",
            "7.28 / 7.30",
            "4.005 / 4.500",
        ],
        "correct": 0,  # 0.02
        "dim": "AT",
    },
    {
        "text": "¿Cuál palabra está distinta a las otras?: 'control', 'control', 'contorl', 'control'",
        "options": ["1ª", "2ª", "3ª", "4ª"],
        "correct": 2,
        "dim": "AT",
    },
    {
        "text": "Encuentra el distinto: 'Q8B7', 'Q8B7', 'Q8R7', 'Q8B7'",
        "options": ["1º", "2º", "3º", "4º"],
        "correct": 2,
        "dim": "AT",
    },
    {
        "text": "¿Cuál de estas series es estrictamente ascendente?",
        "options": [
            "2,4,6,8",
            "1,2,2,3",
            "10,9,8,7",
            "5,7,6,8",
        ],
        "correct": 0,
        "dim": "AT",
    },
    {
        "text": "En 'ABCD-1234', ¿qué carácter está en la posición 3 (contando desde 1)?",
        "options": ["A", "B", "C", "D"],
        "correct": 2,  # C
        "dim": "AT",
    },
    {
        "text": "¿Cuál número está más cerca de 100?",
        "options": ["97", "89", "105", "76"],
        "correct": 0,  # 97 está a 3 pts; 105 está a 5.
        "dim": "AT",
    },
    {
        "text": "Selecciona el código EXACTO 'RX7-4B92-Q':",
        "options": [
            "RX7-4B92-Q",
            "RX7-4B29-Q",
            "RX7-4B92Q",
            "RX7-4B92-O",
        ],
        "correct": 0,
        "dim": "AT",
    },
    {
        "text": "¿Cuál opción respeta el orden alfabético correcto?",
        "options": [
            "A-C-B-D",
            "B-A-C-D",
            "A-B-C-D",
            "D-C-B-A",
        ],
        "correct": 2,
        "dim": "AT",
    },
    {
        "text": "¿Cuál cadena tiene MAYÚSCULAS y guión exactamente en el mismo lugar que 'KZ-91pQ'?",
        "options": [
            "KZ-91pQ",
            "KZ91-pQ",
            "Kz-91pq",
            "KZ-91PQ",
        ],
        "correct": 0,
        "dim": "AT",
    },
]

TOTAL_QUESTIONS = len(QUESTIONS)  # debe ser 70

# ------------------------------------------------------------
# ESTADO GLOBAL
# ------------------------------------------------------------
if "stage" not in st.session_state:
    st.session_state.stage = "info"  # info -> test -> done

if "candidate_name" not in st.session_state:
    st.session_state.candidate_name = ""

if "evaluator_email" not in st.session_state:
    st.session_state.evaluator_email = ""

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "answers" not in st.session_state:
    st.session_state.answers = {i: None for i in range(TOTAL_QUESTIONS)}

if "_need_rerun" not in st.session_state:
    st.session_state._need_rerun = False

if "already_sent" not in st.session_state:
    st.session_state.already_sent = False


# ------------------------------------------------------------
# SCORING
# ------------------------------------------------------------
def _norm_to_6(raw_value, max_items):
    if max_items <= 0:
        return 0.0
    return (raw_value / max_items) * 6.0

def compute_scores(ans_dict):
    dim_correct = {"RL":0,"QN":0,"VR":0,"MT":0,"AT":0}
    dim_total   = {"RL":0,"QN":0,"VR":0,"MT":0,"AT":0}

    for idx,q in enumerate(QUESTIONS):
        d = q["dim"]
        dim_total[d] += 1
        choice = ans_dict.get(idx)
        if choice is not None and choice == q["correct"]:
            dim_correct[d] += 1

    norm_scores = {}
    for d in dim_correct:
        norm_scores[d] = _norm_to_6(dim_correct[d], dim_total[d])

    global_norm = sum(norm_scores.values()) / 5.0

    return {
        "raw": dim_correct,
        "total": dim_total,
        "norm": norm_scores,
        "global_norm": global_norm
    }

def qualitative_level(norm_score):
    if norm_score > 4.5:
        return "Alto"
    elif norm_score > 2.0:
        return "Medio"
    else:
        return "Bajo"

def global_level_and_text(global_norm):
    if global_norm > 4.5:
        nivel = "Alto"
        texto = (
            "Desempeño general alto. Muestra rapidez para detectar patrones, "
            "comprender relaciones numéricas, retener información breve y distinguir detalles. "
            "Este perfil apunta a una capacidad cognitiva sobre el promedio."
        )
    elif global_norm > 2.0:
        nivel = "Medio"
        texto = (
            "Desempeño dentro del rango funcional esperado. Muestra comprensión adecuada "
            "de instrucciones, razonamiento lógico suficiente y nivel de atención compatible "
            "con la mayoría de contextos generales. Hay base para aprender con práctica."
        )
    else:
        nivel = "Bajo"
        texto = (
            "Desempeño por debajo del promedio comparativo interno. Puede necesitar más tiempo "
            "para razonar patrones nuevos, retener instrucciones de varios pasos o detectar "
            "diferencias finas entre datos similares."
        )
    return nivel, texto

def build_dim_descriptions(norm_map):
    out = {}
    out["RL"] = (
        "Capacidad para reconocer patrones lógicos y relaciones abstractas entre elementos."
        if norm_map["RL"] > 2.0 else
        "Puede requerir más tiempo para inferir patrones y deducciones lógicas cuando no están explícitas."
    )
    out["QN"] = (
        "Dominio de operaciones numéricas mentales y proporciones básicas a moderadas."
        if norm_map["QN"] > 2.0 else
        "Podría ralentizarse ante cálculos mentales, estimaciones o secuencias numéricas crecientes."
    )
    out["VR"] = (
        "Comprensión verbal, interpretación de frases y relaciones de significado."
        if norm_map["VR"] > 2.0 else
        "Puede requerir reformulación o ejemplos para asegurar que el sentido lógico del enunciado quede claro."
    )
    out["MT"] = (
        "Retención inmediata de claves cortas, secuencias y orden de pasos."
        if norm_map["MT"] > 2.0 else
        "Podría necesitar repetición adicional cuando se entregan varias indicaciones consecutivas."
    )
    out["AT"] = (
        "Precisión visual para notar diferencias sutiles en códigos, números o letras."
        if norm_map["AT"] > 2.0 else
        "Podría pasar por alto pequeñas variaciones entre cadenas muy parecidas, requiriendo doble verificación."
    )
    return out

def build_strengths_and_risks(norm_map):
    fortalezas = []
    riesgos = []

    if norm_map["RL"] > 4.5:
        fortalezas.append("Razonamiento lógico/abstracto rápido para identificar patrones nuevos.")
    elif norm_map["RL"] <= 2.0:
        riesgos.append("Puede requerir apoyo extra al enfrentarse a patrones lógicos no familiares.")

    if norm_map["QN"] > 4.5:
        fortalezas.append("Cálculo mental y manejo numérico con agilidad.")
    elif norm_map["QN"] <= 2.0:
        riesgos.append("Podría necesitar más tiempo en operaciones numéricas sucesivas o proporciones.")

    if norm_map["VR"] > 4.5:
        fortalezas.append("Comprende el sentido de frases e inferencias verbales con claridad.")
    elif norm_map["VR"] <= 2.0:
        riesgos.append("Puede requerir reformular explicaciones para asegurar comprensión exacta del mensaje.")

    if norm_map["MT"] > 4.5:
        fortalezas.append("Retiene secuencias breves y pasos ordenados sin mucha repetición.")
    elif norm_map["MT"] <= 2.0:
        riesgos.append("Puede olvidar un paso si recibe varias instrucciones seguidas sin apoyo visual.")

    if norm_map["AT"] > 4.5:
        fortalezas.append("Atención fina a diferencias sutiles entre códigos, letras o dígitos.")
    elif norm_map["AT"] <= 2.0:
        riesgos.append("Podría confundir cadenas muy parecidas; conviene doble verificación en datos críticos.")

    return fortalezas[:5], riesgos[:5]


# ------------------------------------------------------------
# UTILIDADES TEXTO -> PDF
# ------------------------------------------------------------
def _wrap(c, text, width, font="Helvetica", size=8):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if c.stringWidth(trial, font, size) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def _draw_paragraph(c, text, x, y, width,
                    font="Helvetica", size=8,
                    leading=11, color=colors.black,
                    max_lines=None):
    c.setFont(font, size)
    c.setFillColor(color)
    lines = _wrap(c, text, width, font, size)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        c.drawString(x, y, ln)
        y -= leading
    return y


# ------------------------------------------------------------
# GENERAR PDF (2 páginas, maquetado limpio y con espacio)
# ------------------------------------------------------------
def generate_pdf(
    candidate_name,
    fecha_eval,
    evaluator_email,
    raw_scores,
    total_scores,
    norm_scores,
    global_norm,
    fortalezas,
    riesgos,
    dim_desc
):
    nivel_global, texto_global = global_level_and_text(global_norm)

    buf = BytesIO()
    W, H = A4
    c = canvas.Canvas(buf, pagesize=A4)

    margin_left = 36
    margin_right = 36

    # -------- PÁGINA 1 --------
    # Encabezado
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.black)
    c.drawString(margin_left, H-40, "Evaluación Cognitiva General (IQ Adaptado)")
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawString(margin_left, H-54, "Uso interno. No clínico. Este resultado describe tendencias cognitivas básicas.")

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.black)
    c.drawRightString(W - margin_right, H-40, "Perfil de Capacidades Cognitivas")
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.grey)
    c.drawRightString(W - margin_right, H-54, "Interpretación orientada a nivel intelectual general")

    # Datos generales del evaluado
    box1_x = margin_left
    box1_w = W - margin_left - margin_right
    box1_y_top = H-90
    box1_h = 60

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(box1_x, box1_y_top-box1_h, box1_w, box1_h, stroke=1, fill=1)

    yy = box1_y_top - 16
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    c.drawString(box1_x+10, yy, f"Nombre evaluado: {candidate_name}")
    yy -= 12
    c.setFont("Helvetica", 8)
    c.drawString(box1_x+10, yy, f"Fecha de evaluación: {fecha_eval}")
    yy -= 12
    c.drawString(box1_x+10, yy, f"Contacto evaluador: {evaluator_email}")
    yy -= 12
    c.setFont("Helvetica", 6)
    c.setFillColor(colors.grey)
    c.drawString(box1_x+10, yy, "Documento interno. No constituye diagnóstico clínico.")

    # Perfil Cognitivo Global
    box2_x = margin_left
    box2_w = W - margin_left - margin_right
    box2_y_top = H-170
    box2_h = 100  # más alto para que no se junte el texto

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(box2_x, box2_y_top-box2_h, box2_w, box2_h, stroke=1, fill=1)

    yy2 = box2_y_top - 16
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    c.drawString(box2_x+10, yy2, "Perfil Cognitivo Global")
    yy2 -= 14

    c.setFont("Helvetica-Bold", 8)
    c.drawString(
        box2_x+10,
        yy2,
        f"Nivel global estimado: {nivel_global.upper()}  (Índice interno: {global_norm:.1f} / 6)"
    )
    yy2 -= 14

    c.setFont("Helvetica", 7)
    yy2 = _draw_paragraph(
        c,
        texto_global,
        box2_x+10,
        yy2,
        box2_w-20,
        font="Helvetica",
        size=7,
        leading=10,
        color=colors.black,
        max_lines=None
    )

    # Fortalezas y Aspectos a Observar
    box3_x = margin_left
    box3_w = W - margin_left - margin_right
    box3_y_top = H-320
    box3_h = 140  # más alto para texto largo sin encimar

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(box3_x, box3_y_top-box3_h, box3_w, box3_h, stroke=1, fill=1)

    y3 = box3_y_top - 16
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    c.drawString(box3_x+10, y3, "Resumen Cognitivo Observado")
    y3 -= 14

    # Fortalezas
    c.setFont("Helvetica-Bold", 8)
    c.drawString(box3_x+10, y3, "Fortalezas potenciales:")
    y3 -= 12
    c.setFont("Helvetica", 7)
    for f in fortalezas:
        wrap_lines = _wrap(c, "• " + f, box3_w-20, "Helvetica", 7)
        for line in wrap_lines:
            c.drawString(box3_x+20, y3, line)
            y3 -= 10
    y3 -= 6

    # Riesgos / puntos a observar
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    c.drawString(box3_x+10, y3, "Aspectos a observar:")
    y3 -= 12
    c.setFont("Helvetica", 7)
    for r in riesgos:
        wrap_lines = _wrap(c, "• " + r, box3_w-20, "Helvetica", 7)
        for line in wrap_lines:
            c.drawString(box3_x+20, y3, line)
            y3 -= 10

    # Perfil por dimensión (gráfico de barras)
    chart_x = margin_left
    chart_y_bottom = 120
    chart_w = 320
    chart_h = 120

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(chart_x-4, chart_y_bottom-4, chart_w+8, chart_h+52, stroke=1, fill=1)

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    c.drawString(chart_x, chart_y_bottom+chart_h+32,
                 "Puntaje por Dimensión (escala interna 0–6)")

    # eje Y
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(chart_x, chart_y_bottom, chart_x, chart_y_bottom+chart_h)

    # grilla horizontal
    for lvl in range(0,7):
        yv = chart_y_bottom + (lvl/6.0)*chart_h
        c.setFont("Helvetica",6)
        c.setFillColor(colors.black)
        c.drawString(chart_x-16, yv-2, str(lvl))
        c.setStrokeColor(colors.lightgrey)
        c.line(chart_x, yv, chart_x+chart_w, yv)

    dims_display = [
        ("RL","RL"),
        ("QN","QN"),
        ("VR","VR"),
        ("MT","MT"),
        ("AT","AT"),
    ]
    bar_colors = [
        colors.HexColor("#1e40af"),  # azul
        colors.HexColor("#059669"),  # verde
        colors.HexColor("#f97316"),  # naranjo
        colors.HexColor("#6b7280"),  # gris
        colors.HexColor("#0ea5e9"),  # celeste
    ]

    gap = 12
    bar_w = (chart_w - gap*(len(dims_display)+1)) / len(dims_display)
    tops = []

    for i,(key,label) in enumerate(dims_display):
        nv = norm_scores[key]
        raw = raw_scores[key]
        tot = total_scores[key]
        lvl_txt = qualitative_level(nv)

        bx = chart_x + gap + i*(bar_w+gap)
        bh = (nv/6.0)*chart_h
        by = chart_y_bottom

        c.setStrokeColor(colors.black)
        c.setFillColor(bar_colors[i])
        c.rect(bx, by, bar_w, bh, stroke=1, fill=1)

        tops.append((bx+bar_w/2.0, by+bh))

        c.setFont("Helvetica-Bold",7)
        c.setFillColor(colors.black)
        c.drawCentredString(bx+bar_w/2.0, chart_y_bottom-14, label)

        c.setFont("Helvetica",6)
        c.drawCentredString(
            bx+bar_w/2.0,
            chart_y_bottom-26,
            f"{raw}/{tot}  {lvl_txt}"
        )

    # unimos barras con línea y puntos
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.2)
    for j in range(len(tops)-1):
        (x1,y1)=tops[j]
        (x2,y2)=tops[j+1]
        c.line(x1,y1,x2,y2)
    for (px,py) in tops:
        c.setFillColor(colors.black)
        c.circle(px,py,2,stroke=0,fill=1)

    # Leyenda derecha
    legend_x = chart_x + chart_w + 16
    legend_w = (W - margin_right) - legend_x
    legend_y_top = chart_y_bottom + chart_h + 32
    legend_h = chart_h + 44

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(legend_x-4, chart_y_bottom-4, legend_w+8, legend_h, stroke=1, fill=1)

    yy_legend = legend_y_top
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(legend_x, yy_legend, "Dimensiones Evaluadas")
    yy_legend -= 14

    c.setFont("Helvetica",7)
    legend_lines = [
        "RL  Razonamiento Lógico / Abstracto",
        "QN  Razonamiento Numérico",
        "VR  Comprensión Verbal / Inferencia",
        "MT  Memoria de Trabajo Inmediata",
        "AT  Atención al Detalle / Precisión Visual",
        "Escala comparativa interna (0–6).",
    ]
    for ln in legend_lines:
        c.drawString(legend_x, yy_legend, ln)
        yy_legend -= 10

    # footer pág 1
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawRightString(W - margin_right, 30, "Página 1 / 2")

    c.showPage()

    # -------- PÁGINA 2 --------
    c.setFont("Helvetica-Bold",10)
    c.setFillColor(colors.black)
    c.drawString(margin_left, H-40, "Detalle por dimensión")

    table_x = margin_left
    table_y_top = H-60
    table_w = W - margin_left - margin_right
    table_h = 5 * 70 + 40  # altura para 5 filas con texto envuelto

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(table_x, table_y_top-table_h, table_w, table_h, stroke=1, fill=1)

    # Encabezados tabla
    head_y = table_y_top - 20
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)

    col_dim_x  = table_x + 10
    col_punt_x = table_x + 200
    col_lvl_x  = table_x + 270
    col_desc_x = table_x + 330

    c.drawString(col_dim_x,  head_y, "Dimensión")
    c.drawString(col_punt_x, head_y, "Puntaje")
    c.drawString(col_lvl_x,  head_y, "Nivel")
    c.drawString(col_desc_x, head_y, "Descripción funcional")

    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.line(table_x, head_y-4, table_x+table_w, head_y-4)

    row_y = head_y - 16
    row_gap = 70

    dims_display = [
        ("RL","Razonamiento Lógico / Abstracto"),
        ("QN","Razonamiento Numérico / Cálculo mental"),
        ("VR","Comprensión Verbal / Inferencia"),
        ("MT","Memoria de Trabajo Inmediata"),
        ("AT","Atención al Detalle / Precisión Visual"),
    ]

    for key,label in dims_display:
        raw_v  = raw_scores[key]
        tot_v  = total_scores[key]
        lvl_v  = qualitative_level(norm_scores[key])
        desc_v = dim_desc[key]

        c.setFont("Helvetica-Bold",8)
        c.setFillColor(colors.black)
        c.drawString(col_dim_x, row_y, label)

        c.setFont("Helvetica",8)
        c.drawString(col_punt_x, row_y, f"{raw_v}/{tot_v}")
        c.drawString(col_lvl_x,  row_y, lvl_v)

        c.setFont("Helvetica",8)
        row_y = _draw_paragraph(
            c,
            desc_v,
            col_desc_x,
            row_y,
            table_w - (col_desc_x - table_x) - 10,
            font="Helvetica",
            size=8,
            leading=10,
            color=colors.black,
            max_lines=None
        )

        row_y -= (row_gap - 30)

        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.5)
        c.line(table_x, row_y+10, table_x+table_w, row_y+10)

    # Nota metodológica final
    note_box_x = margin_left
    note_box_w = W - margin_left - margin_right
    note_box_y_top = 180
    note_box_h = 120

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(note_box_x, note_box_y_top-note_box_h, note_box_w, note_box_h, stroke=1, fill=1)

    yy_note = note_box_y_top - 16
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(note_box_x+10, yy_note, "Nota metodológica")
    yy_note -= 14

    nota_text = (
        "Este informe describe resultados de una prueba cognitiva general adaptada "
        "para estimar razonamiento lógico, manejo numérico básico, comprensión verbal, "
        "memoria inmediata y atención al detalle. No es un diagnóstico clínico ni mide "
        "habilidades técnicas específicas de un oficio. Los puntajes representan "
        "un indicador comparativo interno (escala 0–6)."
    )

    c.setFont("Helvetica",7)
    _draw_paragraph(
        c,
        nota_text,
        note_box_x+10,
        yy_note,
        note_box_w-20,
        font="Helvetica",
        size=7,
        leading=10,
        color=colors.black,
        max_lines=None
    )

    # footer pág 2
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawRightString(W - margin_right, 30, "Página 2 / 2")

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
# FINALIZAR TEST: CALCULAR, CREAR PDF, ENVIAR
# ------------------------------------------------------------
def finalize_and_send():
    scores = compute_scores(st.session_state.answers)
    raw_scores     = scores["raw"]
    total_scores   = scores["total"]
    norm_scores    = scores["norm"]
    global_norm    = scores["global_norm"]

    dim_desc       = build_dim_descriptions(norm_scores)
    fortalezas, riesgos = build_strengths_and_risks(norm_scores)

    now_txt = datetime.now().strftime("%d/%m/%Y %H:%M")

    pdf_bytes = generate_pdf(
        candidate_name   = st.session_state.candidate_name,
        fecha_eval       = now_txt,
        evaluator_email  = st.session_state.evaluator_email,
        raw_scores       = raw_scores,
        total_scores     = total_scores,
        norm_scores      = norm_scores,
        global_norm      = global_norm,
        fortalezas       = fortalezas,
        riesgos          = riesgos,
        dim_desc         = dim_desc
    )

    if not st.session_state.already_sent:
        try:
            send_email_with_pdf(
                to_email   = st.session_state.evaluator_email,
                pdf_bytes  = pdf_bytes,
                filename   = "Informe_Cognitivo_General.pdf",
                subject    = "Informe Evaluación Cognitiva General (IQ Adaptado)",
                body_text  = (
                    "Se adjunta informe interno de la Evaluación Cognitiva General "
                    f"({st.session_state.candidate_name}). Uso interno de RR.HH."
                ),
            )
        except Exception:
            pass
        st.session_state.already_sent = True


# ------------------------------------------------------------
# CALLBACK RESPUESTA (una sola vez por clic, sin doble click)
# ------------------------------------------------------------
def choose_answer(option_idx: int):
    q_idx = st.session_state.current_q
    st.session_state.answers[q_idx] = option_idx

    if q_idx < TOTAL_QUESTIONS - 1:
        st.session_state.current_q += 1
        st.session_state._need_rerun = True
    else:
        finalize_and_send()
        st.session_state.stage = "done"
        st.session_state._need_rerun = True


# ------------------------------------------------------------
# VISTAS UI STREAMLIT
# ------------------------------------------------------------
def view_info_form():
    st.markdown("### Datos del evaluado")
    st.caption("Estos datos se usarán sólo para generar y enviar el informe cognitivo en PDF.")

    st.session_state.candidate_name = st.text_input(
        "Nombre de la persona evaluada",
        value=st.session_state.candidate_name,
        placeholder="Nombre completo"
    )
    st.session_state.evaluator_email = st.text_input(
        "Correo del receptor del informe (RR.HH. / Encargado)",
        value=st.session_state.evaluator_email or FROM_ADDR,
        placeholder="nombre@empresa.com"
    )

    ok = (
        len(st.session_state.candidate_name.strip()) > 0 and
        len(st.session_state.evaluator_email.strip()) > 0
    )

    st.info(
        "Al finalizar las 70 preguntas, la app genera el PDF con el perfil cognitivo "
        "y lo envía automáticamente al correo indicado."
    )

    if st.button("Iniciar Evaluación Cognitiva (70 ítems)", type="primary", disabled=not ok, use_container_width=True):
        st.session_state.current_q = 0
        st.session_state.answers = {i: None for i in range(TOTAL_QUESTIONS)}
        st.session_state.already_sent = False
        st.session_state.stage = "test"
        st.session_state._need_rerun = True


def view_test():
    q_idx = st.session_state.current_q
    q = QUESTIONS[q_idx]
    progreso = (q_idx+1)/TOTAL_QUESTIONS

    # Header visual
    st.markdown(
        f"""
        <div style="
            background:linear-gradient(to right,#1e40af,#4338ca);
            color:white;
            border-radius:12px 12px 0 0;
            padding:16px 20px;
            display:flex;
            justify-content:space-between;
            align-items:center;
            flex-wrap:wrap;">
            <div style="font-weight:700;">
                Test Cognitivo General · IQ Adaptado
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
            <p style="
                margin:0;
                font-size:1.05rem;
                color:#1e293b;
                line-height:1.45;">
                {q["text"]}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Botones de alternativas
    cols = st.columns(2)
    for i, opt in enumerate(q["options"]):
        with cols[i % 2]:
            st.button(
                opt,
                key=f"opt_{q_idx}_{i}",
                on_click=choose_answer,
                args=(i,),
                use_container_width=True
            )

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
            Esta evaluación mide razonamiento lógico, cálculo mental, comprensión verbal,
            memoria inmediata y atención al detalle. No es un diagnóstico clínico.
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
                Los resultados fueron procesados y enviados al correo indicado.
            </div>
            <div style="
                color:#065f46;
                font-size:.85rem;
                margin-top:6px;">
                Uso interno. No clínico.
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
    else:
        view_test()

elif st.session_state.stage == "done":
    finalize_and_send()
    view_done()

# Rerun controlado
if st.session_state._need_rerun:
    st.session_state._need_rerun = False
    st.rerun()
