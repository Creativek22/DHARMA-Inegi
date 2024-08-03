import sys
import os
import base64
import streamlit as st
import pandas as pd

# Añadir el directorio `scripts` al path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)

from data_processing import load_data, filter_data, summarize_data

# Configurar el tema de Streamlit
st.set_page_config(page_title="Directorio empresas en INEGI", layout="centered", initial_sidebar_state="collapsed")

# Mostrar el logo de la empresa centrado y con el tamaño original
logo_path = os.path.join(parent_dir, 'logo', 'logo.webp')
logo_bytes = open(logo_path, "rb").read()
logo_base64 = base64.b64encode(logo_bytes).decode("utf-8")

st.markdown(f"""
    <div style="display: flex; justify-content: center; align-items: center;">
        <img src="data:image/webp;base64,{logo_base64}">
    </div>
""", unsafe_allow_html=True)

# Título de la aplicación
st.title('Directorio empresas en INEGI')

# Cargar los datos
data_path = os.path.join(parent_dir, 'data/inegi.json')
df = load_data(data_path)

# Mostrar el DataFrame completo
st.subheader('Datos Completos')
st.write(df)

# Crear columnas para distribuir los filtros
col1, col2 = st.columns(2)

# Búsqueda por nombre de la unidad económica
search_term = st.text_input('Buscar por nombre de la unidad económica:')
if search_term:
    df = df[df['Nombre de la Unidad Económica'].str.contains(search_term, case=False, na=False)]

# Búsqueda por razón social
search_razon_social = st.text_input('Buscar por razón social:')
if search_razon_social:
    df = df[df['Razón social'].str.contains(search_razon_social, case=False, na=False)]

# Filtros en la primera columna
with col1:
    # Filtro por código de actividad
    if 'Código de la clase de actividad SCIAN' in df.columns:
        codigo_actividad_options = [''] + df['Código de la clase de actividad SCIAN'].unique().tolist()
        codigo_actividad = st.selectbox('Selecciona el código de actividad:', codigo_actividad_options)
        if codigo_actividad:
            df = filter_data(df, 'Código de la clase de actividad SCIAN', codigo_actividad)

    # Filtro por municipio
    if 'Municipio' in df.columns:
        municipio_options = [''] + df['Municipio'].unique().tolist()
        municipio = st.selectbox('Selecciona el municipio:', municipio_options)
        if municipio:
            df = filter_data(df, 'Municipio', municipio)

# Filtros en la segunda columna
with col2:
    # Filtro por descripción del estrato personal ocupado
    if 'Descripcion estrato personal ocupado' in df.columns:
        estrato_personal_order = [
            '0 a 5 personas', '6 a 10 personas', '11 a 30 personas',
            '31 a 50 personas', '51 a 100 personas', '101 a 250 personas',
            '251 y más personas'
        ]
        estrato_personal_options = [opt for opt in estrato_personal_order if opt in df['Descripcion estrato personal ocupado'].unique()]
        estrato_personal = st.selectbox('Selecciona el estrato de personal ocupado:', [''] + estrato_personal_options)
        if estrato_personal:
            df = filter_data(df, 'Descripcion estrato personal ocupado', estrato_personal)

    # Filtro por fecha de incorporación al DENUE
    if 'Fecha de incorporación al DENUE' in df.columns:
        df['Año de incorporación'] = pd.to_datetime(df['Fecha de incorporación al DENUE']).dt.year
        fecha_incorporacion_options = sorted(df['Año de incorporación'].unique().tolist(), reverse=True)
        fecha_incorporacion = st.selectbox('Selecciona el año de incorporación al DENUE:', [''] + [str(year) for year in fecha_incorporacion_options])
        if fecha_incorporacion:
            df = filter_data(df, 'Año de incorporación', int(fecha_incorporacion))

# Botón para realizar la búsqueda
if st.button('Realizar búsqueda'):
    # Mostrar los datos filtrados
    st.subheader('Datos Filtrados')
    st.write(df)

    # Botón para descargar datos filtrados como CSV
    csv = df.to_csv(index=False)
    st.download_button(
        label="Descargar datos filtrados como CSV",
        data=csv,
        file_name='datos_filtrados.csv',
        mime='text/csv'
    )

    # Mostrar las empresas en forma de lista con enlace clickable a Google Maps y sitios web
    st.subheader('Empresas')
    col1, col2 = st.columns(2)
    for idx, row in df.iterrows():
        empresa = row['Nombre de la Unidad Económica']
        correo = row['Correo electrónico'].lower() if pd.notnull(row['Correo electrónico']) else 'N/A'
        correo_clickable = f'<a href="mailto:{correo}">{correo}</a>' if correo != 'N/A' else 'N/A'
        lat = row['Latitud']
        lon = row['Longitud']
        sitio_web = row['Sitio en Internet'] if pd.notnull(row['Sitio en Internet']) else None
        if sitio_web and not sitio_web.startswith('http'):
            sitio_web = 'http://' + sitio_web
        google_maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"

        empresa_info = f"""
        <div style="border:1px solid #ddd; border-radius:10px; padding:10px; margin:10px 0; height:150px; display:flex; flex-direction:column; justify-content:space-between;">
            <div>
                <strong>{empresa}</strong><br>
                <em>Correo:</em> {correo_clickable}<br>
            </div>
            <div style="margin-top:auto;">
                <a href="{google_maps_url}" target="_blank" style="display: inline-block; padding: 5px 10px; color: #007bff; text-decoration: none;">Ver en Maps</a>
                {f'<a href="{sitio_web}" target="_blank" style="display: inline-block; padding: 5px 10px; color: #28a745; text-decoration: none;">Ver sitio web</a>' if sitio_web else '<span style="visibility:hidden;">Ver sitio web</span>'}
            </div>
        </div>
        """

        if idx % 2 == 0:
            col1.markdown(empresa_info, unsafe_allow_html=True)
        else:
            col2.markdown(empresa_info, unsafe_allow_html=True)
