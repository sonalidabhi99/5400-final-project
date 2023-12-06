from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import re
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')


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
def find_most_similar_law(location, user_text):
    """
    Finds the most similar law to the user's text
    args: cleaned_user_text: the user's text that has been cleaned
          inverse_document_matrix: the inverse document matrix
    returns: the most similar law (law_title)
    """
    #clean the user's text
    cleaned_user_text = clean_text(user_text)
    inverse_document_matrix = pd.read_csv('./data/inverse_doc_matrix.csv')
    #filter the inverse document matrix by the location
    filtered_idm = inverse_document_matrix[inverse_document_matrix['location'] == location]
    user_df = pd.DataFrame(columns=filtered_idm.columns)
    new_row = pd.Series(index=filtered_idm.columns) # adding new blank row (so user_df isn't blank)
    user_df = pd.concat([user_df, pd.DataFrame([new_row])], ignore_index=True) # officially adding it
    user_df[filtered_idm.columns[5:]] = 0 # setting all keywords to zero as default
    user_df['law_text'] = cleaned_user_text # setting the user text as the "law"
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
    for l in filtered_idm['law_id']:
        dictionary_of_arrays[l] = filtered_idm[filtered_idm['law_id'] == l].iloc[:, 5:].values
    

    user_array = user_df.iloc[:, 5:].values
    dictionary_for_finding_similar_law = {}


    for law in dictionary_of_arrays:
        dictionary_for_finding_similar_law[law] = cosine_similarity(dictionary_of_arrays[law], user_array)[0][0]

    if len(dictionary_for_finding_similar_law) != 0:
        most_similar_law = max(dictionary_for_finding_similar_law, key=dictionary_for_finding_similar_law.get)
    else:
        most_similar_law = "No Law Found"

    return most_similar_law

def get_law(most_similar_law):
    """
    Looks in the laws dataframe and retrieves the law based on the law_id
    params: most similar law 
    returns: the text
    """
    df = pd.read_csv('./data/laws_dataframe.csv')
    #find the text and title
    try:
        text = df[df['law_id'] == most_similar_law]['law_text'].values[0]
        title = df[df['law_id'] == most_similar_law]['law_title'].values[0]
    except:
        text = "IN GET LAW PART: no law found"
        title = "IN GET LAW PART: no law found"
    return text, title


