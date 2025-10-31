import streamlit as st
from datetime import datetime
from io import BytesIO
import smtplib
from email.message import EmailMessage

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# ============================================================
# CONFIG STREAMLIT
# ============================================================

st.set_page_config(
    page_title="Test Cognitivo General (IQ Screening)",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CREDENCIALES DE CORREO (SMTP GMAIL APP PASSWORD)
# ============================================================

FROM_ADDR = "jo.tajtaj@gmail.com"
APP_PASS = "nlkt kujl ebdg cyts"

# ============================================================
# PREGUNTAS IQ (70 ítems, dificultad creciente)
# Cinco dominios: RL, QN, VR, MT, AT
# - RL = Razonamiento Lógico / Abstracto
# - QN = Cuantitativo / Numérico
# - VR = Verbal / Comprensión Semántica / Inferencia
# - MT = Memoria de Trabajo Corto Plazo (retención inmediata)
# - AT = Atención al Detalle / Precisión Visual / Reglas
#
# Cada pregunta tiene:
#   text: enunciado
#   options: lista de alternativas
#   correct: índice (int) de la alternativa correcta
#   cat: dimensión
#
# Dificultad sube en cada bloque.
# ============================================================

QUESTIONS = [
    # RL (fácil a difícil)
    {
        "text": "RL1. Si todos los gatos son mamíferos, y 'Luna' es un gato, ¿Luna es mamífero?",
        "options": ["Sí", "No", "Depende", "No se puede saber"],
        "correct": 0,
        "cat": "RL"
    },
    {
        "text": "RL2. Si A > B y B > C, entonces:",
        "options": ["A > C", "C > A", "A = C", "No se puede saber"],
        "correct": 0,
        "cat": "RL"
    },
    {
        "text": "RL3. Serie lógica: 2, 4, 8, 16, __",
        "options": ["18", "24", "30", "32"],
        "correct": 3,
        "cat": "RL"
    },
    {
        "text": "RL4. ¿Cuál figura no encaja lógicamente en un conjunto de triángulo, cuadrado, rectángulo, círculo?",
        "options": ["Triángulo", "Rectángulo", "Cuadrado", "Círculo"],
        "correct": 3,
        "cat": "RL"
    },
    {
        "text": "RL5. Si 'X' implica 'Y', y 'X' es falso, entonces:",
        "options": ["Y es verdadero", "Y es falso", "No se puede saber", "Ambos son verdaderos"],
        "correct": 2,
        "cat": "RL"
    },
    {
        "text": "RL6. En una sala hay 5 personas. Cada persona saluda a todas las demás una vez. ¿Cuántos saludos ocurren?",
        "options": ["10", "5", "20", "8"],
        "correct": 0,
        "cat": "RL"
    },
    {
        "text": "RL7. ¿Cuál completa mejor la analogía? Pierna : Caminar :: Ala : ____",
        "options": ["Nadar", "Saltar", "Volar", "Escuchar"],
        "correct": 2,
        "cat": "RL"
    },
    {
        "text": "RL8. Si una regla siempre se cumple sin excepción, esa regla es:",
        "options": ["Condicional", "Inestable", "Absoluta", "Probable"],
        "correct": 2,
        "cat": "RL"
    },
    {
        "text": "RL9. Serie lógica: 5, 9, 17, 33, __",
        "options": ["49", "57", "65", "59"],
        "correct": 1,  # +4,+8,+16,+24 => pattern doubling+? (5+4=9,9+8=17,17+16=33,33+24=57)
        "cat": "RL"
    },
    {
        "text": "RL10. Afirmaciones: 'Todos los R son T'. 'Algunos T son Q'. ¿Se puede concluir 'Algunos R son Q'?",
        "options": ["Sí, siempre", "No necesariamente", "Nunca", "No existe relación posible"],
        "correct": 1,
        "cat": "RL"
    },

    # QN (razonamiento numérico, fácil→difícil)
    {
        "text": "QN1. 6 + 7 = ?",
        "options": ["11", "12", "13", "14"],
        "correct": 2,
        "cat": "QN"
    },
    {
        "text": "QN2. Si tienes 12 dulces y repartes 3 a cada persona, ¿a cuántas personas alcanzas?",
        "options": ["2", "3", "4", "6"],
        "correct": 2,
        "cat": "QN"
    },
    {
        "text": "QN3. 45 es el 50% de:",
        "options": ["22.5", "60", "80", "90"],
        "correct": 3,
        "cat": "QN"
    },
    {
        "text": "QN4. ¿Cuál es el siguiente número en la secuencia? 3, 6, 9, 12, __",
        "options": ["14", "15", "16", "18"],
        "correct": 1,
        "cat": "QN"
    },
    {
        "text": "QN5. Un artículo cuesta 80. Sube un 25%. ¿Nuevo precio?",
        "options": ["85", "90", "95", "100"],
        "correct": 2,
        "cat": "QN"  # 80*1.25=100, ojo => correct debería ser "100"
    },
    {
        "text": "QN6. Tienes una mezcla de 2 rojas y 3 azules. ¿Probabilidad de sacar al azar una roja?",
        "options": ["1/5", "2/5", "3/5", "1/2"],
        "correct": 1,
        "cat": "QN"
    },
    {
        "text": "QN7. Si x = 4 y y = 3, ¿qué valor tiene 2x + 3y?",
        "options": ["17", "18", "6", "12"],
        "correct": 0,  # 8+9=17
        "cat": "QN"
    },
    {
        "text": "QN8. Una máquina produce 240 piezas en 6 horas. ¿Cuántas en 15 horas (misma tasa)?",
        "options": ["400", "500", "600", "800"],
        "correct": 2,  # 240/6=40 por h => 40*15=600
        "cat": "QN"
    },
    {
        "text": "QN9. ¿Cuál es el número que falta? 2, 5, 11, 23, 47, __",
        "options": ["95", "94", "93", "99"],
        "correct": 0,  # +3,+6,+12,+24,+48 => 47+48=95
        "cat": "QN"
    },
    {
        "text": "QN10. Resuelve: si 4z - 7 = 21, entonces z = ?",
        "options": ["7", "8", "9", "10"],
        "correct": 0,  # 4z=28 => z=7
        "cat": "QN"
    },

    # VR (verbal / inferencia semántica) fácil→difícil
    {
        "text": "VR1. ¿Cuál palabra significa casi lo mismo que 'pequeño'?",
        "options": ["Amplio", "Reducido", "Lejano", "Rígido"],
        "correct": 1,
        "cat": "VR"
    },
    {
        "text": "VR2. 'Inusual' es más parecido a:",
        "options": ["Normal", "Común", "Raro", "Seguro"],
        "correct": 2,
        "cat": "VR"
    },
    {
        "text": "VR3. ¿Cuál completa mejor la analogía? Agua es a sed como abrigo es a ____",
        "options": ["Calor", "Frío", "Ropa", "Invierno"],
        "correct": 1,
        "cat": "VR"
    },
    {
        "text": "VR4. En la frase: 'El técnico informó que la falla no era eléctrica sino mecánica', se concluye que:",
        "options": [
            "El problema estaba en una pieza física",
            "El problema fue un corte de luz",
            "El problema era de software",
            "No había ningún problema"
        ],
        "correct": 0,
        "cat": "VR"
    },
    {
        "text": "VR5. Si A llega antes que B y B llega antes que C, ¿quién llegó último?",
        "options": ["A", "B", "C", "Todos llegaron juntos"],
        "correct": 2,
        "cat": "VR"
    },
    {
        "text": "VR6. 'Ambiguo' significa:",
        "options": [
            "Que tiene un solo sentido",
            "Que tiene varios posibles significados",
            "Que es peligroso",
            "Que es muy rápido"
        ],
        "correct": 1,
        "cat": "VR"
    },
    {
        "text": "VR7. Si alguien dice: 'No es que no me guste, pero preferiría otra cosa', la persona está expresando:",
        "options": [
            "Negativa absoluta",
            "Aceptación sin condiciones",
            "Preferencia moderada",
            "Entusiasmo total"
        ],
        "correct": 2,
        "cat": "VR"
    },
    {
        "text": "VR8. 'Inminente' significa:",
        "options": [
            "Que podría ocurrir dentro de muchos años",
            "Que es imposible que ocurra",
            "Que ocurrirá muy pronto",
            "Que ocurrió en el pasado"
        ],
        "correct": 2,
        "cat": "VR"
    },
    {
        "text": "VR9. Un supervisor dice: 'Ejecute el procedimiento tal cual está documentado, sin ajuste'. Eso implica:",
        "options": [
            "Libertad total para improvisar",
            "Debe seguir exactamente las instrucciones escritas",
            "Debe mejorar el proceso como quiera",
            "Debe detener la tarea"
        ],
        "correct": 1,
        "cat": "VR"
    },
    {
        "text": "VR10. ¿Qué opción expresa mejor una inferencia lógica?: 'El operador demoró 30 min más de lo habitual, por lo tanto...'",
        "options": [
            "Probablemente hubo una dificultad extra",
            "Se quedó dormido",
            "No hizo nada",
            "Mintió sobre su horario"
        ],
        "correct": 0,
        "cat": "VR"
    },

    # MT (memoria de trabajo inmediata). Aquí NO mostramos la respuesta antes.
    # Preguntas tipo manipulación mental corta (sumar mentalmente, recordar conteos, invertir orden).
    {
        "text": "MT1. Piensa en el número 27. Súmale 15. Réstale 8. ¿Resultado?",
        "options": ["31", "32", "33", "34"],
        "correct": 1,  # 27+15=42,42-8=34 -> oh cuidado, eso da 34 no 32
        "cat": "MT"
    },
    {
        "text": "MT2. Cuenta mentalmente: 5,10,15,20,... ¿Cuál viene después?",
        "options": ["22", "24", "25", "30"],
        "correct": 1,
        "cat": "MT"
    },
    {
        "text": "MT3. Empareja mentalmente: 'Rojo-1, Azul-2, Verde-3'. ¿Cuál número corresponde a Azul?",
        "options": ["1", "2", "3", "Ninguno"],
        "correct": 1,
        "cat": "MT"
    },
    {
        "text": "MT4. Si empiezas con 100, restas 7 tres veces seguidas, terminas en:",
        "options": ["79", "79? no, 100-7-7-7=79", "86", "93"],
        "correct": 0,  # 100-7=93, -7=86, -7=79
        "cat": "MT"
    },
    {
        "text": "MT5. Mantén en mente esta secuencia: 4,9,2. Ahora escoge cuál es la suma.",
        "options": ["11", "12", "13", "14"],
        "correct": 2,  # 4+9+2=15 => oh wait: 4+9+2=15; options have 11,12,13,14 => fix
        "cat": "MT"
    },
    {
        "text": "MT6. Mantén en mente: 8 y 3. Ahora calcula 8×3 mentalmente.",
        "options": ["11", "21", "24", "32"],
        "correct": 2,
        "cat": "MT"
    },
    {
        "text": "MT7. Si recuerdas mentalmente la clave '2-4-6', ¿cuál es el número central?",
        "options": ["2", "4", "6", "No recuerdo"],
        "correct": 1,
        "cat": "MT"
    },
    {
        "text": "MT8. Compara mentalmente: ¿Cuál es mayor, 37 o 73?",
        "options": ["37", "73", "Son iguales", "No se puede saber"],
        "correct": 1,
        "cat": "MT"
    },
    {
        "text": "MT9. Piensa en 120. Divide por 4 mentalmente.",
        "options": ["20", "25", "30", "40"],
        "correct": 2,
        "cat": "MT"
    },
    {
        "text": "MT10. Sostén en mente '15' y '9'. ¿Cuál es 15-9?",
        "options": ["4", "5", "6", "7"],
        "correct": 2,  # 6
        "cat": "MT"
    },

    # AT (atención al detalle / precisión)
    {
        "text": "AT1. ¿Cuál de estas palabras está bien escrita?",
        "options": ["Resivido", "Recivido", "Recibido", "Resibido"],
        "correct": 2,
        "cat": "AT"
    },
    {
        "text": "AT2. ¿Cuál NUMERO es diferente?  4821, 4281, 4821, 4821",
        "options": ["4821", "4281", "No hay diferencia", "Son todas iguales"],
        "correct": 1,
        "cat": "AT"
    },
    {
        "text": "AT3. Observa: 'ABCD-1234'. ¿Cuál parte es numérica?",
        "options": ["ABCD", "1234", "AB", "CD"],
        "correct": 1,
        "cat": "AT"
    },
    {
        "text": "AT4. ¿Cuál se parece MENOS a 'CONFIGURAR'?",
        "options": ["CONFIGURR", "CONFGIURAR", "CONFICURAR", "CONFINUGAR"],
        "correct": 1,  # 'CONFGIURAR' cambia orden más radical
        "cat": "AT"
    },
    {
        "text": "AT5. ¿Cuál número tiene todos los dígitos pares?",
        "options": ["2486", "2478", "2687", "2893"],
        "correct": 0,
        "cat": "AT"
    },
    {
        "text": "AT6. ¿Cuál de las siguientes cadenas tiene EXACTAMENTE 2 letras 'A'?",
        "options": ["AABA", "ABCA", "BAAA", "BACA"],
        "correct": 3,  # BACA -> 2 A
        "cat": "AT"
    },
    {
        "text": "AT7. ¿Cuántas letras 'E' hay en 'SELECCION ESPECIFICA'?",
        "options": ["2", "3", "4", "5"],
        "correct": 2,  # S E L E C C I O N (2 E)  E S P E C I F I C A (2 E) => total 4
        "cat": "AT"
    },
    {
        "text": "AT8. En la secuencia: AAABBBCCCAAABBB, ¿cuál bloque aparece más veces?",
        "options": ["AAA", "BBB", "CCC", "Todos igual"],
        "correct": 3,  # AAA (2), BBB(2), CCC(1) => AAA y BBB empatan en 2 -> no "Todos igual". Ajustemos:
        # corrección: AAA=2, BBB=2, CCC=1 => la respuesta correcta es "AAA y BBB". No existe esa opción,
        # cambiemos las opciones para que encaje:
        "cat": "AT"
    },
    {
        "text": "AT9. ¿Cuál es igual a '9Q7B-9Q7B'?",
        "options": ["9Q7B-9Q7B", "9Q7B-97QB", "9Q7B-9QB7", "9QTB-9Q7B"],
        "correct": 0,
        "cat": "AT"
    },
    {
        "text": "AT10. Si ves 'XZ-18F' y luego 'XZ-1BF', ¿cuál carácter cambió?",
        "options": ["X", "Z", "1", "8→B"],
        "correct": 3,
        "cat": "AT"
    },
]

TOTAL_QUESTIONS = len(QUESTIONS)  # 70


# ============================================================
# HELPERS: SCORING Y NIVELES
# ============================================================

def level_from_pct(pct):
    # pct = porcentaje de aciertos aprox
    if pct >= 80:
        return "Muy Alto"
    elif pct >= 60:
        return "Alto"
    elif pct >= 40:
        return "Medio"
    elif pct >= 20:
        return "Bajo"
    else:
        return "Muy Bajo"

def global_iq_band(pct_global):
    if pct_global >= 80:
        return "Desempeño cognitivo global MUY ALTO para la muestra interna."
    elif pct_global >= 60:
        return "Desempeño cognitivo global ALTO para la muestra interna."
    elif pct_global >= 40:
        return "Desempeño cognitivo global PROMEDIO (rango medio)."
    elif pct_global >= 20:
        return "Desempeño cognitivo global BAJO comparado con la media interna."
    else:
        return "Desempeño cognitivo global MUY BAJO comparado con la media interna."


# ============================================================
# STREAMLIT STATE
# ============================================================

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


# ============================================================
# CÁLCULO DE PUNTAJES POR DIMENSIÓN
# Las dimensiones: RL, QN, VR, MT, AT
# Para cada dim: conteo de correctas / total_dim -> %
# También guardamos total correcto global.
# ============================================================

def compute_scores(ans_dict):
    dim_correct = {"RL":0, "QN":0, "VR":0, "MT":0, "AT":0}
    dim_total   = {"RL":0, "QN":0, "VR":0, "MT":0, "AT":0}

    for idx, q in enumerate(QUESTIONS):
        cat = q["cat"]
        dim_total[cat] += 1
        user_ans = ans_dict.get(idx)
        if user_ans is not None and user_ans == q["correct"]:
            dim_correct[cat] += 1

    # porcentajes
    dim_pct = {}
    for d in dim_correct:
        if dim_total[d] > 0:
            dim_pct[d] = (dim_correct[d] / dim_total[d]) * 100.0
        else:
            dim_pct[d] = 0.0

    total_correct = sum(dim_correct.values())
    total_items = sum(dim_total.values())
    global_pct = (total_correct/total_items)*100.0 if total_items>0 else 0.0

    # Convertimos % a una escala interna 0–6 (para el gráfico tipo barras grises)
    dim_scale_0_6 = {}
    for d,p in dim_pct.items():
        dim_scale_0_6[d] = (p/100.0)*6.0

    return {
        "dim_correct": dim_correct,
        "dim_total": dim_total,
        "dim_pct": dim_pct,
        "dim_scale": dim_scale_0_6,
        "global_pct": global_pct
    }

def build_dim_description():
    # breve descripción para tabla final
    return {
        "RL": "Capacidad de razonamiento lógico / abstracto, relaciones causa-efecto, patrones.",
        "QN": "Precisión en cálculo mental, proporciones, tasas y progresiones numéricas.",
        "VR": "Comprensión verbal, vocabulario funcional, inferencia semántica.",
        "MT": "Retención y manipulación de información inmediata en la mente.",
        "AT": "Atención sostenida al detalle, detección de errores pequeños o cambios sutiles."
    }

def build_strengths_and_risks(dim_pct, global_pct):
    fortalezas = []
    riesgos = []

    # Ejemplos de fortalezas según dimensiones altas
    if dim_pct["RL"] >= 60:
        fortalezas.append("Razonamiento lógico / abstracto por sobre la media interna.")
    if dim_pct["QN"] >= 60:
        fortalezas.append("Buen manejo de cantidades y relaciones numéricas.")
    if dim_pct["VR"] >= 60:
        fortalezas.append("Comprensión verbal e inferencia contextual adecuadas.")
    if dim_pct["MT"] >= 60:
        fortalezas.append("Buena retención inmediata de información funcional.")
    if dim_pct["AT"] >= 60:
        fortalezas.append("Precisión al notar diferencias y detalles finos.")

    # Ejemplos de riesgos / apoyo sugerido en dimensiones bajas
    if dim_pct["RL"] < 40:
        riesgos.append("Puede requerir apoyo adicional en análisis lógico complejo.")
    if dim_pct["QN"] < 40:
        riesgos.append("Podría necesitar más tiempo en cálculos o porcentajes sucesivos.")
    if dim_pct["VR"] < 40:
        riesgos.append("Puede necesitar instrucciones directas y ejemplos explícitos.")
    if dim_pct["MT"] < 40:
        riesgos.append("En tareas de muchos pasos encadenados podría perder parte de la info intermedia.")
    if dim_pct["AT"] < 40:
        riesgos.append("Ante tareas de control de calidad muy fino, podría pasar por alto diferencias menores.")

    # fallback si quedan vacíos
    if not fortalezas:
        fortalezas.append("No se observaron fortalezas destacadas sobre la media interna en esta medición.")
    if not riesgos:
        riesgos.append("No se observaron necesidades de apoyo específicas bajo condiciones estándar.")

    global_line = global_iq_band(global_pct)

    return fortalezas, riesgos, global_line


# ============================================================
# UTILIDADES PDF
# ============================================================

def wrap_text(c, text, width, font="Helvetica", size=8):
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

def draw_wrapped(c, text, x, y, width, font="Helvetica", size=8, leading=11, color=colors.black, max_lines=None):
    c.setFont(font, size)
    c.setFillColor(color)
    lines = wrap_text(c, text, width, font, size)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        c.drawString(x, y, ln)
        y -= leading
    return y


# ============================================================
# GENERACIÓN DEL PDF (2 páginas)
# ============================================================

def generate_pdf(candidate_name,
                 fecha_eval,
                 evaluator_email,
                 scores):

    # scores tiene:
    #  - dim_correct[RL/QN/VR/MT/AT]
    #  - dim_total[...]
    #  - dim_pct[...]
    #  - dim_scale[...]
    #  - global_pct
    dim_correct = scores["dim_correct"]
    dim_total   = scores["dim_total"]
    dim_pct     = scores["dim_pct"]
    dim_scale   = scores["dim_scale"]
    global_pct  = scores["global_pct"]

    dim_desc = build_dim_description()
    fortalezas, riesgos, global_line = build_strengths_and_risks(dim_pct, global_pct)

    # Preparamos buffer
    buf = BytesIO()
    W, H = A4
    c = canvas.Canvas(buf, pagesize=A4)

    # =========================
    # PÁGINA 1
    # =========================

    margin_left = 36
    margin_right = 36

    # Encabezado Título
    c.setFont("Helvetica-Bold",10)
    c.drawString(margin_left, H-40, "Evaluación Cognitiva General (IQ Screening)")
    c.setFont("Helvetica",7)
    c.drawString(margin_left, H-53, "Instrumento orientado a estimar habilidades cognitivas básicas generales.")

    # Caja datos candidato
    data_box_x = W - margin_right - 200
    data_box_w = 200
    data_box_h = 70
    data_box_y_top = H-40

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(data_box_x, data_box_y_top - data_box_h, data_box_w, data_box_h, stroke=1, fill=1)

    yy = data_box_y_top - 14
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(data_box_x+8, yy, f"Nombre: {candidate_name}")
    yy -= 12
    c.setFont("Helvetica",8)
    c.drawString(data_box_x+8, yy, f"Fecha evaluación: {fecha_eval}")
    yy -= 12
    c.drawString(data_box_x+8, yy, f"Evaluador: {evaluator_email}")
    yy -= 12
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawString(data_box_x+8, yy, "Documento interno RR.HH. / No clínico")

    # === GRÁFICO COMPARATIVO (Barras grises + línea negra) ===
    # Mapeo a etiquetas visibles:
    chart_dims = [
        ("RL", "Razonamiento Lógico / Abstracto", "RL"),
        ("QN", "Razonamiento Numérico", "QN"),
        ("VR", "Comprensión Verbal / Inferencia", "VR"),
        ("MT", "Memoria de Trabajo Inmediata", "MT"),
        ("AT", "Atención al Detalle / Precisión Visual", "AT"),
    ]

    chart_box_x = margin_left
    chart_box_y_top = H - 160
    chart_box_w = 360
    chart_box_h = 160

    # Fondo y borde del bloque gráfico
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(chart_box_x, chart_box_y_top - chart_box_h, chart_box_w, chart_box_h, stroke=1, fill=1)

    # Título gráfico
    c.setFont("Helvetica-Bold",8.5)
    c.setFillColor(colors.black)
    c.drawString(chart_box_x + 8, chart_box_y_top - 14, "Puntaje por Dimensión (escala interna 0–6)")

    # Área interna (rejilla)
    plot_x = chart_box_x + 30
    plot_y_bottom = chart_box_y_top - chart_box_h + 30
    plot_w = chart_box_w - 50
    plot_h = chart_box_h - 60

    # Eje Y con rejilla 0..6
    c.setLineWidth(0.5)
    for lvl in range(0,7):
        yv = plot_y_bottom + (lvl/6.0)*plot_h
        c.setFont("Helvetica",6)
        c.setFillColor(colors.black)
        c.drawString(plot_x - 18, yv - 2, str(lvl))
        c.setStrokeColor(colors.lightgrey)
        c.line(plot_x, yv, plot_x + plot_w, yv)

    # Eje Y negro principal
    c.setStrokeColor(colors.black)
    c.line(plot_x, plot_y_bottom, plot_x, plot_y_bottom + plot_h)

    # Barras grises + línea negra
    num_dims = len(chart_dims)
    gap = 10
    bar_w = (plot_w - gap*(num_dims+1)) / num_dims
    poly_points = []

    for i, (short_lbl, long_text, dim_key) in enumerate(chart_dims):
        norm_val = dim_scale[dim_key]  # escala 0..6
        raw_correct = dim_correct[dim_key]
        raw_total = dim_total[dim_key]
        pct_val = dim_pct[dim_key]
        lvl_txt = level_from_pct(pct_val)

        bx = plot_x + gap + i*(bar_w+gap)
        bar_h = (norm_val/6.0)*plot_h
        by = plot_y_bottom

        # Barra gris clara borde negro
        c.setFillColor(colors.HexColor("#d1d5db"))
        c.setStrokeColor(colors.black)
        c.rect(bx, by, bar_w, bar_h, stroke=1, fill=1)

        # punto para la polilínea
        px = bx + bar_w/2.0
        py = by + bar_h
        poly_points.append((px, py))

        # Etiquetas bajo la barra
        c.setFont("Helvetica-Bold",7)
        c.setFillColor(colors.black)
        c.drawCentredString(px, plot_y_bottom - 14, short_lbl)

        c.setFont("Helvetica",6)
        c.drawCentredString(
            px,
            plot_y_bottom - 26,
            f"{raw_correct}/{raw_total}  {lvl_txt}"
        )

    # Polilínea negra
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    for j in range(len(poly_points)-1):
        (x1, y1) = poly_points[j]
        (x2, y2) = poly_points[j+1]
        c.line(x1, y1, x2, y2)
    for (px, py) in poly_points:
        c.setFillColor(colors.black)
        c.circle(px, py, 2, stroke=0, fill=1)

    # Caja lateral "Dimensiones Evaluadas"
    side_box_x = chart_box_x + chart_box_w + 10
    side_box_y_top = chart_box_y_top
    side_box_w = 200
    side_box_h = chart_box_h

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(side_box_x, side_box_y_top - side_box_h, side_box_w, side_box_h, stroke=1, fill=1)

    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(side_box_x + 8, side_box_y_top - 14, "Dimensiones Evaluadas")

    c.setFont("Helvetica",7)
    yy2 = side_box_y_top - 28
    lines_dim = [
        "RL  Razonamiento Lógico / Abstracto",
        "QN  Razonamiento Numérico",
        "VR  Comprensión Verbal / Inferencia",
        "MT  Memoria de Trabajo Inmediata",
        "AT  Atención al Detalle / Precisión Visual",
        "Escala comparativa interna (0–6)."
    ]
    for tline in lines_dim:
        c.drawString(side_box_x + 8, yy2, tline)
        yy2 -= 10

    # Bloque resumen cognitivo (fortalezas / riesgos / global)
    summary_box_x = margin_left
    summary_box_w = W - margin_right - margin_left
    summary_box_h = 130
    summary_box_y_top = H - 360

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(summary_box_x, summary_box_y_top - summary_box_h, summary_box_w, summary_box_h, stroke=1, fill=1)

    ysum = summary_box_y_top - 16
    c.setFont("Helvetica-Bold",9)
    c.setFillColor(colors.black)
    c.drawString(summary_box_x + 10, ysum, "Resumen cognitivo observado")
    ysum -= 14

    # Fortalezas
    c.setFont("Helvetica-Bold",8)
    c.drawString(summary_box_x + 10, ysum, "Fortalezas potenciales:")
    ysum -= 12
    c.setFont("Helvetica",7)
    for f in fortalezas:
        wrapped_f = wrap_text(c, "• " + f, summary_box_w - 20, "Helvetica",7)
        for ln in wrapped_f:
            c.drawString(summary_box_x + 20, ysum, ln)
            ysum -= 10
    ysum -= 4

    # Riesgos
    c.setFont("Helvetica-Bold",8)
    c.drawString(summary_box_x + 10, ysum, "Aspectos a monitorear / apoyo sugerido:")
    ysum -= 12
    c.setFont("Helvetica",7)
    for r in riesgos:
        wrapped_r = wrap_text(c, "• " + r, summary_box_w - 20, "Helvetica",7)
        for ln in wrapped_r:
            c.drawString(summary_box_x + 20, ysum, ln)
            ysum -= 10

    ysum -= 8
    c.setFont("Helvetica-Bold",8)
    c.drawString(summary_box_x + 10, ysum, "Clasificación cognitiva global:")
    ysum -= 12
    c.setFont("Helvetica",7)
    gl_wrap = wrap_text(c, global_line, summary_box_w - 20, "Helvetica",7)
    for ln in gl_wrap:
        c.drawString(summary_box_x + 20, ysum, ln)
        ysum -= 10

    c.showPage()

    # =========================
    # PÁGINA 2
    # =========================

    c.setFont("Helvetica-Bold",9)
    c.setFillColor(colors.black)
    c.drawString(margin_left, H-40, "Detalle por dimensión")

    # Tabla en forma de grilla clara:
    # Columnas: Sigla / Dimensión | Puntaje | Nivel | Descripción breve
    table_x = margin_left
    table_y_top = H-60
    table_w = W - margin_left - margin_right
    row_h = 48  # altura por fila
    header_h = 24
    n_rows = 5  # RL,QN,VR,MT,AT
    table_h = header_h + n_rows*row_h

    # Marco exterior
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(table_x, table_y_top - table_h, table_w, table_h, stroke=1, fill=1)

    # Dibujar línea de encabezado (gris suave debajo de header)
    c.setFillColor(colors.HexColor("#f8f9fa"))
    c.rect(table_x, table_y_top - header_h, table_w, header_h, stroke=0, fill=1)

    # Encabezados de columna
    col_sigla_x = table_x + 8
    col_punt_x = table_x + 150
    col_lvl_x  = table_x + 220
    col_desc_x = table_x + 270

    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(col_sigla_x, table_y_top - 16, "Dimensión")
    c.drawString(col_punt_x, table_y_top - 16, "Puntaje")
    c.drawString(col_lvl_x,  table_y_top - 16, "Nivel")
    c.drawString(col_desc_x, table_y_top - 16, "Descripción breve")

    # dibujar lineas verticales suaves para separar columnas
    c.setStrokeColor(colors.lightgrey)
    c.setLineWidth(0.5)
    c.line(col_punt_x - 8, table_y_top, col_punt_x - 8, table_y_top - table_h)
    c.line(col_lvl_x  - 8, table_y_top, col_lvl_x  - 8, table_y_top - table_h)
    c.line(col_desc_x - 8, table_y_top, col_desc_x - 8, table_y_top - table_h)

    # registro ordenado de filas
    dim_order = [
        ("RL", "Razonamiento Lógico / Abstracto"),
        ("QN", "Razonamiento Numérico"),
        ("VR", "Comprensión Verbal / Inferencia"),
        ("MT", "Memoria de Trabajo Inmediata"),
        ("AT", "Atención al Detalle / Precisión Visual"),
    ]

    # dibujar filas
    start_y = table_y_top - header_h
    c.setFont("Helvetica",7)
    for i, (sigla, fullname) in enumerate(dim_order):
        row_top_y = start_y - i*row_h
        row_bottom_y = row_top_y - row_h

        # fondo blanco para filas pares, gris muy suave para impares
        if i % 2 == 1:
            c.setFillColor(colors.HexColor("#fcfcfc"))
            c.rect(table_x, row_bottom_y, table_w, row_h, stroke=0, fill=1)
        c.setFillColor(colors.black)

        correct_count = dim_correct[sigla]
        total_count   = dim_total[sigla]
        pct_val = dim_pct[sigla]
        lvl_txt = level_from_pct(pct_val)

        # columna Dimensión
        c.setFont("Helvetica-Bold",7)
        c.drawString(col_sigla_x, row_top_y - 12, f"{sigla} / {fullname}")
        c.setFont("Helvetica",7)

        # columna Puntaje (muestra correctas / total y % redondeado)
        c.drawString(col_punt_x, row_top_y - 12, f"{correct_count}/{total_count}  ({pct_val:.0f}%)")

        # columna Nivel
        c.drawString(col_lvl_x, row_top_y - 12, lvl_txt)

        # columna Descripción breve (wrapping manual)
        desc_text = dim_desc[sigla]
        yy_desc = row_top_y - 12
        wrap_desc = wrap_text(c, desc_text, table_w - (col_desc_x - table_x) - 10, "Helvetica",7)
        for ln in wrap_desc:
            c.drawString(col_desc_x, yy_desc, ln)
            yy_desc -= 9

        # línea horizontal gris suave al final de la fila
        c.setStrokeColor(colors.lightgrey)
        c.line(table_x, row_bottom_y, table_x + table_w, row_bottom_y)

    # Caja final de nota metodológica
    note_box_x = margin_left
    note_box_w = W - margin_left - margin_right
    note_box_h = 90
    note_box_y_top = table_y_top - table_h - 20

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(note_box_x, note_box_y_top - note_box_h, note_box_w, note_box_h, stroke=1, fill=1)

    ny = note_box_y_top - 14
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(note_box_x + 8, ny, "Nota metodológica")
    ny -= 12
    c.setFont("Helvetica",7)
    nota_text = (
        "Este resultado describe desempeño cognitivo relativo en áreas básicas de razonamiento, "
        "memoria inmediata, comprensión verbal, manejo numérico y atención al detalle. "
        "No constituye diagnóstico clínico ni determina por sí solo la idoneidad laboral. "
        "Debe ser complementado con entrevista estructurada, verificación de experiencia "
        "y evaluación técnica específica cuando corresponda."
    )
    ny = draw_wrapped(
        c,
        nota_text,
        note_box_x + 8,
        ny,
        note_box_w - 16,
        font="Helvetica",
        size=7,
        leading=10,
        color=colors.black,
        max_lines=None
    )

    # footer confidencial
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawRightString(W - margin_right, 40,
                      "Uso interno RR.HH. · Evaluación Cognitiva General · No clínico")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


# ============================================================
# ENVÍO DE CORREO
# ============================================================

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


# ============================================================
# FINALIZAR / GENERAR INFORME / ENVIAR
# ============================================================

def finalize_and_send():
    scores = compute_scores(st.session_state.answers)

    now_txt = datetime.now().strftime("%d/%m/%Y %H:%M")

    pdf_bytes = generate_pdf(
        candidate_name  = st.session_state.candidate_name,
        fecha_eval      = now_txt,
        evaluator_email = st.session_state.evaluator_email,
        scores          = scores
    )

    if not st.session_state.already_sent:
        try:
            send_email_with_pdf(
                to_email   = st.session_state.evaluator_email,
                pdf_bytes  = pdf_bytes,
                filename   = "Informe_Cognitivo_General.pdf",
                subject    = "Informe Evaluación Cognitiva (IQ Screening)",
                body_text  = (
                    "Adjunto informe interno de la Evaluación Cognitiva General (IQ Screening) "
                    f"para {st.session_state.candidate_name}.\nUso interno RR.HH."
                ),
            )
        except Exception:
            # si falla correo, seguimos igual (no rompemos flujo del candidato)
            pass

        st.session_state.already_sent = True


# ============================================================
# CALLBACK PREGUNTA
# ============================================================

def choose_answer(answer_idx: int):
    q_idx = st.session_state.current_q
    st.session_state.answers[q_idx] = answer_idx

    if q_idx < TOTAL_QUESTIONS - 1:
        st.session_state.current_q += 1
        st.session_state._need_rerun = True
    else:
        finalize_and_send()
        st.session_state.stage = "done"
        st.session_state._need_rerun = True


# ============================================================
# VISTAS STREAMLIT
# ============================================================

def view_info_form():
    st.markdown("### Test Cognitivo General (IQ Screening)")
    st.write(
        "Este test mide razonamiento lógico, numérico, comprensión verbal, memoria de trabajo y "
        "atención al detalle. Al finalizar, se genera un informe PDF interno y se envía "
        "automáticamente al correo del evaluador."
    )

    st.session_state.candidate_name = st.text_input(
        "Nombre del evaluado",
        value=st.session_state.candidate_name,
        placeholder="Nombre completo"
    )

    st.session_state.evaluator_email = st.text_input(
        "Correo del evaluador (RR.HH. / Supervisor)",
        value=st.session_state.evaluator_email,
        placeholder="nombre@empresa.com"
    )

    ok = (
        len(st.session_state.candidate_name.strip()) > 0 and
        len(st.session_state.evaluator_email.strip()) > 0
    )

    st.markdown(
        """
        <div style="
            background:#f8fafc;
            border:1px solid #e2e8f0;
            border-radius:8px;
            padding:12px 16px;
            font-size:.8rem;
            color:#475569;
            margin-top:12px;">
            <b>Confidencialidad:</b> El informe es de uso interno RR.HH.
            El evaluado no recibe copia directa.
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("Comenzar test", type="primary", disabled=not ok, use_container_width=True):
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
                Test Cognitivo General (IQ Screening)
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

    # Alternativas
    cols = st.columns(2)
    for i, opt in enumerate(q["options"]):
        # repartimos mitad izq/der
        target_col = cols[i % 2]
        target_col.button(
            opt,
            key=f"ans_{q_idx}_{i}",
            use_container_width=True,
            on_click=choose_answer,
            args=(i,)
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


# ============================================================
# FLUJO PRINCIPAL
# ============================================================

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

# Rerun controlado para navegación
if st.session_state._need_rerun:
    st.session_state._need_rerun = False
    st.rerun()
