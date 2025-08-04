from enum import Enum
from typing import NamedTuple

class ItemMembers(NamedTuple):
    Name: str
    Description: str
    Email: str
    GitHub: str
    Phone: str
    Image: str

class Members(Enum):
    MEMBER0 = ItemMembers(
        Name="Darío Fernando Gonzalez Fontecha",
        Description="Comprometido con el desarrollo sostenible, energias renovables y la implementación de tecnologías innovadoras para el sector agropecuario. Con conocimientos en MATLAB, Python y desarrollo Web, oriento mis habilidades hacia el uso de Big Data y computación en la nube para transformar el campo colombiano.",
        Email="",
        GitHub="",
        Phone="+57 301 2350958",
        Image="assets/member0.jpg"
    )
    MEMBER1 = ItemMembers(
        Name="José Camilo Rojas Páez",
        Description="Mi compromiso hacia la sostenibilidad se traduce en proyectos de energías renovables destinados a mejorar el sector agropecuario. Con conocimientos en  MATLAB, Python, Streamlit y Power BI, que aplico al análisis y procesamiento de datos. ",
        Email="rojaspaezcamilo@gmail.com",
        GitHub="https://github.com/Himperion",
        Phone="+57 3015698321",
        Image="assets/member1.jpg"
    )

class DescriptiveText(Enum):
    TEXT0 = """
    Herramienta para la visualización del potencial agropecuario
    de los territorios, permitiendo análizar el rendimiento
    a nivel departamental o municipal según el tipo de cultivo o
    producción. \n
    Se cuenta con **7'333.610** datos en **33 conjuntos** de la **Unidad de Planificación Agropecuaria - UPRA**
    donde mide la aptitud agropecuaria del territorio nacional. También se usan datos abiertos del **geoportal DANE**
    para la división política de los departamentos, municipios y sus respectivas áreas territoriales.
    """