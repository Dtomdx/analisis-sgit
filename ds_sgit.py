import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

DATA_URL = r'Z:\8_COMPARTIDO\DIEGO\Script\Analisis sgit\sgit_catastro.csv'

def load_data():
    try:
        data = pd.read_csv(
            DATA_URL,
            encoding='ISO-8859-1',
            sep=';',
            engine='python',
            quoting=3
        )
        return data
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return pd.DataFrame()

# Page configuration
st.set_page_config(
    page_title="Dashboard Sgit Catastro",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS MÍNIMO solo para eliminar espacios
st.markdown("""
<style>
    .main .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }
</style>
""", unsafe_allow_html=True)

# Cargar datos
df = load_data()
if df.empty:
    st.error("No se pudieron cargar los datos")
    st.stop()

# Procesamiento de datos
df['fecha_informe'] = df['fecha_informe'].apply(
    lambda x: pd.to_datetime(str(x).strip(), dayfirst=True, errors='coerce') 
    if '.' not in str(x) or not str(x).replace('.', '').isdigit() 
    else pd.to_datetime(f"01/01/{int(float(x))}", dayfirst=True, errors='coerce')
)

df['fec_ingreso_catastro'] = df['fec_ingreso_catastro'].apply(
    lambda x: pd.to_datetime(str(x).strip(), dayfirst=True, errors='coerce') 
    if '.' not in str(x) or not str(x).replace('.', '').isdigit() 
    else pd.to_datetime(f"01/01/{int(float(x))}", dayfirst=True, errors='coerce')
)



df['fecha_informe_mes'] = df['fecha_informe'].dt.month
df['mes_ingreso'] = df['fec_ingreso_catastro'].dt.month
df = df.sort_values('fecha_informe')

# Definir funciones de gráficos
def make_time_line(data, selected_year):
    fig = px.line(
        data, 
        x='mes_ingreso', 
        y='cantidad_expedientes',
        color='tipo_expediente',
        title=f"📈 Expedientes ingresados por Mes - Año {selected_year}",
        markers=True
    )
    fig.update_layout(
        xaxis_title="Mes",
        yaxis_title="Cantidad de Expedientes",
        yaxis_type="log",
        xaxis=dict(tickmode='linear', dtick=1, range=[0.5, 12.5]),
        height=300
    )
    return fig

def make_boxplot_dias_cat(data, selected_year):
    fig = px.box(
        data,
        x='fecha_informe_mes',
        y='dias_cat',
        color='tipo_expediente',
        title=f"📦 Días de Atención por Mes - Año {selected_year}",
        #points="all"
    )
    fig.update_layout(
        xaxis_title="Mes",
        yaxis_title="Días de Atención",
        xaxis=dict(tickmode='linear', dtick=1, range=[0.5, 12.5]),
        height=300
    )
    return fig

def make_piechart_entidad(data):
    fig = px.pie(
        data,
        names='entidad',
        values='cantidad_expedientes',
        title="🥧 Expedientes ingresados por Entidad",
        hole=0.4,
        labels={'entidad': ''},

        
    )
    # Personalizar el texto interior
    fig.update_traces(
        textposition='inside',           # Texto dentro de las porciones
        textinfo='percent+label',        # Muestra porcentaje + etiqueta
        insidetextorientation='horizontal',  # Texto horizontal
        textfont_size=12,
        textfont_color='white',
        marker=dict(line=dict(color='white', width=2))
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,  # Oculta la leyenda externa
        uniformtext_minsize=10,
        uniformtext_mode='hide'
    )
    return fig

def make_time_line_dias_cat_prom(data, selected_year):
    fig = px.line(
        data, 
        x='fecha_informe_mes', 
        y='promedio_dias',
        color='tipo_expediente',
        title=f"📈 Promedio de dias de atencion por Mes - Año {selected_year}",
        markers=True
    )
    fig.update_layout(
        xaxis_title="Mes",
        yaxis_title="Dias en Catastro",
        #yaxis_type="log",
        xaxis=dict(tickmode='linear', dtick=1, range=[0.5, 12.5]),
        height=300
    )
    return fig


# HEADER - Fila 1
header_col1, header_col2, header_col3 = st.columns([2, 3, 1])

with header_col1:
    st.markdown("## 🏢 Dashboard Catastro")

with header_col2:
    years_unique = df['fecha_informe'].dt.year.unique()
    years_list = list(map(str, years_unique))
    selected_year = st.selectbox(
        '**Seleccionar Año:**', 
        years_list, 
        key="year_selector"
    )

with header_col3:
    st.markdown(f"### **{selected_year}**")

# Aplicar filtro de año
df_selected_year = df[df['fecha_informe'].dt.year == int(selected_year)]

# Preparar datos
datos_grafico = df_selected_year.groupby(['mes_ingreso', 'tipo_expediente'])['nro_expe'].count().reset_index()
datos_grafico.columns = ['mes_ingreso', 'tipo_expediente', 'cantidad_expedientes']

datos_grafico_dias_cat = df_selected_year.groupby(['fecha_informe_mes', 'tipo_expediente', 'dias_cat']).size().reset_index()
datos_grafico_dias_cat.columns = ['fecha_informe_mes', 'tipo_expediente', 'dias_cat', 'cantidad']

datos_grafico_dias_cat_prom = df_selected_year[
    df_selected_year['tipo_expediente'].isin(['TITULO', 'PUBLICIDAD'])
].groupby(['fecha_informe_mes', 'tipo_expediente']).agg({
    'dias_cat': 'mean'  # ← PROMEDIO de días
}).reset_index()
datos_grafico_dias_cat_prom.columns = ['fecha_informe_mes', 'tipo_expediente', 'promedio_dias']


datos_grafico_tipos_expedientes = df_selected_year.groupby(['entidad'])['nro_expe'].count().reset_index()
datos_grafico_tipos_expedientes.columns = ['entidad','cantidad_expedientes']







# CUERPO PRINCIPAL - Fila 2
col_left, col_center, col_right = st.columns([1.2, 1.8, 1.8])

# COLUMNA IZQUIERDA - Métricas
with col_left:
    # Calcular métricas
    total_expedientes = df_selected_year.shape[0]
    tipos_unicos = df_selected_year['tipo_expediente'].nunique()
    #entidades_unicas = df_selected_year['entidad'].nunique()
    promedio_dias = df_selected_year['dias_cat'].mean() if 'dias_cat' in df_selected_year.columns else 0
    promedio_dias_at_titulos = df_selected_year.groupby('tipo_expediente')['dias_cat'].mean().reset_index()
    
    st.markdown("### 📊 Métricas")
    
    # Métricas en tarjetas simples
    st.metric("Total Expedientes", total_expedientes)
    st.metric("Tipos de Expediente", tipos_unicos)
    #st.metric("Entidades", entidades_unicas)
    st.metric("Promedio Días", f"{promedio_dias:.1f}")
    
    st.markdown("---")
    
    with st.expander("ℹ️ Información"):
        st.write('''
        **Dataset**: Sistema de Gestión Catastral
        - **Fuente**: SGIT Catastro
        - **Contenido**: Expedientes y trámites
        - **Actualización**: Mensual
        ''')

    
    
# COLUMNA CENTRAL - Gráficos principales
with col_center:
    # Gráfico de líneas
    st.plotly_chart(make_time_line(datos_grafico, selected_year), use_container_width=True)
    
    # Boxplot
    st.plotly_chart(make_boxplot_dias_cat(datos_grafico_dias_cat, selected_year), use_container_width=True)

    # Grafico de lineas
    st.plotly_chart(make_time_line_dias_cat_prom(datos_grafico_dias_cat_prom, selected_year), use_container_width=True)
# COLUMNA DERECHA - Pie chart
with col_right:
    # Pie chart
    st.plotly_chart(make_piechart_entidad(datos_grafico_tipos_expedientes), use_container_width=True)
    
    # Distribución por tipo
    with st.expander("📋 Distribución por Tipo"):
        tipo_distribution = df_selected_year['tipo_expediente'].value_counts()
        for tipo, count in tipo_distribution.items():
            st.write(f"**{tipo}**: {count}")
    #tablaproduccion semanal por profesional
    # Agregar selector de mes
    meses = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }

    selected_month = st.selectbox(
        "Selecciona el mes:",
        options=list(meses.keys()),
        format_func=lambda x: meses[x],
        key="month_selector"
    )
    #produccion por mes de profesional 
    df_selected_month = df_selected_year[df_selected_year['fecha_informe'].dt.month == selected_month]
    # Agrupar por profesional para el mes seleccionado
    datos_grafico_prodTotal_sem_prof = df_selected_month.groupby(['profesional_asignado'])['nro_expe'].count().reset_index()
    datos_grafico_prodTotal_sem_prof.columns = ['profesional_asignado', 'produccion_total']
    
    st.markdown(f"### 📈 Producción {meses[selected_month]} {selected_year}")
    
    if not datos_grafico_prodTotal_sem_prof.empty:
        datos_grafico_prodTotal_sem_prof = datos_grafico_prodTotal_sem_prof.sort_values('produccion_total', ascending=False)
        
        # Controlar ancho
        left_space, table_col, right_space = st.columns([0.1, 3, 0.1])
        
        with table_col:
            st.dataframe(
                datos_grafico_prodTotal_sem_prof, 
                use_container_width=True,
                height=250,
                hide_index=True
            )
    else:
        st.info(f"📊 No hay producción para {meses[selected_month]}")
