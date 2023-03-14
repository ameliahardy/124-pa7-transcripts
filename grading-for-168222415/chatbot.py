# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re
import itertools
import string
from porter_stemmer import PorterStemmer


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        self.name = 'Buster Blaze'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.threshold = 5
        self.titles, self.ratings = util.load_ratings('data/ratings.txt')
        self.user_ratings = np.zeros(np.shape(self.ratings)[0])
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.stemmed_sentiment = util.load_sentiment_dictionary(
            'deps/stemmed_sentiment.txt')
        self.fine_graned_sentiment = {'love', 'really', 'terrible', 'hate', 'painful', 'fabulous', 'excellent', 'agony', 'beauty', 'repulsive', 'flawless', 'fantastic', 'excellence', 'worst', 'best', 'rubbish', 'perfect', 'worthless', 'pointless', 'awful', 'great', 'inspiration'}
        self.stemmer = PorterStemmer()
        self.stemmed_fine_graned_sentiment = set()
        for elem in self.fine_graned_sentiment:
            self.stemmed_fine_graned_sentiment.add(self.stemmer.stem(elem))
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(self.ratings)
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        ########################################################################

        greeting_message = "Please tell me about a movie, partner:"

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

        goodbye_message = "See you later alligator"

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
        response = ''
        movie_sentiments = self.extract_sentiment_for_movies(line)
        if not movie_sentiments:
            return "Sorry there partner, I ain't ever heard of that movie before.\n"

        possible_movie_senti = []
        self.get_possible_movie_IDs(movie_sentiments, possible_movie_senti)

        if not possible_movie_senti:
            return "Sorry there partner, I ain't ever heard of that movie before. Can you tell me about another one?\n"

        title_senti = {}
        self.get_title_sentiments(possible_movie_senti, title_senti)

        is_waiting, movie_respond = False, ''
        is_waiting, movie_respond = self.movie_response(is_waiting, movie_respond, title_senti)

        response += movie_respond

        response = self.final_respond(is_waiting, response)
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

    def get_title_sentiments(self, possible_movie_senti, title_senti):
        for movie_senti in possible_movie_senti:
            self.user_ratings[movie_senti[0]] = movie_senti[1]
            title, year, alt_title = self.get_movie_info(self.titles[movie_senti[0]][0])
            movie_title = title + " (" + year + ")"
            title_senti[movie_title] = movie_senti[1]

    def extract_unformated_titles(self, preprocessed_input):
        words = preprocessed_input.split(" ")
        movies = []
        checked = {}
        for i, j in itertools.combinations(range(len(words) + 1), 2):
            if i not in checked:
                checked[i] = -1
            reverse_j = len(words) - (j-i) + 1
            year = None
            last_val = words[reverse_j - 1]
            cur_iter = " ".join(words[i:reverse_j]).strip()
            if (len(last_val) >= 6 and last_val[-1] == ")" and last_val[0] == "(" and last_val[1:-1].isdigit()):
                year = last_val
                cur_iter = " ".join(words[i:reverse_j - 1]).strip().strip(string.punctuation)
            cur_iter = cur_iter.strip(string.punctuation)
            restructured_iter = self.get_english_article_restruct(cur_iter)
            for x in range(len(self.titles)):
                entry_movie, entry_year, entry_alt_title = self.get_movie_info(
                    self.titles[x][0].lower())
                if entry_movie and (cur_iter.lower() == entry_movie or restructured_iter.lower() == entry_movie):
                    new_iter = cur_iter
                    if (year):
                        new_iter += " " + year
                    if new_iter not in movies:
                        movies.append(new_iter)
                    checked[i] = reverse_j
                elif entry_alt_title and (entry_alt_title == cur_iter.lower() or entry_alt_title == restructured_iter.lower()):
                    new_iter = cur_iter
                    if (year):
                        new_iter += " " + year
                    if new_iter not in movies:
                        movies.append(new_iter)
                    checked[i] = reverse_j
        return movies

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
        movies = re.findall(r'\"(.*?)\"', preprocessed_input)
        if len(movies) == 0:
            movies = self.extract_unformated_titles(preprocessed_input)
        return movies

    def get_movie_info(self, entry):
        movie = entry
        year = None
        alt_movie = None
        if (len(entry) >= 6 and entry[-1] == ")" and entry[-6] == "(" and entry[-5:-1].isdigit()):
            year = entry[-5:-1]
            movie = entry[:-6].strip()
        if movie and movie[-1] == ")":
            alt_start_i = movie.rfind("(")
            alt_movie = movie[alt_start_i+1: -1]
            movie = movie[:alt_start_i].strip()
        return movie, year, alt_movie

    def get_english_article_restruct(self, movie):
        articles = ("a", "an", "the", "la", "el", 'mrs. brown', 'i', 'lo', 'der zorn gottes', '3 saptamâni si 2 zile', 'the', 'det', 'las', 'hongryeon', 'die', "je t'aime", 'le', 'der spieler', 'los', 'das', '31. august', 'má panenko', "l'", 'une étrange aventure de lemmy caution', 'les', 'jamón', 'beli macor', 'de', 'une nuit', 'la misma lluvia', 'eine symphonie des grauens', 'un', 'en', 'killer kane', 'città aperta', 'a', 'la', 'il', 'une', 'jie', 'llena eres de gracia', 'den', 'so nah!', 'el', 'companheiro?', 'der', 'io mi ricordo', 'kimi ni', 'un ami qui vous veut du bien')
        words = movie.strip().split(" ")
        if len(words) > 1 and words[0].lower() in articles:
            article = words[0]
            words[-1] = (words[-1] + ",")
            words = words[1:]
            words.append(article)
        return " ".join(words).strip()

    def movie_response(self, is_waiting, movie_respond, title_senti):
        for movie_title in title_senti:
            if title_senti[movie_title] == 0:
                temp = "Pardon partner, I don't know how you felt about " + movie_title + ". Please tell me more about " + movie_title + '.\n'
                is_waiting = True
            elif title_senti[movie_title] == 1:
                temp = "You thought " + movie_title + ' was a rootin tootin good ol film.\n'
            else:
                temp = "You weren't writting letters home about " + movie_title + '.\n'
            movie_respond += temp
        return is_waiting, movie_respond

    def check_str_in_title(self, str, title):
        str = str.translate(str.maketrans('', '', string.punctuation))
        title = title.translate(str.maketrans('', '', string.punctuation))
        # Tokenize
        str_tokens = str.split(' ')
        title_tokens = title.split(' ')
        first = title_tokens[0]
        # Find all occurrences in str of first word in title
        for i in range(len(str_tokens)):
            if str_tokens[i] == first:
                for j in range(len(title_tokens)):
                    if i + j >= len(str_tokens) or title_tokens[j] != str_tokens[i + j]:
                        break
                    # Return True if all tokens following first token in title are in str and in order
                    elif j == len(title_tokens) - 1:
                        return True
        return False

    def creative_movies_by_title(self, title):
        indices = []
        movie, year, extra = self.get_movie_info(title.lower())
        alt_movie = self.get_english_article_restruct(movie)
        temp = set()
        for i in range(len(self.titles)):
            entry_movie, entry_year, entry_alt_title = self.get_movie_info(
                self.titles[i][0].lower())
            if year and entry_year and year != entry_year:
                continue
            if entry_movie == movie or entry_movie == alt_movie:
                indices.append(i)
            elif entry_alt_title and (entry_alt_title == movie or entry_alt_title == alt_movie):
                indices.append(i)
            elif entry_movie and (self.check_str_in_title(entry_movie, movie)) or (entry_alt_title and self.check_str_in_title(entry_alt_title, movie)):
                indices.append(i)
        return indices


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
        if self.creative:
            return self.creative_movies_by_title(title)
        indices = []
        movie, year, extra = self.get_movie_info(title.lower())
        alt_movie = self.get_english_article_restruct(movie)
        for i in range(len(self.titles)):
            entry_movie, entry_year, entry_alt_title = self.get_movie_info(
                self.titles[i][0].lower())
            if year and entry_year and year != entry_year:
                continue
            if entry_movie == movie or entry_movie == alt_movie:
                indices.append(i)
            elif entry_alt_title and (entry_alt_title == movie or entry_alt_title == alt_movie):
                indices.append(i)
        return indices

    def remove_movie(self, sentence):
        return re.sub("\".*?\"", "", sentence)

    def get_word_sentiment(self, word):
        if word not in self.sentiment:
            stemmed_word = self.stemmer.stem(word)
            if stemmed_word not in self.stemmed_sentiment:
                score = 0
            elif self.stemmed_sentiment[stemmed_word] == "pos":
                score = 1
            else:
                score = -1
            return score
        elif self.sentiment[word] == "pos":
            score = 1
        else:
            score = -1
        return score


    def get_negated_input(self, sentence):
        sentence = self.remove_movie(sentence)
        sentence = sentence.split(" ")
        negation_words = ("don't", "didn't", "won't",
                          "not", "dont", "didnt", "wont", "never")
        negating = False
        negated_sentence = []
        for word in sentence:
            punct = False
            if word and re.match(r'\[:punct:]', word[-1]):
                punct = True
                word = word[:-1]
            word = word.lower()
            if word in negation_words:
                negating = not negating
            elif negating:
                word = "NOT_" + word
            if punct:
                negating = False
            negated_sentence.append(word)
        return negated_sentence

    def get_sentence_sentiment(self, sentence):
        net_sentiment = 0
        words = self.get_negated_input(sentence)
        for word in words:
            word = word.strip(string.punctuation)
            neg = False
            if len(word) >= 4 and word[:4] == "NOT_":
                word = word[4:]
                neg = True
            sentiment = self.get_word_sentiment(word)
            if neg:
                sentiment *= -1
            net_sentiment += sentiment
        return net_sentiment

    def get_possible_movie_IDs(self, movie_sentiments, possible_movie_senti):
        for movie_sentiment in movie_sentiments:
            MIDs = self.find_movies_by_title(movie_sentiment[0])
            for MID in MIDs:
                possible_movie_senti.append((MID, movie_sentiment[1]))

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
        net_sentiment = self.get_sentence_sentiment(preprocessed_input)
        if net_sentiment == 0:
            return 0
        net_sentiment = net_sentiment/abs(net_sentiment)
        if self.creative:
            for word in self.remove_movie(preprocessed_input.lower()).split(" "):
                word = word.translate(word.maketrans('', '', string.punctuation))
                if word in self.fine_graned_sentiment:
                    net_sentiment = net_sentiment * 2
                    break
                elif self.stemmer.stem(word) in self.stemmed_fine_graned_sentiment:
                    net_sentiment = net_sentiment * 2
                    break
        return net_sentiment

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
        titles = self.extract_titles(preprocessed_input)
        preprocessed_input = self.remove_movie(preprocessed_input)
        preprocessed_input = preprocessed_input.translate(preprocessed_input.maketrans('', '', string.punctuation))
        multiplier = 0
        base_sentiment = 0
        other_sentiment = 0
        if preprocessed_input.find(" and ") >= 0 or preprocessed_input.find(" or ") >= 0:
            multiplier = 1
        elif preprocessed_input.find(" but ") >= 0:
            multiplier = -1
        preprocessed_input = preprocessed_input.replace(' or ', ' and ')
        preprocessed_input = preprocessed_input.replace(' but ', ' and ')
        statements = preprocessed_input.split(' and ')
        if len(statements) > 1:
            base_sentiment = self.get_sentence_sentiment(statements[0])
            other_sentiment = base_sentiment * multiplier
        for i in range(len(titles)):
            sentiments.append((titles[i], base_sentiment))
            base_sentiment = other_sentiment
        return sentiments

        sentences = preprocessed_input.split('.')
        movie_sentiments = []
        for sentence in sentences:
            titles = self.extract_titles(sentence)
            if len(titles) == 0:
                continue
            for title in titles:
                guesses = self.find_movies_by_title(title)
                if not guesses:
                    continue

                movie_sentiments.append((title, self.extract_sentiment(sentence)))
        return movie_sentiments

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
        return []
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
        new_candidates = []
        # for candidate in candidates:
        #     cand_movie, cand_year, cand_alt_title = self.get_movie_info(
        #         self.titles[candidate][0].lower())
        #     if (self.check_str_in_title(clarification, cand_movie)):
        #         new_candidates.append(candidate)
        return new_candidates


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
        ########################################################################        #                                                                      #
        # WARNING: Do not use self.ratings directly in this function.          #
        ########################################################################

        binarized_ratings = np.copy(ratings)
        for rating in np.nditer(binarized_ratings, op_flags=['readwrite']):
            new_val = 0
            if rating == 0:
                continue
            elif rating > threshold:
                new_val = 1
            else:
                new_val = -1
            rating[...] = new_val
        return binarized_ratings

        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################

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
        # intersection = 0
        # for i in range(len(u)):
        #     if u[i] != 0 and v[i] != 0:
        #         intersection += 1
        # if intersection == 0:
        #     return 0
        demoninator = (np.linalg.norm(u)*np.linalg.norm(v))
        if demoninator == 0:
            return 0
        similarity = np.dot(u, v)/(np.linalg.norm(u)*np.linalg.norm(v))

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

        # Populate this list with k movie indices to recommend to the user.
        recommendations = []

        ratedMID = set([i for i in range(np.shape(ratings_matrix)[0]) if user_ratings[i] != 0])

        i_scores = [(-1, -999) for i in range(k)]

        for i in range(np.shape(ratings_matrix)[0]):
            if i in ratedMID:
                continue

            similarities = [self.similarity(ratings_matrix[i], ratings_matrix[MID]) for MID in ratedMID]
            ratings = [user_ratings[MID] for MID in ratedMID]

            predict_score = np.dot(np.array(similarities), np.array(ratings))

            i_scores.sort(key=lambda x: x[1])
            if predict_score > i_scores[0][1]:
                i_scores[0] = (i, predict_score)

        recommendations = [ele[0] for ele in reversed(i_scores)]

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
        Howdy there! My name is Buster Blaze. I am a rootin-tootin cowboy from the 
        wild wild west. When I'm not riding my horse or fetchin a drink at the saloon, 
        I'm in my cabin reading up on the most recent films. I bet you a tooth and nail 
        that I can give you some great movie recommendations.
        
        All you have to do is tell me if you liked or disliked movies names!
        """

    def final_respond(self, is_waiting, response):
        if sum(self.user_ratings != 0) >= self.threshold:
            print(
                "Looky here partner! I reckon I got enough info to give you some of the best rootin tootin movie recommendations that will knock your socks off!\n")
            recommendations = self.recommend(self.user_ratings, self.ratings)
            titles = []
            for MID in recommendations:
                title, year, alt_title = self.get_movie_info(self.titles[MID][0])
                titles.append(title + " (" + year + ")")
            movies = ''.join([title + ', ' for title in titles])
            response = response + "I reckon you'll like  " + movies + "\n"
        else:
            if not is_waiting:
                response = response + "Please tell me about another movie you've ever done seen.\n"
        return response

if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
