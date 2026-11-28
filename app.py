import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import streamlit_authenticator as stauth
import os
import json
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="AquaControl - Agua del Valle", page_icon="💧", layout="wide")

# --- CSS PERSONALIZADO (DARK MODE / AQUA THEME) ---
st.markdown("""
<style>
    /* 1. Fondo principal oscuro */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* 2. Sidebar oscuro */
    [data-testid="stSidebar"] {
        background-color: #161B22 !important;
        border-right: 1px solid #30363D;
    }
    
    /* Ocultar círculos del menú lateral y dar estilo a los botones */
    [data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { 
        display: none !important; width: 0 !important; margin: 0 !important; 
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label { 
        background-color: transparent; 
        border-radius: 6px; 
        padding: 10px 15px; 
        margin-bottom: 2px; 
        cursor: pointer; 
        border-left: 4px solid transparent; 
        width: 100%; 
        transition: all 0.2s ease; 
        color: #C9D1D9 !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover { 
        background-color: rgba(255, 255, 255, 0.05); 
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] { 
        background-color: rgba(0, 168, 232, 0.15) !important; 
        border-left: 4px solid #00A8E8 !important; 
        font-weight: bold; 
        color: #FFFFFF !important;
    }

    /* 3. Estilo de la tarjeta de login */
    div[data-testid="stVerticalBlock"] > div:has(div.stTabs) {
        background-color: #161B22;
        padding: 2.5rem 2rem;
        border-radius: 12px;
        border: 1px solid #30363D;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
    }

    /* 4. Ajustes de textos y títulos */
    h1, h2, h3, h4, h5, p, span, div {
        color: #FAFAFA;
    }
    
    /* 5. Inputs y Selectbox oscuros */
    div[data-baseweb="input"] input, 
    div[data-baseweb="select"] > div {
        background-color: #0D1117 !important;
        color: #FAFAFA !important;
        border: 1px solid #30363D !important;
    }
    
    /* 6. Pestañas de Login (Tabs) */
    button[data-baseweb="tab"] {
        color: #8B949E !important;
        background-color: transparent !important;
    }
    button[aria-selected="true"] {
        color: #FFFFFF !important;
        border-bottom-color: #00A8E8 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- ARCHIVOS DE CONFIGURACIÓN Y PERSISTENCIA ---
LOGO_FILENAME = "AquaControlLogo.png"
USERS_FILE = "users_aquacontrol.json"
LECTURAS_FILE = "lecturas_diarias.csv"
ALERTAS_FILE = "alertas_fugas.csv"
BALANCE_FILE = "balance_mensual.csv"

# --- FUNCIÓN PARA MANEJAR USUARIOS (JSON) ---
def cargar_usuarios():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        try:
            hash_admin = stauth.Hasher.hash("123")
            hash_op = stauth.Hasher.hash("456")
            hash_amb = stauth.Hasher.hash("789")
        except AttributeError:
            hash_admin = stauth.Hasher(["123"]).generate()[0]
            hash_op = stauth.Hasher(["456"]).generate()[0]
            hash_amb = stauth.Hasher(["789"]).generate()[0]

        default_credentials = {
            "usernames": {
                "admin": {
                    "name": "Supervisor General",
                    "password": hash_admin,
                    "email": "agua@aquacontrol.com",
                    "role": "Administrador"
                },
                "operador1": {
                    "name": "Carlos Méndez",
                    "password": hash_op,
                    "email": "operaciones@aquacontrol.com",
                    "role": "Operador"
                },
                "ambiental1": {
                    "name": "Ing. Laura Gómez",
                    "password": hash_amb,
                    "email": "ambiental@aquacontrol.com",
                    "role": "Área Ambiental"
                }
            }
        }
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_credentials, f, indent=4)
        return default_credentials

# --- INICIALIZACIÓN DE DATOS PERSISTENTES ---
def inicializar_datos():
    if not os.path.exists(LECTURAS_FILE):
        df_lec = pd.DataFrame([
            {
                "fecha": "2026-11-24", "hora": "07:00", "operario": "Carlos Méndez",
                "id_medidor": "AC-M001", "sector": "Sector Norte",
                "lect_ant": 800, "lect_actual": 850, "consumo_m3": 50, "consumo_L": 50000,
                "observaciones": "Lectura normal en números negros"
            }
        ])
        df_lec.to_csv(LECTURAS_FILE, index=False)

    if not os.path.exists(ALERTAS_FILE):
        df_ale = pd.DataFrame([
            {
                "fecha": "2026-11-24", "hora": "03:15", "id_medidor": "AC-M004",
                "ubicacion": "Sector Este", "vol_registrado_m3": 215, "vol_esperado_m3": 160,
                "diferencia_m3": 55, "diferencia_L": 55000,
                "senal_tipo": "Consumo anómalo (Nocturno)",
                "checklist": "Tuberías: Grietas/goteos | Válvulas: Cierres",
                "accion_tomada": "Cierre preventivo de válvula secundaria y activación de reutilización",
                "estado": "En proceso"
            }
        ])
        df_ale.to_csv(ALERTAS_FILE, index=False)

    if not os.path.exists(BALANCE_FILE):
        df_bal = pd.DataFrame([
            {"Fecha": "2026-11-19", "ID Medidor": "AC-M001", "Sector": "Sector Norte", "Vol Extraído m3": 220, "Vol Consumido m3": 170, "Vol Reutilizado m3": 30, "Pérdida m3": 50, "Costo m3": 1.25, "Consumo Usuario L/dia": 180},
            {"Fecha": "2026-11-20", "ID Medidor": "AC-M002", "Sector": "Sector Centro", "Vol Extraído m3": 210, "Vol Consumido m3": 165, "Vol Reutilizado m3": 28, "Pérdida m3": 45, "Costo m3": 1.25, "Consumo Usuario L/dia": 178},
            {"Fecha": "2026-11-21", "ID Medidor": "AC-M003", "Sector": "Sector Sur", "Vol Extraído m3": 205, "Vol Consumido m3": 160, "Vol Reutilizado m3": 25, "Pérdida m3": 45, "Costo m3": 1.25, "Consumo Usuario L/dia": 182},
            {"Fecha": "2026-11-22", "ID Medidor": "AC-M004", "Sector": "Sector Este", "Vol Extraído m3": 215, "Vol Consumido m3": 160, "Vol Reutilizado m3": 35, "Pérdida m3": 55, "Costo m3": 1.25, "Consumo Usuario L/dia": 185},
            {"Fecha": "2026-11-23", "ID Medidor": "AC-M005", "Sector": "Sector Oeste", "Vol Extraído m3": 200, "Vol Consumido m3": 155, "Vol Reutilizado m3": 32, "Pérdida m3": 45, "Costo m3": 1.25, "Consumo Usuario L/dia": 176},
            {"Fecha": "2026-11-24", "ID Medidor": "AC-M006", "Sector": "Sector Rural", "Vol Extraído m3": 150, "Vol Consumido m3": 150, "Vol Reutilizado m3": 10, "Pérdida m3": 0, "Costo m3": 1.25, "Consumo Usuario L/dia": 179},
        ])
        df_bal.to_csv(BALANCE_FILE, index=False)

credentials = cargar_usuarios()
inicializar_datos()

# ==========================================
# --- MÓDULOS DE AQUACONTROL ---
# ==========================================

def modulo_dashboard():
    st.subheader("📊 Tablero General y 6 KPIs (Formato 3 - F-CMK-03)")
    st.write("Monitoreo en tiempo real: **Agua del Valle S.A. de C.V.** | Meta a 3 años: **Reducir 30% extracción y pérdida de agua**.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Agua Extraída (Hoy)", "1,200,000 L/día", "Meta 3 años: 840,000 L (-30%)", delta_color="inverse")
    c2.metric("Agua Utilizada", "960,000 L/día", "80% aprovechamiento")
    c3.metric("Agua Perdida (Hoy)", "240,000 L/día (20%)", "Meta 3 años: 168,000 L (-30%)", delta_color="inverse")
    c4.metric("Agua Reutilizada", "80,000 L/día", "Captación lluvia + reuso")

    st.divider()
    st.markdown("### 🎯 Los 6 KPIs de Desempeño Hídrico")
    k1, k2, k3 = st.columns(3)
    k1.metric("1. % Pérdidas Hoy", "20.0%", "Meta: < 10.0%", delta_color="inverse")
    k2.metric("2. % Agua Reutilizada", "12.0%", "Meta: > 25.0%")
    k3.metric("3. Consumo por Usuario", "180 L/día", "Por trabajador/día")

    k4, k5, k6 = st.columns(3)
    k4.metric("4. Costo por m³", "$1.25 MXN", "Meta: $1.00 MXN", delta_color="inverse")
    k5.metric("5. Balance Hídrico", "0 (Equilibrado)", "Extracción - Consumo - Pérdida - Reuso")
    k6.metric("6. Ahorro Proyectado", "120,000 L/día", "43.8M L/año al bajar pérdidas al 10%")

    st.divider()

    with st.expander("📥 Importar Concentrado Mensual (Formato 3 - CSV / XLSX)"):
        archivo_f3 = st.file_uploader("Sube el archivo exportado por Supervisión:", type=["csv", "xlsx"])
        if archivo_f3 is not None:
            try:
                if archivo_f3.name.endswith(".csv"):
                    df_imp = pd.read_csv(archivo_f3)
                else:
                    df_imp = pd.read_excel(archivo_f3)
                df_imp.to_csv(BALANCE_FILE, index=False)
                st.success("✅ Concentrado Formato 3 importado y actualizado correctamente.")
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")

    df_bal = pd.read_csv(BALANCE_FILE)

    col_graf, col_tabla = st.columns([1.2, 1])
    with col_graf:
        st.markdown("### 📈 Gráfica Diaria: Extraída vs. Consumida vs. Pérdida vs. Reutilizada (m³)")
        chart_data = df_bal.set_index("Fecha")[["Vol Extraído m3", "Vol Consumido m3", "Pérdida m3", "Vol Reutilizado m3"]]
        st.bar_chart(chart_data)

    with col_tabla:
        st.markdown("### 📋 Registro por Sector y Medidor")
        st.dataframe(df_bal, use_container_width=True)


def modulo_captura(nombre_usuario):
    st.subheader("📱 Módulo 1: Captura Diaria de Medidor (Formato 1 - F-RDL-01)")
    st.info("📌 **Regla de lectura:** Lee de izquierda a derecha y registra **únicamente los números negros ($m^3$)**. Ignora los números rojos (decimales). Conversión automática: $1\\text{ }m^3 = 1,000\\text{ Litros}$.")

    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha:", value=datetime.today())
        hora = st.time_input("Hora:", value=datetime.now().time())
        operario = st.text_input("Nombre del operario:", value=nombre_usuario)
        id_medidor = st.selectbox("ID del Medidor:", ["AC-M001", "AC-M002", "AC-M003", "AC-M004", "AC-M005", "AC-M006"])
        sector = st.selectbox("Ubicación / Sector:", ["Sector Norte", "Sector Centro", "Sector Sur", "Sector Este", "Sector Oeste", "Sector Rural"])

    with col2:
        lect_ant = st.number_input("Lectura anterior (m³ - solo números negros):", min_value=0, value=800, step=1)
        lect_actual = st.number_input("Lectura actual (m³ - solo números negros):", min_value=0, value=850, step=1)
        foto_medidor = st.file_uploader("📸 Foto del medidor como comprobación:", type=["jpg", "jpeg", "png"])
        observaciones = st.text_area("Observaciones (fugas, presión baja, humedad):", placeholder="Ej. Mica limpia, sin goteos visibles...")

    consumo_m3 = lect_actual - lect_ant
    consumo_L = consumo_m3 * 1000

    st.divider()
    c_res1, c_res2, c_res3 = st.columns(3)
    c_res1.metric("Consumo del Día (m³)", f"{consumo_m3:,} m³")
    c_res2.metric("Consumo en Litros (DATO CLAVE)", f"{consumo_L:,} L")

    es_nocturno = hora.hour < 6 or hora.hour >= 22
    if consumo_m3 < 0:
        c_res3.error("❌ La lectura actual no puede ser menor a la anterior.")
    elif es_nocturno and consumo_m3 > 0:
        c_res3.warning("⚠️ Consumo nocturno detectado con planta detenida: posible fuga.")
    elif consumo_m3 > 45:
        c_res3.warning("⚠️ Consumo elevado detectado (> 45 m³). Revisar en Módulo 2.")
    else:
        c_res3.success("✅ Lectura dentro de rango normal.")

    if st.button("💾 Guardar Registro Diario (F-RDL-01)", type="primary"):
        if consumo_m3 < 0:
            st.error("Corrige la lectura actual antes de guardar.")
        else:
            df_lec = pd.read_csv(LECTURAS_FILE)
            nuevo_reg = pd.DataFrame([{
                "fecha": str(fecha),
                "hora": hora.strftime("%H:%M"),
                "operario": operario,
                "id_medidor": id_medidor,
                "sector": sector,
                "lect_ant": lect_ant,
                "lect_actual": lect_actual,
                "consumo_m3": consumo_m3,
                "consumo_L": consumo_L,
                "observaciones": observaciones if observaciones else "Sin observaciones"
            }])
            df_lec = pd.concat([nuevo_reg, df_lec], ignore_index=True)
            df_lec.to_csv(LECTURAS_FILE, index=False)
            st.success(f"✅ Registro guardado: {consumo_m3} m³ = {consumo_L:,} L en {id_medidor} ({sector}).")
            if foto_medidor:
                st.image(foto_medidor, caption=f"Evidencia fotográfica - {id_medidor}", width=250)

    st.divider()
    st.markdown("### 📋 Bitácora de Lecturas Diarias Recientes")
    st.dataframe(pd.read_csv(LECTURAS_FILE), use_container_width=True)


def modulo_alertas_prevencion():
    st.subheader("🚨 Módulo 2: Alertas de Fuga, Prevención y Reutilización (Formato 2 - F-RAF-02)")
    st.caption("💡 **Early detection saves costs** — Detectar fugas a tiempo reduce pérdidas de agua, evita daños en infraestructura y activa planes de captación de lluvia y reutilización.")

    tab_reporte, tab_acciones, tab_historial = st.tabs([
        "⚠️ Reportar Consumo Anómalo / Fuga",
        "🌧️ Captación de Lluvia y Reutilización",
        "📋 Historial de Incidencias"
    ])

    with tab_reporte:
        col1, col2 = st.columns(2)
        with col1:
            fecha_al = st.date_input("Fecha de alerta:", value=datetime.today(), key="f_al")
            hora_al = st.time_input("Hora de detección:", value=datetime.now().time(), key="h_al")
            medidor_al = st.selectbox("ID Medidor:", ["AC-M001", "AC-M002", "AC-M003", "AC-M004", "AC-M005", "AC-M006"], key="m_al")
            ubicacion_al = st.selectbox("Ubicación / Sector:", ["Sector Norte", "Sector Centro", "Sector Sur", "Sector Este", "Sector Oeste", "Sector Rural"], key="u_al")

        with col2:
            vol_reg = st.number_input("Volumen registrado hoy (m³):", min_value=0, value=850)
            vol_esp = st.number_input("Volumen esperado (m³):", min_value=0, value=800)
            dif_m3 = vol_reg - vol_esp
            dif_L = dif_m3 * 1000
            st.metric("Diferencia / Agua Perdida Detectada", f"{dif_m3:,} m³ ({dif_L:,} L)", delta="Consumo anómalo" if dif_m3 > 0 else "Normal", delta_color="inverse")

        st.markdown("#### 🔍 Checklist de Inspección Física")
        c_chk1, c_chk2 = st.columns(2)
        chk_tub = c_chk1.checkbox("Revisa tuberías: grietas / humedad / goteos")
        chk_val = c_chk1.checkbox("Inspecciona válvulas: cierres / juntas")
        chk_bom = c_chk2.checkbox("Evalúa bombas: ruido / vibración / presión")
        chk_tan = c_chk2.checkbox("Monitorea tanques: niveles / manchas")

        st.markdown("#### 📡 Señales Clave Detectadas")
        senales = st.multiselect(
            "Selecciona las señales observadas:",
            ["Consumo anómalo", "Consumo nocturno (planta detenida)", "Presión baja", "Humedad en paredes / suelo"],
            default=["Consumo anómalo"]
        )

        accion_tomada = st.text_area("Acción correctiva tomada:", placeholder="Describe el cierre de válvula, reparación de línea crítica o desvío a sistema de reuso...")
        estado_rep = st.radio("Estado del reporte:", ["Pendiente", "En proceso", "Resuelto"], horizontal=True)

        if st.button("🚨 Registrar Alerta de Fuga (F-RAF-02)", type="primary"):
            checks_activos = []
            if chk_tub: checks_activos.append("Tuberías")
            if chk_val: checks_activos.append("Válvulas")
            if chk_bom: checks_activos.append("Bombas")
            if chk_tan: checks_activos.append("Tanques")

            df_ale = pd.read_csv(ALERTAS_FILE)
            nueva_alerta = pd.DataFrame([{
                "fecha": str(fecha_al),
                "hora": hora_al.strftime("%H:%M"),
                "id_medidor": medidor_al,
                "ubicacion": ubicacion_al,
                "vol_registrado_m3": vol_reg,
                "vol_esperado_m3": vol_esp,
                "diferencia_m3": dif_m3,
                "diferencia_L": dif_L,
                "senal_tipo": ", ".join(senales) if senales else "No especificada",
                "checklist": ", ".join(checks_activos) if checks_activos else "Sin revisión",
                "accion_tomada": accion_tomada if accion_tomada else "Pendiente de intervención",
                "estado": estado_rep
            }])
            df_ale = pd.concat([nueva_alerta, df_ale], ignore_index=True)
            df_ale.to_csv(ALERTAS_FILE, index=False)
            st.success(f"✅ Alerta registrada para {medidor_al} ({ubicacion_al}). Pérdida reportada: {dif_L:,} L.")

    with tab_acciones:
        st.markdown("### 🌧️ Activación de Captación de Lluvia y Reutilización")
        st.write("Con los datos de pérdidas por sector, activa los sistemas de ahorro y reuso para reducir la extracción de pozos.")
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            st.toggle("🌧️ Activar Sistema de Captación Pluvial (Presupuesto: $500,000 MXN)", value=True)
            st.toggle("♻️ Activar Circuito de Reutilización para Riego y No Potable (80,000 L/día)", value=True)
            st.toggle("🔧 Priorizar Reemplazo de Líneas Críticas en Sector Este", value=True)
        with col_a2:
            st.info("**Distribución Presupuesto Ambiental ($5M de $96M MXN - 5.2%):**\n"
                    "- Medición y monitoreo: $1.2M – $1.8M\n"
                    "- Reemplazo de líneas críticas: $800,000\n"
                    "- Reutilización de agua: $600,000\n"
                    "- Captación de lluvia: $500,000\n"
                    "- Detección de fugas: $300,000\n"
                    "- Capacitación anual (3 niveles): $150,000")

    with tab_historial:
        st.markdown("### 📋 Seguimiento de Alertas e Incidencias")
        st.data_editor(pd.read_csv(ALERTAS_FILE), use_container_width=True, num_rows="dynamic")


def modulo_mapa_sectores():
    st.subheader("🗺️ Mapa de Pozos, Medidores y Pérdidas por Sector")
    st.write("Ubicación en tiempo real de los medidores (`AC-M001` a `AC-M006`) para identificar dónde se pierde el agua.")

    # OpenStreetMap does not require a Carto API key; CSS filter keeps the dark aesthetic
    st.markdown("""
    <style>
        .leaflet-tile-pane {
            filter: invert(92%) hue-rotate(180deg) brightness(92%) contrast(95%);
        }
    </style>
    """, unsafe_allow_html=True)

    m = folium.Map(location=[32.5149, -117.0382], zoom_start=12, tiles="OpenStreetMap")
    sectores = [
        {"id": "AC-M001 - Sector Norte", "coord": [32.5320, -117.0250], "estado": "Normal (50,000 L/día)", "color": "blue"},
        {"id": "AC-M002 - Sector Centro", "coord": [32.5180, -117.0380], "estado": "Normal (45,000 L/día)", "color": "blue"},
        {"id": "AC-M003 - Sector Sur", "coord": [32.4950, -117.0350], "estado": "Equilibrado", "color": "green"},
        {"id": "AC-M004 - Sector Este", "coord": [32.5120, -116.9950], "estado": "⚠️ ALERTA FUGA: 55,000 L perdidos", "color": "red"},
        {"id": "AC-M005 - Sector Oeste", "coord": [32.5150, -117.0750], "estado": "Reutilización Activa", "color": "cadetblue"},
        {"id": "AC-M006 - Sector Rural", "coord": [32.4850, -116.9800], "estado": "Captación Pluvial Activa", "color": "green"},
    ]
    for s in sectores:
        folium.Marker(
            s["coord"],
            popup=f"<b>{s['id']}</b><br>{s['estado']}",
            tooltip=s["id"],
            icon=folium.Icon(color=s["color"], icon="tint")
        ).add_to(m)

    st_folium(m, width=1000, height=480)


def modulo_reportes_iso():
    st.subheader("📄 Módulo 4: Reportes Mensuales y Auditoría ISO 14001 / NOM")
    st.write("Evidencia documentada para cumplimiento normativo (**ISO 14001 Cláusulas 8, 9 y 10** y **NOMs aplicables**).")

    df_bal = pd.read_csv(BALANCE_FILE)
    total_ext_m3 = df_bal["Vol Extraído m3"].sum()
    total_con_m3 = df_bal["Vol Consumido m3"].sum()
    total_reu_m3 = df_bal["Vol Reutilizado m3"].sum()
    total_per_m3 = df_bal["Pérdida m3"].sum()
    pct_perdida = (total_per_m3 / total_ext_m3 * 100) if total_ext_m3 > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Volumen Total Extraído", f"{total_ext_m3 * 1000:,.0f} L", f"{total_ext_m3:,} m³")
    col2.metric("Pérdida Acumulada", f"{pct_perdida:.2f}%", f"{total_per_m3 * 1000:,.0f} L perdidos", delta_color="inverse")
    col3.metric("Ahorro Estimado en Costos", "-20% costos operativos", "Meta 3 años: -30%")

    st.divider()
    st.markdown("### ✅ Cumplimiento ISO 14001 y Normatividad")
    iso_data = pd.DataFrame([
        {"Cláusula / Norma": "ISO 14001 - Cláusula 8 (Operación)", "Evidencia en AquaControl": "Bitácora diaria F-RDL-01 con foto de medidor y control de lecturas negras", "Estado": "🟢 Cumple"},
        {"Cláusula / Norma": "ISO 14001 - Cláusula 9 (Evaluación)", "Evidencia en AquaControl": "Tablero de 6 KPIs, Balance Hídrico y Concentrado F-CMK-03", "Estado": "🟢 Cumple"},
        {"Cláusula / Norma": "ISO 14001 - Cláusula 10 (Mejora)", "Evidencia en AquaControl": "Alertas tempranas F-RAF-02, detección nocturna y plan de reducción 30%", "Estado": "🟢 En progreso"},
        {"Cláusula / Norma": "NOM-001 / NOM-002 SEMARNAT", "Evidencia en AquaControl": "Registro de volúmenes reutilizados (80,000 L/día) y control de descargas", "Estado": "🟢 Cumple"},
    ])
    st.dataframe(iso_data, use_container_width=True)

    reporte_txt = f"""REPORTE DE AUDITORÍA AMBIENTAL Y BALANCE HÍDRICO - AQUACONTROL
Empresa: Agua del Valle S.A. de C.V.
Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M')}

1. RESUMEN DE VOLÚMENES:
- Volumen Extraído: {total_ext_m3:,} m³ ({total_ext_m3 * 1000:,.0f} L)
- Volumen Consumido: {total_con_m3:,} m³ ({total_con_m3 * 1000:,.0f} L)
- Volumen Reutilizado: {total_reu_m3:,} m³ ({total_reu_m3 * 1000:,.0f} L)
- Volumen Perdido: {total_per_m3:,} m³ ({total_per_m3 * 1000:,.0f} L) -> {pct_perdida:.2f}%

2. METAS ESTRATÉGICAS (3 AÑOS):
- Reducir 30% extracción de agua: de 1,200,000 L/día a 840,000 L/día.
- Reducir 30% pérdida de agua: de 240,000 L/día a 168,000 L/día.
- Ahorro esperado al bajar pérdidas al 10%: 120,000 L/día (43.8 millones L/año).

3. EVIDENCIA NORMATIVA:
- Cumplimiento activo con ISO 14001 (Cláusulas 8, 9 y 10) y NOMs aplicables.
"""
    st.download_button(
        label="📥 Descargar Reporte Oficial ISO 14001 / Balance Hídrico (.txt)",
        data=reporte_txt,
        file_name=f"Reporte_AquaControl_ISO14001_{datetime.today().strftime('%Y%m%d')}.txt",
        mime="text/plain"
    )


def modulo_capacitacion_config():
    st.subheader("🎓 Capacitación (3 Niveles) y Configuración")
    st.markdown("### 📚 Programa de Capacitación del Personal (250 trabajadores | $150,000 MXN/año)")
    cap_df = pd.DataFrame([
        {"Nivel": "Nivel 1 - Todos los trabajadores", "Personal": "250 personas", "Duración": "2 horas", "Temario": "Qué es 1 m³ (1,000 L), reporte de fugas visibles e infografía en pozos"},
        {"Nivel": "Nivel 2 - Operadores y mantenimiento", "Personal": "30 personas", "Duración": "4 horas", "Temario": "Lectura de números negros, cálculo m³ a L, foto comprobación y Formato 1"},
        {"Nivel": "Nivel 3 - Área Ambiental", "Personal": "8 personas", "Duración": "8 horas", "Temario": "Uso de AquaControl, 6 KPIs, Balance Hídrico, alertas y reportes ISO 14001"},
    ])
    st.table(cap_df)

    st.divider()
    st.markdown("### ⚙️ Parámetros del Sistema")
    st.text_input("Empresa:", value="Agua del Valle S.A. de C.V.", disabled=True)
    st.number_input("Meta de Extracción a 3 años (L/día):", value=840000, disabled=True)
    st.number_input("Meta de Pérdida Máxima a 3 años (L/día):", value=168000, disabled=True)
    st.toggle("Alertar automáticamente consumo nocturno (22:00 - 06:00)", value=True)
    if st.button("Guardar Preferencias"):
        st.success("✅ Configuración actualizada.")


# --- 1. SISTEMA DE LOGIN Y REGISTRO ---
authenticator = stauth.Authenticate(credentials, "aquacontrol_dashboard", "aqua_auth_cookie", cookie_expiry_days=30)
authentication_status = st.session_state.get("authentication_status")

if authentication_status is None or authentication_status is False:
    st.write("")
    st.write("")
    col_izq, col_der = st.columns([1.5, 1], gap="large")

    with col_izq:
        st.write("")
        _, centro_logo, _ = st.columns([1, 1.5, 1])
        with centro_logo:
            if os.path.exists(LOGO_FILENAME):
                st.image(LOGO_FILENAME, use_container_width=True)
            else:
                st.markdown("<div style='text-align:center; font-size: 72px;'>💧</div>", unsafe_allow_html=True)

        st.markdown("<h1 style='text-align: center; color: #FFFFFF;'>AquaControl</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #00A8E8;'>Agua del Valle S.A. de C.V.</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8B949E;'>Monitoreo Inteligente del Agua<br>Meta: -30% Extracción y Pérdida de Agua | ISO 14001</p>", unsafe_allow_html=True)

    with col_der:
        st.markdown("### Acceso al Sistema")
        tab_login, tab_registro = st.tabs(["🔐 Ingresar", "📝 Registrarse"])

        with tab_login:
            authenticator.login(location="main")
            if authentication_status is False:
                st.error("Usuario o contraseña incorrectos")
            elif authentication_status is None:
                st.info("Usuarios demo: `admin` (123) | `operador1` (456) | `ambiental1` (789)")

        with tab_registro:
            with st.form("registro_form"):
                nuevo_nombre = st.text_input("Nombre Completo:")
                nuevo_usuario = st.text_input("Usuario:")
                nueva_password = st.text_input("Contraseña:", type="password")
                nuevo_rol = st.selectbox("Rol:", ["Operador", "Área Ambiental", "Administrador"])
                btn_registro = st.form_submit_button("Crear Cuenta")

                if btn_registro:
                    if not nuevo_nombre or not nuevo_usuario or not nueva_password:
                        st.error("Llena todos los campos.")
                    elif nuevo_usuario in credentials["usernames"]:
                        st.error("Usuario ya en uso.")
                    else:
                        try:
                            hashed_pw = stauth.Hasher.hash(nueva_password)
                        except AttributeError:
                            hashed_pw = stauth.Hasher([nueva_password]).generate()[0]
                        credentials["usernames"][nuevo_usuario] = {
                            "name": nuevo_nombre,
                            "password": hashed_pw,
                            "email": "",
                            "role": nuevo_rol
                        }
                        with open(USERS_FILE, "w", encoding="utf-8") as f:
                            json.dump(credentials, f, indent=4)
                        st.success(f"¡Cuenta creada para {nuevo_nombre}!")

elif authentication_status:
    name = st.session_state.get("name")
    username = st.session_state.get("username")
    user_role = credentials["usernames"][username].get("role", "Operador")

    with st.sidebar:
        if os.path.exists(LOGO_FILENAME):
            st.image(LOGO_FILENAME, use_container_width=True)
        else:
            st.markdown("## 💧 AquaControl")
        st.write(f"Bienvenido, **{name}**")
        st.write(f"Rol: **{user_role}**")
        st.divider()

        opciones_menu = ["📊 Dashboard y 6 KPIs", "📱 Captura Diaria (F-1)", "🚨 Alertas y Prevención (F-2)", "🗺️ Mapa de Sectores"]
        if user_role in ["Área Ambiental", "Administrador"]:
            opciones_menu.extend(["📄 Reportes ISO 14001", "🎓 Capacitación y Config."])

        opcion = st.radio("Módulos:", opciones_menu, label_visibility="collapsed")
        st.divider()
        authenticator.logout("Cerrar Sesión", location="sidebar")

    st.title("💧 AquaControl — Monitoreo Inteligente del Agua")
    st.caption(f"Agua del Valle S.A. de C.V. | Sesión activa: {name} ({user_role})")
    st.divider()

    if opcion == "📊 Dashboard y 6 KPIs":
        modulo_dashboard()
    elif opcion == "📱 Captura Diaria (F-1)":
        modulo_captura(name)
    elif opcion == "🚨 Alertas y Prevención (F-2)":
        modulo_alertas_prevencion()
    elif opcion == "🗺️ Mapa de Sectores":
        modulo_mapa_sectores()
    elif opcion == "📄 Reportes ISO 14001":
        modulo_reportes_iso()
    elif opcion == "🎓 Capacitación y Config.":
        modulo_capacitacion_config()


