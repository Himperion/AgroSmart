# -*- coding: utf-8 -*-
import yaml
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import streamlit as st

dict_aptitud_label = {
    0: 'Exclusión legal',
    1: 'No apta',
    2: 'Aptitud baja',
    3: 'Aptitud media',
    4: 'Aptitud alta'
}

dict_aptitud_color = {
    0: '#C4C4C4',
    1: '#E44432',
    2: '#FCC070',
    3: '#79C162',
    4: '#138848'
}

def get_datasets_names():
    dict_product, list_product, list_nameDatasets, list_emojiProduct = {}, [], [], []

    with open('datasets_names.yaml', 'r') as archivo:
        dict_product = yaml.safe_load(archivo)

    for key, value in dict_product.items():
        list_product.append(key)
        list_nameDatasets.append(value['name'])
        list_emojiProduct.append(value['emoji-product'])

    return dict_product, list_product, list_nameDatasets, list_emojiProduct

def from_emojiProduct_to_nameDataset(emojiProduct: str, list_emojiProduct: list, list_nameDatasets: list, list_nameProduct: list) -> str:

    index = list_emojiProduct.index(emojiProduct)
    nameDataset, nameProduct = list_nameDatasets[index], list_nameProduct[index]

    return nameDataset, nameProduct

def get_list_dpto():

    list_dpto = ['AMAZONAS', 'ANTIOQUIA', 'ARAUCA', 'ATLÁNTICO',
                 'BOLÍVAR', 'BOYACÁ', 'CALDAS', 'CAQUETÁ',
                 'CASANARE', 'CAUCA', 'CESAR', 'CHOCÓ', 
                 'CUNDINAMARCA', 'CÓRDOBA', 'GUAINÍA', 'GUAVIARE',
                 'HUILA', 'GUAJIRA', 'MAGDALENA', 'META',
                 'NARIÑO', 'NORTE DE SANTANDER', 'PUTUMAYO', 'QUINDÍO',
                 'RISARALDA', 'ARCHIPIÉLAGO DE SAN ANDRÉS, PROVIDENCIA Y SANTA CATALINA', 'SANTANDER', 'SUCRE',
                 'TOLIMA', 'VALLE DEL CAUCA', 'VAUPÉS', 'VICHADA']

    return list_dpto

def get_dict_Mpio_MpioCode(gdf_openDataDpto: pd.DataFrame) -> dict:

    dict_Mpio_MpioCode = {}

    gdf_openDataDpto['NUM_DATA'] = 1
    gdf_openDataDpto = gdf_openDataDpto.groupby(['MPIO_CODE', 'MUNICIPIO'], as_index=False)['NUM_DATA'].sum()

    for _, row in gdf_openDataDpto.iterrows():
        dict_Mpio_MpioCode[row['MUNICIPIO']] = row['MPIO_CODE']

    return dict_Mpio_MpioCode

def get_dpto_code(dpto_name):

    df_dpto = pd.read_excel('datasets/DICT_CODIGO_DANE.xlsx', sheet_name='DICT_DPTO')
    df_dpto = df_dpto[df_dpto['DEPARTAMENTO'] == dpto_name]

    return df_dpto['DPTO_CODE'].iloc[0]

def get_gdf_DaneDpto(dpto_code) -> gpd.GeoDataFrame:

    gdf_DaneDpto = gpd.read_file('datasets/geoportal_DANE/MGN_ADM_DPTO_POLITICO.gpkg')
    gdf_DaneDpto = gdf_DaneDpto[gdf_DaneDpto['DPTO_CODE'] == dpto_code]

    return gdf_DaneDpto

def get_gdf_DaneDptoMpio(dpto_code)-> gpd.GeoDataFrame:

    gdf_DaneDptoMpio = gpd.read_file('datasets/geoportal_DANE/MGN_ADM_MPIO_GRAFICO.gpkg')
    gdf_DaneDptoMpio = gdf_DaneDptoMpio[gdf_DaneDptoMpio['DPTO_CODE'] == dpto_code]

    return gdf_DaneDptoMpio

def get_gdf_DaneMpio(dpto_code, mpio_code) -> gpd.GeoDataFrame:

    gdf_DaneMpio = gpd.read_file('datasets/geoportal_DANE/MGN_ADM_MPIO_GRAFICO.gpkg')
    gdf_DaneMpio = gdf_DaneMpio[gdf_DaneMpio['DPTO_CODE'] == dpto_code]
    gdf_DaneMpio = gdf_DaneMpio[gdf_DaneMpio['MPIO_CODE'] == mpio_code]
    gdf_DaneMpio["CENTROID"] = gdf_DaneMpio.centroid

    return gdf_DaneMpio

def get_gdf_openDataDpto(nameDataset: str, nameDpto) -> gpd.GeoDataFrame:

    gdf_openDataDpto = gpd.read_file(f'datasets/datos_abiertos/{nameDpto}/{nameDataset}.gpkg')

    return gdf_openDataDpto

def get_gdf_openDataMpio(gdf_openDataDpto: gpd.GeoDataFrame, mpio_code: int)-> gpd.GeoDataFrame:

    gdf_openDataMpio = gdf_openDataDpto[gdf_openDataDpto['MPIO_CODE'] == mpio_code]

    return gdf_openDataMpio

def get_gdf_areaDane(gdf_dane: gpd.GeoDataFrame, column_dane_area: str) -> float:

    return gdf_dane[column_dane_area].iloc[0]

def get_df_areaOpenDataDpto(gdf_openData: gpd.GeoDataFrame, gdf_dane: gpd.GeoDataFrame, column_dane_area: str) -> pd.DataFrame:

    area_dane = get_gdf_areaDane(gdf_dane, column_dane_area)

    gdf_area = gdf_openData.groupby('APTITUD')['AREA_HECTAREAS'].sum().reset_index()
    gdf_area['AREA_KM2'] = gdf_area['AREA_HECTAREAS']*0.01
    gdf_area['AREA_PERCENT'] = (gdf_area['AREA_KM2']/area_dane)*100
    gdf_area['APTITUD_LABEL'] = gdf_area['APTITUD'].map(dict_aptitud_label)
    gdf_area['COLOR'] = gdf_area['APTITUD'].map(dict_aptitud_color)

    return gdf_area

def get_df_topDptoMpio(gdf_openDataDpto: gpd.GeoDataFrame, gdf_DaneDptoMpio: gpd.GeoDataFrame) -> pd.DataFrame:

    gdf_openDataDpto = gdf_openDataDpto[gdf_openDataDpto['APTITUD'] == 4]

    df_topDptoMpio = gdf_openDataDpto.groupby(['MPIO_CODE', 'MUNICIPIO'], as_index=False)['AREA_HECTAREAS'].sum()
    df_topDptoMpio['AREA_KM2'] = df_topDptoMpio['AREA_HECTAREAS']*0.01
    df_topDptoMpio = df_topDptoMpio.sort_values(by='AREA_KM2', ascending=False)
    df_topDptoMpio.reset_index(drop=True, inplace=True)
    df_topDptoMpio['MPIO_AREA'] = None

    for index, row in df_topDptoMpio.iterrows():
        mpio_code = row['MPIO_CODE']
        df_topDptoMpio.loc[index, 'MPIO_AREA'] = gdf_DaneDptoMpio[gdf_DaneDptoMpio['MPIO_CODE'] == mpio_code]['MPIO_AREA'].iloc[0]

    df_topDptoMpio['AREA_PERCENT'] = (df_topDptoMpio['AREA_KM2']/df_topDptoMpio['MPIO_AREA'])*100

    return df_topDptoMpio

def plot_hbar(df: pd.DataFrame, col_y: str, col_x: str, title: str, xlabel: str, color: str):

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.barh(df[col_y], df[col_x], color=color)
    ax.set_xlabel(xlabel)
    ax.set_title(title)

    for bar in bars:
        width = bar.get_width()  # Obtiene el valor de la barra
        ax.text(width + 0.5, bar.get_y() + bar.get_height() / 2,
                f'{round(width, 1)}', ha='center', va='center')


    st.pyplot(fig)

    return
