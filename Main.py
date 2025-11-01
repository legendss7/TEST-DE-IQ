# ============================================================
# TEST COGNITIVO GENERAL (IQ operativo) · Sin imágenes
# - 50 preguntas de dificultad creciente tipo 1er año U
# - Dominios: RL (lógica), CN (numérico), VB (verbal),
#             MA (memoria de trabajo / actualización),
#             PL (planificación / priorización)
# - Temporizador global de 20 minutos (1200 seg)
#   · Se muestra GRANDE arriba a la derecha
#   · Cuando llega a 0: se cierra el test, respuestas no marcadas = incorrectas
# - Pantalla final: sólo mensaje "Evaluación finalizada"
# - PDF de 1 página, estilo ficha comparativa, sin solapamiento de texto
#   · Incluye: datos candidato, perfil global, tabla por dimensión
#   · Todo con espaciado suficiente y sin texto encima
# - Envío automático del PDF al correo del evaluador
#
# Requisitos:
#   pip install streamlit reportlab
#
# IMPORTANTE:
#   - Ajusta FROM_ADDR y APP_PASS a credenciales válidas
#   - Esta app NO usa cargos específicos, es apta para cualquier candidato
# ============================================================

import streamlit as st
from datetime import datetime, timedelta
from io import BytesIO
import smtplib
from email.message import EmailMessage

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# ========== CONFIG STREAMLIT ==========
st.set_page_config(
    page_title="Evaluación Cognitiva",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ========== CREDENCIALES CORREO (ajusta a las tuyas) ==========
FROM_ADDR = "jo.tajtaj@gmail.com"
APP_PASS  = "nlkt kujl ebdg cyts"

# ============================================================
# BANCO DE PREGUNTAS
#
# Formato:
#   "text"           -> enunciado
#   "options"        -> alternativas
#   "correct_index"  -> índice (0..n-1) de la alternativa correcta
#   "domain"         -> RL / CN / VB / MA / PL
#
# Dificultad va subiendo por bloques (C1...C10).
# Sin imágenes, sin mostrar la respuesta en el enunciado.
# ============================================================

QUESTIONS = [
    # ---------- C1 (básico) ----------
    {"text": "Si todo triángulo tiene tres lados, ¿qué se puede afirmar sobre cualquier figura que sea triángulo?",
     "options": ["Tiene tres lados.", "Tiene cuatro lados.", "No tiene lados.", "Cambia de forma."],
     "correct_index": 0, "domain": "RL"},
    {"text": "Un valor aumenta de 10 a 15. ¿Cuál es el aumento absoluto?",
     "options": ["2", "4", "5", "50"],
     "correct_index": 2, "domain": "CN"},
    {"text": "¿Qué palabra es más cercana a 'preciso' en el sentido de 'exacto'?",
     "options": ["difuso", "correcto", "tardío", "emotivo"],
     "correct_index": 1, "domain": "VB"},
    {"text": "Memoriza mentalmente esta secuencia corta: 4 – 9 – 4 – 2. ¿Cuál fue el tercer número?",
     "options": ["2", "4", "9", "6"],
     "correct_index": 1, "domain": "MA"},
    {"text": "Tienes que hacer Paso 1 y luego Paso 2. ¿Cuál paso va primero?",
     "options": ["Paso 1", "Paso 2", "Ninguno", "Depende del humor"],
     "correct_index": 0, "domain": "PL"},

    # ---------- C2 ----------
    {"text": "Si A siempre es mayor que B, y B siempre es mayor que C, ¿cuál afirmación es cierta?",
     "options": ["A > C", "C > A", "B > A", "C = A"],
     "correct_index": 0, "domain": "RL"},
    {"text": "Tienes 24 unidades repartidas en 3 cajas iguales. ¿Cuántas por caja?",
     "options": ["6", "8", "12", "18"],
     "correct_index": 1, "domain": "CN"},
    {"text": "Selecciona el antónimo más cercano de 'riguroso':",
     "options": ["cuidadoso", "relajado", "minucioso", "estricto"],
     "correct_index": 1, "domain": "VB"},
    {"text": "Piensa en la secuencia: L, M, M, T. ¿Qué letra se repitió?",
     "options": ["L", "M", "T", "Ninguna"],
     "correct_index": 1, "domain": "MA"},
    {"text": "Tienes dos tareas: una urgente y una que puede esperar. ¿Cuál haces primero si buscas minimizar riesgo?",
     "options": ["La que puede esperar", "La urgente", "Ninguna", "Ambas a medias"],
     "correct_index": 1, "domain": "PL"},

    # ---------- C3 ----------
    {"text": "Si 'ningún informe sin firma es válido' y 'este informe es válido', ¿qué es correcto?",
     "options": ["Tiene firma.", "No tiene firma.", "Fue destruido.", "No existe."],
     "correct_index": 0, "domain": "RL"},
    {"text": "Si duplicar un número significa multiplicarlo por 2, ¿cuál es el doble de 36?",
     "options": ["18", "36", "54", "72"],
     "correct_index": 3, "domain": "CN"},
    {"text": "Completa la relación: 'Rápido' es a 'veloz' como 'lento' es a:",
     "options": ["pausado", "urgente", "temprano", "crítico"],
     "correct_index": 0, "domain": "VB"},
    {"text": "Recuerda la regla mental: 'A va antes que B, B va antes que C'. ¿Cuál va al medio?",
     "options": ["A", "B", "C", "No se puede saber"],
     "correct_index": 1, "domain": "MA"},
    {"text": "Tienes recursos limitados y dos problemas; uno afecta seguridad inmediata. ¿Qué priorizas?",
     "options": ["Seguridad inmediata", "El más largo", "El más cómodo", "Ninguno"],
     "correct_index": 0, "domain": "PL"},

    # ---------- C4 ----------
    {"text": "Si todos los X son Y, y este objeto es X, ¿qué conclusión es válida?",
     "options": ["El objeto es Y.", "El objeto no es Y.", "El objeto es Z.", "Nada se puede saber."],
     "correct_index": 0, "domain": "RL"},
    {"text": "Un valor baja de 120 a 90. ¿Cuál fue la disminución absoluta?",
     "options": ["10", "20", "30", "40"],
     "correct_index": 2, "domain": "CN"},
    {"text": "Elige la palabra más cercana a 'coherente':",
     "options": ["contradictorio", "alineado", "aleatorio", "temporal"],
     "correct_index": 1, "domain": "VB"},
    {"text": "Memoriza mentalmente: 7 – 2 – 5 – 9 – 2. ¿Cuál fue el segundo número?",
     "options": ["7", "2", "5", "9"],
     "correct_index": 1, "domain": "MA"},
    {"text": "Debes decidir sin toda la información, y el costo de equivocarte es alto. ¿Qué haces primero?",
     "options": ["Ignorar riesgos", "Pedir aclaración rápida clave", "Elegir al azar", "Postergar infinito"],
     "correct_index": 1, "domain": "PL"},

    # ---------- C5 ----------
    {"text": "Si 'A implica B' y 'B implica C', decir 'A implica C' es un ejemplo de:",
     "options": ["asociación emocional", "cadena lógica transitiva", "azar", "memoria sensorial"],
     "correct_index": 1, "domain": "RL"},
    {"text": "Tienes una razón 3:4. ¿Cuál afirmación es más correcta?",
     "options": ["Por cada 3 del primer tipo hay 4 del segundo.",
                 "Siempre hay 7 del primer tipo.",
                 "Nunca cambian las proporciones.",
                 "Significa que 4<3."],
     "correct_index": 0, "domain": "CN"},
    {"text": "¿Cuál opción define mejor 'discrepancia'?",
     "options": ["acuerdo total", "diferencia detectada", "decoración", "rapidez"],
     "correct_index": 1, "domain": "VB"},
    {"text": "Memoriza internamente tres pasos: Revisar → Ajustar → Confirmar. ¿Cuál es el tercer paso?",
     "options": ["Revisar", "Ajustar", "Confirmar", "Ninguno"],
     "correct_index": 2, "domain": "MA"},
    {"text": "Debes repartir un único recurso crítico entre 3 personas. ¿Qué es clave?",
     "options": ["Orden de turnos claro", "Que trabajen todos a la vez", "Que nadie haga pausas", "Elegir por simpatía"],
     "correct_index": 0, "domain": "PL"},

    # ---------- C6 ----------
    {"text": "Una regla dice: 'Si el sistema marca error crítico, detener proceso'. El proceso NO se detuvo. ¿Qué es más lógico?",
     "options": ["Hubo error crítico", "No hubo error crítico", "El proceso explotó", "El proceso no existe"],
     "correct_index": 1, "domain": "RL"},
    {"text": "Un equipo falla en promedio 2 veces por día. ¿Qué describe 'en promedio'?",
     "options": ["Siempre 2 exactas", "Puede variar alrededor de 2", "Nunca falla", "Solo falla lunes"],
     "correct_index": 1, "domain": "CN"},
    {"text": "Selecciona el sinónimo más cercano de 'imparcial':",
     "options": ["justo", "impulsivo", "temporal", "temeroso"],
     "correct_index": 0, "domain": "VB"},
    {"text": "Piensa en esta regla: 'Uno descansa, dos trabajan, luego rotación'. ¿Cuántas personas mínimas hay involucradas?",
     "options": ["1", "2", "3", "4"],
     "correct_index": 2, "domain": "MA"},
    {"text": "Tienes 3 entregas en distintas zonas y un solo vehículo. ¿Qué estrategia inicial tiene más sentido?",
     "options": ["Ruta más eficiente total", "Orden aleatorio", "Ir a la más lejana primero siempre", "No repartir"],
     "correct_index": 0, "domain": "PL"},

    # ---------- C7 ----------
    {"text": "Si un reporte COMPLETO siempre se envía, y encontraste uno que NO se envió, ¿qué es más probable?",
     "options": ["Estaba completo", "Estaba incompleto", "Se destruyó mágicamente", "Nunca existió"],
     "correct_index": 1, "domain": "RL"},
    {"text": "De 50 elementos, 5 presentan error. ¿Cuál es la tasa de error aproximada?",
     "options": ["1%", "5%", "10%", "50%"],
     "correct_index": 2, "domain": "CN"},
    {"text": "Completa la analogía: 'Prever' es a 'anticipar' como 'corregir' es a:",
     "options": ["ignorar", "ajustar", "romper", "ocultar"],
     "correct_index": 1, "domain": "VB"},
    {"text": "Regla mental avanzada: 'Si escuchas PRIORIDAD, todo lo demás se pausa'. ¿Qué implica PRIORIDAD?",
     "options": ["Esperar al final", "Ignorar", "Atender de inmediato", "Borrar todo"],
     "correct_index": 2, "domain": "MA"},
    {"text": "Hay dos incidencias críticas, y un especialista único. ¿Qué haces primero?",
     "options": ["Enviar especialista al riesgo más grave", "Nada", "Cerrar todo sin avisar", "Atender lo menos importante"],
     "correct_index": 0, "domain": "PL"},

    # ---------- C8 ----------
    {"text": "Si 'ningún acceso sin autorización es permitido' y ves a alguien sin autorización adentro, ¿qué puedes concluir?",
     "options": ["Se violó la norma", "No hay norma", "Nunca hubo acceso", "Nada pasó"],
     "correct_index": 0, "domain": "RL"},
    {"text": "Cuando dices 'riesgo bajo, no cero', significa:",
     "options": ["Imposible que pase algo", "Probabilidad pequeña pero existe", "Está ocurriendo ahora", "Garantizado que pase"],
     "correct_index": 1, "domain": "CN"},
    {"text": "¿Qué palabra describe mejor 'metódico'?",
     "options": ["aleatorio", "ordenado", "impulsivo", "improvisado"],
     "correct_index": 1, "domain": "VB"},
    {"text": "Memoriza internamente: B7Q. Regla: avanza cada letra una posición (B→C, Q→R) y suma 1 al número. ¿Resultado?",
     "options": ["B7Q", "C8R", "C6R", "A6P"],
     "correct_index": 1, "domain": "MA"},
    {"text": "Debes reasignar recursos tras una falla mayor inesperada. ¿Qué priorizas primero?",
     "options": ["Impacto en seguridad", "Popularidad del área", "Quién reclama más fuerte", "Antigüedad del empleado"],
     "correct_index": 0, "domain": "PL"},

    # ---------- C9 ----------
    {"text": "Si un sistema se detiene cuando la alarma es REAL, y ahora todo se detuvo, ¿qué es más razonable?",
     "options": ["La alarma era real", "No hubo alarma", "La alarma es siempre falsa", "Se detuvo sin razón"],
     "correct_index": 0, "domain": "RL"},
    {"text": "¿Por qué mirar datos de varios días es mejor que usar sólo 1 día raro?",
     "options": ["Elimina toda variación",
                 "Reduce el sesgo de un día atípico",
                 "Obliga a no cambiar nada",
                 "Hace imposible medir"],
     "correct_index": 1, "domain": "CN"},
    {"text": "¿Qué define mejor 'contingencia'?",
     "options": ["Plan alternativo ante una falla posible",
                 "Descanso social",
                 "Decoración estética",
                 "Chisme interno"],
     "correct_index": 0, "domain": "VB"},
    {"text": "Regla de 'doble chequeo' = repetir toda la revisión desde cero. ¿Para qué sirve?",
     "options": ["Perder tiempo",
                 "Asegurar que no se omitió nada crítico",
                 "Evitar reportar",
                 "Ignorar fallas"],
     "correct_index": 1, "domain": "MA"},
    {"text": "La operación se detiene si no se cumple un estándar mínimo. ¿Por qué frenar aunque cueste dinero?",
     "options": ["Castigar al equipo",
                 "Proteger seguridad y activos críticos",
                 "Evitar auditorías por capricho",
                 "Demostrar autoridad sin motivo"],
     "correct_index": 1, "domain": "PL"},

    # ---------- C10 (más abstracto / integración) ----------
    {"text": "Si 'algunos A son B' y 'tu elemento es A', ¿qué se puede afirmar con certeza?",
     "options": ["Tu elemento es B con seguridad",
                 "Tu elemento no es B",
                 "Podría ser B o no serlo",
                 "A y B son lo mismo siempre"],
     "correct_index": 2, "domain": "RL"},
    {"text": "¿Qué describe mejor una proporción estable?",
     "options": ["Relación relativamente constante entre dos cantidades",
                 "Que las cantidades son idénticas",
                 "Que una cantidad nunca cambia jamás",
                 "Que no se puede comparar"],
     "correct_index": 0, "domain": "CN"},
    {"text": "Selecciona la mejor definición de 'coherencia interna' en un informe:",
     "options": ["Que las partes no se contradigan entre sí",
                 "Que tenga colores llamativos",
                 "Que tenga chistes",
                 "Que sea muy largo"],
     "correct_index": 0, "domain": "VB"},
    {"text": "Cuando mantienes varias reglas mentales al mismo tiempo y decides cuál aplicar a cada caso sin confundirlas, ¿qué habilidad usas más?",
     "options": ["memoria de trabajo / actualización mental",
                 "fuerza física",
                 "reflejo muscular",
                 "suerte"],
     "correct_index": 0, "domain": "MA"},
    {"text": "Te quedan menos de 2 minutos del test total y 3 preguntas pendientes. ¿Qué haces para maximizar puntaje?",
     "options": ["Te rindes",
                 "Respondes rápido priorizando la lógica más básica",
                 "Cierras todo sin contestar",
                 "Cierras el navegador"],
     "correct_index": 1, "domain": "PL"},
]

TOTAL_QUESTIONS = len(QUESTIONS)  # 50

# ============================================================
# ESTADO GLOBAL
# ============================================================

if "stage" not in st.session_state:
    st.session_state.stage = "info"  # info -> test -> done

if "candidate_name" not in st.session_state:
    st.session_state.candidate_name = ""

if "evaluator_email" not in st.session_state:
    st.session_state.evaluator_email = ""

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "answers" not in st.session_state:
    # answers[i] = índice de alternativa elegida, o None si no respondida
    st.session_state.answers = {i: None for i in range(TOTAL_QUESTIONS)}

# temporizador total en segundos (20 min = 1200 s)
TEST_DURATION_SEC = 20 * 60

if "test_start_time" not in st.session_state:
    st.session_state.test_start_time = None  # datetime cuando arranca el test

if "already_sent" not in st.session_state:
    st.session_state.already_sent = False

if "_need_rerun" not in st.session_state:
    st.session_state._need_rerun = False

# ============================================================
# LÓGICA RESULTADOS / INFORME
# ============================================================

def compute_results(answers_dict):
    """
    Devuelve diccionario con:
    - total_correct
    - domain_scores: dict { "RL": {...}, ... }
    - profile_text
    - overall_level
    """
    # contar aciertos globales y por dominio
    per_domain_total = {"RL":0,"CN":0,"VB":0,"MA":0,"PL":0}
    per_domain_ok    = {"RL":0,"CN":0,"VB":0,"MA":0,"PL":0}

    total_correct = 0

    for idx, q in enumerate(QUESTIONS):
        dom = q["domain"]
        per_domain_total[dom] += 1

        chosen = answers_dict.get(idx)
        if chosen is not None and chosen == q["correct_index"]:
            total_correct += 1
            per_domain_ok[dom] += 1

    global_pct = (total_correct / TOTAL_QUESTIONS) * 100.0

    # nivel global
    if global_pct >= 75:
        overall_level = "ALTO"
    elif global_pct >= 45:
        overall_level = "PROMEDIO"
    else:
        overall_level = "BAJO"

    # describir por dominio
    domain_scores = {}
    for dom in ["RL","CN","VB","MA","PL"]:
        tot = per_domain_total[dom]
        ok  = per_domain_ok[dom]
        pct = (ok/tot*100.0) if tot>0 else 0.0

        if pct >= 75:
            lvl = "Alto"
        elif pct >= 45:
            lvl = "Promedio"
        else:
            lvl = "Bajo"

        if dom == "RL":
            name="Lógica / Coherencia"
            desc="Uso de relaciones lógicas y consistencia de reglas."
        elif dom == "CN":
            name="Razonamiento Numérico"
            desc="Manejo de cantidades, proporciones, tasas y variación."
        elif dom == "VB":
            name="Comprensión Verbal"
            desc="Vocabulario, analogías y sentido semántico preciso."
        elif dom == "MA":
            name="Memoria de Trabajo"
            desc="Retener y actualizar reglas breves bajo presión."
        else:
            name="Planificación / Prioridad"
            desc="Toma de decisión y priorización bajo costo/tiempo."

        domain_scores[dom] = {
            "name": name,
            "correct": ok,
            "total": tot,
            "pct": pct,
            "level": lvl,
            "desc": desc
        }

    # texto general del perfil
    profile_text = (
        f"Resultado global: {total_correct}/{TOTAL_QUESTIONS} correctas "
        f"({global_pct:.0f}%). Nivel global estimado: {overall_level} "
        "(Bajo / Promedio / Alto). "
        "Este puntaje refleja velocidad analítica, manejo de memoria activa, "
        "comprensión verbal y priorización bajo límite de tiempo."
    )

    # breve resumen cognitivo
    if overall_level == "ALTO":
        summary_level = (
            "Rendimiento cognitivo sobre promedio, con buena velocidad de análisis, "
            "capacidad de abstracción y priorización bajo presión."
        )
    elif overall_level == "PROMEDIO":
        summary_level = (
            "Desempeño en rango promedio. Muestra capacidad funcional para comprender "
            "reglas, números y decisiones prácticas en condiciones normales."
        )
    else:
        summary_level = (
            "Desempeño bajo el promedio esperado. Podría requerir más apoyo para "
            "mantener foco, retener instrucciones complejas y priorizar bajo presión."
        )

    return {
        "total_correct": total_correct,
        "global_pct": global_pct,
        "overall_level": overall_level,
        "profile_text": profile_text,
        "summary_level": summary_level,
        "domain_scores": domain_scores
    }

# ============================================================
# UTILIDADES PDF
# ============================================================

def _wrap(c, text, width, font="Helvetica", size=8):
    """
    Divide 'text' en líneas que no sobrepasen 'width' pts usando medir stringWidth.
    """
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
    """
    Dibuja párrafo envuelto en 'width'. Devuelve la Y final.
    Con más leading para evitar texto encima.
    """
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
                 evaluator_email,
                 fecha_eval,
                 results_dict):
    """
    Renderiza 1 página tipo ficha, con:
    - Datos del candidato
    - Resumen cognitivo
    - Perfil comparativo global
    - Tabla por dimensión (RL,CN,VB,MA,PL)
    Todo con suficiente espaciado para evitar solapamientos.
    """

    buf = BytesIO()
    W, H = A4  # 595 x 842 aprox
    c = canvas.Canvas(buf, pagesize=A4)

    margin_left = 36
    margin_right = 36
    page_width = W - margin_left - margin_right

    # Encabezado principal
    c.setFont("Helvetica-Bold",11)
    c.setFillColor(colors.black)
    c.drawString(margin_left, H-40, "INFORME DE EVALUACIÓN COGNITIVA")
    c.setFont("Helvetica",7)
    c.setFillColor(colors.grey)
    c.drawString(margin_left, H-55, "Uso interno de RR.HH. / Selección y desarrollo. No es diagnóstico clínico.")

    # Caja 1: Datos del candidato y resumen cognitivo
    box1_y_top = H-70
    box1_h = 120
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.white)
    c.rect(margin_left, box1_y_top-box1_h, page_width, box1_h, stroke=1, fill=1)

    y_cursor = box1_y_top-14
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(margin_left+8, y_cursor, f"Nombre evaluado: {candidate_name}")
    y_cursor -= 12
    c.setFont("Helvetica",8)
    c.drawString(margin_left+8, y_cursor, f"Evaluador / destinatario: {evaluator_email}")
    y_cursor -= 12
    c.drawString(margin_left+8, y_cursor, f"Fecha de evaluación: {fecha_eval}")
    y_cursor -= 16

    # Resumen global
    c.setFont("Helvetica-Bold",8)
    c.drawString(margin_left+8, y_cursor, "Resumen cognitivo observado:")
    y_cursor -= 12
    y_cursor = _draw_par(
        c,
        results_dict["summary_level"],
        margin_left+12,
        y_cursor,
        page_width-24,
        font="Helvetica",
        size=7.5,
        leading=11,
        color=colors.black,
        max_lines=4
    )
    y_cursor -= 8

    # Perfil comparativo global (total correctas, % y nivel)
    c.setFont("Helvetica-Bold",8)
    c.drawString(margin_left+8, y_cursor, "Perfil comparativo global:")
    y_cursor -= 12
    y_cursor = _draw_par(
        c,
        results_dict["profile_text"],
        margin_left+12,
        y_cursor,
        page_width-24,
        font="Helvetica",
        size=7.5,
        leading=11,
        color=colors.black,
        max_lines=5
    )

    # Caja 2: Desempeño por dimensión (tabla tipo grilla)
    box2_y_top = y_cursor - 12
    box2_h = 300  # altura amplia para que el texto quepa con aire
    if box2_y_top - box2_h < 60:
        # si queda muy abajo, forzamos un salto de página para seguridad
        c.showPage()
        # Redibujar encabezado mini en 2da página (esto sólo pasa en overflow extremo)
        c.setFont("Helvetica-Bold",10)
        c.drawString(margin_left, H-40, "INFORME DE EVALUACIÓN COGNITIVA (continuación)")
        c.setFont("Helvetica",7)
        c.setFillColor(colors.grey)
        c.drawString(margin_left, H-55, "Uso interno RR.HH. / No clínico.")
        # reset coords
        box2_y_top = H-70
        y_cursor = box2_y_top
        # seguimos normal
    # Caja 2
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.white)
    c.rect(margin_left, box2_y_top-box2_h, page_width, box2_h, stroke=1, fill=1)

    # título tabla
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(margin_left+8, box2_y_top-14, "Desempeño por dimensión")

    # Cabeceras de la tabla
    table_head_y = box2_y_top-30
    col_dim_x   = margin_left+8
    col_score_x = margin_left+170
    col_level_x = margin_left+260
    col_desc_x  = margin_left+320

    c.setFont("Helvetica-Bold",7)
    c.drawString(col_dim_x,   table_head_y, "Dimensión")
    c.drawString(col_score_x, table_head_y, "Aciertos / Total")
    c.drawString(col_level_x, table_head_y, "Nivel")
    c.drawString(col_desc_x,  table_head_y, "Descripción funcional")

    # filas
    row_y = table_head_y-16
    row_gap = 34  # más grande para evitar solapes

    for dom_key in ["RL","CN","VB","MA","PL"]:
        ds = results_dict["domain_scores"][dom_key]

        # Dimensión / nombre
        c.setFont("Helvetica-Bold",7)
        c.setFillColor(colors.black)
        c.drawString(col_dim_x, row_y, ds["name"])

        # Aciertos / Total
        c.setFont("Helvetica",7)
        c.drawString(col_score_x, row_y, f"{ds['correct']}/{ds['total']}")

        # Nivel
        c.drawString(col_level_x, row_y, ds["level"])

        # Descripción envuelta
        y_after = _draw_par(
            c,
            ds["desc"],
            col_desc_x,
            row_y,
            page_width - (col_desc_x - margin_left) - 8,
            font="Helvetica",
            size=7,
            leading=10,
            color=colors.black,
            max_lines=3
        )
        # siguiente fila deja espacio
        row_y = min(row_y, y_after) - (row_gap - 10)

    # Nota metodológica al final
    note_y = (box2_y_top-box2_h) + 20
    c.setFont("Helvetica-Bold",7)
    c.setFillColor(colors.black)
    c.drawString(margin_left+8, note_y+24, "Nota metodológica")
    _draw_par(
        c,
        "Este informe se basa en respuestas autoadministradas en un test de "
        "razonamiento y toma de decisión bajo límite de tiempo. Describe patrones "
        "cognitivos funcionales (lógica, números, comprensión verbal, memoria "
        "operativa y priorización). No constituye diagnóstico clínico ni, por sí "
        "solo, determina idoneidad absoluta. Debe complementarse con entrevista y "
        "verificación de experiencia.",
        margin_left+8,
        note_y+12,
        page_width-16,
        font="Helvetica",
        size=6.5,
        leading=10,
        color=colors.grey,
        max_lines=8
    )

    # Footer
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawRightString(W-margin_right, 32, "Documento interno RR.HH. · Evaluación Cognitiva · No clínico")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()

# ============================================================
# EMAIL
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
# FINALIZACIÓN DEL TEST
# 1. Marca como malas las no respondidas
# 2. Genera PDF
# 3. Envía correo
# 4. Cambia stage -> done
# ============================================================

def finalize_and_send():
    # 1. asegurar que las no respondidas queden como None (ya están así)
    #    no hay que hacer nada extra porque compute_results ya trata None como mala

    results_dict = compute_results(st.session_state.answers)

    now_txt = datetime.now().strftime("%d/%m/%Y %H:%M")

    pdf_bytes = generate_pdf(
        candidate_name   = st.session_state.candidate_name,
        evaluator_email  = st.session_state.evaluator_email,
        fecha_eval       = now_txt,
        results_dict     = results_dict
    )

    if not st.session_state.already_sent:
        try:
            send_email_with_pdf(
                to_email   = st.session_state.evaluator_email,
                pdf_bytes  = pdf_bytes,
                filename   = "Informe_Cognitivo.pdf",
                subject    = "Informe Evaluación Cognitiva (IQ operativo)",
                body_text  = (
                    "Se adjunta el Informe Cognitivo (IQ operativo) "
                    f"de {st.session_state.candidate_name}. "
                    "Uso interno RR.HH. / No clínico."
                ),
            )
        except Exception:
            # en producción querrías loggear esto
            pass
        st.session_state.already_sent = True

    st.session_state.stage = "done"
    st.session_state._need_rerun = True


# ============================================================
# CALLBACK DE RESPUESTA
# ============================================================

def choose_answer(opt_index: int):
    q_idx = st.session_state.current_q
    st.session_state.answers[q_idx] = opt_index

    # avanzar de pregunta
    if q_idx < TOTAL_QUESTIONS - 1:
        st.session_state.current_q += 1
        st.session_state._need_rerun = True
    else:
        finalize_and_send()


# ============================================================
# MANEJO DEL TEMPORIZADOR
# ============================================================

def get_time_left_sec():
    """
    Devuelve segundos restantes. Si ya se acabó, devuelve 0.
    """
    if st.session_state.test_start_time is None:
        return TEST_DURATION_SEC
    elapsed = (datetime.now() - st.session_state.test_start_time).total_seconds()
    left = TEST_DURATION_SEC - elapsed
    if left < 0:
        left = 0
    return int(left)

def check_timer_and_maybe_finish():
    """
    Si el tiempo llegó a 0, finaliza el test.
    """
    if st.session_state.stage == "test":
        left = get_time_left_sec()
        if left <= 0:
            # tiempo agotado => finalizar
            finalize_and_send()

def format_mm_ss(sec_left: int):
    mm = sec_left // 60
    ss = sec_left % 60
    return f"{mm:02d}:{ss:02d}"

# ============================================================
# VISTAS
# ============================================================

def view_info_form():
    st.markdown(
        "### Evaluación Cognitiva General (IQ Operativo)\n"
        "Esta prueba mide razonamiento lógico, numérico, comprensión verbal, "
        "memoria de trabajo y priorización bajo presión de tiempo.\n\n"
        "**Duración máxima:** 20 minutos.\n"
        "Al finalizar (o al agotarse el tiempo), se genera un informe interno "
        "que se envía automáticamente al correo del evaluador."
    )

    st.session_state.candidate_name = st.text_input(
        "Nombre del evaluado",
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

    if st.button("Iniciar test", type="primary", disabled=not ok, use_container_width=True):
        # reset estado del test
        st.session_state.current_q = 0
        st.session_state.answers = {i: None for i in range(TOTAL_QUESTIONS)}
        st.session_state.already_sent = False
        st.session_state.test_start_time = datetime.now()
        st.session_state.stage = "test"
        st.session_state._need_rerun = True
        st.rerun()


def view_test():
    # Refresco automático cada segundo para que el temporizador baje visualmente
    st_autorefresh = st.experimental_rerun  # fallback if not using st_autorefresh
    # Streamlit moderno tiene st.autorefresh:
    try:
        st.autorefresh(interval=1000, key="timer_autorefresh")
    except Exception:
        # si la versión de Streamlit es vieja no pasa nada
        pass

    check_timer_and_maybe_finish()
    if st.session_state.stage == "done":
        # Si se agotó el tiempo en esta llamada
        st.rerun()

    q_idx = st.session_state.current_q
    q = QUESTIONS[q_idx]

    # progreso
    progreso = (q_idx+1)/TOTAL_QUESTIONS
    sec_left = get_time_left_sec()
    time_str = format_mm_ss(sec_left)

    # colores del timer según tiempo restante
    # verde normal >120s, amarillo <=120s y >30s, rojo <=30s
    if sec_left <= 30:
        timer_bg = "#dc2626"    # rojo
        timer_fg = "#fff"
    elif sec_left <= 120:
        timer_bg = "#facc15"    # amarillo
        timer_fg = "#000"
    else:
        timer_bg = "#1e40af"    # azul oscuro
        timer_fg = "#fff"

    # HEADER (barra superior)
    st.markdown(
        f"""
        <div style="
            background:linear-gradient(to right,#1e40af,#4338ca);
            color:white;
            border-radius:12px 12px 0 0;
            padding:16px 20px;
            display:flex;
            flex-wrap:wrap;
            justify-content:space-between;
            align-items:flex-start;
            row-gap:8px;
        ">
            <div style="flex-grow:1; min-width:200px;">
                <div style="font-weight:700; font-size:1rem;">
                    Test Cognitivo General (50 ítems)
                </div>
                <div style="margin-top:4px; font-size:.8rem; color:#c7d2fe;">
                    Pregunta {q_idx+1} de {TOTAL_QUESTIONS} · {int(round(progreso*100))}%
                </div>
            </div>

            <div style="
                min-width:140px;
                display:flex;
                justify-content:flex-end;
                flex-grow:0;
            ">
                <div style="
                    background:{timer_bg};
                    color:{timer_fg};
                    border-radius:12px;
                    padding:8px 12px;
                    font-family:monospace;
                    font-size:1.2rem;
                    font-weight:700;
                    box-shadow:0 8px 16px rgba(0,0,0,0.4);
                ">
                    ⏱ {time_str}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.progress(progreso)

    # tarjeta de pregunta
    st.markdown(
        f"""
        <div style="
            background:#ffffff;
            border:1px solid #e2e8f0;
            border-radius:12px;
            padding:24px;
            box-shadow:0 12px 24px rgba(0,0,0,0.06);
            margin-top:12px;
        ">
            <p style="
                margin:0;
                font-size:1.05rem;
                color:#1e293b;
                line-height:1.45;
                font-weight:500;
            ">{q["text"]}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # alternativas
    cols = st.columns(2)
    for i, opt in enumerate(q["options"]):
        with cols[i % 2]:
            st.button(
                opt,
                key=f"opt_{q_idx}_{i}",
                use_container_width=True,
                on_click=choose_answer,
                args=(i,)
            )

    # nota confidencialidad
    st.markdown(
        """
        <div style="
            background:#f8fafc;
            border:1px solid #e2e8f0;
            border-radius:8px;
            padding:10px 14px;
            font-size:.8rem;
            color:#475569;
            margin-top:12px;
        ">
            <b>Confidencialidad:</b> Uso interno RR.HH. / Selección y desarrollo.
            El candidato no recibe copia directa del informe.
        </div>
        """,
        unsafe_allow_html=True
    )

    # Si el tiempo cayó a 0 durante la interacción,
    # forzamos finalización de nuevo porque puede haber pasado 1s
    check_timer_and_maybe_finish()
    if st.session_state.stage == "done":
        st.rerun()


def view_done():
    st.markdown(
        """
        <div style="
            background:linear-gradient(to bottom right,#ecfdf5,#d1fae5);
            padding:28px;
            border-radius:14px;
            box-shadow:0 24px 48px rgba(0,0,0,0.08);
            text-align:center;
        ">
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
                margin:0 auto 12px auto;
            ">
                ✔
            </div>
            <div style="
                font-size:1.25rem;
                font-weight:800;
                color:#065f46;
                margin-bottom:6px;
            ">
                Evaluación finalizada
            </div>
            <div style="color:#065f46;">
                Los resultados fueron procesados y enviados al correo del evaluador.
            </div>
            <div style="
                color:#065f46;
                font-size:.85rem;
                margin-top:6px;
            ">
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
    # si por alguna razón no hay hora de inicio (ej. reload duro), la seteamos
    if st.session_state.test_start_time is None:
        st.session_state.test_start_time = datetime.now()
    view_test()

elif st.session_state.stage == "done":
    # aseguramos envío (idempotente gracias a already_sent)
    if not st.session_state.already_sent:
        finalize_and_send()
    view_done()

# ============================================================
# RERUN CONTROLADO
# ============================================================

if st.session_state._need_rerun:
    st.session_state._need_rerun = False
    st.rerun()
