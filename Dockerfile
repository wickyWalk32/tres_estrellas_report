FROM python:3.12-alpine
WORKDIR /reporte_asistencia
RUN apk add --no-cache build-base libffi-dev
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python","-u","webhook_main.py"]