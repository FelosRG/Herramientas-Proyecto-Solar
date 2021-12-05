
# CONFIGURACIONES GENERALES
#--------------------------

# --> Año de los datos que conformarán el dataset. (Solo disponibles 2018,2019,2020)
AÑO_DATOS = 2020 

# CONFIGURACIONES DE LA DESCARGA DE DATOS SATÉLITALES
#----------------------------------------------------

 # --> Días del año del que se descargarán los datos. (12 valor recomendado)
DÍAS   = 1 #8
BANDAS = [4,13]  #[4,6,7,8,9,10,11,12,13,14,15,16]

# No meodificar estos
PRODUCTO = "ABI-L1b-RadC"
VARIABLE = "Rad"

# Horas  (e UTC) en las que se descargarán los datos. (12:00 UTC equivale a 7:00 am hora México.)
HORA_INICIO_UTC , MIN_INICIO_UTC = 15 , 00 #12 , 00
HORA_FINAL_UTC  , MIN_FINAL_UTC  = 16 , 00 #23 , 59

# CONFIGURACIÓN DE LA GENERACIÓN DE DATASETS
#-------------------------------------------:
RESOLUCIÓN      = 5#15   # --> Resolución del grid con el que se divirá méxico. (15 valor recomendado)
VENTANA_RECORTE = 200     # --> Tamaño de la ventana de recoorte alrededor del punto en el pre-procesado.

# Si hay problemas con la memoria ram subir este numero por ejemplo a 10.
NUM_LOCALIDADES_EN_CHUNK = 5

# --> Límites geográficos para la generación del grid espacial.
INF_LAT , SUP_LAT =   16.8 ,  24.3
INF_LON , SUP_LON = -110.8 , -93.1
# ----------------------------------------------------------------------------------------------------

import os
import sys
_path_script    = os.path.realpath(__file__) 
_path_script    = "/".join(_path_script.split("/")[:-1])
sys.path.append(_path_script + "/../")

import h5py
import pickle
import datetime
import numpy as np
from  pathlib import Path
import lib.f_generales as general

PATH_DESCARGA_GOES  = _path_script + "/Descargas/GOES/"
PATH_DESCARGA_NSRDB = _path_script + "/Descargas/NSRDB/"

PATH_PREPROCESADO_GOES = _path_script + "/Preprocesado_GOES/Temporal/"
PATH_DATASET_GOES      = _path_script + "/Preprocesado_GOES/"

PATH_SHAPEFILE = _path_script + "/../Recursos/Shapefiles/shape_file.shp"
PATH_CONFIG    = _path_script + "/Config"

PATH_DATASET_FINAL = _path_script + "/Datasets/"

fill_value = {
    1:1023,
    2:4095,
    3:1023,
    4:2047,
    5:1023,
    6:1023,
    7:16383,
    8:4095,
    9:2047,
    10:4095,
    11:4095,
    12:2047,
    13:4095,
    14:4095,
    15:4095,
    16:1023
    }

FLAGS_GOES = [2,3,4]

def cargar_mask_espacial():
    """
    Cargamos el mask espacial dada la pre-configuración.
    """
    try:
        with open(_path_script + "/config.pickle","rb") as file:
            dic_config = pickle.load(file)
    except FileNotFoundError:
        mensaje = "Se requiere ejecutar primero el script config.py primero."
        raise FileNotFoundError(mensaje)
    Lat = dic_config["Lat"]
    Lon = dic_config["Lon"]
    mask = dic_config["mask espacial"]
    return Lat , Lon , mask

def cargar_mask_temporal(retornar_datetime:bool=False):
    """
    Cargamos el mask temporal dada la pre-configuración.
    """
    try:
        with open(_path_script + "/config.pickle","rb") as file:
            dic_config = pickle.load(file)
    except FileNotFoundError:
        mensaje = "Se requiere ejecutar primero el script config.py primero."
        raise FileNotFoundError(mensaje)
    
    días_descarga = dic_config["mask temporal"]

    # Si parámetro retornar_datetime.
    if retornar_datetime:
        días_descarga_datetime = []
        for día in días_descarga:
            primer_día_año = datetime.datetime(AÑO_DATOS,1,1,0,0)
            delta_días     = datetime.timedelta(days=int(día))
            fecha          = primer_día_año + delta_días
            días_descarga_datetime.append(fecha)
        return días_descarga_datetime
    else:
        return días_descarga

def guardar_batch(datos_array,datos_DQF,datos_t,banda,nombre_batch,path):
    "Guarda un batch de datos al disco."
    path_output_dataset = f"{path}{banda}/"
    Path(path_output_dataset).mkdir(parents=True,exist_ok=True)

    with h5py.File(f"{path_output_dataset}{nombre_batch}", "w") as file:
        # Ajustamos los arrays.
        res = VENTANA_RECORTE
        datos_array = np.array(datos_array) #.reshape(-1,res,res).astype(np.uint16)
        datos_DQF   = np.array(datos_DQF  ) #.reshape(-1,res,res).astype(np.uint16)
        datos_t     = np.array(datos_t) #.astype(np.uint32)
        file.create_dataset("T"    ,data=datos_t    )
        file.create_dataset("Datos",data=datos_array)
        file.create_dataset("DQF"  ,data=datos_DQF  )



if __name__ == "__main__":

    print("SCRIPT DE PRE-CONFIGURACIÓN \n")

    # Generamos el mask espacial de los datos.
    print("Generando el mask espacial ...")

    Lon , Lat , Mask_espacial = general.generar_mask_espacial(
        INF_LAT=INF_LAT,
        SUP_LAT=SUP_LAT,
        INF_LON=INF_LON,
        SUP_LON=SUP_LON,
        RESOLUCIÓN=RESOLUCIÓN,
        PATH_SHAPEFILE=PATH_SHAPEFILE,
    )

    # Generamos el mask temporal de los datos
    print("Generando el mask temporal...")

    Mask_temporal = general.generar_dias_año(dias=DÍAS)
    
    # Guardamos los objetos generados por la configuración.
    print("Guardando la configuración...")

    dic_config = {
        "Lat"  : Lat ,
        "Lon"  : Lon ,
        "mask espacial" : Mask_espacial,
        "mask temporal" : Mask_temporal,
    }

    with open( _path_script + "/config.pickle","wb") as file:
        pickle.dump(dic_config,file)

    print("Script de pre-configuración terminado!")
