
import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# Load dataset
df = pd.read_csv("owid-covid-latest.csv")
df = df[df["continent"].notna()]

# Filter countries with valid data
valid_countries = df.groupby('location')['new_cases'].sum().reset_index()
valid_countries = valid_countries[valid_countries['new_cases'] > 0]['location'].tolist()

# Dash app
app = dash.Dash(__name__)
app.title = "COVID-19 Dashboard"

# Layout
app.layout = html.Div([
    html.H1("COVID-19 Interactive Dashboard", style={"textAlign": "center"}),

    dcc.Dropdown(
        id='country-dropdown',
        options=[{"label": c, "value": c} for c in valid_countries],
        value='India',
        multi=False
    ),

    dcc.Graph(id='line-chart'),
    dcc.Graph(id='bar-chart'),
])

# Robust callback
@app.callback(
    [Output('line-chart', 'figure'),
     Output('bar-chart', 'figure')],
    [Input('country-dropdown', 'value')]
)
def update_dashboard(selected_country):
    dff = df[df['location'] == selected_country]

    if dff.empty or dff['new_cases'].dropna().empty:
        return px.line(title="No data available"), px.bar(title="No data available")

    dff = dff.fillna(0)

    line_fig = px.line(
        dff, x='date', y='new_cases',
        title=f'Daily New COVID-19 Cases in {selected_country}'
    )

    try:
        latest = dff[dff['total_cases'] > 0].iloc[-1]
    except IndexError:
        return line_fig, px.bar(title="No valid total data")

    bar_fig = px.bar(
        x=['total_cases', 'total_deaths', 'total_vaccinations'],
        y=[latest['total_cases'], latest['total_deaths'], latest['total_vaccinations']],
        labels={'x': 'Metric', 'y': 'Count'},
        title=f'Total COVID-19 Stats for {selected_country}'
    )

    return line_fig, bar_fig

# Run app
if __name__ == '__main__':
    app.run(debug=True)
