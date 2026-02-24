
# comunication to evolition_api
from flask import Flask, request
import requests
import os
from dotenv import load_dotenv
import crear_excel_cuota
import crear_excel_asistencia
import base64
import init_config



load_dotenv()
evolution_api_url = os.getenv("EVOLUTION_API_URL")
instance_evolution_api = os.getenv("INSTANCE_EVOLUTION_API")
apy_key = os.getenv("API_KEY")
grupo_id_test = os.getenv("WHATSAPP_GRUPO_ID_TEST")
grupo_id = os.getenv("WHATSAPP_GRUPO_ID")

app = Flask(__name__)

init_config.init()

def send_excel(id_grupo: str, mensaje_especial: str):
    url = f"{evolution_api_url}/message/sendMedia/{instance_evolution_api}"
    url_send_message = f"{evolution_api_url}/message/sendText/{instance_evolution_api}"

    headers = {"apikey": apy_key, "Content-Type": "application/json"}
    funcion, mes, anio = mensaje_especial[0], int(mensaje_especial[1]), int(mensaje_especial[2])

    if(funcion=="ASISTENCIA"):
        file_path = crear_excel_asistencia.crear_excel_asistencia(mes, anio)
    elif(funcion=="CUOTA"):
        file_path = crear_excel_cuota.crear_excel_cuota(mes,anio)

    if(file_path == []):
        print("No file_path")
        requests.post(url_send_message,
                      json={"number": id_grupo, "text": "No hay nada en fecha especificada.", "delay":600},
                      headers=headers )
        return

    print("FILE PATH: " + file_path)
    with open(file_path, "rb") as f:
        encoded_file = base64.b64encode(f.read()).decode()
    body = {
        "number": id_grupo,
        "mediatype": "document",
        "caption": "Archivo Excel",
        "media": f"{encoded_file}",
        "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "fileName": file_path,
        "delay": 1200,
    }

    response = requests.post(url, json=body, headers=headers)

    print("Reply status:", response.status_code)
    print("Reply response:", response.text)

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.json
    message_data = payload.get("data", {}).get("message", {})
    message = ( message_data.get("conversation") or message_data.get("extendedTextMessage", {}).get("text") )
    remoteJid = payload.get("data", {}).get("key", {}).get("remoteJid")

    if not message:
        return "Ignored (no text)", 200

    special_message = message.split(":")

    if((remoteJid==grupo_id_test or remoteJid==grupo_id) and len(special_message) == 3 and special_message[0] in ("ASISTENCIA", "CUOTA") ):
        try:
            value1 = int(special_message[1])
            value2 = int(special_message[2])
            send_excel(remoteJid, special_message)
        except Exception as e:
            print("Error Formato Invalido:",e)
            return "Error: Formato Invalido", 200


    return "OK", 200

app.run(host="0.0.0.0", port=5000)






