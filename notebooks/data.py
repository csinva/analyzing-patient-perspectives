import pandas as pd
import os
import os.path
from os.path import join
import numpy as np
import imodelsx
from tqdm import tqdm
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import traceback

DATA_DIR_INITIAL = '../data/raw/'
DATA_DIR = join(DATA_DIR_INITIAL, '2nd Pass Analysis')


def load_files_dict_single_site():
    files_dict = {}
    files_succ = []
    files_fail = []
    annotators = [x for x in os.listdir(DATA_DIR) if not '.' in x]
    for annotator in annotators:
        # print(annotator)
        annotator_dir = join(DATA_DIR, annotator)
        interviews = [x for x in os.listdir(
            annotator_dir) if x.endswith('.xlsx') and not 'INCOMPLETE' in x]
        # files_dict[annotator] = interviews
        for interview in interviews:
            fname = join(annotator_dir, interview)
            df = pd.read_excel(fname)
            key = interview.replace('Interview Analysis.xlsx', '').strip()
            files_dict[key] = df
            COLS = ['Item #', 'Slide #', 'Domain', 'Subcategory']
            for i in range(4):
                assert df.columns[i] == COLS[i]
            assert df.shape[0] == 46
            # print(df.shape)
            assert df.columns[0] == 'Item #'
            assert df.columns[1] == 'Slide #'
            # display(df.head())
            # print(df.columns)
            try:
                assert 'theme' in pd.Series(df.columns).apply(str.lower).values
                theme_index = np.where(
                    np.array(list(map(str.lower, df.columns.values))) == 'theme')[0][0]
                for i in range(theme_index + 1, len(df.columns), 2):
                    assert '#' in df.columns[
                        i], f'should be a theme number but is {df.columns[i]}'
                assert df.shape[0] == 46
                files_succ.append(key)
            # print error traceback
            except Exception as e:
                # print(traceback.format_exc())
                files_fail.append(key)
    print('success:', len(files_succ))
    print('fail:', files_fail)
    return files_dict


def get_data_for_question_single_site(question_num: int, qs, responses_df, themes_df):
    question = qs.iloc[question_num].strip()
    responses = responses_df.iloc[question_num]
    theme_row = themes_df.iloc[question_num].values

    # responses clean
    for i in range(len(responses)):
        resp = responses[i]
        if pd.isna(resp):
            responses.values[i] = np.nan
        # one of select strings
        elif resp.lower().strip(' .()') in ['not asked', 'see above', 'answer not recorded', 'did not ask', 'n/a', 'above']:
            responses.values[i] = np.nan
        # check if resp is just whitespace or punctuation
        elif not resp.strip(' .,'):
            responses.values[i] = np.nan

        # valid string
        else:
            responses.values[i] = resp.strip(' .(),')

            # set value

    # theme dict
    theme_dict = {}
    for i in range(0, len(theme_row), 2):
        k = theme_row[i]
        v = theme_row[i + 1]

        # remove nan/whitespace from theme_dict
        if isinstance(k, str) and k.strip():
            k = k.strip()

            # v is often an int
            if isinstance(v, str):
                v = v.strip()

            # v is not empty
            if str(v).strip():
                theme_dict[k] = v

    assert not 'NA' in theme_dict.keys(), 'should have implicitly removed themes named "NA"'
    return question, responses, theme_dict
