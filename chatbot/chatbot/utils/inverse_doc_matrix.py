import pandas as pd
import numpy as np
# hide warnings
import warnings
warnings.filterwarnings('ignore')
import logging
import argparse

#python inverse_doc_matrix.py -c ../../data/laws_dataframe.csv -o ../../data/inverse_doc_matrix.csv

def create_idm(csv_path, output_path):
    """
    This function takes in a csv_path, and returns an inverse document matrix
    params: csv_path - string; location of the data file
            output_path - string; location of where the matrix should be stored
    output: inverse_document_matrix - pandas dataframe
    """
    logging.basicConfig(level=logging.INFO)
    logging.info('Reading in the file')
    df = pd.read_csv(csv_path)
    # drop all rows with NaN values for Keywords
    df = df.dropna(subset=['keywords'])
    # drop all columns except for law_title, law_text, state, and keywords
    df = df[['law_id','law_title', 'law_text', 'location', 'keywords']]
    keywords_for_mult_select = []
    # create list of keywords
    for k in df['keywords']:
        if type(k) == float:
            continue
        k = k.split(',')
        k = [x.strip() for x in k]
        for l in k:
            l = l.strip()
            l = l.lower()
            keywords_for_mult_select.append(l)
    keywords_for_mult_select = list(set(keywords_for_mult_select))
    keywords_for_mult_select.sort()
    df = df[['law_id','location', 'law_title', 'law_text']]
    # add blank columns for each keyword
    for keyword in keywords_for_mult_select:
        df[keyword] = np.nan
    # fill in the blank columns with 1 if the keyword is in the law_text
    for index, row in df.iterrows():
        for keyword in keywords_for_mult_select:
            if keyword in row['law_text']:
                df.loc[index, keyword] = 1
            else:
                df.loc[index, keyword] = 0
    inverse_document_matrix = df
    logging.info('finished making inverse doc')
    # add a column for the index
    inverse_document_matrix['index'] = inverse_document_matrix.index
    # put the index column first
    cols = inverse_document_matrix.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    inverse_document_matrix = inverse_document_matrix[cols]
    #output the file: 
    logging.info(f'saving to {output_path}')
    inverse_document_matrix.to_csv(output_path, index = False)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Creates an inverse document matrix based on a csv file')
    parser.add_argument('-c', '--csv_path', required=True, help='input dataframe; must be comma separated')
    parser.add_argument('-o', '--output_path', required=True, help='output location')
    args = parser.parse_args()
    create_idm(args.csv_path, args.output_path)