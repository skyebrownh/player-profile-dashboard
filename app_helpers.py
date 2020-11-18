import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash_html_components as html
import dash_table as dt
import numpy as np
from plotly.subplots import make_subplots

pd.options.mode.chained_assignment = None

play_half = pd.read_csv('./player_half_v1.csv')
# league_info = pd.read_csv('./league_info.csv')
team_boxscore = pd.read_csv('team_boxscores_v1.csv')
team_names = np.unique(play_half['market'])
player_names = np.unique(play_half['full_name'])


##################################################
# BOX SCORE HELPER
###################################################
def box_score_data(player, table_view, season):

    #   TO FIX:
    #   NEED TO FIX THIS TO DO SHOOTING PERCENTAGE BY GAME NOT HALF
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
        # Outputs the box score with an additional column used for giving the result of each game
        ######################################################################################################################################################

        # Sums the statistics for each game
        stats = ['game_id', 'full_name', 'points', 'rebounds', 'blocks', 'assists', 'turnovers', 'total_minutes']
        gamestats = play_half[(play_half['full_name'] == player) & (play_half['season'] == season)][stats].groupby(
            'game_id').sum()

        # Gets scheduled, opponenet name, and game_id
        info = ['scheduled', 'opponent_name', 'game_id']
        gameinfo = play_half[(play_half['full_name'] == player) & (play_half['season'] == season)][info]
        gameinfo = gameinfo.drop_duplicates(keep="first")

        # Calculates game score, merges
        gamescoreinfo = ['game_id', 'points', 'points_against']
        market = np.unique(play_half[(play_half['full_name'] == player) & (play_half['season'] == season)]['market'])[0]
        gamescore = team_boxscore[(team_boxscore['market'] == market) & (team_boxscore['season'] == season)][gamescoreinfo]
        gamescore.insert(0, 'result', "W")
        for i in range(len(gamescore)):
            if gamescore['points'].iloc[i] > gamescore['points_against'].iloc[i]:
                gamescore['result'].iloc[i] = "(W, " + str(gamescore['points'].iloc[i]) + "-" + str(
                    gamescore['points_against'].iloc[i]) + ")"
            else:
                gamescore['result'].iloc[i] = "(L, " + str(gamescore['points'].iloc[i]) + "-" + str(
                    gamescore['points_against'].iloc[i]) + ")"
        box_scores = pd.merge(gameinfo, gamescore, on='game_id').drop(columns=['points', 'points_against'])

        # Extracts total minutes column
        mininfo = ['total_minutes', 'game_id']
        minutes = play_half[(play_half['full_name'] == player) & (play_half['season'] == season)][mininfo]
        minutes = minutes.drop_duplicates(keep="first")

        # Merges all the seperate dataframes into one
        box_scores = pd.merge(box_scores, minutes, on='game_id')
        box_scores = pd.merge(box_scores, gamestats, on='game_id').drop(columns='game_id')

        # Formats the column header, adjusts date to readable form and converts it to dictionary for output in Dash
        box_scores.scheduled = pd.DatetimeIndex(box_scores.scheduled).strftime("%m-%d-%Y")
        box_scores = box_scores.rename(columns=
                           {'scheduled': 'Date', 'opponent_name': 'Opponent', 'result':'Result','total_minutes':'Minutes','efficiency':'Efficiency',
                            'points':'Points','rebounds':'Total Rebounds','assists':'Assists','turnovers':'Turnovers',
                            'steals':'Steals','blocks':'Blocks',#'game_id':'GameID'
                            })
    data = box_scores.to_dict('records')
    return box_scores,data


##################################################
# SEASON AVERAGES & SHOOTING STATS HELPER
##################################################


def player_average_data(player, table_view, season):
    # ['General', 'Advanced', 'Per 36','Per 100 Poss.']
    player_categories = ['game_id', 'field_goals_att', 'field_goals_made', 'free_throws_att', 'turnovers', 'assists',
                         'total_minutes', 'offensive_rebounds', 'blocks', 'steals', 'defensive_rebounds', 'full_name',
                         'points', 'rebounds']
    stats = ['points', 'rebounds', 'blocks', 'assists', 'turnovers', 'total_minutes']
    #TODO: Fix career averages
    if season == 0:
        gamestats = play_half[(play_half['full_name'] == player) &
                              (play_half['total_minutes'] != "00:00")][player_categories].groupby('game_id').sum()
        # Extracts total minutes column
        mininfo = ['total_minutes', 'game_id']
        minutes = play_half[(play_half['full_name'] == player) & (play_half['total_minutes'] != '00:00')][mininfo]
    #TODO: Check 5 game trailing average
    elif season == 5:
        gamestats = play_half[(play_half['full_name'] == player) &
                              (play_half['total_minutes'] != "00:00")][player_categories].groupby('game_id').sum()
        gamestats = gamestats[:5]
        # Extracts total minutes column
        mininfo = ['total_minutes', 'game_id']
        minutes = play_half[(play_half['full_name'] == player) & (play_half['total_minutes'] != '00:00')][mininfo]
    else:
        gamestats = play_half[(play_half['full_name'] == player) & (play_half['season'] == season) & (
            play_half['total_minutes'] != "00:00")][player_categories].groupby('game_id').sum()
        # Extracts total minutes column
        mininfo = ['total_minutes', 'game_id']
        minutes = play_half[(play_half['full_name'] == player) & (play_half['season'] == season)
                        & (play_half['total_minutes'] != '00:00')][mininfo]


    minutes = minutes.drop_duplicates(keep="first")
    minutes['total_minutes'] = minutes['total_minutes'].str.split(':').str.get(0).astype(int)
    # Merges all the seperate dataframes into one
    season_avg = pd.merge(gamestats, minutes, on='game_id')
    season_avg = season_avg.mean()
    season_avg = np.round(season_avg, 1)
    season_avg = pd.DataFrame(season_avg)
    season_avg = season_avg.transpose()


    if table_view=='General':
        season_avg = season_avg[stats]
        shooting = ['season', 'field_goals_att', 'field_goals_made', 'free_throws_att', 'free_throws_made',
                    'two_points_att', 'two_points_made',
                    'three_points_att', 'three_points_made', 'points_in_paint_att', 'points_in_paint_made']
        shootingstats = play_half[(play_half['full_name'] == player) & (play_half['season'] == season)][
            shooting].groupby('season').sum()

        fg = (shootingstats['field_goals_made'] / shootingstats['field_goals_att']) * 100.0
        ft = (shootingstats['free_throws_made'] / shootingstats['free_throws_att']) * 100.0
        twopt = (shootingstats['two_points_made'] / shootingstats['two_points_att']) * 100.0
        threept = (shootingstats['three_points_made'] / shootingstats['three_points_att']) * 100.0
        paint = (shootingstats['points_in_paint_made'] / shootingstats['points_in_paint_att']) * 100.0

        avg = ['fg%', 'ft%', '2pt%', '3pt%', 'paint%']
        avg_val = [fg, ft, twopt, threept, paint]
        avg_val = np.round(avg_val, 1)

        shoot_avg = [{avg[i]: avg_val[i]} for i in range(len(avg))]
        shoot_df = pd.DataFrame(shoot_avg)
        shoot_df = shoot_df.mean(axis=0, skipna=True)
        shoot_df = pd.DataFrame(shoot_df)
        shoot_df = shoot_df.transpose()
        shoot_df.insert(0, 'season', 2019)
        season_avg.insert(0, 'season', 2019)

        avg = pd.merge(season_avg, shoot_df, on='season').drop(columns='season')





    #################################################################
    # Calculate PER 40, & PER 100 Possessions
    #################################################################
    elif table_view == 'Per 40 Min.':
        stats = ['points', 'rebounds', 'offensive_rebounds', 'defensive_rebounds', 'assists', 'blocks', 'turnovers']
        avg = (season_avg[stats]/season_avg['total_minutes'][0]) *40.0          # PER 40 = stat/MP * 40 min
        avg = np.round(avg, 1)
        # Rename column headers

    elif table_view == 'Per 100 Poss.':
        stats = ['points', 'rebounds', 'offensive_rebounds', 'defensive_rebounds', 'assists', 'blocks', 'turnovers']
        avg_poss = calc_Poss(player, season, False).mean()
        avg = (season_avg[stats]/avg_poss) *100.0       #  PER 100 = stat/poss * 100 poss
        avg = np.round(avg, 1)
        # Rename column headers


    # Returns the values to be output in the table
    data = avg.to_dict('records')
    return avg, data


##################################################
# ADVANCED STATS HELPER
##################################################


def advanced_stats(player, season):
    # Equations used for calculating advanced stats
    # USG%: 100 * ((FGA + 0.44 * FTA + TOV) * (Tm MP / 5)) / (MP * (Tm FGA + 0.44 * Tm FTA + Tm TOV))
    # ORtg:
    # AST%: 100 * AST / (((MP / (Tm MP / 5)) * Tm FG) - FG)
    # TOV%: 100 * TOV / (FGA + 0.44 * FTA + TOV)
    # ORB%: 100 * (ORB * (Tm MP / 5)) / (MP * (Tm ORB + Opp DRB))
    # BLK%: 100 * (BLK * (Tm MP / 5)) / (MP * (Opp FGA - Opp 3PA))
    # STL%: 100 * (STL * (Tm MP / 5)) / (MP * Opp Poss)
    # Poss: 0.5 * ((Tm FGA + 0.4 * Tm FTA - 1.07 * (Tm ORB / (Tm ORB + Opp DRB)) * (Tm FGA - Tm FG) + Tm TOV) +
    # (Opp FGA + 0.4 * Opp FTA - 1.07 * (Opp ORB / (Opp ORB + Tm DRB)) * (Opp FGA - Opp FG) + Opp TOV))
    # Opp Poss: 0.5 * ((Opp FGA + 0.4 * Opp FTA - 1.07 * (Opp ORB / (Opp ORB + Tm DRB)) * (Opp FGA - Opp FG) + Opp TOV) +
    # (Tm FGA + 0.4 * Tm FTA - 1.07 * (Tm ORB / (Tm ORB + Opp DRB)) * (Tm FGA - Tm FG) + Tm TOV))
    # FOUL%:
    # DRB%: 100 * (DRB * (Tm MP / 5)) / (MP * (Tm DRB + Opp ORB))

    # stats that we want to extract from dataset
    player_categories = ['game_id', 'field_goals_att', 'field_goals_made', 'free_throws_att', 'turnovers', 'assists',
                         'total_minutes', 'offensive_rebounds', 'blocks', 'steals', 'defensive_rebounds']
    team_categories = ['game_id', 'minutes', 'field_goals_att', 'free_throws_att', 'turnovers', 'field_goals_made',
                       'offensive_rebounds', 'defensive_rebounds', 'three_points_att']
    # 1st half
    p1 = play_half[(play_half['full_name'] == player) & (play_half['season'] == season) & (play_half['period'] == 1)][
        player_categories]
    # 2nd half
    p2 = play_half[(play_half['full_name'] == player) & (play_half['season'] == season) & (play_half['period'] == 2)][
        player_categories]

    comb = pd.merge(p1, p2, on='game_id')
    player_stats = comb.drop_duplicates()

    # combines the two halfs, literally copied and pasted from 'General' stats
    for i in player_categories:
        if i != 'game_id':
            x = i + "_x"
            y = i + "_y"
            player_stats[i] = player_stats[x] + player_stats[y]
    player_stats['total_minutes'] = player_stats['total_minutes_x']
    # drops extra _x and _y columns and gives us only the combined columns
    player_stats = player_stats[player_categories]
    team_name = np.unique(play_half[(play_half['full_name'] == player)]['market'])
    # have to do this to access the actual value
    team_name = team_name[0]

    # team and opponent stats by game
    team = team_boxscore[(team_boxscore['market'] == team_name) &
                         (team_boxscore['game_id'].isin(player_stats['game_id']))][team_categories]
    opponent = team_boxscore[(team_boxscore['market'] != team_name) &
                             (team_boxscore['game_id'].isin(player_stats['game_id']))][team_categories]

    comb = pd.merge(team, opponent, on='game_id')
    comb = pd.merge(player_stats, comb, on='game_id')
    df = comb.drop_duplicates()

    # setting variables for accessing columns in dataframe
    FGA = 'field_goals_att'
    tm_FGA = FGA + '_x'
    opp_FGA = FGA + '_y'
    FTA = 'free_throws_att'
    tm_FTA = FTA + '_x'
    opp_FTA = FTA + '_y'
    TOV = 'turnovers'
    tm_TOV = TOV + '_x'
    opp_TOV = TOV + '_y'
    MP = 'total_minutes'
    tm_MP = 'minutes_x'
    opp_MP = 'minutes_y'
    FG = 'field_goals_made'
    tm_FG = FG + '_x'
    opp_FG = FG + '_y'
    AST = 'assists'
    ORB = 'offensive_rebounds'
    tm_ORB = ORB + '_x'
    opp_ORB = ORB + '_y'
    BLK = 'blocks'
    STL = 'steals'
    DRB = 'defensive_rebounds'
    tm_DRB = DRB + '_x'
    opp_DRB = DRB + '_y'
    tm_3PA = 'three_points_att_x'
    opp_3PA = 'three_points_att_y'
    opp_Poss = 'opp_poss'

    # converting minutes string into int
    df[MP] = df[MP].str.split(':').str.get(0)
    df[tm_MP] = df[tm_MP].str.split(':').str.get(0).astype(int) * 60 + df[tm_MP].str.split(
        ':').str.get(1).astype(int)
    df[opp_MP] = df[opp_MP].str.split(':').str.get(0).astype(int) * 60 + df[opp_MP].str.split(
        ':').str.get(1).astype(int)
    for i in df:
        if i != 'game_id':
            df[i] = df[i].astype(int)


    df['opp_poss'] = calc_Poss(player,season, True)     #calculate opponent possession

    # calculating advanced stats
    USG = 100 * ((df[FGA] + 0.44 * df[FTA] + df[TOV]) * (df[tm_MP] / 5)) / (df[MP] * (df[tm_FGA] + 0.44 * df[tm_FTA]
                                                                                      + df[tm_TOV]))
    AST = 100 * df[AST] / (((df[MP] / (df[tm_MP] / 5)) * df[tm_FG]) - df[FG])
    TOV = 100 * df[TOV] / (df[FGA] + 0.44 * df[FTA] + df[TOV])
    ORB = 100 * (df[ORB] * (df[tm_MP] / 5)) / (df[MP] * (df[tm_ORB] + df[opp_DRB]))
    BLK = 100 * (df[BLK] * (df[tm_MP] / 5)) / (df[MP] * (df[opp_FGA] - df[opp_3PA]))
    STL = 100 * (df[STL] * (df[tm_MP] / 5)) / (df[MP] * df[opp_Poss])
    DRB = 100 * (df[DRB] * (df[tm_MP] / 5)) / (df[MP] * (df[tm_DRB] + df[opp_ORB]))

    # putting series into dataframe
    dataframe = df[['game_id']].copy()
    dataframe['USG%'] = USG
    dataframe['AST%'] = AST
    dataframe['TOV%'] = TOV
    dataframe['ORB%'] = ORB
    dataframe['BLK%'] = BLK
    dataframe['STL%'] = STL
    dataframe['DRB%'] = DRB
    avg_columns = dataframe.mean(axis=0)        #avg the columns
    # rounds the columns
    avg_columns = avg_columns.round(decimals=1)

    datadf = pd.DataFrame(avg_columns)
    datadf = datadf.transpose()

    data = datadf.to_dict('records')
    #   print(data)
    return datadf, data


def get_player_bar_plot(season, team, player, per_unit, stat_names, stat_choices, comparison_names, comparison_choices):
    ludis_colors = ['#A369EC', '#CBEBE5', '#476AF6', '#FF8267', '#b9b9b9', '#FFFFFF']
    season_avg, data = player_average_data(player, 'General', season)
    season_avg = season_avg.rename(columns=
                         {'points': 'Points', 'rebounds': 'Rebounds', 'blocks': 'Blocks', 'assists': 'Assists',
                          'turnovers': 'TO'})
    season_avg = season_avg.round(2)
    career_avg, data = player_average_data(player, 'General', 0)
    career_avg = career_avg.rename(columns=
                      {'points': 'Points', 'rebounds': 'Rebounds', 'blocks': 'Blocks', 'assists': 'Assists',
                       'turnovers': 'TO'})
    career_avg = career_avg.round(2)
    trailing_avg, data = player_average_data(player, 'General', 5)
    trailing_avg = trailing_avg.rename(columns=
                      {'points': 'Points', 'rebounds': 'Rebounds', 'blocks': 'Blocks', 'assists': 'Assists',
                       'turnovers': 'TO'})
    trailing_avg = trailing_avg.round(2)
    team_name = np.unique(play_half[(play_half['full_name'] == player)]['market'])
    # have to do this to access the actual value
    team_name = team_name[0]
    """
    league_season_avg = df_season[stats].mean().round(2)
    team_season_avg = df_season[df_season.team_id == team][stats].round(2).values[0]
    scout_season_avg = df_season[df_season.team_id == scout][stats].round(2).values[0]
    team_name = df_season[(df_season.team_id == team)]['market'].values[0]

    if len(matchups) > 0:
        print("hello")

        game_stats = df_game[(df_game.matchup.isin(matchups)) & \
                             (df_game.team_id == team)][stats].mean().round(2)
        opponents = df_game[(df_game.matchup.isin(matchups)) & \
                            (df_game.team_id == team)]['opponent_id'].unique()
        opponent_avg = df_season[(df_season.team_id.isin(opponents))][stats].mean().round(2)
        opponents_game = df_game[(df_game.matchup.isin(matchups)) & \
                                 (df_game.team_id != team)][stats].mean().round(2)

    else:
        game_stats = team_season_avg
        opponents = df_game[(df_game.team_id == team)]['opponent_id'].unique()
        opponent_avg = df_season[(df_season.team_id.isin(opponents))][stats].mean().round(2)
        opponents_game = opponent_avg
    """
    #TODO: Automate the creation of this list
    data_list = [season_avg, career_avg, trailing_avg]
    #stats = ['PPG', 'RPG', 'BPG', 'APG']
    stat = [0,1,2]
    #comparison_choices = [0,1,2]
    #comparison_names = ['Season Avg.', 'Career Avg.', '5-game Avg.', 'Team Avg.']
    #for i in stat_choices:
        #print(stat_names[i])
        #print(data_list[i])
    #print("stat_names: ",stat_names)
    #print("stat_choices: ",stat_choices)
    #print("comparison_names: ", comparison_names)
    #print("comparison_choices: ", comparison_choices)
    stats = []
    for i in stat_choices:
        stats.append(stat_names[i])
    categories = []
    for i in comparison_choices:
        categories.append(comparison_names[i])
    for i in range(len(data_list)):
        print(data_list[i].columns)
        print(data_list[i][stats])
        data_list[i] = data_list[i][stats].values[0]
    fig = go.Figure(data=[
        go.Bar(name=categories[i], x=stats, y=data_list[i], text=data_list[i],
        #go.Bar(name=comparison_names[comparison_choices], x=stats, y=data_list[stat], text=data_list[stat],
               marker_color=ludis_colors[i],
               hovertemplate=
               ""
               ) for i in range(len(categories))])

    fig.update_layout(
        barmode='group',
        title={
            'text': "Player Comparison: {}".format(player),
            'font': {'size': 30,
                     'color': '#FFFFFF',
                     'family': 'Courier New, monospace'}},
        xaxis=dict(
            ticktext=stats,
            tickvals=[0, 1, 2, 3],
            tickmode="array",
            tickfont=dict(size=15, color='#FFFFFF'),
            titlefont=dict(size=30, color='#FFFFFF')),
        legend=dict(font=dict(color='#FFFFFF')),
        yaxis=dict(
            gridcolor='#FFFFFF',
            tickfont=dict(size=15, color='#FFFFFF')),
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
    )

    fig.update_traces(textposition='auto',
                      texttemplate="")


    """
    table_df = df_game[(df_game.matchup.isin(matchups)) & \
                       (df_game.team_id == team)]
    # print(table_df)
    table_df = color(table_df).rename(
        columns={'market': 'Market', "home_away": "Home/Away", 'opponent_alias': 'Opponent', 'alias_pts': 'Team Score',
                 'opponent_pts': 'Opp. Score'})
    table_df[stats] = table_df[stats].round(2)
    table_df = table_df.sort_values(by='date', ascending=False)
    data = table_df.to_dict(orient='records')
    """
    return fig
##################################################
# Add new helpers here!
##################################################


# Calculate Possession Stat
# If it is the to be calculated for the opponent, switch team stats with opponent stats


def calc_Poss(player, season, isOpp):

    # stats that we want to extract from the dataset
    team_categories = ['game_id', 'minutes', 'field_goals_att', 'free_throws_att', 'turnovers', 'field_goals_made',
                       'offensive_rebounds', 'defensive_rebounds', 'three_points_att']

    player_stats = play_half[(play_half['full_name'] == player) & (play_half['season'] == season)][
        'game_id']

    team_name = np.unique(play_half[(play_half['full_name'] == player)]['market'])
    # have to do this to access the actual value
    team_name = team_name[0]

    # team stats
    team = team_boxscore[(team_boxscore['market'] == team_name) &
                         (team_boxscore['game_id'].isin(player_stats))][team_categories]
    # opponent stats
    opponent = team_boxscore[(team_boxscore['market'] != team_name) &
                             (team_boxscore['game_id'].isin(player_stats))][team_categories]

    comb = pd.merge(team, opponent, on='game_id')
    comb = pd.merge(player_stats, comb, on='game_id')
    df = comb.drop_duplicates()

    # setting variables to accesses columns in dataframe
    tm_FGA = 'field_goals_att_x'
    opp_FGA = 'field_goals_att_y'
    tm_FTA = 'free_throws_att_x'
    opp_FTA = 'free_throws_att_y'
    tm_TOV = 'turnovers_x'
    opp_TOV = 'turnovers_y'
    tm_MP = 'minutes_x'
    opp_MP = 'minutes_y'
    tm_FG = 'field_goals_made_x'
    opp_FG = 'field_goals_made_y'
    tm_ORB = 'offensive_rebounds_x'
    opp_ORB = 'offensive_rebounds_y'
    tm_DRB = 'defensive_rebounds_x'
    opp_DRB = 'defensive_rebounds_y'

    # converting minute string into an int
    df[tm_MP] = df[tm_MP].str.split(':').str.get(0).astype(int) * 60 + df[tm_MP].str.split(
        ':').str.get(1).astype(int)
    df[opp_MP] = df[opp_MP].str.split(':').str.get(0).astype(int) * 60 + df[opp_MP].str.split(
        ':').str.get(1).astype(int)

    # if is opponent poss, switch opponent stats and team stats
    if isOpp:
        poss = 0.5 * ((df[opp_FGA] + 0.4 * df[opp_FTA] - 1.07 * (df[opp_ORB] / (df[opp_ORB] + df[tm_DRB])) * (
                df[opp_FGA] - df[opp_FG])
                      + df[opp_TOV]) + (
                                 df[tm_FGA] + 0.4 * df[tm_FTA] - 1.07 * (df[tm_ORB] / (df[tm_ORB] + df[opp_DRB])) * (
                                     df[tm_FGA] - df[tm_FG]) + df[tm_TOV]))
    else:
        poss = 0.5 * ((df[tm_FGA] + 0.4 * df[tm_FTA] - 1.07 * (df[tm_ORB] / (df[tm_ORB] + df[opp_DRB])) * (
                df[tm_FGA] - df[tm_FG])
                      + df[tm_TOV]) + (
                                 df[opp_FGA] + 0.4 * df[opp_FTA] - 1.07 * (df[opp_ORB] / (df[opp_ORB] + df[tm_DRB])) * (
                                     df[opp_FGA] - df[opp_FG]) + df[opp_TOV]))

    # returns a series of possession by game
    return poss

