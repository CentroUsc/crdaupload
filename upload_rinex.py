#!/usr/bin/env python # [1]



__author__ = "Juan Giglio"
__copyright__ = "Copyright 2024, ADELA Project"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Juan Giglio"
__email__ = "juan.giglio@usach.cl"
__status__ = "Production"

"""
Este script permite subir archivos RINEX desde un directorio local a los servidores de CRDASIR (Centro Regional de Datos Alternos SIRGAS).

Modo de uso:

python upload_rinex.py -d <directorio>

Instalación:

Después de instalar python y pip:

pip install -r requeriments.txt
"""


from getpass import getpass
import requests
import json
import argparse
from pathlib import Path
import datetime

parser = argparse.ArgumentParser(
                    prog='upload_rinex',
                    description='Este script permite subir archivos RINEX desde un directorio local a los servidores de CRDASIR (Centro Regional de Datos Alternos SIRGAS)',
                    epilog='Modo de uso')

parser.add_argument('-d',dest='directory',help='directorio donde se encuentran los archivos',required=True)

args = parser.parse_args()

p=Path(args.directory)


if not p.exists():
    print("directorio "+str(p)+" no existe")
    exit(1)

if not p.is_dir():
    print(str(p)+" no es un directorio")
    exit(1)



username=input("Usuario:")
password = getpass()

# Get token
session=requests.Session()
payload = "grant_type=&username="+username+"&password="+password+"&scope=&client_id=&client_secret="
headers= {
    "accept" : "application/json",
    "content-type": 'application/x-www-form-urlencoded'
}
try:
    response=session.post('https://api.geodesychile.usach.cl/token',headers=headers,data=payload)
except requests.exceptions.ConnectionError as e:
    print("Error de conexión")
    exit(1)
except Exception as e:
    print(e)
    exit(1)

j=json.loads(response.content)

if response.status_code==200:
    print("Autenticación OK")
    access_token = j["access_token"]
    headers= {
        "Authorization" : f'Bearer {access_token}'
    }
    session.headers.update(headers)
    print("Iniciando subida de archivos ",datetime.datetime.now())
    for path in p.glob("**/*"):
        print(path,'\t',path.stat().st_size,end='')
        if path.suffix in ['.Z','.gz']:
            with open(path, 'rb') as f:
                files = {
                    'in_file': f,
                }
                try:
                    response=session.post('https://api.geodesychile.usach.cl/upload/rinex',files=files)
                    if response.status_code==200:
                        j=json.loads(response.content)#.decode('utf-8'))
                        print("\t"+j["station"]+ "\t" +j["year"] +"\t"+ j["doy"] +"\t"+ str(response.elapsed) +"\t"+ "OK")
                except Exception as e:
                    print(e)
        else:
            print("\t\tomitido")

    print("Finalizando subida de archivos",datetime.datetime.now())

elif response.status_code==401:
    print("Usuario o password incorrecto")
else:
    print("Error:",vars(response))







