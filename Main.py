# ============================================================
# TEST COGNITIVO OPERATIVO (IQ ADAPTADO) · 70 ÍTEMS
# Visual estilo EPQR en la app
# PDF con layout tipo "miperfilDISC" (gráfico izq + resumen der + sliders + perfil general)
#
# Requiere:
#   pip install streamlit reportlab
#
# Envío automático del PDF al correo del evaluador al terminar.
# Pantalla final sólo dice "Evaluación finalizada".
# ============================================================

import streamlit as st
from datetime import datetime
from io import BytesIO
import smtplib
from email.message import EmailMessage

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors


# -------------------------------------------------
# CONFIG STREAMLIT
# -------------------------------------------------
st.set_page_config(
    page_title="Evaluación Cognitiva Operativa",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# CREDENCIALES DE CORREO
# -------------------------------------------------
FROM_ADDR = "jo.tajtaj@gmail.com"
APP_PASS  = "nlkt kujl ebdg cyts"
DEFAULT_EVAL_EMAIL = "jo.tajtaj@gmail.com"


# -------------------------------------------------
# PREGUNTAS (70 ítems, 5 dimensiones cognitivas x 14 ítems)
# RL = Razonamiento Lógico
# AT = Atención al Detalle
# VD = Velocidad de Decisión
# MT = Memoria de Trabajo
# CI = Comprensión de Instrucciones
# ítems *_rev se puntúan al revés (suma si responde "No")
# -------------------------------------------------

QUESTIONS = [
    # ---------- RL: Razonamiento Lógico (14 ítems)
    {"text": "Cuando veo un patrón numérico (2, 4, 6, 8...), puedo anticipar el siguiente valor con facilidad.", "cat": "RL"},
    {"text": "Comprender relaciones causa-efecto en procesos me resulta sencillo.", "cat": "RL"},
    {"text": "Me es fácil detectar pasos fuera de orden en una secuencia de trabajo.", "cat": "RL"},
    {"text": "Puedo resolver problemas lógicos sin necesitar mucha ayuda.", "cat": "RL"},
    {"text": "Cuando algo no cuadra en las cifras, lo noto rápido.", "cat": "RL"},
    {"text": "Soy bueno/a siguiendo instrucciones complejas paso a paso.", "cat": "RL"},
    {"text": "Entiendo rápidamente gráficos o esquemas simples.", "cat": "RL"},
    {"text": "Me cuesta reconocer errores lógicos en una explicación.", "cat": "RL_rev"},
    {"text": "Si una pieza está girada o invertida, lo noto al tiro.", "cat": "RL"},
    {"text": "Puedo explicar a otros por qué una solución es correcta.", "cat": "RL"},
    {"text": "Me pierdo con facilidad cuando hay que pensar varios movimientos adelante.", "cat": "RL_rev"},
    {"text": "Ubico inconsistencias entre dos versiones distintas de la misma instrucción.", "cat": "RL"},
    {"text": "Detecto rápidamente cuándo una indicación no tiene sentido.", "cat": "RL"},
    {"text": "Para mí es difícil entender relaciones lógicas si no me las explican dos veces.", "cat": "RL_rev"},

    # ---------- AT: Atención al Detalle (14 ítems)
    {"text": "Suelo notar detalles pequeños (etiquetas, números, series) que otros pasan por alto.", "cat": "AT"},
    {"text": "Puedo revisar información repetitiva sin distraerme.", "cat": "AT"},
    {"text": "Me doy cuenta si hay un dígito cambiado en un código largo.", "cat": "AT"},
    {"text": "Pierdo foco fácilmente cuando tengo que revisar cosas muy chicas.", "cat": "AT_rev"},
    {"text": "Puedo mantenerme concentrado/a en tareas monótonas.", "cat": "AT"},
    {"text": "Si estoy etiquetando o clasificando piezas, rara vez me equivoco.", "cat": "AT"},
    {"text": "Confundo números parecidos (por ejemplo 8 y 3).", "cat": "AT_rev"},
    {"text": "Puedo detectar productos con fallas visuales menores.", "cat": "AT"},
    {"text": "Mantengo registro mental de pequeñas diferencias entre piezas similares.", "cat": "AT"},
    {"text": "Me cuesta fijarme en detalles finos cuando estoy cansado/a.", "cat": "AT_rev"},
    {"text": "Cuando debo verificar códigos o números de serie, lo hago con precisión.", "cat": "AT"},
    {"text": "Pierdo la cuenta fácilmente al contar elementos bajo presión.", "cat": "AT_rev"},
    {"text": "Me concentro bien incluso con ruido y distracciones.", "cat": "AT"},
    {"text": "Soy propenso/a a errores chicos que después generan reproceso.", "cat": "AT_rev"},

    # ---------- VD: Velocidad de Decisión (14 ítems)
    {"text": "Tomo decisiones operativas con rapidez cuando hay urgencia.", "cat": "VD"},
    {"text": "En tareas nuevas tardo demasiado antes de actuar.", "cat": "VD_rev"},
    {"text": "Cuando hay que priorizar, puedo elegir qué va primero sin dudar.", "cat": "VD"},
    {"text": "Puedo seguir trabajando incluso cuando hay que reaccionar al instante.", "cat": "VD"},
    {"text": "Me bloqueo cuando tengo que elegir rápido entre 2 opciones.", "cat": "VD_rev"},
    {"text": "Bajo presión, puedo decidir sin pedir siempre confirmación.", "cat": "VD"},
    {"text": "Si me cambian la orden en el momento, tardo mucho en adaptarme.", "cat": "VD_rev"},
    {"text": "Me resulta natural tomar control por unos minutos para ordenar la situación.", "cat": "VD"},
    {"text": "Me cuesta actuar rápido si la información no está completa.", "cat": "VD_rev"},
    {"text": "Puedo dividir tareas urgentes entre compañeros de forma clara.", "cat": "VD"},
    {"text": "Soy capaz de elegir una acción aunque falte un dato menor.", "cat": "VD"},
    {"text": "Pierdo tiempo dudando incluso con instrucciones relativamente simples.", "cat": "VD_rev"},
    {"text": "Mantengo claridad mental cuando todos piden algo al mismo tiempo.", "cat": "VD"},
    {"text": "Necesito demasiado rato antes de decidir qué hacer ante un imprevisto.", "cat": "VD_rev"},

    # ---------- MT: Memoria de Trabajo (14 ítems)
    {"text": "Puedo recordar 2 o 3 instrucciones seguidas sin tener que preguntarlas de nuevo.", "cat": "MT"},
    {"text": "Se me olvidan rápido los pasos cuando me los acaban de explicar.", "cat": "MT_rev"},
    {"text": "Retengo ubicaciones de herramientas o insumos sin anotarlas.", "cat": "MT"},
    {"text": "Puedo repetir una indicación reciente con las mismas palabras.", "cat": "MT"},
    {"text": "Olvido fácilmente números cortos (por ejemplo, un código de 4 dígitos).", "cat": "MT_rev"},
    {"text": "Recuerdo qué cambios se hicieron hace unos minutos, sin anotarlos.", "cat": "MT"},
    {"text": "Necesito que me repitan varias veces lo que acabo de oír.", "cat": "MT_rev"},
    {"text": "Puedo seguir una instrucción verbal sin tener que verla escrita.", "cat": "MT"},
    {"text": "Puedo retener temporalmente pequeñas cantidades de información técnica.", "cat": "MT"},
    {"text": "Si me dan varias tareas al hilo, pierdo el orden muy rápido.", "cat": "MT_rev"},
    {"text": "Puedo dar feedback al equipo sobre lo último que dijo la jefatura.", "cat": "MT"},
    {"text": "Pierdo la pista fácil de lo que estaba haciendo si me interrumpen.", "cat": "MT_rev"},
    {"text": "Mantengo en mente cambios de turno recién comunicados.", "cat": "MT"},
    {"text": "Necesito anotar todo o si no lo olvido al tiro.", "cat": "MT_rev"},

    # ---------- CI: Comprensión de Instrucciones (14 ítems)
    {"text": "Puedo leer una instrucción corta y aplicarla correctamente.", "cat": "CI"},
    {"text": "Necesito que me muestren físicamente la tarea porque leerla no me basta.", "cat": "CI_rev"},
    {"text": "Entiendo advertencias escritas de seguridad sin ayuda adicional.", "cat": "CI"},
    {"text": "Puedo interpretar rótulos, códigos o pictogramas de seguridad.", "cat": "CI"},
    {"text": "Me cuesta interpretar manuales escritos si no están explicados en persona.", "cat": "CI_rev"},
    {"text": "Si hay una pauta escrita, la puedo seguir sin supervisión constante.", "cat": "CI"},
    {"text": "Puedo explicar con mis palabras instrucciones que acabo de leer.", "cat": "CI"},
    {"text": "Aunque lea el procedimiento, igual hago preguntas básicas.", "cat": "CI_rev"},
    {"text": "Distingo pasos obligatorios vs pasos recomendados en una guía escrita.", "cat": "CI"},
    {"text": "Necesito confirmación constante porque dudo de mi interpretación de lo escrito.", "cat": "CI_rev"},
    {"text": "Comprendo rápido cambios de procedimiento que me entregan por escrito.", "cat": "CI"},
    {"text": "Me confundo con instrucciones nuevas y mezclo pasos.", "cat": "CI_rev"},
    {"text": "Puedo seguir una orden escrita aun si el supervisor no está presente.", "cat": "CI"},
    {"text": "Evito leer documentos largos porque siento que no los entiendo bien.", "cat": "CI_rev"},
]
TOTAL_QUESTIONS = len(QUESTIONS)  # 70


# -------------------------------------------------
# PERFILES DE CARGO (rangos esperados en bruto /14)
# -------------------------------------------------
JOB_PROFILES = {
    "operario": {
        "title": "Operario de Producción",
        "req": {
            "RL": (6, 14),
            "AT": (7, 14),
            "VD": (6, 14),
            "MT": (6, 14),
            "CI": (6, 14),
        },
    },
    "supervisor": {
        "title": "Supervisor Operativo",
        "req": {
            "RL": (8, 14),
            "AT": (7, 14),
            "VD": (8, 14),
            "MT": (7, 14),
            "CI": (8, 14),
        },
    },
    "tecnico": {
        "title": "Técnico de Mantenimiento",
        "req": {
            "RL": (8, 14),
            "AT": (8, 14),
            "VD": (7, 14),
            "MT": (7, 14),
            "CI": (8, 14),
        },
    },
    "logistica": {
        "title": "Personal de Logística",
        "req": {
            "RL": (6, 14),
            "AT": (6, 14),
            "VD": (6, 14),
            "MT": (6, 14),
            "CI": (6, 14),
        },
    },
}


# -------------------------------------------------
# ESTADO STREAMLIT
# -------------------------------------------------
if "stage" not in st.session_state:
    st.session_state.stage = "select_job"  # select_job → info → test → done

if "selected_job" not in st.session_state:
    st.session_state.selected_job = None

if "candidate_name" not in st.session_state:
    st.session_state.candidate_name = ""

if "evaluator_email" not in st.session_state:
    st.session_state.evaluator_email = DEFAULT_EVAL_EMAIL

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "answers" not in st.session_state:
    st.session_state.answers = {i: None for i in range(TOTAL_QUESTIONS)}

if "_need_rerun" not in st.session_state:
    st.session_state._need_rerun = False

if "already_sent" not in st.session_state:
    st.session_state.already_sent = False


# -------------------------------------------------
# SCORING
# -------------------------------------------------
def compute_scores(ans_dict):
    raw = {"RL": 0, "AT": 0, "VD": 0, "MT": 0, "CI": 0}
    for idx, q in enumerate(QUESTIONS):
        a = ans_dict.get(idx)
        if a is None:
            continue
        cat = q["cat"]
        if cat.endswith("_rev"):
            base = cat.replace("_rev", "")
            if a == 0:  # NO suma en invertida
                raw[base] += 1
        else:
            if a == 1:  # SÍ suma en directa
                raw[cat] += 1
    # índice global promedio bruto
    avg_raw = (raw["RL"] + raw["AT"] + raw["VD"] + raw["MT"] + raw["CI"]) / 5.0
    raw["G"] = avg_raw
    return raw


def level_from_raw(v14):
    if v14 >= 9:
        return "Alto"
    elif v14 >= 6:
        return "Medio"
    else:
        return "Bajo"


def build_dim_descriptions(raw_scores):
    desc = {}
    RL = raw_scores["RL"]; AT = raw_scores["AT"]; VD = raw_scores["VD"]
    MT = raw_scores["MT"]; CI = raw_scores["CI"]; G = raw_scores["G"]

    # RL
    if RL >= 9:
        desc["RL"] = "Analiza causas/efectos y detecta errores lógicos con rapidez."
    elif RL >= 6:
        desc["RL"] = "Razonamiento suficiente para entender pasos y detectar fallas comunes."
    else:
        desc["RL"] = "Podría requerir guía adicional para interpretar secuencias o causas."

    # AT
    if AT >= 9:
        desc["AT"] = "Alto foco en detalle y control visual, minimiza errores finos."
    elif AT >= 6:
        desc["AT"] = "Atención al detalle funcional en tareas repetitivas."
    else:
        desc["AT"] = "Riesgo de errores pequeños en tareas finas o monótonas."

    # VD
    if VD >= 9:
        desc["VD"] = "Decide rápido frente a urgencias y organiza prioridades bajo presión."
    elif VD >= 6:
        desc["VD"] = "Toma decisiones operativas con relativa agilidad, requiere confirmación puntual."
    else:
        desc["VD"] = "Puede dudar ante cambios bruscos; prefiere instrucciones claras al momento."

    # MT
    if MT >= 9:
        desc["MT"] = "Retiene instrucciones recientes con fidelidad y las replica correctamente."
    elif MT >= 6:
        desc["MT"] = "Memoria de trabajo adecuada para seguir varios pasos simples seguidos."
    else:
        desc["MT"] = "Podría necesitar repetición o apoyo escrito para no perder secuencia."

    # CI
    if CI >= 9:
        desc["CI"] = "Comprende instrucciones escritas y procedimientos formales con poca supervisión."
    elif CI >= 6:
        desc["CI"] = "Interpreta pautas escritas básicas y puede aplicarlas con apoyo moderado."
    else:
        desc["CI"] = "Puede requerir demostración práctica adicional antes de ejecutar instrucciones nuevas."

    # G
    if G >= 9:
        desc["G"] = "Perfil cognitivo global alto, con recursos sólidos para entender, priorizar y sostener tareas."
    elif G >= 6:
        desc["G"] = "Desempeño general funcional para entornos operativos estándar, con capacidad de aprendizaje directo."
    else:
        desc["G"] = "Puede requerir acompañamiento inicial cercano para asegurar ejecución consistente."

    return desc


def build_strengths_and_risks(raw_scores):
    RL = raw_scores["RL"]; AT = raw_scores["AT"]; VD = raw_scores["VD"]
    MT = raw_scores["MT"]; CI = raw_scores["CI"]

    fortalezas = []
    riesgos = []

    if RL >= 9:
        fortalezas.append("Analiza causas y consecuencias de manera lógica.")
    elif RL < 6:
        riesgos.append("Puede necesitar apoyo para interpretar secuencias y lógica de proceso.")

    if AT >= 9:
        fortalezas.append("Control de calidad visual y precisión en tareas repetitivas.")
    elif AT < 6:
        riesgos.append("Riesgo de errores finos o descuidos operativos bajo cansancio.")

    if VD >= 9:
        fortalezas.append("Toma decisiones rápidas en situaciones de presión.")
    elif VD < 6:
        riesgos.append("Puede dudar ante cambios urgentes; requiere instrucciones claras en caliente.")

    if MT >= 9:
        fortalezas.append("Retiene instrucciones recientes y las replica fielmente.")
    elif MT < 6:
        riesgos.append("Puede requerir repetición o apoyo escrito en secuencias largas.")

    if CI >= 9:
        fortalezas.append("Comprende pautas y advertencias escritas sin depender de supervisión.")
    elif CI < 6:
        riesgos.append("Podría necesitar demostración práctica adicional antes de ejecutar lo leído.")

    return fortalezas[:5], riesgos[:5]


def build_global_desc(raw_scores):
    G = raw_scores["G"]
    if G >= 9:
        return (
            "Describe un funcionamiento analítico y preciso, con buena velocidad "
            "de ejecución y retención de instrucciones."
        )
    elif G >= 6:
        return (
            "Refleja un funcionamiento adecuado para entornos operativos estándar, "
            "con capacidad de aprender la tarea y sostener calidad aceptable."
        )
    else:
        return (
            "Sugiere necesidad de apoyo cercano al inicio para asegurar "
            "estabilidad en la ejecución y en el seguimiento de instrucciones."
        )


def cargo_fit_text(job_key, raw_scores):
    profile = JOB_PROFILES[job_key]
    cargo_name = profile["title"]
    req = profile["req"]

    ok_all = True
    for dim, (mn, mx) in req.items():
        val = raw_scores[dim]
        if not (val >= mn and val <= mx):
            ok_all = False
            break

    if ok_all:
        return (
            f"Para el cargo {cargo_name}: Se observa un perfil que calza con las "
            f"exigencias típicas del puesto."
        )
    else:
        return (
            f"Para el cargo {cargo_name}: Se observan diferencias con lo esperado "
            f"en al menos una dimensión clave del rol."
        )


# -------------------------------------------------
# FUNCIONES DE DIBUJO PDF (ESTILO DISC)
# -------------------------------------------------

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

def _draw_par(c, text, x, y, width, font="Helvetica", size=8,
              leading=11, color=colors.black, max_lines=None):
    c.setFont(font, size)
    c.setFillColor(color)
    lines = _wrap(c, text, width, font, size)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        c.drawString(x, y, ln)
        y -= leading
    return y

def draw_slider(c, x, y, w, left_label, right_label, value_0_to_1):
    """
    value_0_to_1 = 0.0 izquierda, 1.0 derecha
    Dibujamos una línea gris y un punto negro que marca la posición.
    """
    line_y = y - 5
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.line(x, line_y, x + w, line_y)

    # etiquetas
    c.setFont("Helvetica",7)
    c.setFillColor(colors.black)
    c.drawString(x, y+2, left_label)
    c.drawRightString(x + w, y+2, right_label)

    # punto
    px = x + w * value_0_to_1
    c.setFillColor(colors.black)
    c.circle(px, line_y, 2.5, stroke=0, fill=1)

def pct_from_raw14(v14):
    # 0..14 → 0..100
    return (v14 / 14.0) * 100.0

def slider_pos_from_two(v_left, v_right):
    """
    Damos una posición entre dos polos.
    Ejemplo: "detalle" vs "pragmatismo":
       - usamos AT (detalle) vs VD (rapidez).
       value = AT / (AT+VD).
    Si la suma es 0, centramos.
    """
    s = v_left + v_right
    if s <= 0:
        return 0.5
    return v_left / s  # 0..1


def generate_pdf_iq(
    candidate_name,
    cargo_name,
    fecha_eval,
    evaluator_email,
    raw_scores,
    fortalezas,
    riesgos,
    global_desc,
    ajuste_text
):
    """
    Nuevo layout tipo DISC:
    - Encabezado con logo y título arriba.
    - Izquierda: gráfico de barras (%).
    - Derecha: cuadro con datos del candidato + bullets resumen.
    - Abajo: sliders conductuales (tendencias).
    - Último bloque: "Perfil general" (global_desc + ajuste_text).
    """

    buf = BytesIO()
    W, H = A4  # 595 x 842 aprox
    c = canvas.Canvas(buf, pagesize=A4)

    margin_left = 36
    margin_right = 36
    usable_w = W - margin_left - margin_right

    # -------------------------------------------------
    # HEADER
    # -------------------------------------------------
    # Logo ficticio lado izquierdo
    c.setFont("Helvetica-Bold",12)
    c.setFillColor(colors.black)
    c.drawString(margin_left, H-40, "miPerfilIQ®")
    c.setFont("Helvetica",7)
    c.drawString(margin_left, H-55, "capacidad cognitiva & empleo")

    # Título lado derecho
    c.setFont("Helvetica",8)
    c.setFillColor(colors.black)
    c.drawRightString(W-margin_right, H-40, "Perfil cognitivo operativo - Confidencial RR.HH.")

    # -------------------------------------------------
    # GRAFICO DE BARRAS IZQUIERDA
    # -------------------------------------------------
    chart_x = margin_left
    chart_y_bottom = H-300
    chart_w = 180
    chart_h = 140

    # eje Y %
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(chart_x, chart_y_bottom, chart_x, chart_y_bottom+chart_h)

    # rejilla 0..100
    for tick in [0,20,40,60,80,100]:
        yv = chart_y_bottom + (tick/100.0)*chart_h
        c.setFont("Helvetica",6)
        c.setFillColor(colors.black)
        c.drawString(chart_x-20, yv-2, str(tick))
        c.setStrokeColor(colors.lightgrey)
        c.line(chart_x, yv, chart_x+chart_w, yv)

    dims_for_chart = [
        ("RL","RL", colors.HexColor("#3b82f6")),
        ("AT","AT", colors.HexColor("#22c55e")),
        ("VD","VD", colors.HexColor("#f97316")),
        ("MT","MT", colors.HexColor("#6b7280")),
        ("CI","CI", colors.HexColor("#0ea5b7")),
        ("G","G",  colors.HexColor("#2563eb")),  # global
    ]

    gap = 8
    bar_w = (chart_w - gap*(len(dims_for_chart)+1)) / len(dims_for_chart)
    tops = []

    for i,(key,label,color_bar) in enumerate(dims_for_chart):
        if key == "G":
            # G es promedio bruto 0..14 -> % usando el mismo mapeo
            bruto = raw_scores["G"]  # 0..14
            pct_val = (bruto/14.0)*100.0
        else:
            bruto = raw_scores.get(key,0)
            pct_val = pct_from_raw14(bruto)

        bx = chart_x + gap + i*(bar_w+gap)
        bh = (pct_val/100.0)*chart_h
        by = chart_y_bottom

        c.setStrokeColor(colors.black)
        c.setFillColor(color_bar)
        c.rect(bx, by, bar_w, bh, stroke=1, fill=1)

        tops.append((bx+bar_w/2.0, by+bh))

        # etiqueta bajo la barra
        c.setFont("Helvetica-Bold",7)
        c.setFillColor(colors.black)
        c.drawCentredString(bx+bar_w/2.0, chart_y_bottom-12, label)

        # puntaje bruto simple
        if key == "G":
            score_txt = f"{bruto:.1f}/14"
        else:
            score_txt = f"{int(bruto)}/14"
        c.setFont("Helvetica",6)
        c.drawCentredString(bx+bar_w/2.0, chart_y_bottom-24, score_txt)

    # línea poligonal
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    for j in range(len(tops)-1):
        (x1,y1)=tops[j]
        (x2,y2)=tops[j+1]
        c.line(x1,y1,x2,y2)
    for (px,py) in tops:
        c.setFillColor(colors.black)
        c.circle(px,py,2,stroke=0,fill=1)

    # título eje Y
    c.setFont("Helvetica",7)
    c.setFillColor(colors.black)
    c.drawString(chart_x, chart_y_bottom+chart_h+12, "Nivel (porcentaje estimado)")

    # Eje X label
    c.setFont("Helvetica",6)
    c.drawString(chart_x, chart_y_bottom-36,
                 "Dimensiones cognitivas: RL AT VD MT CI G")

    # -------------------------------------------------
    # PANEL DATOS + BULLETS A LA DERECHA DEL GRÁFICO
    # -------------------------------------------------
    panel_x = chart_x + chart_w + 20
    panel_y_top = H-150
    panel_w = (W - margin_right) - panel_x
    panel_h = 180  # caja alta

    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.setFillColor(colors.white)
    c.rect(panel_x, panel_y_top-panel_h, panel_w, panel_h, stroke=1, fill=0)

    yy = panel_y_top - 12
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(panel_x+8, yy, candidate_name.upper())
    yy -= 11
    c.setFont("Helvetica",7)
    c.drawString(panel_x+8, yy, f"Cargo evaluado: {cargo_name}")
    yy -= 11
    c.drawString(panel_x+8, yy, f"Fecha de evaluación: {fecha_eval}")
    yy -= 11
    c.drawString(panel_x+8, yy, f"Evaluador: {evaluator_email.upper()}")
    yy -= 11
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawString(panel_x+8, yy, "Uso interno RR.HH. / No clínico.")
    yy -= 18

    # bullets resumen (fortalezas + riesgos juntos como puntos)
    c.setFont("Helvetica",7)
    c.setFillColor(colors.black)

    bullets = []
    for f in fortalezas:
        bullets.append(f)
    for r in riesgos:
        bullets.append(r)

    # mostramos hasta 6 viñetas
    bullets = bullets[:6]

    for btxt in bullets:
        lines = _wrap(c, "• " + btxt, panel_w-16, "Helvetica",7)
        for ln in lines:
            c.drawString(panel_x+8, yy, ln)
            yy -= 10
        yy -= 2
        if yy < (panel_y_top-panel_h)+20:
            break

    # -------------------------------------------------
    # SLIDERS CONDUCTUALES (A LO LARGO DE LA HOJA)
    # -------------------------------------------------
    sliders_x = margin_left
    sliders_y_top = H-330
    sliders_w = W - margin_left - margin_right

    # cálculos para posicionar las pelotitas:
    RL = raw_scores["RL"]
    AT = raw_scores["AT"]
    VD = raw_scores["VD"]
    MT = raw_scores["MT"]
    CI = raw_scores["CI"]
    G  = raw_scores["G"]

    # 1. Detalle vs Pragmatismo: AT (detalle) vs VD (rapidez práctica)
    pos_detalle = slider_pos_from_two(AT, VD)

    # 2. Calidad / precisión vs Velocidad / acción
    #    Reusamos AT vs VD pero invertimos sentido
    pos_calidad = slider_pos_from_two(AT, VD)  # mismo cálculo, distinto label

    # 3. Analítico vs Intuitivo → RL alto = analítico
    pos_analitico = min(max(RL/14.0,0),1)

    # 4. Autonomía vs Necesita apoyo → CI y MT altos = más autónomo
    autonomy_raw = (CI + MT)/28.0  # 0..1 aprox
    pos_autonomia = min(max(autonomy_raw,0),1)

    # 5. Control / Organización vs Flexibilidad improvisada
    #    usamos VD (acción rápida / flexible) vs MT (sostener orden)
    pos_control = slider_pos_from_two(MT, VD)

    # Dibujamos cada fila
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(sliders_x, sliders_y_top, "Indicadores de estilo operativo observado")
    cur_y = sliders_y_top - 14

    draw_slider(
        c,
        x=sliders_x+5,
        y=cur_y,
        w=sliders_w-10,
        left_label="Más detallista",
        right_label="Más pragmático",
        value_0_to_1=pos_detalle
    )
    cur_y -= 24

    draw_slider(
        c,
        x=sliders_x+5,
        y=cur_y,
        w=sliders_w-10,
        left_label="Enfoque en calidad / control",
        right_label="Velocidad operativa",
        value_0_to_1=pos_calidad
    )
    cur_y -= 24

    draw_slider(
        c,
        x=sliders_x+5,
        y=cur_y,
        w=sliders_w-10,
        left_label="Más analítico",
        right_label="Más intuitivo",
        value_0_to_1=pos_analitico
    )
    cur_y -= 24

    draw_slider(
        c,
        x=sliders_x+5,
        y=cur_y,
        w=sliders_w-10,
        left_label="Trabaja autónomo",
        right_label="Requiere apoyo cercano",
        value_0_to_1=pos_autonomia
    )
    cur_y -= 24

    draw_slider(
        c,
        x=sliders_x+5,
        y=cur_y,
        w=sliders_w-10,
        left_label="Más orden / método",
        right_label="Más reacción inmediata",
        value_0_to_1=pos_control
    )
    cur_y -= 36

    # -------------------------------------------------
    # PERFIL GENERAL (párrafo tipo DISC)
    # -------------------------------------------------
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(margin_left, cur_y, "Perfil general")
    cur_y -= 12

    # armamos un párrafo resumen tipo "Metódico, Analítico, Preciso..."
    perfil_general_txt = (
        f"{global_desc} {ajuste_text}"
    )

    cur_y = _draw_par(
        c,
        perfil_general_txt,
        margin_left,
        cur_y,
        usable_w,
        font="Helvetica",
        size=7,
        leading=10,
        color=colors.black,
        max_lines=8
    )

    cur_y -= 10
    nota_txt = (
        "Documento interno orientado a selección operativa. "
        "Describe tendencias cognitivas útiles para rol productivo "
        "y NO corresponde a diagnóstico clínico."
    )
    cur_y = _draw_par(
        c,
        nota_txt,
        margin_left,
        cur_y,
        usable_w,
        font="Helvetica",
        size=6,
        leading=9,
        color=colors.grey,
        max_lines=5
    )

    # Footer pequeño al final
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawRightString(W-margin_right, 30, "Uso interno RR.HH. · Evaluación Cognitiva Operativa · No clínico")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


# -------------------------------------------------
# ENVÍO DE CORREO CON PDF
# -------------------------------------------------
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


# -------------------------------------------------
# GENERAR + ENVIAR INFORME FINAL
# -------------------------------------------------
def finalize_and_send():
    raw_scores = compute_scores(st.session_state.answers)

    fortalezas, riesgos = build_strengths_and_risks(raw_scores)
    global_desc = build_global_desc(raw_scores)
    ajuste_text = cargo_fit_text(st.session_state.selected_job, raw_scores)

    now_txt = datetime.now().strftime("%d/%m/%Y %H:%M")
    cargo_name = JOB_PROFILES[st.session_state.selected_job]["title"]

    pdf_bytes = generate_pdf_iq(
        candidate_name   = st.session_state.candidate_name,
        cargo_name       = cargo_name,
        fecha_eval       = now_txt,
        evaluator_email  = st.session_state.evaluator_email,
        raw_scores       = raw_scores,
        fortalezas       = fortalezas,
        riesgos          = riesgos,
        global_desc      = global_desc,
        ajuste_text      = ajuste_text
    )

    if not st.session_state.already_sent:
        try:
            send_email_with_pdf(
                to_email   = st.session_state.evaluator_email,
                pdf_bytes  = pdf_bytes,
                filename   = "Informe_Cognitivo_Operativo.pdf",
                subject    = "Informe Cognitivo Operativo (Selección)",
                body_text  = (
                    "Adjunto informe interno de evaluación cognitiva operativa "
                    f"({st.session_state.candidate_name} / {cargo_name}). "
                    "Uso interno RR.HH."
                ),
            )
        except Exception:
            pass
        st.session_state.already_sent = True


# -------------------------------------------------
# CALLBACK PARA RESPUESTAS (sin doble click)
# -------------------------------------------------
def choose_answer(value_yes_or_no: int):
    q_idx = st.session_state.current_q
    st.session_state.answers[q_idx] = value_yes_or_no

    if q_idx < TOTAL_QUESTIONS - 1:
        st.session_state.current_q += 1
        st.session_state._need_rerun = True
    else:
        finalize_and_send()
        st.session_state.stage = "done"
        st.session_state._need_rerun = True


# -------------------------------------------------
# VISTAS STREAMLIT
# -------------------------------------------------
def view_select_job():
    st.markdown("### Evaluación Cognitiva Operativa (IQ Adaptado)")
    st.write("Seleccione el cargo a evaluar:")

    cols = st.columns(2)
    keys_list = list(JOB_PROFILES.keys())
    for i, job_key in enumerate(keys_list):
        with cols[i % 2]:
            if st.button(JOB_PROFILES[job_key]["title"], key=f"job_{job_key}", use_container_width=True):
                st.session_state.selected_job = job_key
                st.session_state.stage = "info"
                st.session_state._need_rerun = True


def view_info_form():
    cargo_titulo = JOB_PROFILES[st.session_state.selected_job]["title"]
    st.markdown(f"#### Datos del candidato\n**Cargo evaluado:** {cargo_titulo}")
    st.info("Estos datos se usan para generar el informe PDF interno y enviarlo automáticamente a RR.HH.")

    st.session_state.candidate_name = st.text_input(
        "Nombre del candidato",
        value=st.session_state.candidate_name,
        placeholder="Nombre completo"
    )

    st.session_state.evaluator_email = st.text_input(
        "Correo del evaluador (RR.HH. / Supervisor)",
        value=st.session_state.evaluator_email or DEFAULT_EVAL_EMAIL,
        placeholder="nombre@empresa.com"
    )

    ok = (
        len(st.session_state.candidate_name.strip()) > 0 and
        len(st.session_state.evaluator_email.strip()) > 0
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
    progreso = (q_idx + 1) / TOTAL_QUESTIONS

    # Header de la pregunta
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
                Test Cognitivo Operativo (70 ítems)
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

    # Tarjeta de la pregunta
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

    col_yes, col_no = st.columns(2)
    with col_yes:
        st.button(
            "Sí",
            key=f"yes_{q_idx}",
            type="primary",
            use_container_width=True,
            on_click=choose_answer,
            args=(1,)
        )
    with col_no:
        st.button(
            "No",
            key=f"no_{q_idx}",
            use_container_width=True,
            on_click=choose_answer,
            args=(0,)
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
            <b>Confidencialidad:</b> Uso interno RR.HH. / Selección operativa.
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


# -------------------------------------------------
# FLUJO PRINCIPAL
# -------------------------------------------------
if st.session_state.stage == "select_job":
    view_select_job()

elif st.session_state.stage == "info":
    view_info_form()

elif st.session_state.stage == "test":
    if st.session_state.current_q >= TOTAL_QUESTIONS:
        st.session_state.stage = "done"
        st.session_state._need_rerun = True
    view_test()

elif st.session_state.stage == "done":
    finalize_and_send()
    view_done()

# Rerun controlado para avanzar sin doble click
if st.session_state._need_rerun:
    st.session_state._need_rerun = False
    st.rerun()
