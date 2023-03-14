# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
#from porter_stemmer import PorterStemmer
import numpy as np
import re
import random
import string
#from constants import * # GD WILL PASTE STUFF HERE LATER
# BC: comentar abaixo se tiver problemas com nltk
from nltk.metrics.distance import edit_distance
from nltk.stem import PorterStemmer

TITLE_INDEX = 0
YEAR_LENGTH = 7
ACCUMULATED_RATINGS = 4
CONFIRMATION_WORDS = ["Ok", "Alright", "Got it", "Roger that", "Very well", "Sure thing", "Gotcha", "Okay", "I see", "Perfect"]

MOVIE_REQUESTS = [
    'Can you share your opinion on a different film?',
    'What did you think of another movie?',
    'Would you mind telling me your thoughts on a separate movie?',
    'I\'m curious to know what you thought about a different movie.',
    'Can you give me your impressions of a different film?',
    'What\'s your take on another movie?',
    'Do you have any thoughts on a different movie you\'ve seen?',
    'I\'d like to hear your opinion on a separate movie.',
    'Can you share your views on a different film?',
    'What\'s your verdict on another movie?',
    'Tell me your thoughts on a different movie you\'ve watched.',
    'I\'m interested in hearing your feedback on a different film.',
    'What did you make of another movie?',
    'Can you let me know your thoughts on a separate movie?',
    'What\'s your impression of a different movie?',
    'I\'m curious to hear your evaluation of a different film.',
    'What\'s your opinion on another movie you\'ve seen?',
    'Can you provide me with your critique of a different movie?',
    'What\'s your reaction to another movie?',
    'I\'d love to hear your assessment of a different film.'
]

CATCH_ALL = [
    "Hmm, let's get back to talking about movies.",
    "Sorry, I don't think I understand what you're trying to say. Could we talk about movies instead?",
    "That's an interesting topic, but let's stick to movies for now.",
    "I'm not sure how to respond to that. Maybe we can talk about movies instead?",
    "I'm here to talk about movies. Do you have any movie recommendations to share?",
    "I'm afraid I'm not equipped to talk about that. Can we discuss movies instead?",
    "Let's keep the conversation focused on movies. Do you have any favorite movie genres?",
    "I appreciate your input, but I think we should stick to movies for now.",
    "I'm a movie recommender chatbot, so let's stick to discussing movies. Do you have any specific movie preferences?",
    "Thanks for sharing your thoughts, but let's talk about movies instead.",
    "I'm not sure how to respond to that. How about we discuss some great movie recommendations?",
    "Let's stay on topic and talk about movies. Have you seen any good movies lately?",
    "I think it's best if we keep the conversation centered around movies. What's your favorite movie of all time?",
    "That's an interesting point, but let's go back to discussing movies. What type of movies do you enjoy?",
    "I appreciate your input, but let's focus on movies for now. Do you have any favorite movie directors?",
    "Let's steer the conversation back to movies. Do you have any recommendations for great movie soundtracks?",
    "Sorry, that's not really what I want to talk about right now. Can we discuss some amazing movie recommendations instead?",
    "Thanks for sharing your thoughts, but let's talk about movies. What's the last movie you watched and enjoyed?",
    "I think we should get back to discussing movies. What are some must-watch movies you'd recommend?"
]

NEGATIVE_AFFIRMATIONS = [
    "angry",
    "sad",
    "frustrated",
    "disappointed",
    "upset",
    "hurt",
    "anxious",
    "overwhelmed",
    "stressed",
    "tired",
    "bored",
    "afraid",
    "insecure",
    "ashed",
    "embarrassed",
]

POSITIVE_AFFIRMATIONS = [
"happy",
"joyful",
"excited",
"grateful",
"content",
"confident",
"inspired",
"motivated",
"energized",
"loved",
"appreciated",
"proud",
"hopeful",
"peaceful",
"relaxed",
]

REQUESTS = [
    "Can you"

]

NEGATIONS = ["didn\'t", "not", "haven't", "never", "don't", "no"]
DOUBLE_WEIGHT = ['love', 'ador', 'hate', 'terribl', 'horribl', 'disgust', 'despis', 'extrem']
INTENSIFIERS = ["really", "very", "very much", "reea"]

CONNECTIVES = ["and", "as well as", ",", "in addition to", "also", "also,", "same for", "or"]
NEGATION_CONNECTIVES = ["but not", "except", "which is not the case for", "differently from", "as opposed to", "contrary to", "not like", "different than"]

AGREES = ["y", "yes", "yeah", "sure", "ok", "let's go", "lets go"]
REFUSES = ["n", "i'm good", "nah", "no", "nope", "nooo", "im good", "i am good", "that's enough", "thats enough"]

ORDERS = ["first", "second", "third", "fourth", "fifth"]
RECENCY = ["most recent", "least recent", "oldest", "newest"]
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
        
        #recommending
        self.has_previously_recommended = False
        self.accumulated_ratings = 0
        self.continue_recommending = False
        self.movie_sentiments = {}
        
        # list of movie recommendations to give to user
        self.recommendations = np.array([])
        
        # Binarize the movie ratings before storing the binarized matrix./watch
        self.ratings = self.binarize(ratings)

        num_movies = self.ratings.shape[0]
        self.user_ratings = np.zeros(num_movies)

        # disambiguate
        self.should_disambiguate = False
        self.movies_to_disambiguate = []
        self.previous_sentiment = 0
        # initialize stemmer
        # BC: comentar abaixo se tiver problemas com nltk
        self.ps = PorterStemmer()

        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        greeting_message = "Hello! Tell me about movies you've recently watched."
        if self.creative:
            greeting_message = "HELLO!!! I'M THE QUASI-YELLING BOT! SOMETIMES I YELL, SOMETIMES I DO NOT. TELL ME ALL THE MOVIES YOU WATCHED RECENTLY!!!"

        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################
        return greeting_message

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        goodbye_message = "See you later playa!"
        if self.creative:
            goodbye_message = "GOODBYE MY FRIEND!!!"

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
        if self.creative:
            return "I processed {} in creative mode!!".format(line)

        def respond_recommend():
            next_recommendation = self.recommendations.pop(0)
            movie_title = self.titles[next_recommendation][TITLE_INDEX]
            self.has_previously_recommended = True
            if self.creative: 
                return "YOU PROBABLY WOULD LIKE \"{}\". WANT MORE RECOMMENDATIONS?".format(movie_title.upper())               
            return "Given what you told me, I think you would like \"{}\". Would you like more recommendations?".format(movie_title)

        def trigger_recommend():
                for idx, sentiment in self.movie_sentiments.items():
                    self.user_ratings[idx] = sentiment
                self.recommendations = self.recommend(self.user_ratings, self.ratings)
                self.accumulated_ratings = 0
                return respond_recommend()
        try: 
            # Get recommendation
            response = ""
            if (self.has_previously_recommended):
                if len(self.recommendations) == 0:
                    self.has_previously_recommended = False
                    if self.creative: response = "THOSE ARE ALL MY RECOMMENDATIONS. PLEASE TELL ME MORE ABOUT THE MOVIES YOU'VE SEEN."
                    return "Those are all recommendations I have for now. Please keep telling me about more movies you've seen."

                line = self.preprocess(line)
                words = line.split()
                if any(word in AGREES for word in words):
                    return respond_recommend()
                elif any(word in REFUSES for word in words):
                    self.has_previously_recommended = False
                    return "{}. What movies did you like to watch?".format(random.choice(CONFIRMATION_WORDS)) 
                else:
                    return "Sorry. I didn't get that. Do you want to keep getting recommendations?"
                
            elif (self.accumulated_ratings == ACCUMULATED_RATINGS and len(self.movie_sentiments.keys()) > 0):
                trigger_recommend()
            
            # atualizar accumulated ratings quando ter que disambiguate
            
            if (self.should_disambiguate):
                movie_idx = self.disambiguate(line, self.movies_to_disambiguate)
                if len(movie_idx) == 0:
                    return "Please give a valid option."
                else:
                    self.should_disambiguate = False
                    idx = movie_idx[0]
                    self.movie_sentiments[idx] = self.previous_sentiment
                    self.accumulated_ratings += 1
                if (self.previous_sentiment == 1):
                    return "{}, you liked {}".format(random.choice(CONFIRMATION_WORDS), self.titles[idx][TITLE_INDEX])
                else:
                    return "{}, you disliked {}".format(random.choice(CONFIRMATION_WORDS), self.titles[idx][TITLE_INDEX])

            # Process movies
            else:
                potential_titles = self.extract_titles(line)
                # if self.creative
                all_idxs = [self.find_movies_by_title(title) for title in potential_titles]

                # No movies were found in the line
                if (len(all_idxs) == 0):   
                    # Case you say "I am angry", etc.
                    # GD if self.creative:
                    words = line.split()
                    for word in words:
                        for neg_affirmation in NEGATIVE_AFFIRMATIONS:
                            if word == neg_affirmation:
                                return "{}? No one should be feeling {} here!".format(word.capitalize(), word)
                        for pos_affirmation in POSITIVE_AFFIRMATIONS:
                            if word == pos_affirmation:
                                return "Everyone should feel {}! It's a great feeling".format(word)    
                    if (len(words) >= 2):
                        first_two_words = ' '.join(words[:2])
                        if (first_two_words == "can you"):
                            return "I can only recommend movies buddy! That's all I know."
                        if (first_two_words == "what is"):
                            return "You would be better off googling what's that."
                        if (first_two_words == "would you"):
                            return "I don't know if I would do that."
                        if (first_two_words == "could you"):
                            return "I could recommend movies for you and that's it."
                        if (first_two_words == "are you" or first_two_words == "you are"):
                            return "I'm just a bot. That's all, dude."
                        if (first_two_words == "what if"):
                            return ("Then stuff will happen.")
                    return random.choice(CATCH_ALL)
                
                # Process multiple movies at once
                if (len(all_idxs) > 1):
                    # if self.creative:
                    # clarify uncertain movies before procceeding
                    liked_movies = []
                    disliked_movies = []
                    neutral_movies = []
                    unheard_movies = []

                    # Handle unheard movies 
                    sentiments = self.extract_sentiment_for_movies(line)
                    for movie, sentiment in sentiments:
                        idxs = self.find_movies_by_title(movie)
                        # Handle ambiguous titles
                        if (len(idxs) > 1):
                            response = "Sorry, I found more than one movie called \"{}\". Here they are:\n".format(movie)
                            for idx in idxs:
                                possible_movie = self.titles[idx][TITLE_INDEX]
                                response += "   - {}\n".format(possible_movie)
                            response += "Which one are you referring to?"
                            self.movies_to_disambiguate = idxs
                            self.should_disambiguate = True
                            self.previous_sentiment = sentiment
                            return response
                        elif (len(idxs) == 1):
                            self.movie_sentiments[idxs[0]] = sentiment
                            self.accumulated_ratings += 1
                            actual_movie_title = self.titles[idxs[0]][TITLE_INDEX]
                            if (sentiment > 0):
                                liked_movies.append(actual_movie_title)
                            elif (sentiment == 0):
                                neutral_movies.append(actual_movie_title)
                            else:
                                disliked_movies.append(actual_movie_title)
                        else:
                            # Handle unheard movies
                            closest_movie = self.find_movies_closest_to_title(movie)
                            if len(closest_movie) > 1:
                                sentiment = self.extract_sentiment(closest_movie)
                                self.accumulated_ratings += 1
                                if (sentiment > 0):
                                    liked_movies.append(closest_movie)
                                elif (sentiment == 0):
                                    neutral_movies.append(closest_movie)
                                else:
                                    disliked_movies.append(closest_movie)
                            else:
                                unheard_movies.append(movie)

                    response = "{}.".format(random.choice(CONFIRMATION_WORDS))
                    if len(liked_movies) > 0:
                        response += " You liked these movies: \"{}\".".format("\", \"".join(liked_movies))
                    if len(disliked_movies) > 0:
                        response += " You did not like these movies: \"{}\".".format("\", \"".join(disliked_movies))
                    if len(neutral_movies) > 0:
                        response += " I don't know what you felt for these movies: \"{}\". ".format("\", \"".join(neutral_movies))
                    if len(unheard_movies) > 0:
                        response += " I have never heard of these movies: \"{}\".".format("\", \"".join(unheard_movies))
                    return response.strip()
                else:
                    idxs = all_idxs[0]
                    title = potential_titles[0]
                    sentiment = self.extract_sentiment(line)
                    # if there are more than one movie
                    if len(idxs) > 1:
                        if (sentiment == 0):
                            return "I'm sorry. I'm not sure if you liked \"{}\"".format(title)
                        else:
                            response = "Sorry, I found more than one movie called \"{}\". Here they are:\n".format(title)
                            for idx in idxs:
                                possible_movie = self.titles[idx][TITLE_INDEX]
                                response += "   - {}\n".format(possible_movie)
                            response += "Which one are you referring to?"
                            self.movies_to_disambiguate = idxs
                            self.should_disambiguate = True
                            self.previous_sentiment = sentiment
                    elif len(idxs) == 1:
                        if (sentiment == 0):
                            response = "I'm sorry. I'm not sure if you liked \"{}\"\n".format(title)
                        elif (sentiment >= 1):
                            confirmation_word = random.choice(CONFIRMATION_WORDS)
                            movie_request = random.choice(MOVIE_REQUESTS)
                            response = "{}, you liked \"{}\". {}\n".format(confirmation_word, title, movie_request)
                            self.movie_sentiments[idxs[0]] = sentiment
                            self.accumulated_ratings += 1
                            if (self.accumulated_ratings == ACCUMULATED_RATINGS):
                                return trigger_recommend()
                        else:
                            confirmation_word = random.choice(CONFIRMATION_WORDS)
                            movie_request = random.choice(MOVIE_REQUESTS)
                            response = "{}, you didn't like \"{}\". {}\n".format(confirmation_word, title, movie_request)
                            self.movie_sentiments[idxs[0]] = sentiment
                            self.accumulated_ratings += 1
                            if (self.accumulated_ratings == ACCUMULATED_RATINGS):
                                return trigger_recommend()
                    else:
                        response = "Sorry! I\'ve never heard of \"{}\".\n".format(title)
            return response.strip() # removes whitespace characters from beginning/end
        except:
            # Reset chatbot in case of crash
            self.has_previously_recommended = False
            self.movie_sentiments = {}
            self.recommendations = []
            num_movies = self.ratings.shape[0]
            self.user_ratings = np.zeros(num_movies)
            self.should_disambiguate = False
            self.movies_to_disambiguate = []
            self.previous_sentiment = 0
            return "Sorry you've confused me. Let's start over...\n. Please tell me about me some of the movies you liked"

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
        #                             END OF YOUR CODE                         #
        ########################################################################
        # lowercase the text
        # text = text.lower()

        # strip whitespace from beggining and end
        text = text.strip()
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
        def get_movie_titles(sentence):
            # remove special characters and lower case the sentence
            sentence = re.sub('[^A-Za-z0-9\s]+', '', sentence).lower()

            # list of common stop words to exclude from movie titles
            stop_words = ['and', 'any', 'are', 'as', 'at', 'be', 
            'because', 'been', 'but', 'by', 'can', 'could', 'did', 'do', 
            'does', 'for', 'from', 'had', 'has', 'have', 'he', 'her', 'his', 
            'how', 'if', 'in', 'into', 'is', 'it', 'its', 'just', 
            'more', 'most', 'much', 'not', 'of', 'on', 'or', 'our', 'out', 
            'over', 'said', 'she', 'should', 'so', 'some', 'than', 'that', 'their', 
            'then', 'there', 'these', 'they', 'this', 'to', 'too', 'up', 'us', 'very','was', 
            'we', 'were', 'what', 'when', 'where', 'which', 'who', 'why', 'will', 'with', 
            'would', 'your']
    

        # initialize list to store movie title substrings
        movie_titles = []
        
        sentence_list = sentence.split()

        # loop through all possible substrings of sentence
        for i in range(len(sentence_list)):
            for j in range(i+1, len(sentence_list)+1):
                # get substring
                if j-i > 10:
                    continue
                substring = sentence_list[i:j]                    
                # check if substring does not contain stop words
                if all(word.lower() not in stop_words for word in substring):
                    # add substring to movie titles list with correct capitalization
                    movie_titles.append(" ".join(word for word in substring))

        return movie_titles
        
        if (self.creative):
            return get_movie_titles(preprocessed_input)
        """
        pattern = r'"([^"]*)"'
        substrings = re.findall(pattern, preprocessed_input)
        return substrings

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
        matching_indices = []        

        words = title.split()
        
        def not_formatted(s):
            s = s.lower()
            return ''.join(ch for ch in s if ch not in string.punctuation)

        """Satisfy both starter and creative 1"""
        def starter():
            patterns = []
            # article pattern
            article = r'\b(a|an|the)\b'
            is_article = False
            if re.match(article, words[0], re.IGNORECASE):  
                pattern = r'(^(\b(a|an|the)\b).*)|(.*(\b(a|an|the)\b))\s*\(\d{4}\)'
                art = words.pop(0)
                is_article = True
                patterns.append(pattern)

            year = r'.*\(?\d{4}\)?$'
            patterns.append(year)
            pattern = "".join([r'(.*\b{}\b)'.format(word) for word in words])
            if not re.search(year, title, re.IGNORECASE) and not is_article:
                pattern += r'\s*\(?\d{4}\)?$'
            # pattern += r'\s*$'
            # print(pattern)
            patterns.append(pattern)

            for i, movie in enumerate(self.titles):
                met = True
                for pattern in patterns:
                    if not re.match(pattern, movie[0], re.IGNORECASE):
                        met = False
                        break

                if met: matching_indices.append(i)

            return matching_indices

        def creative():
            def contains_in_order(lst1, lst2):
                j = 0
                for i in range(len(lst1)):
                    if not_formatted(lst1[i]) == not_formatted((lst2[j])):
                        j += 1
                        if j == len(lst2):
                            return True
                return False

            def article_in_the_end(lst1, lst2):
                if len(lst2) == 1: 
                    return False
                j = 1
                for i in range(len(lst1)):
                    if not_formatted(lst1[i]) == not_formatted((lst2[j])):
                        if j == 0:
                            return True
                        j += 1
                        if j == len(lst2) - 1:
                            j = 0
                return False

            for i, movie in enumerate(self.titles):
                movie_str = movie[0].split()

                # print(movie_str)
                if contains_in_order(movie_str, words) or article_in_the_end(movie_str, words):
                    matching_indices.append(i)
            
            return matching_indices


        if self.creative:
            return creative()
        return starter()
        # return starter()

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
        preprocessed_input = re.sub(r'"[^"]*"', '', preprocessed_input)
        words = preprocessed_input.split()
        sentiment_total = 0
        """
        NEGATION words will "flip" the sentinment of next sentiment word by multipling a factor of -1
        INTENSIFIER words will double the sentiment of next sentiment word
        """
        def initialize():
            return (1, 1, 0)

        def evaluate_sentiment(word, negation, double_weight, intensifier):
            sentiment = 1 if (self.sentiment[word] == "pos") else -1
            sentiment = sentiment * negation * double_weight
            sentiment = (sentiment * 2) if (intensifier > 1) else sentiment
            return sentiment

        (negation, double_weight, intensifier) = initialize()

        for word in words:
            chars_to_strip = " . ! - ( ) [ ] :"
            word = word.strip(chars_to_strip).strip()

            if word in NEGATIONS:
                negation = -1
            if word in INTENSIFIERS:
                intensifier += 1
            
            stemmed_word = self.ps.stem(word)
        
            # a word can be an intensifier and also have positive or negative sentiment
            if stemmed_word in DOUBLE_WEIGHT:
                double_weight = 2
                
            if stemmed_word in self.sentiment:
                sentiment_total += evaluate_sentiment(stemmed_word, negation, double_weight, intensifier)
                (negation, double_weight, intensifier) = initialize()
            elif word in self.sentiment:
                sentiment_total += evaluate_sentiment(word, negation, double_weight, intensifier)
                (negation, double_weight, intensifier) = initialize()

        if sentiment_total >= 2:
            return 2
        elif sentiment_total <= -2:
            return -2
        else:
            return sentiment_total
        
    def extract_sentiment_for_movies(self, preprocessed_input):
        sentiments = []
        potential_titles = self.extract_titles(preprocessed_input)
        # all_idxs = [self.find_movies_by_title(title) for title in potential_titles]
        
        preprocessed_input = preprocessed_input.lower()
        titles = [t.lower() for t in potential_titles]        
        preceding_substrings = util.get_relevant_substrings(titles, preprocessed_input)
        # just applying extract_sentiment on substrings is not enough
        # What we need to do is to parse the connectives and negations
        # CONNECTIVE implies same sentiment as previous substring
        # NEGATION_CONNECTIVES means opposite sentiment as previous substring

        first_score = self.extract_sentiment(preceding_substrings[0])
        sentiment_scores = [first_score]
        for i in range(1, len(preceding_substrings)):
            substr = preceding_substrings[i]
            if (i == len(preceding_substrings) - 1):
               # i like "toy story". "scream" and "red heat" was bad. On the other hand, "jumanji" was so bad!
               if sentiment_scores[i - 1] == 0:
                    sentiment_scores.pop()
                    score = self.extract_sentiment(substr)
                    sentiment_scores.append(score) 
            else:
                if substr in CONNECTIVES:
                    score = sentiment_scores[i - 1]
                elif substr in NEGATION_CONNECTIVES:
                    score = (-1) * sentiment_scores[i - 1]
                else: 
                    score = self.extract_sentiment(substr)
                sentiment_scores.append(score)

        sentiments = list(zip(potential_titles, sentiment_scores))

        """
        new_titles = []
        try:
            for title in titles:
                potential_titles = self.find_movies_by_title(title)
                if len(potential_titles == 1):
                    new_titles.append(potential_titles[0])
                sentiments = list(zip(new_titles, sentiment_scores))
        except:
            sentiments = list(zip(potential_titles, sentiment_scores))
        """
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
        # Calculate edit distance between user input and all movie titles
        distances = []
        for movie in self.titles:
            movie_title = movie[TITLE_INDEX][:-YEAR_LENGTH]
            distance = edit_distance(title.lower(), movie_title.lower())
            # BC: comentar acima se tiver problemas com nltk e incluir distance = 0
            #distance = 0
            distances.append(distance)

        # Find movies with edit distance >= max_distance
        candidates = []
        for index, distance in enumerate(distances):
            if distance <= max_distance:
                candidates.append(index)

        if not candidates:
            return []

        # Find minimum edit distance among all candidates
        min_distance = distances[candidates[0]]
        for i in candidates:
            if distances[i] < min_distance:
                min_distance = distances[i]

        # Find the movies that tie for minimum edit distance
        closest = []
        for i in candidates:
            if distances[i] == min_distance:
                closest.append(i)

        return closest
            
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
        def extract_year(title):
            """ This function returns the year of a movie title. 
            The movie title must necessarily be in the format: name (year)
            """
            pattern = r'(?<=\()\d+(?=\))'
            match = re.search(pattern, title)
            return match.group()
    
         # Create an empty list to store the indices of movies identified by the clarification
        indices = []
        if (clarification == "most recent") or (clarification == "newest") or (clarification == "new"):
            idx = candidates[0]
            indices.append(idx)
            return indices
        elif (clarification == "oldest") or (clarification == "least recent") or (clarification == "old"):
            idx = candidates[-1]
            indices.append(idx)
            return indices

        clarification_words = clarification.split()
        for word in clarification_words:
            if word in ORDERS:
                idx = candidates[ORDERS.index(word)]
                indices.append(idx)
                return indices
        for idx in candidates:
            title = self.titles[idx][TITLE_INDEX]
            year = extract_year(title)
            if year == clarification:
                indices.append(idx)

        return indices
    
    ############################################################################
    # 3. Movie Recommendation helper functions                                 #
    ############################################################################

    @staticmethod
    def binarize(ratings, threshold=2.5):
        """
        Return a binarized version of the given matrix.

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

        # The starter code returns a new matrix shaped like ratings but full of
        # zeros.
        binarized_ratings = np.zeros_like(ratings)

        # Replace entries above threshold with 1 and below or equal to the threshold with -1.
        binarized_ratings[ratings > threshold] = 1
        binarized_ratings[ratings <= threshold] = -1
        binarized_ratings[ratings == 0] = 0 # null values should remain at 0.

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

        ########################################################################
        u_norm = np.linalg.norm(u)
        v_norm = np.linalg.norm(v)
        if u_norm == 0 or v_norm == 0:
            similarity = 0
        else:
            similarity = np.dot(u, v) / (u_norm * v_norm)        
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return similarity

    def recommend(self, user_ratings, ratings_matrix, k=10, creative=False):
        """Generate a list of indices of movies to recommend using collaborative
         filtering.

        You should return a collection of k indices of movies recommendations.

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

        # Populate this list with k movie indices to recommend to the user.
        recommendations = []
        
        num_movies = len(user_ratings)
        # indexes of the movies watched by the user
        watched_idx = [i for i in range(num_movies) if (user_ratings[i] != 0).any()]
        all_ratings = user_ratings.copy()
        
        # evaluates the estimated ratings for the user in all movies
        for i in range(num_movies):
            if i in watched_idx:
                all_ratings[i] = -2
                continue
            r_ix = sum([self.similarity(ratings_matrix[i], ratings_matrix[k]) * user_ratings[k] for k in watched_idx])
            all_ratings[i] = r_ix

        i = 0
        # find the indexes of the k largest values
        while (i < k):
            max_idx = np.argmax(all_ratings)
            # set the max value to a small number to find the next max value (min possible value is -1)
            # if np.isin(max_idx, watched_idx).any():
            #     continue
            all_ratings[max_idx] = -2
            i += 1
            recommendations.append(max_idx)
            
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
        debug_info = ''
        debug_info += "movie sentiments: {}\n".format(self.movie_sentiments)
        debug_info += "accumulated ratings: {}".format(self.accumulated_ratings)
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