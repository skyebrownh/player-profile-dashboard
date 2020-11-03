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
# Helper gathers the column data, formats the columns appropriately
# Outputs either a general box score of the shooting %'s by half
###################################################
def box_score_data(player, table_view, season):
    if table_view=='Shooting % By Half':
        stats = ['scheduled','opponent_name','period','minutes','field_goals_pct','free_throws_pct','two_points_pct','three_points_pct','true_shooting_pct','effective_fg_pct']
        datadf = play_half[(play_half['full_name']==player) & (play_half['season']==season)][stats]
        datadf.scheduled = pd.DatetimeIndex(datadf.scheduled).strftime("%m-%d-%Y")
        datadf = datadf.rename(columns=
                           {'scheduled': 'Date', 'opponent_name': 'Opponent', 'period':'Half','minutes':'Minutes','field_goals_pct':'FG%',
                            'free_throws_pct':'FT%','two_points_pct':'2PT%','three_points_pct':'3PT%','true_shooting_pct':'TS%',
                            'effective_fg_pct':'EFG%'
                            })
        print(datadf)
    #############################################################################################################################################################
    elif table_view== 'General':
        #Changed to general so more statements can be added later

        ######################################################################################################################################################
        # Outputs the box score with an additional column used for giving the result of each game
        ######################################################################################################################################################
        #for all the teams stats in that season
        stats = ['scheduled', 'opponent_name', 'game_id', 'team_points']
        team1 = play_half[(play_half['full_name'] == player) & (play_half['season'] == season)][stats]
        team_name = np.unique(play_half[(play_half['full_name'] == player)]['market'])
        #have to do this to access the actual value
        team_name = team_name[0] 
        #all the people that have played that team that year
        team2 = play_half[(play_half['opponent_name'] == team_name) & (play_half['season'] == season)][stats]
        #print(team2)
        comb = pd.merge(team1, team2, on='game_id')
        #drops duplicates
        unq = comb.drop_duplicates()
        #insert new column at index 0, 'res' is the name of the column, intiallized the string of "W" (Win or Loss)
        unq.insert(0, 'res', "W")
        #filling the 'res' column with Win or Loss and scores.
        for r in range(len(unq)):
            if (unq['team_points_x'].iloc[r] < unq['team_points_y'].iloc[r]):
                unq['res'].iloc[r] = "L"
            unq['res'].iloc[r] = "(" + unq['res'].iloc[r] + ", " + str(unq['team_points_x'].iloc[r]) + "-" + str(
                unq['team_points_y'].iloc[r]) + ")"

        stats = ['scheduled', 'opponent_name', 'minutes', 'efficiency', 'points', 'rebounds', 'assists', 'turnovers',
                 'steals', 'blocks', 'game_id', 'period']
        #1st period         
        p1 = play_half[(play_half['full_name'] == player) & (play_half['season'] == season) & (play_half['period'] == 1)][
            stats]
        #2nd period
        p2 = play_half[(play_half['full_name'] == player) & (play_half['season'] == season) & (play_half['period'] == 2)][
            stats]

        toupdate = ['points', 'rebounds', 'assists', 'turnovers', 'steals', 'blocks']

        stats = ['scheduled', 'opponent_name', 'total_minutes', 'efficiency', 'points', 'rebounds', 'assists',
                 'turnovers',
                 'steals', 'blocks', 'game_id', 'period', 'rank']
        #1st period  
        p1 = play_half[(play_half['full_name'] == player) & (play_half['season'] == season) & (play_half['period'] == 1)][
            stats]
        #2nd period  
        p2 = play_half[(play_half['full_name'] == player) & (play_half['season'] == season) & (play_half['period'] == 2)][
            stats]
        comb = pd.merge(p1, p2, on='game_id') #_x,_y
        datadf = pd.merge(comb, unq, on='game_id') #_x,_x #_y,_x

        #took applicatable cols that we want to update
        toupdate = ['points', 'rebounds', 'assists', 'turnovers', 'steals', 'blocks', 'efficiency']
        #create string
        for i in toupdate:
            x = i + "_x"
            y = i + "_y"
            datadf[i] = datadf[x] + datadf[y]
        #print(datadf.columns)
        datadf['scheduled'] = datadf['scheduled_x_y']
        datadf['opponent_name'] = datadf['opponent_name_x_x']
        datadf['total_minutes'] = datadf['total_minutes_x']
        
        #Extracts these columns to be displayed
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

    ##########################################################################################
    ##      SEASON AVERAGES HELPER
    ##########################################################################################
    elif table_view == 'Season Averages':
        stats = [ 'game_id', 'points', 'rebounds', 'blocks', 'assists', 'turnovers']
        #1st period
        p1 = play_half[(play_half['full_name'] == player) & (play_half['season'] == season) & (play_half['period'] == 1)][
            stats]
        #2nd period
        p2 = play_half[(play_half['full_name'] == player) & (play_half['season'] == season) & (play_half['period'] == 2)][
            stats]
        comb = pd.merge(p1, p2, on='game_id')
        datadf = comb.drop_duplicates()
        
        #get the stats to average without the gameid
        avg_stats = ['points', 'rebounds', 'blocks', 'assists', 'turnovers']

        #combines the two halfs, litteraly copied and pasted from 'General' stats
        for i in avg_stats:
            x = i + "_x"
            y = i + "_y"
            datadf[i] = datadf[x] + datadf[y]
        #drops extra _x and _y columns and gives us only the combined columns
        datadf = datadf[avg_stats]
        
        #This will remove a row that is all zeroes, but will not work with the minutes column since minutes is not an int format
        datadf = datadf.loc[(datadf!=0).any(1)]

        #finds the mean of a column
        avg_columns = datadf.mean(axis=0) 
        #rounds the columns
        avg_columns = avg_columns.round(decimals=1)

        datadf = pd.DataFrame(avg_columns)
        datadf = datadf.transpose()
       
        #This stores rounded averages as a series, which is then converted to a list so that ...
        #...the list can be placed into a new df to be returned as a df, this allows easy changes...
        #... later on to what stats can be displayed and calculated
        #avg_columns = avg_columns.values
        #to_update = avg_columns.tolist()
        #all_rows = [to_update]
        #creates empty dataframe with only column names 
        #datadf = pd.DataFrame(columns = [avg_stats])
        #updates the empty data frame with the calculated averages, you would not believe how long it took me to figure how to do this so that it could adapt for future uses
        #datadf = pd.DataFrame(all_rows,columns = [avg_stats])
        
        datadf = datadf.rename(columns=
                           {'points':'Points', 'rebounds':'Rebounds', 'blocks':'Blocks', 'assists':'Assists', 'turnovers':'Turnovers'})
        #print(datadf)
        

        '''
        WARNINGS:
        AS IT IS NOW, THE DATA FRAME CREATED CONFLICTS WITH SOMETHING IN APP.PY I BELIEVE, I THINK THIS NEEDS TO BE CHANGED TO DISPLAY THE DATA FRAME ON THE WEBSITE
        ALSO MINUTES IS CURRENTLY UNABLE TO BE AVERAGED AS IT IS NOT AN INT
        NEED TO ADD AVERAGES FOR SHOOTING BUT NEED TO TALK ABOUT HOW TO DO THIS, DO IT BY GAME OR OVERALL
        '''
        
        
##################################################        
##################################################
#create dictionary 
##################################################
##################################################
    data = datadf.to_dict('records')
 #   print(data)
    return datadf,data


##################################################
# ADVANCED STATS HELPER
##################################################

def advanced_stats(player, season):
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

    team = team_boxscore[(team_boxscore['market'] == team_name) &
                         (team_boxscore['game_id'].isin(player_stats['game_id']))][team_categories]
    opponent = team_boxscore[(team_boxscore['market'] != team_name) &
                         (team_boxscore['game_id'].isin(player_stats['game_id']))][team_categories]

    comb = pd.merge(team, opponent, on='game_id')
    comb = pd.merge(player_stats, comb, on='game_id')
    df = comb.drop_duplicates()

    FGA = 'field_goals_att'; tm_FGA = FGA+'_x'; opp_FGA = FGA+'_y'
    FTA = 'free_throws_att'; tm_FTA = FTA+'_x'; opp_FTA = FTA+'_y'
    TOV = 'turnovers'; tm_TOV = TOV+'_x'; opp_TOV = TOV+'_y'
    MP = 'total_minutes'; tm_MP = 'minutes_x'; opp_MP = 'minutes_y'
    FG = 'field_goals_made'; tm_FG = FG+'_x'; opp_FG = FG+'_y'
    AST = 'assists';
    ORB = 'offensive_rebounds'; tm_ORB = ORB+'_x'; opp_ORB = ORB+'_y'
    BLK = 'blocks'
    STL = 'steals'
    DRB = 'defensive_rebounds'; tm_DRB = DRB+'_x'; opp_DRB = DRB+'_y'
    tm_3PA = 'three_points_att_x'; opp_3PA = 'three_points_att_y';
    opp_Poss = 'opp_poss'
    df[MP] = df[MP].str.split(':').str.get(0)
    df[tm_MP] = df[tm_MP].str.split(':').str.get(0).astype(int) * 60 + df[tm_MP].str.split(
        ':').str.get(1).astype(int)
    df[opp_MP] = df[opp_MP].str.split(':').str.get(0).astype(int) * 60 + df[opp_MP].str.split(
        ':').str.get(1).astype(int)
    for i in df:
        if i != 'game_id':
            df[i] = df[i].astype(int)

    oppPoss=0.5*((df[opp_FGA]+0.4*df[opp_FTA]-1.07*(df[opp_ORB]/(df[opp_ORB]+df[tm_DRB]))*(df[opp_FGA]-df[opp_FG])
      +df[opp_TOV])+(df[tm_FGA]+0.4*df[tm_FTA]-1.07*(df[tm_ORB]/(df[tm_ORB]+df[opp_DRB]))*(df[tm_FGA]-df[tm_FG])+df[tm_TOV]))
    df['opp_poss'] = oppPoss

    USG = 100 * ((df[FGA]+ 0.44 * df[FTA] + df[TOV]) * (df[tm_MP] / 5)) / (df[MP] * (df[tm_FGA] + 0.44 * df[tm_FTA]
        + df[tm_TOV]))
    AST = 100 * df[AST] / (((df[MP] / (df[tm_MP] / 5)) * df[tm_FG]) - df[FG])
    TOV = 100 * df[TOV] / (df[FGA] + 0.44 * df[FTA] + df[TOV])
    ORB = 100 * (df[ORB] * (df[tm_MP] / 5)) / (df[MP] * (df[tm_ORB] + df[opp_DRB]))
    BLK = 100 * (df[BLK] * (df[tm_MP] / 5)) / (df[MP] * (df[opp_FGA] - df[opp_3PA]))
    STL = 100 * (df[STL] * (df[tm_MP] / 5)) / (df[MP] * df[opp_Poss])
    DRB = 100 * (df[DRB] * (df[tm_MP] / 5)) / (df[MP] * (df[tm_DRB] + df[opp_ORB]))

    dataframe = df[['game_id']].copy()
    dataframe['USG%'] = USG
    dataframe['AST%'] = AST
    dataframe['TOV%'] = TOV
    dataframe['ORB%'] = ORB
    dataframe['BLK%'] = BLK
    dataframe['STL%'] = STL
    dataframe['DRB%'] = DRB
    avg_columns = dataframe.mean(axis=0)
    # rounds the columns
    avg_columns = avg_columns.round(decimals=1)

    datadf = pd.DataFrame(avg_columns)
    datadf = datadf.transpose()


    data = datadf.to_dict('records')
    #   print(data)
    return datadf, data

##################################################
# Add new helpers here!
##################################################