import pandas as pd
import re 
import logging
import argparse

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Cleans the laws in from the dataframe')
    parser.add_argument('-o', '--outDir', required = True, help='output directory')
    args = parser.parse_args()
    logging.info('read in the files')
    df_va = pd.read_csv('virginia_laws.csv')
    df_va = df_va[:-1]
    df_dc = pd.read_csv('dc_laws.csv')
    df_md = pd.read_csv('maryland_laws.csv')
    logging.info('finished reading in the data; starting cleaning')
    combined_pattern = re.compile(r'[A-Z1-9]\.|\([a-z1-9]\)|\(i*\)|\(u[*]')
    section_pattern = re.compile('§')
    df_va['law_text'] = df_va['law_text'].apply(lambda x: combined_pattern.sub("", x))
    df_md['law_text'] = df_md['law_text'].apply(lambda x: combined_pattern.sub("", x))
    df_dc['law_text'] = df_dc['law_text'].apply(lambda x: combined_pattern.sub("", x))

    df_va['law_text'] = df_va['law_text'].apply(lambda x: section_pattern.sub("Section", x))
    df_md['law_text'] = df_md['law_text'].apply(lambda x: section_pattern.sub("Section", x))
    df_dc['law_text'] = df_dc['law_text'].apply(lambda x: section_pattern.sub("Section", x))

    df_va_subset = df_va[['law_title', 'law_text', 'location', 'Type', 'Keywords']]
    df_md_subset = df_md[['law_title', 'law_text', 'location', 'Type', 'Keywords']]
    df_dc_subset = df_dc[['law_title', 'law_text', 'location', 'Type', 'Keywords']]
    df_final = pd.concat([df_va_subset, df_md_subset, df_dc_subset])
    df_final['law_title'] = df_final['law_title'].apply(lambda x: section_pattern.sub("Section", x))
    logging.info(f'finished cleaning the data; writing file to {args.outDir}')
    df_final.to_csv(args.outDir, index = False)