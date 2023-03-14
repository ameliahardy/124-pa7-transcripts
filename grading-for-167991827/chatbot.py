# PA7, CS124, Stanford
# v.1.0.4
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import numpy as np
import re
import porter_stemmer
import random
p = porter_stemmer.PorterStemmer()

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""
    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        self.name = 'trump_gpt'
        self.creative = creative

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
        self.reco_mode = False
        self.user_inputs = np.zeros(len(self.titles))
        self.reco_count = 0
        self.recommended = []
        self.user_movies = []
        self.neutral_followup = False
        self.neutral_movieid = 0
        self.typo_correction = False
        self.typo_options = []
        self.typo_sentiment = 0

        self.sen_copy = {}
        for w in self.sentiment:
            new_key = p.stem(w, None, None)
            self.sen_copy[new_key] = self.sentiment[w]

        self.pos_bank = [
        ("Yay, you liked ", "! Tell me what you think of another movie"),
        ("You like ", "? Thanks for letting me know. Now tell me another one"),
        ("","? That's a good one. Do you have any other movie you like/dislike?"),
        ("Same, I love ", ", too. What else do you have?"),
        ("OK, ", ", it is. Another one?")
        ]
        self.neg_bank = [
        ("Oops, you disliked ", "! Tell me what you think of another movie"),
        ("You don't like ", "? Thanks for letting me know. Now tell me another one"),
        ("You disliked ","? OK. Each to their own. Do you have any other movie you like/dislike?"),
        ("Didn't know you disliked ", " . What other movie do you like/dislike?"),
        ("Oh no! You disliked ", ":( Another one?")
        ]
        self.reco_bank = [
        ("Given what you told me, you might also like ", ". Would you like more recommendation? Type 'Yes' for more or ':quit' to restart"),
        ("I recommend ", "! It's a good one. Want more recommendation? Type 'Yes' or ':quit' to end session"),
        ("You should watch ", " then. Hope you like it. Type 'Yes' for more recommendation or ':quit' to end and restart"),
        ("Here's my recommendation: ", ". Want more? Type 'Yes'. Wanna quit? Type ':quit'"),
        ("Then check out ", "! My fav, too. Type 'Yes' for more recommendation. ':quit' for restart")
        ]
        self.nodata_bank = [
        "No data found. Tell me another one!",
        "Hmm... never heard of that one yet. Tell me another movie you liked/disliked",
        "Couldn't find that one. Let me know if you have another one you liked/disliked",
        "Oops... nothing found on my end. Do you have another movie you could tell me about?",
        "We couldn't find that movie. Give me another one."
        ]
        self.pos_bank_creative = [
        ("Great job, you liked ", "! That's high energy. How 'bout another movie, your thoughts?"),
        ("You like ", "? Tell me another one that's high energy."),
        ("","? That's beautiful. More movie thoughts?"),
        ("Covfefe, I love ", ", too. What else you got, folks?"),
        ("OK, ", ", Next? Keep it high energy.")
        ]
        self.neg_bank_creative = [
        ("You disliked ", ". Sad! That's a low-energy movie. What about another one?"),
        ("You don't like ", "? Let's a build a wall around that. Now tell me another one"),
        ("","? Absolute enemy of the people. Any other movie you like/dislike?"),
        ("Didn't know you disliked the failing", ", too. Only low-energy folks would like that. What about any other movie?"),
        ("OK, ", ", that's as low evergy as it gets. Another one?")
        ]
        self.reco_bank_creative = [
        ("You might also like ", ". No alternative fact. Type 'Yes' for more or ':quit' to restart"),
        ("I recommend ", " bigly. It's high-energy. Want more? Type 'Yes'. Or ':quit' to end session"),
        ("You better watch ", " then. No fake news. Type 'Yes' for more recommendation or ':quit' to end and restart"),
        ("Here's my recommendation: ", ". Cooler than covfefe.  Want more? Type 'Yes'. Wanna quit? Type ':quit'"),
        ("Then check out ", ". High energy. No lyin'. Type 'Yes' for more recommendation. ':quit' for restart")
        ]  
        self.nodata_bank_creative = [
        "No data found. SAD! Tell me another one.",
        "Never heard of that one yet. Must be irrelevant, bigly. Tell me another movie you liked/disliked",
        "FAKE NEWS! Another one you liked/disliked? covfefe.",
        "We couldn't find that movie. - @realDonaldTrump"
        ]
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        if self.creative == True:
            return "Your 46th president here - the election was rigged! Tweet me a movie @realDonaldTrump."
        greeting_message = "Lovely to meet you! How may I help you today?"
        return greeting_message

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        if self.creative == True:
            return "Already leaving? Lame & low energy. Come back soon."
        goodbye_message = "Thanks for dropping by; have a nice day!"
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
        if self.creative:
            if line == "":
                return "Well, let me tell you folks, we've got a problem here. It's a big problem, believe me. It seems like we've got no input found. None, zero, zilch."
            # check if user asked for additonal recommendations
            if self.reco_mode == True:
                if re.match(r'(yes|yup|yeah|yeah)[.!]?', line.lower()):
                    for i in range(len(self.reco_mode_movies)):
                        if self.reco_mode_movies[i] not in self.recommended:
                            random_msg = random.choice(self.reco_bank)
                            reco_msg = random_msg[0] + self.titles[self.reco_mode_movies[i]][0] + random_msg[1]
                            self.reco_count += 1
                            self.recommended.append(self.reco_mode_movies[i])
                            np.delete(self.reco_mode_movies, i)
                            return reco_msg
                elif re.match(r'(no|nope|n|nah)[.!]?', line.lower()):
                    return "Folks, to end this session, just type ':quit'. Easy, right? Trust me, it's fantastic."
                else:
                    return "Folks, keep going with more recs, say Yes! To quit, say :quit. Trust me."

            if self.typo_correction == True:
                if not re.match(r'(yes|yup|yeah|yeah)[.!]?', line.lower()):
                    if self.extract_titles(line):
                        possible_movieids = self.typo_options
                        self.typo_correction = False
                        return "Got it"
                    else:
                        self.typo_correction = False
                        return "No movie was found folks."
                        
                else:
                    possible_movieids = self.typo_options
                    self.typo_correction == False


            # Extract movie title from user input.
            possible_movieids = []
            input_titles = self.extract_titles(line)
            #if len(input_titles) > 1:
            #    return "One movie at a time, thanks."
            if len(input_titles) == 0:
                return "Don't have anything for you, folks. Make sure you're talking about a movie. Orelse a bigly no no."
            elif len(input_titles) > 1:
                return "One movie at a time, folks. We're not there yet to make our chatbot great again."
            else:
                possible_movieids = self.find_movies_by_title(input_titles[0])

                if len(possible_movieids) == 0:
                    self.typo_options = self.find_movies_closest_to_title(input_titles[0])
                
                    if len(self.typo_options) == 0:
                        return random.choice(self.nodata_bank_creative)
                    elif len(self.typo_options) == 1:
                        self.typo_correction = True
                        return "Did you mean " + self.titles[self.typo_options[0]][0] + "?"
                    else:
                        self.typo_correction = True
                        return "Which one did you mean? [" + ", ".join([self.titles[elem][0] for elem in self.typo_options]) + "]"
                elif len(possible_movieids) > 1:
                    return "I found more than one movie related to that movie. Please clarify!"
                

            # Found movie match. Now collect user sentiment towards it
                user_sentiment = self.extract_sentiment(line)

                # Ask follow-up questions if sentiment is neutral
                if user_sentiment == 0:
                    self.neutral_followup = True
                    self.neutral_movieid = possible_movieids.copy()[0]
                    return "Folks, not sure if you liked the movie. Clarify now!"
                else:
                    # Record user sentiment for this movie match in a list user_inputs (global variable)
                    # If input is redundant, don't record, don't count.
                    if possible_movieids[0] not in self.user_movies:
                        self.user_inputs[possible_movieids[0]] = user_sentiment
                        self.user_movies.append(possible_movieids[0])
                    else:
                        return "You already told me about this movie. Tell me a new one!"
                    
                    if user_sentiment > 0:
                        random_msg = random.choice(self.pos_bank_creative)
                        response = random_msg[0] + self.titles[possible_movieids[0]][0] + random_msg[1]
                    else:
                        random_msg = random.choice(self.neg_bank_creative)
                        response = random_msg[0] + self.titles[possible_movieids[0]][0] + random_msg[1]
                    if self.neutral_followup == True:
                        self.neutral_followup = False

                # After five recorded sentiments, output a recommendation for user
                if len(self.user_movies) == 5:
                    print(response)
                    recommendations = self.recommend(self.user_inputs, self.ratings)
                    for i in range(len(recommendations)):
                        if recommendations[i] not in self.recommended:
                            self.reco_mode = True
                            random_msg = random.choice(self.reco_bank_creative)
                            reco_msg = random_msg[0] + self.titles[recommendations[i]][0] + random_msg[1]
                            self.reco_count += 1
                            self.recommended.append(recommendations[i])
                            reco_record = recommendations.copy()
                            np.delete(reco_record,i)
                            self.reco_mode_movies = reco_record
                            return reco_msg
        else:
            if line == "":
                return "No input found. Please put in an input."
            # check if user asked for additonal recommendations
            if self.reco_mode == True:
                if re.match(r'(yes|yup|yeah|yeah)[.!]?', line.lower()):
                    for i in range(len(self.reco_mode_movies)):
                        if self.reco_mode_movies[i] not in self.recommended:
                            random_msg = random.choice(self.reco_bank)
                            reco_msg = random_msg[0] + self.titles[self.reco_mode_movies[i]][0] + random_msg[1]
                            self.reco_count += 1
                            self.recommended.append(self.reco_mode_movies[i])
                            np.delete(self.reco_mode_movies, i)
                            return reco_msg
                elif re.match(r'(no|nope|n|nah)[.!]?', line.lower()):
                    return "To end this session, type ':quit'"
                else:
                    return "Please enter Yes for more recommendations and :quit to end this session"

            # Extract movie title from user input.
            possible_movieids = []
            input_titles = self.extract_titles(line)
            if len(input_titles) > 1:
                return "One movie at a time, thanks."
            elif len(input_titles) == 0:
                return "Don't have anything for you. Make sure you're talking about a movie. If you are, please enclose your movie title with quotation marks!"
            else:
                possible_movieids = self.find_movies_by_title(input_titles[0])

                if len(possible_movieids) == 0:
                    return random.choice(self.nodata_bank)
                
                elif len(possible_movieids) > 1:
                     return "I found more than one movie related to that movie. Please clarify!"
                
                else:
                # Found movie match. Now collect user sentiment towards it
                    user_sentiment = self.extract_sentiment(line)

                    # Ask follow-up questions if sentiment is neutral
                    if user_sentiment == 0:
                        self.neutral_followup = True
                        self.neutral_movieid = possible_movieids.copy()[0]
                        return "Not sure if you liked the movie. Please clarify further!"
                    else:
                        # Record user sentiment for this movie match in a list user_inputs (global variable)
                        # If input is redundant, don't record, don't count.
                        if possible_movieids[0] not in self.user_movies:
                            self.user_inputs[possible_movieids[0]] = user_sentiment
                            self.user_movies.append(possible_movieids[0])
                        else:
                            return "You already told me about this movie. Tell me a new one!"
                        
                        if user_sentiment > 0:
                            random_msg = random.choice(self.pos_bank)
                            response = random_msg[0] + self.titles[possible_movieids[0]][0] + random_msg[1]
                        else:
                            random_msg = random.choice(self.neg_bank)
                            response = random_msg[0] + self.titles[possible_movieids[0]][0] + random_msg[1]
                        if self.neutral_followup == True:
                            self.neutral_followup = False

                # After five recorded sentiments, output a recommendation for user
                if len(self.user_movies) == 5:
                    print(response)
                    recommendations = self.recommend(self.user_inputs, self.ratings)
                    for i in range(len(recommendations)):
                        if recommendations[i] not in self.recommended:
                            self.reco_mode = True
                            random_msg = random.choice(self.reco_bank)
                            reco_msg = random_msg[0] + self.titles[recommendations[i]][0] + random_msg[1]
                            self.reco_count += 1
                            self.recommended.append(recommendations[i])
                            reco_record = recommendations.copy()
                            np.delete(reco_record,i)
                            self.reco_mode_movies = reco_record
                            return reco_msg

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
            c_list = []
            sentence = preprocessed_input
            year_supplied = False

            if re.match(r'.+ {1}\(\d{4}\)', sentence): # year supplied
                year_supplied = True

            for i in range(len(self.titles)):
                movie = self.titles[i][0]
                tokens = movie.split()
                
                if (tokens[-2].lower()) in ['a', 'an', 'the'] and re.match(r'\(\d{4}[-]?(\d{4})?\)', tokens[-1]):
                    if re.search(r'^.*,', tokens[-3]):
                        v = re.search(r'^(.*),', tokens[-3])
                        no_comma = v.group(1)
                        movie = tokens[-2] +  ' ' + ' '.join(tokens[0:-3]) + ' ' + no_comma + ' ' + tokens[-1]
                        movie = re.sub(' +', ' ', movie)

                if year_supplied == True:
                    if movie.lower() in sentence.lower():
                        c_list.append(movie)
                
                else:
                    if re.search(r'^(.*) \(\d{4}[-]?(\d{4})?\) ?$', movie):
                        m = re.search(r'^(.*) \(\d{4}[-]?(\d{4})?\) ?$', movie)
                        movie = m.group(1)
                        movie = movie.lower()
                    
                    if re.search(r'\b{}\b'.format(re.escape(movie)), sentence.lower()):
                        c_list.append(movie)
                        
            
            return list(set(c_list))
        else:
            return re.findall(r'"(.*?)"', preprocessed_input)

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
            result = []     # list of indices
            pattern = title
            tokens = pattern.split()    # list of words in given title
            
            if (tokens[0].lower() in ['a', 'an', 'the', 'le', 'la', 'les', 'los', 'el', 'un', 'une', 'des', 'las', 'der', 'die', 'das']):
                if pattern not in self.titles:
                    if re.match(r'\(\d{4}\)', tokens[-1]): # year supplied
                        pattern = ' '.join(tokens[1:-1]) + ', ' + tokens[0] + ' ' + tokens[-1]
                    else: # year not supplied
                        pattern =  ' '.join(tokens[1:]) + ', ' + tokens[0]

            for i in range(len(self.titles)):
                if pattern.lower() in self.titles[i][0].lower():
                        result.append(i)
                
            return result

        else:
            result = []
            pattern = title

            tokens = pattern.split()
            if len(tokens) >= 1:
                if re.match(r'\(\d{4}\)', tokens[-1]): # if in parentheses, year supplied
                    m = re.search(r"\((\d{4})\)", tokens[-1])
                    y = m.group(1) # captures the year
                    tokens[-1] = "\({}\)".format(y)
                    pattern = ' '.join(tokens[0:])

                if (tokens[0].lower() in ['a', 'an', 'the', 'le', 'la', 'les', 'los', 'el', 'un', 'une', 'des', 'las', 'der', 'die', 'das']):
                    if pattern not in self.titles:
                        if re.match(r'\\\(\d{4}\\\)', tokens[-1]): # year supplied
                            pattern = ' '.join(tokens[1:-1]) + ', ' + tokens[0] + ' ' + tokens[-1]
                        else: # year not supplied
                            pattern =  ' '.join(tokens[1:]) + ', ' + tokens[0]

            # iterate over all titles & check if it matches 'pattern'; if yes, append index to 'result'
            for i in range(len(self.titles)):
                if len(tokens) >= 1 and re.search(r'^' + pattern + r' ?(?:\(\d{4}\))?$', self.titles[i][0]):
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
          sentiment = chatbot.extract_sentiment(chatbot.preprocess('I liked "The Titanic"'))
          print(sentiment) // prints 1
        :param preprocessed_input: a user-supplied line of text that has been
        pre-processed with preprocess()
        :returns: a numerical value for the sentiment of the text
        """
        # tokenize
        #movie = self.extract_titles(preprocessed_input)
        potential = re.split(r'\s+|(".*?")', preprocessed_input.lower())
        input_tokens = [token for token in potential if token is not None and not re.fullmatch(r'^".*?"$', token) and token != '']

        # initialize variables
        positive = 0
        negative = 0
        negation_mode = False

        # get the stem and assign a sentiment score to each considering negation
        for word in input_tokens:
            stem = p.stem(word, None, None)

            if word in ['never', 'didn\'t', 'don\'t', 'not', 'no', 'isn\'t', 'won\'t', 'couldn\'t']:
                negation_mode = True
            
            if stem in self.sen_copy:
                if self.sen_copy[stem] == 'pos':
                    if negation_mode == True:
                        negative = negative + 1
                    else:
                        positive = positive + 1
                else:
                    if negation_mode == True:
                        positive = positive + 1
                    else:
                        negative = negative + 1

            if re.match(r'.*[.,?!]', word):
                negation_mode = False

        # Final rating
        if positive > negative:
            return 1
        elif positive == negative:
            return 0
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
        sentiments = []
        delimiters = ["but", "although", "however", "."]
        regex_pattern = '|'.join(map(re.escape, delimiters))
        sections = re.split(regex_pattern, preprocessed_input)
        sentiment = 0
        for i in range(len(sections)): 
            titles = self.extract_titles(sections[i])
            # print(sections[i])
            sentiment = self.extract_sentiment(sections[i])
            if sentiment == 0 and i > 0:
                sentiment = 1 if sentiments[-1][1] == -1 else -1
            for title in titles:
                title = title.title()
                sentiments.append((title, sentiment))
        return sentiments


    # I used the nltk implementation in my code as permitted in the Ed Post.
    # https://tedboy.github.io/nlps/_modules/nltk/metrics/distance.html#edit_distance
    def edit_dist_init(self, len1, len2):
        lev = []
        for i in range(len1):
            lev.append([0] * len2)
        for i in range(len1):
            lev[i][0] = i
        for j in range(len2):
            lev[0][j] = j
        return lev
    
    # I used the nltk implementation in my code as permitted in the Ed Post.
    # https://tedboy.github.io/nlps/_modules/nltk/metrics/distance.html#edit_distance
    def edit_dist_step(self, lev, i, j, s1, s2, transpositions=False):
        c1 = s1[i - 1]
        c2 = s2[j - 1]

        # skipping a character in s1
        a = lev[i - 1][j] + 1
        # skipping a character in s2
        b = lev[i][j - 1] + 1
        # substitution
        c = lev[i - 1][j - 1] + 2 * (c1 != c2)

        # transposition
        d = c + 1  # never picked by default
        if transpositions and i > 1 and j > 1:
            if s1[i - 2] == c2 and s2[j - 2] == c1:
                d = lev[i - 2][j - 2] + 1

        # pick the cheapest
        lev[i][j] = min(a, b, c, d)

    # I used the nltk implementation in my code as permitted in the Ed Post.
    # https://tedboy.github.io/nlps/_modules/nltk/metrics/distance.html#edit_distance
    def edit_distance(self, s1, s2, transpositions=False):
        # set up a 2-D array
        len1 = len(s1)
        len2 = len(s2)
        lev = self.edit_dist_init(len1 + 1, len2 + 1)

        # iterate over the array
        for i in range(len1):
            for j in range(len2):
                self.edit_dist_step(lev, i + 1, j + 1, s1, s2, transpositions=transpositions)
        return lev[len1][len2]
    
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
        result = []
        potential = title.lower()
        year_supplied = False
        min_val = max_distance

        tokens = potential.split()
        if len(tokens) == 0:
            return result
        
        if re.match(r'\(\d{4}\)', tokens[-1]): # year supplied
            year_supplied = True
        
        dict_val = {}

        for i in range(len(self.titles)):
            
            movie = self.titles[i][0]
            if year_supplied == False: # year not supplied
                if re.search(r'^(.*) \(\d{4}[-]?(\d{4})?\) ?$', movie):
                    m = re.search(r'^(.*) \(\d{4}[-]?(\d{4})?\) ?$', movie)
                    movie = m.group(1)

            movie = movie.lower()

            if movie[0] != potential[0]:
                movie.replace(movie[0], movie[0].upper(), 1)

            edit = self.edit_distance(potential, movie)
            if  edit <= max_distance:
                if edit <= min_val:
                    dict_val[i] = edit
                    min_val = edit
            
            else:
                if (tokens[0].lower()) in ['a', 'an', 'the']:
                    if year_supplied:
                        potential = ' '.join(tokens[1:-1]) + ', ' + tokens[0] + ' ' + tokens[-1]
                    else:
                        potential = ' '.join(tokens[1:]) + ', ' + tokens[0]
                    
                    movie = movie.lower()

                    if movie[0] != potential[0]:
                        movie.replace(movie[0], movie[0].upper(), 1)
                
                    edit = self.edit_distance(potential, movie)
                    if  edit <= max_distance:
                        if edit <= min_val:
                            dict_val[i] = edit
                            min_val = edit

            if dict_val:
                min_value = min(dict_val.values()) 
                result = [key for key in dict_val if dict_val[key] == min_value]
            
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
        # if "former", "first": 1
        # if mention year or sth that's in movie title: that one
        

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
        # Binarizes the supplied ratings matrix.                               #
        # WARNING: Do not use self.ratings directly in this function.          #
        # NOTE: Currently returns FLOATS, not ints (-0., -1., 1.)
        ########################################################################
        binarized_ratings = np.where(ratings > threshold, 1, -1) * np.sign(ratings)
        return binarized_ratings

    def similarity(self, u, v):
        """Calculate the cosine similarity between two vectors.
        You may assume that the two arguments have the same shape.
        :param u: one vector, as a 1D numpy array
        :param v: another vector, as a 1D numpy array
        :returns: the cosine similarity between the two vectors
        """
        ########################################################################
        # Computes cosine similarity between the two vectors.             #
        ########################################################################
        len1 = np.linalg.norm(u)
        len2 = np.linalg.norm(v)
        similarity = np.dot(u, v) / (len1 * len2) if len1 and len2 else 0
        return similarity

    def sim_movie_with_user_ratings(self, movie_vector, selected_ratings_matrix):
        """
        For a given 'movie_vector', calculates similarity score using self.similarity 
        between it and each movie in selected_ratings_matrix.
        :param selected_ratings_matrix: 2D numpy array; subslice of ratings_matrix,
                                         only with rows of movies that user rated
        :param movie_vector: 1D numpy array of each user's ratings of particular movie 
                            (each row of ratings_matrix)
        :returns: 1D numpy array of similarity scores between movie_vector and each rated_movie
        """
        return np.apply_along_axis(func1d=self.similarity, axis=1, arr=selected_ratings_matrix, v=movie_vector)


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
        # Implement a recommendation function that takes a vector              #
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
        
        # get indices of movies alr rated by user
        already_rated_indices = np.nonzero(user_ratings)    
        nonzero_user_ratings = user_ratings[already_rated_indices]  
        selected_ratings_matrix = ratings_matrix[already_rated_indices] 

        # similarity matrix between all movies & user-rated movies
        sim_matrix = np.apply_along_axis(func1d=self.sim_movie_with_user_ratings, axis=1, arr=ratings_matrix, selected_ratings_matrix=selected_ratings_matrix)
        
        # score matrix between all movies & user-rated movies
        score_matrix = np.apply_along_axis(np.dot, 1, sim_matrix, nonzero_user_ratings)

        # remove already rated movies by setting to sentinel val
        score_matrix[already_rated_indices] = -np.inf

        # get top k indices
        recommendations = np.argsort(score_matrix)[::-1][:k]

        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        return recommendations.tolist()

    ############################################################################
    # 4. Debug info                                                            #
    ############################################################################

    def debug(self, line):
        """
        Return debug information as a string for the line string from the REPL
        NOTE: Pass the debug information that you may think is important for
        your evaluators.
        """
        # print(Chatbot.process(self, 'I liked "Othello"'))
        # print(Chatbot.process(self, 'I liked "Jumanji"'))
        # print(Chatbot.process(self, 'I liked "Dead Man Walking"'))
        # print(Chatbot.process(self, 'I liked "The American President"'))
        # print(Chatbot.process(self, 'I liked "Nixon"'))

        # ratings matrix
        # user_ratings = np.zeros(9125)
        # user_ratings[8514] = 1
        # user_ratings[7953] = 1
        # user_ratings[6979] = 1
        # user_ratings[7890] = 1
        # user_ratings[7369] = -1
        # user_ratings[8726] = -1

        # #print(Chatbot.recommend(self, user_ratings, self.ratings, 5, False))
        # #print(Chatbot.extract_sentiment(self, line))
        
        #print(Chatbot.find_movies_closest_to_title(self, 'BAT-MAAAN'))
        #print(Chatbot.find_movies_closest_to_title(self, 'Sleeping Beaty'))
        #print(Chatbot.find_movies_closest_to_title(self, 'Te'))
        #print(Chatbot.find_movies_closest_to_title(self, 'Blardeblargh'))
        #print(Chatbot.find_movies_closest_to_title(self, 'The Notbook'))
        #title = Chatbot.extract_titles(self, line)
        # print(Chatbot.extract_titles(self, line))

        chatbot = Chatbot()
        sentiments = chatbot.extract_sentiment_for_movies('I liked both "Titanic (1997)" and "Ex Machina".')
        print(sentiments) # prints [("Titanic (1997)", 1), ("Ex Machina", 1)]
        sentiments2 = chatbot.extract_sentiment_for_movies('I liked "Titanic (1997)" but I hated "Ex Machina".')
        print(sentiments2) # prints [("Titanic (1997)", 1), ("Ex Machina", -1)]
        sentiments3 = chatbot.extract_sentiment_for_movies('I liked "Titanic (1997)" but not "Ex Machina".')
        print(sentiments3) # prints [("Titanic (1997)", 1), ("Ex Machina", -1)]
        sentiments4 = chatbot.extract_sentiment_for_movies('I liked "Titanic (1997)" and "Jumanji" but not "Ex Machina".')
        print(sentiments4) # prints [("Titanic (1997)", 1), ("Jumanji", 1"), ("Ex Machina", -1)]
        sentiments5 = chatbot.extract_sentiment_for_movies('I hated "Titanic (1997)" and "Jumanji" but not "Ex Machina".')
        print(sentiments5) # prints [("Titanic (1997)", -1), ("Jumanji", -1"), ("Ex Machina", 1)]
        sentiments55 = chatbot.extract_sentiment_for_movies('I hated "Titanic (1997)" and "Jumanji"')
        print(sentiments55)
        sentiments6 = chatbot.extract_sentiment_for_movies('I hated "Titanic (1997)" and "Jumanji". I liked "Ex Machina".')
        print(sentiments6) # prints [("Titanic (1997)", -1), ("Jumanji", -1"), ("Ex Machina", 1)]
        sentiments7 = chatbot.extract_sentiment_for_movies('I hated "Titanic (1997)" and "Jumanji". I hated "Ex Machina".')
        print(sentiments7) # prints [("Titanic (1997)", -1), ("Jumanji", -1"), ("Ex Machina", -1)]



        s1 = chatbot.extract_sentiment_for_movies(chatbot.preprocess('I liked both "I, Robot" and "Ex Machina".'))
        s2 = chatbot.extract_sentiment_for_movies('I liked "I, Robot" but not "Ex Machina".')
        s3 = chatbot.extract_sentiment_for_movies('I didn\'t like either "I, Robot" or "Ex Machina".')
        s4 = chatbot.extract_sentiment_for_movies('I liked "Titanic (1997)", but "Ex Machina" was not good.')
        print(s1)
        print(s2)
        print(s3)
        print(s4)

        # print(Chatbot.extract_sentiment_for_movies(self, line))
        return ""

    ############################################################################
    # 5. Write a description for your chatbot here!                            #
    ############################################################################
    def intro(self):
        """Return a string to use as your chatbot's description for the user.
        Consider adding to this description any information about what your
        chatbot can do and how the user can interact with it.
        """
        s1 = "This is a chatbot that asks the user for user preferences on 5 different movies. It uses item-item collaborative filtering to then generate movie recommendations to the user. To use this chatbot, please input the movie name in parantheses (with the year it was released in case of ambiguity) and whether or not you liked it. Sample input: 'I like \"Titanic (1997)\".', 'I hated \"Jumanji\".' \n"
        s2 = "Note: If you wish to run the chatbot in creative mode, please exit the program and run the following command: python repl.py --creative"
        return s1 + "\n" + s2 + "\n"

if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
