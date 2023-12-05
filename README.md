# 5400 Final Project

# LeTeRS: The Legal Tenants' Rights Summarizer Application
### Sonali Dabhi, Tereza Martinkova, Katherine Mead, Natalie Smith

#### Project Goals

Overall, the aim of this project is to empower renters in the D.C., Maryland, and Virginia areas with legal knowledge of their rights as tenants through an application that allows users to pose an apartment issue they are facing to a chatbot, which will then retrieve the law that best fits the issue and summarize it for the user in an easily understandable way such that it can be understood and referenced to push landlords, property managers, or property management companies to quickly resolve issues they are legally obligated to take care of. 

The driving concept of the application is retrieval augmented generation, or RAG, which is made up of two phases:

1.  Information Retrieval: In this phase, the package retrieves relevant information based on the user's prompt. For the purposes of the LeTeRS application, the user feeding a response to the chatbot prompts the application to filter the dataset of laws and then search for and retrieve the law in the dataset that best matches the user's prompt. For example, if the user tells the chatbot that they are living in Virginia and are experiencing issues with mold, the application will retrieve the law in Virginia that most closely deals with issues relating to mold. Once this law is retrieved, it is passed on to phase two of the RAG process.

2.  Content Generation: Augmented with the information retrieved in phase one, this phase of RAG generates content through a response to the user. In the case of LeTeRS, the content generation phase is the summarizer, wherein the retrieved law from phase one is passed to the LLM summarizer (Google Pegasus, for our purposes). The chatbot then responds to the user with the title and summary of the law that best fits the user's original prompt. 

#### How to use LeTeRS and its key features


**Data Gathering and Cleaning:**
The files that make up the data gathering and cleaning poriton of the application are listed below, and should be run in the order they are listed.

- selenium.ipynb: this file gathers and cleans the D.C., Maryland, and Virginia law csv data using the python package [Selenium.](https://selenium-python.readthedocs.io/) 
- law_cleaning.py: this file takes the cleaned data and subsets the laws by state, splitting up law text and law title. This file makes use of logging to confirm the data is finished cleaning.
- tf_idf.py: using TfidfVectorizer, this file creates keywords for each law through the use of TF-IDF across the collection of laws.

**Information Retrieval**
The files that make up the information retrieval poriton of the application are listed below.

- inverse_doc_matrix.py: this file creates an inverted matrix to find the most similar law to the user's prompt input and returns it. 
- string_matcher.py ? 


**Content Generation (Summarization)**
The files that make up the summarization poriton of the application are listed below.

- app.py: Summarization module + Flask chatbot return (EDIT THIS)

#### LeTeRS code flowchart

![](images/dsan5400.drawio.png)