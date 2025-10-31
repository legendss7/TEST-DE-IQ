# ============================================================
# Evaluación Cognitiva General (IQ Operativo Adaptado)
# 70 preguntas · 5 dimensiones · Informe PDF de 2 páginas
# Envío automático por correo al evaluador
# ============================================================

import streamlit as st
from datetime import datetime
from io import BytesIO
import smtplib
from email.message import EmailMessage

# PDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# ------------------------------------------------------------
# CONFIG STREAMLIT
# ------------------------------------------------------------
st.set_page_config(
    page_title="Evaluación Cognitiva General",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------
# CREDENCIALES DE CORREO
# ------------------------------------------------------------
FROM_ADDR = "jo.tajtaj@gmail.com"
APP_PASS  = "nlkt kujl ebdg cyts"

# ------------------------------------------------------------
# BANCO DE PREGUNTAS (70 ítems)
# Cada pregunta:
#   "text": enunciado
#   "options": lista de 4 alternativas
#   "correct": índice (0..3) de la alternativa correcta
#   "dim": RL / AT / VD / MT / CI
#
# RL = Razonamiento Lógico / Secuencias
# AT = Atención al Detalle / Precisión
# VD = Velocidad de Decisión / Juicio rápido
# MT = Memoria de Trabajo / Retención inmediata
# CI = Comprensión de Instrucciones / Lectura Operativa
#
# 14 preguntas por dimensión = 70 total
# SIN imágenes, todo texto.

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
        "text": "Una máquina hace 12 piezas cada 6 minutos. ¿Cuántas hace en 30 minutos?",
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
        "text": "Un turno termina a las 17:30 y dura 8 horas exactas. ¿A qué hora comenzó?",
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
        "text": "En la orden dice 'pieza #7716'. Se prepara 'pieza #7761'. ¿Coinciden?",
        "options": ["Sí", "No, están invertidos 1 y 6", "No, cambió el 7", "No, todo distinto"],
        "correct": 1,
        "dim": "AT",
    },
    {
        "text": "Si una tabla dice '221.45 mm' y otra dice '221.54 mm', la diferencia está en:",
        "options": ["Las centenas", "Las decenas", "Las centésimas", "Las milésimas"],
        "correct": 2,
        "dim": "AT",
    },
    {
        "text": "Tolerancia máxima 2 mm. La pieza está 1.8 mm fuera. ¿Está aceptable?",
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
        "text": "Instrucción: 'apretar tornillo hasta tope y luego girar 1/4 de vuelta atrás'. ¿Último paso?",
        "options": ["Apretar más fuerte", "Girar 1/4 hacia atrás", "Soltar todo", "No hacer nada"],
        "correct": 1,
        "dim": "AT",
    },
    {
        "text": "Etiqueta: 'EXP: 12/2026'. ¿'EXP' significa...?",
        "options": ["Fecha de compra", "Fecha de producción", "Fecha de vencimiento", "Fecha de turno"],
        "correct": 2,
        "dim": "AT",
    },
    {
        "text": "Plano dice 'usar guantes A'. El operario usa guantes tipo B. ¿Sigue la instrucción?",
        "options": ["Sí, da lo mismo", "Sí, si son cómodos", "No", "Sólo si es supervisor"],
        "correct": 2,
        "dim": "AT",
    },
    {
        "text": "Manual: 'cortar a 120 mm ±2 mm'. La pieza mide 117 mm. ¿Está dentro?",
        "options": ["Sí", "No", "Siempre mejor más corto", "No se sabe"],
        "correct": 1,
        "dim": "AT",
    },
    {
        "text": "Turno 07:00–15:00. ¿Cuántas horas son?",
        "options": ["7", "8", "9", "Depende del break"],
        "correct": 1,
        "dim": "AT",
    },
    {
        "text": "Etiqueta dice 'Caja A12-B'. Se retira 'Caja A21-B'. ¿Es la misma?",
        "options": ["Sí", "No, 12 y 21 no son iguales", "Sí, sólo cambia el orden", "No se sabe"],
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
        "text": "Operación urgente. ¿Qué haces primero?",
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
        "text": "La línea se detiene por falta evidente de insumo. ¿Acción inmediata más lógica?",
        "options": [
            "Avisar al encargado de insumos",
            "Ir a fumar",
            "Ignorar",
            "Reiniciar toda la máquina sin permiso",
        ],
        "correct": 0,
        "dim": "VD",
    },
    {
        "text": "Reportan fuga de aceite. ¿Qué haces primero?",
        "options": [
            "Pisar el aceite",
            "Asegurar zona / informar",
            "Terminar la tarea y luego ver",
            "Nada",
        ],
        "correct": 1,
        "dim": "VD",
    },
    {
        "text": "Debes usar primero la caja con fecha más antigua. ¿Cuál eliges?",
        "options": [
            "Caja 05/05",
            "Caja 10/05",
            "Caja 12/05",
            "Caja sin fecha",
        ],
        "correct": 0,
        "dim": "VD",
    },
    {
        "text": "Un pallet bloquea el pasillo y otro está libre. ¿Cuál mueves primero?",
        "options": ["El que bloquea pasillo", "El libre", "Ninguno", "Los 2 a la vez"],
        "correct": 0,
        "dim": "VD",
    },
    {
        "text": "Suena una alarma roja. ¿Qué haces primero?",
        "options": [
            "Nada",
            "Ver qué indica / detener si corresponde",
            "Apagar todas las luces de la planta",
            "Cambiarte de área sin avisar",
        ],
        "correct": 1,
        "dim": "VD",
    },
    {
        "text": "Hay diferencia entre etiqueta y pedido. ¿Reacción inicial adecuada?",
        "options": [
            "Despachar igual",
            "Avisar diferencia antes de despachar",
            "Tachar la etiqueta con plumón",
            "Esconderlo",
        ],
        "correct": 1,
        "dim": "VD",
    },
    {
        "text": "Supervisor pide priorizar embalaje. ¿Qué haces?",
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
        "text": "La máquina vibra raro, distinto a lo normal:",
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
        "text": "¿Qué caja levantas primero si quieres la más liviana?",
        "options": [
            "Caja '15 kg'",
            "Caja '9 kg'",
            "Caja '22 kg'",
            "Caja sin rotular",
        ],
        "correct": 1,
        "dim": "VD",
    },
    {
        "text": "Notas olor a quemado en tablero eléctrico:",
        "options": [
            "Pones la mano encima",
            "Avisa y detén operación si corresponde",
            "Lo tapas con cinta",
            "Ignoras",
        ],
        "correct": 1,
        "dim": "VD",
    },
    {
        "text": "Salida de emergencia bloqueada con pallets:",
        "options": [
            "No haces nada",
            "Avisa y despeja salida",
            "Apilas más cosas adelante",
            "Te vas a otra área",
        ],
        "correct": 1,
        "dim": "VD",
    },
    {
        "text": "Se está cayendo material frágil:",
        "options": [
            "Intentar estabilizar si es seguro",
            "Alejarse para no lesionarse y avisar",
            "Patear el pallet",
            "Filmar con el celular",
        ],
        "correct": 1,
        "dim": "VD",
    },
    {
        "text": "Dos piezas tienen números distintos y no sabes cuál sirve:",
        "options": [
            "Despachas cualquiera",
            "Pides confirmación antes de moverlas",
            "Borras ambos números",
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
            "Nada",
        ],
        "correct": 0,
        "dim": "MT",
    },
    {
        "text": "Instrucción rápida: 'Etiqueta piezas verdes y luego guarda azules'. ¿Qué haces primero?",
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
        "text": "Te dicen: 'Busca guantes talla M y llévalos al supervisor de línea 2'. ¿Qué entregas?",
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
        "text": "Recuerda estos 3 códigos: Z17, Z18, Z21. ¿Cuál NO estaba?",
        "options": ["Z17", "Z18", "Z21", "Z27"],
        "correct": 3,
        "dim": "MT",
    },
    {
        "text": "Pasos: (1) Alinear caja, (2) Sellar tapa. ¿Qué paso va segundo?",
        "options": ["Alinear caja", "Sellar tapa", "Abrir caja", "Poner etiqueta"],
        "correct": 1,
        "dim": "MT",
    },
    {
        "text": "Mensaje verbal: 'Entrega el informe al supervisor nocturno antes de irte'. ¿Qué debes hacer?",
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
        "text": "Te dicen: 'Termina conteo en pasillo B, luego ve al A'. ¿Qué haces primero?",
        "options": ["Pasillo A", "Pasillo B", "Ninguno", "Ambos a la vez"],
        "correct": 1,
        "dim": "MT",
    },
    {
        "text": "Recuerda orden rápido: rojo → verde → azul. ¿Cuál fue el segundo color?",
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
        "text": "Te pasan: 'Caja 31 va a zona V'. ¿Qué debes recordar?",
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
        "text": "Secuencia verbal: 'Llave grande, llave chica, destornillador plano'. ¿Cuál fue el segundo elemento?",
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
        "text": "Orden: 'Rotar stock según fecha más antigua primero'. ¿Qué prioridad se usa?",
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
            "Apilar sobre la línea roja",
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
            "Sólo si es grande",
            "Inmediatamente",
            "Nunca",
        ],
        "correct": 2,
        "dim": "CI",
    },
]

TOTAL_QUESTIONS = len(QUESTIONS)  # 70

# ------------------------------------------------------------
# ESTADO STREAMLIT
# ------------------------------------------------------------
if "stage" not in st.session_state:
    # flujo ahora: info -> test -> done
    st.session_state.stage = "info"

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

    # normalizar a escala 0-10 visual (14 preguntas cada dimensión)
    norm_dim = {}
    for dim_key in raw_dim:
        norm_dim[dim_key] = (raw_dim[dim_key] / 14.0) * 10.0

    # índice global G (promedio de las 5 dimensiones)
    G_raw = sum(raw_dim.values()) / 5.0
    G_norm = sum(norm_dim.values()) / 5.0

    return {
        "raw": raw_dim,      # bruto (0-14)
        "norm": norm_dim,    # normalizado 0-10
        "G_raw": G_raw,      # promedio bruto
        "G_norm": G_norm,    # promedio 0-10
    }

def level_label(norm_score):
    # escala 0-10
    if norm_score >= 7.5:
        return "Alto"
    elif norm_score >= 4.5:
        return "Medio"
    else:
        return "Bajo"

def build_descriptions():
    return {
        "RL": "Razonamiento lógico / cálculo básico / detección de patrones para prevenir errores.",
        "AT": "Precisión en lectura de datos, números, tolerancias y procedimientos.",
        "VD": "Decisión operativa rápida priorizando seguridad y continuidad básica.",
        "MT": "Memoria inmediata para retener instrucciones verbales y orden de pasos.",
        "CI": "Comprensión de instrucciones escritas u orales y aplicación correcta.",
        "G":  "Indicador promedio global de desempeño cognitivo aplicado.",
    }

def build_strengths_and_risks(norm_dim, G_norm):
    fortalezas = []
    monitoreo = []

    # RL
    if norm_dim["RL"] >= 7.5:
        fortalezas.append("Capacidad clara de razonamiento lógico y anticipación de errores.")
    elif norm_dim["RL"] < 4.5:
        monitoreo.append("Puede requerir acompañamiento inicial en tareas con cálculo o secuencia numérica.")

    # AT
    if norm_dim["AT"] >= 7.5:
        fortalezas.append("Buen nivel de precisión al leer códigos, medidas y tolerancias.")
    elif norm_dim["AT"] < 4.5:
        monitoreo.append("Se sugiere doble verificación en controles de calidad o picking crítico.")

    # VD
    if norm_dim["VD"] >= 7.5:
        fortalezas.append("Toma decisiones rápidas priorizando seguridad básica.")
    elif norm_dim["VD"] < 4.5:
        monitoreo.append("Podría necesitar confirmación antes de actuar en urgencias.")

    # MT
    if norm_dim["MT"] >= 7.5:
        fortalezas.append("Retiene instrucciones verbales sin necesidad de repetir constantemente.")
    elif norm_dim["MT"] < 4.5:
        monitoreo.append("Puede beneficiarse de instrucciones paso a paso más explícitas.")

    # CI
    if norm_dim["CI"] >= 7.5:
        fortalezas.append("Comprende instrucciones operativas y las ejecuta según lo indicado.")
    elif norm_dim["CI"] < 4.5:
        monitoreo.append("Puede requerir apoyo al interpretar protocolos escritos.")

    # Global
    if G_norm >= 7.5:
        fortalezas.append("Desempeño cognitivo global alto para entornos con ritmo exigente.")
    elif G_norm < 4.5:
        monitoreo.append("Requiere apoyo cercano al inicio hasta consolidar funcionamiento.")

    return fortalezas, monitoreo

def global_fit_text(G_norm):
    # conclusión global, sin cargo
    if G_norm >= 4.5:
        return ("Conclusión general: El perfil evaluado se considera APTO en términos "
                "cognitivos funcionales básicos para desempeñar tareas operativas generales.")
    else:
        return ("Conclusión general: El perfil evaluado REQUIERE APOYO INICIAL "
                "para lograr un desempeño operativo estable, especialmente durante "
                "las primeras etapas de entrenamiento.")

# ------------------------------------------------------------
# UTILIDADES PARA PDF
# ------------------------------------------------------------
def wrap_lines(c, text, max_width, font="Helvetica", size=8):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if c.stringWidth(test, font, size) <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_wrapped(c, text, x, y, w,
                 font="Helvetica", size=8,
                 leading=10, color=colors.black,
                 max_lines=None):
    c.setFont(font, size)
    c.setFillColor(color)
    lines = wrap_lines(c, text, w, font, size)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        c.drawString(x, y, ln)
        y -= leading
    return y

# ------------------------------------------------------------
# GENERAR PDF (2 páginas)
# ------------------------------------------------------------
def generate_pdf(candidate_name,
                 fecha_eval,
                 evaluator_email,
                 scores,
                 fortalezas,
                 monitoreo,
                 ajuste_text):

    raw_dim = scores["raw"]      # bruto 0-14
    norm_dim = scores["norm"]    # normalizado 0-10
    G_norm   = scores["G_norm"]
    G_raw    = scores["G_raw"]

    desc_map = build_descriptions()

    # niveles cualitativos
    lvl = {
        "RL": level_label(norm_dim["RL"]),
        "AT": level_label(norm_dim["AT"]),
        "VD": level_label(norm_dim["VD"]),
        "MT": level_label(norm_dim["MT"]),
        "CI": level_label(norm_dim["CI"]),
        "G":  level_label(G_norm),
    }

    # Texto fortalezas / monitoreo
    fortalezas_txt = "• " + "\n• ".join(fortalezas) if fortalezas else "• (Sin fortalezas específicas destacadas en rangos altos)."
    monitoreo_txt  = "• " + "\n• ".join(monitoreo) if monitoreo else "• (Sin observaciones críticas inmediatas)."

    # ---- PAGE 1 ----
    buf = BytesIO()
    W, H = A4  # ~595 x ~842 pt
    c = canvas.Canvas(buf, pagesize=A4)
    margin_x = 36
    margin_top = H - 36

    # Encabezado
    c.setFont("Helvetica-Bold",10)
    c.setFillColor(colors.black)
    c.drawString(margin_x, margin_top, "EMPRESA / LOGO")
    c.setFont("Helvetica",7)
    c.drawString(margin_x, margin_top-12,
                 "Evaluación Cognitiva General · Uso interno RR.HH. · No clínico")

    c.setFont("Helvetica-Bold",10)
    c.drawRightString(W - margin_x, margin_top,
                      "Perfil Cognitivo Operativo (IQ Adaptado)")
    c.setFont("Helvetica",7)
    c.drawRightString(W - margin_x, margin_top-12,
                      "Evaluación de habilidades cognitivas aplicadas")

    # Caja datos del evaluado
    box_w = 250
    box_h = 80
    box_x = W - margin_x - box_w
    box_y_top = margin_top - 40
    box_y = box_y_top - box_h

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(box_x, box_y, box_w, box_h, stroke=1, fill=1)

    yy = box_y_top - 14
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(box_x+10, yy, f"Nombre: {candidate_name}")
    yy -= 12
    c.setFont("Helvetica",8)
    c.drawString(box_x+10, yy, "Evaluación: Cognitiva General")
    yy -= 12
    c.drawString(box_x+10, yy, f"Fecha evaluación: {fecha_eval}")
    yy -= 12
    c.drawString(box_x+10, yy, f"Evaluador: {evaluator_email.upper()}")
    yy -= 12
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawString(box_x+10, yy, "Uso interno. No clínico.")

    # Gráfico de barras dimensiones (RL, AT, VD, MT, CI)
    chart_x = margin_x
    chart_y = box_y  # mismo baseline aprox
    chart_w = 260
    chart_h = 130

    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(chart_x, chart_y + chart_h + 18,
                 "Perfil cognitivo por dimensión (0–10)")

    # eje y
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(chart_x, chart_y, chart_x, chart_y + chart_h)

    # rejilla 0..10
    for lvl_y in range(0,11):
        yv = chart_y + (lvl_y/10.0)*chart_h
        c.setFont("Helvetica",6)
        c.setFillColor(colors.black)
        c.drawString(chart_x-15, yv-2, str(lvl_y))
        c.setStrokeColor(colors.lightgrey)
        c.line(chart_x, yv, chart_x + chart_w, yv)

    dims_plot = ["RL","AT","VD","MT","CI"]
    plot_colors = [
        colors.HexColor("#2563eb"),
        colors.HexColor("#16a34a"),
        colors.HexColor("#f97316"),
        colors.HexColor("#6b7280"),
        colors.HexColor("#0ea5b7"),
    ]
    gap = 10
    bar_w = (chart_w - gap*(len(dims_plot)+1)) / len(dims_plot)
    tops_xy = []
    for i, dimkey in enumerate(dims_plot):
        val = norm_dim[dimkey]  # 0..10
        bh = (val/10.0)*chart_h
        bx = chart_x + gap + i*(bar_w+gap)

        c.setStrokeColor(colors.black)
        c.setFillColor(plot_colors[i])
        c.rect(bx, chart_y, bar_w, bh, stroke=1, fill=1)

        tops_xy.append((bx+bar_w/2.0, chart_y+bh))

        # etiqueta
        c.setFont("Helvetica-Bold",7)
        c.setFillColor(colors.black)
        c.drawCentredString(bx+bar_w/2.0, chart_y-14, dimkey)

        # puntaje bruto y nivel
        c.setFont("Helvetica",6)
        c.drawCentredString(
            bx+bar_w/2.0,
            chart_y-26,
            f"{raw_dim[dimkey]}/14  {lvl[dimkey]}"
        )

    # línea quebrada sobre barras
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    for j in range(len(tops_xy)-1):
        x1,y1 = tops_xy[j]
        x2,y2 = tops_xy[j+1]
        c.line(x1,y1,x2,y2)
    for (px,py) in tops_xy:
        c.setFillColor(colors.black)
        c.circle(px,py,2,stroke=0,fill=1)

    # Caja "Guía de lectura de dimensiones"
    guide_x = margin_x
    guide_y_top = chart_y - 20
    guide_h = 80
    guide_w = W - 2*margin_x

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(guide_x, guide_y_top - guide_h, guide_w, guide_h, stroke=1, fill=1)

    yy2 = guide_y_top - 16
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(guide_x+10, yy2, "Guía de lectura de dimensiones")
    yy2 -= 12

    c.setFont("Helvetica",7)
    lines_dim = [
        "RL = Razonamiento Lógico / Secuencias",
        "AT = Atención al Detalle / Precisión",
        "VD = Velocidad de Decisión / Juicio rápido",
        "MT = Memoria de Trabajo / Retención inmediata",
        "CI = Comprensión de Instrucciones / Lectura Operativa",
        "G  = Índice Cognitivo Global (promedio de las 5 áreas)",
    ]
    for ln in lines_dim:
        c.drawString(guide_x+14, yy2, ln)
        yy2 -= 10

    # Caja "Resumen cognitivo observado"
    summary_x = margin_x
    summary_y_top = guide_y_top - guide_h - 20
    summary_h = 170
    summary_w = W - 2*margin_x

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(summary_x, summary_y_top - summary_h, summary_w, summary_h, stroke=1, fill=1)

    yblock = summary_y_top - 16
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(summary_x+10, yblock, "Resumen cognitivo observado")
    yblock -= 14

    # Fortalezas
    c.setFont("Helvetica-Bold",7)
    c.drawString(summary_x+10, yblock, "Fortalezas potenciales:")
    yblock -= 12
    c.setFont("Helvetica",7)
    yblock = draw_wrapped(
        c,
        fortalezas_txt,
        summary_x+20,
        yblock,
        summary_w-30,
        font="Helvetica",
        size=7,
        leading=9,
        color=colors.black,
    )
    yblock -= 10

    # Monitoreo
    c.setFont("Helvetica-Bold",7)
    c.drawString(summary_x+10, yblock, "Aspectos a monitorear / apoyo sugerido:")
    yblock -= 12
    c.setFont("Helvetica",7)
    draw_wrapped(
        c,
        monitoreo_txt,
        summary_x+20,
        yblock,
        summary_w-30,
        font="Helvetica",
        size=7,
        leading=9,
        color=colors.black,
    )

    # FIN PÁGINA 1
    c.showPage()

    # ---- PAGE 2 ----
    c.setFont("Helvetica-Bold",10)
    c.setFillColor(colors.black)
    c.drawString(margin_x, H-36, "Evaluación Cognitiva General (continuación)")
    c.setFont("Helvetica",7)
    c.drawRightString(W - margin_x, H-36,
                      f"Evaluado: {candidate_name} · {fecha_eval}")

    # TABLA DETALLE POR DIMENSIÓN (ancha, con espacio)
    table_x = margin_x
    table_y_top = H-70
    table_w = W - 2*margin_x

    # definimos filas (incluye G)
    rows = [
        ("Razonamiento Lógico / Secuencias",        "RL"),
        ("Atención al Detalle / Precisión",         "AT"),
        ("Velocidad de Decisión / Juicio rápido",   "VD"),
        ("Memoria de Trabajo / Retención inmediata","MT"),
        ("Comprensión de Instrucciones / Lectura",  "CI"),
        ("Índice Cognitivo Global (G)",             "G"),
    ]

    row_height = 44
    header_height = 24
    table_h = header_height + row_height*len(rows)

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(table_x, table_y_top - table_h, table_w, table_h, stroke=1, fill=1)

    # Encabezado tabla
    c.setFont("Helvetica-Bold",9)
    c.setFillColor(colors.black)
    c.drawString(table_x+10, table_y_top-16, "Detalle por dimensión")

    # línea bajo título
    c.setStrokeColor(colors.lightgrey)
    c.line(table_x, table_y_top-header_height, table_x+table_w, table_y_top-header_height)

    # columnas
    col_dim_x   = table_x+10
    col_score_x = table_x+240
    col_lvl_x   = table_x+300
    col_desc_x  = table_x+360

    c.setFont("Helvetica-Bold",7)
    c.setFillColor(colors.black)
    c.drawString(col_dim_x,   table_y_top-header_height-12, "Dimensión")
    c.drawString(col_score_x, table_y_top-header_height-12, "Puntaje")
    c.drawString(col_lvl_x,   table_y_top-header_height-12, "Nivel")
    c.drawString(col_desc_x,  table_y_top-header_height-12, "Descripción breve")

    # líneas divisorias verticales claras
    c.setStrokeColor(colors.lightgrey)
    c.line(col_score_x-8, table_y_top-header_height, col_score_x-8, table_y_top-table_h)
    c.line(col_lvl_x-8,   table_y_top-header_height, col_lvl_x-8,   table_y_top-table_h)
    c.line(col_desc_x-8,  table_y_top-header_height, col_desc_x-8,  table_y_top-table_h)

    cur_y = table_y_top-header_height-28
    for (label, key) in rows:
        # Puntaje bruto /14 excepto G (promedio bruto)
        if key == "G":
            raw_txt = f"{G_raw:.1f}/14 aprox"
            lvl_txt = lvl["G"]
            desc_txt = desc_map["G"]
        else:
            raw_txt = f"{raw_dim[key]}/14"
            lvl_txt = lvl[key]
            desc_txt = desc_map[key]

        # dimensión
        c.setFont("Helvetica-Bold",7)
        c.setFillColor(colors.black)
        c.drawString(col_dim_x, cur_y, label)

        # puntaje
        c.setFont("Helvetica",7)
        c.drawString(col_score_x, cur_y, raw_txt)

        # nivel
        c.drawString(col_lvl_x, cur_y, lvl_txt)

        # descripción (envuelta, máx 2 líneas)
        c.setFont("Helvetica",7)
        lines_desc = wrap_lines(c, desc_txt, table_x+table_w - col_desc_x - 10, font="Helvetica", size=7)
        printed = 0
        ld_y = cur_y
        for ln in lines_desc:
            c.drawString(col_desc_x, ld_y, ln)
            ld_y -= 9
            printed += 1
            if printed >= 2:
                break

        # línea horizontal separadora
        c.setStrokeColor(colors.lightgrey)
        c.line(table_x, cur_y-16, table_x+table_w, cur_y-16)

        cur_y -= row_height

    # CAJA CONCLUSIÓN / AJUSTE GLOBAL
    concl_top = cur_y - 10
    concl_h   = 90
    concl_w   = table_w
    concl_x   = table_x
    concl_y   = concl_top - concl_h

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(concl_x, concl_y, concl_w, concl_h, stroke=1, fill=1)

    y_concl = concl_top - 16
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(concl_x+10, y_concl, "Conclusión global")
    y_concl -= 12
    c.setFont("Helvetica",7)
    y_concl = draw_wrapped(
        c,
        "Resumen general del desempeño cognitivo observado en esta evaluación:",
        concl_x+10,
        y_concl,
        concl_w-20,
        font="Helvetica",
        size=7,
        leading=9,
        color=colors.black,
    )

    y_concl -= 8
    c.setFont("Helvetica-Bold",7)
    c.drawString(concl_x+10, y_concl, "Ajuste general al desempeño operativo:")
    y_concl -= 12
    c.setFont("Helvetica",7)
    draw_wrapped(
        c,
        ajuste_text,
        concl_x+10,
        y_concl,
        concl_w-20,
        font="Helvetica",
        size=7,
        leading=9,
        color=colors.black,
    )

    # CAJA NOTA METODOLÓGICA / FOOTER
    nota_txt = (
        "Este informe se basa en las respuestas del test cognitivo adaptado para "
        "entornos operativos. Los resultados describen tendencias funcionales "
        "observadas al momento de la evaluación y no constituyen un diagnóstico "
        "clínico ni, por sí solos, una determinación absoluta de idoneidad. "
        "Se recomienda complementar esta información con entrevista estructurada, "
        "verificación de experiencia y evaluación técnica en contexto real."
    )

    nota_h = 90
    nota_x = margin_x
    nota_y_top = 130  # más o menos alto en la página 2
    nota_y = nota_y_top - nota_h
    nota_w = W - 2*margin_x

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(nota_x, nota_y, nota_w, nota_h, stroke=1, fill=1)

    yy_nota = nota_y_top - 16
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(nota_x+10, yy_nota, "Nota metodológica")
    yy_nota -= 12
    c.setFont("Helvetica",6)
    draw_wrapped(
        c,
        nota_txt,
        nota_x+10,
        yy_nota,
        nota_w-20,
        font="Helvetica",
        size=6,
        leading=8,
        color=colors.grey,
    )

    # Pie de página
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawRightString(W - margin_x, 36,
        "Uso interno RR.HH. · Evaluación Cognitiva General · No clínico")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()

# ------------------------------------------------------------
# ENVÍO DE CORREO
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
    fortalezas, monitoreo = build_strengths_and_risks(scores["norm"], scores["G_norm"])
    ajuste_text = global_fit_text(scores["G_norm"])

    now_txt = datetime.now().strftime("%d/%m/%Y %H:%M")

    pdf_bytes = generate_pdf(
        candidate_name   = st.session_state.candidate_name,
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
                filename   = "Informe_Cognitivo_General.pdf",
                subject    = "Informe Evaluación Cognitiva General (IQ Adaptado)",
                body_text  = (
                    "Adjunto informe de Evaluación Cognitiva General "
                    f"({st.session_state.candidate_name}). "
                    "Uso interno RR.HH."
                ),
            )
        except Exception:
            pass
        st.session_state.already_sent = True

# ------------------------------------------------------------
# CALLBACK DE RESPUESTA
# ------------------------------------------------------------
def choose_answer(option_idx: int):
    q_idx = st.session_state.current_q
    st.session_state.answers[q_idx] = option_idx

    if q_idx < TOTAL_QUESTIONS - 1:
        st.session_state.current_q += 1
        st.session_state._need_rerun = True
    else:
        finalize_and_send()
        st.session_state.stage = "done"
        st.session_state._need_rerun = True

# ------------------------------------------------------------
# VISTAS
# ------------------------------------------------------------
def view_info():
    st.markdown("### Evaluación Cognitiva General")
    st.info("Estos datos se utilizan para generar el informe PDF interno y enviarlo automáticamente al correo indicado.")

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

    if st.button("Comenzar test cognitivo (70 preguntas)", type="primary", disabled=not ok, use_container_width=True):
        st.session_state.current_q = 0
        st.session_state.answers = {i: None for i in range(TOTAL_QUESTIONS)}
        st.session_state.already_sent = False
        st.session_state.stage = "test"
        st.session_state._need_rerun = True

def view_test():
    q_idx = st.session_state.current_q
    q = QUESTIONS[q_idx]
    progreso = (q_idx+1)/TOTAL_QUESTIONS

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
                Test Cognitivo General (70 ítems)
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

    # opciones en 2 columnas
    cols = st.columns(2)
    for i_opt, opt_text in enumerate(q["options"]):
        cols[i_opt % 2].button(
            opt_text,
            key=f"q{q_idx}_opt{i_opt}",
            on_click=choose_answer,
            args=(i_opt,),
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
            <b>Confidencialidad:</b> Uso interno RR.HH. / Selección y capacitación.
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

# ------------------------------------------------------------
# FLUJO PRINCIPAL
# ------------------------------------------------------------
if st.session_state.stage == "info":
    view_info()

elif st.session_state.stage == "test":
    if st.session_state.current_q >= TOTAL_QUESTIONS:
        st.session_state.stage = "done"
        st.session_state._need_rerun = True
    view_test()

elif st.session_state.stage == "done":
    finalize_and_send()
    view_done()

# Control de rerun suave para pasar de una pregunta a la siguiente sin doble click
if st.session_state._need_rerun:
    st.session_state._need_rerun = False
    st.rerun()
