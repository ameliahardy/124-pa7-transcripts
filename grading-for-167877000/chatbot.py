# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import heapq
from porter_stemmer import PorterStemmer
import re
import random

PROMPT_FOR_MOVIE = 0
NO_MOVIE_MENTIONED = 1
MOVIE_NOT_IN_DATABASE = 2
POS_SENTIMENT = 3
NEG_SENTIMENT = 4
MAKE_RECOMMENDATION = 5
ASK_FOR_MORE_RECS = 6
RESPOND_TO_ANGRY = 7
RESPOND_TO_SAD = 8
RESPOND_TO_HAPPY = 9

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'CERTain bot'

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

        # Preprocess titles array to be of form {"title":  "Titanic", "year": "1967"}
        self.proc_titles = [self.process_title(title[0]) for title in self.titles]
        self.sentiment_stemmed = {}

        stemmer = PorterStemmer()
        for word, sentiment in self.sentiment.items():
            self.sentiment_stemmed[stemmer.stem(word)] = sentiment

        self.num_processed = 0
        num_titles = len(self.proc_titles)
        self.user_ratings = np.zeros(num_titles)
        self.rec_list = []
        self.num_recommended = 0
        self.ambiguity = []  # stores options when there are multiple movie choice
        self.ambiguity_sentiment = 0
        self.disambiguate_mode = False
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

        greeting_message = "Howdy! They call me CERTain bot. I created by Claire, Emily, Rachel, and Thomas. Tell me about a movie you do or don't like!"

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

        goodbye_message = "Hope you got some good new movie recommendations! Im CERTain you'll enjoy them!"

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return goodbye_message

    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################

    # Helper function to generate varied responses for each case
    def generate_response(self, case, movie_title = ""):
        if (case == PROMPT_FOR_MOVIE):
            sample_responses = [
                "I reckon y'all could give me another movie and tell me how y'all felt about it.",
                "Darlin' you're dryer than the dining hall chicken. Gimme another movie!",
                "We're living in high cotton with all these movies. Come on, one more!",
                "Tell me about another movie you've watched. Did it tickle your toes or scratch your back?",
                "I'm fixin to a recommendation for y'all. Can y'all give me another movie y'all liked or disliked?",
                "What's another movie you've seen sweetie boo thang?",
                "I know y'all lounge at the cinema from high noon to low moon, what's another movie y'alls seen?",
                "Almost there partner, can you tell me another movie though?",
                "Betcha can't name one more movie!",
                "We'll be waiting till the cows come home if y'all keep taking this long. Any other favorite or least favorite movies?",
                "Gimme some sugar, any more movies you've loved or hated?"
            ]
        elif (case == NO_MOVIE_MENTIONED):
            sample_responses = [
                "I'm madder than a wet hen, you didn't give me a movie! ",
                "Y'all about as useful as tits on a bull. Tell me a movie y'all have watched!! ",
                "Sweetie darling pie, I don't see a movie in between quotes. ",
                "Not telling me a movie doesn't even amount to a hill of beans! I'll give y'all another try 'cause I'm feeling nice. "
            ]
        elif (case == MOVIE_NOT_IN_DATABASE):
            sample_responses = [
                f"Bless your heart darling, but I've never heard of \"{movie_title}\". ",
                f"Hold your horses! I've never heard of \"{movie_title}\", gimme a real one buddy. ",
                f"I don't know if I've heard of \"{movie_title}\". That's cattywampus! ",
                f"\"{movie_title}\" doesn't ring a bell in this ol' bot, sorry sweetie. "
            ]
        elif (case == POS_SENTIMENT):
            sample_responses = [
                f"I'm glad \"{movie_title}\" made you feel some typa way! ",
                f"I bet the movie \"{movie_title}\" was pretty as a peach. ",
                f"Heavens to Besty! It sounds like you liked watching \"{movie_title}\". ",
                f"That dog don't hunt but you do! I'm adding \"{movie_title}\" to the list of movies that you've liked. "
            ]
        elif (case == NEG_SENTIMENT):
            sample_responses = [
                f"The movie \"{movie_title}\" must have been worthless as gum on a boot heel. I bet you had a dying duck fit while watching it, huh. ",
                f"Well, that just DILLS my PICKLE! \"{movie_title}\" was terrible wasn't it?! ",
                f"Well, I''ll be damned! I also hated \"{movie_title}\"! ",
                f"It doesn't seem like \"{movie_title}.\" was your cup of tea, sweet tea. Sorry to hear that. ",
                f"Y'all didn't like \"{movie_title}\"? I'll remember that like I remember the 1999 wheat harvest. "
            ]
        elif (case == MAKE_RECOMMENDATION):
            rec_index = self.rec_list[self.num_recommended]
            movie_title = self.name_given_index(rec_index)
            sample_responses = [
                f"\nI suggest you watch \"{movie_title}\". It may butter your biscuit, ya know? ",
                f"\nBased on what y'all say, I think \"{movie_title}\" may make y'all happier than a dead pig. ",
                f"\nY'all might could watch \"{movie_title}\" next! "
            ]
        elif (case == ASK_FOR_MORE_RECS):
            sample_responses = [
                "Would you like another recommendation darlin'? Or shall I hush up. (Or enter :quit if you're done)",
                "I don't reckon y'all would want more movie recommendations? (Or enter :quit if you're done)",
                "Want to hear another one sweetie? (Or enter :quit if you're done)"
            ]
        elif (case == RESPOND_TO_ANGRY):
            sample_responses = [
                "You're angry! Well, I'll be damned, now I'm angry. "
            ]
        elif (case == RESPOND_TO_SAD):
            sample_responses = [
                "Why y'all so sad darlin'? My heart ain't too blessed to hear that. "
            ]
        elif (case == RESPOND_TO_HAPPY):
            sample_responses = [
                "Grinnin' like a possum eatin' a sweet tater because you're happy! That's what I am. "
            ]

        return sample_responses[random.randint(0, len(sample_responses) - 1)]
        
    
    def basic_chat_bot(self, line):
        response = ""
        if self.num_recommended == 0:
            movie_title = self.extract_titles(line)

            # Case where there is no movie mentioned in quotes or the subject changes
            if movie_title == []:
                return self.generate_response(NO_MOVIE_MENTIONED) + self.generate_response(PROMPT_FOR_MOVIE)

            # Case where multiple movies are mentioned at once (not handled in basic mode)
            if len(movie_title) != 1:
                return "Please only tell me about one movie at a time. Go ahead."

            movie_title = movie_title[0]
            movie_indices = self.find_movies_by_title(movie_title)
            num_movies_in_database = len(movie_indices)
            # Case where the movie mentioned is not in the provided database
            if (num_movies_in_database == 0):
                return self.generate_response(MOVIE_NOT_IN_DATABASE, movie_title) + self.generate_response(PROMPT_FOR_MOVIE)
            
            # Case where there are multiple movies that match the specified movie (ambiguity)
            if (num_movies_in_database > 1):
                return f"I found more than one movie called \"{movie_title}\". Could you clarify?"

            # valid movie title for basic mode
            movie_index = movie_indices[0]
            movie_title = self.name_given_index(movie_index)
            movie_sentiment = self.extract_sentiment(line)
            if movie_sentiment == 0:
                response = f"I couldn't tell whether or not you liked \"{movie_title}\". Please rephrase your message. "
            else:
                self.num_processed += 1
                self.user_ratings[movie_index] = movie_sentiment
                # Case for positive sentiment movie
                if movie_sentiment == 1:
                    response = self.generate_response(POS_SENTIMENT, movie_title)
                # Case for negative sentiment movie
                if movie_sentiment == -1:
                    response = self.generate_response(NEG_SENTIMENT, movie_title)

        # TODO: add in responses to "Would you like another recommendation" 
        # TODO: add taking in "no" to finish
        if self.num_processed >= 5:
            if self.num_recommended == 0:
                # maybe add multiple different types of these messages
                response += "That's enough for me to make a recommendation!"
                # change the k value and maybe store rec list as instance variable
                self.rec_list = self.recommend(self.user_ratings, self.ratings, 10, False)
                response += self.generate_response(MAKE_RECOMMENDATION) + self.generate_response(ASK_FOR_MORE_RECS)
                self.num_recommended += 1
            else: 
                if (line[0].lower() == 'y'):
                    response += self.generate_response(MAKE_RECOMMENDATION) + self.generate_response(ASK_FOR_MORE_RECS)
                    self.num_recommended += 1
                else:
                    return self.goodbye()
        else:
            response += self.generate_response(PROMPT_FOR_MOVIE)

        return response

    def creative_chat_bot(self, line):
        # Helper function to identify emotion in input if no movies extracted
        def identify_emotions(line):
            line = re.sub("[,.?!]", "", line).strip()
            tokens = line.split()
            angry_words = ["angry", "furious", "livid", "mad"]
            sad_words = ["sad", "disappointed", "depressed"]
            happy_words = ["happy", "ecstatic", "excited", "elated"]
            
            for word in tokens:
                word = word.lower()
                if word in angry_words:
                    return RESPOND_TO_ANGRY
                if word in sad_words:
                    return RESPOND_TO_SAD
                if word in happy_words:
                    return RESPOND_TO_HAPPY
            return 0
            
        if (self.disambiguate_mode):
            # call helper function
            return self.disambiguation_response(line)

        ## START OF FUNCTION CODE
        response = ""
        if self.num_recommended == 0:
            extracted_titles = self.extract_titles(line)
            # Case where the subject changes (respond to arbitrary input)
            if extracted_titles == []:
                emotion_case = identify_emotions(line)
                if emotion_case is RESPOND_TO_ANGRY: return self.generate_response(RESPOND_TO_ANGRY)
                elif emotion_case is RESPOND_TO_SAD: return self.generate_response(RESPOND_TO_SAD)
                elif emotion_case is RESPOND_TO_HAPPY: return self.generate_response(RESPOND_TO_HAPPY)
                else:
                    return self.generate_response(NO_MOVIE_MENTIONED) + self.generate_response(PROMPT_FOR_MOVIE)
                
            extracted_indices = []
            for movie_title in extracted_titles:
                movie_indices = self.find_movies_by_title(movie_title)
                num_movies_in_database = len(movie_indices)
                # Case where the movie mentioned is not in the provided database
                if (num_movies_in_database == 0):
                    return self.generate_response(MOVIE_NOT_IN_DATABASE, movie_title) + self.generate_response(PROMPT_FOR_MOVIE)
                # CHANGE THIS LATER TO INCORPORATE DISAMBIGUATE
                extracted_indices.append(movie_indices[0])
            
            movie_sentiments = self.extract_sentiment_for_movies(line)
            for sentiment in movie_sentiments:
                if sentiment[1] == 0:
                    emotion_case = identify_emotions(line)
                    if emotion_case is RESPOND_TO_ANGRY: return self.generate_response(RESPOND_TO_ANGRY)
                    elif emotion_case is RESPOND_TO_SAD: return self.generate_response(RESPOND_TO_SAD)
                    elif emotion_case is RESPOND_TO_HAPPY: return self.generate_response(RESPOND_TO_HAPPY)
                    else:
                        return f"I couldn't tell whether or not you liked \"{movie_title}\". Please rephrase your message. "
            
            # Case where there are multiple movies that match the specified movie (ambiguity)
            # fix this catch
            if (num_movies_in_database > 1):
                self.disambiguate_mode = True  # edit this code
                movie_options = ""
                self.ambiguity = movie_indices
                self.ambiguity_sentiment = movie_sentiments[0][1]
                for index in movie_indices:
                    movie_options += f"- {self.name_given_index(index)}\n"
                return f"I found more than one movie called \"{movie_title}\". I narrowed it down to the following options: \n{movie_options}Could you clarify?"

            for i in range(len(extracted_indices)):
                movie_sentiment = movie_sentiments[i]
                movie_title = movie_sentiment[0]
                self.num_processed += 1
                self.user_ratings[extracted_indices[i]] = movie_sentiment[1]
                
                # Case for positive sentiment movie
                if movie_sentiment[1] == 1:
                    response += self.generate_response(POS_SENTIMENT, movie_title)
                # Case for negative sentiment movie
                if movie_sentiment[1] == -1:
                    response += self.generate_response(NEG_SENTIMENT, movie_title)

        if self.num_processed >= 5:
            return self.make_recommendation(line, response)
        else:
            response += self.generate_response(PROMPT_FOR_MOVIE)

        return response
    
    def make_recommendation(self, line, response):
        if self.num_recommended == 0:
            # maybe add multiple different types of these messages
            response += "That's enough for me to make a recommendation!"
            # change the k value and maybe store rec list as instance variable
            self.rec_list = self.recommend(self.user_ratings, self.ratings, 10, False)
            response += self.generate_response(MAKE_RECOMMENDATION) + self.generate_response(ASK_FOR_MORE_RECS)
            self.num_recommended += 1
            return response
        else:
            # take in input from user on whether or not they want another recommendation
            if (line[0].lower() == 'y'):
                response += self.generate_response(MAKE_RECOMMENDATION) + self.generate_response(ASK_FOR_MORE_RECS)
                self.num_recommended += 1
                return response
            else:
                return self.goodbye()

    def disambiguation_response(self, line):
        disamb_result = self.disambiguate(line, self.ambiguity)
        if (len(disamb_result) == 0):
            return "I couldn't quite understand what movie you're specifying? Could you clarify?"
        
        # if control path reaches here, disambiguate has worked successfully
        self.disambiguate_mode = False
        index = disamb_result[0]
        movie_sentiment = self.ambiguity_sentiment
        movie_title = self.name_given_index(index)

        self.num_processed += 1
        self.user_ratings[index] = movie_sentiment
        
        # Case for positive sentiment movie
        if movie_sentiment == 1:
            response = self.generate_response(POS_SENTIMENT, movie_title)
        # Case for negative sentiment movie
        if movie_sentiment == -1:
            response = self.generate_response(NEG_SENTIMENT, movie_title)
        
        if self.num_processed >= 5:
            return self.make_recommendation(line, response)
        else:
            response += self.generate_response(PROMPT_FOR_MOVIE)
        return response


    def name_given_index(self, index):
        if self.proc_titles[index]['year'] == "":
            return self.proc_titles[index]['title']
        return f"{self.proc_titles[index]['title']} ({self.proc_titles[index]['year']})"

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
            # response = "I processed {} in creative mode!!".format(line)
            response = self.creative_chat_bot(line)
        else:
            # TO DO:
            # - sound somewhat naturalistic? figure out how to vary the responses
            response = self.basic_chat_bot(line)
            # response = "I processed {} in starter mode!!".format(line)

        """
        - instance variable that tracks the number of processed movies
        - as each movie is processed, add it to the user ratings matrix
        - once num_processed reaches 5, call recommend function
            - user ratings doesn't need to be binarized until creative mode
                since user rating should only be -1, 0, 1
        """


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
        text = text.strip()
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

        """
        parts = preprocessed_input.split('\"');
        # All of the odd-indexed parts of the sentence will be inside the quotes
        movie_titles = []
        idx = 1
        while idx < len(parts):
            movie_titles.append(parts[idx])
            # Move to the next title
            idx += 2
        return movie_titles
        """
        def string_found(string1, string2):
            if re.search(r'\s' + re.escape(string1) + r'\b', string2):
                return True
            return False

        movie_titles = []
        # find all movies enclosed in quotes
        movie_titles = re.findall('"([^"]*)"', preprocessed_input)
        
        # creative, identify movies without quotation marks and correct capitalization
        # if self.creative and len(movie_titles) == 0:
        if len(movie_titles) == 0:
            for i in range(len(self.proc_titles)):
                movie_title = self.proc_titles[i]['title']
                if string_found(movie_title.lower(), preprocessed_input.lower()):
                     movie_titles.append(movie_title)

        return movie_titles


    def handle_articles(self, title):
        title = title.strip()

        parts = title.split(", ")

        if parts[-1] in ["A", "An", "The"]:
            title = parts[-1] + " " + " ".join(parts[:-1])
        return title

    def handle_foreign_articles(self, title):
        title = title.strip()

        parts = title.split(", ")

        if parts[-1] in ["La", "Le", "L'", "Die", "Les"]:
            title = parts[-1] + " " + " ".join(parts[:-1])
        return title

    def remove_prefix(self, string, prefix):
        return string[len(prefix):] if string.startswith(prefix) else string

    def process_title(self, movie_title):
        res = {}
        years = re.findall("\((\d{4})\)", movie_title) # catch all years
        alt_for_titles = re.findall("\((\D[^\)]+)\)", movie_title) # all titles that are in parenthesis (could be alternate or foreign)
        res["year"] = ""
        res["alt_for"] = [] # returns a list of processed alternate/foreign titles, if any
        title = movie_title

        if len(years) != 0:
            res["year"] = years[0]
            title = re.sub("\((\d{4})\)", "", movie_title)

        if len(alt_for_titles) != 0:
            for i in range(len(alt_for_titles)):
                if (alt_for_titles[i].startswith("a.k.a.")): # alternate name
                    alternate_name = self.remove_prefix(alt_for_titles[i], "a.k.a. ")
                    alternate_name = self.handle_articles(alternate_name) # put article in front
                    res["alt_for"].append(alternate_name) # add to list of all alternate/foreign title(s)
                else: # foreign name
                    foreign_name = self.handle_foreign_articles(alt_for_titles[i])
                    res["alt_for"].append(foreign_name) # add to list of all alternate/foreign title(s)

        res["title"] = self.handle_articles(title)

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
        def string_found(string1, string2):
            if re.search(r'\b(?=\w)' + re.escape(string1) + r'\b', string2):
                return True
            return False

        matches = []
        title_dict = self.process_title(title)
        given_title = title_dict["title"]
        title_year = title_dict["year"]

        for i in range(1, len(self.proc_titles)):
            movie_dict = self.proc_titles[i]
            movie = self.process_title(movie_dict["title"])["title"]
            movie_year = movie_dict["year"]
            movie_alt_for_list = movie_dict["alt_for"] # returns a list of all alternate/foreign names, if any

            if given_title.lower() == movie.lower():
                if title_year != "":
                    if title_year == movie_year:
                        matches.append(i)
                else:
                    matches.append(i)
            elif self.creative and string_found(title_dict["title"].lower(), movie_dict["title"].lower()):
                matches.append(i)
            else:
                for j in range(len(movie_alt_for_list)):
                    if given_title.lower() == movie_alt_for_list[j].lower(): # iterate through list of all foreign/alternate titles
                        matches.append(i)

        return matches

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
        num_pos = 0
        num_neg = 0
        negations = {"not", "didn't", "never", "can't", "don't", "wasn't", "isn't", "couldn't"}

        stemmer = PorterStemmer()
        preprocessed_input = re.sub("\".*\"", "", preprocessed_input)
        titles = self.extract_titles(preprocessed_input)
        for title in titles:
            preprocessed_input = re.sub(title, "", preprocessed_input)
        preprocessed_input = re.sub("[,.?!]", "", preprocessed_input).strip()
        words = preprocessed_input.split(" ")

        # self.sentiment["enjoi"] = "pos"
        # self.sentiment["horribl"] = "neg"
        # self.sentiment["terribl"] = "neg"
        negate = False
        for i in range(len(words)):
            word = stemmer.stem(words[i].lower())
            if word in negations:
                negate = True

            if word in self.sentiment_stemmed:
                if negate:
                    if self.sentiment_stemmed[word] == "pos":
                        num_neg += 1
                        last_sent = -1
                    elif self.sentiment_stemmed[word] == "neg":
                        num_pos += 1
                        last_sent = 1
                else:
                    if self.sentiment_stemmed[word] == "pos":
                        num_pos += 1
                        last_sent = 1
                    elif self.sentiment_stemmed[word] == "neg":
                        num_neg += 1
                        last_sent = -1

        if num_pos > num_neg:
            return 1
        elif num_pos < num_neg:
            return -1
        else:
            if num_pos != 0:
                return last_sent
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
        for title in titles:
            preprocessed_input = re.sub(f"\"{title}\"", "", preprocessed_input)
            # This is where the title doesn't have quotes around it.
            preprocessed_input = re.sub(title.lower(), "", preprocessed_input.lower())

        parts = re.split(' and | but | or |,', preprocessed_input)
        sentiments = []
        for i in range(len(parts)):
            part = parts[i]
            cur_title = titles[min(i, len(titles)-1)]
            cur_sentiment = self.extract_sentiment(part)
            negations = {"not", "didn't", "never", "can't"}
            words = part.split(" ")
            contains_negation = 0
            for negation in negations:
                if negation in words:
                    contains_negation = 1

            sentiments.append([cur_title, cur_sentiment, contains_negation])
        
        for i in range(len(sentiments)):
            if sentiments[i][1] == 0:
                if i > 0 and sentiments[i-1] != 0:
                    sentiments[i][1] = sentiments[i-1][1]
                    contains_negation = sentiments[i][2]
                    if contains_negation == 1:
                        sentiments[i][1] *= -1
        
        for j in range(len(sentiments)-1, -1, -1):
            if sentiments[j][1] == 0:
                if j < len(sentiments) - 1 and sentiments[j+1] != 0:
                    sentiments[j][1] = sentiments[j+1][1]
                    contains_negation = sentiments[i][2]
                    if contains_negation == 1:
                        sentiments[j][1] *= -1
                        
        sentiments = [(sentiment[0], sentiment[1]) for sentiment in sentiments]
        return sentiments

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

        min_indices = [] # what we will return

        title = title.lower()
        n = len(title)
        for x in range(len(self.proc_titles)): # go through all movie titles
            movie = self.process_title(self.proc_titles[x]['title'])["title"] #process_title returns dictionary
            movie = movie.lower() 
            m = len(movie)
            distances = np.zeros((m + 1, n + 1)) # minimum edit distance table
            for i in range(m + 1): #initialization
                distances[i, 0] = i

            for j in range(n + 1): #initialization
                distances[0, j] = j

            for i in range(1, m + 1): # go through character by character
                for j in range(1, n + 1):
                    if movie[i - 1] == title[j - 1]: # to evaluate substitutions
                        cost = 0
                    else: 
                        cost = 2
                    insertion = distances[i - 1 , j] + 1
                    deletion = distances[i, j - 1] + 1
                    substitution = distances[i - 1, j - 1] + cost
                    distances[i, j] = min(insertion, deletion, substitution) # pick least costly option
            
            # only keep track of closest titles
            if (distances[m, n] <= max_distance):
                if (len(min_indices) == 0): # edit distance of very first word
                    min_dist = distances[m, n]
                if (distances[m, n] == min_dist): # edit distance of this movie title is the same as previous minimum
                    min_indices.append(x)
                elif (distances[m, n] < min_dist): # found new minimum edit distance
                    min_indices = [x] # only keep index of this new movie title
                    min_dist = distances[m, n]

        return min_indices

   
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
        matching_movies = []
        clarif_words = clarification.split(" ")
        if clarif_words[0].lower() == "the":
            clarif_words = clarif_words[1:]
        if clarif_words[-1].lower() == "one":
            clarif_words = clarif_words[:-1]
        clarification = " ".join(clarif_words)
        clarification = re.sub("[.?!]", "", clarification).strip().lower()
        for idx in candidates:
            cur_movie = self.proc_titles[idx]
            if clarification in cur_movie['title'].lower() or clarification == cur_movie['year']:
                matching_movies.append(idx)

        position_strings = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eight", "ninth", "tenth"]

        if len(matching_movies) == 0 and self.creative:
            if clarification.isnumeric() and int(clarification)-1 < len(candidates) and int(clarification) > 0:
                matching_movies.append(candidates[int(clarification)-1])
            elif clarification in position_strings:
                matching_movies.append(candidates[position_strings.index(clarification)])
            else:
                options = [(i, self.proc_titles[i]) for i in candidates]
                options = sorted(options, key = lambda d:d[1]["year"])
                for recent_text in {"most recent", "latest", "newest"}:
                    if recent_text in clarification:
                        matching_movies.append(options[-1][0])
                if "oldest" in clarification:
                    matching_movies.append(options[0][0])
        
        return matching_movies

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
        
        binarized_ratings = np.where((ratings <= threshold) & (ratings > 0), -1, ratings)
        binarized_ratings = np.where(binarized_ratings > threshold, 1, binarized_ratings)
        

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

        num_movies = len(user_ratings)
        indices_rated = list(np.nonzero(user_ratings)[0])  # pull indices of movies the user has rated
        
        r_xi = {}
        for i in range(num_movies):
            if i not in indices_rated:  # skip over the indices already rated by the user
                sum = 0
                for j in indices_rated:
                    ## ADD IN: get rid of divide by zero case
                    if np.linalg.norm(ratings_matrix[i]):
                        s_ij = self.similarity(ratings_matrix[i], ratings_matrix[j])
                        r_xj = user_ratings[j]
                        sum += s_ij * r_xj
                r_xi[i] = sum
        
        r_xi_tuples = list(r_xi.items())
        recommendations = heapq.nlargest(k, r_xi_tuples, key=lambda t: t[1])
        recommendations = list(list(zip(*recommendations))[0])

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
        This chatbot has two modes, standard and creative. It will ask you for 5 movie,
        and if you are in creative mode, you can specify many of those movies together!
        Once you tell chatbot how you feel about those movies, it will start recommending them.
        I hope you enjoy using it and get some great movie recommendations!
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
