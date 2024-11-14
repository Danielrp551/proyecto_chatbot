import requests
import json
from datetime import datetime, timedelta

class ZohoCRMManager:
    def __init__(self, client_id, client_secret, redirect_uri, refresh_token):
        self.api_base_url = "https://www.zohoapis.com/crm/v2"
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.refresh_token = refresh_token
        self.access_token = None  # Inicializa el access_token como None
        self.headers = {}  # Inicializa headers como un diccionario vacío
        self.refresh_access_token()  # Refresca el access_token al iniciar la instancia

    def refresh_access_token(self):
        """Refresca el access token y actualiza los headers."""
        url = "https://accounts.zoho.com/oauth/v2/token"
        params = {
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token'
        }
        response = requests.post(url, params=params)
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens.get('access_token')
            self.headers['Authorization'] = f'Zoho-oauthtoken {self.access_token}'
            self.headers['Content-Type'] = 'application/json'
            print("Access token actualizado.")
        else:
            print(f"Error al refrescar el access token: {response.text}")

    def _request_with_token_refresh(self, method, url, **kwargs):
        """Realiza una solicitud y refresca el token en caso de error de autenticación."""
        response = requests.request(method, url, headers=self.headers, **kwargs)
        if response.status_code == 401:  # Unauthorized, probablemente el token ha expirado
            print("El access token ha expirado. Intentando refrescar el token...")
            self.refresh_access_token()
            # Reintenta la solicitud con el nuevo token
            response = requests.request(method, url, headers=self.headers, **kwargs)
        return response

    def obtener_leads_formateados(self, limit=10):
        """
        Obtiene una lista de leads formateados desde Zoho con un límite específico.

        :param limit: Número de leads a obtener, por defecto es 10.
        :return: Lista de diccionarios con los datos formateados de los leads.
        """
        # Obtener los leads de Zoho utilizando el método existente
        leads = self.obtener_todos_los_leads(limit=limit)
        
        # Lista para almacenar los leads formateados
        leads_formateados = []
        
        # Extraer y formatear la información relevante de cada lead
        for lead in leads:
            lead_formateado = {
                "ID": lead.get("id", "ID no disponible"),
                "Nombre": lead.get("First_Name", "") + " " + lead.get("Last_Name", ""),
                "Email": lead.get("Email", "No disponible"),
                "Teléfono": lead.get("Mobile", "No disponible"),
                "Fuente del Lead": lead.get("Lead_Source", "No disponible"),
                "Estado": lead.get("Lead_Status", "No disponible"),
                "Fecha de Creación": lead.get("Fecha_creacion", "No disponible"),
                "Prioridad": lead.get("Prioridad_Lead", "No disponible"),
                "Descripción": lead.get("Description", "No disponible")
            }
            leads_formateados.append(lead_formateado)
        
        return leads_formateados
    

    def obtener_todos_los_leads(self, limit=None):
        """
        Obtiene una lista de leads desde Zoho CRM, con un límite opcional.
        
        Args:
            limit (int): Cantidad máxima de leads a recuperar.
            
        Returns:
            list: Lista de leads.
        """
        url = f"{self.api_base_url}/Leads"
        params = {}
        
        # Establecemos el límite de resultados en los parámetros, si se especifica
        if limit:
            params['per_page'] = limit
            params['page'] = 1

        response = self._request_with_token_refresh("GET", url, params=params)
        if response.status_code == 200:
            leads = response.json().get('data', [])
            print(f"Se obtuvieron {len(leads)} leads.")
            return leads
        else:
            print(f"Error al obtener los leads: {response.text}")
            return []

    def obtener_todos_los_clientes(self, limit=None):
        url = f"{self.api_base_url}/Contacts"
        params = {}
        
        # Si se especifica un límite, lo incluimos en los parámetros
        if limit:
            params['per_page'] = limit

        response = self._request_with_token_refresh("GET", url, params=params)
        if response.status_code == 200:
            contactos = response.json().get('data', [])
            return contactos
        else:
            print(f"Error al obtener los contactos: {response.text}")
            return []

    def obtener_cliente_por_id(self, contact_id):
        url = f"{self.api_base_url}/Contacts/{contact_id}"
        response = self._request_with_token_refresh("GET", url)
        if response.status_code == 200:
            contacto = response.json().get('data', [])[0]
            return contacto
        else:
            print(f"Error al obtener el contacto: {response.text}")
            return None

    def crear_cliente(self, cliente_data):
        url = f"{self.api_base_url}/Contacts"
        data = {
            "data": [
                cliente_data
            ],
            "trigger": [
                "workflow"
            ]
        }
        response = self._request_with_token_refresh("POST", url, data=json.dumps(data))
        if response.status_code == 201:
            print("Cliente creado exitosamente.")
            return response.json()
        else:
            print(f"Error al crear el cliente: {response.text}")
            return None

    # Repite la misma estructura en los otros métodos (actualizar_cliente, eliminar_cliente, etc.)
    def obtener_leads_filtrados(self, fecha_creacion=None, lead_status=None, campaign_name=None, limit=10):
        """
        Obtiene leads de Zoho CRM con filtros aplicados directamente en la solicitud.

        Args:
            fecha_creacion (str): Filtra los leads por fecha de creación (en formato 'YYYY-MM-DD').
            lead_status (str): Filtra los leads por estado del lead.
            campaign_name (str): Filtra los leads por nombre de campaña.
            limit (int): Cantidad máxima de leads a recuperar.

        Returns:
            list: Lista de leads que cumplen con los filtros.
        """
        url = f"{self.api_base_url}/Leads"
        params = {
            'per_page': limit,
            'page': 1
        }
        
        # Construimos el criterio de búsqueda de forma dinámica
        criteria = []
        
        # Filtro por fecha de creación (solo si el campo es soportado por Zoho)
        if fecha_creacion:
            criteria.append(f"(Fecha_creacion:after:{fecha_creacion})")
        
        # Filtro por estado del lead
        if lead_status:
            criteria.append(f"(Lead_Status:equals:{lead_status})")
        
        # Filtro por nombre de campaña, usando el nombre exacto del campo
        if campaign_name:
            criteria.append(f"(Campaing_Name:equals:{campaign_name})")
        
        # Unimos los criterios con "and" para hacer una consulta avanzada
        if criteria:
            params['criteria'] = ' and '.join(criteria)
        
        response = self._request_with_token_refresh("GET", url, params=params)
        if response.status_code == 200:
            leads = response.json().get('data', [])
            print(f"Se obtuvieron {len(leads)} leads filtrados directamente desde Zoho.")
            return leads
        else:
            print(f"Error al obtener los leads filtrados: {response.text}")
            return []

    def formatear_lead(self, lead):
        """
        Toma un diccionario de lead y devuelve un string con los detalles formateados para imprimir.

        Args:
            lead (dict): Diccionario con la información del lead.

        Returns:
            str: Cadena formateada con los detalles del lead.
        """
        # Extrae cada campo o asigna un valor por defecto si no está disponible
        id_lead = lead.get("id", "ID no disponible")
        nombre = f"{lead.get('First_Name', 'Nombre no disponible')} {lead.get('Last_Name', 'Apellido no disponible')}"
        email = lead.get("Email", "Email no disponible")
        telefono = lead.get("Mobile", "Teléfono no disponible")
        fuente = lead.get("Lead_Source", "Fuente no disponible")
        estado = lead.get("Lead_Status", "Estado no disponible")
        fecha_creacion = lead.get("Fecha_creacion", "Fecha de creación no disponible")
        prioridad = lead.get("Prioridad_Lead", "Prioridad no disponible")
        descripcion = lead.get("Description", "Descripción no disponible")
        campaña = lead.get("Campaing_Name", "Campaña no disponible")

        # Formateamos los detalles en un string legible
        lead_formateado = (
            f"ID: {id_lead}\n"
            f"Nombre: {nombre}\n"
            f"Email: {email}\n"
            f"Teléfono: {telefono}\n"
            f"Fuente del Lead: {fuente}\n"
            f"Estado: {estado}\n"
            f"Fecha de Creación: {fecha_creacion}\n"
            f"Prioridad: {prioridad}\n"
            f"Descripción: {descripcion}\n"
            f"Campaña: {campaña}\n"
        )

        return lead_formateado