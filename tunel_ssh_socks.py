# TODO: hacer que se puedan crear multiples tuneles inversos y proxies socks y que se puedan cerrar individualmente.

import socket
import socks  # Asegúrate de haber instalado PySocks
# import socks  # Asegúrate de haber instalado PySocks
original_socket = socket.socket


def obtener_informacion_ip():
    import requests
    try:
        # Obtener la dirección IP y la información de ubicación
        respuesta_ip = requests.get('https://httpbin.org/ip')
        ip = respuesta_ip.json()['origin']

        # Usar ipinfo.io para obtener información detallada de la ubicación
        respuesta_geo = requests.get(f'https://ipinfo.io/{ip}/json')
        datos_geo = respuesta_geo.json()

        pais = datos_geo.get('country', 'No disponible')
        region = datos_geo.get('region', 'No disponible')
        ciudad = datos_geo.get('city', 'No disponible')

        return f"Dirección IP: {ip}\nPaís: {pais}\nRegión: {region}\nCiudad: {ciudad}"
    except Exception as e:
        return f"Error al obtener la información de la IP: {e}"
    




def crear_tunel_ssh(puerto_local, usuario, host_remoto, clave_ssh, puerto_remoto = 22):


    import subprocess

    # Comando para ejecutar el script con pm2
    cmd = f"pm2 start 'ssh -p {puerto_remoto} -i {clave_ssh} -N {usuario}@{host_remoto} -D {puerto_local}' --name tunel-ssh"
    subprocess.run(cmd, shell=True)
   


# crea el gestor de sockets SOCKS
def crear_proxy_socks(puerto_socks):
    # global original_socket

    try:
        # original_socket = socket.socket
        #  # Configura el proxy SOCKS: Configurar el extremo local del tunel SSH
        # local_bind_port = puertosocks
        remote_bind_address = ('localhost', puerto_socks)

        print(f"Configurando el proxy SOCKS en {remote_bind_address[0]}:{remote_bind_address[1]}...")
        # El argumento True al final indica que se resolverán los nombres de host de manera remota.
        socks.set_default_proxy(socks.SOCKS5, "localhost", puerto_socks, True) 
        socket.AF_INET = 2  # IPv4
        socket.socket = socks.socksocket
        # return socks.socksocket
                                
    except Exception as e:
        print(f"Error al establecer el proxy Socks: {e}")





def cerrar_tunel_ssh():
    import subprocess
    import socket

    # Restaurar el socket original
    socket.socket = original_socket

    # Comando para ejecutar el script con pm2
    cmd = f"pm2 delete tunel-ssh"
    subprocess.run(cmd, shell=True)