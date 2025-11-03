import streamlit as st
import pandas as pd
import io
import os
import re

# ===============================
# 🔧 FUNCIONES
# ===============================

def leer_excel(archivo_excel):
    """
    Lee un archivo Excel (.xls o .xlsx) y devuelve un DataFrame de pandas.
    Detecta automáticamente el tipo y usa el motor adecuado.
    """
    try:
        nombre_archivo = archivo_excel.name.lower()

        if nombre_archivo.endswith(".xls"):
            # Para archivos antiguos de Excel (97-2003)
            df = pd.read_excel(archivo_excel, engine="xlrd")
        elif nombre_archivo.endswith(".xlsx"):
            # Para archivos modernos de Excel
            df = pd.read_excel(archivo_excel, engine="openpyxl")
        else:
            st.error("⚠️ Formato de archivo no compatible. Subí un .xls o .xlsx")
            return None

        return df

    except Exception as e:
        st.error(f"Error al leer el archivo Excel: {e}")
        return None


def limpiar_texto(valor):
    """
    Limpia el texto eliminando comillas dobles, espacios y reemplazando comas por puntos.
    """
    if isinstance(valor, str):
        valor = valor.replace('"', '')
        valor = valor.replace(',', '.')
        valor = re.sub(r"\s+", "", valor)
    return valor


def procesar_columnas(df, columnas):
    """
    Toma un DataFrame y una lista de índices de columnas.
    Devuelve un nuevo DataFrame con limpieza aplicada.
    """
    try:
        columnas_idx = [i - 1 for i in columnas]
        df_seleccion = df.iloc[:, columnas_idx].copy()
        df_limpio = df_seleccion.applymap(limpiar_texto)
        return df_limpio

    except Exception as e:
        st.error(f"Error al procesar las columnas: {e}")
        return None


def convertir_a_csv(df, nombre_original):
    """
    Convierte un DataFrame a CSV (separado por ';') y devuelve los bytes.
    """
    try:
        nombre_salida = os.path.splitext(nombre_original)[0] + "-procesado.csv"
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, sep=';', index=False)
        csv_bytes = csv_buffer.getvalue().encode('utf-8')
        return nombre_salida, csv_bytes

    except Exception as e:
        st.error(f"Error al convertir a CSV: {e}")
        return None, None


# ===============================
# 🚀 MAIN APP (Streamlit)
# ===============================

def main():
    st.title("📊 Conversor Excel a CSV con limpieza avanzada")
    st.write("""
    Subí un archivo Excel (.xls o .xlsx), elegí las columnas que querés procesar, 
    y descargá el resultado en formato CSV separado por punto y coma (;).
    
    🔹 El programa eliminará comillas dobles, espacios y cambiará comas (,) por puntos (.).
    """)

    archivo_excel = st.file_uploader("Subí tu archivo Excel (.xlsx o .xls)", type=["xlsx", "xls"])

    if archivo_excel:
        df = leer_excel(archivo_excel)
        if df is not None:
            st.write("Vista previa del archivo:")
            st.dataframe(df.head())

            st.write("Seleccioná las columnas que querés incluir (1 a máximo 15):")
            columnas_str = st.text_input("Ejemplo: 1,2,5,6")

            if columnas_str:
                try:
                    columnas = [int(x.strip()) for x in columnas_str.split(",") if x.strip().isdigit()]

                    if any(i < 1 or i > len(df.columns) for i in columnas):
                        st.warning("⚠️ Ingresaste columnas fuera del rango válido.")
                    else:
                        if st.button("Procesar archivo"):
                            df_procesado = procesar_columnas(df, columnas)
                            if df_procesado is not None:
                                nombre_csv, csv_bytes = convertir_a_csv(df_procesado, archivo_excel.name)
                                if csv_bytes:
                                    st.success("✅ Archivo procesado correctamente.")
                                    st.download_button(
                                        label="⬇️ Descargar CSV procesado",
                                        data=csv_bytes,
                                        file_name=nombre_csv,
                                        mime="text/csv"
                                    )
                except ValueError:
                    st.error("Por favor, ingresá solo números separados por comas.")


# Ejecutar aplicación
if __name__ == "__main__":
    main()