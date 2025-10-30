import streamlit as st
import pandas as pd
import io
import os
import re  # 🔹 Usamos expresiones regulares para limpieza avanzada

# ===============================
# 🔧 FUNCIONES
# ===============================

def leer_excel(archivo_excel):
    """
    Lee un archivo Excel y devuelve un DataFrame de pandas.
    """
    try:
        df = pd.read_excel(archivo_excel)
        return df
    except Exception as e:
        st.error(f"Error al leer el archivo Excel: {e}")
        return None


def limpiar_texto(valor):
    """
    Limpia el texto eliminando:
    - Comillas dobles (")
    - Espacios en cualquier parte del texto
    - Reemplaza comas (,) por puntos (.)
    
    Ejemplo:
      '  1, 2  3 " ' → '1.23'
      '  str, in  g  ' → 'str.ing'
    """
    if isinstance(valor, str):
        # Eliminar comillas dobles
        valor = valor.replace('"', '')
        # Reemplazar comas por puntos
        valor = valor.replace(',', '.')
        # Eliminar todos los espacios (inicio, medio y final)
        valor = re.sub(r"\s+", "", valor)
    return valor


def procesar_columnas(df, columnas):
    """
    Toma un DataFrame y una lista de índices de columnas.
    Devuelve un nuevo DataFrame solo con esas columnas,
    aplicando la limpieza de texto (comillas, espacios, comas).
    """
    try:
        # Ajustar índices (el usuario ingresa posiciones desde 1)
        columnas_idx = [i - 1 for i in columnas]

        # Seleccionar columnas indicadas
        df_seleccion = df.iloc[:, columnas_idx].copy()

        # Limpiar texto en todas las celdas seleccionadas
        df_limpio = df_seleccion.applymap(limpiar_texto)

        return df_limpio

    except Exception as e:
        st.error(f"Error al procesar las columnas: {e}")
        return None


def convertir_a_csv(df, nombre_original):
    """
    Convierte un DataFrame a CSV (separado por ;)
    y devuelve el archivo como bytes descargables.
    El archivo se llamará con el nombre original + '-procesado.csv'
    """
    try:
        # Generar nombre de salida
        nombre_salida = os.path.splitext(nombre_original)[0] + "-procesado.csv"

        # Convertir DataFrame a CSV con separador ';'
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
    Subí un archivo Excel, elegí las columnas que querés procesar, 
    y descargá el resultado en formato CSV separado por punto y coma (;).
    
    🔹 El programa eliminará comillas dobles, espacios y cambiará comas (,) por puntos (.).
    """)

    # 1️⃣ Subir archivo Excel
    archivo_excel = st.file_uploader("Subí tu archivo Excel (.xlsx o .xls)", type=["xlsx", "xls"])

    if archivo_excel:
        # Mostrar preview de las columnas
        df = leer_excel(archivo_excel)
        if df is not None:
            st.write("Vista previa del archivo:")
            st.dataframe(df.head())

            # 2️⃣ Seleccionar posiciones de columnas
            st.write("Seleccioná las columnas que querés incluir (1 a máximo 15):")
            columnas_str = st.text_input("Ejemplo: 1,2,5,6")
            
            if columnas_str:
                try:
                    columnas = [int(x.strip()) for x in columnas_str.split(",") if x.strip().isdigit()]
                    
                    if any(i < 1 or i > len(df.columns) for i in columnas):
                        st.warning("⚠️ Ingresaste columnas fuera del rango válido.")
                    else:
                        # 3️⃣ Botón procesar
                        if st.button("Procesar archivo"):
                            df_procesado = procesar_columnas(df, columnas)
                            if df_procesado is not None:
                                nombre_csv, csv_bytes = convertir_a_csv(df_procesado, archivo_excel.name)

                                # 4️⃣ Mostrar botón de descarga
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
# ===============================