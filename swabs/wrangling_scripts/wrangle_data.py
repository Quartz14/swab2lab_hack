import pandas as pd
import numpy as np
import plotly.graph_objs as go
import json
import plotly.express as px
from sqlalchemy import create_engine
import sqlite3





def return_figures():
    """Creates plotly visualizations

    Args:
        None

    Returns:
        list (dict): list containing the four plotly visualizations

    """
    df_districts = pd.read_csv('data/district_sample_data_001.csv')
    df_districts = df_districts.drop(df_districts.columns[0],axis=1)
    df_districts['district_name'] = [i.lower().strip() for i in df_districts['district_name']]

    df_labs = pd.read_csv('data/lab_sample_data_001.csv')
    df_labs = df_labs.drop(df_labs.columns[0],axis=1)
    df_labs['lab_type'] = ['Public' if i==0 else 'Private' for i in df_labs['lab_type']]


    df_sol = pd.read_csv('data/solution_001.csv')
    conn = sqlite3.connect('data/swap.db')
    df_districts.to_sql('districts', con = conn, if_exists='replace', index=False)
    df_labs.to_sql('labs', con = conn, if_exists='replace', index=False)
    df_sol.to_sql('sol', con = conn, if_exists='replace', index=False)

    with open('data/karnataka_district.json','r') as file:
        k_districts = json.load(file)


    figures = []
    # No. of samples generated in each district
    fig = px.choropleth_mapbox(df_districts, geojson=k_districts, color="samples",
                           locations="district_name", featureidkey="properties.district",
                           title='No. of samples generated in each district',
                           color_continuous_scale=[[0, "yellow"], [0.05,"rgb(242,85,24)"],[0.1, 'rgb(240,5,24)'],[0.15,'rgb(198,6,44)'],[0.2,'rgb(143,17,61)'],[0.25,'rgb(128,54,60)'],[1,"blue"]],
                           #range_color=(0, 12),
                           center={"lat": 15.1, "lon": 76.5},
                           mapbox_style="carto-positron", zoom=5.5)

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(
    annotations=[
        dict(text="Color indicated number of samples<br>generated in each district", showarrow=False,
        x=0, y=0.0, yref="paper", align="left")])
    figures.append(fig)

    #Number of backlogs in each district
    district_backlogs = pd.read_sql('SELECT SUM(s.samples_transferred) as d_backlog,s.source, d.district_name from sol s  join districts d ON s.source=d.district_id where s.transfer_type=1 group by s.source', con = conn)

    fig = px.choropleth_mapbox(district_backlogs, geojson=k_districts, color="d_backlog",
                           locations="district_name", featureidkey="properties.district",
                           color_continuous_scale="YlGn",
                           center={"lat": 15.1, "lon": 76.5},
                           mapbox_style="carto-positron", zoom=5.5)

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(
    annotations=[
        dict(text="Color indicated number of allocations<br>to district headquarters", showarrow=False,
        x=0, y=0.0, yref="paper", align="left")])
    figures.append(fig)

    # District -------> Labs

    transfers = pd.read_sql('SELECT s.samples_transferred as transfer,s.destination, d.district_name as district_name,d.lat as source_lat, d.lon as source_lon, l.lat as dest_lat, l.lon as dest_lon  from sol s  join districts d ON s.source=d.district_id join labs l ON s.destination=l.id where s.transfer_type=0', con = conn)

    button_dict_list = [dict(label = 'All districts',method = 'update',
                        args = [{'visible': [True,True]+[True]*len(transfers)}])]
    dnames  =  transfers['district_name'].unique()
    dnames.sort()

    for district in dnames:
        button_dict_list.append(dict(label=district,
                                method='update',
                                args=[{'visible':[True,True,True]+list(transfers['district_name']==district)}]))

    fig = go.Figure()

    fig.add_trace(go.Choroplethmapbox(geojson=k_districts,featureidkey="properties.district", locations=df_districts['district_name']
                                  ,z=df_districts['samples'],
                                  colorscale="YlGn", zmin=0, zmax=3000,showlegend=False,
                                    marker_opacity=0.5, marker_line_width=0))

    fig.add_trace(go.Scattermapbox(
        lat= df_districts['lat'],
        lon=df_districts['lon'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10,
            color='rgb(0, 0, 0)',
            opacity=0.5
        ),
        text=df_districts['district_name'],
    ))

    #id	lat	lon	district_id	lab_type	capacity	backlogs
    fig.add_trace(go.Scattermapbox(
        lat= df_labs['lat'],
        lon=df_labs['lon'],
        mode = "markers",
        textposition = "bottom right",
        marker=go.scattermapbox.Marker(
            size=5,
            color='rgb(255, 0, 0)',
            opacity=0.8
        ),
        text=df_labs['lab_type'],
    ))

    #ransfer	destination	district_name	source_lat	source_lon	dest_lat	dest_lon
    for i in range(len(transfers)):
        fig.add_trace(
            go.Scattermapbox(
                lon = [transfers['source_lon'][i], transfers['dest_lon'][i]],
                lat = [transfers['source_lat'][i], transfers['dest_lat'][i]],
                mode="lines+text",
                textposition="top center",
                text="Transferred: "+ str(transfers['transfer'][i]),
                line=dict(color="Blue",width=2),
            #line = dict(width = 1,color = 'blue'),
            opacity = float(transfers['transfer'][i]) / float(transfers['transfer'][i].max()),
        )
    )



    #transfer	destination	district_name	source_lat	source_lon	dest_lat	dest_lon
    fig.update_layout(mapbox_style="carto-positron",
                  mapbox_zoom=5.5, mapbox_center = {"lat": 15.1, "lon": 76.5},
                 margin={"r":0,"t":0,"l":0,"b":0})


    # Add dropdown
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=list(button_dict_list),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.1,
                yanchor="top"
                ),
                ]
                )
    fig.update_traces(showlegend=False, selector=dict(type='scattermapbox'))
    fig.update_layout(
    annotations=[
        dict(text="District->Labs<br>labs that receive from a particular district", showarrow=False,
        x=0.5, y=1.1, yref="paper", align="center"),
        dict(text="District capacities<br> (samples generated)", showarrow=False,
        x=1.1, y=1.1, yref="paper", align="right"),
        dict(text="Filter by<br>district", showarrow=False,
        x=0, y=1.1, yref="paper", align="left"),
        dict(text="Districts marked with black points<br>Labs marked with red points<br>Allocation marked with blue line", showarrow=False,
        x=0, y=0.0, yref="paper", align="left")])
    figures.append(fig)
    return figures
