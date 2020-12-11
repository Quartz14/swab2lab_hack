from swabtolabapp import app


from flask import render_template
import plotly.graph_objs as go
import plotly.express as px
import json,plotly
from wrangling_scripts.wrangle_data import return_figures
from wrangling_scripts.wrangle_data_labs import return_figures_labs
from wrangling_scripts.wrangle_data_allocation import return_figures_allocation



@app.route('/')
@app.route('/districts')
def districts():

    figures = return_figures()

    # plot ids for the html id tag
    ids = ['figure-{}'.format(i) for i, _ in enumerate(figures)]

    # Convert the plotly figures to JSON for javascript in html template
    figuresJSON = json.dumps(figures, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('districts.html',
                           ids=ids,
                           figuresJSON=figuresJSON)

@app.route('/labs')
def labs():

    figures_labs = return_figures_labs()

    # plot ids for the html id tag
    ids_labs = ['figure-{}'.format(i) for i, _ in enumerate(figures_labs)]
    print(ids_labs)

    # Convert the plotly figures to JSON for javascript in html template
    figuresJSON_labs = json.dumps(figures_labs, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('labs.html',
                           ids=ids_labs,
                           figuresJSON=figuresJSON_labs)

#return_figures_allocation
@app.route('/allocation')
def allocation():

    figures_alloc = return_figures_allocation()

    # plot ids for the html id tag
    ids_alloc = ['figure-{}'.format(i) for i, _ in enumerate(figures_alloc)]
    print(ids_alloc)

    # Convert the plotly figures to JSON for javascript in html template
    figuresJSON_alloc = json.dumps(figures_alloc, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('allocation.html',
                           ids=ids_alloc,
                           figuresJSON=figuresJSON_alloc)
