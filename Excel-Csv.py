import streamlit as st
import pandas as pd
import io
import os
import re

# ===============================
# 🔧 FUNCIONES
# ===============================

def leer_archivo_flexible(archivo):
    """
    Intenta leer un archivo Excel, CSV o texto plano sin depender solo de la extensión.
    """
    try:
        nombre = archivo.name.lower()

        # Intento 1: Excel moderno
        try:
            df = pd.read_excel(archivo, engine="openpyxl")
            return df
        except Exception:
            archivo.seek(0)

        # Intento 2: Excel viejo (.xls)
        try:
            df = pd.read_excel(archivo, engine="xlrd")
            return df
        except Exception:
            archivo.seek(0)

        # Intento 3: CSV con distintos separadores
        try:
            df = pd.read_csv(archivo, sep=";", encoding="utf-8", engine="python")
            return df
        except Exception:
            archivo.seek(0)

        try:
            df = pd.read_csv(archivo, sep=",", encoding="utf-8", engine="python")
            return df
        except Exception:
            archivo.seek(0)

        # Intento 4: archivo de texto con tabulaciones
        try:
            df = pd.read_csv(archivo, sep="\t", encoding="utf-8", engine="python")
            return df
        except Exception:
            archivo.seek(0)

        # Intento 5: detectar separador automáticamente
        try:
            contenido = archivo.read().decode("utf-8", errors="ignore")
            separador = ";" if contenido.count(";") > contenido.count(",") else ","
            df = pd.read_csv(io.StringIO(contenido), sep=separador)
            return df
        except Exception:
            pass

        st.error("⚠️ No se pudo leer el archivo. Verificá que sea Excel o CSV válido.")
        return None

    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return None


def limpiar_texto(valor):
    if isinstance(valor, str):
        valor = valor.replace('"', '')
        valor = valor.replace(',', '.')
        valor = re.sub(r"\s+", "", valor)
    return valor


def procesar_columnas(df, columnas):
    try:
        columnas_idx = [i - 1 for i in columnas]
        df_sel = df.iloc[:, columnas_idx].copy()
        df_limpio = df_sel.applymap(limpiar_texto)
        return df_limpio
    except Exception as e:
        st.error(f"Error al procesar las columnas: {e}")
        return None


def convertir_a_csv(df, nombre_original):
    try:
        nombre_salida = os.path.splitext(nombre_original)[0] + "-procesado.csv"
        buffer = io.StringIO()
        df.to_csv(buffer, sep=';', index=False)
        csv_bytes = buffer.getvalue().encode('utf-8')
        return nombre_salida, csv_bytes
    except Exception as e:
        st.error(f"Error al convertir a CSV: {e}")
        return None, None


# ===============================
# 🚀 MAIN APP (Streamlit)
# ===============================

def main():
    st.title("📊 Conversor inteligente de Excel/CSV a CSV limpio")
    st.write("""
    Subí un archivo Excel (.xls o .xlsx) o CSV, elegí las columnas a procesar,
    y descargá el resultado en formato CSV con limpieza automática.
    
    🔹 El programa eliminará comillas dobles, espacios y cambiará comas (,) por puntos (.).
    """)

    archivo = st.file_uploader("📂 Subí tu archivo", type=["xlsx", "xls", "csv", "txt"])

    if archivo:
        df = leer_archivo_flexible(archivo)
        if df is not None:
            st.write("✅ Archivo leído correctamente. Vista previa:")
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
                            df_proc = procesar_columnas(df, columnas)
                            if df_proc is not None:
                                nombre_csv, csv_bytes = convertir_a_csv(df_proc, archivo.name)
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


if __name__ == "__main__":
    main()
# ===============================