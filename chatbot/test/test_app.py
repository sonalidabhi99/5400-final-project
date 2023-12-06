#import the libraries
#have to be in the test folder for this referecing to work 
from chatbot.functions.information_retrieval import *
if __name__ == "__main__":

    input1 = ['VA', 'MD', 'DC', 'NY'] #the state 
    input2 = ['i want to pay check', 'my landlord sucks', 'this place is mental'] # user issue
    msls = []
    final_texts = [] # save final texts in list
    titles = [] # save all titles returned in a list

    for text in input2: # iterate through input2 
        text = clean_text(text) # clean the text
        for state in input1: # iterate throguh input1
            msl = find_most_similar_law(state, text) # based on the text and location get most similar law
            msls.append(msl) # append to the list
            final_text, title = get_law(msl) # get final text and title 
            final_texts.append(final_text)  # append to the list
            titles.append(title)  # append to the list
    
    # at this point, you should have 3 lists with most similar law (should be an index), final clean texts,
    # and all the titles. 
    # we want to make sure that the text and title are strings and msl is an idex, and that it's a correct
    # index
    
    for i, msl in enumerate(msls):
        #if its a string, its "No Law Found"
        if type(msl) != str:
            assert type(msl) == int
            assert msl >= 0
            assert msl < 1000
            assert type(final_texts[i]) == str
            assert type(titles[i]) == str



