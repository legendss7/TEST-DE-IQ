# ============================================================
# Test Cognitivo General (IQ Screening) · 70 preguntas
# Nivel: ingreso técnico / universitario inicial
# - Una sola pregunta por pantalla
# - Límite total: 20 minutos (tiempo global, invisible)
# - Si el candidato cambia de pestaña / ventana → se termina
# - Preguntas sin imágenes (razonamiento, memoria activa, secuencias lógicas)
# - Dificultad escala en el orden mostrado
# - Informe PDF en 1 hoja con layout tipo ficha
#
# Requisitos:
#   pip install streamlit reportlab
#
# IMPORTANTE:
#   - Este código NO envía correo. Sólo genera PDF descargable.
#   - Mantiene toda la lógica de finalización automática por tiempo o pérdida de foco.
# ============================================================

import streamlit as st
from datetime import datetime, timedelta
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# ===========================
# CONFIG STREAMLIT
# ===========================
st.set_page_config(
    page_title="Test Cognitivo General",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Tiempo máximo total permitido (20 minutos)
TEST_LIMIT_MINUTES = 20

# ===========================
# UTILIDADES DE PDF
# ===========================
def _wrap(c, text, width, font="Helvetica", size=7):
    """Divide texto en líneas que caben en 'width' (en puntos)."""
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
    size=7,
    leading=9,
    color=colors.black,
    max_lines=None
):
    """
    Dibuja párrafo con salto de línea automático.
    Devuelve la nueva coordenada y (para seguir escribiendo abajo).
    """
    c.setFont(font, size)
    c.setFillColor(color)
    lines = _wrap(c, text, width, font, size)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y

# ===========================
# PREGUNTAS (70)
# Estructura:
#   domain: "RL","CN","VB","MA","PL"
#       RL = Razonamiento Lógico / patrones
#       CN = Cuantitativo / numérico conceptual
#       VB = Verbal / vocabulario / analogías
#       MA = Memoria / Atención / actualización mental
#       PL = Planeamiento / Resolución de problemas
#
#   correct_index: índice 0..3 de la alternativa correcta
#
# Orden:
#   Vamos de más básico a más complejo en ciclos de 5 preguntas
#   (una de cada dominio por ciclo) → total 14 ciclos → 70 preguntas.
# ===========================

QUESTIONS = [
    # --- Ciclo 1 (muy básico) ---
    {
        "text": "RL1. Si todas las llaves abren puertas, y el objeto que tienes en la mano es una llave, ¿qué puedes concluir con más seguridad?",
        "options": [
            "Puede abrir al menos una puerta.",
            "No sirve para nada.",
            "Rompe puertas sin usarse.",
            "Sólo es decorativa."
        ],
        "correct_index": 0,
        "domain": "RL"
    },
    {
        "text": "CN1. Un trabajador arma 4 cajas por hora. En 2 horas arma:",
        "options": ["4 cajas", "6 cajas", "8 cajas", "10 cajas"],
        "correct_index": 2,
        "domain": "CN"
    },
    {
        "text": "VB1. ¿Cuál de estas palabras es más parecida a 'estable' en el sentido de 'que no cambia fácil'?",
        "options": ["volátil", "constante", "frágil", "impulsivo"],
        "correct_index": 1,
        "domain": "VB"
    },
    {
        "text": "MA1. Escucha mentalmente esta secuencia: ROJO, AZUL, ROJO, VERDE. ¿Cuál fue la tercera palabra?",
        "options": ["ROJO", "AZUL", "VERDE", "AMARILLO"],
        "correct_index": 0,
        "domain": "MA"
    },
    {
        "text": "PL1. Tienes que entregar 3 documentos al jefe antes de irte. ¿Cuál orden es más eficiente?: (1) Imprimir, (2) Firmar, (3) Entregar.",
        "options": [
            "Entregar → Firmar → Imprimir",
            "Firmar → Imprimir → Entregar",
            "Imprimir → Firmar → Entregar",
            "Imprimir → Entregar → Firmar"
        ],
        "correct_index": 2,
        "domain": "PL"
    },

    # --- Ciclo 2 ---
    {
        "text": "RL2. Si A siempre llega antes que B, y B siempre llega antes que C, ¿quién llega último?",
        "options": ["A", "B", "C", "A y B juntos"],
        "correct_index": 2,
        "domain": "RL"
    },
    {
        "text": "CN2. Si un producto cuesta 100 y sube 10%, ¿cuánto cuesta ahora?",
        "options": ["90", "100", "110", "120"],
        "correct_index": 2,
        "domain": "CN"
    },
    {
        "text": "VB2. 'Preciso' se parece más a:",
        "options": ["exacto", "lento", "simpático", "temporal"],
        "correct_index": 0,
        "domain": "VB"
    },
    {
        "text": "MA2. Memoriza mentalmente: 5, 2, 7. Ahora intercambia el primer y el último número. ¿Cuál queda en el medio?",
        "options": ["2", "5", "7", "No se puede saber"],
        "correct_index": 0,
        "domain": "MA"
    },
    {
        "text": "PL2. Te dan dos tareas: A (5 min) y B (30 min). Te queda media hora. ¿Cuál haces primero para asegurar un resultado entregable hoy?",
        "options": [
            "Hacer primero B completa",
            "Hacer primero A completa",
            "No hacer ninguna",
            "Empezar ambas y no terminar ninguna"
        ],
        "correct_index": 1,
        "domain": "PL"
    },

    # --- Ciclo 3 ---
    {
        "text": "RL3. Una afirmación dice: 'Todos los técnicos usan guantes.' Pedro es técnico. ¿Qué es más lógico?",
        "options": [
            "Pedro a veces usa guantes.",
            "Pedro nunca usa guantes.",
            "Pedro usa guantes.",
            "Pedro prohíbe guantes."
        ],
        "correct_index": 2,
        "domain": "RL"
    },
    {
        "text": "CN3. Una máquina produce 240 piezas en 8 horas. Suponiendo ritmo constante, ¿cuántas piezas en 1 hora?",
        "options": ["15", "20", "30", "40"],
        "correct_index": 2,
        "domain": "CN"
    },
    {
        "text": "VB3. Elija la opción que completa la analogía: 'Rápido' es a 'veloz' como 'lento' es a:",
        "options": ["pausado", "urgente", "apurado", "reciente"],
        "correct_index": 0,
        "domain": "VB"
    },
    {
        "text": "MA3. Mantén mentalmente: L, M, T, M. ¿Cuál letra apareció 2 veces?",
        "options": ["L", "M", "T", "Ninguna"],
        "correct_index": 1,
        "domain": "MA"
    },
    {
        "text": "PL3. Tienes 3 pedidos urgentes y sólo puedes terminar uno hoy. ¿Cuál eliges primero?",
        "options": [
            "El de menor impacto si falla",
            "El más crítico para el cliente más importante",
            "El que menos te gusta",
            "El que te toma más horas"
        ],
        "correct_index": 1,
        "domain": "PL"
    },

    # --- Ciclo 4 ---
    {
        "text": "RL4. Si 'ningún informe incompleto se firma' y 'este informe está firmado', ¿qué concluyes?",
        "options": [
            "El informe está incompleto",
            "El informe no está incompleto",
            "El informe se perdió",
            "El informe no existe"
        ],
        "correct_index": 1,
        "domain": "RL"
    },
    {
        "text": "CN4. Un cliente paga 250 y recibe 40 de vuelto. ¿Cuánto costaba el producto?",
        "options": ["200", "210", "290", "2900"],
        "correct_index": 1,
        "domain": "CN"
    },
    {
        "text": "VB4. ¿Cuál palabra no encaja con las otras?",
        "options": ["cálido", "templado", "ardiente", "helado"],
        "correct_index": 3,
        "domain": "VB"
    },
    {
        "text": "MA4. Recuerda esta instrucción interna: 'Primero archivar, luego reportar, después enviar'. ¿Qué acción va segunda?",
        "options": ["archivar", "reportar", "enviar", "ninguna"],
        "correct_index": 1,
        "domain": "MA"
    },
    {
        "text": "PL4. Tu jefatura dice: 'No inicies el paso 2 sin cerrar el paso 1'. Pero el paso 2 está urgente. ¿Qué haces?",
        "options": [
            "Empiezo paso 2 igual porque es urgente",
            "Termino paso 1 aunque retrase paso 2",
            "No hago nada",
            "Invento un paso 3"
        ],
        "correct_index": 1,
        "domain": "PL"
    },

    # --- Ciclo 5 ---
    {
        "text": "RL5. Afirmaciones: (1) Algunos turnos nocturnos son pagados extra. (2) Tu turno es nocturno. ¿Qué es más cierto?",
        "options": [
            "Tu turno recibe extra sí o sí",
            "Tu turno no recibe extra",
            "Podrías recibir extra",
            "Ningún turno recibe extra"
        ],
        "correct_index": 2,
        "domain": "RL"
    },
    {
        "text": "CN5. Un contenedor lleva 12 cajas iguales. Cada caja pesa 5 kg. ¿Peso total?",
        "options": ["12 kg", "17 kg", "30 kg", "60 kg"],
        "correct_index": 3,
        "domain": "CN"
    },
    {
        "text": "VB5. 'Imparcial' significa más cercano a:",
        "options": ["justo", "rápido", "tímido", "inseguro"],
        "correct_index": 0,
        "domain": "VB"
    },
    {
        "text": "MA5. Mantén mentalmente la regla: 'Si escuchas X, cambias X por Z'. Secuencia mental: X, A, X. ¿Cuál queda al final tras aplicar la regla?",
        "options": ["X, A, X", "Z, A, Z", "X, Z, X", "Z, Z, Z"],
        "correct_index": 1,
        "domain": "MA"
    },
    {
        "text": "PL5. Debes coordinar a 3 personas y sólo una puede usar la máquina crítica a la vez. ¿Qué es más importante para planificar?",
        "options": [
            "Quién te cae mejor",
            "Orden y turnos claros de uso",
            "Que todos empiecen al mismo tiempo",
            "Que nadie haga pausa"
        ],
        "correct_index": 1,
        "domain": "PL"
    },

    # --- Ciclo 6 ---
    {
        "text": "RL6. Si toda persona puntual genera buena impresión inicial, y Carla no generó buena impresión inicial, ¿qué puedes deducir con más lógica?",
        "options": [
            "Carla fue puntual",
            "Carla llegó tarde",
            "Carla renunció",
            "Carla es jefa"
        ],
        "correct_index": 1,
        "domain": "RL"
    },
    {
        "text": "CN6. Una tarea se estima en 'entre 45 y 60 minutos'. ¿Qué conclusión es más razonable?",
        "options": [
            "Siempre dura 30 minutos",
            "A veces puede tardar 50 minutos",
            "Nunca tarda más de 10 minutos",
            "Siempre dura 90 minutos"
        ],
        "correct_index": 1,
        "domain": "CN"
    },
    {
        "text": "VB6. Completa la relación: 'Ética' está a 'conducta' como 'norma' está a:",
        "options": ["opinión", "regla", "impulso", "secreto"],
        "correct_index": 1,
        "domain": "VB"
    },
    {
        "text": "MA6. Retén mentalmente: B7Q. Ahora cámbialo aplicando: 'toda letra pasa a la siguiente en el abecedario (B→C), y el número súmale 1'. ¿Qué obtienes?",
        "options": ["B7Q", "C8R", "A6P", "C6R"],
        "correct_index": 1,
        "domain": "MA"
    },
    {
        "text": "PL6. Hay una urgencia operativa y falta información parcial. ¿Qué primera acción es más efectiva?",
        "options": [
            "Actuar sin avisar a nadie",
            "Detener todo el proceso inmediatamente sin evaluar impacto",
            "Escalar y pedir aclaración rápida antes de ejecutar",
            "Ignorar la urgencia"
        ],
        "correct_index": 2,
        "domain": "PL"
    },

    # --- Ciclo 7 ---
    {
        "text": "RL7. 'Si se sobrecalienta la máquina, debe detenerse el turno'. El turno NO se detuvo. ¿Qué es más coherente?",
        "options": [
            "La máquina se sobrecalentó igual",
            "La máquina no se sobrecalentó",
            "La máquina explotó",
            "Nadie estaba trabajando"
        ],
        "correct_index": 1,
        "domain": "RL"
    },
    {
        "text": "CN7. Un equipo falla 2 veces al día en promedio. ¿Qué significa 'en promedio'?",
        "options": [
            "Siempre falla 2 veces exactas",
            "Puede fallar 1 día 1 vez y otro día 3 veces",
            "Nunca falla",
            "Sólo falla los lunes"
        ],
        "correct_index": 1,
        "domain": "CN"
    },
    {
        "text": "VB7. Selecciona la opción que es más contraria (antónima) a 'riguroso':",
        "options": ["exigente", "estricto", "cuidadoso", "relajado"],
        "correct_index": 3,
        "domain": "VB"
    },
    {
        "text": "MA7. Recibe mentalmente: 'informe - correo - informe - reunión'. ¿Cuál elemento apareció segunda vez?",
        "options": ["informe", "correo", "reunión", "ninguno"],
        "correct_index": 0,
        "domain": "MA"
    },
    {
        "text": "PL7. Tienes 4 tareas: 1 crítica corto plazo, 1 administrativa larga, 1 idea futura y 1 ajuste menor urgente de seguridad. ¿Cuál haces primero?",
        "options": [
            "La idea futura",
            "La administrativa más larga",
            "Lo urgente de seguridad / corto plazo",
            "Nada, esperas a mañana"
        ],
        "correct_index": 3 if False else 2,  # keep index 2
        "domain": "PL"
    },

    # --- Ciclo 8 ---
    {
        "text": "RL8. Si 'todos los informes A deben pasar por control de calidad' y este documento NO pasó por control, ¿qué deducción es más lógica?",
        "options": [
            "No es un informe A",
            "Es un informe A perfecto",
            "Fue aprobado igual",
            "No existe documento"
        ],
        "correct_index": 0,
        "domain": "RL"
    },
    {
        "text": "CN8. Si duplicar un valor significa multiplicarlo por 2, ¿qué afirmación es correcta?",
        "options": [
            "Duplicar 50 da 25",
            "Duplicar 50 da 50",
            "Duplicar 50 da 100",
            "Duplicar 50 elimina el valor"
        ],
        "correct_index": 2,
        "domain": "CN"
    },
    {
        "text": "VB8. ¿Cuál de estas expresiones es más cercana a 'criterio propio'?",
        "options": ["obediencia ciega", "juicio personal", "caos interno", "miedo al error"],
        "correct_index": 1,
        "domain": "VB"
    },
    {
        "text": "MA8. Recuerda la instrucción mental tipo control de calidad: 'Si escuchas REVISAR, después viene LIBERAR'. Secuencia mental: REVISAR → ?. ¿Qué sigue?",
        "options": ["detener", "archivar", "liberar", "rechazar"],
        "correct_index": 2,
        "domain": "MA"
    },
    {
        "text": "PL8. Tienes recursos limitados para 2 fallas simultáneas. ¿Qué estrategia inicial es más racional?",
        "options": [
            "Dividir recursos según criticidad de las fallas",
            "Usar todos los recursos en la menos importante",
            "Ignorar ambas fallas",
            "Esperar que alguien más lo haga sin avisar"
        ],
        "correct_index": 0,
        "domain": "PL"
    },

    # --- Ciclo 9 ---
    {
        "text": "RL9. 'Si un reporte está completo, entonces se envía'. Un reporte NO fue enviado. ¿Qué es más probable?",
        "options": [
            "El reporte está completo",
            "El reporte está incompleto",
            "El reporte está perfecto",
            "El reporte fue destruido por error"
        ],
        "correct_index": 1,
        "domain": "RL"
    },
    {
        "text": "CN9. Una muestra tiene 20% de piezas defectuosas. ¿Qué significa eso?",
        "options": [
            "Ninguna pieza está mala",
            "Todas las piezas están malas",
            "2 de cada 10, aproximadamente, están malas",
            "20 de cada 1000 están malas, exactamente",
        ],
        "correct_index": 2,
        "domain": "CN"
    },
    {
        "text": "VB9. Elije la mejor analogía: 'prever' está a 'anticipar' como 'corregir' está a:",
        "options": ["ignorar", "ajustar", "fallar", "ocultar"],
        "correct_index": 1,
        "domain": "VB"
    },
    {
        "text": "MA9. Escucha mentalmente una regla de turno: 'Uno descansa, dos trabajan, luego rotación'. ¿Cuál es el total de personas implicadas en la dinámica mínima descrita?",
        "options": ["1", "2", "3", "4"],
        "correct_index": 2,
        "domain": "MA"
    },
    {
        "text": "PL9. Si tienes que coordinar entregas en 3 zonas diferentes y sólo un vehículo disponible, ¿qué enfoque inicial tiene más sentido?",
        "options": [
            "Ir a las zonas en orden aleatorio total",
            "Priorizar ruta más eficiente para reducir tiempo total",
            "Hacer la vuelta más larga al inicio",
            "Quedarse sin repartir"
        ],
        "correct_index": 1,
        "domain": "PL"
    },

    # --- Ciclo 10 ---
    {
        "text": "RL10. Si 'toda alarma verdadera produce detención inmediata', y hubo detención inmediata, ¿qué opción es más lógica?",
        "options": [
            "La alarma fue verdadera con alta probabilidad",
            "No hubo alarma",
            "La alarma fue obligatoriamente falsa",
            "Se detuvo porque sí, sin razón"
        ],
        "correct_index": 0,
        "domain": "RL"
    },
    {
        "text": "CN10. En una inspección aleatoria, ¿por qué sirve el muestreo?",
        "options": [
            "Para revisar todo sin excepción",
            "Para tener una idea general de la calidad sin mirar cada pieza",
            "Para ignorar la calidad",
            "Para descartar siempre el lote entero"
        ],
        "correct_index": 1,
        "domain": "CN"
    },
    {
        "text": "VB10. ¿Cuál es la mejor opción para 'discrepancia'?",
        "options": ["acuerdo", "diferencia", "decoración", "planificación"],
        "correct_index": 1,
        "domain": "VB"
    },
    {
        "text": "MA10. Mantén mentalmente esta secuencia de pasos internos: 'Revisar → Ajustar → Confirmar'. ¿Cuál paso va primero?",
        "options": ["Revisar", "Ajustar", "Confirmar", "Ninguno"],
        "correct_index": 0,
        "domain": "MA"
    },
    {
        "text": "PL10. Tienes dos incidentes críticos al mismo tiempo y un solo técnico experto. ¿Qué haces?",
        "options": [
            "Enviar al técnico experto al incidente más peligroso para seguridad",
            "Pedirle que atienda el más pequeño primero",
            "No mandar a nadie",
            "Cerrar la planta sin informar"
        ],
        "correct_index": 0,
        "domain": "PL"
    },

    # --- Ciclo 11 ---
    {
        "text": "RL11. 'Si un documento es confidencial, sólo gerencia puede verlo'. Este documento fue visto por personal no-gerente. ¿Qué implica?",
        "options": [
            "El documento no era confidencial",
            "La gerencia no existe",
            "El documento fue destruido",
            "El documento es siempre público"
        ],
        "correct_index": 0,
        "domain": "RL"
    },
    {
        "text": "CN11. Se dice: 'El riesgo es bajo pero no cero'. ¿Qué significa?",
        "options": [
            "Es imposible que ocurra un problema",
            "Hay una probabilidad pequeña de que ocurra un problema",
            "El problema ocurrirá siempre",
            "El problema ya ocurrió"
        ],
        "correct_index": 1,
        "domain": "CN"
    },
    {
        "text": "VB11. Selecciona el término más cercano a 'metódico':",
        "options": ["improvisado", "ordenado", "impulsivo", "aleatorio"],
        "correct_index": 1,
        "domain": "VB"
    },
    {
        "text": "MA11. Recuerda regla interna: 'Si el supervisor dice REVISIÓN PRIORITARIA, saltar todo lo demás'. ¿Qué implica 'REVISIÓN PRIORITARIA'?",
        "options": [
            "Se espera al final de la semana",
            "Se ignora la instrucción",
            "Se atiende de inmediato",
            "Se elimina sin ver"
        ],
        "correct_index": 2,
        "domain": "MA"
    },
    {
        "text": "PL11. En planificación de turnos, ¿por qué sirve asignar suplentes?",
        "options": [
            "Para que sobre gente sin rol",
            "Para cubrir ausencias inesperadas sin detener la operación",
            "Para hacer que todos trabajen menos siempre",
            "Para evitar cualquier control"
        ],
        "correct_index": 1,
        "domain": "PL"
    },

    # --- Ciclo 12 ---
    {
        "text": "RL12. 'Si una pieza falla en control, esa pieza no puede ir al cliente'. Una pieza llegó al cliente. ¿Qué deducción tiene más sentido?",
        "options": [
            "Pasó control sin fallar",
            "Falló control pero igual la enviaron (imposible)",
            "No existe el cliente",
            "No existe control"
        ],
        "correct_index": 0,
        "domain": "RL"
    },
    {
        "text": "CN12. ¿Por qué una estimación basada en datos de varios días suele ser mejor que una basada en un solo día?",
        "options": [
            "Porque elimina la variación completamente",
            "Porque ignora los errores",
            "Porque promedia distintas situaciones y reduce sesgos de un día raro",
            "Porque impide cualquier cambio futuro"
        ],
        "correct_index": 2,
        "domain": "CN"
    },
    {
        "text": "VB12. Elija la palabra que mejor encaja con 'consistente' (en el sentido de comportamiento):",
        "options": ["variable", "coherente", "temporal", "aleatorio"],
        "correct_index": 1,
        "domain": "VB"
    },
    {
        "text": "MA12. Mantén mentalmente: 'Prioridad cliente A supera todo lo interno'. ¿Qué haces si cliente A llama durante otra tarea interna estándar?",
        "options": [
            "Ignoro al cliente A",
            "Detengo temporalmente la tarea interna y atiendo cliente A",
            "Hago ambas cosas mal",
            "Cierro todo y me voy"
        ],
        "correct_index": 1,
        "domain": "MA"
    },
    {
        "text": "PL12. ¿Cuál es la ventaja de tener un plan alternativo documentado?",
        "options": [
            "Aumentar el caos",
            "Saber qué hacer si el plan principal falla",
            "Evitar que la gente se comunique",
            "Impedir reportes"
        ],
        "correct_index": 1,
        "domain": "PL"
    },

    # --- Ciclo 13 ---
    {
        "text": "RL13. 'Ningún trabajador sin acreditación puede entrar al área restringida'. Viste a alguien sin acreditación dentro. ¿Qué conclusión es más lógica?",
        "options": [
            "Esa persona sí tenía acreditación válida",
            "Se violó la norma de acceso",
            "Nadie controla accesos",
            "No existe área restringida"
        ],
        "correct_index": 1,
        "domain": "RL"
    },
    {
        "text": "CN13. Una tasa de error baja pero constante puede, con el tiempo:",
        "options": [
            "Acumular problemas serios si no se corrige",
            "Desaparecer mágicamente sola",
            "Convertirse en perfección total",
            "Romper leyes físicas"
        ],
        "correct_index": 0,
        "domain": "CN"
    },
    {
        "text": "VB13. ¿Qué opción se acerca más a 'contingencia' en contexto laboral?",
        "options": [
            "Plan alternativo ante una posible falla",
            "Reunión social sin objetivo",
            "Descanso obligatorio",
            "Instrucción sin sentido"
        ],
        "correct_index": 0,
        "domain": "VB"
    },
    {
        "text": "MA13. Regla mental: 'Cuando escuches DOBLE CHEQUEO, repite revisión completa desde cero'. ¿Para qué sirve eso?",
        "options": [
            "Para ignorar fallas",
            "Para asegurar que no se pasó por alto nada crítico",
            "Para perder el tiempo",
            "Para no reportar errores"
        ],
        "correct_index": 1,
        "domain": "MA"
    },
    {
        "text": "PL13. Tienes que reasignar recursos ante una falla mayor inesperada. ¿Qué priorizas primero?",
        "options": [
            "Impacto en seguridad y operación crítica",
            "Popularidad del área",
            "Antigüedad del empleado",
            "Quién se queja más fuerte"
        ],
        "correct_index": 0,
        "domain": "PL"
    },

    # --- Ciclo 14 (más complejo / abstracto) ---
    {
        "text": "RL14. 'Si A implica B y B implica C, entonces A implica C'. ¿Qué tipo de razonamiento es ese?",
        "options": [
            "Asociación emocional",
            "Cadena lógica transitiva",
            "Reacción impulsiva",
            "Memoria accidental"
        ],
        "correct_index": 1,
        "domain": "RL"
    },
    {
        "text": "CN14. Si un evento tiene probabilidad baja pero consecuencias críticas, ¿qué política de control suele ser más racional?",
        "options": [
            "Ignorarlo porque es improbable",
            "Planificar mitigaciones porque el daño potencial es alto",
            "Decir que jamás ocurrirá",
            "No documentarlo"
        ],
        "correct_index": 1,
        "domain": "CN"
    },
    {
        "text": "VB14. ¿Cuál opción describe mejor 'coherencia interna' en un informe?",
        "options": [
            "Que las partes no se contradigan entre sí",
            "Que cada párrafo tenga chistes",
            "Que sea muy largo",
            "Que tenga colores llamativos"
        ],
        "correct_index": 0,
        "domain": "VB"
    },
    {
        "text": "MA14. Te dan tres reglas verbales distintas, y debes recordar cuál se aplica a cuál área sin mezclarlas. ¿Qué habilidad estás usando principalmente?",
        "options": [
            "Actualización de memoria de trabajo",
            "Fuerza física",
            "Reflejos musculares",
            "Afinidad social"
        ],
        "correct_index": 0,
        "domain": "MA"
    },
    {
        "text": "PL14. La operación se detiene si no se cumple un estándar de seguridad mínimo. ¿Por qué detener todo aunque sea costoso?",
        "options": [
            "Para demostrar autoridad sin razón",
            "Para proteger vida y activos críticos antes que la productividad inmediata",
            "Para castigar al equipo",
            "Para evitar auditorías futuras"
        ],
        "correct_index": 1,
        "domain": "PL"
    },
]

TOTAL_QUESTIONS = len(QUESTIONS)  # Debe ser 70


# ===========================
# ESTADO GLOBAL
# ===========================
if "stage" not in st.session_state:
    st.session_state.stage = "info"  # info -> test -> done

if "candidate_name" not in st.session_state:
    st.session_state["candidate_name"] = ""

if "evaluator_name" not in st.session_state:
    st.session_state["evaluator_name"] = ""

if "current_q" not in st.session_state:
    st.session_state["current_q"] = 0

if "answers" not in st.session_state:
    # answers[i] = indice opción elegida (0..3) o None
    st.session_state["answers"] = {i: None for i in range(TOTAL_QUESTIONS)}

if "test_start_time" not in st.session_state:
    st.session_state["test_start_time"] = None  # se setea al entrar a "test"

if "finished_due_to_focus" not in st.session_state:
    st.session_state["finished_due_to_focus"] = False

if "done_scoring" not in st.session_state:
    st.session_state["done_scoring"] = None  # guardará dict con resultados al final


# ===========================
# LÓGICA DE CONTROL DE TIEMPO Y FOCO
# ===========================

def test_time_expired():
    """True si pasaron más de TEST_LIMIT_MINUTES desde el inicio."""
    if st.session_state.test_start_time is None:
        return False
    elapsed = datetime.now() - st.session_state.test_start_time
    return elapsed > timedelta(minutes=TEST_LIMIT_MINUTES)

def forfeit_detected():
    """
    Detecta si la URL tiene ?forfeit=1 (es decir, el candidato cambió de pestaña/ventana).
    Usamos st.experimental_get_query_params().
    """
    params = st.experimental_get_query_params()
    return params.get("forfeit", ["0"])[0] == "1"

# ===========================
# SCORING
# ===========================

def compute_results():
    """
    Calcula:
    - Cantidad de correctas total
    - % global de acierto
    - Por dominio: correctas, %, nivel
    - Texto de resumen
    """
    domains = ["RL","CN","VB","MA","PL"]
    domain_names = {
        "RL": "Razonamiento Lógico",
        "CN": "Razonamiento Cuantitativo / Numérico",
        "VB": "Comprensión Verbal / Conceptual",
        "MA": "Memoria de Trabajo / Atención",
        "PL": "Planeamiento / Resolución Práctica"
    }

    # conteo total
    total_correct = 0
    domain_counts = {d: {"correct":0, "total":0} for d in domains}

    for i,q in enumerate(QUESTIONS):
        dom = q["domain"]
        domain_counts[dom]["total"] += 1
        ans = st.session_state.answers.get(i, None)
        if ans is not None and ans == q["correct_index"]:
            total_correct += 1
            domain_counts[dom]["correct"] += 1

    global_pct = (total_correct / TOTAL_QUESTIONS)*100.0

    def classify(pct):
        if pct >= 70:
            return "Alto"
        elif pct >= 40:
            return "Promedio"
        else:
            return "Bajo"

    domain_scores = {}
    for d in domains:
        corr = domain_counts[d]["correct"]
        tot  = domain_counts[d]["total"]
        pct  = (corr/tot)*100.0 if tot>0 else 0.0
        domain_scores[d] = {
            "name": domain_names[d],
            "correct": corr,
            "total": tot,
            "pct": pct,
            "level": classify(pct)
        }

    overall_level = classify(global_pct)

    # construir textos dinámicos
    # Descripción general de desempeño cognitivo
    if overall_level == "Alto":
        overview = (
            "El rendimiento global sugiere alta rapidez analítica, buena retención "
            "de información bajo presión y capacidad para manejar relaciones lógicas complejas. "
            "Este perfil suele asociarse a una curva de aprendizaje acelerada y autonomía temprana."
        )
    elif overall_level == "Promedio":
        overview = (
            "El rendimiento global se ubica en un rango funcional, con capacidad de análisis "
            "razonable, comprensión verbal adecuada y manejo numérico suficiente para tareas "
            "estándar. Puede requerir apoyo puntual en escenarios de alta exigencia temporal."
        )
    else:
        overview = (
            "El resultado global indica que la persona podría requerir mayor acompañamiento en "
            "tareas que demanden análisis complejo bajo tiempo limitado, especialmente cuando "
            "se combinan interpretación lógica, cálculo mental y planificación simultánea."
        )

    # Fortaleza principal = dominio con mayor %; Área de apoyo = menor %
    best_dom  = max(domain_scores.keys(), key=lambda d: domain_scores[d]["pct"])
    worst_dom = min(domain_scores.keys(), key=lambda d: domain_scores[d]["pct"])

    strengths_text = (
        f"Fortaleza relativa en {domain_scores[best_dom]['name']} "
        f"(aciertos {domain_scores[best_dom]['correct']}/{domain_scores[best_dom]['total']}, "
        f"{domain_scores[best_dom]['pct']:.0f}%). "
        "Esto sugiere que en ese tipo de demanda cognitiva la persona procesa con mayor eficiencia."
    )

    watch_text = (
        f"Requiere apoyo relativo en {domain_scores[worst_dom]['name']} "
        f"(aciertos {domain_scores[worst_dom]['correct']}/{domain_scores[worst_dom]['total']}, "
        f"{domain_scores[worst_dom]['pct']:.0f}%). "
        "Esto podría notarse cuando la tarea exige ese tipo específico de razonamiento de manera sostenida."
    )

    # perfil comparativo corto
    profile_text = (
        f"Resultado global: {total_correct}/{TOTAL_QUESTIONS} correctas "
        f"({global_pct:.0f}%). Nivel global: {overall_level}. "
        "El puntaje refleja una estimación preliminar de capacidades cognitivas generales "
        "relacionadas con razonamiento lógico, cálculo mental, lenguaje, memoria activa "
        "y priorización operativa bajo presión de tiempo."
    )

    return {
        "total_correct": total_correct,
        "global_pct": global_pct,
        "overall_level": overall_level,
        "domain_scores": domain_scores,
        "overview": overview,
        "strengths_text": strengths_text,
        "watch_text": watch_text,
        "profile_text": profile_text
    }

# ===========================
# PDF BUILDER (1 PÁGINA, ESTILO FICHA)
# ===========================
def generate_pdf(candidate_name, evaluator_name, results_dict):
    """
    Layout final:
    - Encabezado (ancho completo)
    - Fila 1:
        Izquierda: Resumen Global (puntaje total, nivel)
        Derecha : Perfil comparativo (texto)
    - Fila 2:
        Tabla de Desempeño por Dimensión (5 dominios)
    - Fila 3:
        Cuadrícula 2 columnas:
          Fortalezas clave | Aspectos a observar
    - Nota final
    Todo en 1 hoja A4.
    """

    buf = BytesIO()
    W, H = A4  # (595 x 842 aprox)
    c = canvas.Canvas(buf, pagesize=A4)

    margin_left  = 36
    margin_right = 36
    page_width   = W - margin_left - margin_right

    y_cursor = H - 40

    # --- Encabezado ---
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.white)
    header_h = 40
    c.rect(margin_left, y_cursor-header_h, page_width, header_h, stroke=1, fill=1)

    c.setFont("Helvetica-Bold",10)
    c.setFillColor(colors.black)
    c.drawString(margin_left+10, y_cursor-16,
                 "Informe Cognitivo General (Screening)")
    c.setFont("Helvetica",7)
    c.drawString(margin_left+10, y_cursor-28,
                 "Evaluación de razonamiento, memoria operativa, comprensión verbal, cálculo y priorización.")

    right_info = f"Candidato: {candidate_name} | Evaluador: {evaluator_name} | Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    c.setFont("Helvetica",7)
    c.drawRightString(margin_left+page_width-10, y_cursor-16, right_info)

    y_cursor -= (header_h + 12)

    # --- Fila 1: dos columnas ---
    col_gap = 12
    col_w = (page_width - col_gap) / 2
    box_h = 110

    # Izquierda: Resumen Global
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.white)
    c.rect(margin_left, y_cursor-box_h, col_w, box_h, stroke=1, fill=1)

    # Título
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(margin_left+8, y_cursor-14, "Resumen global")

    # Puntaje global + nivel
    c.setFont("Helvetica",7)
    summary_line_1 = (
        f"Respuestas correctas: {results_dict['total_correct']}/{TOTAL_QUESTIONS}  "
        f"({results_dict['global_pct']:.0f}%)"
    )
    c.drawString(margin_left+8, y_cursor-28, summary_line_1)

    summary_line_2 = (
        f"Nivel estimado: {results_dict['overall_level']} "
        "(Bajo / Promedio / Alto)"
    )
    c.drawString(margin_left+8, y_cursor-40, summary_line_2)

    # Descripción general (overview)
    y_tmp = y_cursor-52
    y_tmp = _draw_par(
        c,
        results_dict["overview"],
        margin_left+8,
        y_tmp,
        col_w-16,
        font="Helvetica",
        size=7,
        leading=9,
        color=colors.black,
        max_lines=6
    )

    # Derecha: Perfil comparativo
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.white)
    c.rect(margin_left+col_w+col_gap, y_cursor-box_h, col_w, box_h, stroke=1, fill=1)

    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(margin_left+col_w+col_gap+8, y_cursor-14, "Perfil comparativo")

    y_tmp2 = y_cursor-28
    y_tmp2 = _draw_par(
        c,
        results_dict["profile_text"],
        margin_left+col_w+col_gap+8,
        y_tmp2,
        col_w-16,
        font="Helvetica",
        size=7,
        leading=9,
        color=colors.black,
        max_lines=8
    )

    y_cursor -= (box_h + 12)

    # --- Fila 2: Tabla de Desempeño por Dimensión (ancho completo)
    table_h = 130
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.white)
    c.rect(margin_left, y_cursor-table_h, page_width, table_h, stroke=1, fill=1)

    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(margin_left+8, y_cursor-14, "Desempeño por dimensión cognitiva")

    # Cabeceras de la tabla
    y_head = y_cursor-28
    c.setFont("Helvetica-Bold",7)
    c.drawString(margin_left+8,   y_head, "Dimensión")
    c.drawString(margin_left+190, y_head, "Aciertos / Total")
    c.drawString(margin_left+270, y_head, "Nivel")
    c.drawString(margin_left+320, y_head, "Descripción funcional")

    # Filas
    y_row = y_head-12
    row_leading = 24

    for dom_key in ["RL","CN","VB","MA","PL"]:
        ds = results_dict["domain_scores"][dom_key]

        # Descripción breve de cada dominio en contexto
        if dom_key == "RL":
            desc_text = "Uso de relaciones lógicas y consistencia de reglas."
        elif dom_key == "CN":
            desc_text = "Razonamiento numérico, proporciones y estimación."
        elif dom_key == "VB":
            desc_text = "Comprensión de significado, vocabulario y analogías."
        elif dom_key == "MA":
            desc_text = "Memoria de trabajo, retención y actualización mental."
        else:  # "PL"
            desc_text = "Priorización operativa y toma de decisión bajo presión."

        # Primera línea fija (nombre, score)
        c.setFont("Helvetica-Bold",7)
        c.drawString(margin_left+8, y_row, ds["name"])

        c.setFont("Helvetica",7)
        c.drawString(
            margin_left+190,
            y_row,
            f"{ds['correct']}/{ds['total']}"
        )
        c.drawString(
            margin_left+270,
            y_row,
            ds["level"]
        )

        # descripción envuelta en varias líneas
        y_row2 = _draw_par(
            c,
            desc_text,
            margin_left+320,
            y_row,
            page_width-320-8,
            font="Helvetica",
            size=7,
            leading=9,
            color=colors.black,
            max_lines=3
        )

        # bajar a la siguiente fila dejando aire
        y_row = min(y_row2, y_row-1) - (row_leading-12)

    y_cursor -= (table_h + 12)

    # --- Fila 3: Fortalezas / Aspectos a Observar (2 columnas)
    last_box_h = 110
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.white)
    c.rect(margin_left, y_cursor-last_box_h, col_w, last_box_h, stroke=1, fill=1)
    c.rect(margin_left+col_w+col_gap, y_cursor-last_box_h, col_w, last_box_h, stroke=1, fill=1)

    # Fortalezas
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(margin_left+8, y_cursor-14, "Fortalezas cognitivas observables")

    y_ft = y_cursor-28
    y_ft = _draw_par(
        c,
        "• " + results_dict["strengths_text"],
        margin_left+8,
        y_ft,
        col_w-16,
        font="Helvetica",
        size=7,
        leading=9,
        color=colors.black,
        max_lines=6
    )

    # Aspectos a monitorear
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(margin_left+col_w+col_gap+8, y_cursor-14, "Aspectos a observar / apoyo sugerido")

    y_obs = y_cursor-28
    y_obs = _draw_par(
        c,
        "• " + results_dict["watch_text"],
        margin_left+col_w+col_gap+8,
        y_obs,
        col_w-16,
        font="Helvetica",
        size=7,
        leading=9,
        color=colors.black,
        max_lines=6
    )

    y_cursor -= (last_box_h + 10)

    # Nota final (ancho completo)
    note_h = 60
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.white)
    c.rect(margin_left, y_cursor-note_h, page_width, note_h, stroke=1, fill=1)

    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(margin_left+8, y_cursor-14, "Nota metodológica")

    nota_final = (
        "Este informe describe patrones cognitivos funcionales observados en un contexto "
        "de selección. No es un diagnóstico clínico. Los resultados deben interpretarse "
        "junto con entrevista estructurada y verificación de experiencia técnica."
    )
    _draw_par(
        c,
        nota_final,
        margin_left+8,
        y_cursor-28,
        page_width-16,
        font="Helvetica",
        size=7,
        leading=9,
        color=colors.black,
        max_lines=5
    )

    # Footer pequeño
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawRightString(
        margin_left+page_width-8,
        30,
        "Uso interno RR.HH. · Evaluación Cognitiva General · No clínico"
    )

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


# ===========================
# CALLBACKS
# ===========================

def end_test_and_score(reason_focus=False):
    """
    Cierra el test, calcula resultados, pasa a stage 'done'.
    """
    if reason_focus:
        st.session_state.finished_due_to_focus = True
    results = compute_results()
    st.session_state.done_scoring = results
    st.session_state.stage = "done"


def choose_answer(option_index: int):
    """
    Se llama cuando el usuario marca una respuesta.
    Guarda respuesta, avanza o finaliza.
    También chequea timeout y pérdida de foco.
    """
    q_idx = st.session_state.current_q
    st.session_state.answers[q_idx] = option_index

    # Chequeo de foco
    if forfeit_detected():
        end_test_and_score(reason_focus=True)
        st.experimental_rerun()
        return

    # Chequeo de tiempo
    if test_time_expired():
        end_test_and_score(reason_focus=False)
        st.experimental_rerun()
        return

    # Avanzar a siguiente pregunta
    if q_idx < TOTAL_QUESTIONS - 1:
        st.session_state.current_q += 1
        st.experimental_rerun()
    else:
        end_test_and_score(reason_focus=False)
        st.experimental_rerun()


# ===========================
# VISTAS
# ===========================

def view_info():
    st.markdown(
        """
        <div style="
            background:#ffffff;
            border:1px solid #e2e8f0;
            border-radius:12px;
            padding:20px;
            box-shadow:0 12px 24px rgba(0,0,0,0.06);
        ">
            <h2 style="
                margin:0 0 8px 0;
                font-size:1.3rem;
                font-weight:700;
                color:#1e293b;
            ">Test Cognitivo General (70 ítems)</h2>
            <p style="margin:0; font-size:.9rem; color:#475569; line-height:1.4;">
                Este test mide razonamiento lógico, manejo numérico conceptual,
                comprensión verbal, memoria de trabajo / atención y priorización operativa.
                <br>
                Duración máxima: 20 minutos totales. Si cambias de pestaña o sales de la ventana,
                la evaluación se cierra automáticamente.
                <br>
                Selecciona sólo una alternativa por pregunta.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.session_state.candidate_name = st.text_input(
        "Nombre del evaluado / candidato",
        value=st.session_state.candidate_name,
        placeholder="Nombre completo"
    )
    st.session_state.evaluator_name = st.text_input(
        "Nombre del evaluador / área",
        value=st.session_state.evaluator_name,
        placeholder="Ej: RR.HH. Planta Norte"
    )

    ready = (
        len(st.session_state.candidate_name.strip()) > 0 and
        len(st.session_state.evaluator_name.strip()) > 0
    )

    if st.button("Iniciar evaluación", type="primary", disabled=not ready, use_container_width=True):
        st.session_state.stage = "test"
        st.session_state.current_q = 0
        st.session_state.answers = {i: None for i in range(TOTAL_QUESTIONS)}
        st.session_state.finished_due_to_focus = False
        st.session_state.done_scoring = None
        st.session_state.test_start_time = datetime.now()
        st.experimental_set_query_params()  # limpia ?forfeit
        st.experimental_rerun()


def view_test():
    # Bloque anti-trampa: script que marca ?forfeit=1 cuando la pestaña pierde foco
    st.markdown(
        """
        <script>
        (function(){
            function markForfeit(){
                const url = new URL(window.location.href);
                if(url.searchParams.get("forfeit") !== "1"){
                    url.searchParams.set("forfeit","1");
                    window.location.replace(url.toString());
                }
            }
            // usuario se va de la pestaña / pierde foco
            document.addEventListener("visibilitychange", function(){
                if (document.hidden){
                    markForfeit();
                }
            });
            window.addEventListener("blur", function(){
                markForfeit();
            });
        })();
        </script>
        """,
        unsafe_allow_html=True
    )

    # Check focus & timeout every render
    if forfeit_detected():
        end_test_and_score(reason_focus=True)
        st.experimental_rerun()
        return

    if test_time_expired():
        end_test_and_score(reason_focus=False)
        st.experimental_rerun()
        return

    q_idx = st.session_state.current_q
    q = QUESTIONS[q_idx]

    # Header de progreso
    progreso = (q_idx + 1) / TOTAL_QUESTIONS * 100

    st.markdown(
        f"""
        <div style="
            background:linear-gradient(to right,#1e40af,#4338ca);
            color:white;
            border-radius:12px 12px 0 0;
            padding:16px 20px;
            display:flex;
            justify-content:space-between;
            align-items:flex-start;
            flex-wrap:wrap;">
            <div style="font-weight:700; font-size:1rem; line-height:1.3;">
                Test Cognitivo General
                <div style="font-size:.8rem; font-weight:400; opacity:.8;">
                    Tiempo máximo total: {TEST_LIMIT_MINUTES} minutos
                </div>
            </div>
            <div style="
                background:rgba(255,255,255,0.25);
                padding:4px 10px;
                border-radius:999px;
                font-size:.8rem;
                text-align:center;
                line-height:1.2;
            ">
                Pregunta {q_idx+1} de {TOTAL_QUESTIONS}<br>{int(progreso)}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Tarjeta de pregunta
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
                margin:0 0 1rem 0;
                font-size:1.05rem;
                color:#1e293b;
                line-height:1.45;
                font-weight:500;
            ">
                {q["text"]}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Botones de respuesta
    for opt_i, opt_text in enumerate(q["options"]):
        st.button(
            opt_text,
            key=f"q{q_idx}_opt{opt_i}",
            use_container_width=True,
            on_click=choose_answer,
            args=(opt_i,)
        )

    # Mensaje de confidencialidad
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
            line-height:1.4;
        ">
            <b>Confidencialidad:</b> Uso interno de RR.HH. y evaluación cognitiva general.
            Cambiar de pestaña finaliza el test automáticamente.
        </div>
        """,
        unsafe_allow_html=True
    )


def view_done():
    results = st.session_state.done_scoring
    if not results:
        results = compute_results()
        st.session_state.done_scoring = results

    # Generar PDF con layout tipo ficha
    pdf_bytes = generate_pdf(
        candidate_name=st.session_state.candidate_name,
        evaluator_name=st.session_state.evaluator_name,
        results_dict=results
    )

    # Pantalla final
    st.markdown(
        """
        <div style="
            background:linear-gradient(to bottom right,#ecfdf5,#d1fae5);
            padding:28px;
            border-radius:14px;
            box-shadow:0 24px 48px rgba(0,0,0,0.08);
            text-align:center;
            margin-bottom:20px;
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
            <div style="color:#065f46; line-height:1.4;">
                El test ha sido cerrado. Puedes descargar el informe interno en PDF.
                <br>
                Nota: Esta medición no constituye diagnóstico clínico.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Mostrar resumen clave al evaluador (en pantalla)
    st.markdown(
        f"""
        <div style="
            background:#ffffff;
            border:1px solid #e2e8f0;
            border-radius:12px;
            padding:16px;
            box-shadow:0 12px 24px rgba(0,0,0,0.06);
            margin-bottom:16px;
            line-height:1.4;
            font-size:.9rem;
            color:#1e293b;
        ">
            <b>Correctas totales:</b> {results["total_correct"]}/{TOTAL_QUESTIONS}
            &nbsp; | &nbsp;
            <b>Nivel global:</b> {results["overall_level"]}
            <br><br>
            <b>Fortaleza relativa:</b> {results["strengths_text"]}<br>
            <b>Aspecto a observar:</b> {results["watch_text"]}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.download_button(
        "⬇️ Descargar Informe PDF",
        data=pdf_bytes,
        file_name="Informe_Cognitivo_General.pdf",
        mime="application/pdf",
        use_container_width=True,
        type="primary"
    )

    # Mensaje si terminó por cambiar de pestaña
    if st.session_state.finished_due_to_focus:
        st.warning(
            "El test se cerró automáticamente por pérdida de foco en la ventana "
            "(cambio de pestaña o ventana detectado)."
        )

    st.caption(
        "Uso interno RR.HH. · Evaluación Cognitiva General · No clínico"
    )


# ===========================
# FLUJO PRINCIPAL
# ===========================
if st.session_state.stage == "info":
    view_info()

elif st.session_state.stage == "test":
    # Si ya expiró el tiempo justo al volver a pintar:
    if test_time_expired() or forfeit_detected():
        end_test_and_score(reason_focus=forfeit_detected())
        st.experimental_rerun()
    else:
        view_test()

elif st.session_state.stage == "done":
    view_done()
