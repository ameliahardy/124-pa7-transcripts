# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import re
import numpy as np
from porter_stemmer import PorterStemmer
import os
import math
from collections import defaultdict
from itertools import permutations


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'moviebot'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################
        
        # Initialize user's ratings with zeros
        self.user_ratings = np.zeros(len(self.titles))     
        
        # Keep track of whether a user wants another recommendation
        self.another_recommendation = 0
        
        # Initialize a list for recommendations
        
        self.recommendations = []
        
        self.misspelled = None

        # Binarize the movie ratings before storing the binarized matrix.
        #ratings = np.where(ratings > 5, 1, 0)
        self.ratings = self.binarize(ratings)
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
        
        if self.creative == True:
            greeting_message = "Hey, Dwayne Johnson here. You might know me as The Rock. I've been working with the best actors in Hollywood so let me know if I can recommend you some movies."
        
        else:
            greeting_message = "Welcome to the ultimate movie experience! I am R2-D2, your personal movie recommender robot, programmed to find the perfect film just for you."
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

        if self.creative == True:
            goodbye_message = "HEY! DON'T LEAVE BEFORE DOING YOUR DAILY 1000 PUSHUPS!!!!! AND REMEMBER : BE HUMBLE, BE HUNGRY, AND ALWAYS BE THE HARDEST WORKER IN THE ROOMa"
        else:
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
        
        movies = []
        movies_close = []
        
        if (self.misspelled != None and len(self.movies_close) >= 1) or self.misspelled == None:
            
            # Preprocess the input text
            text = self.preprocess(line)
        
            # Responses acceptable for another recommendation
            responses_for_another_recommendation = ["yes", "yeah", "yes, please", "yeah!", "yes!"]
            
            negative_responses_for_another_recommendation = ["no", "nope", "never", "no!", "nope!"]
            
            if self.another_recommendation == 1 and text in responses_for_another_recommendation:
                response =  "I would also recommend " + str(self.titles[self.recommendations[self.another_recommendation]][0]) + ". How about another one? (yes/no)"
                self.another_recommendation += 1
            elif self.another_recommendation == 2 and text in responses_for_another_recommendation:
                response = str(self.titles[self.recommendations[self.another_recommendation]][0]) + " would be a good movie for you! Would you like more recommendations? (yes/no)" 
                self.another_recommendation += 1
            elif self.another_recommendation > 2 and text in responses_for_another_recommendation:
                response =  "I would also recommend " + str(self.titles[self.recommendations[self.another_recommendation]][0]) + ". How about another one? (yes/no)"
                self.another_recommendation += 1
            elif self.another_recommendation > 0 and text in negative_responses_for_another_recommendation:
                response = "I hope I was useful to you. I you don't need any other recommendations, you can type ':quit' to leave. Would you like more recommendations? (yes/no)"            
            else:
            
                # Extract movie titles from user's input
                if self.clarification == False:
                    extracted_titles = self.extract_titles(text)
                if self.clarification == True:
                    if self.title_to_clarify in text:
                        extracted_titles = self.extract_titles(text)
                        self.clarification = False
                        self.title_to_clarify = ""
                    if self.title_to_clarify not in text:
                        extracted_titles = self.extract_titles(self.title_to_clarify + " " + str(text))
                        self.clarification = False
                        self.title_to_clarify = ""
                    
                
                # Check whether you extracted movies
                if len(extracted_titles) != 0: 
                    
                    if len(extracted_titles) > 1 :
                        response = 'It seems like you are talking about different movies. Could you please give me 1 movie?'
                    
                    if len(extracted_titles) == 1:
        
                        # Bring the information of the movie from our database
                        for extracted_title in extracted_titles:
                            movies_in_database = self.find_movies_by_title(extracted_title)
                            for movie_in_database in movies_in_database:
                                movies.append(self.titles[movie_in_database][0])
                    
                        if len(movies) != 0:
                            
                            if len(movies) == 1:
                                if self.misspelled != None:
                                    sentiment = self.extract_sentiment(self.misspelled)
                                else:
                                    sentiment = self.extract_sentiment(text)
                                if sentiment == 1:
                                    self.user_ratings[movies_in_database[0]] = 1
                                    response = "Oh, so you liked " + movies[0] + "."
                                elif sentiment == 2:
                                    self.user_ratings[movies_in_database[0]] = 1
                                    response = "Oh, so you loved " + movies[0] + "."
                                elif sentiment == -1:
                                    self.user_ratings[movies_in_database[0]] = -1
                                    response = "Oh, so you did not like " + movies[0] + "."
                                elif sentiment == -2:
                                    self.user_ratings[movies_in_database[0]] = -1
                                    response = "Oh, so you hated " + movies[0] + "."
                                else:
                                    response = "I'm sorry, I'm not sure if you liked " + movies[0] + ". Tell me more about it."
                                    
                                # Check whether you have enough ratings from the user. Else, recommend a movie.
                                num_nonzero = np.count_nonzero(self.user_ratings)
                                if num_nonzero < 5 and sentiment != 0:
                                    response += "\n Tell me what you thought of another movie. " + str(num_nonzero)
                                elif num_nonzero >= 5 and self.another_recommendation == 0:
                                    self.recommendations = recommendations = self.recommend(self.user_ratings, self.ratings)
                                    response += "\n Given what you told me, I think you would like " + str(self.titles[recommendations[self.another_recommendation]][0]) + ". Would you like more recommendations?"
                                    self.another_recommendation = 1
                                
                            elif len(movies) > 1 and len(extracted_titles) == 1:
                                
                                response = "I found more than one movie called " + str(extracted_titles[0]) + ". Can you clarify?"
                                self.clarification = True
                                self.title_to_clarify = str(extracted_titles[0])
                                
                            elif len(movies) > 1 and len(extracted_titles) > 1: 
                                # Extract the sentiment from the user input
                                sentiment_for_movies = self.extract_sentiment_for_movies(text)
                                response = "Oh, so you "
                                for movie, sentiment in sentiment_for_movies:
                                    if sentiment == 1:
                                        response += "liked the " + str(movie) + " and you "
                                    elif sentiment == -1:
                                        response += "did not like the " + str(movie) + " and you"
                                
                                response = response[:-9]        
                                response += ".\n"
                        
                        elif len(movies) == 0:     
                            # If you find no movies, try to find the ones closest to the title
                            movies_close_to_title = self.find_movies_closest_to_title(extracted_titles[0])
                            
                            if len(movies_close_to_title) != 0:
                            
                                # Bring the information of the movie from our database
                                for movie_close_to_title in movies_close_to_title:
                                    movies_close.append(self.titles[movie_close_to_title][0])
                                response = "You must have misspelled the movie. Did you mean any of the following movies: " 
                                for movie_close in movies_close:
                                    response += (str(movie_close) + ", ")
                                response = response[:-2]
                                response += "?"
                                self.misspelled = text
                                self.movies_close = movies_close.copy()
                            else:
                                response = "I've never heard of '" + str(extracted_titles[0]) + "', sorry... Tell me about another movie you liked."
                else:
                    response = "Sorry, I don't understand. Tell me about a movie that you have seen."
        elif self.misspelled != None and len(self.movies_close) == 1:
        
        
            # Responses acceptable for another recommendation
            responses_for_another_recommendation = ["yes", "yeah", "yes, please", "yeah!", "yes!"]
            
            negative_responses_for_another_recommendation = ["no", "nope", "never", "no!", "nope!"]
            
            if len(self.movies_close) == 1 and line in responses_for_another_recommendation:
            
                # Preprocess the input text
                #text = str(self.movies_close[0])
            
                # Extract movie titles from user's input
                extracted_titles = self.movies_close
                
                # Check whether you extracted movies
                if len(extracted_titles) != 0: 
                    
                    if len(extracted_titles) > 1 :
                        response = 'It seems like you are talking about different movies. Could you please give me 1 movie?'
                    
                    if len(extracted_titles) == 1:
        
                        # Bring the information of the movie from our database
                        for extracted_title in extracted_titles:
                            movies_in_database = self.find_movies_by_title(extracted_title)
                            for movie_in_database in movies_in_database:
                                movies.append(self.titles[movie_in_database][0])
                    
                        if len(movies) != 0:
                            
                            if len(movies) == 1:
                                if self.misspelled != None:
                                    sentiment = self.extract_sentiment(self.misspelled)
                                else:
                                    sentiment = self.extract_sentiment(text)
                                if sentiment == 1:
                                    self.user_ratings[movies_in_database[0]] = 1
                                    response = "Oh, so you liked " + movies[0] + "."
                                elif sentiment == 2:
                                    self.user_ratings[movies_in_database[0]] = 1
                                    response = "Oh, so you loved " + movies[0] + "."
                                elif sentiment == -1:
                                    self.user_ratings[movies_in_database[0]] = -1
                                    response = "Oh, so you did not like " + movies[0] + "."
                                elif sentiment == -2:
                                    self.user_ratings[movies_in_database[0]] = -1
                                    response = "Oh, so you hated " + movies[0] + "."
                                else:
                                    response = "I'm sorry, I'm not sure if you liked " + movies[0] + ". Tell me more about it."
                                    
                                # Check whether you have enough ratings from the user. Else, recommend a movie.
                                num_nonzero = np.count_nonzero(self.user_ratings)
                                if num_nonzero < 5 and sentiment != 0:
                                    response += "\n Tell me what you thought of another movie. " + str(num_nonzero)
                                elif num_nonzero >= 5 and self.another_recommendation == 0:
                                    self.recommendations = recommendations = self.recommend(self.user_ratings, self.ratings)
                                    response += "\n Given what you told me, I think you would like " + str(self.titles[recommendations[self.another_recommendation]][0]) + ". Would you like more recommendations?"
                                    self.another_recommendation = 1
                                
                            elif len(movies) > 1 and len(extracted_titles) == 1:
                                
                                response = "I found more than one movie called " + str(extracted_titles[0]) + ". Can you clarify?"
                                self.clarification = True
                                self.title_to_clarify = str(extracted_titles[0])
                                
                            elif len(movies) > 1 and len(extracted_titles) > 1: 
                                # Extract the sentiment from the user input
                                sentiment_for_movies = self.extract_sentiment_for_movies(text)
                                response = "Oh, so you "
                                for movie, sentiment in sentiment_for_movies:
                                    if sentiment == 1:
                                        response += "liked the " + str(movie) + " and you "
                                    elif sentiment == -1:
                                        response += "did not like the " + str(movie) + " and you"
                                
                                response = response[:-9]        
                                response += ".\n"
                        
                        elif len(movies) == 0:     
                            # If you find no movies, try to find the ones closest to the title
                            movies_close_to_title = self.find_movies_closest_to_title(extracted_titles[0])
                            
                            if len(movies_close_to_title) != 0:
                            
                                # Bring the information of the movie from our database
                                for movie_close_to_title in movies_close_to_title:
                                    movies_close.append(self.titles[movie_close_to_title][0])
                                response = "You must have misspelled the movie. Did you mean any of the following movies: " 
                                for movie_close in movies_close:
                                    response += (str(movie_close) + ", ")
                                response = response[:-2]
                                response += "?"
                                self.misspelled = text
                            else:
                                response = "I've never heard of '" + str(extracted_titles[0]) + "', sorry... Tell me about another movie you liked."
                else:
                    response = "Sorry, I don't understand. Tell me about a movie that you have seen."
                
                
            
  
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
    
    def light_transform(self, title):
        
        try:
            title = title.lower()  # convert all letters to lowercase
            title = re.sub(r'\(\d{4}\)', '', title)  # remove dates in parentheses
            title = ''.join(c for c in title if c.isalnum() or c.isspace())  # remove non-alphanumeric characters except spaces
            title = title.strip()  # remove leading and trailing spaces
        
        except:
            return 1
        
        return title
    
    def combination(self,string):
        combinations = []
        for i in range(len(string)):
            for j in range(i+1, len(string)+1):
                combinations.append(" ".join(string[i:j]))
                
        return combinations

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
        
        if '"' in preprocessed_input:
            pattern = r'"([^"]*)"'
            quoted_strings = re.findall(pattern, preprocessed_input) 
            movie_titles = [match.strip() for match in quoted_strings]
            
            return movie_titles
        
        
        else:
            # Split the string into words
            words = "".join(char for char in preprocessed_input if char.isalnum() or char.isspace())

                    
            words = words.lower().split()

            # Generate all possible combinations of words, respecting the order
            combinations = self.combination(words)
            movie_titles = []
        
            for movie in self.titles:
                transformed_title = self.transform_title(movie[0])
                if transformed_title in combinations:
                    movie_titles.append(transformed_title)
        
            return list(set(movie_titles))
    
    def transform_title(self, input_string):
       
        try:
            input_string_lower = self.remove_parenthesis(input_string.lower())
            
    
            if input_string_lower.endswith(', the'):
                new_title = 'the ' + input_string_lower[:-5]
            elif input_string_lower.endswith(', an'):
                new_title = 'an ' + input_string_lower[:-4]
            elif input_string_lower.endswith(', a'):
                new_title = 'a ' + input_string_lower[:-3]
            else:
                new_title = input_string_lower
                
            new_title = "".join(char for char in new_title if char.isalnum() or char.isspace())
        
        except:
            pass 

            
        return new_title

    def extract_year(self, input_string):
        # Match and extract the year in parentheses
        pattern = re.compile(r'\((\d{4})(?:[-\)])')
        match = pattern.search(input_string)
    
        if match:
            # If there's a match, extract the year and return it as an integer
            year = int(match.group(1))
        else:
            # If there's no match, return None
            year = None
    
        return year

    def remove_parenthesis(self, input_string):
        
         if not isinstance(input_string, (str, bytes)):
             return "error"


         else:
             transformed_string = re.sub(r'\([^)]*\)', '', input_string)
        

         return transformed_string.strip()

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
        

        
        found_titles = []
        
        if self.creative == False:
            
            # Get the part of the string that is outside the parenthesis
            title_without_par = self.remove_parenthesis(title)
            
            if title_without_par == "error":
                return []
            
            else:
            
                # Remove the, a, an from the string
                title_updated = self.transform_title(title_without_par)
                title_updated = title_updated.strip()
                
                # Extract the year from  the title 
                title_year = self.extract_year(title)
            
                for x in self.titles:
                    title_copy_without_par = self.remove_parenthesis(x[0])
                    title_copy = self.transform_title(title_copy_without_par)
                    
                    if title_updated == title_copy:
                        if title_year:
                            if str(title_year) in str(self.extract_year(x[0])):
                                found_titles.append(self.titles.index(x))
                        else:
                            found_titles.append(self.titles.index(x))  
        
        
        else:
            words_to_remove = ['the','an','a','la','le','die','das','der','el']
            dict_movies = defaultdict(list)
        
        
            # Modify movie names and generate the combinations
            for i, movie in enumerate(self.titles):
                transformed_title = self.light_transform(movie[0])
                combinations = self.combination(transformed_title.split())
                dict_movies[i] += combinations
            
            # Modify our input string
            words = self.light_transform(title)
            words = words.lower().split()
            words = [x for x in words if x not in words_to_remove]
            final_words = ' '.join(words)
            

            for i in dict_movies:
                if final_words in dict_movies[i]:
                    found_titles.append(i)
                
        return found_titles
    
    def tokenize(self,sentence):
            # Define a list of characters to be considered as delimiters
            delimiters = [" ", ".", ",", "!", "?", ";", ":", "\n"]
            
            # Tokenize the input string by splitting it based on the delimiters
            tokens = []
            current_token = ""
            for char in sentence:
                if char not in delimiters:
                    current_token += char
                else:
                    if current_token != "":
                        tokens.append(current_token)
                        current_token = ""
            
            # Append the last token if it exists
            if current_token != "":
                tokens.append(current_token)
                
            return tokens

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
        
        very_positive_words = ['adore', 'cherish', 'love', 'treasure', 'rejoice', 'delight', 'thrill', 'enchant', 'captivate', 'enrapture', 'wonderful', 'amazing', 'marvelous', 'terrific', 'fantastic', 'splendid', 'excellent', 'superb', 'magnificent', 'glorious']
        very_negative_words = ['despise', 'detest', 'loathe', 'abhor', 'disgust', 'revile', 'repudiate', 'reject', 'deplore', 'condemn', 'terrible', 'horrible', 'abominable', 'repulsive', 'vile', 'offensive', 'disgusting', 'atrocious', 'repugnant', 'detestable']
        
        string_without_quotes = re.sub('\".*?\"', '', preprocessed_input)
        tokens = self.tokenize(string_without_quotes)
        
        # Keep track of the sentiment score
        scores = []
        
        # Keep track of the positions of sentiments
        pos = 0
        
        # Keep track of the length of tokens
        i = 0
        
        reverse = 1
        while i < len(tokens):
            if tokens[i] in self.sentiment.keys():
                for j in range(i-1, i-pos, -1):
                    if any(substring in tokens[j] for substring in ("n't", "not", "never")):
                        reverse = -1
                if self.sentiment[tokens[i]] == "pos":
                    if (tokens[i] in very_positive_words) or ("really reeally" in string_without_quotes):
                        scores.append(2*reverse)
                    else:
                        scores.append(1*reverse)
                elif self.sentiment[tokens[i]] == "neg":
                    if (tokens[i] in very_negative_words) or ("really reeally" in string_without_quotes):
                        scores.append(-2*reverse)
                    else:
                        scores.append(-1*reverse)
                pos = 0
            elif tokens[i][0:-1] in self.sentiment.keys():
                copy = tokens[i][0:-1]
                for j in range(i-1, i-pos, -1):
                    if any(substring in tokens[j] for substring in ("n't", "not", "never")):
                        reverse = -1
                if self.sentiment[copy] == "pos":
                    if (copy in very_positive_words) or ("really reeally" in string_without_quotes):
                        scores.append(2*reverse)
                    else:
                        scores.append(1*reverse)
                elif self.sentiment[copy] == "neg":
                    if (copy in very_negative_words) or ("really reeally" in string_without_quotes):
                        scores.append(-2*reverse)
                    else:
                        scores.append(-1*reverse)
                pos = 0
            elif tokens[i][-2:] == "ed" and tokens[i][0:-2] in self.sentiment.keys():
                copy = tokens[i][0:-2]
                for j in range(i-1, i-pos, -1):
                    if any(substring in tokens[j] for substring in ("n't", "not", "never")):
                        reverse = -1
                if self.sentiment[copy] == "pos":
                    if copy in very_positive_words or "really reaally" in string_without_quotes:
                        scores.append(2*reverse)
                    else:
                        scores.append(1*reverse)
                elif self.sentiment[copy] == "neg":
                    if copy in very_negative_words or "really reaally" in string_without_quotes:
                        scores.append(-2*reverse)
                    else:
                        scores.append(-1*reverse)
                pos = 0
            else:
                pos += 1                
                
            i += 1
            reverse = 1
        
        if len(scores) == 1:
            return scores[0]
        elif sum(scores) >= 1:
            if any(num > 1 for num in scores):
                return 2
            else:
                return 1
        elif sum(scores) <= -1:
            if any(num < -1 for num in scores):
                return -2
            else:
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
        
        string_without_quotes = re.sub('\".*?\"', '', preprocessed_input)
        tokens = self.tokenize(string_without_quotes)
        
        # Keep track of the sentiment score
        scores = []
        
        # Keep track of the positions of sentiments
        pos = 0
        
        # Keep track of the length of tokens
        i = 0
        
        reverse = 1
        while i < len(tokens):
            if tokens[i] in self.sentiment.keys():
                for j in range(i-1, i-pos, -1):
                    if any(substring in tokens[j] for substring in ("n't", "not", "never")):
                        reverse = -1
                if self.sentiment[tokens[i]] == "pos":
                    scores.append(1*reverse)
                elif self.sentiment[tokens[i]] == "neg":
                    scores.append(-1*reverse)
                pos = 0
            elif tokens[i][0:-1] in self.sentiment.keys():
                copy = tokens[i][0:-1]
                for j in range(i-1, i-pos, -1):
                    if any(substring in tokens[j] for substring in ("n't", "not", "never")):
                        reverse = -1
                if self.sentiment[copy] == "pos":
                    scores.append(1*reverse)
                elif self.sentiment[copy] == "neg":
                    scores.append(-1*reverse)
                pos = 0
            elif tokens[i][-2:] == "ed" and tokens[i][0:-2] in self.sentiment.keys():
                copy = tokens[i][0:-2]
                for j in range(i-1, i-pos, -1):
                    if any(substring in tokens[j] for substring in ("n't", "not", "never")):
                        reverse = -1
                if self.sentiment[copy] == "pos":
                    scores.append(1*reverse)
                elif self.sentiment[copy] == "neg":
                    scores.append(-1*reverse)
                pos = 0
            else:
                pos += 1                
                
            i += 1
            reverse = 1
            
        if " but not " in string_without_quotes and len(scores) == 1:
            scores.append(scores[0]*-1)
            
            
        titles = self.extract_titles(preprocessed_input)
        
        if len(titles) == len(scores):
            return list(zip(titles, scores))
        elif len(titles) > len(scores) and len(scores) == 1:
            return list(zip(titles, scores*len(titles)))


    def levenshtein_distance(self, s, t):
        # Initialize a matrix of zeros with dimensions (len(s)+1) x (len(t)+1)
        d = [[0 for j in range(len(t)+1)] for i in range(len(s)+1)]
        
        # Populate the first row and column of the matrix
        for i in range(1, len(s)+1):
            d[i][0] = i
        for j in range(1, len(t)+1):
            d[0][j] = j
        
        # Iterate over the remaining cells of the matrix, computing the Levenshtein distance for each pair of substrings
        for j in range(1, len(t)+1):
            for i in range(1, len(s)+1):
                if s[i-1] == t[j-1]:
                    substitution_cost = 0
                else:
                    substitution_cost = 2
                d[i][j] = min(d[i-1][j] + 1,   # deletion
                              d[i][j-1] + 1,   # insertion
                              d[i-1][j-1] + substitution_cost)   # substitution
        
        # Return the Levenshtein distance between the two strings
        return d[len(s)][len(t)]          
        
        

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
        movies = []
        distances = [] 
        title = title.lower()
        for i in range(len(self.titles)):
            copy = self.remove_parenthesis(self.titles[i][0]).lower()
            distance = self.levenshtein_distance(title, copy)
            if distance <= max_distance:
                movies.append(i)
                distances.append(distance)
        results = []
        for i in range(len(movies)):
            if min(distances) == distances[i]:
                results.append(movies[i])
        
        return results
    
    def is_year(self, string):
        if string.isdigit() and len(string) == 4:
            return True
        else:
            return False

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
        results = []
        
        for candidate in candidates:
            if self.is_year(clarification):
                if str("(" + clarification + ")") in self.titles[candidate][0]:
                    results.append(candidate)                
            else: 
                if str(clarification) in self.remove_parenthesis(self.titles[candidate][0]):
                    results.append(candidate)
        return results
            
            

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
        # Compare each element of the input matrix to the threshold
        comparison = ratings > threshold

        # Create a new matrix filled with zeros and the same shape as the input matrix
        binarized_ratings = np.zeros_like(ratings)

        # Use NumPy's where() function to replace elements with 1 or -1 based on the comparison
        binarized_ratings = np.where(comparison, 1, binarized_ratings)  # set positive ratings to 1
        binarized_ratings = np.where(~comparison & (ratings != 0), -1, binarized_ratings)  # set negative ratings to -1
        # leave null ratings as 0


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
        norm_u_v = np.sqrt(np.dot(u, u) * np.dot(v, v))
        
        if norm_u_v == 0:
            return 0
        
        similarity = np.dot(u, v) / norm_u_v
        
        return similarity
    
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
        indices = []
        
        # Iterate over the user ratings
        for i in range(len(user_ratings)):
            
            # Insert zero recommendation for the movies the user has already rated
            if user_ratings[i] == 0:
                
                # Extract the row from the ratings matrix that corresponds to the unrated movie
                unrated_movie_vector = ratings_matrix[i, :].copy()
                
                # Temp variable for the prediction of rating
                predicted_rating = 0
                
                # Iterate over user ratings
                for rated_movie in range(len(user_ratings)):
                    
                    # Spot user's rated movies
                    if user_ratings[rated_movie] != 0 :
                        
                        # Compute similarity between the unrated movie and a rated movie
                        temp_similarity = self.similarity(unrated_movie_vector, ratings_matrix[rated_movie, :].copy())
                        
                        # Add to the weighted mean for the rating prediction
                        predicted_rating += temp_similarity*user_ratings[rated_movie]
                
                # Add the final prediction to the list of recommendations
                recommendations.append(predicted_rating)
                indices.append(i)
        
        k_highest_indices_sorted = sorted(indices, key=lambda x: -recommendations[indices.index(x)])

    
        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        return k_highest_indices_sorted[:k]

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
