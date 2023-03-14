# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re
import string
import nltk
#from nltk.stem import PorterStemmer


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'dominique'

        self.creative = creative

        self.clarify_movie_name = False

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.sentiment["like"] = "pos"
        self.sentiment["liked"] = "pos"
        self.user_ratings = np.zeros(len(ratings))
        self.negations = ["not", "didn't","don't", "never", "nobody","no", "isn't", "haven't", 
                          "hasn't", "shouldn't", "woudln't", "couldn't", "can't", "won't", "cannot"
                         "neither", "nor", "wasn't", "weren't"]
        self.articles = ['a', 'an', 'the', 'les', 'le', 'la', 'un', 'une', 'el']

        self.p = nltk.PorterStemmer()
        
        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings)

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""

        greeting_message = "Confess to your mistress, what do you desire?"

        return greeting_message

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        goodbye_message = "You may be leaving now, but I know you can't wait to crawl back to me."

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

        line = self.preprocess(line)
        titles = self.extract_titles(line)
        
        is_recommend = self.determine_intent(line)

        if len(titles) == 0 and not is_recommend: 
            return "I don't know what movie you're talking about!"
        sentiment = self.extract_sentiment(line)

        for title in titles:
            idxs = self.find_movies_by_title(title)
            if self.clarify_movie_name:
                return "Sorry! I didn't understand. Do you mean {}".format(self.titles[idxs[0]][0])
            if len(idxs) == 0 and not is_recommend:
                return "I don't know what movie you're talking about!"
            for idx in idxs:
                self.user_ratings[idx] = sentiment
        recommended = []
        if is_recommend:
            recommended = self.recommend(self.user_ratings, self.ratings, 1, self.creative)
        if not is_recommend:
            return self.generate_acknowledgement(titles, sentiment)
        else:
            return self.generate_recommendation(recommended)
      
    
    def generate_acknowledgement(self, titles, sentiment):
        titles[0] = titles[0].title()
        if len(titles) > 1 and sentiment > 0:
            if sentiment == 2:
                return "Hearing all your sweet talk about {} and others has me thinking our sessions with the bar soap are going quite well. That said, open wide.".format(titles[0])
            else:
                return "You liked {} and some others? You sure have a lot of time on your hands, almost as much as you do on your knees.".format(titles[0])
        elif len(titles) == 1 and sentiment > 0:
            if sentiment == 2:
                return "How cute. You like {} almost as much as you like when I XXXX your XXX with my XXXXX.".format(titles[0])
            else:
                return "So you like chains, whips and... {}? Curious.".format(titles[0])
        elif len(titles) > 1 and sentiment < 0:
            if sentiment == -2:
                return "Oh boo hoo, you didn't like {} and whatever else. You know what else you won't like? Assume the position.".format(titles[0])
            else: 
                return "Time wasted watching {} and more... all when you could've been serving your mistress.".format(titles[0])
        elif len(titles) == 1 and sentiment < 0:
            if sentiment == -2:
                return "If this ever gets to be too much, remember our safe word(s): {}.".format(titles[0])
            else:
                return "You'll black my boots, but {} is where you draw the line?".format(titles[0])
        else:
            s = "Sorry, I'm not sure how you feel about {}. Get on your knees and... tell me more.".format(titles[0])
            return s
        
    def generate_recommendation(self, recommended):
        return "Fine. You can watch {} while you black my boots!!".format(self.titles[recommended[0]][0].title())
    
    
    def determine_intent(self, line):
        if "recommend" in line:
            return True
        return False
    
    
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

        text = text.translate({ord(i): None for i in '!?.'})
        return text.lower()

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

        def is_sub_list(a, b):
            if not a:
                return 0
            if not b:
                return -100000
            if a[0] == b[0]:
                return is_sub_list(a[1:], b[1:]) + 1
            return is_sub_list(a, b[1:]) + 1


        titles = []
        preprocessed_input = preprocessed_input.lower()
        possible_titles = re.findall('"(.*?)"', preprocessed_input)
        for title in possible_titles:
            title = title.title()
            titles.append(title)

        # Creative 
        if self.creative and len(titles) == 0:
            for i in range(len(self.titles)):
                movie_title = self.titles[i][0]
                movie_name = movie_title.lower().split(' ')

                # extract the movie year
                year = movie_name[-1]
                movie_name.pop(-1)

                # Check if the movie name has starts with an article
                if movie_name[-1] in self.articles:
                    movie_name.insert(0, movie_name[-1])
                    movie_name.pop(-1)
                    movie_name[-1] = movie_name[-1][:-1]

                movie = ''
                for i in range(len(movie_name)):
                    movie += movie_name[i]
                    movie += ' '
                movie = movie.strip()

                line_list = preprocessed_input.split(' ')

                last_index = is_sub_list(movie_name, line_list)
                if last_index > 0:
                    if last_index < len(line_list) and bool(re.search(r'\(\d{4}\)', line_list[last_index])) and len(line_list[last_index]) == 6:
                        if year == line_list[last_index]:
                            titles.append(movie.title())
                        continue
                    titles.append(movie.title())
        return titles
        

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
        titles = []

        title = title.lower()
        title_words = title.split(' ')
        year = ''

        # if the title of the movie includes a year
        if title_words[-1][0] == '(' and title_words[-1][-1] == ')':
            year = title_words[-1]
            title_words.pop(-1)
        
        # if the title starts with an article move it to the end of the title
        if title_words[0] in self.articles:
            title_words[-1] = title_words[-1] + ','
            title_words.append(title_words[0])
            title_words.pop(0)

        title_new = ''
        for i in range(len(title_words)):
            title_new += title_words[i] + ' '
        title_new = title_new.strip()

        found =  False
        for i in range(len(self.titles)):
            movie = self.titles[i][0].lower()
            movie_name = movie.split(' ')
            movie_year = movie_name[-1]
            movie_name.pop(-1)
            alt_title = movie[:-6].split('(')
            if year == '' or year == movie_year:
                for j in range(len(alt_title)):
                    movie_title = alt_title[j].strip()
                    if movie_title == '':
                        continue
                    if movie_title[0] == '(':
                        movie_title = movie_title[1:]
                    if movie_title[-1] == ')':
                        movie_title = movie_title[:-1]
                    movie_title = movie_title.strip()
                    if movie_title == title_new or "a.k.a. " + title_new == movie_title :
                        titles.append(i)
                        found = True
                        break

        if not found and self.creative:
            potential_titles = self.find_movies_closest_to_title(title)
            if len(potential_titles) > 0:
                self.clarify_movie_name = True
                return potential_titles

        return titles

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
        sentiment = 0 # neutral
        
        sentence = preprocessed_input.split(" ")
        negate = False
        is_title = False
        for word in sentence:
            if word[0] == '"':
                is_title = True
            if word[-1] == '"':
                is_title = False
                continue
            if is_title: 
                continue
            word = self.p.stem(word)
            if word in self.negations:
                negate = not negate
            if word in self.sentiment: 
                if self.sentiment[word] == "pos" and negate == False:
                    sentiment += 1
                elif self.sentiment[word] == "pos" and negate == True:
                    sentiment -= 1
                    negate = False
                elif self.sentiment[word] == "neg" and negate == False:
                    sentiment -= 1
                else:
                    sentiment += 1
                    negate = False
        if sentiment < 0:
            if sentiment <= -2:
                return -2
            else:
                return -1
        elif sentiment > 0:
            if sentiment >= 2:
                return 2
            else:
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
        
        for i in range(len(self.titles)):
            movie_title = self.titles[i][0].lower()

            movie_title_list = movie_title.split(' ')
            year = movie_title_list[-1]
            movie_title_list.pop(-1)

            if movie_title_list[-1] in self.articles:
                movie_title_list.insert(0, movie_title_list[-1])
                movie_title_list.pop(-1)
                movie_title_list[-1] = movie_title_list[-1][:-1]

            movie_title = ''
            for j in range(len(movie_title_list)):
                movie_title += movie_title_list[j]
                movie_title += ' '
            movie_title = movie_title.strip()

            if bool(re.search(r'\(\d{4}\)', title)):
                movie_title += ' ' + year

            edit_distance = nltk.edit_distance(title, movie_title)
            
            if edit_distance <= max_distance:
                if edit_distance < max_distance:
                    max_distance = edit_distance
                    closest_movies = []
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
        movies = []
        for candidate in candidates:
            movie = self.titles[candidate]
            if clarification in movie:
                movies.append(candidate)
        return movies

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

        # The starter code returns a new matrix shaped like ratings but full of
        # zeros.
        binarized_ratings = np.zeros_like(ratings)

        for i in range(len(ratings)):
            for j in range(len(ratings[i])):
                binary = 0
                if ratings[i][j] == 0:
                    binary =  0
                elif ratings[i][j] > 2.5:
                    binary =  1
                else:
                    binary = -1
                binarized_ratings[i][j] = binary
        return binarized_ratings

    def similarity(self, u, v):
        """Calculate the cosine similarity between two vectors.

        You may assume that the two arguments have the same shape.

        :param u: one vector, as a 1D numpy array
        :param v: another vector, as a 1D numpy array

        :returns: the cosine similarity between the two vectors
        """
        norm = (np.sqrt(np.dot(u, u)) * np.sqrt(np.dot(v, v)))
        if norm != 0:
            return np.dot(u, v) / norm
        return 0

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
        # Populate this list with k movie indices to recommend to the user.
        recommendations = []

        num_movies = len(user_ratings)
        user_rated_movies = set()

        for i in range(num_movies):
            if user_ratings[i] != 0:
                user_rated_movies.add(i)

        predicted_rating = np.zeros(num_movies)
        for i in range(num_movies):
            movie_similarity = np.array([])
            user_ratings_filtered = np.array([])
            if i not in user_rated_movies:
                for j in user_rated_movies:
                    similarity = self.similarity(ratings_matrix[i], ratings_matrix[j])
                    movie_similarity = np.append(movie_similarity, similarity)
                    user_ratings_filtered = np.append(user_ratings_filtered, user_ratings[j])
            predicted_rating[i] = np.dot(movie_similarity, user_ratings_filtered)
            
        for i in range(k):
            rec_movie = list(predicted_rating).index(np.max(predicted_rating))
            recommendations.append(rec_movie)
            predicted_rating[rec_movie] = 0
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
        This chatbot is named Dominique. Your one stop for movie recommendations through
        the voice of a professional dominatrix. Everything is consensual.
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
