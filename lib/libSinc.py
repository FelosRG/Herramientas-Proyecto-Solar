import os
import datetime
import numpy as np

def revisar_orden_temporal(lista_datetime):
    num_elementos = len(lista_datetime)
    for i in range(num_elementos-1):
        datetime_2 = lista_datetime[i+1]
        datetime_1 = lista_datetime[i]
        if (datetime_2 - datetime_1).total_seconds() < 0:
            raise ValueError("Orden temporal de la lista no respetado!")

class DatosTemporales:
    def __init__(self,lista_datos,lista_datetime):
        self.lista_datos    = lista_datos
        self.lista_datetime = lista_datetime
        if len(lista_datos) != len(lista_datetime):
            raise ValueError(f"Las listas de datos no tienen los mismos elementos: {len(lista_datos)} , {len(lista_datetime)}")
        self.num_datos = len(lista_datos)
        # Revisamos orden temporal.
        revisar_orden_temporal(self.lista_datetime)

class Sincronizador:
    def __init__(self,lista_DatosTemporales,verbose):
        self.lista_objetos = lista_DatosTemporales
        self.num_objetos = len(self.lista_objetos)
        # Creamos una lista con los indices de sincronización.
        self.indices_sincronizacion = np.array([0 for _ in range(self.num_objetos)])
        self.iteraciones = 0

    def _buscador(self,umbral):
        # Reunimos los datetimes de los índices.
        lista_datetime_sinc = [ self.lista_objetos[i].lista_datetime[self.indices_sincronizacion[i] ] for i in range(self.num_objetos) ]
        # Obtenemos el datetime más antiguo.
        fecha_mas_vieja = min(lista_datetime_sinc)
        # Obtenemos los desfaces.
        lista_desfaces = np.array([abs((fecha - fecha_mas_vieja).total_seconds()) for fecha in lista_datetime_sinc])
        indice_fecha_vieja = np.argmin(lista_desfaces)

        self.iteraciones += 1

        # Tomar en cuenta de programar para los index errors.

        # Comparamos los desfaces.
        if np.max(lista_desfaces) <= umbral:
            # Si los desfaces estan dentro del umbral retornamos y avanzamos indices.
            lista_indices = np.copy(self.indices_sincronizacion)
            self.indices_sincronizacion += 1
            return list(lista_indices)
        else:
            # Si no hacemos sincronización adelantamos un índice y hacemos recursión.
            self.indices_sincronizacion[indice_fecha_vieja] += 1
            return None

    def _sincronizar(self,umbral):
        lista_indice = None
        while type(lista_indice) == type(None):
            lista_indice = self._buscador(umbral)
        return lista_indice
            

    def generarSerieTiempo(self,umbral_sinc,umbral_serie=None,longitud=1):
        lista_series_tiempo = []
        # Obtenemos todos los momentos del sincronizador.
        lista_momentos = []
        while True:
            try:
                momento = self._sincronizar(umbral_sinc)
                lista_momentos.append(momento)
            except IndexError:
                break
        if longitud == 1:
            print(f"Iteraciones realizadas {self.iteraciones}")
            return lista_momentos
        else:
            raise NotImplementedError("Aun no creo el código para series de tiemmpo mayores a 1.")



        




