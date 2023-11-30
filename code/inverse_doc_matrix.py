import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import re
from sklearn.metrics.pairwise import cosine_similarity
# hide warnings
import warnings
warnings.filterwarnings('ignore')

# READ IN THE DATA
def create_idm(csv_path):
    df = pd.read_csv(csv_path)
    # drop all rows with NaN values for Keywords
    df = df.dropna(subset=['Keywords'])
    # drop all columns except for law_title, law_text, state, and keywords
    df = df[['law_title', 'law_text', 'location', 'Keywords']]
    keywords_for_mult_select = []
    # create list of keywords
    for k in df['Keywords']:
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
    df = df[['location', 'law_title', 'law_text']]
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

    # add a column for the index
    inverse_document_matrix['index'] = inverse_document_matrix.index

    # put the index column first
    cols = inverse_document_matrix.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    inverse_document_matrix = inverse_document_matrix[cols]
    return inverse_document_matrix


#function to make the string like the keywords: 
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

#function to search and rank the keywords and return a matrix
def find_most_similar_law(location, user_text, inverse_document_matrix):
    """
    Finds the most similar law to the user's text
    args: cleaned_user_text: the user's text that has been cleaned
          inverse_document_matrix: the inverse document matrix
    returns: the most similar law (law_title)
    """
    #clean the user's text
    cleaned_user_text = clean_text(user_text)
    #filter the inverse document matrix by the location
    filtered_idm = inverse_document_matrix[inverse_document_matrix['location'] == location]
    user_df = pd.DataFrame(columns=filtered_idm.columns)
    new_row = pd.Series(index=filtered_idm.columns)
    user_df = user_df.append(new_row, ignore_index=True)
    user_df[filtered_idm.columns[4:]] = 0
    user_df['law_text'] = cleaned_user_text
    user_df['law_title'] = 'user_text'
    user_df['location'] = location

    # fill in the blank columns with 1 if the keyword is in the law_text
    for index, row in user_df.iterrows():
        for keyword in filtered_idm.columns[4:]:
            if keyword in row['law_text']:
                user_df[keyword] = 1
            else:
                user_df[keyword] = 0
    

    dictionary_of_arrays = {}
    for l in filtered_idm['law_title']:
        dictionary_of_arrays[l] = filtered_idm[filtered_idm['law_title'] == l].iloc[:, 4:].values

    user_array = user_df.iloc[:, 4:].values

    dictionary_for_finding_similar_law = {}
    for law in dictionary_of_arrays:
        dictionary_for_finding_similar_law[law] = cosine_similarity(dictionary_of_arrays[law], user_array)[0][0]
    
    most_similar_law = max(dictionary_for_finding_similar_law, key=dictionary_for_finding_similar_law.get)

    return most_similar_law
    

create_idm("./data/clean_data.csv")
print(clean_text("'my money is in the bank and i can't get it out'"))
print(find_most_similar_law('VA', "'my money is in the bank and i can't get it out'", create_idm("./data/clean_data.csv")))

# I am having trouble with mold and no air conditioning and no heat. I hate my landlord!!!
# my money is in the bank and i cant get it out
# I am having trouble with mold and no air conditioning and no heat. I hate my landlord!!!