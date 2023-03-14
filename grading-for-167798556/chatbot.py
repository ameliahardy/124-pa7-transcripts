# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import numpy as np

# Use 're' to find relevant info
import re

import random

from deps.dialogue import NO_TITLES, MANY_TITLES, CONFUSION, NEGATIVE_ANGER, A_EMOTION, POSITIVE_HAPPY, H_EMOTION

ARTICLES = ['a', 'the', 'an']

# Variable used to determine sentiment threshold (ratio of positive to negative words)
LAMBDA = 1
POS_SENTIMENT_ADDONS = ["like", "liked", "love", "loved", "enjoyed"]
NEGATIVE_MODS = ["didn't", "don't", "never", "won't", "not"]
AGREE = ["yes", "ok", "yeah", "sure", "alright", "okay"]




# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 7."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'peterbot'

        self.creative = creative
        self.modes = { "disambiguate" : [], "spellcheck" : []}
        self.sentiment_memory = 2

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
        
        # Store a Numpy vector representing the movies the user has rated
        self.rated_movies = np.zeros(len(self.titles))
        self.n_rated_movies = 0
        self.recommended_movies = []
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

        greeting_message = "Hehehe I am peterbot. This reminds me of the time Quagmire asked me for movie suggestions..."

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

        goodbye_message = "See you at the Clam some time?"

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
        line = self.preprocess(line)
        response = ""
        
        # Mode processes:
        #1. disambiguate
        if self.modes["disambiguate"]:
            ids = self.disambiguate( line, self.modes["disambiguate"])
            # If we find one match, we're done disambiguating
            if len(ids) == 1:
                self.modes["disambiguate"] = []
                if self.sentiment_memory == 1:
                    line = "I like " + '\"' + self.titles[ids[0]][0] + '\"' 
                    
                if self.sentiment_memory == -1:
                    line = "I didn't like " + '\"' + self.titles[ids[0]][0] + '\"'
                if self.sentiment_memory == 0:
                    line = "I saw " + '\"' + self.titles[ids[0]][0] + '\"'
                line = self.preprocess(line)
            # no match
            elif len(ids) == 0:
                # try again or stop
                response = 'Uhhhhhhhhhhm, so that didn\'t help... can you just clarify which movie you meant?'
                return response
            elif len(ids) > 1:
                self.modes["disambiguate"] = ids
                for id in ids:
                    response += self.titles[id][0] + ' or '
                response = 'Which one? ' + response[:-1] + '... oh wait, that\'s it, hehehehehe'
                return response
        # Mode Processes:
        # #2. spellcheck
        elif self.modes["spellcheck"]:
            if len(self.modes["spellcheck"]) == 1:
                should_stop = False
                for yes_keyword in AGREE:
                    if line.find(yes_keyword) != -1:
                        should_stop = True
                        if self.sentiment_memory == 1:
                            line = "I like " + '\"' + self.titles[self.modes["spellcheck"][0]][0] + '\"'
                        if self.sentiment_memory == -1:
                            line = "I didn't like " + '\"' + self.titles[self.modes["spellcheck"][0]][0] + '\"'
                        if self.sentiment_memory == 0:
                            line = "I saw " + '\"' + self.titles[self.modes["spellcheck"][0]][0] + '\"'
                    if should_stop:
                        line = self.preprocess(line)
                        self.modes["spellcheck"] = []
                        break


        if len(self.recommended_movies) > 0:
                # Make a recommendation while they are available and they still want one
                for yes_keyword in AGREE:
                    if line.find(yes_keyword) != -1:
                        response = f"Your responses remind me of the time I saw {self.titles[self.recommended_movies[0]][0]}. Want another?"
                        self.recommended_movies = self.recommended_movies[1:]
                        return response
                self.recommended_movies = []
                self.n_rated_movies = 0
                response = "Ok. All done giving recommendations! Hehehehehehehehe Peter style!"
        else:
            response = ""
            found_titles = self.extract_titles(line)
            #Emotion regulation
            angry_word = ""
            emotion = 0
            for word in NEGATIVE_ANGER:
                if word in line:
                    response = A_EMOTION[random.randrange(0,3)] + word + ". "
                    emotion = 1
                    break
            for word in POSITIVE_HAPPY:
                if word in line:
                    response = H_EMOTION[random.randrange(0,3)] + word + "! "
                    emotion = 1
                    break

            # get rid of non alphabetical letters in found_titles
            # No titles found; could be unrelated to movies or no titles were included
            if len(found_titles) == 0:
                if emotion == 0:
                    response = NO_TITLES[random.randrange(0,6)]
            elif len(found_titles) != 1:
                # More than one title; don't have to handle this case in Starter Mode
                response = MANY_TITLES[random.randrange(0,4)]
            else:
                sentiment = self.extract_sentiment(line)
                potential_movie_ids = self.find_movies_by_title(found_titles[0])
                if len(potential_movie_ids) == 0:
                    # No movies with the given title were found
                    if self.creative:
                        close_titles = self.find_movies_closest_to_title(found_titles[0])
                        if len(close_titles) != 0:
                            self.sentiment_memory = sentiment
                            response = "Did you mean"
                            for title in close_titles:
                                self.modes["spellcheck"].append(title)
                                response += f" {self.titles[title][0]}"
                            response += "?"
                        else: 
                            response = CONFUSION[random.randrange(0,3)]
                    else:
                        response = CONFUSION[random.randrange(0,3)]
                elif len(potential_movie_ids) == 1:
                    # Found exactly one movie to analyze
                    response = f'So you\'ve seen "{self.titles[potential_movie_ids[0]][0]}" '
                    if sentiment == 1:
                        # Positive response
                        response += f'and liked it? Me and the boys love a good {self.titles[potential_movie_ids[0]][1].split("|")[0]} movie too!'
                        self.n_rated_movies += 1
                    elif sentiment == -1:
                        # Negative response
                        response += f'didn\'t like it? Yeah, "{self.titles[potential_movie_ids[0]][0]}" isn\'t really my style either.'
                        self.n_rated_movies += 1
                    else:
                        # Sentiment was neutral; query for more information
                        response += f'? And what did you think?'
                    self.rated_movies[potential_movie_ids[0]] = sentiment
                else:
                    # Ask for clarification by listing out all potential movies found
                    response += 'Did you mean '
                    for i in potential_movie_ids:
                        self.modes["disambiguate"].append(i)
                        self.sentiment_memory = sentiment
                        response += self.titles[i][0] + ' or '
                    response = response[:-4] + '?'
            if self.n_rated_movies >= 5:
                # If we've seen 5 movies, we can make a recommendation
                self.recommended_movies = self.recommend(self.rated_movies, self.ratings)
                response += f' Your responses remind me of the time I saw {self.titles[self.recommended_movies[0]][0]}. Would you like another?'
                self.recommended_movies = self.recommended_movies[1:]
                

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
        text = re.sub('[-?,]+', '', text).lower() # lowercase input and get rid of dashes to help with recognizing better
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
        titles = []
        for match in re.findall('"(.*?)"', preprocessed_input):
            titles.append(match.title())
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
        # Exact (or near exact) match in starter mode
        if not self.creative:
            n_possible = []
            for i in range(len(self.titles)):
                if re.search(title.lower() + "(?: \(\d{4}\))", self.titles[i][0].lower()) or title == self.titles[i][0].lower():
                    n_possible.append(i)
            if len(n_possible) == 1:
                return n_possible
        tokens = []
        ids = []
        title = re.sub("\.", "", self.preprocess(title))
        for token in title.split():
            # Remove articles and years
            if token not in ARTICLES:
                tokens.append(token.lower())
        # Only suggest a title if all tokens appear in the title
        for i in range(len(self.titles)):
            allTokensAppear = True
            for token in tokens:
                if not re.search(r"\b" + token + r"\b(?!')", self.titles[i][0].lower()):
                    # Require all tokens must appear somewhere in the title
                    allTokensAppear = False
                    break
            if allTokensAppear:
                ids.append(i)
        
            
        return sorted(ids, key=lambda x: int(re.search("\d{4}", self.titles[x][0])[0]))

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
        # Don't include titles in sentiment analysis
        input_no_titles = re.sub(' "(.*?)"[\.!?]?', '', preprocessed_input)
        tokens = input_no_titles.split(' ')
        
        # Count all positive and negative tokens
        # If a token is a negative modifier, switch the type of token
        # for the next occuring token that expresses sentiment
        pos_tokens = 0
        neg_tokens = 0
        negate_mode = False
        
        for token in tokens:
            if token in self.sentiment:
                if self.sentiment[token] == 'pos':
                    if not negate_mode:
                        pos_tokens += 1
                    else:
                        neg_tokens += 1
                        negate_mode = False
                if self.sentiment[token] == 'neg':
                    if not negate_mode:
                        neg_tokens += 1
                    else:
                        pos_tokens += 1
                        negate_mode = False
            elif token in POS_SENTIMENT_ADDONS:
                if not negate_mode:
                    pos_tokens += 1
                else:
                    neg_tokens += 1
                    negate_mode = False
            if token in NEGATIVE_MODS:
                negate_mode = not negate_mode
        sentiment = 0
        if pos_tokens == 0 and neg_tokens == 0:
            return sentiment
        if (neg_tokens == 0 and pos_tokens > 0) or pos_tokens / neg_tokens > LAMBDA:
            sentiment = 1
        if sentiment != 1 and (pos_tokens == 0 and neg_tokens > 0) or neg_tokens / pos_tokens > LAMBDA:
            sentiment = -1
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
        return []

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
        potential_movies = []
        min_dist_seen = max_distance
        title = re.sub("-", "", title.lower())
        for k in range(len(self.titles)):
            # Don't include years when calculating edit distance
            comp_title = re.sub("(?: \(\d{4}\))", "", self.titles[k][0]).lower()
            if re.search(r"\b" + title[0], comp_title) and abs(len(comp_title) - len(title)) < max_distance:
                D = np.zeros((len(title), len(comp_title)))
                for j in range(len(comp_title)):
                    D[0][j] = j
                for i in range(len(title)):
                    D[i][0] = i
                for i in range(1, len(title)):
                    for j in range(1, len(comp_title)):
                        D[i][j] = min(D[i - 1][j] + 1, D[i][j - 1] + 1, D[i - 1][j - 1] + (2 if title[i] != comp_title[j] else 0))
                if D[len(title) - 1][len(comp_title) - 1] < min_dist_seen:
                    # New minimum distance; clear list and start using new min
                    potential_movies = []
                    min_dist_seen = D[len(title) - 1][len(comp_title) - 1]
                if D[len(title) - 1][len(comp_title) - 1] == min_dist_seen:
                    # Found a potential match with same minimal edit distance; add
                    potential_movies.append(k)
        return potential_movies

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
        clarifiedIndices = []
        thTranslations = {"first" : 0, "second" : 1, "third": 2, "fourth" : 3, "fifth" : 4, "sixth": 5,
                           "seventh" : 6, "eighth" : 7, "ninth" : 8}

        for cand in candidates:
            title = re.sub("(?: \(\d{4}\))", "", self.titles[cand][0])
            if re.search(clarification.lower(), title.lower()):
                clarifiedIndices.append(cand)
        if not clarifiedIndices:
            # if clarification is a number 
            if clarification.isdigit() and len(candidates) > (int(clarification) - 1):
                return [candidates[int(clarification) - 1]]
            # if clarification includes "n'th" one
            for th in thTranslations.keys():
                if re.search(th, clarification.lower()):
                    return [candidates[thTranslations[th]]]
            # if clarification is year
            year = re.search("\d{4}", clarification)
            if re.search("recent", clarification.lower()):
                candidates = sorted(candidates, key=lambda x: int(re.search("\d{4}", self.titles[x][0])[0]))
                return [candidates[-1]]
            if year:
                return [candidate for candidate in candidates if re.search(year.group(0), self.titles[candidate][0])]
            for token in clarification.split():
                idx = -1

                for i in candidates:
                    if re.search(token, self.titles[i][0]):
                        if idx == -1:
                            idx = i
                        else:
                            idx = -1
                            break
                if idx != -1:
                    return [idx]



        
        return clarifiedIndices

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

        binarized_ratings = np.where(ratings > threshold, 1, ratings)
        binarized_ratings = np.where(ratings <= threshold, -1, binarized_ratings)
        binarized_ratings = np.where(ratings == 0, 0, binarized_ratings)

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
        if np.sum(u) == 0 or np.sum(v) == 0:
            return 0
        similarity = np.dot(u / np.sqrt(np.sum(u ** 2)), v / np.sqrt(np.sum(v ** 2)))
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
        
        r = np.zeros(len(user_ratings))
        rated_movies = [i for i in range(len(user_ratings)) if user_ratings[i] != 0]
        for i in range(len(ratings_matrix)):
            if user_ratings[i] == 0:
                for j in rated_movies:
                    r[i] += (self.similarity(ratings_matrix[i], ratings_matrix[j]) * user_ratings[j])
        recommendations = [(r[i], i) for i in range(len(r))]
        recommendations = sorted(recommendations, key=lambda x: x[0], reverse=True)[:k]
        recommendations = [x[1] for x in recommendations]

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
        A Peter Griffin core chatbot for CS124. Hehehehehehehe.
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')