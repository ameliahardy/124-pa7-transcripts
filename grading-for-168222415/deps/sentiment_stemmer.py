import util
from porter_stemmer import PorterStemmer

sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
stemmer = PorterStemmer()
try:
    with open("./stemmed_sentiment.txt", "w") as f:
        for word in sentiment:
            stemmed_word = stemmer.stem(word)
            f.write(stemmed_word + "," + sentiment[word]+"\n")
except FileNotFoundError:
    print("The 'docs' directory does not exist")
