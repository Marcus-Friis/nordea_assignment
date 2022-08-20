import pandas as pd
import numpy as np


class EventWrangler:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self._match_df = None
        self._team_df = None
        self._player_df = None
        self._stat_df = None

    def get_matches(self) -> pd.DataFrame:
        if self._match_df is not None:
            return self._match_df

        self._match_df = self.df[['match_id', 'match_name']].drop_duplicates()

        # supporting data needed for merging tables
        teams = self.df[['match_id', 'is_home', 'team_id']].drop_duplicates()
        goals = self.df.groupby(['match_id', 'is_home']).sum()['goals_scored']

        # filter to home / away and create new column with team_id & goals
        for home_away, is_home in zip(['home', 'away'], [True, False]):
            mask = teams['is_home'] == is_home
            self._match_df = self._match_df.merge(teams.loc[mask, ['team_id', 'match_id']], on=['match_id'], how='left') \
                .rename(columns={'team_id': f'{home_away}_team_id'})

            mask = goals.index.get_level_values('is_home') == is_home
            self._match_df = self._match_df.merge(goals[mask], on='match_id', how='left') \
                .rename(columns={'goals_scored': f'{home_away}_goals'})

        self._match_df = self._match_df[['match_id', 'match_name', 'home_team_id', 'away_team_id', 'home_goals', 'away_goals']]
        return self._match_df

    def get_players(self) -> pd.DataFrame:
        if self._player_df is not None:
            return self._player_df

        self._player_df = self.df[['player_id', 'team_id', 'player_name']].drop_duplicates()
        return self._player_df

    def get_teams(self):
        if self._team_df is not None:
            return self._team_df

        self._team_df = self.df[['team_id', 'team_name']].drop_duplicates()
        return self._team_df

    def get_stats(self) -> pd.DataFrame:
        if self._stat_df is not None:
            return self._stat_df

        self._stat_df = self.df.groupby(['player_id', 'match_id']).sum()
        self._stat_df['frac_minutes_played'] = self._stat_df['minutes_played'] / 90

        total_goals = self.df.groupby('match_id').sum()['goals_scored']
        total_goals.name = 'total_goals'
        self._stat_df = self._stat_df.join(total_goals, on='match_id', how='left')
        self._stat_df['frac_total_goals'] = self._stat_df['goals_scored'] / self._stat_df['total_goals']

        self._stat_df = self._stat_df[['goals_scored', 'minutes_played', 'frac_minutes_played', 'frac_total_goals']]
        self._stat_df = self._stat_df.reset_index()
        self._stat_df['stat_id'] = np.arange(self._stat_df.shape[0])

        return self._stat_df


if __name__ == '__main__':
    dillerdaller = pd.read_csv('events.csv')
    ew = EventWrangler(dillerdaller)
    match_df = ew.get_matches()
    stat_df = ew.get_stats()
    team_df = ew.get_teams()
    player_df = ew.get_players()
