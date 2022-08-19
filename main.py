# Author: Marcus Friis
# Assignment for Nordea 2nd interview

import pandas as pd
import numpy as np
import os


def get_matches(df: pd.DataFrame) -> pd.DataFrame:
    match_df = df[['match_id', 'match_name']].drop_duplicates()

    # supporting data needed for merging tables
    teams = df[['match_id', 'is_home', 'team_id']].drop_duplicates()
    goals = df.groupby(['match_id', 'is_home']).sum()['goals_scored']

    # filter to home / away and create new column with team_id & goals
    for home_away, is_home in zip(['home', 'away'], [True, False]):
        mask = teams['is_home'] == is_home
        match_df = match_df.merge(teams.loc[mask, ['team_id', 'match_id']], on=['match_id'], how='left') \
            .rename(columns={'team_id': f'{home_away}_team_id'})

        mask = goals.index.get_level_values('is_home') == is_home
        match_df = match_df.merge(goals[mask], on='match_id', how='left') \
            .rename(columns={'goals_scored': f'{home_away}_goals'})

    match_df = match_df[['match_id', 'match_name', 'home_team_id', 'away_team_id', 'home_goals', 'away_goals']]
    return match_df


def get_players(df: pd.DataFrame) -> pd.DataFrame:
    player_df = df[['player_id', 'team_id', 'player_name']].drop_duplicates()
    return player_df


def get_teams(df: pd.DataFrame) -> pd.DataFrame:
    team_df = df[['team_id', 'team_name']].drop_duplicates()
    return team_df


def get_stats(df: pd.DataFrame) -> pd.DataFrame:
    stat_df = df.groupby(['player_id', 'match_id']).sum()
    stat_df['frac_minutes_played'] = stat_df['minutes_played'] / 90

    total_goals = df.groupby('match_id').sum()['goals_scored']
    total_goals.name = 'total_goals'
    stat_df = stat_df.join(total_goals, on='match_id', how='left')
    stat_df['frac_total_goals'] = stat_df['goals_scored'] / stat_df['total_goals']

    stat_df = stat_df[['goals_scored', 'minutes_played', 'frac_minutes_played', 'frac_total_goals']]
    stat_df = stat_df.reset_index()
    stat_df['stat_id'] = np.arange(stat_df.shape[0])

    return stat_df


if __name__ == '__main__':
    df = pd.read_csv('events.csv')

    dir_name = 'output'
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)

    funcs = {'teams': get_teams, 'matches': get_matches, 'stats': get_stats, 'players': get_players}
    for key, val in funcs.items():
        val(df).to_json(f'{dir_name}/{key}.jsonl', orient='records', lines=True)

    # match_df = get_matches(df)
    # player_df = get_players(df)
    # team_df = get_teams(df)
    # stats_df = get_stats(df)
    #
    # match_df.to_json('matches.jsonl', orient='records', lines=True)
    # player_df.to_json('players.jsonl', orient='records', lines=True)
    # team_df.to_json('teams.jsonl', orient='records', lines=True)
    # stats_df.to_json('stats.jsonl', orient='records', lines=True)
    # print(pd.read_json('matches.jsonl', lines=True))
