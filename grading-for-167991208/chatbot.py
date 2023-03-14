# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re
from porter_stemmer import PorterStemmer


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
        self.seenmovies = np.zeros(len(self.titles))
        self.p = PorterStemmer()
        self.alphanum = re.compile('[^a-zA-Z0-9]')
        self.stem_sentiment = {self.p.stem(xx): yy for xx, yy in self.sentiment.items()}
        self.response_counter = 0
        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings)
        self.recommended_so_far = 0
        self.recommended = []
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

        greeting_message = "What can I do for you?"

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

        goodbye_message = "Have a splendid day!"

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
        if self.creative:
            #response = "I processed {} in starter mode!!".format(line)
            #self.find_movies_by_title(self.extract_titles(line)[-1])
            preprocessed_input = self.preprocess(line)
            cond = False

            if preprocessed_input == "yes" or preprocessed_input == "yeah" or preprocessed_input == "yes!" or preprocessed_input == "yeah!":
                cond = True
            elif preprocessed_input == "no" or preprocessed_input == "nope" or preprocessed_input == "no!" or preprocessed_input == "nope!":
                cond = False
                return "Okay. Hope you'll enjoy my recommendations!"
            else:
                movie = self.extract_titles(preprocessed_input)
                if len(movie) == 0:
                    return "I couldn't find a movie... Please try again."
                match = False
                count = 0
                self.seenmovies[self.find_movies_by_title(movie[0])] = 1

                for entry in self.titles:
                    no_year = (entry[0]).split(" (")
                    if movie[0] == no_year[0] or movie[0] == entry[0]:
                        match = True
                    if movie[0] == no_year[0]:
                        count += 1

                if len(movie) == 0:
                    response = "I couldn't find a movie... Please try again."
                elif len(movie) > 1:
                    response = "Please tell me about one movie at a time. Go ahead."
                elif match == False:
                    if len(Chatbot.find_movies_closest_to_title(self, movie[0], max_distance=3)) > 0:
                        response = "Did you mean {}?".format((self.titles)[Chatbot.find_movies_closest_to_title(self, movie[0], max_distance=3)[0]][0])
                        if cond == True:
                            response = "Okay! Can you tell me about another movie?"
                    else:
                        response = "I've never heard of {}. Sorry! Can you tell me about another movie I might have heard of?".format(movie[0])
                elif count > 1:
                    response = "I found more than one movie called {}. Can you specify which movie you mean by providing the date it was released?".format(movie[0])
                else:
                    sentiment = self.extract_sentiment(preprocessed_input)
                    indices = self.find_movies_by_title(movie[0])
                    for index in indices:
                        self.seenmovies[index] = sentiment
                    if sentiment == 1:
                        response = "So you liked {}! Tell me what you think of another movie.".format(movie[0])
                        self.response_counter += 1
                    elif sentiment == -1:
                        response = "So you did not like {}. I'm sorry. Tell me what you think of another movie.".format(movie[0])
                        self.response_counter += 1
                    else:
                        response = "I'm sorry, I cannot tell if you liked {}.\n Tell me more about {}".format(movie[0], movie[0])
            if self.response_counter >= 5 or cond == True:
                if self.recommended_so_far == 0:
                    rec = self.recommend(self.seenmovies, self.ratings, k=10)
                    self.recommended = rec
                to_ret = (self.titles)[self.recommended[self.recommended_so_far]]
                if self.recommended_so_far == 0:
                    response += "I think you'd like {}! Would you like another recommendation?".format(to_ret[0])
                else:
                    response = "I think you'd like {}! Would you like another recommendation?".format(to_ret[0])
                self.recommended_so_far += 1
        else:
            #response = "I processed {} in starter mode!!".format(line)
            #self.find_movies_by_title(self.extract_titles(line)[-1])
            preprocessed_input = self.preprocess(line)
            cond = False

            if preprocessed_input == "yes" or preprocessed_input == "yeah" or preprocessed_input == "yes!" or preprocessed_input == "yeah!":
                cond = True
            elif preprocessed_input == "no" or preprocessed_input == "nope" or preprocessed_input == "no!" or preprocessed_input == "nope!":
                cond = False
                return "Okay. Hope you'll enjoy my recommendations!"
            else:
                movie = self.extract_titles(preprocessed_input)
                if len(movie) == 0:
                    return "I couldn't find a movie... Please try again."
                match = False
                count = 0
                self.seenmovies[self.find_movies_by_title(movie[0])] = 1

                for entry in self.titles:
                    no_year = (entry[0]).split(" (")
                    if movie[0] == no_year[0] or movie[0] == entry[0]:
                        match = True
                    if movie[0] == no_year[0]:
                        count += 1

                if len(movie) == 0:
                    response = "I couldn't find a movie... Please try again."
                elif len(movie) > 1:
                    response = "Please tell me about one movie at a time. Go ahead."
                elif match == False:
                    if len(Chatbot.find_movies_closest_to_title(self, movie[0], max_distance=3)) > 0:
                        response = "Did you mean {}?".format((self.titles)[Chatbot.find_movies_closest_to_title(self, movie[0], max_distance=3)[0]][0])
                        if cond == True:
                            response = "Okay! Can you tell me about another movie?"
                    else:
                        response = "I've never heard of {}. Sorry! Can you tell me about another movie I might have heard of?".format(movie[0])
                elif count > 1:
                    response = "I found more than one movie called {}. Can you specify which movie you mean by providing the date it was released?".format(movie[0])
                else:
                    sentiment = self.extract_sentiment(preprocessed_input)
                    indices = self.find_movies_by_title(movie[0])
                    for index in indices:
                        self.seenmovies[index] = sentiment
                    if sentiment == 1:
                        response = "So you liked {}! Tell me what you think of another movie.".format(movie[0])
                        self.response_counter += 1
                    elif sentiment == -1:
                        response = "So you did not like {}. I'm sorry. Tell me what you think of another movie.".format(movie[0])
                        self.response_counter += 1
                    else:
                        response = "I'm sorry, I cannot tell if you liked {}.\n Tell me more about {}".format(movie[0], movie[0])
            if self.response_counter >= 5 or cond == True:
                if self.recommended_so_far == 0:
                    rec = self.recommend(self.seenmovies, self.ratings, k=10)
                    self.recommended = rec
                to_ret = (self.titles)[self.recommended[self.recommended_so_far]]
                if self.recommended_so_far == 0:
                    response += "I think you'd like {}! Would you like another recommendation?".format(to_ret[0])
                else:
                    response = "I think you'd like {}! Would you like another recommendation?".format(to_ret[0])
                self.recommended_so_far += 1

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
        if self.creative:

            black_listed_titles = ["(not)"]

            to_ret = [""]
            
            quoted_movies = re.findall(r'"([^"]*)"', preprocessed_input)
            if quoted_movies:
                return quoted_movies

            articles_english = ["a", "the", "an"]
            articles_spanish = ["el", "la", "los", "las"]
            articles_italian = ["lo", "il", "la", "l'", "gli", "i", "le"]
            articles_french = ["la", "le", "l'", "les"]
            articles_german = ["der", "die", "das"]
            articles = articles_english + articles_spanish + articles_italian + articles_french + articles_german
            articles_pattern = "(, " + "|, ".join(articles)  + ")$"


            preprocessed_input = preprocessed_input.lower()
            for title in self.titles:
                ## 1. find all foreign titles
                movie_title = title[0].lower()

                movie_title_no_year = re.sub(r' \([0-9]{4}\)', "", movie_title).strip()
                foreign_pattern = "\([\w\-\s_.,!\/]+\)"
                foreign_titles = re.findall(re.compile(foreign_pattern), movie_title_no_year)
                if foreign_titles:
                    for idx, foreign_title in enumerate(foreign_titles):
                        if foreign_title in black_listed_titles:
                            continue
                        foreign_titles[idx] = foreign_title[1:-1]
                        if foreign_titles[idx].startswith('a.k.a. '):
                            foreign_titles[idx] = foreign_titles[idx][len('a.k.a. '):]

                original_title = [""]
                original_title_index = movie_title_no_year.find("(")
                if original_title_index == -1:
                    original_title = [movie_title_no_year]
                else:
                    original_title = [movie_title_no_year[:original_title_index-1]]
                
                all_titles = original_title + foreign_titles
                
                ## 2. alternative article spelling
                ## ^^ but REVERSED compared with find_movies_by_title
                all_titles_alt = []
                for single_title in all_titles:
                    prefix_match = re.search(re.compile(articles_pattern), single_title)
                    prefix, single_title_alt = None, None
                    if prefix_match:
                        prefix = prefix_match.group(0)
                        single_title_alt = re.sub(articles_pattern, "", single_title)
                        single_title_alt = prefix.strip() + " " + single_title_alt
                        single_title_alt = single_title_alt[2:] ## removes ", "
                        all_titles_alt.append(single_title_alt)


                ## 3. match & return
                for single_title in all_titles:

                    if len(single_title) == 1: ## account for movies like M (1931), O (2001)
                        if " " + single_title in preprocessed_input or single_title + " " in preprocessed_input:
                            if len(original_title[0]) > len(to_ret[0]):
                                to_ret = original_title
                    elif single_title in preprocessed_input:
                        if len(original_title[0]) > len(to_ret[0]):
                            to_ret = original_title
                for single_title_alt in all_titles_alt:
                    if single_title_alt in preprocessed_input:
                        if len(original_title[0]) > len(to_ret[0]):
                            to_ret = original_title

            if to_ret[0] == "":
                return []
            return to_ret
        else:
            return re.findall(r'"([^"]*)"', preprocessed_input)


    def begins_with(self, movie_db, movie_user):
        movie_db_ = re.sub(r'[^\w\s]', '', movie_db + " ") ## removes punctuation, adds a space in the end
        movie_user_ = re.sub(r'[^\w\s]', '', movie_user + " ")
        if movie_db_.startswith(movie_user_):
            return True
        return False

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
        title = title.lower()
        title_no_year = title
        match = re.search(r'\([0-9]{4}\)', title)
        year = None
        if match:
            year = match.group(0)
            title_no_year = title.replace(year, "").strip()
        
        #normal titles
        indices = []
        for i, movie in enumerate(self.titles):
            movie_title = movie[0].lower()
            if movie_title.startswith(title_no_year + " (") or movie_title == title_no_year:
                # print(movie_title)
                if match and year in movie_title or not match:
                    indices.append(i)

        articles_english = ["a", "the", "an"]
        articles_spanish = ["el", "la", "los", "las"]
        articles_italian = ["lo", "il", "la", "l'", "gli", "i", "le"]
        articles_french = ["la", "le", "l'", "les"]
        articles_german = ["der", "die", "das"]
        articles = articles_english + articles_spanish + articles_italian + articles_french + articles_german
        articles_pattern = "^(" + " |".join(articles)  + " )"

        #titles with different stylization
        # if len(indices) == 0:
        for i, movie in enumerate(self.titles):
            movie_title = movie[0].lower()

            movie_title_no_year = re.sub(r' \([0-9]{4}\)', "", movie_title)
            foreign_pattern = "\([\w\-\s_.,!\/]+\)"
            foreign_titles = re.findall(re.compile(foreign_pattern), movie_title_no_year)
            if foreign_titles:
                for idx, foreign_title in enumerate(foreign_titles):
                    foreign_titles[idx] = foreign_title[1:-1]
                    if foreign_titles[idx].startswith('a.k.a. '):
                        foreign_titles[idx] = foreign_titles[idx][len('a.k.a. '):]

            prefix_match = re.search(re.compile(articles_pattern), title)
            prefix, title_no_year_alt = None, None
            if prefix_match:
                prefix = prefix_match.group(0)
                title_no_year_alt = title_no_year.replace(prefix, "", 1)
                title_no_year_alt = title_no_year_alt + ", " + prefix.strip()

            if self.begins_with(movie_title, title_no_year) or title_no_year_alt and self.begins_with(movie_title, title_no_year_alt):
                if match and year in movie_title or not match:
                    indices.append(i)
            elif foreign_titles:
                for foreign_title in foreign_titles:
                    if self.begins_with(foreign_title, title_no_year) or title_no_year_alt and self.begins_with(foreign_title, title_no_year_alt):
                        if match and year in movie_title or not match:
                            indices.append(i)

        return indices
        

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
        # remove movie title (in "")
        movie = self.extract_titles(preprocessed_input)[0]
        movie = '"' + movie + '"'
        sentiment_words = preprocessed_input.replace(movie, '')
        sentiment = 0
        negate = False

        # tokenizing the line into sentiment words
        # make sure everything is lower case
        line = sentiment_words.lower()
        # split on whitespace
        line = [xx.strip() for xx in line.split()]
        # remove non alphanumeric characters
        line = [self.alphanum.sub('', xx) for xx in line]
        # remove any words that are now empty
        line = [xx for xx in line if xx != '']
        # stem words
        line = [self.p.stem(xx) for xx in line]

        negation_words = ['wouldnt', 'didnt', 'shouldnt', "cannot", 'cant', 'doesnt', "not", "no", "isnt", "wasnt", "dont", "wont", "cant", "never", "didnt", "wouldnt", "never"]
        negation_words = [self.p.stem(xx) for xx in negation_words]
        love_words = ["love", "cherish", "amazing"]
        love_words = [self.p.stem(xx) for xx in love_words]
        hate_words = ["hate", "terrible", "obnoxious"]
        hate_words = [self.p.stem(xx) for xx in hate_words]
        emphasis_words = ["very", "really", "much", "verily", "especially", "surely"]
        emphasis_words = [self.p.stem(xx) for xx in emphasis_words]
        emphasis = False
        for word in line:
            if word in emphasis_words:
                emphasis = True
                continue
            if word in negation_words:
                negate = True
                continue
            if word in self.stem_sentiment:
                if negate:
                    if self.stem_sentiment[word] == "pos":
                        sentiment -= 1
                        if emphasis:
                            sentiment -= 1
                            emphasis = False
                    elif self.stem_sentiment[word] == "neg":
                        sentiment += 1
                        if emphasis:
                            sentiment += 1
                            emphasis = False
                    negate = False
                else:
                    if self.stem_sentiment[word] == "pos":
                        sentiment += 1
                        if emphasis:
                            sentiment += 1
                            emphasis = False
                        if word in love_words:
                            sentiment += 1
                    elif self.stem_sentiment[word] == "neg":
                        sentiment -= 1
                        if emphasis:
                            sentiment -= 1
                            emphasis = False
                        if word in hate_words:
                            sentiment -= 1

        if self.creative:
            if sentiment > 1:
                return 2
            if sentiment < -1:
                return -2
            return sentiment

        if sentiment > 0:
            sentiment = 1
        if sentiment < 0:
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

        to_rtn = []

        adversative_conjunctions = [
            "but", "although", "however", "nevertheless",
            "yet", "still", "though", "nonetheless"
            ]

        negation_words = ['wouldnt', 'didnt', 'shouldnt', "cannot", 'cant', 'doesnt', "not", "no", "isnt", "wasnt", "dont", "wont", "cant", "never", "didnt", "wouldnt", "never"]
        negation_words = [self.p.stem(xx) for xx in negation_words]

        def split(txt, seps):
            default_sep = seps[0]

            # we skip seps[0] because that's the default separator
            for sep in seps[1:]:
                txt = txt.replace(sep, default_sep)
            return [i.strip() for i in txt.split(default_sep)]

        clauses = split(preprocessed_input, adversative_conjunctions)
        # print("SEPERATION: ", clauses)
        for clause in clauses:
            sentiment = self.extract_sentiment(clause)
            movies = self.extract_titles(clause)
            
            if self.p.stem(clause.split()[0]) in negation_words:
                if sentiment == 0 and len(ratings) != 0:
                    sentiment = -ratings[-1][-1]

            # print(ratings)
            ratings = [(movie, sentiment) for movie in movies]
            to_rtn += ratings

        ## self.extract_sentiment(preprocessed_input)
        return to_rtn

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
        
        def edit_distance(str1, str2):
            n = len(str1)
            m = len(str2)
            D = [[0 for j in range(m+1)] for i in range(n+1)]
            for i in range(1, n+1):
                D[i][0] = i
            for j in range(1, m+1):
                D[0][j] = j
            # Fill in the rest of the matrix
            for i in range(1, n+1):
                for j in range(1, m+1):
                    D[i][j] = min(D[i - 1][j] + 1,  #deletion
                                D[i][j - 1] + 1,  #insertion
                                D[i - 1][j - 1] + sub_cost(str1[i-1], str2[j-1]))  #substitution
            return D[n][m]

        def sub_cost(x, y):
            # Cost of substituting characters
            if x == y:
                return 0
            else:
                return 2  

        
        distances = []
        for movie in self.titles:
            input = (movie[0]).split(' (')
            string1 = input[0].lower()
            string2 = title.lower()
            distance = edit_distance(string1, string2)
            #print(string1)
            #print(string2)
            #print(distance)
            distances.append(distance)
    
        minimum = min(distances)
        minimum_index = []
        j = 0
        for j in range(len(distances)):
            if minimum == distances[j] and minimum <= max_distance:
                minimum_index.append(j)
            j += 1
        return minimum_index


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
        to_ret = []
        for cand in candidates:
            movie = self.titles[cand]
            tokens = (movie[0]).split(" ")
            tokens[len(tokens)-1] = ((tokens[len(tokens)-1]).replace('(', '')).replace(')', '') #remove parentheses around date
            for token in tokens:
                if token in clarification:
                    to_ret.append(cand)
                    break
        return to_ret

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
        binarized_ratings = np.where(ratings > threshold, 1, -1)
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
        num = np.dot(u, v)
        denom = (np.linalg.norm(u) * np.linalg.norm(v))
        if denom == 0:
            similarity = 0
        else:
            similarity = num / denom
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

        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        rated_movie_indices = []
        recs_array = []
        for i in range(len(user_ratings)):
            if user_ratings[i] != 0:
                rated_movie_indices.append(i)
        
        for i in range(ratings_matrix.shape[0]):
            rating = [i, 0]
            for j in rated_movie_indices:
                if j == i:
                    continue
                sim = self.similarity(ratings_matrix[i], ratings_matrix[j])
                rating[1] += sim * user_ratings[j]
            recs_array.append(rating)
        recs_array.sort(key = lambda a: a[1])
        highest = len(recs_array) - 1
        for i in range(len(recs_array)):
            movie_index = recs_array[len(recs_array) - i - 1][0]
            if user_ratings[movie_index] == 0:
                recommendations.append(movie_index)
            if len(recommendations) == k:
                break
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
