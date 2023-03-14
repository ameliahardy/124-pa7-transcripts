# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re
import porter_stemmer
import string
p = porter_stemmer.PorterStemmer()


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        self.name = 'Cowboy Buster Suggester of the World Wide West'
        self.creative = creative

        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        keys = list(self.sentiment.keys())
        for word in keys:
            sentiment = self.sentiment[word]
            del self.sentiment[word]
            stem_word = p.stem(word)
            self.sentiment[stem_word] = sentiment

        # Binarize the movie ratings before storing the binarized matrix.
        # Ratings matrix has shape: num_movies x num_users. 
        self.ratings = self.binarize(ratings)
        self.recommendations = []
        self.user_ratings = np.zeros((len(self.titles),))
    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        greeting_message = f"Howdy pardner! I'm {self.name}. If ya tell me a film you've watched, I'll give ya a suggestion back. Yeehaw!"
        return greeting_message

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        goodbye_message = "Well, looks like it's time for me to ride off into the sunset. Yippee ki-yay!"
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

        if len(np.where(self.user_ratings != 0)[0]) == 5:
            # User has requested another recommendation. 
            return self.make_recommendation(False)

        titles = self.extract_titles(line)
        # detecting anger - creative extension
        angry_words = ['anger', 'angry', 'frustrate', 'frustrated', 'frustrating', 
                       'irritate', 'irritated', 'irritating', 'stupid', 'idiot', 'mad', 'dumb']
        for word in line.split(" "):
            if (word not in titles and word in angry_words):
                print(f"Hold you horses! Sounds like you want to get in a saloon brawl. I'm sorry if I angered you.")
        if len(titles) == 0:
            return "I don't quite yet understand your taste in movies. Tell me 'bout a film you've seen, and don't forget to lasso the title with quotes!"
        if len(titles) > 1 and not self.creative:
            return "Whoa there, cowboy! One film at a time."
        if not self.creative:
            titles = [titles[0]]
        if len(titles) > 1 and self.creative:
            print("Whoa there, looks like you've seen plenty of movies. If it's alright with you, I'll round 'em up and process 'em one by one.")
            sentiments = self.extract_sentiment_for_movies(line)

        for i in range(len(titles)):
            title = titles[i]
            movies = self.find_movies_by_title(title)
            if len(movies) > 1: 
                return f"'Fraid I lassoed more than one movie called {title}. Think you can try again and include the year it was released?"
            if len(movies) == 0:
                if not self.creative:
                    return f"Tarnation! I'm afraid I don't know much 'bout {title}. Try being more specific or tellin' me about another movie."
                close_movies = self.find_movies_closest_to_title(title)
                if len(close_movies) == 0:
                    return f"Tarnation! I'm afraid I don't know much 'bout {title}. Try being more specific or tellin' me about another movie."
                else:
                    close_titles = [self.titles[i][0] for i in close_movies]
                    if len(close_titles) == 1:
                        return f"Check that spelling pardner! Ya reckon this here's it? \n" + "\n".join(close_titles)
                    return f"Check that spelling pardner! Did ya mean to wrangle any one of these? \n" + "\n".join(close_titles)

            movie_i = movies[0]
            if self.creative and len(titles) > 1:
                sentiment = sentiments[i][1]
            else:
                sentiment = self.extract_sentiment(line)
            if sentiment <= -1:
                self.user_ratings[movie_i] = -1
                print(f"Sounds like you didn't much appreciate {title}.") 
            elif sentiment >= 1:
                self.user_ratings[movie_i] = 1
                print(f"Got it, you took a likin' to {title}.")
            elif sentiment == 0: 
                return f"I ain't too sure how you felt about {title}. Did ya like it, or not so much?"

            if len(np.where(self.user_ratings != 0)[0]) == 5:
                return self.make_recommendation(True)
            elif i != len(titles) - 1:
                continue
            else:
                return "Why don't ya tell me the name of one more film ya liked? By hook or by crook I'll find a good suggestion."

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

    def correct_format(text):
        """Returns True if line contains two quotation marks."""

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

        if (preprocessed_input.find('"') != -1 or self.creative == False):
            return re.findall(r'"(.*?)"', preprocessed_input)
        else: #find movies not in quotations marks and not capitalized properly
            candidates = []
            input_lower = preprocessed_input.lower()
            #input_lower_modified = input_lower.replace("the ", "")
            #input_lower_modified = input_lower_modified.replace("an ", "")
            #input_lower_modified = input_lower_modified.replace("a ", "")
            for i in range(len(self.titles)):
                heading = self.titles[i][0]  # 'American in Paris, An (1951)'
                has_year = re.search("\([0-9]{4}\)", heading)
                if has_year:
                    film_name = heading[:has_year.start() - 1]
                    #film_year = heading[has_year.start():]
                name = film_name #remove year
                name = name.lower()
                has_prefix_the = re.search(", the", name)
                if has_prefix_the:
                    name = 'the ' + name[:has_prefix_the.start()]
                has_prefix_an = re.search(", an", name)
                if has_prefix_an:
                    name = 'an ' + name[:has_prefix_an.start()]
                has_prefix_a = re.search(", a", name)
                if has_prefix_a:
                    name = 'a ' + name[:has_prefix_a.start()]
                if len(name) == 1: #weird edge case with 1 letter film names
                    continue
                if input_lower.find(" " + name) != -1:
                    candidates.append(string.capwords(name))
                elif input_lower.find(name) == 0:
                    candidates.append(string.capwords(name))
            return candidates

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
        title = title.title().replace('And ', 'and ').replace('In ', 'in ').replace('Of ', 'of ').replace('To ', 'to ')
        matching_movies = []
        # separate year and title
        has_year = re.search("\([0-9]{4}\)", title)
        if has_year:
            film_name = title[:has_year.start() - 1]
            film_year = title[has_year.start():]
        else:
            film_name = title
            film_year = ""

        # shift the/an/and to end
        first_space = film_name.find(' ')
        if first_space != -1:
            first_word = film_name[:first_space]
            if first_word in ['The', 'An', 'And']:
                film_name = film_name[first_space + 1:] + ', ' + first_word

        for i in range(len(self.titles)):
            heading = self.titles[i][0]  # 'American in Paris, An (1951)'
            if film_year == "":
                # remove years from data if not specified in title
                name = heading[:heading.find('(') - 1]
                if name == film_name:
                    matching_movies.append(i)
            else:
                name = heading
                if name == film_name + ' ' + film_year:
                    matching_movies.append(i)
        return matching_movies

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

        code = re.compile(r'"(.*?)"')
        words = code.sub('', preprocessed_input)
        words = re.split(r'[\s|.]', words)
        pos = 0
        neg = 0
        score = 0
        neg_count = 0

        negation_list = ["don't", "never", "didn't", "can't", "not"]
        intense_emo = ["really", "love", "hate", "extremely", "greatly", "terrible", 
                        "awful", "horrible", "horrific", "amazing", "terrific", "fantastic", "!"]
        for i in range(len(intense_emo)):
            unstemmed = intense_emo[i]
            intense_emo[i] = p.stem(unstemmed)
        intense = False
        for word in words:
            word = p.stem(word)
            if word in negation_list:
                neg_count += 1
            if self.creative:
                if word in intense_emo:
                    intense = True
            if word in self.sentiment:
                if self.sentiment[word] == 'pos':
                    pos += 1
                if self.sentiment[word] == 'neg':
                    neg += 1
        if neg != 0:
            if pos / neg > 1:
                score = 1
            elif pos / neg < 1:
                score = -1
            else:
                score = 0
        else:
            if pos > 0:
                score = 1
            else:
                score = 0
        if neg_count % 2 == 1:
            score = -1 * score
        if self.creative:
            if intense:
                score = 2 * score
        return score

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
          print(
              sentiments) // prints [("Titanic (1997)", 1), ("Ex Machina", 1)]

        :param preprocessed_input: a user-supplied line of text that has been
        pre-processed with preprocess()
        :returns: a list of tuples, where the first item in the tuple is a movie
        title, and the second is the sentiment in the text toward that movie
        """
        
        sentiments = []
        titles = self.extract_titles(preprocessed_input)
        delimiters = "and", "or", "but" #split on conjunctions
        regex_pattern = '|'.join(map(re.escape, delimiters))
        phrases = re.split(regex_pattern, preprocessed_input)
        for i in range(len(titles)):
            title = titles[i]
            sentiment = self.extract_sentiment(phrases[i])
            print(sentiment)
            if sentiment == 0:
                sentiment = sentiments[0][1] #get the sentiment from the previous clause
            sentiments.append((title, sentiment))
        return sentiments


    @staticmethod
    def editDistDP(str1, str2, m, n):
        dp = [[0 for x in range(n + 1)] for x in range(m + 1)]
        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0:
                    dp[i][j] = j
                elif j == 0:
                    dp[i][j] = i
                elif str1[i-1] == str2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(dp[i][j-1],   # Insert
                                    dp[i-1][j],      # Remove
                                    dp[i-1][j-1])    # Replace
        return dp[m][n]

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
        movies_within_max_dist = [] # (movie index, edit distance)

        # separate year and title
        has_year = re.search("\([0-9]{4}\)", title)
        if has_year:
            film_name = title[:has_year.start() - 1]
            film_year = title[has_year.start():]
        else:
            film_name = title
            film_year = ""

        # shift the/an/and to end
        first_space = film_name.find(' ')
        if first_space != -1:
            first_word = film_name[:first_space]
            if first_word in ['The', 'An', 'And']:
                film_name = film_name[first_space + 1:] + ', ' + first_word

        for i in range(len(self.titles)):
            heading = self.titles[i][0]  # 'American in Paris, An (1951)'
            if film_year == "":
                # remove years from data if not specified in title
                name = heading[:heading.find('(') - 1]
                dist = self.editDistDP(name, film_name, len(name), len(film_name))
            else:
                name = heading
                dist = self.editDistDP(name, film_name + ' ' + film_year)
            if dist <= max_distance:
                movies_within_max_dist.append((i, dist))

        if len(movies_within_max_dist) == 0:
            return []
        if len(movies_within_max_dist) ==  1: 
            return [movies_within_max_dist[0][0]]
        
        # at least two movies to consider
        movies_within_max_dist.sort(key=lambda x: x[1])
        min_dist = movies_within_max_dist[0][1]
        for m in range(1, len(movies_within_max_dist)):
            if movies_within_max_dist[m][1] > min_dist:
                return [x[0] for x in movies_within_max_dist[:m]]
        
        return [x[0] for x in movies_within_max_dist]

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
        binarized_ratings = np.zeros_like(ratings)
        for m in range(len(ratings)):
            for u in range(len(ratings[0])):
                if ratings[m][u] == 0:
                    binarized_ratings[m][u] = 0
                elif ratings[m][u] > threshold:
                    binarized_ratings[m][u] = 1
                else:
                    binarized_ratings[m][u] = -1
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
        scores = []
        seen = np.where(user_ratings != 0)[0] # indices of seen/rated movies
        unseen = np.where(user_ratings == 0)[0]
        for i in unseen:  # these are indices (i) of unseen movies
            ratings1 = ratings_matrix[i]
            score = 0
            for j in seen:  # these are indices (j) of rated movies
                ratings2 = ratings_matrix[j]
                if (np.any(ratings1) and np.any(ratings2)):
                    similarity = self.similarity(ratings1, ratings2)
                    user_score = user_ratings[j]
                    score += similarity * user_score
            scores.append((score, i))
        scores.sort(key=lambda x: x[0], reverse=True)
        top = scores[:k]
        recommendations = [x[1] for x in top]
        return recommendations
    
    def make_recommendation(self, first_rec):
        """
        Get recommendations as needed and pick one to give as a recommendation. 
        Asks user if they want more recommendations.
        """
        if len(self.recommendations) == 0:
            self.recommendations = self.recommend(self.user_ratings, self.ratings)
        rec_i = self.recommendations.pop(0)
        rec = self.titles[rec_i][0]
        prompt = "\nHow 'bout I rustle up another tip for ya partner? You can always \":quit\" if not."
        if first_rec: print("Well shucks, I reckon I got all I need to lasso ya up a good recommendation! Giddyup!")
        return f"Well, I kindly suggest you watch \"{rec}.\"" + prompt

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
        Welcome to our World-Wide-West themed Chatbot! Once you tell Cowboy Buster
        how you felt about five movies, he'll politely suggest a few movies that you might like.
        In creative mode, you should be able to speak about these movies without worrying about
        perfect spelling, quotations and/or capitalization.
        """

if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
