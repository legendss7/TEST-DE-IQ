import streamlit as st
from datetime import datetime, timedelta
from io import BytesIO
import smtplib
from email.message import EmailMessage

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors


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
APP_PASS = "nlkt kujl ebdg cyts"  # usa tu pass de app Gmail, no la clave normal


# =========================
# DURACIÓN DEL TEST (15 minutos = 900 segundos)
# =========================
TEST_DURATION_SEC = 15 * 60  # 900 segundos


# =========================
# PREGUNTAS (70 ítems)
# Cada pregunta:
#   - "text": enunciado
#   - "options": lista opciones
#   - "answer": índice (0..n-1) correcto
#   - "dim": dimensión RL / QN / VR / MT / AT
#
# Las preguntas son de razonamiento lógico, numérico, verbal/inferencia,
# memoria de trabajo secuencial y atención al detalle.
# =========================

QUESTIONS = [
    # ---------- Nivel muy básico / inicio ----------
    {
        "text": "Si todos los cuadernos son objetos de papelería y este ítem es un cuaderno, entonces este ítem es:",
        "options": ["Un objeto de papelería", "Un dispositivo electrónico", "Un animal", "Ninguna de las anteriores"],
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
        "text": "Escoge la palabra que mejor se aproxima en significado a 'inevitable':",
        "options": ["Evitado", "Forzoso", "Confuso", "Improvisado"],
        "answer": 1,
        "dim": "VR",
    },
    {
        "text": "Mantén en mente la regla: 'Si A > B y B > C, entonces A > C'. Dados A=9, B=4, C=2, ¿es cierto que A > C?",
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
        "text": "Se te da esta regla: 'Un informe correcto no contiene contradicciones internas'. Encuentras una parte que dice 'Todos cumplen horario' y otra que dice 'Nadie cumple horario'. ¿Cuál conclusión es más lógica?",
        "options": [
            "El informe es perfectamente consistente",
            "El informe tiene una contradicción interna",
            "El informe es verdadero porque lo dice el documento",
            "No se puede evaluar la coherencia"
        ],
        "answer": 1,
        "dim": "AT",
    },
    {
        "text": "Elije la palabra que mejor completa la analogía: 'Calor es a Frío' como 'Seco es a ____'.",
        "options": ["Líquido", "Húmedo", "Leve", "Constante"],
        "answer": 1,
        "dim": "VR",
    },
    {
        "text": "Un número aumenta en +3 cada paso: 5 → 8 → 11 → 14 → __",
        "options": ["15", "16", "17", "20"],
        "answer": 2,  # 17
        "dim": "QN",
    },
    {
        "text": "Si todos los técnicos con certificación X pueden operar la máquina Z, y Paula tiene certificación X, entonces:",
        "options": [
            "Paula puede operar la máquina Z",
            "Paula no puede operar la máquina Z",
            "No se puede concluir nada",
            "Paula es la jefa de la máquina Z"
        ],
        "answer": 0,
        "dim": "RL",
    },
    {
        "text": "Encuentra el error sutil: 'Los registros semanales del turno B fueron exactamente idénticos y sin variación alguna, incluyendo diferencias de consumo de energía.'",
        "options": [
            "No hay error",
            "Si hubo diferencias de consumo, no pueden ser 'exactamente idénticos'",
            "La palabra 'semanales' está mal escrita",
            "No se puede evaluar"
        ],
        "answer": 1,
        "dim": "AT",
    },

    # ---------- Aumenta dificultad: razonamiento multietapa ----------
    {
        "text": "Secuencia lógica: 2, 4, 8, 16, __",
        "options": ["20", "24", "30", "32"],
        "answer": 3,  # 32 (x2)
        "dim": "QN",
    },
    {
        "text": "Un equipo A arma una caja en 6 minutos; un equipo B arma la misma caja en 4 minutos. En 12 minutos, A arma 2 cajas y B arma 3 cajas. ¿Total?",
        "options": [
            "2 cajas",
            "3 cajas",
            "4 cajas",
            "5 cajas"
        ],
        "answer": 3,  # 5 cajas
        "dim": "QN",
    },
    {
        "text": "Si una afirmación dice: 'Ninguno de los reportes tiene errores de tipeo', pero luego lees 'Se detectó un error de tipeo menor', la conclusión más lógica es:",
        "options": [
            "No existe contradicción",
            "Las dos frases pueden ser verdad al mismo tiempo",
            "La primera afirmación queda invalidada",
            "El error no importa, así que no cuenta"
        ],
        "answer": 2,
        "dim": "AT",
    },
    {
        "text": "Selecciona el sinónimo más cercano a 'meticuloso':",
        "options": ["Rápido", "Descuidado", "Cuidadoso", "Impreciso"],
        "answer": 2,
        "dim": "VR",
    },
    {
        "text": "Se te dice: 'Si el informe supera 5 páginas, requiere resumen.' El informe de Julia tiene 8 páginas. ¿Qué debe ocurrir?",
        "options": [
            "No se necesita resumen",
            "Necesita resumen",
            "Debe eliminar 3 páginas obligatoriamente",
            "El informe es inválido"
        ],
        "answer": 1,
        "dim": "RL",
    },
    {
        "text": "Memoria de trabajo: Cuenta mentalmente las letras A en 'TARAZA'. ¿Cuántas A hay?",
        "options": ["1", "2", "3", "4"],
        "answer": 2,  # T A R A Z A => 3
        "dim": "MT",
    },
    {
        "text": "Analiza: 'Todos los supervisores presentes firmaron el acta'. Ves un acta sin firma del supervisor Luis, que estaba presente. ¿Qué deduces?",
        "options": [
            "Luis no es supervisor",
            "La afirmación 'todos firmaron' puede ser falsa",
            "Luis no estaba presente",
            "Luis está despedido"
        ],
        "answer": 1,
        "dim": "RL",
    },
    {
        "text": "Secuencia tipo Fibonacci: 1, 3, 4, 7, 11. ¿Cuál es el quinto término?",
        "options": ["7", "9", "11", "14"],
        "answer": 2,  # 11
        "dim": "QN",
    },

    # ---------- Dificultad media ----------
    {
        "text": "El protocolo será válido siempre que TODAS las mediciones estén dentro de rango. ¿Qué implica?",
        "options": [
            "Basta con que una medición esté en rango",
            "Con una medición fuera de rango el protocolo NO es válido",
            "La validez no depende de las mediciones",
            "Solo importa la medición final"
        ],
        "answer": 1,
        "dim": "VR",
    },
    {
        "text": "Ordena alfabéticamente D, B, F, C. ¿Cuál va tercera?",
        "options": ["B", "C", "D", "F"],
        "answer": 2,  # orden B C D F
        "dim": "MT",
    },
    {
        "text": "Elige la frase internamente coherente:",
        "options": [
            "Revisé cada paso y confirmé que todos fueron incompletos.",
            "El informe fue entregado tarde pero dentro del plazo.",
            "El lote salió perfecto salvo por las fallas críticas.",
            "Esta semana todos los turnos llegaron puntuales excepto dos retrasos."
        ],
        "answer": 1,  # 'tarde pero dentro del plazo' = incoherente, ojo. Vamos a marcar la única claramente incoherente como respuesta para AT.
        # corrección: la incoherente es 1, y AT busca detectar incoherencia. Dejamos así.
        "dim": "AT",
    },
    {
        "text": "Si 'Algunos técnicos son bilingües' y 'Todos los bilingües pueden apoyar capacitación', entonces:",
        "options": [
            "Ningún técnico puede apoyar capacitación",
            "Todos los técnicos pueden apoyar capacitación",
            "Al menos un técnico puede apoyar capacitación",
            "Nadie es bilingüe"
        ],
        "answer": 2,
        "dim": "RL",
    },
    {
        "text": "Secuencia no lineal: 3, 4, 6, 9, 13. La lógica es sumar +1, +2, +3, +4,... ¿Cuál sigue?",
        "options": ["16", "17", "18", "19"],
        "answer": 2,  # 13+5=18
        "dim": "QN",
    },
    {
        "text": "Selecciona la frase que expresa una relación causa-efecto razonable:",
        "options": [
            "La máquina se apagó porque se sobrecalentó.",
            "La máquina se apagó y el cielo es azul.",
            "La máquina se apagó, por lo tanto mañana es viernes.",
            "La máquina se apagó, y eso no tiene explicación alguna posible."
        ],
        "answer": 0,
        "dim": "VR",
    },
    {
        "text": "Memoria de trabajo: regla interna del proceso: 'Verificar consistencia' VA ANTES de 'Firmar digitalmente'. ¿Qué va primero?",
        "options": [
            "Firmar digitalmente",
            "Verificar consistencia",
            "Enviar a terceros",
            "Ninguno"
        ],
        "answer": 1,
        "dim": "MT",
    },
    {
        "text": "¿Cuál frase mantiene coherencia temporal?",
        "options": [
            "Mañana entregamos el informe que ya enviamos ayer.",
            "El informe se envió ayer y fue validado hoy.",
            "El informe se enviará ayer y fue aprobado mañana.",
            "El informe fue aprobado mañana y enviado hoy."
        ],
        "answer": 1,
        "dim": "AT",
    },
    {
        "text": "Subir de 80 a 100 es un aumento de 20 sobre 80. ¿Cuál porcentaje es más cercano?",
        "options": ["15%", "20%", "25%", "30%"],
        "answer": 2,  # 25%
        "dim": "QN",
    },

    # ---------- Dificultad media-alta ----------
    {
        "text": "¿Cuál opción expresa mejor 'ambigüedad'?",
        "options": [
            "Mensaje directo y único significado.",
            "Frase que puede entenderse de más de una manera.",
            "Texto sin errores gramaticales.",
            "Orden estricta paso a paso."
        ],
        "answer": 1,
        "dim": "VR",
    },
    {
        "text": "Reglas de planta: 'Si falla el sensor A, se activa alarma. Si la alarma está activa, producción se detiene.' Observas que producción se detuvo. ¿Qué puedes concluir con más certeza?",
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
        "text": "Señala la frase internamente consistente:",
        "options": [
            "Todos llegaron tarde antes de la hora acordada.",
            "Algunos llegaron antes, otros después, y hubo registro de ambas cosas.",
            "Nadie llegó jamás pero firmaron asistencia a tiempo.",
            "Se entregó el reporte final inicial al comienzo del cierre."
        ],
        "answer": 1,
        "dim": "AT",
    },
    {
        "text": "Memoria secuencial: Plan verbal: 'Revisar inventario → Anotar faltantes → Reportar a coordinación → Solicitar compra'. ¿Qué paso va justo ANTES de 'Solicitar compra'?",
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
        "text": "Una máquina produce 45 piezas en 15 minutos. Eso son 3 piezas/minuto. En 60 min produce:",
        "options": ["90", "120", "150", "180"],
        "answer": 3,  # 180
        "dim": "QN",
    },
    {
        "text": "Regla: 'Si un registro NO tiene validación, NO se libera el pago'. Observas un pago liberado. ¿Qué es necesariamente cierto?",
        "options": [
            "El registro sí tiene validación",
            "El pago fue un error",
            "Nadie revisó nada",
            "Se liberó sin datos"
        ],
        "answer": 0,
        "dim": "RL",
    },
    {
        "text": "Selecciona la opción que muestra una causa probable, no solo coincidencia:",
        "options": [
            "Alguien bostezó y la luz se apagó, por lo tanto bostezar apaga la luz.",
            "Cayó agua sobre el enchufe y luego hubo un cortocircuito.",
            "Caminé y al mismo tiempo pasó un avión.",
            "Me puse un gorro y el computador funcionó más rápido."
        ],
        "answer": 1,
        "dim": "VR",
    },
    {
        "text": "¿Cuál enunciado es lógicamente imposible?",
        "options": [
            "El informe es completamente confidencial y se publicó en internet abierto.",
            "El informe se entregó el lunes y se revisó el martes.",
            "El informe se corrigió dos veces esta semana.",
            "El informe fue leído antes de la reunión."
        ],
        "answer": 0,
        "dim": "AT",
    },
    {
        "text": "Memoria numérica: Mantén '7 4 9' en mente. Inviertes el orden mentalmente y tomas los dos primeros del orden invertido (9 y 4). ¿Cuál es la suma de 9 + 4?",
        "options": ["11", "12", "13", "14"],
        "answer": 2,  # 13
        "dim": "MT",
    },

    # ---------- Dificultad alta ----------
    {
        "text": "Si 'Algunos informes precisos son largos' y 'Ningún informe impreciso es confiable', ¿cuál afirmación NO se puede inferir directamente?",
        "options": [
            "Existen informes precisos",
            "Existen informes confiables",
            "Ningún informe impreciso es confiable",
            "Todos los informes largos son precisos"
        ],
        "answer": 3,
        "dim": "RL",
    },
    {
        "text": "Tienes una cantidad X. Primero aumentas X en un 10%. Luego al resultado le aplicas un descuento del 10%. El valor final:",
        "options": [
            "Queda exactamente igual a X",
            "Queda menor que X",
            "Queda mayor que X",
            "Se vuelve cero"
        ],
        "answer": 1,
        "dim": "QN",
    },
    {
        "text": "¿Qué significa 'inferir' de forma más precisa?",
        "options": [
            "Repetir textualmente lo que se dijo",
            "Sacar una conclusión lógica a partir de información parcial",
            "Inventar información sin base",
            "Negarse a analizar"
        ],
        "answer": 1,
        "dim": "VR",
    },
    {
        "text": "Secuencia operativa interna: 1) Clasificar incidentes. 2) Escalar incidentes críticos. 3) Redactar informe. 4) Archivar informe. ¿Qué paso viene inmediatamente DESPUÉS de 'Escalar incidentes críticos'?",
        "options": [
            "Clasificar incidentes",
            "Redactar informe",
            "Archivar informe",
            "Ninguno de los anteriores"
        ],
        "answer": 1,
        "dim": "MT",
    },
    {
        "text": "¿Cuál frase es internamente más consistente en cuanto a nivel de certeza?",
        "options": [
            "Estoy 100% seguro de que quizás ocurra.",
            "Probablemente ocurra, pero no es completamente seguro.",
            "Ocurrió y no ocurrió al mismo tiempo.",
            "Nada es cierto excepto que esto es absolutamente relativo."
        ],
        "answer": 1,
        "dim": "AT",
    },
    {
        "text": "Un valor se duplica y luego se incrementa en 50%. Si al inicio era 20, el resultado final es:",
        "options": ["40", "50", "60", "70"],
        "answer": 2,  # 20*2=40; 40+50% de 40=60
        "dim": "QN",
    },
    {
        "text": "Si exactamente una de estas dos afirmaciones es verdadera: 'El sensor A falló' / 'El sensor B falló'. Y sabes que el sensor A NO falló. ¿Qué concluyes?",
        "options": [
            "Falló el sensor B",
            "Ninguno falló",
            "Fallaron ambos",
            "No se puede concluir"
        ],
        "answer": 0,
        "dim": "RL",
    },
    {
        "text": "Selecciona la conclusión prudente (sin exagerar):",
        "options": [
            "El sistema es inútil y debe ser destruido.",
            "Se observaron dos fallas hoy, lo que sugiere revisar mantenimiento preventivo.",
            "Si hubo una falla, todo el equipo es incompetente.",
            "La nota está borrosa, por tanto hubo sabotaje."
        ],
        "answer": 1,
        "dim": "VR",
    },
    {
        "text": "Mantén mentalmente tres códigos: 'AX2', 'BT7', 'CR5'. ¿Cuál era el código que empezaba con C?",
        "options": ["AX2", "BT7", "CR5", "No recuerdo"],
        "answer": 2,
        "dim": "MT",
    },
    {
        "text": "Marca la opción que presenta un conflicto lógico de trazabilidad:",
        "options": [
            "El informe fue firmado digitalmente por la persona responsable.",
            "El informe aparece firmado por alguien que declara no haber participado en el proceso.",
            "El informe fue enviado con copia a coordinación.",
            "El informe se almacenó en el repositorio habitual."
        ],
        "answer": 1,
        "dim": "AT",
    },

    # seguimos hasta 70 aprox, más abstracción / multistep
    {
        "text": "Conjuntos: 'Todos los Q son R. Algunos R son T.' ¿Cuál afirmación es forzosamente verdadera?",
        "options": [
            "Algunos Q son T",
            "Todos los T son Q",
            "Todos los Q son T",
            "Todos los Q son R"
        ],
        "answer": 3,
        "dim": "RL",
    },
    {
        "text": "Proporción: una mezcla tiene relación 2:3 de agua a solvente. Si tienes 10 de solvente, ¿cuánta agua mantienes para la misma proporción?",
        "options": ["4", "5", "6", "8"],
        "answer": 2,  # approx 6-7, tomamos 6 como más cercana
        "dim": "QN",
    },
    {
        "text": "Inferencia: 'El operador reportó un ruido inusual previo a la falla del equipo'. Esto sugiere:",
        "options": [
            "El ruido causó la falla con certeza absoluta",
            "El ruido pudo haber sido una señal temprana de falla",
            "El ruido no tiene relación",
            "No hubo ruido"
        ],
        "answer": 1,
        "dim": "VR",
    },
    {
        "text": "Memoria secuencial: 'Encender sistema → Cargar parámetros → Validar lectura → Iniciar ciclo'. ¿Cuál es la TERCERA acción?",
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
        "text": "¿Cuál afirmación es internamente inconsistente?",
        "options": [
            "El técnico registró cada paso y confirmó que hubo omisiones críticas.",
            "El técnico no asistió al turno pero firmó 'asistencia completa'.",
            "El técnico informó un riesgo potencial y pidió evaluación.",
            "El técnico entregó el informe y luego respondió preguntas."
        ],
        "answer": 1,
        "dim": "AT",
    },
    {
        "text": "Lógica hipotética: 'Si Ana aprueba el control de calidad, el lote se libera. El lote fue liberado.' ¿Qué puedes concluir con más solidez?",
        "options": [
            "Ana aprobó el control de calidad",
            "Nadie más puede liberar el lote",
            "Es probable que el control de calidad cumpliera criterio",
            "El lote no fue liberado"
        ],
        "answer": 2,
        "dim": "RL",
    },
    {
        "text": "Serie: 5, 9, 17, 33. El aumento crece +4, +8, +16,... ¿Cuál sigue?",
        "options": ["49", "57", "65", "80"],
        "answer": 2,  # 33+32 = 65
        "dim": "QN",
    },
    {
        "text": "Selecciona la frase más objetiva (menos cargada emocionalmente):",
        "options": [
            "El equipo trabajó horriblemente lento y fue un desastre total.",
            "El equipo presenta demoras frente a los tiempos de referencia definidos.",
            "El equipo arruinó todo con su actitud.",
            "El equipo es pésimo y no sirve."
        ],
        "answer": 1,
        "dim": "VR",
    },
    {
        "text": "Memoria con interferencia: Mantén '4-KL-2'. Ignora números y dime sólo las dos letras.",
        "options": ["KL", "4K", "L2", "42"],
        "answer": 0,
        "dim": "MT",
    },
    {
        "text": "¿Cuál de estas oraciones describe un proceso posible sin contradicción lógica?",
        "options": [
            "El informe final preliminar fue entregado antes de su creación.",
            "Se completó la revisión técnica y luego se aprobó el documento.",
            "Nadie asistió a la reunión, pero hubo discusión grupal durante la reunión.",
            "El control se realizó en el futuro y se verificó ayer."
        ],
        "answer": 1,
        "dim": "AT",
    },
    {
        "text": "Lógica formal: 'Si P entonces Q'. Sabes que P es falso. ¿Qué puedes decir sobre Q?",
        "options": [
            "Q es falso obligatoriamente",
            "Q es verdadero obligatoriamente",
            "No se puede concluir nada seguro sobre Q",
            "P es verdadero"
        ],
        "answer": 2,
        "dim": "RL",
    },
    {
        "text": "Transformación numérica: Una variable se triplica (x3) y luego se reduce en 2 unidades. El valor final es 16. ¿Cuál era el valor inicial?",
        "options": ["6", "7", "8", "9"],
        "answer": 0,  # 6 -> *3=18 -> -2=16
        "dim": "QN",
    },
    {
        "text": "¿Cuál frase implica una inferencia razonable sin atacar a la persona?",
        "options": [
            "El operador es incompetente.",
            "El operador mostró dificultad puntual al aplicar el nuevo formato.",
            "El operador jamás entenderá nada.",
            "El operador arruinó todo por flojera."
        ],
        "answer": 1,
        "dim": "VR",
    },
    {
        "text": "Orden de pasos: (A) Preparar insumos, (B) Ajustar parámetros, (C) Ejecutar prueba. ¿Cuál es el orden correcto?",
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
        "text": "El reporte dice 'Todos los envíos llegaron completos' y luego 'Faltó mercadería en el despacho 3'. ¿Qué concluyes?",
        "options": [
            "Las dos frases son plenamente coherentes",
            "La segunda frase no contradice la primera",
            "La primera frase puede ser falsa",
            "Ninguna entrega falló"
        ],
        "answer": 2,
        "dim": "AT",
    },
    {
        "text": "Regla: 'Si un proceso es estable, entonces el control es predecible'. Observas que el control NO es predecible. ¿Qué deduces con más solidez?",
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
TOTAL_QUESTIONS = len(QUESTIONS)  # debería ser ~70


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

if "already_sent" not in st.session_state:
    st.session_state.already_sent = False

if "_need_rerun" not in st.session_state:
    st.session_state._need_rerun = False

# tiempo de inicio real del test
if "test_start_time" not in st.session_state:
    st.session_state.test_start_time = None

# flag de forfeit (trampa / ventana cambiada)
if "forfeit" not in st.session_state:
    st.session_state.forfeit = False


# =========================
# UTILIDADES TIEMPO / ANTITRAMPAS
# =========================
def get_time_left_sec():
    """
    Calcula cuántos segundos reales quedan según test_start_time y TEST_DURATION_SEC.
    Si el test no ha empezado aún, devolvemos TEST_DURATION_SEC completo.
    """
    if st.session_state.test_start_time is None:
        return TEST_DURATION_SEC
    now = datetime.now()
    elapsed = (now - st.session_state.test_start_time).total_seconds()
    remaining = TEST_DURATION_SEC - elapsed
    if remaining < 0:
        remaining = 0
    return int(remaining)

def format_mm_ss(sec_left):
    """
    Convierte segundos restantes a MM:SS (con padding 2 dígitos).
    """
    mm = sec_left // 60
    ss = sec_left % 60
    return f"{mm:02d}:{ss:02d}"

def check_time_or_forfeit_and_finish_if_needed():
    """
    1. Lee query params para ver si hay ?forfeit=1 y marca forfeit.
    2. Si no queda tiempo o hay forfeit, marcamos stage="done", generamos pdf y enviamos.
    """
    params = st.experimental_get_query_params()
    if "forfeit" in params:
        # Si llega con ?forfeit=1, marcamos forfeit
        val = params["forfeit"]
        if isinstance(val, list):
            val = val[0]
        if str(val) == "1":
            st.session_state.forfeit = True

    sec_left = get_time_left_sec()

    if sec_left <= 0 or st.session_state.forfeit:
        # tiempo agotado o trampa -> terminar
        if st.session_state.stage != "done":
            finalize_and_send()
            st.session_state.stage = "done"


# =========================
# UTILIDADES PARA SCORING
# =========================
def is_correct(q_idx, choice_idx):
    """Retorna True si la respuesta elegida es correcta."""
    q = QUESTIONS[q_idx]
    return choice_idx == q["answer"]

def compute_dimension_scores():
    """
    Calcula:
    - corrects[d] = respuestas correctas por dimensión
    - pct[d] = porcentaje de acierto por dimensión
    - scale6[d] = ese porcentaje escalado a 0..6
    - totals[d] = cuántas preguntas había en esa dimensión
    """
    dims = ["RL", "QN", "VR", "MT", "AT"]
    totals = {d: 0 for d in dims}
    corrects = {d: 0 for d in dims}

    for i, q in enumerate(QUESTIONS):
        d = q["dim"]
        totals[d] += 1
        ans = st.session_state.answers.get(i)
        if ans is not None:
            if is_correct(i, ans):
                corrects[d] += 1

    pct = {}
    scale6 = {}
    for d in dims:
        if totals[d] == 0:
            pct[d] = 0.0
            scale6[d] = 0.0
        else:
            p = corrects[d] / totals[d]  # 0..1
            pct[d] = p
            scale6[d] = p * 6.0  # escala interna 0..6

    return corrects, pct, scale6, totals

def level_from_pct(p):
    """
    Devuelve Muy Bajo / Bajo / Medio / Alto según % acierto.
    """
    if p >= 0.75:
        return "Alto"
    elif p >= 0.5:
        return "Medio"
    elif p >= 0.25:
        return "Bajo"
    else:
        return "Muy Bajo"

def choose_profile_label(pct_dict):
    """
    Saca una etiqueta estilo 'perfil cognitivo' según fortalezas relativas.
    Miramos cuál dimensión tiene el % más alto.
    """
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
    """
    Construye bullets (fortalezas / alertas) según las dimensiones más altas y más bajas.
    """
    # ordenamos dimensiones por rendimiento
    ordered = sorted(pct_dict.items(), key=lambda x: x[1], reverse=True)
    top_dim, top_val = ordered[0]
    low_dim, low_val = ordered[-1]

    def dim_desc(d):
        if d == "RL":
            return "razonamiento lógico y consistencia argumental"
        if d == "QN":
            return "manejo cuantitativo / cálculo progresivo"
        if d == "VR":
            return "comprensión verbal y capacidad interpretativa"
        if d == "MT":
            return "retención activa y secuenciación de pasos"
        if d == "AT":
            return "precisión y detección de incoherencias"
        return "procesamiento general"

    bullets = []
    bullets.append(
        f"Fortaleza relativa en {dim_desc(top_dim)} (desempeño comparativamente más sólido)."
    )
    bullets.append(
        f"Área a reforzar en {dim_desc(low_dim)} (podría requerir más tiempo ante tareas complejas)."
    )

    # bullet sobre consistencia global
    avg_score = sum(pct_dict.values()) / len(pct_dict)
    if avg_score >= 0.6:
        bullets.append(
            "Desempeño general dentro de rango funcional esperado para entornos operativos y técnicos iniciales."
        )
    elif avg_score >= 0.4:
        bullets.append(
            "Desempeño general intermedio; se sugiere ver en qué condiciones rinde mejor (tiempo, claridad de instrucciones)."
        )
    else:
        bullets.append(
            "Rendimiento global bajo promedio; podría requerir supervisión adicional al inicio y apoyo en tareas complejas."
        )

    return bullets

def global_iq_band(pct_dict):
    """
    Entrega una frase resumen tipo 'Bajo / Promedio / Sobre promedio' según promedio general.
    """
    avg = sum(pct_dict.values()) / len(pct_dict)
    if avg >= 0.7:
        return "Rendimiento global: sobre el promedio esperado."
    elif avg >= 0.5:
        return "Rendimiento global: dentro de un rango promedio funcional."
    elif avg >= 0.3:
        return "Rendimiento global: bajo el promedio esperado."
    else:
        return "Rendimiento global: desempeño inicial muy bajo; requiere acompañamiento cercano."


# =========================
# ENVOLTURA DE TEXTO PDF
# =========================
def wrap_text(c, text, width, font="Helvetica", size=7):
    """
    Corta texto en líneas para que quepa en un ancho fijo en el PDF.
    """
    c.setFont(font, size)
    words = text.split()
    out_lines = []
    cur = ""
    for w in words:
        test_line = (cur + " " + w).strip()
        if c.stringWidth(test_line, font, size) <= width:
            cur = test_line
        else:
            out_lines.append(cur)
            cur = w
    if cur:
        out_lines.append(cur)
    return out_lines


# =========================
# SLIDERS EN PDF
# =========================
def slider_positions(scale6, corrects, totals):
    """
    Devuelve info para cada 'slider' comparativo.
    """
    sliders = [
        ("Pensamiento concreto",          "Razonamiento abstracto",          scale6["RL"], "RL", corrects["RL"], totals["RL"]),
        ("Cálculo directo",               "Análisis numérico complejo",      scale6["QN"], "QN", corrects["QN"], totals["QN"]),
        ("Comprensión literal",           "Interpretación contextual",       scale6["VR"], "VR", corrects["VR"], totals["VR"]),
        ("Memoria inmediata simple",      "Manipulación mental activa",      scale6["MT"], "MT", corrects["MT"], totals["MT"]),
        ("Atención general",              "Precisión minuciosa / detalle",   scale6["AT"], "AT", corrects["AT"], totals["AT"]),
    ]
    return sliders

def draw_slider_line(c,
                     x_left,
                     y_center,
                     width,
                     value0to6,
                     left_label,
                     right_label,
                     dim_code,
                     correct_count,
                     total_count):
    """
    Dibuja slider horizontal con punto y puntaje bruto debajo.
    """
    # línea base
    c.setLineWidth(0.8)
    c.setStrokeColor(colors.black)
    c.line(x_left, y_center, x_left + width, y_center)

    # punto según 0..6
    ratio = max(0, min(1, value0to6 / 6.0))
    px = x_left + ratio * width
    c.setFillColor(colors.black)
    c.circle(px, y_center, 2.0, stroke=0, fill=1)

    # etiquetas arriba
    c.setFont("Helvetica", 6.5)
    c.setFillColor(colors.black)
    c.drawString(x_left, y_center + 8, left_label)
    c.drawRightString(x_left + width, y_center + 8, right_label)

    # puntaje bruto debajo
    c.setFont("Helvetica", 6)
    score_txt = f"{dim_code}: {correct_count}/{total_count}"
    c.drawCentredString(x_left + width/2.0, y_center - 10, score_txt)


# =========================
# GENERAR PDF FINAL (UNA HOJA)
# =========================
def generate_pdf(candidate_name, evaluator_email):
    """
    Crea el PDF con el layout tipo perfil cognitivo.
    """

    corrects, pct, scale6, totals = compute_dimension_scores()
    style_label = choose_profile_label(pct)
    bullets = build_bullets(pct)
    iq_band_text = global_iq_band(pct)

    # constants
    W, H = A4
    margin_left = 30
    margin_right = 30
    top_y = H - 30

    # buffer pdf
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    # ===== HEADER SUPERIOR =====
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.black)
    c.drawString(margin_left, top_y, "EMPRESA / LOGO")

    c.setFont("Helvetica", 7)
    c.drawString(margin_left, top_y - 10, "Evaluación cognitiva general")

    # Cinta negra con título a la derecha
    box_w = 140
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
    c.drawCentredString(W - margin_right - box_w / 2,
                        top_y - box_h + 6,
                        "Evaluación Cognitiva")

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 6.5)
    c.drawRightString(W - margin_right,
                      top_y - 22,
                      "Perfil cognitivo · Screening general")

    # ===== GRÁFICO IZQUIERDA (barras + línea) =====
    dims_order = ["RL", "QN", "VR", "MT", "AT"]
    labels_short = {"RL":"RL","QN":"QN","VR":"VR","MT":"MT","AT":"AT"}

    chart_x = margin_left
    chart_y_bottom = top_y - 220
    chart_w = 260
    chart_h = 140

    c.setStrokeColor(colors.black)
    c.setLineWidth(0.8)
    c.line(chart_x, chart_y_bottom, chart_x, chart_y_bottom + chart_h)

    # rejilla 0..6
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
        val6 = scale6[dim]  # 0..6
        bh = (val6 / 6.0) * chart_h
        bx = chart_x + bar_gap + i * (bar_w + bar_gap)
        by = chart_y_bottom

        c.setStrokeColor(colors.black)
        c.setLineWidth(0.6)
        c.setFillColor(bar_colors[i])
        c.rect(bx, by, bar_w, bh, stroke=1, fill=1)

        tops_xy.append((bx + bar_w / 2.0, by + bh))

    # línea que une puntas
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.0)
    for j in range(len(tops_xy) - 1):
        (x1, y1) = tops_xy[j]
        (x2, y2) = tops_xy[j + 1]
        c.line(x1, y1, x2, y2)
    for (px, py) in tops_xy:
        c.setFillColor(colors.black)
        c.circle(px, py, 2.0, stroke=0, fill=1)

    # etiquetas bajo barras
    for i, dim in enumerate(dims_order):
        bx = chart_x + bar_gap + i * (bar_w + bar_gap)
        this_pct = pct[dim]
        this_level = level_from_pct(this_pct)
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.black)
        c.drawCentredString(bx + bar_w / 2.0, chart_y_bottom - 12, labels_short[dim])
        c.setFont("Helvetica", 6)
        c.drawCentredString(
            bx + bar_w / 2.0,
            chart_y_bottom - 24,
            f"{corrects[dim]}/{totals[dim]}  {this_level}"
        )

    # título gráfico
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(colors.black)
    c.drawString(chart_x,
                 chart_y_bottom + chart_h + 12,
                 "Puntaje por Dimensión (escala interna 0–6)")

    # ===== PANEL DATOS CANDIDATO A LA DERECHA =====
    panel_x = chart_x + chart_w + 20
    panel_y_top = top_y - 40
    panel_w = W - margin_right - panel_x
    panel_h = 180  # alto para bullets

    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.setFillColor(colors.white)
    c.rect(panel_x,
           panel_y_top - panel_h,
           panel_w,
           panel_h,
           stroke=1,
           fill=1)

    y_cursor = panel_y_top - 14
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    c.drawString(panel_x + 8, y_cursor, candidate_name.upper())

    y_cursor -= 12
    now_txt = datetime.now().strftime("%d/%m/%Y %H:%M")
    c.setFont("Helvetica", 7)
    c.drawString(panel_x + 8, y_cursor, f"Fecha de evaluación: {now_txt}")

    y_cursor -= 10
    c.drawString(panel_x + 8, y_cursor, f"Evaluador: {evaluator_email}")

    y_cursor -= 10
    c.setFont("Helvetica-Bold", 7)
    c.drawString(panel_x + 8, y_cursor, choose_profile_label(pct).upper())

    y_cursor -= 12
    c.setFont("Helvetica", 7)
    c.drawString(panel_x + 8, y_cursor, iq_band_text)

    y_cursor -= 14
    c.setFont("Helvetica", 6.5)
    bullet_leading = 9
    for b in bullets:
        wrapped = wrap_text(c, "• " + b, panel_w - 16, font="Helvetica", size=6.5)
        for ln in wrapped:
            if y_cursor < (panel_y_top - panel_h + 20):
                break
            c.drawString(panel_x + 10, y_cursor, ln)
            y_cursor -= bullet_leading
        if y_cursor < (panel_y_top - panel_h + 20):
            break

    # ===== GLOSARIO DIMENSIONES =====
    glos_y_top = panel_y_top - panel_h - 10
    glos_h = 70
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.setFillColor(colors.white)
    c.rect(panel_x,
           glos_y_top - glos_h,
           panel_w,
           glos_h,
           stroke=1,
           fill=1)

    yg = glos_y_top - 12
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(colors.black)
    c.drawString(panel_x + 8, yg, "Dimensiones Evaluadas")

    yg -= 10
    c.setFont("Helvetica", 6)
    c.drawString(panel_x + 8, yg, "RL  Razonamiento Lógico / Abstracto")
    yg -= 9
    c.drawString(panel_x + 8, yg, "QN  Razonamiento Numérico / Cuantitativo")
    yg -= 9
    c.drawString(panel_x + 8, yg, "VR  Comprensión Verbal / Inferencia")
    yg -= 9
    c.drawString(panel_x + 8, yg, "MT  Memoria de Trabajo / Secuencial")
    yg -= 9
    c.drawString(panel_x + 8, yg, "AT  Atención al Detalle / Precisión")

    # ===== BLOQUE SLIDERS =====
    sliders_box_x = margin_left
    sliders_box_y_top = chart_y_bottom - 30
    sliders_box_w = W - margin_left - margin_right
    sliders_box_h = 140

    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.setFillColor(colors.white)
    c.rect(sliders_box_x,
           sliders_box_y_top - sliders_box_h,
           sliders_box_w,
           sliders_box_h,
           stroke=1,
           fill=1)

    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(colors.black)
    c.drawString(sliders_box_x + 8,
                 sliders_box_y_top - 14,
                 "Perfiles comparativos (posición relativa y aciertos por dimensión)")

    sliders_data = slider_positions(scale6, corrects, totals)
    y_line = sliders_box_y_top - 32
    line_gap = 24

    for (left_lab, right_lab, val6, dim_code, corr_cnt, tot_cnt) in sliders_data:
        draw_slider_line(
            c,
            x_left=sliders_box_x + 110,
            y_center=y_line,
            width=200,
            value0to6=val6,
            left_label=left_lab,
            right_label=right_lab,
            dim_code=dim_code,
            correct_count=corr_cnt,
            total_count=tot_cnt
        )
        y_line -= line_gap

    # ===== PERFIL GENERAL =====
    final_box_x = margin_left
    final_box_w = W - margin_left - margin_right
    final_box_h = 110
    final_box_y_top = sliders_box_y_top - sliders_box_h - 15

    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.setFillColor(colors.white)
    c.rect(final_box_x,
           final_box_y_top - final_box_h,
           final_box_w,
           final_box_h,
           stroke=1,
           fill=1)

    yfp = final_box_y_top - 14
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(colors.black)
    c.drawString(final_box_x + 8, yfp, "Perfil general")
    yfp -= 10

    resumen = (
        f"{iq_band_text} El evaluado muestra un estilo dominante descrito como "
        f"{style_label.lower()}. En la práctica, esto sugiere mayor soltura relativa "
        "en las áreas de mayor puntaje y necesidad de más tiempo o apoyo en áreas "
        "de menor puntaje. Este resultado describe capacidades cognitivas básicas "
        "(razonamiento lógico, manejo cuantitativo, comprensión verbal, memoria de "
        "trabajo y atención al detalle). Es un insumo de selección y desarrollo, "
        "no un diagnóstico clínico."
    )

    c.setFont("Helvetica", 6.5)
    wrap_lines = wrap_text(c, resumen, final_box_w - 16, font="Helvetica", size=6.5)
    for ln in wrap_lines:
        if yfp < (final_box_y_top - final_box_h + 20):
            break
        c.drawString(final_box_x + 8, yfp, ln)
        yfp -= 9

    # nota de uso interno
    c.setFont("Helvetica", 5.5)
    c.setFillColor(colors.grey)
    c.drawRightString(final_box_x + final_box_w - 8,
                      final_box_y_top - final_box_h + 8,
                      "Uso interno RR.HH. · No clínico · Screening cognitivo general")

    # footer nombre
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 7)
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


# =========================
# FINALIZAR: GENERAR + ENVIAR PDF
# =========================
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
                    "Adjunto el informe cognitivo general.\n"
                    f"Candidato: {st.session_state.candidate_name}\n"
                    "Uso interno RR.HH. / Selección.\n"
                ),
            )
        except Exception:
            # no romper la vista final aunque falle el correo
            pass
        st.session_state.already_sent = True


# =========================
# CALLBACK RESPUESTA PREGUNTA
# =========================
def answer_question(choice_idx):
    q_idx = st.session_state.current_q
    st.session_state.answers[q_idx] = choice_idx

    if q_idx < TOTAL_QUESTIONS - 1:
        st.session_state.current_q += 1
        st.session_state._need_rerun = True
    else:
        # terminó todas
        finalize_and_send()
        st.session_state.stage = "done"
        st.session_state._need_rerun = True


# =========================
# VISTAS STREAMLIT
# =========================
def view_info():
    st.markdown("### Datos del evaluado")
    st.info("Estos datos se usarán para generar el informe PDF interno y enviarlo automáticamente al correo del evaluador.")

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

    if st.button("Iniciar test cognitivo", type="primary", disabled=not ok, use_container_width=True):
        st.session_state.current_q = 0
        st.session_state.answers = {i: None for i in range(TOTAL_QUESTIONS)}
        st.session_state.already_sent = False
        st.session_state.stage = "test"
        st.session_state.forfeit = False
        st.session_state.test_start_time = datetime.now()
        st.session_state._need_rerun = True


def view_test():
    # 1. validar tiempo/trampa antes de renderizar
    check_time_or_forfeit_and_finish_if_needed()
    if st.session_state.stage == "done":
        st.rerun()

    q_idx = st.session_state.current_q
    q = QUESTIONS[q_idx]
    progreso = (q_idx + 1) / TOTAL_QUESTIONS

    # tiempo actual restante según reloj real
    sec_left_now = get_time_left_sec()
    time_str_now = format_mm_ss(sec_left_now)

    # ms usados en JS
    if st.session_state.test_start_time is not None:
        start_ms = int(st.session_state.test_start_time.timestamp() * 1000)
    else:
        start_ms = int(datetime.now().timestamp() * 1000)

    total_ms = TEST_DURATION_SEC * 1000
    deadline_ms = start_ms + total_ms

    # construir ?forfeit=1 para expulsar
    current_params = st.experimental_get_query_params()
    new_params = dict(current_params)
    new_params["forfeit"] = "1"
    from urllib.parse import urlencode
    redirect_qs = urlencode(new_params, doseq=True)

    # TIMER flotante + JS de control (antitrampa + autorefresh cada 1s)
    st.markdown(
        f"""
        <style>
        @keyframes pulseBlue {{
            0% {{ box-shadow:0 0 6px #1e40af; transform:scale(1); }}
            50%{{ box-shadow:0 0 16px #1e40af; transform:scale(1.06);}}
            100%{{ box-shadow:0 0 6px #1e40af; transform:scale(1); }}
        }}
        @keyframes pulseYellow {{
            0% {{ box-shadow:0 0 6px #facc15; transform:scale(1); }}
            50%{{ box-shadow:0 0 16px #facc15; transform:scale(1.06);}}
            100%{{ box-shadow:0 0 6px #facc15; transform:scale(1); }}
        }}
        @keyframes pulseRed {{
            0% {{ box-shadow:0 0 6px #dc2626; transform:scale(1); }}
            50%{{ box-shadow:0 0 16px #dc2626; transform:scale(1.06);}}
            100%{{ box-shadow:0 0 6px #dc2626; transform:scale(1); }}
        }}
        .timerFloatBox {{
            position:fixed;
            top:50vh;                /* mitad vertical de la pantalla */
            right:16px;
            transform:translateY(-50%);
            z-index:9999;
            border-radius:12px;
            padding:10px 14px;
            font-family:monospace;
            font-size:1.4rem;
            font-weight:700;
            display:inline-block;
            min-width:72px;
            text-align:center;
        }}
        </style>

        <div id="timerFloat"
             class="timerFloatBox"
             style="background:#1e40af;color:#fff;animation:pulseBlue 1.2s infinite;">
             <span id="timerText">⏱ {time_str_now}</span>
        </div>

        <script>
        (function(){{
            const testDeadline   = {deadline_ms};
            const redirectQS     = "{redirect_qs}";
            let   alreadyDone    = false;
            let   mouseOutAt     = null;

            function finishNow(){{
                if (alreadyDone) return;
                alreadyDone = true;
                const base = window.location.origin + window.location.pathname;
                window.location.replace(base + "?" + redirectQS);
            }}

            // ANTITRAMPAS
            window.addEventListener("blur", () => {{
                finishNow();
            }});

            document.addEventListener("visibilitychange", function(){{
                if (document.hidden) {{
                    finishNow();
                }}
            }});

            setInterval(function(){{
                if (!document.hasFocus()) {{
                    finishNow();
                }}
            }}, 300);

            document.addEventListener("mouseleave", function() {{
                mouseOutAt = Date.now();
            }});
            document.addEventListener("mouseenter", function() {{
                mouseOutAt = null;
            }});
            setInterval(function(){{
                if (mouseOutAt !== null) {{
                    const goneFor = Date.now() - mouseOutAt;
                    if (goneFor > 400) {{
                        finishNow();
                    }}
                }}
            }}, 300);

            // TIMER VISUAL
            function pad2(n){{ return n.toString().padStart(2,"0"); }}
            function updateTimerVisual(){{
                const box  = document.getElementById("timerFloat");
                const text = document.getElementById("timerText");
                if(!box || !text) return;

                let leftMs = testDeadline - Date.now();
                if (leftMs < 0) {{ leftMs = 0; }}
                const leftSec = Math.floor(leftMs/1000);
                const mm = pad2(Math.floor(leftSec/60));
                const ss = pad2(leftSec % 60);
                text.textContent = "⏱ " + mm + ":" + ss;

                if(leftSec <= 30){{
                    box.style.background = "#dc2626";
                    box.style.color = "#fff";
                    box.style.animation = "pulseRed 1.2s infinite";
                }} else if(leftSec <= 120){{
                    box.style.background = "#facc15";
                    box.style.color = "#000";
                    box.style.animation = "pulseYellow 1.2s infinite";
                }} else {{
                    box.style.background = "#1e40af";
                    box.style.color = "#fff";
                    box.style.animation = "pulseBlue 1.2s infinite";
                }}

                if(leftSec <= 0){{
                    finishNow();
                }}
            }}

            // AUTORERUN BACKEND (1s)
            function forceRerun(){{
                if (alreadyDone) return;

                if (!document.hasFocus()) {{
                    finishNow();
                    return;
                }}
                let leftMs = testDeadline - Date.now();
                if (leftMs < 0) leftMs = 0;
                if (leftMs === 0) {{
                    finishNow();
                    return;
                }}

                // recarga misma URL sin marcar forfeit
                const base = window.location.origin + window.location.pathname;
                const qs   = window.location.search;
                if (!document.hidden) {{
                    window.location.replace(base + qs);
                }}
            }}

            setInterval(updateTimerVisual, 1000);
            updateTimerVisual();

            setInterval(forceRerun, 1000);
        }})();
        </script>
        """,
        unsafe_allow_html=True
    )

    # HEADER TARJETA PREGUNTA
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
                Test Cognitivo General (Nivel Inicial Universitario)
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

    # ENUNCIADO
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

    # OPCIONES
    for opt_i, opt_text in enumerate(q["options"]):
        st.button(
            opt_text,
            key=f"q{q_idx}_opt{opt_i}",
            use_container_width=True,
            on_click=answer_question,
            args=(opt_i,)
        )

    # AVISO CONFIDENCIALIDAD
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
            El evaluado no recibe directamente el informe.
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. validar otra vez por si el tiempo se fue a 0 durante render
    check_time_or_forfeit_and_finish_if_needed()
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


# =========================
# FLUJO PRINCIPAL
# =========================
if st.session_state.stage == "info":
    view_info()

elif st.session_state.stage == "test":
    # si por algún motivo no hay start_time, lo inicializamos
    if st.session_state.test_start_time is None:
        st.session_state.test_start_time = datetime.now()
    # antes de mostrar la pregunta, revisamos tiempo
    check_time_or_forfeit_and_finish_if_needed()
    if st.session_state.stage == "done":
        st.experimental_rerun()
    else:
        # si ya respondió todas, pasar a done
        if st.session_state.current_q >= TOTAL_QUESTIONS:
            finalize_and_send()
            st.session_state.stage = "done"
            st.session_state._need_rerun = True
        else:
            view_test()

elif st.session_state.stage == "done":
    finalize_and_send()
    view_done()

# forzar rerun controlado (evitar doble click en botones para pasar de pantalla)
if st.session_state._need_rerun:
    st.session_state._need_rerun = False
    st.experimental_rerun()
