# -*- coding: utf-8 -*-
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import streamlit as st
import yaml,  warnings

from shapely.geometry import Point

warnings.filterwarnings("ignore", message=".*non conformant file extension.*")

font = {
    'url': "https://fonts.googleapis.com/css2?family=Mansalva&display=swap",
    'font_family': "Mansalva"
}

def str2bool(flag_gcs):

    boolean = False

    if flag_gcs == "True":
        boolean = True

    return boolean

def readFileGoogleCloudStorage(flag_gcs, fs, BUCKET_NAME, file_path, file_type, sheet_name):

    file = None

    if flag_gcs:
        gcs_path = f"gs://{BUCKET_NAME}/{file_path}"
        file = None

        with fs.open(gcs_path, "rb") as f:
            if file_type == 'xlsx':
                file = pd.read_excel(f, sheet_name=sheet_name)
            elif file_type == 'gpkg':
                file = gpd.read_file(f)

    else:
        if file_type == 'xlsx':
            file = pd.read_excel(file_path, sheet_name=sheet_name)
        elif file_type == 'gpkg':
            file = gpd.read_file(file_path)

    return file

def get_str_GoogleFonts():

    custom_font = f"""
    <style>
    @import url({font['url']});
    .custom-font {{
        font-family: '{font['font_family']}', sans-serif;
    }}
    </style>
    """

    return custom_font

def get_dict_customFont(body):

    return {
        'body': f"<h1 class='custom-font'>{body}</h1>",
        'unsafe_allow_html': True
    }

def get_dicts_aptitude(dict_aptitude: dict):

    dict_aptitudeLabel, dict_aptitudeColor, dict_aptitudeEmojin = {}, {}, {}

    for key, value in dict_aptitude.items():
        dict_aptitudeLabel[key] = value['label']
        dict_aptitudeColor[key] = value['color']
        dict_aptitudeEmojin[key] = value['emojin']
        
    return dict_aptitudeLabel, dict_aptitudeColor, dict_aptitudeEmojin

def get_str_markdownLabelAptitude(dict_aptitudeValue: dict) -> str:

    return f"**{dict_aptitudeValue['emojin']} <span style='color: {dict_aptitudeValue['color']};'>{dict_aptitudeValue['label']}</span>**: {dict_aptitudeValue['description']}"

def get_list_markdownLabelAptitude(dict_aptitude: dict) -> list:

    return [get_str_markdownLabelAptitude(dict_aptitude[4-i]) for i in range(0,len(dict_aptitude),1)]

def get_datasets_names():
    dict_product, list_product, list_nameDatasets, list_emojiProduct = {}, [], [], []

    with open('dicts/datasets_names.yaml', 'r') as archivo:
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

def get_list_dpto(dict_dptoNameCode):

    return [key for key in dict_dptoNameCode]

def get_dict_Mpio_MpioCode(gdf_openDataDpto: pd.DataFrame) -> dict:

    dict_Mpio_MpioCode = {}

    gdf_openDataDpto['NUM_DATA'] = 1
    gdf_openDataDpto = gdf_openDataDpto.groupby(['MPIO_CODE', 'MUNICIPIO'], as_index=False)['NUM_DATA'].sum()

    for _, row in gdf_openDataDpto.iterrows():
        dict_Mpio_MpioCode[row['MUNICIPIO']] = row['MPIO_CODE']

    return dict_Mpio_MpioCode

def get_gdf_DaneCountryDpto(flag_gcs, fs, BUCKET_NAME):

    file_path = 'datasets/geoportal_DANE/MGN_ADM_DPTO_POLITICO.gpkg'
    gdf_DaneCountryDpto = readFileGoogleCloudStorage(flag_gcs, fs, BUCKET_NAME, file_path, 'gpkg', None)

    return gdf_DaneCountryDpto

def get_polygonDane(gdf_Dane: gpd.GeoDataFrame, latitude: float, longitude: float) -> gpd.GeoDataFrame:

    point = Point(longitude, latitude)
    gdf_polygon = gdf_Dane[gdf_Dane['geometry'].contains(point)]

    return gdf_polygon

def get_gdf_DaneDpto(flag_gcs, fs, BUCKET_NAME, dpto_code) -> gpd.GeoDataFrame:

    gdf_DaneDpto = get_gdf_DaneCountryDpto(flag_gcs, fs, BUCKET_NAME)
    gdf_DaneDpto = gdf_DaneDpto[gdf_DaneDpto['DPTO_CODE'] == dpto_code]

    return gdf_DaneDpto

def get_gdf_DaneDptoMpio(flag_gcs, fs, BUCKET_NAME, dpto_code)-> gpd.GeoDataFrame:

    file_path = 'datasets/geoportal_DANE/MGN_ADM_MPIO_GRAFICO.gpkg'
    gdf_DaneDptoMpio = readFileGoogleCloudStorage(flag_gcs, fs, BUCKET_NAME, file_path, 'gpkg', None)
    gdf_DaneDptoMpio = gdf_DaneDptoMpio[gdf_DaneDptoMpio['DPTO_CODE'] == dpto_code]

    return gdf_DaneDptoMpio

def get_gdf_DaneDptoMpio2(flag_gcs, fs, BUCKET_NAME, dpto_code, dpto_name):

    file_path = f'datasets/geoportal_DANE/MGN_ADM_DPTO_MPIO_POLITICO/DPTO_{dpto_name}_{dpto_code}.gpkg'
    gdf_DaneDptoMpio = readFileGoogleCloudStorage(flag_gcs, fs, BUCKET_NAME, file_path, 'gpkg', None)

    return gdf_DaneDptoMpio

def get_gdf_DaneMpio(flag_gcs:bool, fs, BUCKET_NAME, dpto_code: int, mpio_code: int) -> gpd.GeoDataFrame:

    file_path = 'datasets/geoportal_DANE/MGN_ADM_MPIO_GRAFICO.gpkg'

   
    gdf_DaneMpio = readFileGoogleCloudStorage(flag_gcs, fs, BUCKET_NAME, file_path, 'gpkg', None)
    
    gdf_DaneMpio = gdf_DaneMpio[gdf_DaneMpio['DPTO_CODE'] == dpto_code]
    gdf_DaneMpio = gdf_DaneMpio[gdf_DaneMpio['MPIO_CODE'] == mpio_code]
    gdf_DaneMpio["CENTROID"] = gdf_DaneMpio.centroid

    return gdf_DaneMpio

def get_gdf_openDataDpto(flag_gcs: bool, fs, BUCKET_NAME, nameDataset: str, nameDpto) -> gpd.GeoDataFrame:

    file_path = f'datasets/datos_abiertos/{nameDpto}/{nameDataset}.gpkg'

    if flag_gcs:
        gdf_openDataDpto = readFileGoogleCloudStorage(flag_gcs, fs, BUCKET_NAME, file_path, 'gpkg', None)
    else:
        gdf_openDataDpto = gpd.read_file(file_path)

    return gdf_openDataDpto

def get_gdf_openDataMpio(gdf_openDataDpto: gpd.GeoDataFrame, mpio_code: int)-> gpd.GeoDataFrame:

    gdf_openDataMpio = gdf_openDataDpto[gdf_openDataDpto['MPIO_CODE'] == mpio_code]

    return gdf_openDataMpio

def get_gdf_areaDane(gdf_dane: gpd.GeoDataFrame, column_dane_area: str) -> float:

    return gdf_dane[column_dane_area].iloc[0]

def get_df_areaOpenDataDpto(gdf_openData: gpd.GeoDataFrame, gdf_dane: gpd.GeoDataFrame, column_dane_area: str, dict_aptitudeLabel: dict, dict_aptitudeColor: dict) -> pd.DataFrame:

    area_dane = get_gdf_areaDane(gdf_dane, column_dane_area)

    gdf_area = gdf_openData.groupby('APTITUD')['AREA_HECTAREAS'].sum().reset_index()
    gdf_area['AREA_KM2'] = gdf_area['AREA_HECTAREAS']*0.01
    gdf_area['AREA_PERCENT'] = (gdf_area['AREA_KM2']/area_dane)*100
    gdf_area['APTITUD_LABEL'] = gdf_area['APTITUD'].map(dict_aptitudeLabel)
    gdf_area['COLOR'] = gdf_area['APTITUD'].map(dict_aptitudeColor)

    return gdf_area

def get_df_aptitudeDptoMpio(gdf_openDataDpto: gpd.GeoDataFrame, gdf_DaneDptoMpio: gpd.GeoDataFrame, numaptitude: int) -> pd.DataFrame:

    gdf_openDataDpto = gdf_openDataDpto[gdf_openDataDpto['APTITUD'] == numaptitude]

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

def get_dict_aptitudLabelReversed(dict_aptitudLabel: dict) -> dict:

    dict_aptitudLabelReversed = {}

    for key in reversed(dict_aptitudLabel):
        dict_aptitudLabelReversed[dict_aptitudLabel[key]] = key

    return dict_aptitudLabelReversed

def get_list_labelSubTab(dict_aptitudLabelReversed: dict, dict_aptitudEmojin: dict) -> dict:

    return [f'{dict_aptitudEmojin[value]}**{key}**' for key, value in dict_aptitudLabelReversed.items()]
