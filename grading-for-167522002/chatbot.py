# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import porter_stemmer
p = porter_stemmer.PorterStemmer()
import random

import numpy as np


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'Cowboy Cap'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.num_recs = 0
        self.input_ratings = np.zeros((ratings.shape[0],1))
        self.rec_counter = 0
        self.disambiguating = False
        self.candidates = None
        self.disambiguate_sentiment = 0
        self.spell_check = False

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

        greeting_message = "Howdy, I'm %s! After we speak, movies won't feel like the wild west anymore. Tell me the name and year of a movie you have seen." % self.name

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

        goodbye_message = "Adios, partner. Hope I was more helpful than Siri! Have a great day!"

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
        pos_sentiment = ["Great, you liked \"%s\"! Tell me what you thought of another movie.",
        "I am so glad you loved \"%s\". What is another movie you have watched and liked or hated?",
        "While I didn't like \"%s\", it sounds like you really did! Can you give me another movie you have watched?",
        "Wow I didn't know you were such a big fan of \"%s\"! Have you watched any other movies?",
        "I'm glad \"%s\" is one of your favorite movies. What is another movie you have watched?"
        ]
        neg_sentiment = ["Okay, you didn't liked \"%s\". Tell me what you thought of another movie.",
        "I am sorry you didn't love \"%s\". What is another movie you have watched and loved or hated?",
        "While I liked \"%s\", it sounds like you didn't! Can you give me another movie you have watched?",
        "Wow I didn't know you didn't like \"%s\" so much! Have you watched any other movies?",
        "I'm sorry to hear \"%s\" is not one of your favorite movies. What is another movie you have watched?"
        ]
        neutral = ["I'm sorry, I'm not sure if you liked \"%s\". Tell me more about it.",
        "I can't tell if you liked or disliked \"%s\". Can you tell me more about it please?",
        "I can see you have watched \"%s\". What did you think of it?",
        "Wow, you must have seen a lot of movies! However, I can't quite seem to figure out how you feel about the movie \"%s\". What did you think of it?",
        "I promise I won't be mad if you didn't like \"%s\". You can tell me what you think about it!"
        ]

        dont_know = ["I've never heard of \"%s\". Tell me about another movie you liked.",
        "I don't recognize the movie \"%s\". Tell me what you thought of another movie.",
        "I can't seem to find the movie \"%s\". Can you give me another movie you have watched?",
        "%s may have been before my generation as I don't recognize it! Have you watched any other movies that I might know?",
        "I'm sorry, I don't know the movie \"%s\". What is another movie you have watched?"
        ]

        not_movie = ["That's interesting, but I don't think you have given me a movie. Make sure you have placed a movie title in quotes!",
        "That's doggone crazy, but you forgot to give me a movie!",
        "Enough of peanut talk. Please make sure you include a movie and your opinion of that movie so I can give you a recommendation!",
        "That's great to hear! It doesn't look like you have told me about a movie you have seen. Can you tell me about one?",
        "I'm sorry, you're barking up the wrong tree. I can't make a recommendation without a movie. What is a movie you have watched and loved or hated?"
        ]

        multi_titles= ["I'm sorry. I can only process your opinons on one movie at a time.",
        "It looks like you have given me your opinions on a few movies. Can you please just tell me your opinon on one movie?",
        "Whoops. You have provided me with too many movies to process. Please limit yourself to one movie at a time!",
        "Whoa there partner. Just one movie at a time.",
        "Slow down there partner. Only one movie and year at a time!"]

        not_clear = ["I found more than one movie called \"%s\". Can you clarify?",
        "I found a whole flock of movies with the name \"%s\"! If you're more specific, I'll be able to get a better idea.",
        "I could give find movies named \"%s\" until the cows come home. Could you give me more details?",
        "%s matches more than one movie! Help me out, partner--be more specific.",
        "I'm rounding up too many movies with the title \"%s\". Let's only catch what we can eat; any other details to thin out this field?"
        ]
        
        rec_responses = ["Based on what you have told me, I think you would like \"%s\". Would you like more recommendations?",
        "Your cinematic catch of the day is \"%s\". Would you like another recommendation?",
        "We've reeled in for you \"%s\". Want another?",
        "The cat dragged this movie in for you: \"%s\". How about another one?",
        "I would also recomemnd \"%s\" would you like more recommendations?"
        ]

        multi_sentiment_pos_responses = ["Great, you liked \"%s\" and \"%s\"!",
        "I am so glad you loved \"%s\" and \"%s\". What is another movie you have watched and liked or hated?",
        "While I didn't like \"%s\" and \"%s\", it sounds like you really did! Can you give me another movie you have watched?",
        "Wow I didn't know you were such a big fan of \"%s\" and \"%s\"! Have you watched any other movies?",
        "I'm glad \"%s\" and \"%s\" are two of your favorite movies. What is another movie you have watched?"
        ]

        question_triggger_words = ["can you", "what is", "how do", "how are ", "should i", "what's your"]

        disambiguate_resp = ["Which one did you mean? "]

        trigger_responses = ["Sorry partner. I can't",
                             "I know more about iPhones than I know about",
                             "I'm not like those city folk. I don't know how",
                             "I don't know the first thing about ",
                             "I don't know if you should or should not",
                             "I don't have a"
                             ]

        resp_index = random.randint(0, 4)
        if self.num_recs == 4:
            recs = self.recommend(self.input_ratings, self.ratings)
            line = line.lower()
            if self.rec_counter == 0:
                movie_name = self.titles[recs[self.rec_counter]][0]
                response = rec_responses[resp_index] % movie_name
            elif line[0] == 'y':
                movie_name = self.titles[recs[self.rec_counter]][0]
                response = rec_responses[resp_index] % movie_name
            elif line[0] == 'n' or self.rec_counter == 9:
                response = "We've reached the end of this old town road. Please enter :quit if you would like to ride off into the sunset with me. If you aren't finished with me yet, type in another movie and we can start this rodeo over again."
                self.num_recs = 0
            self.rec_counter += 1

        elif self.creative:
            title = self.extract_titles(line)
            sentiment = self.extract_sentiment(line)
            movies = []
            if len(title) > 0:
                movies = self.find_movies_by_title(title[0])
            # Disambiguating loop
            if self.disambiguating:
                movie_option = self.disambiguate(line, self.candidates)
                title = self.titles[movie_option[0]][0]
                if self.disambiguate_sentiment == 1 or self.disambiguate_sentiment == 2:
                    response = pos_sentiment[resp_index] % title
                else:
                    response = neg_sentiment[resp_index] % title
                self.num_recs += 1
                self.input_ratings[movie_option[0]] = self.disambiguate_sentiment
                self.disambiguating = False
            # Spell checking loop
            elif self.spell_check:
                line = line.lower()
                if line[0] == 'y':
                    index = self.candidates[0]
                    title = self.titles[index][0]
                    if self.disambiguate_sentiment == 1 or self.disambiguate_sentiment == 2:
                        response = pos_sentiment[resp_index] % title
                    else:
                        response = neg_sentiment[resp_index] % title
                    self.num_recs += 1
                    self.input_ratings[index] = self.disambiguate_sentiment
                    self.spell_check = False
                else:
                    response = "I'm sorry, I don't know what movie you are talking about then. Can you tell me about another movie you have seen?"
                    self.spell_check = False
            # If no movie in quotes
            # HEREHDH HL
            elif len(title) == 0:
                line_lower = line.lower()
                trigger = ""
                for trigger_word in question_triggger_words:
                    if trigger_word in line_lower:
                        trigger = trigger_word
                for i, word in enumerate(question_triggger_words):
                    if trigger == word:
                        our_len = len(trigger)
                        second_part = line[our_len:]
                        if " you " in second_part:
                            second_part = second_part.replace(" you ", " I ")
                        elif " me " in second_part:
                            second_part = second_part.replace(" me ", " you ")

                        if " my " in second_part:
                            second_part = second_part.replace(" my ", " your ")
                        elif " your " in second_part:
                            second_part = second_part.replace(" your ", " my ")

                        if " i " in second_part:
                            second_part = second_part.replace(" i ", " you ")
                        if second_part[len(second_part)-1] == "?":
                            second_part = second_part[:len(second_part)-1] + "."
                        response = trigger_responses[i] + second_part
                if trigger == "":
                    response = not_movie[resp_index] 
            # If multiple movies in input
            elif len(title) > 1:
                response_components = ''
                movie_indexes =  []
                for movie in title:
                    movie_indexes.append(self.find_movies_by_title(movie))
                movie_sentiments = self.extract_sentiment_for_movies(line)
                pos_movie_names = []
                neg_movie_names = []
                for title_sent, sent in movie_sentiments:
                    # Jack I don't know if you want me to increment num_recs here so I'm gonna leave it commented out
                    # self.num_recs += 1
                    if sent == 1:
                        pos_movie_names.append(title_sent)
                        # response_components += pos_sentiment[resp_index] % title_sent + ' '
                    elif sent == -1:
                        neg_movie_names.append(title_sent)
                        # response_components += neg_sentiment[resp_index] % title_sent + ' '
                    
                resp_index = random.randint(0, 4)
                if pos_movie_names != []:
                    pos_formatted = ''
                    for pos_movie in pos_movie_names:
                        if pos_movie == pos_movie_names[-1]:
                            pos_formatted += '\" and \"' + pos_movie
                        elif pos_movie == pos_movie_names[0]:
                            pos_formatted += pos_movie
                        else:
                            pos_formatted += '\", \"' + pos_movie
                    response_components += pos_sentiment[resp_index] % pos_formatted + ' '
                        # response_components += pos_sentiment[resp_index] % pos_movie_names + ' '
                if neg_movie_names != []:
                    neg_formatted = ''
                    for neg_movie in neg_movie_names:
                        if neg_movie == neg_movie_names[-1]:
                            neg_formatted += '\" and \"' + neg_movie
                        elif neg_movie == neg_movie_names[0]:
                            neg_formatted += neg_movie
                        else:
                            neg_formatted += '\", \"' + neg_movie
                    response_components += neg_sentiment[resp_index] % neg_formatted + ' '
                response = response_components
                for index in movie_indexes:
                    self.input_ratings[index] = sentiment
                    self.num_recs += 1
                # response = multi_titles[resp_index]
            # If no movie found matching name
            elif len(movies) == 0:
                title = title[0]
                if title.find("A") == 0 or title.find("An") == 0 or title.find("The") == 0:
                    article_loc = title.find(" ")
                    article = title[0:article_loc]
                    title = title[article_loc + 1:]
                    title = title + ", " + article
                pos_movies = self.find_movies_closest_to_title(title)
                self.disambiguate_sentiment = sentiment
                if len(pos_movies) == 0:
                    response = dont_know[resp_index] % title[0]
                elif len(pos_movies) == 1:
                    prop_title = self.titles[pos_movies[0]]
                    response = "Did you mean %s?" % prop_title[0]
                    self.spell_check = True
                    self.candidates = pos_movies
                else:
                    pos_titles = []
                    for index in pos_movies:
                        pos_titles.append(self.titles[index][0])
                    self.candidates = movies
                    response = disambiguate_resp[0]
                    for movie in pos_titles:
                        response += movie + " or "
                    response = response[:len(response)-4]
                    response += "?"
                    self.disambiguating = True
                    self.disambiguate_sentiment = sentiment
            elif len(movies) > 1:
                pos_titles = []
                for index in movies:
                    pos_titles.append(self.titles[index][0])
                self.candidates = movies
                response = disambiguate_resp[0]
                for movie in pos_titles:
                    response += movie + " or "
                response = response[:len(response)-4]
                response += "?"
                self.disambiguating = True
                self.disambiguate_sentiment = sentiment
            elif sentiment == 0:
                response = neutral[resp_index] % title[0]
            else:  
                if sentiment == 1 or sentiment == 2:
                    response = pos_sentiment[resp_index] % title[0]
                else:
                    response = neg_sentiment[resp_index] % title[0]
                self.num_recs += 1
                self.input_ratings[movies[0]] = sentiment

        else:
            title = self.extract_titles(line)
            sentiment = self.extract_sentiment(line)
            if len(title) > 0:
                movies = self.find_movies_by_title(title[0])
            if len(title) == 0:
                response = not_movie[resp_index] 
            elif len(title) > 1:
                response = multi_titles[resp_index]
            elif len(movies) == 0:
                response = dont_know[resp_index] % title[0]
            elif len(movies) > 1:
                response = not_clear[resp_index] % title[0]
            elif sentiment == 0:
                response = neutral[resp_index] % title[0]
            else:  
                if sentiment == 1:
                    response = pos_sentiment[resp_index] % title[0]
                else:
                    response = neg_sentiment[resp_index] % title[0]
                self.num_recs += 1
                self.input_ratings[movies[0]] = sentiment

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
        result = []
        line = preprocessed_input
        pointer = line.find("\"")
        start = 0
        while pointer != -1:
            second_pointer = line.find("\"", pointer + 1)
            if second_pointer == -1:
                break
            title = line[pointer+1:second_pointer]
            result.append(title)
            pointer = line.find("\"", second_pointer + 1)
        return result

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
        result = []
        is_year = False
        alt_title = False
        if title.find("(") != -1:
            year = title[title.find("("):title.find(")")+1]
            title = title[:title.find("(")-1]
            is_year = True
        if title.find("A") == 0 or title.find("An") == 0 or title.find("The") == 0:
            article_loc = title.find(" ")
            article = title[0:article_loc]
            title = title[article_loc + 1:]
            title = title + ", " + article
        if is_year:
            title = title + " " + year
        for i, movie in enumerate(self.titles):
            if is_year:
                if title == movie[0]:
                    result.append(i)
            elif self.creative:
                title_manipulate = title
                new_title = movie[0][:len(title) + 1]
                second = movie[0][movie[0].find("("): len(movie[0])]
                if any(c.isalpha() for c in second):
                    second_title = second[second.find("(") + 1:second.find(")")]
                    if title == second_title:
                        result.append(i)       
                if new_title[len(new_title) - 1] == ' ':
                    title_manipulate = title + ' '
                elif new_title[len(new_title) - 1].isalpha():
                    new_title = movie[0][:len(title) + 1]
                else:
                    new_title = movie[0][:len(title)]
                if title_manipulate == new_title:
                    result.append(i)
            else:
                new_title = movie[0][:movie[0].find("(")-1]
                if title == new_title:
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
        our_titles = self.extract_titles(preprocessed_input)
        for item in our_titles:
            term = "\"" + item + "\""
            preprocessed_input = preprocessed_input.replace(term, '')
        
        meaning_changers = ['never', 'don\'t', 'didn\'t', 'no', 'not', 'hardly']
        strong_sentiment = ['loved', 'hated', 'really', 'terrible', 'love', 'hate', 'despise', 'adore', 'disgusting', 'thrilled']
        sum = 0
        word = ''
        output = ''
        our_bool = False
        is_strong = False
        for c in preprocessed_input:
            if c.isalpha() or c == '\'':
                word += c.lower()
            else:
                if word:
                    output = p.stem(word, 0, len(word) - 1)
                    if output == 'enjoi': output = 'enjoy'
                    if output in self.sentiment or word in self.sentiment:
                        if output in self.sentiment:
                            ending = self.sentiment[output]
                        else: ending = self.sentiment[word]
                        val = 0
                        if ending == 'pos': 
                            val = 1
                        if ending == 'neg': 
                            val = -1
                        if our_bool:
                            val *= -1
                        sum += val
                        our_bool = False
                    if word in meaning_changers :
                        our_bool = True
                    if word in strong_sentiment:
                        is_strong = True
                word = ''
        if sum > 0: 
            if self.creative:
                return 2
            else:
                return 1
        elif sum == 0:
            return 0
        else: 
            if self.creative:
                return -2
            else:
                return -1

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
        movie_titles = self.extract_titles(preprocessed_input)
        start = 0
        prev = 0
        answer = []
        meaning_changers = ['never', 'don\'t', 'didn\'t', 'no', 'not', 'hardly']
        for title in movie_titles:
            index = preprocessed_input.find(title)
            last_word_start = preprocessed_input.rfind(' ', 0, index - 2)
            last_word_end = preprocessed_input.rfind(' ', 0, index - 1)
            last_word = preprocessed_input[last_word_start + 1: last_word_end]
            end = index + len(title)
            if title == movie_titles[-1]:
                sent = self.extract_sentiment(preprocessed_input[start:index]) + self.extract_sentiment(preprocessed_input[end:])
            else:
                sent = self.extract_sentiment(preprocessed_input[start:index])
            if sent == 0:
                sent = prev
            if sent > 1:
                sent = 1
            elif sent < -1:
                sent = -1
            elif sent == 0:
                sent = prev
            if last_word in meaning_changers:
                sent *= -1
            answer.append((title, sent))
            prev = sent
            start = end
        return answer

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
        distances = []
        count = 0
        minValue = max_distance
        title = title.lower()
        for t in self.titles:
            lower_title = t[0].lower()
            paren_index = lower_title.find('(')
            new_title = lower_title[:paren_index - 1]
            m = len(new_title)
            n = len(title)
            D = np.zeros((m + 1, n + 1))
            for i in range(m + 1):
                D[i][0] = i
            for j in range(n + 1):
                D[0][j] = j
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if new_title[i - 1] == title[j - 1]:
                        D[i][j] = D[i-1][j-1]
                    else:
                        D[i][j] = min(D[i-1, j], D[i, j-1], D[i-1][j-1]) + 1
            distances.append([D[m][n], new_title])
            if D[m][n] < minValue:
                minValue = D[m][n]
        minValueList = []
        for dist in distances:
            if dist[0] <= minValue:
                minValueList.append(count)
            count += 1
        return minValueList

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
        result = []
        if clarification[len(clarification) - 1].isalpha() == False and clarification[len(clarification) - 1].isdigit() == False:
            clarification = clarification[:len(clarification) - 2]
        for movie in candidates:
            if clarification in self.titles[movie][0] and len(clarification) > 3:
                result.append(movie)
            new_clarification = " " + clarification + " "
            if new_clarification in self.titles[movie][0]:
                result.append(movie)
        if len(result) == 0:
            if clarification[0].isdigit(): 
                result.append(candidates[int(clarification)])
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
        binarized_ratings = np.zeros_like(ratings)
        shape = ratings.shape
        for i in range(shape[0]):
            for j in range(shape[1]):
                if ratings[i][j] > threshold:
                    binarized_ratings[i][j] = 1
                elif ratings[i][j] <= threshold and ratings[i][j] > 0:
                    binarized_ratings[i][j] = -1

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
        if (np.linalg.norm(u) * np.linalg.norm(v)) == 0:
            return 0
        similarity = np.dot(u,v) / (np.linalg.norm(u) * np.linalg.norm(v))
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
        shape = ratings_matrix.shape
        sim_to_index = {}
        for j, row in enumerate(ratings_matrix):
            if user_ratings[j]: continue
            sim_sum = 0
            for i, index in enumerate(user_ratings):
                if index:
                    current_sim = self.similarity(row, ratings_matrix[i])
                    sim_sum += current_sim * index
            sim_to_index[j] = sim_sum
        top_k = sorted(sim_to_index.items(), key=lambda x:x[1], reverse=True)
        recommendations = sorted(sim_to_index, key=sim_to_index.get, reverse=True)[:k]

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
        Howdy, partner! We are gonna have a hog-killin' time figuring out the next movie you are going to watch. 
        Please tell me about 5 movies you have seen that were either an ace in the hole or a snake in your boot. 
        Make sure to include only one movie name per line and ensure the name of the movie is in quotes along with 
        the year of the movie in parentheses (if you don't do this you might end up swimming with the fishes). Once 
        I have the names of the movies you have watched, I will make you recommendations. Feel free to say yes if 
        you want to hear more recommendations or no if have had enough. Enough dilly dallying. Let's get to talking!
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
