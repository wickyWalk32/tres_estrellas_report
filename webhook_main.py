
# comunication to evolition_api
from flask import Flask, request
import requests
import os
from dotenv import load_dotenv
import crear_excel_cuota
import crear_excel_asistencia
import base64

load_dotenv()
evolution_api_url = os.getenv("EVOLUTION_API_URL")
instance_evolution_api = os.getenv("INSTANCE_EVOLUTION_API")
apy_key = os.getenv("API_KEY")
grupo_id_test = os.getenv("WHATSAPP_GRUPO_ID_TEST")
grupo_id_tres_estrellas = os.getenv("WHATSAPP_GRUPO_ID_SECRETARIA_TRES_ESTRELLAS")

app = Flask(__name__)


def send_excel(id_grupo: str, mensaje: str):
    url = f"{evolution_api_url}/message/sendMedia/{instance_evolution_api}"
    headers = {"apikey": apy_key, "Content-Type": "application/json"}
    print(mensaje)
    funcion = mensaje.split(":")[0]
    mes = int(mensaje.split(":")[1])
    anio = int(mensaje.split(":")[2])
    if(funcion=="ASISTENCIA"):
        file_path = crear_excel_asistencia.crear_excel_asistencia(mes, anio)
    elif(funcion=="CUOTA"):
        file_path = crear_excel_cuota.crear_excel_cuota(mes,anio)
    print("FILE PATH: "+file_path)
    with open(file_path, "rb") as f:
        encoded_file = base64.b64encode(f.read()).decode()
    body = {
        "number": id_grupo,
        "mediatype": "document",
        "caption": "Here’s the Excel file",
        "media": f"{encoded_file}",
        "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "fileName": file_path
    }

    response = requests.post(url, json=body, headers=headers)

    print("Reply status:", response.status_code)
    print("Reply response:", response.text)

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.json
    message = payload["data"]["message"]["conversation"] or payload["data"]["message"]["extendedTextMessage"]
    remoteJid = payload["data"]["key"]["remoteJid"]

    if(remoteJid==grupo_id_test and (message.split(":")[0]=="ASISTENCIA" or message.split(":")[0]=="CUOTA") ):
        send_excel(remoteJid,message)

    return "OK", 200

app.run(host="0.0.0.0", port=5000)






