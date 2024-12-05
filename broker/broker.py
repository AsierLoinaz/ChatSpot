import sqlite3
from paho.mqtt.client import Client # type: ignore
import json
import time

# Configuración de MQTT
BROKER_ADDRESS = "localhost"  # Cambia a '127.0.0.1' si es necesario
TOPIC = "chatspot"

# Configuración de la base de datos SQLite
DB_FILE = "ChatSpot.db"

# Initalize database if it does not exist
def initialize_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

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

# Get mqtt message and handle them
def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")  
    print(f"Mensaje recibido: {payload} en el topic {msg.topic}")
    
    try:
        # Gets the json in the message
        data = json.loads(payload)
        print(data)
        questionsDict = data.get("questionsDict", {})
        convDuration = data.get("convDuration", 0)
        waitTime = data.get("waitTime", 0)  # Tiempo de espera entre preguntas

        print(waitTime)

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Insert data on the database
        for pregunta_text, duracion_pregunta in questionsDict.items():
            
            cursor.execute("SELECT id FROM pregunta WHERE pregunta = ?", (pregunta_text,))
            result = cursor.fetchone()

            if result: # If the question already exists, do not add it to the questions table
                id_pregunta = result[0]  # Recuperar el ID existente
            else:
                # New questions, add it to db
                cursor.execute("INSERT INTO pregunta (pregunta) VALUES (?)", (pregunta_text,))
                id_pregunta = cursor.lastrowid
            # Add conversation to db
            cursor.execute("""
                INSERT INTO conversacion (id_pregunta, duracion, numero_preguntas, tiempo_espera)
                VALUES (?, ?, ?, ?)
            """, (id_pregunta, convDuration, len(questionsDict), waitTime))
            id_conversacion = cursor.lastrowid

            # Add question duration to db
            cursor.execute("""
                INSERT INTO tiempoPregunta (id_pregunta, id_conversacion, duracion_pregunta)
                VALUES (?, ?, ?)
            """, (id_pregunta, id_conversacion, duracion_pregunta))

        conn.commit()
        conn.close()

        print("Data sucessfully stored in DB.")
    except Exception as e:
        print(f"Error processing message: {e}")


# MQTT configuration and main 
def main():
    initialize_db()
    # MQTT broker address and topic subscription
    client = Client()
    client.on_message = on_message  
    client.connect(BROKER_ADDRESS)  

    client.subscribe(TOPIC)  
    print(f"Conected to broker in {BROKER_ADDRESS} y and subscribed to '{TOPIC}'")
    
    client.loop_forever()  # Loop forever to keep listening

if __name__ == "__main__":
    main()
    