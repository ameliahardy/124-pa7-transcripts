# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
from markupsafe import re
from nbformat import current_nbformat_minor
import util
import porter_stemmer
import numpy as np


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'Slick \'Flick\' Rick'

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.creative = creative
        self.user_ratings = np.zeros(len(self.titles))
        self.movie_count = 0
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

        greeting_message = "Howdy, partner! Name\'s Slick Flick Rick -- how might this cowpoke round up sum flicks fer you today?"

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

        goodbye_message = "And with that, I bid you adieu, buckaroo."

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return goodbye_message

    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################
    def respond_to_emotions(self, words):
        angry = set(['angry', 'bitter', 'frustrated', 'agitated', 'aggravated', 'furious', 'impatient', 'moody', 'pissed', 'upset', 'cranky'])
        happy = set(['happy', 'calm', 'content', 'peaceful', 'relaxed', 'eager', 'ecstatic', 'excited', 'passionate', 'adventurous', 'brave', 'confident', 'safe', 'warm', 'lucky', 'optimistic', 'thankful'])
        sad = set(['sad', 'depressed', 'disappointed', 'discouraged', 'gloomy', 'heartbroken', 'hopeless', 'lonely', 'unhappy', 'bored', 'ashamed', 'worthless', 'useless'])
        fearful = set(['afraid', 'scared', 'frightened', 'nervous', 'terrified', 'worried'])
        disgusted = set(['disgusted', 'revolted', 'nauseated', 'repulsed'])

        for w in words:
            if w in angry:
                return 'Whoa der, partner -- was it somethin\' I sayed that made you {} or...'.format(w)
            elif w in happy:
                return 'Woooowee, sure bucks my bronco knowin\' yer {}!'.format(w)
            elif w in sad:
                return 'Shucks, pal. Here\'s hopin\' ya don\'t feel {} fer too long!'.format(w)
            elif w in fearful:
                return 'Hold ya horses, big hoss! Didn\'t mean to get ya all {} and err\' thang'.format(w)
            elif w in disgusted:
                return 'Oh lawdy, seein\' you all {} makes me wanna hit the tin...'.format(w)
        return "Lemme reel you right back in, amigo. Chew the rag with me \'bout that flick you done seen the otha day!"


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
        # if self.creative:
        #     response = "I processed {} in creative mode!!".format(line)
        # else:
        #     response = "I processed {} in starter mode!!".format(line)
        
        titles = self.extract_titles(line)
        words = line.split(" ")
        words = [w.lower() for w in words]

        with open('./deps/verbs.txt') as f:
            verbs = f.read().splitlines()
        # Respond to questions
        q_words = ["who", "what", "when", "why", "how", "where", "whose", "which"]
        if words[0] in q_words:
            return "Partner, if I knew \'{},\' I\'d spill, but \'til then, tell me \'bout a recent flick you\'ve seen!".format(words[0])
        elif words[0] == "can":
            return "Partner, if I could, I would, but \'til then, tell me \'bout a recent flick you\'ve seen!"
        elif words[-1].endswith("?"):
            return "What in tarnation are you goin\' on about cowpoke... try telling me \'bout a film you seen instead!"

        # Respond to imperative statements
        elif len(words[0]) > 1 and words[0] in verbs:
            return "Pal, aside from herding cattle and hitting the hay, I can\'t exactly \'{}\' anything! ... try spillin\' some beans \'bout that flick you seen!".format(words[0])
        
        else:
            if len(titles) == 1:
                response = self.create_response_for_movie(titles[0], True, line)
            elif len(titles) > 1:
                response = ""
                for i in range(len(titles)):
                    response += f"For {titles[i]}, "
                    response += self.create_response_for_movie(titles[i], False, line) + "\n"
            else:
                # Respond to emotions (no movies)
                response = self.respond_to_emotions(words)
            return response
        # for t in titles: 
        #     idx = [i for i in range(len(self.titles)) if self.titles[i][0] == t][0]
        #     self.user_ratings[idx] = sentiment
        #     self.movie_count += 1


        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################


    def create_response_for_movie(self, title, single_movie_flag, line):
        idx_list = self.find_movies_by_title(title)
        if len(idx_list) > 1:
            response = "Slow ya roll, amigo, did ya mean "
            if not single_movie_flag:
                response = response.lower()
            for i in range(len(idx_list)):
                movie = self.titles[idx_list[i]][0]
                if i == len(idx_list) - 1:
                    response += f"or {movie}?"
                else:
                    response += f"{movie}, "
        elif len(idx_list) == 1:
            movie = self.titles[idx_list[0]][0]
            sentiment = self.extract_sentiment(line)
            if sentiment == 1:
                response = "Yeehaw! Glad to hear ya fancied "
            elif sentiment == -1:
                response = "Shucks, pard, sorry to hear ya didn\'t like "
            else:
                response = "Amen, ain\'t gonna complain but also ain\'t gonna praise "
            if not single_movie_flag:
                response = response.lower()
            response += movie + ". "
            self.user_ratings[idx_list[0]] = sentiment

            self.movie_count += 1
            if self.movie_count > 0 and self.movie_count % 5 == 0: 
                response = "Holler at the sheriff if this cowboy is wrong, but I think you might fancy " + self.titles[self.recommend(self.user_ratings, self.ratings, 1)[0]][0] + " if ya ain\'t been blowin\' smoke."
                return response
        elif len(idx_list) == 0:
            idx_list = self.find_movies_closest_to_title(title)
            if len(idx_list) > 1:
                response = "Slow ya roll, amigo, did ya mean "
                if not single_movie_flag:
                    response = response.lower()
                for i in range(len(idx_list)):
                    movie = self.titles[idx_list[i]][0]
                    if i == len(idx_list) - 1:
                        response += f"or {movie}?"
                    else:
                        response += f"{movie}, "
            elif len(idx_list) == 1:
                movie = self.titles[idx_list[0]][0]
                response = "Slow ya roll, amigo, did ya mean "
                if not single_movie_flag:
                    response = response.lower()
                response += movie + "?"
            if len(idx_list) == 0:
                response = "Who the what now? Sorries, pard, I dunno \'bout that one."
                if not single_movie_flag:
                    response = response.lower()
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
        ##punctuation = [",", ".", ";","?","!",":"]
        #for p in punctuation: 
        #    text = text.replace(p, "")
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
        
        if self.creative: 
            punctuation = [",", ".", ";","?","!",":"]
            for p in punctuation: 
                preprocessed_input = preprocessed_input.replace(p, "")
            quotes =  [i for i, ltr in enumerate(preprocessed_input) if ltr == "\""]
            movies = [preprocessed_input[quotes[i] + 1 : quotes[i + 1]] for i in range(0, len(quotes), 2)]
            
            for m in movies: 
                preprocessed_input = preprocessed_input.replace(m, "")
            words = preprocessed_input.split(" ")

        
            for i in range(len(words)): 
                for j in range(i, len(words)):
                    poss_title = " ".join(words[i:j + 1]).lower()
                
                    if len([self.titles[i][0] for i in self.find_movies_by_title(" ".join(words[i:j + 1]).lower())]):
                        movies.append(" ".join(words[i:j + 1]).title())
        else: 
            quotes =  [i for i, ltr in enumerate(preprocessed_input) if ltr == "\""]
            movies = [preprocessed_input[quotes[i] + 1 : quotes[i + 1]] for i in range(0, len(quotes), 2)]
            
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
        idx_list = []
        title = title.replace(",", "").lower()
        words = title.split(" ")
        for idx, t in enumerate(self.titles):
            
            alt_title = None
            #w = t[0][:t.index("(")].replace(",", "").split(" ")
            #if "(" in t[0][: len(w) - 1 ]: 
            #    alt_title = w[w.index("(") + 1: w.index(")")].split(" ")
           #print(t[0])
            if "(" in t[0]: 
                title = t[0][0:t[0].rindex("(") - 1].replace(",", "").lower()
                if "a.k.a. " in title: 
                    title = title.replace("a.k.a. ", "")
                if "(" in title: 
                    alt_title = title[title.rindex("(") + 1 : title.rindex(")")]
                    if "a.k.a. " in alt_title: 
                        alt_title = alt_title.replace("a.k.a. ", "")
                    alt_title = alt_title.split(" ")
                    title = title[:title.rindex("(") - 1]
            else: 
                title = t[0]
            title = title.split(" ")
            if "(" in t[0]:
                title += [t[0][t[0].rindex("("):]]
                if alt_title is not None: 
                    alt_title += [t[0][t[0].rindex("("):]]
           
            if set(words) == set(title) or set(words) == set(title[: len(title) - 1 ]) or (alt_title != None and (set(words) == set(alt_title) or set(words) == set(alt_title[: len(alt_title) - 1 ]))):
                idx_list.append(idx)
            
        return idx_list

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
        ps = porter_stemmer.PorterStemmer()
        score = 0
        titles = self.extract_titles(preprocessed_input)
        text = preprocessed_input
        negations = ["never", "not", "didn\'t", "wasn\'t", "don\'t", "can\'t", "couldn\'t", "weren\'t", "shouldn\'t", "cannot"]
        for t in titles: 
            text = text.replace(t, '')
        words = text.split(" ")
        words_that_dont_stem_correctly  = {"enjoi" : "pos", "dislik" : "neg"}
        for idx, word in enumerate(words): 
            w = ps.stem(word)
            if word in self.sentiment: 
                score = score + 1 if (self.sentiment[word] == "pos" and len(set(words[0:idx]).intersection(set(negations))) == 0) or (self.sentiment[word] == "neg" and len(set(words[0:idx]).intersection(set(negations))) > 0) else score - 1
            elif w in self.sentiment: 
                score = score + 1 if (self.sentiment[w] == "pos" and len(set(words[0:idx]).intersection(set(negations))) == 0) or (self.sentiment[w] == "neg" and len(set(words[0:idx]).intersection(set(negations))) > 0) else score - 1
            elif w in words_that_dont_stem_correctly: 
                score = score + 1 if (words_that_dont_stem_correctly[w] == "pos" and len(set(words[0:idx]).intersection(set(negations))) == 0) or (words_that_dont_stem_correctly[w] == "neg" and len(set(words[0:idx]).intersection(set(negations))) > 0) else score - 1
                
        return score if score == 0 else score / abs(score)

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
        return []
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
        idx_list = []
        title = title.replace(",", "")
        words = title.lower().split(" ")
        min_edit_distance = max_distance
        for idx, t in enumerate(self.titles):
            if "(" in t[0]: 
                temp_title = t[0][0:t[0].rindex("(") - 1]
            
            edit_distance = self.EditDistDP(temp_title, title)
            if edit_distance <= max_distance:
                if edit_distance < min_edit_distance:
                    min_edit_distance = edit_distance
                    max_distance = min_edit_distance
                    idx_list = [idx]
                elif edit_distance == min_edit_distance:
                    idx_list.append(idx)
            else:
                temp_split = temp_title.lower().split(" ")
                edit_distance = -1
                if len(temp_split) == len(words):
                    for i in range(len(temp_split)):
                        word_edit_distance = self.EditDistDP(temp_split[i], words[i])
                        if i == 0:
                            if word_edit_distance <= min_edit_distance:
                                edit_distance = word_edit_distance
                            else:
                                break
                        else:
                            edit_distance += word_edit_distance
                            if edit_distance <= max_distance:
                                break
                    if edit_distance != -1 and edit_distance <= max_distance:
                        if edit_distance < min_edit_distance:
                            min_edit_distance = edit_distance
                            max_distance = min_edit_distance
                            idx_list = [idx]
                        elif edit_distance == min_edit_distance:
                            idx_list.append(idx)
                            

                            


        return idx_list

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
        response = []
        user_input = clarification.split(" ")

        for candidate in candidates: 
            title = self.titles[candidate][0]
            title = title.split(" ")
            if len(user_input) < len(title): 
                input_no_space = "".join(user_input)
                for i in range(len(title) - len(user_input) + 1): 
                    if input_no_space == "".join(title[i:i+len(user_input)]) or "("+input_no_space+")" == "".join(title[i:i+len(user_input)]):
                        response.append(candidate)
        return response

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
        binarized_ratings = np.copy(ratings)
        binarized_ratings[binarized_ratings == 0] = 10
        binarized_ratings[binarized_ratings <= threshold] = -1
        binarized_ratings[binarized_ratings == 10] = 0
        binarized_ratings[binarized_ratings > threshold] = 1

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
        #num = sum([u[i] * v[i] for i in range(len(u))])
        #denom = sum([l**2 for l in u])**.5 * sum([l**2 for l in v])**.5  
        #return num / denom 
        return np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
       

    def EditDistDP(self, str1, str2):
        
        len1 = len(str1)
        len2 = len(str2)
    
        # Create a DP array to memoize result
        # of previous computations
        DP = [[0 for i in range(len1 + 1)]
                for j in range(2)]
    
        # Base condition when second String
        # is empty then we remove all characters
        for i in range(0, len1 + 1):
            DP[0][i] = i
    
        # Start filling the DP
        # This loop run for every
        # character in second String
        for i in range(1, len2 + 1):
            
            # This loop compares the char from
            # second String with first String
            # characters
            for j in range(0, len1 + 1):
    
                # If first String is empty then
                # we have to perform add character
                # operation to get second String
                if (j == 0):
                    DP[i % 2][j] = i
    
                # If character from both String
                # is same then we do not perform any
                # operation . here i % 2 is for bound
                # the row number.
                elif(str1[j - 1] == str2[i-1]):
                    DP[i % 2][j] = DP[(i - 1) % 2][j - 1]
                
                # If character from both String is
                # not same then we take the minimum
                # from three specified operation
                else:
                    DP[i % 2][j] = (1 + min(DP[(i - 1) % 2][j],
                                        min(DP[i % 2][j - 1],
                                    DP[(i - 1) % 2][j - 1])))
        return DP[len2 % 2][len1]


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
        b_user_ratings = user_ratings
        b_ratings_matrix = ratings_matrix
    #    filled_rows = set([i for i in b_user_ratings if i != 0])
        filled_rows = set([i for i in range(len(b_user_ratings)) if b_user_ratings[i] != 0])

        for i in range(len(user_ratings)): 
            if b_user_ratings[i] != 0: 
                continue
            score = 0
            #for each of the items that are in the users ratings
            for j in filled_rows: 
                #for each of the users in the matrix
                score += self.similarity(b_ratings_matrix[i], b_ratings_matrix[j]) * b_user_ratings[j]
            if len(recommendations) < k: 
                recommendations.append((i, score))
            if score > min(recommendations, key = lambda x: x[1])[1]: 
                recommendations.remove(min(recommendations, key = lambda x: x[1]))
                recommendations.append((i, score))

        return [x[0] for x in sorted(recommendations, key = lambda x: x[1], reverse = True)]
                
    

        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        

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
