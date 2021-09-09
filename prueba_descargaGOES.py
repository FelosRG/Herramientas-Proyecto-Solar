import lib.libGOES
import datetime
import netCDF4
import numpy as np

fecha_inicio = datetime.datetime(2020,1,1,17,0)
fecha_final  = datetime.datetime(2020,1,1,18,0)

lib.libGOES.descargaIntervaloGOES16(producto        = "ABI-L1b-RadC",
                                    datetime_inicio = fecha_inicio,
                                    datetime_final  = fecha_final,
                                    banda = 3 ,
                                    output_path = "NETCDF_DATA/")