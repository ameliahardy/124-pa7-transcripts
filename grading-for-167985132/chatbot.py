# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re
from io import open
import os
from porter_stemmer import PorterStemmer
from collections import defaultdict
import random

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'CutieBot'
        self.no_response = 0
        self.creative = creative
        self.user_movies = {}
        self.user_ratings = []
        self.vectorized_rating = []
        self.suggestions = []
        self.recommended_id = 0
        self.use_corrected = False
        self.closest_movie = []
        self.previous_line = ""
        self.should_recommend = False
        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings, 2.5)
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

        greeting_message = "Hello there, I'm CutieBot. I am a real movie fan. I can help you to find your next favorite movie. Would you like to watch a great movie tonight? If so, please answer yes but if not please enter :quit." 

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

        goodbye_message = "Oh alright then. Have a cute day!"

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
            self.no_response += 1
            if self.should_recommend:
                if ("yes" in line) or ("Yes" in line) or ("YES" in line):
                    return self.recommend_single_movie()
                else:
                    self.goodbye()

            if (("yes" in line) or ("Yes" in line) or ("YES" in line)) and self.no_response < 2:
                return "Great! Lets talk about movies. Please tell me about one movie you liked or disliked. Please write the movie title in quotes."
            
            if ('""' in line):
                return "Please write the name of the movie in single quotes"
            
            titles = self.extract_titles(line)

            if len(self.closest_movie) > 0:
                if ("yes" in line) or ("Yes" in line) or ("YES" in line):
                    titles = [self.closest_movie[0]]
                    line = self.previous_line
                else:
                    self.use_corrected = False
                    self.closest_movie = []
                    self.previous_line = ""
                    return "Oh okay. Then, tell me another movie."
                
            if(len(titles)) == 0:
                return self.confused_chatbot()
            elif(len(titles)) >= 2:
                return "Please take a deep breath and talk about only one movie at a time!"
            
            senti = self.extract_sentiment(line)

            for i in range(len(titles)):
                lst = self.find_movies_by_title(titles[i])
                if len(lst) == 0:
                    closest_movies = self.find_movies_closest_to_title(titles[i], max_distance=3)
                    self.closest_movie = self.titles[closest_movies[0]]
                    self.previous_line = line
                    if self.closest_movie == "":
                        return "I dont know that movie. I am so sorry! Would you care to talk about a different one?"
                    self.use_corrected = True
                    return "Did you mean {}?".format(self.closest_movie)

                if len(lst) >= 2:
                    respond = "I found multiple movies with that description. Please tell me if you meant: "
                    if(len(lst) < 7):
                        len_lst = len(lst)
                    else:
                        len_lst = 7
                    
                    for i in range(len_lst):  
                        respond += self.titles[lst[i]][0]
                        if (i+2 == (len(lst))):
                            respond += " or "
                        if (i < len(lst) -1):
                            respond += ", "
                    respond += "?"
                    return respond
            
                if lst[0] in self.user_movies:
                    return "You have already told this movie, tell me another movie!"

                if senti != 0:
                    self.user_movies[lst[0]] = senti

                if len(self.user_movies) > 1:
                    vectorized_ratings = np.zeros(len(self.titles))
                    for movie in self.user_movies:
                        vectorized_ratings[movie] = self.user_movies[movie]
                    self.suggestions = self.recommend(vectorized_ratings, self.ratings)
                    return self.recommend_single_movie()

                if (senti == 0):
                    return "Sorry I couldn't totally understand your emotions. Could you be more clear on this? Did you like or dislike the movie {}? ".format(self.titles[lst[0]][0])
                elif (senti > 0):
                    return self.positive_answer(self.titles[lst[0]][0])
                else:
                    return self.negative_answer(self.titles[lst[0]][0])
        
        else: 
            if self.should_recommend:
                if ("yes" in line) or ("Yes" in line) or ("YES" in line):
                    return self.recommend_single_movie()
                else:
                    self.goodbye()

            if (("yes" in line) or ("Yes" in line) or ("YES" in line)) and self.should_recommend:
                return "Great! Lets talk about movies. Please tell me about one movie you liked or disliked. Please write the movie title in quotes."
            
            if ('""' in line):
                return "Please write the name of the movie in single quotes"
            
            titles = self.extract_titles(line)

            if(len(titles)) == 0:
                return self.confused_chatbot()
            elif(len(titles)) >= 2:
                return "Please take a deep breath and talk about only one movie at a time!"
            senti = self.extract_sentiment(line)

            for i in range(len(titles)):
                lst = self.find_movies_by_title(titles[i])
                if len(lst) == 0:
                    return "I dont know that movie. I am so sorry! Would you care to talk about a different one?"
                if len(lst) >= 2:
                    respond = "I found multiple movies with that description. Please tell me if you meant: "
                    if(len(lst) < 7):
                        len_lst = len(lst)
                    else:
                        len_lst = 7
                    
                    for i in range(len_lst):  
                        respond += self.titles[lst[i]][0]
                        if (i+2 == (len(lst))):
                            respond += " or "
                        if (i < len(lst) -1):
                            respond += ", "
                    respond += "?"
                    return respond
            
                if lst[0] in self.user_movies:
                    return "You have already told this movie, tell me another movie!"

                if senti != 0:
                    self.user_movies[lst[0]] = senti

                if len(self.user_movies) > 1:
                    vectorized_ratings = np.zeros(len(self.titles))
                    for movie in self.user_movies:
                        vectorized_ratings[movie] = self.user_movies[movie]
                    self.suggestions = self.recommend(vectorized_ratings, self.ratings)
                    return self.recommend_single_movie()

                if (senti == 0):
                    return "Sorry I couldn't totally understand your emotions. Could you be more clear on this? Did you like or dislike the movie {}? ".format(self.titles[lst[0]][0])
                elif (senti > 0):
                    return self.positive_answer(self.titles[lst[0]][0])
                else:
                    return self.negative_answer(self.titles[lst[0]][0])

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return response

    def recommend_single_movie(self):
      self.should_recommend = True
      if self.recommended_id < len(self.suggestions):
        if self.recommended_id == 0:
            response = "CutieBot thinks that you will probably love \"{}\"! Would you like another recommendation? If so please tell yes, or tell :quit".format(self.titles[self.suggestions[0]][0])
            self.recommended_id += 1
            return response
        else:
            response = self.suggest_answer(self.titles[self.suggestions[self.recommended_id]][0])
            self.recommended_id += 1
            return response
      else:
        return "Sorry, I don't have any more recommendations!"
    
    def confused_chatbot(self):
        responses = [
                "I apologize, but as a movie recommender chatbot, I am only able to provide recommendations related to movies. Let's talk about a movie you watched recently.",
                "Unfortunately, I am not programmed to assist with that request. My specialty is movie recommendations.",
                "I'm sorry, but I'm not capable of providing assistance outside of movie recommendations. Is there a specific movie you're interested in?",
                "While I'd love to help, I'm only capable of providing recommendations related to movies. Tell me a movie you watched recently so I can suggest a great movie for you to watch?",
                "I apologize, but I am not able to provide assistance with that inquiry. However, I can recommend a movie that you might enjoy. Please tell me a movie you watched recently.",
                "I'm not able to provide assistance with that request, but I'd be happy to suggest a movie that matches your interests.  Please tell me a movie you watched recently.",
                "I'm sorry, but I'm not programmed to provide assistance for that inquiry. Would you like me to recommend a movie instead? If so, please tell me a movie you watched recently.",
                "While I can't help with that request, I'd love to recommend a great movie for you. What is your favorite movie?",
                "I apologize, but as a movie recommender chatbot, I am limited to providing recommendations related to movies. Can I suggest one for you? Help me with my suggestion by telling me a movie you watched recently.",
                "While I'm not able to assist with that particular question, I'm always happy to suggest a fantastic movie. Tell me one of your favorite movies!",
                  ]
        return random.choice(responses)
    
    def positive_answer(self, title):
        responses = [
            "I completely agree! {} was fantastic. What other movie do you like or dislike?".format(title),
            "Yes, {} was amazing! Tell me one more movie that you watched.".format(title),
            "I loved {} too! What's another movie that you have watched?".format(title),
            "Absolutely! {} was so well-made. What's another movie that you have watched?".format(title),
            "I'm with you on that one! {} was so captivating. What other movie have you seen recently?".format(title),
            "I couldn't agree more! {} was definitely one of my favorites. Have you seen any other great movie lately?".format(title),
            "{}  was incredible! What's another movie that you have watched?".format(title),
            "Totally agree! {} had me on the edge of my seat. What other movie have you watched?".format(title),
            "Yes, {} was so heartwarming. Tell me one more movie that you watched.".format(title),
            "I loved {} too! What's another movie that you have watched?".format(title),
                  ]
        return random.choice(responses)
    
    def negative_answer(self, title):
        responses = [
            "I totally get it. {} wasn't for everyone. Do you have any other movies in mind?".format(title),
            "I understand. {} wasn't really my cup of tea either. What other movie have you watched recently?".format(title),
            "Yeah, {} wasn't my favorite either. What other movie have you watched recently?".format(title),
            "I hear you. {} wasn't great. What's another movie that you have watched?".format(title),
            "I agree, {} wasn't the best. What other movie have you watched recently?".format(title),
            "I get where you're coming from. {} wasn't my favorite either. What is another movie that you thought were better?".format(title),
            "I can see why you didn't like {}. What's another movie that you have watched??".format(title),
            "I agree, {} wasn't the best. Do you have any other favorite?".format(title),
            "I understand why you didn't like {}. Tell me one more movie that you watched.".format(title),
            "I see your point. {} wasn't great. Tell me one more movie that you watched.".format(title),
                ]
        return random.choice(responses)

    def suggest_answer(self, title):
        responses = [
                "Another movie you might like is {}. Would you like another recommendation? If so, please say yes or type :quit.".format(title),
                "Have you seen {}? I think you might enjoy it. Would you like me to suggest another movie? If so, please say yes or type :quit.".format(title),
                "Another great movie is {}. Would you like me to suggest another one? If so, please say yes or type :quit.".format(title),
                "I think you would enjoy {} if you haven't already seen it. Would you like another recommendation? If so, please say yes or type :quit.".format(title),
                "I recommend checking out {} if you haven't seen it yet. Would you like another recommendation? If so, please say yes or type :quit.".format(title),
                "Another movie you might like is {}. Do you want me to suggest another one? If so, please say yes or type :quit.".format(title),
                ]
        return random.choice(responses)
  
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
        movie_titles = []
        pattern = r'\"([^\"]*)\"'
        matches = re.findall(pattern, preprocessed_input)
        for match in matches:
            movie_titles.append(match)

        if self.creative and len(matches) == 0:  # creative mode, movies without quotation marks and correct capitalization (ONLY)
            articles = ['a', 'an', 'the']
            lowered_input = preprocessed_input.lower()
            tokenized_input = lowered_input.split(' ')

            for i in range(len(tokenized_input)):  # strip any punctuation from input
                tokenized_input[i] = tokenized_input[i].strip('.,?!:;')

            for i in range(len(self.titles)):  # iterate through each movie
                candidate_title = self.titles[i][0].lower()
                truncated_candidate = candidate_title[:candidate_title.find("(")].strip()  # no date

                tokenized_candidate = truncated_candidate.split(' ')
                for i in range(len(tokenized_candidate)):
                    tokenized_candidate[i] = tokenized_candidate[i].strip(',.?!;:')  # strip any punctuation
                    if tokenized_candidate[i] in articles:  # get rid of articles
                        tokenized_candidate[i] = ''

                while '' in tokenized_candidate:  # get rid of residue of articles
                    tokenized_candidate.remove('')
                
                if len(tokenized_candidate) == 1:  # for single-word candidate titles
                    if (tokenized_candidate[0] in tokenized_input):
                        movie_titles.append(truncated_candidate)
                elif len(tokenized_candidate) > 1:  # for multi-word candidate titles
                    count_found = 0
                    for token in tokenized_candidate:
                        if token in tokenized_input:
                            count_found += 1
                    if count_found == len(tokenized_candidate):
                        movie_titles.append(truncated_candidate)           
        return movie_titles

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
        movie_match = []
        articles = {"an", "a", "the"} if not self.creative else {
            "an", "a", "the", "der", "die", "das",
            "ein", "eine", "einer", "eines", "einem", "einen",
            "la", "le", "en", "et", "les", "ces", "des", "el"
        }
        title = title.lower()
        titles = [title]
        tokens = title.split()
        new_title = " ".join(tokens[1:]) + ", " + tokens[0] if tokens[-1][0] != "(" else " ".join(tokens[1:-1]) + ", " + \
                                                                                         tokens[0] + " " + tokens[-1]
        titles.append(new_title) if tokens[0].lower() in articles else None
        for index, movie_title in enumerate(self.titles):
            movie_title = movie_title[0].lower()
            truncated_title = movie_title[:movie_title.find("(")].strip()
            alternate_titles = re.findall(r"\(([^)]+)\)", movie_title)
            regex_pattern = r"{}[^a-zA-Z$]".format(re.escape(title))
            for search_term in titles:
                match_found = False
                if search_term == truncated_title or search_term == movie_title:
                    movie_match.append(index)
                    match_found = True
                elif alternate_titles and self.creative:
                    for alias in alternate_titles:
                        alias = re.sub(r"\ba\.?k\.?a\.?\b", ' ', alias).strip()
                        if alias == search_term:
                            movie_match.append(index)
                            match_found = True
                if self.creative and not match_found and re.search(regex_pattern, movie_title):
                    movie_match.append(index)
        indices = list(set(movie_match))
        return indices

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
        stemmer = PorterStemmer()
        
        # stemmed version of the sentiment dictionary
        stemmed_key = {}
        for sentiment_word in list(self.sentiment.keys()):
            stemmed_key[stemmer.stem(sentiment_word)] = self.sentiment[sentiment_word]
        stemmed_input = []
        
        # remove all movie titles (since movie titles can include sentiment words)
        pattern = r'(\"[^\"]*\")'
        movie_titles = re.findall(pattern, preprocessed_input)
        sentiment_only = preprocessed_input.strip(".!?,")
        for title in movie_titles:
            sentiment_only = sentiment_only.replace(title, "")
        
        # use porter stemmer to find sentiments
        tokenized_input = sentiment_only.split(" ")
        if '' in tokenized_input: tokenized_input.remove('')
        for token in tokenized_input:
            token = token.strip(".!?,")
            stemmed_input.append(stemmer.stem(token))
        
        # set up negations 
        negations = ['didn\'t', 'not', 'never']
        not_sentiment = 0
        sentiment_count = 0
        negated = False
        negation_count = 0

        # categorize sentiments
        for i in range(len(stemmed_input)):
            if stemmed_input[i] in negations:
                negated = not negated
                negation_count += 1
            elif stemmed_input[i] not in list(stemmed_key.keys()):
                not_sentiment += 1
            elif stemmed_key[stemmed_input[i]] == 'pos':
                if not negated:
                    sentiment_count += 1
                else: 
                    sentiment_count -= 1
                    negated = False
            elif stemmed_key[stemmed_input[i]] == 'neg':
                if not negated:
                    sentiment_count -= 1
                else:
                    sentiment_count += 1
                    negated = False
        
        if not_sentiment == len(stemmed_input): 
            return 0
        
        if self.creative and (negation_count == 0):  # for creative mode
            if sentiment_count <= 0:
                return -2
            else: 
                return 2
        else:
            if sentiment_count <= 0: 
                return -1
            else: 
                return 1


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
    
        quoted_pattern = r'"([^"]+)"'  
        conjunction_pattern = r'\b(and|or|but|yet|nor)\b'  
        movies = re.findall(quoted_pattern, preprocessed_input)
        conjunctions = re.findall(conjunction_pattern, preprocessed_input)
        sentiments = []

        reverse = ["nor"]
        both = ["and", "or"]
        negative = ["yet", "but"]
        sentiment = self.extract_sentiment(preprocessed_input)
        if conjunctions[0] in both:
            sentiments.append((movies[0], sentiment))
            sentiments.append((movies[1], sentiment))
        elif conjunctions[0] in negative:
            sentiments.append((movies[0], sentiment))
            sentiments.append((movies[0], -sentiment))
        elif conjunctions[0] in reverse:
            sentiments.append((movies[0], -sentiment))
            sentiments.append((movies[1], -sentiment))

        return sentiments

    def calculateMinEditDist(self, given_title, len_i, potential, len_j):
        """ Helper function for find_movies_closest_to_title (created by Sara)
            returns the minimum edit distance between two given strings using
            algorithm from Week1 lecture videos
        """
        matrix = self.initializeMatrix(len_i, len_j)
        for i in [n+1 for n in range(len_i)]:
            for j in [m+1 for m in range(len_j)]:
                if given_title[i - 1] == potential[j - 1]:
                    matrix[i][j] = matrix[i - 1][j - 1]
                else:
                    matrix[i][j] = min(matrix[i][j - 1] + 1, matrix[i - 1][j] + 1, matrix[i - 1][j - 1] + 2)
        return matrix[len_i][len_j]


    def initializeMatrix(self, len_i, len_j):
        matrix = [[0 for x in range(len_j + 1)] for y in range(len_i + 1)]
        for i in range(len_i + 1):
            for j in range(len_j + 1):
                if i == 0:
                    matrix[i][j] = j
                elif j == 0:
                    matrix[i][j] = i
        return matrix
        

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
        closest = []
        for index, potential_title in enumerate(self.titles):

            articles = ['an', 'a', 'the']
            candidate_title = potential_title[0].lower()
            truncated_candidate = candidate_title[:candidate_title.find("(")].strip()  # no date
            tokenized_title = truncated_candidate.split(' ')
            for i in range(len(tokenized_title)):
                tokenized_title[i] = tokenized_title[i].strip(',.?!;:')  # strip any punctuation
                if tokenized_title[i] in articles:  # get rid of articles
                    tokenized_title[i] = ''
            while '' in tokenized_title:  # get rid of residue of articles
                tokenized_title.remove('')
            candidate = ' '.join(tokenized_title) 

            edit_distance = self.calculateMinEditDist(title.lower(), len(title), candidate, len(candidate))
            if edit_distance <= max_distance:
                closest.append((edit_distance, index))
            
            closest.sort()  # min distances to the front
            final_closest = []
            if len(closest) > 0:
                min_possible_dist = closest[0][0]
            for movie_dist in closest:
                if movie_dist[0] == min_possible_dist:
                    final_closest.append(movie_dist[1])  # append the index
                else:
                    # since list is sorted, no more potential candidates
                    break
        return final_closest


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
        index = []
        clarification = clarification.upper()
        for movie in candidates:
            title = self.titles[movie][0].upper()
            alternative_names = re.findall(' \(.[^\)\(]*\)', title)
            title = re.sub(r'\([^)]*\)','', title)

            for i in range(len(alternative_names)):
                #get whatever is inside the brackets
                alternative_names[i] = re.search(r'\((.*?)\)', alternative_names[i]).group(1)
                alternative_names[i] = re.sub('AKA ', '', alternative_names[i])
            
            if(clarification in title) or (clarification in alternative_names):
                index.append(movie)

        if clarification.isdigit() and int(clarification) <=len(candidates):
            index.append(candidates[int(clarification) - 1])
        
        
        if (re.search('(\W|^)(FIRST|1ST)(\W|$)', clarification)) and len(candidates) >= 1:
            index = [candidates[0]]
        elif re.search('(\W|^)(SECOND|2ND)(\W|$)', clarification) and len(candidates) >= 2:
            index = [candidates[1]]
        elif re.search('(\W|^)(THIRD|3RD)(\W|$)', clarification) and len(candidates) >= 3:
            index = [candidates[2]]
        elif re.search('(\W|^)(FOURTH|4TH)(\W|$)', clarification) and len(candidates) >= 4:
            index = [candidates[3]]
        elif re.search('(\W|^)(FIFTH|5TH)(\W|$)', clarification) and len(candidates) >= 5:
            index = [candidates[4]]
        elif re.search('(\W|^)(SIXTH|6TH)(\W|$)', clarification) and len(candidates) >= 6:
            index = [candidates[5]]
        elif re.search('(\W|^)(SEVENTH|7TH)(\W|$)', clarification) and len(candidates) >= 7:
            index = [candidates[6]]
        elif re.search('(\W|^)(EIGHTH|8TH)(\W|$)', clarification) and len(candidates) >= 8:
            index = [candidates[7]]
        elif re.search('(\W|^)(NINTH|9TH)(\W|$)', clarification) and len(candidates) >= 9:
            index = [candidates[8]]
        elif re.search('(\W|^)(TENTH|10TH)(\W|$)', clarification) and len(candidates) >= 10:
            index = [candidates[9]]

        if not index:
            return candidates
        else:
            return index

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
        above_threshold = ratings > threshold
        at_or_below_threshold = ratings <= threshold
        binarized_ratings = np.full_like(ratings, -1)
        binarized_ratings[above_threshold] = 1
        binarized_ratings[at_or_below_threshold] = -1
        binarized_ratings[ratings == 0] = 0
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
        dot_product = np.dot(u, v)
        dot_product = dot_product.astype(float)
        norm_u = np.linalg.norm(u)
        norm_v = np.linalg.norm(v)
        similarity = dot_product / (norm_u * norm_v)
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

        movies_seen = np.where(user_ratings != 0) 
        ratings_seen = ratings_matrix[movies_seen]

        #Get cosine similarity between what user has rated and everything else
        similarity = (ratings_seen @ ratings_matrix.T)
        similarity = np.float64(similarity)

        #Normalize
        rat_matx_norm = np.linalg.norm(ratings_matrix, axis=1)
        rat_seen_norm = np.linalg.norm(ratings_seen, axis=1)

        r = similarity.shape[0]
        c = similarity.shape[1]
        for i in range(r):
            if rat_seen_norm[i] != 0: 
                similarity[i,:] = similarity[i,:] / rat_seen_norm[i]
            else:
                similarity[i:] = 0
        for j in range(c):
            if rat_matx_norm[j] != 0: 
                similarity[:,j] = similarity[:,j] / rat_matx_norm[j]
            else:  
                similarity[:,j] = 0

        user_rat_seen = user_ratings[movies_seen]
        total_ratings = (similarity.T @ user_rat_seen)

        total_ratings[movies_seen] = -np.inf
        
        indices = list(range(len(total_ratings)))
        sorted_indices = sorted(indices, key=lambda i: -total_ratings[i])
        recommendations = sorted_indices[:k]
            
        # #############################################################################
        # #                             END OF YOUR CODE                              #
        # #############################################################################
        return recommendations[:k]

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
        This chatbot, CutieBot tries to get to know its users by prompting them
        for movies they liked and did not like. CutieBot first detects the names 
        of movies that are mentioned in the user's text. Then, it acknowledges 
        the negative or positive or neutral sentiment towards the movie that is 
        felt by the user. Finally, it tries to produce the best recommendation 
        for the next movie the user should watch.
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
