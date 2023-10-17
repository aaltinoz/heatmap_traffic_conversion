# !pip install dash jupyter-dash # uncomment code if you are not running on google colab
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from jupyter_dash import JupyterDash
import datetime
from datetime import datetime
from google.colab import files
from plotly.graph_objs import Figure
from datetime import datetime, timedelta

def run_dash_app():
    STORE_NAME = input("Please enter store name: ")
    print("Please upload Conversion data as a csv file")
    uploaded = files.upload()

    for fn in uploaded.keys():
        print('User uploaded file "{name}" with length {length} bytes'.format(name=fn, length=len(uploaded[fn])))

    #Get data
    filename = list(uploaded.keys())[0] 
    conversion = pd.read_csv(filename)

      
    print("Please upload Traffic data as a csv file")
    uploaded = files.upload()

    for fn in uploaded.keys():
        print('User uploaded file "{name}" with length {length} bytes'.format(name=fn, length=len(uploaded[fn])))

    #Get data
    filename = list(uploaded.keys())[0]
    traffic = pd.read_csv(filename)
    
    # preprocess for conversion
    conversion.index = pd.to_datetime(conversion['publish_time']).dt.strftime('%m/%d/%Y %H:%M:%S')
    conversion['Sales'] = conversion.iloc[:, 8]
    conversion['Orders'] = conversion.iloc[:, 16]
    conversion['Order Items'] = conversion.iloc[:, 22]
    
    
    
    # preprocess for traffic
    traffic.index = pd.to_datetime(traffic['publish_time']).dt.strftime('%m/%d/%Y %H:%M:%S')
    traffic = traffic.rename(columns={'impressions':'Impressions',
                              'clicks': 'Clicks',
                              'cost': 'Cost'})
    traffic_y_labels=traffic['hour'].unique()


    # Start Dash App
    app = dash.Dash(__name__)


    # Set layout
    app.layout = html.Div([
        dcc.RadioItems(
            id='metric-radio',
            options=[{'label': i, 'value': i} for i in ['Sales', 'Orders', 'Order Items','Impressions', 'Clicks', 'Cost']],
            value='Sales',
            style={"fontFamily": "Oswald", "fontSize": "18px"}
        ),
        dcc.Graph(id='heatmap')]
    )

    # Function for determining how many weekdays in data
    def count_weekdays(datetime_index):
        # Define the order of weekdays
        order_of_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # Get the weekday names for each date in the DateTimeIndex
        weekdays = pd.to_datetime(datetime_index).day_name()

        # Use value_counts to count the occurrences of each weekday
        day_counts_unsorted = weekdays.value_counts().to_dict()

        # Sort the dictionary based on the order of weekdays and filter out zeros
        day_counts = {day: day_counts_unsorted.get(day, 0) for day in order_of_days if day_counts_unsorted.get(day, 0) != 0}
        
        return day_counts

    # Apply function
    conversion_day_counts = count_weekdays(conversion.index)
    traffic_day_counts = count_weekdays(traffic.index)


    # Create Callbacks
    @app.callback(
        Output('heatmap', 'figure'),
        Input('metric-radio', 'value')
    )

    # function for upgrading table
    def update_figure(selected_metric):
        if selected_metric in ['Sales', 'Orders', 'Order Items']:
          heatmap_data = conversion.pivot_table(index='hour', columns='day', values=selected_metric, aggfunc='sum').fillna(0).divide(conversion_day_counts.values())

          fig = go.Figure(data=go.Heatmap(
              z=heatmap_data.values,
              x=pd.Series(conversion_day_counts.keys()),
              y=[str(val) for val in heatmap_data.index],
              colorscale='Greens'
          ))
          fig.update_layout(title=f'{STORE_NAME} {selected_metric} Heatmap ',
                            xaxis_title='Date',
                            yaxis_title='Hour of Day',
                            width=1000,
                            height=600,
                            font=dict(
                                family='Roboto'
                            )
                            )

          return fig
        else:
          heatmap_data = traffic.pivot_table(index='hour', columns='day', values=selected_metric, aggfunc='sum').fillna(0).divide(traffic_day_counts.values())

          fig = go.Figure(data=go.Heatmap(
              z=heatmap_data.values,
              x=pd.Series(traffic_day_counts.keys()),
              y=[str(val) for val in heatmap_data.index],
              colorscale='Greens'
          ))
          fig.update_layout(title=f'{STORE_NAME} {selected_metric} Heatmap ',
                            xaxis_title='Date',
                            yaxis_title='Hour of Day',
                            width=1000,
                            height=600,
                            font=dict(
                                family='Roboto'
                            )
                            )
          return fig


    app.run(jupyter_mode='external')

