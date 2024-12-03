import sqlite3
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Archivo de la base de datos
DB_FILE = "ChatSpot.db"

# Inicializar la aplicación Dash
app = dash.Dash(__name__, external_stylesheets=["https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"])
app.title = "ChatSpot Statistics"

# Función para recuperar datos de la base de datos
def fetch_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Duraciones de las conversaciones
    df_conversations = pd.read_sql_query("SELECT duracion FROM conversacion", conn)

    # Top 5 preguntas que más tiempo tardan
    top_5_longest = pd.read_sql_query("""
        SELECT p.pregunta, AVG(tp.duracion_pregunta) AS avg_time
        FROM tiempoPregunta tp
        JOIN pregunta p ON tp.id_pregunta = p.id
        GROUP BY tp.id_pregunta
        ORDER BY avg_time DESC
        LIMIT 5
    """, conn)

    # Preguntas que menos tiempo tardan
    top_5_shortest = pd.read_sql_query("""
        SELECT p.pregunta, AVG(tp.duracion_pregunta) AS avg_time
        FROM tiempoPregunta tp
        JOIN pregunta p ON tp.id_pregunta = p.id
        GROUP BY tp.id_pregunta
        ORDER BY avg_time ASC
        LIMIT 5
    """, conn)

    conn.close()
    return df_conversations, top_5_longest, top_5_shortest

# Layout de la aplicación
app.layout = html.Div([
    html.H1("ChatSpot Statistics", className="text-center mt-4"),
    
    # Gráfico 1: Boxplot de las duraciones de las conversaciones
    html.Div([
        dcc.Graph(id="boxplot-durations-graph"),
    ], className="mb-4"),

    # Gráfico 2: Top 5 preguntas que más tiempo tardan
    html.Div([
        html.H3("Top 5 Longest Questions", className="text-center"),
        dcc.Graph(id="top-5-longest-graph"),
    ], className="mb-4"),

    # Gráfico 3: Preguntas que menos tiempo tardan
    html.Div([
        html.H3("Top 5 Shortest Questions", className="text-center"),
        dcc.Graph(id="top-5-shortest-graph"),
    ], className="mb-4"),

    # Auto-actualización cada 5 segundos
    dcc.Interval(id="interval-update", interval=5000, n_intervals=0)
], className="container")

# Callbacks para actualizar los gráficos en tiempo real
@app.callback(
    [Output("boxplot-durations-graph", "figure"),
     Output("top-5-longest-graph", "figure"),
     Output("top-5-shortest-graph", "figure")],
    [Input("interval-update", "n_intervals")]
)
def update_graphs(n_intervals):
    df_conversations, top_5_longest, top_5_shortest = fetch_data()

    # Gráfico 1: Boxplot de las duraciones de las conversaciones
    if not df_conversations.empty:
        boxplot_fig = px.box(
            df_conversations,
            y="duracion",
            title="Conversation Durations (Boxplot)",
            labels={"duracion": "Duration (s)"}
        )
    else:
        boxplot_fig = go.Figure()
        boxplot_fig.update_layout(title="Conversation Durations (No Data)")

    # Gráfico 2: Top 5 preguntas que más tiempo tardan
    if not top_5_longest.empty:
        top_5_longest_fig = px.bar(top_5_longest, x="avg_time", y="pregunta", orientation="h", color="avg_time",
                                    title="Top 5 Longest Questions", labels={"avg_time": "Average Time (s)", "pregunta": "Question"})
    else:
        top_5_longest_fig = go.Figure()
        top_5_longest_fig.update_layout(title="Top 5 Longest Questions (No Data)")

    # Gráfico 3: Preguntas que menos tiempo tardan
    if not top_5_shortest.empty:
        top_5_shortest_fig = px.bar(top_5_shortest, x="avg_time", y="pregunta", orientation="h", color="avg_time",
                                     title="Top 5 Shortest Questions", labels={"avg_time": "Average Time (s)", "pregunta": "Question"})
    else:
        top_5_shortest_fig = go.Figure()
        top_5_shortest_fig.update_layout(title="Top 5 Shortest Questions (No Data)")

    return boxplot_fig, top_5_longest_fig, top_5_shortest_fig

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run_server(debug=True)
