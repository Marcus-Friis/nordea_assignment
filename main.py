# Author: Marcus Friis
# Nordea PYTHON DEVELOPER ASSIGNMENT

import pandas as pd
import os
from eventWrangler import EventWrangler

if __name__ == '__main__':
    # load dataset and initialise data wrangler
    events_df = pd.read_csv('events.csv')
    ew = EventWrangler(events_df)

    # create tables from EventWrangler
    output_dict = {'matches': ew.get_matches(),
                   'teams': ew.get_teams(),
                   'players': ew.get_players(),
                   'stats': ew.get_stats()}

    # create directory for output files
    dir_name = 'output'
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)

    # loop through datasets and output each table as .jsonl file
    for key, val in output_dict.items():
        val.to_json(f'{dir_name}/{key}.jsonl', orient='records', lines=True)
