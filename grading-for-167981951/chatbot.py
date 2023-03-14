# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import random
import re
import string
import porter_stemmer
from heapq import nlargest


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'Dean'

        self.creative = creative

        self.ending = 'Tell me what you think of another movie.'

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        # Set process variables
        self.pos_punc = ['!', '.']
        self.neg_punc = ['.']
        self.pos_emotions = ['happi', 'joy',
                             'excit', 'hype', 'content', 'delight']
        self.neg_emotions = ['mad', 'unhappi',
                             'discont', 'sad', 'miser', 'reget']
        self.conf_words = ['Ok', 'Sure', 'So']
        self.pos_sent = ['enjoyed', 'grooved with',
                         'vibed with', 'liked']
        self.neg_sent = ["didn't like", "didnt enjoy", "disliked"]
        self.arbitrary_input = ["Sorry, I only know how to talk about movies.", "Hm, that's not really what I want to talk about right now, let's go back to movies.",
                                "Ok, got it."]

        # Parse the titles for ease of use in other funcions
        # Each element in the form: ([list of alternate titles], year)
        # Includes article handling of database titles
        self.titles_parsed = []
        for item in self.titles:
            title = item[0]
            # Get the title and year of the movie in the database
            text = re.match(
                r'((?:(?! \(([0-9]+)\)$).)*)(?: \(([0-9]+)\)[ ]?$)?', title).group(1).lower()
            year = re.match(r'(.*)(?: \(([0-9]+)\)[ ]?$)', title)
            if year != None:
                year = year.group(2)
            # Extract alternate titles
            alternates = [x[len('a.k.a. '):] if x.startswith('a.k.a. ') else x for x in re.findall(
                r'(?:\(((?!.*?\bnot\b.*?)[^()]*?)\))', text)]  # first part achieves .removeprefix functionality
            text = re.sub(
                r'(?:\(((?!.*?\bnot\b.*?)[^()]*?)\))', '', text).strip()
            alternates.append(text)
            # Handle articles
            alt_titles = []
            for elem in alternates:
                article_pattern = r".*(, (?:a|an|the|la|el|die|les|le|il|det|der|lo|l'|i))$"
                article = re.match(article_pattern, elem)
                if article != None:
                    if article.group(1) != ", l'":
                        alt_titles.append(article.group(1)[2:] + " " + re.sub(
                            r"(, (?:a|an|the|la|el|die|les|le|il|det|der|lo|l'|i))$", '', elem).strip())
                    else:
                        alt_titles.append(article.group(1)[
                            2:] + re.sub(r"(, (?:a|an|the|la|el|die|les|le|il|det|der|lo|l'|i))$", '', elem).strip())
                else:
                    alt_titles.append(elem)
            # Add to list of parsed titles
            self.titles_parsed.append((alt_titles, year))

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings)

        # Initialize user ratings
        # self.user_ratings = [0 for x in range(len(self.titles))]
        self.user_ratings = np.zeros(len(self.titles))
        self.user_recs = []
        self.movies_rated = 0
        self.recommending = False

        # Global variables for disambiguation
        self.need_disambiguate = False
        self.disambiguate_matches = []
        self.need_clarification = False
        self.title_to_be_clarified = 0
        self.previous_line = ""
        self.clarify_sentiment = False
        self.previous_title = []

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

        greeting_message = "Hey there! I'm a Dean, a chatbot whose job it is to recommend you movies. Can you tell me a movie you've seen recently?"

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
        ########################################################################
        # TODO: Implement the extraction and transformation in this method,    #
        # possibly calling other functions. Although your code is not graded   #
        # directly based on how modular it is, we highly recommended writing   #
        # code in a modular fashion to make it easier to improve and debug.    #
        ########################################################################
        if (self.recommending):
            check_yn = re.sub("[^\w]", "", line).upper().strip(
                string.punctuation)
            if (check_yn == 'YES' or check_yn == 'YEAH'):
                punc = random.choice(self.pos_punc)
                if len(self.user_recs) < 1:
                    response = "Sorry, I have reached my max capacity of recommendations!"
                    return response
                rec = '"' + string.capwords(self.titles_parsed[self.user_recs.pop(
                )][0][0]) + ' (' + self.titles_parsed[self.user_recs.pop()][1] + ')"'
                response = "Given what you told me, I think you would like {}{} Would you like more?".format(
                    rec, punc)
                return response

            else:
                self.recommending = False
                response = "Ok sounds good."
                return response

        response = ""

        # Extract title index from user input
        title_index = []
        multiple_sentiments = None
        multiple = False
        if self.clarify_sentiment:
            title_index = self.previous_title
            self.clarify_sentiment = False
        elif self.need_disambiguate:
            self.disambiguate_matches = self.disambiguate(
                line, self.disambiguate_matches)
            if len(self.disambiguate_matches) > 1:
                matches_text = ['"' + string.capwords(self.titles_parsed[idx][0][0]) +
                                ' (' + self.titles_parsed[idx][1] + ')"' for idx in self.disambiguate_matches]
                response = "Sorry, I'm not sure which movie you are referring to. Did you mean " + \
                    ' or '.join(matches_text) + "?"
                return response
            elif len(self.disambiguate_matches) == 0:
                self.need_disambiguate = False
                response = "Ok. Moving on. Tell me about another movie!"
                return response
            else:
                self.need_disambiguate = False
                line = self.previous_line
                title_index = self.disambiguate_matches
        elif self.need_clarification:
            check_yn = re.sub("[^\w]", "", line).upper()
            self.need_clarification = False
            if (check_yn == 'YES' or check_yn == 'YEAH'):
                title_index.append(self.title_to_be_clarified)
                line = self.previous_line
            else:
                response = "Ok. Tell us about something else you've watched!"
                return response
        else:
            # Extract titles from line
            potential_titles = self.extract_titles(line)
            if len(potential_titles) == 0:
                # Bot identify and response to emotions
                p = porter_stemmer.PorterStemmer()
                tokens = line.split(' ')
                for pos_token in tokens:
                    stemmed_token = p.stem(pos_token, 0, len(pos_token) - 1)
                    if (stemmed_token in self.pos_emotions):
                        response = "Oh did I make you {}? I'm glad!".format(
                            pos_token)
                        return response
                    elif (stemmed_token in self.neg_emotions):
                        response = "Sorry did I make you {}? My fault.".format(
                            pos_token)
                        return response
                # Bot response to arbitrary input
                response = random.choice(self.arbitrary_input)
                return response
            elif len(potential_titles) > 1:
                # extract sentiment for multiple movies (assumes they exist in database)
                if len(re.findall("\"(.*?)\"", line)) == 0:
                    response = "I think you are referring to a movie. Can you repeat what you said and put quotations around the title?"
                    return response
                else:
                    multiple_movies = self.extract_sentiment_for_movies(line)
                    for elem in multiple_movies:
                        elem_title = self.find_movies_by_title(elem[0])
                        if len(elem_title) == 0:
                            response = "Sorry, I could not recognize one or more of the movies you mentioned."
                            return response
                        title_index.append(elem_title[0])
                    multiple_sentiments = [x[1] for x in multiple_movies]
                    multiple = True
            # Check if title is in database
            title = potential_titles[0]
            matches = self.find_movies_by_title(title)
            if len(matches) == 0 and not multiple:
                matches = self.find_movies_closest_to_title(title)
                if len(matches) == 0:
                    response = "Sorry, I'm not sure what movie you are referring to."
                    return response
                elif len(matches) > 1:
                    self.need_disambiguate = True
                    self.disambiguate_matches = matches
                    self.previous_line = line
                    matches_text = ['"' + string.capwords(
                        self.titles_parsed[idx][0][0]) + ' (' + self.titles_parsed[idx][1] + ')"' for idx in matches]
                    response = "Sorry, I'm not sure which movie you are referring to. Did you mean " + \
                        ' or '.join(matches_text) + "?"
                    return response
                else:
                    response = 'Did you mean "' + \
                        string.capwords(
                            self.titles_parsed[matches[0]][0][0]) + ' (' + self.titles_parsed[matches[0]][1] + ')"'
                    self.previous_line = line
                    self.title_to_be_clarified = matches[0]
                    self.need_clarification = True
                    return response
            elif len(matches) > 1 and not multiple:
                self.need_disambiguate = True
                self.disambiguate_matches = matches
                self.previous_line = line
                matches_text = ['"' + string.capwords(
                    self.titles_parsed[idx][0][0]) + ' (' + self.titles_parsed[idx][1] + ')"' for idx in matches]
                response = "Sorry, I'm not sure which movie you are referring to. Did you mean " + \
                    ' or '.join(matches_text) + "?"
                return response
            if not multiple:
                title_index = matches

        # Extract sentiment
        sentiments = [self.extract_sentiment(line)]
        if multiple_sentiments != None:
            sentiments = multiple_sentiments

        # Output response depending on sentiments
        for i, sent in enumerate(sentiments):
            if (sent != 0):
                conf_word = random.choice(self.conf_words)
                sent_word = random.choice(
                    self.pos_sent) if sent > 0 else random.choice(self.neg_sent)
                movie_word = '"' + \
                    string.capwords(
                        self.titles_parsed[title_index[i]][0][0]) + ' (' + self.titles_parsed[title_index[i]][1] + ')"'
                punc = random.choice(
                    self.pos_punc) if sent > 0 else random.choice(self.neg_punc)

                # Generate response
                if i == len(sentiments) - 1 and i == 0:
                    response += "{}, you {} {}{} {}".format(
                        conf_word, sent_word, movie_word, punc, self.ending)
                elif i == len(sentiments) - 1:
                    response += "you {} {}{} {}".format(
                        sent_word, movie_word, punc, self.ending)
                elif i == 0:
                    response += "{}, you {} {} and ".format(
                        conf_word, sent_word, movie_word)
                else:
                    response += "you {} {} and ".format(
                        sent_word, movie_word)

                self.user_ratings[i] = sent
                self.movies_rated += 1
            else:
                movie_word = '"' + \
                    string.capwords(
                        self.titles_parsed[title_index[i]][0][0]) + ' (' + self.titles_parsed[title_index[i]][1] + ')"'
                self.clarify_sentiment = True
                self.previous_title = title_index
                response = "I'm sorry, I'm not sure if you liked " + \
                    movie_word + ". Can you tell me more about it?"
                return response

        if (self.movies_rated >= 5):
            punc = random.choice(self.pos_punc)
            self.user_recs = self.recommend(self.user_ratings, self.ratings)
            rec = '"' + string.capwords(self.titles_parsed[self.user_recs.pop(
            )][0][0]) + ' (' + self.titles_parsed[self.user_recs.pop()][1] + ')"'
            response = response + '\n' + \
                "given what you told me, I think you would like {}{} Would you like more?".format(
                    rec, punc)
            self.recommending = True

        # if self.creative:
        #     response = "I processed {} in creative mode!!".format(line)
        # else:
        #     response = "I processed {} in starter mode!!".format(line)

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

        # capture movies that have quotation marks
        regex = "\"(.*?)\""
        matches = re.findall(regex, preprocessed_input)
        if self.creative and len(matches) == 0:
            lowercase_input = preprocessed_input.lower()
            for i, item in enumerate(self.titles_parsed):
                for title in item[0]:
                    forms = [" " + title + " ", " " + title +
                             "\n", " " + title + ".", " " + title + "!"]
                    for form in forms:
                        if form in lowercase_input:
                            matches.append(title)
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
        # Extract the title and year (if available) of the input title (assumes there's space between title and year)
        text = re.match(
            r'((?:(?! \(([0-9]+)\)$).)*)(?: \(([0-9]+)\)[ ]?$)?', title).group(1).lower()
        year = re.match(r'(.*)(?: \(([0-9]+)\)[ ]?$)', title)
        if year != None:
            year = year.group(2)

        # Extract alternate titles
        alternates = {x[len('a.k.a. '):] if x.startswith('a.k.a. ') else x for x in re.findall(
            r'(?:\(((?!.*?\bnot\b.*?)[^()]*?)\))', text)}  # first part achieves .removeprefix functionality
        text = re.sub(r'(?:\(((?!.*?\bnot\b.*?)[^()]*?)\))', '', text).strip()
        alternates.add(text)

        # Each element in self.titles is list with 2 strings in the format "[Title, Genres]"
        # Indices in the list correspond to indices in the text file.
        results = set()
        for i in range(len(self.titles_parsed)):
            db_titles, db_year = self.titles_parsed[i]
            # If a match is found add it to results
            if not self.creative:
                if alternates & set(db_titles):
                    if year != None and db_year != None:
                        if year == db_year:
                            results.add(i)
                    else:
                        results.add(i)
            else:
                for key in alternates:
                    for match in db_titles:
                        if key == match or key + " " in match or key + ":" in match:
                            if year != None and db_year != None:
                                if year == db_year:
                                    results.add(i)
                            else:
                                results.add(i)
        return list(results)

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
        # Removing titles from input string, using Re from extract_titles
        regex = "\"(.*?)\""
        input_without_titles = re.sub(regex, "", preprocessed_input)

        # Common negation words to look for
        negation_words = ["didn't", "not", "never", "neither", "nor", "barely", "hardly",
                          "scarcely", "rarely", "don't", "no", "nothing", "none", "nobody", "nowhere"]

        # Words with strong sentiment
        strong_sentiment = ["terrible", "loved",
                            "love", "hate", "hated", "best", "worst"]

        # Adverb sentiment
        adverb_sentiment = ["really", "very",
                            "extremely", "seriously", "especially"]

        # Import stemming functionality
        p = porter_stemmer.PorterStemmer()

        tokens = input_without_titles.split()
        res = 0
        negation_coefficient = 1
        sentiment_coefficient = 1
        # Track whether current word has punctuation at end: negation doesn't apply after punctuation
        punc = False
        for token in tokens:
            # Handle edge case where enjoyed is stemmed to enjoi instead of enjoy
            if token == "enjoyed":
                token = "enjoy"
            punc = False
            if token[-1] in string.punctuation:
                token = token[:-1]
                punc = True
            stemmed_token = p.stem(token, 0, len(token) - 1)
            if token in negation_words:
                negation_coefficient = -1
            if self.creative:
                # In creative, we modify the score for words with stronger sentiment
                if token in adverb_sentiment:
                    res += negation_coefficient
                    continue
                if token in strong_sentiment:
                    sentiment_coefficient = 2
            if token in self.sentiment:
                # Score increases or decreases as a function of the sentiment of the token and whether it's negated
                res += negation_coefficient * sentiment_coefficient * \
                    (1 if self.sentiment[token] == "pos" else -1)
                if punc == True:
                    negation_coefficient = 1
                continue
            if stemmed_token in self.sentiment:
                res += negation_coefficient * sentiment_coefficient * \
                    (1 if self.sentiment[stemmed_token] == "pos" else -1)
                if punc == True:
                    negation_coefficient = 1
            sentiment_coefficient = 1
        return res

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
        titles = self.extract_titles(preprocessed_input)
        res = []
        for title in titles:
            res.append((title, 0))
        regex = "\"(.*?)\""
        input_with_placeholders = re.sub(regex, "%", preprocessed_input)

        # Common negation words to look for
        negation_words = ["didn't", "not", "never", "neither", "nor", "barely", "hardly",
                          "scarcely", "rarely", "don't", "no", "nothing", "none", "nobody", "nowhere"]

        # Import stemming functionality
        p = porter_stemmer.PorterStemmer()

        conjunctions = ["and", "but", "nor", "or"]

        punctuation = string.punctuation.replace("%", "")

        phrases = re.split('%', input_with_placeholders)
        jumped = False

        phrase_idx = 0

        for idx, title in enumerate(titles):
            phrase = phrases[phrase_idx]
            tokens = phrase.split()

            if (tokens[0] in punctuation or tokens[0] in conjunctions) and (len(tokens) < 3) and (phrase_idx == len(phrases)-1 or len(phrases[phrase_idx+1].split()) < 3):
                res[idx] = (res[idx][0], res[idx-1][1])
                phrase_idx += 1
                continue

            if (tokens[0] in punctuation or tokens[0] in conjunctions) and not jumped:
                jumped = True
                phrase_idx += 1

            tokens = phrases[phrase_idx].split()

            negation_coefficient = 1
            # Track whether current word has punctuation at end: negation doesn't apply after punctuation
            punc = False
            phrase_res = 0
            for token in tokens:
                # Handle edge case where enjoyed is stemmed to enjoi instead of enjoy
                if token == "enjoyed":
                    token = "enjoy"
                punc = False
                if token[-1] in punctuation:
                    token = token[:-1]
                    punc = True
                stemmed_token = p.stem(token, 0, len(token) - 1)
                if token in negation_words:
                    negation_coefficient = -1
                if token in self.sentiment:
                    # Score increases or decreases as a function of the sentiment of the token and whether it's negated
                    phrase_res += negation_coefficient * \
                        (1 if self.sentiment[token] == "pos" else -1)
                    if punc == True:
                        negation_coefficient = 1
                    continue
                if stemmed_token in self.sentiment:
                    phrase_res += negation_coefficient * \
                        (1 if self.sentiment[stemmed_token] == "pos" else -1)
                    if punc == True:
                        negation_coefficient = 1
            res[idx] = (res[idx][0], phrase_res)
            phrase_idx += 1
        return res

    @staticmethod
    def calc_edit_dist(s1, s2, m, n):
        """Helper function to calculate edit distance between two strings
        """
        dp = [[0 for x in range(n + 1)] for x in range(m + 1)]

        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0:
                    dp[i][j] = j
                elif j == 0:
                    dp[i][j] = i
                elif s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = min(dp[i][j-1] + 1,
                                   dp[i-1][j] + 1,
                                   dp[i-1][j-1] + 2 if s1[i-1] != s2[j-1] else dp[i-1][j-1] + 0)

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
        len_title = len(title)
        res = []
        min_dist = float('inf')

        for i, movie_info in enumerate(self.titles_parsed):
            movies, year = movie_info
            for m in movies:
                temp = self.calc_edit_dist(m, title.lower(), len(m), len_title)
                if temp == min_dist and temp <= max_distance:
                    res.append(i)
                elif temp < min_dist and temp <= max_distance:
                    min_dist = temp
                    res = [i]
        return res

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
        clarification = clarification.lower().strip(string.punctuation)
        result = []
        # Check if clarification exists as substring in title
        for i in candidates:
            candidate = self.titles[i][0].lower()
            found = re.findall(
                '(?<![a-zA-Z0-9])' + re.escape(clarification) + '(?![a-zA-Z0-9])', candidate)
            if len(found) > 0:
                result.append(i)

        return result

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

        # Track ratings of 0, to make 0 again after binarizing
        keep_mask = ratings == 0
        # Binarize ratings
        binarized_ratings = np.where(ratings > threshold, 1, -1)
        binarized_ratings[keep_mask] = 0

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
        if (np.linalg.norm(u) == 0 or np.linalg.norm(v) == 0):
            similarity = 0
        else:
            norm_u = np.linalg.norm(u)
            norm_v = np.linalg.norm(v)
            similarity = (np.dot(u, v) / (norm_u * norm_v))

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
        dict = {}
        # loop over movies user hasn't rated
        for i in np.where(user_ratings == 0)[0]:
            rating = 1e-8
            # we want to calculate cosine similarity between movie user hasn't rated and each movie in data
            for j in np.where(user_ratings != 0)[0]:
                similarity = self.similarity(
                    ratings_matrix[i, :], ratings_matrix[j, :])
                rating += (similarity * user_ratings[j])
            dict[i] = rating
        recommendations = nlargest(k, dict, key=dict.get)

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
