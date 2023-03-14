# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import porter_stemmer

import numpy as np
import re

import sys
import subprocess
try: 
    from nltk.stem.porter import *
    #from nltk.tokenize import word_tokenize
except:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'nltk'])
    from nltk.stem.porter import *
    #from nltk.tokenize import word_tokenize

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 7."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        self.name = 'MovieRecommenderBot'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = Chatbot.binarize(ratings)

        #self.stemmer = porter_stemmer.PorterStemmer()
        self.stemmer = PorterStemmer()

        #stem the entire dictionary
        
        new_sentiment = {}
        for key in self.sentiment.keys():
            new_key = self.stemmer.stem(key)
            new_sentiment[new_key] = self.sentiment[key]
        self.sentiment = new_sentiment
        
        
        self.movie_list = [] 
        self.opin = 0
        self.fine_grained = util.load_sentiment_dictionary('deps/fine_grained.txt')

        self.user_ratings = np.zeros((9125))
        self.numrated = 0

        self.recs = []
        self.num_of_recs_given = 0
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        ########################################################################
        # DONE: Write a short greeting message                                 #
        ########################################################################

        greeting_message = "How may I assist you today?"

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
        
        response = ''
        # initial processing
        preprocessed = self.preprocess(line)
#        print(preprocessed)
        title_list = self.extract_titles(preprocessed)
        # print(title_list)
        movies = []
        for title in title_list:
            if len(title_list) > 1:
                movie = self.find_movies_by_title(title)
                # print(movie)
                movies.append(movie)
            else:
                movies = self.find_movies_by_title(title)
        # print(movies)
        opinion = self.extract_sentiment(preprocessed)
#        print(opinion)

        if preprocessed.count('"') > 2:
            # print(preprocessed)
            list_of_tuples = self.extract_sentiment_for_movies(preprocessed)
            # print(list_of_tuples)
            response = "Oh, ok. So you "
            for i in range(len(list_of_tuples)):
                tup = list_of_tuples[i]
                if tup[1] >= 0:
                    response = response + "liked " + tup[0]
                else:
                    response = response + "didn't like " + tup[0]
                if i != len(list_of_tuples)-1:
                    response = response + " and "
                else:
                    response = response + "."
            return response

        # disambiguate (after given clarification)
        if len(self.movie_list) >0:
            # print(self.movie_list)
            # print(preprocessed)
            narrowed_down = self.disambiguate(preprocessed, self.movie_list)
            # need to disambiguate again
            if len(narrowed_down) > 1:
                self.movie_list = narrowed_down
                response = "Meow! Which movie did you mean? Please share without quotation marks. "
                for i in range(len(narrowed_down)):
                    if i == len(narrowed_down):
                        response += '%s. ' %self.titles[narrowed_down[i]][0]
                    response += '%s, ' %self.titles[narrowed_down[i]][0]
            # we have our answer
            else:
                movies = narrowed_down
                opinion = self.opin
                # print(movies)
                # self.movie_list = []
                # self.opin = 0

        # print(movies)
        # print(self.movie_list)
        #first time there's multiple movies
        if len(movies) > 1 and len(self.movie_list) == 0:
            self.movie_list = movies
            self.opin = opinion
            
            response = "Meow! Which movie did you mean? Please share without quotation marks. "
            for i in range(len(movies)):
                if i == len(movies):
                        response += '%s. ' %self.titles[movies[i]][0]
                response += '%s, ' %self.titles[movies[i]][0]

            return response

        # print("line 142 :", movies)
        if len(movies)>0:
            movie = movies[0]
        # print(self.titles[movies[0]])
        emotion_neg_words = ['Upset', 'Sad', 'Angry', 'Tired', 'Frustrated', 'Lonely', 'Nervous', 'Hurt', 'Confused', 'Overwhelmed', 'Insecure', 'Jealous', 'Worried', 'Disappointed', 'Hopeless', 'Miserable', 'Enraged', 'Fearful']
        emotion_pos_words = ['Happy',  'Excited', 'Hopeful', 'Proud', 'Glad', 'Loved', 'Surprised', 'Calm', 'Relaxed', 'Grateful', 'Appreciated', 'Determined', 'Empowered']


        # doing the opinions to give final confirmation
        if len(self.recs) == 0:

            if len(movies) == 1: 
                self.user_ratings[movie] = opinion
                self.numrated+=1

            if(self.numrated >= 5):
                self.recs = self.recommend(self.user_ratings,self.ratings,5)

            if opinion == 1 and response == '' and len(self.movie_list) != 1 and len(movies) != 0:
                # print(movie)
                response = "So you like %s. Please share another movie. Meow!" % self.titles[movie][0]
                if self.numrated == 5:
                    response = "So you like %s. " % self.titles[movie][0]
                    response = response + "My suggestion for a movie you might like is %s. Would you like another recommendation? Meow!" %self.titles[self.recs[self.num_of_recs_given]][0]
                    self.num_of_recs_given += 1
            elif opinion == -1 and response == '' and len(self.movie_list) != 1 and len(movies) != 0:
                response = "So you didn't like %s. Please share another movie. Meow!" % self.titles[movie][0]
                if self.numrated == 5:
                    response = "So you didn't like %s. " % self.titles[movie][0]
                    response = response + "My suggestion for a movie you might like is %s. Would you like another recommendation? Meow!" %self.titles[self.recs[self.num_of_recs_given]][0]
                    self.num_of_recs_given += 1
            elif len(movies) == 0 and response == '' and len(self.movie_list) != 1:
                for word in emotion_neg_words:
                    word = word.lower()
                    if word in preprocessed:
                        response = "Oh! Did I make you %s? I'm sorry! Meow!" %word
                for word in emotion_pos_words:
                    word = word.lower()
                    if word in preprocessed:
                        response = "Oh! I made you %s? I'm glad! Meow!" %word
                if 'Can you' in preprocessed:
                    response = "I'm sorry, I can't %s. I am a movie-recommendation bot. Meow!" % preprocessed[preprocessed.rindex('Can you')+7:]
                elif 'What is' in preprocessed:
                    response = "I'm sorry, I don't know the answer to %s. I am a movie-recommendation bot. Meow!" % preprocessed
                elif response == '':
                    response = "Sorry, I don't think this is a movie. Let's chat about movies. Meow!"
            elif opinion == 0 and response == '' and len(self.movie_list) != 1 and len(movies) != 0:
                response = "I'm sorry, I'm not sure if you liked %s. Please tell me more about it. Meow!" % self.titles[movie][0]
            # print('length:', len(self.movie_list))
            if opinion == 2 and response == '' and len(self.movie_list) != 1 and len(movies) != 0:
                response = "So you love %s. Please share another movie. Meow!" % self.titles[movie][0]
                if self.numrated == 5:
                    response = "So you love %s. " % self.titles[movie][0]
                    response = response + "My suggestion for a movie you might like is %s. Would you like another recommendation? Meow!" %self.titles[self.recs[self.num_of_recs_given]][0]
                    self.num_of_recs_given += 1
            elif opinion == -2 and response == '' and len(self.movie_list) != 1 and len(movies) != 0:
                response = "So you hate %s. Please share another movie. Meow!" % self.titles[movie][0]
                if self.numrated == 5:
                    response = "So you hate %s. " % self.titles[movie][0]
                    response = response + "My suggestion for a movie you might like is %s. Would you like another recommendation? Meow!" %self.titles[self.recs[self.num_of_recs_given]][0]
                    self.num_of_recs_given += 1
            # zeroing out the record keeping because we have our movie
            if len(movies) == 1: #means we have our final movie
                self.opin = 0
                self.movie_list = []


            # if len(movies) == 1: 
            #     self.user_ratings[movie] = opinion
            #     self.numrated+=1

            # if(self.numrated >= 5):
            #     self.recs = self.recommend(self.user_ratings,self.ratings,5)

        elif len(self.recs) != 0:
            if "no" in preprocessed:
                response = "I hope you enjoy your movie! Meow!"
            elif "yes" in preprocessed:
                response = "My suggestion for a movie you might like is %s. Would you like another recommendation? Meow!" %self.titles[self.recs[self.num_of_recs_given]][0]
                self.num_of_recs_given += 1
            else:
                response = "Would you like another movie recommendation? Meow!"


        # user_ratings = np.zeros((9125))
        # user_ratings[8514] = 1
        # user_ratings[7953] = 1
        # user_ratings[6979] = 1
        # user_ratings[7890] = 1
        # user_ratings[7369] = -1
        # user_ratings[8726] = -1
        # print(self.recommend(user_ratings, self.ratings, 5))
        

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return response

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
        for i in range(len(text)):
            if text[i-1] == '"':
                text[i].upper()
            if text[i-1] != '"':
                text[i].lower()
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
        res = []

        on = False
        onIndex = -1
        i = 0
        while(i < len(preprocessed_input)):
            if(preprocessed_input[i]=="\""):
                #start of potential title
                if(not on):
                    onIndex = i+1
                    on = True
                #end of potential title
                else:
                    res.append(preprocessed_input[onIndex:i])
                    on = False
                
            i+=1
        return res

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

        res = []
        year_format = r' \([0-9]{4}\)'
        # print("Title ", title)
        for i in range(len(self.titles)):
            curr = self.titles[i][0]
            # print(curr)
            curr_article_front = curr
            """if (curr.find(", The ") == len(curr) - 12):
                curr_article_front = "The " + curr[:-12] + " " + curr[-6:]
            elif(curr.find(", An ") == len(curr) - 11):
                curr_article_front = "An " + curr[:-11] + " " + curr[-6:]
            elif(curr.find(", A ") == len(curr) - 10):
                curr_article_front = "A " + curr[:-10] + " " + curr[-6:]"""
            if (len(curr) >= 12 and curr.find(", The ") == len(curr) - 12):
                curr_article_front = "The " + curr[:-12] + " " + curr[-6:]
            elif(len(curr) >= 11 and curr.find(", An ") == len(curr) - 11):
                curr_article_front = "An " + curr[:-11] + " " + curr[-6:]
            elif(len(curr) >= 10 and curr.find(", A ") == len(curr) - 10):
                curr_article_front = "A " + curr[:-10] + " " + curr[-6:]
            
            curr_no_year = curr
            curr_article_front_no_year = curr_article_front
            if(re.search(year_format,curr)):
                curr_no_year = curr[:re.search(year_format,curr).start()]
            if(re.search(year_format,curr_article_front)):
                curr_article_front_no_year = curr_article_front[:re.search(year_format,curr_article_front).start()]
            """
            print("curr: ", curr)
            print("curr_article_front: ", curr_article_front)
            print("curr_no_year: ", curr_no_year)
            print("curr_article_front_no_year: ", curr_article_front_no_year)
            """
            # print("curr", curr)
            if (not self.creative):
                if title==curr or title==curr_article_front or title==curr_no_year or title==curr_article_front_no_year:
                    res.append(i) 
            else:
                if title in curr or title in curr_article_front or title in curr_no_year or title in curr_article_front_no_year:
                    pluraltitle = title+"s"
                    ingtitle = title+"ing"
                    erstitle = title+'ers'
                    if pluraltitle not in curr and pluraltitle not in curr_article_front and pluraltitle not in curr_no_year and pluraltitle not in curr_article_front_no_year:
                        if ingtitle not in curr and ingtitle not in curr_article_front and ingtitle not in curr_no_year and ingtitle not in curr_article_front_no_year:
                            if erstitle not in curr and erstitle not in curr_article_front and erstitle not in curr_no_year and erstitle not in curr_article_front_no_year:
                                res.append(i) 
        # print("Return of find movies by title", res)
        return res

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

        if self.creative == False:
            #get rid of movie titles
            on = False
            onIndex = -1
            i = 0
            while(i < len(preprocessed_input)):
                if on and preprocessed_input[i]!= "\"":
                    preprocessed_input = preprocessed_input[:i] + "x" + preprocessed_input[i+1:]

                if(preprocessed_input[i]=="\""):
                    #start of potential title
                    if(not on):
                        onIndex = i+1
                        on = True
                    #end of potential title
                    else:
                        on = False          
                i+=1

            negators = ["don't", "not","isn't","wasn't","weren't","ain't","aint","isnt","wasnt","werent","didn't","never"]
            negation_words = ['no', 'not', 'never', 'none', 'nobody', 'nothing', 'neither', 'nor', 'without', 'cannot', 'won\'t', 'don\'t', 'didn\'t', 'isn\'t', 'aren\'t', 'wasn\'t', 'weren\'t', 'haven\'t', 'hasn\'t', 'hadn\'t', 'shouldn\'t', 'wouldn\'t', 'couldn\'t', 'mightn\'t', 'needn\'t', 'rarely', 'scarcely', 'seldom', 'hardly', 'barely', 'refuse']

            negators = negators + negation_words
            
            tokens = preprocessed_input.split()

            #replace punctuations
            punctuation = '''!()-[]{};:"\, <>./?@#$%^&*_~''' #removed ' as a token
            for i in range(len(tokens)):
                for x in punctuation:
                    tokens[i] = tokens[i].replace(x,"")
                    tokens[i] = self.stemmer.stem(tokens[i])
            
            """
            tokens = word_tokenize(preprocessed_input)
            for i in range(len(tokens)):
                tokens[i] = self.stemmer.stem(tokens[i])
                """
            res = 0


            #calculate sentiment
            for i in range(len(tokens)):
                curr = tokens[i]
                shift = 0
                if(curr in self.sentiment.keys()):
                    shift = 1 if self.sentiment[curr]=="pos" else -1
                
                #check prev word for negation
                if(i >= 1 and tokens[i-1] in negators and tokens[i-1] not in self.sentiment.keys()):
                    shift *= -1

                #check 2 words back for negation
                if(i >= 2 and tokens[i-2] in negators and tokens[i-2] not in self.sentiment.keys()):
                    shift *= -1

                #check 3 words back for negation
                if(i >= 3 and tokens[i-3] in negators and tokens[i-3] not in self.sentiment.keys()):
                    shift *= -1

                # print("Word: ", curr, ", Shift: ", shift)
                res += shift
            return np.sign(res)
        if self.creative == True:
            sentiment = 0
            negation_words = ['no', 'not', 'never', 'none', 'nobody', 'nothing', 'neither', 'nor', 'without', 'cannot', 'won\'t', 'don\'t', 'didn\'t', 'isn\'t', 'aren\'t', 'wasn\'t', 'weren\'t', 'haven\'t', 'hasn\'t', 'hadn\'t', 'shouldn\'t', 'wouldn\'t', 'couldn\'t', 'mightn\'t', 'needn\'t', 'rarely', 'scarcely', 'seldom', 'hardly', 'barely', 'refuse']
            intensification = ['really', 'somewhat']

            preprocessed_input = preprocessed_input.split(' ')

            for word in preprocessed_input:
                if word in self.fine_grained:
                    sentiment += int(self.fine_grained[word])
                if word[:-1] in self.fine_grained:
                    sentiment += int(self.fine_grained[word[:-1]])

            for elem in negation_words:
                if elem in preprocessed_input:
                    sentiment = sentiment * -1

            if 'really' in preprocessed_input:
                sentiment = sentiment * 2

            if 'somewhat' in preprocessed_input:
                sentiment = sentiment / 2
            # print(sentiment)
            if sentiment == 0:
                return 0
            if sentiment <= 1 and sentiment > 0:
                return 1
            if sentiment >= -1 and sentiment < 0:
                return -1
            if sentiment > 1:
                return 2
            if sentiment < -1:
                return -2
#

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
        sentiments = []


        p = preprocessed_input


        first_half  = p[:len(p)//2]
        second_half = p[len(p)//2:]

        sent_val_1 = self.extract_sentiment(first_half)

        sent_val_2 = self.extract_sentiment(second_half)

        movie_list_1 = self.extract_titles(first_half)

        movie_list_2 = self.extract_titles(second_half)

        for i in range(len(movie_list_1)):
            sentiments.append((movie_list_1[i], sent_val_1))

        for i in range(len(movie_list_2)):
            sentiments.append((movie_list_2[i], sent_val_2))

        return sentiments

    def get_distance(self, title1, title2):
        dp = np.zeros((len(title1) + 1, len(title2) + 1))
        for i in range(len(title1) + 1):
            dp[i][0] = i
        for j in range(len(title2) + 1):
            dp[0][j] = j
        
        for i in range(1, len(title1) + 1):
            for j in range(1, len(title2) + 1):
                insertion1 = dp[i - 1][j] + 1
                insertion2 = dp[i][j - 1] + 1
                substitution = dp[i - 1][j - 1] if title1[i - 1] == title2[j - 1] else dp[i - 1][j - 1] + 2
                dp[i][j] = min(insertion1, insertion2, substitution)
        return dp[-1][-1]

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

        res = []
        year_format = r' \([0-9]{4}\)'        
        distances = np.zeros((len(self.titles))) + 1000000
        mindist = 1000000
        title = title.lower()

        for i in range(len(self.titles)):
            curr = self.titles[i][0]
            curr = curr.lower()
            curr_article_front = curr
            if (len(curr) >= 12 and curr.find(", The ") == len(curr) - 12):
                curr_article_front = "The " + curr[:-12] + " " + curr[-6:]
            elif(len(curr) >= 11 and curr.find(", An ") == len(curr) - 11):
                curr_article_front = "An " + curr[:-11] + " " + curr[-6:]
            elif(len(curr) >= 10 and curr.find(", A ") == len(curr) - 10):
                curr_article_front = "A " + curr[:-10] + " " + curr[-6:] 
            
            curr_no_year = curr
            curr_article_front_no_year = curr_article_front
            if(re.search(year_format,curr)):
                curr_no_year = curr[:re.search(year_format,curr).start()]
            if(re.search(year_format,curr_article_front)):
                curr_article_front_no_year = curr_article_front[:re.search(year_format,curr_article_front).start()]
            """
            
            print("curr: ", curr)
            print("curr_article_front: ", curr_article_front)
            print("curr_no_year: ", curr_no_year)
            print("curr_article_front_no_year: ", curr_article_front_no_year)
            """
            dist = min(self.get_distance(title, curr), self.get_distance(title, curr_article_front), self.get_distance(title, curr_no_year), self.get_distance(title, curr_article_front_no_year))
            if dist <= max_distance:
                distances[i] = dist
            if dist < mindist:
                mindist = dist

        inv_dists = np.argsort(distances)

        #nothing to return
        if distances[inv_dists[0]] > mindist:
            return []
        for i in range(len(distances)):
            if(distances[inv_dists[i]] > mindist):
                return inv_dists[:i] 

        

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
        ls = []
        for i in range(len(candidates)):
            # print(candidates)
            # print(self.titles[candidates[i]][0])
            # print(clarification)
            if clarification[-1] == '.':
                clarification = clarification[:-1]
            if len(clarification) == 4 and clarification in self.titles[candidates[i]][0]:
                # print(self.titles[candidates[i]][0][:-6])
                # print('made it here')
                ls.append(candidates[i])
                return ls
            elif clarification in self.titles[candidates[i]][0][:-6]:
                # print(self.titles[candidates[i]][0])
                # print('made it here')
                ls.append(candidates[i])
        return ls

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
        binarized_ratings = np.zeros_like(ratings)

        for i in range(ratings.shape[0]):
            for j in range(ratings.shape[1]):
                if ratings[i][j] == 0:
                    continue
                if ratings[i][j] > threshold:
                    binarized_ratings[i][j] = 1
                    continue
                binarized_ratings[i][j] = -1

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
        nu = np.linalg.norm(u)
        nv = np.linalg.norm(v)

        #calculation: return normalised u dot product with normalised v
        #casework: avoid divide-by-zero errors for the norms
        if(nu!=0 and nv!=0):
            return np.dot(u/nu,v/nv)
        elif nu!=0 and nv==0:
            return np.dot(u/nu,v)
        elif nu==0 and nv!=0:
            return np.dot(u,v/nv)
        else:
            return np.dot(u,v)
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################

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

        # Populate this list with k movie indices to recommend to the user.

        recommendations = []

        num_users = ratings_matrix.shape[1]
        num_movies = ratings_matrix.shape[0]

        similarities = np.zeros((num_movies,num_movies))

        for i in range(num_movies): #go thru user ratings for each movie
            if user_ratings[i] == 0: #skip over user-unrated movies
                continue
            for j in range(num_movies): #compute similarity between user-rated movie and every other movie
                #skip over rated movies: want similarities between rated and unrated movies
                if(user_ratings[j]!=0):
                    continue
                
                temp = self.similarity(ratings_matrix[i],ratings_matrix[j])
                similarities[i][j] = temp
                similarities[j][i] = temp
        
        ratings = np.zeros((num_movies)) - 1000000
        for i in range(num_movies):
            if user_ratings[i] != 0:
                continue
            ratings[i] = np.dot(user_ratings, similarities[i])
        #argsort ratings by values, return indices
        return np.argsort(ratings)[-1:-k-1:-1]
        #return np.argsort(ratings)[-1:-15:-1]


        ##########
        """
        recommendations = []

        num_users = ratings_matrix.shape[1]
        num_items = ratings_matrix.shape[0]

        similarities = np.zeros((num_items, num_items))
        for i in range(num_items):
            for j in range(num_items):
                similarities[i][j] = self.similarity(ratings_matrix[i], ratings_matrix[j])

        
        ratings = np.zeros((num_items)) - 100000
        for i in range(num_items):
            if user_ratings[i] != 0:
                continue
            ratings[i] = np.dot(user_ratings, similarities[i])
        
        #argsort ratings by values, return indices
        return np.argsort(ratings)[:k]
        """
        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        #return recommendations

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
        I am a movie chatbot. I gather top intel on the movies and tell you all about it. You can chat with me, and based on your previous tastes, I'll recommend new movies for you to watch. Tell me about your tastes, and I'll listen. Based on our chat, I'll generate some recommendations. I'll try to be friendly.
        """
        """
        # Your task is to implement the chatbot as detailed in the PA7
        # instructions.
        # Remember: in the starter mode, movie names will come in quotation marks
        # and expressions of sentiment will be simple!
        # TODO: Write here the description for your own chatbot!
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
