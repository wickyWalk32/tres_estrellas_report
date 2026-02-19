Para inicializar la aplicacion

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
(in venv) pip install -r requirements.txt    # Instalar las librerias especificadas en requirements.txt
(in venv) pip install library_name           # Instalar las librerias
(in venv) pip freeze > requirements.txt      # Guardar librerias instaladas
(in venv) python main.py                     # Ejecuar el codigo



(en carpeta de docker-compose.yaml de evolution api)
docker compose up

( En carpta de Dockerfile ) Crear imagen
docker build -t reporte_tres_estrellas .


docker run --name reporte_tres_estrellas -p 5000:5000 --env-file .env reporte_tres_estrellas
(muy importante ponerle el nombre al contenedor)

Conectar app a la network de evolution-api
docker network connect 827e50744787 reporte_tres_estrellas


docker rm -f reporte_tres_estrellas    # Remover contenedor (de ser necesario)









- Archivo .env  VARIABLES DE AMBIENTE


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











BASE DE DATOS PostgreSQL
- Query de PostgreSql para obtener asistencia por mes (procedure asistencia_pivot_by_date)

CREATE OR REPLACE FUNCTION asistencia_pivot_by_date(month_number INT, year_number INT)
RETURNS JSON AS
$$
DECLARE
    cols TEXT;
    sql TEXT;
    result JSON;
BEGIN
    -- 1️⃣ Build dynamic column list (ordered by date)
    SELECT string_agg(
               format('"%s" INT', to_char(fecha_practica, 'YYYY-MM-DD')),
               ', ' ORDER BY fecha_practica
           )
    INTO cols
    FROM (
        SELECT DISTINCT fecha_practica
        FROM practica
        WHERE EXTRACT(MONTH FROM fecha_practica) = month_number
          AND EXTRACT(YEAR FROM fecha_practica) = year_number
        ORDER BY fecha_practica
    ) sub;

    -- 2️⃣ Build dynamic SQL
    sql := format(
    $f$
    SELECT json_agg(row_to_json(final_rows))
    FROM (
        SELECT
            j.nombre || ' ' || j.apellido AS jugador,
            ct.*
        FROM crosstab(
            $c$
            SELECT
                j.id_jugador,
                p.fecha_practica::TEXT,
                CASE WHEN a.id_practica IS NOT NULL THEN 1 ELSE 0 END
            FROM jugador j
            CROSS JOIN practica p
            LEFT JOIN jugador_practica a
              ON a.id_jugador = j.id_jugador
             AND a.id_practica = p.id_practica
            WHERE EXTRACT(MONTH FROM p.fecha_practica) = %1$s
              AND EXTRACT(YEAR FROM p.fecha_practica) = %2$s
            ORDER BY 1,2
            $c$,
            $v$
            SELECT DISTINCT fecha_practica::TEXT
            FROM practica
            WHERE EXTRACT(MONTH FROM fecha_practica) = %1$s
              AND EXTRACT(YEAR FROM fecha_practica) = %2$s
            ORDER BY fecha_practica
            $v$
        ) AS ct(id_jugador INT, %3$s)
        JOIN jugador j ON j.id_jugador = ct.id_jugador
        ORDER BY j.apellido, j.nombre
    ) final_rows
    $f$, month_number, year_number, cols);

    -- 3️⃣ Execute and return JSON
    EXECUTE sql INTO result;
    RETURN result;
END;
$$
LANGUAGE plpgsql;





- Query de PostgreSQL para obtener cuotas por mes (cuotas_x_mes)
- Procedure para obtener cuotas por mes de alumnos que asistieron al menos una vez dicho mes

CREATE OR REPLACE FUNCTION cuotas_x_mes(
    month_number INT,
    year_number INT
)
RETURNS TABLE(
    nombre_y_apellido TEXT,
    fecha_cuota DATE,
    valor NUMERIC,
    detalle_pago VARCHAR(200)
) 
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH asistencia_nula_mes_anio AS (
        SELECT j.id_jugador
        FROM jugador j
        CROSS JOIN practica p
        LEFT JOIN jugador_practica jp 
            ON jp.id_jugador = j.id_jugador 
            AND jp.id_practica = p.id_practica
        WHERE EXTRACT(MONTH FROM p.fecha_practica) = month_number
          AND EXTRACT(YEAR FROM p.fecha_practica) = year_number
        GROUP BY j.id_jugador
        HAVING COUNT(jp.id_practica) = 0
    )
    SELECT 
        CONCAT(j.nombre, ' ', j.apellido) AS nombre_y_apellido,
        c.fecha_cuota,
        c.valor,
        c.detalle_pago
    FROM jugador j
    LEFT JOIN cuota c 
        ON c.id_jugador = j.id_jugador
        AND EXTRACT(YEAR FROM c.fecha_cuota) = year_number
        AND EXTRACT(MONTH FROM c.fecha_cuota) = month_number
    WHERE j.id_jugador NOT IN (SELECT id_jugador FROM asistencia_nula_mes_anio);
END;
$$;




