# ============================================================
# TEST COGNITIVO OPERATIVO (IQ ADAPTADO) · 70 ÍTEMS
# Visual estilo EPQR (card blanca + barra progreso)
# PDF ordenado y ancho completo en secciones largas
# Envío automático de PDF al evaluador (sin mostrar informe en pantalla)
# Pantalla final: "Evaluación finalizada"
# Requiere: pip install streamlit reportlab
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
# CREDENCIALES DE CORREO (reemplaza por las tuyas reales si cambian)
# -------------------------------------------------
FROM_ADDR = "jo.tajtaj@gmail.com"
APP_PASS  = "nlkt kujl ebdg cyts"   # clave de app Gmail
DEFAULT_EVAL_EMAIL = "jo.tajtaj@gmail.com"  # a quién enviar el informe


# -------------------------------------------------
# DEFINICIÓN DE DIMENSIONES COGNITIVAS
# Vamos a medir 5 dimensiones base + índice global:
# RL = Razonamiento Lógico / Secuencias
# AT = Atención al Detalle / Precisión
# VD = Velocidad de Decisión / Juicio rápido
# MT = Memoria de Trabajo / Retención inmediata
# CI = Comprensión de Instrucciones / Lectura Operativa
#
# Cada dimensión tendrá 14 ítems => 14 x 5 = 70
# Nota: para simplificar el ejemplo, los ítems son sí/no.
# En producción puedes reemplazar por reactivos reales tipo matrices / analogías, etc.
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

    # ---------- AT: Atención al Detalle / Precisión (14 ítems)
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

    # ---------- VD: Velocidad de Decisión / Juicio rápido (14 ítems)
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

    # ---------- MT: Memoria de Trabajo / Retención inmediata (14 ítems)
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

    # ---------- CI: Comprensión de Instrucciones / Lectura Operativa (14 ítems)
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
# PERFILES DE CARGO (rangos esperados promedio bruto de cada dimensión)
# Aquí definimos el ajuste al cargo. Los rangos son ejemplo.
# -------------------------------------------------
JOB_PROFILES = {
    "operario": {
        "title": "Operario de Producción",
        # Rangos esperados en puntaje bruto /14 por dimensión
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
# SCORING / PERFIL COGNITIVO
# Reglas:
#   - cat normal (RL, AT, VD, MT, CI): sumar 1 si responde "Sí"/1.
#   - cat con "_rev": sumar 1 si responde "No"/0 (porque son ítems invertidos).
# G (global) = promedio bruto de las 5 dimensiones en 0-14, escalado /10 para el PDF.
# -------------------------------------------------
def compute_scores(ans_dict):
    raw = {
        "RL": 0,
        "AT": 0,
        "VD": 0,
        "MT": 0,
        "CI": 0,
    }

    for idx, q in enumerate(QUESTIONS):
        a = ans_dict.get(idx)
        if a is None:
            continue
        cat = q["cat"]

        if cat.endswith("_rev"):
            base = cat.replace("_rev", "")
            # Suma si respondió NO (0) en ítem inverso
            if a == 0:
                raw[base] += 1
        else:
            # normal: suma si respondió SÍ (1)
            if a == 1:
                raw[cat] += 1

    # promedio bruto para global
    avg_raw = (raw["RL"] + raw["AT"] + raw["VD"] + raw["MT"] + raw["CI"]) / 5.0
    raw["G"] = avg_raw  # G se maneja aparte en PDF

    return raw


def level_from_raw(v14):
    # Clasificación simple
    # >=9/14 "Alto", >=6/14 "Medio", <6 "Bajo"
    # Para G usamos el mismo criterio pero con escala /14 aprox
    if v14 >= 9:
        return "Alto"
    elif v14 >= 6:
        return "Medio"
    else:
        return "Bajo"


def build_dim_descriptions(raw_scores):
    """
    Devuelve un dict por dimensión con texto breve
    para la tabla 'Detalle por dimensión'.
    """
    desc = {}

    RL = raw_scores["RL"]
    AT = raw_scores["AT"]
    VD = raw_scores["VD"]
    MT = raw_scores["MT"]
    CI = raw_scores["CI"]
    G  = raw_scores["G"]

    # RL
    if RL >= 9:
        desc["RL"] = (
            "Capacidad sólida para identificar secuencias lógicas, "
            "entender causas/efectos y detectar inconsistencias en procesos."
        )
    elif RL >= 6:
        desc["RL"] = (
            "Muestra razonamiento operativo adecuado para interpretar pasos "
            "y detectar errores comunes."
        )
    else:
        desc["RL"] = (
            "Podría requerir apoyo extra para detectar fallas lógicas o "
            "anticipar el paso siguiente sin guía directa."
        )

    # AT
    if AT >= 9:
        desc["AT"] = (
            "Destaca en precisión visual y control de detalles pequeños, "
            "reduciendo reprocesos por errores finos."
        )
    elif AT >= 6:
        desc["AT"] = (
            "Mantiene un nivel práctico de atención al detalle y consistencia "
            "en tareas repetitivas."
        )
    else:
        desc["AT"] = (
            "Puede presentar deslices en tareas finas o repetitivas, "
            "lo que sugiere necesidad de verificación adicional."
        )

    # VD
    if VD >= 9:
        desc["VD"] = (
            "Toma decisiones ágiles frente a urgencia, prioriza y ejecuta "
            "con rapidez sin bloquearse."
        )
    elif VD >= 6:
        desc["VD"] = (
            "Responde de manera funcional en escenarios con presión temporal, "
            "requiriendo confirmación ocasional."
        )
    else:
        desc["VD"] = (
            "Puede dudar ante cambios rápidos o imprevistos; "
            "podría necesitar instrucciones claras en caliente."
        )

    # MT
    if MT >= 9:
        desc["MT"] = (
            "Retiene instrucciones recientes y las replica con fidelidad, "
            "lo que favorece la continuidad operativa."
        )
    elif MT >= 6:
        desc["MT"] = (
            "Memoria de trabajo adecuada para seguir varios pasos simples "
            "sin necesidad de repetir."
        )
    else:
        desc["MT"] = (
            "Podría requerir instrucciones reiteradas o apoyo escrito "
            "para sostener secuencias de pasos."
        )

    # CI
    if CI >= 9:
        desc["CI"] = (
            "Interpreta instrucciones escritas, códigos y advertencias "
            "con claridad, pudiendo actuar con mínima supervisión."
        )
    elif CI >= 6:
        desc["CI"] = (
            "Comprende pautas básicas por escrito y puede aplicarlas "
            "con apoyo moderado."
        )
    else:
        desc["CI"] = (
            "Podría necesitar refuerzo verbal o demostración práctica "
            "antes de aplicar instrucciones nuevas."
        )

    # G (global)
    if G >= 9:
        desc["G"] = (
            "Describe un perfil cognitivo global alto, con recursos sólidos "
            "para comprender, decidir y sostener tareas bajo presión."
        )
    elif G >= 6:
        desc["G"] = (
            "Indica un desempeño global funcional para entornos operativos, "
            "con capacidad de aprender y sostener instrucciones."
        )
    else:
        desc["G"] = (
            "Sugiere necesidad de acompañamiento inicial más cercano "
            "para asegurar comprensión y ejecución estable."
        )

    return desc


def build_strengths_and_risks(raw_scores):
    """
    Genera listas de fortalezas y aspectos a monitorear para el bloque
    'Resumen cognitivo observado'.
    """
    RL = raw_scores["RL"]
    AT = raw_scores["AT"]
    VD = raw_scores["VD"]
    MT = raw_scores["MT"]
    CI = raw_scores["CI"]

    fortalezas = []
    riesgos = []

    if RL >= 9:
        fortalezas.append("Capacidad para detectar fallas lógicas y anticipar pasos críticos.")
    elif RL < 6:
        riesgos.append("Podría requerir guía adicional para interpretar secuencias y causas/efectos.")

    if AT >= 9:
        fortalezas.append("Control de detalle y consistencia visual que reduce reprocesos.")
    elif AT < 6:
        riesgos.append("Riesgo de errores menores en tareas repetitivas o muy finas.")

    if VD >= 9:
        fortalezas.append("Toma decisiones rápida en entornos dinámicos.")
    elif VD < 6:
        riesgos.append("Puede dudar ante cambios urgentes; mejor con instrucciones claras.")

    if MT >= 9:
        fortalezas.append("Retención inmediata estable, replica instrucciones con fidelidad.")
    elif MT < 6:
        riesgos.append("Puede necesitar que le repitan o dejarle apuntes visibles.")

    if CI >= 9:
        fortalezas.append("Comprende instrucciones escritas y las ejecuta con autonomía.")
    elif CI < 6:
        riesgos.append("Podría requerir demostración práctica adicional antes de actuar.")

    # Limitar tamaño visual
    return fortalezas[:5], riesgos[:5]


def build_global_desc(raw_scores):
    G = raw_scores["G"]
    if G >= 9:
        return (
            "El perfil global sugiere recursos cognitivos sólidos para ejecutar, "
            "priorizar y sostener instrucciones en ritmo operativo acelerado."
        )
    elif G >= 6:
        return (
            "El desempeño cognitivo global se considera funcional para entornos "
            "operativos estándar, con capacidad de aprendizaje directo en el puesto."
        )
    else:
        return (
            "El desempeño indica que podría requerir acompañamiento inicial más "
            "cercano y supervisión clara para asegurar consistencia en la tarea."
        )


def cargo_fit_text(job_key, raw_scores):
    """
    Devuelve texto de ajuste al cargo. Si todas las dimensiones
    están dentro del rango esperado -> "CONSISTENTE".
    Si alguna queda fuera -> "NO CONSISTENTE".
    """
    profile = JOB_PROFILES[job_key]
    req = profile["req"]  # dict {dim:(min,max)}
    cargo_name = profile["title"]

    ok_all = True
    for dim, (mn, mx) in req.items():
        got = raw_scores[dim]
        if not (got >= mn and got <= mx):
            ok_all = False
            break

    if ok_all:
        return (
            f"Ajuste al cargo: El perfil evaluado se considera "
            f"GLOBALMENTE CONSISTENTE con las exigencias habituales "
            f"del cargo {cargo_name}."
        )
    else:
        return (
            f"Ajuste al cargo: El perfil evaluado NO SE CONSIDERA CONSISTENTE "
            f"con las exigencias habituales del cargo {cargo_name}."
        )


# -------------------------------------------------
# UTILIDADES PARA PDF (con la nueva maquetación corregida)
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

def generate_pdf_iq(candidate_name,
                    cargo_name,
                    fecha_eval,
                    evaluator_email,
                    raw_scores,
                    strengths_list,
                    monitor_list,
                    desc_by_dim,
                    global_desc,
                    ajuste_text,
                    nota_text):
    """
    Layout final ajustado:
    - Header
    - Izquierda: gráfico barras (0-10 visual)
    - Derecha: datos + guía
    - Caja ancho completo: Resumen cognitivo observado
    - Caja ancho completo: Detalle por dimensión
    - Caja ancho completo: Desempeño Global / Ajuste / Nota
    """

    buf = BytesIO()
    W, H = A4
    c = canvas.Canvas(buf, pagesize=A4)

    margin_left = 36
    margin_right = 36
    usable_w = W - margin_left - margin_right

    # ---------- HEADER ----------
    c.setFont("Helvetica-Bold",10)
    c.drawString(margin_left, H-40, "EMPRESA / LOGO")
    c.setFont("Helvetica",7)
    c.drawString(margin_left, H-55, "Evaluación de capacidad cognitiva aplicada al rol")

    c.setFont("Helvetica-Bold",11)
    c.drawRightString(W-margin_right, H-40, "Perfil Cognitivo Operativo (IQ Adaptado)")
    c.setFont("Helvetica",7)
    c.drawRightString(W-margin_right, H-55,
        "Uso interno RR.HH. / Procesos productivos · No clínico")

    # ---------- GRÁFICO IZQUIERDA ----------
    chart_x = margin_left
    chart_y_bottom = H-260
    chart_w = 240
    chart_h = 120

    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    # eje Y
    c.line(chart_x, chart_y_bottom, chart_x, chart_y_bottom+chart_h)

    # grid 0..10
    for lvl in range(0,11):
        yv = chart_y_bottom + (lvl/10.0)*chart_h
        c.setFont("Helvetica",6)
        c.setFillColor(colors.black)
        c.drawString(chart_x-15, yv-2, str(lvl))
        c.setStrokeColor(colors.lightgrey)
        c.line(chart_x, yv, chart_x+chart_w, yv)

    dims_order = [
        ("RL","RL", colors.HexColor("#3b82f6")),
        ("AT","AT", colors.HexColor("#22c55e")),
        ("VD","VD", colors.HexColor("#f97316")),
        ("MT","MT", colors.HexColor("#6b7280")),
        ("CI","CI", colors.HexColor("#0ea5b7")),
    ]

    def to_scale10(v14):
        return (v14/14.0)*10.0

    gap = 10
    bar_w = (chart_w - gap*(len(dims_order)+1)) / len(dims_order)
    tops = []

    for i,(key,label,color_bar) in enumerate(dims_order):
        bruto = raw_scores.get(key,0)
        val10 = to_scale10(bruto)

        bx = chart_x + gap + i*(bar_w+gap)
        bh = (val10/10.0)*chart_h
        by = chart_y_bottom

        c.setStrokeColor(colors.black)
        c.setFillColor(color_bar)
        c.rect(bx, by, bar_w, bh, stroke=1, fill=1)

        tops.append((bx+bar_w/2.0, by+bh))

        c.setFont("Helvetica-Bold",7)
        c.setFillColor(colors.black)
        c.drawCentredString(bx+bar_w/2.0, chart_y_bottom-14, label)

        # Puntaje bruto único
        c.setFont("Helvetica",6)
        c.drawCentredString(
            bx+bar_w/2.0,
            chart_y_bottom-26,
            f"{int(bruto)}/14"
        )

    # línea que une puntos
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.2)
    for j in range(len(tops)-1):
        (x1,y1)=tops[j]
        (x2,y2)=tops[j+1]
        c.line(x1,y1,x2,y2)
    for (px,py) in tops:
        c.setFillColor(colors.black)
        c.circle(px,py,2.0,stroke=0,fill=1)

    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(chart_x, chart_y_bottom+chart_h+12,
                 "Perfil cognitivo normalizado (0–10 visual)")

    # ---------- BLOQUE DERECHA: DATOS + GUÍA ----------
    box_x = chart_x + chart_w + 24
    box_w = (W - margin_right) - box_x

    # Datos candidato
    box1_h = 72
    box1_y_top = H-160
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(box_x, box1_y_top-box1_h, box_w, box1_h, stroke=1, fill=1)

    yy = box1_y_top-14
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(box_x+8, yy, f"Nombre: {candidate_name}")
    yy -= 11
    c.setFont("Helvetica",8)
    c.drawString(box_x+8, yy, f"Cargo evaluado: {cargo_name}")
    yy -= 11
    c.drawString(box_x+8, yy, f"Fecha evaluación: {fecha_eval}")
    yy -= 11
    c.drawString(box_x+8, yy, f"Evaluador: {evaluator_email.upper()}")
    yy -= 11
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawString(box_x+8, yy, "Documento interno. No clínico.")

    # Guía de lectura
    box2_h = 80
    box2_y_top = box1_y_top - box1_h - 12
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(box_x, box2_y_top-box2_h, box_w, box2_h, stroke=1, fill=1)

    gy = box2_y_top-14
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(box_x+8, gy, "Guía de lectura de dimensiones")
    gy -= 12
    c.setFont("Helvetica",7)
    guia_lines = [
        "RL = Razonamiento Lógico / Secuencias",
        "AT = Atención al Detalle / Precisión",
        "VD = Velocidad de Decisión / Juicio rápido",
        "MT = Memoria de Trabajo / Retención inmediata",
        "CI = Comprensión de Instrucciones / Lectura Operativa",
        "G  = Índice Cognitivo Global (promedio)",
    ]
    for gl in guia_lines:
        c.drawString(box_x+8, gy, gl)
        gy -= 10

    # ---------- BLOQUE CENTRAL (ANCHO COMPLETO):
    # RESUMEN COGNITIVO OBSERVADO
    resumen_y_top = H-320
    resumen_h = 120
    resumen_x = margin_left
    resumen_w = usable_w

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(resumen_x, resumen_y_top-resumen_h, resumen_w, resumen_h, stroke=1, fill=1)

    ry = resumen_y_top-14
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(resumen_x+8, ry, "Resumen cognitivo observado")
    ry -= 14

    # Fortalezas
    c.setFont("Helvetica-Bold",7)
    c.drawString(resumen_x+8, ry, "Fortalezas potenciales:")
    ry -= 12

    c.setFont("Helvetica",7)
    for f in strengths_list:
        wrapped = _wrap(c, "• " + f, resumen_w-16, "Helvetica",7)
        for line in wrapped:
            c.drawString(resumen_x+12, ry, line)
            ry -= 10
            if ry < (resumen_y_top-resumen_h)+28:
                break
        if ry < (resumen_y_top-resumen_h)+28:
            break

    ry -= 6
    c.setFont("Helvetica-Bold",7)
    c.drawString(resumen_x+8, ry, "Aspectos a monitorear / apoyo sugerido:")
    ry -= 12

    c.setFont("Helvetica",7)
    for m in monitor_list:
        wrapped = _wrap(c, "• " + m, resumen_w-16, "Helvetica",7)
        for line in wrapped:
            c.drawString(resumen_x+12, ry, line)
            ry -= 10
            if ry < (resumen_y_top-resumen_h)+8:
                break
        if ry < (resumen_y_top-resumen_h)+8:
            break

    # ---------- DETALLE POR DIMENSIÓN (ANCHO COMPLETO)
    table_y_top = resumen_y_top - resumen_h - 16
    table_h = 170
    table_x = margin_left
    table_w = usable_w

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(table_x, table_y_top-table_h, table_w, table_h, stroke=1, fill=1)

    # Título tabla
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(table_x+8, table_y_top-14, "Detalle por dimensión")

    header_y = table_y_top-32
    c.setStrokeColor(colors.black)
    c.line(table_x, header_y+6, table_x+table_w, header_y+6)

    c.setFont("Helvetica-Bold",7)
    c.drawString(table_x+8,   header_y, "Dimensión")
    c.drawString(table_x+240, header_y, "Puntaje")
    c.drawString(table_x+300, header_y, "Nivel")
    c.drawString(table_x+350, header_y, "Descripción breve")

    row_y = header_y-16
    row_spacing = 34  # fila más alta para evitar texto encima

    # valores para la tabla
    avg_raw = raw_scores["G"]  # promedio bruto 0..14
    dim_rows = [
        ("RL", "Razonamiento Lógico / Secuencias", raw_scores["RL"]),
        ("AT", "Atención al Detalle / Precisión",  raw_scores["AT"]),
        ("VD", "Velocidad de Decisión / Juicio rápido", raw_scores["VD"]),
        ("MT", "Memoria de Trabajo / Retención inmediata", raw_scores["MT"]),
        ("CI", "Comprensión de Instrucciones / Lectura Operativa", raw_scores["CI"]),
        ("G",  "Índice Cognitivo Global (G)", avg_raw),
    ]

    for key,label,val in dim_rows:
        # columna texto dimensión
        c.setFont("Helvetica-Bold",7)
        c.setFillColor(colors.black)
        c.drawString(table_x+8, row_y, label)

        # puntaje: para G usamos /10 aprox, resto /14
        c.setFont("Helvetica",7)
        if key == "G":
            puntaje_txt = f"{val:.1f}/10"
            lvl_txt = level_from_raw(val)  # usa misma lógica
        else:
            puntaje_txt = f"{int(val)}/14"
            lvl_txt = level_from_raw(val)

        c.drawString(table_x+240, row_y, puntaje_txt)
        c.drawString(table_x+300, row_y, lvl_txt)

        # descripción breve envuelta
        desc_txt = desc_by_dim.get(key, "")
        row_y = _draw_par(
            c,
            desc_txt,
            table_x+350,
            row_y,
            table_w-360,
            font="Helvetica",
            size=7,
            leading=9,
            color=colors.black,
            max_lines=3
        )

        row_y -= (row_spacing-18)

    # ---------- BLOQUE FINAL: DESEMPEÑO GLOBAL / AJUSTE / NOTA
    bottom_block_h = 160
    bottom_block_y_top = table_y_top - table_h - 20
    bottom_block_x = margin_left
    bottom_block_w = usable_w

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(bottom_block_x,
           bottom_block_y_top-bottom_block_h,
           bottom_block_w,
           bottom_block_h,
           stroke=1, fill=1)

    yb = bottom_block_y_top-14
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(bottom_block_x+8, yb, "Desempeño cognitivo global")
    yb -= 12
    yb = _draw_par(
        c,
        global_desc,
        bottom_block_x+8,
        yb,
        bottom_block_w-16,
        font="Helvetica",
        size=7,
        leading=10,
        color=colors.black,
        max_lines=4
    )

    yb -= 10
    c.setFont("Helvetica-Bold",8)
    c.drawString(bottom_block_x+8, yb, "Ajuste al cargo evaluado")
    yb -= 12
    yb = _draw_par(
        c,
        ajuste_text,
        bottom_block_x+8,
        yb,
        bottom_block_w-16,
        font="Helvetica",
        size=7,
        leading=10,
        color=colors.black,
        max_lines=4
    )

    yb -= 10
    c.setFont("Helvetica-Bold",8)
    c.drawString(bottom_block_x+8, yb, "Nota metodológica")
    yb -= 12
    _draw_par(
        c,
        nota_text,
        bottom_block_x+8,
        yb,
        bottom_block_w-16,
        font="Helvetica",
        size=6,
        leading=9,
        color=colors.grey,
        max_lines=10
    )

    # footer
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawRightString(W-margin_right, 30,
        "Uso interno RR.HH. · Evaluación Cognitiva Operativa · No clínico")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


# -------------------------------------------------
# ENVÍO CORREO
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
# GENERAR + ENVIAR INFORME
# -------------------------------------------------
def finalize_and_send():
    raw_scores = compute_scores(st.session_state.answers)

    # armar descripciones
    desc_by_dim = build_dim_descriptions(raw_scores)
    fortalezas, riesgos = build_strengths_and_risks(raw_scores)
    global_desc = build_global_desc(raw_scores)
    ajuste_text = cargo_fit_text(st.session_state.selected_job, raw_scores)

    nota_text = (
        "Este informe se basa en la auto-respuesta declarada por la persona evaluada "
        "en el test cognitivo adaptado para entornos operativos. Los resultados describen "
        "tendencias funcionales observadas al momento de la evaluación y no constituyen "
        "un diagnóstico clínico ni, por sí solos, una determinación absoluta de idoneidad. "
        "Se recomienda complementar esta información con entrevista estructurada, "
        "verificación de experiencia y evaluación técnica del cargo."
    )

    now_txt = datetime.now().strftime("%d/%m/%Y %H:%M")
    cargo_name = JOB_PROFILES[st.session_state.selected_job]["title"]

    pdf_bytes = generate_pdf_iq(
        candidate_name   = st.session_state.candidate_name,
        cargo_name       = cargo_name,
        fecha_eval       = now_txt,
        evaluator_email  = st.session_state.evaluator_email,
        raw_scores       = raw_scores,
        strengths_list   = fortalezas,
        monitor_list     = riesgos,
        desc_by_dim      = desc_by_dim,
        global_desc      = global_desc,
        ajuste_text      = ajuste_text,
        nota_text        = nota_text
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
            # en producción podrías registrar/loggear el error
            pass
        st.session_state.already_sent = True


# -------------------------------------------------
# CALLBACK RESPUESTA (maneja SÍ y NO sin doble click)
# -------------------------------------------------
def choose_answer(value_yes_or_no: int):
    q_idx = st.session_state.current_q
    st.session_state.answers[q_idx] = value_yes_or_no

    if q_idx < TOTAL_QUESTIONS - 1:
        st.session_state.current_q += 1
        st.session_state._need_rerun = True
    else:
        # terminó
        finalize_and_send()
        st.session_state.stage = "done"
        st.session_state._need_rerun = True


# -------------------------------------------------
# VISTAS UI STREAMLIT
# -------------------------------------------------
def view_select_job():
    st.markdown("### Evaluación Cognitiva Operativa (IQ Adaptado)")
    st.write("Seleccione el cargo a evaluar:")

    cols = st.columns(2)
    keys_list = list(JOB_PROFILES.keys())
    for i, job_key in enumerate(keys_list):
        with cols[i % 2]:
            if st.button(JOB_PROFILES[job_key]["title"],
                         key=f"job_{job_key}",
                         use_container_width=True):
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
    # aseguro que si recarga la vista done, el PDF ya fue enviado
    finalize_and_send()
    view_done()

# control de rerun suave
if st.session_state._need_rerun:
    st.session_state._need_rerun = False
    st.rerun()
