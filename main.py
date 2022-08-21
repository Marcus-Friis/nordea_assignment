# Author: Marcus Friis
# Nordea PYTHON DEVELOPER ASSIGNMENT

import pandas as pd
import os
from eventWrangler import EventWrangler

if __name__ == '__main__':
    events_df = pd.read_csv('events.csv')
    ew = EventWrangler(events_df)

    output_dict = {'matches': ew.get_matches(),
                   'teams': ew.get_teams(),
                   'players': ew.get_players(),
                   'stats': ew.get_stats()}

    dir_name = 'output'
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)

    for key, val in output_dict.items():
        val.to_json(f'{dir_name}/{key}.jsonl', orient='records', lines=True)
