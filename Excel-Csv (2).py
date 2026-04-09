import streamlit as st
import pandas as pd
import io
import os
import re
import zipfile

# ===============================
# 🔧 FUNCIONES
# ===============================

def leer_archivo_flexible(archivo):
    try:
        try:
            df = pd.read_excel(archivo, engine="openpyxl")
            return df
        except Exception:
            archivo.seek(0)

        try:
            df = pd.read_excel(archivo, engine="xlrd")
            return df
        except Exception:
            archivo.seek(0)

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

        try:
            df = pd.read_csv(archivo, sep="\t", encoding="utf-8", engine="python")
            return df
        except Exception:
            archivo.seek(0)

        try:
            contenido = archivo.read().decode("utf-8", errors="ignore")
            separador = ";" if contenido.count(";") > contenido.count(",") else ","
            df = pd.read_csv(io.StringIO(contenido), sep=separador)
            return df
        except Exception:
            pass

        st.error(f"⚠️ No se pudo leer '{archivo.name}'. Verificá que sea Excel o CSV válido.")
        return None

    except Exception as e:
        st.error(f"Error al leer '{archivo.name}': {e}")
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
        df_limpio = df_sel.apply(lambda col: col.map(limpiar_texto))
        return df_limpio
    except Exception as e:
        st.error(f"Error al procesar las columnas: {e}")
        return None


def convertir_a_csv_bytes(df, nombre_original):
    try:
        nombre_salida = os.path.splitext(nombre_original)[0] + "-procesado.csv"
        buffer = io.StringIO()
        df.to_csv(buffer, sep=';', index=False)
        csv_bytes = buffer.getvalue().encode('utf-8')
        return nombre_salida, csv_bytes
    except Exception as e:
        st.error(f"Error al convertir a CSV: {e}")
        return None, None


def crear_zip(archivos_procesados):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for nombre, contenido in archivos_procesados:
            zf.writestr(nombre, contenido)
    return zip_buffer.getvalue()


# ===============================
# 🚀 MAIN APP (Streamlit)
# ===============================

def main():
    st.title("📊 Conversor inteligente de Excel/CSV a CSV limpio")
    st.write("""
    Subí uno o varios archivos Excel (.xls, .xlsx) o CSV, elegí las columnas a procesar,
    y descargá todos los resultados juntos en un archivo comprimido (.zip).

    🔹 El programa eliminará comillas dobles, espacios y cambiará comas (,) por puntos (.).
    """)

    archivos = st.file_uploader(
        "📂 Subí tus archivos (podés seleccionar varios a la vez)",
        type=["xlsx", "xls", "csv", "txt"],
        accept_multiple_files=True,
    )

    if archivos:
        st.divider()
        st.markdown(f"**{len(archivos)} archivo(s) cargado(s):**")

        primer_df = None
        for archivo in archivos:
            df_preview = leer_archivo_flexible(archivo)
            archivo.seek(0)
            if df_preview is not None:
                primer_df = df_preview
                st.caption(f"Vista previa de **{archivo.name}** (referencia para elegir columnas):")
                st.dataframe(df_preview.head(3), use_container_width=True)
                break

        if primer_df is not None:
            n_cols = len(primer_df.columns)
            st.info(f"ℹ️ El archivo tiene **{n_cols} columna(s)**. Numeradas del 1 al {n_cols}.")

            columnas_str = st.text_input("Columnas a incluir (separadas por coma):", placeholder="Ejemplo: 1,4")

            if columnas_str:
                try:
                    columnas = [int(x.strip()) for x in columnas_str.split(",") if x.strip().isdigit()]

                    if not columnas:
                        st.warning("⚠️ No se detectaron columnas válidas.")
                    elif any(i < 1 or i > n_cols for i in columnas):
                        st.warning(f"⚠️ Alguna columna está fuera del rango válido (1 a {n_cols}).")
                    else:
                        st.write(f"✅ Se procesarán las columnas **{columnas}** en los **{len(archivos)}** archivo(s).")

                        if st.button("⚙️ Procesar todos los archivos"):
                            archivos_procesados = []
                            errores = []
                            progress = st.progress(0, text="Procesando...")

                            for idx, archivo in enumerate(archivos):
                                archivo.seek(0)
                                df = leer_archivo_flexible(archivo)
                                if df is None:
                                    errores.append(archivo.name)
                                    continue

                                if any(i > len(df.columns) for i in columnas):
                                    errores.append(f"{archivo.name} (tiene menos columnas que las seleccionadas)")
                                    continue

                                df_proc = procesar_columnas(df, columnas)
                                if df_proc is None:
                                    errores.append(archivo.name)
                                    continue

                                nombre_csv, csv_bytes = convertir_a_csv_bytes(df_proc, archivo.name)
                                if csv_bytes:
                                    archivos_procesados.append((nombre_csv, csv_bytes))

                                progress.progress((idx + 1) / len(archivos), text=f"Procesando {archivo.name}…")

                            progress.empty()

                            if errores:
                                st.warning(f"⚠️ No se pudieron procesar: {', '.join(errores)}")

                            if archivos_procesados:
                                st.success(f"✅ {len(archivos_procesados)} archivo(s) procesado(s) correctamente.")

                                if len(archivos_procesados) == 1:
                                    nombre, contenido = archivos_procesados[0]
                                    st.download_button(
                                        label="⬇️ Descargar CSV procesado",
                                        data=contenido,
                                        file_name=nombre,
                                        mime="text/csv",
                                    )
                                else:
                                    zip_bytes = crear_zip(archivos_procesados)
                                    st.download_button(
                                        label=f"⬇️ Descargar todos ({len(archivos_procesados)} archivos) en .zip",
                                        data=zip_bytes,
                                        file_name="archivos_procesados.zip",
                                        mime="application/zip",
                                    )

                except ValueError:
                    st.error("Por favor, ingresá solo números separados por comas.")


if __name__ == "__main__":
    main()
