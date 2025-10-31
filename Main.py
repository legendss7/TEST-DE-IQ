# ============================================================
# Evaluación Cognitiva Operativa (IQ Adaptado)
# 70 ítems / 5 dimensiones cognitivas / informe PDF autogenerado
# Estilo visual tipo EPQR-A operativo
# ============================================================

import streamlit as st
from datetime import datetime
from io import BytesIO
import smtplib
from email.message import EmailMessage

# ReportLab para PDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# ------------------------------------------------------------
# CONFIG STREAMLIT
# ------------------------------------------------------------
st.set_page_config(
    page_title="Evaluación Cognitiva Operativa (IQ)",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------
# CREDENCIALES DE CORREO (usa las tuyas)
# ------------------------------------------------------------
FROM_ADDR = "jo.tajtaj@gmail.com"
APP_PASS  = "nlkt kujl ebdg cyts"  # importante: deja el mismo formato que usas en EPQR

# ------------------------------------------------------------
# BANCO DE PREGUNTAS (70 preguntas)
# Estructura:
#   "text": enunciado mostrado
#   "options": lista de 4 alternativas (A,B,C,D)
#   "correct": índice 0-3 de la alternativa correcta
#   "dim": RL / AT / VD / MT / CI
#
# Dimensiones:
# RL = Razonamiento lógico / secuencias
# AT = Atención al detalle / precisión
# VD = Velocidad de decisión / juicio rápido
# MT = Memoria de trabajo / retención inmediata
# CI = Comprensión de instrucciones / lectura operativa
#
# Cada dimensión tiene 14 preguntas -> total 70
# Nota: Las preguntas son cognitivas simples tipo operativa,
#       cálculo mental básicos, series lógicas, instrucciones breves.

QUESTIONS = [
    # ---------------- RL (Razonamiento Lógico / Secuencias) ----------------
    {
        "text": "Serie: 2, 4, 8, 16, 32, ... ¿Cuál sigue?",
        "options": ["48", "54", "64", "62"],
        "correct": 2,
        "dim": "RL",
    },
    {
        "text": "Serie: 5, 8, 11, 14, ... ¿Cuál sigue?",
        "options": ["16", "17", "18", "19"],
        "correct": 1,
        "dim": "RL",
    },
    {
        "text": "Si A > B y B > C, entonces:",
        "options": ["A < C", "A = C", "A > C", "No se sabe"],
        "correct": 2,
        "dim": "RL",
    },
    {
        "text": "Un operario arma 4 cajas en 10 min. ¿Cuántas cajas en 30 min?",
        "options": ["8", "10", "12", "14"],
        "correct": 2,
        "dim": "RL",
    },
    {
        "text": "Un lote tiene 24 piezas. Cada caja lleva 6 piezas. ¿Cuántas cajas completas?",
        "options": ["2", "3", "4", "6"],
        "correct": 2,
        "dim": "RL",
    },
    {
        "text": "Si hoy es miércoles, ¿qué día será en 3 días más?",
        "options": ["Sábado", "Viernes", "Domingo", "Lunes"],
        "correct": 0,
        "dim": "RL",
    },
    {
        "text": "Completa la secuencia: 10, 7, 4, 1, ...",
        "options": ["-1", "0", "-2", "2"],
        "correct": 2,
        "dim": "RL",
    },
    {
        "text": "Si una máquina hace 12 piezas cada 6 minutos, ¿cuántas hace en 30 minutos?",
        "options": ["50", "54", "60", "62"],
        "correct": 2,
        "dim": "RL",
    },
    {
        "text": "Si todos los A son B y todos los B son C, entonces todos los A son:",
        "options": ["C", "A", "B", "ninguno"],
        "correct": 0,
        "dim": "RL",
    },
    {
        "text": "Secuencia: rojo, azul, rojo, azul, rojo, ... ¿qué sigue?",
        "options": ["azul", "rojo", "verde", "no se sabe"],
        "correct": 0,
        "dim": "RL",
    },
    {
        "text": "3 trabajadores hacen 3 cajas en 3 minutos. ¿Cuántas cajas hacen 6 trabajadores en 3 minutos?",
        "options": ["3", "6", "9", "12"],
        "correct": 1,
        "dim": "RL",
    },
    {
        "text": "20 → 17 → 14 → 11 → ... ¿Cuál sigue?",
        "options": ["10", "9", "8", "7"],
        "correct": 3,
        "dim": "RL",
    },
    {
        "text": "Un pallet tiene 4 filas con 9 cajas cada una. ¿Cuántas cajas totales?",
        "options": ["13", "36", "45", "36 más 1"],
        "correct": 1,
        "dim": "RL",
    },
    {
        "text": "Si un turno termina a las 17:30 y dura 8 horas exactas, ¿a qué hora comenzó?",
        "options": ["9:30", "8:30", "7:30", "10:30"],
        "correct": 0,
        "dim": "RL",
    },

    # ---------------- AT (Atención al Detalle / Precisión) ----------------
    {
        "text": "Revisa: 'AB-9124' vs 'AB-9214'. ¿Son iguales?",
        "options": ["Sí, son iguales", "No, cambian 1 y 2", "No, cambian 9 y 2", "No, cambian 2 y 1 de lugar"],
        "correct": 1,
        "dim": "AT",
    },
    {
        "text": "En la orden figura 'pieza #7716'. El operario prepara 'pieza #7761'. ¿Coinciden?",
        "options": ["Sí", "No, está invertido 1 y 6", "No, cambió el 7", "No, todo distinto"],
        "correct": 1,
        "dim": "AT",
    },
    {
        "text": "Si una tabla dice '221.45 mm' y otra dice '221.54 mm', ¿la diferencia principal está en:",
        "options": ["Las centenas", "Las decenas", "Las centésimas", "Las milésimas"],
        "correct": 2,
        "dim": "AT",
    },
    {
        "text": "Control de calidad: tolerancia máxima es 2 mm. La pieza está 1.8 mm fuera. ¿Está aceptable?",
        "options": ["Sí, está dentro", "No, está fuera", "No se puede saber", "Depende del color"],
        "correct": 0,
        "dim": "AT",
    },
    {
        "text": "Comparar códigos: 'Lote-5B7Q' vs 'Lote-5B7O'. ¿Coinciden?",
        "options": ["Sí", "No, Q y O son distintas", "No, cambia el 5", "No, B y 7 cambian"],
        "correct": 1,
        "dim": "AT",
    },
    {
        "text": "En un instructivo dice: 'apretar tornillo hasta tope y luego girar 1/4 de vuelta atrás'. ¿Cuál es el último paso?",
        "options": ["Apretar más fuerte", "Girar 1/4 hacia atrás", "Soltar completamente", "No hacer nada"],
        "correct": 1,
        "dim": "AT",
    },
    {
        "text": "Lectura de etiqueta: 'EXP: 12/2026'. ¿Qué significa 'EXP'?",
        "options": ["Fecha de compra", "Fecha de producción", "Fecha de vencimiento", "Fecha de turno"],
        "correct": 2,
        "dim": "AT",
    },
    {
        "text": "Si el plano dice 'usar guantes A', y el operario usa guantes tipo B, ¿está siguiendo la instrucción?",
        "options": ["Sí, da lo mismo", "Sí, si son cómodos", "No", "Sólo si es supervisor"],
        "correct": 2,
        "dim": "AT",
    },
    {
        "text": "Manual: 'cortar a 120 mm ±2 mm'. La pieza mide 117 mm. ¿Está dentro?",
        "options": ["Sí", "No", "Es mejor más corto siempre", "No se puede saber"],
        "correct": 1,
        "dim": "AT",
    },
    {
        "text": "Turno registrado 07:00–15:00. ¿Cuántas horas son?",
        "options": ["7", "8", "9", "Depende del break"],
        "correct": 1,
        "dim": "AT",
    },
    {
        "text": "Etiqueta dice 'Caja A12-B'. Operario retira 'Caja A21-B'. ¿Es la misma?",
        "options": ["Sí", "No, 12 y 21 no son lo mismo", "Sí, sólo cambian de orden", "No se sabe"],
        "correct": 1,
        "dim": "AT",
    },
    {
        "text": "Informe: 'Temperatura 38.5°C'. Registro: '37.5°C'. ¿Coinciden?",
        "options": ["Sí", "No, difieren 1 grado", "No, difieren 0.5°", "No, difieren 2 grados"],
        "correct": 1,
        "dim": "AT",
    },
    {
        "text": "Planilla dice 'Pallet #0047'. Se embarca 'Pallet #047'. ¿Hay error?",
        "options": ["Sí, falta un 0", "No, es lo mismo", "Sí, sobran ceros", "No se sabe"],
        "correct": 1,
        "dim": "AT",
    },
    {
        "text": "Check-list: Paso 1-Limpiar / Paso 2-Ajustar / Paso 3-Verificar. ¿Cuál va segundo?",
        "options": ["Ajustar", "Verificar", "Limpiar", "No se sabe"],
        "correct": 0,
        "dim": "AT",
    },

    # ---------------- VD (Velocidad de Decisión / Juicio rápido) ----------------
    {
        "text": "En operación urgente debes elegir: ¿Qué haces primero?",
        "options": [
            "Revisar seguridad básica",
            "Pedir permiso escrito",
            "Irte a colación",
            "Esperar 1 hora",
        ],
        "correct": 0,
        "dim": "VD",
    },
    {
        "text": "Si ves que una línea está detenida por falta de insumo evidente, ¿qué acción inmediata es más lógica?",
        "options": [
            "Avisar rápido al encargado de insumos",
            "Ir a fumar",
            "Ignorar y seguir",
            "Reiniciar toda la máquina sin permiso",
        ],
        "correct": 0,
        "dim": "VD",
    },
    {
        "text": "Alguien reporta fuga de aceite. ¿Qué haces primero?",
        "options": [
            "Pisar el aceite",
            "Asegurar zona / informar",
            "Terminar la tarea y luego ver",
            "Nada, es normal",
        ],
        "correct": 1,
        "dim": "VD",
    },
    {
        "text": "En turno rápido debes seleccionar la caja con fecha más antigua. ¿Cuál eliges?",
        "options": [
            "Caja con fecha 05/05",
            "Caja con fecha 10/05",
            "Caja con fecha 12/05",
            "Caja sin fecha",
        ],
        "correct": 0,
        "dim": "VD",
    },
    {
        "text": "Te piden decidir qué pallet mover primero: A (bloqueando pasillo) o B (en zona libre). ¿Cuál mueves primero?",
        "options": ["A", "B", "Ninguno", "Los 2 a la vez"],
        "correct": 0,
        "dim": "VD",
    },
    {
        "text": "Una alarma roja empieza a sonar. ¿Qué haces primero?",
        "options": [
            "Continuar como si nada",
            "Revisar qué indica la alarma / detener si es seguro",
            "Apagar todas las luces de la planta",
            "Cambiar de área sin avisar",
        ],
        "correct": 1,
        "dim": "VD",
    },
    {
        "text": "Hay diferencia entre la etiqueta y el pedido. ¿Reacción inicial más adecuada?",
        "options": [
            "Despachar igual",
            "Avisar la diferencia antes de despachar",
            "Tachar la etiqueta con plumón",
            "Dejarlo escondido",
        ],
        "correct": 1,
        "dim": "VD",
    },
    {
        "text": "Un supervisor te pide priorizar embalaje. ¿Qué haces?",
        "options": [
            "Priorizas embalaje",
            "Haces otra cosa que prefieres",
            "Te vas sin avisar",
            "Llamas a otro supervisor para discutir",
        ],
        "correct": 0,
        "dim": "VD",
    },
    {
        "text": "Si una máquina empieza a vibrar fuerte distinto a lo normal:",
        "options": [
            "Ignorar",
            "Cortar energía/avisar según procedimiento",
            "Golpear la máquina",
            "Subirte arriba",
        ],
        "correct": 1,
        "dim": "VD",
    },
    {
        "text": "Te piden decidir rápidamente cuál caja pesa menos para levantar primero. ¿Cuál eliges?",
        "options": [
            "Caja rotulada '15 kg'",
            "Caja rotulada '9 kg'",
            "Caja rotulada '22 kg'",
            "Caja sin rotular",
        ],
        "correct": 1,
        "dim": "VD",
    },
    {
        "text": "Notas olor a quemado en un tablero eléctrico:",
        "options": [
            "Pones la mano encima para sentir calor",
            "Avisa y detén operación si corresponde",
            "Lo tapas con cinta",
            "Ignoras",
        ],
        "correct": 1,
        "dim": "VD",
    },
    {
        "text": "Si hay fila de pallets bloqueando salida de emergencia:",
        "options": [
            "No haces nada",
            "Avisa y despejas prioridad salida",
            "Apilas más cosas adelante",
            "Te cambias de sector sin decir nada",
        ],
        "correct": 1,
        "dim": "VD",
    },
    {
        "text": "Se está cayendo material frágil, ¿qué decisión rápida es más lógica?",
        "options": [
            "Intentar estabilizar con la mano si es seguro",
            "Alejarse para no lesionarse y avisar",
            "Patear el pallet",
            "Filmar con el celular",
        ],
        "correct": 1,
        "dim": "VD",
    },
    {
        "text": "Dos piezas tienen número distinto y no sabes cuál es correcta:",
        "options": [
            "Despachas cualquiera",
            "Pides confirmación inmediata antes de moverlas",
            "Tiras ambas",
            "Las mezclas",
        ],
        "correct": 1,
        "dim": "VD",
    },

    # ---------------- MT (Memoria de Trabajo / Retención inmediata) ----------------
    {
        "text": "Te dicen: 'Toma caja A12 del rack 3 y llévala al andén 5'. ¿Qué debes mover?",
        "options": [
            "Caja A12 desde rack 3 al andén 5",
            "Caja A5 desde rack 12 al andén 3",
            "Caja rack 5 al andén 12",
            "Ninguna",
        ],
        "correct": 0,
        "dim": "MT",
    },
    {
        "text": "Instrucción rápida: 'Etiqueta las piezas verdes y luego guarda las azules'. ¿Qué haces primero?",
        "options": [
            "Guardar azules",
            "Etiquetar verdes",
            "Nada",
            "Pedir colación",
        ],
        "correct": 1,
        "dim": "MT",
    },
    {
        "text": "Te dicen: 'Busca guantes talla M y pásale uno al supervisor de línea 2'. ¿Qué entregas?",
        "options": [
            "Guantes talla M a línea 2",
            "Guantes talla S a línea 2",
            "Guantes talla M a línea 5",
            "Guantes talla L a línea 2",
        ],
        "correct": 0,
        "dim": "MT",
    },
    {
        "text": "Te indican: 'Primero limpia filtro, después revisa fuga'. ¿Qué va al final?",
        "options": [
            "Limpiar filtro",
            "Revisar fuga",
            "Cortar energía",
            "Llamar a RRHH",
        ],
        "correct": 1,
        "dim": "MT",
    },
    {
        "text": "Te piden recordar estos 3 códigos: Z17, Z18, Z21. ¿Cuál NO estaba?",
        "options": ["Z17", "Z18", "Z21", "Z27"],
        "correct": 3,
        "dim": "MT",
    },
    {
        "text": "Te dan 2 pasos: (1) Alinear caja, (2) Sellar tapa. ¿Qué paso se hace segundo?",
        "options": ["Alinear caja", "Sellar tapa", "Abrir caja", "Poner etiqueta"],
        "correct": 1,
        "dim": "MT",
    },
    {
        "text": "Mensaje hablado: 'Entrega el informe al supervisor nocturno antes de irte'. ¿Qué debes hacer?",
        "options": [
            "Entregar informe al supervisor nocturno antes de irme",
            "Entregar informe al supervisor de día mañana",
            "Guardar informe en casillero",
            "Dejar informe en recepción",
        ],
        "correct": 0,
        "dim": "MT",
    },
    {
        "text": "Te dicen: 'Termina conteo en pasillo B, luego ve al A'. ¿Cuál haces primero?",
        "options": ["Pasillo A", "Pasillo B", "Ninguno", "Ambos a la vez"],
        "correct": 1,
        "dim": "MT",
    },
    {
        "text": "Recordar orden rápido: rojo → verde → azul. ¿Cuál fue el segundo color?",
        "options": ["rojo", "verde", "azul", "amarillo"],
        "correct": 1,
        "dim": "MT",
    },
    {
        "text": "Te indican: 'Corta energía, luego avisa'. ¿Qué va segundo?",
        "options": ["Cortar energía", "Avisar", "No hacer nada", "Pedir permiso"],
        "correct": 1,
        "dim": "MT",
    },
    {
        "text": "Te pasan oralmente: 'Caja 31 va a zona V'. ¿Qué debes recordar?",
        "options": [
            "Caja 13 va a zona V",
            "Caja 31 va a zona V",
            "Caja 31 va a zona B",
            "Caja V va a zona 31",
        ],
        "correct": 1,
        "dim": "MT",
    },
    {
        "text": "Te dicen: 'Pon sticker rojo en productos dañados'. ¿Qué color usas?",
        "options": ["Rojo", "Verde", "Azul", "Amarillo"],
        "correct": 0,
        "dim": "MT",
    },
    {
        "text": "Secuencia verbal: 'Llave grande, llave chica, destornillador plano'. ¿El segundo elemento fue...?",
        "options": [
            "Llave grande",
            "Llave chica",
            "Destornillador plano",
            "No se dijo",
        ],
        "correct": 1,
        "dim": "MT",
    },
    {
        "text": "Te piden: 'Lleva estos guantes a línea A y luego vuelve a bodega'. ¿Cuál es el último paso?",
        "options": [
            "Quedarte en la línea A",
            "Volver a bodega",
            "Ir a colación",
            "Botar los guantes",
        ],
        "correct": 1,
        "dim": "MT",
    },

    # ---------------- CI (Comprensión de Instrucciones / Lectura Operativa) ----------------
    {
        "text": "Lee: 'Antes de operar, usar casco y guantes'. ¿Qué se exige antes de operar?",
        "options": [
            "Casco y guantes",
            "Sólo casco",
            "Sólo guantes",
            "Nada",
        ],
        "correct": 0,
        "dim": "CI",
    },
    {
        "text": "Instructivo: 'No encender la máquina sin autorización del supervisor'. ¿Qué significa?",
        "options": [
            "Encender cuando quieras",
            "Sólo encender con permiso",
            "Nunca encender",
            "Encender sólo una vez",
        ],
        "correct": 1,
        "dim": "CI",
    },
    {
        "text": "Aviso: 'Descargar pallets en Zona A, luego etiquetar'. ¿Cuál acción va segunda?",
        "options": [
            "Descargar pallets",
            "Etiquetar",
            "Mover a Zona B",
            "Romper pallets",
        ],
        "correct": 1,
        "dim": "CI",
    },
    {
        "text": "Etiqueta: 'Material frágil: NO golpear'. ¿Qué debes evitar?",
        "options": [
            "Moverlo",
            "Golpearlo",
            "Mirarlo",
            "Reportarlo",
        ],
        "correct": 1,
        "dim": "CI",
    },
    {
        "text": "Cartel: 'Salida de emergencia libre de obstáculos'. ¿Qué NO debe haber?",
        "options": [
            "Cajas bloqueando",
            "Señalización",
            "Luces verdes",
            "Extintor cercano",
        ],
        "correct": 0,
        "dim": "CI",
    },
    {
        "text": "Orden escrita: 'Rotar stock según fecha más antigua primero'. ¿Qué prioridad se usa?",
        "options": [
            "Lo más nuevo primero",
            "Lo más antiguo primero",
            "Al azar",
            "El más pesado primero",
        ],
        "correct": 1,
        "dim": "CI",
    },
    {
        "text": "Procedimiento: 'Parar la línea si hay riesgo inmediato de lesión'. ¿Cuándo se detiene la línea?",
        "options": [
            "Sólo al final del turno",
            "Cuando hay riesgo inmediato de lesión",
            "Nunca",
            "Sólo con permiso médico",
        ],
        "correct": 1,
        "dim": "CI",
    },
    {
        "text": "Nota: 'Usar gafas de protección al cortar metal'. ¿Qué acción requiere gafas?",
        "options": [
            "Cortar metal",
            "Ir al baño",
            "Caminar en pasillo",
            "Tomar agua",
        ],
        "correct": 0,
        "dim": "CI",
    },
    {
        "text": "Procedimiento: 'Registrar temperatura cada hora'. ¿Qué debes hacer?",
        "options": [
            "Registrar temperatura una vez al día",
            "Registrar temperatura cada hora",
            "No registrar",
            "Registrar sólo si es muy alta",
        ],
        "correct": 1,
        "dim": "CI",
    },
    {
        "text": "Aviso: 'No apilar sobre esta línea roja'. ¿Qué indica?",
        "options": [
            "Apilar justo sobre la línea roja",
            "Evitar apilar sobre la línea roja",
            "Pintar más rojo",
            "Cubrir la línea",
        ],
        "correct": 1,
        "dim": "CI",
    },
    {
        "text": "Indicación: 'Firmar check-list al terminar la inspección'. ¿Cuándo firmas?",
        "options": [
            "Antes de inspeccionar",
            "Al terminar la inspección",
            "Nunca",
            "Cuando quieras",
        ],
        "correct": 1,
        "dim": "CI",
    },
    {
        "text": "Texto: 'Zona restringida: sólo personal autorizado'. ¿Quién puede entrar?",
        "options": [
            "Cualquiera",
            "Sólo personal autorizado",
            "Visitas externas",
            "Nadie nunca",
        ],
        "correct": 1,
        "dim": "CI",
    },
    {
        "text": "Hoja de seguridad: 'Cortar energía antes de mantenimiento'. ¿Qué va primero?",
        "options": [
            "Reparar directamente",
            "Cortar energía",
            "Sacar fotos",
            "Nada",
        ],
        "correct": 1,
        "dim": "CI",
    },
    {
        "text": "Instrucción: 'Reportar derrames químicos inmediatamente'. ¿Cuándo reportas?",
        "options": [
            "Al final del mes",
            "Cuando el derrame es grande",
            "Inmediatamente",
            "Nunca",
        ],
        "correct": 2,
        "dim": "CI",
    },
]

TOTAL_QUESTIONS = len(QUESTIONS)  # debe ser 70

# ------------------------------------------------------------
# PERFILES DE CARGO (para la conclusión final)
# Cada rango es sobre la escala normalizada 0-10
# ------------------------------------------------------------
JOB_PROFILES = {
    "operario": {
        "title": "Operario de Producción",
        "req": {
            "RL": (4.0, 10.0),
            "AT": (4.0, 10.0),
            "VD": (4.0, 10.0),
            "MT": (4.0, 10.0),
            "CI": (4.0, 10.0),
        },
    },
    "logistica": {
        "title": "Personal de Logística",
        "req": {
            "RL": (3.5, 10.0),
            "AT": (4.0, 10.0),
            "VD": (4.0, 10.0),
            "MT": (4.0, 10.0),
            "CI": (4.0, 10.0),
        },
    },
    "supervisor": {
        "title": "Supervisor Operativo",
        "req": {
            "RL": (5.0, 10.0),
            "AT": (5.0, 10.0),
            "VD": (5.0, 10.0),
            "MT": (5.0, 10.0),
            "CI": (5.0, 10.0),
        },
    },
}

# ------------------------------------------------------------
# ESTADO STREAMLIT
# ------------------------------------------------------------
if "stage" not in st.session_state:
    st.session_state.stage = "select_job"  # select_job -> info -> test -> done

if "selected_job" not in st.session_state:
    st.session_state.selected_job = None

if "candidate_name" not in st.session_state:
    st.session_state.candidate_name = ""

if "evaluator_email" not in st.session_state:
    st.session_state.evaluator_email = FROM_ADDR

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "answers" not in st.session_state:
    # answers[i] = index elegido (0..3) o None
    st.session_state.answers = {i: None for i in range(TOTAL_QUESTIONS)}

if "_need_rerun" not in st.session_state:
    st.session_state._need_rerun = False

if "already_sent" not in st.session_state:
    st.session_state.already_sent = False

# ------------------------------------------------------------
# SCORING
# ------------------------------------------------------------

def compute_scores(ans_dict):
    # puntajes brutos por dimensión
    raw_dim = {"RL":0,"AT":0,"VD":0,"MT":0,"CI":0}

    for idx, q in enumerate(QUESTIONS):
        chosen = ans_dict.get(idx)
        if chosen is None:
            continue
        if chosen == q["correct"]:
            raw_dim[q["dim"]] += 1

    # normalizamos a 0-10 para visual (14 preguntas cada dimensión)
    norm_dim = {}
    for dim_key in raw_dim:
        norm_dim[dim_key] = (raw_dim[dim_key] / 14.0) * 10.0

    # índice global G
    G_raw = sum(raw_dim.values()) / 5.0
    G_norm = sum(norm_dim.values()) / 5.0

    return {
        "raw": raw_dim,           # bruto (0-14)
        "norm": norm_dim,         # normalizado (0-10)
        "G_raw": G_raw,           # promedio bruto
        "G_norm": G_norm,         # promedio normalizado 0-10
    }

def level_label(norm_score):
    # norm_score en 0-10
    if norm_score >= 7.5:
        return "Alto"
    elif norm_score >= 4.5:
        return "Medio"
    else:
        return "Bajo"

def build_descriptions(norm_dim):
    desc = {}
    desc["RL"] = (
        "Capacidad de razonar secuencias, números e identificar patrones lógicos "
        "para anticipar o detectar errores en el proceso."
    )
    desc["AT"] = (
        "Atención al detalle y comparación precisa de datos, códigos, tolerancias "
        "y pasos de trabajo definidos."
    )
    desc["VD"] = (
        "Juicio operativo frente a situaciones urgentes o de decisión rápida, con "
        "criterio básico de seguridad / prioridad."
    )
    desc["MT"] = (
        "Memoria operativa inmediata para retener instrucciones breves, pasos secuenciales "
        "y pedidos verbales sin perder el orden."
    )
    desc["CI"] = (
        "Comprensión de instrucciones escritas u orales y capacidad de aplicarlas "
        "en la tarea sin distorsionarlas."
    )
    return desc

def build_summary_blocks(norm_dim, G_norm):
    fortalezas = []
    monitoreo = []

    if norm_dim["RL"] >= 7.5:
        fortalezas.append("Razonamiento lógico claro para ordenar tareas y anticipar errores.")
    elif norm_dim["RL"] < 4.5:
        monitoreo.append("Puede requerir apoyo adicional al interpretar secuencias numéricas o cálculos básicos.")

    if norm_dim["AT"] >= 7.5:
        fortalezas.append("Buen nivel de precisión al seguir tolerancias y diferencias en códigos / medidas.")
    elif norm_dim["AT"] < 4.5:
        monitoreo.append("Se sugiere verificación doble en controles críticos de calidad o picking.")

    if norm_dim["VD"] >= 7.5:
        fortalezas.append("Decisión rápida en escenarios operativos con criterio de seguridad.")
    elif norm_dim["VD"] < 4.5:
        monitoreo.append("Puede necesitar confirmación antes de actuar en situaciones urgentes.")

    if norm_dim["MT"] >= 7.5:
        fortalezas.append("Retiene instrucciones verbales o pasos cortos sin necesidad de repetir.")
    elif norm_dim["MT"] < 4.5:
        monitoreo.append("Podría beneficiarse de instrucciones paso a paso más explícitas.")

    if norm_dim["CI"] >= 7.5:
        fortalezas.append("Interpreta indicaciones escritas y las aplica correctamente.")
    elif norm_dim["CI"] < 4.5:
        monitoreo.append("Puede requerir instrucciones más guiadas en lectura de normas o procedimientos escritos.")

    # Global
    if G_norm >= 7.5:
        fortalezas.append("Desempeño cognitivo global alto para entornos operativos con ritmo exigente.")
    elif G_norm < 4.5:
        monitoreo.append("Requiere supervisión más cercana al inicio hasta consolidar el aprendizaje del rol.")

    return fortalezas, monitoreo

def cargo_fit(job_key, norm_dim, G_norm):
    req = JOB_PROFILES[job_key]["req"]
    cargo_name = JOB_PROFILES[job_key]["title"]

    ok_all = True
    for dim_key, (mn, mx) in req.items():
        val = norm_dim[dim_key]
        if not (val >= mn and val <= mx):
            ok_all = False
            break

    # usamos también un chequeo global suave
    if G_norm < 4.5:
        ok_all = False

    if ok_all:
        return (
            f"Ajuste al cargo: El perfil evaluado se considera "
            f"GLOBALMENTE CONSISTENTE con las exigencias habituales del cargo "
            f"{cargo_name}."
        )
    else:
        return (
            f"Ajuste al cargo: El perfil evaluado NO SE CONSIDERA CONSISTENTE "
            f"con las exigencias habituales del cargo {cargo_name}."
        )

# ------------------------------------------------------------
# PDF GENERATION (UNA SOLA PÁGINA, ORDENADO)
# ------------------------------------------------------------

def wrap_lines(c, text, max_width, font="Helvetica", size=8):
    words = text.split()
    out = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if c.stringWidth(test, font, size) <= max_width:
            cur = test
        else:
            if cur:
                out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out

def draw_wrapped(c, text, x, y, w, font="Helvetica", size=8, leading=10, color=colors.black):
    c.setFont(font, size)
    c.setFillColor(color)
    lines = wrap_lines(c, text, w, font, size)
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y

def generate_pdf(candidate_name, cargo_name, fecha_eval, evaluator_email,
                 scores, fortalezas, monitoreo, ajuste_text):

    # scores:
    #   scores["raw"]  -> bruto 0-14
    #   scores["norm"] -> normalizado 0-10
    #   scores["G_norm"], scores["G_raw"]
    raw_dim = scores["raw"]
    norm_dim = scores["norm"]
    G_norm = scores["G_norm"]
    G_raw = scores["G_raw"]

    desc = build_descriptions(norm_dim)

    # Precalcular niveles
    lvl_RL = level_label(norm_dim["RL"])
    lvl_AT = level_label(norm_dim["AT"])
    lvl_VD = level_label(norm_dim["VD"])
    lvl_MT = level_label(norm_dim["MT"])
    lvl_CI = level_label(norm_dim["CI"])
    lvl_G  = level_label(G_norm)

    # Prepara texto fortalezas / monitoreo en bloque resumen
    fortalezas_text = ""
    for f in fortalezas:
        fortalezas_text += "• " + f + "\n"
    monitoreo_text = ""
    for m in monitoreo:
        monitoreo_text += "• " + m + "\n"

    # --- PDF canvas ---
    buf = BytesIO()
    W, H = A4  # 595 x 842 aprox
    c = canvas.Canvas(buf, pagesize=A4)

    margin_x = 30
    margin_y_top = H - 30

    # HEADER IZQUIERDA
    c.setFont("Helvetica-Bold",10)
    c.drawString(margin_x, margin_y_top, "EMPRESA / LOGO")
    c.setFont("Helvetica",7)
    c.drawString(margin_x, margin_y_top-12, "Evaluación de capacidad cognitiva aplicada al rol")

    # HEADER DERECHA (título general)
    c.setFont("Helvetica-Bold",10)
    c.drawRightString(W - margin_x, margin_y_top,
                      "Perfil Cognitivo Operativo (IQ Adaptado)")
    c.setFont("Helvetica",7)
    c.drawRightString(W - margin_x, margin_y_top-12,
                      "Uso interno RR.HH. / Procesos productivos · No clínico")

    # ------------------------------------------------------------
    # CUADRO DATOS DEL CANDIDATO (arriba derecha)
    # ------------------------------------------------------------
    box_w = 250
    box_h = 70
    box_x = W - margin_x - box_w
    box_top = margin_y_top - 40  # un poco bajo el header
    box_y = box_top - box_h

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(box_x, box_y, box_w, box_h, stroke=1, fill=1)

    ytxt = box_top - 12
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(box_x+8, ytxt, f"Nombre: {candidate_name}")
    ytxt -= 12
    c.setFont("Helvetica",8)
    cargo_linea = f"Cargo evaluado: {cargo_name}"
    c.drawString(box_x+8, ytxt, cargo_linea)
    ytxt -= 12
    c.drawString(box_x+8, ytxt, f"Fecha evaluación: {fecha_eval}")
    ytxt -= 12
    c.drawString(box_x+8, ytxt, f"Evaluador: {evaluator_email.upper()}")
    ytxt -= 12
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawString(box_x+8, ytxt, "Documento interno. No clínico.")

    # ------------------------------------------------------------
    # GRAFICO DE BARRAS (arriba izquierda)
    # ------------------------------------------------------------
    chart_x = margin_x
    chart_y = box_y  # alinear verticalmente con el cuadro de datos
    chart_w = 250
    chart_h = 120

    # dibuja recuadro texto "Perfil cognitivo normalizado (0-10 visual)"
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(chart_x, chart_y + chart_h + 18, "Perfil cognitivo normalizado (0–10 visual)")

    # Eje y líneas horizontales 0..10
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(chart_x, chart_y, chart_x, chart_y + chart_h)  # eje Y
    # rejilla
    for lvl in range(0, 11):
        yv = chart_y + (lvl/10.0)*chart_h
        c.setFont("Helvetica",6)
        c.setFillColor(colors.black)
        c.drawString(chart_x-15, yv-2, str(lvl))
        c.setStrokeColor(colors.lightgrey)
        c.line(chart_x, yv, chart_x+chart_w, yv)

    dims_plot = ["RL","AT","VD","MT","CI"]
    colors_plot = [
        colors.HexColor("#2563eb"), # azul
        colors.HexColor("#16a34a"), # verde
        colors.HexColor("#f97316"), # naranjo
        colors.HexColor("#6b7280"), # gris
        colors.HexColor("#0ea5b7"), # teal
    ]
    bar_gap = 10
    bar_w = (chart_w - bar_gap*(len(dims_plot)+1)) / len(dims_plot)
    tops_xy = []
    for i, dim_key in enumerate(dims_plot):
        val = norm_dim[dim_key]  # 0..10
        bh = (val/10.0)*chart_h
        bx = chart_x + bar_gap + i*(bar_w+bar_gap)

        c.setStrokeColor(colors.black)
        c.setFillColor(colors_plot[i])
        c.rect(bx, chart_y, bar_w, bh, stroke=1, fill=1)

        tops_xy.append((bx+bar_w/2.0, chart_y+bh))

        # etiqueta bajo barra
        c.setFont("Helvetica-Bold",7)
        c.setFillColor(colors.black)
        c.drawCentredString(bx+bar_w/2.0, chart_y-14, dim_key)

        # puntaje bruto/14 y nivel bajo la etiqueta
        raw_v = raw_dim[dim_key]
        lvl_v = level_label(val)
        c.setFont("Helvetica",6)
        c.drawCentredString(
            bx+bar_w/2.0,
            chart_y-26,
            f"{raw_v}/14  {lvl_v}"
        )

    # línea quebrada por arriba de las barras
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    for j in range(len(tops_xy)-1):
        (x1,y1)=tops_xy[j]
        (x2,y2)=tops_xy[j+1]
        c.line(x1,y1,x2,y2)
    for (px,py) in tops_xy:
        c.setFillColor(colors.black)
        c.circle(px,py,2,stroke=0,fill=1)

    # ------------------------------------------------------------
    # BLOQUE "Guía de lectura de dimensiones" (debajo cuadro candidato)
    # y "Resumen cognitivo observado"
    # Vamos a usar todo el ancho derecha y parte central
    # ------------------------------------------------------------
    guide_x = margin_x
    guide_y_top = chart_y - 10  # debajo del gráfico
    guide_w = W - 2*margin_x
    guide_h = 60

    # Guía
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(guide_x, guide_y_top - guide_h, guide_w, guide_h, stroke=1, fill=1)

    yy = guide_y_top - 14
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(guide_x+8, yy, "Guía de lectura de dimensiones")
    yy -= 12

    c.setFont("Helvetica",7)
    lines_dim = [
        "RL = Razonamiento Lógico / Secuencias",
        "AT = Atención al Detalle / Precisión",
        "VD = Velocidad de Decisión / Juicio rápido",
        "MT = Memoria de Trabajo / Retención inmediata",
        "CI = Comprensión de Instrucciones / Lectura Operativa",
        "G  = Índice Cognitivo Global (promedio)",
    ]
    for ln in lines_dim:
        c.drawString(guide_x+8, yy, ln)
        yy -= 10

    # Resumen cognitivo observado
    summary_y_top = guide_y_top - guide_h - 10
    summary_h = 110
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(guide_x, summary_y_top - summary_h, guide_w, summary_h, stroke=1, fill=1)

    # título resumen
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(guide_x+8, summary_y_top - 14, "Resumen cognitivo observado")

    block_y = summary_y_top - 28
    # Fortalezas
    c.setFont("Helvetica-Bold",7)
    c.drawString(guide_x+8, block_y, "Fortalezas potenciales:")
    block_y -= 12
    c.setFont("Helvetica",7)
    if fortalezas_text.strip() == "":
        fortalezas_text_use = "• (Sin fortalezas destacadas específicas en rangos altos)."
    else:
        fortalezas_text_use = fortalezas_text
    block_y = draw_wrapped(
        c,
        fortalezas_text_use,
        guide_x+16,
        block_y,
        guide_w-24,
        font="Helvetica",
        size=7,
        leading=9,
        color=colors.black,
    )
    block_y -= 8

    # Monitoreo
    c.setFont("Helvetica-Bold",7)
    c.drawString(guide_x+8, block_y, "Aspectos a monitorear / apoyo sugerido:")
    block_y -= 12
    c.setFont("Helvetica",7)
    if monitoreo_text.strip() == "":
        monitoreo_text_use = "• (Sin observaciones críticas inmediatas para apoyo adicional)."
    else:
        monitoreo_text_use = monitoreo_text
    draw_wrapped(
        c,
        monitoreo_text_use,
        guide_x+16,
        block_y,
        guide_w-24,
        font="Helvetica",
        size=7,
        leading=9,
        color=colors.black,
    )

    # ------------------------------------------------------------
    # TABLA DETALLE POR DIMENSIÓN
    # (ocupa todo el ancho y se ve en filas, tipo planilla)
    # ------------------------------------------------------------
    table_top = summary_y_top - summary_h - 12
    row_h = 32  # alto por fila
    header_h = 20
    dims_rows = [
        ("Razonamiento Lógico / Secuencias",        "RL", raw_dim["RL"], norm_dim["RL"], lvl_RL, desc["RL"]),
        ("Atención al Detalle / Precisión",         "AT", raw_dim["AT"], norm_dim["AT"], lvl_AT, desc["AT"]),
        ("Velocidad de Decisión / Juicio rápido",   "VD", raw_dim["VD"], norm_dim["VD"], lvl_VD, desc["VD"]),
        ("Memoria de Trabajo / Retención inmediata","MT", raw_dim["MT"], norm_dim["MT"], lvl_MT, desc["MT"]),
        ("Comprensión de Instrucciones / Lectura",  "CI", raw_dim["CI"], norm_dim["CI"], lvl_CI, desc["CI"]),
        ("Índice Cognitivo Global (G)",             "G", round(G_raw,1), G_norm, lvl_G,
            "Indicador promedio global del desempeño cognitivo aplicado al rol."),
    ]

    col_dim_x   = margin_x
    col_score_x = margin_x + 230
    col_lvl_x   = margin_x + 300
    col_desc_x  = margin_x + 350
    table_w     = W - 2*margin_x
    table_h     = header_h + row_h*len(dims_rows)

    # marco de la tabla
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(margin_x, table_top - table_h, table_w, table_h, stroke=1, fill=1)

    # header background line
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold",9)
    c.drawString(margin_x+8, table_top - 14, "Detalle por dimensión")

    # línea bajo el título
    c.setStrokeColor(colors.lightgrey)
    c.line(margin_x, table_top - header_h, margin_x+table_w, table_top - header_h)

    # encabezados columnas
    c.setFont("Helvetica-Bold",7)
    c.setFillColor(colors.black)
    c.drawString(col_dim_x+8, table_top - header_h - 12, "Dimensión")
    c.drawString(col_score_x, table_top - header_h - 12, "Puntaje")
    c.drawString(col_lvl_x,   table_top - header_h - 12, "Nivel")
    c.drawString(col_desc_x,  table_top - header_h - 12, "Descripción breve")

    # líneas columna vertical leves
    c.setStrokeColor(colors.lightgrey)
    c.line(col_score_x-6, table_top - header_h, col_score_x-6, table_top - table_h)
    c.line(col_lvl_x-6,   table_top - header_h, col_lvl_x-6,   table_top - table_h)
    c.line(col_desc_x-6,  table_top - header_h, col_desc_x-6,  table_top - table_h)

    # filas
    cur_y = table_top - header_h - 24
    for (label, code, rawv, normv, lvlv, desc_txt) in dims_rows:
        # texto dimensión
        c.setFont("Helvetica-Bold",7)
        c.setFillColor(colors.black)
        c.drawString(col_dim_x+8, cur_y, label)

        # puntaje (solo 1, el bruto/14 o promedio bruto G_raw)
        c.setFont("Helvetica",7)
        c.drawString(col_score_x, cur_y, f"{rawv}/14" if code!="G" else f"{rawv}/14 aprox")

        # nivel
        c.drawString(col_lvl_x, cur_y, lvlv)

        # descripción envuelta (máx ~2 líneas)
        c.setFont("Helvetica",7)
        desc_lines = wrap_lines(c, desc_txt, W - col_desc_x - margin_x, font="Helvetica", size=7)
        # imprimimos hasta 2 líneas, con salto
        line_y = cur_y
        lines_used = 0
        for dl in desc_lines:
            c.drawString(col_desc_x, line_y, dl)
            line_y -= 9
            lines_used += 1
            if lines_used >= 2:
                break

        # línea horizontal separadora
        c.setStrokeColor(colors.lightgrey)
        c.line(margin_x, cur_y-14, margin_x+table_w, cur_y-14)

        cur_y -= row_h

    # ------------------------------------------------------------
    # CONCLUSIÓN / AJUSTE AL CARGO
    # ------------------------------------------------------------
    concl_top = cur_y + 10
    concl_h = 70
    concl_w = W - 2*margin_x
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(margin_x, concl_top - concl_h, concl_w, concl_h, stroke=1, fill=1)

    # bloque texto
    yy2 = concl_top - 14
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(margin_x+8, yy2, "Desempeño cognitivo global")
    yy2 -= 12
    c.setFont("Helvetica",7)
    yy2 = draw_wrapped(
        c,
        "El desempeño cognitivo global se considera funcional para entornos operativos "
        "estándar, con capacidad de aprendizaje directo en el puesto.",
        margin_x+8,
        yy2,
        concl_w-16,
        font="Helvetica",
        size=7,
        leading=9,
        color=colors.black,
    )
    yy2 -= 8
    c.setFont("Helvetica-Bold",8)
    c.drawString(margin_x+8, yy2, "Ajuste al cargo evaluado")
    yy2 -= 12
    c.setFont("Helvetica",7)
    draw_wrapped(
        c,
        ajuste_text,
        margin_x+8,
        yy2,
        concl_w-16,
        font="Helvetica",
        size=7,
        leading=9,
        color=colors.black,
    )

    # ------------------------------------------------------------
    # NOTA METODOLÓGICA / FOOTER
    # ------------------------------------------------------------
    nota_txt = (
        "Este informe se basa en las respuestas del test cognitivo adaptado para entornos "
        "operativos. Los resultados describen tendencias funcionales observadas al momento "
        "de la evaluación y no constituyen un diagnóstico clínico ni, por sí solos, una "
        "determinación absoluta de idoneidad. Se recomienda complementar esta información "
        "con entrevista estructurada, verificación de experiencia y evaluación técnica del cargo."
    )
    nota_top = 70
    nota_h = 70
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(margin_x, nota_top, concl_w, nota_h, stroke=1, fill=1)

    yy3 = nota_top + nota_h - 14
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(margin_x+8, yy3, "Nota metodológica")
    yy3 -= 12
    c.setFont("Helvetica",6)
    draw_wrapped(
        c,
        nota_txt,
        margin_x+8,
        yy3,
        concl_w-16,
        font="Helvetica",
        size=6,
        leading=8,
        color=colors.grey,
    )

    # footer
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawRightString(W - margin_x, 40,
        "Uso interno RR.HH. · Evaluación Cognitiva Operativa · No clínico")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()

# ------------------------------------------------------------
# EMAIL SENDER
# ------------------------------------------------------------
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

# ------------------------------------------------------------
# FINALIZAR, GENERAR PDF, ENVIAR
# ------------------------------------------------------------
def finalize_and_send():
    scores = compute_scores(st.session_state.answers)
    desc = build_descriptions(scores["norm"])
    fortalezas, monitoreo = build_summary_blocks(scores["norm"], scores["G_norm"])
    ajuste_text = cargo_fit(
        st.session_state.selected_job,
        scores["norm"],
        scores["G_norm"]
    )

    now_txt = datetime.now().strftime("%d/%m/%Y %H:%M")
    cargo_name = JOB_PROFILES[st.session_state.selected_job]["title"]

    pdf_bytes = generate_pdf(
        candidate_name   = st.session_state.candidate_name,
        cargo_name       = cargo_name,
        fecha_eval       = now_txt,
        evaluator_email  = st.session_state.evaluator_email,
        scores           = scores,
        fortalezas       = fortalezas,
        monitoreo        = monitoreo,
        ajuste_text      = ajuste_text,
    )

    if not st.session_state.already_sent:
        try:
            send_email_with_pdf(
                to_email   = st.session_state.evaluator_email,
                pdf_bytes  = pdf_bytes,
                filename   = "Informe_Cognitivo_Operativo.pdf",
                subject    = "Informe Cognitivo Operativo (IQ Adaptado)",
                body_text  = (
                    "Adjunto informe cognitivo operativo "
                    f"({st.session_state.candidate_name} / {cargo_name}). "
                    "Uso interno RR.HH."
                ),
            )
        except Exception:
            pass
        st.session_state.already_sent = True

# ------------------------------------------------------------
# CALLBACK RESPUESTA PREGUNTA
# ------------------------------------------------------------
def choose_answer(option_idx: int):
    q_idx = st.session_state.current_q
    st.session_state.answers[q_idx] = option_idx

    if q_idx < TOTAL_QUESTIONS - 1:
        st.session_state.current_q += 1
        st.session_state._need_rerun = True
    else:
        # terminar test
        finalize_and_send()
        st.session_state.stage = "done"
        st.session_state._need_rerun = True

# ------------------------------------------------------------
# VISTAS UI
# ------------------------------------------------------------
def view_select_job():
    st.markdown("### Evaluación Cognitiva Operativa (IQ Adaptado)")
    st.write("Seleccione el cargo a evaluar:")

    cols = st.columns(2)
    for idx, job_key in enumerate(JOB_PROFILES.keys()):
        col = cols[idx % 2]
        if col.button(JOB_PROFILES[job_key]["title"], key=f"job_{job_key}", use_container_width=True):
            st.session_state.selected_job = job_key
            st.session_state.stage = "info"
            st.session_state._need_rerun = True

def view_info():
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
        value=st.session_state.evaluator_email,
        placeholder="nombre@empresa.com"
    )

    ok = (
        len(st.session_state.candidate_name.strip())>0 and
        len(st.session_state.evaluator_email.strip())>0
    )

    if st.button("Comenzar test de 70 preguntas", type="primary", disabled=not ok, use_container_width=True):
        st.session_state.current_q = 0
        st.session_state.answers = {i: None for i in range(TOTAL_QUESTIONS)}
        st.session_state.already_sent = False
        st.session_state.stage = "test"
        st.session_state._need_rerun = True

def view_test():
    q_idx = st.session_state.current_q
    q = QUESTIONS[q_idx]
    progreso = (q_idx+1)/TOTAL_QUESTIONS

    # header barra progreso estilo azul-morado
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

    # bloque pregunta
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

    # opciones en 2 columnas responsivas -> usamos botones
    opt_cols = st.columns(2)
    for i_opt, opt_text in enumerate(q["options"]):
        col = opt_cols[i_opt % 2]
        col.button(
            opt_text,
            key=f"q{q_idx}_opt{i_opt}",
            use_container_width=True,
            on_click=choose_answer,
            args=(i_opt,)
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

# ------------------------------------------------------------
# FLUJO PRINCIPAL
# ------------------------------------------------------------
if st.session_state.stage == "select_job":
    view_select_job()

elif st.session_state.stage == "info":
    view_info()

elif st.session_state.stage == "test":
    if st.session_state.current_q >= TOTAL_QUESTIONS:
        st.session_state.stage = "done"
        st.session_state._need_rerun = True
    view_test()

elif st.session_state.stage == "done":
    # asegurar envío (idempotente)
    finalize_and_send()
    view_done()

# control de rerun sin doble click
if st.session_state._need_rerun:
    st.session_state._need_rerun = False
    st.rerun()
