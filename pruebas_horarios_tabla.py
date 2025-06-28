from components.database_mysql_component import DataBaseMySQLManager
import datetime as dt
import pytz
from collections import defaultdict
import calendar
from datetime import datetime

dbMySQLManager = DataBaseMySQLManager()

horarios_tabla = dbMySQLManager.obtener_horarios_mes("july",tipo_servicio="facial", todos=True)
fecha = "2025-07-05"  # Fecha de ejemplo, puedes cambiarla según sea necesario

print("Horarios del mes:", horarios_tabla)

lima_tz = pytz.timezone('America/Lima')
hoy = dt.datetime.now(lima_tz).date()
input_date = dt.datetime.strptime(fecha, '%Y-%m-%d')  # Define input_date antes de usarlo
day_label   = input_date.strftime("%A").lower()
month_label = input_date.strftime("%B").lower()
day_number  = input_date.day 

working_hours = []

if horarios_tabla:
    for h in horarios_tabla:
        # a) Recurrentes: coinciden día de la semana
        if (
            h["tipo_horario"] == "recurrente"
            and h["dia_recurrente"] == day_label
        ):
            start = dt.datetime.strptime(h["inicio"], "%H:%M").time()
            end   = dt.datetime.strptime(h["fin"],   "%H:%M").time()
            working_hours.append({"start": start, "end": end})

        # b) Fijos: coinciden día del mes y mes
        elif (
            h["tipo_horario"] == "fijo"
            and int(h["fecha_fijo"]) == day_number
            and h["mes_horario"] == month_label
        ):
            start = dt.datetime.strptime(h["inicio"], "%H:%M").time()
            end   = dt.datetime.strptime(h["fin"],   "%H:%M").time()
            working_hours.append({"start": start, "end": end})

print("Horarios de trabajo disponibles:")
for wh in working_hours:
    print(f"Desde: {wh['start']} Hasta: {wh['end']}")



def formatear_horarios_prompt_es_v3(horarios: list[dict]) -> str:
    """
    Devuelve un bloque de texto en español, agrupado por mes, listo para
    incluirse en tu prompt.  Ejemplo de salida:

    Horarios disponibles:
    - Junio:
      • Todos los Martes de 13:30 a 20:30 (servicio capilar)
      • Todos los Jueves de 13:30 a 20:30 (servicio capilar)
      • Todos los Sábados de 10:00 a 17:00 (servicio capilar)
      • El 28 de junio de 2025 de 08:00 a 21:00 (servicio facial)
    - Julio:
      • El 5 de julio de 2025 de 21:51 a 22:51 (servicio facial)
    """

    # Traducciones
    meses_es = {
        "january": "Enero", "february": "Febrero", "march": "Marzo",
        "april": "Abril", "may": "Mayo", "june": "Junio",
        "july": "Julio", "august": "Agosto", "september": "Septiembre",
        "october": "Octubre", "november": "Noviembre", "december": "Diciembre"
    }
    dias_es = {
        "monday": "Lunes", "tuesday": "Martes", "wednesday": "Miércoles",
        "thursday": "Jueves", "friday": "Viernes",
        "saturday": "Sábado", "sunday": "Domingo"
    }

    # --- Agrupar por mes inglés ----
    agrupado = defaultdict(list)
    for h in horarios:
        agrupado[h["mes_horario"].lower()].append(h)

    # --- Orden cronológico de los meses ---
    def idx_mes(m):
        return list(calendar.month_name).index(m.capitalize())

    lineas = ["Horarios disponibles:"]
    for mes_ing in sorted(agrupado.keys(), key=idx_mes):
        mes_es = meses_es.get(mes_ing, mes_ing.capitalize())
        lineas.append(f"- {mes_es}:")
        for h in agrupado[mes_ing]:
            servicio = h["tipo_servicio"].lower().strip()  # facial | capilar
            inicio, fin = h["inicio"], h["fin"]

            if h["tipo_horario"].lower() == "recurrente":
                dia = dias_es.get(h["dia_recurrente"].lower(), h["dia_recurrente"])
                lineas.append(f"  • Todos los {dia} de {inicio} a {fin} (servicio {servicio})")
            else:
                # fecha_fijo puede venir como '28' o '2025-06-28'
                fecha_raw = h["fecha_fijo"]
                if len(fecha_raw) in (1, 2):                      # solo día
                    año = datetime.now().year
                    fecha = f"{int(fecha_raw)} de {mes_es.lower()} de {año}"
                else:                                             # AAAA-MM-DD
                    dt = datetime.strptime(fecha_raw, "%Y-%m-%d")
                    mes_es_det = meses_es[calendar.month_name[dt.month].lower()]
                    fecha = f"{dt.day} de {mes_es_det.lower()} de {dt.year}"

                lineas.append(f"  • El {fecha} de {inicio} a {fin} (servicio {servicio})")

    return "\n".join(lineas)

HorariosPrompt = formatear_horarios_prompt_es_v3(horarios_tabla)
print("Horarios formateados para prompt:\n", HorariosPrompt)