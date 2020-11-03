import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import app_helpers as ah

play_half = pd.read_csv('player_half_v1.csv')
#league_info = pd.read_csv('./league_info.csv')
team_names = np.unique(play_half['market'])
player_names = np.unique(play_half['full_name'])

# Box Score Options

#TODO: Does season averages do anything?

box_score_view = ['General','Shooting % By Half','Season Averages']
season_view = [2019,2018,2017,2016]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[

    #Title
    html.H1(children='NCAA Player Profile Dashboard',style={'textAlign':'center'}),

    ##################################################
    # Player Averages
    ##################################################
    html.H3(children='Player Averages',style={'textAlign':'left'}),
    html.Div([
        #filters at the top
        html.Div([
            dcc.Dropdown(
                #identfier that correspods
                id='player_average_season',
                options=[{'label': i, 'value': i} for i in season_view],
                value=2019
            )
        ], style={'width': '10%', 'float': 'center', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='player_average_team',
                # placeholder='Select Team',
                value='Kentucky',
                options=[{'label':team_names[i], 'value':team_names[i]} for i in range(len(team_names))],
            ),
        ], style={'width': '25%', 'float': 'center', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='player_average_player',
                value='Ashton Hagans',
                #options = [{'label':player_names[i], 'value':player_names[i]} for i in range(len(player_names))],
            )
        ], style={'width': '25%', 'float': 'center', 'display': 'inline-block'}),
    ]),
    html.Div(
        dt.DataTable(id='player_avg',
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold', 'textAlign': 'center'},
            style_cell={'textAlign': 'center'},
            style_header_conditional=[
                {
                    'if':{'column_id':'scheduled'},
                    'column_name':'Date',
                    'column_type':'datetime'
                },
            ]
        )
    ),
    ##################################################

    # Advanced Stats
    ##################################################
    html.H3(children='Advanced Stats',style={'textAlign':'left'}),
    html.Div([
        #filters at the top
        html.Div([
            dcc.Dropdown(
                #identfier that correspods
                id='advanced_season',
                options=[{'label': i, 'value': i} for i in season_view],
                value=2019
            )
        ], style={'width': '10%', 'float': 'center', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='advanced_team',
                # placeholder='Select Team',
                value='Kentucky',
                options=[{'label':team_names[i], 'value':team_names[i]} for i in range(len(team_names))],
            ),
        ], style={'width': '25%', 'float': 'center', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='advanced_player',
                value='Ashton Hagans',
                #options = [{'label':player_names[i], 'value':player_names[i]} for i in range(len(player_names))],
            )
        ], style={'width': '25%', 'float': 'center', 'display': 'inline-block'}),
    ]),
    html.Div(
        dt.DataTable(id='advanced_stats',
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold', 'textAlign': 'center'},
            style_cell={'textAlign': 'center'},
            style_header_conditional=[
                {
                    'if':{'column_id':'scheduled'},
                    'column_name':'Date',
                    'column_type':'datetime'
                },
            ]
        )
    ),
    ##################################################
    # Box Score Team and Player Select
    ##################################################
    html.H3(children='Box Scores',style={'textAlign':'left'}),
    html.Div([
        #filters at the top
        html.Div([
            dcc.Dropdown(
                #identfier that corresponds to app callbacks
                id='box_score_season',
                options=[{'label': i, 'value': i} for i in season_view],
                value=2019
            )
        ], style={'width': '10%', 'float': 'center', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='team_filter_box_scores',
                # placeholder='Select Team',
                value='Kentucky',
                options=[{'label':team_names[i], 'value':team_names[i]} for i in range(len(team_names))],
            ),
        ], style={'width': '25%', 'float': 'center', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='player_select_box_scores',
                value='Ashton Hagans',
                # options = whats returned
            )
        ], style={'width': '25%', 'float': 'center', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='box_score_type',
                value='General',
                options=[{'label':i, 'value':i} for i in box_score_view]
            )
        ], style={'width': '25%', 'float': 'center', 'display': 'inline-block'}),
    ]),
    html.Div(
        dt.DataTable(id='player_box_score',
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold', 'textAlign': 'center'},
            style_cell={'textAlign': 'center'},
            style_header_conditional=[
                {
                    'if':{'column_id':'scheduled'},
                    'column_name':'Date',
                    'column_type':'datetime'
                },
            ]
        )
    ),

])


##################################################
# Box Score With Team and Player Select
##################################################
# For the box score table

@app.callback(
    dash.dependencies.Output('player_select_box_scores','options'),
    dash.dependencies.Output('player_box_score','columns'),
    dash.dependencies.Output('player_box_score', 'data'),
    dash.dependencies.Input('team_filter_box_scores','value'),
    dash.dependencies.Input('box_score_type','value'),
    dash.dependencies.Input('player_select_box_scores','value'),
    dash.dependencies.Input('box_score_season','value')
)

def player_box_scores(team, table_view, player, season):
    roster = np.unique(play_half[(play_half['market'] == team)]['full_name'])
    roster_options = [{'label': i, 'value': i} for i in roster]

    roster_check = np.unique(play_half[(play_half['market'] == team) & (play_half['season'] == season)]['full_name'])
    roster_check_options = [{'label': i, 'value': i} for i in roster_check]

    if (table_view =='General'):
        column_labels = ['Date','Opponent','Minutes','Efficiency','Points','Rebounds','Assists','Turnovers','Steals','Blocks']
    elif(table_view =='Shooting % By Half'):
        column_labels = ['Date','Opponent','Half', 'Minutes','FG%','FT%','2PT%','3PT%','TS%','EFG%']
    columns = [{"name":i,"id":i} for i in column_labels]

    #ah is apphelper.py ,
    datadf,data = ah.box_score_data(player,table_view,season)
    columns=[{"name":i,"id":i} for i in datadf.columns]
    
    
    return roster_check_options, columns,data

@app.callback(

    dash.dependencies.Output('player_average_player','options'),
    dash.dependencies.Output('player_avg','columns'),
    dash.dependencies.Output('player_avg', 'data'),
    dash.dependencies.Input('player_average_team','value'),
    dash.dependencies.Input('player_average_player','value'),
    dash.dependencies.Input('player_average_season','value')
)

def player_averages(team, player, season):
    roster = np.unique(play_half[(play_half['market'] == team)]['full_name'])
    roster_options = [{'label': i, 'value': i} for i in roster]
    roster_check = np.unique(play_half[(play_half['market'] == team) & (play_half['season'] == season)]['full_name'])
    roster_check_options = [{'label': i, 'value': i} for i in roster_check]
    table_view = 'Season Averages'
    column_labels = ['Points', 'Rebounds', 'Blocks', 'Assists', 'Turnovers']
    columns = [{"name":i,"id":i} for i in column_labels]
    #ah is apphelper.py
    datadf,data = ah.box_score_data(player,table_view,season)
    columns=[{"name":i,"id":i} for i in datadf.columns]

    #return roster_options, columns, data
    return roster_check_options,columns,data


##################################################
# Advanced Stats
##################################################

@app.callback(

    dash.dependencies.Output('advanced_player','options'),
    dash.dependencies.Output('advanced_stats','columns'),
    dash.dependencies.Output('advanced_stats', 'data'),
    dash.dependencies.Input('advanced_team','value'),
    dash.dependencies.Input('advanced_player','value'),
    dash.dependencies.Input('advanced_season','value')
)

def advanced_stats(team, player, season):
    roster = np.unique(play_half[(play_half['market'] == team)]['full_name'])
    roster_options = [{'label': i, 'value': i} for i in roster]
    roster_check = np.unique(play_half[(play_half['market'] == team) & (play_half['season'] == season)]['full_name'])
    roster_check_options = [{'label': i, 'value': i} for i in roster_check]
    table_view = 'Advanced Stats'
    column_labels = ['USG%', 'AST%', 'TOV%', 'ORB%', 'BLK%', 'STL%', 'DRB%']
    columns = [{"name":i,"id":i} for i in column_labels]
    #ah is apphelper.py
    datadf,data = ah.advanced_stats(player, season)
    columns=[{"name":i,"id":i} for i in datadf.columns]

    #return roster_options, columns, data
    return roster_check_options,columns,data



##################################################
# INSERT NEW ELEMENTS HERE                       #
##################################################

##################################################
##################################################


if __name__ == '__main__':
    app.run_server(debug=True,  port= 8050)
