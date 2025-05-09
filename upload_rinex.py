#!/usr/bin/env python

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

Después de instalar python:

pip install -r requeriments.txt
"""

import logging
from getpass import getpass
import asyncio
import aiohttp
import argparse
from pathlib import Path
import datetime
import yaml
import sys
# Load configuration
with open('config.yml', 'r') as config_file:
    config = yaml.safe_load(config_file)

api_url = config['api_url']
token_url = config['token_url']
update_passwd_url = config['update_passwd_url']


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Argument parsing
parser = argparse.ArgumentParser(
    prog='upload_rinex',
    description='Este script permite subir archivos RINEX desde un directorio local a los servidores de CRDASIR (Centro Regional de Datos Alternos SIRGAS)',
    epilog='Modo de uso\n python rinex_upload.py -d <directorio> \n python rinex_upload.py --change-password'
)
parser.add_argument('-d', dest='directory', help='directorio donde se encuentran los archivos')
parser.add_argument('--change-password', action='store_true', help='Cambiar contraseña del usuario')
args = parser.parse_args()

async def get_token(session, token_url, username, password):
    payload = {
        "grant_type": "",
        "username": username,
        "password": password,
        "scope": "",
        "client_id": "",
        "client_secret": ""
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded"
    }
    async with session.post(token_url, headers=headers, data=payload) as response:
        if response.status == 200:
            logger.info("Autenticación OK")
            return await response.json()
        elif response.status == 401:
            logger.error("Usuario o password incorrecto")
            exit(1)
        else:
            logger.error("Error en la respuesta del servidor: %s", response.status)
            
        response.raise_for_status()
        exit(1)

async def upload_file(session, path, api_url):
    if path.suffix in ['.Z', '.gz']:
        with open(path, 'rb') as f:
            files = {'in_file': f}
            async with session.post(api_url, data=files) as response:
                if response.status == 200:
                    j = await response.json()
                    logger.info("OK: %s",path)
                elif response.status==409:
                    logger.info("OK*: %s",path)
                else:
                    try:
                        j = await response.json()
                        logger.error("Error archivo %s, %s", path,j['detail'] )
                    except Exception as e:
                        logger.error(str(e))
    else:
        logger.info("Archivo omitido: %s", path)


async def update_password(session,api_url):
    old_password = getpass("Password actual: ")
    new_password = getpass("Nuevo password: ")
    confirm_password = getpass("Confirmar nuevo password: ")

    if new_password != confirm_password:
        logger.error("Nuevo password no coincide.")
        return

    data = {
        "old_password": old_password,
        "new_password": new_password,
        "new_password2": confirm_password
    }
    async with session.put(f"{update_passwd_url}", json=data) as response:
        if response.status == 200:
            logger.info("Password updated successfully.")
        else:
            try:
                response_json = await response.json()
                logger.error(f"Error updating password: {response_json.get('detail')}")
            except Exception as e:
                logger.error(f"Error: {str(e)}")






async def main():

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    print("Upload RINEX CRDASIR %s"%(__version__))    
    username = input("Usuario:")
    password = getpass()
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        token_response = await get_token(session, token_url, username, password)
        access_token = token_response["access_token"]
        headers = {"Authorization": f'Bearer {access_token}'}
        session.headers.update(headers)
        
        # Actualiza password
        if args.change_password:
            await update_password(session, api_url)
            return  # salir después de cambiar la contraseña

        # Sube archivos
        p = Path(args.directory)
        if not p.exists():
            logger.error("Directorio %s no existe", str(p))
            exit(1)

        if not p.is_dir():
            logger.error("%s no es un directorio", str(p))
            exit(1)

        init_time=datetime.datetime.now()
        logger.info("Iniciando subida de archivos %s", init_time)
        tasks = [upload_file(session, path, api_url) for path in p.glob("**/*") if path.is_file()]
        await asyncio.gather(*tasks)
        end_time=datetime.datetime.now()
        logger.info("Finalizando subida de archivos %s", end_time)
        logger.info("Tiempo transcurrido %s",end_time-init_time)



if __name__ == '__main__':
    asyncio.run(main())
