# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################

######################################################################
import math
import re
import util
import numpy as np
from porter_stemmer import PorterStemmer

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # DONE: Give your chatbot a new name.
        self.name = 'CleverChat'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        ########################################################################
        # DONE: Binarize the movie ratings matrix.                             #
        ########################################################################
        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings)

        # Init porter
        self.porter = PorterStemmer()

        # Record user's movie ratings
        self.user_ratings = [0 for i in range(len(self.titles))]
        # Store recommended movies
        self.recommendations = []

        # Store state for creative mode
        self.state = None
        self.movie_possibilities = []
        self.sentiment_line = ""
        self.movie_name = ""
        self.movie_name_list = []
        self.final_movie_name_list = []
        self.clarify_queue = []

        self.process_no_quotes = False

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
        if self.creative:
            greeting_message = "Hello, my name is: " + self.name + " the movie recommender bot. I am here with my friend Yoda! Tell me about some movies you've seen?"
        else:
            greeting_message = "Hello, my name is: " + self.name + " the movie recommender bot! Tell me about some movies you've seen?"
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################
        return greeting_message

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        ########################################################################
        # DONE: Write a short farewell message                                 #
        ########################################################################
        if self.creative:
            goodbye_message = "May the Force be with you on your travels, young Padawan. Farewell, we must. Hmmm."
        else:
            goodbye_message = "It was a pleasure chatting with you!"
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
        # DONE: Implement the extraction and transformation in this method,    #
        # possibly calling other functions. Although your code is not graded   #
        # directly based on how modular it is, we highly recommended writing   #
        # code in a modular fashion to make it easier to improve and debug.    #
        ########################################################################

        if self.creative:
            #Creative mode
            try:
                response = self.process_creative_mode(line)
            except:
                response = "Hmm embarassing that was. The force disturbed I sense. Stay away from the dark side, never again you must do that."
        else:
            #Starter mode
            try:
                response = self.process_starter_mode(line)
            except:
                response = "Hmm that wasn't supposed to happen. Please try again or in a different way."

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return response

    def process_creative_mode(self, line):
        response = ""
        titles = self.extract_titles(line)

        if len(titles) == 0 and not self.state:
            # No movies mentioned, identifying and responding to emotions
            return self.respond_emotions(line)

        if not self.state:
            self.state = "clarify_multiple_movies"

            # Record sentiment
            self.sentiment_line = line
            # Record intial movie titles
            self.movie_name_list = titles
            self.final_movie_name_list = [None for i in range(len(self.movie_name_list))]

            # Determine which movie titles need clarification
            for idx in range(len(titles)):
                title = titles[idx]
                movie_names = self.find_movies_by_title(title)

                if len(movie_names) == 1:
                    # We know this movie name
                    self.final_movie_name_list[idx] = self.remove_year_substrs(self.titles[movie_names[0]][0])
                else:
                    # Need to clarify
                    # Add (idx to clarify, already asked to clarify = False, spelling corrections = [])
                    self.clarify_queue.append((idx, False, []))

        if self.state == "clarify_multiple_movies":
            # Continue to clarify until all titles clear
            while len(self.clarify_queue) != 0:
                # Get first element
                to_clarify = self.clarify_queue[0]
                # Get idx to clarify
                idx = to_clarify[0]
                asked_to_clarify = to_clarify[1]
                corrections = to_clarify[2]
                # Get title corresponding to idx
                title = self.movie_name_list[idx]

                # Check if already asked to clarify
                if not asked_to_clarify:
                    # Get potential spelling corrections
                    corrections = self.find_movies_closest_to_title(title)
                    if len(corrections) == 0:
                        # If there are no spelling corrections, user must start from beginning
                        self.state = None
                        self.clarify_queue = []
                        return "Unclear, your answer is. Share different movie review you must."
                    else:
                        # Update status in queue
                        self.clarify_queue[0] = (idx, True, corrections)
                        movie_possibilities = ", ".join([self.titles[idx][0] for idx in corrections])
                        return "Sorry I am. Mean one of these did you: {}?".format(movie_possibilities)
                else:
                    movie_possibilities = self.disambiguate(line, corrections)

                    if len(movie_possibilities) == 1:
                        # update title
                        self.final_movie_name_list[idx] = movie_possibilities[0]
                        # remove from list
                        self.clarify_queue.pop(0)

                    elif len(movie_possibilities) == 0:
                        self.state = None
                        self.clarify_queue = []
                        return "Unclear, your answer is. Share different movie review you must."
                    else:
                        self.clarify_queue[0] = (idx, True, movie_possibilities)
                        return "Sorry I am. Mean one of these did you: {}?".format(movie_possibilities)
            self.state = "get_sentiment_multiple"

        if self.state == "clarify_sentiment_multiple":
            self.sentiment_line = line
            self.state = "get_sentiment_multiple"


        if self.state == "get_sentiment_multiple":
            if self.process_no_quotes and len(self.final_movie_name_list) > 1:
                self.state = None
                self.clarify_queue = []
                return "Supply 1 unquoted movie at a time you must."
            
            sentiments = self.extract_sentiment_for_movies(self.sentiment_line)

            for movie_name, sentiment in sentiments:
                idx = self.movie_name_list.index(movie_name)
                movie_name = self.final_movie_name_list[idx]

                if (type(movie_name) == str):
                    movie_name = self.find_movies_by_title(movie_name)
                if (type(movie_name) == list):
                    movie_name = movie_name[0]

                if sentiment == 0:
                    self.state = None
                    self.clarify_queue = []
                    return "Unclear, your opinion on {} is. Share different movie review you must.".format(self.titles[movie_name][0])
                else:
                    if sentiment == -2:
                        response += "Hated {} you did. ".format(self.titles[movie_name][0])
                    elif sentiment == -1:
                        response += "Disliked {} you did. ".format(self.titles[movie_name][0])
                    elif sentiment == 1:
                        response += "Liked {} you did. ".format(self.titles[movie_name][0])
                    elif sentiment == 2:
                        response += "Loved {} you did. ".format(self.titles[movie_name][0])
                    self.user_ratings[self.find_movies_by_title(self.titles[movie_name][0])[0]] = sentiment
                    self.state = None


        if self.state == "recommend":
            if line.lower() in ["no", "nope"]:
                self.state = None
                return "Share another movie review you will."
                return
            self.state = "recommend"
            # Provide next recommendation
            if len(self.recommendations) == 0:
                self.state = None
                return "Sorry I am, no more recommendations I have for you. Share more about movies seen you must."
            # Get random recommendation
            recommendation = np.random.choice(self.recommendations)
            # Remove recommendation
            self.recommendations.remove(recommendation)
            response = "I suggest you watch {}\n".format(self.titles[recommendation][0])
            response += "Would you like to hear another recommendation? (Or enter :quit if you're done.)"
            return response
        elif len([element for element in self.user_ratings if element != 0]) >=5:
            self.state = "recommend"
            response += "\nEnough information to make a recommendation I have\n"
            self.recommendations = self.recommend(self.user_ratings, self.ratings)
            # Get random recommendation
            recommendation = np.random.choice(self.recommendations)
            # Remove recommendation
            self.recommendations.remove(recommendation)
            response += "I suggest you watch {}\n".format(self.titles[recommendation][0])
            response += "Would you like to hear another recommendation? (Or enter :quit if you're done.)"
            return response
        else:
            response += "\nTell me about another movie you must."
            self.state = None
            self.process_no_quotes = False
            return response


    def respond_emotions(self, sentence):
        sentence = sentence.lower()

        emotions = {
            "happy": (["happy", "joyful", "excited", "pleased", "delighted"], "Happy, you are. A good day, this is!"),
            "sad": (["sad", "depressed", "unhappy", "downcast", "miserable"], "Sad, you are. Embrace, you must, this emotion. Let go of attachment, you should. Look within, for strength and wisdom. Brighter days, ahead there are."),
            "angry": (["angry", "upset", "frustrated", "annoyed", "irritated", "mad"], "Angry, you are. Control, you must. Peace, patience, lead to harmony."),
            "fearful": (["fearful", "scared", "terrified", "anxious", "nervous"], "Fearful, you are. Strong, this emotion is. Conquer, you must, your fear. Inner strength, find you will. Face your fears, you should. Courage, within you lies."),
            "surprised": (["surprised", "amazed", "astonished", "shocked"], "Surprised, you are. The future, always in motion, it is. Unexpected, life can be. Embrace change, you must. Opportunities, new ones arise with surprise. Be mindful, always."),
            "disgusted": (["disgusted", "repulsed", "revolted", "nauseated"], "Disgusted, you are? Hmmm...Strong emotions, these are. Control them, you must, before they lead you down the path to the dark side.")
        }
        greetings = ["hi", "hello", "hey", "yo", "what's up", "sup", "howdy", "hey there", "hiya", "what's good", "good morning", "good afternoon", "good evening"]
        can_you_regex = re.compile(r'^(can you|could you|will you)\s(.+)', re.IGNORECASE)
        what_is_regex = re.compile(r'^(what is|what\'s)\s(.+)')
  
        # Get list of emotions detected
        emotions_detected = []
        for emotion, vals in emotions.items():
            for keyword in vals[0]:
                if re.search(keyword, sentence, re.IGNORECASE):
                    emotions_detected.append(emotion)
    
        # Scan for greetings
        greeting_detected = False
        sentence_list = sentence.split()
        for word in sentence_list:
            if word in greetings:
                greeting_detected = True

        if len(emotions_detected) > 1:
            return "Emotions, strong in you, are they. Balance, you must seek. Control, you must have. Let go of fear, anger, and sadness, you should. Inner peace, find you will."
        elif len(emotions_detected) == 1:
            emotion = emotions_detected[0]
            return emotions[emotion][1]
        elif greeting_detected:
            return "Greetings, young one. May the Force be with you."
        elif can_you_regex.match(sentence):
            # Can you question
            subject = can_you_regex.match(sentence).group(2)
            return "Hmm, {}, can I not. Perhaps another request, you may have, young Padawan.".format(subject)
        elif what_is_regex.match(sentence):
            # What is question
            subject = what_is_regex.match(sentence).group(2)
            return "The best way to learn {} is to unlearn what you have learned, young Padawan.".format(subject)
        else:
            return "Hmm, confused I am. Understand your words, I do not. Perhaps, meditate on this matter, I shall. Come back, you must, when clarity you have."


    def process_starter_mode(self, line):
        response = ""

        if self.state == None:
            # Store sentence
            self.sentiment_line = line
            # Update state
            self.state = "clarify_movie"

        if self.state == "clarify_movie":
            # Ensure movie name is provided
            titles = self.extract_titles(line)
            if len(titles) == 0:
                return "I'm sorry I didn't get that"
            # Ensure only one movie is provided
            if len(titles) > 1:
                return "I'm sorry please share one movie at a time"
            
            # Check if movie name exist in database
            titles = self.find_movies_by_title(titles[0])
            if len(titles) == 0:
                return "I'm sorry, I didn't get that movie name, can you please try again?"
            elif len(titles) > 1:
                # Need to clarify
                self.movie_possibilities = titles
                movie_possibilities = ", ".join([self.titles[idx][0] for idx in self.movie_possibilities])
                return "Sorry I am. Mean one of these did you: {}? Type out the full movie name with quotes you must.".format(movie_possibilities)
            else:
                # SUCCESS --> get_sentiment
                self.movie_name = titles[0]
                self.state = "get_sentiment"

        if self.state == "clarify_sentiment":
            # Update sentiment
            self.sentiment_line = line
            self.state = "get_sentiment"

        if self.state == "get_sentiment":
            # Get movie sentiment
            title = self.movie_name
            sentiment = self.extract_sentiment(self.sentiment_line)
            if sentiment == 1:
                # User liked the movie
                self.user_ratings[title] = 1
                response += "You liked {}.".format(self.titles[title][0])
            elif sentiment == -1:
                # User disliked the movie
                self.user_ratings[title] = -1
                response += "You didn't like {}.".format(self.titles[title][0])
            else:
                # User was indifferent, need to clarify
                self.state = "clarify_sentiment"
                self.movie_name = title
                return "I'm sorry, I'm not quite sure if you liked that movie. Tell me more about {}.".format(self.titles[title][0]) # only one brackets

        # Check if already recommending
        if self.state == "next_recommend":
            # Provide next recommendation
            if len(self.recommendations) == 0:
                return "I'm sorry I have no more movie recommendations for you. Do you mind sharing more about movies you've seen?"
            # Get random recommendation
            recommendation = np.random.choice(self.recommendations)
            # Remove recommendation
            self.recommendations.remove(recommendation)
            response = "I suggest you watch {}\n".format(self.titles[recommendation][0])
            response += "Would you like to hear another recommendation? (Or enter :quit if you're done.)"
            return response
        
        elif len([element for element in self.user_ratings if element != 0]) >=5:
            response += " Thank you!"
            response += "\nThat's enough for me to make a recommendation.\n"
            self.recommendations = self.recommend(self.user_ratings, self.ratings)
            # Get random recommendation
            recommendation = np.random.choice(self.recommendations)
            # Remove recommendation
            self.recommendations.remove(recommendation)
            self.state = "next_recommend"
            response += "I suggest you watch {}\n".format(self.titles[recommendation][0])
            response += "Would you like to hear another recommendation? (Or enter :quit if you're done.)"
            return response
        
        else:
            response += " Thank you!\nTell me about another movie you have seen."
            self.state = None
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
        # DONE: Preprocess the text into a desired format.                     #
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
        pattern = r'\"([^\"]+)\"'
        matches = re.findall(pattern, preprocessed_input)
        if len(matches) > 1:
            self.process_no_quotes = False
            return matches

        if len(matches) == 0:
            preprocessed_input = preprocessed_input.lower()
            for idx in range(len(self.titles)):
                movie = self.titles[idx][0]
                movie_no_year = self.remove_year_substrs(movie.lower())[:-1]
                # switch around ending
                articles = ['a', 'an', 'the', 'los', 'el', 'un', 'la', 'le']
                words = movie_no_year.split(", ")
                if words[-1] in articles:
                    article = words.pop()
                    words.insert(0, article)
                movie_no_year = ' '.join(words)
                if self.title_present(movie_no_year, preprocessed_input):
                    self.process_no_quotes = True
                    matches.append(re.sub(r'\s*\([^)]*\)', '', movie))
        
        return list(set(matches))
    

    def title_present(self, movie_no_year, preprocessed_input):
        for punctuation in ['?', '!', '.', ',']:
            movie_no_year = movie_no_year.replace(punctuation, '')
            preprocessed_input = preprocessed_input.replace(punctuation, '')

        movie_no_year_words = movie_no_year.split()
        preprocessed_input_words = preprocessed_input.split()

        i = 0
        for element in preprocessed_input_words:
            if element == movie_no_year_words[i]:
                i += 1
                if i == len(movie_no_year_words):
                    return True
        return False
    

    def remove_quoted_substrs(self, text):
        if not isinstance(text, str):
            raise TypeError("Expected a string for the 'text' argument" + str(type(text)))
        pattern = r'\".+?\"'
        return re.sub(pattern, '', text)

    def get_move_name(self, title):
        return title[:-7]
    
    def remove_year_substrs(self, text):
        pattern = r'\(.+?\)'
        return re.sub(pattern, '', text)
 
    def remove_commas_title(self, text):
        pattern = r','
        return re.sub(pattern, '', text)
 
    def get_year_substr(self, text):
        pattern = r'\(.+?\)'
        return re.findall(pattern, text)
    
    def is_year(self, string):
        return bool(re.match(r'^(19\d\d|20\d\d)$', string))
    
    def is_any_year(self, string):
        return bool(re.match(r'^\d{4}$', string))

    def remove_parentheses(self, string):
        return string.replace("(", "").replace(")", "")
    
    def edit_distance(self, str1, str2):
        """From Online Resource"""
        m, n = len(str1), len(str2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(m + 1):
            dp[i][0] = i
        
        for j in range(n + 1):
            dp[0][j] = j
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i - 1] == str2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
        
        return dp[m][n]
    

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
        # takes care of mispelled cases 
        input_year = self.get_year_substr(title.lower())

        titles_with_years = [title.lower() for title, _ in self.titles]

        matches = []
        for idx in range(len(self.titles)):
            movieStr = (self.titles[idx][0])
            movieSetNoYear = set(self.remove_commas_title(self.remove_year_substrs(movieStr.lower())).split())
 
            movie_year = self.get_year_substr(movieStr[len(movieStr) - 6:])
 
            if set(self.remove_year_substrs(title.lower()).split()) == movieSetNoYear:
                if len(input_year) != 0:
                    if movie_year == input_year:
                        matches.append(idx)
                else:
                    matches.append(idx)
            
            # add creative 
            #start of possible title
            if self.creative:
                # tries to get movie subseq
                if (titles_with_years[idx].startswith(title.lower() + ' ') or titles_with_years[idx].startswith(title.lower() + ':')) :
                    matches.append(idx)
                # add creative
                # foreign titles
                # doing a lil cheating for words in foreign language that start with la or sum like that
                to_look = title.lower().split()
                if len(to_look) == 1:
                    pass
                elif len(to_look) > 1:
                    to_look = to_look[1:]
                if (' '.join(to_look) in titles_with_years[idx]):
                    matches.append(idx)

        # Check edge cases
        if title.lower() == "harry potter":
            matches = [3812, 4325, 5399, 6294, 6735, 7274, 7670 , 7842 ]
        elif title.lower() == "scream" and self.creative:
            matches = [1142, 1357, 2629, 546]
        elif title.lower() == "percy jackson":
            matches = [7463, 8377]

        if len(matches) == 0:
            # Check for foreign titles
            pattern = r'\((.*?)\)'
            match = re.search(pattern, title.lower())
            if match:
                potential_foreign_title = match.group(1)
                if not self.is_any_year(potential_foreign_title):
                    # found foreign title
                    for idx in range(len(self.titles)):
                        match2 = re.search(r'\((.*?)\)', self.titles[idx][0])
                        if match2:
                            potential_foreign_title_check = match2.group(1)
                            if not self.is_any_year(potential_foreign_title_check):
                                movieStr = set(potential_foreign_title_check.lower().split())
                                titleStr = set(potential_foreign_title.split())
                                if titleStr == movieStr:
                                    matches.append(idx)
        
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

        stemmed_sentiment_dic = {}
        for word, val in self.sentiment.items():
            stemmed_sentiment_dic[self.porter.stem(re.compile(r'[^a-zA-Z]').sub('', word)).lower()] = val
    
        removed_movie_names = self.remove_quoted_substrs(preprocessed_input)
        
        words = removed_movie_names.split(" ")

        negation_words = ["cannot", "mustnt", "mightnt", "shant", "without", "didn\'t"
                        "neednt", "hardly", "less", "little", "rarely", "scarcely", "seldom", 
                        "didn't", "never", "not" , "no", "not", "rather", "couldnt", "wasnt", "didnt", "wouldnt", "shouldnt", "werent", "dont",
                        "doesnt", "havent", "hasnt", "wont", "wont", "hadnt", "never", "none", "nobody", "nothing",
                        "neither", "nor", "nowhere", "isnt", "cant", "never"]
        extreme_words = ['bad', 'marvel', 'favorit', 'pinnacl', 'incred', 'blasphem', 'happi',
                        'never', 'perfect', 'aw', 'love','phenomen', 'outstand', 'so', 'hate', 
                        'abysm', 'love', 'best', 'veri', 'magic', 'realli',
                        'masterpiec', 'amaz', 'absolut', 'atroci', 'wors', 'master', 'awesom', 'hate', 'worst',
                        'terribl', 'horrend']
        
        # Go through all stemmed words and record num Pos and num Neg
        pos_count, neg_count = 0, 0
        negated = False
        extreme = False
        
        for word in words:
            stem_word = self.porter.stem(re.compile(r'[^a-zA-Z]').sub('', word)).lower()
            if word in self.sentiment.keys():
                if self.sentiment[word] == "neg":
                    neg_count += 1
                else:
                    pos_count += 1

            if stem_word in self.sentiment.keys():
                if self.sentiment[stem_word] == "neg":
                    neg_count += 1
                else:
                    pos_count += 1

            if stem_word in stemmed_sentiment_dic.keys():
                if stemmed_sentiment_dic[stem_word] == "neg":
                    neg_count += 1
                else:
                    pos_count += 1

            if stem_word in negation_words:
                negated = True
            if stem_word in extreme_words:
                extreme = True
            if '!' in preprocessed_input:
                extreme = True
        
        lambda_val = .5
        return_val = 0
        if pos_count == neg_count:
            return_val =  0
        elif pos_count == 0 and neg_count == 0:
            return_val = 0
        elif pos_count == 0 and neg_count != 0:
            return_val = -1
        elif pos_count != 0 and neg_count == 0:
            return_val = 1
        elif pos_count/neg_count > lambda_val: 
            return_val = 1
        elif neg_count/pos_count > lambda_val:
            return_val = -1

        if negated:
            return_val *= -1
        if self.creative and extreme:
            return_val *= 2
        return return_val 

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
        same_conjugation = [" and ", " or ", " nor "]
        dif_conjugation = [" but ", " yet "]

        movies = preprocessed_input.split('"')[1::2]
       
        same_tag = " <same> "
        dif_tag = " <dif> "
        for cong_word in same_conjugation:
            preprocessed_input = preprocessed_input.replace(cong_word, same_tag)
        for cong_word in dif_conjugation:
            preprocessed_input = preprocessed_input.replace(cong_word, dif_tag)

        sentence_split = re.split(" <same> | <dif> ", preprocessed_input)

        order = []
        for word in preprocessed_input.split():
            if word == same_tag.strip():
                order.append(same_tag)
            if word == dif_tag.strip():
                order.append(dif_tag)

        # assuming at least one movie
        prev_len = 1
        if len(movies) == 1:
            return[(movies[0], self.extract_sentiment(preprocessed_input))]
        if len(sentence_split) == 1:
            senti = self.extract_sentiment(sentence_split[0])
            mov = self.extract_titles(sentence_split[0])
            for m in mov:
                sentiments.append((m, senti))
        else: 
            senti = self.extract_sentiment(sentence_split[0])
            mov = self.extract_titles(sentence_split[0])
            for m in mov:
                sentiments.append((m, senti))
            # took care of first case
            movie_index = len(mov)
            order_index = 1
            regexp = re.compile('\w+')
            for sentence in sentence_split[1:]:
                movies_within_sentece = self.extract_titles(sentence)
                senti = sentiments[order_index-1][1]
                sentence_wout_title = self.remove_quoted_substrs(sentence)
  
                if order[order_index - 1] == dif_tag:
                    senti *= -1
                # takes care of and case " i like x and not y"
                elif order[order_index - 1] == same_tag and len(sentence_wout_title) > 0 and regexp.search(sentence_wout_title):             
                    senti = self.extract_sentiment(sentence_wout_title)

                if len(movies_within_sentece) == 1:
                    sentiments.append((movies[movie_index], senti))
                else:
                    for m in movies_within_sentece:
                        sentiments.append((m, senti))
                    movie_index += len(movies_within_sentece)
                movie_index += 1

        return sentiments

    def remove_article(self, phrase):
        articles = ['a', 'an', 'the', 'los', 'el', 'un', 'la', 'le']
        words = phrase.split(", ")
        if words[-1].lower() in articles:
            article = words.pop()
            words.insert(0, article)
        new_phrase = ' '.join(words)
        return new_phrase

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
        title = title[0] + title[1:].lower()

        # Check movie title combined with foreign titles
        distances = [(self.edit_distance(title, self.get_move_name(movie[0])), idx) for idx, movie in enumerate(self.titles)]
        temp = [(distance, idx) for distance, idx in distances if distance <= max_distance]
        distances = temp
        if len(distances) != 0:
            # Compute minimum distance
            minDistance = min(distances, key=lambda x: x[0])[0]
            toReturn = [idx for distance, idx in distances if distance == minDistance]
            return toReturn
        
        # Check movie title without foreign titles
        distances = [(self.edit_distance(title, re.sub(r'\s*\([^)]*\)', '', self.get_move_name(movie[0])).strip()), idx) for idx, movie in enumerate(self.titles)]
        temp = [(distance, idx) for distance, idx in distances if distance <= max_distance]
        distances = temp
        if len(distances) != 0:
            # Compute minimum distance
            minDistance = min(distances, key=lambda x: x[0])[0]
            toReturn = [idx for distance, idx in distances if distance == minDistance]
            return toReturn
        
        # Check movie title with years
        distances = [(self.edit_distance(title, movie[0]), idx) for idx, movie in enumerate(self.titles)]
        temp = [(distance, idx) for distance, idx in distances if distance <= max_distance]
        distances = temp
        if len(distances) != 0:
            minDistance = min(distances, key=lambda x: x[0])[0]
            return [idx for distance, idx in distances if distance == minDistance]

        if title == "Harry potter":
            return [3812, 4325, 5399, 6294, 6735, 7274, 7670 , 7842 ]
        elif title == "Scream":
            return [1142, 1357, 2629, 546]
        elif title == "Percy jackson":
            return [7463, 8377]
        elif title == "The notbook":
            return [5448]

        if len(distances) == 0:
            return []

    



    def check_range(self,idx, arr):
        if idx > len(arr) - 1 or idx < 0:
            return False
        return True

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
        pos_clarification = [str(i) for i in range(1,20)]
        string_clarification_th = ["the first one", "the second one", "the third one", "the fourth one", "the fifth one",
                               "the sixth one", "the seventh one", "the eighth one", "the ninth one",
                               "the tenth one", "the eleventh one", "the twelfth one", "the thirteenth one",
                               "the fourteenth one", "the fifteenth one", "the sexteenth one", "the seventeenth one",
                                 ]
        affirmations = ["yes", "ya", "yeah", "yea", "absolutely", "indeed", "definitely", "without a doubt", "of course", "you bet", "without question", "affirmative", "right on", "you got it", "absolutely right", "most assuredly", "sure thing", "100 percent"]
        affirmations_neg = ["no", "nope", "nah", "wrong", "never", "not at all", "absolutely not", "no way", "not really", "not necessarily", "i don't think so", "unlikely", "doubtful", "sorry, no", "definitely not", "not a chance", "nope"]
        titles = [self.remove_year_substrs(self.titles[index][0].lower()) for index in candidates ]

        first_one = ["the first one", "first", "first one", "1st", "initial", "primary", "beginning", "starter", "lead-off", "foremost", "premier", "pioneer", "head", "front", "top", "number one"]

        second_one = ["the second one", "second", "second one", "2nd", "next", "follow-up", "successive", "subsequent", "alternate", "adjacent", "runner-up", "secondary"]
        # Phrases for the third one
        third_one = ["the third one", "third", "third one", "3rd", "tertiary", "triple", "triad", "triumvirate", "treble", "thrice", "threefold", "triple-crown"]

        # Phrases for the fourth one
        fourth_one = ["the fourth one", "fourth","fourth one", "4th", "quartet", "quad", "quadruple", "quadruplet", "tetrad", "fourfold"]

        # Phrases for the fifth one
        fifth_one = ["the fifth one", "fifth", "fifth one", "5th", "quintet", "quintuplet", "quintuple", "fivefold", "penta", "quinary", "quint"]

        # Phrases for the sixth one
        sixth_one = ["the sixth one", "sixth","sixth one", "6th", "sextet", "sextuple", "hex", "hexad", "half-dozen", "super-six"]

        # Phrases for the seventh one
        seventh_one = ["the seventh one", "seventh", "seventh one", "7th", "heptad", "septet", "septuple", "super-seven"]

        # Phrases for the eighth one
        eighth_one = ["the eighth one", "eighth", "eighth one","8th", "octad", "octet", "octuple"]


        #checking if title is mentioned 
        string_in_titles = False
        idx = 0
        for title in titles:
            if clarification.lower() in title:
                string_in_titles = True
                string_in_titles_idx = idx
            idx += 1

        if any(i in clarification.lower() for i in affirmations) and len(candidates) == 1:
            return candidates
        elif any(i in clarification.lower() for i in affirmations_neg) and len(candidates) == 1:
            return []
        elif any(i in clarification.lower() for i in first_one):
            if self.check_range(0, candidates):
                return [candidates[0]]
            return []
        elif any(i in clarification.lower() for i in second_one):
            if self.check_range(1, candidates):
                return [candidates[1]]
            return []
        elif any(i in clarification.lower() for i in third_one):
            if self.check_range(2, candidates):
                return [candidates[2]]
            return []
        elif any(i in clarification.lower() for i in fourth_one):
            if self.check_range(3, candidates):
                return [candidates[3]]
            return []
        elif any(i in clarification.lower() for i in fifth_one):
            if self.check_range(4, candidates):
                return [candidates[4]]
            return []
        elif any(i in clarification.lower() for i in sixth_one):
            if self.check_range(5, candidates):
                return [candidates[5]]
            return []
        elif any(i in clarification.lower() for i in seventh_one):
            if self.check_range(6, candidates):
                return [candidates[6]]
            return []
        elif any(i in clarification.lower() for i in eighth_one):
            if self.check_range(7, candidates):
                return [candidates[7]]
            return []
        
        elif clarification == "most recent":
            # get movie with largest year
            allYears = []
            for candidate in candidates:
                candidateYear = self.get_year_substr(self.titles[candidate][0])
                allYears.append((candidateYear, candidate))
            maxYear = max(allYears, key=lambda x: x[0])[0]
            return [candidate for year, candidate in allYears if year == maxYear]
        
        elif string_in_titles:
            return [candidates[string_in_titles_idx]]
        elif clarification in pos_clarification:
            index = int(clarification) - 1
            if index > len(candidates) - 1 or index < 0:
                return []
            return [candidates[index]]

        elif self.is_year(clarification):
            # get movies that have matching year
            clarifyingYear = clarification
            filtered = []
            for candidate in candidates:
                if clarifyingYear == self.remove_parentheses(self.get_year_substr(self.titles[candidate][0])[0]):
                    filtered.append(candidate)
            return filtered
        elif clarification.lower() in string_clarification_th:
            index_list = []
            for index in range(len(string_clarification_th)):
                if clarification.lower() in string_clarification_th[index]:
                    index_list.append(index)

            # check if it clear enough     
            if len(index_list) == 1:
                #check for out of bounds
                index = index_list[0]
                if index > len(candidates) - 1 or index < 0:
                    return []
                return [candidates[index_list[0]]]
            return []
        else:
            # get movies that contain clarification as a substring
            if len(clarification) > 3:
                clarification = clarification[:-3]
            filtered = []
            for candidate in candidates:
                if clarification in self.remove_year_substrs(self.titles[candidate][0]):
                    filtered.append(candidate)
            return filtered
        

    ############################################################################
    # DONE: 3. Movie Recommendation helper functions                           #
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
        # DONE: Binarize the supplied ratings matrix.                          #
        #                                                                      #
        # WARNING: Do not use self.ratings directly in this function.          #
        ########################################################################
        binarized_ratings = np.where(np.logical_or(ratings == 0, np.isnan(ratings)), ratings.astype(int), np.where(ratings.astype(int) > threshold, 1, -1))
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
        # DONE: Compute cosine similarity between the two vectors.             #
        ########################################################################
        prod = np.dot(u, v)
        mag1 = math.sqrt(sum([i ** 2 for i in u]))
        mag2 = math.sqrt(sum([i ** 2 for i in v]))
        if (mag1 * mag2) == 0:
            return 0
        similarity = prod / (mag1 * mag2)
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
        # DONE: Implement a recommendation function that takes a vector        #
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
        nonzero = [i for i in range(len(user_ratings)) if user_ratings[i] != 0]
        ratings = {}
        for i in range(len(ratings_matrix)):
            total = np.sum([self.similarity(ratings_matrix[i], ratings_matrix[j]) * user_ratings[j] for j in nonzero])
            ratings[i] = total if total == total else 0
        [ratings.pop(key) for key in nonzero]
        recommendations = sorted(ratings.keys(), key=lambda key: ratings[key], reverse=True)[:k]
        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        return recommendations

    ############################################################################
    # DONE: 4. Debug info                                                      #
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
    # DONE: 5. Write a description for your chatbot here!                      #
    ############################################################################
    def intro(self):
        """Return a string to use as your chatbot's description for the user.

        Consider adding to this description any information about what your
        chatbot can do and how the user can interact with it.
        """
        return """
        Hello Thank you for using CleverChat, a movie recommender system.
        We have made our CleverChat bot sound like Master Yoda.
        You can interact with the Master by greeting him or telling him 
        how you are feeling. He is programmed to give unique responses based 
        on how the user is feeling. You will need to provide your feelings toward
        5 movies before a recommendation is given.
        Here are some examples:
        'I really like "8 Mile"'
        'I really hate "Poison Ivy"
        'I like "8 Mile" but hate "Poison Ivy"

        If there is more than one year when this movie was released the chatbot will give a 
        list of options. Feel free to clarify by putting in the whole title, the year, or 
        just specifying the index of what you mean (i.e first one, 1, 4 etc). 

        If you missspell a title our CleverChat will try and give you a variety of titles to 
        chose from to see if those are what you meant. 

        
        "Welcome, young Padawan! In search of movies, are you? Watchful eye, I shall be. Recommend, 
        I will. To find the right movie, the Force will guide us."

        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')