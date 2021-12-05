"""
Web-scraping de los datos de weather underground.
"""

import os
import sys
_path_script    = os.path.realpath(__file__) 
_path_script    = "/".join(_path_script.split("/")[:-1])
sys.path.append(_path_script + "/../")

import pathlib
import config
import pandas as pd
import datetime
import lib.libGOES     as GOES
import lib.libWU       as WU
import lib.f_generales as general

PATH_CSV_ESTACIONES = f"{_path_script}/../Recursos/EstacionesMetereológicas_WU.csv"
PATH_NSRDB_WU       = f"{_path_script}/Descargas/NSRDB/WU/"
PATH_GUARDADO       = f"{_path_script}/Descargas/WU/"

# Revisamos la existencia de los paths.
pathlib.Path(PATH_NSRDB_WU).mkdir(parents=True,exist_ok=True)
pathlib.Path(PATH_GUARDADO).mkdir(parents=True,exist_ok=True)

# Cargamos la configurción de los días a descargar.
días_descarga = config.cargar_mask_temporal(retornar_datetime=True)

# Cargamos las estaciones metereológicas.
df_estaciones = pd.read_csv(PATH_CSV_ESTACIONES)

print("Iniciando descarga de los datos de Weather Underground...")
for index,localidad in df_estaciones.iterrows():
    lista_datasets = []

    # Obtenemos los datos de la estación.
    nombre_estación = localidad["Estación"]

    print(f"Descargando datos de {nombre_estación}...")
    for fecha in días_descarga:
        print(fecha)
        # Obtenemos los datos de fecha.
        día , mes  , año = fecha.day , fecha.month , config.AÑO_DATOS

        # Descargamos los datos.
        try:
            df_dataset = WU.obtenerDatos_WU(nombre_estación,día,mes,año)
        except Exception as error:
            print("Error en la descarga, pasando al siguiente conjunto de datos...")
            print(error)
            continue

        # Añadimos todos los datos a una sola lista para concatenerlos despues.
        lista_datasets.append(df_dataset)
    
    # Unimos los datasets recolectados.
    try:
        df_estación_datos = pd.concat(lista_datasets,ignore_index=True)
    except:
        print(f"No se encontrarón datos válidos para la estación: {nombre_estación}.")
        continue
    
    # Guardamos los datos de esa estaciones.
    df_estación_datos.to_csv(PATH_GUARDADO + nombre_estación + ".csv")





