# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util, random, json

import numpy as np
import heapq
import re

from porter_stemmer import PorterStemmer

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        self.name = "April"

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings("data/ratings.txt")
        self.sentiment = util.load_sentiment_dictionary("data/sentiment.txt")

        # movie title: id/index
        self.title_cache = {}
        # index -> preprocessed title data in form (titles, year)
        self.title_data = {}

        # possible articles
        self.articles = ["The", "A", "An", "Le", "Les", "La", "El", "En", "Il", "L'", "Die", "Das"]

        # Preprocess title data for use in search
        for idx, entry in enumerate(self.titles):
            entry_title_year = entry[0]
            entry_titles = self.get_all_titles(entry_title_year)
            entry_year = self.extract_movie_year(entry_title_year)

            self.title_data[idx] = (entry_titles, entry_year)

            title = self.extract_english_title(entry_title_year)
            self.title_cache[title.lower()] = idx

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings)

        # List of user rated movies
        self.user_ratings = np.zeros(len(self.ratings))
        # Set of movie (indices) rated by the user. We use a set to ensure
        # we get five distinct data points before giving recommendations.
        self.num_recent_reviews = 0
        self.reviewed_movies = set()
        self.recommendations = None
        self.recommending = False

        self.cur_sentiment = None
        self.disambiguating = False
        self.ambiguous_movies = None

        self.confirming = False
        self.confirm_movie = None

        # Constants
        self.responses = json.load(open("deps/responses.json"))
        self.PROMPT = '> '
        self.BOT_PROMPT = '\001\033[96m\002%s> \001\033[0m\002' % self.name # Taken from repl.py



    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        greeting_message = "Um hi I'm April Ludgate, I'm only here because I get college credit for this. Tell me about your movie taste, or don't. I don't really care."
        return greeting_message

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        goodbye_message = "Bye I guess."
        return goodbye_message

    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################
    def generate_recommendation(self):
        rec = self.titles[self.recommendations.pop(0)][0]
        response = '\n'.join([
                     random.choice(self.responses["recommendation"]["strs"]).format(rec),
                     "Would you like to hear another recommendation?"
                   ])
        return response
    
    def add_user_rating(self, response, movie_idx, sentiment):
        self.user_ratings[movie_idx] = sentiment
        self.reviewed_movies.add(movie_idx)

        if len(self.reviewed_movies) - self.num_recent_reviews >= 5:
            # Recommend a movie because we received 5 new reviews.
            print(self.BOT_PROMPT + response) # Print explicit confirmation of movie review

            print(' '.join([
                    random.choice(self.responses["recommending"]["strs"]),
                    random.choice(self.responses["recommending_2"]["strs"])
                  ]))

            # Start determining recommendations
            self.recommending = True
            self.recommendations = self.recommend(self.user_ratings, self.ratings)
            response = self.generate_recommendation()

            self.num_recent_reviews = len(self.reviewed_movies)
        else:
            # Add request for more reviews because we aren't recommending.
            response = ' '.join([
                response,
                random.choice(self.responses["request_more_reviews"]["strs"])
            ])
        return response


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
        if self.creative:
            response = "I processed {} in creative mode!!".format(line)
            
        affirmatives = ["yes", "yeah", "ok", "alright", "sure", "okay"]
        negatives = ["no", "nah", "nay"]
        if self.recommending:
            # Recommended a movie already, now in recommendation flow
            line = line.lower()
            if any(word in line for word in affirmatives):
                if len(self.recommendations) == 0:
                    response = "Sorry, I'm out of recommendations (and caring). Enter :quit to exit."
                else:
                    response = self.generate_recommendation()
            elif any(word in line for word in negatives):
                response = "Provide more movie reviews or just leave already (enter :quit)."
                self.recommending = False
            else:
                response = "I didn't catch that because I wasn't listening. Do you want more recommendations?"
            return response
        
        if self.disambiguating:
            movies = self.disambiguate(line, self.ambiguous_movies)
            num_movies = len(movies)
            if num_movies == 1:
                # Potential successful disambiguation, need to confirm
                self.confirming = True
                self.disambiguating = False
                self.confirm_movie = movies[0]
                title = self.titles[movies[0]][0]
                response = random.choice(self.responses["confirm_movie"]["strs"]).format(title)
            elif num_movies > 1:
                # Still unclear which movie, so continue disambiguating
                movie_titles = [self.titles[idx][0] for idx in movies]
                movie_titles_str = '[' + ", ".join(movie_titles) + ']'
                response = random.choice(self.responses["clarify_title"]["strs"]).format(line, movie_titles_str)
            else:
                # No movies are left, say we could not find a movie
                self.disambiguating = False
                response = ' '.join([
                    random.choice(self.responses["not_found"]["strs"]).format(line),
                    random.choice(self.responses["request_more_reviews"]["strs"])
                ])
            return response

        if self.confirming:
            # Happens if we need to confirm movie after disambiguation or after spell-correcting
            # 'line' should be an affirmative or a negative
            line = line.lower()
            title = self.titles[self.confirm_movie][0]
            if any(word in line for word in affirmatives):
                self.confirming = False
                confirmation_responses = self.responses["confirm_pos"] if self.cur_sentiment > 0 else self.responses["confirm_neg"]
                response = random.choice(confirmation_responses["strs"]).format(title)
                response = self.add_user_rating(response, self.confirm_movie, self.cur_sentiment)
            elif any(word in line for word in negatives):
                self.confirming = False
                response = "Sorry, rate a different movie."
            else:
                response = f"Sorry, I didn't catch that because I don't care. You wanted to review \"{title}\"?"
            return response

        preprocessed_input = self.preprocess(line)
        titles = self.extract_titles(preprocessed_input)
        if len(titles) != 1:
            # More than one title was provided in quotes,
            # or there were extra double quotes.
            response = random.choice(self.responses["catchalls"]["strs"])
        else:
            title = titles[0]
            movie_idxs = self.find_movies_by_title(title)
            # Identify the sentiment
            sentiment = self.extract_sentiment(preprocessed_input)
            self.cur_sentiment = sentiment
            if sentiment == 0:
                # Unknown sentiment
                response = random.choice(self.responses["clarify_sentiment"]["strs"]).format(title)
                return response

            # Check for the movie in our database
            num_found_movies = len(movie_idxs)
            if num_found_movies == 0:
                # Could not find movie, so look for nearest possible movies
                movie_idxs = self.find_movies_closest_to_title(title)
                num_found_movies = len(movie_idxs)
                if num_found_movies == 1:
                    # Found potential spell-corrected movie, need to confirm
                    title_year = self.titles[movie_idxs[0]][0]
                    title = self.extract_english_title(title_year)
                    self.confirming = True
                    self.confirm_movie = movie_idxs[0]
                    response = random.choice(self.responses["confirm_movie"]["strs"]).format(title_year)
                    return response
            if num_found_movies == 0:
                # Movie was not found, even after spell-correcting
                response = ' '.join([
                    random.choice(self.responses["not_found"]["strs"]).format(title),
                    random.choice(self.responses["request_more_reviews"]["strs"])
                ])
            elif num_found_movies > 1:
                # Ask the user to disambiguate which movie
                self.disambiguating = True
                self.ambiguous_movies = movie_idxs
                movie_titles = [self.titles[idx][0] for idx in movie_idxs]
                movie_titles_str = '[' + ", ".join(movie_titles) + ']'
                response = random.choice(self.responses["clarify_title"]["strs"]).format(title, movie_titles_str)
            else:
                # Sentiment and movie found, use explicit confirmation
                confirmation_responses = self.responses["confirm_pos"] if sentiment > 0 else self.responses["confirm_neg"]
                response = random.choice(confirmation_responses["strs"]).format(title)
                
                # Tracking sentiment on movie reviews
                movie_idx = movie_idxs[0]
                response = self.add_user_rating(response, movie_idx, sentiment)

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
        # Extract all titles enclosed by double quotes
        # format: "XXXXXX"
        titles = ["%s" % m for m in re.findall("\"(.*?)\"", preprocessed_input)]

        if not self.creative:
            return titles

        # Creative mode: try to find any other titles
        # This shouldn't duplicate the previous step since the double quotes would preclude detection
        words = preprocessed_input.split(" ")

        # consider all possible substrings for movies
        for i in range(len(words)):
            for j in range(i, len(words)):
                title = (" ".join(words[i:j+1]))
                
                if title.lower() in self.title_cache and title not in titles:
                    titles.append(title)
                # trim punctuation if needed
                elif title[-1] in "!.?":
                    no_punc = title[:-1]
                    if no_punc.lower() in self.title_cache and title not in titles:
                        titles.append(no_punc)

        return titles

    def move_articles_to_front(self, string):
        for article in self.articles:
            end = ", " + article
            if string.endswith(end):
                string = article + " " + string[: -len(end)]
        
        return string.strip()

    def extract_movie_year(self, movie_title):
        if not "(" in movie_title:
            return ""

        last_opening_parenth = movie_title.rindex("(")
        return movie_title[last_opening_parenth + 1 : -1]


    def extract_english_title(self, movie_title):
        title_string = movie_title

        # remove anything after the first opening parenthesis
        if "(" in title_string:
            first_opening_parenth = title_string.index("(")
            title_string = title_string[0:first_opening_parenth].strip()

        return self.move_articles_to_front(title_string)
    
    def extract_alternate_titles(self, movie_title):
        if not "(" in movie_title:
            return []

        # remove English title
        first_opening_parenth = movie_title.index("(")
        movie_title = movie_title[first_opening_parenth:].strip()

        possible_akas = ["a.k.a.", "aka"]

        output = []
        # format: (XXXXXX)
        for m in re.findall("\((.*?)\)", movie_title):
            s = "%s" % m

            # remove any akas
            for aka in possible_akas:
                if s.startswith(aka):
                    s = s[len(aka):]
                    break
            
            # don't add years as alt titles
            if s.isnumeric():
                continue

            s = self.move_articles_to_front(s)
            output.append(s)

        return output
    
    def get_all_titles(self, title):
        titles = [self.extract_english_title(title)]
        titles.extend(self.extract_alternate_titles(title))

        # convert to lowercase so we can catch bad capitalization
        # make it a set so search is faster
        titles = set(t.lower() for t in titles)

        return titles
    
    def find_disambiguate_title_matches(self, title):
        """
        Returns all movies containing the tokens in `title` as a sublist 
        (i.e. consecutively and in the same order)
        """
        matches = set()
        for idx in range(len(self.titles)):
            # format: title + separator
            if len(re.findall(f"{title}[^\w]", self.titles[idx][0])) > 0:
                matches.add(idx)

        return matches

    def find_movies_by_title(self, title):
        """Given a movie title, return a list of indices of matching movies.

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
        output = set()
        query_titles = self.get_all_titles(title)
        possible_query_year = self.extract_movie_year(title)

        # for all the title entries, check if they match the query
        for idx in range(len(self.titles)):
            entry_titles, entry_year = self.title_data[idx]

            year_matches = (
                entry_year == possible_query_year
                if len(possible_query_year) > 0
                else True
            )

            if len(query_titles.intersection(entry_titles)) > 0 and year_matches:
                output.add(idx)
        
        # allow for disambiguation if we are in creative mode
        if self.creative:
            output.update(self.find_disambiguate_title_matches(title))

        return list(output)

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
        negation_words = ["didn't", "don't", "never", "not", "won't", "wouldn't"]

        p = PorterStemmer()
        stemmed_sentiment = {p.stem(k, 0, len(k) - 1): v for k, v in self.sentiment.items()}
        def get_word_sentiment(word):
            word = p.stem(word, 0, len(word) - 1)
            if word not in stemmed_sentiment:
                return 0
            return 1 if stemmed_sentiment[word] == 'pos' else -1
        
        # make tokenized_text
        tokenized_text = preprocessed_input
        if (not self.creative):
            title = ''.join(self.extract_titles(preprocessed_input))
            tokenized_text = preprocessed_input.replace(title, "[TITLE]")
            while (True):
                index = tokenized_text.find('"')
                if (index == -1): break
                tokenized_text = tokenized_text.replace('"', "")
        
        # remove token
        token_index = tokenized_text.find("[TITLE]")
        text_before_token = tokenized_text[:token_index]
        text_after_token = tokenized_text[token_index+7:]
        
        words_before_token = text_before_token.split()
        words_after_token = text_after_token.split()
        words = []
        for word in words_before_token:
            words.append(word)
        for word in words_after_token:
            words.append(word)

        # calculate sum
        negation_word_present = False
        running_sum = 0
        for word in words:
            sentiment_score = get_word_sentiment(word)
            running_sum += sentiment_score
            if word in negation_words:
                negation_word_present = True

        # KATY: slide says only before next punc mark? necessary here?
        if negation_word_present:
            if (running_sum == 0): 
                running_sum = -1
            else: running_sum *= -1

        # return value
        if running_sum == 0: return 0
        elif running_sum > 0: return 1
        else: return -1

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
        result = []
        
        # get titles
        titles = self.extract_titles(preprocessed_input)
        
        # tokenized text
        tokenized_text = preprocessed_input
        for title in titles:
            title = ''.join(title)
            tokenized_text = tokenized_text.replace(title, "[TITLE]")
        
        # remove any quotation marks
        while (True):
            index = tokenized_text.find('"')
            if (index == -1): break
            tokenized_text = tokenized_text.replace('"', "")
        
        # process each title
        last_rating = None
        num_titles = len(titles)
        for i in range(num_titles):
            # split text 
            title = titles[i]
            cur_title_index = tokenized_text.find("[TITLE]")
            
            text_to_process = tokenized_text[0:cur_title_index+7]
            if (i == num_titles-1):
                text_to_process = tokenized_text
            
            # get cur_rating
            cur_rating = self.extract_sentiment(text_to_process)
            if (last_rating != None and cur_rating == 0):
                cur_rating = last_rating
            
            # append to result
            result.append((title, cur_rating))
            
            # update for next pass
            tokenized_text = tokenized_text[cur_title_index+7:]
            last_rating = cur_rating
            
        return result
            
            
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
        # List of movie indices
        within_max_distance = list()
        title = title.lower()
        for i in range(len(self.titles)):
            movies, year = self.title_data[i]
            distances = list()
            for movie_title in movies:
                # Compare over every title in every language
                M = len(title)
                N = len(movie_title)
                dp = [[0] * (N + 1) for _ in range(M + 1)]
                for x in range(M + 1):
                    dp[x][0] = x
                for y in range(N + 1):
                    dp[0][y] = y

                for x in range(1, M + 1):
                    for y in range(1, N + 1):
                        if title[x - 1] == movie_title[y - 1]:
                            dp[x][y] = dp[x - 1][y - 1]
                        else:
                            dp[x][y] = min(dp[x - 1][y] + 1,
                                           dp[x][y - 1] + 1,
                                           dp[x - 1][y - 1] + 2)

                distances.append(dp[-1][-1])

            if min(distances) <= max_distance:
                # One of the titles is within max_distance of the title
                within_max_distance.append((i, min(distances)))

        if len(within_max_distance) == 0:
            # No matches
            return list()

        # Sort by lowest edit distance
        within_max_distance.sort(key=lambda pr: pr[1])
        lowest_distance = within_max_distance[0][1]

        # Return all movies that match the lowest edit_distance
        return list(map(lambda pr: pr[0], filter(lambda pr: pr[1] == lowest_distance, within_max_distance)))

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
        clarification = clarification.lower()

        # All candidates whose titles (and/or year) contain the clarification as substring
        full_string = [candidate for candidate in candidates if clarification in self.titles[candidate][0].lower()]

        # All candidates whose titles (NOT year) contain the clarification as substring
        title_only = [candidate for candidate in candidates if clarification in self.extract_english_title(self.titles[candidate][0]).lower()]

        if len(full_string) == 0:
            return title_only
        elif len(title_only) == 0:
            return full_string
        else:
            return full_string if len(full_string) < len(title_only) else title_only
        

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

        binarized = np.where(
            ratings == 0,
            0,
            np.where(
                ratings > threshold, 1, np.where(ratings <= threshold, -1, ratings)
            ),
        )

        return binarized

    def similarity(self, u, v):
        """Calculate the cosine similarity between two vectors.

        You may assume that the two arguments have the same shape.

        :param u: one vector, as a 1D numpy array
        :param v: another vector, as a 1D numpy array

        :returns: the cosine similarity between the two vectors
        """
        u_norm = np.linalg.norm(u)
        v_norm = np.linalg.norm(v)

        # don't divide by 0!
        if u_norm == 0 or v_norm == 0:
            return 0

        return np.dot(u, v) / (u_norm * v_norm)

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
        NUM_MOVIES = len(user_ratings)

        if not creative:
            heap = []

            # Delete the columns of all unrated movies to reduce matrix size
            unrated_movies = np.nonzero(np.where(user_ratings != 0,
                                                 0,
                                                 1)
                                       )[0]
            reduced_matrix = np.delete(ratings_matrix, unrated_movies, axis=0)

            # Array with size equal to row size of reduced_matrix
            x = np.delete(user_ratings, unrated_movies)
            for movie_i in range(len(unrated_movies)):
                # Skip any movies the user already has rated
                if user_ratings[movie_i] != 0:
                    continue
                
                # Rating calculation using numpy functions
                # Calculate the cosine similarity of movie_i with every movie in the matrix
                # Equation for cosine similarity:
                # cosine_sum(u, i) = np.dot(u, i) * (1 / (norm(u) * norm(i)))

                # Dot product of movie_i with every movie in the ratings matrix
                dot_products = reduced_matrix.dot(ratings_matrix[movie_i])

                # Norm of every movie in the ratings matrix
                reduced_matrix_norms = np.linalg.norm(reduced_matrix, axis=1)

                # Norm of movie_i
                movie_i_norm = np.linalg.norm(ratings_matrix[movie_i])
                
                # Equivalent to norm(u) * norm(i) for every movie in reduced matrix with movie_i
                multiplied_norms = movie_i_norm * reduced_matrix_norms
                # We use reciprocals (i.e. 1 / norm(u) * norm(i)) to avoid division by zero errors
                with np.errstate(divide="ignore"): # Removes the divide by zero warning
                    reciprocals = np.where(multiplied_norms == 0, 0, 1 / multiplied_norms) 
                
                # Calculating cosine similarity of movie_i with every movie
                cosine_sims = np.multiply(dot_products, reciprocals)

                # Rating is equal to the sum of the cosine similarity of
                # movie_i and movie_j times user_rating_j for j in len(reduced_matrix)
                rating = cosine_sims.dot(x)

                # Python heaps are min heaps, so we need to negate to return the max
                heap.append((-rating, movie_i))

            heapq.heapify(heap)
            recommendations = [heapq.heappop(heap)[1] for _ in range(k)]

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
        debug_info = "debug info"
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
        I can recommend movies to you if you tell me your feelings about
        a few of them. You can hit enter once you're done typing so I can 
        respond. Make sure to enclose the movie names in double quotes 
        if you're running in basic mode. 
        """


if __name__ == "__main__":
    print("To run your chatbot in an interactive loop from the command line, " "run:")
    print("    python3 repl.py")
