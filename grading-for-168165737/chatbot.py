# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import numpy as np
from collections import defaultdict
from difflib import SequenceMatcher
from porter_stemmer import PorterStemmer
import random

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

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        self.p = PorterStemmer()

        # Positive Prior, Negative Prior
        self.positive_prior, self.negative_prior = 1627/3626, 1999/3626

        self.ratings = self.binarize(ratings)
        self.movies_to_recommend = []
        self.user_ratings = np.zeros(len(self.ratings))
        self.rec_count = -1

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

        greeting_message = random.choice(
            ["Heyyyyyyyy girly-cat! ",
             "Wassup! ",
             "Hello, earthling. "
             ])

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

        goodbye_message = random.choice([
            "See you slay-ter! ",
            "Byeeeeeeeeeeeeeee. ",
            "Goodbye, coding wizard. "
        ])

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
        def modified_extract_titles(preprocessed_input):
            """Modified extract potential movie titles from a line of pre-processed text.
                with spaces removed in between characters
            :param preprocessed_input: a user-supplied line of text that has been
            pre-processed with preprocess()
            :returns: list of movie titles that are potentially in the text
            """
            preprocessed_input = ''.join(preprocessed_input)
            if "\"" in preprocessed_input or "\'" in preprocessed_input:
                return preprocessed_input.split('\"')[1::2]

            def generate_subsets(l):
                if l == []:
                    return [[]]
                subsets = generate_subsets(l[1:])
                return subsets + [[l[0]] + subset for subset in subsets]

            def get_title_given_index(
                idx): return self.titles[idx][0].split('(')[0].strip()

            def remove_punc(x): return ''.join(
                c for c in x if c.isalnum() or c.isspace())
            possibilities = set([' '.join(sorted(p)) for p in generate_subsets(
                remove_punc(preprocessed_input).lower().split())])

            def candidate(index): return ' '.join(
                sorted(remove_punc(get_title_given_index(index)).lower().split()))
            result = [get_title_given_index(i) for i in range(
                len(self.titles)) if candidate(i) in possibilities]
            return [x for x in result if x]

        ########################################################################
        # TODO: Implement the extraction and transformation in this method,    #
        # possibly calling other functions. Although your code is not graded   #
        # directly based on how modular it is, we highly recommended writing   #
        # code in a modular fashion to make it easier to improve and debug.    #
        ########################################################################

        response = ""

        movie = modified_extract_titles(line)

        # update what movies user likes/dislikes
        self.movies_to_recommend.append(movie)

        # Dealing with arbitrary responses / failing gracefully when there is no movie detected.
        if len(movie) == 0 and len(self.movies_to_recommend) <= 5:
            confused_response = ["I don't get it XMXM?", "Interesting. Please tell me more.",
                                 "Only you are so unique to have been so brave with what you said."]
            response = random.choice(confused_response)
            return response

        # update user rating
        sent = self.extract_sentiment(self.preprocess(line))
        # user rating is only updated when recommendations haven't happened
        if self.rec_count == -1:
            self.user_ratings[self.find_movies_by_title(movie[0])] = sent

         # Recommendation system that activates when user lists five or more movies in the database
        if len(self.movies_to_recommend) >= 5:
            self.rec_count += 1
            recommendation_id = self.recommend(
                self.user_ratings, self.ratings)[self.rec_count]
            movie = self.titles[recommendation_id]
            recommendation_response = [f"Based on what you've told me, sounds like you would enjoy {movie[0]}. Would you like another recommendation? ",
                                       f"Seems you might be in favor of {movie[0]}. Would you like another recommendation? ", f"You perhaps might enjoy {movie[0]}. Would you like another recommendation? "]
            response = random.choice(recommendation_response)
            if line == "no":
                response = self.goodbye()
            return response

        # When user enters multiple movies, the chatbot performs multi-movie sentiment analysis
        temp_movie = movie
        if len(movie) >= 2:
            while len(temp_movie) >= 1:
                if sent == 1:
                    multiple_movie_pos_res = [
                        f"Sounds like you enjoyed {movie[0]}. ",
                        f"Seems you were in favor of {movie[0]}. ",
                        f"You seem to enjoy {movie[0]}. ",
                        f"Appears you like {movie[0]}. "
                    ]
                    response += random.choice(multiple_movie_pos_res)
                elif sent == -1:
                    multiple_movie_neg_res = [
                        f"Sounds like you didn't enjoy {movie[0]}. ",
                        f"Seems you weren't in favor of {movie[0]}. ",
                        f"You seem to not enjoy {movie[0]}. ",
                        f"Appears you don't like {movie[0]}. "
                    ]
                    response += random.choice(multiple_movie_neg_res)
                temp_movie.pop(0)
            return response

        movie = (movie[0])

        # If the user enters a movie that isn't in the database, this clarification message prompts the user.
        if self.find_movies_by_title(movie) == []:
            response = f"Ok, seems like we haven't heard of {movie}. Can you give me another title?"
            self.movies_to_recommend.pop(0)
            return response

        movie = " ".join(movie.split())

        # Chatbot finds movies with similar titles and asks to clarify
        similar_movies = self.find_movies_closest_to_title(movie, 2)
        if len(similar_movies) > 1:
            response = f"I found more than one movie called {movie}. Can you clarify?"
            self.movies_to_recommend.pop(0)
            return response

        # Finally returns the movie and sentiment to the user in a naturalistic, human sounding manner
        positive_answer_list = [f"Ok, sounds like you enjoyed {movie}. What other movies do you like?",
                                f"{(movie)} is definitely an interesting watch. Tell me more!",
                                f"I'm glad you liked {(movie)}. I would be happy if you could share what you thought of another movie."]
        negative_answer_list = [f"Ok, it doesn't sound like you enjoyed {(movie)}. What other movies do you like or dislike?",
                                f"{(movie)} is definitely not good apparently. Can you tell me more about other movies?",
                                f"I'm glad you shared that about {(movie)}. Is there another movie where you thought negatively in the same way?"]
        if self.creative:
            response = "I processed {} in creative mode!!".format(line)
        else:
            sent = self.extract_sentiment(self.preprocess(line))
            if sent == 1:
                response = random.choice(positive_answer_list)
            elif sent == -1:
                response = random.choice(negative_answer_list)
            else:
                response = f"I'm sorry, I'm not sure if you liked {movie}. Tell me more about it."

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
        text = text.strip().split()
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
        preprocessed_input = ' '.join(preprocessed_input)
        if "\"" in preprocessed_input or "\'" in preprocessed_input:
            return preprocessed_input.split('\"')[1::2]

        def generate_subsets(l):
            if l == []:
                return [[]]
            subsets = generate_subsets(l[1:])
            return subsets + [[l[0]] + subset for subset in subsets]

        def get_title_given_index(
            idx): return self.titles[idx][0].split('(')[0].strip()

        def remove_punc(x): return ''.join(
            c for c in x if c.isalnum() or c.isspace())
        possibilities = set([' '.join(sorted(p)) for p in generate_subsets(
            remove_punc(preprocessed_input).lower().split())])

        def candidate(index): return ' '.join(
            sorted(remove_punc(get_title_given_index(index)).lower().split()))
        result = [get_title_given_index(i) for i in range(
            len(self.titles)) if candidate(i) in possibilities]
        return [x for x in result if x]

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
        if not self.creative:
            def similar(a, b): return SequenceMatcher(None, a, b).ratio()
            data = [(similar(movie.lower(), title.lower()), i)
                    for i, (movie, _) in enumerate(self.titles)]
            result = {overlap: [index for key, index in data if key == overlap]
                      for overlap in set(k for k, v in data)}
            return [i for i in result[max(result)] if set(title.lower().split()) <= set(self.titles[i][0].lower().replace(',', '').split())]
        else:
            result, get_title = [], lambda idx: self.titles[idx][0].split('(')
            for i in range(len(self.titles)):
                formed = ''.join(get_title(i)[:-1]).replace(')', '').strip() if len(
                    get_title(i)) == 3 else get_title(i)[0].strip()
                current_movie_title = formed.replace(
                    ':', '').replace(',', '').lower().split()
                title_to_compare = title.replace(
                    ':', '').replace(',', '').lower().split()
                if set(title_to_compare) <= set(current_movie_title):
                    result.append(i)
            return result

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

        punctuation = ["?", ".", "!", ",", ";", ":"]
        super_pos = list(map(self.p.stem, ["fantastic", "loved", "amazing", "excellent",
                                           "outstanding", "terrific", "perfect", "delightful"]))
        super_neg = list(
            map(self.p.stem, ["terrible", "horrible", "disaster", "awful"]))
        amp_words = list(
            map(self.p.stem, ["super", "very", "really", "extremely", "entirely"]))
        negation = ["didn't", "never", "not", "no", "nothing"]
        punctuation = ["?", ".", "!", ",", ";", ":"]

        for i in range(len(preprocessed_input)):
            word = preprocessed_input[i]
            punct = [char for char in word if char in punctuation]
            if len(punct) > 0:
                word = word[:-len(punct)]
                preprocessed_input[i] = word
                for j in punct:
                    preprocessed_input.insert(i+1, j)

        pos_count, neg_count, count = 1, 1, 0
        preprocessed_input = ' '.join(
            ' '.join(preprocessed_input).split('\"')[0::2]).split()
        sentiment_stemmed = {self.p.stem(
            k): v for k, v in self.sentiment.items()}
        words = [self.p.stem(word.lower()) for word in preprocessed_input]

        flipped, amp = False, False
        for word in words:
            if word in negation:
                flipped = True
            if word in amp_words:
                amp = True
                continue
            if word in sentiment_stemmed:
                if sentiment_stemmed[word] == "pos":
                    if flipped:
                        neg_count += 1
                    else:
                        pos_count += 2 if (word in super_pos or amp) and self.creative else 1
                elif sentiment_stemmed[word] == "neg":
                    if flipped:
                        pos_count += 1
                    else:
                        neg_count += 2 if (word in super_neg or amp) and self.creative else 1
                count += 1
            punct = [char for char in word if char in punctuation]
            if len(punct) > 0:
                flipped, amp = False, False
        if ((pos_count)/(count + len(self.sentiment))) == ((neg_count)/(count + len(self.sentiment))):
            return 0
        pos_score = ((pos_count)/(count + len(self.sentiment))) * \
            self.positive_prior
        neg_score = ((neg_count)/(count + len(self.sentiment))) * \
            self.negative_prior
        if neg_score == pos_score:
            return 0
        elif self.creative and (neg_count - pos_count) > 1:
            return -2
        elif self.creative and (pos_count - neg_count) > 1:
            return 2
        elif neg_score > pos_score:
            return -1
        else:
            return 1

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

        # don't want to split here bc makes it a list
        text_joined = ' '.join(preprocessed_input)
        movies_and_sentiment = []
        movies = self.extract_titles(preprocessed_input)
        segmenters = ["but", "and", ".", ",", "!", "?"]
        pos_count = 0
        neg_count = 0
        for movie in movies:
            mov_index = text_joined.find(movie)
            start = max(text_joined.rfind(segmenter, 0, mov_index)
                        for segmenter in segmenters)
            # should change this to for loop
            if start == -1:
                start = 0
            end = len(text_joined) - 1
            for segmenter in segmenters:
                val = text_joined.find(segmenter, mov_index + len(movie))
                if val != -1:
                    end = val
                    break
            str_to_check_sent = text_joined[start:end]
            sent_val = str_to_check_sent.split()
            sentiment = self.extract_sentiment(sent_val)
            if sentiment == -1:
                neg_count += 1
            if sentiment == 1:
                pos_count += 1
            movies_and_sentiment.append([movie, sentiment])
        more_pos = False
        if pos_count > neg_count:
            more_pos = True
        flip_words = ["but", "but not", "not"]
        for val in movies_and_sentiment:
            if val[1] == 0:
                if more_pos and not any([x in str_to_check_sent for x in flip_words]):
                    val[1] = 1
                if more_pos and any([x in str_to_check_sent for x in flip_words]):
                    val[1] = -1
                if not more_pos and not any([x in str_to_check_sent for x in flip_words]):
                    val[1] = -1
                if not more_pos and any([x in str_to_check_sent for x in flip_words]):
                    val[1] = 1
        return [(x, y) for x, y in movies_and_sentiment]

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
        possible = set()
        def get_title_given_index(
            idx): return self.titles[idx][0].split('(')[0].strip()

        def similar(a, b): return SequenceMatcher(None, a, b).ratio()
        data = [(similar(get_title_given_index(i).lower(), title.lower()), i)
                for i, _ in enumerate(self.titles)]
        result = {overlap: [index for key, index in data if key == overlap]
                  for overlap in set(k for k, v in data)}

        for i in range(len(self.titles)):
            movie_name = get_title_given_index(i)
            lensum = len(title) + len(movie_name)
            for j in range(max_distance):
                levenshtein_distance = 1 - (j/lensum)
                if levenshtein_distance > 0.5:
                    possible.add(levenshtein_distance)
        l = [v for k, v in result.items() if k in possible]
        return sum(l, [])

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
        movies = [(i, title.replace(',', '').rsplit('(', 1)[0].strip(), title.replace(',', '').rsplit(
            '(', 1)[-1].replace(')', '')) for i, (title, _) in enumerate(self.titles) if i in candidates]
        ordinals = ['first', 'second', 'third', 'fourth', 'fifth']

        for i, ordinal in enumerate(ordinals):
            if ordinal in clarification:
                return [candidates[i]]

        if len(clarification) == 1 and clarification.isdigit():
            return [candidates[int(clarification)-1]]

        age_map = {'most recent': 1, 'newest': 1,
                   'oldest': 0, 'least recent': 0}
        if clarification in age_map:
            year_sorted = sorted(movies, key=lambda x: x[2])
            return [year_sorted[-1][0]] if age_map[clarification] else [year_sorted[0][0]]

        result = []
        for i, movie, year in movies:
            to_search = ' '.join([movie, year]).title()
            counts = [to_search.count(word.title())
                      for word in clarification.split()]
            result.append((sum(counts), i))

        return [sorted(result)[-1][1]]
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

        binarized_ratings = np.where(
            ratings > threshold, 1, np.where(ratings != 0, -1, 0))

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
        if np.linalg.norm(u) == 0 or np.linalg.norm(v) == 0:
            similarity = 0
        else:
            similarity = np.dot(u, v) / (np.linalg.norm(u)*np.linalg.norm(v))
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

        sims = [((i, j), self.similarity(ratings_matrix[i], ratings_matrix[j]))
                for i in range(ratings_matrix.shape[0]) for j in np.nonzero(user_ratings)[0]]
        sims = [(x, np.multiply(user_ratings[y], d)) for (
            x, y), d in sims if np.count_nonzero(np.isin((x, y), np.nonzero(user_ratings))) == 1]
        d = defaultdict(list)
        for x, y in sims:
            d[x] += [y]
        d = {np.sum(v): k for k, v in d.items()}
        recommendations = [item for _, item in sorted(
            d.items(), reverse=True)[:k]]

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
         Our chatbot takes in movies from user input and does the following:
        
          - Update user rating based on user input
          - Look into user rating in order to give recommendations 
          - Contains a recommendation system that activates when user lists five or more movies in the database
          - Deals with arbitrary responses / failing gracefully when there is no movie detected.
          - The chatbot performs multi-movie sentiment analysis
          - If the user enters a movie that isn't in the database, a clarification message prompts the user.
          - If the chatbot finds movies with similar titles, it asks to clarify
          - Returns the movie and sentiment to the user in a naturalistic, human sounding manner
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
