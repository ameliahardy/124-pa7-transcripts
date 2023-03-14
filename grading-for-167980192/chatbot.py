# PA7, CS124, Stanford
# v.1.0.4
# GITHUB V
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import string
import numpy as np
import re
import porter_stemmer

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        self.name = 'MovieChatbot'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        self.movies = util.load_titles('data/movies.txt')

        self.title_to_ids = {}
        self.id_to_title = {}
        self.alt_titles = {}
        self.foreign_titles = {}

        self.user_movie_ids = []

        self.recs = []

        self.user_ratings = np.zeros((9125,1))
        self.numinputs = 0
        
        # Make title_to_ids dict to use keys are lower/whitespace removed/ no dates
        for i in range(len(self.movies)):
            # Remove the year if it's present, and store it in a variable
            title = self.movies[i][0]
            match = re.search(r'\((\d{4})\)$', title)
            if match:
                year = match.group(1)
                title = re.sub(r'\s*\(\d{4}\)$', '', title)
            else:
                year = None
            
            # Move the article to the end, if it's present
            article_match = re.search(r'^(a|an|the)\s+', title, re.IGNORECASE)
            if article_match:
                article = article_match.group(1)
                title = re.sub(r'^(a|an|the)\s+', '', title, flags=re.IGNORECASE) + ', ' + article
            else:
                article = None
                
                
            # Store alternate title to title id
            alt_match = re.search(r'\(.*\)$', title, re.IGNORECASE)
            if alt_match and not article_match:
                alt = alt_match.group(0)
                
                alt_title = ""
                aka_match = re.search(r'\(a\.k\.a\.\s+(.+)\)$', alt, re.IGNORECASE)
                if aka_match:
                    # AKA title
                    alt_title = re.sub(r'\(a\.k\.a\.\s+', '', alt, flags=re.IGNORECASE)
                    alt_title = re.sub(r'\)', '', alt_title, flags=re.IGNORECASE)
                    alt_title = alt_title.strip()
                else:
                    # Foreign title
                    foreign_article_match = re.search(r'^\((la|el|en|le|the|a|an|los|las|les|los|il|l\'|gli|i|der|das|die)\s+', alt, re.IGNORECASE)
                    if foreign_article_match:
                        foreign_article = foreign_article_match.group(1)
                        alt_title = re.sub(r'^\((la|el|en|le|the|a|an|los|las|les|los|il|l\'|gli|i|der|das|die)\s+', '', alt, flags=re.IGNORECASE)
                        alt_title = alt_title.strip(")") + ', ' + foreign_article
                    else:
                        # Foreign title without article
                        alt_title = alt.strip("()")
                    
                if alt_title in self.alt_titles:
                    self.alt_titles[alt_title].append(i)
                else:
                    self.alt_titles[alt_title] = [i]
            
            # Return both versions of the title (with and without year)
            titles = [title]
            if year is not None:
                titles.append(title + ' (' + year + ')')

            for ttl in titles:
                if ttl in self.title_to_ids:
                    self.title_to_ids[ttl].append(i)
                else:
                    self.title_to_ids[ttl] = [i]

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings, 2.5)
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        greeting_message = "Hello, we are going to recommend you movies based on your reviews, type creative to do creative reviews, otherwise just type a review!"
        return greeting_message

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        goodbye_message = "Have a nice day! great chatting with you"
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
        response = ''
        if self.numinputs == 0 and line.find('creative') != -1:
            response = "you selected creative mode, fire away creative reviews"
            self.creative = True
        else:
            if self.creative:
                response += "creative modee"
            if self.numinputs < 3:
                s = self.extract_sentiment_for_movies(line)
                x = self.recommend(self.user_ratings, self.ratings, 3, self.creative)
                self.numinputs += 1
                if len(s) == 0:
                        response += "sorry, I missed that movie .. tell me more "
                for ind, tit in enumerate(s):
                    rate = s[tit]
                    if s[tit] > 0:
                        response += "you liked "
                    elif rate < 0:
                        response += "you disliked "
                    else:
                        response += "you feel neutral about "
                    response += tit

                response += " \n please tell me more about your movie preferences "
                response += "we need " + str(4 - self.numinputs) + " more reviews to recommend"
            else:
                self.recs = []
                s = self.extract_sentiment_for_movies(line)
                x = self.recommend(self.user_ratings, self.ratings, 3, self.creative)
                response += "based on your ratings I recommend "
                for rec in self.recs:
                    response += "\n" + rec

            
        #######################################################################
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

        reg = '"([^"]*)"'
        matches = re.findall(reg, preprocessed_input)
        for match in matches:
            mvs = self.find_movies_by_title(match)
            if mvs == None:
                continue
            for mov in mvs: 
                self.user_movie_ids.append(mov)
        return matches

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
        key = title

        # Remove the year if it's present, and store it in a variable
        match = re.search(r'\((\d{4})\)$', title)
        if match:
            year = match.group(1)
            key = re.sub(r'\s*\(\d{4}\)$', '', title)
        else:
            year = None

        # Move the article to the end, if it's present
        article_match = re.search(r'^(a|an|the)\s+', title, re.IGNORECASE)
        if article_match:
            article = article_match.group(1)
            key = re.sub(r'^(a|an|the)\s+', '', key, flags=re.IGNORECASE) + ', ' + article 
            
        if year is not None:
            key = key + " (" + year + ")"

        ret = []
        alt_bool = False
        if key in self.title_to_ids:
            ret = self.title_to_ids[key]
        else:
            if self.creative:
                if key in self.alt_titles:
                    # AKA titles or foreign title without articles properly formatted
                    ret = self.alt_titles[key]
                    alt_bool = True
                else:
                    # Foreign title with articles
                    foreign_article_match = re.search(r'^(la|el|en|le|the|a|an|los|las|les|los|il|l\'|gli|i|der|das|die)\s+', key, re.IGNORECASE)
                    if foreign_article_match:
                        foreign_article = foreign_article_match.group(1)
                        key = re.sub(r'^(la|el|en|le|the|a|an|los|las|les|los|il|l\'|gli|i|der|das|die)\s+', '', key, flags=re.IGNORECASE) + ', ' + foreign_article
                        if key in self.alt_titles:
                            ret = self.alt_titles[key]
                            alt_bool = True
        
        if self.creative and not alt_bool:
            # Disambiguation part 1
            for movie in self.title_to_ids:
                if key == movie:
                    ret.extend(self.title_to_ids[movie])
                elif movie.lower().startswith(key.lower() + " ") or movie.lower().startswith(key.lower() + ":"):
                    ret.extend(self.title_to_ids[movie])
                elif movie.lower().endswith(" " + key.lower()):
                    ret.extend(self.title_to_ids[movie])

        if ret is None:
            ret = []

        return list(set(ret))

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
        sentiment = 0
        negation = False
        score = 0
        previous_word = None
        
        end_of_sentence = ["!", "?", ",", ";", ":", "."]
        strong_words = ["really", "very", "never", "extremely", "totally", "absolutely", "completely", "utterly", "entirely"]
        pos = ["liked", "loved", "loves", "enjoyed", "enjoys", "likes", "totally"]
        strong_pos = ["loved", "love", "loves"]
        negs = ["not", "never", "no", "barely", "hardly", "scarcely", "nor", "neither", "didn't"]
        strong_neg = ["terrible", "awful", "horrible", "worst", "hate", "hated", "hates"]
        
        for word in preprocessed_input.split(" "):
            og_word = word
            word = ''.join(x for x in og_word if not x in end_of_sentence)
            
            word_score = 0
            if word.endswith('n\'t') or word in negs:
                negation = True
            elif word in self.sentiment or word in strong_neg or word in pos:
                if word in pos or (word in self.sentiment and 'pos' == self.sentiment[word]):
                    if negation:
                        if word in strong_pos and self.creative:
                            word_score -= 2
                        else:
                            word_score -= 1
                    else:
                        if word in strong_pos and self.creative:
                            word_score += 2
                        else:
                            word_score += 1
                elif word in strong_neg or (word in self.sentiment and 'neg' == self.sentiment[word]):
                    if negation:
                        if word in strong_neg and self.creative:
                            word_score += 2
                        else:
                            word_score += 1
                    else:
                        if word in strong_neg and self.creative:
                            word_score -= 2
                        else:
                            word_score -= 1
            word_contains_punc = any(ele in og_word for ele in end_of_sentence)
            if word in string.punctuation or word_contains_punc and self.creative: 
                negation = False
            if previous_word in strong_words and self.creative: 
                if word_score == 0:
                    word = previous_word # Ensures that this strength is applied to the next word
                word_score *= 2
            if word == 'but':
                score = score -1 
            previous_word = word
            score += word_score
        sentiment = score

        return sentiment

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
        movie_ids = {}
        mov2_sent = {}
        sent = self.extract_sentiment(preprocessed_input)
        titles = self.extract_titles(preprocessed_input)
        for t in titles:
            mov2_sent[t] = sent
            movie_ids  = self.find_movies_by_title(t)
            if movie_ids == None:
                continue
            for idd in movie_ids:
                self.user_ratings[idd] = sent
        return mov2_sent

    def dist(self, s1, s2):
        """
        Computes the Levenshtein distance between two strings s1 and s2.

        :param s1: the first string
        :param s2: the second string
        :return: the Levenshtein distance between s1 and s2
        """
        if len(s1) > len(s2):
            s1, s2 = s2, s1

        # Initialize the matrix
        distances = range(len(s1) + 1)

        for index2, char2 in enumerate(s2):
            new_distances = [index2 + 1]

            for index1, char1 in enumerate(s1):
                if char1 == char2:
                    new_distances.append(distances[index1])
                else:
                    new_distances.append(1 + min((distances[index1], distances[index1 + 1], new_distances[-1])))

            distances = new_distances

        return distances[-1]


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
        min_dist = 100
        choices = []
        for i in self.title_to_ids.keys():
            d = self.dist(i, title)
            if d <= max_distance:
                min_dist = d
                for j in self.title_to_ids[i]:
                    choices.append(j)
        return choices

    def disambiguate(self, clarification, candidates=[]):
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
        # Check if the clarification matches a movie year in parentheses
        year_match = re.search(r"\b\d{4}\b", clarification)
        new_candidates = []
        if year_match:
            # If it does, filter the candidates to only include movies with that year
            year = clarification
            for idx in candidates:
                title = self.movies[idx][0]
                match = re.search(r'\((\d{4})\)', title)
                if match[1] == year:
                    new_candidates.append(idx)

        if len(clarification) == 1:
            try:
                index = int(clarification) - 1
                if index >= 0 and index < len(candidates):
                    return [candidates[index]]
            except ValueError:
                pass

        # Check if the clarification matches a movie title
        title_match = []
        for idx in candidates:
            movie_title = self.movies[idx][0]
            if movie_title.lower() == clarification.lower():
                # If it matches exactly, return that movie index
                title_match.append(idx)
            elif clarification.lower() in movie_title.lower() :
                # If it's a prefix of the title, remember this movie index for later
                title_match.append(idx)

        if title_match != []:
            return title_match

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

        binarized_ratings = []
        for row in ratings:
            binarized_row = []
            for rating in row:
                if rating > threshold:
                    binarized_row.append(1)
                elif rating <= threshold and rating != 0:
                    binarized_row.append(-1)
                else:
                    binarized_row.append(0)
            binarized_ratings.append(binarized_row)
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
        if np.linalg.norm(u)  == 0 or np.linalg.norm(v) == 0:
            return 0
        else:
            similarity = np.matmul(u,v)/(np.linalg.norm(u)*np.linalg.norm(v))
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

        # Populate this list with k movie indices to recommend to the user.
        recommendations = []
        id_to_my_rating = {}

        sh =  np.shape(ratings_matrix )

        # get the list of movies we rated. (Linear scan) and return as a list of indices
        
        our_movies = []
        for i in range(np.shape(user_ratings)[0]):         
            if user_ratings[i] != 0:
                our_movies.append(i)
                print("We have recorded that you rated", self.movies[i][0], user_ratings[i] )

        # loop over all movies B
        movie_closeness = []
        for i in range(sh[0]):
            if i in our_movies:
                continue
            score = 0
            for j in our_movies:
                score += user_ratings[j] *  self.similarity(ratings_matrix[i], ratings_matrix[j])
            movie_closeness.append( (i, score) )

        list1 = sorted(movie_closeness, key=lambda x:x[1], reverse=True)
        for a in list1[0:5]:
            self.recs.append(self.movies[a[0]][0])

        return list(map(lambda x:x[0],  list1[0:k]))

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
        Hello! Welcome to our movie recommender chatbot. Tell us which movies
        you like, dislike, or have seen, and we'll recommend movies you might
        find enjoy.
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
