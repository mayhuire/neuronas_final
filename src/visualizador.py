import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class VisualizadorEconomico:
    """
    Clase para la visualización de indicadores económicos procesados.
    Permite cargar datos en formato CSV y generar diferentes tipos de gráficos.
    """

    def __init__(self, ruta_csv: str, carpeta_salida: str = "output/"):
        """
        Constructor del visualizador económico.
        """
        self.ruta_csv = ruta_csv
        self.carpeta_salida = carpeta_salida
        self.df = None

        # Crea la carpeta de salida si no existe
        os.makedirs(self.carpeta_salida, exist_ok=True)

    def cargar_datos(self) -> pd.DataFrame:
        """
        Carga los datos del archivo CSV limpio en un DataFrame de pandas
        y realiza validaciones de integridad de los datos.
        """
        if not os.path.exists(self.ruta_csv):
            raise FileNotFoundError(f"Error: El archivo de datos no existe en la ruta: '{self.ruta_csv}'")

        try:
            self.df = pd.read_csv(self.ruta_csv)
        except Exception as e:
            raise ValueError(f"Error al leer el archivo CSV: {e}")

        if self.df.empty:
            raise ValueError("Error: El archivo CSV está vacío o no contiene filas de datos.")

        columnas_requeridas = ["pais", "indicador", "anio", "valor"]
        columnas_faltantes = [col for col in columnas_requeridas if col not in self.df.columns]
        if columnas_faltantes:
            raise ValueError(f"Error: Columnas requeridas no encontradas: {columnas_faltantes}")

        self.df["anio"] = pd.to_numeric(self.df["anio"], errors="coerce").astype("Int64")
        self.df["valor"] = pd.to_numeric(self.df["valor"], errors="coerce")

        print("--- Datos Cargados Exitosamente ---")
        return self.df

    def grafico_lineas(self, pais: str, indicador: str, anio_inicio: int = None, anio_fin: int = None) -> str:
        """
        Genera y guarda un gráfico de líneas para mostrar la evolución temporal de un indicador en un país.
        """
        if self.df is None or self.df.empty:
            raise ValueError("Error: No se han cargado datos. Ejecute primero 'cargar_datos()'.")

        df_filtrado = self.df[
            (self.df["pais"].str.lower() == pais.lower()) &
            (self.df["indicador"].str.contains(indicador, case=False, na=False))
        ]

        if df_filtrado.empty:
            raise ValueError(f"Error: No se encontraron datos para el país '{pais}' con el indicador '{indicador}'.")

        if anio_inicio is not None:
            df_filtrado = df_filtrado[df_filtrado["anio"] >= anio_inicio]
        if anio_fin is not None:
            df_filtrado = df_filtrado[df_filtrado["anio"] <= anio_fin]

        if df_filtrado.empty:
            raise ValueError(f"Error: El rango de años [{anio_inicio} - {anio_fin}] no contiene datos.")

        df_filtrado = df_filtrado.sort_values("anio")
        nombre_indicador_real = df_filtrado["indicador"].iloc[0]
        nombre_pais_real = df_filtrado["pais"].iloc[0]

        plt.figure(figsize=(10, 6))
        sns.set_theme(style="whitegrid")

        plt.plot(
            df_filtrado["anio"],
            df_filtrado["valor"],
            marker="o",
            linestyle="-",
            color="#0f4c81",
            linewidth=2.5,
            markersize=7,
            label=nombre_indicador_real
        )

        plt.title(f"Evolución de: {nombre_indicador_real}\nen {nombre_pais_real}", fontsize=13, fontweight="bold", pad=15)
        plt.xlabel("Año", fontsize=11)
        plt.ylabel("Valor", fontsize=11)

        anios_validos = df_filtrado["anio"].dropna().unique()
        plt.xticks(anios_validos, rotation=45)

        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend(loc="best")
        plt.tight_layout()

        nombre_archivo = f"lineas_{nombre_pais_real.lower().replace(' ', '_')}_{indicador.lower().replace(' ', '_')}.png"
        nombre_archivo = "".join([c for c in nombre_archivo if c.isalnum() or c in ["_", ".", "-"]])
        ruta_salida = os.path.join(self.carpeta_salida, nombre_archivo)

        plt.savefig(ruta_salida, dpi=300)
        plt.close()
        return ruta_salida

    def grafico_barras(self, indicador: str, anio: int, top_n: int = None) -> str:
        """
        Genera y guarda un gráfico de barras comparativo entre países para un indicador y año específicos.

        Args:
            indicador (str): Nombre del indicador (búsqueda parcial, insensible a mayúsculas).
            anio (int): Año del indicador para la comparación.
            top_n (int, opcional): Si se define, limita a los top N países con mayores valores.

        Returns:
            str: Ruta del gráfico guardado en disco.
        """
        if self.df is None or self.df.empty:
            raise ValueError("Error: No se han cargado datos. Ejecute primero 'cargar_datos()'.")

        # Filtrar por indicador y año
        df_filtrado = self.df[
            (self.df["indicador"].str.contains(indicador, case=False, na=False)) &
            (self.df["anio"] == anio)
        ]

        # Validación: Filtro sin datos
        if df_filtrado.empty:
            raise ValueError(f"Error: No se encontraron datos para el indicador '{indicador}' en el año {anio}.")

        # Agrupar y ordenar datos
        df_agrupado = df_filtrado.groupby("pais")["valor"].mean().reset_index()
        df_agrupado = df_agrupado.sort_values("valor", ascending=False)

        if top_n is not None:
            df_agrupado = df_agrupado.head(top_n)

        nombre_indicador_real = df_filtrado["indicador"].iloc[0]

        plt.figure(figsize=(12, 6))
        sns.set_theme(style="whitegrid")

        # Paleta de colores degradada
        colores = sns.color_palette("mako", len(df_agrupado))

        bars = plt.bar(
            df_agrupado["pais"],
            df_agrupado["valor"],
            color=colores,
            edgecolor="gray",
            linewidth=0.7
        )

        plt.title(f"Comparativa por País: {nombre_indicador_real}\nAño: {anio}", fontsize=13, fontweight="bold", pad=15)
        plt.xlabel("País", fontsize=11)
        plt.ylabel("Valor", fontsize=11)
        plt.xticks(rotation=45, ha="right")

        # Añadir etiquetas de texto sobre las barras para mayor claridad
        for bar in bars:
            altura = bar.get_height()
            plt.annotate(
                f"{altura:.2f}",
                xy=(bar.get_x() + bar.get_width() / 2, altura),
                xytext=(0, 3),  # Desplazamiento vertical en puntos
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9
            )

        plt.grid(True, axis="y", linestyle="--", alpha=0.6)
        plt.tight_layout()

        nombre_archivo = f"barras_{indicador.lower().replace(' ', '_')}_{anio}.png"
        nombre_archivo = "".join([c for c in nombre_archivo if c.isalnum() or c in ["_", ".", "-"]])
        ruta_salida = os.path.join(self.carpeta_salida, nombre_archivo)

        plt.savefig(ruta_salida, dpi=300)
        plt.close()
        print(f"Gráfico de barras guardado en: {ruta_salida}")
        return ruta_salida
