from components.openai_component import OpenAIManager

openai = OpenAIManager()


# Datos de ejemplo
cliente = {
    "celular": "+51987654321",
    "estado": "nuevo"
}

cliente_nuevo = True
campania = "Promoción Especial de Mayo - 40% de descuento en la consulta inicial"

# Llamada a la función

mensaje = "que citas tienes para el martes 28?"

mensaje_respuesta = openai.consulta_test_original(cliente, cliente_nuevo, campania, mensaje)


# Visualización del resultado
print(mensaje_respuesta)