Para inicializar la aplicacion

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
(in venv) pip install -r requirements.txt    # Instalar las librerias especificadas en requirements.txt
(in venv) pip install library_name           # Instalar las librerias
(in venv) pip freeze > requirements.txt      # Guardar librerias instaladas
(in venv) python main.py                     # Ejecuar el codigo


- Archivo .env


EVOLUTION_API_URL= http://localhost:9090 (ejemplo) // url donde se ejecuta evolution api
WHATSAPP_GRUPO_ID_SECRETARIA_TRES_ESTRELLAS=numero@g.us //id del grupo tres estrellas



EVOLUTION API & WEBHOOK
| Field                          | Meaning                    |
| ------------------------------ | -------------------------- |
| `remoteJid`                    | Chat ID (group or private) |
| `participant`                  | Actual sender in group     |
| `senderLid` / `participantLid` | Device-level ID            |
| `@lid`                         | Linked device ID           | NO  usar (cambian valores por sesion)
| `@g.us`                        | Group                      | Usar para grupos
| `@s.whatsapp.net`              | Phone number               | Usar para chats privados











BASE DE DATOS MYSQL
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




- Query de MySql para obtener cuotas por mes (procedure asistencia_pivot_by_date)
- Procedure para obtener cuotas por mes especiificado de alumnos que asistieron al menos una vez

delimiter $$
create procedure cuotas_x_mes(in month_number int, in year_number int)
BEGIN
drop temporary table if exists asistencia_nula_mes_anio;
create temporary table asistencia_nula_mes_anio as (
select j.id_jugador from jugador j
cross join practica p
left join jugador_practica jp on jp.id_jugador = j.id_jugador and jp.id_practica=p.id_practica
where month(p.fecha_practica) = 1 and year(p.fecha_practica)= 2026
group by j.id_jugador
having count(jp.id_practica)=0
);

select concat(j.nombre, ' ',j.apellido) as 'Nombre y Apellido',c.fecha_cuota,c.valor,c.detalle_pago
from jugador j
left join cuota c on c.id_jugador = j.id_jugador
and year(c.fecha_cuota) = year_number and month(c.fecha_cuota) = month_number
where j.id_jugador not in (select id_jugador from asistencia_nula_mes_anio);
END $$
delimiter ;




