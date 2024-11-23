# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv('spacex_launch_dash.csv')
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create spacex_df from csv
spacex_df = pd.read_csv('spacex_launch_dash.csv')
spacex_df = spacex_df.drop(columns='Unnamed: 0')

# Get launch sites
launch_sites = spacex_df['Launch Site'].unique()  # ['CCAFS LC-40', 'VAFB SLC-4E', 'KSC LC-39A', 'CCAFS SLC-40']
launch_sites = list(launch_sites)

# Create Options list
options = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in launch_sites]

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                  
                                dcc.Dropdown(id='site-dropdown',
                                    options=options,
                                    value='ALL',
                                    placeholder='Select a Launch Site',
                                    searchable=True
                                    ),
                                html.Br(),

                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),
                                
                                # Payload text
                                html.P('Payload range (Kg):'),

                                # Payload slider
                                dcc.RangeSlider(id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    marks={0: '0',
                                        100: '100'},
                                    value=[0, 10000]),

                                # Payload graph
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
            Input(component_id='site-dropdown', component_property='value'))
            
def get_pie_chart(entered_site):
    
    filtered_df = spacex_df

    if entered_site == 'ALL':
        filtered_df = spacex_df.groupby('Launch Site')['class'].sum()
        
        fig = px.pie(filtered_df, 
                     values='class', 
                     names=launch_sites, 
                     title='Total Success Launches by Site')
        
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        site_succ = filtered_df.groupby('class')['class'].count()
        fig = px.pie(site_succ, values='class', 
                            names=site_succ.index,
                            title=f'Total Success Launches for site {entered_site}')
    
    return fig

# Callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
            [Input(component_id='site-dropdown', component_property='value'), 
             Input(component_id='payload-slider', component_property='value')])
            
def get_scatterplot(entered_site, payload_mass_range):
    min_mass = payload_mass_range[0]
    max_mass = payload_mass_range[1]

    filtered_payload = (spacex_df['Payload Mass (kg)'] > min_mass) & \
                        (spacex_df['Payload Mass (kg)'] < max_mass)

    filtered_df = spacex_df[filtered_payload]
    
    
    
    if entered_site == 'ALL':
        fig = px.scatter(filtered_df, x='Payload Mass (kg)',
                    y='class',
                    color='Launch Site',
                    title=f'Correlation between Payload ({min_mass}-{max_mass}) and Success for all sites')
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == entered_site) &
                                 filtered_payload]
                
        fig = px.scatter(filtered_df, x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version Category',
                         title=f'Correlation between Payload ({min_mass}-{max_mass}) and Success for {entered_site}')
    return fig
    

# Run the app
if __name__ == '__main__':
    app.run_server()
