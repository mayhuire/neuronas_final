import requests
import json
import os
import re

class APIEconomia:
    def __init__(self):
        self.base_url = "https://api.worldbank.org/v2"

    def validar_codigo(self, codigo):
        """
        Valida que el código del indicador tenga el formato correcto.
        """
        patron = r'^[A-Z]{2}\.[A-Z]+\.[A-Z]+$'

        if not re.match(patron, codigo):
            raise ValueError(f"Código de indicador inválido: {codigo}")
        
    def obtener_datos(self, pais, indicador, anio_inicio=2000, anio_fin=2023):
        """
        Obtiene los datos desde la API del Banco Mundial.
        """
        self.validar_codigo(indicador)

        url = (
            f"{self.base_url}/country/{pais}/indicator/{indicador}"
            f"?format=json&date={anio_inicio}:{anio_fin}&per_page=100"
        )

        try:
            respuesta = requests.get(url, timeout=10)
            respuesta.raise_for_status()
            datos_json = respuesta.json()

            if not datos_json or len(datos_json) < 2:
                return []

            lista_datos = []

            for dato in datos_json[1]:
                if dato["value"] is None:
                    continue

                lista_datos.append({
                    "pais": dato["country"]["value"],
                    "indicador": dato["indicator"]["value"],
                    "anio": dato["date"],
                    "valor": dato["value"]
                })

            return lista_datos

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al conectar con la API: {e}")
        
    def guardar_json(self, datos, nombre_archivo):
        """
        Guarda los datos obtenidos en un archivo JSON.
        """

        carpeta = "data/crudo"

        os.makedirs(carpeta, exist_ok=True)

        ruta = os.path.join(carpeta, nombre_archivo)

        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=4)

        print(f"Archivo guardado en: {ruta}")
        
        return ruta