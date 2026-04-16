from openai import OpenAI
import streamlit as st
import joblib
import pandas as pd


# Diseño

# UI

st.set_page_config(page_title="SeguroSmart AI", layout="centered")

st.markdown("""
<style>

/* Fondo */
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: #e2e8f0;
}

/* Títulos */
h1, h2, h3 {
    color: #f8fafc;
}

/* Subheader */
.css-10trblm {
    text-align: center;
}

/* Botones */
.stButton > button {
    background: linear-gradient(90deg, #6366f1, #22c55e);
    color: white;
    border-radius: 12px;
    height: 3em;
    font-weight: bold;
    border: none;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: scale(1.03);
    opacity: 0.9;
}

/* Inputs */
.stSelectbox, .stSlider {
    background-color: #1e293b;
    border-radius: 10px;
    padding: 5px;
}

/* Separadores */
hr {
    border: 1px solid #334155;
}

/* Mensajes */
.stSuccess {
    background-color: #22c55e !important;
    color: black !important;
    border-radius: 12px;
    font-weight: bold;
}

/* Chat */
[data-testid="stChatMessage"] {
    background-color: #1e293b;
    border-radius: 12px;
    padding: 10px;
}

/* Labels */
label {
    color: #cbd5f5 !important;
    font-weight: 500;
}

/* Caption */
.css-1v0mbdj p {
    color: #94a3b8;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-thumb {
    background: #475569;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# Header

st.markdown("""
<h1 style='text-align: center;'>🛡️ SeguroSmart AI</h1>
<p style='text-align: center; color: #94a3b8; font-size: 16px;'>

¡Tu asesor inteligente de seguros en segundos!

Analiza tu perfil financiero y de riesgo para recomendarte el seguro ideal de forma clara y personalizada
</p>
""", unsafe_allow_html=True)



# CONFIG IA


client = OpenAI()


# CARGAR MODELO


model = joblib.load("modelo_seguro.pkl")
columns = joblib.load("columnas.pkl")

# GUÍA PRÁCTICA

st.markdown("""
<div style='background-color:#1e293b;padding:15px;border-radius:12px;margin-bottom:15px;'>

### 🚀 Empieza en 3 pasos

✔ Completa tu perfil  
✔ Da clic en **"Analizar perfil"**  
✔ Recibe tu recomendación personalizada  

<p style='color:#94a3b8;font-size:13px;margin-top:10px;'>
También puedes explorar explicaciones, riesgos, comparaciones y hacer preguntas al asesor 🤖
</p>

</div>
""", unsafe_allow_html=True)


st.markdown("### 🧾 Completa tu perfil")

# INPUTS


edad = st.slider("Edad", 20, 35)

ingreso_opcion = st.selectbox("Ingresos mensuales", [
    "Menos de 10k",
    "10k-20k",
    "20k-40k",
    "40k-60k",
    "60k+"
])

ingresos_map = {
    "Menos de 10k": 8000,
    "10k-20k": 15000,
    "20k-40k": 30000,
    "40k-60k": 50000,
    "60k+": 70000
}

ingresos = ingresos_map[ingreso_opcion]

dependientes = st.selectbox("Dependientes", [0,1,2,3,4])

ocupacion = st.selectbox("Ocupación", ["formal","informal","independiente"])
tipo_vivienda = st.selectbox("Tipo de vivienda", ["propia","rentada"])

fuma = 1 if st.selectbox("¿Fuma?", ["No","Sí"]) == "Sí" else 0
ejercicio = 1 if st.selectbox("¿Hace ejercicio?", ["No","Sí"]) == "Sí" else 0
enfermedad = 1 if st.selectbox("¿Tiene enfermedad?", ["No","Sí"]) == "Sí" else 0

tiene_auto = 1 if st.selectbox("¿Tiene auto?", ["No","Sí"]) == "Sí" else 0


# BOTÓN PRINCIPAL


if st.button("Analizar perfil"):

    st.session_state.pop("explicacion", None)

    input_data = pd.DataFrame(columns=columns)
    input_data.loc[0] = 0

    input_data["edad"] = edad
    input_data["ingresos"] = ingresos
    input_data["dependientes"] = dependientes
    input_data["tiene_auto"] = tiene_auto

    input_data["capacidad_pago"] = ingresos / (dependientes + 1)

    riesgo_score = (
        edad * 0.25 +
        enfermedad * 25 +
        fuma * 15 -
        ejercicio * 10
    )

    input_data["riesgo_score"] = riesgo_score

    input_data["indice_proteccion_actual"] = (
        tiene_auto * 20 +
        (1 if tipo_vivienda == "propia" else 0) * 20
    )

    input_data["tiene_seguridad_social"] = 1 if ocupacion == "formal" else 0

    input_data["estabilidad_ingresos"] = {
        "formal": 2,
        "independiente": 1,
        "informal": 0
    }[ocupacion]

    input_data["estado_civil_soltero"] = 1
    input_data["ocupacion_independiente"] = 1 if ocupacion == "independiente" else 0
    input_data["ocupacion_informal"] = 1 if ocupacion == "informal" else 0
    input_data["tipo_vivienda_rentada"] = 1 if tipo_vivienda == "rentada" else 0

    for col in columns:
        if col not in input_data:
            input_data[col] = 0

    input_data = input_data[columns]

    _ = model.predict(input_data)[0]

    # SISTEMA INTELIGENTE
  

    scores = {}

    score_salud = 0
    if enfermedad == 1:
        score_salud += 70
    if fuma == 1:
        score_salud += 30
    if edad > 50:
        score_salud += 20

    if score_salud > 0:
        scores["salud"] = score_salud

    if dependientes > 0:
        score_vida = 60
        if ingresos > 20000:
            score_vida += 20
        if ingresos < 15000:
            score_vida += 10
        scores["vida"] = score_vida

    if tiene_auto:
        score_auto = 40
        if ingresos > 20000:
            score_auto += 10
        scores["auto"] = score_auto

    if tipo_vivienda == "propia":
        scores["hogar"] = 30

    if len(scores) == 0:
        scores["salud"] = 10

    ranking = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    principal = ranking[0][0]
    secundario = ranking[1][0] if len(ranking) > 1 else None

    map_names = {
        "vida": "Seguro de Vida ❤️",
        "salud": "Seguro de Gastos Médicos 🏥",
        "auto": "Seguro de Auto 🚗",
        "hogar": "Seguro de Hogar 🏠"
    }

    st.session_state.update({
        "principal": principal,
        "secundario": secundario,
        "map_names": map_names,
        "edad": edad,
        "ingreso_opcion": ingreso_opcion,
        "dependientes": dependientes,
        "ocupacion": ocupacion,
        "tipo_vivienda": tipo_vivienda,
        "fuma": fuma,
        "ejercicio": ejercicio,
        "enfermedad": enfermedad,
        "tiene_auto": tiene_auto,
        "riesgo_score": riesgo_score
    })


# RESULTADOS


if "principal" in st.session_state:

    st.success(f"🎯 Recomendación principal: {st.session_state['map_names'][st.session_state['principal']]}")

    st.markdown("### 🧩 Segunda recomendación")

    if st.session_state["secundario"]:
        st.write(f"👉 {st.session_state['map_names'][st.session_state['secundario']]}")
    else:
        st.write("No se detectan necesidades adicionales relevantes")

    st.markdown("---")
    st.markdown("### 📊 Indicador de riesgo (referencial)")

    r = st.session_state["riesgo_score"]

    if r < 20:
        st.write("🟢 Riesgo bajo")
    elif r < 40:
        st.write("🟡 Riesgo medio")
    else:
        st.write("🔴 Riesgo alto")


# IA EXPLICACIÓN


if "principal" in st.session_state:

    st.markdown("---")
    st.markdown("### 🤖 Explicación inteligente con IA")

    if st.button("Explícame esta recomendación"):

        st.session_state["generando_exp"] = True
        st.session_state["explicacion"] = ""

        prompt = f"""
        Eres un asesor experto en seguros personales.

        REGLAS:
        - No hagas preguntas
        - No invites a continuar
        - No uses frases como "si quieres"
        - Respuesta clara y profesional
        - Usa lenguaje claro y entendible para el usuario
        - Debes ser breve (en máximo 10 renglones cumplir con el objetivo)
        - Usa los elementos que quieras para facilitar la lectura al usuario
        - Estructura el texto a manera de que se vea bonito y no amontonado

        Usuario:
        Edad: {st.session_state['edad']}
        Ingresos: {st.session_state['ingreso_opcion']}
        Dependientes: {st.session_state['dependientes']}
        Ocupación: {st.session_state['ocupacion']}
        Vivienda: {st.session_state['tipo_vivienda']}

        Seguro: {st.session_state['map_names'][st.session_state['principal']]}

        Explica por qué es recomendable y qué cubre.
        """

        with st.chat_message("assistant"):
            placeholder = st.empty()

            with client.responses.stream(
                model="gpt-5-mini",
                input=prompt
            ) as stream:

                for event in stream:
                    if event.type == "response.output_text.delta":
                        st.session_state["explicacion"] += event.delta
                        placeholder.markdown(st.session_state["explicacion"] + "▌")

            placeholder.markdown(st.session_state["explicacion"])
            st.session_state["generando_exp"] = False



# ⚠️ ESCENARIO SIN SEGURO


if "principal" in st.session_state:

    st.markdown("---")
    st.markdown("### ⚠️  Riesgo de no estar asegurado")

    if st.button("Analizar riesgo sin seguro"):

        with st.chat_message("assistant"):

            placeholder = st.empty()
            respuesta = ""

            prompt = f"""
            Eres un asesor de riesgos.

            Usuario:
            Edad: {st.session_state['edad']}
            Ingresos: {st.session_state['ingreso_opcion']}
            Dependientes: {st.session_state['dependientes']}
            Seguro recomendado: {st.session_state['map_names'][st.session_state['principal']]}

            Explica qué podría pasar si NO contrata este seguro.
            Incluye:
            - Consecuencias financieras
            - Riesgos personales
            - Impacto a corto y largo plazo
            - Apela, motiva o incita a que se contrate el seguro
            -Usa lenguaje claro y entendible para el usuario
            - Debes ser breve (en máximo 10 renglones cumplir con el objetivo)
            - Usa los elementos que quieras para facilitar la lectura al usuario
            - Estructura el texto a manera de que se vea bonito y no amontonado

            No hagas preguntas.
            No invites a continuar.
            """

            with client.responses.stream(
                model="gpt-5-mini",
                input=prompt
            ) as stream:

                for event in stream:
                    if event.type == "response.output_text.delta":
                        respuesta += event.delta
                        placeholder.markdown(respuesta + "▌")

            placeholder.markdown(respuesta)


# ⚖️ COMPARADOR DE SEGUROS


st.markdown("---")
st.markdown("### ⚖️ Comparador inteligente de seguros")

seguro1 = st.selectbox("Seguro 1", ["vida", "salud", "auto", "hogar"], key="seg1")
seguro2 = st.selectbox("Seguro 2", ["vida", "salud", "auto", "hogar"], key="seg2")

if st.button("Comparar seguros"):

    with st.chat_message("assistant"):

        placeholder = st.empty()
        respuesta = ""

        prompt = f"""
        Eres un asesor experto en seguros.

        Compara:
        - {seguro1}
        - {seguro2}

        Explica:
        - Diferencias clave
        - Cuándo conviene cada uno
        - Para qué tipo de persona es mejor cada uno
        - Debes ser breve (en máximo 10 renglones cumplir con el objetivo)
        - Usa los elementos que quieras para facilitar la lectura al usuario
        - Estructura el texto a manera de que se vea bonito y no amontonado

        Respuesta clara, profesional y directa.
        No hagas preguntas.
        """

        with client.responses.stream(
            model="gpt-5-mini",
            input=prompt
        ) as stream:

            for event in stream:
                if event.type == "response.output_text.delta":
                    respuesta += event.delta
                    placeholder.markdown(respuesta + "▌")

        placeholder.markdown(respuesta)


st.markdown("---")
st.markdown("## 🧠 Explora más opciones")


# CHAT


if "chat" not in st.session_state:
    st.session_state.chat = []


st.markdown("""
<p style='color:#94a3b8;font-size:14px;'>
Interactúa con el asesor en tiempo real usando el chat inferior ⬇️
</p>
""", unsafe_allow_html=True)


user_input = st.chat_input("Puedes preguntarme sobre seguros, coberturas o recomendaciones personalizadas...")


for i, (role, msg) in enumerate(st.session_state.chat):
    if i == len(st.session_state.chat) - 1 and role == "assistant":
        continue
    with st.chat_message("user" if role == "user" else "assistant"):
        st.markdown(msg)

if user_input:

    st.session_state.chat.append(("user", user_input))

   
    with st.chat_message("user"):
        st.markdown(user_input)

  
    with st.chat_message("assistant"):

        placeholder = st.empty()
        respuesta = ""

        with client.responses.stream(
            model="gpt-5-mini",
            input=f"""
            Eres asesor experto en seguros.

            SOLO habla de seguros (vida, salud, auto, hogar), no respondas a cuestionamientos de cualquier otro tipo.
            Si no: "Solo puedo ayudarte con temas de seguros".

            - Debes ser breve (en máximo 15 renglones cumplir con el objetivo)
            - Usa los elementos que quieras para facilitar la lectura al usuario
            - Estructura el texto a manera de que se vea bonito y no amontonado
            Pregunta:
            {user_input}
            """
        ) as stream:

            for event in stream:
                if event.type == "response.output_text.delta":
                    respuesta += event.delta
                    placeholder.markdown(respuesta + "▌")

        placeholder.markdown(respuesta)

    st.session_state.chat.append(("assistant", respuesta))