# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
# vector norm
from numpy.linalg import norm
# regex
import re
# string
import string
#random
import random
from porter_stemmer import PorterStemmer
from collections import defaultdict


# noinspection PyMethodMayBeStatic

class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        self.creative = creative
        if self.creative:
            self.name = 'PiRRRate Pete'
        else:
            self.name = 'Pete'
        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.p = PorterStemmer()
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.titles_list = [element[0] for element in self.titles]
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        self.movie_yrs = [] 
        
        self.sentiment_stemmed = {self.p.stem(sentiment): v for sentiment, v in self.sentiment.items()}
        ########################################################################
        ########################################################################
        ratings = self.binarize(ratings, threshold=2.5)
        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = ratings
        self.recommendations = []
        self.recommend_idx = 0

        self.user_ratings = {} # a dictionary of the form index: sentiment
        self.ask_recommendation = False # boolean flag
        self.message_sentiment = None

        self.positive_responses = ["yes", "y", "sure", "yep", "yeah", "ok", "okay"]
        self.negative_responses = ["no", "n", "nope", "nah", "naur", "never"]
        self.num_rec = 0
        self.multiplier = 1
        
        #disambiguate dict 
        self.numbers_written_dict = {
            "first": 1,
            "second": 2, 
            "third": 3, 
            "fourth": 4, 
            "fifth": 5, 
            "sixth": 6, 
            "seventh": 7, 
            "eight": 8, 
            "ninth": 9, 
            "tenth": 10, 
        }


        #vars for processing: 
        #creative mode convo types
        self.disambiguate_type = 1
        self.spell_check_type = 2
        self.new_convo_type = 3
        self.recommend_type = 4

        #others for response state 
        self.convo_type = self.new_convo_type

        #disambiguate response 
        self.title_possibilities = []
        

        
        
        self.parrot = ''' 
                {SQWAAAAAAWK!}
                       \     _    
                          /` '\

                          
                        \ |     \\
                         `\\     `\\_
                            \\    __ `\\
                            l  \\   `\\ `\\__
                            \\  `\\./`     ``\\
                            \\ ____ / \\   l
                                ||  ||  )  /
                        -------(((-(((---l /-------
                                        l /
                                    / /
                                    / /
                                    //
                                    / 
'''

        


        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        ########################################################################
        ########################################################################
        if self.creative:
            greeting_message = "\n" + self.parrot + "Ahoy, matey! I'm PiRRRate Pete, herrre to give you some rrrecommendations!"
        else:
            greeting_message = "Hi! I'm Pete, a movie chatbot. Give me some movies and I'll give you some recommendations!"

        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################
        return greeting_message

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        ########################################################################
        ########################################################################

        if self.creative:
            goodbye_message = "Yourrr movies are safe with me. Dead pirrrates tell no tales! Also, make sure to enjoy the movies I recommended in a safe and legal way. You wouldn't steal a car, would you?"
        else:
            goodbye_message = "Bye for now!"

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return goodbye_message

    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################
    def dict_to_array(self, d, length):
        """
        Convert a dictionary in the form {index: value} into an array.
        """
        array = np.zeros(length)
        for index, value in d.items():
            array[index] = value
        return array
    
    def starter_process(self, line):
        response = ""
        if len(self.user_ratings) < 5:
            titles = self.extract_titles(line)
            message_sentiment = self.extract_sentiment(line)

            # user gives multiple titles
            if len(titles) > 1:
                responses = ["One movie at a time, buck-o!", "Slow down... give me one movie!"]
                return random.choice(responses)
            
            # unable to detect title
            if titles == []:
                responses = ["Tell me the name of a movie!",\
                              "I didn't catch a movie title there — are you sure you're formatting your message right?",\
                            "Let's chat about movies.", "That doesn't sound like the name of a movie to me.",\
                                "For Pete's sake, we're here to discuss movies!", "I charge by the hour, pal, so don't waste my time."]
                return random.choice(responses)
            
            title_idx = 9999
            candidates = self.find_movies_by_title(titles[0])
            
            if not candidates:
                responses = ["Sorry, I don't think I know that movie... Could you try telling me about a different one?",\
                             "Are you gaslighting me?", "I haven't heard of that one.", "Try another one, please!"]
                return random.choice(responses)

            if len(candidates) > 1:
                responses = ["I wasn't able to tell which movie you were referring to — could you be more specific?"]
                return random.choice(responses)
            
            title_idx = self.find_movies_by_title(titles[0])[0]
            
            if title_idx in self.user_ratings:
                return "You already told me about " + titles[0] + ". How about a different film?"
            
            acknowledge_pos = ["It sounds like you like \"{}\".", "I also love \"{}\"!"]
            acknowledge_neg = ["It sounds like you don't like \"{}\".", "Sounds like you're not the biggest fan of \"{}\"."]
            acknowledge_neutral = ["You seem... ambivalent. Did you like \"{}\"?", "I'm not sure if you like the movie \"{}\".",\
                              "Tell me, what do you think about \"{}\"?"]
            if message_sentiment > 0: # positive
                self.user_ratings[title_idx] = 1
                response = random.choice(acknowledge_pos).format(titles[0])
            elif message_sentiment == 0: # neutral
                return random.choice(acknowledge_neutral).format(titles[0])
            else: 
                self.user_ratings[title_idx] = -1 #negative
                response = random.choice(acknowledge_neg).format(titles[0])
                
            response = response + "\nPlease tell me about another movie!"
        
            if len(self.user_ratings) == 5:
                print("Great! I have enough information to recommend you a movie now.\n...one moment please...")
            
        if len(self.user_ratings) >= 5:
            if self.num_rec > 9:
                return "Sorry! That's all the recommendations I have for now. Type ':quit' if you'd like to make a new query?"
            
            if not self.ask_recommendation:
                self.recommend(self.dict_to_array(self.user_ratings, len(self.titles)), self.ratings)

            if self.ask_recommendation:
                if line.lower() in self.positive_responses:
                    recommended_title = self.titles[self.recommendations[self.num_rec]][0]
                    self.num_rec += 1
                    responses = ['I think you would like \"{}\"!', '\"{}\" might be right up your alley.']
                    response = random.choice(responses).format(recommended_title) + " Do you want another recommendation?"
                elif line.lower() in self.negative_responses:
                    return "Ok then..."
                else:
                    return "Sorry, I didn't get that. Say yes if you want a recommendation and no if you don't."
                
            else:
                recommended_title = self.titles[self.recommendations[self.num_rec]][0]
                self.num_rec += 1
                responses = ['I found a movie that would be perfect for you: \"{}\"!', 'I think you would like \"{}\"!', '\"{}\" might be right up your alley.']
                response = random.choice(responses).format(recommended_title) + " Would you like another recommendation?"
                self.ask_recommendation = True

        return response

    def return_recommendation(self, idx_list):
        """This function takes in a list of recommendation indices and returns the name of a
          movie that hasn't already been recommended. If the bot has already made all the recommendations,
          ask if the user wants more.
        """
        if self.recommend_idx > len(idx_list):
            return 9999
        
        response = idx_list[self.recommend_idx]
        return response
        
    
    def creative_process(self, line):
        response = ""
        #extraction mode
        if len(self.user_ratings) < 5:
            message_sentiment = self.extract_sentiment_for_movies(line)
            # message_sentiment = self.extract_sentiment(line)
            
            # if message_sentiment.keys() == []:
            #     responses = ["Tell me the name of a movie, you scallywag!",\
            #                 "Let's chat about movies. Or pirates *suggestive wink*", "That doesn't sound like the name of a movie to me, you scurvy dog.",\
            #                     "Tell me the name of a movie, or I'll make you walk the plank!", "I charge by the hour, lassie, so don't waste my time."]
            #     return random.choice(responses)
            
            candidates = []
            for title in message_sentiment.keys():
                candidates = self.find_movies_by_title(title)

            if candidates == []:
                responses = ["Sorry, I don't think I know that movie... Could you try telling me about a different one?",\
                            "Are you gaslighting me?", "I haven't heard of that one.", "Try another film, please!"]
                return random.choice(responses)
            
            if len(candidates) > 1:
                print("Yo ho ho, I found several possible movies with that name:")
                for candidate in candidates:
                    to_print = '  * ' + self.titles[candidate][0] + '(' + self.titles[candidate][1] + ')'
                    print(to_print)
                print("Which of these did ye mean?")
                
                disambig_result = self.disambiguate(line, candidates)
                if (len(disambig_result) != 1):
                    return "ANGRY PARROT NOISE: Tell us another movie pls"
                
            title_idx = self.find_movies_by_title(title)[0]
            if title_idx in self.user_ratings:
                return "Ye already told me about " + title + ". How about a different film?"
                
            acknowledge_pos = ["It sounds like ye like \"{}\".", "Avast! \"{}\". Savvy!"]
            acknowledge_neg = ["Sink me! Ye don't like \"{}\"!", "Sounds like yerr not the biggest fan of \"{}\"."]
            acknowledge_neutral = ["Heave ho! Did ye like \"{}\" or not?", "Tell me if ye like, \"{}\", alright?",\
                                "Tell me, what do ye think about \"{}\"?"]
            if message_sentiment[title] > 0: # positive
                self.user_ratings[title_idx] = 1
                response = random.choice(acknowledge_pos).format(title)
            elif message_sentiment[title] == 0: # neutral
                return random.choice(acknowledge_neutral).format(title)
            else: 
                self.user_ratings[title_idx] = -1 #negative
                response = random.choice(acknowledge_neg).format(title)
                    
            response = response + "\nPlease tell me about another movie!"
            
        if len(self.user_ratings) == 5:
            print("Shiver me timbers! I can give this scallywag a movie!\n...now...")



        #recommendation mode
        '''
        if len(candidates) > 1:
            clarified = [self.find_movie_by_idx(movie) for movie in self.disambiguate(line, candidates)]
            if len(clarified == 2):
                return '\nWhich movie did you mean: "{clarified[0]}" or "{clarified[1]}"?'
            if len(clarified > 2):
                response_str = ', '.join('"' + movie + '"' for movie in clarified[:-1])
                response = '\nWhich movie did you mean: ' + response_str + ', or "' + clarified[-1] + '"'
        return response
        '''
        return response
         

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
        #DEBUGNOTE: these two lines below are for testing disambiguate function (without completing process)
        # index = self.disambiguate(line, [2716, 1359])
        # print(index)

        if self.creative:
            response = self.creative_process(line)
        else: #starter mode
            response = self.starter_process(line)

        #drafted other version for process below:
        # if self.convo_type != self.recommend_type:
        #     if self.convo_type == self.disambiguate_type:
        #         self.title_possibilities = self.disambiguate(line, self.title_possibilities)

        #         #narrowing convo
        #         if len(self.title_possibilities) > 1:
        #             print("fill in later")
        #         elif len(self.title_possibilities) == 0:
        #             self.convo_type = self.new_convo_type
        #             return "Errrrr tell me about another movie!"
        #         else: 
        #             self.
                
        





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

    # citation: written by chatGPT
    def levenshtein_edit_dis (self, str1, str2): # s, t
        # Initialize matrix of zeros of size (len(str1)+1) x (len(str)+1)
        d = [[0 for j in range(len(str2) + 1)] for i in range(len(str1) + 1)]
    
        # Populate first row and column of matrix
        for i in range(len(str1) + 1):
            d[i][0] = i
        for j in range(len(str2) + 1):
            d[0][j] = j
        
        # fill in rest of matrix
        for j in range(1, len(str2) + 1):
            for i in range(1, len(str1) + 1):
                if str1[i-1] == str2[j-1]:
                    substitution_cost = 0
                else:
                    substitution_cost = 1
                d[i][j] = min(d[i-1][j] + 1,           # deletion
                            d[i][j-1] + 1,           # insertion
                            d[i-1][j-1] + substitution_cost)  # substitution
        
        # Return the final edit distance
        return d[len(str1)][len(str2)]
    

    def clean_text(self, text):
        """Removes punctuation and articles. This function returns a list of 
        of words, rather than a single string.
        """
        text_words = re.sub(r'[^\w\s]','',text).lower().split()
        for article in ["the", "an", "a"]:
            if article in text_words:
                text_words.remove(article)
        return text_words
    

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
        titles = []
        
        if not self.creative:
            title_pattern = '"([^"]*)"' 
            titles = re.findall(title_pattern, preprocessed_input)

        input_words = self.clean_text(preprocessed_input)
        inpt_yrs = re.findall('(\d{4})', preprocessed_input)

        if self.creative:
            year_pattern = '\((\d{4}-?(?:\d{4})?)\)' 
            for movie in self.titles:
                movie_title = movie[0]
                title_words = self.clean_text(movie_title)

                mov_yrs = re.findall(year_pattern, movie_title) # capture group is 4 numbers without parentheses
                if mov_yrs != []:
                    mov_yr = mov_yrs[0]

                for k in range(len(title_words)):
                    if title_words[k] == mov_yr:
                        title_words.pop(k)
                        break

                found_list = []
                for word in title_words:
                    if word in input_words:
                        found_list.append(word)

                if len(found_list) == len(title_words):
                    if inpt_yrs != []:
                        for inpt_yr in inpt_yrs:
                            if inpt_yr == mov_yr:
                                self.movie_yrs.append(mov_yr)
                                titles.append(movie_title)
                    else:
                        movie_title = re.sub(year_pattern, '', movie[0])[:-1] 
                        titles.append(movie_title)

        self.movie_yrs = []
        return list(set(titles))

    def find_movies_by_title(self, title):
        """ Given a movie title, return a list of indices of matching movies.

        - If no movies are found that match the given title, return an empty
        list.
        - If multiple movies are found that match the given title, return a list
        containing all of the indices of these matching movies.
        - If exactly one movie is found that matches the given title, return a
        list that contains the index of that matching movie.

        Example:
          ids = chatbot.find_movies_by_title('Titanic')
          print(ids) // prints [1359, 2716]

        :param title: a string containing a movie title
        :returns: a list of indices of matching movies
        """
        matching_indices_list = []

        #draft 1:
        for i, original_title in enumerate(self.titles):
            og_title = original_title[0]
            titles_option_one = set()
            title_without_date = "(".join(og_title.split("(")[:-1])[:-1]
            titles_option_one.add(title_without_date)

            for regex in re.finditer(r'\((.*?)\)', title_without_date):
                titles_option_one.add(regex.group(1))
            
            title_without_brackets = "(".join(title_without_date.split("(")[:-1])
            if title_without_brackets != "":
                titles_option_one.add(title_without_brackets)

            #making second set of titles that could possibly work 
            titles_option_two = set()

            for option in titles_option_one:
                titles_option_two.add(option)
                match = re.match(r'^(.*), (\w+)$', option)
                
                if match:
                    titles_option_two.add(match.group(2) + " " + match.group(1))
            

            #now get title with the date
            date = og_title[len(title_without_date):]
            titles_option_three = set()
            for option in titles_option_two:
                titles_option_three.add(option)
                titles_option_three.add(option + date)

                #now do matching again
                match = re.findall(r'\((.*?)\)', option)

                for alternate_name in match:
                    if alternate_name != date:
                        if alternate_name.startswith("a.k.a "):
                            titles_option_three(alternate_name[len("a.k.a "):])
                        second_match = re.match(r'^(.*), (\w+)$', alternate_name)
                        if second_match:
                            titles_option_three.add(second_match.group(2) + " " + second_match.group(1))

            if " (" in og_title: 
                titles_option_three.add(og_title[:og_title.index(" (")])

            if title in titles_option_three:
                matching_indices_list.append(i)
        
        return matching_indices_list
    

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
        p = PorterStemmer()
        title = self.extract_titles(preprocessed_input)
        neg_words = [p.stem(word) for word in ["not", "no", "never", "didn't", "don't"]]
        super_words = [p.stem(word) for word in ["really", "very", "so", "extremely"]]
        happy_words = [p.stem(word) for word in ["amazing", "love", "perfect", "adore"]]
        sad_words = [p.stem(word) for word in ["terrible", "awful", "hate", "despise", "revile"]]
        self.emotion_words = []
        # we don't want to include the title when extracting sentiment
        if len(title) > 0:
            preprocessed_input = preprocessed_input.replace(title[0], "")
        # convert user's input into a list of words
        preprocessed_input = re.sub(r'[^\w\s]','', preprocessed_input)
        input_words = preprocessed_input.split(' ')
        pos_count,  neg_count, i = 0, 0, 0
        self.multiplier = 1
        while i < len(input_words):
            w = p.stem(input_words[i])
            # if we see a negation word, we need to negate everything after it 
            if w in neg_words and i != len(input_words) - 1:
                j = i + 1
                negate_w = p.stem(input_words[j])
                while j < len(input_words):
                    if negate_w in self.sentiment_stemmed:
                        if self.sentiment_stemmed[negate_w] == 'pos':
                            neg_count += 1 * self.multiplier
                        elif self.sentiment_stemmed[negate_w] == 'neg':
                            pos_count += 1 * self.multiplier
                    j += 1
                    if j <= len(input_words) - 1:
                        negate_w = p.stem(input_words[j])
                    i = j
            elif w in super_words:
                self.multiplier = 2
            elif w in happy_words:
                pos_count += 2
                self.emotion_words.append(input_words[i])
            elif w in sad_words:
                neg_count += 2
                self.emotion_words.append(input_words[i])
            else:
                if w in self.sentiment_stemmed:
                    if self.sentiment_stemmed[w] == 'pos':
                        pos_count += 1 * self.multiplier
                        self.emotion_words.append(input_words[i])
                    elif self.sentiment_stemmed[w] == 'neg':
                        neg_count += 1 * self.multiplier
                        self.emotion_words.append(input_words[i])
            i += 1
        # line below for testing
        # print("Sentiments: negative, positive", neg_count, pos_count)
        if pos_count > neg_count:
            if self.creative and pos_count - neg_count >= 2:
                return 2
            return 1
        elif neg_count > pos_count:
            if self.creative and neg_count - pos_count >= 2:
                return 2
            return -1
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
        sentiments = {}
        input_sentences = re.split(',|_-.', preprocessed_input)

        if input_sentences == []:
            return sentiments

        for input_sentence in input_sentences:
            movie_title = self.extract_titles(input_sentence)
            if movie_title != []:
                movie_ids = self.find_movies_by_title(movie_title[0])
                if movie_ids != []:
                    sentiments[movie_title[0]] = self.extract_sentiment(input_sentence)
        return sentiments
    

    #need to clean all the titles so we can use them to find closest to title 
    def helper_for_closest(self):
        all_titles = defaultdict(list) #dict: title : list of indices 

        #draft 1:
        for i, original_title in enumerate(self.titles):
            og_title = original_title[0]
            titles_option_one = set()
            title_without_date = "(".join(og_title.split("(")[:-1])[:-1]
            titles_option_one.add(title_without_date)

            for regex in re.finditer(r'\((.*?)\)', title_without_date):
                titles_option_one.add(regex.group(1))
            
            title_without_brackets = "(".join(title_without_date.split("(")[:-1])
            if title_without_brackets != "":
                titles_option_one.add(title_without_brackets)
                
            #making second set of titles that could possibly work 
            titles_option_two = set()

            for option in titles_option_one:
                titles_option_two.add(option)
                match = re.match(r'^(.*), (\w+)$', option)
                
                if match:
                    titles_option_two.add(match.group(2) + " " + match.group(1))

            #now get title with the date
            date = og_title[len(title_without_date):]
            
            titles_option_three = set()
            for option in titles_option_two:
                titles_option_three.add(option)
                titles_option_three.add(option + date)

                #now do matching again
                match = re.findall(r'\((.*?)\)', option)

                for alternate_name in match: 
                    if alternate_name != date:
                        if alternate_name.startswith("a.k.a "):
                            titles_option_three(alternate_name[len("a.k.a "):])
                        second_match = re.match(r'^(.*), (\w+)$', alternate_name)
                        if second_match:
                            titles_option_three.add(second_match.group(2) + " " + second_match.group(1))

            if " (" in og_title: 
                titles_option_three.add(og_title[:og_title.index(" (")])


            for option in titles_option_three:
                all_titles[option].append(i)
                all_titles[option + date].append(i)
        return all_titles
        


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
        #around 20 lines 
        #return [1656]

        #HHELLPPPPPPPPP HEERREEEEEE
        #?????? we need to get all title combinations of cleaned titles 
        title = title.lower()
        print(title)
        title_possibilities = self.helper_for_closest()

        # note: code below should be okay (approved by TA)
        correct_titles = []
        for i in range(max_distance + 1):
            correct_titles.append([])
        #correct_titles = [[] for i in range(max_distance + 1)]
        for possibility in title_possibilities: # can we just cycle through all of self.titles?
            edit_dist = self.levenshtein_edit_dis(title, possibility)
            if edit_dist <= max_distance:
                for i in title_possibilities[possibility]:
                    correct_titles[edit_dist].append(i)
        
        for title_list in correct_titles:
            if len(title_list) != 0: #if there is something then we return 
                return title_list

        return []


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
        #draft and pseudocode below:
        result = []

        #### other draft below:

        #covering the following case: year clarification   
        corresponding_results = []
        corresponding = False
        dates = []

        for candidate in candidates:
            title = self.titles[candidate][0]
            title_without_date = "(".join(title.split("(")[:-1])[:-1]

            #get the date from the title 
            date = title[len(title_without_date):]
            dates.append(int(date[2:-1]))

            #check on the clarification provided 
            if clarification in title_without_date or f" ({clarification})" == date:
                corresponding_results.append(candidate)
                #update 
                corresponding = True
            
            if corresponding == True:
                return corresponding_results

        #covering the following case: clarification of the ordering 
        if clarification.isnumeric() and 1<= int(clarification) and int(clarification) <= len(candidates):
            return [candidates[int(clarification) - 1]]
        
        #covering the following case: clarification with spelled out numbers
        movie_ordering = None
        for number in self.numbers_written_dict.keys():
            if number in clarification:
                movie_ordering = self.numbers_written_dict[number]
                break
        if movie_ordering is not None:
            return [candidates[movie_ordering -1]]


        #covering the following case: clarification timing  
        old_words = ["early", "former", "historic", "old"]
        old_num = 0
        recent_words = ["recent", "modern", "new", "contemporary", "brand new"] 
        recent_num = 0 

        #sort date indices
        date_indices_sorted = np.argsort(np.array(dates)) #fixed small typo 'argosrt -> argsort
        for word in old_words:
            if word in clarification:
                old_num += 1
        for word in recent_words:
            if word in clarification:
                recent_num += 1 
        if old_num > recent_num:
            return [candidates[date_indices_sorted[0]]]
        elif (old_num < recent_num):
            return [candidates[date_indices_sorted[-1]]]

        #disambiguate part 2: 
        #Narrow down from candidates given a user's response
        #such as an exact substring belonging to the right movie
        substring_results = []
        for candidate in candidates:
            title = self.titles[candidate][0]
            #find edit distance between the title and the clarification
            edit_distance_result = self.levenshtein_edit_dis(title, clarification)
            substring_results.append(edit_distance_result)
        # problem string
        return [candidates[np.argsort(np.array(substring_results))[0]]]



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
        #                                                                      #
        # WARNING: Do not use self.ratings directly in this function.          #
        ########################################################################

        binarized_ratings = np.where(ratings > threshold, 1, 
                                     (np.where(ratings == 0, 0, -1)))

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
        ########################################################################
        normalization = norm(u) * norm(v)
        if normalization > 0:
            similarity = np.dot(u, v) / normalization
        else:
            similarity = 0
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
        # WARNING: Do not use the self.ratings matrix directly in this         #
        # function.                                                            #
        #                                                                      #
        # For starter mode, you should use item-item collaborative filtering   #
        # with cosine similarity, no mean-centering, and no normalization of   #
        # scores.                                                              #
        ########################################################################

        # Populate this list with k movie indices to recommend to the user.
        recommendations = []

        #code start draft #1
        #from oh- Set how floating-point errors are handled.
        np.seterr(divide='ignore', invalid='ignore')

        #do matrix multiplication 
        similarity_matrix = ratings_matrix @ ratings_matrix.T 
        similarity_matrix = np.nan_to_num(similarity_matrix/(np.linalg.norm(ratings_matrix, axis=1, keepdims=True) * np.linalg.norm(ratings_matrix.T, axis=0, keepdims=True)))

        #get weighted averages
        weighted = np.array(similarity_matrix @ np.matrix(np.reshape(user_ratings, (-1,1))))[:, 0]
        #sort everything 
        sorted_weighted = np.argsort(-np.array(weighted))
        for sort_weight_avg in sorted_weighted:
            if user_ratings[sort_weight_avg] == 0:
                recommendations.append(sort_weight_avg)

        # remove everything from recommendations (list) already in self.user_ratings (dict)
        new_recs = [x for x in recommendations if x not in self.user_ratings.keys()]
        #return the top k
        new_recs = new_recs[:k]

        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        self.recommendations = new_recs
        return new_recs
    

    # def give_recommendation(self):
    #     recommend_sentences = ["You would love \"{}\"!", "I think you might like \"{}\".",\
    #                            "It's no Rick and Morty, but I think \"{}\" would be right up your alley:)"]
    #     response = random.choice(recommend_sentences).format(self.recommendations[self.recommend_idx])
    #     self.recommend_idx += 1
    #     return response

    ############################################################################
    # 4. Debug info                                                            #
    ############################################################################

    def debug(self, line):
        """
        Return debug information as a string for the line string from the REPL

        NOTE: Pass the debug information that you may think is important for
        your evaluators.
        """
        title = self.extract_titles(line)
        debug_info = title, self.user_ratings
        return debug_info
 
    ############################################################################
    # 5. Write a description for your chatbot here!                            #
    ############################################################################
    def intro(self):
        """
        Return a string to use as your chatbot's description for the user.

        Consider adding to this description any information about what your
        chatbot can do and how the user can interact with it.
        Your task is to implement the chatbot as detailed in the PA7
        instructions.
        Remember: in the starter mode, movie names will come in quotation marks
        and expressions of sentiment will be simple!
        TODO: Write here the description for your own chatbot!
        """
        if self.creative:
            return """In creative mode, this chatbot becomes a PIRATE! Pirate Pete is 
            able to detect when you love or hate a movie, can take in multiple movie inputs
            at once, and more! Give it a try, scallywag! But remember, don't pirate any movies!""" 
        else: 
            return """In starter mode, this chatbot is a placid and normal chatbot. 
            Give it the titles of five movies in quotations and correctly formatted,
            and it will give you up to 10 recommendations!"""
        


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')