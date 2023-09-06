import streamlit as st
import requests
from io import BytesIO
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import json
import random 
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go


st.set_page_config(layout="wide")
st.set_option('deprecation.showPyplotGlobalUse', False)

st.sidebar.write("Conoce los temas más sobresalientes de las solicitudes de información")

st.sidebar.title("Selecciona estado y año: ")
state = st.sidebar.selectbox("Estado", ['Yucatán'])

year = st.sidebar.selectbox("Año", [ '2022'])

run = st.sidebar.button('Mostrar')


if run:
    try:
        if state.lower() == 'yucatán':
            if year == '2022':
                archivo_json = 'yucatan2022.json'  # Agrega la ruta correcta al archivo JSON
                # Datos  de probabilidades de palabras clave para cada tópico
                nombre_archivo = "data2022.json"

                # Leer el archivo JSON
                with open(nombre_archivo, 'r') as archivo:
                    data = json.load(archivo)
                
                # Crear una lista de diccionarios con los datos de cada tópico
                wordcloud_data = []
                for topic, word_probs in data.items():
                    for word, prob in word_probs.items():
                        wordcloud_data.append({"Topic": topic, "Word": word, "Probability": prob})

                # Asignar ubicaciones aleatorias en Yucatán para cada palabra
                num_words = sum(len(topic_data) for topic_data in data.values())
                random_latitudes = np.random.uniform(20.3, 21.3, num_words)  # Rango de latitudes para Yucatán
                random_longitudes = np.random.uniform(-88.3, -89.3, num_words)  # Rango de longitudes para Yucatán


                df1 = pd.DataFrame(wordcloud_data)

                # Escalar las probabilidades para el tamaño de fuente
                max_prob = df1["Probability"].max()
                min_prob = df1["Probability"].min()
                df1["Size"] = np.interp(df1["Probability"], (min_prob, max_prob), (2, 200))
                mapbox_token = "pk.eyJ1IjoiaXZhbmxvc2FyIiwiYSI6ImNrZTJpdWN0NDA5cXUyem1oOGx3NGh1bGsifQ.wuhB2vmk4QGrciFWYygqaA"

                # Crear la nube de palabras interactiva con Plotly Express
                fig_mapa = px.scatter_mapbox(
                    df1,
                    lat=random_latitudes,
                    lon=random_longitudes,
                    hover_name="Word",
                    hover_data={"Probability": True},
                    text="Word",
                    size="Size",
                    color="Topic",
                    color_discrete_sequence=px.colors.qualitative.Plotly,
                    zoom=7.5,
                    mapbox_style="outdoors",
                    title="Nube de Palabras por Tópico en Yucatán",
                    labels={"Probability": "Probabilidad", "Word": "Palabra"},
                )

                # Cambiar el color del texto en la burbuja (etiqueta) a blanco
                fig_mapa.update_traces(
                    textfont_color='black'

                )

                # Ajustar el tamaño del mapa
                fig_mapa.update_layout(
                width=1200,  # Ajusta el ancho del gráfico según tus preferencias
                height=900,  # Ajusta la altura del gráfico según tus preferencias

                )


                # Mostrar el mapa interactivo
                fig_mapa.update_layout(mapbox=dict(accesstoken=mapbox_token))

                # Crear un diccionario para hacer un seguimiento de los tópicos agregados
                added_topics = {}

                for row in df1.itertuples():
                    topic = row.Topic
                    if topic not in added_topics:
                        added_topics[topic] = True
                        fig_mapa.add_annotation(
                            go.layout.Annotation(
                                text=topic,
                                x=random_latitudes[row.Index],
                                y=random_longitudes[row.Index],
                                showarrow=False,
                                font=dict(size=14),
                            )
                        )


                # Datos de ejemplo en una lista de tuplas
                def load_data():
                    data = pd.read_csv("topic_2022_yucatan.csv")
                    return data
                # Cargar los datos desde el CSV
                data = load_data()
                # Crear el primer gráfico
                st.title("Tópicos LDA en Yucatán durante 2021")
                st.plotly_chart(fig_mapa)
                # Título de la aplicación
                st.title("Descripción de Tópicos")
                st.dataframe(data)
            else:
                st.error("Año no válido")
                st.stop()

            # Leer el archivo JSON línea por línea
            data = []
            with open(archivo_json, 'r') as json_file:
                for line in json_file:
                    data.append(json.loads(line))

            # Crear el DataFrame a partir de los datos
            dfyuc = pd.DataFrame(data)


        st.write("Datos cargados exitosamente:", df)  # Mostrar el DataFrame
    except json.JSONDecodeError as e:
        st.error("Error al cargar el archivo JSON: {}".format(e))
    
    # Obtener los valores y frecuencias de la columna DEPENDENCIA#############################################
    dependencia_counts = dfyuc['DEPENDENCIA'].value_counts()

    # Generar colores aleatorios para cada barra
    colors = [f'#{random.randint(0, 0xFFFFFF):06x}' for _ in range(len(dependencia_counts[:50]))]

    # Crear un gráfico interactivo de barras utilizando Plotly Express
    fig_dependencia = px.bar(dependencia_counts[:50], x=dependencia_counts[:50].index, y='DEPENDENCIA',
                 title='Top 25 Dependencias más Comunes', labels={'DEPENDENCIA': 'Cantidad', 'x': 'Dependencia'},
                 color=colors)  # Usar los colores generados para colorear las barras
    fig_dependencia.update_layout(
        xaxis={'categoryorder': 'total descending'},
        xaxis_title='Dependencia',
        yaxis_title='Cantidad',
        width=1200,  # Ajusta el ancho del gráfico según tus preferencias
        height=900,  # Ajusta la altura del gráfico según tus preferencias
    )
    fig_dependencia.update_xaxes(tickangle=90)



    # Calcular el conteo de cada sector ###############################################################
    count_data = dfyuc['SECTOR'].value_counts().reset_index()
    count_data.columns = ['SECTOR', 'COUNT']
    # Crear el segundo gráfico
    fig_sector = px.bar(count_data, x='SECTOR', y='COUNT', title='Distribución de Sectores', color='COUNT',
                        color_continuous_scale='inferno')
    fig_sector.update_layout(
        xaxis={'categoryorder': 'total descending'},
        xaxis_title='Sector',
        yaxis_title='Frecuencia',
        xaxis_tickangle=45,
        width=1200,
        height=600
    )
# Calcular el conteo de cada medio de entrada################################
    count_data = dfyuc['MEDIOENTRADA'].value_counts().reset_index()
    count_data.columns = ['MEDIOENTRADA', 'COUNT']

    # Crear un gráfico de barras
    figmedioentrada = px.bar(count_data, x='MEDIOENTRADA', y='COUNT', title='Distribución de Medios de Entrada')
    # Ajusta el tamaño del gráfico
    figmedioentrada.update_layout(
               width=1200,
        height=600  # Ajusta la altura del gráfico según tus preferencias
    )
    
    # Calcular el conteo de cada tipo de solicitud ################################
    count_data = dfyuc['TIPOSOLICITUD'].value_counts().reset_index()
    count_data.columns = ['TIPOSOLICITUD', 'COUNT']
    fig_tipo_sol = px.bar(count_data, x='TIPOSOLICITUD', y='COUNT', title='Distribución de Tipos de Solicitud')
    fig_tipo_sol.update_layout(
               width=1200,
        height=600 # Ajusta la altura del gráfico según tus preferencias
    )
    
    # Calcular el conteo de cada respuesta######################################
    count_data = dfyuc['RESPUESTA'].value_counts().reset_index()
    count_data.columns = ['RESPUESTA', 'COUNT']
    # Crear un gráfico de barras
    fig_respuesta = px.bar(count_data, x='RESPUESTA', y='COUNT', title='Distribución de Respuestas')
    fig_respuesta.update_layout(
                width=1200,
        height=600 # Ajusta la altura del gráfico según tus preferencias
    )
    fig_respuesta.update_xaxes(tickangle=90)
    # Mostrar ambos gráficos en Streamlit
    st.title("Distribución de Dependencias")
    st.plotly_chart(fig_dependencia)
    st.title("Distribución de Sectores")
    st.plotly_chart(fig_sector)
    st.title("Distribución de Medios de Entrada")
    st.plotly_chart(figmedioentrada)
    st.title("Distribución de Tipo de Solicitud")
    st.plotly_chart(fig_tipo_sol)
    st.title("Distribución de Tipo de Respuestas")
    st.plotly_chart(fig_respuesta)
    
