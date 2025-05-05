import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Contable Dinámico",
    layout="wide",
)

# Estilos CSS personalizados
st.markdown(
    """
    <style>
        .stMetric {
            font-size: 18px;
        }
        /* Ajuste de margenes de gráfico */
        .js-plotly-plot .main-svg {
            margin: 0px !important;
        }
    </style>
    """, unsafe_allow_html=True
)

# Título
st.title("📊 Dashboard Contable Dinámico y Responsive")

# Cargar archivo Excel desde interfaz
uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"], help="Selecciona un archivo .xlsx con tus datos contables.")

if uploaded_file:
    # Cargar datos
    df = pd.read_excel(uploaded_file)

    # Procesamiento de datos
    # Crear columna de tipo de comprobante desde prefijo de NUMERO CBTE
    df["TIPO CBTE"] = df["NUMERO CBTE"].astype(str).str[:2]
    # Convertir FECHA a datetime y extraer MES y AÑO
    df["FECHA"] = pd.to_datetime(df["FECHA"])
    df["MES"] = df["FECHA"].dt.strftime("%B")
    df["AÑO"] = df["FECHA"].dt.year

    # Mostrar datos originales en expander
    with st.expander("📄 Ver datos originales"):
        st.dataframe(df)

    # Barra lateral de filtros
    st.sidebar.header("Filtros")
    with st.sidebar.expander("Configurar filtros"):
        tipo_cbte = st.multiselect("Tipo de Comprobante", df["TIPO CBTE"].unique())
        usuario = st.multiselect("Usuario", df["USUARIO"].unique())
        partida = st.multiselect("Partida Presupuestaria", df["PARTIDA"].unique())
        cuenta = st.multiselect("Cuenta Contable", df["CUENTA"].unique())
        centro_costo = st.multiselect("Centro de Costo", df["CENTRO COSTO"].unique())
        año = st.multiselect("Año", df["AÑO"].unique())

    # Aplicar filtros al DataFrame
    df_filtrado = df.copy()
    if tipo_cbte:
        df_filtrado = df_filtrado[df_filtrado["TIPO CBTE"].isin(tipo_cbte)]
    if usuario:
        df_filtrado = df_filtrado[df_filtrado["USUARIO"].isin(usuario)]
    if partida:
        df_filtrado = df_filtrado[df_filtrado["PARTIDA"].isin(partida)]
    if cuenta:
        df_filtrado = df_filtrado[df_filtrado["CUENTA"].isin(cuenta)]
    if centro_costo:
        df_filtrado = df_filtrado[df_filtrado["CENTRO COSTO"].isin(centro_costo)]
    if año:
        df_filtrado = df_filtrado[df_filtrado["AÑO"].isin(año)]

    # Cálculo de KPIs
    ingresos = df_filtrado[df_filtrado["IMPORTE"] > 0]["IMPORTE"].sum()
    egresos = df_filtrado[df_filtrado["IMPORTE"] < 0]["IMPORTE"].sum()
    saldo = ingresos + egresos
    promedio_mensual = df_filtrado.groupby("MES")["IMPORTE"].sum().mean()

    # Mostrar KPIs en dos columnas por fila para mejor responsividad
    st.subheader("🔢 KPIs")
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col1.metric("🟢 Ingresos (Bs)", f"{ingresos:,.2f}")
    col2.metric("🔴 Egresos (Bs)", f"{egresos:,.2f}")
    col3.metric("⚖️ Saldo (Bs)", f"{saldo:,.2f}")
    col4.metric("📅 Promedio Mensual (Bs)", f"{promedio_mensual:,.2f}")

    # Selección de tipo de gráfico
    st.sidebar.header("Gráficos")
    chart_type = st.sidebar.selectbox(
        "Selecciona el tipo de gráfico", ["Barras", "Líneas", "Área"], index=0
    )

    # Gráfico de movimiento mensual
    st.subheader("📈 Movimiento Mensual")
    if chart_type == "Barras":
        fig = px.bar(
            df_filtrado, x="MES", y="IMPORTE", color="TIPO CBTE", title="Ingresos y Egresos por Mes"
        )
    elif chart_type == "Líneas":
        fig = px.line(
            df_filtrado, x="MES", y="IMPORTE", color="TIPO CBTE", title="Ingresos y Egresos por Mes"
        )
    else:
        fig = px.area(
            df_filtrado, x="MES", y="IMPORTE", color="TIPO CBTE", title="Ingresos y Egresos por Mes"
        )
    st.plotly_chart(fig, use_container_width=True)

    # Tabla de datos filtrados en expander
    with st.expander("📋 Detalle de Transacciones Filtradas"):
        st.dataframe(df_filtrado)

else:
    st.info("Por favor, sube un archivo Excel para comenzar.")