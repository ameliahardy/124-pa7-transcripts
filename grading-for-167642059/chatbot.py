# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import numpy as np
from porter_stemmer import PorterStemmer
import random
import re

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False): 
        self.name = 'YodaBot'
        self.creative = creative
        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.porter_stemmer = PorterStemmer()
        self.stemmed_sentiment = {self.porter_stemmer.stem(k):v for k, v in self.sentiment.items()}
        
        #Emotion detection
        # 0. Happy, 1. Sad, 2. Fear, 3. Anger 4. Neutral
        ########################################################################
        self.happy_list = ['happy','joy','blissfulness','bliss','joyfulness','enjoyment','beatitude','blessedness','satisfaction','felicity','pleasure','gladness','ecstasy','elation','delight','exultation','cheerfulness','euphoria','exhilaration','contentedness','comfort','joyousness','glee']
        self.sad_list = ['sad','sorry','bad','melancholy','upset','worried','sorrowful','disappointed','saddened','mournful','uneasy','hopeless','dejected','heartsick','troubled','gloomy','forlorn','crestfallen','doleful','melancholic','depressing','glum','downhearted']
        self.fear_list = ['fear', 'anxiety','fearfulness','dread','panic','terror','trepidation','fright','scare','horror','concern','dismay','alarm','phobia','nervousness','apprehension','pang','alarum','agitation','jitters','qualm','creeps']
        self.anger_list = ['anger','indignation','rage','fury','outrage','irritation','mood','wrathfulness','resentment','exasperation','mad','jealousy','bitterness','irritability','hostility','contempt','madness','ire','annoyance','angriness','choler','spleen','temper','malice']
        
        self.stemmed_happy = [self.porter_stemmer.stem(w) for w in self.happy_list]
        self.stemmed_sad = [self.porter_stemmer.stem(w) for w in self.sad_list]
        self.stemmed_fear = [self.porter_stemmer.stem(w) for w in self.fear_list]
        self.stemmed_anger = [self.porter_stemmer.stem(w) for w in self.anger_list]
        ########################################################################
        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings)
        ratings = self.binarize(ratings)
        ########################################################################
        self.num_movies = np.shape(self.ratings)[0]
        self.num_ratings = np.shape(self.ratings)[1]
        ########################################################################
        self.movie_input_counter = 0
        self.user_ratings = [0] * self.num_movies
        self.disambiguating = False
        self.prior_indices = []
        self.prior_sentiment = 0
        self.spellcheck = False
        self.given_recommendations = 0

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        if self.creative:
            r = random.randint(0, 2)
            if r == 0:
                greeting_message = "Hi, {} the movie recommender I am. Movie reviews You give to me, and help you I can.".format(self.name)
            elif r == 1:
                greeting_message = "Hello! Yoda, my name is, and I can recommend you movies. Me about a couple of movies you like or dislike tell. Hrmmm.".format(self.name)
            elif r == 2:
                greeting_message = "Hi there, Yoda I am! Movies I recommend based on your movie preferences. Me about a movie you like or dislike, start by telling.".format(self.name)
        else:
            r = random.randint(0, 2)
            if r == 0:
                greeting_message = "Hi, {} the movie recommender I am. Movie reviews You give to me, and help you I can.".format(self.name)
            elif r == 1:
                greeting_message = "Hello! My name is {} and I can recommend you movies. Tell me about a couple of movies you like or dislike.".format(self.name)
            elif r == 2:
                greeting_message = "Hi there, I'm {}! I recommend movies based on your movie preferences. Start by telling me about a movie you like or dislike.".format(self.name)
        return greeting_message

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        if self.creative:
            r = random.randint(0, 2)
            if r == 0:
                goodbye_message = "Good-bye. Miss you I will. Good friend you are. For this conversation, much gratitude and respect, I have."
            elif r == 1:
                goodbye_message = "For talking to me, thank you. See you again soon, I hope!"
            elif r == 2:
                goodbye_message = "For using {}, thank you. A lot of fun I had. Come back if you need more movie recommendations!".format(self.name)
        else:
            r = random.randint(0, 2)
            if r == 0:
                goodbye_message = "Have a nice day!"
            elif r == 1:
                goodbye_message = "Thank you for talking with me. Hope to see you again soon!"
            elif r == 2:
                goodbye_message = "Thanks for using {}. I had a lot of fun. Come back if you need more movie recommendations!".format(self.name)
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
        # Emotion recognition function
        def detectEmotion(line):
            line = line.lower()
            vals = np.zeros(4)
            word_list = re.findall(r"[\w']+|[.,!?;]", line)
            emotion = {0: 'Happy', 1: 'Sad', 2: 'Fear', 3: 'Anger', 4: 'Neutral'}
            
            for w in word_list:
                if w in self.happy_list or self.porter_stemmer.stem(w) in self.stemmed_happy:
                    vals[0] += 1
                elif w in self.sad_list or self.porter_stemmer.stem(w) in self.stemmed_sad:
                    vals[1] += 1
                elif w in self.fear_list or self.porter_stemmer.stem(w) in self.stemmed_fear:
                    vals[2] += 1
                elif w in self.anger_list or self.porter_stemmer.stem(w) in self.stemmed_anger:
                    vals[3] += 1

            if len(set(vals)) == 1:
                return emotion[4]
            else:
                return emotion[np.argmax(vals)]
            
        if self.creative:
            line = self.preprocess(line)
            if self.given_recommendations > 0 and (line.lower() == "yes" or line.lower() == "y" or line.lower() == "yep" or line.lower() == "yup"):
                r = random.randint(0, 2)
                if r == 0:
                    response = " I would also recommend the movie {}.".format(''.join(self.movie_recommendations[self.given_recommendations]))
                elif r == 1:
                    response = " I think you would also like the movie {}.".format(''.join(self.movie_recommendations[self.given_recommendations]))
                elif r == 2:
                    response = " You also should check out {}.".format(''.join(self.movie_recommendations[self.given_recommendations]))
                response += " Would you like to hear another recommendation? (Or enter :quit if you're done.)"
                self.given_recommendations += 1
                return response
            line_emotion = detectEmotion(line)
            if self.disambiguating or self.spellcheck:  # If last line was ambiguous, keep sentiment and titles from previous input
                sentiment = self.prior_sentiment
                movie_titles = self.prior_movie_titles
            else:
                sentiment = self.extract_sentiment(line)
                movie_titles = self.extract_titles(line)
            r = random.randint(0, 2)
            r1 = random.randint(0, 2)
            response = ""
            if len(movie_titles) == 0:
                question = False
                q = random.randint(0, 2)
                if line.endswith("?"): # Remove '?' to answer a question
                    question = True
                    line = line[:-1]
                if line.lower().startswith("can you "):
                    response += "No, I cannot" + line[7: ] + "."
                elif line.lower().startswith("will you"):
                    response += "No, I will not" + line[8: ] + "."
                elif line.lower().startswith("what is "):
                    response += "I don't know what" + line[7: ] + " is."
                elif line.lower().startswith("where is "):
                    response += "I don't know where" + line[8: ] + " is."
                elif line.lower().startswith("how do I "):
                    response += "I don't know how to" + line[8: ] + "."
                elif question:
                    if q == 0:
                        response += "A question, that is. The answer, know I do not."
                    elif q == 1:
                        response += "The answer to that question, wish I knew I do."
                    elif q == 2:
                        response += "Perplexing question, that is. Beyond my capabilities to answer, that is."
                elif line_emotion == 'Neutral':
                    if r1 == 0:
                        response += "Talk about that, I do not want to right now."
                    elif r1 == 1:
                        response += "On the topic of movies, stay we must."
                    elif r1 == 2:
                        response += "Interesting, that is. "
                    if r == 0:
                        response += " Instead, put quotation marks around a movie title. My specialty, that is. Yeesssssss."
                    elif r == 1:
                        response += " Movie titles, put quotation marks around them, understand that I do."
                    elif r == 2:
                        response += " Sorry, I don't understand. Happy to give movie recommendations, I am, if quotations marks around titles, you put."
                else:
                    em = ''
                    if line_emotion == 'Happy':
                        em = 'happiness'
                    elif line_emotion == 'Sad':
                        em = 'sadness'
                    else:
                        em = line_emotion.lower()
                    response += "Your " + em + ", feel it I do."
                r = random.randint(0, 2)
                if r == 0:
                    response += " A movie recommender I am, remember that you must."
                elif r == 1:
                    response += " Sorry, limited I am. Just a movie recommender, remember I am."
                elif r == 2:
                    response += " Only limited to recommending you movies, my capacity is."
            elif len(movie_titles) != 1:
                if r == 0:
                    response = "One movie at a time, please tell me."
                elif r == 1:
                    response = "Process multiple movies at once I cannot. Like or dislike a movie, one at a time you tell me."
                elif r == 2:
                    response = "More than one movie I noticed you gave. About the movies again one at a time can you tell me?"
            else:
                if self.spellcheck:
                    if line.lower().startswith("y"):
                        movie_title_index = self.prior_indices
                        self.spellcheck = False
                if self.disambiguating:
                    movie_title_index = self.disambiguate(line, self.prior_indices)
                    self.disambiguating = False
                else:
                    movie_title_index = self.find_movies_by_title(movie_titles[0])
                if len(movie_title_index) == 0:
                    spellcheck_indices = self.find_movies_closest_to_title(movie_titles[0], 3)
                    r = random.randint(0,2)
                    if len(spellcheck_indices) == 0:
                        if r == 0:
                            response = "Of {} I've never heard, sorry. Me about another movie tell. Hmm.".format(movie_titles[0].title())
                        elif r == 1:
                            response = "Sorry, understand the movie name you gave me I do not. Can you try again with a different movie?"
                        elif r == 2:
                            response = "In my database {} doesn't seem to be. Please try again. Hrmmm.".format(movie_titles[0].title())
                    elif len(spellcheck_indices) != 1:
                        movie_list = []
                        for ind in spellcheck_indices:
                            movie_list.append(self.titles[ind][0])
                        
                        if r == 0:
                            response = "Wrong spelling possibly. Did you mean one of these: \"{}\"? If so, a correctly spelled movie name you must type.".format(movie_list)
                        elif r == 1:
                            response = "Close you were, but far you were. Did you mean one of these: \"{}\"? If so, a correctly spelled movie name you must type.".format(movie_list)
                        elif r == 2:
                            response = "Typo you did commit. Did you mean one of these: \"{}\"? If so, a correctly spelled movie name you must type.".format(movie_list)
                    else:
                        self.spellcheck = True
                        movie_list = []
                        for ind in spellcheck_indices:
                            movie_list.append(self.titles[ind][0])
                        self.spellcheck = True
                        self.prior_indices = spellcheck_indices
                        self.prior_sentiment = sentiment
                        self.prior_movie_titles = movie_list
                        if r == 0:
                            response = "Wrong spelling possibly. Did you mean \"{}\"? If so, type yes or no.".format(movie_list[0].title())
                        elif r == 1:
                            response = "Close you were, but far you were. Did you mean \"{}\"? If so, type yes or no.".format(movie_list[0].title())
                        elif r == 2:
                            response = "Typo you did commit. Did you mean \"{}\"? If so, type yes or no.".format(movie_list[0].title())
                elif len(movie_title_index) > 1:  # Multiple options, call line ambiguous and get clarifying input
                    movie_list = []
                    for ind in movie_title_index:
                        movie_list.append(self.titles[ind][0])
                    
                    self.disambiguating = True
                    self.prior_sentiment = sentiment
                    self.prior_movie_titles = movie_titles
                    self.prior_indices = movie_title_index

                    if r == 0:
                        response = "More than one movie called \"{}\", I found. ".format(movie_titles[0].title())
                    elif r == 1:
                        response = "Multiple movies by that name there are. Yess."
                    elif r == 2:
                        response = "There are many movies called \"{}\", my database shows. Yrsssss.".format(movie_titles[0].title())
                    r = random.randint(0, 2)
                    if r == 0:
                        response += " Hrmmm. Clarify which one using a key word or year, can you?: \"{}\"".format('\", \"'.join(movie_list))
                    elif r == 1:
                        response += " Which one did you mean? A key word or year you may use: \"{}\"".format('\", \"'.join(movie_list))
                    elif r == 2:
                        response += " One of these specify please. A key word or year helpful it is: \"{}\"".format('\", \"'.join(movie_list))
                else:
                    actual_movie_title = self.titles[movie_title_index[0]][0]
                    if sentiment == 1:
                        if r == 0:
                            response = "You liked {}!".format(''.join(actual_movie_title))
                        elif r == 1:
                            response = "I'm glad to hear that you liked the movie {}.".format(''.join(actual_movie_title))
                        elif r == 2:
                            response = "Great, so you liked {}.".format(''.join(actual_movie_title))
                        self.movie_input_counter += 1
                    elif sentiment == -1:
                        if r == 0:
                            response = "You disliked {}.".format(''.join(actual_movie_title))
                        elif r == 1:
                            response = "I'm sorry to hear that you disliked the movie {}.".format(''.join(actual_movie_title))
                        elif r == 2:
                            response = "Okay, so you disliked {}.".format(''.join(actual_movie_title))
                        self.movie_input_counter += 1
                    elif sentiment == 0:
                        if r == 0:
                            response = "I'm sorry, I'm not sure if you liked {}. Tell me more about it.".format(''.join(actual_movie_title))
                        elif r == 1:
                            response = "It seems like you were neutral with the movie {}. If this is incorrect, tell me more about it.".format(''.join(actual_movie_title))
                        elif r == 2:
                            response = "Wait, so did you like or dislike {}?".format(''.join(actual_movie_title))   
                    else:
                        print("\n\nERROR, sentiment is not 0, 1, or -1\n\n")
                    self.user_ratings[movie_title_index[0]] = sentiment
                    if (sentiment == -1 or sentiment == 1) and self.movie_input_counter < 5:
                        r = random.randint(0, 2)
                        if r == 0:
                            response += " Tell me about more movies!"
                        elif r == 1:
                            response += " What other movies have you seen and did you like or dislike them?"
                        elif r == 2:
                            response += " Tell me about movies that you have a strong feeling about."
                    if self.movie_input_counter == 5:
                        movie_recommendations_indices = self.recommend(self.user_ratings, self.ratings)
                        movie_recommendations = [self.titles[movie_recommendations_index][0] for movie_recommendations_index in movie_recommendations_indices]
                        r = random.randint(0, 2)
                        if r == 0:
                            response += " I have all the information I need for now. Based on that, I would recommend the movie {}.".format(''.join(movie_recommendations[0]))
                        elif r == 1:
                            response += " Based on the movie preferences you have me, I think you would like the movie {}.".format(''.join(movie_recommendations[0]))
                        elif r == 2:
                            response += " I think I have a good sense of what kinds of movies you like. You should check out {}".format(''.join(movie_recommendations[0]))
                        response += " Would you like to hear another recommendation? (Or enter :quit if you're done.)"
        else:
            if self.given_recommendations > 0 and (line.lower() == "yes" or line.lower() == "y" or line.lower() == "yep" or line.lower() == "yup"):
                r = random.randint(0, 2)
                if r == 0:
                    response = " I would also recommend the movie {}.".format(''.join(self.movie_recommendations[self.given_recommendations]))
                elif r == 1:
                    response = " I think you would also like the movie {}.".format(''.join(self.movie_recommendations[self.given_recommendations]))
                elif r == 2:
                    response = " You also should check out {}.".format(''.join(self.movie_recommendations[self.given_recommendations]))
                response += " Would you like to hear another recommendation? (Or enter :quit if you're done.)"
                self.given_recommendations += 1
                return response
            line = self.preprocess(line)
            sentiment = self.extract_sentiment(line)
            movie_titles = self.extract_titles(line)
            r = random.randint(0, 2)
            if len(movie_titles) == 0:
                if r == 0:
                    response = "Please put quotation marks around the movie title."
                elif r == 1:
                    response = "Sorry, I don't understand movie titles if they don't have quotation marks around them."
                elif r == 2:
                    response = "Sorry, I don't understand what you mean."
            elif len(movie_titles) != 1:
                if r == 0:
                    response = "Please tell me about one movie at a time."
                elif r == 1:
                    response = "Sorry, I can't process multiple movies at once. Tell me if you like or dislike one movie at a time."
                elif r == 2:
                    response = "I noticed you gave me more than one movie. Can you tell me about the movies again one at a time?"
            else:
                movie_title_index = self.find_movies_by_title(movie_titles[0])
                if len(movie_title_index) == 0:
                    if r == 0:
                        response = "I've never heard of {}, sorry. Tell me about another movie.".format(movie_titles[0].title())
                    elif r == 1:
                        response = "Sorry, I don't understand the movie name you gave me. Can you try again with a different movie?"
                    elif r == 2:
                        response = "{} doesn't seem to be in my database. Please try again.".format(movie_titles[0].title())
                elif len(movie_title_index) > 1:
                    if r == 0:
                        response = "I found more than one movie called \"{}\".".format(movie_titles[0].title())
                    elif r == 1:
                        response = "There are multiple movies by that name."
                    elif r == 2:
                        response = "My database shows there are many movies called \"{}\".".format(movie_titles[0].title())
                    r = random.randint(0, 2)
                    if r == 0:
                        response += " Can you clarify?"
                    elif r == 1:
                        response += " Can you input the movie name followed by its year of release in parentheses?"
                    elif r == 2:
                        response += " Please specify the movie's year of release."
                else:
                    actual_movie_title = self.titles[movie_title_index[0]][0]
                    if sentiment == 1:
                        if r == 0:
                            response = "You liked {}!".format(''.join(actual_movie_title))
                        elif r == 1:
                            response = "I'm glad to hear that you liked the movie {}.".format(''.join(actual_movie_title))
                        elif r == 2:
                            response = "Great, so you liked {}.".format(''.join(actual_movie_title))
                        self.movie_input_counter += 1
                    elif sentiment == -1:
                        if r == 0:
                            response = "You disliked {}.".format(''.join(actual_movie_title))
                        elif r == 1:
                            response = "I'm sorry to hear that you disliked the movie {}.".format(''.join(actual_movie_title))
                        elif r == 2:
                            response = "Okay, so you disliked {}.".format(''.join(actual_movie_title))
                        self.movie_input_counter += 1
                    elif sentiment == 0:
                        if r == 0:
                            response = "I'm sorry, I'm not sure if you liked {}. Tell me more about it.".format(''.join(actual_movie_title))
                        elif r == 1:
                            response = "It seems like you were neutral with the movie {}. If this is incorrect, tell me more about it.".format(''.join(actual_movie_title))
                        elif r == 2:
                            response = "Wait, so did you like or dislike {}?".format(''.join(actual_movie_title))   
                    else:
                        print("\n\nERROR, sentiment is not 0, 1, or -1\n\n")
                    self.user_ratings[movie_title_index[0]] = sentiment
                    if (sentiment == -1 or sentiment == 1) and self.movie_input_counter < 5:
                        r = random.randint(0, 2)
                        if r == 0:
                            response += " Tell me about more movies!"
                        elif r == 1:
                            response += " What other movies have you seen and did you like or dislike them?"
                        elif r == 2:
                            response += " Tell me about movies that you have a strong feeling about."
                    if self.movie_input_counter == 5:
                        movie_recommendations_indices = self.recommend(self.user_ratings, self.ratings)
                        self.movie_recommendations = [self.titles[movie_recommendations_index][0] for movie_recommendations_index in movie_recommendations_indices]
                        r = random.randint(0, 2)
                        if r == 0:
                            response += " I have all the information I need for now. Based on that, I would recommend the movie {}.".format(''.join(self.movie_recommendations[0]))
                        elif r == 1:
                            response += " Based on the movie preferences you have me, I think you would like the movie {}.".format(''.join(self.movie_recommendations[0]))
                        elif r == 2:
                            response += " I think I have a good sense of what kinds of movies you like. You should check out {}.".format(''.join(self.movie_recommendations[0]))
                        self.given_recommendations += 1
                        response += " Would you like to hear another recommendation? (Or enter :quit if you're done.)"
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
        return re.findall('"([^"]*)"', preprocessed_input) # extract from "" marks

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

        # Idea: have title be in the format of "The Blade Runner (2017)" --> adjust extract_titles
        # This function then extracts a year (if there is one) and the title name
        # If no year, have to be able to find all movies with that title

        # regex gets title name
        if self.creative:
            indices = []
            given_movie_title = re.sub(r" ?\([^)]+\)", "", title).lower()
            if given_movie_title.startswith("a "):
                given_movie_title = given_movie_title[2:] + ", a"
            elif given_movie_title.startswith("an "):
                given_movie_title = given_movie_title[3:] + ", an"
            elif given_movie_title.startswith("the "):
                given_movie_title = given_movie_title[4:] + ", the"
            given_movie_year = re.findall(r"\((.*?)\)", title)
            for i in range(len(self.titles)):
                movie_title_year = self.titles[i][0]
                movie_titles = [re.sub(r" ?\([^)]+\)", "", movie_title_year).lower()]
                movie_year = re.findall(r"\((.*?)\)", movie_title_year)
                alternate_titles = re.findall(r"\(a\.k\.a\. (.*?)\)", self.titles[i][0].lower())
                movie_titles = movie_titles + alternate_titles
                for movie_title in movie_titles:
                    if re.search(r"\b{}\b".format(given_movie_title), movie_title, re.IGNORECASE) is not None and given_movie_year == movie_year:
                        indices.append(i)
                    elif len(given_movie_year) == 0 and re.search(r"\b{}\b".format(given_movie_title), movie_title, re.IGNORECASE) is not None:
                        indices.append(i)
            return list(set(indices))
        else:
            indices = []
            given_movie_title = re.sub(r" ?\([^)]+\)", "", title).lower()
            if given_movie_title.startswith("a "):
                given_movie_title = given_movie_title[2:] + ", a"
            elif given_movie_title.startswith("an "):
                given_movie_title = given_movie_title[3:] + ", an"
            elif given_movie_title.startswith("the "):
                given_movie_title = given_movie_title[4:] + ", the"
            given_movie_year = re.findall(r"\((.*?)\)", title)
            for i in range(len(self.titles)):
                movie_title_year = self.titles[i][0]
                movie_title = re.sub(r" ?\([^)]+\)", "", movie_title_year).lower()
                movie_year = re.findall(r"\((.*?)\)", movie_title_year)
                if movie_title == given_movie_title and given_movie_year == movie_year:
                    indices.append(i)
                elif len(given_movie_year) == 0 and movie_title == given_movie_title:
                    indices.append(i)
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
        input = re.sub('"([^"]*)"', '', preprocessed_input)
        word_list = re.findall(r"[\w']+|[.,!?;]", input)
        negation_words = ["no", "not", "rather", "couldn't", "wasn't", "didn't", "wouldn't", "shouldn't", "weren't", "don't",
                     "doesn't", "haven't", "hasn't", "won't", "wont", "hadn't", "never", "none", "nobody", "nothing",
                     "neither", "nor"]
        result = 0
        score = 1
        for word in word_list:
            if word in negation_words:
                score = -1
            elif not word.isalpha():
                score = 1
            elif word in self.sentiment:
                if self.sentiment[word] == 'pos':
                    result += score * 1
                elif self.sentiment[word] == 'neg':
                    result += score * -1
            elif self.porter_stemmer.stem(word) in self.stemmed_sentiment:
                if self.stemmed_sentiment[self.porter_stemmer.stem(word)] == 'pos':
                    result += score * 1
                elif self.stemmed_sentiment[self.porter_stemmer.stem(word)] == 'neg':
                    result += score * -1
        if result < 0:
            return -1
        elif result > 0:
            return 1
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
        pass
               

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
        closest_movies = []
        title = title.lower()
        if title.startswith("a "):
            title = title[2:] + ", a"
        elif title.startswith("an "):
            title = title[3:] + ", an"
        elif title.startswith("the "):
            title = title[4:] + ", the"
        curr_min = max_distance
        def editDistance(string1, string2):
            m = len(string1)
            n = len(string2)
            
            dp = np.zeros((m + 1, n + 1))
            dp[:, 0] = np.arange(0, m + 1)
            dp[0] = np.arange(0, n + 1)
            
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if string1[i - 1] == string2[j - 1]:
                        dp[i][j] = dp[i - 1][j - 1]
                    else:
                        dp[i][j] = min(dp[i - 1][j - 1] + 2, dp[i - 1][j] + 1, dp[i][j - 1] + 1)  
            return dp[m][n]
        
        for i in range(len(self.titles)):
            movie_title_year = self.titles[i][0]
            movie_title = str(re.sub(r" ?\([^)]+\)", "", movie_title_year)).lower()
            distance = editDistance(title, movie_title)
            if distance == curr_min:
                closest_movies.append(i)
            elif distance < curr_min:
                closest_movies = []
                curr_min = distance
                closest_movies.append(i)
        return closest_movies

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
        return [c for c in candidates 
            if clarification.lower() in re.sub(r" ?\([^)]+\)", "", self.titles[c][0]).lower() 
            or clarification in re.findall(r"\((.*?)\)", self.titles[c][0])]

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
        binarized_ratings = np.where(ratings > threshold, 1,
                                                       (np.where(ratings == 0, ratings, -1)))
        return binarized_ratings

    def similarity(self, u, v):
        """Calculate the cosine similarity between two vectors.

        You may assume that the two arguments have the same shape.

        :param u: one vector, as a 1D numpy array
        :param v: another vector, as a 1D numpy array

        :returns: the cosine similarity between the two vectors
        """
        similarity = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
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
        recommendations = []
        for i in range(len(ratings_matrix)):
            rated_indices = np.nonzero(user_ratings)
            curr_movie_rating = np.sum([self.similarity(ratings_matrix[i], ratings_matrix[j]) * user_ratings[j]
                                 for j in rated_indices[0] if user_ratings[j] != 0 and i != j and np.linalg.norm(ratings_matrix[i]) != 0])
            recommendations.append([curr_movie_rating, i])
        recommendations = np.array(recommendations)
        recommendations = recommendations[np.argsort(recommendations[:,0])] # sorts by column
        recommendations = [int(i[1]) for i in recommendations[-k:]]  # get k highest scores, get index of those movies
        return recommendations[::-1]

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
        YodaBot can respond to regular speech, analyze a users sentiment of movies, 
        and give a recomendation of a new movie that the user may like given their 
        original preferences. When a user enters information about a movie, the movie
        should be enclosed in quotes and the users opinion on the movie should be
        provided. After providing five movie sentiments, YodaBot will return its movie
        recomendation. 
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
