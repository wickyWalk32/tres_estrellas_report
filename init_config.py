import requests
from dotenv import load_dotenv
import os
import qrcode


load_dotenv()

host = os.getenv("EVOLUTION_API_URL")
api_key = os.getenv("API_KEY")
instance_name = os.getenv("INSTANCE_EVOLUTION_API")
whatsapp_number = os.getenv("WHATSAPP_OWNER_NUMBER")
webhook_url = os.getenv("WEBHOOK_URL")

url_fetch_instance = f"{host}/instance/fetchInstances"
url_create_instance = f"{host}/instance/create"
url_delete_instance = f"{host}/instance/delete/{instance_name}"
url_connect_instance = f"{host}/instance/connect/{instance_name}"
url_webhook_set = f"{host}/webhook/set/{instance_name}"    # POST
url_webhook_find = f"{host}/webhook/find/{instance_name}"   # GET

def connect():
    print("EMPEZAMOS BIEN PEPE")
    qr_code = None
    instancias = requests.get(url_fetch_instance, headers={"apikey": api_key})
    print("instancias encontradas:", instancias.json())
    if(instancias.json() == []):
        print("No se encuentran instancias. A crear una nueva")
        body =  {
        "instanceName": instance_name,
        "token": api_key,
        "number": whatsapp_number,
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS",
        "webhook": {
            "url": webhook_url,
            "enabled": True,
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
        qr_code = creation_data.json().get("qrcode",None).get("code")
        if(qr_code):
            print_qr(qr_code)
        else:
            print("No QR code found in the response")

    if ( qr_code == None or instancias.json() != [] ):
        print("using url connect")
        response = requests.get(url_connect_instance,headers={"apikey":api_key})
        print("Respuesta a conexion:",response)
        qr_code = response.json().get("code")
        print_qr(qr_code)
        return True

    if (instancias.json()[0].get("connectionStatus", {}) != 'close'):
            print("Ya existe una conexion")
            return True

def clean():
    response = requests.delete(f"{url_delete_instance}",headers={"apikey":api_key})
    print("Instancia WhatsApp eliminada",response.json())

def print_qr(qr_code_text):
    qr = qrcode.QRCode()
    qr.add_data(qr_code_text)
    qr.make()
    qr.print_ascii()


def init():
    for x in range(5):
        if(connect()):
            print("Conexion Exitosa")
            return
        else:
            clean()

# Mainly for debugging
def set_webhook():
    print("SET WEBHOOK")
    body_config = {
        "webhook":{
            "url": webhook_url,
            "enabled":True,
            "events": ["MESSAGES_UPSERT"],
                   },
    }
    response = requests.post(url_webhook_set, json=body_config, headers={"apikey":api_key})
    print(response.json())

def get_webhook():
    print("GET WEBHOOK")
    response = requests.get(url_webhook_find, headers={"apikey":api_key})
    print(response.json())

# init()