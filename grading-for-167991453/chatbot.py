# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import re
import numpy as np
import string
from porter_stemmer import PorterStemmer
import re
import math
import random


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'Netflixer'
        self.n_movies_named = 0
        self.user_ratings = np.zeros(9125)
        self.recommended_movies = []
        self.recommended_movie_curr_index = 0

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
        self.ratings = self.binarize(ratings)
        self.ps = PorterStemmer()
        
        stemmed = {}
        for key in self.sentiment:
            key2 = self.ps.stem(key)
            stemmed[key2] = self.sentiment[key]
        self.sentiment = stemmed
        #print(self.sentiment)
        """
        self.pos_words = []
        pos_words_file = open('data/positive-words.txt', 'r')
        lines = pos_words_file.readlines()
        for line in lines:
            cur_line = self.ps.stem(line.strip())
            #if cur_line in self.sentiment:
             #   continue
            self.pos_words.append(cur_line)
            
        self.neg_words = []
        neg_words_file = open('data/negative-words.txt', 'r')
        lines = neg_words_file.readlines()
        for line in lines:
            cur_line = self.ps.stem(line.strip())
            #if cur_line in self.sentiment:
             #   continue
            self.neg_words.append(cur_line)
        """
        
        afinn = open('deps/afinn.txt', 'r')
        lines = afinn.readlines()
        white_str = list(string.whitespace)  
        self.afinn_words = {}
        for line in lines:
            #print(line)
            x = [splits for splits in line.strip().split(" ") if splits]
            #print(x)
            num = int(x[len(x) - 1])
            """
            if num > 2:
                num = 2
            if num < -2:
                num = -2
            """
            self.afinn_words[self.ps.stem(x[0])] = num
        #print(self.afinn_words["terribl"])
        
        negation_file = open('deps/negations.txt', 'r')
        lines = negation_file.readlines()
        
        self.negations = []
        for line in lines:
            self.negations.append(line.strip())
        #print(self.negations)
      
        
        
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

        greeting_message = "Hello, how can I help you today?"

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

    def process_dialogue_phrase(self, match):
        phrase = match.lower()
        pattern = r"\bmy\b"
        phrase = re.sub(pattern, "jkfgh", phrase)
        pattern = r"\bme\b"
        phrase = re.sub(pattern, "jkfgl", phrase)
        pattern = r"\byou\b"
        phrase = re.sub(pattern, "me", phrase)
        pattern = r"\byour\b"
        phrase = re.sub(pattern, "my", phrase)
        pattern = r"\bjkfgh\b"
        phrase = re.sub(pattern, "your", phrase)
        pattern = r"\bjkfgl\b"
        phrase = re.sub(pattern, "you", phrase)
        return phrase

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
        
        n = 4
        liked_prefix_phrases = ["Nice! You liked ", "Good choice that you liked ", "I see, you enjoyed ", "So, you loved ", "It's awesome that you were entertained by "]
        disliked_prefix_phrases = ["I understand that you did not like ", "Hmm. I'm sorry to hear that you hated ", "I understand that you did not really enjoy ", "So it was not fun to watch ", "That's unfortunate that you did not take a pleasing to "]
        neutral_prefixes = ["Sorry, I am not sure whether or not you liked ", "Just to clarify, you did not like ", "Could you repeat that please? I did not understand how you felt about ", "Damn it! I did not get that. Did you or did you not like ", "I am afraid I am not certain as to whether or not you enjoyed "]
        # index 1 and 3 have question marks
        neutral_suffixes = ["Enlighten me some more.", "Could you clarify?", "Did you like it?...", "Please expound.", "Tell me :)"]
        suffix_phrases = ["Please tell me more.", "I'd love to hear about some more movies.", "What other movies did you have in mind?", "Please tell me about another movie you liked or disliked", "What other movie have you had the pleasure of seeing?"]
        recommendation_phrases = ["Ummmm. I would suggest {movie}! You're gonna love it. Would you like another recommendation?", "Well here is another one then, you might like {movie}. Do you want another recommendation?", "I got {movie} for you. Keep going?", "Check out the classic {movie}. It will blow your mind, I believe. More recommendations?", "Watch this: {movie}. This is a good one based on your preferences. More suggestions?"]

        line = self.preprocess(line)
        response = ""

        if self.n_movies_named >= 5:
            #
            if "no" in line.lower():
                return "Alright then. Nice chat. Stay in touch !!"
            else:
                # If I run out of recommendations, fetch more and keep going
                if len(self.recommended_movies) == self.recommended_movie_curr_index:
                    recommended_movies = self.recommend(self.user_ratings, self.ratings, self.recommended_movie_curr_index * 2, False)
                    self.recommended_movies = recommended_movies

                movie = self.titles[self.recommended_movies[self.recommended_movie_curr_index]][0]
                response = recommendation_phrases[random.randint(0, n)].format(movie=movie)
                self.recommended_movie_curr_index += 1
                return response

        titles = self.extract_titles(line)
        if len(titles) == 0:
            #no movie mentioned

            #handle what is and can you questions
            if self.creative:
                raw_line = line.strip().lower()

                #what is 
                pattern = r"(?:(?:what)[^A-Za-z0-9]+(?:is\s)([\w|\s]+)[\?]?)"
                #pattern = r"whats\s([\w|\s]+)[\?]?"
                matches = re.findall(pattern, raw_line)
                if len(matches) == 0:
                    #what's
                    pattern = r"(?:whats\s([\w|\s]+)[\?]?)"
                    matches = re.findall(pattern, raw_line)
                if len(matches) != 0:
                    #match = re.sub(pattern, "", preprocessed_input)
                    phrase = self.process_dialogue_phrase(matches[0])
                    return [f"I really wish I knew what {phrase} is but I can only help with movies if you tell them to me and whether or not you liked them.", f"I don't really know what {phrase} is but I would love for you to tell me about movies."][random.randint(0,1)]
                
                
                #can you
                pattern = r"(?:(?:can)[^A-Za-z0-9]+(?:you\s)([\w|\s]+)[\?]?)"
                matches = re.findall(pattern, raw_line)
                if len(matches) != 0:
                    phrase = self.process_dialogue_phrase(matches[0])
                    return [f"I don't think I can {phrase} but I can definitely help with movies", f"How about we switch from how I can {phrase} and talk about movies you like?"][random.randint(0,1)]
            
                #handle I am ... emotion 
                #pattern = r"(?:(?:i)[^A-Za-z0-9]+(?:you\s)([\w|\s]+)[\?]?)"
                pattern = r"i\sam\s(([\w|\s]+)[.]?)"
                matches = re.findall(pattern, raw_line)
                if len(matches) == 0:
                    pattern = r"im\s(([\w|\s]+)[.]?)"
                    matches = re.findall(pattern, raw_line)
                if len(matches) != 0:
                    sentiment = self.extract_sentiment(line)
                    phrase = self.process_dialogue_phrase(matches[0][0].strip())
                    if sentiment == 0:
                        #neutral
                        return f"I think it is interesting that you are {phrase} on this fine day. Much as I would like to chat about that, my expertise is in movies."
                    elif sentiment > 0:
                        #positive
                        return f"Way to go!! It's awesome being {phrase}. I would be jealous if I could!"
                    else:
                        #negative
                        return f"Oh no! I am so sad to hear that. I apologize if I had anything to do with you being {phrase}. I only want to help."
                    # return "sentiment is " + str(sentiment)

            return ["I don't quite get that. Please tell me about some movies you have seen", "Hmm. I am not sure I got that. I would love to talk about movies though. Could you tell me about some you have seen?",  "Hm, that's not really what I want to talk about right now, let's go back to movies", "Unfortunately I am only able to help with movies. Could you tell me about one you've seen?", "Gotcha! Unfortunately I can only help with movies. Tell me about one :)" ][random.randint(0,4)]
        if len(titles) > 1:
            # more than one movie mentioned
            if self.creative:
                sentimented_movies = self.extract_sentiment_for_movies(line)
                if len(sentimented_movies) == 0:
                    #no movie
                    return "I did not find a matching movie from the titles you gave. Could you check and try again?"
                multiple_movie_response = ""
                for i in range(len(sentimented_movies)):
                    # exactly one movie
                    sentiment = sentimented_movies[i][1]
                    title = sentimented_movies[i][0]
                    movie_indexes = self.find_movies_by_title(title)
                
                    if len(movie_indexes) == 0:
                        #no movie with this name
                        multiple_movie_response += " " + [f"I couldn't find the movie {title}. Could you check and try again? Or tell me about another movie?", f"Damn it! I do not seem to have {title} in my database."][random.randint(0,1)]
                        continue
                    if len(movie_indexes) == 1:
                        #just one movie find sentiment
                        if sentiment == 1:
                            response = liked_prefix_phrases[random.randint(0,n)] + f"{title}. "
                            multiple_movie_response += " " + response
                            self.n_movies_named += 1
                            self.user_ratings[movie_indexes[0]] = 1
                        elif sentiment == -1:
                            response = disliked_prefix_phrases[random.randint(0,n)] + f"{title}. "
                            multiple_movie_response += " " + response
                            self.n_movies_named += 1
                            self.user_ratings[movie_indexes[0]] = -1
                        else:
                            p = random.randint(0,n)
                            if p % 2 == 1:
                                response = neutral_prefixes[p] + f"{title}? "
                                multiple_movie_response += " " + response
                            else:
                                response = neutral_prefixes[p] + f"{title}. "
                                multiple_movie_response += " " + response
                    else:
                        # multiple options hence get clarification
                        multiple_movie_response += " " + [f"There seems to be several matches to {title}. Would you be more specific?", f"I can see several movies with the title {title}. Could you please give me more information?"][random.randint(0,1)]
                if len(multiple_movie_response) > 0:
                    return multiple_movie_response
            return ["Please tell me about one movie at a time if you would.", "I'm so sorry but I can only handle one movie at a time. Could you tell me about one of these?"][random.randint(0,1)]

        sentiment = self.extract_sentiment(line)
        title = titles[0]

        movies = self.find_movies_by_title(title)

        if len(movies) == 0:
            #no movie with this name
            return [f"I couldn't find the movie {title}. Could you check and try again? Or tell me about another movie?", f"Damn it! I do not seem to have {title} in my database. My apologies, could you tell me about another one?"][random.randint(0,1)]
        if len(movies) == 1:
            #just one movie find sentiment
            if sentiment == 1:
                response = liked_prefix_phrases[random.randint(0,n)] + f"{title}. " + suffix_phrases[random.randint(0,n)]
                self.n_movies_named += 1
                self.user_ratings[movies[0]] = 1
            elif sentiment == -1:
                response = disliked_prefix_phrases[random.randint(0,n)] + f"{title}. " + suffix_phrases[random.randint(0,n)]
                self.n_movies_named += 1
                self.user_ratings[movies[0]] = -1
            else:
                p = random.randint(0,n)
                if p % 2 == 1:
                    response = neutral_prefixes[p] + f"{title}? " + neutral_suffixes[random.randint(0,n)]
                else:
                    response = neutral_prefixes[p] + f"{title}. " + neutral_suffixes[random.randint(0,n)]
        else:
            # multiple options hence get clarification
            return [f"There seems to be several matches to {title}. Would you be more specific?", f"I can see several movies with the title {title}. Could you please give me more information?"][random.randint(0,1)]

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        if len(response) == 0:
            return "Hmm, I seem to have had difficulty understanding that. Mind rephrasing?"
        if self.n_movies_named == 5:
            recommended_movies = self.recommend(self.user_ratings, self.ratings, 5, False)
            self.recommended_movies = recommended_movies
            self.recommended_movie_curr_index = 0
            response = f"Voila! That's enough for me to make a recommendation. I would recommend {self.titles[recommended_movies[self.recommended_movie_curr_index]][0]}. Would you fancy another recommendation?"
            self.recommended_movie_curr_index += 1
            #  CONTINUE FROM HERE !!!
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
        # leave this method unmodified.                                     #
        ########################################################################

        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################
        altered = text.replace("'", "")
        altered = altered.replace(".", "")
        altered = altered.replace("!", "")
        #altered = altered.replace(",", "")

        
        return altered

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
        movie_list = []
        movie_pattern = '"(.*?)"'
        #Find matches
        movie_matches = re.findall(movie_pattern, preprocessed_input)
        movies_list = []
        #iterate over the matches
        for match in movie_matches:
            movies_list.append(match)
        
        return movies_list

        


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
        tokens = re.sub(r'[^\w\s]', '', title).strip().split() #separate by spacing
        token_set_no_year = set([t for t in tokens if not re.findall(r"\b\d{4}\b", t)])
        token_set_year  = set([t for t in tokens])
        has_year = True if re.findall(r"\b\d{4}\b", title) else False
        token_set = token_set_year if has_year else token_set_no_year
        for i in range(len(self.titles)):
            title_tokens = re.sub(r'[^\w\s]', '', self.titles[i][0]).strip().split()
            lower_title_tokens = [t for t in title_tokens ]
            """" 
            If the title does not have a year included, then we should disregard the year
            in the search title 
            """
            if not has_year:
                lower_title_tokens =  [t for t in title_tokens if not re.findall(r"\b\d{4}\b", t)]
            lower_title_set = set(lower_title_tokens)
            # if creative mode is on, relax some constraints
            should_add = token_set.issubset(lower_title_set) if self.creative else lower_title_set == token_set
            if should_add:
                res.append(i)
            #DOES THIS RESPECT ORDER???
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
        pattern =r"\".+\"" #r"([^\"]*(?:\".+\"))"
        match = re.sub(pattern, "", preprocessed_input)
        
        #tokenized = preprocessed_input.split('"')
        
        keywords = match #tokenized[0]+tokenized[2]
        key_tokens = keywords.split()

        
        total = 0
        negation = 1
        really = 1
        
        #print(preprocessed_input)

        for i in range(len(key_tokens)):
            
            if key_tokens[i] in self.negations:
                negation = -1
                continue
                
            if key_tokens[i].lower() == "really":
                really = 2
                continue
            
            stemmed = self.ps.stem(key_tokens[i])
            if stemmed in self.afinn_words:
                total += (self.afinn_words[stemmed]*negation*really)
                negation = 1
                really = 1
                
            
            """
            if stemmed in self.sentiment:
                if self.sentiment[stemmed] == "pos":
                    if negation:
                        total -= 1
                        negation = False
                    else:
                        total += 1
                else:
                    if negation:
                        total += 1
                        negation = False
                    else:
                        total -= 1
            """       

            
        if not self.creative:
            if total > 1:
                total = 1
            elif total < -1:
                total = -1
        else:
            if total > 2:
                total = 2
            elif total < -2:
                total = -2
            
        #print("---")
        #print(total)
        #print("---")
        return total

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
        
        key_tokens = []
        titles = []
        cur_str = ""
        title = False
        title_count = 0
        for char in preprocessed_input:
            if char == '"' and not title:
                if cur_str != "":
                    key_tokens += cur_str
                    cur_str = ""
                
                title = True
                cur_str += char
                continue
            if char == '"' and title:
                title = False
                cur_str += char
                cur_str += ";"
                titles += cur_str
                cur_str = ""
                key_tokens.append(str(title_count))
                title_count += 1
                continue
            
            cur_str += char
        
        if cur_str != "":
            key_tokens += cur_str
        
        key_tokens = ''.join(key_tokens).split(" ")
        while "" in key_tokens:
            key_tokens.remove("")
            
        titles = ''.join(titles).replace('"','').split(";")
        while "" in titles:
            titles.remove("")
        
      
        #combined_sentiment = ["both","either", "and"]
        separate_sentiment = ["but", "however"]
        
        really = 1
        negation = 1        
        sentiment_arr = []
        prev_sentiment = 0
        cur_sentiment = 0
        cur_movie = -1
        film_cache = 0

        for i in range(len(key_tokens)):

            if key_tokens[i] in self.negations:
                negation = -1
                continue

            if key_tokens[i] == "really":
                really = 2
                continue
                
            if key_tokens[i] in separate_sentiment:
                if film_cache > 0:
                    temp = 0
                    while temp < film_cache:
                        sentiment_arr.append(cur_sentiment)
                        temp += 1

                    cur_sentiment = 0
                    film_cache = 0
                    continue
                
                if cur_movie != -1:
                    sentiment_arr.append(cur_sentiment)
                
                cur_movie = 1
                prev_sentiment = cur_sentiment
                cur_sentiment = 0
             
            if any(char.isdigit() for char in key_tokens[i]) and cur_movie == -1:
                if cur_sentiment != 0:
                    sentiment_arr.append(cur_sentiment*really*negation)
                    negation = 1
                    really = 1
                    prev_sentiment = cur_sentiment
                    cur_sentiment = 0

                elif prev_sentiment != 0:
                    sentiment_arr.append(prev_sentiment*really*negation)
                    negation = 1
                    really = 1
                    cur_movie = -1
                else:
                    film_cache += 1

   
            stemmed = self.ps.stem(key_tokens[i].replace(",",""))
            if stemmed in self.afinn_words:
                cur_sentiment += self.afinn_words[stemmed]*negation*really
                negation = 1
                really = 1              
           

            
        if cur_movie != -1 and cur_sentiment != 0 and len(titles) != len(sentiment_arr):
            sentiment_arr.append(cur_sentiment*really*negation)
                
        elif cur_movie == -1 and cur_sentiment != 0 and len(titles) != len(sentiment_arr):
            while len(titles) != len(sentiment_arr):
                sentiment_arr.append(cur_sentiment*really*negation)
        
        elif really != 1 or negation != 1:
            sentiment_arr.append(sentiment_arr[len(sentiment_arr)-1]*really*negation)
   
        final = []

        for i in range(len(sentiment_arr)):
            if sentiment_arr[i] > 1:
                sentiment_arr[i] = 1
            elif sentiment_arr[i] < -1:
                sentiment_arr[i] = -1
            
            temp_tup = (titles[i], sentiment_arr[i])
            final.append(temp_tup)

            
        return final

    
    # def find_movies_closest_to_title(self, title, max_distance=3):
    #     """Creative Feature: Given a potentially misspelled movie title,
    #     return a list of the movies in the dataset whose titles have the least
    #     edit distance from the provided title, and with edit distance at most
    #     max_distance.

    #     - If no movies have titles within max_distance of the provided title,
    #     return an empty list.
    #     - Otherwise, if there's a movie closer in edit distance to the given
    #     title than all other movies, return a 1-element list containing its
    #     index.
    #     - If there is a tie for closest movie, return a list with the indices
    #     of all movies tying for minimum edit distance to the given movie.

    #     Example:
    #       # should return [1656]
    #       chatbot.find_movies_closest_to_title("Sleeping Beaty")

    #     :param title: a potentially misspelled title
    #     :param max_distance: the maximum edit distance to search for
    #     :returns: a list of movie indices with titles closest to the given title
    #     and within edit distance max_distance
    #     """

    #     return []

    """
    Given two strings, we return the edit distnce between the two strings using Levenshtein's Algorithm
    :param1 str1: first string input
    :param2 str2: the second string input
    return: an int which is the minimum edit_distance btn str1 and str2
    """
    def edit_distance(self,str1, str2):
        #init Levenshtein Matrix
        m, n = len(str1), len(str2)
        #List comprehension for 2D matrix
        lev_matrix = [[0 for j in range(n+1)] for i in range(m+1)]
        #init edges of lev_matrix
        lev_matrix[0] = list(range(n + 1))
        for i in range(m + 1):
            lev_matrix[i][0] = i
        
        #Fill in the matrix now
        for i in range(1, m+1):
            for j in range(1, n+1):
                if str1[i-1] == str2[j-1]:
                    lev_matrix[i][j] = lev_matrix[i-1][j-1]
                else:
                    lev_matrix[i][j] = 1 + min(lev_matrix[i-1][j], lev_matrix[i][j-1], lev_matrix[i-1][j-1])

        #When done with the dynamic programming return the bottom-right cell
        return lev_matrix[m][n]
        

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
        
        close_movies = []
        #keeps track of the min edit distance so far
        min_distance_soFar = max_distance + 1
        #Loop over the movie in the dataset and compare
        # edit distance with the mispelled title
        for i, movie_title in enumerate (self.titles):
            dataset_movie = re.sub(r'\b\d{4}\b', "", self.titles[i][0]).strip("()").strip(" ").lower()
            #Compute edit distance
            clean_title = title.lower()
            distance = self.edit_distance(dataset_movie, clean_title)

            if distance <= max_distance:
                if distance < min_distance_soFar:
                    #update min_distance_soFar
                    min_distance_soFar = distance 
                    #replaces any previous contents of 
                    #close_movie with this new closest movie index.
                    close_movies = [i] 

                elif distance == min_distance_soFar:
                    close_movies.append(i)
        return close_movies



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
        binarized_ratings = ratings
        binarized_ratings[binarized_ratings == 0] = 40
        binarized_ratings[binarized_ratings<=threshold ] = -1
        binarized_ratings[binarized_ratings == 40] = 0
        binarized_ratings[binarized_ratings>threshold] = 1
        
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
        #print("dot is ",  np.dot(u, v), " and norm of u is ", np.linalg.norm(u), " and norm of v is ", np.linalg.norm(v))
        similarity = 0 
        u_norm = np.linalg.norm(u)
        v_norm = np.linalg.norm(v)
        if (u_norm != 0 and v_norm != 0):
            similarity = np.dot(u, v)/(u_norm * v_norm)
        
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return similarity


    def get_movie_similarities(self, movie_ratings, ratings_matrix, user_ratings):
        lst = np.zeros(len(user_ratings))
        for i in range(len(ratings_matrix)):
            if user_ratings[i] != 0:
                lst[i] = self.similarity(movie_ratings, ratings_matrix[i])
        return lst


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

        #THIS IS THE THIRD APPROACH
        recommendations = []
        
        for i in range(len(user_ratings)):
            if user_ratings[i] == 0:
                # this has not been rated hence find
                #print("find ", i)
                movie_similarities = self.get_movie_similarities(ratings_matrix[i],ratings_matrix, user_ratings)
                recommendations.append(np.dot(movie_similarities, user_ratings))
            else:
                recommendations.append(-math.inf)

        ranked_recommendations = np.argsort(recommendations)
        largest_indices = list(ranked_recommendations[::-1][:k])
        return largest_indices

        # ########################################################################
        # #                        END OF YOUR CODE                              #
        # ########################################################################

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
    print('python3 repl.py')
