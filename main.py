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

    print("Please upload Conversion data as a csv file")
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
    
    conversion_y_labels = conversion['hour'].unique()
    
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
    def count_weekdays(data_to_use):
      start_date =  datetime.strptime(data_to_use.index.min(), '%m/%d/%Y %H:%M:%S').date()
      end_date =  datetime.strptime(data_to_use.index.max(), '%m/%d/%Y %H:%M:%S').date()

      day_counts = {
          'Monday': 0,
          'Tuesday': 0,
          'Wednesday': 0,
          'Thursday': 0,
          'Friday': 0,
          'Saturday': 0,
          'Sunday': 0
      }

      current_date = start_date
      while current_date <= end_date:
          weekday_name = current_date.strftime('%A')
          day_counts[weekday_name] += 1
          current_date += timedelta(days=1)

      return day_counts

    # Apply function
    conversion_day_counts = count_weekdays(conversion)
    traffic_day_counts = count_weekdays(traffic)


    # Convert 1,2,3 to Mon Tues Wed
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_dict = {idx+1: day for idx, day in enumerate(days)}


    # Create Callbacks
    @app.callback(
        Output('heatmap', 'figure'),
        Input('metric-radio', 'value')
    )

    # function for upgrading table
    def update_figure(selected_metric):
        if selected_metric in ['Sales', 'Orders', 'Order Items']:
          heatmap_data = conversion.pivot_table(index='hour', columns='day', values=selected_metric, aggfunc='mean').fillna(0).divide(conversion_day_counts.values())

          fig = go.Figure(data=go.Heatmap(
              z=heatmap_data.values,
              x=heatmap_data.columns.map(day_dict),
              y=heatmap_data.index.tolist(),
              colorscale='RdBu'
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
          fig.update_yaxes(title_text="Hours", tickvals=np.arange(len(conversion_y_labels)), ticktext=sorted(conversion_y_labels))
          fig.update_xaxes(title_text="Days",
                          tickvals=heatmap_data.columns.map(day_dict),
                          ticktext=heatmap_data.columns.map(day_dict))
          return fig
        else:
          heatmap_data = traffic.pivot_table(index='hour', columns='day', values=selected_metric, aggfunc='mean').fillna(0).divide(traffic_day_counts.values())

          fig = go.Figure(data=go.Heatmap(
              z=heatmap_data.values,
              x=heatmap_data.columns.map(day_dict),
              y=heatmap_data.index.tolist(),
              colorscale='RdBu'
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
          fig.update_yaxes(title_text="Hours", tickvals=np.arange(len(conversion_y_labels)), ticktext=sorted(traffic_y_labels))
          fig.update_xaxes(title_text="Days",
                          tickvals=heatmap_data.columns.map(day_dict),
                          ticktext=heatmap_data.columns.map(day_dict))
          return fig


    app.run(jupyter_mode='external')
