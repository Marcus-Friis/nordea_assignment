# Author: Marcus Friis
# Nordea PYTHON DEVELOPER ASSIGNMENT
# Class for wrangling and extracting data from "events.csv"
# Maybe split into one class per table, a superclass to inherit from and maybe a collection class

import pandas as pd
import numpy as np


class EventWrangler:
    """
    Class for extracting information from the "events.csv" dataset.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self._match_df = None
        self._team_df = None
        self._player_df = None
        self._stat_df = None

    def get_matches(self) -> pd.DataFrame:
        """
        Wrangles event data to get information about matches, the teams participating and the goals scored.
        Contains:
        | match_id | match_name | home_team_id | away_team_id | home_goals | away_goals |
        """
        if self._match_df is not None:
            return self._match_df

        self._match_df = self.df[['match_id', 'match_name']].drop_duplicates()

        # supporting data needed for extracting team- and goal information
        teams = self.df[['match_id', 'is_home', 'team_id']].drop_duplicates()
        goals = self.df.groupby(['match_id', 'is_home']).sum()['goals_scored']

        # dict for masking and labeling home and away teams and goals
        home_status = {'home': True, 'away': False}

        # for home and away team, create new columns with team_ids & goals
        for home_away, is_home in home_status.items():
            # mask team data and add team_id to _match_df as home/away_team_id
            mask = teams['is_home'] == is_home
            self._match_df = self._match_df.merge(teams.loc[mask, ['team_id', 'match_id']], on=['match_id'], how='left') \
                .rename(columns={'team_id': f'{home_away}_team_id'})

            # mask goal data and add goals to _match_df as home/away_goals
            mask = goals.index.get_level_values('is_home') == is_home
            self._match_df = self._match_df.merge(goals[mask], on='match_id', how='left') \
                .rename(columns={'goals_scored': f'{home_away}_goals'})

        # select relevant columns
        self._match_df = self._match_df[['match_id', 'match_name', 'home_team_id', 'away_team_id', 'home_goals', 'away_goals']]
        return self._match_df

    def get_players(self) -> pd.DataFrame:
        """
        Wrangles event data to get information about individual players
        Contains:
        | player_id | team_id | player_name |
        """
        if self._player_df is not None:
            return self._player_df

        # dropping duplicates gives strictly player ids and other info, provided no id has other info
        self._player_df = self.df[['player_id', 'team_id', 'player_name']].drop_duplicates()
        return self._player_df

    def get_teams(self):
        """
        Wrangles event data to get information about teams
        Contains:
        | team_id | team_name |
        """
        if self._team_df is not None:
            return self._team_df

        # dropping duplicates gives strictly teams ids and names, provided no id has multiple assigned names
        self._team_df = self.df[['team_id', 'team_name']].drop_duplicates()
        return self._team_df

    def get_stats(self) -> pd.DataFrame:
        """
        Wrangles event data to get statistics regarding each players performance in matches
        Contains:
        | stat_id | player_id | match_id | goals_scored | minutes_played |
        | frac_minutes_played | frac_total_goals |
        """
        if self._stat_df is not None:
            return self._stat_df

        # get number of goals, minutes played, and fraction of minutes played per player for every match
        self._stat_df = self.df.groupby(['player_id', 'match_id']).sum()
        self._stat_df['frac_minutes_played'] = self._stat_df['minutes_played'] / 90

        # get total amount of goals per match and add it to _stat_df to use for calculating fraction of goals
        total_goals = self.df.groupby('match_id').sum()['goals_scored']
        total_goals.name = 'total_goals'  # rename to allow for merging
        self._stat_df = self._stat_df.join(total_goals, on='match_id', how='left')
        self._stat_df['frac_total_goals'] = self._stat_df['goals_scored'] / self._stat_df['total_goals']

        # select desired columns, reset index to remove match_id and player_id from index (happens when using groupby)
        # and create new range of numbers to use as stat_id
        self._stat_df = self._stat_df[['goals_scored', 'minutes_played', 'frac_minutes_played', 'frac_total_goals']]
        self._stat_df = self._stat_df.reset_index()
        self._stat_df['stat_id'] = np.arange(self._stat_df.shape[0])  # create custom unique index for each stat

        #
        self._stat_df = self._stat_df[['stat_id', 'player_id', 'match_id', 'goals_scored', 'minutes_played',
                                       'frac_minutes_played', 'frac_total_goals']]

        return self._stat_df


if __name__ == '__main__':
    # test functions
    events_df = pd.read_csv('events.csv')
    ew = EventWrangler(events_df)
    match_df = ew.get_matches()
    stat_df = ew.get_stats()
    team_df = ew.get_teams()
    player_df = ew.get_players()
    print(player_df)
