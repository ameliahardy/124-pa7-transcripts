# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re
import porter_stemmer
import random
from collections import deque


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'cowboybot'

        self.creative = creative
        self.no_recs = 0
        # responses
        self.cowboy_pos = ["Well, yeehaw! You sure seemed to like {}!",
                           "{} is just dandy!",
                           "There ain't a film more swell than {}!",
                           "{} was more fun than my old horse, Friday!",
                           "{} pairs great with an ice-cold sarsaparilla.",
                           "I had a hoot watching {} with my ranching buddies."
                           ]
        self.cowboy_neutral = ["Eh, I guess I seen better than {}.",
                               "Ain't much to talk about {}, now is there?",
                               "{} ain't my first pick either, partner.",
                               "I don't remember much about {} either, pal.",
                               "{} isn't good, but it sure ain't the worst."
                               "{} was a bit of a snoozer, but maybe that's just me."
                               ]
        self.cowboy_neg = ["{} was more vile than a snake in my boot!",
                           "{} has got to be the worst film I ever did see.",
                           "Nothin' worse than {} in the whole wild west."
                           "I'd rather be caught in a shootout than see {} again.",
                           "I didn't care for {} too much either, partner."
                           "My old buddy Buffalo Bill didn't like {} either."
                           ]
        self.cowboy_more = ["Let's hear some more.", "What's next?", "Tell me somethin' else.", "Tell me another, partner.",
                            "What else you got?", "What's next, partner?", "Gimme another.", "Hit me with another!", "Let me hear another."]

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.strong = {"enjoi": 1, "terribl": -1}
        self.negation = ["didn't", "never", "not", "don't"]
        self.intense = ["terribl", "love", "hate", "really"]
        self.user_ratings = []
        self.user_titles = []  # it's the indices of movies the user rated
        self.done = 0
        self.recs = []

        # Disambiguation stuff!
        self.disambiguation_mode = False
        self.disambig_list = []
        self.saved_line = ""
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
            greeting_message = "Howdy, partner! I'm CowboyBot, the best fella for movie recommendations in the whole Wild West. Gimme a movie and how ya feel about it, and we'll get this rodeo started!"
        else:
            greeting_message = "How can I help you?"

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
            goodbye_message = "Well, partner, it's time for me to ride off into the sunset. Till next time! Yeehaw!"
        else:
            goodbye_message = "Have a nice day!"

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

        # Creative mode responses to user preferences

        # The 'done' flag signals whether or not the chatbot has compiled the list of recs. This
        # block of code allows the user to ask for another rec one by one if there are any left.
        response = ""

        if self.done:
            if self.no_recs:
                return "See you next time. Type ':quit' to quit."
            if line.lower() == "yes":
                if len(self.recs) > 0:
                    response = "Try this one: " + self.recs.pop(0)[0] + ". "
                    response += "Want another recommendation, partner? Type YES or NO."
                else:
                    self.no_recs = 1
                    response = "Ok, that's all I got. Type ':quit' to quit."
                    return response

            elif line.lower() == "no":
                self.no_recs = 1
                response = "Ok, that's all I got. Type ':quit' to quit."
                return response
            else:
                if self.creative:
                    response += "Type YES or NO, partner! Want another rec?"
                else:
                    response += "Type YES or NO."

                return response

        response = ""

        if self.creative:
            # print(found)

            # The disambiguation_mode flag signals whether the chatbot is currently attempting to disambiguate
            # which movie the user is referring to.
            if self.disambiguation_mode:
                results = self.disambiguate(line, self.disambig_list)
                if len(results) > 1:  # Need to disambiguate more
                    response = "Which of these did you mean?"
                    for index in results:
                        response += "\n" + str(self.titles[index][0])
                    response += "?"
                    self.disambiguation_mode = True
                    self.disambig_list = results
                    return response

                elif len(results) < 1:
                    # Ask again
                    response = "I didn't understand that! Which of these did you mean?"
                    for index in self.disambig_list:
                        response += "\n" + str(self.titles[index][0])
                    return response

                else:  # Successfully disambiguated
                    preprocessed = self.preprocess(self.saved_line)
                    found = results
                    matches = [self.titles[found[0]][0]]

                    # reset
                    self.saved_line = ""
                    self.disambiguation_mode = False
                    self.disambig_list = []

            else:  # regular, non disambiguating path
                matches = self.extract_titles(line)
                # print(matches)
                preprocessed = self.preprocess(line)
                if len(matches) == 0:
                    return "Please try again, I don't understand."
                elif len(matches) > 1:  # Multiple-movie input
                    #print("im processing multiple movies")
                    sentiments = self.extract_sentiment_for_movies(
                        preprocessed)
                    # print(sentiments)
                    for movie, sent in sentiments:
                        if sent == 1:
                            phrase = random.choice(self.cowboy_pos)
                            response += phrase.format(movie) + " "
                            self.cowboy_pos.remove(phrase)
                        elif sent == 0:
                            phrase = random.choice(self.cowboy_neutral)
                            response += phrase.format(movie) + " "
                            self.cowboy_neutral.remove(phrase)
                        else:
                            phrase = random.choice(self.cowboy_neg)
                            response += phrase.format(movie) + " "
                            self.cowboy_neg.remove(phrase)
                else:
                    found = self.find_movies_by_title(matches[0])

                    # Movie unclear or not found

                    if not found:
                        # Try spellcheck
                        candidates = self.find_movies_closest_to_title(
                            matches[0])
                        response = "Did you mean one of these?"
                        for candidate in candidates:
                            response += "\n" + str(self.titles[candidate][0])
                        self.disambiguation_mode = True
                        self.disambig_list = candidates
                        self.saved_line = line
                        return response

                    elif (len(found) > 1):  # start disambiguation
                        response = "Which of these did you mean?"
                        for index in found:
                            response += "\n" + str(self.titles[index][0])
                        self.disambiguation_mode = True
                        self.disambig_list = found
                        self.saved_line = line
                        return response

            #print("matches", matches, len(matches))
            if len(matches) == 1:
                sent = self.extract_sentiment(preprocessed)
                self.user_ratings.append(sent)
                self.user_titles.append(found[0])
                movie = matches[0]
                if sent == 1:
                    phrase = random.choice(self.cowboy_pos)
                    response += phrase.format(movie) + " "
                    self.cowboy_pos.remove(phrase)
                    print(self.cowboy_pos)
                elif sent == 0:
                    phrase = random.choice(self.cowboy_neutral)
                    response += phrase.format(movie) + " "
                    self.cowboy_neutral.remove(phrase)
                else:
                    phrase = random.choice(self.cowboy_neg)
                    response += phrase.format(movie) + " "
                    self.cowboy_neg.remove(phrase)

            # Sufficient information collected
            if len(self.user_ratings) == 5:
                self.done = 1
                self.user_ratings = self.user_ratings
                temp = self.recommend(self.user_ratings, self.ratings)
                for mov_index in temp:
                    self.recs.append(self.titles[mov_index])
                response += " Well, here ya are, partner!\n"
                response += str(self.recs.pop(0)[0])
                if len(self.recs) > 0:
                    response += " Want another recommendation, partner? Type YES or NO."
                else:
                    self.no_recs = 1
            else:
                choice = random.choice(self.cowboy_more)
                response += " " + choice
                self.cowboy_more.remove(choice)

        else:  # starter mode
            matches = self.extract_titles(line)
            preprocessed = self.preprocess(line)

            if len(matches) == 0:  # arbitrary input place
                return "Please try again, I don't understand."

            found = self.find_movies_by_title(matches[0])

            # Movie was unclear or not found
            if (len(found) == 0):
                return "Please try again, I don't understand."

            sent = self.extract_sentiment(preprocessed)
            self.user_ratings.append(sent)
            self.user_titles.append(found[0])
            movie = matches[0]
            if sent == 1:
                phrase = random.choice(self.cowboy_pos)
                response += phrase.format(movie) + " "
                self.cowboy_pos.remove(phrase)
            elif sent == 0:
                phrase = random.choice(self.cowboy_neutral)
                response += phrase.format(movie) + " "
                self.cowboy_neutral.remove(phrase)
            else:
                phrase = random.choice(self.cowboy_neg)
                response += phrase.format(movie) + " "
                self.cowboy_neg.remove(phrase)

            # Sufficient information collected
            if len(self.user_ratings) == 5:
                self.done = 1
                self.user_ratings = self.user_ratings
                temp = self.recommend(self.user_ratings, self.ratings)
                for mov_index in temp:
                    self.recs.append(self.titles[mov_index])
                response += "I think you're gonna like this! Try watching "
                response += str(self.recs.pop(0)[0])
                if len(self.recs) > 0:
                    response += " \n Would you like another recommendation? Type YES or NO."
                else:
                    self.no_recs = 1

            else:
                choice = random.choice(self.cowboy_more)
                response += " " + choice
                self.cowboy_more.remove(choice)

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
        matches = []
        pattern = '\"([^""]*)\"'
        matches = re.findall(pattern, preprocessed_input)
        return matches

    def process_db(self):
        titles_db = []
        for i in range(len(self.titles)):
            db_title = re.split('\(|\)', self.titles[i][0])
            db_title = list(filter(None, db_title))
            db_title[0] = re.sub(r'[^\w\s\(\)0-9]', '', db_title[0])
            for i in range(1, len(db_title)):
                db_title[i] = re.sub('a.k.a. ', "", db_title[i])
            titles_db.append(db_title)
        return titles_db

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
        partial_match = []
        found = []
        title = re.split('\(|\)', title)
        title = list(filter(None, title))
        #print("399", title)
        title[0] = re.sub(r'[^\w\s\(\)0-9]|', '', title[0])
        #print("401", title[0])
        title_set = set(title[0].strip().split())
        #print("403", title_set)
        titles_db = self.process_db()
        for x in range(len(titles_db)):
            '''
            db_title = re.split('\(|\)', self.titles[x][0])
            db_title = list(filter(None, db_title))
            db_title[0] = re.sub(r'[^\w\s\(\)0-9]', '', db_title[0])
            '''
            db_title = titles_db[x]
            # print(db_title)
            # get actual title
            for i in range(len(db_title)):
                db_title[i] = re.sub(r'[^\w\s\(\)0-9]', '', db_title[i])
                db_title_set = set(db_title[i].strip().split())
                if title_set == db_title_set:
                    if title[-1] == db_title[-1] or len(title) == 1:
                        found.append(x)
                        break
            # else:
            # build for regex
            if len(title) == 1:
                title_ = " " + title[0].strip() + " "
                db_title_ = " " + db_title[0].strip() + " "
                if title_ in db_title_:
                    partial_match.append(x)

        # if found:
        #     if len(found) > 1 and partial_match:
        #         found = found.extend(partial_match)
        #         print(found)
        # else:
        #     found = partial_match
        if self.creative:
            return list(set(found + partial_match))
        else:
            return found

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
        tokens = re.split('\"[0-9\w\s\(\)]+\"', preprocessed_input)
        tokens = "".join(list(filter(None, tokens)))
        p = porter_stemmer.PorterStemmer()
        words = tokens.split()
        output = ""
        word = ''
        for c in tokens:
            if c.isalpha():
                word += c.lower()
            else:
                if word:
                    output += p.stem(word, 0, len(word) - 1)
                    word = ''
                output += c.lower()

        score = 0
        flag = 1
        emph = 0
        if '!' in output:
            emph = 1
        clauses = re.split('[,\.\!\?]', output)
        for clause in clauses:
            for word in clause.split():
                if word in self.intense:
                    emph = 1
                if word in self.negation:
                    flag = -1
                if word in self.sentiment:
                    if self.sentiment[word] == "neg":
                        score += -1 * flag
                    else:
                        score += 1 * flag
                if word in self.strong:
                    score += self.strong[word] * flag
            flag = 1
        if self.creative:
            multiplier = 1
            if emph == 1:
                multiplier = 2
            if score > 0:
                return multiplier * 1
            elif score < 0:
                return multiplier * -1
            else:
                return multiplier * 0
        else:
            if score > 0:
                return 1
            elif score < 0:
                return -1
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

        clauses = re.split(" but | yet | although ", preprocessed_input)
        sentiments = []
        prev_sentiment = 0
        for clause in clauses:
            titles = re.split(" and | or | also ", clause)
            for part in titles:
                title = self.extract_titles(part)
                sentiment = self.extract_sentiment(part)
                if sentiment != 0:
                    prev_sentiment = sentiment
                else:
                    for word in self.negation:
                        if word in part:
                            prev_sentiment = -1 * prev_sentiment
                sentiments.append((title[0], prev_sentiment))
        return sentiments

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

        distances = dict()
        title = title.split("(")[0].strip().lower()
        for index, movie in enumerate(self.titles):
            movie_title = movie[0].split("(")[0].strip().lower()
            #print("new movie", index, movie_title)
            if abs(len(movie_title) - len(title)) > max_distance:
                continue
                # There is no edit distance between these titles that would be less than the maximum edit distance
            else:
                # ed = self.editDistance(title, movie_title, len(title), len(movie_title), max_distance)
                ed = self.minDistance(title, movie_title, max_distance)
                #print("Edit distance", index, ed, abs(len(movie_title) - len(title)))
                if ed <= max_distance:
                    if ed not in distances:  # instantiate
                        distances[ed] = []
                    distances[ed].append(index)

        # find the lowest edit distance that was found
        i = sorted(distances.keys())
        # print(i)
        if i:
            return distances[i[0]]
        else:
            return []

    # CITATION: The minDistance() function comes from
    # https://leetcode.com/problems/edit-distance/solutions/3233545/python3-56-ms-faster-than-99-95-of-python3/?languageTags=python3.
    def minDistance(self, word1: str, word2: str, max_distance: int) -> int:
        if word1 == word2:
            return 0
        if len(word1) == 0 or len(word2) == 0:
            return max(len(word1), len(word2))
        w1 = list(word1)
        w2 = list(word2)
        num = 0
        queue = deque()
        queue.append((0, 0))
        visited = set()
        while len(queue) > 0:
            for _ in range(len(queue)):
                i, j = queue.popleft()
                if (i, j) in visited:
                    continue
                visited.add((i, j))
                while i < len(w1) and j < len(w2) and w1[i] == w2[j]:
                    i += 1
                    j += 1
                if i == len(w1) and j == len(w2):
                    return num
                if num > max_distance:
                    return 100  # dummy value
                queue.append((i, j + 1))
                queue.append((i + 1, j + 1))
                queue.append((i + 1, j))
            num += 1

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

        # SPECIAL CASE FOR SPELLCHECK

        if len(candidates) == 1:
            if "yes" in clarification.lower():
                return candidates

        found = []

        clarification = " " + clarification.lower().strip().replace("(",
                                                                    "").replace(")", "") + " "
        for candidate in candidates:
            title = " " + \
                self.titles[candidate][0].lower().strip().replace(
                    "(", "").replace(")", "") + " "
            if clarification in title:
                found.append(candidate)
        return found

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

        :param ratings: a (num_movies x num_users) matrix of user ratings, fromx 
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
        categorize = np.vectorize(
            lambda x: 1 if x > threshold else (0 if x == 0 else -1))
        binarized_ratings = categorize(ratings)
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

        cosine_sim = np.dot(u, v)
        norm1 = np.linalg.norm(u)
        norm2 = np.linalg.norm(v)
        if norm1 == 0 or norm2 == 0:
            return 0

        cosine_sim = cosine_sim / (norm1 * norm2)

        return cosine_sim

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
        # scores.

        # Pseudocode:
        # j = 5 (
        ########################################################################

        # Populate this list with k movie indices to recommend to the user.
        recommendations = []

        relevant_ratings = list(np.nonzero(user_ratings)[0])
        result = 0
        for row_index in range(len(ratings_matrix)):
            row = ratings_matrix[row_index, :]
            for i in range(len(relevant_ratings)):
                movie = relevant_ratings[i]
                user_rating = user_ratings[movie]
                if row_index != movie:
                    sim = self.similarity(
                        row, ratings_matrix[movie, :])
                    result += (sim * user_rating)
            '''
            for user_movie_index in range(len(user_ratings)):
                user_rating = user_ratings[user_movie_index]
                if user_movie_index != row_index and user_rating != 0:
                    # get the corresponding vector for user_movie_index within the big matrix.
                    sim = self.similarity(
                        row, ratings_matrix[user_movie_index, :])
                    result += sim * user_rating
            '''
            recommendations.append(result)
            result = 0
        #top_k = sorted(recommendations, reverse=True)
        top_k = np.argsort(recommendations)
        top_k = np.flip(top_k)
        top_k = top_k[:k]
        # np.flip(top_k)
        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        return list(top_k)

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
        Hi! I am a movie recommender chatbot. Tell me 5 movie opinions and I'll recommend you your next fave!
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
