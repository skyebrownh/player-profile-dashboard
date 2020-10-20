import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash_html_components as html
import dash_table as dt
import numpy as np
from plotly.subplots import make_subplots

pd.options.mode.chained_assignment = None

play_half = pd.read_csv('./player_half_v1.csv')
league_info = pd.read_csv('./league_info.csv')
team_names = np.unique(play_half['market'])
player_names = np.unique(play_half['full_name'])


##################################################
# Helper gathers the column data, formats the columns appropriately
# Outputs either a general box score of the shooting %'s by half
###################################################
def box_score_data(player, table_view, season):
    if table_view=='Shooting % By Half':
        stats = ['scheduled','opponent_name','period','minutes', 'field_goals_pct','free_throws_pct','two_points_pct','three_points_pct','true_shooting_pct','effective_fg_pct']
        datadf = play_half[(play_half['full_name']==player) & (play_half['season']==season)][stats]
        datadf.scheduled = pd.DatetimeIndex(datadf.scheduled).strftime("%m-%d-%Y")
        datadf = datadf.rename(columns=
                           {'scheduled': 'Date', 'opponent_name': 'Opponent', 'period':'Half','minutes':'Minutes','field_goals_pct':'FG%',
                            'free_throws_pct':'FT%','two_points_pct':'2PT%','three_points_pct':'3PT%','true_shooting_pct':'TS%',
                            'effective_fg_pct':'EFG%'
                            })

    else:

        ######################################################################################################################################################
        # This commented out code output the stats without the result column. It still combines the two halves
        ######################################################################################################################################################
        # This joins the halves into one game and outputs the correct stats for the game
        # stats = ['scheduled', 'opponent_name', 'minutes', 'efficiency', 'points', 'rebounds', 'assists', 'turnovers',
        #          'steals', 'blocks', 'game_id', 'period','total_minutes']
        # p1 = play_half[(play_half['full_name'] == player) & (play_half['season'] == season) & (play_half['period'] == 1)][
        #     stats]
        # p2 = play_half[(play_half['full_name'] == player) & (play_half['season'] == season) & (play_half['period'] == 2)][
        #     stats]
        # comb = pd.merge(p1,p2,on='game_id')
        # toupdate = ['points', 'rebounds', 'assists', 'turnovers', 'steals', 'blocks','efficiency']
        # for i in toupdate:
        #     x = i+"_x"
        #     y = i+"_y"
        #     comb[i] = comb[x]+comb[y]
        # comb['scheduled'] = comb['scheduled_x']
        # comb['opponent_name'] = comb['opponent_name_x']
        # comb['total_minutes'] = comb['total_minutes_x']
        # final_stats = ['scheduled', 'opponent_name', 'total_minutes', 'efficiency', 'points', 'rebounds', 'assists', 'turnovers',
        #          'steals', 'blocks']
        # datadf = comb[final_stats]
        ######################################################################################################################################################

        ######################################################################################################################################################
        # Outputs the box score with an additional column used for giving the result of each game
        ######################################################################################################################################################
        stats = ['scheduled', 'opponent_name', 'game_id', 'team_points']
        team1 = play_half[(play_half['full_name'] == player) & (play_half['season'] == season)][stats]
        team_name = np.unique(play_half[(play_half['full_name'] == player)]['market'])
        team_name = team_name[0]
        team2 = play_half[(play_half['opponent_name'] == team_name) & (play_half['season'] == season)][stats]

        comb = pd.merge(team1, team2, on='game_id')
        unq = comb.drop_duplicates()
        unq.insert(0, 'res', "W")
        for r in range(len(unq)):
            if (unq['team_points_x'].iloc[r] < unq['team_points_y'].iloc[r]):
                unq['res'].iloc[r] = "L"
            unq['res'].iloc[r] = "(" + unq['res'].iloc[r] + ", " + str(unq['team_points_x'].iloc[r]) + "-" + str(
                unq['team_points_y'].iloc[r]) + ")"

        stats = ['scheduled', 'opponent_name', 'minutes', 'efficiency', 'points', 'rebounds', 'assists', 'turnovers',
                 'steals', 'blocks', 'game_id', 'period']
        p1 = \
        play_half[(play_half['full_name'] == player) & (play_half['season'] == season) & (play_half['period'] == 1)][
            stats]
        p2 = \
        play_half[(play_half['full_name'] == player) & (play_half['season'] == season) & (play_half['period'] == 2)][
            stats]
        toupdate = ['points', 'rebounds', 'assists', 'turnovers', 'steals', 'blocks']

        stats = ['scheduled', 'opponent_name', 'total_minutes', 'efficiency', 'points', 'rebounds', 'assists',
                 'turnovers',
                 'steals', 'blocks', 'game_id', 'period', 'rank']
        p1 = \
        play_half[(play_half['full_name'] == player) & (play_half['season'] == season) & (play_half['period'] == 1)][
            stats]
        p2 = \
        play_half[(play_half['full_name'] == player) & (play_half['season'] == season) & (play_half['period'] == 2)][
            stats]
        comb = pd.merge(p1, p2, on='game_id')
        datadf = pd.merge(comb, unq, on='game_id')

        toupdate = ['points', 'rebounds', 'assists', 'turnovers', 'steals', 'blocks', 'efficiency']
        for i in toupdate:
            x = i + "_x"
            y = i + "_y"
            datadf[i] = datadf[x] + datadf[y]
        datadf['scheduled'] = datadf['scheduled_x_y']
        datadf['opponent_name'] = datadf['opponent_name_x_x']
        datadf['total_minutes'] = datadf['total_minutes_x']
        final_stats = ['scheduled', 'opponent_name', 'res', 'total_minutes', 'efficiency', 'points', 'rebounds',
                       'assists',
                       'turnovers', 'steals', 'blocks']
        datadf = datadf[final_stats]

        ######################################################################################################################################################



        # Formats the column header, adjusts date to readable form and converts it to dictionary for output in Dash
        datadf.scheduled = pd.DatetimeIndex(datadf.scheduled).strftime("%m-%d-%Y")
        datadf = datadf.rename(columns=
                           {'scheduled': 'Date', 'opponent_name': 'Opponent', 'res':'Result','total_minutes':'Minutes','efficiency':'Efficiency',
                            'points':'Points','rebounds':'Total Rebounds','assists':'Assists','turnovers':'Turnovers',
                            'steals':'Steals','blocks':'Blocks',#'game_id':'GameID'
                            })
    data = datadf.to_dict('records')
    return datadf,data
##################################################
##################################################


##################################################
# Add new helpers here!
##################################################
##################################################
##################################################