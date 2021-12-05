import os
import sys
_path_script    = os.path.realpath(__file__) 
_path_script    = "/".join(_path_script.split("/")[:-1])
sys.path.append(_path_script + "/../")

import time
import netCDF4
import h5py
import shutil
import lib.f_generales as general
import numpy  as np
import pandas as pd
import lib.libGOES as GOES
from   pathlib import Path

import config

# Cargando configuraciones.
Lat,Lon,mask  = config.cargar_mask_espacial()
días_descarga = config.cargar_mask_temporal()
batch_totales = len(días_descarga)

# Separamos las comunidades en chunks
lista_lat , lista_lon = [] , []
for i in range(config.RESOLUCIÓN):
    for j in range(config.RESOLUCIÓN):
        if mask[i,j]:
            lat = Lat[i,j]
            lon = Lon[i,j]
            lista_lat.append(lat)
            lista_lon.append(lon)
            
Lat , Lon       = np.array(lista_lat) , np.array(lista_lon)
coordenadas     = np.stack([Lat,Lon],axis=1)
num_comunidades = int(np.sum(mask))

def separador_GOES(banda):
    chunks_id          = np.array_split(np.arange(num_comunidades),config.NUM_LOCALIDADES_EN_CHUNK)
    chunks_comunidades = np.array_split(coordenadas,config.NUM_LOCALIDADES_EN_CHUNK)
    chunks_procesados  = 0
    tiempo_o = time.time()
    for chunk,chunk_ids in zip(chunks_comunidades,chunks_id):
        # Creamos lista con la estructura de datos.
        Lista_comunidades = [ [0,0,[],[],[]] for _ in range(len(chunk))]
        for num_batch in range(batch_totales):
            # Abrimos batch
            path_batch = f"{config.PATH_PREPROCESADO_GOES}{banda}/" + "Batch_" + str(num_batch).zfill(2) + ".h5"
            with h5py.File(path_batch,"r") as batch:
                Arrays = batch["Datos"][()]
                DQF    = batch["DQF"][()]
                T      = batch["T"][()]
            for i,id_comunidad,comunidad in zip(range(len(chunk)),chunk_ids , chunk):
                # Encontramos coordenadas de cada comunidad.
                lat , lon = comunidad[0],comunidad[1]
                Lista_comunidades[i][0] = lat
                Lista_comunidades[i][1] = lon
                # Separemos datos de esa comunidad y añadimos al chunk.
                Lista_comunidades[i][2] += list(Arrays[id_comunidad::num_comunidades])
                Lista_comunidades[i][3] += list(DQF[id_comunidad::num_comunidades])
                Lista_comunidades[i][4] += list(T[id_comunidad::num_comunidades])

        # FALTA IMPLEMENTAR EL GUARDADO DE CHUNKS!
        for comunidad in Lista_comunidades:
            lat , lon = comunidad[0] , comunidad[1]
            nombre_archivo = general.asignarNombreArchivo(lat=lat,lon=lon,extensión="h5")
            config.guardar_batch(
                comunidad[2]      ,
                comunidad[3]      ,
                comunidad[4]      ,
                banda             ,
                nombre_archivo                ,
                path=config.PATH_DATASET_GOES )
        chunks_procesados += 1
        print(f"Chunks procesados {chunks_procesados} de {config.NUM_LOCALIDADES_EN_CHUNK}")
        t = time.time()
        t = round((t-tiempo_o)/60 , 2)
        print(f"Tiempo transcurrido {t} min\n")
        
    print(f"Proceso terminado para la banda {banda}!")

if __name__ == "__main__":
    # Ordenamos los datos por localidad, se hará en chunks para hacer eficiente.
    print("Iniciando ordenamiento de los datos...")
    for banda in config.BANDAS:
        print(f"Ordenando banda {banda}...\n")
        separador_GOES(banda)