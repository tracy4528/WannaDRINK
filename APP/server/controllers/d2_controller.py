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
    sql = """SELECT avg(trend_num) as trend_index,store FROM product.google_trend group by store order by trend_index desc;"""
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    result = {}
    for item in data:
        store=item['store']
        stat=item['trend_index']
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

def store_google_trend():
    cursor = conn.cursor()

    sql = """SELECT * FROM google_trend where trend_date between '2023-09-01' AND '2023-09-30' """
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    store_data = {  'Date': pd.date_range('2023-09-01', periods=30)}
    for item in data:
        store = item['store']
        trend_num = item['trend_num']
        if store not in store_data:
            store_data[store] = []
        store_data[store].append(trend_num)
    
    return store_data

def update_line_plot(selected_groups):
    data = {}
    df = pd.DataFrame(data)
    store_data=store_google_trend()
    for store, trend_nums in store_data.items():
            store_series = pd.Series(trend_nums, name=store)
            df = pd.concat([df, store_series], axis=1)
    lines = []
    for group in selected_groups:
        trace = go.Scatter(
            x=df['Date'],
            y=df[group],
            mode='lines+markers',
            name=group
        )
        lines.append(trace)

    layout = go.Layout(
        title='手搖飲過去一個月聲量比較',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Value'),
    )

    return lines,layout

def hot_article():
    cursor = conn.cursor()
    sql = """SELECT * FROM ptt_articles where crawl_date='20231003' ORDER BY push DESC limit 10"""
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    url = [item['url'] for item in data ]
    push = [item['push'] for item in data ]
    title = [item['title'] for item in data ]

    return url,push,title


def drink_quiz():
    cursor = conn.cursor()
    sql = """SELECT * FROM drink_quiz """
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    url = [item['url'] for item in data ]
    title = [item['title'] for item in data ]

    return url,title

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

dash = Dash(server=app, routes_pathname_prefix="/dashboard_/")
dash_app = Dash( external_stylesheets=[dbc.themes.MATERIA])





@dash.callback([
    Output('line-plot', 'figure'),
    Output('his-plot', 'figure'),
    Output('ptt-table', 'figure'),
    Output('quiz-table', 'figure'),
    Output('total-store', 'children'),
    Output('total-drink', 'children'),
    Output('total-brand', 'children')],
    Input('group-selector', 'value'))

def google_trend_rank(selected_groups):
    lines,layout=update_line_plot(selected_groups)
    fig_group = go.Figure(data=lines, layout=layout)
    google=drink_google_result()
    text_store=all_store()
    text_drink=12057
    text_brand=241


    fig_bar = go.Figure(data=[
        go.Bar(go.Bar(x=list(google.keys()), y=list(google.values())))
    ])
    fig_bar.update_layout(barmode='stack')

    url,push,title=hot_article()
    url_quiz,title_quiz=drink_quiz()

    fig_ptt = go.Figure(data=[go.Table(
        columnwidth = [20,100,100],
        header = dict(
            values = ['push','url','title'],
            line_color='darkslategray',
            align=['center','center','center'],
            font=dict(color='darkslategray', size=12),
            height=40
        ),
        cells=dict(
            values=[push,url,title],
            line_color='darkslategray',
            fill=dict(color= 'white'),
            align=['center', 'center','center'],
            font_size=12,
            height=30)
            )
        ])
    fig_ptt.update_layout(
        title='PTT 手搖飲版熱門文章')
    
    fig_quiz= go.Figure(data=[go.Table(
        columnwidth = [60,120],
        header = dict(
            values = ['title','url'],
            line_color='darkslategray',
            align=['center','center'],
            font=dict(color='darkslategray', size=12),
            height=40
        ),
        cells=dict(
            values=[title_quiz,url_quiz],
            line_color='darkslategray',
            fill=dict(color= 'white'),
            align=['center', 'center'],
            font_size=12,
            height=30)
            )
        ])
    fig_quiz.update_layout(
        title='手搖飲大會考')

    return fig_group, fig_bar ,fig_ptt, fig_quiz ,text_store, text_drink, text_brand



dash.layout = dbc.Container([ 
    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id='group-selector',
            options=[
                {'label': '茶湯會', 'value': '茶湯會'},
                {'label': '迷客夏', 'value': '迷客夏'},
                {'label': '一沐日', 'value': '一沐日'},
                {'label': '五十嵐', 'value': '五十嵐'},
                {'label': '大苑子', 'value': '大苑子'},
                {'label': '茶的魔手', 'value': '茶的魔手'},
                {'label': '珍煮丹', 'value': '珍煮丹'},
                {'label': '大茗', 'value': '大茗'},
                {'label': '烏弄', 'value': '烏弄'}
            ],
            value=['茶湯會', '迷客夏', '一沐日', '五十嵐', '大苑子'],
            multi=True,
        ), width=6),
    ]),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='line-plot', figure={}, style={'width': '100%', 'display': 'inline-block'}), width=12),
        dbc.Col(dcc.Graph(id='his-plot', figure={}, style={'width': '100%', 'display': 'inline-block'}), width=12)
        ]),

    html.Hr(),

    dbc.Row(
        [
            dbc.Col(
                     dcc.Graph(id='ptt-table', style={'width': '100%', 'display': 'inline-block'}), width=12
                     ),
            dbc.Col(dcc.Graph(id='quiz-table', style={'width': '100%', 'display': 'inline-block'}), width=12)
        
        ]),
    html.Br(),

    html.Br(),
    dbc.Row([dbc.Col(html.H3("已收集的店家數", className="mb-4 pl-8 pr-8"))]),
    dbc.Row([dbc.Col(html.Div(id='total-store'), width=12)],className="mb-4 pl-8 pr-8"),

    html.Br(),
    dbc.Row([dbc.Col(html.H3("已收集的飲料數", className="mb-4 pl-8 pr-8"))]),
    dbc.Row([dbc.Col(html.Div(id='total-drink'), width=12)],className="mb-4 pl-8 pr-8"),

    dbc.Row([dbc.Col(html.H3("已收集的品牌數", className="mb-4 pl-8 pr-8"))]),
    dbc.Row([dbc.Col(html.Div(id='total-brand'), width=12)],className="mb-4 pl-8 pr-8")




])


    # dbc.Row([
    #     dbc.Col(html.H3("已收集的店家數"), width=4),
    #     dbc.Col(html.H3("已收集的飲料數"), width=8),
    #     dbc.Col(html.H3("已收集的品牌數"), width=4)
    # ]),
    
    # dbc.Row([
    #     dbc.Col(html.Div(id='total-store'), width=4),
    #     dbc.Col(html.Div(id='total-drink'), width=8),
    #     dbc.Col(html.Div(id='total-brand'), width=4)
    # ]),