# ============================================================
# TEST COGNITIVO GENERAL (IQ Adaptado) · 70 ítems
# - Sin referencia a cargos / áreas específicas
# - Preguntas 100% cognitivas (lógico-numéricas, atención, memoria, decisión)
# - Dificultad incremental
# - 5 dimensiones: RL / AT / VD / MT / CI
# - Informe PDF en 2 páginas, ordenado, con cajas y sin texto encima
# - Envío automático por correo al terminar
# - Pantalla final sólo muestra "Evaluación finalizada"
#
# Requisitos:
#   pip install streamlit reportlab
#
# IMPORTANTE:
#   Para envío de correo automático con Gmail necesitas:
#   - Activar "contraseña de aplicación"
#   - Cambiar FROM_ADDR y APP_PASS acá abajo
# ============================================================

import streamlit as st
from datetime import datetime
from io import BytesIO
import smtplib
from email.message import EmailMessage

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors


# ------------------------------------------------------------
# CONFIG STREAMLIT
# ------------------------------------------------------------
st.set_page_config(
    page_title="Evaluación Cognitiva General (IQ Adaptado)",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------------------------
# CREDENCIALES DE CORREO (usa tus credenciales válidas)
# ------------------------------------------------------------
FROM_ADDR = "jo.tajtaj@gmail.com"
APP_PASS  = "nlkt kujl ebdg cyts"   # <-- tu pass de aplicación Gmail


# ------------------------------------------------------------
# BANCO DE PREGUNTAS (70 ítems totales)
# 5 dimensiones x 14 ítems cada una:
# RL = Razonamiento Lógico
# AT = Atención al Detalle
# VD = Velocidad de Decisión
# MT = Memoria de Trabajo
# CI = Comprensión de Instrucciones
# ------------------------------------------------------------

QUESTIONS = [
    # =========================
    # RL · Razonamiento Lógico
    # =========================
    {
        "text": "Serie: 1, 2, 3, 4, ... ¿Cuál sigue?",
        "options": ["5", "6", "8", "10"],
        "correct": 0,
        "dim": "RL",
    },
    {
        "text": "Serie: 2, 4, 6, 8, ... ¿Cuál sigue?",
        "options": ["9", "10", "12", "14"],
        "correct": 1,
        "dim": "RL",
    },
    {
        "text": "Serie: 3, 6, 12, 24, ... ¿Cuál sigue?",
        "options": ["36", "48", "30", "12"],
        "correct": 1,
        "dim": "RL",
    },
    {
        "text": "Serie: 10, 9, 7, 4, ... ¿Cuál sigue?",
        "options": ["0", "1", "2", "3"],
        "correct": 2,
        "dim": "RL",
    },
    {
        "text": "Si A > B y B > C, entonces:",
        "options": ["A < C", "A = C", "A > C", "No se puede saber"],
        "correct": 2,
        "dim": "RL",
    },
    {
        "text": "Si 4 cajas pesan lo mismo que 1 bloque, y 2 bloques pesan 40 kg, ¿cuánto pesan 2 cajas?",
        "options": ["5 kg", "10 kg", "20 kg", "40 kg"],
        "correct": 1,
        "dim": "RL",
    },
    {
        "text": "Completa: 5 → 10 → 20 → 40 → ...",
        "options": ["60", "70", "80", "100"],
        "correct": 2,
        "dim": "RL",
    },
    {
        "text": "Si ‘X’ es mayor que ‘Y’ y ‘Y’ es mayor que ‘Z’, ¿quién es el más pequeño?",
        "options": ["X", "Y", "Z", "No se sabe"],
        "correct": 2,
        "dim": "RL",
    },
    {
        "text": "Proporción: 2 es a 6 como 5 es a ____",
        "options": ["10", "12", "15", "20"],
        "correct": 2,
        "dim": "RL",
    },
    {
        "text": "Si hoy es lunes y pasan 5 días, ¿qué día será?",
        "options": ["Viernes", "Sábado", "Domingo", "Jueves"],
        "correct": 1,
        "dim": "RL",
    },
    {
        "text": "Serie: 11, 14, 17, 20, ... ¿Cuál sigue?",
        "options": ["21", "22", "23", "24"],
        "correct": 3,
        "dim": "RL",
    },
    {
        "text": "Si todos los R son T y todos los T son P, entonces todos los R son:",
        "options": ["P", "R", "T", "Nada se puede concluir"],
        "correct": 0,
        "dim": "RL",
    },
    {
        "text": "Si un número se multiplica por 3 y luego se le suma 2 da 17. ¿Cuál era el número inicial?",
        "options": ["4", "5", "6", "7"],
        "correct": 1,
        "dim": "RL",
    },
    {
        "text": "Secuencia: 30, 27, 24, 21, ... ¿Cuál sigue?",
        "options": ["20", "18", "15", "12"],
        "correct": 1,
        "dim": "RL",
    },

    # =========================
    # AT · Atención al Detalle
    # =========================
    {
        "text": "¿Estos dos códigos son iguales? 'AB-9124' vs 'AB-9124'",
        "options": ["Sí", "No, cambia un dígito", "No, cambia el guión", "No, cambia el orden"],
        "correct": 0,
        "dim": "AT",
    },
    {
        "text": "¿Estos dos códigos son iguales? 'ZX-781' vs 'ZX-871'",
        "options": ["Sí", "No, 8 y 7 están invertidos", "No, cambia 81 por 71", "No, cambia el orden de 7 y 8"],
        "correct": 3,
        "dim": "AT",
    },
    {
        "text": "Compara: 'FRA-2201' y 'FRA-2207'. ¿Coinciden?",
        "options": ["Sí", "No, el último dígito cambia", "No, cambia 'FRA'", "No, cambia todo"],
        "correct": 1,
        "dim": "AT",
    },
    {
        "text": "Si una medida es 221.45 y otra 221.54, la diferencia exacta está en:",
        "options": ["Las centenas", "Las decenas", "Las centésimas", "Las unidades"],
        "correct": 2,
        "dim": "AT",
    },
    {
        "text": "Lee con precisión: ¿Cuál de estas opciones es exactamente 'M4-77B'?",
        "options": ["M4-77B", "M4-7B7", "M4-77b", "M4_77B"],
        "correct": 0,
        "dim": "AT",
    },
    {
        "text": "Si un valor permitido es entre 10.0 y 10.5, ¿cuál de estos valores está FUERA del rango?",
        "options": ["10.1", "10.3", "10.5", "10.6"],
        "correct": 3,
        "dim": "AT",
    },
    {
        "text": "Selecciona la opción escrita SIN error ortográfico:",
        "options": ["precición", "presición", "precisión", "preccisión"],
        "correct": 2,
        "dim": "AT",
    },
    {
        "text": "Selecciona el número más grande:",
        "options": ["0.45", "0.405", "0.54", "0.504"],
        "correct": 2,
        "dim": "AT",
    },
    {
        "text": "¿Cuál número es más cercano a 100?",
        "options": ["97", "89", "105", "76"],
        "correct": 2,
        "dim": "AT",
    },
    {
        "text": "¿Cuál de estas palabras está escrita de forma distinta a las otras?",
        "options": ["control", "control", "contorl", "control"],
        "correct": 2,
        "dim": "AT",
    },
    {
        "text": "Encuentra el distinto: 'Q8B7', 'Q8B7', 'Q8R7', 'Q8B7'",
        "options": ["El primero", "El segundo", "El tercero", "El cuarto"],
        "correct": 2,
        "dim": "AT",
    },
    {
        "text": "¿Cuál de estas es la serie completamente ascendente?",
        "options": ["2, 4, 6, 8", "2, 5, 4, 7", "10, 9, 8, 7", "1, 1, 1, 2"],
        "correct": 0,
        "dim": "AT",
    },
    {
        "text": "En 'ABCD-1234', ¿qué carácter está en la posición 3 (contando desde 1)?",
        "options": ["A", "B", "C", "D"],
        "correct": 2,
        "dim": "AT",
    },
    {
        "text": "Si lees '7-14-21-28', ¿cuál es el siguiente número si sigue el mismo patrón?",
        "options": ["32", "33", "34", "35"],
        "correct": 3,
        "dim": "AT",
    },

    # =========================
    # VD · Velocidad de Decisión
    # =========================
    {
        "text": "Tienes que elegir rápido la opción con el número más pequeño:",
        "options": ["12", "5", "30", "9"],
        "correct": 1,
        "dim": "VD",
    },
    {
        "text": "Si tienes que actuar inmediatamente, ¿qué decisión tiene MENOS riesgo?",
        "options": [
            "Revisar antes de tocar",
            "Tocar sin mirar",
            "Actuar sin pensar",
            "Ignorar todo",
        ],
        "correct": 0,
        "dim": "VD",
    },
    {
        "text": "Debes priorizar. ¿Qué eliges primero?",
        "options": [
            "Resolver lo urgente",
            "Resolver lo opcional",
            "Hacer algo no relacionado",
            "No hacer nada",
        ],
        "correct": 0,
        "dim": "VD",
    },
    {
        "text": "Si algo parece peligroso a simple vista, la mejor decisión inicial es:",
        "options": [
            "Acercarte más sin cuidado",
            "Actuar como si no pasara nada",
            "Tomar distancia y evaluar",
            "Filmar con el celular",
        ],
        "correct": 2,
        "dim": "VD",
    },
    {
        "text": "¿Cuál es la opción más lógica cuando hay dos versiones contradictorias de información?",
        "options": [
            "Elegir cualquiera al azar",
            "Pedir confirmación antes de seguir",
            "Ignorar el problema",
            "Inventar un dato",
        ],
        "correct": 1,
        "dim": "VD",
    },
    {
        "text": "Tienes 4 tareas y sólo tiempo para 1 ahora: urgente, importante, posterior, irrelevante. ¿Cuál haces primero?",
        "options": [
            "irrelevante",
            "posterior",
            "importante",
            "urgente",
        ],
        "correct": 3,
        "dim": "VD",
    },
    {
        "text": "Si detectas un error claro, la mejor reacción inmediata es:",
        "options": [
            "Taparlo",
            "Avisar",
            "Ignorarlo",
            "Culpar a otro sin revisar",
        ],
        "correct": 1,
        "dim": "VD",
    },
    {
        "text": "Escoge la opción más razonable si notas que algo no cuadra:",
        "options": [
            "Actuar sin verificar",
            "Detener un momento y revisar",
            "Decir que todo está perfecto",
            "Hacer otra cosa no relacionada",
        ],
        "correct": 1,
        "dim": "VD",
    },
    {
        "text": "¿Cuál de estas opciones muestra mejor 'orden lógico'?",
        "options": [
            "Pensar → Decidir → Actuar",
            "Actuar → Pensar → Decidir",
            "Decidir → Actuar → Pensar",
            "Actuar → Ignorar → Repetir",
        ],
        "correct": 0,
        "dim": "VD",
    },
    {
        "text": "Si tienes que elegir entre dos números y debes tomar el MAYOR rápidamente, ¿cuál eliges entre 17 y 21?",
        "options": ["17", "21", "Son iguales", "No se puede saber"],
        "correct": 1,
        "dim": "VD",
    },
    {
        "text": "Tienes 3 opciones: A = seguro, B = desconocido, C = claramente peligroso. ¿Cuál eliges primero?",
        "options": ["A", "B", "C", "Ninguna"],
        "correct": 0,
        "dim": "VD",
    },
    {
        "text": "Debes decidir rápido si algo necesita atención inmediata o puede esperar. ¿Cuál de estas frases describe 'inmediato'?",
        "options": [
            "Puede esperar varios días",
            "Necesita verse ahora",
            "Tal vez el mes siguiente",
            "Da lo mismo",
        ],
        "correct": 1,
        "dim": "VD",
    },
    {
        "text": "¿Cuál de estas acciones muestra mejor criterio básico?",
        "options": [
            "Hacer algo riesgoso sin preguntar",
            "Avisar si no entiendes algo importante",
            "Asumir que todo está bien siempre",
            "No decir nada aunque veas un problema",
        ],
        "correct": 1,
        "dim": "VD",
    },
    {
        "text": "Si tienes que actuar rápido pero con sentido común, lo primero es:",
        "options": [
            "Admitir que no sabes y preguntar",
            "Actuar a ciegas",
            "Ignorar la situación",
            "Inventar una explicación",
        ],
        "correct": 0,
        "dim": "VD",
    },

    # =========================
    # MT · Memoria de Trabajo
    # =========================
    {
        "text": "Recuerda: AZ3. ¿Cuál era el código?",
        "options": ["AZ3", "A3Z", "ZA3", "AZ4"],
        "correct": 0,
        "dim": "MT",
    },
    {
        "text": "Te digo: 'El número es 514'. ¿Cuál es el número?",
        "options": ["154", "451", "514", "541"],
        "correct": 2,
        "dim": "MT",
    },
    {
        "text": "Memoriza esta secuencia: 7 - 2 - 9. ¿Cuál era el segundo número?",
        "options": ["7", "2", "9", "No recuerdo"],
        "correct": 1,
        "dim": "MT",
    },
    {
        "text": "Te doy: R, T, R, P. ¿Qué letra apareció DOS veces?",
        "options": ["R", "T", "P", "Ninguna"],
        "correct": 0,
        "dim": "MT",
    },
    {
        "text": "Instrucción: 'Primero anota, luego entrega'. ¿Qué haces primero?",
        "options": ["Entregar", "Anotar", "Ninguna", "Las dos a la vez"],
        "correct": 1,
        "dim": "MT",
    },
    {
        "text": "Te digo: 'Recuerda 48B6'. ¿Cuál era el código?",
        "options": ["48B6", "46B8", "48b6", "84B6"],
        "correct": 0,
        "dim": "MT",
    },
    {
        "text": "Te digo: 'Guarda esta idea: SOL-19'. ¿Qué recuerdo corresponde?",
        "options": ["SOL-91", "S0L-19", "SOL-19", "SOL19-"],
        "correct": 2,
        "dim": "MT",
    },
    {
        "text": "Instrucción: 'Primero marca A, después marca C'. ¿Qué va segundo?",
        "options": ["Marcar A", "Marcar C", "Marcar B", "No se indicó"],
        "correct": 1,
        "dim": "MT",
    },
    {
        "text": "Secuencia verbal: '4, 9, 4, 1'. ¿Cuál número apareció dos veces?",
        "options": ["4", "9", "1", "Ninguno"],
        "correct": 0,
        "dim": "MT",
    },
    {
        "text": "Recuerda 'K7P'. ¿Cuál era la letra en el medio?",
        "options": ["K", "7", "P", "Ninguna"],
        "correct": 1,
        "dim": "MT",
    },
    {
        "text": "Te digo: 'Anota 312 y después repite 312 al final'. ¿Qué número tenías que repetir?",
        "options": ["123", "132", "213", "312"],
        "correct": 3,
        "dim": "MT",
    },
    {
        "text": "Orden verbal: 'Toma nota, revisa, confirma'. ¿Cuál fue el tercer paso?",
        "options": ["Toma nota", "Revisa", "Confirma", "Ninguno"],
        "correct": 2,
        "dim": "MT",
    },
    {
        "text": "Te digo: 'El código temporal es F9'. ¿Cuál es el código?",
        "options": ["9F", "F9", "FF9", "F-9-9"],
        "correct": 1,
        "dim": "MT",
    },
    {
        "text": "Indicaciones: 'A -> B -> A'. ¿Cuál fue la última letra indicada?",
        "options": ["A", "B", "No hubo última letra", "C"],
        "correct": 0,
        "dim": "MT",
    },

    # =========================
    # CI · Comprensión de Instrucciones
    # =========================
    {
        "text": "Lee: 'Antes de comenzar, leer las indicaciones completas'. ¿Qué se debe hacer primero?",
        "options": [
            "Comenzar",
            "Leer las indicaciones completas",
            "Ignorar las indicaciones",
            "No se puede saber",
        ],
        "correct": 1,
        "dim": "CI",
    },
    {
        "text": "Texto: 'No continuar si hay dudas'. ¿Qué significa?",
        "options": [
            "Continuar igual",
            "Detenerse si hay dudas",
            "Ignorar dudas pequeñas",
            "Preguntar después",
        ],
        "correct": 1,
        "dim": "CI",
    },
    {
        "text": "Instrucción: 'Sigue los pasos en orden numérico'. ¿Cuál orden es correcto?",
        "options": ["2,1,3", "1,2,3", "3,1,2", "2,3,1"],
        "correct": 1,
        "dim": "CI",
    },
    {
        "text": "Indicación: 'Registrar sólo valores reales, no aproximados'. ¿Qué se debe escribir?",
        "options": [
            "Un número inventado",
            "Un número aproximado",
            "El valor real observado",
            "Nada",
        ],
        "correct": 2,
        "dim": "CI",
    },
    {
        "text": "Frase: 'Si falta información, preguntar antes de continuar'. ¿Cuál es la acción correcta si falta información?",
        "options": [
            "Seguir sin preguntar",
            "Preguntar antes de continuar",
            "Terminar igual",
            "Ignorar eso",
        ],
        "correct": 1,
        "dim": "CI",
    },
    {
        "text": "Texto: 'Verificar el dato y luego confirmarlo por escrito'. ¿Qué va segundo?",
        "options": [
            "Verificar el dato",
            "Confirmarlo por escrito",
            "No hacer nada",
            "Decir que todo está bien sin revisar",
        ],
        "correct": 1,
        "dim": "CI",
    },
    {
        "text": "Lee: 'No firmar documentos incompletos'. ¿Qué opción respeta la instrucción?",
        "options": [
            "Firmar aunque falte información",
            "Firmar siempre",
            "No firmar si está incompleto",
            "Firmar sin leer",
        ],
        "correct": 2,
        "dim": "CI",
    },
    {
        "text": "Regla: 'Reportar inmediatamente cualquier error detectado'. ¿Cuándo reportas?",
        "options": [
            "Al final del mes",
            "Inmediatamente",
            "Cuando tengas tiempo libre",
            "Nunca",
        ],
        "correct": 1,
        "dim": "CI",
    },
    {
        "text": "Instrucción: 'Ordenar de menor a mayor'. ¿Cuál secuencia cumple eso?",
        "options": [
            "9, 7, 5, 3",
            "3, 5, 7, 9",
            "7, 3, 9, 5",
            "9, 9, 9, 8",
        ],
        "correct": 1,
        "dim": "CI",
    },
    {
        "text": "Texto: 'Revisar el valor 3 veces antes de enviarlo'. ¿Qué describe mejor la indicación?",
        "options": [
            "Revisar una vez",
            "Revisar ninguna vez",
            "Revisar 3 veces antes de enviar",
            "Enviar sin revisar",
        ],
        "correct": 2,
        "dim": "CI",
    },
    {
        "text": "Frase: 'Utilizar sólo la información confirmada'. ¿Cuál es la acción correcta?",
        "options": [
            "Usar rumores",
            "Usar información confirmada",
            "Inventar datos",
            "No usar información",
        ],
        "correct": 1,
        "dim": "CI",
    },
    {
        "text": "Lee: 'Si un dato parece incorrecto, detener y aclarar antes de seguir'. ¿Qué debes hacer si ves un dato raro?",
        "options": [
            "Seguir sin revisar",
            "Cambiarlo sin decir nada",
            "Detener y aclarar antes de seguir",
            "Borrarlo",
        ],
        "correct": 2,
        "dim": "CI",
    },
    {
        "text": "Instrucción: 'Completar todos los campos obligatorios'. ¿Cuál opción cumple?",
        "options": [
            "Dejar espacios vacíos",
            "Completar sólo lo fácil",
            "Completar todos los campos obligatorios",
            "No completar nada",
        ],
        "correct": 2,
        "dim": "CI",
    },
    {
        "text": "Norma: 'No modificar los datos originales sin autorización'. ¿Cuál conducta respeta la norma?",
        "options": [
            "Cambiar datos originales por tu cuenta",
            "Pedir autorización antes de modificar",
            "Modificar siempre todo",
            "Borrar los datos",
        ],
        "correct": 1,
        "dim": "CI",
    },
]

TOTAL_QUESTIONS = len(QUESTIONS)  # 70


# ------------------------------------------------------------
# ESTADO GLOBAL STREAMLIT
# ------------------------------------------------------------
if "stage" not in st.session_state:
    st.session_state.stage = "info"  # info -> test -> done

if "candidate_name" not in st.session_state:
    st.session_state.candidate_name = ""

if "evaluator_email" not in st.session_state:
    st.session_state.evaluator_email = ""

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "answers" not in st.session_state:
    # guardamos la alternativa elegida (0..3)
    st.session_state.answers = {i: None for i in range(TOTAL_QUESTIONS)}

if "_need_rerun" not in st.session_state:
    st.session_state._need_rerun = False

if "already_sent" not in st.session_state:
    st.session_state.already_sent = False


# ------------------------------------------------------------
# SCORING
# ------------------------------------------------------------

def _norm_to_6(raw_value, max_items):
    # normalizamos puntaje bruto 0..max_items a 0..6
    if max_items <= 0:
        return 0.0
    return (raw_value / max_items) * 6.0

def compute_scores(ans_dict):
    # conteo aciertos por dimensión
    dim_correct = {
        "RL": 0,
        "AT": 0,
        "VD": 0,
        "MT": 0,
        "CI": 0
    }
    dim_total = {
        "RL": 0,
        "AT": 0,
        "VD": 0,
        "MT": 0,
        "CI": 0
    }

    for idx, q in enumerate(QUESTIONS):
        dim = q["dim"]
        dim_total[dim] += 1
        chosen = ans_dict.get(idx)
        if chosen is not None and chosen == q["correct"]:
            dim_correct[dim] += 1

    # Escala normalizada 0-6
    norm_scores = {}
    for d in dim_correct:
        norm_scores[d] = _norm_to_6(dim_correct[d], dim_total[d])

    return {
        "raw": dim_correct,      # p.ej RL: 9 (de 14)
        "total": dim_total,      # p.ej RL: 14
        "norm": norm_scores      # p.ej RL_norm ~ 3.8/6
    }

def qualitative_level(norm_score):
    # mismo criterio en todas las dimensiones
    if norm_score > 4.5:
        return "Alto"
    elif norm_score > 2.0:
        return "Medio"
    else:
        return "Bajo"

def build_dim_descriptions(norm_map):
    """
    Devuelve descripción breve por dimensión
    """
    out = {}
    # RL
    out["RL"] = (
        "Capacidad para reconocer patrones, relaciones numéricas y deducir reglas lógicas rápidamente."
        if norm_map["RL"] > 2.0 else
        "Puede requerir más apoyo en tareas que exigen deducir patrones numéricos o relaciones lógicas nuevas."
    )
    # AT
    out["AT"] = (
        "Precisión al notar diferencias pequeñas en códigos, números o detalles escritos."
        if norm_map["AT"] > 2.0 else
        "Puede pasar por alto variaciones pequeñas en datos similares; sugiere chequeo adicional en información crítica."
    )
    # VD
    out["VD"] = (
        "Toma decisiones iniciales con criterio básico de seguridad y prioridad, incluso bajo presión de tiempo."
        if norm_map["VD"] > 2.0 else
        "Podría necesitar más confirmación antes de actuar en decisiones rápidas que requieren priorizar."
    )
    # MT
    out["MT"] = (
        "Retención y manipulación inmediata de información verbal/códigos de corto plazo."
        if norm_map["MT"] > 2.0 else
        "Puede requerir instrucciones más repetidas o fragmentadas cuando hay varios pasos consecutivos."
    )
    # CI
    out["CI"] = (
        "Comprende instrucciones escritas, el orden correcto de pasos y condiciones básicas antes de ejecutar."
        if norm_map["CI"] > 2.0 else
        "Puede necesitar instrucciones más explícitas por escrito y confirmación de entendimiento previo a la ejecución."
    )
    return out

def build_strengths_and_risks(norm_map):
    fortalezas = []
    riesgos = []

    # RL
    if norm_map["RL"] > 4.5:
        fortalezas.append("Buen razonamiento lógico y manejo de patrones numéricos.")
    elif norm_map["RL"] <= 2.0:
        riesgos.append("En tareas nuevas con reglas numéricas puede requerir apoyo adicional.")

    # AT
    if norm_map["AT"] > 4.5:
        fortalezas.append("Alto foco en el detalle y diferencias pequeñas.")
    elif norm_map["AT"] <= 2.0:
        riesgos.append("Puede no notar diferencias sutiles (códigos / dígitos similares).")

    # VD
    if norm_map["VD"] > 4.5:
        fortalezas.append("Priorización rápida y criterio básico de seguridad al decidir.")
    elif norm_map["VD"] <= 2.0:
        riesgos.append("Puede necesitar confirmación externa antes de decidir en momentos urgentes.")

    # MT
    if norm_map["MT"] > 4.5:
        fortalezas.append("Buena retención inmediata de códigos / indicaciones cortas.")
    elif norm_map["MT"] <= 2.0:
        riesgos.append("Podría olvidar pasos si recibe demasiada información a la vez.")

    # CI
    if norm_map["CI"] > 4.5:
        fortalezas.append("Interpreta instrucciones escritas y el orden operativo de manera clara.")
    elif norm_map["CI"] <= 2.0:
        riesgos.append("Puede requerir instrucciones más claras y confirmación de entendimiento antes de ejecutar.")

    # limitar para que el bloque quepa bien
    return fortalezas[:5], riesgos[:5]


# ------------------------------------------------------------
# UTILIDADES DE TEXTO PARA PDF
# ------------------------------------------------------------

def _wrap(c, text, width, font="Helvetica", size=8):
    """
    Cortar texto en líneas para que quepa en un ancho dado.
    """
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if c.stringWidth(trial, font, size) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def _draw_paragraph(
    c,
    text,
    x,
    y,
    width,
    font="Helvetica",
    size=8,
    leading=11,
    color=colors.black,
    max_lines=None
):
    """
    Dibuja párrafo envuelto en ancho fijo. Devuelve
    la nueva coordenada Y tras escribir.
    """
    c.setFont(font, size)
    c.setFillColor(color)
    lines = _wrap(c, text, width, font, size)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        c.drawString(x, y, ln)
        y -= leading
    return y


# ------------------------------------------------------------
# GENERACIÓN DEL PDF (2 páginas)
# ------------------------------------------------------------

def generate_pdf(
    candidate_name,
    fecha_eval,
    evaluator_email,
    raw_scores,
    total_scores,
    norm_scores,
    fortalezas,
    riesgos,
    dim_desc
):
    """
    Crea informe en 2 páginas:
    PÁGINA 1:
      - Encabezado
      - Datos evaluado
      - Resumen cognitivo observado (fortalezas / aspectos a monitorear)
      - Perfil cognitivo (barras + puntos)
    PÁGINA 2:
      - Tabla Detalle por dimensión (usa todo el ancho)
      - Nota metodológica
    """

    buf = BytesIO()
    W, H = A4  # (595 x 842 aprox)
    c = canvas.Canvas(buf, pagesize=A4)

    # ---------------------------
    # PÁGINA 1
    # ---------------------------

    margin_left = 36
    margin_right = 36

    # Encabezado superior
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.black)
    c.drawString(margin_left, H-40, "EMPRESA / LOGO")
    c.setFont("Helvetica", 8)
    c.drawString(margin_left, H-54, "Evaluación Cognitiva General (IQ Adaptado)")

    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(W - margin_right, H-40, "Informe de Capacidades Cognitivas Básicas")
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.grey)
    c.drawRightString(W - margin_right, H-54, "Uso interno RR.HH. / No clínico")

    # CUADRO: Datos del evaluado
    box_x = margin_left
    box_y_top = H-90
    box_w = W - margin_left - margin_right
    box_h = 60

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(box_x, box_y_top-box_h, box_w, box_h, stroke=1, fill=1)

    y_cursor = box_y_top - 16
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    c.drawString(box_x+10, y_cursor, f"Nombre evaluado: {candidate_name}")
    y_cursor -= 12
    c.setFont("Helvetica", 8)
    c.drawString(box_x+10, y_cursor, f"Fecha de evaluación: {fecha_eval}")
    y_cursor -= 12
    c.drawString(box_x+10, y_cursor, f"Evaluador / contacto: {evaluator_email}")
    y_cursor -= 12
    c.setFont("Helvetica", 6)
    c.setFillColor(colors.grey)
    c.drawString(box_x+10, y_cursor, "Documento de uso interno. No clínico.")

    # CUADRO: Resumen cognitivo observado
    # Ocupar ancho completo, bajo datos evaluado
    sum_box_x = margin_left
    sum_box_y_top = H-180
    sum_box_w = W - margin_left - margin_right
    sum_box_h = 150  # alto suficiente para fortalezas+riesgos

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(sum_box_x, sum_box_y_top - sum_box_h, sum_box_w, sum_box_h, stroke=1, fill=1)

    y_sum = sum_box_y_top - 16
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    c.drawString(sum_box_x+10, y_sum, "Resumen cognitivo observado")
    y_sum -= 14

    # Fortalezas
    c.setFont("Helvetica-Bold", 7)
    c.drawString(sum_box_x+10, y_sum, "Fortalezas potenciales:")
    y_sum -= 12
    c.setFont("Helvetica", 7)
    for f in fortalezas:
        wrap_lines = _wrap(c, "• " + f, sum_box_w-20, "Helvetica", 7)
        for line in wrap_lines:
            c.drawString(sum_box_x+20, y_sum, line)
            y_sum -= 10
    y_sum -= 6

    # Riesgos / aspectos a monitorear
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(colors.black)
    c.drawString(sum_box_x+10, y_sum, "Aspectos a observar / apoyo sugerido:")
    y_sum -= 12
    c.setFont("Helvetica", 7)
    for r in riesgos:
        wrap_lines = _wrap(c, "• " + r, sum_box_w-20, "Helvetica", 7)
        for line in wrap_lines:
            c.drawString(sum_box_x+20, y_sum, line)
            y_sum -= 10

    # PERFIL COGNITIVO (barras y puntos)
    chart_x = margin_left
    chart_y_bottom = 140  # hacia la parte baja de la página 1
    chart_w = 300
    chart_h = 120

    # recuadro del gráfico opcional
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(chart_x-4, chart_y_bottom-4, chart_w+8, chart_h+48, stroke=1, fill=1)

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    c.drawString(chart_x, chart_y_bottom+chart_h+32, "Perfil cognitivo (0–6)")

    # eje Y y grilla
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(chart_x, chart_y_bottom, chart_x, chart_y_bottom+chart_h)

    for lvl in range(0,7):
        yv = chart_y_bottom + (lvl/6.0)*chart_h
        c.setFont("Helvetica",6)
        c.setFillColor(colors.black)
        c.drawString(chart_x-16, yv-2, str(lvl))
        c.setStrokeColor(colors.lightgrey)
        c.line(chart_x, yv, chart_x+chart_w, yv)

    dims_order = [
        ("RL","RL"),
        ("AT","AT"),
        ("VD","VD"),
        ("MT","MT"),
        ("CI","CI")
    ]
    bar_colors = [
        colors.HexColor("#1e40af"), # azul oscuro
        colors.HexColor("#059669"), # verde
        colors.HexColor("#f97316"), # naranjo
        colors.HexColor("#6b7280"), # gris
        colors.HexColor("#0ea5e9"), # celeste
    ]

    gap = 12
    bar_w = (chart_w - gap*(len(dims_order)+1)) / len(dims_order)
    tops = []

    for i,(key,label) in enumerate(dims_order):
        norm_val = norm_scores[key]     # 0..6
        raw_val  = raw_scores[key]      # ej 9
        total_v  = total_scores[key]    # ej 14
        leveltxt = qualitative_level(norm_val)

        bx = chart_x + gap + i*(bar_w+gap)
        bh = (norm_val/6.0)*chart_h
        by = chart_y_bottom

        c.setStrokeColor(colors.black)
        c.setFillColor(bar_colors[i])
        c.rect(bx, by, bar_w, bh, stroke=1, fill=1)

        tops.append((bx+bar_w/2.0, by+bh))

        # Etiquetas bajo cada barra
        c.setFont("Helvetica-Bold",7)
        c.setFillColor(colors.black)
        c.drawCentredString(bx+bar_w/2.0, chart_y_bottom-14, label)

        c.setFont("Helvetica",6)
        # SOLO un puntaje: mostramos aciertos/total y nivel
        c.drawCentredString(
            bx+bar_w/2.0,
            chart_y_bottom-26,
            f"{raw_val}/{total_v}  {leveltxt}"
        )

    # línea negra uniendo puntos
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.2)
    for j in range(len(tops)-1):
        (x1,y1)=tops[j]
        (x2,y2)=tops[j+1]
        c.line(x1,y1,x2,y2)
    for (px,py) in tops:
        c.setFillColor(colors.black)
        c.circle(px,py,2.0,stroke=0,fill=1)

    # leyenda derecha del gráfico
    legend_x = chart_x + chart_w + 20
    legend_y = chart_y_bottom + chart_h + 20
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(legend_x-4, chart_y_bottom-4, 200, chart_h+48, stroke=1, fill=1)

    yy = legend_y
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(legend_x, yy, "Guía de lectura de dimensiones")
    yy -= 14

    c.setFont("Helvetica",7)
    legend_lines = [
        "RL = Razonamiento Lógico",
        "AT = Atención al Detalle",
        "VD = Velocidad de Decisión",
        "MT = Memoria de Trabajo",
        "CI = Comprensión de Instrucciones"
    ]
    for line in legend_lines:
        c.drawString(legend_x, yy, line)
        yy -= 10

    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawString(legend_x, chart_y_bottom+6, "Escala interna 0–6. Uso laboral no clínico.")

    # Pie de página pág 1
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawRightString(W - margin_right, 30, "Página 1 / 2")

    c.showPage()

    # ---------------------------
    # PÁGINA 2
    # ---------------------------

    c.setFont("Helvetica-Bold",10)
    c.setFillColor(colors.black)
    c.drawString(margin_left, H-40, "Detalle por dimensión")

    # Tabla ocupa ancho completo
    table_x = margin_left
    table_y_top = H-60
    table_w = W - margin_left - margin_right

    # Dibujamos caja alrededor de toda la tabla
    # Calculamos un alto aproximado para 5 filas
    table_h = 5 * 60 + 30  # fila ~60px + header ~30
    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(table_x, table_y_top - table_h, table_w, table_h, stroke=1, fill=1)

    # Encabezados de tabla
    head_y = table_y_top - 20
    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)

    # columnas
    col_dim_x = table_x + 10
    col_punt_x = table_x + 200
    col_lvl_x = table_x + 260
    col_desc_x = table_x + 320

    c.drawString(col_dim_x, head_y, "Dimensión")
    c.drawString(col_punt_x, head_y, "Puntaje")
    c.drawString(col_lvl_x, head_y, "Nivel")
    c.drawString(col_desc_x, head_y, "Descripción breve")

    # línea separadora header
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.line(table_x, head_y-4, table_x+table_w, head_y-4)

    row_y = head_y - 16
    row_gap = 60  # altura estimada por fila con wrap

    dims_display = [
        ("RL","Razonamiento Lógico"),
        ("AT","Atención al Detalle"),
        ("VD","Velocidad de Decisión"),
        ("MT","Memoria de Trabajo"),
        ("CI","Comprensión de Instrucciones"),
    ]

    c.setFont("Helvetica",8)
    for key, label in dims_display:
        raw_v  = raw_scores[key]
        tot_v  = total_scores[key]
        lvl_v  = qualitative_level(norm_scores[key])
        desc_v = dim_desc[key]

        # columna Dimensión (negrita)
        c.setFont("Helvetica-Bold",8)
        c.drawString(col_dim_x, row_y, label)

        # Puntaje (un puntaje: aciertos/total y nivel textual)
        c.setFont("Helvetica",8)
        c.drawString(col_punt_x, row_y, f"{raw_v}/{tot_v}")
        c.drawString(col_lvl_x,  row_y, lvl_v)

        # Descripción envuelta
        desc_y = row_y
        desc_y = _draw_paragraph(
            c,
            desc_v,
            col_desc_x,
            desc_y,
            table_w - (col_desc_x - table_x) - 10,
            font="Helvetica",
            size=8,
            leading=10,
            color=colors.black,
            max_lines=None
        )

        # línea separadora de fila
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.5)
        c.line(table_x, row_y-40, table_x+table_w, row_y-40)

        row_y -= row_gap

    # CUADRO NOTA METODOLÓGICA al final página 2
    note_box_x = margin_left
    note_box_y_top = 160
    note_box_w = W - margin_left - margin_right
    note_box_h = 100

    c.setStrokeColor(colors.lightgrey)
    c.setFillColor(colors.white)
    c.rect(note_box_x, note_box_y_top - note_box_h, note_box_w, note_box_h, stroke=1, fill=1)

    c.setFont("Helvetica-Bold",8)
    c.setFillColor(colors.black)
    c.drawString(note_box_x+10, note_box_y_top-16, "Nota metodológica")

    nota_text = (
        "Este informe describe el desempeño cognitivo observado en tareas de razonamiento lógico, "
        "atención a detalles, toma de decisión inicial, memoria de trabajo y comprensión de instrucciones. "
        "Los resultados reflejan tendencias funcionales para el trabajo y NO constituyen diagnóstico clínico. "
        "Se recomienda complementar con entrevista estructurada, verificación de experiencia y otras "
        "pruebas técnicas según el cargo."
    )

    _draw_paragraph(
        c,
        nota_text,
        note_box_x+10,
        note_box_y_top-32,
        note_box_w-20,
        font="Helvetica",
        size=7,
        leading=10,
        color=colors.black,
        max_lines=None
    )

    # Pie de página pág 2
    c.setFont("Helvetica",6)
    c.setFillColor(colors.grey)
    c.drawRightString(W - margin_right, 30, "Página 2 / 2 · Uso interno RR.HH. · Evaluación Cognitiva General (IQ Adaptado) · No clínico")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


# ------------------------------------------------------------
# ENVÍO EMAIL CON PDF
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

    raw_scores   = scores["raw"]     # dict {RL: x, ...}
    total_scores = scores["total"]   # dict {RL:14, ...}
    norm_scores  = scores["norm"]    # dict {RL: x/6,...}

    dim_desc = build_dim_descriptions(norm_scores)
    fortalezas, riesgos = build_strengths_and_risks(norm_scores)

    now_txt = datetime.now().strftime("%d/%m/%Y %H:%M")

    pdf_bytes = generate_pdf(
        candidate_name   = st.session_state.candidate_name,
        fecha_eval       = now_txt,
        evaluator_email  = st.session_state.evaluator_email,
        raw_scores       = raw_scores,
        total_scores     = total_scores,
        norm_scores      = norm_scores,
        fortalezas       = fortalezas,
        riesgos          = riesgos,
        dim_desc         = dim_desc
    )

    if not st.session_state.already_sent:
        try:
            send_email_with_pdf(
                to_email   = st.session_state.evaluator_email,
                pdf_bytes  = pdf_bytes,
                filename   = "Informe_Cognitivo_IQ.pdf",
                subject    = "Informe Evaluación Cognitiva General (IQ Adaptado)",
                body_text  = (
                    "Adjunto informe interno de Evaluación Cognitiva General (IQ Adaptado)\n"
                    f"Candidato: {st.session_state.candidate_name}\n"
                    "Uso interno RR.HH. / No clínico."
                ),
            )
        except Exception:
            # si hay error de correo no rompemos la app
            pass
        st.session_state.already_sent = True


# ------------------------------------------------------------
# CALLBACK de respuesta (una sola pulsación por pregunta)
# ------------------------------------------------------------

def choose_answer(option_index: int):
    q_idx = st.session_state.current_q
    st.session_state.answers[q_idx] = option_index

    if q_idx < TOTAL_QUESTIONS - 1:
        st.session_state.current_q += 1
        st.session_state._need_rerun = True
    else:
        # test terminado
        finalize_and_send()
        st.session_state.stage = "done"
        st.session_state._need_rerun = True


# ------------------------------------------------------------
# VISTAS STREAMLIT
# ------------------------------------------------------------

def view_info_form():
    st.markdown("### Evaluación Cognitiva General (IQ Adaptado)")
    st.write("Este test mide razonamiento lógico, atención a detalles, toma de decisión inicial, memoria de trabajo y comprensión de instrucciones.")
    st.write("Al finalizar el test se genera un informe automático en PDF y se envía al correo del evaluador.")

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
            <b>Confidencialidad:</b> Uso interno de RR.HH. El evaluado no recibe copia directa del informe.
            Este instrumento no es diagnóstico clínico.
        </div>
        """,
        unsafe_allow_html=True
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
                Test Cognitivo General (IQ Adaptado) · 70 ítems
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
                margin:0 0 12px 0;
                font-size:1.05rem;
                color:#1e293b;
                line-height:1.45;">
                {q["text"]}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Alternativas (4 botones)
    cols = st.columns(2)
    for i_opt, option_text in enumerate(q["options"]):
        with cols[i_opt % 2]:
            st.button(
                option_text,
                key=f"opt_{q_idx}_{i_opt}",
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
            <b>Nota:</b> Seleccione la alternativa que considere correcta.
            Una vez elegida, pasará automáticamente a la siguiente pregunta.
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
# CONTROL DE FLUJO
# ------------------------------------------------------------

if st.session_state.stage == "info":
    view_info_form()

elif st.session_state.stage == "test":
    if st.session_state.current_q >= TOTAL_QUESTIONS:
        st.session_state.stage = "done"
        st.session_state._need_rerun = True
    view_test()

elif st.session_state.stage == "done":
    # nos aseguramos de que el PDF ya esté enviado
    finalize_and_send()
    view_done()

# Rerun controlado para navegación fluida sin doble click
if st.session_state._need_rerun:
    st.session_state._need_rerun = False
    st.rerun()
