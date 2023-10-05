import os
from datetime import datetime
from dotenv import load_dotenv
import pymysql
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import sys
sys.path.append('/Users/tracy4528/Desktop/appwork/01personal/APP')
from server import app
from config import MysqlConfig
import pandas as pd
import plotly.express as px


load_dotenv()

my_db_conf = MysqlConfig()
conn = pymysql.connect(**my_db_conf.db_config)

def all_store():
    cursor = conn.cursor()

    sql = """SELECT count(*) FROM store_info;"""
    cursor.execute(sql)
    data = cursor.fetchone()
    cursor.close()
    return data['count(*)']

def drink_google_result():
    cursor = conn.cursor()
    sql = """SELECT article_stat, store FROM google_search_article group by store order by article_stat desc limit 10;"""
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    result = {}
    for item in data:
        store=item['store']
        stat=item['article_stat']
        result[store] = stat

    return result
print(drink_google_result().keys)

dash = Dash(server=app, routes_pathname_prefix="/admin/dashboard.html/")
dash.config.suppress_callback_exceptions = True

@dash.callback(
    [Output('total-revenue', 'children'),
     Output('bar-graph', 'figure')])


def update_graph():
    totalrevenue=all_store()
    google=drink_google_result()

    fig_bar = go.Figure(data=[
        go.Bar(go.Bar(x=list(google.keys()), y=list(google.values())))

    ])
    fig_bar.update_layout(barmode='stack')
    
    return fig_bar,f'Total store: {str(totalrevenue)}'

fig_bar,text1=update_graph()



dash.layout = html.Div([
    html.Div(id='total-revenue', children=text1, 
             style={'width': '49%'}),
             dcc.Graph(id='his-graph', figure=fig_bar, style={'width': '49%', 'display': 'inline-block'})
    ])

