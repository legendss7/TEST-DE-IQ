import streamlit as st
from datetime import datetime, timedelta
from io import BytesIO
import smtplib
from email.message import EmailMessage

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import urllib.parse

# =========================
# CONFIG STREAMLIT
# =========================
st.set_page_config(
    page_title="Evaluación Cognitiva General",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================
# CREDENCIALES CORREO
# =========================
FROM_ADDR = "jo.tajtaj@gmail.com"
APP_PASS = "nlkt kujl ebdg cyts"  # app password de Gmail


# =========================
# PREGUNTAS (70 ítems)
# dim:
# RL = Razonamiento Lógico / Abstracto
# QN = Cuantitativo / Numérico
# VR = Verbal / Comprensión Semántica
# MT = Memoria de Trabajo / Secuencial
# AT = Atención al Detalle / Precisión
#
# Dificultad sube progresivamente: básicas → condicionales → multistep → abstractas.
# SIN mostrar la respuesta dentro del enunciado.
# =========================

QUESTIONS = [
    {
        "text": "Si todos los cuadernos son objetos de papelería y este ítem es un cuaderno, entonces este ítem es:",
        "options": ["Un objeto de papelería", "Un dispositivo electrónico", "Un animal", "No se puede concluir"],
        "answer": 0,
        "dim": "RL",
    },
    {
        "text": "Completa la secuencia numérica: 2, 4, 6, 8, __",
        "options": ["9", "10", "11", "12"],
        "answer": 1,
        "dim": "QN",
    },
    {
        "text": "Selecciona el sinónimo más cercano a 'inevitable':",
        "options": ["Forzoso", "Improvisado", "Opcional", "Evitado"],
        "answer": 0,
        "dim": "VR",
    },
    {
        "text": "Regla mental: 'Si A > B y B > C, entonces A > C'. Dado A=9, B=4, C=2, ¿es verdadero que A > C?",
        "options": ["Sí", "No"],
        "answer": 0,
        "dim": "MT",
    },
    {
        "text": "Un operario revisa 2 unidades cada 5 minutos. ¿Cuántas revisa en 15 minutos?",
        "options": ["2", "4", "6", "8"],
        "answer": 2,  # 6
        "dim": "QN",
    },
    {
        "text": "Se afirma: 'El informe es 100% coherente'. Luego lees: 'Hay partes que se contradicen'. ¿Conclusión lógica?",
        "options": [
            "El informe es perfectamente coherente",
            "El informe presenta contradicciones internas",
            "No se puede evaluar nada",
            "La contradicción es automática, no cuenta"
        ],
        "answer": 1,
        "dim": "AT",
    },
    {
        "text": "Analogía verbal: 'Calor' es a 'Frío' como 'Seco' es a:",
        "options": ["Constante", "Húmedo", "Ligero", "Líquido"],
        "answer": 1,
        "dim": "VR",
    },
    {
        "text": "Un número aumenta siempre en +3: 5 → 8 → 11 → 14 → __",
        "options": ["15", "16", "17", "20"],
        "answer": 2,  # 17
        "dim": "QN",
    },
    {
        "text": "Si todos los técnicos con Certificación X pueden usar la máquina Z, y Paula tiene Certificación X, entonces:",
        "options": [
            "Paula puede usar la máquina Z",
            "Paula no puede usar la máquina Z",
            "No se concluye nada",
            "Paula es jefa de la máquina Z"
        ],
        "answer": 0,
        "dim": "RL",
    },
    {
        "text": "Detecta el problema: 'Los reportes fueron idénticos en todo, incluidas las diferencias de energía consumida'.",
        "options": [
            "No hay problema",
            "Si hubo diferencias de energía, no pueden ser 'idénticos en todo'",
            "La palabra 'diferencias' está mal escrita",
            "No se puede evaluar"
        ],
        "answer": 1,
        "dim": "AT",
    },

    # --- Dificultad subiendo ---
    {
        "text": "Secuencia lógica: 2, 4, 8, 16, __",
        "options": ["20", "24", "30", "32"],
        "answer": 3,  # 32 (x2)
        "dim": "QN",
    },
    {
        "text": "Equipo A arma una caja en 6 min. Equipo B arma la misma caja en 4 min. En 12 min, ¿cuántas cajas hace A?",
        "options": ["1", "2", "3", "4"],
        "answer": 1,  # 12/6 =2
        "dim": "QN",
    },
    {
        "text": "Misma situación: en 12 min, ¿cuántas cajas hace B?",
        "options": ["1", "2", "3", "4"],
        "answer": 2,  # 12/4 =3
        "dim": "QN",
    },
    {
        "text": "Entonces, trabajando en paralelo sin estorbarse, ¿cuántas cajas totales salen en 12 min?",
        "options": ["4", "5", "6", "8"],
        "answer": 1,  # 2 + 3 =5
        "dim": "QN",
    },
    {
        "text": "Se dice: 'Ninguno de los reportes tiene errores de tipeo'. Pero luego: 'Se detectó un error de tipeo menor.'",
        "options": [
            "No hay contradicción",
            "Las dos frases son compatibles",
            "La primera frase queda en duda",
            "El error menor no cuenta, así que da igual"
        ],
        "answer": 2,
        "dim": "AT",
    },
    {
        "text": "Sinónimo más cercano de 'meticuloso':",
        "options": ["Descuidado", "Rápido", "Cuidadoso", "Impreciso"],
        "answer": 2,
        "dim": "VR",
    },
    {
        "text": "Regla: 'Si el informe supera 5 páginas, requiere resumen'. El informe de Julia tiene 8 páginas. Entonces:",
        "options": [
            "No necesita resumen",
            "Necesita resumen",
            "Debe eliminar 3 páginas",
            "El informe es inválido"
        ],
        "answer": 1,
        "dim": "RL",
    },
    {
        "text": "Memoria de trabajo: Cuenta mentalmente cuántas letras A hay en 'TARAZA'",
        "options": ["1", "2", "3", "4"],
        "answer": 2,  # T A R A Z A =3 A
        "dim": "MT",
    },
    {
        "text": "Afirmación: 'Todos los supervisores presentes firmaron el acta'. Ves un acta sin firma de Luis, quien estuvo presente.",
        "options": [
            "Luis no es supervisor",
            "La afirmación 'todos firmaron' puede ser falsa",
            "Luis no estuvo presente",
            "Luis fue despedido"
        ],
        "answer": 1,
        "dim": "RL",
    },
    {
        "text": "Serie definida como suma de los dos términos anteriores. Si los dos primeros términos son 1 y 3, ¿quinto término?",
        "options": [
            "7",
            "9",
            "11",
            "14"
        ],
        "answer": 2,  # 1,3,4,7,11
        "dim": "QN",
    },

    # --- Media ---
    {
        "text": "Frase: 'El protocolo es válido solo si TODAS las mediciones están dentro de rango'. ¿Qué implica?",
        "options": [
            "Basta con una medición dentro de rango",
            "Con una medición fuera de rango el protocolo NO es válido",
            "La validez no depende de mediciones",
            "Solo importa la medición final"
        ],
        "answer": 1,
        "dim": "VR",
    },
    {
        "text": "Ordena mentalmente alfabéticamente: D, B, F, C. ¿Cuál va tercera en el orden alfabético?",
        "options": ["B", "C", "D", "F"],
        "answer": 2,  # B C D F
        "dim": "MT",
    },
    {
        "text": "Identifica la frase incoherente lógicamente:",
        "options": [
            "Revisé cada paso y confirmé que todos fueron incompletos.",
            "El informe fue entregado tarde pero dentro del plazo.",
            "El lote salió perfecto salvo por fallas críticas.",
            "Esta semana todos los turnos llegaron puntuales excepto dos retrasos."
        ],
        "answer": 1,  # tarde pero dentro del plazo = choque
        "dim": "AT",
    },
    {
        "text": "Si 'Algunos técnicos son bilingües' y 'Todos los bilingües pueden capacitar', entonces:",
        "options": [
            "Ningún técnico puede capacitar",
            "Todos los técnicos pueden capacitar",
            "Al menos un técnico puede capacitar",
            "Nadie es bilingüe"
        ],
        "answer": 2,
        "dim": "RL",
    },
    {
        "text": "Secuencia numérica: 3, 4, 6, 9, 13, __ (+1,+2,+3,+4,...)",
        "options": ["16", "17", "18", "19"],
        "answer": 2,  # +5 =>18
        "dim": "QN",
    },
    {
        "text": "Escoge la causa-efecto más lógica:",
        "options": [
            "Se sobrecalentó el motor → La máquina se apagó",
            "Bostecé → Se cortó la luz",
            "Caminé → Mañana es feriado",
            "Llevaba gorro → El PC calculó más rápido"
        ],
        "answer": 0,
        "dim": "VR",
    },
    {
        "text": "Memoria secuencial: Regla mental: 'Para validar un registro, primero verificar consistencia, luego firmar digital'. ¿Qué va primero?",
        "options": [
            "Firmar digital",
            "Verificar consistencia",
            "Enviar reporte externo",
            "Nada"
        ],
        "answer": 1,
        "dim": "MT",
    },
    {
        "text": "¿Cuál frase mantiene coherencia temporal?",
        "options": [
            "Mañana entregamos el informe que ya enviamos ayer.",
            "El informe se envió ayer y se revisó hoy.",
            "El informe se enviará ayer y fue aprobado mañana.",
            "El informe fue aprobado mañana y enviado hoy."
        ],
        "answer": 1,
        "dim": "AT",
    },
    {
        "text": "Un costo sube de 80 a 100. ¿El aumento porcentual aproximado?",
        "options": ["15%", "20%", "25%", "30%"],
        "answer": 2,  # 20/80=25%
        "dim": "QN",
    },
    {
        "text": "¿Cuál define mejor 'ambigüedad'?",
        "options": [
            "Mensaje directo con único significado",
            "Frase que admite más de una interpretación posible",
            "Texto sin errores gramaticales",
            "Orden estricta paso a paso"
        ],
        "answer": 1,
        "dim": "VR",
    },

    # --- Media-alta ---
    {
        "text": "Regla: 'Si falla el sensor A, se activa alarma. Si hay alarma, se detiene producción'. Ves producción detenida. Con más seguridad puedes concluir que:",
        "options": [
            "El sensor A falló",
            "La alarma estuvo activa",
            "Ninguna máquina sirve",
            "No se detuvo realmente"
        ],
        "answer": 1,
        "dim": "RL",
    },
    {
        "text": "¿Cuál afirmación es internamente consistente?",
        "options": [
            "Algunos llegaron antes, otros después, y se registraron ambas cosas",
            "Nadie llegó jamás pero hubo discusión grupal en persona",
            "Estoy 100% seguro de que quizás pase",
            "Todos faltaron y todos asistieron al mismo tiempo"
        ],
        "answer": 0,
        "dim": "AT",
    },
    {
        "text": "Memoria de pasos: Plan mental: 'Revisar inventario → Anotar faltantes → Reportar a coordinación → Solicitar compra'. ¿Qué paso es justo ANTES de 'Solicitar compra'?",
        "options": [
            "Revisar inventario",
            "Anotar faltantes",
            "Reportar a coordinación",
            "No se indica"
        ],
        "answer": 2,
        "dim": "MT",
    },
    {
        "text": "Una máquina produce 45 piezas en 15 min (ritmo constante). ¿Cuántas en 60 min?",
        "options": ["90", "120", "150", "180"],
        "answer": 3,  # 3/min *60 =180
        "dim": "QN",
    },
    {
        "text": "Regla: 'Si un registro NO tiene validación, NO se libera el pago'. Ves un pago liberado. ¿Qué debe ser cierto?",
        "options": [
            "El registro sí tiene validación",
            "El pago fue error",
            "Nadie revisó nada",
            "Se liberó sin datos"
        ],
        "answer": 0,
        "dim": "RL",
    },
    {
        "text": "Selecciona la opción que describe relación causa probable, no simple coincidencia:",
        "options": [
            "Cayó agua sobre el enchufe y hubo cortocircuito",
            "Caminé y pasó un avión, entonces caminar causa aviones",
            "Me puse un gorro y el PC se aceleró por magia",
            "Miré la pared y cambió el clima"
        ],
        "answer": 0,
        "dim": "VR",
    },
    {
        "text": "¿Cuál enunciado es lógicamente imposible?",
        "options": [
            "El informe es confidencial y se publicó libremente en internet",
            "El informe se entregó el lunes y se revisó el martes",
            "El informe se corrigió dos veces esta semana",
            "El informe fue leído antes de la reunión"
        ],
        "answer": 0,
        "dim": "AT",
    },
    {
        "text": "Memoria de trabajo numérica: Mantén '7 4 9' en mente. Invierte mentalmente el orden a '9 4 7'. Suma los dos primeros de la versión invertida.",
        "options": ["9", "11", "12", "13"],
        "answer": 3,  # 9+4=13
        "dim": "MT",
    },
    {
        "text": "Lógica: 'Todos los Q son R. Algunos R son T.' ¿Cuál es forzosamente verdadera?",
        "options": [
            "Todos los Q son T",
            "Todos los T son Q",
            "Algunos Q son T",
            "Todos los Q son R"
        ],
        "answer": 3,
        "dim": "RL",
    },
    {
        "text": "Proporción: Mezcla agua:solvente = 2:3. Si tienes 10 unidades de solvente, ¿cuánta agua se requiere para mantener proporción?",
        "options": ["4", "5", "6", "7"],
        "answer": 2,  # ~6.67 -> aprox 6
        "dim": "QN",
    },

    # --- Alta ---
    {
        "text": "Inferencia verbal: 'El operador reportó un ruido extraño ANTES de la falla del equipo'. Esto sugiere:",
        "options": [
            "El ruido causó la falla con certeza absoluta",
            "El ruido pudo ser una señal temprana de la falla",
            "El ruido no tiene relación posible",
            "No hubo ruido"
        ],
        "answer": 1,
        "dim": "VR",
    },
    {
        "text": "Memoria secuencial: 'Encender sistema → Cargar parámetros → Validar lectura → Iniciar ciclo'. ¿Qué acción es la TERCERA?",
        "options": [
            "Encender sistema",
            "Cargar parámetros",
            "Validar lectura",
            "Iniciar ciclo"
        ],
        "answer": 2,
        "dim": "MT",
    },
    {
        "text": "Detecta inconsistencia lógica interna:",
        "options": [
            "El técnico registró cada paso y confirmó que hubo omisiones críticas",
            "El técnico no asistió al turno pero firmó 'asistencia completa'",
            "El técnico informó un riesgo y pidió revisión",
            "El técnico entregó el informe y respondió preguntas"
        ],
        "answer": 1,
        "dim": "AT",
    },
    {
        "text": "Hipótesis lógica: 'Si Ana aprueba calidad, el lote se libera. El lote fue liberado.' ¿Qué es más razonable concluir?",
        "options": [
            "Ana aprobó calidad con certeza",
            "Nadie más puede liberar el lote",
            "Probablemente calidad fue aprobada",
            "El lote no fue liberado"
        ],
        "answer": 2,
        "dim": "RL",
    },
    {
        "text": "Serie compleja: 5, 9, 17, 33, __ (incrementos +4,+8,+16,+32...)",
        "options": ["49", "57", "65", "80"],
        "answer": 2,  # 33+32=65
        "dim": "QN",
    },
    {
        "text": "Selecciona la afirmación más objetiva (menos emocional):",
        "options": [
            "El equipo trabajó horriblemente lento y fue un desastre",
            "El equipo presenta demoras frente a los tiempos de referencia definidos",
            "El equipo es pésimo e inútil",
            "El equipo arruinó todo por flojera"
        ],
        "answer": 1,
        "dim": "VR",
    },
    {
        "text": "Memoria de trabajo combinatoria: Mantén mentalmente tres códigos. (No los mostramos ahora). Pregunta: ¿Cuál es la limitación de este tipo de prueba?",
        "options": [
            "Exige retener información temporal sin apoyo visual",
            "No mide razonamiento lógico",
            "Solo mide matemáticas",
            "Obliga a copiar respuestas de otra persona"
        ],
        "answer": 0,
        "dim": "MT",
    },
    {
        "text": "Atención al detalle documental: ¿Qué caso genera conflicto de trazabilidad?",
        "options": [
            "El informe fue firmado digitalmente por la persona que lo elaboró",
            "El informe figura firmado por alguien que dice no haber participado",
            "El informe se envió con copia a coordinación",
            "El informe se almacenó en la carpeta correspondiente"
        ],
        "answer": 1,
        "dim": "AT",
    },
    {
        "text": "Lógica condicional: 'Si P entonces Q'. Sabes que P es falso. ¿Qué puedes asegurar sobre Q?",
        "options": [
            "Q es falso sí o sí",
            "Q es verdadero sí o sí",
            "No se puede concluir nada sobre Q",
            "P es verdadero"
        ],
        "answer": 2,
        "dim": "RL",
    },
    {
        "text": "Transformación numérica: Un valor se duplica y luego aumenta 50%. Si al inicio era 20, ¿cuál es el valor final?",
        "options": ["40", "50", "60", "70"],
        "answer": 2,  # 20*2=40; 40+50%=60
        "dim": "QN",
    },

    # --- muy alta / cierre ---
    {
        "text": "Inferencia verbal prudente:",
        "options": [
            "El sistema falló hoy dos veces → Hay que destruir la planta completa",
            "El sistema falló hoy dos veces → Podría requerir mantenimiento preventivo",
            "El sistema falló hoy → Toda la empresa es incompetente",
            "El sistema falló hoy → Hubo sabotaje seguro"
        ],
        "answer": 1,
        "dim": "VR",
    },
    {
        "text": "Memoria de orden: Pasos: (A) Preparar insumos, (B) Ajustar parámetros, (C) Ejecutar prueba. ¿Orden correcto?",
        "options": [
            "B → A → C",
            "A → B → C",
            "C → B → A",
            "B → C → A"
        ],
        "answer": 1,
        "dim": "MT",
    },
    {
        "text": "Atención al detalle de consistencia: El reporte dice 'Todos los envíos llegaron completos' y luego 'Faltó mercadería en el despacho 3'. ¿Qué implica?",
        "options": [
            "Plena coherencia",
            "La segunda frase confirma la primera",
            "La primera afirmación puede ser falsa",
            "No se puede concluir"
        ],
        "answer": 2,
        "dim": "AT",
    },
    {
        "text": "Contraposición lógica: 'Si el proceso es estable → el control es predecible'. Observas que el control NO es predecible. Entonces:",
        "options": [
            "El proceso no es estable",
            "El proceso es estable",
            "El proceso no existe",
            "No se puede deducir nada"
        ],
        "answer": 0,
        "dim": "RL",
    },
]

TOTAL_QUESTIONS = len(QUESTIONS)  # debería ser 70


# =========================
# ESTADO GLOBAL
# =========================
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

# timer
if "test_start_time" not in st.session_state:
    st.session_state.test_start_time = None  # datetime

if "already_sent" not in st.session_state:
    st.session_state.already_sent = False

if "_need_rerun" not in st.session_state:
    st.session_state._need_rerun = False


# =========================
# SCORING UTILS
# =========================
def is_correct(q_idx, choice_idx):
    q = QUESTIONS[q_idx]
    return choice_idx == q["answer"]

def compute_dimension_scores():
    dims = ["RL", "QN", "VR", "MT", "AT"]
    totals = {d: 0 for d in dims}
    corrects = {d: 0 for d in dims}

    for i, q in enumerate(QUESTIONS):
        d = q["dim"]
        totals[d] += 1
        ans = st.session_state.answers.get(i)
        if ans is not None and is_correct(i, ans):
            corrects[d] += 1

    pct = {}
    scale6 = {}
    for d in dims:
        if totals[d] == 0:
            pct[d] = 0.0
            scale6[d] = 0.0
        else:
            p = corrects[d] / totals[d]
            pct[d] = p
            scale6[d] = p * 6.0

    return corrects, pct, scale6, totals

def level_from_pct(p):
    if p >= 0.75:
        return "Alto"
    elif p >= 0.5:
        return "Medio"
    elif p >= 0.25:
        return "Bajo"
    else:
        return "Muy Bajo"

def choose_profile_label(pct_dict):
    best_dim = max(pct_dict, key=lambda d: pct_dict[d])
    mapping = {
        "RL": "Analítico / Lógico",
        "QN": "Numérico / Cuantitativo",
        "VR": "Verbal / Comprensión Semántica",
        "MT": "Memoria Operacional / Secuencial",
        "AT": "Atención al Detalle / Precisión",
    }
    return mapping.get(best_dim, "Perfil Mixto")

def build_bullets(pct_dict):
    ordered = sorted(pct_dict.items(), key=lambda x: x[1], reverse=True)
    top_dim, _ = ordered[0]
    low_dim, _ = ordered[-1]

    def dim_desc(d):
        if d == "RL":
            return "razonamiento lógico y consistencia argumental"
        if d == "QN":
            return "manejo cuantitativo / cálculo progresivo"
        if d == "VR":
            return "comprensión verbal e inferencia contextual"
        if d == "MT":
            return "retención activa y secuenciación de pasos"
        if d == "AT":
            return "precisión y detección de incoherencias"
        return "procesamiento general"

    bullets = []
    bullets.append(
        f"Fortaleza relativa en {dim_desc(top_dim)}."
    )
    bullets.append(
        f"Área a reforzar en {dim_desc(low_dim)}."
    )

    avg_score = sum(pct_dict.values()) / len(pct_dict)
    if avg_score >= 0.6:
        bullets.append(
            "Desempeño global dentro de rango funcional esperado."
        )
    elif avg_score >= 0.4:
        bullets.append(
            "Desempeño global intermedio; sugiere condiciones claras de trabajo."
        )
    else:
        bullets.append(
            "Rendimiento global inicial bajo; podría requerir acompañamiento cercano en tareas complejas."
        )
    return bullets

def global_iq_band(pct_dict):
    avg = sum(pct_dict.values()) / len(pct_dict)
    if avg >= 0.7:
        return "Rendimiento global: sobre el promedio esperado."
    elif avg >= 0.5:
        return "Rendimiento global: rango promedio funcional."
    elif avg >= 0.3:
        return "Rendimiento global: bajo el promedio esperado."
    else:
        return "Rendimiento global: desempeño inicial muy bajo."

def wrap_text(c, text, width, font="Helvetica", size=7):
    c.setFont(font, size)
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test_line = (cur + " " + w).strip()
        if c.stringWidth(test_line, font, size) <= width:
            cur = test_line
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def slider_positions(scale6, corrects, totals):
    sliders = [
        ("Pensamiento concreto",          "Razonamiento abstracto",          scale6["RL"], "RL", corrects["RL"], totals["RL"]),
        ("Cálculo directo",               "Análisis numérico complejo",      scale6["QN"], "QN", corrects["QN"], totals["QN"]),
        ("Comprensión literal",           "Inferencia contextual",           scale6["VR"], "VR", corrects["VR"], totals["VR"]),
        ("Memoria inmediata simple",      "Manipulación mental activa",      scale6["MT"], "MT", corrects["MT"], totals["MT"]),
        ("Atención general",              "Precisión minuciosa / detalle",   scale6["AT"], "AT", corrects["AT"], totals["AT"]),
    ]
    return sliders

def draw_slider_line(c, x_left, y_center, width, value0to6,
                     left_label, right_label,
                     dim_code, correct_count, total_count):
    c.setLineWidth(0.8)
    c.setStrokeColor(colors.black)
    c.line(x_left, y_center, x_left + width, y_center)

    ratio = max(0, min(1, value0to6 / 6.0))
    px = x_left + ratio * width
    c.setFillColor(colors.black)
    c.circle(px, y_center, 2.0, stroke=0, fill=1)

    c.setFont("Helvetica", 6.5)
    c.setFillColor(colors.black)
    c.drawString(x_left, y_center + 8, left_label)
    c.drawRightString(x_left + width, y_center + 8, right_label)

    c.setFont("Helvetica", 6)
    c.drawCentredString(
        x_left + width/2.0,
        y_center - 10,
        f"{dim_code}: {correct_count}/{total_count}"
    )

# =========================
# GENERAR PDF (1 hoja estilo DISC adaptado)
# =========================
def generate_pdf(candidate_name, evaluator_email):
    corrects, pct, scale6, totals = compute_dimension_scores()
    style_label = choose_profile_label(pct)
    bullets = build_bullets(pct)
    iq_band_text = global_iq_band(pct)

    W, H = A4
    margin_left = 30
    margin_right = 30
    top_y = H - 30

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    # HEADER
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.black)
    c.drawString(margin_left, top_y, "EMPRESA / LOGO")

    c.setFont("Helvetica", 7)
    c.drawString(margin_left, top_y - 10, "Evaluación cognitiva general")

    box_w = 160
    box_h = 18
    c.setFillColor(colors.black)
    c.rect(W - margin_right - box_w,
           top_y - box_h + 2,
           box_w,
           box_h,
           stroke=0,
           fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(W - margin_right - box_w/2,
                        top_y - box_h + 6,
                        "Evaluación Cognitiva General")

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 6.5)
    c.drawRightString(W - margin_right,
                      top_y - 22,
                      "Perfil cognitivo · Screening interno RR.HH.")

    # GRAFICO IZQUIERDA
    dims_order = ["RL", "QN", "VR", "MT", "AT"]
    labels_short = {"RL":"RL","QN":"QN","VR":"VR","MT":"MT","AT":"AT"}

    chart_x = margin_left
    chart_y_bottom = top_y - 220
    chart_w = 260
    chart_h = 140

    c.setStrokeColor(colors.black)
    c.setLineWidth(0.8)
    c.line(chart_x, chart_y_bottom, chart_x, chart_y_bottom + chart_h)

    for lvl in range(0, 7):
        yv = chart_y_bottom + (lvl / 6.0) * chart_h
        c.setFont("Helvetica", 6)
        c.setFillColor(colors.black)
        c.drawString(chart_x - 15, yv - 2, str(lvl))
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.5)
        c.line(chart_x, yv, chart_x + chart_w, yv)

    bar_gap = 12
    bar_w = (chart_w - bar_gap * (len(dims_order) + 1)) / len(dims_order)

    tops_xy = []
    bar_colors = [
        colors.HexColor("#1e3a8a"),
        colors.HexColor("#047857"),
        colors.HexColor("#6b7280"),
        colors.HexColor("#2563eb"),
        colors.HexColor("#0f766e"),
    ]

    for i, dim in enumerate(dims_order):
        val6 = scale6[dim]
        bh = (val6 / 6.0) * chart_h
        bx = chart_x + bar_gap + i * (bar_w + bar_gap)
        by = chart_y_bottom

        c.setStrokeColor(colors.black)
        c.setLineWidth(0.6)
        c.setFillColor(bar_colors[i])
        c.rect(bx, by, bar_w, bh, stroke=1, fill=1)

        tops_xy.append((bx + bar_w/2.0, by + bh))

    c.setStrokeColor(colors.black)
    c.setLineWidth(1.0)
    for j in range(len(tops_xy)-1):
        (x1,y1)=tops_xy[j]
        (x2,y2)=tops_xy[j+1]
        c.line(x1,y1,x2,y2)
    for (px,py) in tops_xy:
        c.setFillColor(colors.black)
        c.circle(px,py,2.0,stroke=0,fill=1)

    for i, dim in enumerate(dims_order):
        bx = chart_x + bar_gap + i*(bar_w+bar_gap)
        this_pct = pct[dim]
        this_level = level_from_pct(this_pct)
        c.setFont("Helvetica",7)
        c.setFillColor(colors.black)
        c.drawCentredString(bx+bar_w/2.0, chart_y_bottom-12, labels_short[dim])
        c.setFont("Helvetica",6)
        c.drawCentredString(
            bx+bar_w/2.0,
            chart_y_bottom-24,
            f"{corrects[dim]}/{totals[dim]}  {this_level}"
        )

    c.setFont("Helvetica-Bold",7)
    c.setFillColor(colors.black)
    c.drawString(chart_x,
                 chart_y_bottom+chart_h+12,
                 "Puntaje por Dimensión (escala interna 0–6)")

    # PANEL DATOS DERECHA
    panel_x = chart_x + chart_w + 20
    panel_y_top = top_y - 40
    panel_w = W - margin_right - panel_x
    panel_h = 180

    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.setFillColor(colors.white)
    c.rect(panel_x,
           panel_y_top-panel_h,
           panel_w,
           panel_h,
           stroke=1,
           fill=1)

    y_cursor = panel_y_top - 14
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(panel_x+8, y_cursor, candidate_name.upper())

    y_cursor -= 12
    now_txt = datetime.now().strftime("%d/%m/%Y %H:%M")
    c.setFont("Helvetica",7)
    c.drawString(panel_x+8, y_cursor, f"Fecha de evaluación: {now_txt}")

    y_cursor -= 10
    c.drawString(panel_x+8, y_cursor, f"Evaluador: {evaluator_email}")

    y_cursor -= 10
    c.setFont("Helvetica-Bold",7)
    c.drawString(panel_x+8, y_cursor, choose_profile_label(pct).upper())

    y_cursor -= 12
    c.setFont("Helvetica",7)
    c.drawString(panel_x+8, y_cursor, global_iq_band(pct))

    y_cursor -= 14
    c.setFont("Helvetica",6.5)
    bullet_leading = 9
    for b in build_bullets(pct):
        wrapped = wrap_text(c, "• " + b, panel_w-16, "Helvetica", 6.5)
        for ln in wrapped:
            if y_cursor < (panel_y_top - panel_h + 20):
                break
            c.drawString(panel_x+10, y_cursor, ln)
            y_cursor -= bullet_leading
        if y_cursor < (panel_y_top - panel_h + 20):
            break

    # GLOSARIO
    glos_y_top = panel_y_top - panel_h - 10
    glos_h = 70
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.setFillColor(colors.white)
    c.rect(panel_x,
           glos_y_top-glos_h,
           panel_w,
           glos_h,
           stroke=1,
           fill=1)

    yg = glos_y_top-12
    c.setFont("Helvetica-Bold",7)
    c.setFillColor(colors.black)
    c.drawString(panel_x+8, yg, "Dimensiones Evaluadas")

    yg -= 10
    c.setFont("Helvetica",6)
    c.drawString(panel_x+8, yg, "RL  Razonamiento Lógico / Abstracto")
    yg -= 9
    c.drawString(panel_x+8, yg, "QN  Cuantitativo / Numérico")
    yg -= 9
    c.drawString(panel_x+8, yg, "VR  Verbal / Comprensión Semántica")
    yg -= 9
    c.drawString(panel_x+8, yg, "MT  Memoria de Trabajo / Secuencial")
    yg -= 9
    c.drawString(panel_x+8, yg, "AT  Atención al Detalle / Precisión")

    # SLIDERS BOX
    sliders_box_x = margin_left
    sliders_box_y_top = chart_y_bottom - 30
    sliders_box_w = W - margin_left - margin_right
    sliders_box_h = 140

    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.setFillColor(colors.white)
    c.rect(sliders_box_x,
           sliders_box_y_top-sliders_box_h,
           sliders_box_w,
           sliders_box_h,
           stroke=1,
           fill=1)

    c.setFont("Helvetica-Bold",7)
    c.setFillColor(colors.black)
    c.drawString(sliders_box_x+8,
                 sliders_box_y_top-14,
                 "Perfiles comparativos (posición relativa y aciertos por dimensión)")

    corrects_, pct_, scale6_, totals_ = corrects, pct, scale6, totals
    sliders_data = slider_positions(scale6_, corrects_, totals_)
    y_line = sliders_box_y_top - 32
    line_gap = 24

    for (left_lab,right_lab,val6,code,corr,tot) in sliders_data:
        draw_slider_line(
            c,
            x_left=sliders_box_x+110,
            y_center=y_line,
            width=200,
            value0to6=val6,
            left_label=left_lab,
            right_label=right_lab,
            dim_code=code,
            correct_count=corr,
            total_count=tot
        )
        y_line -= line_gap

    # PERFIL GENERAL
    final_box_x = margin_left
    final_box_w = W - margin_left - margin_right
    final_box_h = 110
    final_box_y_top = sliders_box_y_top - sliders_box_h - 15

    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.setFillColor(colors.white)
    c.rect(final_box_x,
           final_box_y_top-final_box_h,
           final_box_w,
           final_box_h,
           stroke=1,
           fill=1)

    yfp = final_box_y_top - 14
    c.setFont("Helvetica-Bold",7)
    c.setFillColor(colors.black)
    c.drawString(final_box_x+8, yfp, "Perfil general")
    yfp -= 10

    resumen = (
        f"{global_iq_band(pct)} El evaluado muestra un estilo dominante descrito como "
        f"{style_label.lower()}. Esto sugiere más soltura relativa en las áreas con "
        "mejor puntaje y necesidad de más apoyo donde el rendimiento fue menor. "
        "Este resultado resume razonamiento lógico, numérico, comprensión verbal, "
        "memoria operativa y atención al detalle. Uso interno de RR.HH.; no es "
        "diagnóstico clínico."
    )

    c.setFont("Helvetica",6.5)
    wrap_lines = wrap_text(c, resumen, final_box_w-16, "Helvetica",6.5)
    for ln in wrap_lines:
        if yfp < (final_box_y_top-final_box_h+20):
            break
        c.drawString(final_box_x+8, yfp, ln)
        yfp -= 9

    c.setFont("Helvetica",5.5)
    c.setFillColor(colors.grey)
    c.drawRightString(final_box_x+final_box_w-8,
                      final_box_y_top-final_box_h+8,
                      "Uso interno RR.HH. · No clínico · Screening cognitivo general")

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold",7)
    c.drawCentredString(W/2, 20, candidate_name.upper())

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


# =========================
# ENVÍO POR CORREO
# =========================
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


def finalize_and_send():
    pdf_bytes = generate_pdf(
        candidate_name=st.session_state.candidate_name,
        evaluator_email=st.session_state.evaluator_email,
    )

    if not st.session_state.already_sent:
        try:
            send_email_with_pdf(
                to_email=st.session_state.evaluator_email,
                pdf_bytes=pdf_bytes,
                filename="Informe_Cognitivo.pdf",
                subject="Informe Evaluación Cognitiva General",
                body_text=(
                    "Adjunto informe cognitivo general.\n"
                    f"Candidato: {st.session_state.candidate_name}\n"
                    "Uso interno RR.HH. / Selección."
                ),
            )
        except Exception:
            pass
        st.session_state.already_sent = True


# =========================
# CONTROL DE TIEMPO Y ANTI-CAMBIO DE PESTAÑA
# =========================

EXAM_DURATION_SECONDS = 20 * 60  # 20 minutos

def get_remaining_seconds():
    """Calcula segundos restantes. Si ya se acabó el tiempo, devuelve 0."""
    if st.session_state.test_start_time is None:
        return EXAM_DURATION_SECONDS
    elapsed = (datetime.now() - st.session_state.test_start_time).total_seconds()
    remaining = EXAM_DURATION_SECONDS - elapsed
    return max(0, int(remaining))

def time_is_over():
    return get_remaining_seconds() <= 0

def forfeit_detected():
    """Detecta si el usuario cambió de pestaña, usando un truco con JS que marca ?forfeit=1."""
    query_params = st.query_params
    # st.query_params es un Mapping[str, str or list]
    # Nos basta detectar 'forfeit'=='1'
    if "forfeit" in query_params:
        val = query_params["forfeit"]
        if isinstance(val, list):
            return "1" in val
        return val == "1"
    return False


# =========================
# CALLBACK RESPUESTA
# =========================
def answer_question(choice_idx):
    # Guarda respuesta
    q_idx = st.session_state.current_q
    st.session_state.answers[q_idx] = choice_idx

    # Avanza o finaliza
    if q_idx < TOTAL_QUESTIONS - 1:
        st.session_state.current_q += 1
        st.session_state._need_rerun = True
    else:
        finalize_and_send()
        st.session_state.stage = "done"
        st.session_state._need_rerun = True


# =========================
# VISTAS STREAMLIT
# =========================
def view_info():
    st.markdown("### Datos del evaluado")
    st.info(
        "Este test mide razonamiento lógico, numérico, comprensión verbal, "
        "memoria de trabajo y atención al detalle. "
        "Duración máxima: 20 minutos. "
        "Si cambias de pestaña o minimizas la ventana durante el test, "
        "la evaluación se da por terminada inmediatamente."
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

    st.write("---")

    if st.button("Iniciar test (20 minutos cronometrados)", type="primary", disabled=not ok, use_container_width=True):
        st.session_state.current_q = 0
        st.session_state.answers = {i: None for i in range(TOTAL_QUESTIONS)}
        st.session_state.already_sent = False
        st.session_state.test_start_time = datetime.now()
        st.session_state.stage = "test"
        st.session_state._need_rerun = True


def view_test():
    # 1. chequear forfeit pestaña o fin de tiempo
    if forfeit_detected() or time_is_over():
        finalize_and_send()
        st.session_state.stage = "done"
        st.session_state._need_rerun = True
        return

    # 2. mostrar JS que marca ?forfeit=1 si cambia de pestaña
    st.markdown(
        """
        <script>
        // Si el usuario cambia de pestaña / pierde foco, marcamos forfeit=1 en la URL.
        document.addEventListener("visibilitychange", function() {
            if (document.hidden) {
                const url = new URL(window.location.href);
                url.searchParams.set('forfeit','1');
                window.location.replace(url.toString());
            }
        });
        </script>
        """,
        unsafe_allow_html=True
    )

    # 3. mostrar temporizador restante
    remaining_sec = get_remaining_seconds()
    mm = remaining_sec // 60
    ss = remaining_sec % 60
    tiempo_str = f"{mm:02d}:{ss:02d}"

    q_idx = st.session_state.current_q
    q = QUESTIONS[q_idx]
    progreso = (q_idx + 1) / TOTAL_QUESTIONS

    # HEADER visual responsive
    st.markdown(
        f"""
        <div style="
            width:100%;
            background:linear-gradient(to right,#1e40af,#4338ca);
            color:white;
            border-radius:12px 12px 0 0;
            padding:16px 20px;
            display:flex;
            flex-wrap:wrap;
            row-gap:8px;
            justify-content:space-between;
            align-items:flex-start;
            font-family:system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;">
            <div style="font-weight:700;min-width:200px;">
                Test Cognitivo General (Nivel Univ. 1er año)
            </div>
            <div style="
                display:flex;
                flex-direction:column;
                align-items:flex-end;
                font-size:.8rem;
                background:rgba(255,255,255,0.15);
                padding:6px 10px;
                border-radius:8px;
                line-height:1.4;">
                <div><b>Pregunta:</b> {q_idx+1} / {TOTAL_QUESTIONS}</div>
                <div><b>Progreso:</b> {int(round(progreso*100))}%</div>
                <div><b>Tiempo restante:</b> {tiempo_str}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.progress(progreso)

    # CUERPO PREGUNTA
    st.markdown(
        f"""
        <div style="
            background:#ffffff;
            border:1px solid #e2e8f0;
            border-radius:12px;
            padding:24px;
            box-shadow:0 12px 24px rgba(0,0,0,0.06);
            margin-top:12px;
            font-family:system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;">
            <p style="
                margin:0;
                font-size:1.05rem;
                color:#1e293b;
                line-height:1.45;
                font-weight:500;">
                {q["text"]}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # OPCIONES (full width, responsive)
    for opt_i, opt_text in enumerate(q["options"]):
        st.button(
            opt_text,
            key=f"q{q_idx}_opt{opt_i}",
            use_container_width=True,
            on_click=answer_question,
            args=(opt_i,)
        )

    # aviso confidencialidad
    st.markdown(
        """
        <div style="
            width:100%;
            background:#f8fafc;
            border:1px solid #e2e8f0;
            border-radius:8px;
            padding:12px 16px;
            font-size:.8rem;
            color:#475569;
            margin-top:12px;
            line-height:1.4;
            font-family:system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;">
            <b>Importante:</b><br>
            • No cambies de pestaña ni minimices la ventana. Eso finaliza el test.<br>
            • Tienes 20 minutos totales. Al terminar el tiempo, la prueba se cierra automáticamente.<br>
            • El informe se enviará a RR.HH. (uso interno, no clínico).
        </div>
        """,
        unsafe_allow_html=True
    )


def view_done():
    st.markdown(
        """
        <div style="
            width:100%;
            background:linear-gradient(to bottom right,#ecfdf5,#d1fae5);
            padding:28px;
            border-radius:14px;
            box-shadow:0 24px 48px rgba(0,0,0,0.08);
            text-align:center;
            font-family:system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;">
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


# =========================
# FLUJO PRINCIPAL
# =========================
if st.session_state.stage == "info":
    view_info()

elif st.session_state.stage == "test":
    # seguridad extra: si por alguna razón no hay hora inicio, la seteamos ahora
    if st.session_state.test_start_time is None:
        st.session_state.test_start_time = datetime.now()
    view_test()

elif st.session_state.stage == "done":
    finalize_and_send()
    view_done()

# RERUN CONTROLADO (para avanzar de pantalla sin doble click)
if st.session_state._need_rerun:
    st.session_state._need_rerun = False
    st.rerun()
