# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import re
import numpy as np
from porter_stemmer import PorterStemmer


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=True):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'MeganTheeStallion'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.ratings = self.binarize(ratings)
        self.user_ratings = np.zeros(np.shape(self.ratings)[0])
        self.counter = 0
        self.recommedations_so_far = 0
        self.movie_correction_idx = []
        self.pending_sentiment = 0 
        self.spellcheck = False
        self.no_quotes = False
        self.pending_movie_options = False
        self.pending_movies_indices = []
        self.ignore_words = {}
        self.pending_movie = ""
    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        ########################################################################
        # TODO: Write a short greeting message                                 #
        ########################################################################

        if self.creative is True:
            greeting_message = "Hey Hotties. We about to be on some hot girl stuff today. Imma tell you which movies are popping off but tell me which ones you f with first."

        else:
            greeting_message = "Hi! I'm MovieBot! I'm going to recommend a movie to you. To do this, tell me about a movie that you have seen."

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
        if self.creative is True:
            goodbye_message = "Aight byee hottie. I’ma just rap and do me."
        else:
            goodbye_message = "Goodbye! Have a nice day!"

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
        
        line = line.lower()
        response = ""
        
        if self.counter == 4: 
            response = self.recommend_loop(line, self.counter, self.user_ratings, self.recommedations_so_far)
        
        else: 
            if self.pending_movie_options:
                if line[0] != "\"" :
                    line = "\"" + line + "\""
            potential_titles = self.extract_titles(line) 
            
            if self.creative: #correction was suggested to user already
                if line[:3] == "yes" and len(self.movie_correction_idx) > 0:
                    movie_indicies = self.movie_correction_idx
                    corrected_movie = self.titles[self.movie_correction_idx[0]][0]
                    self.spellcheck = True
                    
                    potential_titles = [corrected_movie]
                    
                if line[:2] == "no" and len(self.movie_correction_idx) > 0: 
                    if self.creative is False:
                        return "I'm sorry I don't know that movie then. Can you try describing a different one?"
                    else:
                        return "Girrrll! Give me another movie then."
                
            if len(potential_titles) > 1: 
                if self.creative: 
                    response = self.multiple_sentiments_helper(line)
                    if len(response) == 0:

                            #response = "I'm sorry, can you specify a movie within quotes?" #placeholder bc extract_mult sentiments and movie without quotes not working
                        response = "Put the title in quotes will ya?"
                else: 
                    response = "I'm sorry, tell me about one movie in particular."
            elif len(potential_titles) == 0:
                response = "I'm sorry, can you please specify a movie within quotes?"
            
            #one potential title was found 
            else: 
                if self.creative and self.pending_movie_options:
                    movie_indicies = self.disambiguate(line, self.pending_movies_indices)
                    if len(movie_indicies) != 0:
                        self.pending_movie = self.titles[movie_indicies[0]][0]
                        potential_titles = [self.pending_movie]
                        
                    else: 
                        response= "I'm sorry, that's not one of the options. Please try again."
                else:
                    movie_indicies = self.find_movies_by_title(potential_titles[0])
                
                #if the potential title was not in the database
                if len(movie_indicies) == 0: 
                    if self.creative: 
                        if not self.pending_movie_options:
                            response = self.movie_correction_dialogue(potential_titles)
                            self.pending_sentiment = self.extract_sentiment(line)
                    else: 
                        response = "I've never heard of {}. Can you specify another movie?".format(potential_titles[0])
                
                elif len(movie_indicies) > 1: 
                    if self.creative and not self.pending_movie_options and not self.spellcheck:
                        potential_movies_str = self.format_potential_titles(movie_indicies)
                        #response = "I've heard of more than one movie called {}, ".format(potential_titles[0])
                        response = "I know of more movies called {}, ".format(potential_titles[0])
                        response += "which one did you want: {}?".format(potential_movies_str)
                        self.pending_movie_options = True
                        self.pending_movies_indices = movie_indicies
                        self.pending_sentiment = self.extract_sentiment(line)
                    else: 
                        response = "I've heard of more than one movie called {}, can you specify which one?".format(potential_titles[0])

                
                #The movie was found in the database
                else: 
                    
                    if self.creative:
                        if (line == "yes" and self.spellcheck) or self.pending_movie_options:
                            sentiment = self.pending_sentiment
                        else:
                            sentiment = self.extract_sentiment(line)
                        self.pending_movie_options = False
                    else: 
                        sentiment = self.extract_sentiment(line)
                        
                    if sentiment == 0: 
                        if self.creative is False:
                            response = "I'm not sure if you liked {}. Tell me more about it.".format(potential_titles[0])
                        else:
                            response = "I can't read your feelings about {}. Just spill it girl!".format(potential_titles[0])

                    else: 
                        self.user_ratings[movie_indicies[0]] = sentiment
                        self.counter += 1
                        if sentiment == -1:
                            if self.creative is False:
                                response = "Okay, you didn't like {}. Tell me what you thought about another movie".format(potential_titles[0])
                            else:
                                response = "Aight so {} wasn't your vibe. Give me another movie.".format(potential_titles[0])
                        elif sentiment == 1: 
                            if self.creative is False:
                                response = "Okay, you liked {}. Tell me what you thought about another movie".format(potential_titles[0])
                            else:
                                response = "Okay, so {} popped OFF. Give me another movie.".format(potential_titles[0])

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


    def format_potential_titles(self, movie_indicies):
        result = ""
        for idx in movie_indicies: 
            title = self.titles[idx][0]
            if len(result) > 0: 
                result += " or "
            result += title
        return result 

    def recommend_loop(self, line, counter, user_ratings, recommedations_so_far):
        line = line.lower()
        recommend_indices = self.recommend(self.user_ratings, self.ratings, 5, self.creative)
        if self.recommedations_so_far < 5: 
            movie = self.titles[recommend_indices[recommedations_so_far]][0]
            self.recommedations_so_far += 1
            if line == "yes":
                response = "I would also recommend {}. Would you like another one? (Or enter :quit if you're done.)".format(movie)
            elif line == "no":
                response = "Please enter :quit to exit."
            else: 
                response = "Given what you have said, I think you would like {}. Would you like another recommendation?(Or enter :quit if you're done.)".format(movie)
        else: 
            response = "That's all the recommendations I have. Please enter :quit to finish."
        return response 

    def movie_correction_dialogue(self, potential_titles):
        self.movie_correction_idx = self.find_movies_closest_to_title(potential_titles[0], max_distance=3)
        if len(self.movie_correction_idx) == 0: 
            response = "I'm sorry, I'm never heard of {}. Can you tell me how you felt about another movie?".format(potential_titles[0])
        else:
            movie_correction = self.titles[self.movie_correction_idx[0]][0]
            response = "Did you mean {}?".format(movie_correction)
        return response

    def multiple_sentiments_helper(self, line): 
        response = ""
        sentiment_list = self.extract_sentiment_for_movies(line)
        if len(sentiment_list) != 0: 
            for sentiment_pair in sentiment_list:
                movie = sentiment_pair[0]
                sentiment = sentiment_pair[1]
                if len(response) > 0: 
                    response += " and "
                
                if sentiment == -1: 
                    if len(response) == 0: 
                        response += "You did not like {}".format(movie)
                    else:
                        response +=  "you did not like {}".format(movie)
                else: 
                    if len(response) == 0: 
                        response += "You liked {}".format(movie)
                    else:
                        response += "you liked {}".format(movie)
                movie_indicies = self.find_movies_by_title(movie)
                if len(movie_indicies) > 0: 
                    self.user_ratings[movie_indicies[0]] = sentiment
                    self.counter += 1
            response += "."
        return response 


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
        potential_titles = []
        start = 0 
        for i in range(len(preprocessed_input)): 
            first_quote = preprocessed_input.find("\"", start)
            if first_quote != -1: 
                next_quote = preprocessed_input.find("\"", first_quote+1)
                if next_quote != -1: 
                    title = preprocessed_input[first_quote+1:next_quote]
                    potential_titles.append(title)     
                    start = next_quote + 1   
        if len(potential_titles) == 0: 
            self.no_quotes = True
            max_length = sorted([len(pair[0].split()) for pair in self.titles], reverse=True)[0]
            sentence = preprocessed_input.lower()
            punctuation = ['.', '"', '!', ',']
            for p in punctuation: 
                sentence = sentence.replace(p, '')
            tokens = sentence.split()
            for i in range(len(tokens)):
                for j in range(i + 1, min([len(tokens) + 1, i + max_length])):
                    window = tokens[i:j]
                    title = ' '.join(window)
                    original = self.creative
                    self.creative = False
                    if len(self.find_movies_by_title(title)) > 0:
                        potential_titles.append(title)
                    self.creative = original
            static = [title for title in potential_titles]
            for s in static: 
                for big_s in potential_titles:
                    if not s == big_s and s in big_s: 
                        potential_titles.remove(s)
                        break
        else:
            self.no_quotes = False
        self.ignore_words = set([token for title in [title.split() for title in potential_titles] for token in title])
        return potential_titles

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
        #0%Toy Story (1995)%
        #put in article handling? 
        #what if the split title has the or whatever
        ids = []
        title = title.lower()

        contains_year = bool(re.search(r'\([0-9][0-9][0-9][0-9]\)', title))
        year = title[-6:] if contains_year else ''
        if contains_year:
            title = title[:-7]

        if title[:4] == 'the ':
            title = title[4:] + ', the'
        elif title[:3] == 'an ':
            title = title[3:] + ', an'
        elif title[:2] == 'a ':
            title = title[2:] + ', a'
        #do within the loop
        if self.creative is True:
            #handle languages here, re-format
            #spanish
            if title[:3] == 'el ':
                title = title[3:] + ', el'
            elif title[:3] == 'la ':
                title = title[3:] + ', la'
            #elif title[:4] == 'los ':
                #title = title[4:] + ', los'
            elif title[:4] == 'las ':
                title = title[4:] + ', las'
            #italian
            elif title[:3] == 'lo ':
                title = title[3:] + ', lo'
            elif title[:3] == 'il ':
                title = title[3:] + ', il'
            elif title[:3] == 'l\' ':
                title = title[3:] + ', l\''
            elif title[:4] == 'gli ':
                title = title[4:] + ', gli'
            #elif title[:2] == 'i ':
                #title = title[4:] + ', i'
            elif title[:3] == 'le ':
                title = title[4:] + ', le'
            #french
            elif title[:4] == 'les ':
                title = title[4:] + ', les'
            #german
            elif title[:4] == 'die ':
                title = title[4:] + ', die'
            elif title[:5] == 'eine ':
                title = title[5:] + ', eine'
            elif title[:6] == 'keine ':
                title = title[6:] + ', keine'

        # USER INPUTS:
        # title: string like "golden globe, the"
        # year: either empty "" or "(1997)" depending on if contains_year is True or False

        for movie_id, (curr_title, _) in enumerate(self.titles):
            curr_title = curr_title.lower()
            '''
            Data to parse:
                DONE - Title that the user enters (and the preposition is at the end after the comma)
                DONE - [optional] Year that the user enters, including parentheses
                DONE - All title names of the movie as a List (and removing all 'a.k.a.'s)
                DONE - Year of the movie title, including parentheses (curr_title[-6:])
            '''
            curr_year = curr_title[-6:]     # something like "(1997)"
            curr_title = curr_title[:-7]    # everything before " (1997)"
            # curr_title can be something like "Golden Globe, The (Blah Blah, El) (a.k.a. hello)"
            all_curr_titles = []
            idx_of_open_p = curr_title.find("(")
            if idx_of_open_p == -1:    # There are no alternate titles or foreign
                all_curr_titles.append(curr_title)
            else:
                all_curr_titles.append(curr_title[:idx_of_open_p-1])
                curr_title = curr_title[idx_of_open_p:]    # Now just "(Blah Hehe Blah, El) (a.k.a. hello)"
                while curr_title:
                    idx_of_close_p = curr_title.find(")")
                    candidate = curr_title[1:idx_of_close_p]
                    # Check if candidate begins with "a.k.a. "
                    if candidate.startswith("a.k.a. "):
                        candidate = candidate[7:]
                    all_curr_titles.append(candidate)
                    curr_title = curr_title[idx_of_close_p + 2:]

            if contains_year and year != curr_year:
                continue

            # All code after here implies year is a match (or no year specified)
            if self.creative is False:
                if title == all_curr_titles[0]:
                    ids.append(movie_id)
            else:
                # Either matches exactly, or starts with and has a space at the end, or starts with a space and ends with a space
                for t in all_curr_titles:
                    if title == t or t.startswith(title + " ") or (" " + title + " ") in t or t.endswith(" " + title):
                        ids.append(movie_id)
                        break

        return ids

        """
        if contains_year and curr_title == title or not contains_year and curr_title[:-7] == title:
            ids.append(movie_id)
            continue
        #what about the normal case with foreign title but they didn't have the foregin title
        #do within the loop
                
        # (la guierre) (2015) HANDLE YEAR CASE WITH FOREIGN AND AKA TITLE
        if self.creative is True:
            # disambiguate_helper(movie_id, curr_title, title, ids, contains_year)

            #disambiguate (no foreign titles or alternate) #Twelve Monkeys (a.k.a. 12 Monkeys) can be two akas
            if contains_year is False:
                input_tokens = title.split(" ")#what if someone types in hi, we need to treat it as a separate token
                data_tokens = curr_title.split(" ")
                found_title = False
                for index, word in enumerate(data_tokens):
                    if input_tokens[0] == word and found_title is False:
                        if len(input_tokens) == 1:
                            ids.append(movie_id)
                            found_title = True
                        else:
                            counter = 1
                            while counter < len(data_tokens) and counter < len(input_tokens):
                                if input_tokens[counter] != data_tokens[counter]:
                                    break
                                counter +=1
                                if counter == len(input_tokens):
                                    ids.append(movie_id)
                                    found_title = True
                                #if we get to this stage, we have found all the tokens
                
    #['Blade Runner (1982)', 'Action|Sci-Fi|Thriller']
    #['American President, The (1995)', 'Action|Sci-Fi|Thriller']
    #input : Titanic, Titanic (1972)
    """


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
        self.extract_titles(preprocessed_input)
        preprocessed_input = self.remove_movie(preprocessed_input)
        negation_words = ['didn\'t', 'never', 'don\'t', 'not']
        result = 0 
        p = PorterStemmer()
        stemmed_dict = {}
        for key in self.sentiment.keys(): 
            stemmed = p.stem(key)
            stemmed_dict[stemmed] = self.sentiment[key]
        tokens = preprocessed_input.split()
        negation = False
        for token in tokens: 
            if token in negation_words: 
                negation = True
            stemmed_token = p.stem(re.sub(r'\W+', '', token))
            if stemmed_token in stemmed_dict:
                sentiment = stemmed_dict[stemmed_token]
                if sentiment == 'neg':
                    if negation: 
                        result = 1
                    else: 
                        result = -1
                else:
                    if negation: 
                        result = -1
                    else: 
                        result = 1
        return result

    def remove_movie(self, input):
        """Helper to remove movie title from string before sentiment extraction"""
        input_list = input.split()
        for word in self.ignore_words:
            if word in input_list:
                input_list.remove(word)
            elif word + '"' in input_list:
                input_list.remove(word + '"')
            elif '"' + word in input_list: 
                input_list.remove('"' + word)
        self.ignore_words = {}
        input = ' '.join(input_list)
        return input 

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
        outputs = []
        titles = self.extract_titles(preprocessed_input)
        if self.no_quotes:
            mood = self.extract_sentiment(preprocessed_input)
            return [(title, mood) for title in titles]
        sections = preprocessed_input.split('"')
        conjunction = '\s*(,|;)?\s*(and|or)?\s*'
        switch = '\s*(,|;)?\s*(but)?\s*(not)?\s*'
        sentiments = []
        for section in sections:
            if section in titles:
                sentiments.append('MOVIE')
            else:
                sentiment = self.extract_sentiment(section)
                if sentiment == 1: 
                    sentiments.append('1')
                elif sentiment == -1: 
                    sentiments.append('-1')
                elif re.fullmatch(conjunction, section): 
                    sentiments.append('AND')
                elif re.fullmatch(switch, section): 
                    sentiments.append('BUT')
        current_mood = 0
        current_film = 0
        films_passed = 0
        for token in sentiments: 
            if token == 'MOVIE':
                films_passed += 1
                if current_mood != 0: 
                    outputs.append((titles[current_film], current_mood))
                    current_film += 1
            elif token == 'AND':
                continue
            elif token == 'BUT':
                current_mood *= -1
            else: 
                current_mood = int(token)
                while films_passed > current_film:
                    outputs.append((titles[current_film], current_mood))
                    current_film += 1
        return outputs

    def find_movies_closest_to_title(self, title, max_distance):
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

        levenstein edit distance algorithm:
        https://blog.paperspace.com/implementing-levenshtein-distance-word-autocomplete-autocorrect/
        """
        
        movies = []
        indices = []
        curr_min_distance = 100
        token1 = title.lower()

        for token2 in self.titles:
            token2 = token2[0].lower()
            year = token2[len(token2)-7:]
            token2 = token2[:len(token2)-7]
            
            if token2[-5:] == ', the':
                token2 = 'the ' + token2[:-5] 
            elif token2[-4:] == ', an':
                token2 = 'an ' + token2[:-4]  
            elif token2[-3:] == ', a':
                token2 = 'an ' + token2[:-3]

            distances = np.zeros((len(token1) + 1, len(token2) + 1))
            
            #compute Levenstein distance matrix
            for t1 in range(len(token1) + 1):
                distances[t1][0] = t1
            for t2 in range(len(token2) + 1):
                distances[0][t2] = t2      
            a = 0
            b = 0
            c = 0
            for t1 in range(1, len(token1) + 1):
                for t2 in range(1, len(token2) + 1):
                    if (token1[t1-1] == token2[t2-1]):
                        distances[t1][t2] = distances[t1 - 1][t2 - 1]
                    else:
                        a = distances[t1][t2 - 1]
                        b = distances[t1 - 1][t2]
                        c = distances[t1 - 1][t2 - 1]
                            
                        if (a <= b and a <= c):
                            distances[t1][t2] = a + 1
                        elif (b <= a and b <= c):
                            distances[t1][t2] = b + 1
                        else:
                            distances[t1][t2] = c + 1
            final_distance = distances[len(token1)][len(token2)]
            token2 += year
            
            #update movie corrections list
            if final_distance <= max_distance: 
                if final_distance == curr_min_distance and len(movies) != 0:
                    movies.append(token2)
                elif final_distance < curr_min_distance:
                    movies = [token2]
                    curr_min_distance = final_distance
        for movie in movies:
            idx = self.find_movies_by_title(movie)
            if len(idx) != 0: 
                indices.append(idx[0])
        return indices 
                


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
        ids = []
        clarification = clarification.lower()
        if "\"" in clarification:
            clarification=clarification.replace('\"', '')
        if "\"" in clarification:
            clarification=clarification.replace('\"', '')
    

        # Case 1: user enters a valid year (search in title and in ())
        is_year = bool(re.search(r'^[0-9][0-9][0-9][0-9]$', clarification))
        for candidate in candidates:
            curr_title = self.titles[candidate][0].lower()
            if is_year:
                if curr_title[-5:-1] == clarification or curr_title.startswith(clarification + " ") or (" " + clarification + " ") in curr_title or curr_title[:-7].endswith(" " + clarification):
                    ids.append(candidate)
            else:
                if curr_title.startswith(clarification + " ") or (" " + clarification + " ") in curr_title or curr_title[:-7].endswith(" " + clarification):
                    ids.append(candidate)

        return ids

        pass

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
        binarized_ratings = np.zeros_like(ratings)
        rows, cols = ratings.shape
        for row in range(rows):
            for col in range(cols): 
                if ratings[row, col] > threshold: 
                    binarized_ratings[row, col] = 1
                elif ratings[row, col] > 0: 
                    binarized_ratings[row, col] = -1
                else: 
                    binarized_ratings[row, col] = 0
        return binarized_ratings

    def similarity(self, u, v):
        """Calculate the cosine similarity between two vectors.

        You may assume that the two arguments have the same shape.

        :param u: one vector, as a 1D numpy array
        :param v: another vector, as a 1D numpy array

        :returns: the cosine similarity between the two vectors
        """
        magu = np.linalg.norm(u)
        magv = np.linalg.norm(v)
        dotprod = np.dot(u, v)
        return dotprod / (magu * magv)

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
        recommendations = []
        rated_movies = np.nonzero(user_ratings)[0]
        for i in range(ratings_matrix.shape[0]):
            if i in rated_movies or not np.any(ratings_matrix[i]):
                continue
            r = 0
            for j in rated_movies:
                rating = user_ratings[j]
                sim = self.similarity(ratings_matrix[i], ratings_matrix[j])
                r += (rating * sim)
            recommendations.append((i, r))
        toprecs = [rec[0] for rec in sorted(recommendations, key=lambda rec: rec[1], reverse=True)]
        return toprecs[:k]

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
        Hi! I'm a chatbot created by Maya, Kathryn, and Za. 
        I can recommend movies for you based on your opinion of 5 movies you've seen in the past. 
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
