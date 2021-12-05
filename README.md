# Herramientas para el manejo de datos satelitales y de radiación solar :earth_americas:

![alt text](https://github.com/FelosRG/Herramientas-Proyecto-Solar/blob/main/Figuras/portada_GOES16.jpg?raw=true)

<b> ! Nota para Adrián : Revisar que el código no contenga API-keys privadas antes de actualizar!</b> <br> <br>

## Contenido :writing_hand:

  - [Objetivos](#objetivos)
  - [Instalación de dependencias](#instalación-de-dependencias)
  - [Manual de generación de datasets](#manual-de-generación-de-datasets)

## Objetivos
En este repositorio están herramientas para la adquisición y manejo de datos satelitales provenientes del satélite GOES-16 y datos de radiación solar con el objetivo de la creación de datasets para el entrenamiento de modelos de inteligencia artificial para la predicción de la radiación solar. <br>

## Instalación de dependencias
**Se recomienda el uso de Anaconda (Python3)**<br>
Una vez clonado (o descargado) el repositorio, entramos en él y ejecutamos el siguiente comando con pip para instalar todas las dependencias requeridas:

Si se tiene anaconda
``` 
conda install requeriments.txt
```
Sin anaconda
``` 
pip3 install requeriments.txt
```
Después de instalar las dependencias es necesario conseguir una API-KEY del Nation Solar Radiation Database para la descarga de los datos de radiación solar en https://developer.nrel.gov/signup/

Una vez se tenga la API-KEY se necesita editar un par de campos en el script ubicado en **lib/libNSRDB.py** de la siguiente forma:
``` 
API_KEY = "abcdef12345"
EMAIL   = 'ejemplo@jemplo.com'
```
## Manual de generación de datasets
Es posible generar datasets con información de múltiples bandas y de radiación solar, para conseguir una dataset en la carpeta **Datasets/** están los siguientes scripts que deben de ser ejecutados en el siguiente orden

* **config.py**<br>
  En este script se colocan las configuración principales para la descarga de los datos satelitales y de radiación solar así un primer pre-procesado de los datos satelitales.<br>

  Tras su ejecución se creará un archivo **config.pickle** que contendrá  parte de las configuraciones realizadas.

  **Antes de su ejecución es necesario modificar los ajustes que se deseen**

* **descarga_GOES.py**<br>
  Descarga los datos satelitales según las configuraciones establecidas en **config.py** los archivos descargados se encontrarán en la carpeta **Datasets/Descargas/GOES/**

* **descarga_NSRDB.py**<br>
Descarga de los datos de radiación solar del National Solar Radiation Database (NSRDB) según las configuraciones establecidas en **config.py**

* **pre-procesado_GOES.py**<br>
  Realiza un primer procesado de los datos satelitales para facilitar los siguientes pasos.

* **separador_GOES.py**
  Clasifica los datos según las localizaciones, este es el paso final previo a la generación de el dataset.

* **gen_dataset.py**<br>
Antes de ejecutar este script se necesitan colocar las configuraciones deseadas como
  * Las bandas que se usarán en el dataset.
  * Tamaño de las imágenes satelitales alrededor de cada punto.
  * Si el dataset será de una serie de tiempo y de qué longitud será esta serie de tiempo.
  
  Una vez colocada estas configuraciones al principio del script se puede ejecutar el script.

  El dataset generado se encontrará en la carpeta **Datasets/Datasets/**  y tendrá como nombre las principales configuraciones realizadas por ejemplo:<br>

  **Ventana_5-Bandas_4_6_-Secuencia_1-Resolucion_5-NSRDB.h5**
  
  Que significa:
  * [Ventana] Las imágenes del dataset estan compuestas por imágenes de 5px de ventana (10x10 px de tamaño)
  * [Bandas] El datset contiene datos de la banda 4 y 6 del satélite GOES
  * [Secuecia] El dataset está compuesto por series de tiempo de 1 de longitud.
  * [Resolución] El grid con la que se dividió la región especificada fue de 5x5.
  * [NSRDB] Significa que los datos solares provienen del National Solar Radiation Database. (Proximamente quiero implementar otras fuentes de datos de radiación solar)

Notar que el dataset está en formato h5, que es posible abrir con la libería h5py, de la siguiente forma:

```python 
import h5py

# nombre ejemplo
nombre_dataset = Ventana_5-Bandas_4_6_-Secuencia_1-Resolucion_5-NSRDB.h5

# Para ver los nombre de las variables disponibles dentro del dataset
with h5py.File(nombre_dataset,"r") as dataset:
  print(dataset.keys())

# Para extaer los datos de una variable
with h5py.File(nombre_dataset,"r") as dataset:
  variable = dataset["nombre de la variable"][()]
```

Todas las variables se devuelven en numpy arrays <br><br>


## Tutorial de generación de dataset

En esta sección está que esperar del dataset generado y como  se puede usar.<br> Para ello vamos a correr el dataset en las siguientes configuraciones

**En config.py** <br>
Modificamos las siguintes configuraciones como:

```python
DÍAS = 1        # Para descargar solo un día del año de datos satélitales.
BANDAS = [4,13] # Pero puede ser cualquier otro par de bandas

# Descargaremos entre las horas de 7am a 7pm hora de méxico
HORA_INICIO_UTC , MIN_INICIO_UTC = 12 , 00
HORA_FINAL_UTC  , MIN_FINAL_UTC  = 23 , 59

# Dividimos a la región especificada en un grid 5x5, cada intersección del grid es un lugar de donde se generarán los datos del dataset.
RESOLUCIÓN = 5

VENTANA_RECORTE = 200

# Las otras configuraciones las dejamos como estan.
```

Guardamos config.py y ejecutamos los siguientes scripts en el siguiente orden:

* config.py
* descarga_GOES.py
* descarga_NSRDB.py
* pre-procesado.py
* separador.py

Despues modificamos las configuraciones en **gen_dataset.py**

```python
# El dataset estará conformado por información de las bandas 4 y 13
BANDAS  = [4,13]

# Utilizaremos los 200 pixeles de ventana de la ventana de recorte puesta en config.py
VENTANA = 200 

# Información de los datos del NSRDB que ocuparemos en la generación de nuestro dataset
DATOS_NSRDB = ["GHI","Solar Zenith Angle","Clearsky GHI"]

# Las otras configuraciones las dejamos como estan.
```

Guardamos y ejecutamos **gen_dataset.py**, una vez finalizado el procesado tendremos nuestro dataset en **Dasets/Datasets/** llamado<br>

**Ventana_200-Bandas_4_13-Secuencia_1-Resolucion_5-NSRDB.h5**

<br><br>

## Tutorial de visualización del dataset

Ya con el dataset generado movemos el dataset (o lo descargamos a nuestra computadora si se está trabajando en una computadora remota) a una carpeta aparte donde crearemos un script o notebook de python

Con los siguiente:

```python

import h5py
import matplotlib.pyplot as plt

nombre_dataset = "Ventana_200-Bandas_4_13-Secuencia_1-Resolucion_5-NSRDB.h5"
with h5py.File(nombre_dataset,"r") as dataset:
  GHI = dataset["GHI"][()]
  Banda_4 = dataset["4"][()]
  Banda_13 = dataset["13"][()]
 
```












