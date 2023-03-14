# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import math
import random
import re
from porter_stemmer import PorterStemmer
from deps.emotions import emotions
import util
import string

import numpy as np


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'moviebot'
        self.all_titles = None
        self.creative = creative
        self.allTitles = {}
        self.toTitle = {}
        self.getAllTitles()
        # self.reformat_titles(all_titles)

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings)
        self.user_ratings = np.zeros(len(self.titles))
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

        self.movies = 0
        self.recommendations = []
        self.recommendations_index = 0

        self.affirmatives = ["yes", "yep", "yeah", "yup", "sure", "ok", "okay", "alright", "affirmative", "indeed", "certainly", "definitely", "absolutely", "by all means"]
        self.negatives = ["no", "nope", "nah", "negative", "never", "not at all", "not really", "not sure", "not now", "not yet"]

        self.closest_movie = False
        self.closest_movie_input = ""

        self.disambiguate_movies = False
        self.disambiguate_movies_input = ""

        self.catch_all_responses = ["I'm not sure I understand.", "I'm sorry, I don't have the information you're looking for.", "Let's talk about something else for now.", "I'm sorry, I didn't quite catch that.", "I'm not sure what you mean.", "Let me check on that and get back to you.", "I'm always learning. Can you tell me more about that?"]


    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        ########################################################################
        # TODO: Write a short greeting message                                 #
        ########################################################################

        greeting_message = "Hi! I'm MovieBot! I'm going to recommend a movie to you. First I will ask you about your taste in movies. Tell me about a movie that you have seen."

        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################
        return greeting_message

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        ########################################################################
        # TODO: Write a short farewell message                                 #
        ########################################################################

        goodbye_message = "Have a nice day!"

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return goodbye_message

    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################

    def process(self, line):
        """Process a line of input from the REPL and generate a response.

        This is the method that is called by the REPL loop directly with user
        input.

        You should delegate most of the work of processing the user's input to
        the helper functions you write later in this class.

        Takes the input string from the REPL and call delegated functions that
          1) extract the relevant information, and
          2) transform the information into a response to the user.

        Example:
          resp = chatbot.process('I loved "The Notebook" so much!!')
          print(resp) // prints 'So you loved "The Notebook", huh?'

        :param line: a user-supplied line of text
        :returns: a string containing the chatbot's response to the user input
        """
        ########################################################################
        # TODO: Implement the extraction and transformation in this method,    #
        # possibly calling other functions. Although your code is not graded   #
        # directly based on how modular it is, we highly recommended writing   #
        # code in a modular fashion to make it easier to improve and debug.    #
        ########################################################################

        if self.creative:
            if self.movies < 5:
                preprocessed_input = self.preprocess(line)
                sentiment = self.extract_sentiment(preprocessed_input)
                titles = self.extract_titles(preprocessed_input)

                if self.closest_movie:
                    closest_movie = self.closest_movie
                    self.closest_movie = False
                    line = line.translate(str.maketrans('', '', string.punctuation)).strip().lower()
                    if line in self.affirmatives:
                        line = self.closest_movie_input
                        preprocessed_input = self.preprocess(line)
                        sentiment = self.extract_sentiment(preprocessed_input)
                        titles = self.extract_titles(preprocessed_input)
                        title = titles[0]
                        preprocessed_input = preprocessed_input.replace(title, "")
                        preprocessed_input = preprocessed_input.replace("\"", "")
                        titles = self.reformat_titles(titles)
                        preprocessed_input = preprocessed_input + f'"{titles[0]}"'
                    else:
                        return(f"I'm not sure what you're talking about then. Let's try again with a different movie!\n")
                elif self.disambiguate_movies:
                    # search for line in disambiguate_movies titles
                    matches = self.disambiguate(line, self.disambiguate_movies)
                    self.disambiguate_movies = False
                    if len(matches) != 1:
                        return "I'm still not sure which movie you're talking about. Try being more specific!\n"
                    movie = matches[0]
                    preprocessed_input = self.preprocess(self.disambiguate_movies_input + f' "{self.titles[movie][0]}"') 
                    sentiment = self.extract_sentiment(preprocessed_input)
                    titles = self.extract_titles(preprocessed_input)
                    
                if len(titles) == 0:
                    emotions_present = []
                    for (emotion, synonyms) in emotions.items():
                        words = [word for word in synonyms if word in preprocessed_input.lower()]
                        if (len(words) > 0):
                            emotions_present.append(emotion)
                    if (len(emotions_present) > 0):
                        if emotions_present[0].lower() in ["sadness", "fear", "anger", "disgust"]:
                            return(f"I'm so sorry. Perhaps watching a movie will make you feel better!")
                        else:
                            return(f"I'm glad to hear you're feeling that way. Thanks for sharing!")
                    elif (preprocessed_input.lower().startswith("can you")):
                        ask = preprocessed_input.lower()
                        ask = ask.translate(str.maketrans('', '', string.punctuation))
                        ask = ' ' + ask + ' '
                        ask = ask.replace(" can you ", "").replace(" me ", " you ").replace(" my ", " your ").replace(" i ", " you ")
                        ask = ask.strip()
                        return(f"Sorry, I can't {ask} at this time.")
                    elif (preprocessed_input.lower().startswith("will you")):
                        ask = preprocessed_input.lower()
                        ask = ask.translate(str.maketrans('', '', string.punctuation))
                        ask = ' ' + ask + ' '
                        ask = ask.replace(" will you ", "").replace(" does ", "").replace(" me ", " you ").replace(" my ", " your ").replace(" i ", " you ")
                        ask = ask.strip()
                        return(f"Thanks for asking, but I don't want to {ask}!")
                    else:
                        # respond to arbitrary input
                        return(random.choice(self.catch_all_responses))
                                    
                # do spell-check and disambiguation
                if len(titles) != 0:
                    matching_movie = self.find_movies_by_title(titles[0]) # int[]
                    if len(matching_movie) == 0:
                        autocomplete_movies = self.find_movies_closest_to_title(titles[0], 5)
                        if (len(autocomplete_movies) > 0):
                            closest_movie = autocomplete_movies[0]
                            closest_movie_title = self.titles[closest_movie][0]
                            self.closest_movie = closest_movie
                            line = line.replace("\"", "")
                            self.closest_movie_input = line.replace(titles[0], f'"{closest_movie_title}"')
                            return (f"Did you mean {closest_movie_title}?\n")
                    elif len(matching_movie) > 1:
                        self.disambiguate_movies = matching_movie
                        self.disambiguate_movies_input = line.replace(f'"{titles[0]}"', "")
                        return (f"I found more than one movie called '{titles[0]}'. Which one did you mean? {[self.titles[movie][0] for movie in matching_movie]}\n")
                    else:
                        matched_movie = matching_movie[0]
                                
                matched_movies = []
                for title in titles:
                    i = self.find_movies_by_title(title)
                    if(len(i) > 0):
                        matched_movies.append(i)
                        
                if len(matched_movies) >= 1:
                    sentiments = self.extract_sentiment_for_movies(preprocessed_input)
                    response = "Got it"
                    for i, tuple in enumerate(sentiments):
                        if i == len(sentiments) - 1 and len(sentiments) > 1:
                            response += ", and you " + ("liked" if tuple[1] == 1 else "didn't like") + f" '{tuple[0]}'"
                        else:
                            response += ", you " + ("liked" if tuple[1] == 1 else "didn't like") + f" '{tuple[0]}'"
                        movie_idx = self.find_movies_by_title(tuple[0])[0]
                        self.user_ratings[movie_idx] = tuple[1]
                        self.movies += 1
                    print(response)
                    if self.movies >= 5:
                        print("That's all the info I needed! Let me think about what kind of movies you'd like...")
                        self.recommendations = self.recommend(self.user_ratings, self.ratings, k=10)
                        return (f"I recommend you watch {self.titles[self.recommendations[self.recommendations_index]][0]}. Would you like more movie recommendations?")
                    else:
                        return "What's another movie you liked/disliked?"
                else:
                    return "Sorry, I don't know that movie. Please try again."
                
            line = line.strip().translate(str.maketrans('', '', string.punctuation)).lower()
            if line in self.affirmatives:
                self.recommendations_index += 1
                if self.recommendations_index >= len(self.recommendations):
                    return("I'm sorry, I don't have any more recommendations for you. Maybe try again later?")
                return (f"I recommend you watch {self.titles[self.recommendations[self.recommendations_index]][0]}. Would you like more movie recommendations?")
            elif line in self.negatives:
                return "Ok, thanks for using MovieBot!"
            else:
                return "Sorry, I didn't understand that. Please answer with 'yes' or 'no'."
        # STANDARD MODE
        else:
            if self.movies < 5:
                preprocessed_input = self.preprocess(line)
                sentiment = self.extract_sentiment(preprocessed_input)
                titles = self.extract_titles(preprocessed_input)
                if len(titles) > 1:
                    return("Please tell me about your preferences one movie at a time")
                elif len(titles) == 0:
                    return("Sorry, I don't think you mentioned a movie, can you please tell me about a movie you liked/disliked?")
                title = titles[0]

                matching_movie = self.find_movies_by_title(titles[0]) # int[]
                if len(matching_movie) == 0:
                    return(f"I've never heard of '{title}', sorry... Tell me about another movie you liked.\n")
                elif len(matching_movie) > 1:
                    return(f"I found more than one movie called '{title}'. Can you clarify?\n")

                matched_movie = matching_movie[0]
                self.user_ratings[matched_movie] = sentiment

                if sentiment == 0:
                    return(f"I'm sorry, I'm not sure if you liked '{title}'. Tell me more about whether you liked it.\n")
                elif sentiment == 1:
                    self.movies += 1
                    if self.movies < 5:
                        return(f"Ok, you liked '{title}'! Tell me what you thought of another movie.\n")                        
                else:
                    self.movies += 1
                    if self.movies < 5:
                        return(f"Hmm, it seems like you didn't really like '{title}'. Can you tell me about a different movie?\n")
                if self.movies == 5:
                    print("Got it! Let me think about what kind of movies you'd like...")
                    self.recommendations = self.recommend(self.user_ratings, self.ratings, k=10)
                    return (f"I recommend you watch {self.titles[self.recommendations[self.recommendations_index]][0]}. Would you like more movie recommendations?")

            line = line.strip().translate(str.maketrans('', '', string.punctuation)).lower()

            if line in self.affirmatives:
                self.recommendations_index += 1
                if self.recommendations_index >= len(self.recommendations):
                    return("I'm sorry, I don't have any more recommendations for you. Maybe try again later?")
                return (f"I recommend you watch {self.titles[self.recommendations[self.recommendations_index]][0]}. Would you like more movie recommendations?")
            elif line in self.negatives:
                return "Ok, thanks for using MovieBot!"
            else:
                return "Sorry, I didn't understand that. Please answer with 'yes' or 'no'."

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################

    @staticmethod
    def preprocess(text):
        """Do any general-purpose pre-processing before extracting information
        from a line of text.

        Given an input line of text, this method should do any general
        pre-processing and return the pre-processed string. The outputs of this
        method will be used as inputs (instead of the original raw text) for the
        extract_titles, extract_sentiment, and extract_sentiment_for_movies
        methods.

        Note that this method is intentially made static, as you shouldn't need
        to use any attributes of Chatbot in this method.

        :param text: a user-supplied line of text
        :returns: the same text, pre-processed
        """
        ########################################################################
        # TODO: Preprocess the text into a desired format.                     #
        # NOTE: This method is completely OPTIONAL. If it is not helpful to    #
        # your implementation to do any generic preprocessing, feel free to    #
        # leave this method unmodified.                                        #
        ########################################################################

        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

        return text

    def getAllTitles(self = 1):
        movie_tuple = util.load_titles('./data/movies.txt')
        for i, (m, tags) in enumerate(movie_tuple):
            self.toTitle[i]=m
            permutations=[]
            nums = re.findall(r"\d{4}", m)
            date = nums[-1] if len(nums)>0 else "####"
            m1 = re.sub(r"\s\(\d{4}\)", "", m)
            strs = re.findall(r"^[^\s(]+(?:[^(][^\s(]+)*",m1)
            strs += re.findall(r"\((?:a.k.a.)?\s?([^)]*)\)", m1)
            for s in strs:
                article = re.findall(r",[ \w]+$",s)
                if len(article)==0:
                    permutations+=[s, s+" ("+date+")"]
                else:
                    base = re.findall(r"(.*),[ \w]+$",s)[0]
                    permutations+=[base, base+" ("+date+")"]
                    base = article[0][2:]+" "+base
                    permutations+=[base, base+" ("+date+")"]
                permutations+=[s]
            for alias in permutations: 
                if alias not in self.allTitles.keys():
                    self.allTitles[alias]=[]
                self.allTitles[alias]+=[i]

    def extract_titles(self, preprocessed_input):
        """Extract potential movie titles from a line of pre-processed text.

        Given an input text which has been pre-processed with preprocess(),
        this method should return a list of movie titles that are potentially
        in the text.

        - If there are no movie titles in the text, return an empty list.
        - If there is exactly one movie title in the text, return a list
        containing just that one movie title.
        - If there are multiple movie titles in the text, return a list
        of all movie titles you've extracted from the text.

        Example:
          potential_titles = chatbot.extract_titles(chatbot.preprocess(
                                            'I liked "The Notebook" a lot.'))
          print(potential_titles) // prints ["The Notebook"]

        :param preprocessed_input: a user-supplied line of text that has been
        pre-processed with preprocess()
        :returns: list of movie titles that are potentially in the text
        """
        # Define a regular expression pattern to match movie titles
        pattern = r'"([^"]+)"'

        # Search for matches using the pattern
        matches = re.findall(pattern, preprocessed_input)

        # Return the matches as a list
        return matches
    
    def reformat_titles(self, all_titles):
        for title in all_titles:
            pattern = r"\s*\(\d{4}\)"
            if not re.search(pattern, title):
                for i in range(len(all_titles)):
                    # Remove "(2016)" from the string using re.sub()
                    all_titles[i] = re.sub(pattern, "", all_titles[i])
                    # Remove leading and trailing whitespace from the string using
                    all_titles[i] = all_titles[i].strip()

            # Define a regular expression pattern to match ", The", " An", or " A" at the beginning of a string
            pattern = r", (The|An|A)"

            for i in range(len(all_titles)):
                # Check if the pattern matches the string
                match = re.search(pattern, all_titles[i])

                if match:
                    match = match.group()
                    all_titles[i] = re.sub(pattern, "", all_titles[i])
                    match = match.strip()
                    all_titles[i] = match[2:] + ' ' + all_titles[i]

        return all_titles

    def find_movies_by_title(self, title):
        """ Given a movie title, return a list of indices of matching movies.
        - If no movies are found that match the given title, return an empty
        list.
        - If multiple movies are found that match the given title, return a list
        containing all of the indices of these matching movies.
        - If exactly one movie is found that matches the given title, return a
        list
        that contains the index of that matching movie.
        Example:
            ids = chatbot.find_movies_by_title('Titanic')
            print(ids) // prints [1359, 2716]
        :param title: a string containing a movie title
        :returns: a list of indices of matching movies
        """
        pattern = re.compile("\\b"+title.lower()+"\\b")
        matched_titles=[]
        for db_title,j in self.allTitles.items():
            for i in j:
                if title.lower() == db_title.lower():
                    matched_titles.append(i)
        if self.creative:
            for db_title,j in self.allTitles.items():
                for i in j:
                    if re.search(pattern, db_title.lower()):
                        matched_titles.append(i)

        return list(set(matched_titles))
        

    def extract_sentiment(self, preprocessed_input):
        """Extract a sentiment rating from a line of pre-processed text.

        You should return -1 if the sentiment of the text is negative, 0 if the
        sentiment of the text is neutral (no sentiment detected), or +1 if the
        sentiment of the text is positive.

        As an optional creative extension, return -2 if the sentiment of the
        text is super negative and +2 if the sentiment of the text is super
        positive.

        Example:
          sentiment = chatbot.extract_sentiment(chatbot.preprocess(
                                                    'I liked "The Titanic"'))
          print(sentiment) // prints 1

        :param preprocessed_input: a user-supplied line of text that has been
        pre-processed with preprocess()
        :returns: a numerical value for the sentiment of the text
        """
        sentiment_lexicon = util.load_sentiment_dictionary(
            './data/sentiment.txt')

        # remove movie titles from the input i.e. for "I loved "10 Things I Hate About You"""
        titles = self.extract_titles(preprocessed_input)
        for title in titles:
            preprocessed_input = preprocessed_input.replace(title, '')

        words = preprocessed_input.split()
        sentiment = 0

        # use porter stemmer
        stemmer = PorterStemmer()
        # stem the input words
        stemmed_words = []
        for word in words:
            stemmed_words.append(stemmer.stem(word.lower()))
        # stem the keys of the sentiment lexicon
        stemmed_sentiment_lexicon = {}
        for key in sentiment_lexicon:
            stemmed_sentiment_lexicon[stemmer.stem(
                key.lower())] = sentiment_lexicon[key]

        negation = ["not", "didn't", "never", "no", "none", "neither", "nor",
                    "nowhere", "nobody", "nothing", "hardly", "scarcely", "barely"]
        a = []
        for word in stemmed_words:
            if word in stemmed_sentiment_lexicon.keys():
                a.append(word)
            if word in negation:
                a.append(word)
        stemmed_words = a
        for i, word in enumerate(stemmed_words):
            if word in stemmed_sentiment_lexicon:
                if stemmed_sentiment_lexicon[word] == 'pos':
                    if stemmed_words[i-1] not in negation:
                        sentiment += 1
                    else:
                        sentiment -= 1
                elif stemmed_sentiment_lexicon[word] == 'neg':
                    if stemmed_words[i-1] not in negation:
                        sentiment -= 1
                    else:
                        sentiment += 1

        if sentiment < 0:
            return -1
        elif sentiment > 0:
            return 1
        else:
            return 0

    def extract_sentiment_for_movies(self, preprocessed_input):
        """Creative Feature: Extracts the sentiments from a line of
        pre-processed text that may contain multiple movies. Note that the
        sentiments toward the movies may be different.

        You should use the same sentiment values as extract_sentiment, described

        above.
        Hint: feel free to call previously defined functions to implement this.

        Example:
        sentiments = chatbot.extract_sentiment_for_text(
                        chatbot.preprocess(
                        'I liked both "Titanic (1997)" and "Ex Machina".'))
        print(sentiments) // prints [("Titanic (1997)", 1), ("Ex Machina", 1)]

        :param preprocessed_input: a user-supplied line of text that has been
        pre-processed with preprocess()
        :returns: a list of tuples, where the first item in the tuple is a movie
        title, and the second is the sentiment in the text toward that movie
        """
        titles = self.extract_titles(preprocessed_input)
        slices = []

        for title in titles:
            start = preprocessed_input.find(title)
            slices.append(preprocessed_input[:start])
            preprocessed_input = preprocessed_input[start+len(title):]
        
        and_words = ["and", "or"]
        not_words = ["not", "but"]

        result = []
        lastSentiment = 0
        for i in range(len(slices)):
            title = titles[i]
            slice = slices[i]

            sentiment = self.extract_sentiment(slice)
            if sentiment != 0:
                result.append((title, sentiment))
            else:
                if any(word in slice for word in and_words):
                    sentiment = lastSentiment
                    result.append((title, sentiment))
                elif any(word in slice for word in not_words):
                    sentiment = -lastSentiment
                    result.append((title, sentiment))
                else:
                    sentiment = lastSentiment
                    result.append((title, sentiment))
            lastSentiment = sentiment
        
        return result

    def levDist(self,a,b):
        arr = list(range(len(a)+1))
        arr2=[]
        for i in range(len(b)):
            arr2=[i+1]+[0]*len(a)
            for j in range(len(a)):
                if(a[j]==b[i]):
                    arr2[j+1]=arr[j]
                else:
                    arr2[j+1]=min(arr[j+1]+1,arr2[j]+1)
            arr=arr2
        return arr[-1]

    def find_movies_closest_to_title(self, title, max_distance=5):
        """Creative Feature: Given a potentially misspelled movie title,
        return a list of the movies in the dataset whose titles have the least
        edit distance from the provided title, and with edit distance at most
        max_distance.

        - If no movies have titles within max_distance of the provided title,
        return an empty list.
        - Otherwise, if there's a movie closer in edit distance to the given
        title than all other movies, return a 1-element list containing its
        index.
        - If there is a tie for closest movie, return a list with the indices
        of all movies tying for minimum edit distance to the given movie.

        Example:
          # should return [1656]
          chatbot.find_movies_closest_to_title("Sleeping Beaty")

        :param title: a potentially misspelled title
        :param max_distance: the maximum edit distance to search for
        :returns: a list of movie indices with titles closest to the given title
        and within edit distance max_distance
        """
        movie_tuple = util.load_titles('./data/movies.txt')

        minMovies=[]
        minDist=max_distance+1

        title=title.lower()

        for name,j in self.allTitles.items():
            for i in j:
                d=self.levDist(name.lower(),title)
                if(d<minDist):
                    minMovies=[i]
                    minDist=d
                elif(d == minDist and i not in minMovies):
                    minMovies+=[i]
        return minMovies

    def disambiguate(self, clarification, candidates):
        """Creative Feature: Given a list of movies that the user could be
        talking about (represented as indices), and a string given by the user
        as clarification (eg. in response to your bot saying "Which movie did
        you mean: Titanic (1953) or Titanic (1997)?"), use the clarification to
        narrow down the list and return a smaller list of candidates (hopefully
        just 1!)
        - If the clarification uniquely identifies one of the movies, this
        should return a 1-element list with the index of that movie.
        - If it's unclear which movie the user means by the clarification, it
        should return a list with the indices it could be referring to (to
        continue the disambiguation dialogue).
        Example:
            chatbot.disambiguate("1997", [1359, 2716]) should return [1359]
        :param clarification: user input intended to disambiguate between the
        given movies
        :param candidates: a list of movie indices
        :returns: a list of indices corresponding to the movies identified by
        the clarification
        """
        clarification = clarification.translate(str.maketrans('', '', string.punctuation))
        matches = [a for a in candidates if clarification in re.sub(r"\(\d{4}\)","",self.toTitle[a].lower())]
        if len(matches) == 0:
            matches = [a for a in candidates if clarification in self.toTitle[a]]
        return matches


    ############################################################################
    # 3. Movie Recommendation helper functions                                 #
    ############################################################################

    @staticmethod
    def binarize(ratings, threshold=2.5):
        """Return a binarized version of the given matrix.

        To binarize a matrix, replace all entries above the threshold with 1.
        and replace all entries at or below the threshold with a -1.

        Entries whose values are 0 represent null values and should remain at 0.

        Note that this method is intentionally made static, as you shouldn't use
        any attributes of Chatbot like self.ratings in this method.

        :param ratings: a (num_movies x num_users) matrix of user ratings, from
         0.5 to 5.0
        :param threshold: Numerical rating above which ratings are considered
        positive

        :returns: a binarized version of the movie-rating matrix
        """
        ########################################################################
        # TODO: Binarize the supplied ratings matrix.                          #
        #                                                                      #
        # WARNING: Do not use self.ratings directly in this function.          #
        ########################################################################

        # The starter code returns a new matrix shaped like ratings but full of
        # zeros.
        binarized_ratings = np.where(ratings > threshold, 1, -1)
        binarized_ratings = np.where(ratings == 0, 0, binarized_ratings)

        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        return binarized_ratings

    def similarity(self, u, v):
        """Calculate the cosine similarity between two vectors.

        You may assume that the two arguments have the same shape.

        :param u: one vector, as a 1D numpy array
        :param v: another vector, as a 1D numpy array

        :returns: the cosine similarity between the two vectors
        """
        ########################################################################
        # TODO: Compute cosine similarity between the two vectors.             #
        ########################################################################
        if np.linalg.norm(u)*np.linalg.norm(v) == 0:
            return 0
        similarity = np.dot(u, v)/(np.linalg.norm(u)*np.linalg.norm(v))
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return similarity

    def recommend(self, user_ratings, ratings_matrix, k=10, creative=False):
        """Generate a list of indices of movies to recommend using collaborative
         filtering.

        You should return a collection of `k` indices of movies recommendations.

        As a precondition, user_ratings and ratings_matrix are both binarized.

        Remember to exclude movies the user has already rated!

        Please do not use self.ratings directly in this method.

        :param user_ratings: a binarized 1D numpy array of the user's movie
            ratings
        :param ratings_matrix: a binarized 2D numpy matrix of all ratings, where
          `ratings_matrix[i, j]` is the rating for movie i by user j
        :param k: the number of recommendations to generate
        :param creative: whether the chatbot is in creative mode

        :returns: a list of k movie indices corresponding to movies in
        ratings_matrix, in descending order of recommendation.
        """

        ########################################################################
        # TODO: Implement a recommendation function that takes a vector        #
        # user_ratings and matrix ratings_matrix and outputs a list of movies  #
        # recommended by the chatbot.                                          #
        #                                                                      #
        # WARNING: Do not use the self.ratings matrix directly in this         #
        # function.                                                            #
        #                                                                      #
        # For starter mode, you should use item-item collaborative filtering   #
        # with cosine similarity, no mean-centering, and no normalization of   #
        # scores.                                                              #
        ########################################################################
        count = 0
        rxi = []
        for i in range(len(ratings_matrix)):
            # if np.count_nonzero(ratings_matrix[i]) == 0:
            #     rxi.append(0)
            #     break
            sum = 0
            for j in range(len(user_ratings)):
                if user_ratings[j] != 0 and i != j:
                    sum += self.similarity(ratings_matrix[i],ratings_matrix[j]) * user_ratings[j]
            rxi.append(sum)
        recommendations = np.argsort(rxi)[::-1][:k].tolist()
        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        return recommendations

    ############################################################################
    # 4. Debug info                                                            #
    ############################################################################

    def debug(self, line):
        """
        Return debug information as a string for the line string from the REPL

        NOTE: Pass the debug information that you may think is important for
        your evaluators.
        """
        debug_info = 'debug info'
        return debug_info

    ############################################################################
    # 5. Write a description for your chatbot here!                            #
    ############################################################################
    def intro(self):
        """Return a string to use as your chatbot's description for the user.

        Consider adding to this description any information about what your
        chatbot can do and how the user can interact with it.
        """
        return """
        Your task is to implement the chatbot as detailed in the PA7
        instructions.
        Remember: in the starter mode, movie names will come in quotation marks
        and expressions of sentiment will be simple!
        TODO: Write here the description for your own chatbot!
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')