import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px

# ─── Data Prep ────────────────────────────────────────────────────────────────
spacex_df = pd.read_csv("spacex_launch_dash.csv")
min_payload = spacex_df["Payload Mass (kg)"].min()
max_payload = spacex_df["Payload Mass (kg)"].max()

# ─── App Definition ───────────────────────────────────────────────────────────
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1("SpaceX Launch Records Dashboard", style={'textAlign':'center'}),

    # TASK 1: Dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=(
            [{'label': 'All Sites', 'value': 'ALL'}] +
            [{'label': site, 'value': site}
             for site in sorted(spacex_df["Launch Site"].unique())]
        ),
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Pie chart
    dcc.Graph(id='success-pie-chart'),
    html.Br(),

    # TASK 3: Payload range slider
    html.P("Payload range (kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={i: str(i) for i in range(0, 10001, 2000)},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Scatter chart
    dcc.Graph(id='success-payload-scatter-chart'),
])

# ─── CALLBACK: update pie chart ────────────────────────────────────────────────
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie(entered_site):
    if entered_site == 'ALL':
        df = spacex_df.groupby("Launch Site")["class"].sum().reset_index()
        fig = px.pie(
            df,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        df = spacex_df[spacex_df["Launch Site"] == entered_site]
        counts = df['class'].value_counts().rename_axis('Outcome').reset_index(name='Count')
        counts['Outcome'] = counts['Outcome'].map({1:'Success', 0:'Failure'})
        fig = px.pie(
            counts,
            values='Count',
            names='Outcome',
            title=f"Launch Outcomes for {entered_site}"
        )
    return fig

# ─── CALLBACK: update scatter chart ────────────────────────────────────────────
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def update_scatter(entered_site, payload_range):
    low, high = payload_range
    mask = (spacex_df["Payload Mass (kg)"] >= low) & (spacex_df["Payload Mass (kg)"] <= high)
    filtered = spacex_df[mask]
    if entered_site != 'ALL':
        filtered = filtered[filtered["Launch Site"] == entered_site]

    fig = px.scatter(
        filtered,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title="Payload vs. Outcome",
        labels={"class": "Launch Outcome (1=Success, 0=Failure)"}
    )
    return fig

# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run_server(debug=True)
