import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output
import json




'''
TASK 1 DATA
'''
df_essential = pd.read_csv('EssentialWorkers.csv', index_col=0)
df_essential.columns = df_essential.columns.str.replace(r'\s*i\d+$', '', regex=True)
total_row = pd.to_numeric(df_essential.loc['Total - Occupation - Unit group - National Occupational Classification (NOC) 2021 10'].str.replace(',', ''))
nursing_row = pd.to_numeric(df_essential.loc['313 Nursing and allied health professionals'].str.replace(',', ''))
police_row = pd.to_numeric(df_essential.loc['42100 Police officers (except commissioned)'].str.replace(',', ''))
firefighter_row = pd.to_numeric(df_essential.loc['42101 Firefighters'].str.replace(',', ''))

nursing_per_capita = (nursing_row / total_row ) * 1000
police_per_capita = (police_row / total_row) * 1000
firefighter_per_capita = (firefighter_row / total_row) * 1000

df_essential_map = pd.DataFrame({'Nursing': nursing_per_capita, 'Police': police_per_capita, 'Firefighter': firefighter_per_capita})
df_essential_map = df_essential_map.reset_index().rename(columns={'index': 'Province'})

df_essential_melted = df_essential_map.melt(id_vars=['Province'], var_name='Occupation', value_name='PerCapita')



with open('canada.geojson') as f:
      canada_geojson = json.load(f)

'''
TASK 2 DATA
'''
df_gender = pd.read_csv('task2.csv', index_col=0, header=1)
df_gender.columns = df_gender.columns.str.strip()

top_level_nocs = [
    'Legislative and senior management occupations',
    'Business, finance and administration occupations',
    'Natural and applied sciences and related occupations',
    'Health occupations',
    'Occupations in education, law and social, community and government services',
    'Occupations in art, culture, recreation and sport',
    'Sales and service occupations',
    'Trades, transport and equipment operators and related occupations',
    'Natural resources, agriculture and related production occupations',
    'Occupations in manufacturing and utilities'
]

df_gender_filtered = df_gender[df_gender.index.isin(top_level_nocs)].copy()
df_gender_filtered['Occupation'] = df_gender_filtered.index

for col in ['Total', 'Men', 'Women']:
    df_gender_filtered[col] = pd.to_numeric(df_gender_filtered[col].str.replace(',', '',))

'''
TASk 3 DATA
'''
df_major = pd.read_csv('task3.csv', index_col=0)
df_major.columns = df_major.columns.str.replace(r'\s*i\d+$', '',regex=True)


total_row = pd.to_numeric(df_major.loc['Total - Major field of study - Classification of Instructional Programs (CIP) 2021 9'].str.replace(',', ''))
cs_row = pd.to_numeric(df_major.loc['11.07 Computer science'].str.replace(',', ''))
ele_row = pd.to_numeric(df_major.loc['14.10 Electrical, electronics and communications engineering'].str.replace(',', ''))
mech_row = pd.to_numeric(df_major.loc['14.19 Mechanical engineering'].str.replace(',', ''))

cs_per_capita = (cs_row / total_row ) * 1000
ele_per_capita = (ele_row / total_row) * 1000
mech_per_capita = (mech_row / total_row) * 1000

df_major_capita = pd.DataFrame({'Computer Science': cs_per_capita, 'Electrical Engineering': ele_per_capita, 'Mechanical Engineering': mech_per_capita})
df_major_capita = df_major_capita.reset_index().rename(columns={'index': 'Province'})
df_capita_melted = df_major_capita.melt(id_vars=['Province'], var_name='Major', value_name='PerCapita')


df_major_total = pd.DataFrame({'Computer Science': cs_row, 'Electrical Engineering': ele_row, 'Mechanical Engineering': mech_row})
df_major_total = df_major_total.reset_index().rename(columns={'index': 'Province'})
df_total_melted = df_major_total.melt(id_vars=['Province'], var_name='Major', value_name='Total')

'''
TASK 4 DATA
'''
df_gender_dist = pd.read_csv('task4.csv', index_col=0)
df_gender_dist.columns = df_gender_dist.columns.str.replace(r'\s*i\d+$', '', regex=True).str.strip()
male_row = pd.to_numeric(df_gender_dist.loc['Men+ 11'].str.replace(',', ''))
female_row = pd.to_numeric(df_gender_dist.loc['Women+ 12'].str.replace(',', ''))

male_percentage = (male_row / (male_row+female_row)) * 100
female_percentage = (female_row /(male_row+female_row)) * 100

df_gender_pie = pd.DataFrame({
    'Province': male_percentage.index.tolist() * 2,
    'Gender': ['Male'] * len(male_percentage) + ['Female'] * len(female_percentage),
    'Percentage': list(male_percentage) + list(female_percentage)
})

print(df_gender_pie)




app = dash.Dash(__name__)
server = app.server
app.layout = html.Div([
    html.H1('Canada Employment Anaylsis'),
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='Task 1: Essential Workers Visualization', value='tab-1', children=[
            html.Div([
                html.H2('Essential Workers per 1000 Total Workers Per Province'),
                html.P("Select an occupation to display on the map"),
                dcc.RadioItems(
                    id='occupation-radio',
                    options=[
                        {'label': 'Police', 'value': 'Police'},
                        {'label': 'Firefighter', 'value': 'Firefighter'},
                        {'label': 'Nursing', 'value': 'Nursing'}
                    ],
                    value='Police',
                    inline=True
                ),
                dcc.Graph(id='choropleth-map')
            ], style={'padding': 10})
        ]),
        dcc.Tab(label='Task 2: Gender Based Statistics', value='tab-2', children=[
            html.Div([
                html.H2('Gender-based Employment Statistics by Occupation'),
                html.P("Select a gender to display on the bar chart"),
                dcc.Dropdown(
                    id='gender-dropdown',
                    options=[
                        {'label': 'Total', 'value': 'Total'},
                        {'label': 'Men', 'value': 'Men'},
                        {'label': 'Women', 'value': 'Women'}

                    ],
                    value='Total',
                    clearable = False,
                    style={
                        'width': '50%',
                        'marginBottom': '50px'
                    }
                ),
                dcc.Graph(id='gender-bar-chart')
            ], style={'padding': '10px' , 'height': '1000px'})
        ]),
        dcc.Tab(label='Task 3: Major per Province', value='tab-3', children=[
            html.Div([
                html.H2('Electrical Engineers, Mechanical Engineers, Computer Scientists per province'),
                html.P("Select a major to display on the stacked area chart"),
                dcc.Checklist(
                    id='major-checklist',
                    options=[
                        {'label': 'Computer Science', 'value': 'Computer Science'},
                        {'label': 'Electrical Engineering', 'value': 'Electrical Engineering'},
                        {'label': 'Mechanical Engineering', 'value': 'Mechanical Engineering'}
                    ],
                    value=['Computer Science'],
                    inline=True
                ),
                dcc.RadioItems(
                    id='Total-per-capita-radio',
                    options=[
                        {'label': 'Per Capita', 'value': 'PerCapita'},
                        {'label': 'Total', 'value': 'Total'}

                    ],
                    value='PerCapita',
                    inline=True
                ),
                dcc.Graph(id='major-stacked-area-chart')
            ]),
        ]),
        dcc.Tab(label='Task 4: Gender Distribution', value='tab-4', children=[
            html.Div([
                html.H2('Gender Distribution by Province'),
                html.P('Use slider to select province'),
                html.Div([
                    dcc.Slider(
                        id='province-slider',
                        min=0,
                        max=len(df_gender_pie['Province'].unique()) - 4,
                        step=1,
                        value=0,
                        marks={i: prov for i, prov in enumerate(df_gender_pie['Province'].unique()[:-3])}
                    )
                ], style={'marginBottom': '40px'}), 
                dcc.Graph(id='gender-pie')
            ], style={'padding': '0 40px 40px 40px'})
        ])
    ])
])

@app.callback(
    Output('choropleth-map', 'figure'),
    Input('occupation-radio', 'value')
)
def update_map(occupation):

  dff = df_essential_melted[df_essential_melted["Occupation"] == occupation]
  fig = px.choropleth_mapbox(
      dff,
      geojson=canada_geojson,
      locations="Province",
      featureidkey="properties.name",
      color="PerCapita",
      color_continuous_scale="Blues",
      mapbox_style="carto-positron",
      center={"lat": 62, "lon": -96},
      zoom = 2,
      opacity=0.5,
      title=f'{occupation} Per 1000 total workers by Province'
  )
  fig.update_geos(fitbounds='locations', visible=False)
  fig.update_layout(height=800)
  return fig

@app.callback(
    Output('gender-bar-chart', 'figure'),
    Input('gender-dropdown', 'value')
)
def update_bar_chart(selected_gender):
    fig = px.bar(
        df_gender_filtered,
        x='Occupation',
        y=selected_gender,
        color='Occupation',
        title=f'{selected_gender} Employment by Top-level NOC Occupation'
    )
    fig.update_layout(
        height=600,
        xaxis_title='Top-level NOC Occupation',
        yaxis_title='Number of Workers',
        legend_title_text='Occupation'
    )
    fig.update_xaxes(showticklabels=False)
    fig.update_layout(height=800)
    return fig

@app.callback(
    Output('major-stacked-area-chart', 'figure'),
    Input('major-checklist', 'value'),
    Input('Total-per-capita-radio', 'value')
)

def update_stacked_chart(selected_majors, view):
  if view == 'Total':
    df = df_total_melted[df_total_melted['Major'].isin(selected_majors)]
    y_col = 'Total'
    y_title = 'Total Employment'
  else:
    df = df_capita_melted[df_capita_melted['Major'].isin(selected_majors)]
    y_col = 'PerCapita'
    y_title = 'Per 1000 People'

  fig = px.area(
      df,
      x='Province',
      y=y_col,
      color='Major',
      title='Engineering related majors across Canada',
      labels={y_col: y_title}
  )

  fig.update_layout(
        height=800,
        xaxis_title='Province',
        yaxis_title=y_title,
        legend_title_text='Major Field'
    )
  return fig

@app.callback(
    Output('gender-pie', 'figure'),
    Input('province-slider', 'value')
)
def update_pie_chart(selected_province):
  provinces = df_gender_pie['Province'].unique()
  selected_province_name = provinces[selected_province]
  dff = df_gender_pie[df_gender_pie['Province'] == selected_province_name ]

  fig = px.pie(
      dff,
      names='Gender',
      values='Percentage',
      title=f'Gender Distribution in {selected_province_name}'
  )
  fig.update_traces(textinfo='percent+label')
  return fig

if __name__ == '__main__':
    app.run(debug=False)
