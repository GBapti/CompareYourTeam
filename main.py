from flask import Flask, render_template, request
import pandas as pd
app = Flask(__name__)


#-------------------------Parti data-------------------------
csv_file_path = 'C:\\Users\\bapti\\Documents\\Projet\\Foot\\Base de données\\data_foot_v1\\data_foot_20240531.csv'
data_foot = pd.read_csv(csv_file_path)
dico_date = {}
dico_team = {}
dico_competition = {}

#-------------------------Partie fonction-------------------------
def get_date(data):
    date_minimum = min(data['Date'])
    date_maximum = max(data['Date'])
    return date_minimum,date_maximum

def get_info(data):
    teams = sorted(data['HomeTeam'].unique())
    competitions = sorted(data['Compétition'].unique())
    saisons = data['saison'].unique()
    return teams,competitions,saisons

def get_team_result(row, equipe_choisie):
    if row['HomeTeam'] == equipe_choisie:
        if row['NB BUT DOMICILE'] > row['NB BUT EXTERIEUR']:
            return 'WH'
        elif row['NB BUT DOMICILE'] < row['NB BUT EXTERIEUR']:
            return 'LH'
        else:
            return 'DH'
    elif row['AwayTeam'] == equipe_choisie:
        if row['NB BUT EXTERIEUR'] > row['NB BUT DOMICILE']:
            return 'WA'
        elif row['NB BUT EXTERIEUR'] < row['NB BUT DOMICILE']:
            return 'LA'
        else:
            return 'DA'
    else:
        return 'non concerné'

def get_team_goal_scored(row, equipe_choisie):
    if row['HomeTeam'] == equipe_choisie:
        return row['NB BUT DOMICILE']
    elif row['AwayTeam'] == equipe_choisie:
        return row['NB BUT EXTERIEUR']
    else:
        return 'non concerné'

def get_team_goal_conceded(row, equipe_choisie):
    if row['HomeTeam'] == equipe_choisie:
        return row['NB BUT EXTERIEUR']
    elif row['AwayTeam'] == equipe_choisie:
        return row['NB BUT DOMICILE']
    else:
        return 'non concerné'

def get_max_info(data):
    victoires = {}
    defaites = {}
    nuls = {}
    buts_marqués = {}
    buts_encaissés = {}
    for index, row in data.iterrows():
        buts_marqués[row["HomeTeam"]] = buts_marqués.get(row["HomeTeam"], 0) + row['NB BUT DOMICILE']
        buts_marqués[row["AwayTeam"]] = buts_marqués.get(row["AwayTeam"], 0) + row['NB BUT EXTERIEUR']
        buts_encaissés[row["HomeTeam"]] = buts_encaissés.get(row["HomeTeam"], 0) + row['NB BUT EXTERIEUR']
        buts_encaissés[row["AwayTeam"]] = buts_encaissés.get(row["AwayTeam"], 0) + row['NB BUT DOMICILE']
        if row["Résultat"] == "H":
            victoires[row["HomeTeam"]] = victoires.get(row["HomeTeam"], 0) + 1
            defaites[row["AwayTeam"]] = defaites.get(row["AwayTeam"], 0) + 1
        elif row["Résultat"] == "A":
            victoires[row["AwayTeam"]] = victoires.get(row["AwayTeam"], 0) + 1
            defaites[row["HomeTeam"]] = defaites.get(row["HomeTeam"], 0) + 1
        elif row["Résultat"] == "D":
            nuls[row["HomeTeam"]] = nuls.get(row["HomeTeam"], 0) + 1
            nuls[row["AwayTeam"]] = nuls.get(row["AwayTeam"], 0) + 1

    team_win_max = max(victoires, key=victoires.get)
    team_nul_max = max(nuls, key=nuls.get)
    team_lose_max = max(defaites, key=defaites.get)
    team_buts_marqués_max = max(buts_marqués, key=buts_marqués.get)
    team_buts_encaissés_max = max(buts_encaissés, key=buts_encaissés.get)

    max_win = victoires[team_win_max]
    max_nul = nuls[team_nul_max]
    max_lose = defaites[team_lose_max]
    buts_marqués_max = buts_marqués[team_buts_marqués_max]
    buts_encaissés_max = buts_encaissés[team_buts_encaissés_max]

    return team_win_max,team_nul_max,team_lose_max,max_win ,max_nul,max_lose,team_buts_marqués_max,team_buts_encaissés_max,buts_marqués_max,buts_encaissés_max

def get_max_info_for_team(data, team_selected):
    victoires = {}
    defaites = {}
    nuls = {}
    for index, row in data.iterrows():
        if row["Résultat"] == "H":
            if row["HomeTeam"] != team_selected:
                victoires[row["HomeTeam"]] = victoires.get(row["HomeTeam"], 0) + 1
            if row["AwayTeam"] != team_selected:
                defaites[row["AwayTeam"]] = defaites.get(row["AwayTeam"], 0) + 1
        elif row["Résultat"] == "A":
            if row["AwayTeam"] != team_selected:
                victoires[row["AwayTeam"]] = victoires.get(row["AwayTeam"], 0) + 1
            if row["HomeTeam"] != team_selected:
                defaites[row["HomeTeam"]] = defaites.get(row["HomeTeam"], 0) + 1
        elif row["Résultat"] == "D":
            if row["HomeTeam"] != team_selected:
                nuls[row["HomeTeam"]] = nuls.get(row["HomeTeam"], 0) + 1
            if row["AwayTeam"] != team_selected:
                nuls[row["AwayTeam"]] = nuls.get(row["AwayTeam"], 0) + 1

    team_win_max = max(victoires, key=victoires.get)
    team_nul_max = max(nuls, key=nuls.get)
    team_lose_max = max(defaites, key=defaites.get)

    max_win = victoires[team_win_max]
    max_nul = nuls[team_nul_max]
    max_lose = defaites[team_lose_max]

    return team_win_max,team_nul_max,team_lose_max,max_win ,max_nul,max_lose

#-------------------------Parti serveur application-------------------------
@app.route('/', methods=['GET', 'POST'])
def home():

    if request.method == 'POST':
        if request.form.get('form_name') == 'FormulaireDate':

            dico_date['date_debut_use'] = request.form.get('selected_date_Début')
            dico_date['date_fin_use'] = request.form.get('selected_date_Fin')

        elif request.form.get('ReinitialisationDate') == '':

            dico_date['date_debut_use'] = dico_date['date_minimum']
            dico_date['date_fin_use'] = dico_date['date_maximum']
    else:
        dico_date['date_minimum'], dico_date['date_maximum'] = get_date(data_foot)
        dico_date['date_debut_use'], dico_date['date_fin_use'] = dico_date['date_minimum'], dico_date['date_maximum']


    data_foot_usable = data_foot[(data_foot['Date'] >= dico_date['date_debut_use']) & (data_foot['Date'] <= dico_date['date_fin_use'])]
    teams, competitions, saisons = get_info(data_foot_usable)
    nb_goals = sum(data_foot_usable['NB BUT DOMICILE'])+sum(data_foot_usable['NB BUT EXTERIEUR'])

    return render_template('CompareYourTeamAccueilV3.html', date_minimum_debut=dico_date['date_minimum'],date_maximum_début=dico_date['date_fin_use'],date_minimum_fin=dico_date['date_debut_use'],date_maximum_fin=dico_date['date_maximum'],dateDebutUse=dico_date['date_debut_use'],dateFinUse=dico_date['date_fin_use'], nb_matches = data_foot_usable.shape[0],nb_goals=nb_goals,nb_teams=len(teams), nb_competitions=len(competitions),nb_saisons = len(saisons))

@app.route('/Unique', methods=['GET', 'POST'])
def accueil_selection_unique():
    print(request.form)
    if request.method == 'POST':
        if request.form.get('form_name') == 'FormulaireDate':

            dico_date['date_debut_use'] = request.form.get('selected_date_Début')
            dico_date['date_fin_use'] = request.form.get('selected_date_Fin')
            data_foot_usable = data_foot[(data_foot['Date'] >= dico_date['date_debut_use']) & (data_foot['Date'] <= dico_date['date_fin_use'])]
        elif request.form.get('ReinitialisationDate') == '':

            dico_date['date_debut_use'] = dico_date['date_minimum']
            dico_date['date_fin_use'] = dico_date['date_maximum']
            data_foot_usable = data_foot[(data_foot['Date'] >= dico_date['date_debut_use']) & (data_foot['Date'] <= dico_date['date_fin_use'])]

    else:
        dico_team['team_selected'] = ""
        dico_competition['competition_selected'] = ""
        dico_date['date_minimum'], dico_date['date_maximum'] = get_date(data_foot)
        dico_date['date_debut_use'], dico_date['date_fin_use'] = dico_date['date_minimum'], dico_date['date_maximum']
        data_foot_usable = data_foot[(data_foot['Date'] >= dico_date['date_debut_use']) & (data_foot['Date'] <= dico_date['date_fin_use'])]

    teams, competitions, saisons = get_info(data_foot)
    if data_foot_usable.shape[0] > 0:
        grouped_resultat = data_foot_usable.groupby('Résultat')
        result_counts = grouped_resultat['Résultat'].value_counts()
        result_home=result_counts.get('H', 0)
        result_nul = result_counts.get('D', 0)
        result_away=result_counts.get('A', 0)
        percent_home = round((result_home/data_foot_usable.shape[0])*100,1)
        percent_nul = round((result_nul/data_foot_usable.shape[0])*100,1)
        percent_away = round((result_away/data_foot_usable.shape[0])*100,1)
        type_sortie = ""
        goal_home_team = sum(data_foot_usable['NB BUT DOMICILE'])
        goal_away_team = sum(data_foot_usable['NB BUT EXTERIEUR'])
        goal_total = goal_home_team + goal_away_team
        percent_goal_home_team = round((goal_home_team/goal_total)*100,1)
        percent_goal_away_team = round((goal_away_team/goal_total)*100,1)

        team_win_max, team_nul_max, team_lose_max, max_win, max_nul, max_lose,team_buts_marqués_max,team_buts_encaissés_max,buts_marqués_max,buts_encaissés_max = get_max_info(data_foot_usable)

    else :
        type_sortie = "Aucune Données"
        result_home, result_nul, result_away, percent_home, percent_nul, percent_away,team_win_max, team_nul_max, team_lose_max, max_win, max_nul, max_lose,team_buts_marqués_max,team_buts_encaissés_max,buts_marqués_max,buts_encaissés_max = 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0

    return render_template('CompareYourTeam_Accueil_Individual_Selection.html',date_minimum_debut=dico_date['date_minimum'],date_maximum_début=dico_date['date_fin_use'],date_minimum_fin=dico_date['date_debut_use'],date_maximum_fin=dico_date['date_maximum'],dateDebutUse=dico_date['date_debut_use'],dateFinUse=dico_date['date_fin_use'], teams_Liste=teams, competitions_Liste=competitions ,type_sortie=type_sortie, WinHomePercent=percent_home,nbWinHome=result_home,NulPercent=percent_nul,nbNul=result_nul,WinAwayPercent=percent_away,nbWinAway=result_away, goal_home_team=goal_home_team,goal_away_team=goal_away_team,percent_goal_home_team=percent_goal_home_team,percent_goal_away_team=percent_goal_away_team,team_win_max=team_win_max, team_lose_max=team_lose_max,team_nul_max=team_nul_max, max_win=max_win, max_nul=max_nul,max_lose=max_lose,team_buts_marqués_max=team_buts_marqués_max,team_buts_encaissés_max=team_buts_encaissés_max,buts_marqués_max=buts_marqués_max,buts_encaissés_max=buts_encaissés_max)

@app.route('/Unique/Team', methods=['GET', 'POST'])
def team_selection_unique():
    print(request.form)
    if request.method == 'POST':
        if request.form.get('form_name') == 'FormulaireDate':

            dico_date['date_debut_use'] = request.form.get('selected_date_Début')
            dico_date['date_fin_use'] = request.form.get('selected_date_Fin')
            data_foot_usable = data_foot[((data_foot['HomeTeam'] == dico_team['team_selected']) | (data_foot['AwayTeam'] == dico_team['team_selected'])) & (data_foot['Compétition'].isin(dico_team['team_competitions_checked'])) & (data_foot['Date'] >= dico_date['date_debut_use']) & (data_foot['Date'] <= dico_date['date_fin_use'])]
        elif request.form.get('ReinitialisationDate') == '':

            dico_date['date_debut_use'] = dico_date['date_minimum']
            dico_date['date_fin_use'] = dico_date['date_maximum']
            data_foot_usable = data_foot[((data_foot['HomeTeam'] == dico_team['team_selected']) | (data_foot['AwayTeam'] == dico_team['team_selected'])) & (data_foot['Compétition'].isin(dico_team['team_competitions_checked'])) & (data_foot['Date'] >= dico_date['date_debut_use']) & (data_foot['Date'] <= dico_date['date_fin_use'])]
        elif request.form.get('form_name') == 'SelectionTeam':
            if dico_team['team_selected'] != request.form.get('TeamList'):
                # Mise en place du dataframe
                dico_team['team_selected'] = request.form.get('TeamList')
                data_foot_usable = data_foot[(data_foot['HomeTeam'] == dico_team['team_selected']) | (data_foot['AwayTeam'] == dico_team['team_selected'])]
                # Récupération des compétitions de l'équipe
                dico_competition['competition_selected'] = ""
                dico_team['team_competitions'] = sorted(data_foot_usable['Compétition'].unique())
                dico_team['team_competitions_checked'] = dico_team['team_competitions']
                # Récupération des dates
                dico_date['date_minimum'], dico_date['date_maximum'] = get_date(data_foot_usable)
                dico_date['date_debut_use'], dico_date['date_fin_use'] = dico_date['date_minimum'], dico_date['date_maximum']
            else :
                dico_team['team_competitions_checked'] = request.form.getlist('CompetitionCheck')
                data_foot_usable = data_foot[((data_foot['HomeTeam'] == dico_team['team_selected']) | (data_foot['AwayTeam'] == dico_team['team_selected'])) & (data_foot['Compétition'].isin(dico_team['team_competitions_checked'])) & (data_foot['Date'] >= dico_date['date_debut_use']) & (data_foot['Date'] <= dico_date['date_fin_use'])]

    else:
        dico_team['team_selected'] = ""
        dico_competition['competition_selected'] = ""
        dico_date['date_minimum'], dico_date['date_maximum'] = get_date(data_foot)
        dico_date['date_debut_use'], dico_date['date_fin_use'] = dico_date['date_minimum'], dico_date['date_maximum']
        data_foot_usable = data_foot[(data_foot['Date'] >= dico_date['date_debut_use']) & (data_foot['Date'] <= dico_date['date_fin_use'])]
        teams, competitions, saisons = get_info(data_foot)
        return render_template('CompareYourTeam_Accueil_Individual_Selection.html',date_minimum_debut=dico_date['date_minimum'],date_maximum_début=dico_date['date_fin_use'],date_minimum_fin=dico_date['date_debut_use'], date_maximum_fin=dico_date['date_maximum'],dateDebutUse=dico_date['date_debut_use'], dateFinUse=dico_date['date_fin_use'],teams_Liste=teams, competitions_Liste=competitions)

    teams, competitions, saisons = get_info(data_foot)

    if data_foot_usable.shape[0] > 0:
        #Obtenir les résultats
        data_foot_usable['Team_Result'] = data_foot_usable.apply(get_team_result, axis=1, equipe_choisie=dico_team['team_selected'])
        grouped_resultat = data_foot_usable.groupby('Team_Result')
        result_counts = grouped_resultat['Team_Result'].value_counts()
        result_win = result_counts.get('WH', 0)+result_counts.get('WA', 0)
        result_nul = result_counts.get('DH', 0)+result_counts.get('DA', 0)
        result_lose = result_counts.get('LH', 0)+result_counts.get('LA', 0)
        percent_win = round((result_win / data_foot_usable.shape[0]) * 100, 1)
        percent_nul = round((result_nul / data_foot_usable.shape[0]) * 100, 1)
        percent_lose = round((result_lose / data_foot_usable.shape[0]) * 100, 1)
        nb_match_home = sum([result_counts.get('WH', 0),result_counts.get('DH', 0),result_counts.get('LH', 0)])
        nb_match_away = sum([result_counts.get('WA', 0), result_counts.get('DA', 0), result_counts.get('LA', 0)])
        percent_win_home =  round((result_counts.get('WH', 0) / nb_match_home) * 100, 1)
        percent_win_away = round((result_counts.get('WA', 0) / nb_match_away) * 100, 1)
        percent_nul_home = round((result_counts.get('DH', 0) / nb_match_home) * 100, 1)
        percent_nul_away = round((result_counts.get('DA', 0) / nb_match_away) * 100, 1)
        percent_lose_home = round((result_counts.get('LH', 0) / nb_match_home) * 100, 1)
        percent_lose_away = round((result_counts.get('LA', 0) / nb_match_away) * 100, 1)
        type_sortie = ""
        # Obtenir les buts
        data_foot_usable['Team_Goal_Scored'] = data_foot_usable.apply(get_team_goal_scored, axis=1,equipe_choisie=dico_team['team_selected'])
        data_foot_usable['Team_Goal_Conceded'] = data_foot_usable.apply(get_team_goal_conceded, axis=1,equipe_choisie=dico_team['team_selected'])
        goal_team_scored = sum(data_foot_usable['Team_Goal_Scored'])
        goal_team_conceded = sum(data_foot_usable['Team_Goal_Conceded'])
        goal_total = goal_team_scored + goal_team_conceded
        percent_goal_team_scored = round((goal_team_scored / goal_total) * 100, 1)
        percent_goal_team_conceded = round((goal_team_conceded / goal_total) * 100, 1)
        #
        team_win_max, team_nul_max, team_lose_max, max_win, max_nul, max_lose= get_max_info_for_team(data_foot_usable, dico_team['team_selected'])
    else:
        data_foot_usable['Team_Result'] = data_foot_usable.apply(get_team_result, axis=1,equipe_choisie=dico_team['team_selected'])
        grouped_resultat = data_foot_usable.groupby('Team_Result')
        result_counts = grouped_resultat['Team_Result'].value_counts()
        goal_team_scored,goal_team_conceded,percent_goal_team_scored,percent_goal_team_conceded,result_win,result_nul,result_lose,percent_win,percent_nul,percent_lose,percent_win_home,percent_win_away,percent_nul_home,percent_nul_away,percent_lose_home,percent_lose_away,team_win_max, team_lose_max,team_nul_max, max_win, max_nul,max_lose=0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
        type_sortie="Aucune Données"

    return render_template('CompareYourTeam_Team_Selected.html',date_minimum_debut=dico_date['date_minimum'],date_maximum_début=dico_date['date_fin_use'],date_minimum_fin=dico_date['date_debut_use'],date_maximum_fin=dico_date['date_maximum'],dateDebutUse=dico_date['date_debut_use'],dateFinUse=dico_date['date_fin_use'], teams_Liste=teams, competitions_Liste=competitions, selected_team=dico_team['team_selected'], divisionCases = dico_team['team_competitions'], divisionCasesValid = dico_team['team_competitions_checked'],  type_sortie=type_sortie, databases=data_foot_usable.sort_values(by='Date', ascending=False).head(20),  WinPercent=percent_win,nbWin=result_win,NulPercent=percent_nul,nbNul=result_nul,LosePercent=percent_lose,nbLose=result_lose, nbWinAway=result_counts.get('WA', 0) ,nbWinHome=result_counts.get('WH', 0),nbNulAway=result_counts.get('DA', 0) ,nbNulHome=result_counts.get('DH', 0),nbLoseAway=result_counts.get('LA', 0) ,nbLoseHome=result_counts.get('LH', 0), percent_win_home=percent_win_home,percent_win_away=percent_win_away, percent_nul_home=percent_nul_home,percent_nul_away=percent_nul_away, percent_lose_home=percent_lose_home,percent_lose_away=percent_lose_away, goal_team_scored=goal_team_scored,goal_team_conceded=goal_team_conceded,percent_goal_team_scored=percent_goal_team_scored,percent_goal_team_conceded=percent_goal_team_conceded, team_win_max=team_win_max, team_lose_max=team_lose_max,team_nul_max=team_nul_max, max_win=max_win, max_nul=max_nul,max_lose=max_lose)

@app.route('/Unique/Competition', methods=['GET', 'POST'])
def competition_selection_unique():
    print(request.form)
    if request.method == 'POST':
        if request.form.get('form_name') == 'FormulaireDate':

            dico_date['date_debut_use'] = request.form.get('selected_date_Début')
            dico_date['date_fin_use'] = request.form.get('selected_date_Fin')
            data_foot_usable = data_foot[(data_foot['Compétition'] == dico_competition['competition_selected']) & ((data_foot['HomeTeam'].isin(dico_competition['competition_teams_checked'])) & (data_foot['AwayTeam'].isin(dico_competition['competition_teams_checked']))) & (data_foot['Date'] >= dico_date['date_debut_use']) & (data_foot['Date'] <= dico_date['date_fin_use'])]
        elif request.form.get('ReinitialisationDate') == '':

            dico_date['date_debut_use'] = dico_date['date_minimum']
            dico_date['date_fin_use'] = dico_date['date_maximum']
            data_foot_usable = data_foot[(data_foot['Compétition'] == dico_competition['competition_selected']) & ((data_foot['HomeTeam'].isin(dico_competition['competition_teams_checked'])) & (data_foot['AwayTeam'].isin(dico_competition['competition_teams_checked']))) & (data_foot['Date'] >= dico_date['date_debut_use']) & (data_foot['Date'] <= dico_date['date_fin_use'])]

        elif request.form.get('form_name') == 'SelectionDiv':
            if dico_competition['competition_selected'] != request.form.get('CompetitionList'):
                # Mise en place du dataframe
                dico_competition['competition_selected'] = request.form.get('CompetitionList')
                data_foot_usable = data_foot[(data_foot['Compétition'] == dico_competition['competition_selected'])]
                # Récupération des compétitions de l'équipe
                dico_team['team_selected'] = ""
                dico_competition['competition_teams'] = sorted(data_foot_usable['HomeTeam'].unique())
                dico_competition['competition_teams_checked'] = dico_competition['competition_teams']
                # Récupération des dates
                dico_date['date_minimum'], dico_date['date_maximum'] = get_date(data_foot_usable)
                dico_date['date_debut_use'], dico_date['date_fin_use'] = dico_date['date_minimum'], dico_date['date_maximum']
            else :
                dico_competition['competition_teams_checked'] = request.form.getlist('TeamCheck')
                data_foot_usable = data_foot[(data_foot['Compétition'] == dico_competition['competition_selected']) & ((data_foot['HomeTeam'].isin(dico_competition['competition_teams_checked'])) & (data_foot['AwayTeam'].isin(dico_competition['competition_teams_checked']))) & (data_foot['Date'] >= dico_date['date_debut_use']) & (data_foot['Date'] <= dico_date['date_fin_use'])]
    else:
        dico_team['team_selected'] = ""
        dico_competition['competition_selected'] = ""
        dico_date['date_minimum'], dico_date['date_maximum'] = get_date(data_foot)
        dico_date['date_debut_use'], dico_date['date_fin_use'] = dico_date['date_minimum'], dico_date['date_maximum']
        data_foot_usable = data_foot[(data_foot['Date'] >= dico_date['date_debut_use']) & (data_foot['Date'] <= dico_date['date_fin_use'])]
        teams, competitions, saisons = get_info(data_foot)
        return render_template('CompareYourTeam_Accueil_Individual_Selection.html', date_minimum_debut=dico_date['date_minimum'],date_maximum_début=dico_date['date_fin_use'],date_minimum_fin=dico_date['date_debut_use'], date_maximum_fin=dico_date['date_maximum'],dateDebutUse=dico_date['date_debut_use'], dateFinUse=dico_date['date_fin_use'],teams_Liste=teams, competitions_Liste=competitions)

    teams, competitions, saisons = get_info(data_foot)
    if data_foot_usable.shape[0] > 0:
        grouped_resultat = data_foot_usable.groupby('Résultat')
        result_counts = grouped_resultat['Résultat'].value_counts()
        result_home = result_counts.get('H', 0)
        result_nul = result_counts.get('D', 0)
        result_away = result_counts.get('A', 0)
        percent_home = round((result_home / data_foot_usable.shape[0]) * 100, 1)
        percent_nul = round((result_nul / data_foot_usable.shape[0]) * 100, 1)
        percent_away = round((result_away / data_foot_usable.shape[0]) * 100, 1)
        type_sortie = ""
        goal_home_team = sum(data_foot_usable['NB BUT DOMICILE'])
        goal_away_team = sum(data_foot_usable['NB BUT EXTERIEUR'])
        goal_total = goal_home_team + goal_away_team
        percent_goal_home_team = round((goal_home_team / goal_total) * 100, 1)
        percent_goal_away_team = round((goal_away_team / goal_total) * 100, 1)

        team_win_max, team_nul_max, team_lose_max, max_win, max_nul, max_lose,team_buts_marqués_max,team_buts_encaissés_max,buts_marqués_max,buts_encaissés_max = get_max_info(data_foot_usable)
    else :
        type_sortie = "Aucune Données"
        result_home,result_nul,result_away,percent_home,percent_nul,percent_away,goal_home_team,goal_away_team,percent_goal_home_team,percent_goal_away_team,team_win_max, team_nul_max, team_lose_max, max_win, max_nul, max_lose,team_buts_marqués_max,team_buts_encaissés_max,buts_marqués_max,buts_encaissés_max=0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0

    return render_template('CompareYourTeam_Competition_Selected.html',date_minimum_debut=dico_date['date_minimum'],date_maximum_début=dico_date['date_fin_use'],date_minimum_fin=dico_date['date_debut_use'],date_maximum_fin=dico_date['date_maximum'],dateDebutUse=dico_date['date_debut_use'],dateFinUse=dico_date['date_fin_use'], teams_Liste=teams, competitions_Liste=competitions, teamsCases= dico_competition['competition_teams'],teamsCasesValid=dico_competition['competition_teams_checked'], selected_division=dico_competition['competition_selected'], type_sortie=type_sortie ,databases=data_foot_usable.sort_values(by='Date', ascending=False).head(20),WinHomePercent=percent_home,nbWinHome=result_home,NulPercent=percent_nul,nbNul=result_nul,WinAwayPercent=percent_away,nbWinAway=result_away, goal_home_team=goal_home_team,goal_away_team=goal_away_team,percent_goal_home_team=percent_goal_home_team,percent_goal_away_team=percent_goal_away_team ,team_win_max=team_win_max, team_lose_max=team_lose_max,team_nul_max=team_nul_max, max_win=max_win, max_nul=max_nul,max_lose=max_lose,team_buts_marqués_max=team_buts_marqués_max,team_buts_encaissés_max=team_buts_encaissés_max,buts_marqués_max=buts_marqués_max,buts_encaissés_max=buts_encaissés_max)


@app.route('/Multiple', methods=['GET', 'POST'])
def accueil_selection_multiple():


    return render_template('CompareYourTeam_Accueil_Multiple_Selection.html')

if __name__ == '__main__':
    app.run(debug=True)
