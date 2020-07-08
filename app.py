import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

import plotly.express as px
import os
import pandas as pd
from datetime import timedelta



app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# Clean the data and generate plots
def main(confirmed, deaths, recovered, population):
    output = {}

    # Get population data
    pop = pd.read_csv(population, skiprows=2, header=1)
    pop = pop[['Country Name', '2019']]
    pop = pop.replace('United States', 'US')
    pop = pop.replace('Russian Federation', 'Russia')
    pop.columns = ['country', 'population']

    # declare columns to retain after melting the data
    required_columns = ['Province/State', 'Country/Region', 'Lat', 'Long'] 

    # Clean and save the files
    dfc = import_data(confirmed, "confirmed", required_columns)
    dfd = import_data(deaths, "deaths", required_columns)
    dfr = import_data(recovered, "recovered", required_columns)

    # Change to datetime
    dfc["date"] = pd.to_datetime(dfc["date"])
    dfd["date"] = pd.to_datetime(dfd["date"])
    dfr["date"] = pd.to_datetime(dfr["date"])

    #Merge everything
    df = pd.merge(dfc, dfd, "left")
    df = pd.merge(df, dfr, "left")
    df = df.rename(columns={"confirmed" : "Confirmed", "deaths":"Deaths", "recovered":"Recovered", "Country/Region":"country"})
    # Group by to country granularity
    df = df.groupby(['country', 'date']).sum().reset_index()

    # Join population data
    df = df.merge(pop, 'left', left_on='country', right_on='country')

    # Gete list of all countries
    list_of_countries = df['country']
    output['list_of_countries'] = list_of_countries

    latest_date = df["date"].max()
    start_date = df["date"].min()
    dfl = df[df.date == latest_date]

    # Plot latest summary
    df_summary = dfl.sum()
    df_summary = pd.DataFrame(df_summary).T.drop(["country", "Lat", "Long", "population"], axis=1).T
    df_summary.columns = ["total"]
    df_summary["total"] = df_summary["total"].astype("int64")
    df_summary = df_summary.reset_index().sort_values(by="total", ascending=False)

    fig_summary = px.pie(df_summary, names='index', values='total', color_discrete_sequence=px.colors.qualitative.Dark2)
    # fig_summary.update_traces(texttemplate='%{text:.2s}', textposition='outside',
    #                            marker=dict(color='#ff7f0e'))
    fig_summary.update_traces(textposition='inside', textinfo='label+value')
    fig_summary.update_layout(xaxis_showgrid=False, yaxis_showgrid=False, xaxis_visible=True, yaxis_visible=False, xaxis_title_text="",
                                bargroupgap=0, bargap=0.1, plot_bgcolor="#1E1E1E", paper_bgcolor="#1E1E1E", font=dict(color="white"),
                                margin= {'t': 0, 'b': 10, 'l': 10, 'r': 0}, showlegend=False, width=200, height=200)

    # Get last 24 hours cases reported
    yesterday_date = df["date"].max() - pd.DateOffset(1)
    dfy = df[df.date == yesterday_date]
    dfl_change = pd.merge(dfl, dfy, "left", on=["country", "Lat", "Long"], suffixes=('_today', '_yesterday'))
    dfl_change["Change in 24 hours, Confirmed"] = dfl_change["Confirmed_today"] - dfl_change["Confirmed_yesterday"]
    dfl_change["Change in 24 hours, Deaths"] = dfl_change["Deaths_today"] - dfl_change["Deaths_yesterday"]
    dfl_change["Change in 24 hours, Recovered"] = dfl_change["Recovered_today"] - dfl_change["Recovered_yesterday"]
    dfl_change_summary = dfl_change.groupby(["country"]).sum()[["Confirmed_today", "Confirmed_yesterday", "Deaths_today","Recovered_today",
                                                                    "Change in 24 hours, Confirmed", "Change in 24 hours, Deaths", 
                                                                    "Change in 24 hours, Recovered"]]

    # Save results to output dictionary
    output['df'] = df  
    output['dfl'] = dfl
    output['dfl_change_summary'] = dfl_change_summary
    output['fig_summary'] = fig_summary
    output['latest_date'] = latest_date.date()
    output['start_date'] = start_date.date()

    return output

   
def import_data(data, val_name, required_columns):
    df = pd.read_csv(data)
    melt_columns = [col for col in df.columns if col not in required_columns]
    df_melted = pd.melt(df, id_vars=required_columns, var_name="date", value_vars = melt_columns, value_name=val_name)
    df_melted["date"] = pd.to_datetime(df_melted.date)

    return df_melted  
    

# Path to the data
path_data = "data/csse_covid_19_time_series"
confirmed = os.path.join(path_data, "time_series_covid19_confirmed_global.csv")
deaths = os.path.join(path_data, "time_series_covid19_deaths_global.csv")
recovered = os.path.join(path_data, "time_series_covid19_recovered_global.csv")
population = os.path.join("data/world_population.csv")

# Load and clean the data
output = main(confirmed, deaths, recovered, population)
latest_date = output['latest_date'] 
start_date = output['start_date'] 
dates = [start_date + timedelta(days=x) for x in range((latest_date-start_date).days + 1)]
dates_dict = {i:dt for i, dt in enumerate(dates)}
total_days = len(dates)

df = output['df']
dfl = output['dfl']
dfl_change_summary = output['dfl_change_summary']
fig_summary = output['fig_summary']
# Gete list of all countries
list_of_countries = output['list_of_countries'].unique()

# Top 5 countries with highest confirmed cases to set defaults
selected_countries = list(dfl.sort_values('Confirmed', ascending=False)['country'].iloc[0:5])


# Create the dash layout
app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                html.Div(
                className="three columns div-user-controls",
                children=[
                    html.Div(
                        className='row',
                        children=[
                            html.Img(
                            className="logo", src=app.get_asset_url("dash-logo-new.png")
                        ),

                        html.Div(
                            children=[
                                html.H2("TRACKING COVID-19"),
                        html.P(
                            """Select a range of dates and countries to compare total number of cases."""
                        ),                    
                            ]
                        ),
                        html.Hr(),
                        html.H6('Select Date Range'),

                    
                    html.Div(
                        className='div-for-dropdown',
                        children=[
                            dcc.RangeSlider(
                                id='date_slider',
                                marks={0:start_date},
                                min=0,
                                max=total_days-1,
                                value=[0, total_days-1],
                                allowCross=False
                    )

                        ]
                    ),  

                    html.H6('Select Countries'),

                      html.Div(
                        className='div-for-dropdown',
                        children=[
                            dcc.Dropdown(
                                id="country_dropdown",
                                options=[
                                    {"label": i, "value": i}
                                    for i in list_of_countries
                                ],
                                value=selected_countries,
                                multi=True,
                            )                              
                        ]
                    ),

                    html.H6("Total Cases Worldwide:"),

                    html.Div(
                        className='div-for-charts3',
                        children=[dcc.Graph(
                            figure=fig_summary,
                            config={
                                    'displayModeBar': False
                                    })]
                    ), 

                    html.P(f"Last updated on: {latest_date}"),
                    html.P("sreejimunthikodu@yahoo.com"),
                     dcc.Markdown(
                            children=[
                                "Data Source: [Johns Hopkins University](https://github.com/CSSEGISandData/COVID-19)"  
                                
                            ]
                        ),
                
                        ],
                    )                  
            ]
        ),

        # Plots
        html.Div(   
            className="nine columns div-for-charts bg-dark",             
                children=[html.Div(
                    className="row",
                    children=[
                        html.Div(
                            className='six columns',
                            children=[dcc.Graph(
                                id='summary_plot',
                                config={
                                    'displayModeBar': False
                                    })]
                        ),
                        
                        html.Div(
                            className='six columns',
                            children=[dcc.Graph(
                                id='summary_plot_24hours',
                                config={
                                    'displayModeBar': False
                                    })]
                        ),
                    ]                    
                ),
                    html.Div(
                        className='div-for-charts2',
                            children=[dcc.Graph(
                                id='time_line_plot',
                                config={
                                    'displayModeBar': False
                                    })]
                        ),                  
            ]
        ),
            ],
        ),

    ]
)

# Callbacks
@app.callback(
    [Output('time_line_plot', 'figure'),
    Output('summary_plot', 'figure'),
    Output('summary_plot_24hours', 'figure')],
    [Input('country_dropdown', 'value'),
    Input('date_slider', 'value')]
)
def update_figure(selected_country, time_range):

    start = dates_dict[time_range[0]]
    end = dates_dict[time_range[1]]    
    dfn = df.query("country == @selected_country and date >= @start and date <= @end")
    # Confirmed cases per 10000 population
    dfn["Confirmed"] = dfn["Confirmed"]/dfn["population"]*10000
    # Plot timeline
    fig_tl = px.line(dfn, x="date", y="Confirmed", color='country')
    # for trace in fig_tl.data:
    #     trace.name = trace.name.split('=')[1]

    fig_tl.update_layout(xaxis_showgrid=False, yaxis_showgrid=False, yaxis_title_text="",
                                xaxis_title_text="", showlegend=True, title=f"Total Confirmed Cases per 10,000 Population Between {start} and {end}",
                                plot_bgcolor="#323130", paper_bgcolor="#323130", font=dict(color="white"),
                                margin= {'t': 50, 'b': 10, 'l': 10, 'r': 0})

    # Plot summary of selected countries
    dfn = dfl.query("country == @selected_country")
    dfn = dfn.melt(id_vars=['country'], value_vars=['Confirmed', "Recovered", 'Deaths'])
    fig_sum = px.bar(dfn, y="variable", x="value", facet_row='country', color='country', orientation='h')
    # for trace in fig_sum.data:
    #     trace.name = trace.name.split('=')[1]

    fig_sum.for_each_annotation(lambda a: a.update(text=""))
    fig_sum.for_each_xaxis(lambda a: a.update(showgrid=False, title=""))    
    fig_sum.for_each_yaxis(lambda a: a.update(showgrid=False, title=''))
    fig_sum.update_xaxes(tickangle=0)

    fig_sum.update_layout(bargroupgap=0, bargap=0.1, plot_bgcolor="#323130", paper_bgcolor="#323130", font=dict(color="white"),
                          title=f"Total Cases as on {latest_date}", showlegend=False)

    # Plot change in last 24 hours for the selected countries
    dfn_24 = dfl_change_summary.query("country == @selected_country")
    dfn_24 = dfl_change_summary.query("country == @selected_country").reset_index()
    dfn_24 = dfn_24.rename(columns={'Change in 24 hours, Confirmed' : "Confirmed", "Change in 24 hours, Recovered" : "Recovered", 'Change in 24 hours, Deaths' : "Deaths"})
    dfn_24 = dfn_24.melt(id_vars=['country'], value_vars=["Confirmed", "Recovered", "Deaths"])

    fig_24 = px.bar(dfn_24, y="variable", x="value", facet_row='country', color='country', orientation='h')
    # for trace in fig_24.data:
    #     trace.name = trace.name.split('=')[1]
    fig_24.for_each_annotation(lambda a: a.update(text=""))
    fig_24.for_each_xaxis(lambda a: a.update(showgrid=False, title=""))    
    fig_24.for_each_yaxis(lambda a: a.update(showgrid=False, title=''))
    fig_24.update_layout(bargroupgap=0, bargap=0.1, plot_bgcolor="#323130", paper_bgcolor="#323130", font=dict(color="white"),
                         title=f"New cases in the Last 24 Hours ({latest_date})")
    fig_24.update_xaxes(tickangle=0)

    return [fig_tl, fig_sum, fig_24]

if __name__ == '__main__':
    app.run_server()