
from dash import Dash 
from dash.dependencies import Input, Output, State
import pandas as pd
from dash import dcc
from dash import html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import base64
import io


# Create the Dash app
app = Dash(__name__)

# Define the layout
app.layout = html.Div(
    children=[
        html.H1("Data Visualization for Emergency Response Management Services in Zimbabwe"),
        html.Div(
            children=[
                html.Label("Select a chart type:"),
                dcc.Dropdown(
                    id="chart-type",
                    options=[
                        {"label": "Bar Chart - Incidents by Type", "value": "bar"},
                        {"label": "Line Chart - Incidents over Time", "value": "line"},
                        {"label": "Pie Chart - Top 5 Incidents", "value": "pie"},
                        {"label": "Histogram - Incidents by Hour", "value": "histogram"},
                    ],
                    value="bar",
                ),
            ],
        ),
        dcc.Upload(
            id="upload-data",
            children=html.Div([
                "Drag and drop or click to select a file"
            ]),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px"
            },
            multiple=False,
        ),
        dcc.Graph(id="chart"),
    ]
)

# Define callback function to update the chart based on user selection and uploaded data
@app.callback(
    Output("chart", "figure"),
    [Input("chart-type", "value")],
    [State("upload-data", "contents")]
)
def update_chart(chart_type, uploaded_data):
    if uploaded_data is not None:
        # Read the uploaded data file as a DataFrame
        content_type, content_string = uploaded_data.split(",")
        decoded_content = base64.b64decode(content_string)
        try:
            df = pd.read_csv(io.StringIO(decoded_content.decode("utf-8")))
        except Exception as e:
            print(e)
            return go.Figure()

        if chart_type == "bar":
            # Create a bar chart of incidents by type from the uploaded data
            incidents_by_type = df["title"].value_counts().reset_index()
            incidents_by_type.columns = ["Incident Type", "Count"]
            figure = px.bar(incidents_by_type, x="Incident Type", y="Count", color="Incident Type")
        elif chart_type == "line":
            # Create a line chart of incidents over time from the uploaded data
            df["timeStamp"] = pd.to_datetime(df["timeStamp"], format="mixed")
            incidents_over_time = df.groupby(pd.to_datetime(df["timeStamp"]).dt.date).size().reset_index()
            incidents_over_time.columns = ["Date", "Count"]
            figure = px.line(incidents_over_time, x="Date", y="Count")
        elif chart_type == "pie":
            # Create a pie chart of top 5 incidents from the uploaded data
            top_5_incidents = df["title"].value_counts().nlargest(5)
            figure = px.pie(top_5_incidents, names=top_5_incidents.index, values=top_5_incidents.values)
        elif chart_type == "histogram":
            # Create a histogram of incidents by hour from the uploaded data
            df["timeStamp"] = pd.to_datetime(df["timeStamp"], format="mixed")
            df["Hour"] = pd.to_datetime(df["timeStamp"]).dt.hour
            figure = px.histogram(df, x="Hour", nbins=24)
        else:
            figure = go.Figure()

        return figure

    else:
        return go.Figure()

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
