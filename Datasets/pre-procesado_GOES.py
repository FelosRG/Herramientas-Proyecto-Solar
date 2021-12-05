#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Objetivo: Iterar sobre los datos descargados para hacerle el
pre-procesamiento.
"""
import os
import sys
_path_script    = os.path.realpath(__file__) 
_path_script    = "/".join(_path_script.split("/")[:-1])
sys.path.append(_path_script + "/../")

import time
import netCDF4
import h5py
import shutil
import numpy  as np
import pandas as pd
import lib.libGOES as GOES
from   pathlib import Path

import config
import lib.f_generales as general

# Cargamos configuración.
dias_descarga  = config.cargar_mask_temporal()
Lat, Lon, mask = config.cargar_mask_espacial()

def pre_procesado_GOES(banda):
    
    path_descarga = config.PATH_DESCARGA_GOES + str(banda)
    # Métricas
    num_datos = 0
    num_batch = 0
    batch_totales = len(dias_descarga)

    t_o = time.time()
    # Iteramos sobre un batch.
    for num_batch in range(len(dias_descarga)):
        path_batch   = path_descarga  +  "/Batch_" + str(num_batch).zfill(2) + "/"
        lista_netCDF = os.listdir(path_batch)
        lista_netCDF.sort()
        # Inicializamos listas de guardado.      
        datos_array = []
        datos_DQF   = []
        datos_t     = []
        # Iteramos sobre los archivos de ese batch.
        for archivo in lista_netCDF:
            # Abrimos netCDF y extraemos datos.
            nc = netCDF4.Dataset(path_batch + archivo)
            try:
                t = float(np.array(nc.variables["t"]))
            except:
                t = float(np.array(nc.variables["time"])[0])
            # Obtenemos los datos.
            array_datos = np.array(nc.variables[config.VARIABLE])
            array_DQF   = np.array(nc.variables["DQF"])

            # Iteramos sobre cada localidad.
            for i in range(config.RESOLUCIÓN):
                for j in range(config.RESOLUCIÓN):
                    lat , lon = Lat[i,j] , Lon[i,j]
                    if mask[i,j]:
                        # Recortamos.
                        px_y , px_x   = GOES.coordinates2px_GOES(nc , latitud=lat , longitud=lon)
                        array_datos_V = GOES.cortarYcentrar_GOES(array_datos,px_x,px_y,ventana=config.VENTANA_RECORTE)
                        array_DQF_V   = GOES.cortarYcentrar_GOES(array_DQF  ,px_x,px_y,ventana=config.VENTANA_RECORTE)
                        # Agregamos a la lista de guardado.
                        datos_array.append(np.array(array_datos_V).astype(np.int16))
                        datos_DQF.append(np.array(array_DQF_V).astype(np.int8))
                        datos_t.append(t)
                        # Métricas.
                        num_datos += 1
            # Cerramos netCDF
            nc.close()
        # Guardamos batch.
        nombre_batch = "Batch_" + str(num_batch).zfill(2) + ".h5"
        config.guardar_batch(datos_array,datos_DQF,datos_t,banda,nombre_batch,path=config.PATH_PREPROCESADO_GOES)
        num_batch += 1
        porcentaje = round((num_batch / batch_totales)*100,1)
        print(f"Num batch procesados: {num_batch} de {batch_totales} ({porcentaje}%)")
        print(f"Datos generados     : {num_datos}")
        # Obtenemos tiempo transcurrido
        t_f = time.time()
        t_trans = round((t_f-t_o)/60,1)
        print(f"Tiempo transcurrido {t_trans} min\n")
    print("Pre-procesado terminado!")

if __name__ == "__main__":
    texto = """ SCRIPT DE PREPROCESADO\n"""
    print(texto)
    print("Iniciando preprocesado de los datos descargados...")
    for banda in config.BANDAS:
        pre_procesado_GOES(banda)
