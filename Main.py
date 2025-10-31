# ============================================================
# Test Cognitivo General / IQ Screen · 70 ítems
# Dimensiones:
#   RL = Razonamiento Lógico / Abstracto (tipo Raven verbal)
#   QN = Razonamiento Cuantitativo / Proporcional
#   VR = Comprensión Verbal / Inferencia
#   MT = Memoria de Trabajo / Manipulación mental
#   AT = Atención al Detalle / Precisión
#
# Flujo:
#   1. Datos del candidato
#   2. Test de 70 preguntas (Sí/No ya no aplica: ahora es multialternativa)
#   3. Se genera y envía PDF automáticamente al correo del evaluador
#   4. Pantalla final: "Evaluación finalizada"
#
# PDF:
#   - 2 páginas
#   - Página 1: cabecera, datos persona, gráfico radial simplificado, resumen cognitivo
#   - Página 2: tabla "Detalle por dimensión" + Fortalezas / Puntos a observar
#
# Librerías necesarias:
#   pip install streamlit reportlab
#
# ============================================================

import streamlit as st
from datetime import datetime
from io import BytesIO
import smtplib
from email.message import EmailMessage

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm

# -----------------------------------------------------------
# CONFIG STREAMLIT
# -----------------------------------------------------------
st.set_page_config(
    page_title="Evaluación Cognitiva / IQ",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------
# CREDENCIALES DE CORREO
# -----------------------------------------------------------
FROM_ADDR = "jo.tajtaj@gmail.com"
APP_PASS  = "nlkt kujl ebdg cyts"  # contraseña de aplicación (placeholder)

# -----------------------------------------------------------
# PREGUNTAS (70 ítems totales)
# Dimensiones: RL, QN, VR, MT, AT
# Cada pregunta:
#   text: enunciado
#   options: lista de 4 alternativas
#   correct: índice de la alternativa correcta (0..3)
#   cat: categoría/dimensión
# -----------------------------------------------------------

QUESTIONS = [
    # RL (Razonamiento Lógico / Abstracto / tipo Raven textual) - 14 preguntas
    {
        "text": "RL1. Patrón verbal: A, B, A, B, A, __. ¿Qué sigue?",
        "options": ["A", "B", "C", "No se puede saber"],
        "correct": 1,
        "cat": "RL",
    },
    {
        "text": "RL2. Secuencia de formas: triángulo, cuadrado, triángulo, cuadrado, triángulo, __. ¿Qué sigue?",
        "options": ["Círculo", "Cuadrado", "Rectángulo", "No se puede determinar"],
        "correct": 1,
        "cat": "RL",
    },
    {
        "text": "RL3. Regla: 'Cada pieza nueva agrega un lado más que la anterior'. Si una figura tenía 5 lados, luego otra con 6 lados. ¿Cuántos lados debería tener la siguiente?",
        "options": ["5", "6", "7", "8"],
        "correct": 2,
        "cat": "RL",
    },
    {
        "text": "RL4. Una matriz verbal tiene tres filas. En cada fila los tonos van 'claro → medio → oscuro'. En la tercera fila observas 'claro → medio → __'. ¿Qué completa mejor el patrón?",
        "options": ["claro", "medio", "oscuro", "No se puede saber"],
        "correct": 2,
        "cat": "RL",
    },
    {
        "text": "RL5. Regla lógica: 'Si ocurre A, entonces debe activarse B'. Sabes que B está activo. ¿Qué puedes afirmar con mayor precisión?",
        "options": [
            "A ocurrió con certeza",
            "A no ocurrió",
            "A pudo haber ocurrido, pero no es seguro",
            "B no tiene relación con A"
        ],
        "correct": 2,
        "cat": "RL",
    },
    {
        "text": "RL6. Todas las piezas tipo X tienen 3 puntas negras. Ves una pieza con 3 puntas negras. ¿Qué es más correcto?",
        "options": [
            "Seguro es tipo X",
            "Podría ser tipo X, pero no es 100% seguro",
            "Seguro NO es tipo X",
            "No puede existir una pieza tipo X"
        ],
        "correct": 1,
        "cat": "RL",
    },
    {
        "text": "RL7. En cada paso, una figura gana exactamente un punto negro adicional (1 punto, luego 2, luego 3...). ¿Cómo se vería DOS PASOS después de una figura con 4 puntos negros?",
        "options": [
            "Seguiría con 4 puntos",
            "Tendría 5 puntos",
            "Tendría 6 puntos",
            "No se puede inferir"
        ],
        "correct": 2,
        "cat": "RL",
    },
    {
        "text": "RL8. Secuencia alternada: 'pieza fija', 'pieza móvil', 'pieza fija', 'pieza móvil', ... ¿Qué viene después?",
        "options": ["pieza fija", "pieza móvil", "pieza inactiva", "no se sabe"],
        "correct": 1,
        "cat": "RL",
    },
    {
        "text": "RL9. Todas las A son B. Todas las B son C. ¿Qué conclusión es lógicamente válida?",
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
        "text": "RL10. Norma: 'Para despachar, el control debe estar firmado'. Se despachó un producto. ¿Qué afirmación es más lógica?",
        "options": [
            "Alguien firmó el control",
            "Nadie firmó el control",
            "No hubo producto",
            "No se puede decir nada"
        ],
        "correct": 0,
        "cat": "RL",
    },
    {
        "text": "RL11. Progresión: una figura con 8 lados, luego 9 lados, luego 10 lados. ¿Cuál descripción corresponde a la figura DOS pasos después de la de 8 lados?",
        "options": ["9 lados", "10 lados", "11 lados", "12 lados"],
        "correct": 1,  # 8→9→10 → dos pasos después de 8 = 10 lados
        "cat": "RL",
    },
    {
        "text": "RL12. Secuencia doble: claro-cuadrado / oscuro-cuadrado / claro-triángulo / oscuro-triángulo / claro-cuadrado / ... ¿Qué sigue?",
        "options": [
            "oscuro-cuadrado",
            "oscuro-triángulo",
            "claro-triángulo",
            "claro-cuadrado"
        ],
        "correct": 0,
        "cat": "RL",
    },
    {
        "text": "RL13. Afirmación: 'Ningún componente tipo Z tiene bordes redondos'. Estás frente a un componente tipo Z. ¿Qué deducción sí es segura?",
        "options": [
            "Tiene bordes redondos",
            "No tiene bordes redondos",
            "Tiene exactamente 3 bordes",
            "Todos los Z son idénticos"
        ],
        "correct": 1,
        "cat": "RL",
    },
    {
        "text": "RL14. Dos reglas: (1) 'Si A está activo, B también debe estarlo'. (2) 'Si B está activo, C también debe estarlo'. Ves un equipo con A activo. ¿Qué afirmación es más sólida?",
        "options": [
            "Tiene B, pero no necesariamente C",
            "Tiene B y C activos",
            "No tiene B ni C",
            "Solo tiene C activo"
        ],
        "correct": 1,
        "cat": "RL",
    },

    # QN (Razonamiento Cuantitativo / Proporcional / Ritmo)
    {
        "text": "QN1. Una máquina llena 45 cajas en 15 minutos con ritmo constante. ¿Cuántas en 60 minutos?",
        "options": ["90", "120", "135", "180"],
        "correct": 3,  # 45/15=3 por min -> *60=180
        "cat": "QN",
    },
    {
        "text": "QN2. Un supervisor dice: 'Este equipo perdió cerca de 20% de eficiencia respecto a 200 unidades por turno'. Aproximadamente, ¿cuántas unidades produjo este turno?",
        "options": ["120", "140", "160", "180"],
        "correct": 2,  # 200-20%=160
        "cat": "QN",
    },
    {
        "text": "QN3. Volumen por hora: 30, 45, 67, 100, ... Cada paso sube más que el anterior. ¿Cuál es la proyección más razonable para la siguiente hora?",
        "options": ["110", "130", "140", "100 otra vez"],
        "correct": 2,  # ~+45 => 145 aprox, más cerca 140
        "cat": "QN",
    },
    {
        "text": "QN4. Un lote es el 40% de la producción diaria y ese lote tiene 220 unidades. ¿Cuál sería la producción diaria total aproximada?",
        "options": ["400", "500", "550", "600"],
        "correct": 2,  # 220 ~40% => ~550
        "cat": "QN",
    },
    {
        "text": "QN5. Un inspector ve mediciones de tiempo de respuesta (segundos): 12, 15, 15, 18. ¿Cuál valor está más cerca del promedio?",
        "options": ["12", "15", "18", "Ninguno se acerca"],
        "correct": 1,  # promedio ~15
        "cat": "QN",
    },
    {
        "text": "QN6. Turno A produjo 25% más que Turno B. Turno B hizo 160 unidades. ¿Cuántas hizo A, aprox.?",
        "options": ["180", "190", "200", "220"],
        "correct": 2,  # 160 *1.25=200
        "cat": "QN",
    },
    {
        "text": "QN7. Proceso interno: primero duplicas 40, luego aumentas ese resultado en 50%. ¿Resultado final aproximado?",
        "options": ["80", "100", "120", "140"],
        "correct": 2,  # 40->80->80+40=120
        "cat": "QN",
    },
    {
        "text": "QN8. Cada pieza tarda ~7 min en completarse de forma estable. Si se hacen 11 piezas seguidas al mismo ritmo, ¿duración total aprox.?",
        "options": ["63 min", "70 min", "77 min", "84 min"],
        "correct": 2,  # 7*11=77
        "cat": "QN",
    },
    {
        "text": "QN9. Serie que baja cada vez menos: 120 → 110 → 101 → 93 → __. ¿Qué número esperas si la caída sigue reduciéndose gradualmente?",
        "options": ["88", "86", "85", "84"],
        "correct": 1,  # -10,-9,-8,-7 => 86
        "cat": "QN",
    },
    {
        "text": "QN10. Un tambor rinde 30 litros de mezcla. Necesitas 5 tambores para una tarea completa. ¿Litros totales?",
        "options": ["90", "120", "135", "150"],
        "correct": 3,  # 30*5=150
        "cat": "QN",
    },
    {
        "text": "QN11. Un proceso sube 10%, y luego vuelve a subir otro 10%. ¿Cuál frase describe mejor el aumento total?",
        "options": [
            "Aumentó ~10% en total",
            "Aumentó ~20% exactos",
            "Aumentó un poco más de 20%",
            "Duplicó la producción"
        ],
        "correct": 2,  # ~21%
        "cat": "QN",
    },
    {
        "text": "QN12. Cuatro lecturas de peso de un paquete: 98.9 / 99.2 / 98.8 / 99.1. ¿Cuál afirmación es más razonable?",
        "options": [
            "El peso real ronda cerca de 50",
            "El peso real ronda cerca de 99",
            "El peso real ronda cerca de 150",
            "Es imposible estimar un rango"
        ],
        "correct": 1,
        "cat": "QN",
    },
    {
        "text": "QN13. Dos sublíneas paralelas: una produce el doble que la otra. Si la más rápida entrega unas 200 unidades, ¿cuánto esperas aprox. de la más lenta?",
        "options": ["50", "80", "100", "120"],
        "correct": 2,  # ~100
        "cat": "QN",
    },
    {
        "text": "QN14. Se estima que cierto equipo baja ~5% de rendimiento por hora en jornadas largas. Tras 4 horas seguidas, ¿qué afirmación es más coherente?",
        "options": [
            "Mantendrá exactamente el 100% inicial",
            "Estará levemente por debajo del 80% inicial",
            "Estará exactamente en 50%",
            "Subirá sobre el 110%"
        ],
        "correct": 1,  # ~20% caída
        "cat": "QN",
    },

    # VR (Comprensión Verbal / Inferencia) - 14 preguntas
    {
        "text": "VR1. 'Inminente' significa algo que:",
        "options": [
            "ocurrirá muy pronto",
            "no ocurrirá jamás",
            "ya ocurrió hace mucho",
            "es puramente decorativo"
        ],
        "correct": 0,
        "cat": "VR",
    },
    {
        "text": "VR2. 'Ambiguo' describe algo que:",
        "options": [
            "tiene un solo sentido muy claro",
            "puede tener más de una interpretación",
            "es físicamente peligroso",
            "es muy lento"
        ],
        "correct": 1,
        "cat": "VR",
    },
    {
        "text": "VR3. Informe: 'La falla detectada es mecánica, no eléctrica'. ¿Qué sugiere con más precisión?",
        "options": [
            "Se quemó un circuito interno",
            "Hay desgaste o daño físico de una pieza",
            "Fue solo un error de software",
            "No hubo daño real"
        ],
        "correct": 1,
        "cat": "VR",
    },
    {
        "text": "VR4. 'Ejecute las instrucciones exactamente como están escritas' implica:",
        "options": [
            "Puede improvisar",
            "Debe seguirlas al pie de la letra",
            "Debe detener la actividad",
            "Debe proponer otro método"
        ],
        "correct": 1,
        "cat": "VR",
    },
    {
        "text": "VR5. 'Mitigar un riesgo' significa:",
        "options": [
            "aumentarlo",
            "ignorar que existe",
            "reducir su impacto",
            "garantizar que nunca pase nada"
        ],
        "correct": 2,
        "cat": "VR",
    },
    {
        "text": "VR6. 'No es que odie esta opción, pero preferiría otra'. Eso expresa principalmente:",
        "options": [
            "rechazo total",
            "preferencia moderada por otra alternativa",
            "entusiasmo extremo",
            "indiferencia absoluta"
        ],
        "correct": 1,
        "cat": "VR",
    },
    {
        "text": "VR7. 'Restricción estricta' indica:",
        "options": [
            "regla flexible",
            "regla sin excepciones",
            "simple sugerencia",
            "norma opcional"
        ],
        "correct": 1,
        "cat": "VR",
    },
    {
        "text": "VR8. Un supervisor anota: 'Este operador tardó 30 minutos más de lo normal'. ¿Cuál inferencia es más razonable?",
        "options": [
            "Probablemente encontró una dificultad adicional",
            "Seguro se quedó dormido",
            "No hizo nada en la jornada",
            "Mintió con certeza"
        ],
        "correct": 0,
        "cat": "VR",
    },
    {
        "text": "VR9. 'Actúa conforme al estándar' quiere decir:",
        "options": [
            "hazlo tal como está definido oficialmente",
            "hazlo a tu manera personal",
            "no lo hagas",
            "cámbialo libremente"
        ],
        "correct": 0,
        "cat": "VR",
    },
    {
        "text": "VR10. 'Ejecución sin desvíos' implica que:",
        "options": [
            "se aceptan cambios libres",
            "se sigue exactamente el plan descrito",
            "se detiene hasta nuevo aviso",
            "el plan es opcional"
        ],
        "correct": 1,
        "cat": "VR",
    },
    {
        "text": "VR11. Regla: 'Si el sello de seguridad está roto, NO usar el equipo'. Ves el equipo en uso. ¿Qué deducción es más lógica?",
        "options": [
            "El sello probablemente está intacto",
            "El sello seguro está roto",
            "No existe sello",
            "No se puede deducir nada"
        ],
        "correct": 0,
        "cat": "VR",
    },
    {
        "text": "VR12. 'Requiere verificación inmediata' indica:",
        "options": [
            "puede esperar varios días",
            "debe revisarse ahora",
            "debe ignorarse",
            "solo jefatura puede verlo algún día"
        ],
        "correct": 1,
        "cat": "VR",
    },
    {
        "text": "VR13. 'El proceso debe replicarse fielmente' se interpreta como:",
        "options": [
            "debe copiarse tal cual",
            "debe omitirse",
            "debe rehacerse libremente",
            "debe detenerse"
        ],
        "correct": 0,
        "cat": "VR",
    },
    {
        "text": "VR14. 'La falla fue atribuida a operación humana, no al sistema'. ¿Qué implica con más fuerza?",
        "options": [
            "hubo un error en la ejecución manual",
            "el sistema está roto",
            "no hubo falla real",
            "nadie hizo nada mal"
        ],
        "correct": 0,
        "cat": "VR",
    },

    # MT (Memoria de Trabajo / Manipulación mental) - 14 preguntas
    {
        "text": "MT1. Empieza en 36. Súmale 9. Luego réstale 7. ¿Resultado final?",
        "options": ["36", "38", "40", "44"],
        "correct": 1,  # 38
        "cat": "MT",
    },
    {
        "text": "MT2. Parte en 82. Resta 15. Luego súmale 6. ¿Cuál es el resultado final?",
        "options": ["67", "69", "73", "76"],
        "correct": 2,  # 73
        "cat": "MT",
    },
    {
        "text": "MT3. Mantén 14 y 7. Súmalos mentalmente. Duplica ese resultado. ¿Resultado final?",
        "options": ["28", "30", "32", "42"],
        "correct": 3,  # 42
        "cat": "MT",
    },
    {
        "text": "MT4. Conserva 96. Divídelo mentalmente por 3. Luego réstale 4. ¿Con qué valor terminas?",
        "options": ["24", "28", "30", "32"],
        "correct": 1,  # 28
        "cat": "MT",
    },
    {
        "text": "MT5. Parte con 150. Resta 28. Luego divide el resultado entre 2. ¿Valor final aproximado?",
        "options": ["56", "60", "61", "66"],
        "correct": 2,  # 61
        "cat": "MT",
    },
    {
        "text": "MT6. Empieza con 64. Divídelo en 8 partes iguales. Multiplica ese resultado por 7. ¿Cuál obtienes?",
        "options": ["42", "48", "54", "56"],
        "correct": 3,  # 56
        "cat": "MT",
    },
    {
        "text": "MT7. Piensa en 37. Invierte mentalmente el orden de sus dígitos. Súmale 4 a ese número invertido. ¿Qué obtienes?",
        "options": ["74", "75", "76", "77"],
        "correct": 3,  # 37→73→+4=77
        "cat": "MT",
    },
    {
        "text": "MT8. Mantén 508. Resta 30 mentalmente. Luego invierte el orden de las cifras del número resultante. ¿Cuál queda?",
        "options": ["874", "847", "784", "885"],
        "correct": 0,  # 478→874
        "cat": "MT",
    },
    {
        "text": "MT9. Conserva 245. Súmale 55. Divide ese total entre 5. ¿Resultado final?",
        "options": ["58", "59", "60", "61"],
        "correct": 2,  # 300/5=60
        "cat": "MT",
    },
    {
        "text": "MT10. Mantén 312. Resta 27. Luego vuelve a restar 27 al nuevo resultado. ¿En qué número terminas?",
        "options": ["246", "258", "270", "282"],
        "correct": 1,  # 258
        "cat": "MT",
    },
    {
        "text": "MT11. Conserva 96. Súmale 17 mentalmente. Invierte las cifras del resultado. ¿Cuál es ese número invertido?",
        "options": ["311", "411", "611", "911"],
        "correct": 0,  # 96+17=113→311
        "cat": "MT",
    },
    {
        "text": "MT12. Retén 18 y 24. Calcula el promedio (la mitad de su suma). ¿Cuál es el promedio?",
        "options": ["19", "20", "21", "22"],
        "correct": 2,  # 21
        "cat": "MT",
    },
    {
        "text": "MT13. Empieza en 500. Divide mentalmente ese valor en 4 partes iguales. Al resultado réstale 48 y luego súmale 3. ¿Con qué número terminas?",
        "options": ["77", "78", "79", "80"],
        "correct": 3,  # 80
        "cat": "MT",
    },
    {
        "text": "MT14. Mantén dos pasos: (1) suma 11 a 54; (2) réstale 9 al resultado. ¿Valor final?",
        "options": ["52", "54", "56", "58"],
        "correct": 2,  # 56
        "cat": "MT",
    },

    # AT (Atención al Detalle / Precisión) - 14 preguntas
    {
        "text": "AT1. ¿Cuál está correctamente escrito en español estándar?",
        "options": ["Resivido", "Recibido", "Recivido", "Resibido"],
        "correct": 1,
        "cat": "AT",
    },
    {
        "text": "AT2. Secuencias: 4821 / 4281 / 4821 / 4821. ¿Cuál es la única diferente?",
        "options": ["1ª", "2ª", "3ª", "4ª"],
        "correct": 1,
        "cat": "AT",
    },
    {
        "text": "AT3. ¿Qué parte del código 'ABCD-1234' es solo numérica?",
        "options": ["ABCD", "1234", "ABC", "CDA"],
        "correct": 1,
        "cat": "AT",
    },
    {
        "text": "AT4. ¿Cuál altera el orden interno de 'CONFIGURAR' pero mantiene exactamente las mismas letras?",
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
        "text": "AT5. ¿Cuál de estos números contiene solo dígitos pares?",
        "options": ["2486", "2478", "2687", "2893"],
        "correct": 0,
        "cat": "AT",
    },
    {
        "text": "AT6. ¿Cuál de las siguientes cadenas contiene exactamente dos letras 'A'?",
        "options": ["AABA", "ABCA", "BAAA", "BACA"],
        "correct": 3,
        "cat": "AT",
    },
    {
        "text": "AT7. ¿Cuántas letras 'E' hay en la frase 'SELECCION ESPECIFICA'?",
        "options": ["2", "3", "4", "5"],
        "correct": 2,  # 4
        "cat": "AT",
    },
    {
        "text": "AT8. ¿Cuál coincide exactamente con '9Q7B-9Q7B'?",
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
        "text": "AT9. Compara 'XZ-18F' con 'XZ-1BF'. ¿Qué cambió?",
        "options": [
            "La X cambió",
            "La Z cambió",
            "El dígito '8' fue reemplazado por la letra 'B'",
            "Nada cambió"
        ],
        "correct": 2,
        "cat": "AT",
    },
    {
        "text": "AT10. ¿Cuál está correctamente escrita?",
        "options": ["Instrución", "Instrocsión", "Instrucción", "Instrucsion"],
        "correct": 2,
        "cat": "AT",
    },
    {
        "text": "AT11. ¿Cuál de estas secuencias tiene más letras 'R'?",
        "options": ["RRST", "RSTT", "TRTS", "STTT"],
        "correct": 0,
        "cat": "AT",
    },
    {
        "text": "AT12. Observa: AB12-CD34 / AB12-CD34 / AB12-DC34 / AB12-CD34. ¿Cuál es la única distinta?",
        "options": ["1ª", "2ª", "3ª", "4ª"],
        "correct": 2,
        "cat": "AT",
    },
    {
        "text": "AT13. ¿Cuál número tiene dígitos en orden estrictamente descendente de izquierda a derecha?",
        "options": ["9751", "9517", "9753", "7531"],
        "correct": 3,
        "cat": "AT",
    },
    {
        "text": "AT14. Observa estas cadenas:\nA) Q7B-14XZ\nB) Q7B-14ZX\nC) Q7B-14XZ\nD) Q7B-14XZ\n¿Cuál es la única diferente?",
        "options": ["A", "B", "C", "D"],
        "correct": 1,
        "cat": "AT",
    },
]

TOTAL_QUESTIONS = len(QUESTIONS)  # 70

# -----------------------------------------------------------
# ESTADO GLOBAL STREAMLIT
# -----------------------------------------------------------
if "stage" not in st.session_state:
    st.session_state.stage = "info"  # info -> test -> done

if "candidate_name" not in st.session_state:
    st.session_state.candidate_name = ""

if "evaluator_email" not in st.session_state:
    st.session_state.evaluator_email = ""

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "answers" not in st.session_state:
    # answers[q_idx] = índice alternativa elegida (0..3)
    st.session_state.answers = {i: None for i in range(TOTAL_QUESTIONS)}

if "already_sent" not in st.session_state:
    st.session_state.already_sent = False

if "_need_rerun" not in st.session_state:
    st.session_state._need_rerun = False


# -----------------------------------------------------------
# SCORING
# -----------------------------------------------------------
def compute_dimension_scores(ans_dict):
    """
    Retorna:
      raw_scores: aciertos por dimensión (0..14 cada una)
      perc_scores: porcentaje de acierto (0..100)
    """
    dims = ["RL", "QN", "VR", "MT", "AT"]
    raw = {d: 0 for d in dims}
    total = {d: 0 for d in dims}

    for idx, q in enumerate(QUESTIONS):
        cat = q["cat"]
        total[cat] += 1
        chosen = ans_dict.get(idx)
        if chosen is not None and chosen == q["correct"]:
            raw[cat] += 1

    perc = {}
    for d in dims:
        if total[d] > 0:
            perc[d] = (raw[d] / total[d]) * 100.0
        else:
            perc[d] = 0.0

    return raw, perc

def overall_level(perc):
    """
    Devuelve clasificación general de rendimiento cognitivo:
    - Alta (>=75 promedio)
    - Promedio (>=40 y <75)
    - Bajo (<40)
    """
    avg = sum(perc.values())/len(perc)
    if avg >= 75:
        return "Alto rendimiento cognitivo general"
    elif avg >= 40:
        return "Rendimiento promedio"
    else:
        return "Rendimiento bajo"

def build_dim_description(perc_scores):
    """
    Breve descripción de cada dimensión según su %.
    Más alto => mejor desempeño observado en esa habilidad.
    """
    desc = {}

    def level_text(p, high_txt, mid_txt, low_txt):
        if p >= 75:
            return high_txt
        elif p >= 40:
            return mid_txt
        else:
            return low_txt

    desc["RL"] = level_text(
        perc_scores["RL"],
        "Capacidad sólida para identificar patrones, deducir reglas y anticipar la siguiente secuencia lógica.",
        "Muestra comprensión aceptable de patrones y relaciones básicas.",
        "Puede requerir más tiempo para detectar reglas abstractas y relaciones no explícitas."
    )

    desc["QN"] = level_text(
        perc_scores["QN"],
        "Buen manejo de cantidades, proporciones y estimaciones numéricas aplicadas.",
        "Razonamiento numérico funcional en contextos conocidos.",
        "Puede presentar dificultad para estimar proporciones y proyectar cantidades bajo cambios."
    )

    desc["VR"] = level_text(
        perc_scores["VR"],
        "Buena comprensión verbal, interpreta con precisión instrucciones y matices de lenguaje.",
        "Comprensión verbal adecuada para seguir y explicar instrucciones.",
        "Puede requerir instrucciones más explícitas o repetidas para evitar malentendidos."
    )

    desc["MT"] = level_text(
        perc_scores["MT"],
        "Buena memoria de trabajo: mantiene y manipula varios pasos mentales de forma consistente.",
        "Memoria de trabajo suficiente para resolver pasos simples en secuencia.",
        "Puede perder información intermedia al hacer varios pasos mentales seguidos."
    )

    desc["AT"] = level_text(
        perc_scores["AT"],
        "Alta precisión visual/atencional para distinguir detalles sutiles y errores mínimos.",
        "Nivel de atención al detalle adecuado para tareas estándar de control.",
        "Puede pasar por alto diferencias finas, lo que sugiere revisar exactitud en tareas críticas."
    )

    return desc

def build_strengths_and_risks(perc_scores):
    fortalezas = []
    monitoreo = []

    if perc_scores["RL"] >= 75:
        fortalezas.append("Detecta patrones y reglas rápidamente, lo que facilita entender procesos nuevos.")
    elif perc_scores["RL"] < 40:
        monitoreo.append("Puede requerir apoyo inicial para entender reglas nuevas o cambios de secuencia.")

    if perc_scores["QN"] >= 75:
        fortalezas.append("Buen manejo de cantidades y estimaciones numéricas en contexto de trabajo.")
    elif perc_scores["QN"] < 40:
        monitoreo.append("Podría necesitar guía adicional al estimar tiempos / volúmenes en condiciones cambiantes.")

    if perc_scores["VR"] >= 75:
        fortalezas.append("Interpreta instrucciones escritas/orales con precisión y puede transmitirlas.")
    elif perc_scores["VR"] < 40:
        monitoreo.append("Puede requerir instrucciones más directas para evitar malentendidos.")

    if perc_scores["MT"] >= 75:
        fortalezas.append("Mantiene varios pasos mentales activos sin perder la secuencia.")
    elif perc_scores["MT"] < 40:
        monitoreo.append("Podría beneficiarse de instrucciones divididas en pasos cortos.")

    if perc_scores["AT"] >= 75:
        fortalezas.append("Detecta detalles finos y errores pequeños de forma consistente.")
    elif perc_scores["AT"] < 40:
        monitoreo.append("Podría omitir detalles menores bajo presión; recomendable verificación cruzada.")

    # limitar a 4 cada uno
    return fortalezas[:4], monitoreo[:4]

def cognitive_summary_text(level_str):
    if "Alto" in level_str:
        return (
            "El desempeño global sugiere una capacidad cognitiva por sobre el promedio, "
            "con buen potencial para aprender procesos complejos, adaptarse a nuevas "
            "exigencias y resolver problemas bajo presión de forma autónoma."
        )
    elif "promedio" in level_str:
        return (
            "El desempeño global se ubica dentro de rangos funcionales habituales. "
            "Esto sugiere que la persona puede desempeñarse adecuadamente en la mayoría "
            "de las tareas operativas o administrativas estándar, con apoyo puntual "
            "en escenarios de alta complejidad o carga mental sostenida."
        )
    else:
        return (
            "El desempeño global sugiere que algunas tareas con alta demanda cognitiva "
            "podrían requerir acompañamiento inicial, supervisión más cercana o "
            "segmentar instrucciones en pasos claros y secuenciales."
        )

# -----------------------------------------------------------
# UTILIDADES DE PDF
# -----------------------------------------------------------

def wrap_text(c, text, max_width, font="Helvetica", size=8):
    """
    Envuelve texto en líneas según ancho en puntos.
    """
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if c.stringWidth(test, font, size) <= max_width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_paragraph(c, text, x, y, max_width, font="Helvetica", size=8, leading=11, color=colors.black, max_lines=None):
    """
    Dibuja párrafo envuelto. Devuelve nueva y final.
    """
    c.setFont(font, size)
    c.setFillColor(color)
    lines = wrap_text(c, text, max_width, font, size)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        c.drawString(x, y, ln)
        y -= leading
    return y

def draw_box_with_title(c, x, y_top, w, h, title, body_lines, body_font="Helvetica", body_size=8):
    """
    Dibuja una caja con título en negrita y líneas de texto debajo.
    body_lines es lista de strings ya envueltas o bullets.
    Devuelve y final.
    """
    # caja
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(x, y_top - h, w, h, stroke=1, fill=1)

    # título
    ty = y_top - 12
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.black)
    c.drawString(x + 8, ty, title)

    # cuerpo
    cy = ty - 12
    c.setFont(body_font, body_size)
    c.setFillColor(colors.black)
    for line in body_lines:
        # ajustar ancho
        wrapped = wrap_text(c, line, w - 16, body_font, body_size)
        for wln in wrapped:
            if cy < y_top - h + 10:
                break
            c.drawString(x + 8, cy, wln)
            cy -= 10
        if cy < y_top - h + 10:
            break

    return y_top - h

def generate_pdf(candidate_name,
                 evaluator_email,
                 fecha_eval,
                 raw_scores,
                 perc_scores,
                 level_str,
                 dim_desc,
                 fortalezas,
                 monitoreo,
                 global_summary):
    """
    Genera PDF en 2 páginas.
    Diseño:
      PÁGINA 1:
        - Header
        - Datos del candidato
        - Radar-like (tabla radial simulada a la izquierda)
        - Resumen cognitivo global (caja grande)

      PÁGINA 2:
        - Detalle por dimensión (cuadro ancho)
        - Fortalezas
        - Aspectos a observar
        - Nota metodológica
    """
    buf = BytesIO()
    W, H = A4  # ~595 x 842 pt
    c = canvas.Canvas(buf, pagesize=A4)

    # ------------------------
    # PÁGINA 1
    # ------------------------
    margin_left = 36
    margin_right = 36
    usable_w = W - margin_left - margin_right

    # Encabezado
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.black)
    c.drawString(margin_left, H - 40, "Informe de Evaluación Cognitiva General (IQ Screening)")
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.grey)
    c.drawRightString(W - margin_right, H - 40, "Uso interno RR.HH. / No clínico")

    # Datos del candidato (caja)
    box1_x = margin_left
    box1_y_top = H - 60
    box1_w = usable_w
    box1_h = 70

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(box1_x, box1_y_top - box1_h, box1_w, box1_h, stroke=1, fill=1)

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    c.drawString(box1_x + 8, box1_y_top - 14, "Datos del candidato")

    c.setFont("Helvetica", 8)
    c.drawString(box1_x + 8,  box1_y_top - 28, f"Nombre evaluado: {candidate_name}")
    c.drawString(box1_x + 8,  box1_y_top - 40, f"Fecha evaluación: {fecha_eval}")
    c.drawString(box1_x + 8,  box1_y_top - 52, f"Evaluador / Área responsable: {evaluator_email}")

    # Representación tipo "radar" + porcentajes por dimensión
    # En vez de gráfico poligonal real, mostramos una grilla clara:
    chart_x = margin_left
    chart_y_top = box1_y_top - box1_h - 16
    chart_w = usable_w * 0.45
    chart_h = 110

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(chart_x, chart_y_top - chart_h, chart_w, chart_h, stroke=1, fill=1)

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    c.drawString(chart_x + 8, chart_y_top - 14, "Resumen porcentual por dimensión (%)")

    # listado de dimensiones con su % y aciertos
    dims_list = ["RL", "QN", "VR", "MT", "AT"]
    dim_names = {
        "RL": "Lógico / Patrones",
        "QN": "Cuantitativo",
        "VR": "Verbal / Comprensión",
        "MT": "Memoria de trabajo",
        "AT": "Atención al detalle",
    }

    row_y = chart_y_top - 30
    c.setFont("Helvetica", 7)
    for d in dims_list:
        txt_dim = dim_names[d]
        txt_val = f"{perc_scores[d]:.0f}% ({raw_scores[d]}/{14})"
        c.drawString(chart_x + 8, row_y, f"{txt_dim}: {txt_val}")
        row_y -= 12

    # Nivel global
    c.setFont("Helvetica-Bold", 7)
    c.drawString(chart_x + 8, row_y - 4, f"Nivel global observado: {level_str}")

    # Caja grande con resumen cognitivo global
    summary_x = chart_x + chart_w + 16
    summary_w = usable_w - chart_w - 16
    summary_y_top = chart_y_top
    summary_h = chart_h

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(summary_x, summary_y_top - summary_h, summary_w, summary_h, stroke=1, fill=1)

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    c.drawString(summary_x + 8, summary_y_top - 14, "Resumen cognitivo observado")

    body_y = summary_y_top - 28
    body_y = draw_paragraph(
        c,
        global_summary,
        summary_x + 8,
        body_y,
        summary_w - 16,
        font="Helvetica",
        size=7,
        leading=10,
        color=colors.black,
        max_lines=None,
    )

    # Página 1 terminada
    c.showPage()

    # ------------------------
    # PÁGINA 2
    # ------------------------
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.black)
    c.drawString(margin_left, H - 40, "Detalle por dimensión cognitiva")

    # Tabla grande: Descripción por dimensión
    table_x = margin_left
    table_y_top = H - 60
    table_w = usable_w
    table_h = 200  # caja grande

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(table_x, table_y_top - table_h, table_w, table_h, stroke=1, fill=1)

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    c.drawString(table_x + 8, table_y_top - 14, "Desempeño por dimensión")

    row_y = table_y_top - 28
    c.setFont("Helvetica", 7)

    for d in dims_list:
        # Nombre dimensión y puntaje
        c.setFont("Helvetica-Bold", 7)
        c.drawString(table_x + 8, row_y, f"{dim_names[d]}  ({raw_scores[d]}/14 · {perc_scores[d]:.0f}%)")
        row_y -= 10
        c.setFont("Helvetica", 7)

        row_y = draw_paragraph(
            c,
            dim_desc[d],
            table_x + 16,
            row_y,
            table_w - 24,
            font="Helvetica",
            size=7,
            leading=10,
            color=colors.black,
            max_lines=None,
        )
        row_y -= 8
        if row_y < (table_y_top - table_h + 40):
            break

    # Cuadro Fortalezas / Aspectos a Observar en dos columnas
    col_box_h = 120
    col_box_w = (usable_w - 16) / 2.0
    col1_x = margin_left
    col2_x = margin_left + col_box_w + 16
    col_y_top = table_y_top - table_h - 20

    # Fortalezas
    fort_lines = ["Fortalezas identificadas:"] + [f"• {f}" for f in fortalezas] if fortalezas else ["Fortalezas identificadas:", "• Se observan fortalezas funcionales en áreas cognitivas evaluadas."]
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(col1_x, col_y_top - col_box_h, col_box_w, col_box_h, stroke=1, fill=1)

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    c.drawString(col1_x + 8, col_y_top - 14, "Fortalezas potenciales")
    yfort = col_y_top - 28
    c.setFont("Helvetica", 7)
    for line in fort_lines[1:]:
        wrapped = wrap_text(c, line, col_box_w - 16, "Helvetica", 7)
        for wln in wrapped:
            if yfort < col_y_top - col_box_h + 12:
                break
            c.drawString(col1_x + 8, yfort, wln)
            yfort -= 10
        if yfort < col_y_top - col_box_h + 12:
            break

    # Aspectos a observar
    mon_lines = ["Aspectos a monitorear / apoyo sugerido:"] + [f"• {m}" for m in monitoreo] if monitoreo else ["Aspectos a monitorear / apoyo sugerido:", "• Podría requerir apoyo en escenarios de alta carga cognitiva sostenida."]
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(col2_x, col_y_top - col_box_h, col_box_w, col_box_h, stroke=1, fill=1)

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    c.drawString(col2_x + 8, col_y_top - 14, "Aspectos a monitorear / apoyo sugerido")
    ymon = col_y_top - 28
    c.setFont("Helvetica", 7)
    for line in mon_lines[1:]:
        wrapped = wrap_text(c, line, col_box_w - 16, "Helvetica", 7)
        for wln in wrapped:
            if ymon < col_y_top - col_box_h + 12:
                break
            c.drawString(col2_x + 8, ymon, wln)
            ymon -= 10
        if ymon < col_y_top - col_box_h + 12:
            break

    # Nota metodológica (caja completa al final)
    note_box_y_top = col_y_top - col_box_h - 20
    note_box_h = 100

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(margin_left, note_box_y_top - note_box_h, usable_w, note_box_h, stroke=1, fill=1)

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    c.drawString(margin_left + 8, note_box_y_top - 14, "Nota metodológica")

    nota_text = (
        "Este informe se basa en las respuestas del evaluado en un test cognitivo breve. "
        "Los resultados describen tendencias de razonamiento lógico, numérico, verbal, "
        "memoria de trabajo y atención al detalle en el momento de la evaluación. "
        "No constituye un diagnóstico clínico ni es la única base de decisión laboral. "
        "Se sugiere complementar con entrevista estructurada, verificación de experiencia "
        "y evaluación técnica específica del cargo."
    )

    draw_paragraph(
        c,
        nota_text,
        margin_left + 8,
        note_box_y_top - 28,
        usable_w - 16,
        font="Helvetica",
        size=7,
        leading=10,
        color=colors.black,
        max_lines=None,
    )

    # Footer
    c.setFont("Helvetica", 6)
    c.setFillColor(colors.grey)
    c.drawRightString(W - margin_right, 30, "Evaluación Cognitiva General · Uso interno RR.HH. · No clínico")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()

# -----------------------------------------------------------
# EMAIL
# -----------------------------------------------------------

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

# -----------------------------------------------------------
# FINALIZAR, GENERAR, ENVIAR
# -----------------------------------------------------------

def finalize_and_send():
    raw_scores, perc_scores = compute_dimension_scores(st.session_state.answers)
    level_str = overall_level(perc_scores)
    dim_desc = build_dim_description(perc_scores)
    fortalezas, monitoreo = build_strengths_and_risks(perc_scores)
    global_summary = cognitive_summary_text(level_str)

    now_txt = datetime.now().strftime("%d/%m/%Y %H:%M")

    pdf_bytes = generate_pdf(
        candidate_name   = st.session_state.candidate_name,
        evaluator_email  = st.session_state.evaluator_email,
        fecha_eval       = now_txt,
        raw_scores       = raw_scores,
        perc_scores      = perc_scores,
        level_str        = level_str,
        dim_desc         = dim_desc,
        fortalezas       = fortalezas,
        monitoreo        = monitoreo,
        global_summary   = global_summary,
    )

    if not st.session_state.already_sent:
        try:
            send_email_with_pdf(
                to_email   = st.session_state.evaluator_email,
                pdf_bytes  = pdf_bytes,
                filename   = "Informe_Cognitivo.pdf",
                subject    = "Informe Evaluación Cognitiva (IQ Screening)",
                body_text  = (
                    "Adjunto informe de evaluación cognitiva general "
                    f"({st.session_state.candidate_name}). Uso interno RR.HH."
                ),
            )
        except Exception:
            # No interrumpimos la app si hay problema de correo.
            pass
        st.session_state.already_sent = True

# -----------------------------------------------------------
# CALLBACK SELECCIÓN DE RESPUESTA
# -----------------------------------------------------------

def choose_answer(option_index: int):
    q_idx = st.session_state.current_q
    st.session_state.answers[q_idx] = option_index

    if q_idx < TOTAL_QUESTIONS - 1:
        st.session_state.current_q += 1
        st.session_state._need_rerun = True
    else:
        finalize_and_send()
        st.session_state.stage = "done"
        st.session_state._need_rerun = True

# -----------------------------------------------------------
# VISTAS UI
# -----------------------------------------------------------

def view_info_form():
    st.markdown("### Evaluación Cognitiva General (IQ Screening)")
    st.info("Estos datos se usan para generar el informe PDF interno y enviarlo automáticamente al evaluador.")

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

    # Header estilizado
    st.markdown(
        f"""
        <div style="
            background:linear-gradient(to right,#1e3a8a,#4338ca);
            color:white;
            border-radius:12px 12px 0 0;
            padding:16px 20px;
            display:flex;
            justify-content:space-between;
            align-items:center;
            flex-wrap:wrap;">
            <div style="font-weight:700;">
                Test Cognitivo General (IQ) · {TOTAL_QUESTIONS} ítems
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

    # Opciones de respuesta (4 alternativas)
    # Dos columnas (2 y 2) para orden visual limpio
    cols = st.columns(2)
    for i, opt in enumerate(q["options"]):
        cols[i % 2].button(
            opt,
            key=f"q{q_idx}_opt{i}",
            on_click=choose_answer,
            args=(i,),
            use_container_width=True
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
            <b>Confidencialidad:</b> Uso interno RR.HH. / Selección inicial.
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

# -----------------------------------------------------------
# RENDER FLOW
# -----------------------------------------------------------

if st.session_state.stage == "info":
    view_info_form()

elif st.session_state.stage == "test":
    if st.session_state.current_q >= TOTAL_QUESTIONS:
        st.session_state.stage = "done"
        st.session_state._need_rerun = True
    else:
        view_test()

elif st.session_state.stage == "done":
    # asegurar PDF enviado / no reenviar en loop
    finalize_and_send()
    view_done()

# control de rerun suave
if st.session_state._need_rerun:
    st.session_state._need_rerun = False
    st.rerun()
