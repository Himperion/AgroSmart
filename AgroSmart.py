# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import folium
import fun

from streamlit_folium import st_folium

def style_function(color):
    return lambda x: {
        'fillColor': color,
        'color': color,
        'weight': 1,
        'fillOpacity': 0.5
    }

dict_aptitud_label = {
    0: 'Exclusión legal',
    1: 'No apta',
    2: 'Aptitud baja',
    3: 'Aptitud media',
    4: 'Aptitud alta'
}

dict_product, list_nameProduct, list_nameDatasets, list_emojiProduct = fun.get_datasets_names()
list_dpto = fun.get_list_dpto()

st.markdown("# 🌿AgroSmart")

tap1, tap2, tap3 = st.tabs(['Municipal', 'Departamental', 'Localizado'])

with tap1:
    #with st.container(border=True):
    with st.form('form_1'):
        options_products = st.selectbox(label='Aptitud agropecuaria:', options=list_emojiProduct, index=18)
        options_dpto = st.selectbox(label='Departamento:', options=list_dpto, index=26)

        nameDataset, nameProduct = fun.from_emojiProduct_to_nameDataset(options_products, list_emojiProduct, list_nameDatasets, list_nameProduct)
        dpto_code = fun.get_dpto_code(options_dpto)
        gdf_openDataDpto = fun.get_gdf_openDataDpto(nameDataset, options_dpto)
        dict_Mpio_MpioCode = fun.get_dict_Mpio_MpioCode(gdf_openDataDpto)

        options_mpio = st.selectbox(label='Municipio:', options=[key for key in dict_Mpio_MpioCode], index=None,
                                    placeholder='Seleccione una opción')


        submitted = st.form_submit_button('Aceptar')

        if submitted and options_mpio is not None:
            mpio_code = dict_Mpio_MpioCode[options_mpio]
            
            gdf_openDataMpio = fun.get_gdf_openDataMpio(gdf_openDataDpto, mpio_code)

            m = folium.Map(location=[4.36, -74.04], zoom_start=6, tiles="CartoDB positron")

            for _, r in gdf_openDataMpio.iterrows():
                #sim_geo = gpd.GeoSeries(r['THE_GEOM']).simplify(tolerance=0.0001)
                sim_geo = gpd.GeoSeries(r['geometry'])
                geo_j = sim_geo.to_json()
                geo_j = folium.GeoJson(data=geo_j,
                                       style_function=style_function(r['COLOR']))
                folium.Popup('{0} \nÁrea(he): {1}'.format(dict_aptitud_label[r['APTITUD']], r['AREA_HECTAREAS'])).add_to(geo_j)
                geo_j.add_to(m)

            st_data = st_folium(m, width=700, height=500)
            

with tap2:
    with st.form('form_2'):
        options_products = st.selectbox(label='Aptitud agropecuaria:', options=list_emojiProduct, index=18)
        options_dpto = st.selectbox(label='Departamento:', options=list_dpto, index=26)
        option_croquis_mpio = st.checkbox('Ver división municipal del departamento')

        submitted = st.form_submit_button('Aceptar')

        if submitted:
            nameDataset, nameProduct = fun.from_emojiProduct_to_nameDataset(options_products, list_emojiProduct, list_nameDatasets, list_nameProduct)
            dpto_code = fun.get_dpto_code(options_dpto)
            gdf_DaneDpto = fun.get_gdf_DaneDpto(dpto_code)
            gdf_DaneDptoMpio = fun.get_gdf_DaneDptoMpio(dpto_code)
            gdf_openDataDpto = fun.get_gdf_openDataDpto(nameDataset, options_dpto)
            df_areaOpenDataDpto = fun.get_df_areaOpenDataDpto(gdf_openDataDpto, gdf_DaneDpto, 'DPTO_AREA')
            df_topDptoMpio = fun.get_df_topDptoMpio(gdf_openDataDpto, gdf_DaneDptoMpio)
             
            sub2_tab1, sub2_tab2, sub2_tab3 = st.tabs(['🗺️ **Distribución geográfica**',
                                                       '📊 **Distribución porcentual**',
                                                       '🥇 **Top municipios**'])

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
                df_hbar1 = df_topDptoMpio.head(10)
                df_hbar1 = df_hbar1.sort_values(by='AREA_KM2', ascending=True)
                title_hbar1 = f'TOP 10 ÁREA CON APTITUD ALTA POR MUNICIPIO EN {options_dpto}'
                xlabel_hbar1 = 'Área con aptitud alta (km²)'

                fun.plot_hbar(df=df_hbar1, col_y='MUNICIPIO', col_x='AREA_KM2',
                              title=title_hbar1, xlabel=xlabel_hbar1, color='#138848')

                df_hbar2 = df_topDptoMpio.sort_values(by='AREA_PERCENT', ascending=False).head(10)
                df_hbar2 = df_hbar2.sort_values(by='AREA_PERCENT', ascending=True)
                title_hbar2 = f'TOP 10 PORCENTAJE DEL TERRITORIO CON APTITUD ALTA POR MUNICIPIO EN {options_dpto}'
                xlabel_hbar2 = 'Porcentaje de área con aptitud alta en el municipio (%)'

                fun.plot_hbar(df=df_hbar2, col_y='MUNICIPIO', col_x='AREA_PERCENT',
                              title=title_hbar2, xlabel=xlabel_hbar2, color='#138848')