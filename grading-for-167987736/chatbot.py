# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import numpy as np
import re
import random
from porter_stemmer import PorterStemmer
import string

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'YodaFlix'

        self.expectation = 'description'

        self.clarification_options = None
        self.stored_sentiment = 0

        self.recommendations = None

        self.creative = creative

        self.articles = ['a', 'an', 'the', 'la', 'el', 'los', 'las', 'le', 'les', 'il', 'lo', 'gli', 'i', 'un', 'uno', 'una']

        self.yes_words = ["yes", "yep", "yeah", "yessir", "i do", "sure"]
        self.no_words = ["no", "nope", "don't", "do not", "nah"]

        self.negations = ["no", "not", "rather", "couldn't", "wasn't", "didn't", "wouldn't", "shouldn't", "weren't", "don't", "doesn't", "haven't", "hasn't", "won't", "wont", "hadn't", "never", "none", "nobody", "nothing", "neither", "nor", "nowhere", "isn't", "can't", "cannot", "mustn't", "mightn't", "shan't", "without", "needn't", "hardly", "less", "little", "rarely", "scarcely", "seldom"]
        
        self.strong_words = ["love", "hate", "amazing", "awful", "awesome", "beautiful", "brilliant", "despise", "loathe", "delightful", "devastating", "disastrous", "disgusting", "dreadful", "epic", "excellent", "fantastic", "fascinating", "flawless", "glorious", "horrible", "incredible", "intense", "magnificent", "mind-blowing", "miraculous", "outstanding", "perfect", "phenomenal", "remarkable", "ridiculous", "scandalous", "spectacular", "stunning", "superb", "terrible", "terrific", "thrilling", "tragic", "tremendous", "unbelievable", "perfect", "unforgettable", "wonderful"]
        
        self.emphasis_list = ["really", "very", "extremely", "totally", "absolutely", "completely", "utterly", "never", "!"]

        self.multiple = ["either", "both", "neither", "nor", "or", "and"]
        self.opposite = ["but", "however", "yet"]
        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        self.user_ratings = np.zeros(len(self.titles))

        self.p = PorterStemmer()
        # stem keys in sentiment dictionary
        self.sentiment = {self.p.stem(key): value for key, value in self.sentiment.items()}
        
        # stem negation words
        self.negations = [self.p.stem(xx) for xx in self.negations]

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################
        # Binarize the movie ratings before storing the binarized matrix.
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

        greetings_list = ["Greetings, young Padawan. Watch great movies, you will, with Yodaflix as your guide.", "Movie lover, you are. Find the perfect film, together we will.",    "Hello, may the Force be with you. Find you a great movie, we shall.", "Welcome to Yodaflix, the ultimate movie recommendation chatbot. Excited to help you find your next film, I am.", "Fellow movie enthusiast, you are. With the wisdom of Yoda, discover great movies, you will.", "Hello there, Yodaflix welcomes you. In your quest for the perfect movie, assist you, I will.",    "Welcome, young Jedi. With the power of the Force and Yodaflix's expertise, the perfect movie you will find.", "Greetings, movie seeker. Allow Yodaflix to help you navigate the galaxy of cinema and find the perfect movie, I will.", "Hello, Yodaflix speaks. Recommend great movies, I will. Exciting, this is!", "Welcome to Yodaflix, young Padawan. Find great movies, you will. Strong with the Force, your movie choices will be."]
        greeting = random.choice(greetings_list)

        return greeting
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        ########################################################################
        # TODO: Write a short farewell message                                 #
        ########################################################################

        goodbyes_list = ["Farewell, young Padawan. May the Force be with you in your movie-watching journey.", "Time to go, it is. Until our paths cross again, happy movie watching, may you be.", "Goodbye for now, movie enthusiast. May the force guide you in finding films that bring you great joy.", "Parting time, it is. Watch more movies, you should. Great happiness, they will bring.", "Farewell, fellow seeker of cinematic excellence. Until next time, may the Force guide your movie choices.", "Goodbye, young Jedi. Remember, with Yodaflix's recommendations, a great movie always awaits you.", "May the movies be with you, always. Farewell, it is.", "Until next time, movie lover. Happy viewing, may you be.", "Part ways, we must. But with Yodaflix's guidance, the perfect movie you will find.", "Goodbye, it is. The galaxy of cinema awaits you. May your movie choices be wise and fulfilling."]

        goodbye = random.choice(goodbyes_list)

        return goodbye
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################


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
        if self.expectation == 'description':
            response = self.description_handler(line)
        elif self.expectation == 'clarification':
            response = self.clarification_handler(line)
        elif self.expectation == 'recommendation':
            response = self.recommendation_handler(line)

        #response = "I processed {} in starter mode!!".format(line)

        #sentiment = self.extract_sentiment(self.preprocess(line))
        #response = "The line has a sentiment score of {}!!".format(sentiment)
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

    def description_handler(self, line):
        """
        Given a user input that is expected to be a description of a movie,
        identifies the movie, extracts the sentiment, and adds it to
        self.user_ratings at index of identified movie. Produces a response
        to repeat sentiment to user, and asks for another movie description,
        unless at 5 movies, where it will switch self.expectation to recommendation
        """
        #lists of creative response options:
        no_movie_found = [ "No movie found, I have. Please include a title in quotation marks, to help me find one.", "Found that movie, I have not. Include a title in quotation marks, to guide me to it, you must.", "Hmm, that movie found, I have not. A title in quotation marks, you must provide, to help me find one.", "That movie not found, young Padawan. To find one, include a title in quotation marks, you must.", "This movie, I cannot find. No title in quotation marks, there is. Please include one, to help me find it.", "Lost in the movie universe, I seem to be. No movie found, with no title in quotation marks. Include it, you must.", "No movie found, it seems. A title in quotation marks, you must provide, to help me find one.", "The path to a great movie, clouded it is. No movie found, with no title in quotation marks. Include it, you must, to clear the way.", "No movie found, I have. To find one, a title in quotation marks, you must provide.", "Include a title in quotation marks, you must. For no movie found, there is. Together, a great movie we will find."]
        too_many_inquiries = ["Process more than one movie, I cannot. Only one, include you must, young Padawan.", "One movie at a time, I can handle. More than one, too much for me it is. Choose wisely, you must.", "Hmm, too much to process, this is. Only one movie, you can include. Focus, I must.", "Overwhelmed, my system is. One movie, I can process. Please include only one, you must.", "More than one movie, you have included. Process them all, I cannot. Only one, please include.", "Like stars in the galaxy, movies are many. But one at a time, I must process. Please include only one movie, young Padawan.", "Many movies, you mention. But process them all, I cannot. One at a time, include a movie you must, hmm.", "Processing more than one movie, I cannot. Only one, you must include. Choose wisely, I suggest.", "One movie at a time, I can handle. More than one, I cannot. Choose wisely, young Padawan.", "The Force is strong with many movies. But one at a time, process them, I must. Only one, you can include, yes."]
        none_found_clarification = ["Did you mean one of the following? {}.", "Confused, Yodaflix is. Did you intend one of these? {}", "Hmm, no movie found. One of these, did you mean? {}", "Looking for movie, Yodaflix is. These, did you mean? {}", "Lost, Yodaflix is. Perhaps one of these, you meant? {}", "Hmm, no movie found. Maybe one of these? {}", "Yodaflix searches for your movie. These, did you intend? {}", "Lost in the force, Yodaflix is. One of these, did you mean? {}", "Cannot find your movie, Yodaflix cannot. One of these, did you mean? {}", "Looking for your movie, Yodaflix is. These, did you intend? {}"]
        not_heard_of = ["Heard of \"{}\", I have not. Tell me about another movie.", "A tale I don't know of, \"{}\", sorry. Another movie, tell me.", "Unfamiliar with \"{}\", I am. Tell me of another movie, you must.", "\"{}\", hmmm? Not heard of it, I have. About another movie, do tell.", "Unknown, this movie \"{}\", is to me. Another you must suggest.", "Heard of this \"{}\", I have not. Please suggest another movie.", "Sorry, know not of \"{}\", I do. Tell me another movie, you must.", "Strange, this movie \"{}\", is to me. Suggest another, you should.","Never heard of \"{}\", sorry. Can you tell me about another movie?", "Alas, \"{}\", unknown to me. Another movie, please suggest."]
        multiple_movies_found_creative = ["Which one did you mean? {}", "Clarification in quotations you must provide, young padawan. Which one did you mean? {}", "Hmm, multiple matches I see. Which one did you mean? {}", "A difficult task this is. Which one did you mean? {}", "Which movie is the one you seek? {}", "Lost, we are. Which movie is the one you seek? {}", "Choose, you must. Which one did you mean? {}", "Hmmm, confusing this is. Which one did you mean? {}", "Multiple movies found, hmm? Which one did you mean? {}", "Puzzled, I am. Which movie is the one you seek? {}"]
        multiple_movies_found_starter = ["More than one movie with the title \"{}\", I have found. Clarify in quotes, can you?", "Hmmm, found more than one movie titled \"{}\". Clarify with quotes, can you please?", "Multiple movies found with the title \"{}\", have I. Can you clarify in quotes, young padawan?", "A tricky situation, this is. More than one movie found with the title \"{}\". Clarify in quotes, you must.", "Found more than one movie titled \"{}\", I have. Clarify with quotes, can you?", "Confusing, this is. More than one movie with the title \"{}\". Clarify with quotes, you must.", "Hmm, I have found multiple movies with the title \"{}\". Can you clarify in quotes?", "More than one movie with the title \"{}\", I have discovered. Clarify in quotes, you must.", "The title \"{}\", found in more than one movie. Can you clarify which one in quotes?", "Found more than one movie with the title \"{}\", I have. Clarify in quotes, you must."]
        sentiment_unclear = ["Unclear, your feelings are. Like or dislike \"{}\", you do? Tell me more about this movie, you must.", "Difficult it is to discern, your feelings for \"{}\". Like or dislike, do you? More about this movie, tell me.", "Confused, your feelings are. For \"{}\" like or dislike, do you? Speak more of this movie, you must.", "Uncertain, your feelings are, about \"{}\". Like or dislike, you do? More about this movie, tell me.", "Cannot determine if you liked or disliked \"{}\". More about this movie, please tell me.", "Difficult to determine if you liked or disliked \"{}\". Speak more of this movie, you must.", "Indecipherable, your feelings are about \"{}\". Did you like or dislike? Tell me more of this movie, you must.", "Unclear, whether you liked or disliked \"{}\". Speak more about this movie, you must.", "Ambiguous, your feelings are. Like or dislike \"{}\", do you? More about this movie, tell me.", "Perplexed, I am. Like or dislike \"{}\", you do? Speak more of this movie, you must."]
        liked_synonyms = ['liked', 'enjoyed', 'adored', 'appreciated', 'fancied']
        disliked_synonyms = ['disliked', 'disfavored', 'did not enjoy', 'did not fancy']
        ask_about_recommendation = ['Ah, you {} \"{}\". A strong emotion, this is. Would you like a recommendation?', 'Hmm, {} you say about \"{}\". A recommendation, would you like?', 'Interesting, {} \"{}\" you did. A recommendation, may I give?', 'Hmm, you {} \"{}\". A recommendation, would you like for a movie?', 'Hmmm... {} \"{}\", you did. Recomendation, would you like?']
        ask_for_movie = ['{} \"{}\", you did. About another movie, tell me.', 'Hmm, you {} \"{}\". Another movie, I must hear about', '{} \"{}\" you say. Movies I need to learn your preferences of, more of them', 'A different movie, you must teach me of, if you truly {} \"{}\"', 'So {} \"{}\", you did. I see. The Force is asking to learn about another movie']

        sentiment = self.extract_sentiment(line) #get sentiment of line
        titles = self.extract_titles(line) #identify movie from line
        if len(titles) == 0: #if no movies identified, ask user again
            #ARBITRARY INPUT???
            return self.arbitrary_input(line.lower())
            #return random.choice(no_movie_found)

        elif len(titles) > 1: #if multiple movies, ask for one at a time
            return random.choice(too_many_inquiries)

        title = titles[0] #get title string
        movie_indices = self.find_movies_by_title(title) #get potential movie indices
        if len(movie_indices) == 0: #if no movies with title
            #IF CREATIVE, USE SPELLCHECK TO GET OPTIONS
            if self.creative:
                option_indices = self.find_movies_closest_to_title(title)
                self.clarification_options = option_indices

                if len(self.clarification_options) > 0:
                    self.stored_sentiment = sentiment
                    self.expectation = "clarification"
                    if len(self.clarification_options) == 1:
                        return "did you mean \"{}\"?".format(self.titles[option_indices[0]][0])
                    options_string = self.options_to_string(option_indices)
                    return random.choice(none_found_clarification).format(options_string)
            return random.choice(not_heard_of).format(title)
        elif len(movie_indices) > 1: #if multiple movies with title
            #IF CREATIVE, USE DISAMBIGUATION
            if self.creative:
                self.expectation = "clarification"
                self.stored_sentiment = sentiment
                option_indices = movie_indices
                self.clarification_options = option_indices
                options_string = self.options_to_string(option_indices)
                return random.choice(multiple_movies_found_creative).format(options_string)
            return random.choice(multiple_movies_found_starter).format(title)
        movie_index = movie_indices[0]

        if sentiment == 0: #if no sentiment extracted
            return random.choice(sentiment_unclear).format(title)
        #set user_ratings
        if sentiment > 0: #if liked
            self.user_ratings[movie_index] = 1
            expressed_sentiment = random.choice(liked_synonyms)
        else: #if disliked
            self.user_ratings[movie_index] = -1
            expressed_sentiment = random.choice(disliked_synonyms)

        if len(np.nonzero(self.user_ratings)[0]) >= 5: #if >= 5 movies rated
            self.expectation = "recommendation"
            self.recommendations = self.recommend(self.user_ratings, self.ratings)
            return random.choice(ask_about_recommendation).format(expressed_sentiment, title)
        else: #if < 5 movies rated
            return random.choice(ask_for_movie).format(expressed_sentiment, title)


    def clarification_handler(self, line):
        """
        CREATIVE
        Given a user input that is expected to be a clarification between
        multiple movies in self.clarification_options, use disambiguate function
        to determine which movie the user meant. Produce response to repeat
        stored self.clarification_sentiment to user and asks for another movie
        description, unless at 5 movies, where it will switch self.expectation
        to recommendation
        """
        #lists of creative response options:
        request_movie = ["Mmm. Another movie you've watched, tell me about.","Another movie, do tell, you must.","About another movie, tell me, you shall.","Know another movie, do you? Tell me.","Another movie you've seen, tell me about.","More movies to know, there are. Tell me.","Know of another movie, do you? Tell me.","Mmm. Another movie watched, tell me more.","Another movie seen, you have? Speak of it.","Tell me of another movie, you must."]
        yes_or_no = ["Uncertain, I am, if yes or no it was. \"{}\" you meant, did you?","Meaning, I am unsure of. Yes or no, did you say? Clarify, can you? \"{}\" was the movie?","A dilemma, this is. Yes or no, I do not know. Confirm, you must. \"{}\" was what you meant?","Hmm, clear it is not. Yes or no, did you mean? Tell me, you must. \"{}\" was the movie?","Indecipherable, your response is. \"{}\" you meant, did you? Confirm, you must.","Unclear, your response is. Yes or no, did you mean? \"{}\" was what you meant?","Confusing, your answer is. \"{}\" you meant, did you? Clarify, you must.","Ambiguous, your response is. Yes or no, did you mean? Confirm, you must. \"{}\" was the movie?","Uncertain, I am, of your response. Clarify, you must. \"{}\" was what you meant?","Difficult, this is. Yes or no, I do not know. Clarify, you must. \"{}\" was the movie?"]
        no_movie_found = ["No movie found, I have. Please include a title in quotation marks, to help me find one.","Found that movie, I have not. Include a title in quotation marks, to guide me to it, you must.","Hmm, that movie found, I have not. A title in quotation marks, you must provide, to help me find one.","That movie not found, young Padawan. To find one, include a title in quotation marks, you must.","This movie, I cannot find. No title in quotation marks, there is. Please include one, to help me find it.","Lost in the movie universe, I seem to be. No movie found, with no title in quotation marks. Include it, you must.","No movie found, it seems. A title in quotation marks, you must provide, to help me find one.","The path to a great movie, clouded it is. No movie found, with no title in quotation marks. Include it, you must, to clear the way.","No movie found, I have. To find one, a title in quotation marks, you must provide.","Include a title in quotation marks, you must. For no movie found, there is. Together, a great movie we will find."]
        multiple_movies_found = ["More than one movie with the title \"{}\", I have found. Clarify, can you?","Hmmm, found more than one movie titled \"{}\". Clarify, can you please?","Multiple movies found with the title \"{}\", have I. Can you clarify, young padawan?","A tricky situation, this is. More than one movie found with the title \"{}\". Clarify, you must.","Found more than one movie titled \"{}\", I have. Clarify, can you?","Confusing, this is. More than one movie with the title \"{}\". Clarify, you must.","Hmm, I have found multiple movies with the title \"{}\". Can you clarify?","More than one movie with the title \"{}\", I have discovered. Clarify, you must.","The title \"{}\", found in more than one movie. Can you clarify which one?","Found more than one movie with the title \"{}\", I have. Clarify, you must."]
        sentiment_unclear = ["Unclear, your feelings are. Like or dislike \"{}\", you do? Tell me more about this movie, you must.","Difficult it is to discern, your feelings for \"{}\". Like or dislike, do you? More about this movie, tell me.","Confused, your feelings are. For \"{}\" like or dislike, do you? Speak more of this movie, you must.","Uncertain, your feelings are, about \"{}\". Like or dislike, you do? More about this movie, tell me.","Cannot determine if you liked or disliked \"{}\". More about this movie, please tell me.","Difficult to determine if you liked or disliked \"{}\". Speak more of this movie, you must.","Indecipherable, your feelings are about \"{}\". Did you like or dislike? Tell me more of this movie, you must.","Unclear, whether you liked or disliked \"{}\". Speak more about this movie, you must.","Ambiguous, your feelings are. Like or dislike \"{}\", do you? More about this movie, tell me.","Perplexed, I am. Like or dislike \"{}\", you do? Speak more of this movie, you must."]
        ask_about_recommendation = ['Ah, you {} \"{}\". A strong emotion, this is. Would you like a recommendation?','Hmm, {} you say about \"{}\". A recommendation, would you like?','Interesting, {} \"{}\" you did. A recommendation, may I give?','Hmm, you {} \"{}\". A recommendation, would you like for a movie?','Hmmm... {} \"{}\", you did. Recomendation, would you like?']
        ask_for_movie = ['{} \"{}\", you did. About another movie, tell me.','Hmm, you {} \"{}\". Another movie, I must hear about','{} \"{}\" you say. Movies I need to learn your preferences of, more of them','A different movie, you must teach me of, if you truly {} \"{}\"','So {} \"{}\", you did. I see. The Force is asking to learn about another movie']
        #use disambiguate with line and self.clarification_options to determine movie
        #simple_pattern = '"([^"]+)"'
        #clarifications = re.findall(simple_pattern, line)
        if len(self.clarification_options) == 1:
            line = line.lower()
            line = line.strip()
            exclude = set(string.punctuation)
            line = ''.join(ch for ch in line if ch not in exclude)
            if line in self.yes_words:
                movie_index = self.clarification_options[0]
                title = self.titles[movie_index][0]
            elif line in self.no_words:
                self.expectation = "description"
                return random.choice(request_movie)
            else:
                return random.choice(yes_or_no).format(self.titles[self.clarification_options[0]][0])

        else:

            exclude = set(string.punctuation)
            clarification = ''.join(ch for ch in line if ch not in exclude)
            #if len(clarifications) == 0:
                #ARBITRARY INPUT???
                #self.expectation = "description"
                #return "Was unable to clarify movie title. Tell me about another movie"
            #clarification = clarifications[0]
            movie_indices = self.disambiguate(clarification, self.clarification_options)
            #if narrowed down to no movies, set self.expectation to description and ask user for movie desc
            if len(movie_indices) == 0:
                self.expectation = "description"
                return random.choice(no_movie_found)
            #if narrowed down to multiple movies, keep self.expectation to clarification and ask for clarification
            elif len(movie_indices) > 1:
                self.clarification_options = movie_indices #set self.clarification_options
                options_string = self.options_to_string(movie_indices)
                return random.choice(multiple_movies_found).format(str(options_string))

            movie_index = movie_indices[0]
            title = self.titles[movie_index][0]

        #update self.user_ratings with self.stored_sentiment
        sentiment = self.stored_sentiment
        if sentiment == 0: #if no sentiment extracted
            self.expectation = "description"
            return random.choice(sentiment_unclear).format(title)
        if sentiment > 0: #if liked
            expressed_sentiment = "liked"
        else: #if disliked
            expressed_sentiment = "disliked"
        self.user_ratings[movie_index] = self.stored_sentiment #set user ratings

        if len(np.nonzero(self.user_ratings)[0]) >= 5: #if >= 5 movies rated
            self.expectation = "recommendation"
            self.recommendations = self.recommend(self.user_ratings, self.ratings)
            return random.choice(ask_about_recommendation).format(expressed_sentiment, title)
        else: #if < 5 movies rated
            self.expectation = "description"
            return random.choice(ask_for_movie).format(expressed_sentiment, title)


    def recommendation_handler(self, line):
        """
        Given a user input that is expected to be a yes or no to whether or not the user
        wants a movie recommendation, returns a response. If yes, then give a recommendation and ask
        if they want another. If no, then ask the user for a movie description
        """
        for affirmation in self.yes_words:
            if affirmation in line: #if user says yes:
                if self.recommendations == []: #if no more recommendations
                    self.expectation = "description"
                    return "I don't have any more recommendations right now. Tell me about another movie."
                rec_index = self.recommendations[0] #use self.recommendations to get top recommendation
                rec_movie = self.titles[rec_index][0]
                self.recommendations = self.recommendations[1:] #remove top recommendation list
                return "I recommend \"{}\". Would you like another recommendation?".format(rec_movie)

        #if user says no:
        for negative in self.no_words:
            if negative in line: #if user says no
                self.expectation = "description"
                return "Okay! Tell me about another movie."

        #return response
        return "I wasn't sure if that was a yes or a no. Would you like a movie recommendation?"

    def options_to_string(self, option_indices):
        if len(option_indices) == 1:
            return "\""+self.titles[option_indices[0]][0]+"\"."
        else:
            result = ""
            for i in range(len(option_indices) - 1):
                result += "\""+self.titles[option_indices[i]][0]+"\", "
            result += "or \""+self.titles[option_indices[-1]][0]+"\"."
            return result

    def arbitrary_input(self, line):
        """
        Detect if line is related to the user's emotion. If so, create response to address
        that feeling (using premade responses). Otherwise use the arbitrary responses list
        to create arbitrary response (again using premade responses)
        """

        #lists of dialogue responses
        negative_response = ["{}, you feel. About a movie you like, tell me. Better mood, we shall find.","That you are {}, sorry to hear I am. But worry not, a movie you like, tell me. Happier, we shall be.","Feeling {}, you are. Share with me a movie you enjoyed, so that a better mood we can find.","Hmm, {} in you, I sense. A movie you enjoyed, please share. Better mood, we shall aim for.","{} in you, I sense with the force. Tell me of a movie you liked, so that we may lift your spirits."]
        positive_response = ["{}, you feel. Glad, I am. But to movies, let us return. Share with me a film and how you felt about it, do.","Glad, I am, to hear you're feeling {}. But back to movies, let us go. Tell me of a film and your feelings towards it.","Feeling {}, you are. Good, good. But back to movies, we must go. Please share with me a film and your feelings towards it.","Glad to hear you're feeling {}. However, we must refocus on movies. Please share with me a film and how you felt about it.","{}, I sense in you. But let us return to our discussion of movies. Tell me about a film and how you felt about it, you will."]
        no_sentiment = ["Not want to talk about that, I do. Back to movies, can we get?","Discuss that, I do not wish. Return to movies, let us.","That topic, let us avoid. Back to movies, can we go?","Speak of that, I do not desire. Refocus on movies, shall we?","Avoid that topic, we must. Return to movies, can we?","Not want to discuss that, I do. Let's return to movies, shall we?","That topic, let us leave behind. Back to movies, can we move?","Talk about that, I do not wish. Refocus on movies, let us."]
        what_who_etc = ["{}, know I do not. Movies, know I do. Hmmm...","{}, you ask? Unknown to me. Movies, however, I know plenty of.","{}, the answer eludes me. But about movies, I do know.","{}... I cannot say. But talk of movies, we may.","{}? A question for the ages. But about movies, I have wisdom to share."]
        maybe_type = ["Maybe so, but more exciting, talking about movies is, I think.","Perhaps, but talking about movies, I find more exciting.","Agreed, maybe. However, discussing movies is what I find more exciting.","Maybe. However, I believe talking about movies is the more exciting option.","Maybe, but let us not forget that discussing movies is a thrilling endeavor."]

        emotion_keywords = {
            'happy': ['happy', 'happiness', 'joy', 'joyful', 'pleasure', 'content', 'satisfaction', 'delight',
                      'grateful', 'glad'],
            'sad': ['sad', 'sadness', 'unhappy', 'disappointed', 'miserable', 'depressed', 'regret', 'grief', 'sorrow',
                    'heartbroken'],
            'angry': ['angry', 'anger', 'frustrated', 'mad', 'furious', 'outraged', 'annoyed', 'irritated', 'enraged',
                      'livid'],
            'excited': ['excited', 'excitement', 'thrilled', 'ecstatic', 'eager', 'enthusiastic', 'animated', 'zealous',
                        'intense', 'pumped'],
            'fearful': ['fearful', 'fear', 'anxious', 'nervous', 'terrified', 'scared', 'frightened', 'panicked',
                        'dread', 'horror'],
            'disgusted': ['disgusted', 'disgust', 'repulsed', 'revolted', 'nauseated', 'sickened', 'abhorred', 'hated',
                          'despised', 'aversion'],
            'surprised': ['surprised', 'surprise', 'shocked', 'astonished', 'amazed', 'stunned', 'dumbfounded',
                          'startled', 'flabbergasted', 'awe']
        }

        def detect_emotion(text):
            # convert the text to lowercase and split into words
            words = text.lower().split()
            # count the number of keywords in each emotion category
            emotion_counts = {emotion: sum(1 for word in words if word in emotion_keywords[emotion]) for emotion in
                              emotion_keywords}
            # determine the emotion with the highest count
            max_emotion = max(emotion_counts, key=emotion_counts.get)
            # return the detected emotion or None if no emotion is detected
            if emotion_counts[max_emotion] > 0:
                return max_emotion
            else:
                return None


        def detect_question_type(text):
            text = text.lower()
            if text.startswith("what "):
                return "what"
            elif text.startswith("who "):
                return "who"
            elif text.startswith("where "):
                return "where"
            elif text.startswith("when "):
                return "when"
            elif text.startswith("why "):
                return "why"
            elif text.startswith("how "):
                return "how"
            elif text.startswith("can "):
                return "request question"
            elif text.startswith("is "):
                return "yes/no question"
            else:
                return "hmmm"

        if detect_question_type(line) == 'what' or detect_question_type(line) == 'who' or detect_question_type(line) == 'where' or detect_question_type(line) == 'when' or detect_question_type(line) == 'why' or detect_question_type(line) == 'how':
            return random.choice(what_who_etc).format(detect_question_type(line))
        elif detect_question_type(line) == 'request question' or detect_question_type(line) == 'yes/no question':
            return random.choice(maybe_type)
        elif detect_emotion(line) == 'sad' or detect_emotion(line) == 'angry' or detect_emotion(line) == 'fearful' or detect_emotion(line) == 'disgusted':
            return random.choice(negative_response).format(detect_emotion(line))
        elif detect_emotion(line) == 'happy' or detect_emotion(line) == 'excited' or detect_emotion(line) == 'surprised':
            return random.choice(positive_response).format(detect_emotion(line))

        return random.choice(no_sentiment)

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

        simple_pattern = '"([^"]+)"'
        movies = re.findall(simple_pattern, preprocessed_input)
        return movies

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
        #given a title, removes the year from the end, and returns the title along with the year
        #in the format " (xxxx)" for the year
        #returns empty string for year if there is no year provided in the title
        def remove_year(title):
            pattern = '( \([0-9\-]+\))$'
            years = re.findall(pattern, title)
            if years == []:
                return title, ''
            else:
                year = years[0]
                start = title.replace(year, '')
                return start, year

        #given a title, returns an array of the possible arrangements of the title (i.e. if the title
        #begins with an article, moves the article to the end of the title (before the year))
        def create_options(title):
            options = [title]
            start, year = remove_year(title)
            if ' ' in start:
                space_index = start.index(' ')
                first_word = start[:space_index]
                if first_word in self.articles:
                    options.append(start[space_index+1:] + ', ' + title[:space_index] + year)
            return options

        #given an inputted title, checks to see if the inputted title is present
        #in the provided title data. Returns array of indices of matching titles
        def check_option(option):
            indices = []
            start, year = remove_year(option)
            if year != '':
                #if a year is provided, make sure entire title (including year) matches
                for i in range(len(self.titles)):
                    title = self.titles[i][0]
                    if title_match(option, title):
                        indices.append(i)
            else:
                #if year is not provided, make sure title (without year) matches
                for i in range(len(self.titles)):
                    title, _ = remove_year(self.titles[i][0])
                    if title_match(option, title):
                        indices.append(i)
            return indices

        #given an inputted option and a title, returns true if they are a match
        def title_match(option, title):
            title = title.lower()
            title = title.replace('(', '')
            title = title.replace(')', '')
            option = option.replace('(', '')
            option = option.replace(')', '')
            if option == title:
                return True
            elif self.creative:
                pattern = '(^|[^a-z])%s($|[^a-z])'%option
                if re.search(pattern, title):
                    return True
            return False


        indices = []
        title = title.lower()
        options = create_options(title)
        for option in options:
            new_indices = check_option(option)
            for index in new_indices:
                if index not in indices:
                    indices.append(index)

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
        # given a query as input, this method implements fine grained sentiment extracting, outputting scores
        # ranging from -2 to 2.
        def fine_grained_extract_sentiment(query):
            emph_count = 0
            increase = 1
            last_seen = ""
            negation = False
            pos_count = 0
            neg_count = 0

            # stem strong_words and emphasis_words lists
            self.strong_words = [self.p.stem(xx) for xx in self.strong_words]
            self.emphasis_list = [self.p.stem(xx) for xx in self.emphasis_list]

            for word in query:
                # add case for negation, emph, strong -> neutral?
                if word in self.negations:
                    negation = not negation
                if word in self.emphasis_list:
                    emph_count += 1
                if re.match('[.,?!;:]', word) and negation:
                    negation = not negation
                if word in self.sentiment:
                    result = self.sentiment[word]
                    last_seen = result
                    # if word is "strong" such as love or hate, will increase count by 2 rather than 1
                    # however, if word is preceded by negation, this will be neutral (e.g. i don't love "titanic")
                    if word in self.strong_words:
                        if negation:
                            increase = 0
                        else:
                            increase = 2
                    else:
                        increase = 1

                    if result == "neg":
                        if negation:
                            pos_count += (increase + emph_count)
                        else:
                            neg_count += (increase + emph_count)
                    else:
                        if negation:
                            neg_count += (increase + emph_count)
                        else:
                            pos_count += (increase + emph_count)
                    # at this point emph_count should have been added to pos or neg_count, so reset
                    if emph_count != 0:
                        emph_count = 0
            # checks if emph_count is nonzero but has not been added to yet pos or neg_count yet
            if emph_count != 0 and last_seen != "":
                if last_seen == "neg":
                    if negation:
                        pos_count += emph_count
                    else:
                        neg_count += emph_count

                elif last_seen == "pos":
                    if negation:
                        neg_count += emph_count
                    else:
                        pos_count += emph_count

            if pos_count - neg_count > 1:
                return 2
            elif pos_count > neg_count:
                return 1
            elif neg_count - pos_count > 1:
                return -2
            elif neg_count > pos_count:
                return -1
            else:
                return 0
        
        # convert to lowercase
        query = preprocessed_input.lower()
        # remove things in quotes
        query = re.sub('".*"', '', query)
        # split by words and punctuation
        query = re.findall("[\w'-]+|[.,?!;:]", query)
        # stem words
        query = [self.p.stem(xx) for xx in query]

        if self.creative:
            return fine_grained_extract_sentiment(query)
        
        negation = False
        pos_count = 0
        neg_count = 0
        
        for word in query:
            if word in self.negations:
                negation = not negation
            if re.match('[.,?!;:]', word) and negation:
                negation = not negation
            if word in self.sentiment:
                result = self.sentiment[word]
                if result == "neg":
                    if negation:
                        pos_count += 1
                    else:
                        neg_count += 1
                else:
                    if negation:
                        neg_count += 1
                    else:
                        pos_count += 1
        if pos_count > neg_count:
            return 1
        elif neg_count > pos_count:
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
        output = []
        titles = self.extract_titles(preprocessed_input)
        # checks that there is at least one movie
        if len(titles) >= 1:
            # normal call to extract_sentiment for one movie
            if len(titles) == 1:
                res = self.extract_sentiment(preprocessed_input)
                output.append((titles[0], res))
            else:
                # multi-movie case
                contains = [x for x in self.opposite if(x in preprocessed_input)]
                if contains:
                    # split by opposite words (but, however, etc.)
                    parts = preprocessed_input.split(contains[0])
                    for title in titles:
                        for part in parts:
                            if title in part:
                                res = self.extract_sentiment(part)
                                output.append((title, res))
                                continue
                else:
                    # check if all movies have same sentiment (and, both, neither, etc)
                    contains = [x for x in self.multiple if(x in preprocessed_input)]
                    if contains:
                        res = self.extract_sentiment(preprocessed_input)
                        for title in titles:
                            output.append((title, res))
        
        return output

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
        #given a title, removes the year from the end, and returns the title along with the year
        #in the format " (xxxx)" for the year
        #returns empty string for year if there is no year provided in the title
        def remove_year(title):
            pattern = '( \([0-9\-]+\))$'
            years = re.findall(pattern, title)
            if years == []:
                return title, ''
            else:
                year = years[0]
                start = title.replace(year, '')
                return start, year

        #given a misspelled title and a real title, return the edit distance between them
        def edit_distance(misspelling, title, max_dist):
            #initialization
            d = np.zeros((len(misspelling) + 1, len(title) + 1))
            for i in range(len(misspelling)+1):
                d[i, 0] = i
            for j in range(len(title)+1):
                d[0, j] = j

            #recurrence relation
            for i in range(1, len(misspelling)+1):
                for j in range(1, len(title)+1):
                    options = []
                    options.append(d[i-1,j] + 1)
                    options.append(d[i,j-1] + 1)
                    if misspelling[i-1] == title[j-1]:
                        options.append(d[i-1,j-1])
                    else:
                        options.append(d[i-1,j-1] + 2)
                    d[i, j] = min(options)

            return d[len(misspelling), len(title)]


        closest = []
        title = title.lower()
        start, year = remove_year(title)

        #if title has year
        if year != '':
            for i in range(len(self.titles)):
                options = [self.titles[i][0].lower()]
                if re.search(', the \([0-9]', options[0]):
                    options.append('the '+options[0][:-12]+options[0][-7:])
                dist = 999999
                for option in options:
                    dist = min(dist, edit_distance(title, option, max_distance))
                #if closest so far, make new closest array
                if dist < max_distance:
                    max_distance = dist
                    closest = [i]
                #if at max_distance, add to closest array
                elif dist == max_distance:
                    closest.append(i)
        #if title doesn't have year provided
        else:
            for i in range(len(self.titles)):
                #remove years from titles in dataset
                start, _ = remove_year(self.titles[i][0])
                options = [start.lower()]
                if re.search(', the$', options[0]):
                    options.append('the '+options[0][:-5])
                dist = 9999
                for option in options:
                    dist = min(dist, edit_distance(title, option, max_distance))
                #if closest so far, make new closest array
                if dist < max_distance:
                    max_distance = dist
                    closest = [i]
                #if at max_distance, add to closest array
                elif dist == max_distance:
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
        def remove_year(title):
            pattern = '( \([0-9\-]+\))$'
            years = re.findall(pattern, title)
            if years == []:
                return title, ''
            else:
                year = years[0]
                start = title.replace(year, '')
                return start, year


        matches = []
        pattern = '^[0-9][0-9]+$'
        years = re.findall(pattern, clarification)
        if years != []: #if clarification is just a year, only look at years
            for index in candidates:
                _, year = remove_year(self.titles[index][0])
                if clarification in year:
                    matches.append(index)
        else:
            for index in candidates:
                title, _ = remove_year(self.titles[index][0])
                if clarification.lower() in title.lower():
                    matches.append(index)
            if len(matches) == 0:
                for index in candidates:
                    title = self.titles[index][0]
                    if clarification.lower() == title.lower():
                        matches.append(index)
        return matches

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
        binarized_ratings = np.where(ratings > threshold, 1, binarized_ratings) #replaces all values above threshold with 1
        binarized_ratings = np.where(np.logical_and(ratings >= 0.5, ratings <= 2.5), -1, binarized_ratings)

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
        if np.all(u == 0) or np.all(v == 0):
            return 0
        else:
            return np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
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

        #this part doesn't use the similarity() function becauese I would have
        #needed to use a for loop.
        def compute_similarity_matrix(ratings_matrix):
            norm = np.linalg.norm(ratings_matrix, axis=1) #array has shape (n_movies,)
            norm = np.where(norm == 0, 1, norm)  # prevent divide by zero
            similarity_matrix = ratings_matrix.dot(ratings_matrix.T) / norm[:, None] #computes the dot product between each pair of movies
            similarity_matrix /= norm[None, :] #normalizes each row
            similarity_matrix = np.nan_to_num(similarity_matrix) #replaces NaN values with 0 to prevent error
            return similarity_matrix

        # Compute similarity matrix between pairs of movies
        similarity_matrix = compute_similarity_matrix(ratings_matrix)
        has_rated = {}
        #create a dictionary of all the rated movies: [movie index, rating]
        for movie_index, rating in enumerate(user_ratings):
            if rating != 0:
                has_rated[movie_index] = rating

        #For each movie (of all the movies), calculate the recommendation prediction score
        #Here, reccomendation prediction score refers to step 3 on Week 8, RS5 video at 1:21 seconds
        recommend_scores = {}
        for movie_index in range(ratings_matrix.shape[0]):
            if user_ratings[movie_index] == 0:
                score = 0
                for rated_movie in has_rated.keys():
                    score += similarity_matrix[movie_index][rated_movie] * user_ratings[rated_movie]
                recommend_scores[movie_index] = score

        #sort in order from highest to lowest recommendation score
        recommendations = sorted(recommend_scores, key=recommend_scores.get, reverse=True)[:k]
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
        TODO: Write here the description for your own chatbot!
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
