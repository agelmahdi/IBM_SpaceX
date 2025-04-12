# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")
sites = spacex_df['Launch Site'].unique()
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
payload = spacex_df['Payload Mass (kg)']

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                             options= 
                                                [{'label': 'All Sites', 'value': 'ALL'}] + \
                                                [{'label': site, 'value': site} for site in sites],
                                             value='ALL'
                                             ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min = min_payload,max=max_payload,
                                                #  step=100,
                                                value=[min_payload, max_payload],
                                                marks={i: f'{i} kg' for i in range(
                                                    int(min_payload),
                                                    int(max_payload) + 1,
                                                    1000
                                                )},
                                                tooltip={"placement": "bottom", "always_visible": True}),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def showPie(selected_site):

    launch_counts = spacex_df.groupby(['Launch Site', 'class']).size().reset_index(name='Count')
   
    launch_counts['Outcome'] = launch_counts['class'].map({1: 'Success', 0: 'Failure'})

    if selected_site == 'ALL':
        success_counts = launch_counts[launch_counts['class'] == 1]
        success_by_site = success_counts.groupby('Launch Site')['Count'].sum().reset_index()
        
        fig = px.pie(
            success_by_site,
            values='Count',
            names='Launch Site',
            title='Distribution of Successful Launches Across Sites',
            color='Launch Site',
            hole=0.3
        )
           
    else:
        site_data = launch_counts[launch_counts['Launch Site'] == selected_site]
        
        fig = px.pie(
            site_data,
            values='Count',
            names='Outcome',
            title=f'Launch Outcomes at {selected_site}',
            color='Outcome',
            color_discrete_map={'Success': '#00CC96', 'Failure': '#EF553B'},
            hole=0.4
        )

    return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def payloadRange(selected_site,payload_range):
    success_df = spacex_df[
    (spacex_df['class'] == 1) & 
    (spacex_df['Payload Mass (kg)'].between(*payload_range)) & 
    ((spacex_df['Launch Site'] == selected_site) if selected_site != 'ALL' else True)
    ] 
        
    fig = px.scatter(
        success_df,
        x='Launch Site',
        y='Payload Mass (kg)',
        title=f'Successful Launches at {selected_site} ({payload_range[0]}kg-{payload_range[1]}kg)',
        color='Launch Site',
        labels={'Payload Mass (kg)': 'Payload Mass (kg)', 'Launch Site': 'Launch Site'},
        hover_data=['Booster Version Category', 'Booster Version']
    )
  
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
