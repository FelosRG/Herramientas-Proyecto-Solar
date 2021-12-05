import re
import time
import datetime
import requests
import numpy  as np
import pandas as pd


from pathlib  import Path
from dateutil import parser, rrule
from bs4   import BeautifulSoup as BS

import lib.libNSRDB    as NSRDB
import lib.f_generales as Misc


def obtenerDatos_WU(estación,día,mes,año):

    # --------------------------------------------
    # Obtenemos los datos de Weather Underground #
    # --------------------------------------------

    # Obtenemos el html
    día = str(día)
    mes = str(mes).zfill(2)
    url = f"https://www.wunderground.com/dashboard/pws/{estación}/table/{año}-{mes}-{día}/{año}-{mes}-{día}/daily"
    html  = requests.get(url).text
    soup  = BS(html,"lxml")

    # Adquiramos la tabla en formato ¿¿ JSON ??
    tabla    = soup.find_all("script")[9]
    json_txt = re.findall(">.+",str(tabla))[0][1:-9]

    # Obtenemos Solar Radiation High
    SR_H = re.findall("solarRadiationHigh&q;:[0-9]+\.*[0-9]*",json_txt)
    SR_H = [int(valor[22:]) for valor in SR_H]

    # Obtenemos el time-stamp
    T = re.findall("obsTimeUtc&q;:&q;[0-9-:T]+",json_txt)
    T = [t[17:] for t in T]

    # Algunas veces hay un dato extra de tiempo.
    if len(T) != len(SR_H):
        T = T[:-1]
    
    # Revisamos que las longitudes coincidan.
    if len(T) != len(SR_H):
        print(url)
        raise ValueError(f"No coincide longitudes {len(T)} {len(SR_H)}")
    # Pasamos los datos a datetime.
    T = [datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S") for t in T]

    # Devolvemos el dataframe.
    dic_df = {"datetime":T,"GHI":SR_H}
    return pd.DataFrame(dic_df)

def obtenerDatos_WU_sincronizar(estación,día,mes,año,path_NSRDB):
    """
    Descarga los datos metereológicos de una estación de Weather Undergroud,
    a la vez, descarga los datos del NSRDB, y se realiza una sincronización.
    Se devuelve un dataframe con los datos de ambas fuentes.

    El parámetro path_datos sirve para no tener que descargar los mismos datos siempre.
    """

    # --------------------------------------------
    # Obtenemos los datos de Weather Underground #
    # --------------------------------------------

    # Obtenemos el html
    día = str(día)
    mes = str(mes).zfill(2)
    url = f"https://www.wunderground.com/dashboard/pws/{estación}/table/{año}-{mes}-{día}/{año}-{mes}-{día}/daily"
    html  = requests.get(url).text
    soup  = BS(html,"lxml")

    # Adquiramos la tabla en formato ¿¿ JSON ??
    tabla    = soup.find_all("script")[9]
    json_txt = re.findall(">.+",str(tabla))[0][1:-9]

    # Obtenemos Solar Radiation High
    SR_H = re.findall("solarRadiationHigh&q;:[0-9]+\.*[0-9]*",json_txt)
    SR_H = [int(valor[22:]) for valor in SR_H]

    # Obtenemos el time-stamp
    T = re.findall("obsTimeUtc&q;:&q;[0-9-:T]+",json_txt)
    T = [t[17:] for t in T]

    # Algunas veces hay un dato extra de tiempo.
    if len(T) != len(SR_H):
        T = T[:-1]
    if len(T) != len(SR_H):
        print(url)
        raise ValueError(f"No coincide longitudes {len(T)} {len(SR_H)}")

    T = [datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S") for t in T]

    # Redondeamos a minutos y despues a 5 minutos
    for i in range(len(T)):
        s = T[i].second
        if s >= 30:
            dif   = 60 - s
            delta = datetime.timedelta(seconds=dif)
            T[i]  = T[i] + delta
    for i in range(len(T)):
        m        = T[i].minute
        sobrante = m%5
        if sobrante >= 3:
            T[i] = T[i] + datetime.timedelta(minutes=5-sobrante)
        else:
            T[i] = T[i] -  datetime.timedelta(minutes=sobrante)
    
    # Separamos la fecha
    Year   = [t.year   for t in T ]
    Month  = [t.month  for t in T ]
    Day    = [t.day    for t in T ]
    Hour   = [t.hour   for t in T ]
    Minute = [t.minute for t in T ]

    # Obtenemos la latitud y longitud del lugar.
    try:
        lat = float( re.findall("lat&q;:[0-9]+\.*[0-9]*" ,json_txt)[0][7:] )
        lon = float( re.findall("lon&q;:-[0-9]+\.*[0-9]*",json_txt)[0][7:] )
    # Si falla este paso es porque no hay datos disponibles para ese fecha en esa estación.
    except:
        raise ValueError("No se ha encontrado ningun dato durante el web scraping.")
    
    # -----------------------------
    # Descagamos datos del NSRDB. #
    # -----------------------------

    nombre = Misc.asignarNombreArchivo(lat=lat,lon=lon)
    if Path(path_NSRDB + nombre).is_file():
        df_data = pd.read_csv(path_NSRDB + nombre)
    else:
        columnas = ["Month","Day","Hour","Minute","Clearsky GHI","GHI","Fill Flag","Solar Zenith Angle"]
        # Nos aseguramos una descarga correcta.
        descarga_correcta = False
        while descarga_correcta == False:
            try:
                df_data  = NSRDB.getData(lat=lat,lon=lon,year=año,intervalo=5,UTC=True)
                descarga_correcta = True
            except:
                continue
        df_data  = df_data[columnas]
        df_data.to_csv(path_NSRDB + nombre)
    
    # -------------------------------------------------------------
    # Sincronizamos los datos del NSRDB y del Weather underground #
    # -------------------------------------------------------------

    # Hacemos match y generamos columna de radiación máxima.
    Max_GHI   = []
    GHI_NSRDB = []
    Zenit     = []
    for i in range(len(T)):
        df_data_F =   df_data[  df_data["Month" ] == T[i].month ]
        df_data_F = df_data_F[df_data_F["Day"   ] == T[i].day   ]
        df_data_F = df_data_F[df_data_F["Hour"  ] == T[i].hour  ]
        df_data_F = df_data_F[df_data_F["Minute"] == T[i].minute]
        # Obtenemos los valores de interes.
        try:
            Max_GHI.append(  df_data_F["Clearsky GHI"].values[0])
            GHI_NSRDB.append(df_data_F["GHI"].values[0])
            Zenit.append(    df_data_F["Solar Zenith Angle"].values[0])
        except:
            print(T[i])
    
    # Retornamos un dataset con el msismo estilo que los datos provenientes del NSRDB.
    dataset = {
        "Year"    : Year   , 
        "Month"   : Month  ,
        "Day"     : Day    ,
        "Hour"    : Hour   ,
        "Minute"  : Minute ,
        "DateTime": T      , # T lleva la información de datetime desde más arriba.
        "GHI"     : SR_H   ,
        "GHI_NSRDB"    : GHI_NSRDB ,
        "Clearsky GHI" : Max_GHI   ,
        "Solar Zenith Angle" : Zenit ,
    }
    df_dataset = pd.DataFrame(dataset)
    
    return df_dataset
    