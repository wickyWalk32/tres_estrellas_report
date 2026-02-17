FROM python:3.12.10-slim
WORKDIR /reporte_asistencia
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python","webhook_main.py"]