import sqlite3
from paho.mqtt.client import Client # type: ignore
import json
import time

# Configuración de MQTT
BROKER_ADDRESS = "localhost"  # Cambia a '127.0.0.1' si es necesario
TOPIC = "chatspot"

# Configuración de la base de datos SQLite
DB_FILE = "ChatSpot.db"

# Función para inicializar la base de datos
def initialize_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Crear tablas si no existen
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pregunta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pregunta TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_pregunta INTEGER NOT NULL,
            duracion REAL NOT NULL,
            tiempo_espera REAL NOT NULL,
            numero_preguntas INTEGER NOT NULL,
            FOREIGN KEY (id_pregunta) REFERENCES pregunta (id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tiempoPregunta (
            id_pregunta INTEGER NOT NULL,
            id_conversacion INTEGER NOT NULL,
            duracion_pregunta REAL NOT NULL,
            PRIMARY KEY (id_pregunta, id_conversacion),
            FOREIGN KEY (id_pregunta) REFERENCES pregunta (id),
            FOREIGN KEY (id_conversacion) REFERENCES conversacion (id)
        )
    """)
    conn.commit()
    conn.close()

# Función para manejar el mensaje recibido
def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")  # Decodifica el mensaje recibido
    print(f"Mensaje recibido: {payload} en el topic {msg.topic}")
    
    try:
        # Suponemos que el mensaje es JSON con datos para las tablas
        data = json.loads(payload)
        print(data)
        questionsDict = data.get("questionsDict", {})
        convDuration = data.get("convDuration", 0)
        waitTime = data.get("waitTime", 0)  # Tiempo de espera entre preguntas

        print(waitTime)

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Insertar cada pregunta y asociarla a una conversación
        for pregunta_text, duracion_pregunta in questionsDict.items():
            # Insertar o recuperar la pregunta
            cursor.execute("SELECT id FROM pregunta WHERE pregunta = ?", (pregunta_text,))
            result = cursor.fetchone()

            if result:
                id_pregunta = result[0]  # Recuperar el ID existente
            else:
                # Insertar la nueva pregunta
                cursor.execute("INSERT INTO pregunta (pregunta) VALUES (?)", (pregunta_text,))
                id_pregunta = cursor.lastrowid
            # Insertar la conversación
            cursor.execute("""
                INSERT INTO conversacion (id_pregunta, duracion, numero_preguntas, tiempo_espera)
                VALUES (?, ?, ?, ?)
            """, (id_pregunta, convDuration, len(questionsDict), waitTime))
            id_conversacion = cursor.lastrowid

            # Insertar la duración de esta pregunta
            cursor.execute("""
                INSERT INTO tiempoPregunta (id_pregunta, id_conversacion, duracion_pregunta)
                VALUES (?, ?, ?)
            """, (id_pregunta, id_conversacion, duracion_pregunta))

        conn.commit()
        conn.close()

        print("Datos almacenados exitosamente en la base de datos.")
    except Exception as e:
        print(f"Error procesando el mensaje: {e}")


# Configuración del cliente MQTT
def main():
    initialize_db()
    
    client = Client()
    client.on_message = on_message  # Asigna la función de callback
    client.connect(BROKER_ADDRESS)  # Conecta al broker

    client.subscribe(TOPIC)  # Suscribirse al topic
    print(f"Conectado al broker en {BROKER_ADDRESS} y suscrito al topic '{TOPIC}'")
    
    client.loop_forever()  # Mantiene la conexión abierta

if __name__ == "__main__":
    main()
    