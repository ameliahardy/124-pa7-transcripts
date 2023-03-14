# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import re

import util

import numpy as np
import porter_stemmer

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""
    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.creative = creative
        if self.creative:
            self.name = 'CineBotYoda'
        else:
            self.name = 'CineBot'

        self.recommendations = []
        self.num_pts = 0
        self.confirming = []
        self.not_found = ""
        self.not_found_sent = 0

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.user = np.zeros((len(self.titles),))

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

        if self.creative:
            greetings = ["A movie you seek, hm...? Help you, YodaCinebot will."]
            greeting_message = np.random.choice(greetings)
        else:
            greetings = ["Greetings! I'm CineBot, here to help you discover your next cinematic obsession."]
            greeting_message = np.random.choice(greetings)

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
        if self.creative:
            goodbye_message = "Farewell, and may the Force be with you. "
        else:
            goodbye_message = "Enjoy your movie!"

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
        response = ""
        titles_fnd = self.extract_titles(line)
        titles_idx = []
        sents = []

        # Emotion Checking
        if self.creative:
            response += self.comment_emotions(line)

        if self.creative and "can you" in line.lower() and line.lower().index("can you") == 0:
            str = line[8:]
            if str[-1] == '?':
                str = str[:-1]
            if "your" in str:
                str = str.replace("your", "my")
            elif "my" in str:
                str = str.replace("my", "your")
            return np.random.choice(["Only when relating to movies, can I {}. ", "Unless discussing movies, {}, I cannot. "]).format(str)

        if self.creative and "what is" in line.lower() and line.lower().index("what is") == 0:
            str = line[8:]
            if str[-1] == '?':
                str = str[:-1]
            if "your" in str:
                str = str.replace("your", "my")
            elif "my" in str:
                str = str.replace("my", "your")
            return np.random.choice(["Tell you what {} is, I shall not. ", "Know what {} is, I do not. "]).format(str)

        if self.num_pts >= 5 and is_yes(line):
            return response + self.give_rec(self.recommendations)

        if self.num_pts >= 5 and is_no(line):
            self.num_pts = 4
            self.recommendations = []
            if self.creative:
                response += "If more recommendations you would like, tell me about more movies, you must. "
            else:
                response += "If you'd like more recommendations, just tell me about some more movies that you've watched! "

        if len(self.confirming) > 0:
            title = self.confirming.pop(0)
            if is_yes(line):
                self.confirming = []
                response += self.repeat_user([self.title_from_id(title)], [self.not_found_sent])
                if self.not_found_sent == 0:
                    return "Understand your feelings toward \"{}\", I do not. Specify, you should. ".format(self.title_from_id(title))
                if self.user[title] == 0:
                    self.num_pts += 1
                self.user[title] = self.not_found_sent
                if self.num_pts >= 5:
                    self.recommendations = self.recommend(self.binarize(self.user), self.ratings, k=25)
                    response += self.give_rec(self.recommendations)
                return response
            elif len(self.confirming) > 0:
                return response + confirm_spelling(self.title_from_id(self.confirming[0]))
            else:
                return response + "Heard of \"{}\", I have not. Try another one, you should. ".format(self.not_found)
        elif len(titles_fnd) == 0:
            if response == "":
                if self.creative:
                    responses = ["Hmm... Confused I am. Discuss movies, we should. ", "Clouded, the future is, but movies, we should discuss. "]
                else:
                    responses = ["Let's get back to discussing movies. ", "Maybe we should get talk more about movies. "]
                return np.random.choice(responses)
            else:
                return response

        if self.creative and len(titles_fnd) > 1:
            pairs = self.extract_sentiment_for_movies(line)
            if pairs[0][1] == 0:
                return response + "Understand your feelings toward these movies, I do not. Specify, you should. "
            for pair in pairs:
                id = self.find_movies_by_title('"' + pair[0] + '"')
                if id != []:
                    titles_idx.append(id[0])
                    sents.append(pair[1])
                else:
                    self.confirming = self.find_movies_closest_to_title(pair[0])
                    if len(self.confirming) != 0:
                        self.not_found = pair[0]
                        self.not_found_sent = pair[1]
                        return response + confirm_spelling(self.title_from_id(self.confirming[0]))
                    return "Heard of \"{}\", I have not. Try another one, you should. ".format(self.not_found)
        else:
            idx_check = self.find_movies_by_title(titles_fnd[0])
            for title in idx_check:
                titles_idx.append(title)

            if len(idx_check) > 1:
                if self.creative:
                    return response + "Too many movies named \"{}\", there are. Specify, can you? ".format(titles_fnd[0])
                else:
                    return response + "Sorry, there are many movies named \"{}\". Can you specify? ".format(titles_fnd[0])
            sent = self.extract_sentiment(line)
            if len(titles_idx) == 0:
                if self.creative:
                    self.confirming = self.find_movies_closest_to_title(titles_fnd[0])
                    self.not_found = titles_fnd[0]
                    if len(self.confirming) != 0:
                        self.not_found_sent = sent
                        return response + confirm_spelling(self.title_from_id(self.confirming[0]))
                    return "Heard of \"{}\", I have not. Try another one, you should. ".format(self.not_found)
                else:
                    return "Sorry, I've never heard of \"{}\". Can you try another? ".format(titles_fnd[0])
            sents.append(sent)
            if sent == 0:
                if self.creative:
                    if response == "":
                        return "Understand your feelings toward \"{}\", I do not. Specify, you should. ".format(self.title_from_id(titles_idx[0]))
                    else:
                        return response
                else:
                    return response + "I'm not sure I understand your feelings on \"{}\". Please specify. ".format(self.title_from_id(titles_idx[0]))

        for i in range(len(titles_idx)):
            if self.user[titles_idx[i]] == 0:
                self.num_pts += 1
            self.user[titles_idx[i]] = sents[i]

        response += self.repeat_user(titles_fnd, sents)

        if self.num_pts >= 5:
            self.recommendations = self.recommend(self.binarize(self.user), self.ratings, k=25)
            response += self.give_rec(self.recommendations)
        else:
            if self.creative:
                responses = ["Another movie, talk about, you should. ", "About another movie, tell me. ", "Perhaps another movie, we should dicuss. "]
            else:
                responses = ["Tell me about another movie. ", "What's another movie that you've seen? ", "Are there any other movies you've liked or disliked?"]
            response += np.random.choice(responses)
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
        movies = re.findall('\"[^\"]+\"', preprocessed_input)
        for i in range(len(movies)):
            movies[i] = movies[i][1:-1]
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

        idx = []
        title_year = re.findall('\(\d\d\d\d\)', title.lower())
        title_comp = re.findall('[\w\'\-]+', title.lower())
        if title_year != []:
            title_year = title_year[0][1:-1]
            title_comp.remove(title_year)

        for i in range(len(self.titles)):
            dict_year = re.findall('\(\d\d\d\d\)', self.titles[i][0].lower())
            dict_comp = re.findall('[\w\'\-]+', self.titles[i][0].lower())
            if dict_year != []:
                dict_year = dict_year[0][1:-1]
                dict_comp.remove(dict_year)
            if set(title_comp) == set(dict_comp) and (title_year == [] or title_year == dict_year):
                idx.append(i)

        return idx

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

        negation = ["didn\'t", "don\'t", "never", "won\'t", "not", "can\'t", "nor", "isn\'t", "hadn\'t"]

        ps = porter_stemmer.PorterStemmer()
        titles = re.findall('\"[^\"]+\"', preprocessed_input)
        processed_input = preprocessed_input

        for title in titles:
            processed_input = processed_input.replace(title, '')
        input = re.findall('[\w|\']+', processed_input)

        while "really" in input:
            input.remove("really")

        sent = []
        for n in range(len(input)):
            word = input[n]
            if word not in self.sentiment:
                word = ps.stem(input[n])
            if word not in self.sentiment:
                if word == "enjoi":
                    sent.append(1)
                elif word == "dislik":
                    sent.append(-1)
                else:
                    sent.append(0)
            elif self.sentiment[word] == 'pos':
                sent.append(1)
            else:
                sent.append(-1)

        # TODO: Refine this, it's an absolute mess
        inv = 1
        for n in range(len(input)):
            if input[n] in negation and n < len(input)-1:
                inv = -1
        sent = np.array(sent)
        num_pos = len(np.where(sent == 1)[0])
        num_neg = len(np.where(sent == -1)[0])
        if self.creative and num_pos > 2.4*num_neg:
            return 2 * inv
        elif self.creative and num_neg > 2.4*num_pos:
            return -2 * inv
        elif num_pos > num_neg:
            return 1 * inv
        elif num_neg > num_pos:
            return -1 * inv
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
        titles = re.findall('\"[^\"]+\"', preprocessed_input)
        sents = []

        last = 0
        for t in range(len(titles)):
            title = titles[t][1:-1]
            if t < len(titles)-1:
                cur = preprocessed_input.index(title)
            else:
                cur = len(preprocessed_input)
            sent = self.extract_sentiment(preprocessed_input[last:cur])

            inv = 1
            if sent == 0 and sents != []:
                if " not " in preprocessed_input[last:cur]:
                    inv = -1
                sents.append((title, inv*sents[-1][1]))
            else:
                sents.append((title, sent))
            last = cur
        return sents


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

        rem_year = True
        if '(' in title:
            rem_year = False
        costs = []
        found_idx = []
        for i in range(len(self.titles)):
            potential = self.titles[i][0]
            if rem_year and '(' in potential:
                potential = potential[:potential.index('(')-1]
            cost = min_edit_dist(title, potential)
            if cost <= max_distance:
                costs.append(cost)
                found_idx.append(i)
        if found_idx == []:
            return []

        min_cost = min(costs)
        result = []
        for i in range(len(found_idx)):
            if costs[i] == min_cost:
                result.append(found_idx[i])
        return result

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
        binarized_ratings[np.where(ratings > threshold)] = 1
        binarized_ratings[np.where(ratings <= threshold)] = -1
        binarized_ratings[np.where(ratings == 0)] = 0

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
        epsilon = 0.00000001
        similarity = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v) + epsilon)
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
        sims = []
        ratings = np.array(ratings_matrix)
        for m in range(len(ratings)):
            score = np.nan
            if user_ratings[m] == 0:
                score = 0
                for u in range(len(user_ratings)):
                    if user_ratings[u] != 0:
                        score += user_ratings[u]*self.similarity(ratings[m], ratings[u])
            sims.append(score)
        sims = np.array(sims)

        recommendations = []
        for i in range(k):
            arg = np.nanargmax(sims)
            sims[arg] = np.nan
            recommendations.append(arg)

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
        if self.creative:
            return "CineBotYoda, your personal movie recommendation expert, I am! Whether action, romance, or comedy; recommend movies to you, I will. In \"Quotation Marks\" type your movie, and let the Force guide you!"
        return "Welcome to CineBot, your personal movie recommendation expert! Whether you're in the mood for action, romance, or comedy, CineBot has got you covered. Just tell us what movies you like in \"quotation marks\", and let the movie magic begin!"


    def give_rec(self, recs):
        if not self.creative:
            if len(recs) == 0:
                return "I'm afraid that I'm out of recommendations. "
            return "You should watch \"{}\"! Would you like another recommendation? ".format(self.title_from_id(recs.pop(0)))
        else:
            if len(recs) == 0:
                return "Out of recommendations, i am."
            return "Watch \"{}\", you should. Seek another recommendation, do you? ".format(self.title_from_id(recs.pop(0)))

    def title_from_id(self, id):
        title = self.titles[id][0]
        fnd = re.findall(" (\d\d\d\d)", title)
        if len(fnd) != 0:
            title = title.replace(fnd[0], "")
        return title

    def repeat_user(self, titles, sents):
        response = ""
        positive_sents = []
        negative_sents = []
        for i in range(len(sents)):
            if sents[i] > 0:
                positive_sents.append(titles[i])
            elif sents[i] < 0:
                negative_sents.append(titles[i])
        if self.creative:
            starters = ["", "Hmm... "]
            pos_res = ["Liked ", "Enjoyed ", "Loved "]
            neg_res = ["Disliked ", "Hated ", "Loathed "]
            endings = [", I see. ", ", you did. "]
        else:
            starters = ["I see ", "I understand that ", "So ", "I realize that "]
            pos_res = ["you liked ", "you enjoyed ", "you favored "]
            neg_res = ["you didn't like ", "you disliked ", "you were not fond of "]
            endings = [". "]
        response += np.random.choice(starters)
        # Positive sentiments
        if len(positive_sents) > 0:
            response += np.random.choice(pos_res)
            for i in range(len(positive_sents)):
                response += '"{}"'.format(positive_sents[i])
                if len(positive_sents) > 2 and i < len(positive_sents)-1:
                    response += ", "
                if len(positive_sents) > 1 and i == len(positive_sents)-2:
                    response += " and "
            if len(negative_sents) > 0:
                response += ", but "
        # Negative sentiments
        if len(negative_sents) > 0:
            if len(positive_sents) > 0 and self.creative:
                response += np.random.choice(neg_res).lower()
            else:
                response += np.random.choice(neg_res)
            for i in range(len(negative_sents)):
                response += '"{}"'.format(negative_sents[i])
                if len(negative_sents) > 2 and i < len(negative_sents) - 1:
                    response += ", "
                if len(negative_sents) > 1 and i == len(negative_sents) - 2:
                    response += " and "
        return response + np.random.choice(endings)

    def comment_emotions(self, line):
        response = ""

        titles = re.findall('\"[^\"]+\"', line)
        processed_input = line
        for title in titles:
            processed_input = processed_input.replace(title, '')
        input = re.findall('[\w|\']+', processed_input)

        anger_words = ["angry", "mad", "furious", "irrate", "outraged", "annoyed", "insulted", "frustrated", "enraged"]
        sad_words = ["sad", "depressed", "upset", "worried", "unhappy", "miserable", "melancholy", "heartbroken"]
        happy_words = ["happy", "excited", "delighted", "astonished", "joyful"]
        fear_words = ["afraid", "scared", "horrified", "anxious", "fearful", "terrified", "frightened", "nervous", "petrified"]
        bored_words = ["bored", "unsatisfied"]
        is_angry = False
        is_sad = False
        is_happy = False
        is_fear = False
        is_bored = False

        for w in input:
            if w in anger_words and not is_angry:
                is_angry = True
                response += np.random.choice(["An ally of the Dark Side, anger is. Be {}, you should not. ", "Learn to let go of your negative feelings, you should. Being {} can lead only to the Dark Side. "]).format(w)
            elif w in sad_words and not is_sad:
                is_sad = True
                response += np.random.choice(["{}, you should not be, for many great movies there are to watch. ", "If {} you find yourself, then a comedy, you should watch. "]).format(w)
            elif w in happy_words and not is_happy:
                is_happy = True
                response += np.random.choice(["Only when {}, can one appreciate the greatest movies. ", "A gift, being {} is, for positive feelings are the strength of the Light Side of the Force. "]).format(w)
            elif w in fear_words and not is_fear:
                is_fear = True
                response += "Fear is the path to the Dark Side. Fear leads to anger. Anger leads to hate. Hate leads to suffering. "
            elif w in bored_words and not is_bored:
                is_bored = True
                response += np.random.choice(["If bored you are, watch another movie, you should. ", "Hmm... Only by watching movies can one hope to satisfy their boredom. "])
        return response

def min_edit_dist(u, v):
    arr = np.zeros((len(u)+1, len(v)+1))
    for i in range(len(u)+1):
        arr[i, 0] = i
    for j in range(len(v)+1):
        arr[0, j] = j
    for i in range(1, len(u)+1):
        for j in range(1, len(v)+1):
            edit = 1
            if u[i-1] == v[j-1]:
                edit = 0
            arr[i, j] = min(arr[i,j-1]+1, arr[i-1, j]+1, arr[i-1, j-1]+edit)
    return int(arr[len(u), len(v)])

def is_yes(line):
    aff = ["yes", "yeah", "yep", "course"]
    neg = ["no", "nope", "nah", "never"]
    words = re.findall('[\w|\']+', line.lower())
    for w in words:
        if w in aff:
            return True
        if w in neg:
            return False
    return False

def is_no(line):
    aff = ["yes", "yeah", "yep", "course"]
    neg = ["no", "nope", "nah", "never"]
    words = re.findall('[\w|\']+', line.lower())
    for w in words:
        if w in aff:
            return False
        if w in neg:
            return True
    return False

def confirm_spelling(title):
    responses = ["Mean to say, \"{}\" did you?", "A misspelling I sense. Intended to say, \"{}\", did you?"]
    return np.random.choice(responses).format(title)


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
