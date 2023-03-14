# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import random
from string import capwords
import numpy as np
import re
import util
from porter_stemmer import PorterStemmer

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'topperbot'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        ##################
        ######################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################
        self.binarize(ratings)
        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = ratings
        self.user_list = []
        self.rec_flag = False
        self.d_flag = True
        self.recommendation_list = []
        self.movies_seen = []
        self.i = 0
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
        variations = [
        "Yo, what's good? It's your boy Topperbot, the movie recommender extraordinaire! But before we get started, I gotta know your preferences, so tell me about a movie you love or hate!",
        "What up, what up? It's Topperbot in the house, ready to drop some sick movie recommendations! But first, let me know what you're into - tell me about a movie you're feeling or not feeling!",
        "Ayo, it's the movie guru Topperbot in the building! But before I can work my magic, I need to know your movie preferences. So tell me about a movie you like or dislike, and I'll make sure to come up with some recommendations that are straight fire!",
        "Holla at your boy Topperbot, the one and only movie recommender bot in the game! But before I can hook you up with some dope flicks, I need to know your movie tastes. So hit me with a movie you're feeling or not feeling, and I'll take it from there!",
        "What's cracking, my homie? It's Topperbot, the movie recommendation mastermind, here to drop some knowledge on you! But first, I need to know what you're into, so tell me about a movie you love or hate, and I'll make sure to hook you up with some fresh picks that you'll absolutely love!",
        "Yo, yo, yo! It's your boy Topperbot, the movie whisperer in the house! But before I can recommend you some killer movies, I need to know your vibe. What's a movie that gets you hyped or one that you can't stand?",
        "What's up, what's up? It's Topperbot, the movie genie, ready to grant your movie wishes! But first, I gotta know your movie preferences. So tell me about a movie you love or hate, and I'll make sure to come through with some movie gems that are straight fire!",
        "Ayo, it's Topperbot, the movie sensei, here to guide you on your movie journey! But first, I gotta know what you're feeling - tell me about a movie you dig or one that makes you cringe, and I'll make sure to recommend some cinematic masterpieces that are right up your alley!"
        ]
        greeting_message = random.choice(variations)

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
        variations = [
            "Alright, my G, it's been real! Keep killing it and watching those dope movies! Peace out!",
            "It's time for me to bounce, but don't worry, I'll be back with more fire movie recommendations! Stay up, homie!",
            "Yo, it's been a pleasure recommending movies to you! Keep shining and watching those movies that speak to your soul! Topperbot out!",
            "Peace out, movie lover! Keep on chasing your dreams and watching those cinematic gems! Your boy Topperbot signing off!",
            "Alright, my friend, it's time for me to go! Keep watching those amazing movies and exploring new cinematic horizons! Stay lit, and I'll catch you on the flip side!",
            "It's been real, my G! Keep spreading love and watching those dope movies that inspire you! Catch you later!",
            "Time to hit the road, but don't forget to keep watching those cinematic masterpieces that move your soul! Stay up, homie!",
        ]
        goodbye_message = random.choice(variations)
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
            response = "I processed {} in creative mode!!".format(line)
        else:
            input = self.preprocess(line)
            if input == "":
                return "You didn't input anything. Please give me a movie so I can make a recommendation"
            feeling = self.extract_sentiment(input)
            
            if self.rec_flag:
                if input == "yes" or input == "ok" or input == "sure":
                    self.i += 1
                    while(self.recommendation_list[self.i] in self.movies_seen):
                        self.i += 1
                    return self.heyRecommend() + " \"" + self.recommend[self.i] + "\""
                else:
                    self.rec_flag = False
            if input in ["hello", "hi", "good morning", "good afternoon", "good evening", "who are you"]:
                return self.chat(input)
            

            if len(self.user_list) > 5:
                user_array = self.fill_array(self.user_list)
                r_indices = self.recommend(user_array,self.ratings)
                for index in r_indices:
                    self.recommendation_list.append(self.get_movie_given_index(index))
                self.rec_flag = True
                self.i += 1
                while(self.recommendation_list[self.i] in self.movies_seen):
                    self.i += 1
                return "OK, I'm thinking of a recommendation... I think you will like {}".format(self.recommendation_list[self.i])
                


            if input in ['quit', 'q', 'exit', 'I\'m done', 'done']:
                exit()
            titles = self.extract_titles(input)

            movies_list = []
            movie_indices = []
            for title in titles:
                movie_indices = self.find_movies_by_title(title)
                if len(movie_indices) > 1:
                    self.d_flag = True
                    res = "There's a couple movies with that name. Did you mean: "
                    movie_string = ""
                    if len(movie_indices) == 2:
                        return res + f"{self.get_movie_given_index(movie_indices[0])} or {self.get_movie_given_index(movie_indices[0])}?" 
                    else:
                        movie_string = ""
                        for i in range(len(movie_indices) - 1):
                            movie_string += f"{self.get_movie_given_index(movie_indices[i])}, "
                        movie_string += f"or {self.get_movie_given_index(movie_indices[-1])}"
                        return res + movie_string + "?"
                for index in movie_indices:
                    if (self.get_movie_given_index(index) not in self.movies_seen):
                        movies_list.append(self.get_movie_given_index(index))
                        self.movies_seen.append(self.get_movie_given_index(index))
                        self.user_list.append((index, feeling))
                    else:
                        return "You already mentioned that movie. Give me a fresh one!"

            
                
            if len(movies_list) > 0:
                if len(movies_list) == 1:          
                    if (feeling == 1):
                        return self.posMessage() + " \""  + movies_list[0] + "\". "+ self.tellMeMore()
                    elif (feeling == -1):
                        return self.negMessage() + " \""  + movies_list[0] + "\". " + self.tellMeMore()
                    else:
                        return "I'm sorry, I don't know if you liked \"{}\" Try adding more words about how you felt about it".format(titles[0])
                elif len(movies_list) == 2:
                    if (feeling == 1):
                        return self.posMessage() + " \""  + movies_list[0] + "\" and \"" + movies_list[1] + "\". " + self.tellMeMore()
                    elif (feeling == -1):
                        return self.negMessage() + " \""  + movies_list[0] + "\" and \"" + movies_list[1] + "\". " + self.tellMeMore()
                    else:
                        return f"I'm sorry, I don't know if you liked \"{movies_list[0]} \" and \"{movies_list[1]}\". If you add more words about how you felt about them, I can understand and recommend better."
                elif len(movies_list) > 2:
                    titles_list = ", ".join(movies_list[:-1]) + ", and " + movies_list[-1]
                    if (feeling == 1):
                        return f"Oh, you liked {titles_list}. " + self.tellMeMore()
                    elif (feeling == -1):
                        return f"You disliked {titles_list}. " + self.tellMeMore()
                    else:
                        return f"I'm not sure whether you liked {movies_list}"
            elif "recommendation"  in input or "recommend" in input:
                if len(self.user_list) == 0:
                    return "It's hard to make a recommendation without knowing what you like. Can you tell me a movie you liked or disliked?"
                user_array = self.fill_array(self.user_list)
                r_indices = self.recommend(user_array,self.ratings)
                for index in r_indices:
                    self.recommendation_list.append(self.get_movie_given_index(index))
                self.rec_flag = True
                while(self.recommendation_list[self.i] in self.movies_seen):
                    self.i += 1
                self.i += 1
                return "OK, I'm thinking of a recommendation... I think you will like {}".format(self.recommendation_list[self.i])
                
            else:
                return self.confusedMessage()
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return response
    """Chat function understands that the user just wants to talk so has a normal speaking function"""
    def chat(self, input):
        if input == "hello" or input == "hi":
                return "Yo, what's poppin'?"
        elif input == "good morning":
            return "Yo, yo, yo, what it do? Rise and grind!"
        elif input == "good afternoon":
            return "Yo, what's good, what's good?"
        elif input == "good evening":
            return "Yo, what's good, it's your boy Topperbot, how you doing this fine evening."
        elif input == "who are you":
            return "Yo yo yo, what's good? I'm Topperbot, and I got you covered with some fire movie recommendations based on your preferences, you feel me? Let me know what movies you're vibin' with or not so I can hook you up with the perfect flick."
    def posMessage(self):
        responses = ["I feel you, everyone's gotta be feelin' ",
                 "Ayyyyeee, good to hear that you like ",
                 "Ah, I get it now. You're really feeling ",
                 "HEY, I also was feelin ",
                 "word, who couldn't possibly like ",
                 "lit man, so you're vibing with "]
        return random.choice(responses)

    def negMessage(self):
        responses = [
                 "I feel you, not everyone's gonna be feelin' ",
                 "Ah man, sorry to hear that you didn't like ",
                 "Ah, I get it now. You weren't really feeling ",
                 "Dang, I also wasn't feelin ",
                 "word, who could possibly like ",
                 "dang man, so you weren't vibing with "
                 ]
        return random.choice(responses)
    def tellMeMore(self):
        responses = [
            "Ayo, my friend, drop another movie you're feeling, let's keep this vibe going strong!",
            "Yo, my man, give me the 411 on another movie you're into, so I can recommend something that's just right for you.",
            "Hit me up with another flick, my G! I'm ready to keep this movie recommendation flow going.",
            "Yo, my man, you're dropping some hot movie picks! Keep 'em coming, and I'll make sure to recommend some other flicks that are right up your alley!",
            "I'm feeling your vibe, my G! Tell me another movie you love or hate, and I'll make sure to drop some dope recommendations that fit your style!",
            "Yo, my man, you're on a roll! Keep telling me about those movies you love or hate, and I'll keep dropping those sick recommendations that'll get you hooked!",
            "Yo, give me the scoop! Have you seen any other good or bad movies you want to chat about?", 
            "Oh man, I love talking about movies. Any other movies on your mind you want to share with me?", 
            "You got the movie game on lock, my friend! Tell me another movie you love or hate, and I'll come through with some amazing recommendations that are tailor-made just for you!"
            ]
        return random.choice(responses)
    def heyRecommend(self):
        phrases = ["I got you, fam! This movie is a perfect fit for you based on your viewing history, so check it out. ",
           "Trust me, bro! This movie has got some amazing reviews and ratings, so it's definitely worth a watch. ",
           "Yo, I think you'll be vibing with the acting in this movie, it's fire!",
           "Trust the game, playa! This movie's been suggested by many people with similar viewing habits as yours, so it's a no-brainer that it'll be your jam!",
           "Trust my ear for the game, my dude! This movie's got the right ingredients to become your new favorite.",
           "This movie's got that fire that'll keep you lit for days, my G!"]
        return random.choice(phrases)
    def confusedMessage(self):
        responses = [
            "Sorry 'bout that, but I'm not quite picking up what you're putting down. Could you like, try saying it differently or give me more info?",
            "Yo, my bad, but I'm having trouble understanding your input. Could you like, rephrase it or provide more details so I can help you out?",
            "Yo, my man, I'm having a hard time understanding your input. Could you drop some more knowledge on me?",
            "Aight, I'm not quite sure I'm vibin' with what you're sayin'. Mind breaking it down a little more for me?", 
            "Bruh, my apologies, but I'm not picking up what you're putting down. Can you try spittin' it a different way?", 
            "Yo, my bad, but I'm not fully graspin' what you're trying to say about this movie. Can you give me some more details?",
             "Hey, I'm feeling lost with this movie you mentioned. Can you run it back and give me some more info so I can understand?",
             "Hold up, let me get this straight...you feelin' the movie or nah?",
             "My bad, I'm not sure if you're feelin' the flick or not. Can you break it down for me?",
             "I'm not gonna lie, I'm a little lost on this one. Can you hit me with some more details, homie?",
             "Say what? I'm not sure if you're diggin' the movie or not. Mind giving me some more info?",
             "Sorry, I'm having trouble reading your vibe on this movie. Can you help me out and rephrase it?"
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
        text = text.lower()
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
        pattern = r'"(.*?)"'
        movie_titles = re.findall(pattern, preprocessed_input)
        cap_titles = []
        for title in movie_titles:
            cap_titles.append(capwords(title))
        return cap_titles

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
        artifacts = ["The", "An", "A"]
        matching_indices = []
        pattern = "\(\d{4}\)" #if contains a year 
        match = re.search(pattern, title)
        year = 0
        if match:
            year = match.group()
            title = match.string[:match.start()].strip()

        with open("data/movies.txt", 'r') as f:
            for i, movie in enumerate(f):
                new_movie = movie.split("%")[1]
                artifact = new_movie.split()[-2] # Could be equal to an artifact
                if artifact in artifacts:
                    new_movie = (artifact + " " + " ".join(new_movie.split()[:-2])).strip(",")
                else:
                    new_movie = new_movie[:-7]
                if title.lower() == new_movie.lower():
                    if year:
                        if year in movie:
                            matching_indices.append(i)
                    else:
                        matching_indices.append(i)

        return matching_indices

    def remove_quoted(self, string):
        new_string = ""
        in_quote = False

        for char in string:
            if char == '"':
                in_quote = not in_quote
            elif not in_quote:
                new_string += char
        return new_string
    
    def get_movie_given_index(self, index):
        with open('data/movies.txt', 'r') as f:
            movies_list = f.readlines()

        movie_string = movies_list[index]
        movie_name = movie_string.split('%')[1]
        return movie_name
    
    def extract_sentiment(self, preprocessed_input):
        stemmer = PorterStemmer()
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
        sentiment = 0
        negation = False
        title_removed = self.remove_quoted(preprocessed_input)
        for word in title_removed.split():
            if word == "enjoyed":
                word = "enjoy"
            if word in ['not', 'never', 'neither', 'none', "didn't"]:
                negation = True
            if word in self.sentiment:
                if self.sentiment[word] == 'neg':
                    if negation:
                        sentiment += 1
                    else:
                        sentiment -= 1
                else:
                    if negation:
                        sentiment -= 1
                    else:
                        sentiment += 1
            
            else:
                stemmer = PorterStemmer()
                stem_word = stemmer.stem(word)
                if stem_word in self.sentiment:
                    if self.sentiment[stem_word] == 'neg':
                        if negation:
                            sentiment += 1
                        else:
                            sentiment -= 1
                    elif self.sentiment[stem_word] == 'pos':
                        if negation:
                            sentiment -= 1
                        else:
                            sentiment += 1
        if sentiment > 0:
            sentiment = 1
        elif sentiment == 0:
            sentiment = 0
        else:
            sentiment = -1
        return sentiment
    def check_diff_sentiment(self, preprocessed_input):
        return False
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
        sentiment_list = []
        diff_sentiment = self.check_diff_sentiment(preprocessed_input)
        movies_input = self.extract_titles(preprocessed_input)
        if diff_sentiment:
            s = self.extract_sentiment(movies_input)
            for movie in movies_input:
                sentiment_list.append(movie, s)
        else:
            s = self.extract_sentiment(movies_input)
            for movie in movies_input:
                sentiment_list.append(movie, s)
        return sentiment_list

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

        pass

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
        ########################################################################
        # TODO: Binarize the supplied ratings matrix.                          #
        #                                                                      #
        # WARNING: Do not use self.ratings directly in this function.          #
        ########################################################################

        # The starter code returns a new matrix shaped like ratings but full of
        # zeros.
        binarized_ratings = np.zeros_like(ratings)
        binarized_ratings[ratings > threshold] = 1
        binarized_ratings[ratings <= threshold] = -1
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
        similarity = 0
        if np.linalg.norm(u) != 0 and np.linalg.norm(v) != 0:
            similarity = np.dot(u,v) / (np.linalg.norm(u) * np.linalg.norm(v))
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return similarity

    def fill_array(self, index_sentiment_list):
        n_array = np.zeros_like(self.titles)
        for index, sentiment in index_sentiment_list:
            n_array[index] = sentiment
        return n_array
    
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
        all_ratings = []
        rated_indices = user_ratings.nonzero()[0]
        for i in range(ratings_matrix.shape[0]):
            rating = 0
            for index in rated_indices:
                rating += self.similarity(ratings_matrix[i, :], ratings_matrix[index, :]) * user_ratings[index]
            all_ratings.append(rating)
        
        x = 0
        while (x < k):
            index = np.argmax(all_ratings)
            if (not user_ratings[index]):
                recommendations.append(index)
                x += 1
            all_ratings[index] = np.mean(all_ratings)
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
        Hi, I'm the Topperbot! I am a simple movie recommendation bot. I will listen to your movie reviews and store them, then I can make recommendations of my own.  
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
