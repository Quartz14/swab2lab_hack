import pandas as pd
import numpy as np
import plotly.graph_objs as go
import json
import plotly.express as px
from sqlalchemy import create_engine
import sqlite3





def return_figures_allocation():
    """Creates plotly visualizations

    Args:
        None

    Returns:
        list (dict): list containing the 3 plotly visualizations

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

    #ALLOCATIONS
    percent_sent = pd.read_sql('SELECT d.district_name,  d.samples as samples_generated, 100*(d.samples-s.samples_transferred)/d.samples as "percent(%) sent to labs", s.samples_transferred as samples_in_headquarters from sol s join districts d on s.source=d.district_id where s.transfer_type=1 group by s.source',con=conn)

    Color = []
    for percent in percent_sent['percent(%) sent to labs']:
        if(percent<25):
            Color.append('rgb(248, 201, 216)')
        elif(percent<50):
            Color.append('rgb(208, 216, 220)')
        elif(percent<75):
            Color.append('rgb(234, 215, 239)')
        else:
            Color.append('rgb(165, 243, 214)')



    fig = go.Figure(data=[go.Table(
        header=dict(values=['district name', 'samples generated', 'percent(%) sent to labs','samples in headquarters'],
        fill_color='paleturquoise',align='left'),
        cells=dict(values=[percent_sent.district_name, percent_sent.samples_generated, percent_sent['percent(%) sent to labs'],percent_sent.samples_in_headquarters],
        fill_color=[Color],
        align='left'))])

    fig.update_layout(
        annotations=[
            dict(text="District allocations and backlog", showarrow=False,
            x=0.5, y=1.3, yref="paper", align="center"),
            dict(text="Rows colored based on 'percent(%) sent to labs' in intervals of 25%<br>Example:rows that have sent more than 75% of generated samples<br> are colored green", showarrow=False,
            x=1, y=1.2, yref="paper", align="right")])

    figures.append(fig)
    # TABLE 2
    combined = pd.read_sql('SELECT s.destination as lab_id ,SUM(s.samples_transferred) as "samples transfered", l.capacity as "lab capacity", l.backlogs as "backlogs in lab", l.capacity-l.backlogs-SUM(s.samples_transferred)  as "remaining capacity in lab" FROM sol s JOIN labs l ON s.destination=l.id WHERE s.transfer_type=0 GROUP BY s.destination', con = conn)

    fig = go.Figure(data=[go.Table(
    header=dict(values=list(combined.columns),
        fill_color='paleturquoise',align='left'),
        cells=dict(values=[combined.lab_id, combined["samples transfered"], combined["lab capacity"],combined["backlogs in lab"], combined['remaining capacity in lab']],
        fill_color='lavender',align='left'))])

    fig.update_layout(
    annotations=[
    dict(text="Labs allocations and backlog", showarrow=False,
    x=0.5, y=1.1, yref="paper", align="center")])
    figures.append(fig)

    #BAR chart
    transfer_type = pd.read_sql('SELECT d.district_name,s.transfer_type, SUM(s.samples_transferred) as transfer from sol s join districts d ON s.source=d.district_id group by s.source, s.transfer_type', con = conn)
    transfer_type['transfer_type'] = ['Transfer to lab' if i==0 else 'Keep backlog' for i in transfer_type['transfer_type']]

    fig = px.bar(transfer_type, x="district_name", y="transfer", text="transfer",color="transfer_type", title="Allocations by type")
    figures.append(fig)

    return figures
