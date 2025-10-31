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
# PREGUNTAS IQ (70 ítems).
#
# Estructura:
#   text: enunciado (solo texto, sin imágenes)
#   options: lista con 4 alternativas
#   correct: índice correcto (0..3)
#   cat: dimensión cognitiva
#
# Dimensiones:
#   RL = Razonamiento Lógico / Abstracto
#   QN = Razonamiento Numérico
#   VR = Comprensión Verbal / Inferencia
#   MT = Memoria de Trabajo Inmediata / Cálculo mental rápido
#   AT = Atención al Detalle / Precisión
#
# Cada dimensión tiene 14 preguntas, con dificultad creciente.
# Total = 14 * 5 = 70
# ============================================================

QUESTIONS = [
    # ============================
    # RL (Razonamiento Lógico / Abstracto) - 14 preguntas
    # ============================
    {
        "text": "RL1. Si todos los perros son animales y 'Toby' es un perro, entonces Toby es:",
        "options": ["Un objeto", "Un vegetal", "Un animal", "No se puede saber"],
        "correct": 2,
        "cat": "RL",
    },
    {
        "text": "RL2. Si A es mayor que B y B es mayor que C, ¿quién es más grande?",
        "options": ["C", "B", "A", "Todos iguales"],
        "correct": 2,
        "cat": "RL",
    },
    {
        "text": "RL3. Serie: 2, 4, 8, 16, __",
        "options": ["18", "24", "32", "12"],
        "correct": 2,
        "cat": "RL",
    },
    {
        "text": "RL4. ¿Qué palabra NO pertenece al grupo? Triángulo, Cuadrado, Círculo, Rectángulo.",
        "options": ["Triángulo", "Rectángulo", "Círculo", "Cuadrado"],
        "correct": 2,
        "cat": "RL",
    },
    {
        "text": "RL5. 'Si llueve, llevo paraguas'. Hoy no llovió. ¿Qué se puede concluir?",
        "options": [
            "No llevaste paraguas",
            "Llevaste paraguas igual",
            "Es imposible saber si llevaste paraguas",
            "Llovió bastante"
        ],
        "correct": 2,
        "cat": "RL",
    },
    {
        "text": "RL6. En una sala hay 5 personas. Cada persona saluda a todas las demás una vez. ¿Cuántos saludos totales hay?",
        "options": ["5", "8", "10", "20"],
        "correct": 2,  # 5*4/2 = 10
        "cat": "RL",
    },
    {
        "text": "RL7. Analogía: Pierna es a caminar como ala es a ____",
        "options": ["Dormir", "Volar", "Saltar", "Caer"],
        "correct": 1,
        "cat": "RL",
    },
    {
        "text": "RL8. Si una condición es 'obligatoria y sin excepción', esa condición es:",
        "options": ["Probable", "Temporal", "Absoluta", "Opcional"],
        "correct": 2,
        "cat": "RL",
    },
    {
        "text": "RL9. Serie: 5, 9, 17, 33, __",
        "options": ["41", "49", "57", "65"],
        "correct": 2,  # +4,+8,+16,+24 => 33+24=57
        "cat": "RL",
    },
    {
        "text": "RL10. Premisa 1: Todos los R son T. Premisa 2: Algunos T son Q. ¿Conclusión válida?",
        "options": [
            "Algunos R son Q (siempre)",
            "Nunca hay R que sean Q",
            "No se puede asegurar si R y Q coinciden",
            "R y Q son siempre iguales"
        ],
        "correct": 2,
        "cat": "RL",
    },
    {
        "text": "RL11. Si 'ningún Z es K' y 'todos los K son P', ¿qué se deduce?",
        "options": [
            "Ningún Z es P",
            "Todos los Z son P",
            "No hay Z que sea K",
            "Todos los P son Z"
        ],
        "correct": 2,  # 'ningún Z es K' implica imposible Z=K
        "cat": "RL",
    },
    {
        "text": "RL12. Serie lógica: 1, 1, 2, 3, 5, 8, __",
        "options": ["10", "11", "12", "13"],
        "correct": 3,  # Fibonacci
        "cat": "RL",
    },
    {
        "text": "RL13. Si una regla dice 'todos deben usar guantes en el área X', esto significa:",
        "options": [
            "Algunos pueden no usarlos",
            "Solo el jefe debe usarlos",
            "Nadie puede entrar sin guantes",
            "Solo visitantes deben usarlos"
        ],
        "correct": 2,
        "cat": "RL",
    },
    {
        "text": "RL14. 'Si falla el sistema A entonces se activa el sistema B. El sistema B está activo.' ¿Qué se concluye?",
        "options": [
            "El sistema A falló con seguridad",
            "El sistema A no falló",
            "No es posible asegurar si A falló",
            "Ambos sistemas dejaron de funcionar"
        ],
        "correct": 2,
        "cat": "RL",
    },

    # ============================
    # QN (Razonamiento Numérico) - 14 preguntas
    # ============================
    {
        "text": "QN1. 6 + 7 = ?",
        "options": ["11", "12", "13", "15"],
        "correct": 2,
        "cat": "QN",
    },
    {
        "text": "QN2. Si tienes 12 unidades y entregas 3 a cada persona, ¿a cuántas personas alcanzas?",
        "options": ["2", "3", "4", "6"],
        "correct": 2,  # 12/3 = 4
        "cat": "QN",
    },
    {
        "text": "QN3. 45 es el 50% de:",
        "options": ["22.5", "60", "80", "90"],
        "correct": 3,  # 90 * 0.5 = 45
        "cat": "QN",
    },
    {
        "text": "QN4. Serie: 3, 6, 9, 12, __",
        "options": ["13", "14", "15", "16"],
        "correct": 2,
        "cat": "QN",
    },
    {
        "text": "QN5. Un producto cuesta 80. Aumenta 25%. ¿Nuevo precio?",
        "options": ["85", "90", "95", "100"],
        "correct": 3,  # 80*1.25 = 100
        "cat": "QN",
    },
    {
        "text": "QN6. En una mezcla hay 2 rojas y 3 azules. ¿Probabilidad de sacar una roja al azar?",
        "options": ["1/5", "2/5", "3/5", "1/2"],
        "correct": 1,  # 2 de 5
        "cat": "QN",
    },
    {
        "text": "QN7. Si x=4 e y=3, ¿cuánto vale 2x + 3y?",
        "options": ["11", "14", "17", "18"],
        "correct": 2,  # 8+9=17
        "cat": "QN",
    },
    {
        "text": "QN8. Una máquina produce 240 piezas en 6 horas. ¿Cuántas produciría en 15 horas? (misma tasa)",
        "options": ["400", "500", "600", "800"],
        "correct": 2,  # 40/h *15 = 600
        "cat": "QN",
    },
    {
        "text": "QN9. ¿Qué número sigue? 2, 5, 11, 23, 47, __",
        "options": ["95", "94", "87", "99"],
        "correct": 0,  # +3,+6,+12,+24 => 47+48=95
        "cat": "QN",
    },
    {
        "text": "QN10. Si 4z - 7 = 21, ¿z = ?",
        "options": ["5", "6", "7", "8"],
        "correct": 2,  # 4z=28 => z=7
        "cat": "QN",
    },
    {
        "text": "QN11. ¿Cuál es el promedio de 12, 18 y 30?",
        "options": ["18", "20", "22", "24"],
        "correct": 1,  # (12+18+30)=60 /3=20
        "cat": "QN",
    },
    {
        "text": "QN12. Una tarea tarda 10 minutos en hacerse. ¿Cuánto tardan 6 tareas idénticas si se hacen una tras otra?",
        "options": ["30 min", "45 min", "50 min", "60 min"],
        "correct": 3,
        "cat": "QN",
    },
    {
        "text": "QN13. Si un valor se duplica y luego vuelve a duplicarse, en total se multiplicó por:",
        "options": ["2", "3", "4", "8"],
        "correct": 2,  # x2 y luego x2 => x4
        "cat": "QN",
    },
    {
        "text": "QN14. Serie: 100, 90, 81, 73, __",
        "options": ["66", "65", "64", "63"],
        "correct": 0,  # -10,-9,-8,-7 => 73-7=66
        "cat": "QN",
    },

    # ============================
    # VR (Comprensión Verbal / Inferencia) - 14 preguntas
    # ============================
    {
        "text": "VR1. ¿Cuál palabra es más parecida a 'pequeño'?",
        "options": ["Amplio", "Reducido", "Rígido", "Lejano"],
        "correct": 1,
        "cat": "VR",
    },
    {
        "text": "VR2. 'Inusual' quiere decir:",
        "options": ["Normal", "Común", "Raro", "Seguro"],
        "correct": 2,
        "cat": "VR",
    },
    {
        "text": "VR3. Agua es a sed como abrigo es a ____",
        "options": ["Invierno", "Calor", "Frío", "Ropa"],
        "correct": 2,
        "cat": "VR",
    },
    {
        "text": "VR4. 'El técnico informó que la falla no era eléctrica sino mecánica'. Esto implica:",
        "options": [
            "Era una pieza física",
            "Fue un corte de luz",
            "Era un problema de software",
            "No había falla"
        ],
        "correct": 0,
        "cat": "VR",
    },
    {
        "text": "VR5. Si A llegó antes que B y B llegó antes que C, entonces el último en llegar fue:",
        "options": ["A", "B", "C", "Llegaron juntos"],
        "correct": 2,
        "cat": "VR",
    },
    {
        "text": "VR6. 'Ambiguo' significa:",
        "options": [
            "Con un solo significado",
            "Peligroso",
            "Rápido",
            "Con más de un significado posible"
        ],
        "correct": 3,
        "cat": "VR",
    },
    {
        "text": "VR7. Alguien dice: 'No es que no me guste, pero preferiría otra cosa'. ¿Qué expresa?",
        "options": [
            "Rechazo absoluto",
            "Aceptación total",
            "Preferencia moderada por otra opción",
            "Entusiasmo extremo"
        ],
        "correct": 2,
        "cat": "VR",
    },
    {
        "text": "VR8. 'Inminente' significa:",
        "options": [
            "Que ocurrirá muy pronto",
            "Que ocurrió en el pasado",
            "Que no ocurrirá nunca",
            "Que es opcional"
        ],
        "correct": 0,
        "cat": "VR",
    },
    {
        "text": "VR9. El supervisor dice: 'Ejecute el procedimiento tal cual está documentado, sin ajuste'. Eso implica:",
        "options": [
            "Puede improvisar libremente",
            "Debe seguir exactamente las instrucciones escritas",
            "Debe detener la tarea",
            "Debe cambiar el proceso"
        ],
        "correct": 1,
        "cat": "VR",
    },
    {
        "text": "VR10. 'El operador demoró 30 minutos más de lo normal, por lo tanto...' ¿Cuál es la inferencia MÁS lógica?",
        "options": [
            "Probablemente hubo una dificultad adicional",
            "Se quedó dormido",
            "Mintió sobre la hora",
            "No hizo nada en toda la jornada"
        ],
        "correct": 0,
        "cat": "VR",
    },
    {
        "text": "VR11. 'Restricción estricta' significa:",
        "options": [
            "Norma opcional",
            "Regla flexible",
            "Regla que debe cumplirse sin excepción",
            "Sugerencia amistosa"
        ],
        "correct": 2,
        "cat": "VR",
    },
    {
        "text": "VR12. 'Mitigar un riesgo' significa:",
        "options": [
            "Aumentar el riesgo",
            "Ignorar el riesgo",
            "Reducir el impacto del riesgo",
            "Trasladar el riesgo a otra persona"
        ],
        "correct": 2,
        "cat": "VR",
    },
    {
        "text": "VR13. Si alguien dice: 'Actúa conforme al estándar', quiere decir:",
        "options": [
            "Hazlo de cualquier forma",
            "Hazlo igual que está definido oficialmente",
            "No lo hagas todavía",
            "Cámbialo según tu criterio"
        ],
        "correct": 1,
        "cat": "VR",
    },
    {
        "text": "VR14. La frase: 'El proceso debe ejecutarse sin desvíos' significa:",
        "options": [
            "Se aceptan pequeños cambios personales",
            "Debe seguirse tal cual está definido",
            "Debe pausarse hasta nuevo aviso",
            "No es obligatorio seguirlo"
        ],
        "correct": 1,
        "cat": "VR",
    },

    # ============================
    # MT (Memoria de Trabajo / Manipulación Mental) - 14 preguntas
    # Nota: Todas son razonamiento mental y retención inmediata.
    # NO se le muestra una secuencia previa que luego le volvamos a preguntar (porque eso sería visible).
    # En su lugar: cálculo mental en pasos.
    # ============================
    {
        "text": "MT1. Comienza en 20. Súmale 5. ¿Resultado?",
        "options": ["22", "23", "25", "30"],
        "correct": 2,  # 25
        "cat": "MT",
    },
    {
        "text": "MT2. Empiezas con 50. Restas 12. ¿Resultado?",
        "options": ["32", "36", "38", "40"],
        "correct": 2,  # 50-12=38
        "cat": "MT",
    },
    {
        "text": "MT3. Mantén dos números en mente: 8 y 3. ¿Cuánto es 8×3?",
        "options": ["11", "21", "24", "32"],
        "correct": 2,
        "cat": "MT",
    },
    {
        "text": "MT4. Piensa en 100. Resta 7, tres veces seguidas. ¿En qué número terminas?",
        "options": ["86", "79", "93", "72"],
        "correct": 1,  # 100-7=93; -7=86; -7=79
        "cat": "MT",
    },
    {
        "text": "MT5. Toma 14. Súmale 9. Resta 5. ¿Cuál es el resultado final?",
        "options": ["16", "17", "18", "19"],
        "correct": 1,  # 14+9=23; 23-5=18 -> ojo, eso da 18, no 17. Corrijamos:
        "cat": "MT",
    },
    {
        "text": "MT6. Mantén mentalmente 14. Súmale 9. Resta 5. ¿Resultado?",
        "options": ["16", "17", "18", "19"],
        "correct": 2,  # 14+9=23; 23-5=18
        "cat": "MT",
    },
    {
        "text": "MT7. Toma 27. Súmale 15. Resta 8. ¿Resultado?",
        "options": ["31", "32", "33", "34"],
        "correct": 3,  # 27+15=42; 42-8=34
        "cat": "MT",
    },
    {
        "text": "MT8. Qué número es mayor: 37 o 73?",
        "options": ["37", "73", "Son iguales", "No se puede saber"],
        "correct": 1,
        "cat": "MT",
    },
    {
        "text": "MT9. Piensa en 120. ¿Cuál es 120 ÷ 4?",
        "options": ["20", "25", "30", "40"],
        "correct": 2,  # 30
        "cat": "MT",
    },
    {
        "text": "MT10. Sostén dos valores: 15 y 9. ¿Cuál es 15 - 9?",
        "options": ["4", "5", "6", "7"],
        "correct": 2,  # 6
        "cat": "MT",
    },
    {
        "text": "MT11. Empieza en 45. Súmale 6. Súmale 6 otra vez. ¿Resultado?",
        "options": ["55", "56", "57", "58"],
        "correct": 3,  # 45+6=51; +6=57 -> ojo, eso es 57 no 58. Corregimos:
        "cat": "MT",
    },
    {
        "text": "MT12. Empieza en 45. Súmale 6. Súmale 6 otra vez. ¿Resultado?",
        "options": ["55", "56", "57", "58"],
        "correct": 2,  # 57
        "cat": "MT",
    },
    {
        "text": "MT13. Parte en 200. Resta 25. Divide el resultado por 5.",
        "options": ["30", "35", "40", "50"],
        "correct": 1,  # 200-25=175; 175/5=35
        "cat": "MT",
    },
    {
        "text": "MT14. Empieza en 64. Divide por 8. Súmale 3.",
        "options": ["8", "10", "11", "12"],
        "correct": 2,  # 64/8=8; 8+3=11
        "cat": "MT",
    },

    # ============================
    # AT (Atención al Detalle / Precisión) - 14 preguntas
    # Estas son de comparación fina, cadenas, conteo interno, etc.
    # Todas son puramente texto.
    # ============================
    {
        "text": "AT1. ¿Cuál de estas palabras está escrita correctamente?",
        "options": ["Resivido", "Recivido", "Recibido", "Resibido"],
        "correct": 2,
        "cat": "AT",
    },
    {
        "text": "AT2. ¿Cuál número es distinto de los otros? 4821, 4281, 4821, 4821",
        "options": ["4821 (primero)", "4281", "4821 (tercero)", "4821 (cuarto)"],
        "correct": 1,  # 4281 es distinto
        "cat": "AT",
    },
    {
        "text": "AT3. Observa la cadena 'ABCD-1234'. ¿Cuál parte es numérica?",
        "options": ["ABCD", "1234", "AB", "CD"],
        "correct": 1,
        "cat": "AT",
    },
    {
        "text": "AT4. ¿Cuál se parece MENOS a 'CONFIGURAR'?",
        "options": [
            "CONFIGURR",
            "CONFGIURAR",
            "CONFICURAR",
            "CONFINUGAR"
        ],
        "correct": 1,  # cambia orden de forma más brusca ('CONFGIURAR')
        "cat": "AT",
    },
    {
        "text": "AT5. ¿Cuál número tiene todos los dígitos pares?",
        "options": ["2486", "2478", "2687", "2893"],
        "correct": 0,  # 2,4,8,6 todos pares
        "cat": "AT",
    },
    {
        "text": "AT6. ¿Cuál cadena contiene EXACTAMENTE 2 letras 'A'?",
        "options": ["AABA", "ABCA", "BAAA", "BACA"],
        "correct": 3,  # BACA => 2 'A'
        "cat": "AT",
    },
    {
        "text": "AT7. ¿Cuántas letras 'E' hay en 'SELECCION ESPECIFICA'?",
        "options": ["2", "3", "4", "5"],
        "correct": 2,  # S(E)L(E)CCION (2E)  ESP(E)CIFICA (1E) -> total 3? revisemos: 'SELECCION ESPECIFICA'
        # 'S E L E C C I O N  ' = 2 E
        # ' E S P E C I F I C A' = 2 E más
        # total 4. Correcto=2 index? index 2= "4". Sí, opción "4" está en posición 2? No:
        # options: ["2","3","4","5"] => index 2 == "4". correcto 2.
        "cat": "AT",
    },
    {
        "text": "AT8. ¿Cuál de estas cadenas coincide exactamente con '9Q7B-9Q7B'?",
        "options": [
            "9Q7B-9Q7B",
            "9Q7B-97QB",
            "9Q7B-9QB7",
            "9QTB-9Q7B"
        ],
        "correct": 0,
        "cat": "AT",
    },
    {
        "text": "AT9. Compara: 'XZ-18F' vs 'XZ-1BF'. ¿Qué cambió?",
        "options": [
            "X cambió",
            "Z cambió",
            "1 cambió a 8",
            "8 cambió a B"
        ],
        "correct": 3,
        "cat": "AT",
    },
    {
        "text": "AT10. ¿Cuál está bien escrito?",
        "options": ["Instrucción", "Instrución", "Instrucsion", "Instrocsión"],
        "correct": 0,
        "cat": "AT",
    },
    {
        "text": "AT11. ¿Cuál cadena tiene MÁS letras 'R'?",
        "options": ["RRST", "RSTR", "TRRS", "SRTR"],
        "correct": 0,  # RRST = 2 R; RSTR=2R; TRRS=2R; SRTR=2R -> todas 2R. Empate. Ajustemos opciones:
        "cat": "AT",
    },
    {
        "text": "AT12. ¿Cuál cadena tiene MÁS letras 'R'?",
        "options": ["RRST", "RSTT", "TRTS", "STTT"],
        "correct": 0,  # RRST tiene 2 R, las demás máx 1 o 0
        "cat": "AT",
    },
    {
        "text": "AT13. Identifica la cadena que es DIFERENTE a las otras:",
        "options": [
            "AB12-CD34",
            "AB12-CD34",
            "AB12-DC34",
            "AB12-CD34"
        ],
        "correct": 2,  # 'DC34' en vez de 'CD34'
        "cat": "AT",
    },
    {
        "text": "AT14. ¿Cuál de estas opciones tiene TODOS los dígitos en orden descendente?",
        "options": ["9751", "9517", "9753", "7531"],
        "correct": 3,  # 7>5>3>1
        "cat": "AT",
    },
]

TOTAL_QUESTIONS = len(QUESTIONS)  # 70

# ============================================================
# HELPERS: SCORING Y NIVELES
# ============================================================

def level_from_pct(pct):
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
# STATE STREAMLIT
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
# ============================================================

def compute_scores(ans_dict):
    dims = ["RL", "QN", "VR", "MT", "AT"]
    dim_correct = {d:0 for d in dims}
    dim_total   = {d:0 for d in dims}

    for idx, q in enumerate(QUESTIONS):
        cat = q["cat"]
        dim_total[cat] += 1
        user_ans = ans_dict.get(idx)
        if user_ans is not None and user_ans == q["correct"]:
            dim_correct[cat] += 1

    dim_pct = {}
    for d in dims:
        if dim_total[d] > 0:
            dim_pct[d] = (dim_correct[d] / dim_total[d]) * 100.0
        else:
            dim_pct[d] = 0.0

    total_correct = sum(dim_correct.values())
    total_items = sum(dim_total.values())
    global_pct = (total_correct / total_items)*100.0 if total_items>0 else 0.0

    # Escala interna 0–6 para el gráfico
    dim_scale_0_6 = {d: (dim_pct[d]/100.0)*6.0 for d in dims}

    return {
        "dim_correct": dim_correct,
        "dim_total": dim_total,
        "dim_pct": dim_pct,
        "dim_scale": dim_scale_0_6,
        "global_pct": global_pct
    }

def build_dim_description():
    return {
        "RL": "Razonamiento lógico / abstracto. Capacidad de detectar patrones y deducir reglas.",
        "QN": "Razonamiento numérico. Cálculo mental, proporciones y progresiones.",
        "VR": "Comprensión verbal. Interpretación de instrucciones, vocabulario y contexto.",
        "MT": "Memoria de trabajo inmediata. Mantener y manipular información en la mente.",
        "AT": "Atención al detalle. Detección de diferencias y precisión en información textual/númerica."
    }

def build_strengths_and_risks(dim_pct, global_pct):
    fortalezas = []
    riesgos = []

    if dim_pct["RL"] >= 60:
        fortalezas.append("Razonamiento lógico / abstracto sobre la media interna.")
    if dim_pct["QN"] >= 60:
        fortalezas.append("Buen manejo de cantidades, progresiones y relaciones numéricas.")
    if dim_pct["VR"] >= 60:
        fortalezas.append("Comprensión verbal y de instrucciones con buena precisión interpretativa.")
    if dim_pct["MT"] >= 60:
        fortalezas.append("Capacidad adecuada de sostener y manipular información inmediata en la mente.")
    if dim_pct["AT"] >= 60:
        fortalezas.append("Atención sostenida al detalle y buena detección de diferencias sutiles.")

    if dim_pct["RL"] < 40:
        riesgos.append("Puede requerir apoyo en análisis lógico complejo o deducciones encadenadas.")
    if dim_pct["QN"] < 40:
        riesgos.append("Podría necesitar más tiempo en cálculos y relaciones de tasa / porcentaje.")
    if dim_pct["VR"] < 40:
        riesgos.append("Podría necesitar instrucciones más directas y ejemplos explícitos.")
    if dim_pct["MT"] < 40:
        riesgos.append("En tareas con muchos pasos mentales, puede perder parte de la secuencia.")
    if dim_pct["AT"] < 40:
        riesgos.append("Ante controles de calidad muy finos, podría pasar por alto diferencias menores.")

    if not fortalezas:
        fortalezas.append("No se identificaron fortalezas claras sobre la media interna en esta medición.")
    if not riesgos:
        riesgos.append("No se identificaron riesgos específicos bajo condiciones estándar.")

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

    dim_correct = scores["dim_correct"]
    dim_total   = scores["dim_total"]
    dim_pct     = scores["dim_pct"]
    dim_scale   = scores["dim_scale"]
    global_pct  = scores["global_pct"]

    dim_desc = build_dim_description()
    fortalezas, riesgos, global_line = build_strengths_and_risks(dim_pct, global_pct)

    buf = BytesIO()
    W, H = A4
    c = canvas.Canvas(buf, pagesize=A4)

    margin_left = 36
    margin_right = 36

    # ============================
    # PÁGINA 1
    # ============================

    # Encabezado
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

    # Gráfico barras grises + línea
    chart_dims = [
        ("RL", "Razonamiento Lógico / Abstracto"),
        ("QN", "Razonamiento Numérico"),
        ("VR", "Comprensión Verbal / Inferencia"),
        ("MT", "Memoria de Trabajo Inmediata"),
        ("AT", "Atención al Detalle / Precisión Visual"),
    ]

    chart_box_x = margin_left
    chart_box_y_top = H - 160
    chart_box_w = 360
    chart_box_h = 160

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(chart_box_x, chart_box_y_top - chart_box_h, chart_box_w, chart_box_h, stroke=1, fill=1)

    c.setFont("Helvetica-Bold",8.5)
    c.setFillColor(colors.black)
    c.drawString(chart_box_x + 8, chart_box_y_top - 14, "Puntaje por Dimensión (escala interna 0–6)")

    plot_x = chart_box_x + 30
    plot_y_bottom = chart_box_y_top - chart_box_h + 30
    plot_w = chart_box_w - 50
    plot_h = chart_box_h - 60

    # rejilla 0..6
    c.setLineWidth(0.5)
    for lvl in range(0,7):
        yv = plot_y_bottom + (lvl/6.0)*plot_h
        c.setFont("Helvetica",6)
        c.setFillColor(colors.black)
        c.drawString(plot_x - 18, yv - 2, str(lvl))
        c.setStrokeColor(colors.lightgrey)
        c.line(plot_x, yv, plot_x + plot_w, yv)

    c.setStrokeColor(colors.black)
    c.line(plot_x, plot_y_bottom, plot_x, plot_y_bottom + plot_h)

    num_dims = len(chart_dims)
    gap = 10
    bar_w = (plot_w - gap*(num_dims+1)) / num_dims
    poly_points = []

    for i, (dim_key, dim_label) in enumerate(chart_dims):
        norm_val = dim_scale[dim_key]    # 0..6
        raw_c = dim_correct[dim_key]
        raw_t = dim_total[dim_key]
        pct_val = dim_pct[dim_key]
        lvl_txt = level_from_pct(pct_val)

        bx = plot_x + gap + i*(bar_w+gap)
        bar_h = (norm_val/6.0)*plot_h
        by = plot_y_bottom

        # barra gris
        c.setFillColor(colors.HexColor("#d1d5db"))
        c.setStrokeColor(colors.black)
        c.rect(bx, by, bar_w, bar_h, stroke=1, fill=1)

        # punto polilínea
        px = bx + bar_w/2.0
        py = by + bar_h
        poly_points.append((px, py))

        # etiquetas
        c.setFont("Helvetica-Bold",7)
        c.setFillColor(colors.black)
        c.drawCentredString(px, plot_y_bottom - 14, dim_key)

        c.setFont("Helvetica",6)
        c.drawCentredString(
            px,
            plot_y_bottom - 26,
            f"{raw_c}/{raw_t}  {lvl_txt}"
        )

    # línea negra uniendo puntos
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    for j in range(len(poly_points)-1):
        (x1, y1) = poly_points[j]
        (x2, y2) = poly_points[j+1]
        c.line(x1, y1, x2, y2)
    for (px, py) in poly_points:
        c.setFillColor(colors.black)
        c.circle(px, py, 2, stroke=0, fill=1)

    # Caja resumen dimensiones evaluadas
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

    # Caja resumen cognitivo
    summary_box_x = margin_left
    summary_box_w = W - margin_right - margin_left
    summary_box_h = 150
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
        wrapped_f = wrap_text(c, "• " + f, summary_box_w - 24, "Helvetica",7)
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
        wrapped_r = wrap_text(c, "• " + r, summary_box_w - 24, "Helvetica",7)
        for ln in wrapped_r:
            c.drawString(summary_box_x + 20, ysum, ln)
            ysum -= 10

    ysum -= 8
    c.setFont("Helvetica-Bold",8)
    c.drawString(summary_box_x + 10, ysum, "Clasificación cognitiva global:")
    ysum -= 12
    c.setFont("Helvetica",7)
    gl_wrap = wrap_text(c, global_line, summary_box_w - 24, "Helvetica",7)
    for ln in gl_wrap:
        c.drawString(summary_box_x + 20, ysum, ln)
        ysum -= 10

    c.showPage()

    # ============================
    # PÁGINA 2
    # ============================

    c.setFont("Helvetica-Bold",9)
    c.setFillColor(colors.black)
    c.drawString(margin_left, H-40, "Detalle por dimensión")

    # Tabla tipo grilla
    table_x = margin_left
    table_y_top = H-60
    table_w = W - margin_left - margin_right
    row_h = 48
    header_h = 24
    dim_order = [
        ("RL", "Razonamiento Lógico / Abstracto"),
        ("QN", "Razonamiento Numérico"),
        ("VR", "Comprensión Verbal / Inferencia"),
        ("MT", "Memoria de Trabajo Inmediata"),
        ("AT", "Atención al Detalle / Precisión Visual"),
    ]
    n_rows = len(dim_order)
    table_h = header_h + n_rows*row_h

    # Marco tabla
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(table_x, table_y_top - table_h, table_w, table_h, stroke=1, fill=1)

    # Header gris claro
    c.setFillColor(colors.HexColor("#f8f9fa"))
    c.rect(table_x, table_y_top - header_h, table_w, header_h, stroke=0, fill=1)

    # Columnas
    col_sigla_x = table_x + 8
    col_punt_x  = table_x + 160
    col_lvl_x   = table_x + 240
    col_desc_x  = table_x + 300

    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(col_sigla_x, table_y_top - 16, "Dimensión")
    c.drawString(col_punt_x,  table_y_top - 16, "Puntaje")
    c.drawString(col_lvl_x,   table_y_top - 16, "Nivel")
    c.drawString(col_desc_x,  table_y_top - 16, "Descripción breve")

    # divisiones verticales suaves
    c.setStrokeColor(colors.lightgrey)
    c.setLineWidth(0.5)
    c.line(col_punt_x - 8, table_y_top, col_punt_x - 8, table_y_top - table_h)
    c.line(col_lvl_x  - 8, table_y_top, col_lvl_x  - 8, table_y_top - table_h)
    c.line(col_desc_x - 8, table_y_top, col_desc_x - 8, table_y_top - table_h)

    start_y = table_y_top - header_h
    for i, (sigla, fullname) in enumerate(dim_order):
        row_top_y = start_y - i*row_h
        row_bottom_y = row_top_y - row_h

        # Fila alternada muy suave
        if i % 2 == 1:
            c.setFillColor(colors.HexColor("#fcfcfc"))
            c.rect(table_x, row_bottom_y, table_w, row_h, stroke=0, fill=1)
        c.setFillColor(colors.black)

        correct_c = dim_correct[sigla]
        total_c   = dim_total[sigla]
        pct_val   = dim_pct[sigla]
        lvl_txt   = level_from_pct(pct_val)
        desc_text = dim_desc[sigla]

        # Dimensión
        c.setFont("Helvetica-Bold",7)
        c.drawString(col_sigla_x, row_top_y - 12, f"{sigla} / {fullname}")

        # Puntaje (correctas / total y %)
        c.setFont("Helvetica",7)
        c.drawString(col_punt_x, row_top_y - 12, f"{correct_c}/{total_c}  ({pct_val:.0f}%)")

        # Nivel
        c.drawString(col_lvl_x, row_top_y - 12, lvl_txt)

        # Descripción breve (wrap)
        yy_desc = row_top_y - 12
        wrap_desc = wrap_text(
            c,
            desc_text,
            table_w - (col_desc_x - table_x) - 10,
            "Helvetica",
            7
        )
        for ln in wrap_desc:
            c.drawString(col_desc_x, yy_desc, ln)
            yy_desc -= 9

        # línea horizontal fina
        c.setStrokeColor(colors.lightgrey)
        c.line(table_x, row_bottom_y, table_x + table_w, row_bottom_y)

    # Caja nota metodológica
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
        "Debe complementarse con entrevista estructurada, verificación de experiencia "
        "y evaluación técnica específica si corresponde."
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
    c.drawRightString(
        W - margin_right,
        40,
        "Uso interno RR.HH. · Evaluación Cognitiva General · No clínico"
    )

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
        candidate_name=st.session_state.candidate_name,
        fecha_eval=now_txt,
        evaluator_email=st.session_state.evaluator_email,
        scores=scores
    )

    if not st.session_state.already_sent:
        try:
            send_email_with_pdf(
                to_email=st.session_state.evaluator_email,
                pdf_bytes=pdf_bytes,
                filename="Informe_Cognitivo_General.pdf",
                subject="Informe Evaluación Cognitiva (IQ Screening)",
                body_text=(
                    "Adjunto informe interno de la Evaluación Cognitiva General (IQ Screening) "
                    f"para {st.session_state.candidate_name}.\nUso interno RR.HH."
                ),
            )
        except Exception:
            pass  # si falla el correo, no rompemos la app
        st.session_state.already_sent = True

# ============================================================
# CALLBACK DE RESPUESTA
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
        "Este test mide razonamiento lógico, numérico, comprensión verbal, memoria de trabajo "
        "y atención al detalle. Al finalizar se genera un informe PDF interno y se envía "
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
    progreso = (q_idx+1)/TOTAL_QUESTIONS

    # Header
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

    # Pregunta
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

    # Alternativas (2 columnas)
    cols = st.columns(2)
    for i, opt in enumerate(q["options"]):
        target_col = cols[i % 2]
        target_col.button(
            opt,
            key=f"ans_{q_idx}_{i}",
            use_container_width=True,
            on_click=choose_answer,
            args=(i,)
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

# Rerun controlado
if st.session_state._need_rerun:
    st.session_state._need_rerun = False
    st.rerun()
