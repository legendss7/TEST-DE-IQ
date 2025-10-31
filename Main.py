# ============================================================
# Test Cognitivo Operativo (IQ Laboral Adaptado) · 70 ítems
# 5 dimensiones + índice global G
# Visual estilo EPQR (card blanca + barra progreso)
# Auto-avance (sin doble click)
# PDF ordenado (barras + tablas) + envío automático por correo
# Pantalla final sólo "Evaluación finalizada"
#
# Requisitos:
#   pip install streamlit reportlab
#
# NOTA:
# - Cambia FROM_ADDR y APP_PASS por credenciales válidas
#   antes de usar envío real.
# ============================================================

import streamlit as st
from datetime import datetime
from io import BytesIO
import smtplib
from email.message import EmailMessage

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# ---------- CONFIG STREAMLIT ----------
st.set_page_config(
    page_title="Test Cognitivo Operativo",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------- CREDENCIALES DE CORREO ----------
FROM_ADDR = "jo.tajtaj@gmail.com"
APP_PASS  = "nlkt kujl ebdg cyts"  # <-- cámbialo en uso real

# -------------------------------------------------
# DIMENSIONES:
# RL = Razonamiento Lógico / Secuencias
# AT = Atención al Detalle / Precisión
# VD = Velocidad de Decisión / Juicio rápido
# MT = Memoria de Trabajo / Retención inmediata
# CI = Comprensión de Instrucciones / Lectura Operativa
# G  = Índice Global Cognitivo (promedio normalizado)
# -------------------------------------------------

# Cada ítem:
#   text: la pregunta/afirmación
#   cat:  dimensión ("RL","AT","VD","MT","CI")
#   ans:  1 si la respuesta correcta es "Sí", 0 si la respuesta correcta es "No"
QUESTIONS = [
    # 14 ítems RL (Razonamiento Lógico / Secuencias)
    {"text": "En la secuencia 2, 4, 8, 16, 32, el siguiente número lógico sería 64. ¿Es correcto?", "cat": "RL", "ans": 1},
    {"text": "Si todos los turnos A empiezan a las 07:00 y hoy es turno A, entonces hoy NO empiezas a las 07:00. ¿Es correcto?", "cat": "RL", "ans": 0},
    {"text": "Si Pedro es más alto que Juan, y Juan es más alto que Luis, entonces Pedro es más alto que Luis. ¿Es correcto?", "cat": "RL", "ans": 1},
    {"text": "5 + 5 + 5 es igual a 20. ¿Es correcto?", "cat": "RL", "ans": 0},
    {"text": "Si una pieza pasa primera fase y luego segunda fase, entonces pasó control completo. ¿Es correcto asumirlo?", "cat": "RL", "ans": 1},
    {"text": "Si 'A implica B' y 'B implica C', entonces 'A implica C' es una conclusión válida. ¿Es correcto?", "cat": "RL", "ans": 1},
    {"text": "La mitad de 60 es 40. ¿Es correcto?", "cat": "RL", "ans": 0},
    {"text": "Si un lote falla control de calidad, ese lote debe detenerse. El lote 12 falló control. ¿Debe detenerse el lote 12? ¿Sí?", "cat": "RL", "ans": 1},
    {"text": "En la serie 10, 7, 4, 1, -2… el siguiente número debería ser -5. ¿Es correcto?", "cat": "RL", "ans": 1},
    {"text": "Si todos los operarios deben usar casco y Ana es operaria, entonces Ana debe usar casco. ¿Sí?", "cat": "RL", "ans": 1},
    {"text": "Si hoy es viernes y mañana es lunes, la afirmación es lógica. ¿Sí?", "cat": "RL", "ans": 0},
    {"text": "8 es el doble de 4. ¿Sí?", "cat": "RL", "ans": 1},
    {"text": "Si un producto sin sello puede salir igual al camión, ¿es correcto según el estándar normal de seguridad?", "cat": "RL", "ans": 0},
    {"text": "Si A>B y B=C entonces A=C. ¿Sí?", "cat": "RL", "ans": 1},

    # 14 ítems AT (Atención al Detalle / Precisión)
    {"text": "Si una etiqueta dice 'Lote 5B' y el pedido dice 'Lote 58', ¿son idénticos?", "cat": "AT", "ans": 0},
    {"text": "Detectar un dígito errado en el código de barras puede evitar enviar producto equivocado. ¿Sí?", "cat": "AT", "ans": 1},
    {"text": "Si el manual dice 'apretar a 12 Nm' y alguien aprieta a 21 Nm, ¿está correcto?", "cat": "AT", "ans": 0},
    {"text": "Leer dos veces las instrucciones reduce errores de armado. ¿Sí?", "cat": "AT", "ans": 1},
    {"text": "Si un pallet tiene 49 cajas y la guía dice 50, ¿eso debe reportarse antes de despacho?", "cat": "AT", "ans": 1},
    {"text": "Confundir 0.5 L con 5 L no genera impacto. ¿Sí?", "cat": "AT", "ans": 0},
    {"text": "Revisar números de serie es parte de control de calidad. ¿Sí?", "cat": "AT", "ans": 1},
    {"text": "Si el plano indica tornillo M8 pero se instala M6 igual está perfecto. ¿Sí?", "cat": "AT", "ans": 0},
    {"text": "Comparar la orden impresa con el producto final evita errores. ¿Sí?", "cat": "AT", "ans": 1},
    {"text": "Si faltan dos pernos de seguridad en un ensamblaje crítico, ¿eso es aceptable para despacho inmediato?", "cat": "AT", "ans": 0},
    {"text": "Marcar como 'revisado' sin revisar genera riesgo. ¿Sí?", "cat": "AT", "ans": 1},
    {"text": "Detectar diferencias pequeñas entre piezas puede prevenir fallas. ¿Sí?", "cat": "AT", "ans": 1},
    {"text": "Una etiqueta 'EXP 2026' es igual a 'EXP 2028'. ¿Sí?", "cat": "AT", "ans": 0},
    {"text": "Comprobar que el sello de seguridad esté cerrado es parte del rol operativo. ¿Sí?", "cat": "AT", "ans": 1},

    # 14 ítems VD (Velocidad de Decisión / Juicio rápido)
    {"text": "Ante una fuga pequeña de aceite en piso, ¿se debe alertar y señalizar de inmediato?", "cat": "VD", "ans": 1},
    {"text": "Si hay un cable pelado en zona húmeda, ¿lo dejo igual hasta el próximo turno sin avisar?", "cat": "VD", "ans": 0},
    {"text": "Si una alarma roja de máquina se enciende, ¿continuar operando normalmente es lo correcto?", "cat": "VD", "ans": 0},
    {"text": "Si veo una condición insegura, debo informar antes de seguir. ¿Sí?", "cat": "VD", "ans": 1},
    {"text": "En caso de confusión de instrucciones críticas, ¿preguntar rápido evita un error mayor?", "cat": "VD", "ans": 1},
    {"text": "Si escucho un ruido anormal fuerte y metálico en la máquina, ¿ignorar es aceptable?", "cat": "VD", "ans": 0},
    {"text": "Usar EPP (elementos de protección personal) inmediato frente a un riesgo químico leve es una buena decisión rápida. ¿Sí?", "cat": "VD", "ans": 1},
    {"text": "Ante un derrame en pasillo principal, ¿bloquear el paso temporalmente es razonable?", "cat": "VD", "ans": 1},
    {"text": "Si un compañero está operando sin guantes en zona cortante, ¿debo avisar o parar la tarea?", "cat": "VD", "ans": 1},
    {"text": "Ante un error grave en preparación de pedido urgente, ¿es mejor despachar igual sin decir nada?", "cat": "VD", "ans": 0},
    {"text": "Pedir aclaración rápida cuando hay instrucciones contradictorias es una buena práctica. ¿Sí?", "cat": "VD", "ans": 1},
    {"text": "Si veo chispas saliendo de un equipo eléctrico, ¿es correcto suponer que 'es normal' y seguir?", "cat": "VD", "ans": 0},
    {"text": "Cuando aparece una condición de riesgo, reaccionar en el momento puede prevenir accidentes. ¿Sí?", "cat": "VD", "ans": 1},
    {"text": "Si una carretilla vibra raro a alta velocidad, ¿puedo seguir igual porque estoy apurado?", "cat": "VD", "ans": 0},

    # 14 ítems MT (Memoria de Trabajo / Retención inmediata)
    {"text": "Si el supervisor da 3 pasos seguidos (cortar, etiquetar, sellar) ¿debo poder recordarlos al ejecutar?", "cat": "MT", "ans": 1},
    {"text": "Recordar medidas exactas (por ejemplo, 12 mm y no 10 mm) es parte del trabajo operativo. ¿Sí?", "cat": "MT", "ans": 1},
    {"text": "Si me dan una instrucción corta, la olvido al instante y eso no importa. ¿Sí?", "cat": "MT", "ans": 0},
    {"text": "Retener temporalmente códigos de ubicación en bodega ayuda a ubicar más rápido. ¿Sí?", "cat": "MT", "ans": 1},
    {"text": "Recordar qué producto va en qué pallet sin tener que mirar cada 10 segundos mejora el flujo. ¿Sí?", "cat": "MT", "ans": 1},
    {"text": "Si me dicen 'lleva caja A a área B y vuelve con caja C', ¿debo ser capaz de hacerlo sin olvidarlo de inmediato?", "cat": "MT", "ans": 1},
    {"text": "Confundir siempre izquierda/derecha inmediata no afecta el proceso logístico. ¿Sí?", "cat": "MT", "ans": 0},
    {"text": "Puedo mantener en mente pequeñas listas de 2-3 pasos mientras las ejecuto. ¿Sí?", "cat": "MT", "ans": 1},
    {"text": "Recordar qué pieza ajusté y cuál falta reduce errores de montaje. ¿Sí?", "cat": "MT", "ans": 1},
    {"text": "Me pierdo con instrucciones simples de dos pasos y eso es normal e indiferente en producción. ¿Sí?", "cat": "MT", "ans": 0},
    {"text": "Puedo seguir una indicación verbal corta sin que me la repitan 4 veces. ¿Sí?", "cat": "MT", "ans": 1},
    {"text": "Saber qué herramienta acabo de usar ayuda a no repetir tareas. ¿Sí?", "cat": "MT", "ans": 1},
    {"text": "Mantener la secuencia exacta de armado evita tener que desarmar luego. ¿Sí?", "cat": "MT", "ans": 1},
    {"text": "Si olvido el paso 2 de 3, no hay riesgo en el resultado final. ¿Sí?", "cat": "MT", "ans": 0},

    # 14 ítems CI (Comprensión de Instrucciones / Lectura Operativa)
    {"text": "Si el procedimiento escrito dice 'Apagar ANTES de limpiar', eso significa limpiar con la máquina apagada. ¿Sí?", "cat": "CI", "ans": 1},
    {"text": "Si una guía indica 'solo personal autorizado', cualquiera del turno puede entrar igual. ¿Sí?", "cat": "CI", "ans": 0},
    {"text": "Entender un aviso de seguridad evita accidentes. ¿Sí?", "cat": "CI", "ans": 1},
    {"text": "Si el rótulo dice 'inflamable', eso significa 'no hay riesgo de fuego'. ¿Sí?", "cat": "CI", "ans": 0},
    {"text": "Seguir instrucciones paso a paso escritas ayuda a mantener estándar constante. ¿Sí?", "cat": "CI", "ans": 1},
    {"text": "Si un instructivo dice 'NO levantar sin faja lumbar', entonces se debe usar faja para levantar. ¿Sí?", "cat": "CI", "ans": 1},
    {"text": "Ignorar advertencias técnicas porque 'parecen exageradas' es correcto. ¿Sí?", "cat": "CI", "ans": 0},
    {"text": "Comprender etiquetas de riesgo químico es parte del trabajo seguro. ¿Sí?", "cat": "CI", "ans": 1},
    {"text": "Si una alarma indica 'cortar energía', debo mantener la energía encendida. ¿Sí?", "cat": "CI", "ans": 0},
    {"text": "Leer una orden de trabajo correctamente evita producir el modelo equivocado. ¿Sí?", "cat": "CI", "ans": 1},
    {"text": "El símbolo de guantes obligatorios significa que puedo trabajar con las manos desnudas. ¿Sí?", "cat": "CI", "ans": 0},
    {"text": "Comprender señales visuales / pictogramas acelera la coordinación en planta. ¿Sí?", "cat": "CI", "ans": 1},
    {"text": "Si el aviso dice 'Peligro: Alta tensión', significa que es totalmente seguro tocar. ¿Sí?", "cat": "CI", "ans": 0},
    {"text": "Seguir instrucciones impresas exactamente igual en cada turno mejora la estandarización. ¿Sí?", "cat": "CI", "ans": 1},
]

TOTAL_QUESTIONS = len(QUESTIONS)  # 70

# ---------- PERFILES DE CARGO (rangos esperados en escala 0–10 normalizada) ----------
# Para cada cargo definimos los rangos aceptables por dimensión + G.
# G = promedio de (RL,AT,VD,MT,CI) normalizados
JOB_PROFILES = {
    "operario": {
        "title": "Operario de Producción",
        "req": {
            "RL": (4.0, 10.0),
            "AT": (5.0, 10.0),
            "VD": (5.0, 10.0),
            "MT": (4.0, 10.0),
            "CI": (4.5,10.0),
            "G":  (5.0, 10.0),
        },
    },
    "supervisor": {
        "title": "Supervisor Operativo",
        "req": {
            "RL": (5.0, 10.0),
            "AT": (5.0, 10.0),
            "VD": (6.0, 10.0),
            "MT": (5.0, 10.0),
            "CI": (5.0,10.0),
            "G":  (6.0, 10.0),
        },
    },
    "tecnico": {
        "title": "Técnico de Mantenimiento",
        "req": {
            "RL": (5.5, 10.0),
            "AT": (6.0, 10.0),
            "VD": (5.0, 10.0),
            "MT": (5.5, 10.0),
            "CI": (5.5,10.0),
            "G":  (6.0, 10.0),
        },
    },
    "logistica": {
        "title": "Personal de Logística",
        "req": {
            "RL": (4.0, 10.0),
            "AT": (5.5, 10.0),
            "VD": (5.0, 10.0),
            "MT": (4.5, 10.0),
            "CI": (4.5,10.0),
            "G":  (5.0, 10.0),
        },
    },
}

# ---------- ESTADO GLOBAL STREAMLIT ----------
if "stage" not in st.session_state:
    st.session_state.stage = "select_job"  # select_job → info → test → done

if "selected_job" not in st.session_state:
    st.session_state.selected_job = None

if "candidate_name" not in st.session_state:
    st.session_state.candidate_name = ""

if "evaluator_email" not in st.session_state:
    st.session_state.evaluator_email = ""

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "answers" not in st.session_state:
    # answers[i] = 1 (Sí) o 0 (No)
    st.session_state.answers = {i: None for i in range(TOTAL_QUESTIONS)}

if "_need_rerun" not in st.session_state:
    st.session_state._need_rerun = False

if "already_sent" not in st.session_state:
    st.session_state.already_sent = False

# ============================================================
# UTILIDADES DE CÁLCULO / INFORME
# ============================================================

def _norm_to_ten(raw_value, max_items=14):
    # normaliza puntaje correcto 0..14 a escala 0..10
    return (raw_value / max_items) * 10.0

def compute_scores(ans_dict):
    # contamos aciertos por dimensión
    raw_dim = {"RL":0, "AT":0, "VD":0, "MT":0, "CI":0}
    total_dim = {"RL":0, "AT":0, "VD":0, "MT":0, "CI":0}

    for idx, q in enumerate(QUESTIONS):
        given = ans_dict.get(idx)
        if given is None:
            continue
        cat = q["cat"]
        correct = q["ans"]
        total_dim[cat] += 1
        if given == correct:
            raw_dim[cat] += 1

    # normalizamos 0..10
    norm_dim = {}
    for d in raw_dim:
        norm_dim[d] = _norm_to_ten(raw_dim[d], max_items=14)

    # índice global G es el promedio de las 5 escalas norm_dim
    G_val = sum(norm_dim[d] for d in ["RL","AT","VD","MT","CI"]) / 5.0

    raw_dim["G"]  = None  # G no tiene bruto directo
    norm_dim["G"] = G_val

    return {"raw": raw_dim, "norm": norm_dim}

def qualitative_level(score10):
    # score10 está en escala 0..10
    if score10 >= 7.5:
        return "Alto"
    elif score10 >= 5.0:
        return "Medio"
    else:
        return "Bajo"

def build_short_desc(norm_scores):
    # Mensaje breve por dimensión
    desc = {}
    RL = norm_scores["RL"]
    AT = norm_scores["AT"]
    VD = norm_scores["VD"]
    MT = norm_scores["MT"]
    CI = norm_scores["CI"]
    G  = norm_scores["G"]

    desc["RL"] = "Capacidad de razonar relaciones lógicas y secuencias de forma correcta."
    desc["AT"] = "Nivel de precisión y cuidado en la comparación de datos y detalles técnicos."
    desc["VD"] = "Habilidad para tomar decisiones rápidas en condiciones de operación y seguridad."
    desc["MT"] = "Memoria inmediata para seguir pasos en el orden indicado sin perder información clave."
    desc["CI"] = "Comprensión de instrucciones y avisos escritos / simbólicos aplicados al trabajo."
    desc["G"]  = "Índice cognitivo global estimado a partir de las cinco áreas anteriores."

    # Podemos modular levemente partes según nivel, si quieres:
    # (opcional, mantengo descripciones estables para que quepa en PDF)
    return desc

def build_strengths_risks(norm_scores):
    fortalezas = []
    monitoreo  = []

    if norm_scores["AT"] >= 7.5:
        fortalezas.append("Alto foco en precisión y control de detalles críticos de calidad.")
    elif norm_scores["AT"] < 5.0:
        monitoreo.append("Requiere refuerzo en control de detalles finos antes de liberar producto.")

    if norm_scores["VD"] >= 7.5:
        fortalezas.append("Buena respuesta rápida frente a riesgos operativos y decisiones de seguridad.")
    elif norm_scores["VD"] < 5.0:
        monitoreo.append("Podría requerir apoyo adicional cuando hay que reaccionar con rapidez ante fallas.")

    if norm_scores["MT"] >= 7.5:
        fortalezas.append("Buena retención de instrucciones cortas y orden de pasos.")
    elif norm_scores["MT"] < 5.0:
        monitoreo.append("Puede beneficiarse de instrucciones más estructuradas o apoyo visual paso a paso.")

    if norm_scores["CI"] >= 7.5:
        fortalezas.append("Comprende instrucciones escritas/señaléticas y las aplica correctamente.")
    elif norm_scores["CI"] < 5.0:
        monitoreo.append("Podría necesitar acompañamiento adicional al inicio para la interpretación de pautas técnicas y seguridad.")

    if norm_scores["RL"] >= 7.5:
        fortalezas.append("Capacidad lógica para entender reglas, secuencias y consecuencias operativas.")

    if norm_scores["G"] >= 7.5:
        fortalezas.append("Perfil cognitivo global alto para entornos de exigencia técnica y cambio rápido.")
    elif norm_scores["G"] < 5.0:
        monitoreo.append("Se sugiere inducción guiada y verificación temprana de comprensión en tareas críticas.")

    # Limitar a máx 4 ítems cada bloque
    return fortalezas[:4], monitoreo[:4]

def cargo_fit_text(job_key, norm_scores):
    req = JOB_PROFILES[job_key]["req"]
    cargo_name = JOB_PROFILES[job_key]["title"]

    ok_all = True
    for dim, (mn, mx) in req.items():
        val = norm_scores[dim]
        if not (val >= mn and val <= mx):
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
            f"Ajuste al cargo: El perfil evaluado NO SE CONSIDERA "
            f"CONSISTENTE con las exigencias habituales del cargo {cargo_name}."
        )

def build_commitment_line(norm_scores):
    # Para IQ no evaluamos compromiso explícito -> lo adaptamos a desempeño cognitivo esperado:
    if norm_scores["G"] >= 7.5:
        return "Desempeño cognitivo estimado: nivel alto para entornos con alta precisión, coordinación y cambio operativo."
    elif norm_scores["G"] >= 5.0:
        return "Desempeño cognitivo estimado: nivel funcional esperado para tareas operativas estándar con supervisión inicial normal."
    else:
        return "Desempeño cognitivo estimado: podría requerir acompañamiento adicional inicial en tareas de mayor complejidad técnica."

# ============================================================
# UTILIDADES PDF
# ============================================================

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

def _draw_par(c, text, x, y, width,
              font="Helvetica", size=8, leading=11,
              color=colors.black, max_lines=None):
    c.setFont(font, size)
    c.setFillColor(color)
    lines = _wrap(c, text, width, font, size)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        c.drawString(x, y, ln)
        y -= leading
    return y

def generate_pdf(candidate_name,
                 cargo_name,
                 fecha_eval,
                 evaluator_email,
                 norm_scores,
                 raw_scores,
                 fortalezas,
                 monitoreo,
                 desc_dim,
                 compromiso_text,
                 ajuste_text,
                 nota_text):

    buf = BytesIO()
    W, H = A4
    c = canvas.Canvas(buf, pagesize=A4)

    margin_left  = 36
    margin_right = 36

    # Encabezado
    c.setFont("Helvetica-Bold",10)
    c.drawString(margin_left, H-40, "EMPRESA / LOGO")
    c.setFont("Helvetica",7)
    c.drawString(margin_left, H-55, "Evaluación de capacidad cognitiva aplicada al rol")

    c.setFont("Helvetica-Bold",11)
    c.drawRightString(W-margin_right, H-40, "Perfil Cognitivo Operativo (IQ Adaptado)")
    c.setFont("Helvetica",7)
    c.drawRightString(W-margin_right, H-55, "Uso interno RR.HH. / Procesos productivos · No clínico")

    # --- Gráfico barras (RL,AT,VD,MT,CI,G) escala 0..10 normalizada ---
    chart_x = margin_left
    chart_y_bottom = H-270
    chart_w = 250
    chart_h = 120

    dims_order = [("RL","RL"),("AT","AT"),("VD","VD"),
                  ("MT","MT"),("CI","CI"),("G","G")]

    bar_colors = [
        colors.HexColor("#1d4ed8"),  # azul intenso
        colors.HexColor("#10b981"),  # verde
        colors.HexColor("#f97316"),  # naranjo
        colors.HexColor("#6366f1"),  # violeta
        colors.HexColor("#6b7280"),  # gris
        colors.HexColor("#0ea5b7"),  # teal
    ]

    # eje y y grilla
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(chart_x, chart_y_bottom, chart_x, chart_y_bottom+chart_h)

    for lvl in range(0,11):  # 0..10
        yv = chart_y_bottom + (lvl/10.0)*chart_h
        c.setFont("Helvetica",6)
        c.setFillColor(colors.black)
        c.drawString(chart_x-15, yv-2, str(lvl))
        c.setStrokeColor(colors.lightgrey)
        c.line(chart_x, yv, chart_x+chart_w, yv)

    gap = 10
    bar_w = (chart_w - gap*(len(dims_order)+1)) / len(dims_order)
    tops = []

    for i,(key,label) in enumerate(dims_order):
        val_norm = norm_scores[key]  # 0..10
        bx = chart_x + gap + i*(bar_w+gap)
        bh = (val_norm/10.0)*chart_h
        by = chart_y_bottom

        c.setStrokeColor(colors.black)
        c.setFillColor(bar_colors[i])
        c.rect(bx, by, bar_w, bh, stroke=1, fill=1)

        tops.append((bx+bar_w/2.0, by+bh))

        lvl_txt = qualitative_level(val_norm)
        c.setFont("Helvetica-Bold",7)
        c.setFillColor(colors.black)
        c.drawCentredString(bx+bar_w/2.0, chart_y_bottom-14, label)

        # Puntaje bruto sólo aplica a dimensiones base (no G)
        if key != "G":
            raw_v = raw_scores[key]
            c.setFont("Helvetica",6)
            c.drawCentredString(
                bx+bar_w/2.0,
                chart_y_bottom-26,
                f"{raw_v}/14  {val_norm:.1f}/10  {lvl_txt}"
            )
        else:
            c.setFont("Helvetica",6)
            c.drawCentredString(
                bx+bar_w/2.0,
                chart_y_bottom-26,
                f"{val_norm:.1f}/10  {lvl_txt}"
            )

    # línea que une los top points
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
    c.drawString(chart_x, chart_y_bottom+chart_h+12, "Perfil cognitivo normalizado (0–10)")

    # --- Cuadro Datos candidato (derecha arriba) ---
    box_x = margin_left + chart_w + 30
    box_y_top = H-140
    box_w = W - margin_right - box_x
    box_h = 70
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(box_x, box_y_top-box_h, box_w, box_h, stroke=1, fill=1)

    yy = box_y_top-12
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(box_x+8, yy, f"Nombre: {candidate_name}")
    yy -= 12
    c.setFont("Helvetica",8)
    c.drawString(box_x+8, yy, f"Cargo evaluado: {cargo_name}")
    yy -= 12
    c.drawString(box_x+8, yy, f"Fecha evaluación: {fecha_eval}")
    yy -= 12
    c.drawString(box_x+8, yy, f"Evaluador: {evaluator_email.upper()}")
    yy -= 12
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawString(box_x+8, yy, "Documento interno. No clínico.")

    # --- Guía dimensiones (derecha media) ---
    guide_y_top = H-230
    guide_h = 75
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(box_x, guide_y_top-guide_h, box_w, guide_h, stroke=1, fill=1)

    gy = guide_y_top-14
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(box_x+8, gy, "Guía de lectura de dimensiones")
    gy -= 12
    c.setFont("Helvetica",7)
    lines_dim = [
        "RL = Razonamiento Lógico / Secuencias",
        "AT = Atención al Detalle / Precisión",
        "VD = Velocidad de Decisión / Juicio rápido",
        "MT = Memoria de Trabajo / Retención inmediata",
        "CI = Comprensión de Instrucciones / Lectura Operativa",
        "G  = Índice Cognitivo Global (promedio)",
    ]
    for gl in lines_dim:
        c.drawString(box_x+8, gy, gl)
        gy -= 10

    # --- Resumen conductual observado (derecha abajo) ---
    sum_y_top = H-330
    sum_h = 110
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(box_x, sum_y_top-sum_h, box_w, sum_h, stroke=1, fill=1)

    sy = sum_y_top-14
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(box_x+8, sy, "Resumen cognitivo observado")
    sy -= 14

    c.setFont("Helvetica-Bold",7)
    c.drawString(box_x+8, sy, "Fortalezas potenciales:")
    sy -= 12
    c.setFont("Helvetica",7)
    for f in fortalezas:
        wrapped = _wrap(c, "• " + f, box_w-16, "Helvetica",7)
        for line in wrapped:
            c.drawString(box_x+12, sy, line)
            sy -= 10
            if sy < sum_y_top - sum_h + 28:
                break
        if sy < sum_y_top - sum_h + 28:
            break

    sy -= 6
    c.setFont("Helvetica-Bold",7)
    c.drawString(box_x+8, sy, "Aspectos a monitorear / apoyo sugerido:")
    sy -= 12
    c.setFont("Helvetica",7)
    for m in monitoreo:
        wrapped = _wrap(c, "• " + m, box_w-16, "Helvetica",7)
        for line in wrapped:
            c.drawString(box_x+12, sy, line)
            sy -= 10
            if sy < sum_y_top - sum_h + 8:
                break
        if sy < sum_y_top - sum_h + 8:
            break

    # --- Tabla Detalle por dimensión (toda la fila bajo el gráfico) ---
    table_x = margin_left
    table_y_top = H-360
    # ancho hasta casi margen derecho
    table_w = W - margin_right - table_x
    table_h = 180

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(table_x, table_y_top-table_h, table_w, table_h, stroke=1, fill=1)

    # Título
    title_y = table_y_top-14
    c.setFont("Helvetica-Bold",9)
    c.setFillColor(colors.black)
    c.drawString(table_x+8, title_y, "Detalle por dimensión")

    # Línea separadora
    c.setStrokeColor(colors.lightgrey)
    c.setLineWidth(0.5)
    c.line(table_x, title_y-6, table_x+table_w, title_y-6)

    # Encabezados columnas
    header_y = title_y - 20
    c.setFont("Helvetica-Bold",7)
    c.setFillColor(colors.black)
    # Nota: no dibujamos texto 'Dimensión' encima nuevamente
    # Lo dejamos implícito en cada fila
    c.drawString(table_x + 200, header_y, "Puntaje")
    c.drawString(table_x + 260, header_y, "Nivel")
    c.drawString(table_x + 300, header_y, "Descripción breve")

    # Línea separadora
    c.setStrokeColor(colors.lightgrey)
    c.setLineWidth(0.5)
    c.line(table_x, header_y-4, table_x+table_w, header_y-4)

    row_y = header_y - 16
    row_gap = 32

    dims_display = [
        ("RL","Razonamiento Lógico / Secuencias"),
        ("AT","Atención al Detalle / Precisión"),
        ("VD","Velocidad de Decisión / Juicio rápido"),
        ("MT","Memoria de Trabajo / Retención inmediata"),
        ("CI","Comprensión de Instrucciones / Lectura Operativa"),
        ("G","Índice Cognitivo Global (G)"),
    ]

    for key,label in dims_display:
        c.setFont("Helvetica-Bold",7)
        c.setFillColor(colors.black)
        c.drawString(table_x + 8, row_y, label)

        val_norm = norm_scores[key]
        lvl_v    = qualitative_level(val_norm)

        if key != "G":
            raw_v = raw_scores[key]
            puntaje_txt = f"{raw_v}/14  {val_norm:.1f}/10"
        else:
            puntaje_txt = f"{val_norm:.1f}/10"

        c.setFont("Helvetica",7)
        c.drawString(table_x + 200, row_y, puntaje_txt)
        c.drawString(table_x + 260, row_y, lvl_v)

        # descripción envuelta
        desc_text = desc_dim[key]
        row_y_after = _draw_par(
            c,
            desc_text,
            x=table_x + 300,
            y=row_y,
            width=table_w - 320,
            font="Helvetica",
            size=7,
            leading=9,
            color=colors.black,
            max_lines=3
        )

        used_block_h = row_y - row_y_after
        if used_block_h < row_gap:
            row_y = row_y - row_gap
        else:
            row_y = row_y_after - 10

        # línea entre filas
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.4)
        c.line(table_x, row_y + 4, table_x + table_w, row_y + 4)

    # --- Bloque final (Conclusión / Nota metodológica)
    concl_x = margin_left
    concl_y_top = 180
    concl_w = W - margin_right - margin_left
    concl_h = 180
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(concl_x, concl_y_top-concl_h, concl_w, concl_h, stroke=1, fill=1)

    sub_x = concl_x+8
    sub_w = concl_w-16

    # Subbloque 1: Desempeño cognitivo estimado
    y1 = concl_y_top-14
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(sub_x, y1, "Desempeño / Nivel Cognitivo Global")
    y1_after = _draw_par(
        c,
        compromiso_text,
        x=sub_x,
        y=y1-14,
        width=sub_w,
        font="Helvetica",
        size=7,
        leading=10,
        color=colors.black,
        max_lines=4
    )

    # Subbloque 2: Ajuste al cargo
    y2 = y1_after-8
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(sub_x, y2, "Ajuste al cargo evaluado")
    y2_after = _draw_par(
        c,
        ajuste_text,
        x=sub_x,
        y=y2-14,
        width=sub_w,
        font="Helvetica",
        size=7,
        leading=10,
        color=colors.black,
        max_lines=4
    )

    # Nota metodológica
    nota_y = y2_after-8
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(sub_x, nota_y, "Nota metodológica")
    _draw_par(
        c,
        nota_text,
        x=sub_x,
        y=nota_y-14,
        width=sub_w,
        font="Helvetica",
        size=6,
        leading=9,
        color=colors.grey,
        max_lines=8
    )

    # footer
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawRightString(W-margin_right, 40,
                      "Uso interno RR.HH. · Evaluación Cognitiva Operativa · No clínico")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()

# ============================================================
# ENVÍO EMAIL
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
# FINALIZAR TEST → CALCULAR, GENERAR PDF, ENVIAR
# ============================================================

def finalize_and_send():
    scores = compute_scores(st.session_state.answers)
    raw_scores  = scores["raw"]   # bruto por dim (0..14) excepto G=None
    norm_scores = scores["norm"]  # normalizado 0..10 + G

    desc_dim    = build_short_desc(norm_scores)
    fortalezas, monitoreo = build_strengths_risks(norm_scores)

    compromiso_text = build_commitment_line(norm_scores)
    ajuste_text     = cargo_fit_text(
        st.session_state.selected_job,
        norm_scores
    )

    nota_text = (
        "Este informe se basa en el desempeño del evaluado en una batería de "
        "70 ítems de razonamiento lógico aplicado al trabajo, atención al detalle, "
        "velocidad de decisión ante riesgo, memoria de trabajo y comprensión de "
        "instrucciones operativas. No constituye diagnóstico clínico ni, por sí solo, "
        "una determinación absoluta de idoneidad laboral. Debe complementarse con "
        "entrevista estructurada, verificación de experiencia y evaluación técnica del cargo."
    )

    now_txt = datetime.now().strftime("%d/%m/%Y %H:%M")
    cargo_name = JOB_PROFILES[st.session_state.selected_job]["title"]

    pdf_bytes = generate_pdf(
        candidate_name   = st.session_state.candidate_name,
        cargo_name       = cargo_name,
        fecha_eval       = now_txt,
        evaluator_email  = st.session_state.evaluator_email,
        norm_scores      = norm_scores,
        raw_scores       = raw_scores,
        fortalezas       = fortalezas,
        monitoreo        = monitoreo,
        desc_dim         = desc_dim,
        compromiso_text  = compromiso_text,
        ajuste_text      = ajuste_text,
        nota_text        = nota_text
    )

    if not st.session_state.already_sent:
        try:
            send_email_with_pdf(
                to_email   = st.session_state.evaluator_email,
                pdf_bytes  = pdf_bytes,
                filename   = "Informe_Cognitivo_Operativo.pdf",
                subject    = "Informe Cognitivo Operativo (IQ Adaptado)",
                body_text  = (
                    "Adjunto informe interno de desempeño cognitivo operativo "
                    f"({st.session_state.candidate_name} / {cargo_name}). "
                    "Uso RR.HH. interno."
                ),
            )
        except Exception:
            pass
        st.session_state.already_sent = True

# ============================================================
# CALLBACK RESPUESTA (auto avance sin doble click)
# ============================================================

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

# ============================================================
# VISTAS
# ============================================================

def view_select_job():
    st.markdown("### Evaluación Cognitiva Operativa (IQ Adaptado)")
    st.write("Seleccione el cargo / perfil objetivo:")

    cols = st.columns(2)
    keys = list(JOB_PROFILES.keys())
    for i, job_key in enumerate(keys):
        col = cols[i % 2]
        if col.button(JOB_PROFILES[job_key]["title"], key=f"job_{job_key}", use_container_width=True):
            st.session_state.selected_job = job_key
            st.session_state.stage = "info"
            st.session_state._need_rerun = True

def view_info_form():
    cargo_titulo = JOB_PROFILES[st.session_state.selected_job]["title"]
    st.markdown(f"#### Datos del candidato\n**Cargo evaluado:** {cargo_titulo}")
    st.info("Estos datos se usarán en el informe PDF interno y se enviarán automáticamente a RR.HH.")

    st.session_state.candidate_name = st.text_input(
        "Nombre del candidato",
        value=st.session_state.candidate_name,
        placeholder="Nombre completo"
    )
    st.session_state.evaluator_email = st.text_input(
        "Correo del evaluador (RR.HH. / Supervisor)",
        value=st.session_state.evaluator_email or FROM_ADDR,
        placeholder="nombre@empresa.com"
    )

    ok = (
        len(st.session_state.candidate_name.strip()) > 0 and
        len(st.session_state.evaluator_email.strip()) > 0
    )

    if st.button("Comenzar test cognitivo (70 ítems)", type="primary", disabled=not ok, use_container_width=True):
        st.session_state.current_q = 0
        st.session_state.answers = {i: None for i in range(TOTAL_QUESTIONS)}
        st.session_state.already_sent = False
        st.session_state.stage = "test"
        st.session_state._need_rerun = True

def view_test():
    q_idx = st.session_state.current_q
    q = QUESTIONS[q_idx]
    progreso = (q_idx+1)/TOTAL_QUESTIONS

    # Header estilo tarjeta gradiente
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
                Test Cognitivo Operativo · IQ Adaptado
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
            <p style="font-size:.8rem;color:#64748b;margin-top:12px;">
                Responda considerando una situación de trabajo real.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_yes, col_no = st.columns(2)
    with col_yes:
        st.button(
            "Sí / Correcto",
            key=f"yes_{q_idx}",
            type="primary",
            use_container_width=True,
            on_click=choose_answer,
            args=(1,)
        )
    with col_no:
        st.button(
            "No / Incorrecto",
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

# ============================================================
# FLUJO PRINCIPAL
# ============================================================

if st.session_state.stage == "select_job":
    view_select_job()

elif st.session_state.stage == "info":
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

# Rerun controlado para el avance automático
if st.session_state._need_rerun:
    st.session_state._need_rerun = False
    st.rerun()
