# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
from enum import _EnumDict
from queue import Empty
from turtle import title
from enum import Enum
import random
from porter_stemmer import PorterStemmer
import util
import re
import numpy as np


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'Chavo del Ocho'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        # Get Porter Stemmer and use on sentiment dictionary
        self.ps = PorterStemmer()
        self.stem_sentiment = {self.ps.stem(key):val for key,val in self.sentiment.items()}

        self.articles = ['a', 'an', 'and', 'the', 'le', 'la']
        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings)

        self.mode = self.Mode.DEFAULT

        self.titles_in_input = []

        self.ratings_needed = 5
        self.n_recs = 6
        self.user_ratings = np.zeros((ratings.shape[0],))
        self.count_rated = 0
        self.recommendations = []
        self.next_rec = None
        self.options_to_check = []
        self.prev_sentiment = 0
        
        return
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

    class Mode(Enum):
        DEFAULT = "default"
        GIVE_RECS = "give_recs"
        DISAMBIGUATE = "disambiguate"
        SPELL_CHECKING = "spell_checking"
        MULTIPLE_MATCHES = "multiple_matches"
        CHECK_ONE_OPTION = "check_one_option"
        CHECK_MULTIPLE_OPTIONS = "check_multiple_options"

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        ########################################################################
        # TODO: Write a short greeting message                                 #
        ########################################################################

        greeting_message = """Hola! I'm Chavo and I can help you find your new favorite movie! Just tell me about a
movie that you have seen and whether or not you like it. Ah, just make sure to place the movie between
quotes so I can recognize it, por favor!"""

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

        goodbye_message = "Adiós! Hope have a nice day!"

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return goodbye_message

    ############################################################################
    # 2. Processing of conversation                                            #
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

        preprocessed = self.preprocess(line)

        if self.mode == self.Mode.GIVE_RECS:
            response = self.run_give_recs(preprocessed)
        elif self.mode == self.Mode.CHECK_MULTIPLE_OPTIONS:
            response = self.run_check_multiple(preprocessed)
        elif self.mode == self.Mode.CHECK_ONE_OPTION:
            response = self.run_check_one(preprocessed)
        else:
            # Mode is getting movie recs / arbitrary / emotion
            response = self.run_default(preprocessed)
        
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return response
    
    ############################################################################
    # 2. Functions for running steps                                           #
    ############################################################################
    
    def run_give_recs(self, preprocessed):
        sentiment = self.is_affirmative(preprocessed)
        if sentiment >= 0:
            # Provide recommendation
            rec_title = self.titles[self.recommendations[self.next_rec]][0]
            self.next_rec += 1
            if self.next_rec == len(self.recommendations):
                self.next_rec = 0
                return self.generate_response(self.Response.LAST_REC, [rec_title])
            else:
                res_enum = self.Response.FIRST_REC if self.next_rec == 1 else self.Response.ANOTHER_REC
                return " ".join([
                                self.generate_response(res_enum, [rec_title]),
                                self.generate_response(self.Response.ASK_MORE_REC)
                                ])
        else:
            # Exit
            return self.generate_response(self.Response.GOODBYE)


    def run_default(self, preprocessed):
        self.titles_in_input = self.extract_titles(preprocessed)
        
        if len(self.titles_in_input) == 0:
            if not self.creative:
                return self.generate_response(self.Response.NO_TITLE_FOUND)
            
            # Creative mode: arbitrary or emotion
            emotion, emotion_type = self.extract_emotion(preprocessed)
            if emotion:
                res = self.Response.EMOTION_GOOD if emotion == 1 else self.Response.EMOTION_BAD
                return self.generate_response(res, [emotion_type])

            if self.has_salute(preprocessed):
                return self.generate_response(self.Response.SALUTE_RES)
            elif self.has_how_are_you(preprocessed):
                return self.generate_response(self.Response.HOW_ARE_YOU_RES)
            elif self.has_arbitrary_topic(preprocessed):
                return self.generate_response(self.Response.ARBITRARY)

            return self.generate_response(self.Response.NO_TITLE_FOUND)

        elif len(self.titles_in_input) > 1:
            # TODO: If we want multiple sentiment, then change this line
            return self.generate_response(self.Response.MORE_THAN_ONE_TITLE_FOUND)
        
        title = self.titles_in_input[0]
        sentiment = self.extract_sentiment(preprocessed)
        if sentiment == 0:
            return self.generate_response(self.Response.SENTIMENT_NOT_FOUND, [title])

        # TODO: Implement Disambiaguation and spell checking
        indexes = self.find_movies_by_title(title)

        if len(indexes) == 0:
            if not self.creative:
                return self.generate_response(self.Response.NO_MOVIE_MATCH, [title])
            
            # TODO: Add for spell checking
            candidate_indices = self.find_movies_closest_to_title(title)

            if len(candidate_indices) == 0:
                return self.generate_response(self.Response.NO_MOVIE_MATCH, [title])

            self.prev_sentiment = sentiment
            self.options_to_check = [(index, self.titles[index][0]) for index in candidate_indices]

            if len(candidate_indices) == 1:
                self.mode = self.Mode.CHECK_ONE_OPTION
                return " ".join([
                        self.generate_response(self.Response.DID_YOU_MEAN, [self.options_to_check[0][1]])
                    ])
            else:
                self.mode = self.Mode.CHECK_MULTIPLE_OPTIONS
                return " ".join([
                        self.generate_response(self.Response.WHICH_OPTION, [", ".join([f"\"{el[1]}\"" for el in self.options_to_check])])
                    ])
        
        elif len(indexes) > 1:
            if not self.creative:
                return " ".join([
                    self.generate_response(self.Response.MULTIPLE_MOVIE_MATCHES, [title]),
                    self.generate_response(self.Response.TRY_AGAIN)
                ])
            self.prev_sentiment = sentiment
            self.options_to_check = [(index, self.titles[index][0]) for index in indexes]
            self.mode = self.Mode.CHECK_MULTIPLE_OPTIONS
            return " ".join([
                    self.generate_response(self.Response.MULTIPLE_MOVIE_MATCHES, [title]),
                    self.generate_response(self.Response.WHICH_OPTION, [", ".join([f"\"{el[1]}\"" for el in self.options_to_check])])
                ])
        
        index = indexes[0]
        full_title = self.titles[index][0]

        # run sentiment analysis
        if sentiment == 0:
            return self.generate_response(self.Response.SENTIMENT_NOT_FOUND, [full_title])
        
        return self.rank_movie_and_respond(index, sentiment)
        
        
    def run_check_one(self, preprocessed):
        # cases: positive then store rec OR neg ask for movies again
        sentiment = self.is_affirmative(preprocessed)
        if sentiment > 0:
            return self.rank_movie_and_respond(self.options_to_check[0][0], self.prev_sentiment)
        
        self.mode = self.Mode.DEFAULT
        return " ".join([
            self.generate_response(self.Response.OKAY),
            self.generate_response(self.Response.ASK_MORE_MOVIES)
            ])


    def run_check_multiple(self, preprocessed):
        # cases: first match then store rec OR no matches so ask again
        candidate_indices = [el[0] for el in self.options_to_check]
        new_candidates = self.disambiguate(preprocessed, candidate_indices)

        if len(new_candidates) == 0:
            self.mode = self.Mode.DEFAULT
            return " ".join([
                self.generate_response(self.Response.OKAY),
                self.generate_response(self.Response.ASK_MORE_MOVIES)
                ])
        elif len(new_candidates) == 1:
            return self.rank_movie_and_respond(new_candidates[0], self.prev_sentiment)
        
        self.options_to_check = [(index, self.titles[index][0]) for index in new_candidates] 
        
        return " ".join([
            self.generate_response(self.Response.SORRY),
            self.generate_response(self.Response.WHICH_OPTION, [", ".join([f"\"{el[1]}\"" for el in self.options_to_check])])
            ])

    def rank_movie_and_respond(self, index, sentiment):
        self.user_ratings[index] = sentiment
        self.count_rated += 1

        full_title = self.titles[index][0]

        enum_res = self.Response.ACK_POSITIVE if sentiment > 0 else self.Response.ACK_NEGATIVE
        response = self.generate_response(enum_res, [full_title])

        if self.count_rated >= self.ratings_needed:
            self.recommendations = self.recommend(self.user_ratings, self.ratings, k=self.n_recs)
            rec_title = self.titles[self.recommendations[0]][0]
            self.next_rec = 1
            self.mode = self.Mode.GIVE_RECS
            return " ".join([response,
                             self.generate_response(self.Response.READY_FOR_RECS),
                             self.generate_response(self.Response.FIRST_REC, [rec_title]),
                             self.generate_response(self.Response.ASK_MORE_REC)
                             ])
        else:
            return " ".join([response, self.generate_response(self.Response.ASK_MORE_MOVIES)])
        
    def is_affirmative(self, line):
        positive_set = ["yes", "yeah", "yess", "sure", "positive", "yup"]
        negative_set = ["no", "nah", "noo", "negative", "nope"]
        input_set = set(line.lower().split())
        
        diff = len(input_set.intersection(positive_set)) - len(input_set.intersection(negative_set))
        if diff > 0:
            return 1
        elif diff == 0:
            return 0
        else:
            return -1
        
    def extract_emotion(self, line):
        emotions = {
            1: ["happy", "happiness", "cheerful", "delighted", "elated", "glad", "joyful", "thrilled", "joyous", "jubilant"],
            -1: ["angry", "mad", "sad", "frustrated", "melancholic", "somber", "pessimistic", "sorrowful", "resentful", "annoyed", "lonely"]
        }

        cleaned = self.clean_string(line.lower())
        for etype in emotions:
            for w in emotions[etype]:
                if w in cleaned:
                    return etype, w
        return 0, ""
    
    def has_salute(self, line):
        cleaned = self.clean_string(line.lower())
        options = ["hi", "hello", "sup", "heyo", "aloha", "hola", "salute"]
        for option in options:
            if option in cleaned:
                return True
        return False

    def has_how_are_you(self, line):
        cleaned = self.clean_string(line.lower())
        options = ["how are you", "how are things", "are you good", "hows life"]
        for option in options:
            if option in cleaned:
                return True
        return False

    def has_arbitrary_topic(self, line):
        cleaned = self.clean_string(line.lower())
        options = ["how can", "can you help", "im tired", "whats your", "what is the", "can i"]
        for option in options:
            if option in cleaned:
                return True
        return False
    
    @staticmethod
    def clean_string(string):
        # Replace all non-alphanumeric characters with an empty string
        cleaned_string = re.sub(r'[^a-zA-Z0-9\s]', '', string)
        return cleaned_string

    ############################################################################
    # 2. Responses                                                             #
    ############################################################################

    class Response(Enum):
        NO_TITLE_FOUND = ["I didn't see any title. Can you try again por favor?", "Hmmm, is that a movie? Can you try again?", "Not sure I got that. Try writing your movie between quotes!"]
        MORE_THAN_ONE_TITLE_FOUND = ["Please let's do only one movie at a time. I'm not that smart yet!", "I can only handle one movie at a time! Could you try again amigo?"]
        NO_MOVIE_MATCH = ["Couldn't match any movie with the title \"{}\". Can you try again por favor?"]
        MULTIPLE_MOVIE_MATCHES = ["Woah! I found multiple matches for \"{}\"."]
        SENTIMENT_NOT_FOUND = ["I couldn't tell if you liked or not \"{}\". Can you try again por favor?"]
        ACK_POSITIVE = ["Gracias! I see that you liked \"{}\", not bad taste!", "Great, so you liked \"{}\". I love it too."]
        ACK_NEGATIVE = ["I see that you didn't liked \"{}\" (not my favorite either ha!)", "So you did not like \"{}\", it was no bueno I know!"]
        ASK_MORE_MOVIES = ["Can you tell me about another movie? Gracias"]
        READY_FOR_RECS = ["Excelente, I'm ready to provide you with recommendations!"]
        FIRST_REC = ["My first rec for you is \"{}\".", "The first thing that comes to mind is that you should watch \"{}\"."]
        ASK_MORE_REC = ["Would you want another rec amigo?"]
        ANOTHER_REC = ["My next recommendation is for you to watch \"{}\"! Muy bueno!"]
        LAST_REC = ["Okay... I have one last recommendation for you: \"{}\". Would you want to go back to the first rec?"]
        GOODBYE = ["Okay! Hope you have a nice day! Adiós!"]
        SORRY = ["Sorry, I didn't get that.", "Perdón, what was that?"]
        WHICH_OPTION = ["Which one did you mean? {}", "So which one are you talking about {}?"]
        OKAY = ["Okay.", "I see.", "Hmm okay.", "Right.", "Bueno bueno."]
        TRY_AGAIN = ["Can you try again por favor?", "Let's try one more time amigo."]
        DID_YOU_MEAN = ["Wait... did you mean \"{}\"?", "Are you referring to \"{}\"?"]
        HOW_ARE_YOU_RES = ["I'm good! I hope you are too! Would you like to tell me about a movie you've watched?"]
        ARBITRARY = ["Hmm I can't really talk about that. But let's chat about movies you've liked!",
                     "I'd rather not discuss that, but I can assist you with movies! Sí sí sí",
                     "I am not allowed to discuss other topics. Would you want to talk about movies? Ajuaaa"]
        EMOTION_BAD = ["I'm sorry that you're feeling {}. I would give you a hug if I had a body!", "Ohhh, sorry to hear that. Hopefully a good movie rec can cheer you up! Yuup"]
        EMOTION_GOOD = ["That's great, I'm also feeling {} myself!!! SIII", "Great to hear that you're feeling {}! Tadaaa"]
        SALUTE_RES = ["Hola hola!", "Heyo! Wanna tell me about movies you've seen?"]

    def generate_response(self, res, args=[]):
        return random.choice(res.value).format(*args)

    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################

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
        
        # remove any special characters? only want alphanumeric im guessing...
        # return text.lower()

        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

        return text

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
        # regex that allows nested speech marks --> (["'])(?:(?=(\\?))\2.)*?\1
        # Find text inside speech marks
        text = re.findall(r'"([^"]*)"', preprocessed_input)

        
        return text
    
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
        # print(title)
        # Do some cleanup on the title
        title = title.lower()
        title_words = title.split()

        # Move any articles to the end of the sentence (but before year)
        if (title_words[0] in self.articles):
            date = ""
            if (re.match('\(\d{4}\)', title_words[-1]) != None):
                date = title_words[-1] # date = title_words.pop(-1)
                title_words.pop(-1)
            title_words[-1] = title_words[-1] + ","
            title_words.append(title_words[0])
            title_words.pop(0)
            if len(date) > 0:
                title_words.append(date)
        title = " ".join(title_words)
        # print(title)
        
        # ids = [[i, item[0]] for i, item in enumerate(self.titles) if re.match(title, item[0])]
        ids = []
        for i, movie in enumerate(self.titles):
            movie_lowercase = movie[0].lower()
            movie_datestripped = re.sub(' \(\d{4}\)', '', movie_lowercase)
            akas = re.findall(' \(.[^\)\(]*\)', movie_datestripped)
            # akas = [re.sub('(?<=\. )\w+', '', aka) for aka in akas]
            akas = [aka.replace('(a.k.a. ', '') for aka in akas]
            akas = [aka[1:-1] for aka in akas]
            movie_altstripped = re.sub(' \(.*\)', '', movie_datestripped)
            movie_variations = [movie_lowercase, movie_altstripped, movie_datestripped]
            # Add any akas to the options
            for aka in akas:
                movie_variations.append(aka)
                # print(movie_variations)
            if title in movie_variations:
                # print(akas)
                ids.append(i)
    
        # Remove any double counted indices
        ids = list(set(ids))
        # print(ids)
        return ids  

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
          
        Creative Feature: Extracts the sentiments from a line of
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
        
        # Get Movies
        movies = self.titles_in_input
        if len(movies) == 0: return 0

        # Create a reverse dictionary that implies negation
        reverse_dictionary = ["not", "didnt", "dont", "no", "never", "hardly"]

        # Create list of words that imply a strong feeling
        positive_words = ["incredible", "great", "excellent", "best", "love", "delight", "sensational", "superb", "fantastic", "amazing", "joy", "wonderful", "adore", "outstanding", "terrific", "unmatched", "exhilirating"]
        negative_words = ["terrible", "nasty", "shit", "abysmal", "horrific", "horrendous", "horrible", "awful", "sucked", "bad", "disaster", "carcrash", "hated"]
        adverbs = ["really", "particularly", "remarkably", "notably", "reeaally", "reaaally", "reeeally", "realli", "reealli"]
        # Stem these words
        positive_words = [self.ps.stem(w) for w in positive_words]
        negative_words = [self.ps.stem(w) for w in negative_words]
        adverbs = [self.ps.stem(w) for w in adverbs]
        # Create empty list of tuples (title, score)
        '''
        movie_sentiments = []
        for i in range(len(movies)): 
            movie_sentiments.append((movies[i], 0))
        '''

        # Get rid of film from input line and tidy (remove non-alphanumerics and whitespace and then use porter stemmer)
        removal_str = '\"' + movies[0] + '\"'
        line = preprocessed_input.replace(removal_str, "").lower()
        line = [char.strip() for char in line.split()]
        line = [re.compile('[^a-zA-Z0-9]').sub('', char) for char in line]
        line = [self.ps.stem(w) for w in line]
        # print(line)
        # Keep track of the sentiment score
        score = 0

        # Loop through the line, checking if a word is in the sentiment dictionary
        for i, word in enumerate(line):
            # print(i, word)
            # Keep a binary negation indicator
            negation_counter = 1

            if word in self.stem_sentiment.keys():
                
                # Edge case: double negatives NOT WORKING CURRENTLY

                if (i and line[i-1] in reverse_dictionary) or (i > 1 and line[i-2] in reverse_dictionary): negation_counter = -1
                if self.stem_sentiment[word] == "pos" and negation_counter > 0:
                    score += 1 
                    if self.creative and (word in positive_words or (i and line[i-1] in adverbs)): score += 1 
                elif self.stem_sentiment[word] == "pos" and negation_counter < 0:
                    score -= 1 
                elif self.stem_sentiment[word] != "pos" and negation_counter > 0:
                    score -= 1
                    if self.creative and (word in negative_words or (i and line[i-1] in adverbs)): score -= 1 
                elif self.stem_sentiment[word] != "pos" and negation_counter < 0:
                    score += 1
                    
            # print("Score is " + str(score))
            # print("Negation counter is " + str(negation_counter))

        if self.creative:
            if score > 1: return 2
            elif score < -1: return -2
            else: return score
        else:     
            if score > 0: return 1
            elif score < 0: return -1

        return 0


    #helper function for find_movies_closest_to_title and gets minimum for three numbers
    def minimum_calulator(self, replace, insert, delete):
        return min(min(replace, insert), delete)

        # helper dp function for find_movies_closest_to_title and gets minimum edit distance
    def edit_distance(self, str_x, str_y, x_len, y_len):
        dp = [[0 for _ in range(y_len + 1)] for _ in range(x_len + 1)]

        for i in range(x_len + 1):
            for j in range(y_len + 1):
                if i == 0:
                    dp[i][j] = j
                elif j == 0:
                    dp[i][j] = i
                elif str_x[i - 1] == str_y[j - 1]:
                    dp[i][j] = dp[i -1][j - 1]
                else:
                    dp[i][j] = min(1 + min(dp[i-1][j], dp[i][j-1]), 2 + dp[i-1][j-1])
        return dp[x_len][y_len]

    def find_movies_closest_to_title(self, title, max_distance=3):
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
        list = []
        movie_to_edit_distance = {}
        #list we will add our titles to
        title_len = len(title) #we will be comparing this title to the list of movie names we have
        curr_distance = 4
        #we need curr_distance < max_distance
        for i, title_and_genre in enumerate(self.titles):
            movie_and_year = title_and_genre[0]
            #pattern to extract movie without year by taking string up until first parantheses
            #pattern = r'^[^\s(]+(?= \s+\()'
            #pattern = r'^[^ (\n]+(?= \()'
            #pattern =r'^.*?(?= \()'
            pattern = r'([^\(\)]+)\s*\(\d{4}\)'
            movie_matches = re.search(pattern, movie_and_year)
            if movie_matches:
                movie = movie_matches.group(1)
                movie_len = len(movie)
                #if movie[0].lower() == title[0].lower():
                movie_distance = self.edit_distance(movie, title, movie_len, title_len)
                if movie_distance < (max_distance + 1):
                    movie_to_edit_distance[movie_and_year] = movie_distance

                    #new part 
                    if movie_distance < curr_distance:
                        curr_distance = movie_distance
                        list = []
                        list += [i]
                    elif movie_distance == curr_distance:
                        list += [i]
        return list


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
        recommendation_list = []
        #clar = self.preprocess(clarification)
        possible_list = self.extract_titles(clarification)
        #return re.findall(r'"([^"]*)"', clarification)
        clarification = clarification.lower()
        for i, movie_and_year in enumerate(self.titles):
            pattern = r'([^\(\)]+)\s*\(\d{4}\)'
            movie_matches = re.search(pattern, movie_and_year[0])
            if movie_matches:
                movie = movie_matches.group(1)
                movie = movie.lower()
                if movie in clarification:
                    for index in self.find_movies_by_title(movie_and_year[0]):
                        if index in candidates:
                            return [index]
                        #else:
                           #recommendation_list.append(i)
        for i,j in enumerate(candidates):
            i = i + 1
            for word in clarification.split():
                if str(i) == word:
                    return[j]
        string_1 = "recent"
        if string_1 in clarification:
            return [candidates[0]]
        if 'last' in clarification:
            return[candidates[len(candidates) - 1]]

        return recommendation_list
    

    def extract_sentiment_for_movies(self, preprocessed):
        return []


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
        binarized_ratings = np.where(ratings > threshold, 1, np.where((ratings > 0) & (ratings <= threshold), -1, 0))

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
        similarity = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
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

        np.seterr(invalid='ignore')

        top_k = k

        # how can i use numpy to apply an parallelized arbitrary operation between a vector of shape (n,) and a matrix of size (1,n), similar to matrix multiplication?
        
        n = user_ratings.shape[0]

        r_x = user_ratings[user_ratings != 0] # (k,)
        r_x_indices_all = np.column_stack((user_ratings, np.arange(n)))
        r_x_indices = r_x_indices_all[r_x_indices_all[:, 0] != 0][:, 1]

        k = r_x.shape[0]

        # compute similarities
        sim_matrix = np.zeros((k, n))
        for i, v1 in enumerate(ratings_matrix):
            for j, j_in_ratings in enumerate(r_x_indices):
                v2 = ratings_matrix[int(j_in_ratings)]
                sim_matrix[j][i] = self.similarity(v1, v2) # (k, n)

        new_ratings = np.matmul(sim_matrix.T, r_x) # (n, 1)

        # add column with indices
        ratings_and_indices_matrix = np.column_stack((new_ratings, np.arange(int(n))))

        # delete those in r_x
        zero_indices = (user_ratings == 0)
        ratings_and_indices_matrix = ratings_and_indices_matrix[zero_indices, :]

        # sort
        sorted_indices = np.argsort(-ratings_and_indices_matrix[:, 0])
        sorted_arr = ratings_and_indices_matrix[sorted_indices, :]

        # select top k elements and keep only indices
        recommendations = sorted_arr[:top_k][:, 1].astype(int).tolist()

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
        Welcome to the Chavo del Ocho Movie Chatbot! This is an engaging chatbot
        that can mainly help you find your next favorite movie recommendation!
        Just provide him with a few movies you've seen and tell him what you thought
        of them and magic will happen. Chavo is smart and can find movies even
        when you don't write them with the exact name. Exciting!
        
        But that's not all, Chavo can handle open ended conversation (you can tell
        him about your feelings) and many more! 
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
