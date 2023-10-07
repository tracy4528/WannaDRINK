import os
from datetime import datetime
from dotenv import load_dotenv
import pymysql
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import sys
# sys.path.append('/Users/tracy4528/Desktop/appwork/01personal/APP')
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

def hot_keyword():
    cursor = conn.cursor()
    sql = """SELECT keyword FROM hot_keyword order by id desc limit 1;"""
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    keyword= data[0]['keyword'].split(',')
    result_list = [item.strip() for item in keyword if item.strip()]
    return result_list

def boba_tea():
    cursor = conn.cursor()
    sql = """SELECT store, store_review_number,price FROM product.drink_list where name ='珍珠奶茶' order by price desc limit 20 ;"""
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    shops = []
    reviews = []
    prices = []
    for item in data:
        shop=item['store']
        review=item['store_review_number']
        price=item['price']
        shops.append(shop)
        reviews.append(review)
        prices.append(price)

    return shops, reviews, prices

dash = Dash(server=app, routes_pathname_prefix="/dashboard/")


dash_app = Dash( external_stylesheets=[dbc.themes.SKETCHY])


dash.config.suppress_callback_exceptions = True

@dash.callback(
    [Output('total-revenue', 'children'),
     Output('total', 'figure'),
     Output('bar-graph', 'figure'),
     Output('graph', 'figure'),
     Output('bubble-graph', 'figure')])


def update_graph():
    totalrevenue=all_store()
    google=drink_google_result()
    keyword=hot_keyword()
    boba=boba_tea()

    fig_bar = go.Figure(data=[
        go.Bar(go.Bar(x=list(google.keys()), y=list(google.values())))
    ])
    fig_bar.update_layout(barmode='stack')

    fig = go.Figure(data=[go.Table(
        header=dict(values=['排行', '熱門關鍵字'],
                    line_color='darkslategray',
                    align='left'),
        cells=dict(values=[[1,2,3,4,5], 
                        keyword], 
                line_color='darkslategray',
                align='left'))
                ]) 
    
    fig_all = go.Figure(data=[go.Table(
        header=dict(values=['總店家數']),
        cells=dict(values=[totalrevenue]))
                ]) 
    
    size = boba[2]
    stores=boba[0]
    bubble_fig = go.Figure(data=[go.Scatter(
    x=boba[1],
    y=boba[2],
    mode='markers',
    marker=dict(
        size=size,
        sizemode='area',
        sizeref=2.*max(size)/(40.**2),
        sizemin=4
    ),text=stores
)])
    
    
    
    return fig_all,bubble_fig,fig,fig_bar,f'Total store: {str(totalrevenue)}'

fig_all,bubble_fig,fig,fig_bar,text1=update_graph()



dash.layout = html.Div([
    html.Div(id='total-revenue', children=text1, style={'width': '49%'}),
             dcc.Graph(id='his-graph', figure=fig_bar, style={'width': '49%', 'display': 'inline-block'}),
             dcc.Graph(id='total', figure=fig_all, style={'width': '49%', 'display': 'inline-block'}),
             dcc.Graph(id='graph',figure=fig, style={'width': '49%', 'display': 'inline-block'}),
             dcc.Graph(id='bubble-graph',figure=bubble_fig, style={'width': '49%', 'display': 'inline-block'})
    ])

