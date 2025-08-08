import geopandas as gpd
import pandas as pd
import streamlit as st
import plotly.express as px

font = {
    "url": "https://fonts.googleapis.com/css2?family=Mansalva&display=swap",
    "font_family": "Mansalva"
}

#%% FONTS

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

#%% CF_R2

def get_file_name_cf_r2(dpto_name: str, dpto_code: int, partial_name: str):

    return f"datasets-agrosmart/{dpto_name}/{dpto_code}-{partial_name}"

def get_path_dpto_item(dpto_name: str, dpto_code: int, partial_name: str):

    return f"datasets-agrosmart/{dpto_name}/{dpto_code}-{partial_name}"

def open_dataset_dpto_item(r2_fs, path_dpto_item: str, aptitude_select: list, aptitude_color: dict, aptitude_label: dict) -> gpd.GeoDataFrame:

    gdf_dpto_item = None

    with r2_fs.open(path_dpto_item, "rb") as f:
        gdf_dpto_item = gpd.read_parquet(f)
        gdf_dpto_item["COLOR"] = gdf_dpto_item["APTITUD"].replace(aptitude_color)
        gdf_dpto_item["LABEL"] = gdf_dpto_item["APTITUD"].replace(aptitude_label)

    if gdf_dpto_item is not None and len(aptitude_select) < 5:
        gdf_dpto_item = gdf_dpto_item[gdf_dpto_item["APTITUD"].isin(aptitude_select)]

    return gdf_dpto_item

#%% datasets_DANE

def get_gdf_dane_dpto(dpto_code) -> gpd.GeoDataFrame:

    gdf_dane_dpto = gpd.read_file("assets/geoportal_DANE/MGN_ADM_DPTO_POLITICO.gpkg")
    gdf_dane_dpto = gdf_dane_dpto[gdf_dane_dpto["DPTO_CODE"] == dpto_code]
    gdf_dane_dpto = gdf_dane_dpto.to_crs(epsg=3116)

    return gdf_dane_dpto

def get_gdf_dane_dpto_mpio(dpto_code) -> gpd.GeoDataFrame:

    gdf_dane_dpto_mpio = gpd.read_file("assets/geoportal_DANE/MGN_ADM_MPIO_GRAFICO.gpkg")
    gdf_dane_dpto_mpio = gdf_dane_dpto_mpio[gdf_dane_dpto_mpio["DPTO_CODE"] == dpto_code]
    gdf_dane_dpto_mpio = gdf_dane_dpto_mpio.to_crs(epsg=3116)

    return gdf_dane_dpto_mpio

#%% Tools

def get_gdf_unique_legend(gdf_dpto_item: gpd.GeoDataFrame) -> gpd.GeoDataFrame:

    gdf_unique_legend = gdf_dpto_item.drop_duplicates(subset=["COLOR", "LABEL"])

    return gdf_unique_legend

def get_df_info_dpto(gdf_dpto_item: gpd.GeoDataFrame, dict_aptitude_label: dict, dict_aptitude_color: dict, area_dpto: float) -> pd.DataFrame:

    df_info_dpto = gdf_dpto_item.groupby("APTITUD")["AREA_HECTAREAS"].sum().reset_index()
    df_info_dpto["AREA_KM2"] = df_info_dpto["AREA_HECTAREAS"]*0.01
    df_info_dpto["AREA_PERCENT"] = (df_info_dpto["AREA_KM2"]/area_dpto)*100
    df_info_dpto["APTITUD_LABEL"] = df_info_dpto["APTITUD"].map(dict_aptitude_label)
    df_info_dpto["COLOR"] = df_info_dpto["APTITUD"].map(dict_aptitude_color)

    diff_area = area_dpto - df_info_dpto["AREA_KM2"].sum()

    if diff_area < area_dpto:
        new_row = {
            "APTITUD": 99,
            "AREA_HECTAREAS": diff_area/10,
            "AREA_KM2": diff_area,
            "AREA_PERCENT": (diff_area/area_dpto)*100,
            "APTITUD_LABEL": "⚪ No clasificado",
            "COLOR": "#D3D3D3"
        }

        df_info_dpto.loc[len(df_info_dpto)] = new_row

    return df_info_dpto

def get_df_result_dpto_mpio(gdf_dpto_item: gpd.GeoDataFrame, gdf_dane_dpto_mpio: gpd.GeoDataFrame, dict_code_mpio: dict, aptitude: int) -> tuple[pd.DataFrame, pd.DataFrame]:

    gdf_dpto_item_aptitude: gpd.GeoDataFrame = gdf_dpto_item[gdf_dpto_item["APTITUD"] == aptitude]

    df_result_dpto_mpio: pd.DataFrame = gdf_dpto_item_aptitude.groupby(["MPIO_CODE"], as_index=False)["AREA_HECTAREAS"].sum()
    df_result_dpto_mpio["AREA_KM2"] = df_result_dpto_mpio["AREA_HECTAREAS"]*0.01
    df_result_dpto_mpio["MUNICIPIO"] = df_result_dpto_mpio["MPIO_CODE"].replace(dict_code_mpio)
    df_result_dpto_mpio.reset_index(drop=True, inplace=True)

    df_result_dpto_mpio = df_result_dpto_mpio.merge(gdf_dane_dpto_mpio[["MPIO_CODE", "MPIO_AREA"]], on="MPIO_CODE", how="left")
    df_result_dpto_mpio["AREA_PERCENT"] = (df_result_dpto_mpio["AREA_KM2"]/df_result_dpto_mpio["MPIO_AREA"])*100

    df_km2_dpto_mpio = get_df_column_dpto_mpio(df_result_dpto_mpio, "AREA_KM2")
    df_percent_dpto_mpio = get_df_column_dpto_mpio(df_result_dpto_mpio, "AREA_PERCENT")

    return df_km2_dpto_mpio, df_percent_dpto_mpio

def get_df_column_dpto_mpio(df_result_dpto_mpio: pd.DataFrame, column: str) -> pd.DataFrame:

    df_column_dpto_mpio = df_result_dpto_mpio.sort_values(by=column, ascending=False)
    df_column_dpto_mpio.reset_index(drop=True, inplace=True)
    df_column_dpto_mpio = df_column_dpto_mpio[["MPIO_CODE", "MUNICIPIO", "MPIO_AREA", "AREA_HECTAREAS", "AREA_KM2", "AREA_PERCENT"]]

    return df_column_dpto_mpio

#%% potly

def get_bar_chart_top_dpto_mpio(df_column_dpto_mpio: pd.DataFrame, column: str, column_label: str, top: int, color_aptitude: str, title: str):

    fig = px.bar(
         df_column_dpto_mpio,
         x=column,
         y="MUNICIPIO",
         orientation="h",
         labels={"MUNICIPIO": "Municipio", column: column_label},
         color_discrete_sequence=[color_aptitude]
    )

    fig.update_yaxes(autorange="reversed")

    fig.update_layout(
        title={
            "text": title,
            "x": 0.5,
            "xanchor": "center"
        },
        title_font_size=16
    )
                            
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"modeBarButtonsToRemove": ["zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d", "zoom2d", "pan2d", "select2d", "lasso2d"],
                "displaylogo": False
                }
    )

    return


