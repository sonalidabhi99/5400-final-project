import pandas as pd 
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import numpy as np

import re
import logging
import argparse

# example call: 
# python tf_idf.py -f ../data/clean_data.csv -o ../data/laws_dataframe.csv -l law_text -k Keywords

def clean_text(text):
    """
    Cleans the text by removing punct, stop words, and lemmatizing the words in the law 
    args: text
    returns: cleaned text (text)
    """
    #constants 
    punct = """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~""" 
    stop_words = stopwords.words('english')
    lemmatizer = WordNetLemmatizer()

    text = text.lower()
    text = "".join([char for char in text if char not in punct])
    text = re.sub('\s+',' ',text) 
    #remove all numbers 
    text = re.sub("\d", ' ', text) 
    text = word_tokenize(text)
    text = [lemmatizer.lemmatize(word) for word in text if word not in stop_words]
    text = " ".join(text)
    return text



def get_keywords(vectorizer, feature_names, doc):
    """
    Returns the top 10 keywords based on the idf-tf
    modified code from here: https://www.kaggle.com/code/rowhitswami/keywords-extraction-using-tf-idf-method
    args: vectorizer: a TfidfVectorizer vectorizer object
         feature_names: vectorizer.get_feature_names_out() object based on the entire corpora
         doc: the specific doc to get the keywords for
    returns: a list of the keywords for that doc 
    """
    tf_idf_vector = vectorizer.transform([doc])
    #sort the matrix
    tf_idf_matrix = tf_idf_vector.tocoo()
    tfidf_sorted = sorted(zip(tf_idf_matrix.col, tf_idf_matrix.data), key=lambda x: (x[1], x[0]), reverse=True)
    #get the top 10 only
    tfidf_sorted = tfidf_sorted[:10]
    score_vals = []
    feature_vals = []
    for idx, score in tfidf_sorted:
        score_vals.append(round(score, 3))
        feature_vals.append(feature_names[idx])
    keywords= {}
    for idx in range(len(feature_vals)):
        keywords[feature_vals[idx]]=score_vals[idx]

    return list(keywords.keys())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Pull Data based on method specified')
    parser.add_argument('-f', '--file', required=True, help='file to read in')
    parser.add_argument('-o', '--outputDir', required=True, help='directory to save final dataframe to')
    parser.add_argument('-l', '--law_column', required=True, help='column of law text')
    parser.add_argument('-k', '--keyword_columns', required=True, help='column of existing keywords')
    args = parser.parse_args()
    logging.info('reading in the data')
    df = pd.read_csv(args.file)
    vectorizer = TfidfVectorizer(stop_words='english')
    df[args.keyword_columns] = df[args.keyword_columns].replace(np.nan, '', regex=True)
    df['law_text_keywords'] = df[args.law_column] + df[args.keyword_columns]
    logging.info('cleaning the data ')
    df['law_text_tfidf'] = df['law_text_keywords'].apply(clean_text)
    corpora = df['law_text_tfidf'].to_list()
    logging.info('getting keywords from the entire corpora')
    vectorizer.fit_transform(corpora)
    feature_names = vectorizer.get_feature_names_out() 
    result = []
    logging.info('getting keywords for each individual doc')
    for doc in corpora:
        df_temp = {}
        df_temp['full_text'] = doc
        df_temp['top_keywords'] = get_keywords(vectorizer, feature_names, doc)
        result.append(df_temp)
    result = pd.DataFrame(result)
    #only keep the columns i want: law_title, law_text, location, keywords 
    df = df[['law_title', 'law_text', 'location']]
    #adding to original data: 
    df['keywords'] = result['top_keywords']     
    logging.info(f'saving the results to {args.outputDir}')   
    df.to_csv(args.outputDir)
