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

external_stylesheet = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

dash = Dash(server=app, routes_pathname_prefix="/dashboard/")
# dash_app = Dash( external_stylesheets=[dbc.themes.SKETCHY])
dash_app = Dash( external_stylesheets=external_stylesheet)




@dash.callback(
    [Output('total', 'figure'),
     Output('his-graph', 'figure'),
     Output('bubble-graph', 'figure'),
     Output('ptt-table', 'figure'),
     Output('quiz-table', 'figure'),
     Output('line-plot', 'figure')],
    Input('group-selector', 'value')
    )


def update_graph(selected_groups):
    totalrevenue=all_store()
    google=drink_google_result()
    keyword=hot_keyword()
    boba=boba_tea()
    url,push,title=hot_article()
    url_quiz,title_quiz=drink_quiz()
    lines,layout=update_line_plot(selected_groups)
    

    fig_bar = go.Figure(data=[
        go.Bar(go.Bar(x=list(google.keys()), y=list(google.values())))
    ])
    fig_bar.update_layout(barmode='stack')

    # fig = go.Figure(data=[go.Table(
    #     columnorder = [1,2],
    #     columnwidth = [20,100],
    #     header=dict(values=['排行', '熱門關鍵字'],
    #                 line_color='darkslategray',
    #                 align='left'),
    #     cells=dict(values=[[1,2,3,4,5], 
    #                     keyword], 
    #             line_color='darkslategray',
    #             align='left'))
    #             ]) 
    
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

    fig_group = go.Figure(data=lines, layout=layout)

    link_list = [
        html.A(titl, href=ur, target="_blank")
        for titl, ur in zip(title, url)
        ]
    
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
    
    _quiz= go.Figure(data=[go.Table(
        columnwidth = [100,100],
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
    
    
    return fig_all,bubble_fig,fig_bar,fig_group, fig_ptt,_quiz


dash.layout = html.Div([
    html.Div(id='total-revenue', children='', style={'width': '49%'}),
             dcc.Graph(id='his-graph', figure={}, style={'width': '49%', 'display': 'inline-block'}),
             dcc.Graph(id='total', figure={}, style={'width': '49%', 'display': 'inline-block'}),
             
             dcc.Graph(id='ptt-table',figure={}, style={'width': '49%', 'display': 'inline-block'}),
             dcc.Graph(id='quiz-table',figure={}, style={'width': '49%', 'display': 'inline-block'}),
             dcc.Graph(id='bubble-graph',figure={}, style={'width': '49%', 'display': 'inline-block'}),
             dcc.Graph(id='line-plot',figure={}, style={'width': '80%', 'display': 'inline-block'}),
             dcc.Dropdown(
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
                value=['茶湯會','迷客夏','一沐日','五十嵐','大苑子'], 
                multi=True, 
            )
             
    ])

'''
dash.layout = html.Div([
    html.Div([
        dcc.Dropdown(
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
        ),
    ], style={'width': '80%', 'display': 'inline-block'}),
    
    html.Br(),
    
    dcc.Graph(id='line-plot', figure={}, style={'width': '80%', 'display': 'inline-block'}),
    dcc.Graph(id='his-graph', figure={}, style={'width': '49%', 'display': 'inline-block'}),
    dcc.Graph(id='ptt-table', figure={}, style={'width': '49%', 'display': 'inline-block'}),
    dcc.Graph(id='quiz-table', figure={}, style={'width': '49%', 'display': 'inline-block'}),
    dcc.Graph(id='bubble-graph', figure={}, style={'width': '49%', 'display': 'inline-block'}),
    
])
'''