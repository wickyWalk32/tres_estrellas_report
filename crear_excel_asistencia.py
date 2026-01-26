import mysql.connector
from openpyxl.utils import get_column_letter
from openpyxl import  load_workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.layout import Layout, ManualLayout
from dotenv import load_dotenv
import os

load_dotenv()

user_name = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

conn = mysql.connector.connect(
    host="localhost",        # Database server address
   #port=port_number,    # specify only if default 3306 port is not the one being used
    user=user_name,
    password=password,
    database=db_name
)
cursor = conn.cursor(buffered=True) # Para ejecutar SQL queries


cursor.execute("SET SESSION group_concat_max_len = 1000000") # evitar esto: mysql.connector.errors.DatabaseError: 1260 (HY000): Row 11 was cut by GROUP_CONCAT()
#cursor.callproc("asistencia_pivot") # rocorrerlo con el fetchall() para evitar excel_data=[]
cursor.execute("CALL asistencia_pivot()")
data = cursor.fetchall()
cursor.close()
conn.close()

headers = [col[0] for col in cursor.description] # ['jugador', fecha1,fecha2,...]
excel_data = [list(headers)] + [list(x) for x in data]

file_path = "Asistencia.xlsx"
wb = load_workbook(file_path)
ws = wb.active

for i, col in enumerate(ws.iter_cols(min_row=1, max_row=1)):
    col_letter = get_column_letter(i + 1)
    ws.column_dimensions[col_letter].width = 20 if i == 0 else 12


# Grafico de Columnas Apiladas
chart = BarChart()
chart.type = "col"
chart.style = 10
chart.title = "Asistencia"
chart.grouping = "stacked"

chart.width = 45    # default 15
chart.height = 25   # default 7.5
chart.layout = Layout(
    ManualLayout( x=0.10, y=0.15, h=0.8, w=0.8, xMode="edge", yMode="edge",)
)
chart.legend.position = "b"  # bottom

#Forzar a que aparezcan los ejes (asistencias y nombres)
chart.x_axis.delete = False
chart.y_axis.delete = False

chart.overlap = 100
chart.gapWidth = 85
chart.y_axis.majorUnit = 1


data_ref = Reference(ws, min_col=2, max_col=ws.max_column, min_row=1, max_row=ws.max_row)
cats_ref = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)
chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(cats_ref)


ws.add_chart(chart, "A81")

wb.save(file_path)

#fecha = fechas[i][0].strftime('%d-%m-%Y')
