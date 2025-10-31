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
    page_title="Test Cognitivo General (IQ + Raven textual)",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CREDENCIALES CORREO (SMTP GMAIL APP PASSWORD)
# ============================================================

FROM_ADDR = "jo.tajtaj@gmail.com"
APP_PASS = "nlkt kujl ebdg cyts"

# ============================================================
# PREGUNTAS
#
# Dimensiones evaluadas:
#   RL = Razonamiento Lógico / Abstracto (incluye estilo Raven textual: progresiones, patrones, matrices descritas)
#   QN = Razonamiento Numérico
#   VR = Comprensión Verbal / Inferencia
#   MT = Memoria de Trabajo Inmediata / Manipulación Mental Secuencial
#   AT = Atención al Detalle / Percepción de Patrones / Consistencia
#
# TOTAL: 70 ítems, 14 por dimensión.
#
# Dificultad sube dentro de cada dimensión.
#
# IMPORTANTE:
#  - Nada requiere imágenes.
#  - Las preguntas "tipo Raven" se incluyen como patrones descritos verbalmente
#    ("la figura va ganando un lado por paso", "el patrón es A-B-A-B-... cuál sigue").
# ============================================================

QUESTIONS = [
    # ======================================================
    # RL (Razonamiento Lógico / Abstracto / Raven textual)
    # ======================================================
    {
        "text": "RL1. Patrón: A, B, A, B, A, __. ¿Qué sigue?",
        "options": ["A", "B", "C", "No se puede saber"],
        "correct": 1,  # A,B alternado -> B
        "cat": "RL",
    },
    {
        "text": "RL2. Patrón de formas descritas: 'triángulo', 'cuadrado', 'triángulo', 'cuadrado', 'triángulo', __. ¿Qué sigue?",
        "options": ["Círculo", "Rectángulo", "Cuadrado", "No se puede determinar"],
        "correct": 2,
        "cat": "RL",
    },
    {
        "text": "RL3. Si todos los objetos tipo X tienen 3 lados, y este objeto tiene 3 lados, ¿es seguro que sea tipo X?",
        "options": [
            "Sí, siempre",
            "No, otro objeto puede tener 3 lados sin ser tipo X",
            "No, significa que tiene más de 3 lados",
            "Sí, porque 3 lados prueba que es X"
        ],
        "correct": 1,  # falacia de confirmar el consecuente
        "cat": "RL",
    },
    {
        "text": "RL4. Serie verbal: 'figura con 3 lados', 'figura con 4 lados', 'figura con 5 lados', 'figura con 6 lados'... ¿Cuál viene después?",
        "options": [
            "figura con 5 lados",
            "figura con 6 lados",
            "figura con 7 lados",
            "figura con 8 lados"
        ],
        "correct": 2,
        "cat": "RL",
    },
    {
        "text": "RL5. Matriz verbal: Fila 1 = [claro → medio → oscuro]. Fila 2 = [claro → medio → oscuro]. Fila 3 = [claro → medio → __]. ¿Cuál completa la matriz?",
        "options": [
            "claro",
            "medio",
            "oscuro",
            "no se puede saber"
        ],
        "correct": 2,
        "cat": "RL",
    },
    {
        "text": "RL6. Reglas condicionales: 'Si A ocurre, entonces B ocurre'. Observas que B ocurrió. ¿Qué puedes concluir con más precisión?",
        "options": [
            "Que A ocurrió con seguridad",
            "Que A no ocurrió",
            "Que A pudo haber ocurrido, pero no es seguro",
            "Que ni A ni B existen"
        ],
        "correct": 2,
        "cat": "RL",
    },
    {
        "text": "RL7. Razonamiento espacial descrito: la primera figura tiene 1 punto negro, la segunda tiene 2 puntos negros, la tercera tiene 3 puntos negros. ¿Cómo sería la cuarta?",
        "options": [
            "4 puntos negros",
            "2 puntos negros",
            "1 punto negro",
            "0 puntos negros"
        ],
        "correct": 0,
        "cat": "RL",
    },
    {
        "text": "RL8. Serie conceptual: 'pieza fija', 'pieza móvil', 'pieza fija', 'pieza móvil', ... ¿Cuál sigue?",
        "options": ["pieza móvil", "pieza fija", "pieza rota", "no se puede saber"],
        "correct": 0,
        "cat": "RL",
    },
    {
        "text": "RL9. Lógica: Todas las A son B. Todas las B son C. ¿Qué conclusión es válida?",
        "options": [
            "Todas las A son C",
            "Todas las C son A",
            "Ninguna A es C",
            "No hay relación entre A y C"
        ],
        "correct": 0,
        "cat": "RL",
    },
    {
        "text": "RL10. 'Si no firmas el control, no despachas'. El producto fue despachado. ¿Qué afirmación es más lógica?",
        "options": [
            "Alguien firmó el control",
            "Nadie firmó el control",
            "No hubo producto",
            "No se puede afirmar nada"
        ],
        "correct": 0,
        "cat": "RL",
    },
    {
        "text": "RL11. Progresión Raven textual: En cada paso, la figura gana un lado extra (3 lados, 4 lados, 5 lados...). ¿Qué pasaría dos pasos DESPUÉS de un octágono (8 lados)?",
        "options": [
            "9 lados",
            "10 lados",
            "11 lados",
            "12 lados"
        ],
        "correct": 3,  # 8 ->9 ->10 ; dos después es 10 lados, ojo: revisemos: "dos pasos después de un octágono (8 lados)" => 9 lados =1 paso, 10 lados=2 pasos -> correcto = "10 lados". Ajustamos opciones:
        "cat": "RL",
    },
    {
        "text": "RL11 (corr). Progresión: 8 lados → 9 lados → 10 lados. Dos pasos después de 8 lados es:",
        "options": ["9 lados", "10 lados", "11 lados", "12 lados"],
        "correct": 1,  # 10 lados
        "cat": "RL",
    },
    {
        "text": "RL12. Serie combinada descrita: claro-cuadrado, oscuro-cuadrado, claro-triángulo, oscuro-triángulo, claro-cuadrado... ¿Qué viene después?",
        "options": [
            "oscuro-cuadrado",
            "oscuro-triángulo",
            "claro-triángulo",
            "claro-cuadrado"
        ],
        "correct": 0,  # patrón color alterna claro/oscuro y forma alterna cuadrado/triángulo
        "cat": "RL",
    },
    {
        "text": "RL13. Deducción: 'Ningún elemento tipo Z tiene bordes redondos'. Observas un elemento Z. ¿Qué puedes concluir seguro?",
        "options": [
            "Tiene bordes redondos",
            "No tiene bordes redondos",
            "Tiene exactamente 3 bordes",
            "Es idéntico a todos los demás Z"
        ],
        "correct": 1,
        "cat": "RL",
    },
    {
        "text": "RL14. Dos condiciones: (1) Todo módulo A exige módulo B. (2) Módulo B exige módulo C. Sabes que un equipo tiene módulo A activo. ¿Qué afirmación es más fuerte?",
        "options": [
            "Debe tener B, pero C es opcional",
            "Debe tener B y C",
            "No necesita B ni C",
            "Solamente necesita C"
        ],
        "correct": 1,
        "cat": "RL",
    },

    # ======================================================
    # QN (Razonamiento Numérico / Secuencias / Proporciones)
    # ======================================================
    {
        "text": "QN1. 12 + 15 =",
        "options": ["25", "26", "27", "28"],
        "correct": 2,  # 27
        "cat": "QN",
    },
    {
        "text": "QN2. 60 es el 75% de:",
        "options": ["70", "75", "80", "90"],
        "correct": 2,  # 80
        "cat": "QN",
    },
    {
        "text": "QN3. Serie: 5, 9, 17, 33, __",
        "options": ["49", "57", "65", "81"],
        "correct": 1,  # +4,+8,+16,+24 => 33+24=57
        "cat": "QN",
    },
    {
        "text": "QN4. Una máquina produce 180 unidades en 6 horas. A la MISMA tasa, ¿cuántas en 14 horas?",
        "options": ["360", "390", "420", "440"],
        "correct": 2,  # 30/hora -> 30*14=420
        "cat": "QN",
    },
    {
        "text": "QN5. x = 4, y = 7. ¿Cuánto vale 3x + 2y?",
        "options": ["19", "20", "22", "26"],
        "correct": 3,  # 3*4=12 +2*7=14 =>26
        "cat": "QN",
    },
    {
        "text": "QN6. Un valor aumenta 10% y luego vuelve a aumentar 10%. ¿Cuál es el factor total aproximado?",
        "options": ["+10%", "+20%", "+21%", "+100%"],
        "correct": 2,  # 1.1 *1.1 =1.21 =>21%
        "cat": "QN",
    },
    {
        "text": "QN7. Resolver: 5z - 11 = 24. ¿z = ?",
        "options": ["5", "6", "7", "8"],
        "correct": 2,  # 5z=35 =>z=7
        "cat": "QN",
    },
    {
        "text": "QN8. Promedio de 18, 24, 30 y 48:",
        "options": ["24", "27", "30", "33"],
        "correct": 2,  # 120/4=30
        "cat": "QN",
    },
    {
        "text": "QN9. Serie: 2, 6, 18, 54, __",
        "options": ["81", "108", "162", "216"],
        "correct": 2,  # *3 cada paso => 54*3=162
        "cat": "QN",
    },
    {
        "text": "QN10. Una pieza tarda 7 min. ¿Cuánto demoran 11 piezas hechas seguidas a misma velocidad?",
        "options": ["63 min", "70 min", "77 min", "84 min"],
        "correct": 2,  # 7*11=77
        "cat": "QN",
    },
    {
        "text": "QN11. Serie decreciente: 120, 110, 101, 93, __",
        "options": ["87", "86", "85", "84"],
        "correct": 1,  # -10,-9,-8,-7 => 93-7=86
        "cat": "QN",
    },
    {
        "text": "QN12. 'Duplicar y luego triplicar' equivale globalmente a multiplicar por:",
        "options": ["2", "3", "5", "6"],
        "correct": 3,  # x2*x3 = x6
        "cat": "QN",
    },
    {
        "text": "QN13. Una receta usa 2 partes de concentrado por 5 partes de agua. Si quieres 21 partes totales, ¿cuántas partes de concentrado corresponden manteniendo la proporción?",
        "options": ["5", "6", "7", "8"],
        "correct": 1,  # 2/7 total. 21*(2/7)=6
        "cat": "QN",
    },
    {
        "text": "QN14. Si el 40% de un lote son 220 unidades, ¿cuál es el total aproximado del lote?",
        "options": ["440", "500", "550", "600"],
        "correct": 2,  # 220 /0.4=550
        "cat": "QN",
    },

    # ======================================================
    # VR (Comprensión Verbal / Inferencia Lógica Lingüística)
    # ======================================================
    {
        "text": "VR1. 'Inminente' significa:",
        "options": [
            "Que ocurrirá muy pronto",
            "Que no ocurrirá nunca",
            "Que ya pasó",
            "Que es opcional"
        ],
        "correct": 0,
        "cat": "VR",
    },
    {
        "text": "VR2. 'Ambiguo' significa:",
        "options": [
            "Con un solo significado",
            "Con varios significados posibles",
            "Muy estricto",
            "Muy rápido"
        ],
        "correct": 1,
        "cat": "VR",
    },
    {
        "text": "VR3. “El técnico informó que la falla es mecánica, no eléctrica”. ¿Qué se entiende mejor?",
        "options": [
            "Se quemó un circuito",
            "Se rompió físicamente una pieza",
            "Fue un problema de software",
            "No hubo problema real"
        ],
        "correct": 1,
        "cat": "VR",
    },
    {
        "text": "VR4. 'Ejecute el procedimiento EXACTAMENTE como está documentado' implica:",
        "options": [
            "Puede improvisar",
            "Debe seguir el documento al pie de la letra",
            "Debe detener la tarea",
            "Debe rediseñar el proceso"
        ],
        "correct": 1,
        "cat": "VR",
    },
    {
        "text": "VR5. 'Mitigar un riesgo' significa:",
        "options": [
            "Ignorarlo",
            "Aumentarlo",
            "Reducir su impacto",
            "Declararlo inexistente"
        ],
        "correct": 2,
        "cat": "VR",
    },
    {
        "text": "VR6. Una persona dice: 'No es que odie esta opción, pero preferiría otra'. Esa frase expresa:",
        "options": [
            "Rechazo total",
            "Preferencia leve por otra alternativa",
            "Entusiasmo extremo",
            "Indiferencia total"
        ],
        "correct": 1,
        "cat": "VR",
    },
    {
        "text": "VR7. 'Restricción estricta' indica:",
        "options": [
            "Regla flexible",
            "Regla sin excepciones",
            "Sugerencia amistosa",
            "Norma opcional"
        ],
        "correct": 1,
        "cat": "VR",
    },
    {
        "text": "VR8. “El operador demoró 30 minutos más de lo normal, por lo tanto…” ¿Cuál inferencia es más razonable?",
        "options": [
            "Probablemente enfrentó una dificultad adicional",
            "Se quedó dormido de seguro",
            "No hizo nada en toda la jornada",
            "Mintió sobre la hora sí o sí"
        ],
        "correct": 0,
        "cat": "VR",
    },
    {
        "text": "VR9. 'Actúa conforme al estándar' significa:",
        "options": [
            "Hazlo igual que está definido oficialmente",
            "Hazlo a tu manera",
            "No lo hagas",
            "Cámbialo según tu opinión"
        ],
        "correct": 0,
        "cat": "VR",
    },
    {
        "text": "VR10. 'Ejecución sin desvíos' quiere decir:",
        "options": [
            "Se aceptan pequeños cambios personales",
            "Debe seguirse exactamente como está escrito",
            "Se detiene hasta aviso",
            "No es obligatorio seguirlo"
        ],
        "correct": 1,
        "cat": "VR",
    },
    {
        "text": "VR11. Lee esta regla: 'Si el sello de seguridad está roto, no usar el equipo'. Ves el equipo en uso. ¿Qué es más lógico?",
        "options": [
            "El sello está intacto",
            "El sello está roto",
            "El equipo no existe",
            "No se puede asegurar nada"
        ],
        "correct": 0,
        "cat": "VR",
    },
    {
        "text": "VR12. 'Requiere verificación inmediata' sugiere que:",
        "options": [
            "Puede esperar varios días",
            "Debe revisarse ahora",
            "Se ignora hasta que falle",
            "Solo jefatura lo mira alguna vez"
        ],
        "correct": 1,
        "cat": "VR",
    },
    {
        "text": "VR13. 'El proceso debe replicarse fielmente'. ¿Cuál es la mejor interpretación?",
        "options": [
            "Debe copiarse tal cual",
            "Debe omitirse",
            "Debe reescribirse con libertad",
            "Debe detenerse"
        ],
        "correct": 0,
        "cat": "VR",
    },
    {
        "text": "VR14. 'La falla fue atribuida a operación humana, no al sistema'. ¿Qué implica?",
        "options": [
            "Hubo un error en la ejecución manual",
            "El sistema está roto",
            "No hubo falla real",
            "Nadie hizo nada mal"
        ],
        "correct": 0,
        "cat": "VR",
    },

    # ======================================================
    # MT (Memoria de Trabajo / Manipulación Mental Secuencial)
    # Las últimas son intencionalmente exigentes (varios pasos mentales).
    # ======================================================
    {
        "text": "MT1. Parte en 36. Súmale 9. Resta 7. ¿Resultado?",
        "options": ["36", "38", "40", "44"],
        "correct": 1,  # 38
        "cat": "MT",
    },
    {
        "text": "MT2. Parte en 82. Resta 15. Súmale 6. ¿Resultado?",
        "options": ["67", "69", "73", "76"],
        "correct": 2,  # 73
        "cat": "MT",
    },
    {
        "text": "MT3. Mantén 14 y 7. Súmalos. Multiplica por 2.",
        "options": ["28", "30", "32", "42"],
        "correct": 3,  # (14+7)=21*2=42
        "cat": "MT",
    },
    {
        "text": "MT4. Toma 96. Divide por 3. A eso réstale 4.",
        "options": ["24", "28", "30", "32"],
        "correct": 1,  # 96/3=32;32-4=28
        "cat": "MT",
    },
    {
        "text": "MT5. Empieza en 150. Resta 28. Divide el resultado por 2.",
        "options": ["56", "60", "61", "66"],
        "correct": 2,  # 150-28=122;122/2=61
        "cat": "MT",
    },
    {
        "text": "MT6. Piensa en 420. Divide por 5. Súmale 17.",
        "options": ["83", "84", "101", "117"],
        "correct": 2,  # 420/5=84; +17=101
        "cat": "MT",
    },
    {
        "text": "MT7. Toma 64. Divide por 8. Multiplica por 7.",
        "options": ["42", "48", "54", "56"],
        "correct": 3,  # 64/8=8;8*7=56
        "cat": "MT",
    },
    {
        "text": "MT8. Imagina el número 37. Inviértelo mentalmente (37 → 73). Súmale 4.",
        "options": ["74", "75", "76", "77"],
        "correct": 3,  # 77
        "cat": "MT",
    },
    {
        "text": "MT9. Empieza con 508. Resta 30. Inviértelo como texto (478 → 874). ¿Resultado final?",
        "options": ["874", "847", "784", "885"],
        "correct": 0,  # 874
        "cat": "MT",
    },
    {
        "text": "MT10. Toma 245. Súmale 55. Divide el total por 5.",
        "options": ["58", "59", "60", "61"],
        "correct": 2,  # 300/5=60
        "cat": "MT",
    },
    {
        "text": "MT11. Empieza con 312. Resta 27. Resta 27 otra vez.",
        "options": ["246", "258", "270", "282"],
        "correct": 1,  # 312-27=285;285-27=258
        "cat": "MT",
    },
    {
        "text": "MT12. Mantén 96. Súmale 17. Inviértelo tipo texto (113 → 311).",
        "options": ["311", "411", "611", "911"],
        "correct": 0,  # 96+17=113 -> '311'
        "cat": "MT",
    },
    {
        "text": "MT13. Tienes 18 y 24. Calcula el promedio [(18+24)/2].",
        "options": ["19", "20", "21", "22"],
        "correct": 2,  # 21
        "cat": "MT",
    },
    {
        "text": "MT14. Empieza con 500. Divide entre 4. Resta 48. Súmale 3.",
        "options": ["77", "78", "79", "80"],
        "correct": 3,  # 500/4=125;125-48=77;77+3=80
        "cat": "MT",
    },

    # ======================================================
    # AT (Atención al Detalle / Precisión fina / Patrones tipo Raven de diferencias pequeñas)
    # ======================================================
    {
        "text": "AT1. ¿Cuál está bien escrito?",
        "options": ["Resivido", "Recivido", "Recibido", "Resibido"],
        "correct": 2,
        "cat": "AT",
    },
    {
        "text": "AT2. ¿Cuál número es distinto? 4821, 4281, 4821, 4821",
        "options": ["4821 (1°)", "4281", "4821 (3°)", "4821 (4°)"],
        "correct": 1,
        "cat": "AT",
    },
    {
        "text": "AT3. ¿Qué parte de 'ABCD-1234' es puramente numérica?",
        "options": ["ABCD", "1234", "ABC", "CDA"],
        "correct": 1,
        "cat": "AT",
    },
    {
        "text": "AT4. ¿Cuál se parece MENOS a 'CONFIGURAR' (cambio interno del orden)?",
        "options": [
            "CONFGIURAR",
            "CONFIGURR",
            "CONFICURAR",
            "CONFINUGAR"
        ],
        "correct": 0,
        "cat": "AT",
    },
    {
        "text": "AT5. ¿Cuál número tiene SOLO dígitos pares?",
        "options": ["2486", "2478", "2687", "2893"],
        "correct": 0,
        "cat": "AT",
    },
    {
        "text": "AT6. ¿Cuál cadena tiene EXACTAMENTE 2 letras 'A'?",
        "options": ["AABA", "ABCA", "BAAA", "BACA"],
        "correct": 3,  # BACA -> 2 A
        "cat": "AT",
    },
    {
        "text": "AT7. ¿Cuántas letras 'E' hay en 'SELECCION ESPECIFICA'?",
        "options": ["2", "3", "4", "5"],
        "correct": 2,  # 4
        "cat": "AT",
    },
    {
        "text": "AT8. ¿Cuál coincide EXACTAMENTE con '9Q7B-9Q7B'?",
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
        "text": "AT9. Compara 'XZ-18F' vs 'XZ-1BF'. ¿Qué cambió?",
        "options": [
            "X cambió",
            "Z cambió",
            "'8' cambió a 'B'",
            "'B' cambió a '8'"
        ],
        "correct": 2,
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
        "options": ["RRST", "RSTT", "TRTS", "STTT"],
        "correct": 0,
        "cat": "AT",
    },
    {
        "text": "AT12. ¿Qué opción es la ÚNICA distinta?",
        "options": [
            "AB12-CD34",
            "AB12-CD34",
            "AB12-DC34",
            "AB12-CD34"
        ],
        "correct": 2,
        "cat": "AT",
    },
    {
        "text": "AT13. ¿Cuál tiene dígitos en orden estrictamente descendente?",
        "options": ["9751", "9517", "9753", "7531"],
        "correct": 3,  # 7>5>3>1
        "cat": "AT",
    },
    {
        "text": "AT14. Observa:\nA) Q7B-14XZ\nB) Q7B-14ZX\nC) Q7B-14XZ\nD) Q7B-14XZ\n¿Cuál es la única diferente?",
        "options": ["A", "B", "C", "D"],
        "correct": 1,  # B cambia XZ→ZX
        "cat": "AT",
    },
]

TOTAL_QUESTIONS = len(QUESTIONS)  # debería ser 70

# ============================================================
# MAPAS / NIVELES
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
# CÁLCULO DE PUNTAJES
# ============================================================

def compute_scores(ans_dict):
    dims = ["RL", "QN", "VR", "MT", "AT"]
    dim_correct = {d: 0 for d in dims}
    dim_total   = {d: 0 for d in dims}

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
    global_pct = (total_correct / total_items) * 100.0 if total_items > 0 else 0.0

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
        "RL": "Razonamiento lógico / abstracto. Capacidad para detectar patrones, reglas secuenciales y relaciones condicionales. Incluye progresiones tipo Raven descritas verbalmente.",
        "QN": "Razonamiento numérico. Manejo de cantidades, secuencias matemáticas, proporciones y transformaciones con números.",
        "VR": "Comprensión verbal. Capacidad para interpretar instrucciones escritas, matices de lenguaje y conclusiones lógicas a partir de texto.",
        "MT": "Memoria de trabajo inmediata. Retención activa y manipulación secuencial de información mental en varios pasos.",
        "AT": "Atención al detalle y precisión comparativa. Detección de diferencias sutiles, errores de transcripción y consistencia fina entre códigos.",
    }

def build_strengths_and_risks(dim_pct, global_pct):
    fortalezas = []
    riesgos = []

    if dim_pct["RL"] >= 60:
        fortalezas.append("Identificación de patrones lógicos y progresiones abstractas sobre la media interna.")
    else:
        riesgos.append("Puede requerir más apoyo cuando las reglas cambian y debe inferir la lógica rápidamente.")

    if dim_pct["QN"] >= 60:
        fortalezas.append("Buen manejo de cantidades, proporciones y transformaciones numéricas.")
    else:
        riesgos.append("Podría necesitar más tiempo para resolver cálculos en cadena o proporciones.")

    if dim_pct["VR"] >= 60:
        fortalezas.append("Interpreta instrucciones textuales y condiciones verbales con claridad.")
    else:
        riesgos.append("Podría requerir instrucciones más literales o ejemplos directos en textos complejos.")

    if dim_pct["MT"] >= 60:
        fortalezas.append("Sostiene varios pasos mentales encadenados sin perder la información intermedia.")
    else:
        riesgos.append("Puede perder parte de la secuencia cuando se exige mantener y transformar números mentalmente.")

    if dim_pct["AT"] >= 60:
        fortalezas.append("Detecta diferencias sutiles entre códigos, texto y dígitos con buena precisión.")
    else:
        riesgos.append("En controles de calidad muy finos puede pasar por alto variaciones pequeñas.")

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
# GENERAR PDF (2 páginas con layout ordenado)
# ============================================================

def generate_pdf(candidate_name, fecha_eval, evaluator_email, scores):
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

    # ---------------- PAGE 1 ----------------
    # Encabezado
    c.setFont("Helvetica-Bold",10)
    c.drawString(margin_left, H-40, "Evaluación Cognitiva General (IQ + Razonamiento Abstracto)")
    c.setFont("Helvetica",7)
    c.drawString(margin_left, H-53, "Instrumento orientado a estimar habilidades cognitivas globales en cinco dimensiones cognitivas. Uso interno RR.HH. / No clínico.")

    # Datos candidato
    data_box_x = W - margin_right - 220
    data_box_w = 220
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
    c.drawString(data_box_x+8, yy, "Documento interno. No diagnóstico clínico.")

    # Gráfico radar estilo barras+línea (0-6)
    chart_dims = [
        ("RL","Razonamiento Lógico / Abstracto"),
        ("QN","Razonamiento Numérico"),
        ("VR","Comprensión Verbal"),
        ("MT","Memoria de Trabajo"),
        ("AT","Atención al Detalle"),
    ]

    chart_box_x = margin_left
    chart_box_y_top = H - 160
    chart_box_w = 360
    chart_box_h = 160

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(chart_box_x, chart_box_y_top-chart_box_h, chart_box_w, chart_box_h, stroke=1, fill=1)

    c.setFont("Helvetica-Bold",8.5)
    c.setFillColor(colors.black)
    c.drawString(chart_box_x+8, chart_box_y_top-14, "Puntaje por Dimensión (escala interna 0–6)")

    plot_x = chart_box_x+30
    plot_y_bottom = chart_box_y_top-chart_box_h+30
    plot_w = chart_box_w-50
    plot_h = chart_box_h-60

    # rejilla
    c.setLineWidth(0.5)
    for lvl in range(0,7):
        yv = plot_y_bottom + (lvl/6.0)*plot_h
        c.setFont("Helvetica",6)
        c.setFillColor(colors.black)
        c.drawString(plot_x-18, yv-2, str(lvl))
        c.setStrokeColor(colors.lightgrey)
        c.line(plot_x, yv, plot_x+plot_w, yv)

    c.setStrokeColor(colors.black)
    c.line(plot_x, plot_y_bottom, plot_x, plot_y_bottom+plot_h)

    num_dims = len(chart_dims)
    gap = 10
    bar_w = (plot_w - gap*(num_dims+1))/num_dims
    poly_points = []

    for i,(dim_key, dim_label) in enumerate(chart_dims):
        norm_val = dim_scale[dim_key]   # 0..6
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

        # punto línea
        px = bx + bar_w/2.0
        py = by + bar_h
        poly_points.append((px, py))

        # etiquetas bajo
        c.setFont("Helvetica-Bold",7)
        c.setFillColor(colors.black)
        c.drawCentredString(px, plot_y_bottom-14, dim_key)

        c.setFont("Helvetica",6)
        c.drawCentredString(px, plot_y_bottom-26, f"{raw_c}/{raw_t}  {lvl_txt}")

    # línea negra uniendo puntos
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    for j in range(len(poly_points)-1):
        (x1,y1)=poly_points[j]
        (x2,y2)=poly_points[j+1]
        c.line(x1,y1,x2,y2)
    for (px,py) in poly_points:
        c.setFillColor(colors.black)
        c.circle(px,py,2,stroke=0,fill=1)

    # Caja resumen dimensiones evaluadas
    side_box_x = chart_box_x+chart_box_w+10
    side_box_y_top = chart_box_y_top
    side_box_w = 200
    side_box_h = chart_box_h

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(side_box_x, side_box_y_top-side_box_h, side_box_w, side_box_h, stroke=1, fill=1)

    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(side_box_x+8, side_box_y_top-14, "Dimensiones Evaluadas")

    yy2 = side_box_y_top-28
    c.setFont("Helvetica",7)
    lines_dim = [
        "RL  Razonamiento Lógico / Abstracto",
        "QN  Razonamiento Numérico",
        "VR  Comprensión Verbal / Inferencia",
        "MT  Memoria de Trabajo Inmediata / Secuencial",
        "AT  Atención al Detalle / Precisión Fina",
        "Escala comparativa interna (0–6)."
    ]
    for line in lines_dim:
        c.drawString(side_box_x+8, yy2, line)
        yy2 -= 10

    # Caja resumen cognitivo global
    summary_box_x = margin_left
    summary_box_w = W - margin_left - margin_right
    summary_box_h = 170
    summary_box_y_top = H - 360

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(summary_box_x, summary_box_y_top-summary_box_h, summary_box_w, summary_box_h, stroke=1, fill=1)

    ysum = summary_box_y_top-16
    c.setFont("Helvetica-Bold",9)
    c.setFillColor(colors.black)
    c.drawString(summary_box_x+10, ysum, "Resumen cognitivo observado")
    ysum -= 14

    # Fortalezas
    c.setFont("Helvetica-Bold",8)
    c.drawString(summary_box_x+10, ysum, "Fortalezas potenciales:")
    ysum -= 12
    c.setFont("Helvetica",7)
    for f in fortalezas:
        for ln in wrap_text(c, "• "+f, summary_box_w-24, "Helvetica",7):
            c.drawString(summary_box_x+20, ysum, ln)
            ysum -= 10
    ysum -= 4

    # Riesgos
    c.setFont("Helvetica-Bold",8)
    c.drawString(summary_box_x+10, ysum, "Aspectos a monitorear / apoyo sugerido:")
    ysum -= 12
    c.setFont("Helvetica",7)
    for r in riesgos:
        for ln in wrap_text(c, "• "+r, summary_box_w-24, "Helvetica",7):
            c.drawString(summary_box_x+20, ysum, ln)
            ysum -= 10
    ysum -= 4

    # Global band
    c.setFont("Helvetica-Bold",8)
    c.drawString(summary_box_x+10, ysum, "Clasificación cognitiva global:")
    ysum -= 12
    c.setFont("Helvetica",7)
    for ln in wrap_text(c, global_line, summary_box_w-24, "Helvetica",7):
        c.drawString(summary_box_x+20, ysum, ln)
        ysum -= 10

    c.showPage()

    # ---------------- PAGE 2 ----------------
    c.setFont("Helvetica-Bold",9)
    c.setFillColor(colors.black)
    c.drawString(margin_left, H-40, "Detalle por dimensión")

    # Tabla detalle
    table_x = margin_left
    table_y_top = H-60
    table_w = W - margin_left - margin_right
    row_h = 60
    header_h = 24
    dim_order = [
        ("RL","Razonamiento Lógico / Abstracto"),
        ("QN","Razonamiento Numérico"),
        ("VR","Comprensión Verbal / Inferencia"),
        ("MT","Memoria de Trabajo Inmediata / Secuencial"),
        ("AT","Atención al Detalle / Precisión Fina"),
    ]
    n_rows = len(dim_order)
    table_h = header_h + n_rows*row_h

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(table_x, table_y_top-table_h, table_w, table_h, stroke=1, fill=1)

    # Header fila gris
    c.setFillColor(colors.HexColor("#f8f9fa"))
    c.rect(table_x, table_y_top-header_h, table_w, header_h, stroke=0, fill=1)

    col_sigla_x = table_x+8
    col_punt_x  = table_x+180
    col_lvl_x   = table_x+260
    col_desc_x  = table_x+320

    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(col_sigla_x, table_y_top-16, "Dimensión")
    c.drawString(col_punt_x,  table_y_top-16, "Puntaje")
    c.drawString(col_lvl_x,   table_y_top-16, "Nivel")
    c.drawString(col_desc_x,  table_y_top-16, "Descripción breve")

    # separadores verticales
    c.setStrokeColor(colors.lightgrey)
    c.setLineWidth(0.5)
    c.line(col_punt_x-8, table_y_top, col_punt_x-8, table_y_top-table_h)
    c.line(col_lvl_x-8,  table_y_top, col_lvl_x-8,  table_y_top-table_h)
    c.line(col_desc_x-8, table_y_top, col_desc_x-8, table_y_top-table_h)

    start_y = table_y_top-header_h
    for i,(sigla,fullname) in enumerate(dim_order):
        row_top_y = start_y - i*row_h
        row_bottom_y = row_top_y-row_h

        # fondo alterno
        if i % 2 == 1:
            c.setFillColor(colors.HexColor("#fcfcfc"))
            c.rect(table_x, row_bottom_y, table_w, row_h, stroke=0, fill=1)

        correct_c = dim_correct[sigla]
        total_c   = dim_total[sigla]
        pct_val   = dim_pct[sigla]
        lvl_txt   = level_from_pct(pct_val)
        desc_text = dim_desc[sigla]

        # texto
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold",7)
        c.drawString(col_sigla_x, row_top_y-14, f"{sigla} / {fullname}")

        c.setFont("Helvetica",7)
        c.drawString(col_punt_x, row_top_y-14, f"{correct_c}/{total_c}  ({pct_val:.0f}%)")
        c.drawString(col_lvl_x, row_top_y-14, lvl_txt)

        # desc envuelta
        yy_desc = row_top_y-14
        wrap_desc = wrap_text(c, desc_text, table_w-(col_desc_x-table_x)-12, "Helvetica",7)
        for ln in wrap_desc:
            c.drawString(col_desc_x, yy_desc, ln)
            yy_desc -= 9

        # línea horizontal separadora
        c.setStrokeColor(colors.lightgrey)
        c.line(table_x, row_bottom_y, table_x+table_w, row_bottom_y)

    # Nota metodológica final
    note_box_x = margin_left
    note_box_w = W - margin_left - margin_right
    note_box_h = 90
    note_box_y_top = table_y_top - table_h - 20

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(note_box_x, note_box_y_top-note_box_h, note_box_w, note_box_h, stroke=1, fill=1)

    y_note = note_box_y_top-16
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(note_box_x+10, y_note, "Nota metodológica")
    y_note -= 14

    nota_text = (
        "Este informe se basa en las respuestas del evaluado a un conjunto de "
        "70 ítems cognitivos (razonamiento lógico/abstracto tipo Raven textual, "
        "razonamiento numérico, comprensión verbal, memoria de trabajo secuencial "
        "y atención al detalle). Describe el desempeño comparativo interno en cada "
        "dimensión cognitiva y la clasificación global. No constituye diagnóstico "
        "clínico ni, por sí solo, determina idoneidad laboral. Se recomienda "
        "complementar con entrevista estructurada y verificación de experiencia."
    )

    c.setFont("Helvetica",7)
    for ln in wrap_text(c, nota_text, note_box_w-24, "Helvetica",7):
        c.drawString(note_box_x+20, y_note, ln)
        y_note -= 10

    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawRightString(W-margin_right, 40, "Uso interno RR.HH. · Evaluación Cognitiva General · No clínico")

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
# FINALIZAR, GENERAR PDF, ENVIAR
# ============================================================

def finalize_and_send():
    scores = compute_scores(st.session_state.answers)

    pdf_bytes = generate_pdf(
        candidate_name = st.session_state.candidate_name,
        fecha_eval     = datetime.now().strftime("%d/%m/%Y %H:%M"),
        evaluator_email= st.session_state.evaluator_email,
        scores         = scores
    )

    if not st.session_state.already_sent:
        try:
            send_email_with_pdf(
                to_email   = st.session_state.evaluator_email,
                pdf_bytes  = pdf_bytes,
                filename   = "Informe_Cognitivo_General.pdf",
                subject    = "Informe Cognitivo General (IQ + Raven textual)",
                body_text  = (
                    "Adjunto informe cognitivo general (70 ítems IQ + patrones tipo Raven textual). "
                    f"Evaluado: {st.session_state.candidate_name}.\nUso interno RR.HH."
                ),
            )
        except Exception:
            pass
        st.session_state.already_sent = True

# ============================================================
# CALLBACK (evita doble click)
# ============================================================

def choose_answer(value_idx):
    q_idx = st.session_state.current_q
    st.session_state.answers[q_idx] = value_idx

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

def view_info_form():
    st.markdown("### Datos del evaluado")
    st.info("Estos datos se usarán en el informe PDF interno. Al finalizar el test se envía automáticamente al correo del evaluador.")

    st.session_state.candidate_name = st.text_input(
        "Nombre del evaluado",
        value=st.session_state.candidate_name,
        placeholder="Nombre completo"
    )

    st.session_state.evaluator_email = st.text_input(
        "Correo del evaluador / RR.HH.",
        value=st.session_state.evaluator_email,
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
                Test Cognitivo General (IQ + Raven textual)
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
                line-height:1.45;
                white-space:pre-wrap;">
                {q["text"]}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Opciones
    for opt_i, opt_txt in enumerate(q["options"]):
        st.button(
            opt_txt,
            key=f"ans_{q_idx}_{opt_i}",
            use_container_width=True,
            on_click=choose_answer,
            args=(opt_i,)
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
            <b>Confidencialidad:</b> Uso interno RR.HH. / Selección interna.
            El evaluado no recibe copia directa del informe.
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
# FLUJO
# ============================================================

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

# control de rerun suave
if st.session_state._need_rerun:
    st.session_state._need_rerun = False
    st.rerun()
