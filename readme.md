Para inicializar la aplicacion

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
(in venv) pip install -r requirements.txt    # Instalar las librerias especificadas en requirements.txt
(in venv) pip install library_name           # Instalar las librerias
(in venv) pip freeze > requirements.txt      # Guardar librerias instaladas
(in venv) python main.py                     # Ejecuar el codigo








- Query de MySql para obtener asistencia por mes (procedure asistencia_pivot_by_date)

DELIMITER $$
CREATE PROCEDURE asistencia_pivot_by_date(in month_number int, in year_number int)
BEGIN

DECLARE cols TEXT;
SELECT GROUP_CONCAT( DISTINCT
CONCAT('MAX(CASE WHEN p.id_practica = ',
 p.id_practica, ' AND a.id_practica IS NOT NULL 
 THEN 1 ELSE 0 END) AS `',
 p.fecha_practica,'`	')
 order by p.fecha_practica asc
    ) INTO cols
    FROM practica p
    where month(p.fecha_practica) = month_number 
    and year(p.fecha_practica) = year_number;
    

    SET @sql = CONCAT(
        'SELECT CONCAT(j.nombre, '' '', j.apellido) AS jugador, ', cols, '
        FROM jugador j
        CROSS JOIN practica p
        LEFT JOIN jugador_practica a ON a.id_jugador = j.id_jugador
		AND a.id_practica = p.id_practica
        GROUP BY j.id_jugador
        ORDER BY j.id_jugador'
    );

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
END$$
DELIMITER ;





