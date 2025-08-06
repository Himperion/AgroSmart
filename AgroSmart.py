# -*- coding: utf-8 -*-
import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.express as px
import folium, yaml, s3fs
#import fun

import funtions

from matplotlib.patches import Patch
from streamlit_folium import st_folium
from shapely.geometry import Point

from data.aptitude import DICT_APTITUDE, DICT_LABEL_APTITUDE, DICT_APTITUDE_NAME, DICT_APTITUDE_COLOR, DICT_APTITUDE_LABEL, LIST_APTITUDE_LABEL
from data.info import Members, DescriptiveText
from data.items_da import DICT_ITEMS, DICT_ITEMS_NAME_LABEL, DICT_ITEMS_LABEL_NAME, DICT_DPTO, LIST_DPTO_NAME

def style_function(color):
    return lambda x: {
        'fillColor': color,
        'color': color,
        'weight': 1,
        'fillOpacity': 0.5
    }

#%% CLOUDFLARE_R2
    
r2_fs = s3fs.S3FileSystem(
    key=st.secrets.CLOUDFLARE_R2["ACCESS_KEY_ID"],
    secret=st.secrets.CLOUDFLARE_R2["SECRET_ACCESS_KEY"],
    client_kwargs={
        "endpoint_url": st.secrets.CLOUDFLARE_R2["BUCKET_ENDPOINT"]
    }
)

selectCoordinateOptions = ["Sistema sexagesimal GMS", "Sistema decimal GD"]
    
def pageHome():

    tab1, tab2 = st.tabs(["Descripción", "Equipo humano"])

    with tab1:
        st.markdown(DescriptiveText.TEXT0.value)

    with tab2:
        with st.container(border=True):
            col1, col2 = st.columns([0.3, 0.7], vertical_alignment="center")

            with col1:
                st.image(Members.MEMBER0.value.Image, width=200)

            with col2:
                st.subheader(Members.MEMBER0.value.Name, divider=True)
                st.caption(Members.MEMBER0.value.Description)
                st.markdown(f"📧 {Members.MEMBER0.value.Email}")
                st.markdown(f"🐈‍⬛ {Members.MEMBER0.value.GitHub}")

        with st.container(border=True):
            col1, col2 = st.columns([0.3, 0.7], vertical_alignment="center")

            with col1:
                st.image(Members.MEMBER1.value.Image, width=200)

            with col2:
                st.subheader(Members.MEMBER1.value.Name, divider=True)
                st.caption(Members.MEMBER1.value.Description)
                st.markdown(f"📧 {Members.MEMBER1.value.Email}")
                st.markdown(f"🐈‍⬛ {Members.MEMBER1.value.GitHub}")

    return

# """
# def pageMpio():
#     options_products, options_dpto = None, None

#     st.subheader('Análisis de aptitud municipal', divider='green')

#     with st.container(border=True):
#         options_products = st.selectbox(label='**Aptitud agropecuaria:**', options=list_emojiProduct, index=18)
#         options_dpto = st.selectbox(label='**Departamento:**', options=list_dpto, index=26)

#     if options_products is not None and options_dpto is not None:
#         with st.form('form_1'):

#             nameDataset, nameProduct = fun.from_emojiProduct_to_nameDataset(options_products, list_emojiProduct, list_nameDatasets, list_nameProduct)
#             dpto_code = dict_dptoNameCode[options_dpto]
#             gdf_openDataDpto = fun.get_gdf_openDataDpto(flag_gcs, fs, BUCKET_NAME, nameDataset, options_dpto)
#             dict_Mpio_MpioCode = fun.get_dict_Mpio_MpioCode(gdf_openDataDpto)

#             options_mpio = st.selectbox(label='**Municipio:**', options=[key for key in dict_Mpio_MpioCode], index=None,
#                                         placeholder='Seleccione una opción')
            
#             submitted = st.form_submit_button('**Aceptar**')
    
#             if submitted and options_products is not None and options_dpto is not None and options_mpio is not None:
#                 mpio_code = dict_Mpio_MpioCode[options_mpio]
                
#                 gdf_openDataMpio = fun.get_gdf_openDataMpio(gdf_openDataDpto, mpio_code)
#                 gdf_DaneMpio = fun.get_gdf_DaneMpio(flag_gcs, fs, BUCKET_NAME, dpto_code, mpio_code)
#                 df_areaOpenDataMpio = fun.get_df_areaOpenDataDpto(gdf_openDataMpio, gdf_DaneMpio, 'MPIO_AREA', dict_aptitudeLabel, dict_aptitudeColor)

#                 centroid_mpio = [round(x, 3) for x in gdf_DaneMpio["CENTROID"].iloc[0].coords[0]]

#                 m = folium.Map(location=[centroid_mpio[1], centroid_mpio[0]], zoom_start=9, tiles="CartoDB positron")

#                 for _, r in gdf_openDataMpio.iterrows():
#                     sim_geo = gpd.GeoSeries(r['geometry'])
#                     geo_j = sim_geo.to_json()
#                     geo_j = folium.GeoJson(data=geo_j, style_function=style_function(r['COLOR']))
#                     folium.Popup('{0} \nÁrea(he): {1}'.format(dict_aptitudeLabel[r['APTITUD']], r['AREA_HECTAREAS'])).add_to(geo_j)
#                     geo_j.add_to(m)

#                 sub1_tab1, sub1_tab2 = st.tabs([
#                     '🗺️ **Distribución geográfica**',
#                     '📊 **Distribución porcentual**'])

#                 with sub1_tab1:
#                     with st.container(height=400):
#                         st_data = st_folium(m, width=700, height=400)

#                 with sub1_tab2:
#                     fig, ax = plt.subplots(1, 1, figsize=(6, 4))
#                     ax.pie(df_areaOpenDataMpio['AREA_PERCENT'],
#                     labels=[f"{row['APTITUD_LABEL']}\n{round(row['AREA_KM2'],1)} km²" for _, row in df_areaOpenDataMpio.iterrows()],
#                     colors=df_areaOpenDataMpio['COLOR'],
#                     autopct='%1.1f%%', textprops={'fontsize': 7})
                
#                     ax.set_title(f'{options_mpio} - {nameProduct}', fontsize=8)
                
#                     st.pyplot(fig)

#     return
# """

def pageDpto():
    st.subheader('Análisis de aptitud departamental', divider='green')


    with st.form("form_dpto"):
        options_products = st.selectbox(label="**Aptitud agropecuaria:**", options=[key for key in DICT_ITEMS_LABEL_NAME], index=18)
        options_dpto = st.selectbox(label="**Departamento:**", options=LIST_DPTO_NAME, index=26)
        options_aptitude = st.multiselect(label="**Clasificación de la aptitud agropecuaria**", options=LIST_APTITUDE_LABEL, default=LIST_APTITUDE_LABEL[:-3])
        option_croquis_mpio = st.checkbox('Ver división municipal del departamento')

        submitted = st.form_submit_button("**Aceptar**")

        if submitted and options_dpto is not None and len(options_aptitude) != 0:
            dpto_code = DICT_DPTO[options_dpto]["DPTO_CODE"]
            partial_name = DICT_ITEMS[DICT_ITEMS_LABEL_NAME[options_products]]["PARTIAL_NAME"]
            aptitude_select = [DICT_LABEL_APTITUDE[value] for value in options_aptitude]

            path_dpto_item = funtions.get_path_dpto_item(dpto_name=options_dpto, dpto_code=dpto_code, partial_name=partial_name)

            gdf_dpto_item = funtions.open_dataset_dpto_item(r2_fs, path_dpto_item, aptitude_select, DICT_APTITUDE_COLOR, DICT_APTITUDE_NAME)
            gdf_dane_dpto = funtions.get_gdf_dane_dpto(dpto_code)
            gdf_dane_dpto_mpio = funtions.get_gdf_dane_dpto_mpio(dpto_code)

            area_dpto = gdf_dane_dpto["DPTO_AREA"].iloc[0]

            with st.container(border=True):
    
                dpto_tab1, dpto_tab2, dpto_tab3 = st.tabs(['🗺️ **Distribución geográfica**',
                                                        '📊 **Distribución porcentual**',
                                                        '🏆 **Top municipios**'])
                
                with dpto_tab1:
                    unique_legend = funtions.get_gdf_unique_legend(gdf_dpto_item)

                    legend_elements = [
                        Patch(facecolor=row["COLOR"], edgecolor='black', label=row["LABEL"])
                        for _, row in unique_legend.iterrows()
                        ]

                    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

                    gdf_dpto_item.plot(ax=ax, color=gdf_dpto_item["COLOR"], edgecolor="none")
                    gdf_dane_dpto.plot(ax=ax, edgecolor="black", facecolor="none", linewidth=0.5)

                    if option_croquis_mpio:
                        gdf_dane_dpto_mpio.plot(ax=ax, edgecolor="black", facecolor="none", linewidth=0.5)

                    ax.legend(handles=legend_elements, title="Clasificación", loc="upper right")
                    ax.axis("off")

                    st.pyplot(fig)
                    
                with dpto_tab2:
                    df_info_dpto = funtions.get_df_info_dpto(gdf_dpto_item, DICT_APTITUDE_LABEL, DICT_APTITUDE_COLOR, area_dpto)

                    fig = px.pie(
                        df_info_dpto,
                        values="AREA_PERCENT",
                        names="APTITUD_LABEL",
                        color="APTITUD_LABEL",
                        color_discrete_map=dict(zip(df_info_dpto["APTITUD_LABEL"], df_info_dpto["COLOR"]))
                    )

                    fig.update_traces(
                        hovertemplate=(
                            "<b>%{label}</b><br>"
                            "<br>"
                            "<b>Área Total (km²):</b> %{customdata[0]:,.2f}<br>"
                            "<b>Porcentaje:</b> %{percent}<extra></extra>"
                            )
                    )

                    fig.update_traces(customdata=df_info_dpto[['AREA_KM2']], selector=dict(type='pie'))

                    st.plotly_chart(fig, use_container_width=True)

                with dpto_tab3:
                    dpto_tab3_sub1, dpto_tab3_sub2, dpto_tab3_sub3, dpto_tab3_sub4, dpto_tab3_sub5 = None, None, None, None, None

                    if len(aptitude_select) == 1:
                        dpto_tab3_sub1 = st.tabs(options_aptitude)
                        
                    elif len(aptitude_select) == 2:
                        dpto_tab3_sub1, dpto_tab3_sub2 = st.tabs(options_aptitude)
                    elif len(aptitude_select) == 3:
                        dpto_tab3_sub1, dpto_tab3_sub2, dpto_tab3_sub3 = st.tabs(options_aptitude)
                    elif len(aptitude_select) == 4:
                        dpto_tab3_sub1, dpto_tab3_sub2, dpto_tab3_sub3, dpto_tab3_sub4 = st.tabs(options_aptitude)
                    elif len(aptitude_select) == 5:
                        dpto_tab3_sub1, dpto_tab3_sub2, dpto_tab3_sub3, dpto_tab3_sub4, dpto_tab3_sub5 = st.tabs(options_aptitude)

                    dict_code_mpio = DICT_DPTO[options_dpto]["DICT_CODE_MPIO"]
                    top = 15

                    if dpto_tab3_sub1 is not None:
                        with dpto_tab3_sub1:
                            df_result_dpto_mpio = funtions.get_df_result_dpto_mpio(gdf_dpto_item, gdf_dane_dpto_mpio, dict_code_mpio, aptitude_select[0])
                            label: str = DICT_APTITUDE[aptitude_select[0]]["Label"]
                            color_aptitude = DICT_APTITUDE_COLOR[aptitude_select[0]]

                            fig = px.bar(
                                funtions.get_df_result_top_dpto_mpio(df_result_dpto_mpio, "AREA_KM2", top),
                                x="AREA_KM2",
                                y="MUNICIPIO",
                                orientation="h",
                                labels={"AREA_KM2": "Área (km²)", "MUNICIPIO": "Municipio"},
                                color_discrete_sequence=[color_aptitude]
                            )

                            fig.update_yaxes(autorange="reversed")

                            fig.update_layout(
                                title={
                                    "text": f"TOP {top} ÁREA POR {label.upper()} POR MUNICIPIOS EN {options_dpto}",
                                    "x": 0.5,
                                    "xanchor": "center"
                                },
                                title_font_size=16
                            )
                            
                            st.plotly_chart(
                                fig,
                                use_container_width=True,
                                config={
                                    "modeBarButtonsToRemove": ["zoomIn2d",
                                                               "zoomOut2d",
                                                               "autoScale2d",
                                                               "resetScale2d",
                                                               "zoom2d",
                                                               "pan2d",
                                                               "select2d",
                                                               "lasso2d"],
                                    "displaylogo": False
                                }
                            )
                            

                            

                            

                            

                            
                        




            



    # """
    # with st.form('form_2'):
    #     options_products = st.selectbox(label='**Aptitud agropecuaria:**', options=list_emojiProduct, index=18)
    #     options_dpto = st.selectbox(label='**Departamento:**', options=list_dpto, index=26)
    #     option_croquis_mpio = st.checkbox('Ver división municipal del departamento')

    #     submitted = st.form_submit_button('**Aceptar**')

    #     if submitted and options_dpto is not None:
    #         nameDataset, nameProduct = fun.from_emojiProduct_to_nameDataset(options_products, list_emojiProduct, list_nameDatasets, list_nameProduct)
    #         dpto_code = dict_dptoNameCode[options_dpto]
    #         gdf_DaneDpto = fun.get_gdf_DaneDpto(flag_gcs, fs, BUCKET_NAME, dpto_code)
    #         gdf_DaneDptoMpio = fun.get_gdf_DaneDptoMpio(flag_gcs, fs, BUCKET_NAME, dpto_code)
    #         gdf_openDataDpto = fun.get_gdf_openDataDpto(flag_gcs, fs, BUCKET_NAME, nameDataset, options_dpto)
    #         df_areaOpenDataDpto = fun.get_df_areaOpenDataDpto(gdf_openDataDpto, gdf_DaneDpto, 'DPTO_AREA', dict_aptitudeLabel, dict_aptitudeColor)
             
    #         sub2_tab1, sub2_tab2, sub2_tab3 = st.tabs(['🗺️ **Distribución geográfica**',
    #                                                    '📊 **Distribución porcentual**',
    #                                                    '🏆 **Top municipios**'])

            
    #         with sub2_tab3:
    #             list_labelSubTab = fun.get_list_labelSubTab(dict_aptitudLabelReversed, dict_aptitudeEmojin)

    #             with st.container(border=True):
    #                 resub2_1, resub2_2, resub2_3, resub2_4, resub2_5 = st.tabs(list_labelSubTab)

    #                 dict_reSubTap = {
    #                     4: resub2_1,
    #                     3: resub2_2,
    #                     2: resub2_3,
    #                     1: resub2_4,
    #                     0: resub2_5
    #                 }

    #                 cont_idx = 0

    #                 for key, value in dict_reSubTap.items():
    #                     df_aptitudeDptoMpio = fun.get_df_aptitudeDptoMpio(gdf_openDataDpto, gdf_DaneDptoMpio, key)
    #                     aptitudeLabel = dict_aptitudeLabel[key]

    #                     with value:
    #                         st.markdown(f"**TOP 10 ÁREA CON {aptitudeLabel.upper()} POR MUNICIPIOS EN {options_dpto}**")

    #                         df_hbar1 = df_aptitudeDptoMpio.head(10)
    #                         df_hbar1 = df_hbar1.sort_values(by='AREA_KM2', ascending=True)
    #                         xlabel_hbar1 = f'Área con {aptitudeLabel} (km²)'

    #                         fun.plot_hbar(df=df_hbar1, col_y='MUNICIPIO', col_x='AREA_KM2',
    #                                       title=None, xlabel=xlabel_hbar1, color=dict_aptitudeColor[key])
                            
    #                         st.markdown(f"**TOP 10 PORCENTAJE DEL TERRITORIO CON {aptitudeLabel.upper()} POR MUNICIPIOS EN {options_dpto}**")
                            
    #                         df_hbar2 = df_aptitudeDptoMpio.sort_values(by='AREA_PERCENT', ascending=False).head(10)
    #                         df_hbar2 = df_hbar2.sort_values(by='AREA_PERCENT', ascending=True)
    #                         xlabel_hbar2 = f'Porcentaje de área municipal con {aptitudeLabel} (%)'

    #                         fun.plot_hbar(df=df_hbar2, col_y='MUNICIPIO', col_x='AREA_PERCENT',
    #                                       title=None, xlabel=xlabel_hbar2, color=dict_aptitudeColor[key])
                            
    #                     cont_idx = cont_idx + 1

    # """
    return

# """
# def pageLocal():
#     st.subheader('Análisis localizado', divider='green')

#     click_map = folium.Map(location=[4.64, -74], zoom_start=5)
#     click_marker = folium.LatLngPopup()
#     click_map.add_child(click_marker)

#     with st.container(height=400):
#         map_local = st_folium(click_map, width=700, height=400)

#     if map_local and map_local["last_clicked"]:
#         coords = map_local["last_clicked"]
#         latitude = round(coords['lat'], 5)
#         longitude = round(coords['lng'], 5)

#     with st.form('form_3'):
#         optionsMultiProducts = st.multiselect('**Aptitud agropecuaria:**', options=list_emojiProduct, default=list_emojiProduct[18])

#         submitted = st.form_submit_button('**Aceptar**')

#         if submitted:
#             gdf_DaneCountryDpto = fun.get_gdf_DaneCountryDpto(flag_gcs, fs, BUCKET_NAME)
            
#             gdf_polygonDpto = fun.get_polygonDane(gdf_DaneCountryDpto, latitude, longitude)

#             if gdf_polygonDpto.shape[0] == 1:
#                 dpto_code = gdf_polygonDpto.iloc[0]['DPTO_CODE']
#                 dpto_name = dict_dptoCodeName[dpto_code]

#                 gdf_DaneDptoMpio = fun.get_gdf_DaneDptoMpio2(flag_gcs, fs, BUCKET_NAME, dpto_code, dpto_name)

#                 gdf_polygonMpio = fun.get_polygonDane(gdf_DaneDptoMpio, latitude, longitude)

#                 mpio_code = gdf_polygonMpio.iloc[0]['DPTO_CODE']
#                 mpio_name = gdf_polygonMpio.iloc[0]['MUNICIPIO']

#                 st.text(f'{dpto_name} - {mpio_name}')

#                 openDataPath = f'datasets/datos_abiertos/dpto_name/'

#                 #nameDataset, nameProduct = fun.from_emojiProduct_to_nameDataset(options_products, list_emojiProduct, list_nameDatasets, list_nameProduct)


#                 #st.text(optionsMultiProducts)


#     return
# """

st.markdown(funtions.get_str_GoogleFonts(), unsafe_allow_html=True)
st.markdown(**funtions.get_dict_customFont("🌿AgroSmart App"))


with st.sidebar:
    
    st.text("En construcción")
        

pg = st.navigation([
    st.Page(pageHome, title='Inicio', icon='🏠'),
    st.Page(pageDpto, title='Departamento'),
    #st.Page(pageMpio, title='Municipio'),
    #st.Page(pageLocal, title='Local'),
])
pg.run()

st.divider()

with st.expander("**Clasificación de la aptitud agropecuaria**", icon="🏆"):
    with st.container(border=True):
        for key, value in DICT_APTITUDE.items():
            st.markdown(f"{value['Emoji']} **{value['Name']}:** {value['Description']}", unsafe_allow_html=True)