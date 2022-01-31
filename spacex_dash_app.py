# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()


def drop_down_options(df):
    def option(site, value):
        return {'label': site, 'value': value}
    options = [option('All Sites', 'ALL')]
    for i, site in enumerate(launch_sites(df)):
        options.append(option(site, site))
    return options


def get_pie_chart(df, site):
    if site in launch_sites(df):
        return px.pie(df[df['Launch Site'] == site],
                      names='class',
                      title=f'Success launches for {site} site')
    else:
        return px.pie(df[df['class'] == 1],
                      names='Launch Site',
                      title='Total success launches by site')


def get_range_slider_marks(max_value, min_value, ticks=20):
    delta = float(max_value - min_value) / ticks
    marks = {}
    for i in range(ticks + 1):
        value = min_value + i * delta
        marks[value] = f'{value:.0f}Kg'
    return marks


def get_scatter_chart(df, site, payload_range=[0, 50000]):
    min_range, max_range = payload_range
    new_df = df[df['Payload Mass (kg)'].between(min_range, max_range)]
    if site in launch_sites(df):
        new_df = new_df[new_df['Launch Site'] == site]
    return px.scatter(new_df,
                      x='Payload Mass (kg)',
                      y='class',
                      color='Booster Version Category')


def launch_sites(df):
    return df['Launch Site'].unique()


def launch_server():

    # Create a dash application
    app = dash.Dash(__name__)

    # Create an app layout
    app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                            style={'textAlign': 'center', 'color': '#503D36',
                                                'font-size': 40}),
                                    # TASK 1: Add a dropdown list to enable Launch Site selection
                                    # The default select value is for ALL sites
                                    dcc.Dropdown(id='site-dropdown',
                                        options=drop_down_options(spacex_df),
                                        value='ALL',
                                        placeholder='Select a Launch Site here',
                                        searchable=True,
                                        ),
                                    html.Br(),

                                    # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                    # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                    html.Div(dcc.Graph(id='success-pie-chart')),
                                    html.Br(),

                                    html.P("Payload range (Kg):"),
                                    # TASK 3: Add a slider to select payload range
                                    dcc.RangeSlider(id='payload-slider',
                                        min=min_payload,
                                        max=max_payload,
                                        step=None,  # It will use marks
                                        value=[min_payload, max_payload],
                                        marks=get_range_slider_marks(max_payload, min_payload)),

                                    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                    ])

    # TASK 2:
    # Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
    @app.callback(Output(component_id='success-pie-chart', component_property='figure'),
                  Input(component_id='site-dropdown', component_property='value'))
    def get_web_pie_chart(site):
        return get_pie_chart(spacex_df, site)

    # TASK 4:
    # Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
    @app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
                  [
                    Input(component_id='site-dropdown', component_property='value'),
                    Input(component_id='payload-slider', component_property='value'),
                  ])
    def get_web_scatter_chart(site, payload_range):
        return get_scatter_chart(spacex_df, site, payload_range)

    app.run_server(port=3000)


# Run the app
if __name__ == '__main__':
    launch_server()