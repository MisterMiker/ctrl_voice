import paho.mqtt.client as paho
import time
import json
import streamlit as st
import cv2
import numpy as np
from PIL import Image as Image, ImageOps as ImagOps
from keras.models import load_model

# --- Funciones de callback MQTT ---
def on_publish(client, userdata, result):  # create function for callback
    print("El dato ha sido publicado\n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

# --- Configuración del cliente MQTT ---
broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("APP_CERR")
client1.on_message = on_message
client1.on_publish = on_publish
client1.connect(broker, port)

# --- Cargar modelo Keras ---
model = load_model('keras_model.h5')
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

# --- Interfaz Streamlit ---
st.title("Cerradura Inteligente")

img_file_buffer = st.camera_input("Toma una Foto")

if img_file_buffer is not None:
    # Convertir la imagen en formato adecuado
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    img = Image.open(img_file_buffer)

    newsize = (224, 224)
    img = img.resize(newsize)
    img_array = np.array(img)

    # Normalizar imagen
    normalized_image_array = (img_array.astype(np.float32) / 127.0) - 1
    data[0] = normalized_image_array

    # Ejecutar predicción
    prediction = model.predict(data)
    print(prediction)

    # --- Detección de gestos ---
    if prediction[0][0] > 0.3:
        st.header('Abriendo 🚪')
        # Publica en el mismo topic y con JSON válido
        client1.publish("ZuluMikerCasa", json.dumps({"gesto": "Abre"}), qos=0, retain=False)
        time.sleep(0.2)

    if prediction[0][1] > 0.3:
        st.header('Cerrando 🔒')
        client1.publish("ZuluMikerCasa", json.dumps({"gesto": "Cierra"}), qos=0, retain=False)
        time.sleep(0.2)
