# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re
import porter_stemmer
from collections import deque
import random

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        

        self.creative = creative
        self.name = 'Movie RECOMMENDER BOT'
        if self.creative:
            self.name = 'MarioMovieBot:)'
        
        

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.movies = np.array(util.load_titles('data/movies.txt'))[:, 0]
        

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings)
        #print(self.ratings.shape[0])
        
        # Variables need for the robot to keep track of information
        self.recommended_movies = deque()
        self.movies_rated, self.user_rates = [], []
        self.ASK_NEXT_MOVIE = "Tell me more about another movie you have watched."
        self.ASK_RECOM = "Would you like more recommendations :)"
        self.ALL_CCONFIRM = ["yeah", "yes", "ye", "yah", "yep", "yeah!", "yes!", "yep!", "ye!"]
        
        # For creative
        self.FLAG_MORE_MOVIES = False
        self.FLAG_line = ""
        self.FLAG_title = ""
        self.FLAG_indexes = []
        self.FLAG_CONFIRM_MOVIE = False
        self.FLAG_creative_title = False
        
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        ########################################################################
        # TODO: Write a short greeting message                                 #
        ########################################################################

        greeting_message = "Hello! Let's-a find you the best movie?"
        
        list_of_greetings = [ 
        "Hello, it's-a me, Mario! Let's-a find you the best movie! Yiiiiiipeee!",
        "Hello, it's-a me, Mario! Let's-a find you the best movie! Yahoohoohoo!",
        "Hello, it's-a me, Mario! It's Mario time! Let's find you a movie!",
        "Wahoo! It's-a me, Mario! Let's find you a movie! Here we go!",
        "Yahoohoohoo! It's-a me, Mario! Let's find you a movie! Let's-a go!"
        ]
        
        if self.creative:
            greeting_message = random.choice(list_of_greetings)
        
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

        goodbye_message = "Thank you so much for playing my game. Have a nice day!"
        
        
        list_of_greetings = [ 
            "Oh no, you're leaving! Goodbye, then and remeber Mario number one! Woo-hoo!",
            "Thank you so much for playing my game! We did it! Good job little guy/gal. Bye!",
            "So long, eh Bowser! Yes! I'm the winner! I hope you found a movie! Goodbye!",
            "Hui hew! Just what I needed! Okey-dokey! Bye-bye! Yeah, ha ha ha!",
            "Buh-bye! Thanks for playing! Get me out of here!"
        ]
        if self.creative:
            goodbye_message = random.choice(list_of_greetings)

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return goodbye_message

    
    def mario_asks_recommendations(self):
        """ 
        mario_asks_recommendations: This function will randomly select
        a sentence that will ask the User for another recommendation.
        E.X. - Would you like more recommendations?
        @return selected_sentence
        """
        if self.creative == False:
            return self.ASK_RECOM
        list_of_sentences = [
            "Here a-we go again! Would you like more movie recommendations?",
            "There's a MORE?!? Would you like more movie recommendations?",
            "Take-a this! Would you like more movie recommendations?",
            "Hey! Come back here! Would you like more movie recommendations?",
            "Let's get-a going! Would you like more movie recommendations?",
            "Looks like Mario's gonna have to find a job. Would you like more movie recommendations?"

        ]
        selected_sentence = random.choice(list_of_sentences)
        return selected_sentence
    
    def mario_asks_user_another_movie(self):
        """ 
        mario_asks_user_another_movie: This function will randomly select
        a sentence that will ask the User for another movies to be 
        entered. E.X. - Ask Next Movie - Tell me more movies you like
        @return selected_sentence
        """
        if self.creative == False:
            return self.ASK_NEXT_MOVIE
        list_of_sentences = [
            "Oh, come on! Tell me more movies you have watched.",
            "Oh, yeah! Hoho! Wahoo! Tell me more movies you have watched.",
            "Let's-a go! Rate a movie you have wacthed before.",
            "Let's-a go, little guys! Rate a movie you have watched.",
            "Hey! Come back here, you big-a monkey! Tell me more movies you like."
        ]
        selected_sentence = random.choice(list_of_sentences)
        return selected_sentence
    
    
    def mario_responds_to_user_likes_movies(self, movie):
        """ 
        mario_responds_to_user_likes_movies: This function will randomly 
        select a sentence that will acknowledge to the User that they like
        the movie they entered.
        E.X. - You like this movies
        @return selected_sentence
        """
        if self.creative == False:
            return "Ok! you like \"{}\"! ".format(movie)
        
        list_of_sentences = [
        "Mama Mia! Wahoo! I see you like \"{}\".".format(movie),
        "Yiiiiiipeee! I see you like \"{}\".".format(movie),
        "That's-a so nice! I see you like \"{}\".".format(movie),
        "Oh-ho, YEAH! I see you like \"{}\".".format(movie),
        "Yahoo! I see you like \"{}\".".format(movie)
        ]
        selected_sentence = random.choice(list_of_sentences)
        return selected_sentence
    
    def mario_responds_to_user_not_like_movies(self, movie):
        """ 
        mario_responds_to_user_not_like_movies: This function will 
        randomly select a sentence that will acknowledge to the User that they like
        they do not like the movie entered.
        E.X. - You do not like this movie.
        @return selected_sentence
        """
        if self.creative == False:
            return "Ok! you don't like \"{}\"! ".format(movie)
        list_of_sentences = [
            "Oh-ho, no! I see you did not like \"{}\".".format(movie),
            "Oh, come on! I see you did not like \"{}\".".format(movie),
            "Ouch-ouch-ouch! I see you did not like \"{}\".".format(movie),
            "I see you did not like \"{}\". Looks like it's time to go fishing again.".format(movie),
            "Mamma mia, the horror! I see you did not like \"{}\".".format(movie)
        ]
        selected_sentence = random.choice(list_of_sentences)
        return selected_sentence
    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################
    
    def clear_all_containers(self):
        self.recommended_movies = deque()
        self.movies_rated, self.user_rates = [], []
        self.clear_flags()

    def clear_flags(self):
        self.FLAG_MORE_MOVIES = False
        self.FLAG_line = ""
        self.FLAG_title = ""
        self.FLAG_indexes = []
        self.FLAG_CONFIRM_MOVIE = False
        self.FLAG_creative_title = False
    
    
    def comple_from_sentiment(self, sentiment, title, movie_index, can_print_rec = True):
        self.clear_flags()
        if (sentiment == 0):
            return "I'm sorry, I'm not sure if you liked \"{}\", tell me more about it.".format(self.movies[movie_index])
        if movie_index in self.movies_rated:
            idx = self.movies_rated.index(movie_index)
            if self.user_rates[idx] == sentiment:
                return "You already rated \"{}\"! ".format(title) + "{}".format(self.mario_asks_user_another_movie() if can_print_rec else "")
            else:
                self.user_rates[idx] = sentiment
                return "Ok! You have changed your opinion on \"{}\". ".format(self.movies[movie_index]) + "You{}like it now!".format(" " if sentiment == 1 else " don't ")
       
        self.movies_rated.append(movie_index)
        self.user_rates.append(sentiment)
        response = ""
        if sentiment == -1:
            response = self.mario_responds_to_user_not_like_movies(self.movies[movie_index])
        else:
            response = self.mario_responds_to_user_likes_movies(self.movies[movie_index])
        if len(self.movies_rated) >= 5 and can_print_rec:
            return self.recommend_first_movie(response)
        
        if can_print_rec:
            return response + self.mario_asks_user_another_movie()
        return response
    
    
    def recommend_first_movie(self, response):
        # Let's get the reccommmended first top movie
        user_ratings = np.zeros(self.ratings.shape[0])
        for index in range(len(self.movies_rated)):
            user_ratings[self.movies_rated[index]] = self.user_rates[index]
        recommendations = self.recommend(user_ratings, self.ratings)
        for movie_index_ in recommendations:
            self.recommended_movies.append(self.titles[movie_index_][0])
        top_movie = "\nGiven what you told me, I think you would like \"{}\". ".format(self.recommended_movies.popleft()) + self.mario_asks_recommendations()
        return response + top_movie
    
    def process_non_creative(self, line):
        titles_list = self.extract_titles(line)
        if len(titles_list) == 0 or len(titles_list) > 1:
            return "Please enter one movie at a time, and I would help you recommend movies :)"
        movies_index = self.find_movies_by_title(titles_list[0])
        if (len(movies_index) == 0):
            return "I've never heard of \"{}\", sorry...".format(titles_list[0]) + self.mario_asks_user_another_movie()
        elif len(movies_index) > 1:
            return "I found more than one movie called \"{}\". Please, can you be more specific about the movie title?".format(titles_list[0])
        return self.comple_from_sentiment(self.extract_sentiment(line), titles_list[0], movies_index[0])

    
    # Returns a string of all movies in a single string.
    def movies_options_str(self, movies_index):
        final = ""
        for i in range(len(movies_index)-1):
            idx = movies_index[i]
            final += self.movies[idx] + ", "
        return final + "or " + self.movies[movies_index[-1]]
    
        
    def process_creative(self, line):
        titles = self.extract_titles(line)
        if len(titles) == 0:
            return "I don't think I understand what you mean. "+ self.mario_asks_user_another_movie()
        if len(titles) == 1: #Taking care of only one movie title
            movies_extracted = self.find_movies_by_title(titles[0])
            if len(movies_extracted) == 0 or (self.FLAG_creative_title and len(movies_extracted) == 1): # Find the closest movie
                movies_extracted = self.find_movies_closest_to_title(titles[0])
                if len(movies_extracted) == 0:
                    return "I've never heard of \"{}\", sorry...".format(titles[0]) + self.mario_asks_user_another_movie()
                elif len(movies_extracted) == 1:
                    self.FLAG_line = line
                    self.FLAG_title = titles[0]
                    self.FLAG_indexes = movies_extracted
                    self.FLAG_CONFIRM_MOVIE = True
                    if self.FLAG_creative_title:
                        return "Are you referring to this movie, \"{}\"? ".format(self.movies[movies_extracted[0]])
                    return "Do you mean \"{}\"? ".format(self.movies[movies_extracted[0]])
            movie_index = movies_extracted[0]
            if len(movies_extracted) > 1:
                self.FLAG_line = line
                self.FLAG_MORE_MOVIES = True
                self.FLAG_title = titles[0]
                self.FLAG_indexes = movies_extracted
                return "Which one did you mean?\n" + self.movies_options_str(movies_extracted)
            return self.comple_from_sentiment(self.extract_sentiment(line), titles[0], movie_index)
        
        
        multiple_movies = self.extract_sentiment_for_movies(line)
        response = ""
        
        for m_s in multiple_movies:
            #print(m_s)
            movie, sentiment = m_s[0], m_s[1]
            movies_extracted = self.find_movies_by_title(movie)
            #print(movies_extracted)
            if len(movies_extracted) == 0 or len(movies_extracted) > 1:
                continue
            response += self.comple_from_sentiment(sentiment, movie, movies_extracted[0], False)
        if len(self.movies_rated) >= 5:
            return self.recommend_first_movie(response)
        return response + self.mario_asks_user_another_movie()
            
                       
                
            
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
            if self.FLAG_MORE_MOVIES:
                movies_idx = self.disambiguate(line, self.FLAG_indexes)
                if len(movies_idx) == 1:
                    return self.comple_from_sentiment(self.FLAG_line, self.FLAG_title, movies_idx[0])
                else:
                    self.clear_flags()
                    return "I don't think I understand you! Can you please re-write the name of the movie you've watched. Or, " + self.mario_asks_user_another_movie()
            elif self.FLAG_CONFIRM_MOVIE:
                if line.lower() in self.ALL_CCONFIRM:
                    return self.comple_from_sentiment(self.FLAG_line, self.FLAG_title, self.FLAG_indexes[0])
                else:
                    self.clear_flags()
                    return "Ok! Can you please re-write the name of the movie you've watched. Or, " + self.mario_asks_user_another_movie()
            elif len(self.movies_rated) >= 5:
                if line.lower() in self.ALL_CCONFIRM:
                    return "I would also recommend \"{}\". ".format(self.recommended_movies.popleft()) + self.mario_asks_recommendations()
                else:
                    self.clear_all_containers()
                    return "Ok no problem! Let's restart with the movies you have watched :)"
            response = self.process_creative(line)
        else:
            if len(self.movies_rated) >= 5:
                if line.lower() in self.ALL_CCONFIRM:
                    return "I would also recommend \"{}\". ".format(self.recommended_movies.popleft()) + self.mario_asks_recommendations()
                else:
                    self.clear_all_containers()
                    return "Ok no problem! Let's restart with the movies you have watched :)"
            response = self.process_non_creative(line)

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
        pattern = '"([^"]*)"'
        matches = re.findall(pattern, preprocessed_input)
        if len(matches) == 0 and self.creative:
            match = []
            result_string = ""
            largest_match = 0
            smallest_title = 10000 #arbitrarily large number assumed to be longer than any movie title character length

            # create a list of strings of each individual word in the input
            set1 = re.split("\,\s*|\s|[\!\?\:]", preprocessed_input.lower())

            for title in self.titles:
                # create an analogous list using for the title
                set2 = re.split("\,\s*|\s|[\!\?\:]", title[0].lower())
                # find the insectiion of the two lists
                set3 = [value for value in set1 if value in set2]

                # if there is any intersection (otherwise not worth checking - return empty string if never hit)
                if (len(set3) > 0):
                    check = 0
                    for string in set3:
                        check += len(string)
                    # if the number of intersecting characters is greater than for any previosuly encountered title
                    if (check > largest_match):
                        largest_match = check
                        result_string = title[0]
                    # if there is a tile with just as many intresecting strings, but that is shorter
                    if check == largest_match and len(title[0]) < smallest_title:
                        smallest_title = len(title[0])
                        result_string = title[0]
            # if the input is entered with a date
            if len((re.findall("\([0-9]{4}\)", preprocessed_input))) > 0:
                # include the date in the return string
                match.append(result_string)
            else:
                # otherwise truncate it
                match.append(re.split("\s\([0-9]{4}\)",result_string)[0])
            self.FLAG_creative_title = True
            return match
        
        return matches
        

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
        indexes = []
        movies = np.array(util.load_titles('data/movies.txt'))[:, 0]
        title_words = re.split('\s|,\s', title)

        if self.creative:
            ## Identifying movies without quotation marks and correct capitalization (part 2) ##
            # convert title to all lowercase and split into a list to ease search
            title = title.lower()
            title_words = re.split('\s|,\s|[^a-z0-9\']', title)
            title_words = [x for x in title_words if x != '']
            foreign_articles = [#French:
                                "l'", "le", "la", "les", "un", "une",
                                #Spanish:
                                "el", "la", "las", "lo", "los", "una",
                                 #German (excluded "die" b/c it's a common english word):
                                 "das", "dem", "der", "des", "ein", "eine", "einem", "einen", "enier", "eines", "'s",
                                 #Italian (excluded "i" for same reason as above): 
                                 "'gl", "gli", "il", "'o", "un'",
                                 #English:
                                 "the", "an", "a"]
            ## Alternate/foreign titles handling ##
            # if foreign (or common english) article at beginning of input, remove the article to ease search
            if title_words[0] in foreign_articles:
                idx = len(title_words[0])
                del title_words[0]
                title = title[(idx + 1):]

            for i in range(movies.shape[0]):
                # narrow down search by looking for title as a substring in each movie
                if title in movies[i].lower():
                    ## Disambiguation (part 1) ##
                    # check that exact words in the input title are found *consecutively* in the curr movie title
                    curr_movie_words = re.split('\s|,\s|[^a-z0-9\']', movies[i].lower())
                    curr_movie_words = [x for x in curr_movie_words if x != '']
                    if title_words[0] in curr_movie_words:
                        first_match_idx = curr_movie_words.index(title_words[0])
                        for j in range(len(title_words)):
                            if curr_movie_words[first_match_idx] == title_words[j]:
                                first_match_idx += 1
                                if j == len(title_words) - 1:
                                    indexes.append(i)
                            else:
                                break

            return indexes
        
        ### STARTER-MODE CODE ###
        for i in range(movies.shape[0]):
            curr_title_words = re.split('\s|,\s', movies[i])
            if curr_title_words[-1] == title_words[-1] and all(word in curr_title_words for word in title_words) and (len(title_words) == len(curr_title_words)):
                indexes.append(i)
            elif all(word in curr_title_words[:-1] for word in title_words) and (len(title_words) == len(curr_title_words[:-1])):
                indexes.append(i)


        

        return indexes

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
        
        stemd_sentiment = {}
        p = porter_stemmer.PorterStemmer()
        for word, sentiment in self.sentiment.items():
            w = p.stem(word, 0, len(word) - 1)
            stemd_sentiment[w] = sentiment
        
        final = ""
        open_ = False
        for c in preprocessed_input:
            if c == '"' and open_ == False:
                open_ = True
            elif c == '"' and open_ == True:
                open_ = False
            elif open_ == False:
                final+=c
        negative_words = ["don't", "didn't", "not", "never"]
        c_neg = 0
        c_pos = 0
        list_words = re.split('\s|,\s', final)
        for word in list_words:
            w = word.lower()
            stemed = p.stem(w, 0, len(w) - 1)
            #print(w, stemed)
            if w in negative_words or stemed in negative_words:
                c_neg+=1
            elif w in stemd_sentiment:
                if stemd_sentiment[w] == 'neg':
                    c_neg += 1
                else:
                    c_pos +=1
            elif stemed in stemd_sentiment:
                if stemd_sentiment[stemed] == 'neg' :
                    c_neg += 1
                else:
                    c_pos +=1
        
        
        if (c_neg >= c_pos) and (c_neg  != 0 or c_pos != 0):
            return -1
        if abs(c_neg - c_pos) == 0:
            return 0
        #print(c_neg, c_pos)
        return 1 #c_pos > c_neg

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
        # Credits given to the conceptual understanding of this function. Thank you, Angela Zhao :)
        movies_to_process = self.extract_titles(preprocessed_input)
        if not movies_to_process:
            return []
        if len(movies_to_process) == 1:
            return [ (movies_to_process[0], self.extract_sentiment(preprocessed_input)) ]
        

        # search for negators in the input string
        negators = ["not", "didn't", "but", "yet", "nevertheless", "neither", "nor", "or"
                    "however", "nonetheless", "except", "don't"]
        words_in_input = re.split(r'"[^"]*"|\s+|,\s+', preprocessed_input)
        words_in_input = [x for x in words_in_input if x != '']
        negations_in_input = [x for x in words_in_input if(x in negators)]

        split_found = False
        sentiment_for_movies = []
        
        if negations_in_input:
            first_movie_idx = preprocessed_input.index(movies_to_process[0])

            # search for appropriate spot to split the input string to determine sentiment of each half...
            # Example 1: if input is " I liked "X" but not "Y" or "Z" ", split the string at "but"...
            # Example 2: if input is " I didn't like "X" but I did like "Y" and "Z" ", still split at "but"...
            for neg_word in negations_in_input:
                neg_idx = preprocessed_input.index(neg_word)
                # print("NEG_IDX = ", neg_idx, "FIRST_MOVIE_IDX = ", first_movie_idx)
                if neg_idx > first_movie_idx:
                    before_negation = preprocessed_input[:neg_idx]
                    split_found = True
                    break

            if split_found:
                # Example 1: " I didn't like "X" but I did like "Y" and "Z" " -- split at "but"; sentiment = -1 for first half, 1 for second half
                # Example 2: " I liked "X" yet not "Y" " -- split at "yet"; sntmt=1 for first half, -1 for second half
                initial_sntmt = self.extract_sentiment(before_negation)
                movies_before_negation = [movie for movie in movies_to_process if(movie in before_negation)]
                for movie in movies_to_process:
                    if movie in movies_before_negation:
                        sentiment_for_movies.append( (movie, initial_sntmt) )
                    else:
                        sentiment_for_movies.append( (movie, -initial_sntmt) )
                
        if not split_found: 
            # no appropriate negations detected so likely to be the same sentiment for all movies mentioned in the input
            sentiment = self.extract_sentiment(preprocessed_input)
            for movie in movies_to_process:
                sentiment_for_movies.append( (movie, sentiment) )
        return sentiment_for_movies

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
        title_no_date = self.remove_date(title)
        distances = np.array([self.min_edit_distance(title_no_date, self.remove_date(movie)) for movie in self.movies])
        indexes = np.argsort(distances)
        final = []
        tie = (distances[indexes[0]] == distances[indexes[1]]) & (distances[indexes[0]] <=3)
        for i in indexes:
            if tie == True and distances[indexes[0]] == distances[i]:
                final.append(i)
            elif tie == True and distances[indexes[0]] != distances[i]:
                return final
            elif distances[i] > 3:
                break
            else:
                final.append(i)
        return final#list(np.where(distances <= max_distance)[0])

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
        indexes = []
        set_clar = set(re.split('\s|\s|: |\(|\)|\.', clarification))
        for candidate in candidates:
            set_cand = set(re.split('\s|\s|: |\(|\)|\.', self.movies[candidate]))
            if (set_clar & set_cand) == set_clar:
                indexes.append(candidate)
        return indexes
            
    def remove_date(self, x, char1 = "(", char2 = ")"):
        x = x.lower()
        stop_words = ["a", "the", "the,", "a,"]
        list_words = re.split('\s', x)
        no_stop_words = ""
        for w in list_words:
            if not w in stop_words:
                no_stop_words += w
        x = no_stop_words
        final = ""
        p = ""
        open_ = False
        for i, c in enumerate(x):
            if c == char1 and open_ == False:
                open_ = True
                p = ""
            elif c == char2 and open_ == True:
                open_ = False
                if not p.isnumeric():
                    final += char1 + p + char2
                    p = ""
            elif open_ == False and c != " ":
                final+=c
            elif open_ == True:
                p +=c
        return final
    
    def min_edit_distance(self, source, target):
        n = len(source)
        m = len(target)
        # Create a distance matrix
        D = [[0 for i in range(m + 1)] for j in range(n + 1)]

        # Initialising first row and first column
        for i in range(n + 1):
            D[i][0] = i
        for j in range(m + 1):
            D[0][j] = j
        
        # Recurrence relation:
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                if source[i - 1] == target[j - 1]:
                    D[i][j] = D[i - 1][j - 1]
                else:
                    insertion = 1 + D[i][j - 1]
                    deletion = 1 + D[i - 1][j]
                    replacement = 2 + D[i - 1][j - 1]
                    # Choosing the best option:
                    D[i][j] = min(insertion, deletion, replacement)
        return D[n][m]
    
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
        binarized_neg = np.where((ratings <= threshold) & (ratings != 0), -1, ratings)
        binarized_ratings = np.where(binarized_neg > threshold, 1, binarized_neg)
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
        similarity = 0
        denom1 = np.sqrt(np.sum(u**2))
        denom2 = np.sqrt(np.sum(v**2))
        if denom1 == 0 or denom2 == 0:
            return 0
    
        similarity = np.dot(u/denom1, v/denom2)
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

        # Populate this list with k movie indices to recommend to the user.
        recommendations = []
        
        user_neg_rated = np.where(user_ratings == -1)[0]
        user_pos_rated = np.where(user_ratings == 1)[0]
        user_all_rated = np.append(user_neg_rated, user_pos_rated)
        
        all_r_ij = np.zeros(user_ratings.shape[0])
        for i in range(ratings_matrix.shape[0]):
            r_i = 0
            if i in user_all_rated:
                continue
            else:
                movie_i = ratings_matrix[i]
                for j in user_all_rated:
                    if user_ratings[j] == 0:
                        print("Error! User rating should never be equals to 0!")
                    r_i += self.similarity(movie_i, ratings_matrix[j]) * user_ratings[j]
                
                all_r_ij[i] = r_i
        movies_indexes = np.argsort(all_r_ij)[::-1]
        count = 0
        for movie in movies_indexes:
            if movie in user_all_rated:
                continue
            else:
                recommendations.append(movie)
                count += 1
                if count == k:
                    break
            
    
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
        if self.creative:
            return """
            "Yahooo! It's-a me, Mario, and I'm in creative mode, woo hoo! 
            I'm your movie recommending chat bot, and I'm ready to help you 
            find some-a great movies! Just give me your opinion, no matter how-a strong,
            on 5 movies, and I'll-a find you one that I think you'll love! And don't-a 
            worry, you can keep adding your preferences, more than one at a time too,
            and I'll keep making recommendations based on previous entries! Movie titles
            can be with or without-a quotation marks, and you don't-a need to worry about
            your poor spelling abilities, hahaha! 
            Let's-a gooooo!"
            """
        return """
        Hello! Welcome to the movie recommender bot. I am here to help you find new movies 
        you will enjoy. Please provide your option of 5 movies, one at a time, with movie 
        titles in quotations and I will provide a recommendation. If you wish to continue, 
        your subsequent entries will accumulate on the previous or start fresh otherwise. 
        Enjoy!
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
