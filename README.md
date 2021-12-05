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

  El dataset generado se encontrará en la carpeta **Datasets/Datasets/** 
