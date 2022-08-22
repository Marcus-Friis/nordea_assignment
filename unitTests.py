# Author: Marcus Friis
# Nordea PYTHON DEVELOPER ASSIGNMENT
# script for unit testing all methods of EventWrangler

import unittest
from eventWrangler import EventWrangler
import numpy as np
import pandas as pd
import pandas.api.types as ptypes


# TODO: restructure file, split into 4 seperate files
# TODO: abstract base class with type dict and abstract methods test_columns and test_dtypes???
# class DtypeTests:
#     type_dict = {'int': ptypes.is_integer_dtype, 'str': ptypes.is_string_dtype, 'float': ptypes.is_float_dtype}


class TestGetMatches(unittest.TestCase):
    """
    Class for unit testing EventWrangler's get_matches() method.
    """

    # before each test, create new instance of EventWrangler to ensure clean testing
    @classmethod
    def setUpClass(cls) -> None:
        cls.events_df = pd.read_csv('events.csv')
        cls.ew = EventWrangler(cls.events_df)
        cls.df = cls.ew.get_matches()

    # ensures each column is named and ordered in accordance to the assignment description
    def test_columns(self) -> None:
        desired = np.array(['match_id', 'match_name', 'home_team_id', 'away_team_id', 'home_goals', 'away_goals'])
        actual = np.array(self.df.columns)
        is_equal = np.all(desired == actual)
        self.assertTrue(is_equal, 'column mismatch')

    # ensures each column is typed as specified by the assignment description
    def test_dtypes(self) -> None:
        dtypes = self.df.dtypes
        type_dict = {'int': ptypes.is_integer_dtype, 'str': ptypes.is_string_dtype, 'float': ptypes.is_float_dtype}
        col_types = {'match_id': 'int', 'match_name': 'str', 'home_team_id': 'int', 'away_team_id': 'int',
                     'home_goals': 'int', 'away_goals': 'int'}
        # apply appropriate type check to columns
        for key, val in col_types.items():
            self.assertTrue(type_dict[val](dtypes[key]), f'column {key} is not type {val}')

    # checks that all team_ids from events appear in the correct column in matches
    def test_team_ids_home_column(self) -> None:
        home_dict = {'home': True, 'away': False}

        for key, val in home_dict.items():
            mask = self.events_df['is_home'] == val
            ids = self.events_df.loc[mask, 'team_id']
            check = np.isin(ids, self.df[f'{key}_team_id']).all()
            self.assertTrue(check, f'team_id with {key}={val} in events does not exist in {key}_team_id')

    # tests that the sum of home_goals and away_goals == total_goals per match
    def test_goal_sum(self) -> None:
        goal_sum = self.df.set_index('match_id')
        goal_sum['sum'] = goal_sum['home_goals'] + goal_sum['away_goals']
        total_goals = self.events_df.groupby('match_id').sum()['goals_scored']
        merged = goal_sum[['sum']].merge(total_goals, on='match_id')
        check = (merged['sum'] == merged['goals_scored']).all()
        self.assertTrue(check, 'sum of home_goals and away_goals do not equal number of goals in match')


class TestGetPlayers(unittest.TestCase):
    """
    Class for unit testing EventWrangler's get_players() method.
    """

    # before each test, create new instance of EventWrangler to ensure clean testing
    @classmethod
    def setUpClass(cls) -> None:
        cls.events_df = pd.read_csv('events.csv')
        cls.ew = EventWrangler(cls.events_df)
        cls.df = cls.ew.get_players()

    # ensures each column is named and ordered in accordance to the assignment description
    def test_columns(self) -> None:
        desired = np.array(['player_id', 'team_id', 'player_name'])
        actual = np.array(self.df.columns)
        is_equal = np.all(desired == actual)
        self.assertTrue(is_equal, 'column mismatch')

    # ensures each column is typed as specified by the assignment description
    def test_dtypes(self) -> None:
        dtypes = self.df.dtypes
        self.assertTrue(ptypes.is_integer_dtype(dtypes['player_id']), 'player_id is not integer')
        self.assertTrue(ptypes.is_integer_dtype(dtypes['team_id']), 'team_id is not integer')
        self.assertTrue(ptypes.is_string_dtype(dtypes['player_name']), 'player_name is not string')

    # tests that player_id functions as a key to the table and that there are no duplicates
    # can return false positive if there is a duplicate in player table and a player_id in events that isn't in players
    def test_player_id_duplicates(self) -> None:
        n = self.df.shape[0]
        m = self.events_df['player_id'].drop_duplicates().shape[0]
        self.assertEqual(n, m, 'more player_ids than expected')


class TestGetTeams(unittest.TestCase):
    """
    Class for unit testing EventWrangler's get_teams() method.
    """

    # before each test, create new instance of EventWrangler to ensure clean testing
    @classmethod
    def setUpClass(cls) -> None:
        cls.events_df = pd.read_csv('events.csv')
        cls.ew = EventWrangler(cls.events_df)
        cls.df = cls.ew.get_teams()

    # ensures each column is named and ordered in accordance to the assignment description
    def test_columns(self) -> None:
        desired = np.array(['team_id', 'team_name'])
        actual = np.array(self.df.columns)
        is_equal = np.all(desired == actual)
        self.assertTrue(is_equal, 'column mismatch')

    # ensures each column is typed as specified by the assignment description
    def test_dtypes(self) -> None:
        dtypes = self.df.dtypes
        self.assertTrue(ptypes.is_integer_dtype(dtypes['team_id']), 'team_id is not integer')
        self.assertTrue(ptypes.is_string_dtype(dtypes['team_name']), 'player_name is not string')

    # tests that team_id is a key to the table and there are no duplicates
    # could return false positive if there is a duplicate in team table and a team_id in events that isn't in teams
    def test_team_id_duplicates(self) -> None:
        n = self.df.shape[0]
        m = self.events_df['team_id'].drop_duplicates().shape[0]
        self.assertEqual(n, m, 'one or more team_ids have multiple assigned names')


class TestGetStat(unittest.TestCase):
    """
    Class for unit testing EventWrangler's get_stats() method.
    """

    # before each test, create new instance of EventWrangler to ensure clean testing
    @classmethod
    def setUpClass(cls) -> None:
        cls.events_df = pd.read_csv('events.csv')
        cls.ew = EventWrangler(cls.events_df)
        cls.df = cls.ew.get_stats()

    # ensures each column is named and ordered in accordance to the assignment description
    def test_columns(self) -> None:
        desired = np.array(['stat_id', 'player_id', 'match_id', 'goals_scored', 'minutes_played', 'frac_minutes_played',
                            'frac_total_goals'])
        actual = np.array(self.df.columns)
        is_equal = np.all(desired == actual)
        self.assertTrue(is_equal, 'column mismatch')

    # ensures each column is typed as specified by the assignment description
    def test_dtypes(self) -> None:
        dtypes = self.df.dtypes
        type_dict = {'int': ptypes.is_integer_dtype, 'str': ptypes.is_string_dtype, 'float': ptypes.is_float_dtype}
        col_types = {'stat_id': 'int', 'player_id': 'int', 'match_id': 'int', 'goals_scored': 'int',
                     'minutes_played': 'int', 'frac_minutes_played': 'float', 'frac_total_goals': 'float'}
        # apply appropriate type check to columns
        for key, val in col_types.items():
            self.assertTrue(type_dict[val](dtypes[key]), f'column {key} is not type {val}')

    # tests that frac_minutes_played and frac_total_goals are in range 0 -> 1
    def test_between_01(self) -> None:
        cols = ['frac_minutes_played', 'frac_total_goals']
        for col in cols:
            check = (self.df[col] < 0) | (self.df[col] > 1)
            self.assertFalse(np.any(check), f'{col} is not 0 <= {col} <= 1')


if __name__ == '__main__':
    unittest.main()

