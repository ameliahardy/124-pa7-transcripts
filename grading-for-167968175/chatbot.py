# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re 
from porter_stemmer import PorterStemmer
from collections import defaultdict


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'waffler'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.user_recs = []
        self.user_sents = np.zeros(len(self.titles))
        self.creative_prev_sent = []
        self.comp_recs = []
        self.rec = False
        self.spellcheck = False
        self.disamb = False
        self.spellcheck_prev = []
        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

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
        ########################################################################
        # TODO: Write a short greeting message                                 #
        ########################################################################

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
        if self.creative:
            response = "I processed {} in creative mode!!".format(line)
        else:
            response = "I processed {} in starter mode!!".format(line)

        
        if self.spellcheck:
            line = line.lower()
            if line == 'yes':
                curr_movie = self.spellcheck_ans[0]
                curr_sent = self.extract_sentiment(self.spellcheck_prev)
                if curr_sent == 0:
                    response = "I can't tell what you thought about this movie."
                else:
                    self.user_recs.append(self.titles[curr_movie])
                    self.user_sents[curr_movie] = curr_sent
                    if len(self.user_recs) >= 5:
                        self.comp_recs = self.recommend(self.user_sents, self.ratings, k=10, creative=self.creative)
                        curr_ans = self.titles[self.comp_recs.pop(0)]
                        response = "Based on what you've told me, I'd recommend {}. Would you like another recommendation?".format(curr_ans)
                        self.rec = True
                    else:
                        if curr_sent == 1:
                            response = "Great, so you liked {}. Tell me about another movie you've seen.".format(self.titles[curr_movie][0])
                        if curr_sent == -1:
                            response = "Okay, so you didn't like {}. Tell me about another movie you've seen.".format(self.titles[curr_movie][0])
                self.spellcheck = False
                self.spellcheck_ans = []
                self.spellcheck_prev = ""
                return response
            if line == 'no':
                response = "I'm sorry, I don't understand. Can you tell me what you thought about a movie you saw?"
                return response
            else:
                title = self.extract_titles(line)
                if len(title) != 1:
                    response = "I'm sorry, I don't understand. Can you tell me what you thought about a movie you saw?"
                    return response
                movie_ind = self.find_movies_by_title(title)
                if len(movie_ind) == 0:
                    response = "I'm sorry, I can't find any movies named '{}'. Can you tell me what you thought about a movie you saw?".format(title)
                    return response
                if len(movie_ind) > 1:  
                    response = "I'm sorry, I've found multiple movies '. Can you tell me what you thought about a movie you saw?".format(title)
                    return response
                self.user_recs.append(self.titles[curr_movie])
                self.user_sents[curr_movie] = curr_sent
                if len(self.user_recs) >= 5:
                    self.comp_recs = self.recommend(self.user_sents, self.ratings, k=10, creative=self.creative)
                    curr_ans = self.titles[self.comp_recs.pop(0)]
                    response = "Based on what you've told me, I'd recommend {}. Would you like another recommendation?".format(curr_ans)
                    self.rec = True
                else:
                    if curr_sent == 1:
                        response = "Great, so you liked {}. Tell me about another movie you've seen.".format(self.titles[curr_movie])
                    if curr_sent == -1:
                        response = "Okay, so you didn't like {}. Tell me about another movie you've seen.".format(self.titles[curr_movie])
                self.spellcheck = False
                self.spellcheck_ans = []
                self.spellcheck_prev = ""
                return response
                

        
        
        if len(self.user_recs) == 5:
            if line == 'yes':
                if len(self.comp_recs) > 0:
                    resp = self.titles[self.comp_recs.pop(0)]
                    response = "Another recommendation is {}. Would you like another?".format(resp)
                    return response
                else:
                    response = "I'm sorry, I have no more recommendations"
                    return response
            if line == 'no':
                return self.goodbye
            # extract movie titles; if can't find any titles given, ask for a movie title
        if len(self.user_recs) < 5:
            input = self.preprocess(line)
            titles = self.extract_titles(input)
            if len(titles) == 0:
                if self.creative:
                    spellcheck = self.find_movies_closest_to_title(input)
                    self.spellcheck = True
                    self.spellcheck_ans = spellcheck
                    self.spellcheck_prev = input
                    response = "Did you mean {}?".format(spellcheck)
                else:
                    response = "I'm sorry, I don't understand. Can you tell me what you thought of a movie you've seen?"
                return response
            if len(titles) > 1:
                # TODO: build in creative mode for multiple movies
                if self.creative:
                    sents = self.extract_sentiment_for_movies(input)
                    response = "Okay, so "
                    for sent in sents:
                        self.user_recs.append(sent[0])
                        movie_index = self.find_movies_by_title(sent[0])
                        self.user_sents[movie_index] = sent[1]
                        if sent[1] < 1:
                            response = response + "you didn't like {}, ".format(sent[0])
                        if sent[1] >= 1:
                            response = response + "you liked {}, ".format(sent[0])
                    return response
                else:
                    response = "Could you discuss one movie at a time?"
                    return response
            # check for title in database, check that there's only one
            poss_movies = self.find_movies_by_title(titles[0])
            if len(poss_movies) > 1:
                # built in disambiguate for creative mode
                if self.creative:
                    poss_movies_list = []
                    for index in poss_movies:
                        poss_movies_list.append(self.titles[index])
                    response = "I've found multiple movies: {}. Which one did you mean?".format(poss_movies_list)
                else:
                    response = "I've found multiple movies called '{}', can you clarify?".format(titles[0])
                return response
            if len(poss_movies) == 0:
                close_movies = self.find_movies_closest_to_title(titles[0])
                if len(close_movies) > 0:
                    close_movies_list = []
                    for index in close_movies:
                        close_movies_list.append(self.titles[index])
                    response = "Did you mean: '{}'".format(close_movies_list)
                    self.spellcheck = True
                    self.spellcheck_ans = close_movies
                    self.spellcheck_prev = input
                else:
                    response = "Sorry, I can't find any movies called '{}', tell me about another movie you've seen".format(
                        titles[0])
                return response
            # extract sentiment for line
            curr_sentiment = self.extract_sentiment(input)
            if curr_sentiment == 0:
                response = "I can't tell if you liked '{}', can you provide more information?".format(titles[0])
                return response
            self.user_recs.append(titles[0])
            self.user_sents[poss_movies] = curr_sentiment
            if len(self.user_recs) == 5:
                self.comp_recs = self.recommend(self.user_sents, self.ratings, k=10, creative=self.creative)
                curr_ans = self.titles[self.comp_recs.pop(0)]
                response = "Based on what you've told me, I recommend {}. Would you like another recommendation?".format(
                    curr_ans)
                return response
            # built in strong sentiment for creative mode
            if self.creative and curr_sentiment > 1:
                response = "Okay, so you really liked '{}'. Tell me what you thought of another movie.".format(
                    titles[0])
            if self.creative and curr_sentiment < -1:
                response = "Okay, so you really disliked '{}'. Tell me what you thought of another movie.".format(
                    titles[0])
            if curr_sentiment == 1:
                response = "Okay, you liked '{}'. Tell me what you thought of another movie.".format(titles[0])
            if curr_sentiment == -1:
                response = "Okay, you didn't like '{}'. Tell me what you thought of another movie.".format(titles[0])
            return response

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
        return re.findall('\"(.+?)\"', preprocessed_input)



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
        if self.creative:
            title.strip()
            title = title.lower()
            words = title.split()
            newtitle = ''
            year = False
            prefix = False
            string1 = ''
            string2 = ''
            if words[-1][-1] == ')':
                year = True
            if words[0].lower() in ['the', 'an', 'le', 'les', 'a', 'la', 'el', 'un', 'une']:
                prefix = True
            if year:
                string1 = "([0-9]+)%" + '[a-zA-Z\s,0-9\\.\\:]*\\(?[a-zA-Z\\s,\\.\\:0-9]*' + ' '.join(words[:-1]).lower() + '[\\s\\)][a-zA-Z\\s,0-9\\(\\)\\.\\:]*' + '\\(' + words[-1][1:-1].lower() + '\\)'
                if prefix:
                    string2 = "([0-9]+)%" + '[a-zA-Z\s,0-9\\.\\:]*\\(?[a-zA-Z\\s,\\.\\:0-9]*' + ' '.join(words[1:-1]).lower() + ', ' + words[0].lower() + '[\\s\\)][a-zA-Z\\s,0-9\\(\\)\\.\\:]*' + '\\(' + words[-1][1:-1].lower() + '\\)'
            else:
                string1 = "([0-9]+)%" + '[a-zA-Z\s,0-9\\.\\:]*\\(?[a-zA-Z\\s,\\.\\:0-9]*' + " ".join(words).lower() + '[\\s\\)][a-zA-Z\\s,0-9\\(\\)\\.\\:]*\\([0-9]+\\)'
                #print(title, string1)
                if prefix:
                    string2 = "([0-9]+)%" + '[a-zA-Z\s,0-9\\.\\:]*\\(?[a-zA-Z\\s,\\.\\:0-9]*' + ' '.join(words[1:]).lower() + ', ' + words[0].lower() + '[\\s\\)][a-zA-Z\\s,0-9\\(\\)\\.\\:]*\\([0-9]+\\)'

            ids = set()
            #print(string1)
            #print(string2)

            with open('data/movies.txt', 'r') as file:
                txt = (file.read()).lower()

                idmatches = re.findall(string1, txt)
                for idmatch in idmatches:
                    ids.add(int(idmatch))
                if string2 != '':
                    idmatches = re.findall(string2, txt)
                    for idmatch in idmatches:
                        ids.add(int(idmatch))
            return list(ids)
        else:
            title.strip()
            words = title.split()
            year = words[-1][-1] == ')'
            prefix = words[0].lower() in ['the', 'an', 'le', 'les', 'a', 'la', 'el', 'un', 'une']
            newwords = words
            if prefix:
                if year:
                    newwords = words[1:-1] + [words[0]] + [words[-1]]
                    newwords[-3] = newwords[-3] + ','
                else:
                    newwords = words[1:] + [words[0]]
                    newwords[-2] = newwords[-2] + ','
            if year:
                newwords[-1] = "\\(" + newwords[-1][1:-1] + "\\)"
                search = "([0-9]+)%" + ' '.join(newwords)
            else:
                search = "([0-9]+)%" + ' '.join(newwords) + ' \\([0-9]+\\)'
            #print(search)

            ids = set()

            with open('data/movies.txt', 'r') as file:
                txt = file.read()
                idmatches = re.findall(search, txt)
                for idmatch in idmatches:
                    ids.add(int(idmatch))

            return list(ids)


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
        p = PorterStemmer()
        negatives = ['not', 'never', 'neither', 'nor', 'barely', 'hardly', 'scarcely', 'seldom', 'rarely', "shouldn't",
                     "can't", "didn't", "won't", "doesn't", "don't"]
        if self.creative:
            strong_sents = ['love', 'loved', 'awesome', 'horrible', 'hated', 'hate', 'great', 'terrible', 'favorite',
                            'worst']
            supers = ['really', 'strongly']

        sentiment_dict = defaultdict(int)

        with open('data/sentiment.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                pair = line.split(',')
                if pair[1][:-1] == 'pos':
                    sentiment_dict[p.stem(pair[0])] = 1
                else:
                    sentiment_dict[p.stem(pair[0])] = -1

        preprocessed_input = re.sub(r'".*"', '', preprocessed_input)

        words = re.split('! ?|@ ?|# ?|; %|; &|; *|\(|\)|\s|\. ?', preprocessed_input)
        value = 0
        multiplier = 1
        for word in words:
            word = word.lower()
            stem = p.stem(word)
            if word in negatives:
                multiplier *= -1
            if self.creative and word in supers:
                multiplier *= 2
            else:
                if self.creative and word in strong_sents:
                    value += (multiplier * 2 * sentiment_dict[stem])
                else:
                    value += (multiplier * sentiment_dict[stem])
        return value

        # not sure if this has the potential to return values over -2 and so on

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
        # not sure if this is buggy, passes in gradescope but can't get local testing to work
        sents_part1 = []
        sents_part2 = []
        titles = self.extract_titles(preprocessed_input)
        num_titles = len(titles)
        curr_num = 0
        previous_num = 0
        while curr_num < num_titles:
            line_1 = preprocessed_input.find(titles[curr_num])
            index_start = line_1 + len(titles[curr_num]) + 1
            curr_sent = self.extract_sentiment(preprocessed_input[previous_num:index_start])
            if curr_sent == 0 and curr_num > 0:
                negations = ['not']
                if any(neg in preprocessed_input[previous_num:index_start] for neg in negations):
                    curr_sent = -1 * sents_part2[curr_num - 1]
                else:
                    curr_sent = sents_part2[curr_num - 1]
            sents_part1.append(titles[curr_num])
            sents_part2.append(curr_sent)
            curr_num += 1
            previous_num = index_start
        return zip(sents_part1, sents_part2)


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
        dist_1 = len(title)
        title.strip()
        title = title.lower()
        closest_titles = []
        ids = []
        least_dist = float("inf")
        for tit in self.titles:
            curr_tit = tit[0]
            curr_tit.strip()
            if curr_tit[-1] == ')':
                curr_tit = curr_tit[:-7]
            curr_tit = curr_tit.lower()
            words = curr_tit.split()
            if words[-1] in ['the', 'an', 'le', 'les', 'a', 'la', 'el', 'un', 'une']:
                words = [words[-1]] + words[0:-1]
                words[-1] = words[-1][:-1]
            curr_tit = ' '.join(words)
            #print(curr_tit)
            dist_2 = len(curr_tit)
            # distance calculation

            arr = [[0 for i in range(dist_2 + 1)] for j in range(dist_1 + 1)]
            for j in range(dist_2 + 1):
                arr[0][j] = j
            for i in range(dist_1 + 1):
                arr[i][0] = i
            for i in range(1, dist_1 + 1):
                for j in range(1, dist_2 + 1):
                    if title[i - 1] == curr_tit[j - 1]:
                        arr[i][j] = min((arr[i - 1][j] + 1), (arr[i][j - 1] + 1), arr[i - 1][j - 1])
                    else:
                        arr[i][j] = min((arr[i - 1][j] + 1), (arr[i][j - 1] + 1), (arr[i - 1][j - 1] + 2))
            dist = arr[dist_1][dist_2]

            if dist <= max_distance:
                if dist < least_dist:
                    least_dist = dist
                    ids = [self.find_movies_by_title(tit[0])[0]]
                elif dist == least_dist:
                    ids.append(self.find_movies_by_title(tit[0])[0])

        return ids



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
        result = []

        for candidate in candidates:
            regex = str(candidate) + '%(.+) \\((.+)\\)'
            with open('data/movies.txt', 'r') as file:
                movies = file.read()
                title = re.findall(regex, movies)
            if clarification in title[0][0].lower() or (len(clarification) == 4 and clarification in title[0][1].lower()):
                result.append(candidate)

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
        
        #binarized_ratings = ratings
        #binarized_ratings[(0 < binarized_ratings) & (binarized_ratings < threshold)] = -1
        #binarized_ratings[binarized_ratings > threshold] = 1
        binarized_ratings = np.zeros_like(ratings)
        binarized_ratings[ratings > threshold] = 1
        binarized_ratings[ratings <= threshold] = -1
        binarized_ratings[ratings == 0] = 0

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
        #numerator = np.dot(u, v)
        #denominator = np.sqrt(np.dot(u, u)) * np.sqrt(np.dot(v, v))
        #similarity = numerator / denominator
        unorm = np.sqrt(np.dot(u, u))
        vnorm = np.sqrt(np.dot(v, v))
        if unorm == 0 or vnorm == 0:
            return 0
        similarity = np.dot(u,v)/(unorm*vnorm)
        
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

        rated = set()
        for i in range(len(user_ratings)):
            if user_ratings[i] != 0:
                rated.add(i)

        ratings = np.array([])
        for i in range(len(ratings_matrix)):
            x = np.array([])
            y = np.array([])
            if user_ratings[i] == 0:
                for j in rated:
                    if user_ratings[j] != 0:
                        y = np.append(y, [user_ratings[j]])
                        sim = self.similarity(ratings_matrix[i], ratings_matrix[j])
                        x = np.append(x, [sim])
            ratings = np.append(ratings, [np.dot(x, y)])

        recommendations = list(np.flip(np.argsort(ratings)[-k:]))

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
