import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import app_helpers as ah

play_half = pd.read_csv('player_half_v1.csv')
team_boxscore = pd.read_csv('./team_boxscores_v1.csv')
# league_info = pd.read_csv('./league_info.csv')
team_names = np.unique(play_half['market'])
player_names = np.unique(play_half['full_name'])

stat_names = ['Points', 'Rebounds', 'Assists', 'TO', 'Blocks']
#stat_choices = [0,1,2,3,4,5,6,7]
comparison_categories = ['Career Avg.', 'Season Avg.', '5-game Avg.', 'Team Avg.']

# Box Score Options
box_score_view = ['General', 'Shooting % By Half']
average_view = ['General', 'Per 40 Min.','Per 100 Poss.']
season_view = [2019, 2018, 2017, 2016]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[

    # Title
    html.H1(children='NCAA Player Profile Dashboard', style={'textAlign': 'center'}),

    ##################################################
    # Player Averages With Dropdowns
    ##################################################
    html.H3(children='Player Averages', style={'textAlign': 'left'}),
    html.Div([
        html.Div([
            dcc.Dropdown(
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
                options=[{'label': team_names[i], 'value': team_names[i]} for i in range(len(team_names))],
            ),
        ], style={'width': '15%', 'float': 'center', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='player_average_player',
                value='Ashton Hagans',
            )

        ], style={'width': '15%', 'float': 'center', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='player_average_view',
                value='General',
                options=[{'label': i, 'value': i} for i in average_view]
            )
        ], style={'width': '10%', 'float': 'center', 'display': 'inline-block'}),

    ]),

    # Season averages for player
    html.Div(
        dt.DataTable(id='player_avg',
                     style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold',
                                   'textAlign': 'center'},
                     style_cell={'textAlign': 'center'},
                     style_header_conditional=[
                         {
                             'if': {'column_id': 'scheduled'},
                             'column_name': 'Date',
                             'column_type': 'datetime'
                         },
                     ],
                     style_table={'maxWidth': '50%'}
                     )
    ),
    html.H3(children='Player Comparison', style={'textAlign': 'left'}),
    # Compare player to using bar plot
    html.Label(children='Select Season, Team, Player, Game, Stats, Comparison Categories:',
            style={'padding-right': '10px', 'padding-left': '10px',
                   'backgroundColor': '#dcdcdc', 'padding-top': '10px',
                   'borderTop': 'thin lightgrey solid'
                   }),


    html.Div([
        html.Div([
            dcc.Dropdown(
                id='season_select_bar_plot',
                options=[{'label': i, 'value': i} for i in season_view],
                value=2019
            )
        ], style={'width': '10%', 'float': 'center', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='team_select_bar_plot',
                # placeholder='Select Team',
                value='Kentucky',
                options=[{'label': team_names[i], 'value': team_names[i]} for i in range(len(team_names))],
            ),
        ], style={'width': '15%', 'float': 'center', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='player_select_bar_plot',
                value='Ashton Hagans',
            )

        ], style={'width': '15%', 'float': 'center', 'display': 'inline-block'}),
        #html.Div([
        #    dcc.Dropdown(
        #        id='game_select_bar_plot',
        #        placeholder= 'Select Games to View...',
        #        multi=True)
        #], style={'width': '15%', 'float': 'center', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='stats_select_bar_plot',
                options=[{'label': stat_names[st], 'value': st} for st in range(len(stat_names))],
                value = [0,1],
                multi=True)], style={'width': '25%', 'float': 'center', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='comparisons_select_bar_plot',
                options=[{'label': comparison_categories[cc], 'value': cc} for cc in range(len(comparison_categories))],
                value = [0,1],
                multi=True)], style={'width': '25%', 'float': 'center', 'display': 'inline-block'}),
        ],
        style={
        'backgroundColor': '#dcdcdc',
        'padding-bottom': '15px',
        'padding-top': '5px',
    }),
    html.Div([
        dcc.RadioItems(
            id='per_unit_select_bar_plot',
            options=[
                {'label': 'Per Game', 'value': 0},
                {'label': 'Per 40 Min.', 'value': 1},
                {'label': 'Per 100 Poss.', 'value': 2}],
            value=0,
            labelStyle={'display': 'inline-block', 'margin': '5px'})],
        style={'width': '30%', 'float': 'center','padding-left': '40%',
               'padding-right': '30%', 'padding-top': '20px',
               'backgroundColor': '#dcdcdc',
               'borderBottom': 'thin lightgrey solid',}),
    html.Div([
        dcc.Graph(
            id='player_comparison_bar_plot',
        )], style={'padding-bottom': '5px', 'backgroundColor': '#000000'
                   }),
    ##################################################
    # Advanced Stats
    ##################################################
    html.H3(children='Advanced Stats', style={'textAlign': 'left'}),
    html.Div([
        # filters at the top
        html.Div([
            dcc.Dropdown(
                # identfier that correspods
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
                options=[{'label': team_names[i], 'value': team_names[i]} for i in range(len(team_names))],
            ),
        ], style={'width': '25%', 'float': 'center', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='advanced_player',
                value='Ashton Hagans',
                # options = [{'label':player_names[i], 'value':player_names[i]} for i in range(len(player_names))],
            )
        ], style={'width': '25%', 'float': 'center', 'display': 'inline-block'}),
    ]),
    html.Div(
        dt.DataTable(id='advanced_stats',
                     style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold',
                                   'textAlign': 'center'},
                     style_cell={'textAlign': 'center'},
                     style_header_conditional=[
                         {
                             'if': {'column_id': 'scheduled'},
                             'column_name': 'Date',
                             'column_type': 'datetime'
                         },
                     ]
                     )
    ),
    ##################################################
    # Box Score Team and Player Select
    ##################################################
    html.H3(children='Box Scores', style={'textAlign': 'left'}),
    html.Div([
        # filters at the top
        html.Div([
            dcc.Dropdown(
                # identfier that corresponds to app callbacks
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
                options=[{'label': team_names[i], 'value': team_names[i]} for i in range(len(team_names))],
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
                options=[{'label': i, 'value': i} for i in box_score_view]
            )
        ], style={'width': '25%', 'float': 'center', 'display': 'inline-block'}),
    ]),
    html.Div(
        dt.DataTable(id='player_box_score',
                     style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold',
                                   'textAlign': 'center'},
                     style_cell={'textAlign': 'center'},
                     style_header_conditional=[
                         {
                             'if': {'column_id': 'scheduled'},
                             'column_name': 'Date',
                             'column_type': 'datetime'
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
    dash.dependencies.Output('player_select_box_scores', 'options'),
    dash.dependencies.Output('player_box_score', 'columns'),
    dash.dependencies.Output('player_box_score', 'data'),
    dash.dependencies.Input('team_filter_box_scores', 'value'),
    dash.dependencies.Input('box_score_type', 'value'),
    dash.dependencies.Input('player_select_box_scores', 'value'),
    dash.dependencies.Input('box_score_season', 'value')
)
def player_box_scores(team, table_view, player, season):
    roster = np.unique(play_half[(play_half['market'] == team)]['full_name'])
    roster_options = [{'label': i, 'value': i} for i in roster]

    roster_check = np.unique(play_half[(play_half['market'] == team) & (play_half['season'] == season)]['full_name'])
    roster_check_options = [{'label': i, 'value': i} for i in roster_check]

    if (table_view == 'General'):
        column_labels = ['Date', 'Opponent', 'Minutes', 'Efficiency', 'Points', 'Rebounds', 'Assists', 'Turnovers',
                         'Steals', 'Blocks']
    elif (table_view == 'Shooting % By Half'):
        column_labels = ['Date', 'Opponent', 'Half', 'Minutes', 'FG%', 'FT%', '2PT%', '3PT%', 'TS%', 'EFG%']
    columns = [{"name": i, "id": i} for i in column_labels]

    # ah is apphelper.py ,
    datadf, data = ah.box_score_data(player, table_view, season)
    columns = [{"name": i, "id": i} for i in datadf.columns]

    return roster_check_options, columns, data


##################################################
# Bar Plot
##################################################
# For the player comparison

@app.callback(
    dash.dependencies.Output('player_select_bar_plot', 'options'),
    #dash.dependencies.Output('game_select_bar_plot', 'options'),
    dash.dependencies.Output('player_comparison_bar_plot', 'figure'),
    dash.dependencies.Input('season_select_bar_plot', 'value'),
    dash.dependencies.Input('team_select_bar_plot', 'value'),
    #dash.dependencies.Input('game_select_bar_plot', 'value'),
    dash.dependencies.Input('player_select_bar_plot', 'value'),
    dash.dependencies.Input('per_unit_select_bar_plot', 'value'),
    dash.dependencies.Input('stats_select_bar_plot', 'value'),
    dash.dependencies.Input('comparisons_select_bar_plot', 'value')

)
# TODO: Add a game select and support for per 40/100, team averages

def player_bar_plot(season, team, player, per_unit, stat_choices, comparison_choices):
    roster = np.unique(play_half[(play_half['market'] == team)]['full_name'])
    roster_options = [{'label': i, 'value': i} for i in roster]
    roster_check = np.unique(play_half[(play_half['market'] == team) & (play_half['season'] == season)]['full_name'])
    roster_check_options = [{'label': i, 'value': i} for i in roster_check]
    #boxscore_df, data = ah.box_score_data(player, 'General', season)
    #print(data)
    #print(datadf)
    #game_select_options = boxscore_df.Date + ' ' + boxscore_df.Opponent + ' ' + boxscore_df.Result
    #sorted_gl = datadf.sort_values(by = 'date', ascending = False)
    #game_select_options = [{'label': i, 'value': i} for i in sorted_gl[sorted_gl.team_id == team].matchup]
    column_labels = ['Date', 'Opponent', 'Minutes', 'Efficiency', 'Points', 'Rebounds', 'Assists', 'Turnovers',
                         'Steals', 'Blocks']
    columns = [{"name": i, "id": i} for i in column_labels]
    figure = ah.get_player_bar_plot(season, team, player, per_unit, stat_names, stat_choices, comparison_categories, comparison_choices)
    # ah is apphelper.py ,
    #datadf, data = ah.box_score_data(player, table_view, season)
    #columns = [{"name": i, "id": i} for i in datadf.columns]

    return roster_check_options, figure #game_select_options, #figure


##################################################
# Season Averages and Shooting Percentages
##################################################
@app.callback(
    dash.dependencies.Output('player_average_player', 'options'),
    dash.dependencies.Output('player_avg', 'columns'),
    dash.dependencies.Output('player_avg', 'data'),
    dash.dependencies.Input('player_average_team', 'value'),
    dash.dependencies.Input('player_average_player', 'value'),
    dash.dependencies.Input('player_average_season', 'value'),
    dash.dependencies.Input('player_average_view', 'value'),
)
def player_averages(team, player, season, stat_view):
    roster_check = np.unique(play_half[(play_half['market'] == team) & (play_half['season'] == season)]['full_name'])
    roster_check_options = [{'label': i, 'value': i} for i in roster_check]
    if stat_view == 'General':
        column_labels = ['PPG', 'RPG', 'BPG', 'APG', 'TO', 'MPG', 'FG%', 'FT%', '2PT%', '3PT%', 'Paint%']
    elif stat_view == 'Per 40 Min.':
        column_labels = ['Points', 'Total Rebounds', 'ORB', 'DRB', 'Assists', 'TO', 'Steals', 'Blocks']
    elif stat_view == 'Per 100 Poss.':
        column_labels = ['Points', 'Total Rebounds', 'ORB', 'DRB', 'Assists', 'TO', 'Steals', 'Blocks']
    columns = [{"name": i, "id": i} for i in column_labels]

    datadf,data = ah.player_average_data(player,stat_view,season)


    if stat_view == 'General':
        # Renames the column headers
        datadf = datadf.rename(columns=
                           {'points': 'PPG', 'rebounds': 'RPG', 'blocks':'BPG','assists':'APG','turnovers':'TOPG',
                            'total_minutes': 'MPG', 'fg%':'FG%','ft%':'FT%','2pt%':'2PT%','3pt%':'3PT%',
                            'paint%':'Paint%'})
    elif stat_view == 'Per 40 Min.' or stat_view == 'Per 100 Poss.':
        datadf = datadf.rename(columns=
                         {'points': 'Points', 'rebounds': 'Total Rebounds', 'offensive_rebounds': 'ORB',
                          'defensive_rebounds': 'DRB', 'blocks': 'Blocks', 'assists': 'Assists',
                          'turnovers': 'TO', 'steals': 'Steals'})
    columns = [{"name": i, "id": i} for i in datadf.columns]
    data = datadf.to_dict('records')
    #return roster_options, columns, data
    return roster_check_options, columns, data



##################################################
# Advanced Stats
##################################################

@app.callback(
    dash.dependencies.Output('advanced_player', 'options'),
    dash.dependencies.Output('advanced_stats', 'columns'),
    dash.dependencies.Output('advanced_stats', 'data'),
    dash.dependencies.Input('advanced_team', 'value'),
    dash.dependencies.Input('advanced_player', 'value'),
    dash.dependencies.Input('advanced_season', 'value')
)
def advanced_stats(team, player, season):
    roster = np.unique(play_half[(play_half['market'] == team)]['full_name'])
    roster_options = [{'label': i, 'value': i} for i in roster]
    roster_check = np.unique(play_half[(play_half['market'] == team) & (play_half['season'] == season)]['full_name'])
    roster_check_options = [{'label': i, 'value': i} for i in roster_check]
    table_view = 'Advanced Stats'
    column_labels = ['USG%', 'AST%', 'TOV%', 'ORB%', 'BLK%', 'STL%', 'DRB%']
    columns = [{"name": i, "id": i} for i in column_labels]
    # ah is apphelper.py
    datadf, data = ah.advanced_stats(player, season)
    columns = [{"name": i, "id": i} for i in datadf.columns]

    # return roster_options, columns, data
    return roster_check_options, columns, data


##################################################
# INSERT NEW ELEMENTS HERE                       #
##################################################
# player averages for: career, season, 5 games
# compare against: position averages, team averages

##################################################
##################################################


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
