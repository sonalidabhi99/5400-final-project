## String Matcher

# import packages here

class StringMatcher:
    """Interface for matching strings based on regex"""

    def __init__(self, input1, input2, law, keywords, text, summary):
        self.input1 = input1
        self.input2 = input2
        self.law = law
        self.keywords = keywords
        self.text = text
        self.summary = summary
    
    def __str__(self):
      
        return f'Matching texts: ({self.input2},{self.keywords})'
    
    def __rep__(self):
        return f'{self.__class__.__name__}({self.__str__()})'

    def filtering(self):
        pass

    def cosine_similarity(self):
        documents = [self.input2, ]
        count_vectorizer = CountVectorizer(stop_words="english")
        count_vectorizer = CountVectorizer()
        sparse_matrix = count_vectorizer.fit_transform(documents)
        doc_term_matrix = sparse_matrix.todense()
        df = pd.DataFrame(
        doc_term_matrix,
        columns=count_vectorizer.get_feature_names_out(),
        index=["twitter", "facebook", "tiktok", "instagram"],
        )
print(df)
print(cosine_similarity(df, df))
        