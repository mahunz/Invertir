import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
from financialreportingdfformatted import getfinancialreportingdf,getfinancialreportingdfformatted,save_sp500_stocks_info, save_russell_info , save_self_stocks_info
from format import format

import dash_table.FormatTemplate as FormatTemplate
import dash_table as dtable

from eligibilitycheck import eligibilitycheck
from futurepricing import generate_price_df
from pandas_datareader import data as web
from datetime import datetime as dt

import pdb

# Set up global variables
stockpricedf = 1
financialreportingdf =1
discountrate=0.2
margin = 0.15


# Set up the app
app = dash.Dash(__name__)
server = app.server

app.config['suppress_callback_exceptions']=True

def getTabla(jsonDF):
    DF=pd.read_json(jsonDF, orient='split')




app.layout = html.Div([
    html.Div([
        #html.H2('Valor de la Inversión'),
        # First let users choose stocks
        html.H3('Elija la acción'),
        dcc.Dropdown(
            id='StockDropdown',
            options=save_sp500_stocks_info()+save_self_stocks_info(),
            value='mmm'
        ),
        html.H3('Gráfico del precio de la acción histórico'),
        dcc.Graph(id='my-graph'),
        html.P('')

    ],style={'width': '40%', 'display': 'inline-block'}),
    html.Div([
        html.H3('Variables críticas e indicadores'),
        dtable.DataTable(
                id='financialreportdtable',
                columns=[],
                data=[],
                editable=False,
                row_selectable=False,
                row_deletable=False,
                selected_rows=[1, 2, 3, 4, 5, 6],
                page_action='native',
                style_cell_conditional=[
                    {
                        'if': {'column_id': c},
                        'textAlign': 'left'
                    } for c in ['index']
                ],
                style_data_conditional=[
                    {'if': {'row_index': 'odd'},
                     'backgroundColor': 'rgb(248, 248, 248)',
                     }
                ],
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'fontSize': '16px',
                    'font-family': 'calibri',
                    'text_align': 'center'

                },
                style_cell={
                    'fontSize': '16px',
                    'font-family': 'calibri',
                },
            ),
        html.P(''),
        html.H3('Avisos'),
        html.Table(id='ListaAvisos'),
        html.P('')
    ], style={'width': '55%', 'float': 'right', 'display': 'inline-block'}),
    html.H3('Valuación'),
    html.Div([
        html.Label('Tasa de descuento'),
        dcc.Input(
            id='discountrate_IP',
            value=discountrate,
            type='number',
            step=0.01,

#       style={'float': 'right'}
        ),
    #    html.H4('Margen Seguridad'),
        html.Label('Margen Seguridad'),
        dcc.Input(
            id='margin_IP',
            value=margin,
            type='number',
            step=0.01
            #       style={'float': 'right'}
        ),
    ], style={'columnCount': 8}),
html.Table(id='expected-future-price-table'),
html.Div(id='InfoBalance', style={'display': 'none'}),
html.Div(id='stockprice', style={'display': 'none'})

])


# For the stocks graph
@app.callback([Output('my-graph', 'figure'),Output('stockprice', 'children')], [Input('StockDropdown', 'value')])
def update_graph(selected_dropdown_value):
    print("Buscando histórico de para gráfico stock " + selected_dropdown_value )
    stockpricedf = web.DataReader(
        selected_dropdown_value.strip(), data_source='yahoo',
        start=dt(2013, 1, 1), end=dt.now())
    return {
        'data': [{
            'x': stockpricedf.index,
            'y': stockpricedf.Close
        }]
    }, stockpricedf.to_json(date_format='iso', orient='split')


# Genera la tabla de los balances

@app.callback([Output('InfoBalance', 'children'),Output('financialreportdtable','data'),Output('financialreportdtable','columns'),Output('ListaAvisos','children')], [Input('StockDropdown', 'value')])
def CopiaInfoBalanceWeb(selected_dropdown_value):
    print("Buscando balances para stock " + selected_dropdown_value)
    InfoBalanceRes = getfinancialreportingdf(selected_dropdown_value)
    data = InfoBalanceRes.reset_index().to_dict('rows')
    columns=([{"name": i.upper(), "id": i, } for i in (InfoBalanceRes.reset_index().columns)])
    InfoBalanceResFormat = InfoBalanceRes.apply(format)
    reasonlist = eligibilitycheck(InfoBalanceResFormat)

    return InfoBalanceResFormat.to_json(orient='split'),data,columns, [html.Tr(html.Th('Lista de avisos'))] + [html.Tr(html.Td(reason)) for reason in reasonlist]


# for the expected-future-price-table
@app.callback(Output('expected-future-price-table', 'children'), [ Input('StockDropdown', 'value'),Input('InfoBalance', 'children'),Input('stockprice', 'children'),
                                                                   Input('discountrate_IP', 'value'),Input('margin_IP', 'value')])
def generate_future_price_table(selected_dropdown_value, jsonInfoBalanceRes,jsonstockpricedf,discountrate,marginrate,max_rows=10):
    print("Calculando el precio futuro " + selected_dropdown_value)

    InfoBalanceRes = pd.read_json(jsonInfoBalanceRes, orient='split')
    stockpricedf = pd.read_json(jsonstockpricedf, orient='split')

    pricedf = generate_price_df(selected_dropdown_value,InfoBalanceRes,stockpricedf,discountrate,marginrate)

    pricedf=pricedf.reset_index()
#    print(pricedf)
#    print(range(min(len(pricedf), max_rows)))
#    print(pricedf.columns)
    # Header
    return [html.Tr([html.Th(col) for col in pricedf.columns])] + [html.Tr([
        html.Td(html.B(pricedf.iloc[i][col])) if col == 'decision' else html.Td(pricedf.iloc[i][col])
        for col in pricedf.columns ]) for i in range(min(len(pricedf), max_rows))]

if __name__ == '__main__':
    app.run_server(debug=True,  port=8050)