import requests
from dotenv import load_dotenv
import os
import base64
from io import BytesIO
from PIL import Image


load_dotenv()

host = os.getenv("EVOLUTION_API_URL")
api_key = os.getenv("API_KEY")
instance_name = os.getenv("INSTANCE_EVOLUTION_API")
whatsapp_number = os.getenv("WHATSAPP_OWNER_NUMBER")

url_fetch_instance = f"{host}/instance/fetchInstances"
url_create_instance = f"{host}/instance/create"
url_delete_instance = f"{host}/instance/delete/{instance_name}"
url_connect_instance = f"{host}/instance/connect/{instance_name}"

def connect():
    print("EMPEZAMOS BIEN PEPE")
    instancias = requests.get(url_fetch_instance, headers={"apikey": api_key})
    print("instancias encontradas:", instancias.json())
    if(instancias.json()[0].get("connectionStatus", {}) != 'close'):
        print("Ya existe una conexion")
        return True
    if(instancias.json() == []):
        print("No se encuentran instancias. a crear una nueva")
        body =  {
        "instanceName": instance_name,
        "token": api_key,
        "number": whatsapp_number,
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS",
        "webhook": {
            "url": "host.docker.internal:5000",
            "base64": True,
            "headers": {
                 "autorization": "Bearer TOKEN",
                 "Content-Type": "application/json"
                 },
         "events": ["MESSAGES_UPSERT"]
            },
        }
        print("Creando...")
        creation_data = requests.post(url_create_instance,json=body,headers={"apikey":api_key})
        print("request result:", creation_data.json())
        qr_base64 = creation_data.json().get("qrcode",{}).get("base64")
        if (qr_base64==None):
            print("using url connect")
            response = requests.post(url_connect_instance,headers={"apikey":api_key}).json()
            print("Respuesta a conexion:",response)
            qr_base64 = response.get("base64")

        if(qr_base64):
            print("Generando base64 en limpio")
            if qr_base64.startswith("data:image"):
                qr_base64 = qr_base64.split(",")[1]
                print("clean qr: ",qr_base64)

            # Display in terminal
            image_bytes = base64.b64decode(qr_base64)
            image = Image.open(BytesIO(image_bytes))
            image.show()
            return True
        else:
            print("No QR code found in the response")


def clean():
    response = requests.delete(f"{url_delete_instance}",headers={"apikey":api_key})
    print("Instancia WhatsApp eliminada",response.json())

def init():
    for x in range(5):
        if(connect()):
            print("Conexion Exitosa")
            return
        else:
            clean()

# init()