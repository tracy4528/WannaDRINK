import os
from datetime import datetime
from dotenv import load_dotenv
import pymysql
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output,dash_table
import dash_bootstrap_components as dbc
import sys
# sys.path.append('/01personal/APP')
from server import app
from config import MysqlpoolConfig
import pandas as pd
import plotly.express as px
import mysql.connector
from mysql.connector import pooling
from server.utils.util import initialize_mysql_pool



today_date = datetime.now().strftime("%Y%m%d")
conn_pool = initialize_mysql_pool()



def all_store():
    conn = conn_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """SELECT count(*) FROM store_info;"""
    cursor.execute(sql)
    data = cursor.fetchone()

    brand_cursor = conn.cursor(dictionary=True)
    sql_brand="SELECT count(distinct store) as num FROM drink_list ;"
    brand_cursor.execute(sql_brand)
    brand_data = brand_cursor.fetchone()
    
    drink_cursor = conn.cursor(dictionary=True)
    sql_drink="SELECT count(*) as drink_num FROM drink_list;"
    drink_cursor.execute(sql_drink)
    drink_data = drink_cursor.fetchone()

    cursor.close()
    conn.close() 
    return data['count(*)'], brand_data['num'], drink_data['drink_num']

def drink_google_result():
    conn = conn_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """SELECT avg(trend_num) as trend_index,store FROM product.google_trend group by store order by trend_index desc;"""
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    result = {}
    for item in data:
        store=item['store']
        stat=item['trend_index']
        result[store] = stat
    return result


def store_google_trend():
    conn = conn_pool.get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """SELECT * FROM google_trend where trend_date between '2023-09-01' AND '2023-09-30' """
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
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
        title='上個月手搖飲品牌聲量走勢, 資料來源：google trend 手搖飲主題,此資料已對結果進行標準化為範圍從 0 到 100 的相對值',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Value'),
    )

    return lines,layout

def hot_article():
    conn = conn_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = f"SELECT * FROM ptt_articles where crawl_date='20231017' ORDER BY push DESC limit 10"
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    url = [item['url'] for item in data ]
    push = [item['push'] for item in data ]
    title = [f"<a href='{item['url']}'>{item['title']}</a>" for item in data ]
    df = pd.DataFrame({'Title': title, 'Push': push, 'URL': url})

    return df


def drink_quiz():
    conn = conn_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """SELECT * FROM drink_quiz """
    cursor.execute(sql)
    data = cursor.fetchall()
    
    url = [item['url'] for item in data ]
    title = [item['title'] for item in data ]
    cursor.close()
    conn.close()

    return url,title


external_stylesheet=['https://cdn.staticfile.org/twitter-bootstrap/4.5.2/css/bootstrap.min.css']

dash = Dash(server=app, routes_pathname_prefix="/dashboard_/",external_stylesheets=external_stylesheet)





@dash.callback([
    Output('line-plot', 'figure'),
    Output('his-plot', 'figure'),
    Output('total-store', 'children'),
    Output('total-drink', 'children'),
    Output('total-brand', 'children'),
    Output('article-table', 'data')],
    [Input('group-selector', 'value'),
     Input('interval-component', 'n_intervals')])

def dashboard(selected_groups, n_intervals):

    lines,layout=update_line_plot(selected_groups)
    fig_group = go.Figure(data=lines, layout=layout)

    google=drink_google_result()
    text_store, brand_num, drink_num=all_store()
  

    fig_bar = go.Figure(data=[
        go.Bar(go.Bar(x=list(google.keys()), y=list(google.values())))
    ])
    fig_bar.update_layout(barmode='stack', title_text='上個月手搖飲品牌聲量平均值,資料來源：google trend 手搖飲主題,此資料已對結果進行標準化為範圍從 0 到 100 的相對值')

    
    df=hot_article()
    


    return fig_group, fig_bar ,text_store, drink_num, brand_num, df.to_dict('records')



dash.layout = html.Div([ 

    dbc.Breadcrumb(
    items=[
        {
            "label": "Mainpage",
            "href": "http://127.0.0.1:5000/"
    
        },
        {"label": "Dashboard", "active": True},
    ]),
    html.Br(),
    html.Br(),


    dbc.Row(
            [
                dbc.Col(html.H3("已收集的店家數")),
                dbc.Col(html.H3("已收集的飲料數")),
                dbc.Col(html.H3("已收集的品牌數")),
            ]),

    dbc.Row(
            [
                dbc.Col(html.Div(id='total-store')),
                dbc.Col(html.Div(id='total-drink')),
                dbc.Col(html.Div(id='total-brand')),
            ]),

    html.Br(),
    html.Hr(),

    html.Br(),
    html.Br(),
    html.H5(f"手搖飲品牌聲量走勢", style={'padding-left': '30px'}),
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
        ),width =8,  style={'padding-left': '30px'}),
    ]),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='line-plot', figure={}, style={'width': '100%', 'display': 'inline-block'}), width=12),

        html.H5(f"手搖飲品牌聲量月平均", style={'padding-left': '30px'}),
        dbc.Col(dcc.Graph(id='his-plot', figure={}, style={'width': '100%', 'display': 'inline-block'}), width=12)
        ]),

    html.Br(),
    
    html.H5(f"手搖飲熱門文章", style={'padding-left': '30px'}),
    dash_table.DataTable(
        id='article-table',
        columns=[
            {'name': '文章標題', 'id': 'Title', 'presentation': 'markdown'},
            {'name': '留言數', 'id': 'Push', 'presentation': 'markdown'}
        ],
        data=None,
        markdown_options={"html": True},
        style_table={ 'padding': '30px'},
        style_header={"textAlign": "center"}
    ),

    html.Br(),
    html.Br(),

    
    html.H5("手搖飲大會考！", style={'padding': '30px'}),
    dbc.Row(
        [dbc.Col(dbc.Card([
            dbc.CardBody(
                [
                    html.P(
                        "【飲料王測驗】第一屆飲料王大測驗網址",
                        className="card-text",
                    ),
                    dbc.Button("Go", href="https://docs.google.com/forms/d/e/1FAIpQLSfRGcAtpAMz6TNpw4Hg77Dw_4Ig_1hesBICigncGvUtB7iFpA/viewform"),
                ]
            )
          ]), style={'width':'25%', 'display': 'inline-block', 'padding': '30px'} ),
        dbc.Col(dbc.Card([
            dbc.CardBody(
                [
                    html.P(
                        "【飲料王測驗】第二屆飲料王大測驗網址",
                        className="card-text",
                    ),
                    dbc.Button("Go", color="primary", href="https://docs.google.com/forms/d/e/1FAIpQLSekHa-wLDY8GjPkYNp0VSRCzKlLsYIDxwoubSe2AbV6mA3zFA/viewform"),
                ]
            )
          ]), style={'width':'25%', 'display': 'inline-block', 'padding': '30px'})
    ]),


    html.Br(),
    
    dcc.Interval(
        id='interval-component',
        interval=12*60*60*1000,  
        n_intervals=0  
    )


])

