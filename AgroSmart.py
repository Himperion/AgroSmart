# -*- coding: utf-8 -*-
import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import folium, yaml, gcsfs
import fun

from streamlit_folium import st_folium
from shapely.geometry import Point

def style_function(color):
    return lambda x: {
        'fillColor': color,
        'color': color,
        'weight': 1,
        'fillOpacity': 0.5
    }

with open('dicts/dict_aptitude.yaml', 'r') as archivo:
    dict_aptitude = yaml.safe_load(archivo)

with open('dicts/dict_dptoNameCode.yaml', 'r') as archivo:
    dict_dptoNameCode = yaml.safe_load(archivo)

if 'management' not in st.session_state:
    st.session_state['management'] = 1

if st.session_state['management'] == 0:
    flag_gcs = False
    BUCKET_NAME = None
    fs = None
elif st.session_state['management'] == 1:
    flag_gcs = True
    GCS_TOKEN = dict(st.secrets.GCS_TOKEN)
    PROJECT_ID = GCS_TOKEN['project_id']
    BUCKET_NAME = st.secrets.GCS_INFO['bucket_name']
    fs = gcsfs.GCSFileSystem(project=PROJECT_ID, token=GCS_TOKEN)

dict_aptitudeLabel, dict_aptitudeColor, dict_aptitudeEmojin = fun.get_dicts_aptitude(dict_aptitude)
list_markdownLabelAptitude = fun.get_list_markdownLabelAptitude(dict_aptitude)
dict_product, list_nameProduct, list_nameDatasets, list_emojiProduct = fun.get_datasets_names()
list_dpto = fun.get_list_dpto(dict_dptoNameCode)
dict_aptitudLabelReversed = fun.get_dict_aptitudLabelReversed(dict_aptitudeLabel)
dict_dptoCodeName = {value: key for key, value in dict_dptoNameCode.items()}

selectCoordinateOptions = ["Sistema sexagesimal GMS", "Sistema decimal GD"]
    
def pageHome():

    tab1, tab2 = st.tabs(["Descripción", "Equipo humano"])

    with tab1:

        description = """
        Herramienta para la visualización del potencial agropecuario
        de los territorios, permitiendo análizar el rendimiento
        a nivel departamental o municipal según el tipo de cultivo o
        producción. \n
        Se cuenta con **7'333.610** datos en **33 conjuntos** de la **Unidad de Planificación Agropecuaria - UPRA**
        donde mide la aptitud agropecuaria del territorio nacional. También se usan datos abiertos del **geoportal DANE**
        para la división política de los departamentos, municipios y sus respectivas áreas territoriales.
        """

        st.markdown(description)

    with tab2:

        with st.container(border=True):
            col1, col2 = st.columns([0.3, 0.7], vertical_alignment="center")

            with col1:
                st.image("img/member2.jpg", width=200)

            with col2:
                st.subheader("Darío Fernando Gonzalez Fontecha", divider=True)
                st.caption("Comprometido con el desarrollo sostenible, energias renovables y la implementación de tecnologías innovadoras para el sector agropecuario. Con conocimientos en MATLAB, Python y desarrollo Web, oriento mis habilidades hacia el uso de Big Data y computación en la nube para transformar el campo colombiano.")
                st.markdown("📧 dario.gonzalez@correo.uis.edu.co")

        with st.container(border=True):
            col1, col2 = st.columns([0.3, 0.7], vertical_alignment="center")

            with col1:
                st.image("img/member1.jpg", width=200)

            with col2:
                st.subheader("José Camilo Rojas Páez", divider=True)
                st.caption("Mi compromiso hacia la sostenibilidad se traduce en proyectos de energías renovables destinados a mejorar el sector agropecuario. Con conocimientos en  MATLAB, Python, Streamlit y Power BI, que aplico al análisis y procesamiento de datos. ")
                
                st.markdown("📧 jose.rojas9@correo.uis.edu.co")
                st.markdown("🐈‍⬛ https://github.com/Himperion")
        

    

    return

def pageMpio():
    options_products, options_dpto = None, None

    st.subheader('Análisis de aptitud municipal', divider='green')

    with st.container(border=True):
        options_products = st.selectbox(label='**Aptitud agropecuaria:**', options=list_emojiProduct, index=18)
        options_dpto = st.selectbox(label='**Departamento:**', options=list_dpto, index=26)

    if options_products is not None and options_dpto is not None:
        with st.form('form_1'):

            nameDataset, nameProduct = fun.from_emojiProduct_to_nameDataset(options_products, list_emojiProduct, list_nameDatasets, list_nameProduct)
            dpto_code = dict_dptoNameCode[options_dpto]
            gdf_openDataDpto = fun.get_gdf_openDataDpto(flag_gcs, fs, BUCKET_NAME, nameDataset, options_dpto)
            dict_Mpio_MpioCode = fun.get_dict_Mpio_MpioCode(gdf_openDataDpto)

            options_mpio = st.selectbox(label='**Municipio:**', options=[key for key in dict_Mpio_MpioCode], index=None,
                                        placeholder='Seleccione una opción')
            
            submitted = st.form_submit_button('**Aceptar**')
    
            if submitted and options_products is not None and options_dpto is not None and options_mpio is not None:
                mpio_code = dict_Mpio_MpioCode[options_mpio]
                
                gdf_openDataMpio = fun.get_gdf_openDataMpio(gdf_openDataDpto, mpio_code)
                gdf_DaneMpio = fun.get_gdf_DaneMpio(flag_gcs, fs, BUCKET_NAME, dpto_code, mpio_code)
                df_areaOpenDataMpio = fun.get_df_areaOpenDataDpto(gdf_openDataMpio, gdf_DaneMpio, 'MPIO_AREA', dict_aptitudeLabel, dict_aptitudeColor)

                centroid_mpio = [round(x, 3) for x in gdf_DaneMpio["CENTROID"].iloc[0].coords[0]]

                m = folium.Map(location=[centroid_mpio[1], centroid_mpio[0]], zoom_start=9, tiles="CartoDB positron")

                for _, r in gdf_openDataMpio.iterrows():
                    sim_geo = gpd.GeoSeries(r['geometry'])
                    geo_j = sim_geo.to_json()
                    geo_j = folium.GeoJson(data=geo_j, style_function=style_function(r['COLOR']))
                    folium.Popup('{0} \nÁrea(he): {1}'.format(dict_aptitudeLabel[r['APTITUD']], r['AREA_HECTAREAS'])).add_to(geo_j)
                    geo_j.add_to(m)

                sub1_tab1, sub1_tab2 = st.tabs([
                    '🗺️ **Distribución geográfica**',
                    '📊 **Distribución porcentual**'])

                with sub1_tab1:
                    with st.container(height=400):
                        st_data = st_folium(m, width=700, height=400)

                with sub1_tab2:
                    fig, ax = plt.subplots(1, 1, figsize=(6, 4))
                    ax.pie(df_areaOpenDataMpio['AREA_PERCENT'],
                    labels=[f"{row['APTITUD_LABEL']}\n{round(row['AREA_KM2'],1)} km²" for _, row in df_areaOpenDataMpio.iterrows()],
                    colors=df_areaOpenDataMpio['COLOR'],
                    autopct='%1.1f%%', textprops={'fontsize': 7})
                
                    ax.set_title(f'{options_mpio} - {nameProduct}', fontsize=8)
                
                    st.pyplot(fig)

    return

def pageDpto():
    st.subheader('Análisis de aptitud departamental', divider='green')

    with st.form('form_2'):
        options_products = st.selectbox(label='**Aptitud agropecuaria:**', options=list_emojiProduct, index=18)
        options_dpto = st.selectbox(label='**Departamento:**', options=list_dpto, index=26)
        option_croquis_mpio = st.checkbox('Ver división municipal del departamento')

        submitted = st.form_submit_button('**Aceptar**')

        if submitted and options_dpto is not None:
            nameDataset, nameProduct = fun.from_emojiProduct_to_nameDataset(options_products, list_emojiProduct, list_nameDatasets, list_nameProduct)
            dpto_code = dict_dptoNameCode[options_dpto]
            gdf_DaneDpto = fun.get_gdf_DaneDpto(flag_gcs, fs, BUCKET_NAME, dpto_code)
            gdf_DaneDptoMpio = fun.get_gdf_DaneDptoMpio(flag_gcs, fs, BUCKET_NAME, dpto_code)
            gdf_openDataDpto = fun.get_gdf_openDataDpto(flag_gcs, fs, BUCKET_NAME, nameDataset, options_dpto)
            df_areaOpenDataDpto = fun.get_df_areaOpenDataDpto(gdf_openDataDpto, gdf_DaneDpto, 'DPTO_AREA', dict_aptitudeLabel, dict_aptitudeColor)
             
            sub2_tab1, sub2_tab2, sub2_tab3 = st.tabs(['🗺️ **Distribución geográfica**',
                                                       '📊 **Distribución porcentual**',
                                                       '🏆 **Top municipios**'])

            with sub2_tab1:
                fig, ax = plt.subplots(1, 1, figsize=(10, 8))

                gdf_openDataDpto.plot(ax=ax, color=gdf_openDataDpto['COLOR'], edgecolor="none")

                if option_croquis_mpio:
                    gdf_DaneDptoMpio.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=0.5)
                else:
                    gdf_DaneDpto.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=0.5)

                ax.set_title(f'{options_dpto} - {nameProduct}', fontsize=10)
                ax.set_xlabel("Longitud")
                ax.set_ylabel("Latitud")
                ax.grid()

                st.pyplot(fig)

            with sub2_tab2:
                fig, ax = plt.subplots(1, 1, figsize=(6, 4))
                ax.pie(df_areaOpenDataDpto['AREA_PERCENT'],
                    labels=[f"{row['APTITUD_LABEL']}\n{round(row['AREA_KM2'],1)} km²" for _, row in df_areaOpenDataDpto.iterrows()],
                    colors=df_areaOpenDataDpto['COLOR'],
                    autopct='%1.1f%%', textprops={'fontsize': 7})
                
                ax.set_title(f'{options_dpto} - {nameProduct}', fontsize=8)
                
                st.pyplot(fig)

            with sub2_tab3:
                list_labelSubTab = fun.get_list_labelSubTab(dict_aptitudLabelReversed, dict_aptitudeEmojin)

                with st.container(border=True):
                    resub2_1, resub2_2, resub2_3, resub2_4, resub2_5 = st.tabs(list_labelSubTab)

                    dict_reSubTap = {
                        4: resub2_1,
                        3: resub2_2,
                        2: resub2_3,
                        1: resub2_4,
                        0: resub2_5
                    }

                    cont_idx = 0

                    for key, value in dict_reSubTap.items():
                        df_aptitudeDptoMpio = fun.get_df_aptitudeDptoMpio(gdf_openDataDpto, gdf_DaneDptoMpio, key)
                        aptitudeLabel = dict_aptitudeLabel[key]

                        with value:
                            st.markdown(f"**TOP 10 ÁREA CON {aptitudeLabel.upper()} POR MUNICIPIOS EN {options_dpto}**")

                            df_hbar1 = df_aptitudeDptoMpio.head(10)
                            df_hbar1 = df_hbar1.sort_values(by='AREA_KM2', ascending=True)
                            xlabel_hbar1 = f'Área con {aptitudeLabel} (km²)'

                            fun.plot_hbar(df=df_hbar1, col_y='MUNICIPIO', col_x='AREA_KM2',
                                          title=None, xlabel=xlabel_hbar1, color=dict_aptitudeColor[key])
                            
                            st.markdown(f"**TOP 10 PORCENTAJE DEL TERRITORIO CON {aptitudeLabel.upper()} POR MUNICIPIOS EN {options_dpto}**")
                            
                            df_hbar2 = df_aptitudeDptoMpio.sort_values(by='AREA_PERCENT', ascending=False).head(10)
                            df_hbar2 = df_hbar2.sort_values(by='AREA_PERCENT', ascending=True)
                            xlabel_hbar2 = f'Porcentaje de área municipal con {aptitudeLabel} (%)'

                            fun.plot_hbar(df=df_hbar2, col_y='MUNICIPIO', col_x='AREA_PERCENT',
                                          title=None, xlabel=xlabel_hbar2, color=dict_aptitudeColor[key])
                            
                        cont_idx = cont_idx + 1

    return

def pageLocal():
    st.subheader('Análisis localizado', divider='green')

    click_map = folium.Map(location=[4.64, -74], zoom_start=5)
    click_marker = folium.LatLngPopup()
    click_map.add_child(click_marker)

    with st.container(height=400):
        map_local = st_folium(click_map, width=700, height=400)

    if map_local and map_local["last_clicked"]:
        coords = map_local["last_clicked"]
        latitude = round(coords['lat'], 5)
        longitude = round(coords['lng'], 5)

    with st.form('form_3'):
        optionsMultiProducts = st.multiselect('**Aptitud agropecuaria:**', options=list_emojiProduct, default=list_emojiProduct[18])

        submitted = st.form_submit_button('**Aceptar**')

        if submitted:
            gdf_DaneCountryDpto = fun.get_gdf_DaneCountryDpto(flag_gcs, fs, BUCKET_NAME)
            
            gdf_polygonDpto = fun.get_polygonDane(gdf_DaneCountryDpto, latitude, longitude)

            if gdf_polygonDpto.shape[0] == 1:
                dpto_code = gdf_polygonDpto.iloc[0]['DPTO_CODE']
                dpto_name = dict_dptoCodeName[dpto_code]

                gdf_DaneDptoMpio = fun.get_gdf_DaneDptoMpio2(flag_gcs, fs, BUCKET_NAME, dpto_code, dpto_name)

                gdf_polygonMpio = fun.get_polygonDane(gdf_DaneDptoMpio, latitude, longitude)

                mpio_code = gdf_polygonMpio.iloc[0]['DPTO_CODE']
                mpio_name = gdf_polygonMpio.iloc[0]['MUNICIPIO']

                st.text(f'{dpto_name} - {mpio_name}')

                openDataPath = f'datasets/datos_abiertos/dpto_name/'

                #nameDataset, nameProduct = fun.from_emojiProduct_to_nameDataset(options_products, list_emojiProduct, list_nameDatasets, list_nameProduct)


                #st.text(optionsMultiProducts)


                
            

            


    return


st.markdown(fun.get_str_GoogleFonts(), unsafe_allow_html=True)
st.markdown(**fun.get_dict_customFont("🌿AgroSmart App"))

with st.sidebar:
    if not fun.str2bool(st.secrets.GCS_INFO['hide_widget_management']):
        list_optionsManagement = ["💾 Local", "☁️ Google Cloud"]
        optionsManagement = st.pills('**Gestión de archivos:**', options=list_optionsManagement,
                                     selection_mode='single', default=list_optionsManagement[st.session_state['management']],
                                     disabled=fun.str2bool(st.secrets.GCS_INFO['disable_widget_management']))
        
        if optionsManagement is not None:
            st.session_state['management'] = list_optionsManagement.index(optionsManagement)
        

pg = st.navigation([
    st.Page(pageHome, title='Inicio', icon='🏠'),
    st.Page(pageDpto, title='Departamento'),
    st.Page(pageMpio, title='Municipio'),
    st.Page(pageLocal, title='Local'),
])
pg.run()

st.divider()

with st.expander('**Clasificación de la aptitud agropecuaria**', icon='🏆'):
    with st.container(border=True):
        for i in range(0,len(list_markdownLabelAptitude),1):
            st.markdown(list_markdownLabelAptitude[i], unsafe_allow_html=True)
