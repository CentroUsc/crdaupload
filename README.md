# `upload_rinex.py`

Este script permite subir archivos **RINEX** desde un directorio local a los servidores de **CRDASIR** (Centro Regional de Datos Alternos SIRGAS) de manera automatizada y asincrónica.

## 🚀 Requisitos

- Python 3.8 o superior
- Conexión a internet
- Credenciales válidas de acceso

## 🛠 Instalación

Clona el repositorio o descarcárgalo en tu directorio local. Realiza la instalación básica o con entorno virtual.


### Instalación básica
1. Instalar dependencias, desde la carpeta donde se encuentra el script:
   ```bash
   pip install -r requeriments.txt
   ```





### Instalación con entorno virtual 

1. Crea un entorno virtual (opcional pero recomendado)

Es una buena práctica utilizar un entorno virtual para gestionar las dependenciasto. Para crear un entorno virtual, ejecuta los siguientes comandos:

```bash
# Crear un entorno virtual en la carpeta 'venv'
python -m venv venv
```
Activa el entorno virtual en Windows
```bash
venv\Scripts\activate
```
Activa el entorno virtual en MacOS/Linux
```bash

source venv/bin/activate
```

2. Instala las dependencias
   ```bash
   pip install -r requeriments.txt
   ```

## Modo de uso

python upload_rinex.py -d ./rinex_data/

