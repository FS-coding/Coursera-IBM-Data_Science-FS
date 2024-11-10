import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

# Load the data using pandas
data = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv')

# Initialize the Dash app
app = dash.Dash(__name__)

# Set the title of the dashboard
app.title = 'Automobile Statistics Dashboard'

# List of years 
year_list = [i for i in range(1980, 2024, 1)]

# App layout
app.layout = html.Div(children=[
    html.H1(app.title,
            style={'textAlign': 'center', 
            'color': '#503D36', 
            'font-size': 24}),
    
    html.Div([
        html.Label('Select Statistics:'),
        #Dropdown Report type
        dcc.Dropdown(
            id='dropdown-statistics',
            options=[
                {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}],
            placeholder='Select a report type', 
            value='Select Statistics',
            style={'textAlign': 'center',
                   'width': '80%',
                   'padding': '3px',
                   'font-size': 'px'}
        )
    ]),

    html.Div(
        # Dropdown to select year
        dcc.Dropdown(
            id='select-year',
            options=[{'label': i, 'value': i} for i in year_list],
            value='Select-year',
            placeholder='Select-year',
            style={'textAlign': 'center',
                         'width': '80%',
                         'padding': '3px',
                         'font-size': 'px'}
        )
    ),

    # Inner division for output display
    html.Div([
        html.Div(id='output-container', 
                 className='chart-grid', 
                 style={'display': 'flex'}
                 )
            ])
])

# Callback for sisabling year selection if Yearly Statiscits is not chosen
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics', component_property='value'))

def update_input_container(selected_statistics):
    if selected_statistics == 'Yearly Statistics': 
        return False
    else: 
        return True

# Callback for plotting
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-statistics', component_property='value'),
     Input(component_id='select-year', component_property='value')])


def update_output_container(report_type, input_year):
    if report_type == 'Recession Period Statistics':
        # Filter the data for recession periods
        recession_data = data[data['Recession'] == 1]
          
        # Plot 1 Automobile sales fluctuate over Recession Period (year wise)
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.scatter(yearly_rec, 
                x='Year',
                y='Automobile_Sales',
                title='Average Automobile Sales fluctuation over Recession Period'))

        # Plot 2 Calculate the average number of vehicles sold by vehicle type and represent as a Bar chart
        average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()                
        fig2 = px.bar(average_sales,
                          x='Vehicle_Type',
                          y='Automobile_Sales',
                          title='Average Automobile Sales by Vehicle type',
                          color='Vehicle_Type')
        fig2.update_xaxes(tickangle=270)
        
        R_chart2  = dcc.Graph(figure=fig2)
                          
        
        # Plot 3 Pie chart for total expenditure share by vehicle type during recessions
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        fig3 = px.pie(exp_rec, 
                      values='Advertising_Expenditure', 
                      names='Vehicle_Type', 
                      title='Total expenditure share by vehicle type')   
        R_chart3 = dcc.Graph(figure=fig3)

        # Plot 4 bar chart for the effect of unemployment rate on vehicle type and sales
        unemp_data = recession_data.groupby('Vehicle_Type')[['unemployment_rate', 'Automobile_Sales']].mean().reset_index()
        fig4 = px.bar(unemp_data,
                             x='Vehicle_Type',
                             y='Automobile_Sales',
                             color='unemployment_rate',
                             labels={'unemployment_rate': 'Unemployment Rate', 
                                     'Automobile_Sales': 'Average Automobile Sales'},
                                             title='Effect of Unemployment Rate on Vehicle Type and Sales')
        fig4.update_xaxes(tickangle=270)
        R_chart4 = dcc.Graph(figure=fig4)


        return html.Div([
            html.Div(className='chart-item', 
                     children=[html.Div(children=R_chart1),
                               html.Div(children=R_chart2)],
                               style={'display': 'flex'}),

            html.Div(className='chart-item', 
                     children=[html.Div(children=R_chart3),
                               html.Div(children=R_chart4)],
                               style={'display': 'flex'})
            ], style={'display': 'flex', 'flexDirection': 'column'})

    # Yearly Statistic Report Plots
    # Check for Yearly Statistics.                             
    elif report_type == 'Yearly Statistics':
        yearly_data = data[data['Year'] == input_year]
                              
        # Plot 1 Yearly Automobile sales using line chart for the whole period.
        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        fig1 = px.line(yas, 
                       x='Year', 
                       y='Automobile_Sales', 
                       #color='Reporting_Airline', 
                       title='Yearly Automobile sales per year')
        
        Y_chart1 = dcc.Graph(figure=fig1)
            
        # Plot 2: Total Monthly Automobile sales using line chart.
        mas=data.groupby('Month')['Automobile_Sales'].mean().reset_index()
        fig2=px.line(mas,
            x='Month',
            y='Automobile_Sales',
            title='Total Monthly Automobile Sales')
        Y_chart2 = dcc.Graph(figure=fig2)

        # Plot 3: bar chart for average number of vehicles sold during the given year
        avr_vdata=yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        fig3=px.bar(avr_vdata,
                    x='Vehicle_Type',
                    y='Automobile_Sales',
                    color='Vehicle_Type',
                    title=f'Average Vehicles Sold by Vehicle Type in the year {input_year}')
        Y_chart3 = dcc.Graph(figure=fig3)

        # Plot4: Total Advertisement Expenditure for each vehicle using pie chart
        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()

        exp_data=yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        fig4 = px.pie(exp_data, 
                      values='Advertising_Expenditure', 
                      names='Vehicle_Type', 
                      title='Total Advertisement Expenditure for each vehicle')
        
        Y_chart4 = dcc.Graph(figure=fig4)

        return html.Div([                  
                html.Div(className='chart-item', 
                         children=[
                             html.Div(children=Y_chart1),
                             html.Div(children=Y_chart2)],
                             style={'display':'flex'}),
                html.Div(className='chart-item', 
                         children=[
                             html.Div(children=Y_chart3),
                             html.Div(children=Y_chart4)
                            ],
                             style={'display':'flex'})
            ], style={'display': 'flex', 'flexDirection': 'column'})
    
    else:
        return None

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)

