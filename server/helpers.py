import re
import datetime

def extract_datetime(message):
    print("Mensaje recibido:", repr(message))
    # Expresiones regulares para distintos formatos de fecha y hora
    date_patterns = [
        r'(\d{4}-\d{2}-\d{2})',  # AAAA-MM-DD
        r'(\d{2}/\d{2}/\d{4})',  # DD/MM/AAAA
        r'(\d{1,2} de [a-zA-Z]+)',  # D de Mes
    ]
    
    time_patterns = [
        r'(\d{1,2}:\d{2} ?[apAP]\.?[mM]\.?)',  # HH:MM AM/PM con o sin puntos
        r'(\d{1,2}:\d{2})',  # HH:MM (24 horas)
    ]
    
    # Buscar fecha en el mensaje
    user_date = None
    for pattern in date_patterns:
        match = re.search(pattern, message)
        if match:
            date_str = match.group(0)
            try:
                if '-' in date_str:
                    user_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                elif '/' in date_str:
                    user_date = datetime.datetime.strptime(date_str, '%d/%m/%Y').date()
                else:
                    day, month = date_str.split(' de ')
                    month_dict = {
                        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
                        "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
                    }
                    user_date = datetime.date(datetime.datetime.now().year, month_dict[month.lower()], int(day))
            except ValueError:
                continue

            print("User date",user_date)

    # Buscar hora en el mensaje
    user_time = None
    for pattern in time_patterns:
        match = re.search(pattern, message)
        if match:
            time_str = match.group(0)
            print("Hora encontrada:", time_str)
            try:
                # Si incluye AM/PM en cualquier formato
                if re.search(r'[apAP][\.]?[mM][\.]?', time_str):
                    # Normalizamos el formato quitando espacios y puntos
                    time_str = re.sub(r'[\s\.]+', '', time_str).lower()
                    print("Hora normalizada y len :", time_str, time_str.__len__())
                    #user_time = datetime.datetime.strptime(time_str, '%I:%M%p').time()
                    # Procesar manualmente la hora AM/PM
                    hour, minute = map(int, time_str[:-2].split(':'))
                    am_pm = time_str[-2:]
                    if am_pm == 'pm' and hour != 12:
                        hour += 12
                    elif am_pm == 'am' and hour == 12:
                        hour = 0
                        
                    user_time = datetime.time(hour, minute)                    
                    print("User time AMPM : ",user_time)
                    break # priorizar el formato 12h
                else:
                    if not user_time:
                        user_time = datetime.datetime.strptime(time_str, '%H:%M').time()
                        print("User time 24h:", user_time)
            except ValueError as e:
                print("Error al convertir la hora : ",e)
                continue
    
    if user_date and user_time:
        # Combinar la fecha y la hora en un solo objeto de fecha y hora
        print("Fecha y hora combinadas:", user_date, user_time)
        combined_datetime = datetime.datetime.combine(user_date, user_time)
        return combined_datetime.strftime('%Y-%m-%d'), combined_datetime.strftime('%H:%M')
    elif user_date:
        return user_date.strftime('%Y-%m-%d'), None
    elif user_time:
        return None, user_time.strftime('%H:%M')
    else:
        return None, None


def formatear_fecha_hora(fecha_str, hora_str):
    # Convertir la cadena de fecha a un objeto datetime
    fecha_dt = datetime.datetime.strptime(fecha_str, '%Y-%m-%d')
    
    # Convertir la cadena de hora a un objeto datetime para formatear
    hora_dt = datetime.datetime.strptime(hora_str, '%H:%M')

    # Formatear la fecha a un formato más legible
    fecha_formateada = fecha_dt.strftime('%A %d de %B').capitalize()

    # Convertir la hora a AM/PM manualmente
    def convertir_a_am_pm(hora):
        if hora.hour < 12:
            return f"{hora.hour}:{hora.strftime('%M')} a.m."
        elif hora.hour == 12:
            return f"12:{hora.strftime('%M')} p.m."
        else:
            return f"{hora.hour - 12}:{hora.strftime('%M')} p.m."

    hora_formateada = convertir_a_am_pm(hora_dt)

    return fecha_formateada, hora_formateada
