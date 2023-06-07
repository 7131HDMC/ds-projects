import psycopg2 
import sqlalchemy
from sqlalchemy import create_engine
import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash_bootstrap_templates import ThemeSwitchAIO


import pandas as pd 

engine = create_engine("postgresql://postgres:admin@localhost:5432/postgres")

# df = pd.read_csv("vgsales.csv", index_col=0)
# df.to_sql("vgsales", con=engine, if_exists="replace")

df = pd.read_sql("SELECT * FROM vgsales", con=engine, index_col="Rank")

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

FONT_AWESOME = ["https://use.fontawesome.com/releases/v5.10.2/css/all.css"]
server = Flask(__name__)
app = dash.Dash(__name__, server=server,  external_stylesheets=FONT_AWESOME, suppress_callback_exceptions=True)

#
tab_card = {"height": "100%"}

main_config = {
    "hovermode": "x unified",
    "legend": {
        "yanchor": "top",
        "y": 0.9,
        "xanchor": "left",
        "x": 0.1,
        "title": {"text": None},
        "font": {"color": "white"},
        "bgcolor": "rgba(0,0,0,0.5)"
    },
    'margin': {"l":0,"r":0,"t":20,"b":0}
}
template_theme1 = "zephyr"
template_theme2= "solar"
url_theme1 = dbc.themes.ZEPHYR
url_theme2 = dbc.themes.SOLAR 

global_genres = df.groupby(["Genre"])["Global_Sales"].sum().sort_values(ascending=False).reset_index()["Genre"].unique().tolist()
global_genres.insert(0, "Global")

top_publishers = df.groupby(["Publisher"])["Global_Sales"].sum()
top_publishers = top_publishers.sort_values(ascending=False).head(10).reset_index()


df_store = df.to_dict()

app.layout = dbc.Container([
    dcc.Store(id="dataset", data=df_store),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Legend("Game Sales Metrics")
                        ], sm=8),
                        dbc.Col([
                            html.I(className="fa fa-gamepad", style={"font-size": "300%"})
                        ], sm=4, align="center")
                    ]),
                    
                    dbc.Row([
                        dbc.Col([
                            ThemeSwitchAIO(aio_id="theme",  icons={"left": "fa fa-sun", "right": "fa fa-moon"}, themes=[url_theme2, url_theme1]),
                            html.Legend("Theme")
                        ], style={"margin-top": "10px"})
                    ]),
                    dbc.Row([
                        dbc.Button("Profile", href="https://www.linkedin.com/in/hari-dasa/", target="_blank"),
                    ], style={"margin-top": "10px"}),
                ])
            ], style=tab_card)
        ],sm=4, lg=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="graph0", className="dbc", config={"displayModeBar": False, "showTips": False})
                ])
            ], style=tab_card)
        ], sm=12, lg=10)
    ], className="g-2 my-auto", style={"margin-top": "7px"}),


    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.Row([
                        dbc.Col([
                            dcc.RangeSlider(
                                id="rangeslider",
                                marks={int(x): f'{x}' for x in df["Year"].unique() },
                                step=3,
                                min=1980,
                                max=2017,
                                value=[1980, 2017],
                                dots=True,
                                pushable=3,
                                tooltip={"always_visible": False, "placement": "bottom"},
                            )
                        ], sm=12, style={"margin-top": "15px"}),
                    dcc.Interval(id="interval", interval=10000),
                ], className="g-1", style={"height":"20%", "justify-content":"center"})
            ], style=tab_card)
        ])
    ], className="g-2 my-auto", style={"margin-top": "7px"}),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                        html.H4("Top 10 Best Selling Games"),
                        dcc.Graph(id="graph1", className="dbc", config={"displayModeBar": False, "showTips":False})
                ])
            ], style=tab_card)
        ], sm=12, lg=4, style={"margin-top": "7px"}),

        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id="graph2", className="dbc", config={"displayModeBar": False, "showTips":False})

                        ])
                    ], style=tab_card)
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id="graph3", className="dbc", config={"displayModeBar": False, "showTips":False})
                            ])
                        ])
                    ], style=tab_card)
                ], sm=12, lg=4),
                dbc.Col([
                    dbc.Card([
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id="graph4", className="dbc", config={"displayModeBar": False, "showTips":False})
                            ])
                        ])
                    ], style=tab_card)
                ], sm=12, lg=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H5("Filter by Genre"),
                                    dbc.RadioItems(
                                        id="radio-genre",
                                        options=[{"label": x, "value":x} for x in global_genres],
                                        value="Global",
                                        inline=True,
                                        labelCheckedClassName="text-success",
                                        inputCheckedClassName="border border-success bg-success",
                                    ),
                                ])
                            ])
                        ])
                    ], style=tab_card)
                ], sm=12, lg=4)
            ], className="g-2 my-auto")
        ], sm=12, lg=8)
    ], justify="center", className="g-2 my-auto")

], fluid=True, style={"height": "100vh"})


### Callbacks
#Pie Charts
@app.callback(
    Output("graph0", "figure"),
    Input("rangeslider", "value"),
    Input("radio-genre", "value"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def graph0(date, radio, toggle):
    template =  template_theme2 if toggle else template_theme1

    if radio == "Global":
        mask = (df["Year"] >= date[0]) & (df["Year"] <= date[1])
    else:
        mask = (df["Year"] >= date[0]) & (df["Year"] <= date[1]) & (df["Genre"].isin([radio]))
    
    df_subplot = df.loc[mask]

    df_NA = df_subplot.sort_values(ascending=False, by="NA_Sales").head(6).rename(columns={"NA_Sales" : "Sales"})
    df_EU = df_subplot.sort_values(ascending=False, by="EU_Sales").head(6).rename(columns={"EU_Sales" : "Sales"})
    df_JP = df_subplot.sort_values(ascending=False, by="JP_Sales").head(6).rename(columns={"JP_Sales" : "Sales"})
    df_other = df_subplot.sort_values(ascending=False, by="Other_Sales").head(6).rename(columns={"Other_Sales" : "Sales"})

    subplot_topgames = make_subplots(rows=1, cols=4, specs=[[{"type": "pie"}, {"type": "pie"}, {"type": "pie"}, {"type": "pie"}]])

    subplot_topgames.add_trace(go.Pie(
        labels=df_NA["Name"], values=df_NA["Sales"], hole=.2
    ), col=1, row=1)
    subplot_topgames.add_trace(go.Pie(
        labels=df_EU["Name"], values=df_EU["Sales"], hole=.2
    ), col=2, row=1)
    subplot_topgames.add_trace(go.Pie(
        labels=df_JP["Name"], values=df_JP["Sales"], hole=.2
    ), col=3, row=1)
    subplot_topgames.add_trace(go.Pie(
        labels=df_other["Name"], values=df_other["Sales"], hole=.2
    ), col=4, row=1)

    subplot_topgames.update_layout(height=200, template=template, margin={"l":0,"r":0,"t":20,"b":0})
    
    return subplot_topgames

#Horizontal
@app.callback(
    Output("graph1", "figure"),
    Input("rangeslider", "value"),
    Input("radio-genre", "value"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def graph1(date, radio, toggle):
    template =  template_theme2 if toggle else template_theme1

    if radio == "Global":
        mask = (df["Year"] >= date[0]) & (df["Year"] <= date[1])
    else:
        mask = (df["Year"] >= date[0]) & (df["Year"] <= date[1]) & (df["Genre"].isin([radio]))
    
    df_topglobal = df.loc[mask]
    df_topglobal = df_topglobal.head(10).sort_values(by="Global_Sales", ascending=True)
    text = [f'{x} - U${y}  ' for x,y in zip(df_topglobal["Name"].unique(), df_topglobal["Global_Sales"].unique())]

    fig = go.Figure(go.Bar(
        x=df_topglobal["Global_Sales"],
        y=df_topglobal["Name"], orientation="h", text=text
    ))
    fig.update_layout(main_config, height=410, xaxis={"title": None, "showticklabels":False}, yaxis={"title": None, "showticklabels":False}, template=template)

    return fig


#Horizontal
@app.callback(
    Output("graph2", "figure"),
    Input("rangeslider", "value"),
    Input("radio-genre", "value"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def graph2(date, radio, toggle):
    template =  template_theme2 if toggle else template_theme1

    if radio == "Global":
        mask = (df["Year"] >= date[0]) & (df["Year"] <= date[1])
    else:
        mask = (df["Year"] >= date[0]) & (df["Year"] <= date[1]) & (df["Genre"].isin([radio]))
    
    df_years = df.loc[mask]
    trace = df_years.groupby("Year")["Global_Sales"].sum().reset_index()

    fig = go.Figure(go.Scatter(
        x=trace["Year"],
        y=trace["Global_Sales"],
        mode="lines+markers",
        fill="tonexty",
        name="Global Sales"
    ))
    fig.update_layout(main_config, height=200, xaxis={"title": None, "showticklabels":False}, yaxis={"title": None, "showticklabels":False}, template=template)
    fig.add_annotation(text=f'Sales from {date[0]} to {date[1]}',
        xref="paper", yref="paper",
        x=0.05, y=0.85, showarrow=False,
        font=dict(size=20, color="gray"),
        align="center", opacity=0.8, bgcolor="rgba(0,0,0,0.8)"
    )
    return fig


#Horizontal
@app.callback(
    Output("graph3", "figure"),
    Output("graph4", "figure"),
    Input("rangeslider", "value"),
    Input("radio-genre", "value"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def indicators(date, radio, toggle):
    template =  template_theme2 if toggle else template_theme1

    mask = (df["Year"] >= date[0]) & (df["Year"] <= date[1])

    df_graph4 = df_graph3 = df.loc[mask]

    df_graph3 = df_graph3.groupby(["Publisher"])["Global_Sales"].sum().reset_index()
    df_graph4 = df_graph4.groupby(["Genre"])["Global_Sales"].sum().reset_index()

    value1 = df_graph3["Global_Sales"].max()
    name1  = df_graph3.loc[df_graph3["Global_Sales"].idxmax()]["Publisher"]
    value2 = df_graph4["Global_Sales"].max()
    name2  = df_graph4.loc[df_graph4["Global_Sales"].idxmax()]["Genre"]

    fig2 = go.Figure()
    fig1 = go.Figure()

    fig1.add_trace(go.Indicator(
        mode="number",
        title={"text": f"<span style='font-size:150%'> Top Seller - {name1}</span><br><span style='font-size:0.7em'>{date[0]} - {date[1]}</span>"},
        value=value1,
        number={"valueformat": ".2f"}
    ))
    
    fig2.add_trace(go.Indicator(
        mode="number",
        title={"text": f"<span style='font-size:150%'> Top Genre - {name2} </span><br><span style='font-size:0.7em'>{date[0]} - {date[1]}</span>"},
        value=value2,
        number={"valueformat": ".2f"}
    ))

    fig1.update_layout(main_config, height=273, template=template)    
    fig2.update_layout(main_config, height=273, template=template)  

    return fig1, fig2



if __name__=="__main__":
    app.run_server(debug=True)