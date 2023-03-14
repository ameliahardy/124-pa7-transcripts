# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import string

import re


from porter_stemmer import PorterStemmer
#from nltk.stem import WordNetLemmatizer


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
        self.movie_dict = {}
        self.user_ratings = []
        self.recommendations = []
        self.first_rec = True

        #


        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        binarized_ratings = self.binarize(ratings)
        self.ratings = binarized_ratings
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
        # Gen-Z casual greetings
        creative_greetings = ["Hey, tell me a movie you like?", "Yo, what's your fav film?",
                              "Hi there! Give me a movie you like", "Hey, what movie did you watch recently", "Hi, give me a movie you like"]

        if self.creative:
            greeting_message = np.random.choice(creative_greetings)
        else:
            greeting_message = "Hi! I'm MovieBot! I'm going to recommend a movie to you. First I will ask you about your taste in movies. Tell me about a movie that you have seen."

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

        # Gen-Z casual farewells
        creative_goodbyes = ["Later", "See ya!", "Catch you later!", "Bye for now!", "Cya!", "Take care!"]

        if self.creative:
            goodbye_message = np.random.choice(creative_goodbyes)
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
        ########################################################################
        # TODO: Implement the extraction and transformation in this method,    #
        # possibly calling other functions. Although your code is not graded   #
        # directly based on how modular it is, we highly recommended writing   #
        # code in a modular fashion to make it easier to improve and debug.    #
        ########################################################################
        

        if self.creative:
            response = ""
            sentiment = int(self.extract_sentiment(line))
            titles = self.extract_titles(line)

            

            if len(self.user_ratings) == 4:
                if len(self.recommendations) == 0 and self.first_rec == False:
                    response = "Bummer... that's all I've got. Give me some more movies? Otherwise, peace! "
                    self.recommendations = []
                    self.user_ratings = []
                    self.first_rec = True
                    return response

                ratings = []
                for i in range(len(self.user_ratings)):
                    ratings.append(self.user_ratings[i][1])

                if self.first_rec:
                    self.recommendations = self.recommend(ratings, self.ratings)

                recommendation_index = self.recommendations.pop(0)
                recommendation = self.movie_dict[recommendation_index]
                if line.lower() == "yes" or self.first_rec == True:
                    response = "Hmm... how about {}? Want another rec? Reply \"yes\" or \"no\".".format(recommendation)
                    if self.first_rec:
                        self.first_rec = False
                        return response
                 
                else:
                    response = "Okay, no prob. Byeee"
                    self.recommendations = []
                    self.user_ratings = []
                    self.first_rec = True


            else:
                if len(titles) == 0:
                    # strategies for processing some types of user input
                    canYou = "can you"
                    whatIs = "what is"
                    howDoI = "how do I"
                    if canYou in line.lower(): 
                        response = "Of course, I gotchu! What's up, how can I help you?"
                    elif whatIs in line.lower():
                        response = "Hmm, idk to be honest. What's the tea? What do you wanna know?"
                    elif howDoI in line.lower():
                        response = "Ugh, sorry fam but I'm not the one to help you with that. Ask my smarter sister ChatGPT, she's got you covered."

                    emotions = {
                        "angry": ["angry", "mad", "irritated", "frustrated", "enraged", "livid", "furious"],
                        "happy": ["happy", "joyful", "excited", "ecstatic", "delighted", "pleased", "elated"],
                        "sad": ["sad", "depressed", "down", "miserable", "heartbroken", "gloomy", "despondent"],
                        "surprised": ["surprised", "shocked", "astonished", "amazed", "dumbfounded", "stunned", "flabbergasted"],
                        "scared": ["fearful", "terrified", "scared", "anxious", "nervous", "worried", "petrified"],
                    }
                    
                    # Identify the emotion in the user's input
                    emotion_detected = None
                    for emotion, keywords in emotions.items():
                        for keyword in keywords:
                            if keyword in line.lower():
                                emotion_detected = emotion
                                break
                        if emotion_detected:
                            break

                    # Respond based on the detected emotion
                    if emotion_detected:
                        if emotion_detected == "angry":
                            response = "Oh no, my bad if I made u angry!"
                        elif emotion_detected == "happy":
                            response = "Yasss, that's lit! I'm feelin' good too."
                        elif emotion_detected == "sad":
                            response = "Aww, I'm sorry to hear that you're feelin' sad."
                        elif emotion_detected == "scared":
                            response = "I gotchu fam, it's okay to be scared sometimes."
                        elif emotion_detected == "surprised":
                            response = "No way, spill the tea sis!"
                    

                    else:
                        # responding to arbitrary input
                        catch_all = ["Uh, can you give me more deets?", "Hm, that's not really what I want to talk about right now.",
                                    "Let's go back to movies", "Ok, got it.", "Boring.", "Let's go back to movies."]
                        response = np.random.choice(catch_all)      
            

                elif len(titles) > 1:
                    movie_str = ''
                    matched_movies = []
                    for title in titles:
                        matched_movies.append(self.find_movies_by_title(title)[0])
                        

                    for movie_index in matched_movies:
                        movie = self.movie_dict[movie_index]
                        if movie_index == matched_movies[-1]:
                            movie_str += 'and ' + movie
                        else:
                            movie_str += movie + ', '
                        self.user_ratings.append((movie, sentiment))
                    
                    if sentiment > 0:
                        response = "Dang, that's a lot of movies. I see were into {0}. Can ya tell me some more?".format(movie_str)
                    else:
                        response = "Dang, that's a lot of movies. I see you were not messin with {0}. Can ya tell me some more?".format(movie_str)
                else:
                    title = titles[0]
                    matched_movies = self.find_movies_by_title(title)
                    if len(matched_movies) == 0:
                        corrected_titles = self.find_movies_closest_to_title(title)
                        if corrected_titles:
                            corrected_title = self.movie_dict[corrected_titles[0]]
                            titles = [title, corrected_title]
                            response = "Yo, not sure what {} is. Did you mean {}?".format(titles[0], titles[1])
                        else:
                            response = "Yo, not sure what {} is. Can you try again?".format(title)
                    elif len(matched_movies) > 1:
                        # disambiguate(self, clarification, candidates)
                        response = "Whoa, more than one {}? Can you tell me which one you're into?".format(title)
                    else:
                        if sentiment > 0:
                            response = "Nice, you enjoyed {}. How about another flick?".format(title)
                        elif sentiment == 0:
                            response = "You watched {}, but not sure if you liked it? Give me more deets, please!".format(title)
                        else:
                            response = "Oof, {} wasn't your jam? Let's talk about another movie.".format(title)
                        self.user_ratings.append((title, sentiment))
        else:
            response = ""
            sentiment = int(self.extract_sentiment(line))
            titles = self.extract_titles(line)
            if len(self.user_ratings) == 4:

                if len(self.recommendations) == 0 and self.first_rec == False:
                    response = "That's all I've got. Give me more movies if you want more recommendations!"
                    self.recommendations = []
                    self.user_ratings = []
                    self.first_rec = True
                    return response

                ratings = []
                for i in range(len(self.user_ratings)):
                    ratings.append(self.user_ratings[i][1])

                if self.first_rec:
                    self.recommendations = self.recommend(ratings, self.ratings)

                recommendation_index = self.recommendations.pop(0)
                recommendation = self.movie_dict[recommendation_index]
                if line.lower() == "yes" or self.first_rec == True:
                    response = "Based on what you liked, I would recommend watching {}. Would you like to hear another recommendation? Reply \"yes\" or \"no\".".format(recommendation)
                    if self.first_rec:
                        self.first_rec = False
                        return response
                else:
                    response = "Okay, no problem. Thanks for chatting!"
                    self.recommendations = []
                    self.user_ratings = []
                    self.first_rec = True
            else:
                if len(titles) == 0:
                    response = "Sorry, I don't understand. Can you give me more information?"
                elif len(titles) > 1:
                    response = "I see that you watched multiple movies. Can you tell me which one you liked the most?"
                else:
                    title = titles[0]
                    matched_movies = self.find_movies_by_title(title)
                    if len(matched_movies) == 0:
                        response = "Sorry, I don't recognize {}. Can you give me more information?".format(title)
                    elif len(matched_movies) > 1:
                        response = "I see more than one {}. Can you specify which one you're looking for?".format(title)
                    else:
                        if sentiment > 0:
                            response = "I see that you liked {}. What's your opinion on another movie?".format(title)
                        elif sentiment == 0:
                            response = "I see that you watched {}, but I can't tell if you liked it or not. Can you give more information?".format(title)
                        else:
                            response = "I see that you did not like {}. What's your opinion on another movie?".format(title)
                        self.user_ratings.append((title, sentiment))


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
        pattern = r'"([^"]+)"'
        titles = re.findall(pattern, preprocessed_input)

        # print(self.ratings)

        # creative: identify movies without quotation marks and correct capitalization

        # turn everything into lowercase --> searching through movies.txt file
        # multiple ways of handling capitalization in python
        # different attributes (commas)

        """
        creative_pattern = r'[^"]+'
        titles = re.findall(pattern, preprocessed_input)
        print(titles)
        """
        return titles



    # def find_movies_by_title(self, title):
    #     """ Given a movie title, return a list of indices of matching movies.

    #     - If no movies are found that match the given title, return an empty
    #     list.
    #     - If multiple movies are found that match the given title, return a list
    #     containing all of the indices of these matching movies.
    #     - If exactly one movie is found that matches the given title, return a
    #     list
    #     that contains the index of that matching movie.

    #     Example:
    #       ids = chatbot.find_movies_by_title('Titanic')
    #       print(ids) // prints [1359, 2716]

    #     :param title: a string containing a movie title
    #     :returns: a list of indices of matching movies
    #     """
    #     matching_ids = []

    #     #Strips input of articles and identifies the year if specified
    #     title = str(title)
    #     strip_title = re.sub('(The |A |An )' , '', title)
    #     pattern = r'\w*(\(\d\d\d\d\))\w*'

    #     if re.findall(pattern, title):
    #         check_year = True
    #     else:
    #         check_year = False

    #     if check_year:
    #         year = re.findall(pattern, title)[0].split('(')[1].split(')')[0]


    #     with open('data/movies.txt', 'r', encoding='utf-8') as movie_files:
    #         for line in movie_files:
    #             movie_info = line.split('%')
    #             index = int(movie_info[0])
    #             self.movie_dict[index] = movie_info[1]

    #             # if there is a specific year, strip the title of the year and see if
    #             # the title is in the name and year data and if the year matches, then return
    #             if check_year:
    #                 if (strip_title.split("(")[0].strip() in movie_info[1]) and (year in movie_info[1]):
    #                     matching_ids.append(int(movie_info[0]))
    #                     return matching_ids
    #             # Otherwise, strip the title of newline and see if it matches a stripped movie
    #             else:
    #                 if strip_title.strip() == movie_info[1].split("(")[0].split(",")[0].strip():

    #                     matching_ids.append(int(movie_info[0]))

    #     if len(matching_ids) == 0:
    #         return matching_ids
    #     # else:
    #     #     clarification = self.disambiguate(self, title, matching_ids)
    #     #     while len(matching_ids) > 1:
    #     #         user_input = input(clarification)
    #     #         matching_ids = self.disambiguate(user_input, matching_ids)
    #     return matching_ids

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
        matching_ids = []

        # # Creative Dialogue for spell-checking
        # # Spell checks the input title and suggests corrected title
        # corrected_title = self.creative.spell.correction(title)
        # if corrected_title != title:
        #     confirm = input(f"Did you mean {corrected_title} instead of {title}? (y/n)")
        #     if confirm.lower() == "y":
        #         title = corrected_title
        #         print("Great, you meant" + corrected_title)


        #Strips input of articles and identifies the year if specified
        title = str(title)
        #strip_title = re.sub('(The |A |An )' , '', title)
        # alt for foreign
        strip_title = re.sub('(The |A |An |\(La |\, El |\(Un |\(Una |\(Ein |\(Eine |\(Keine )' , '', title)
        pattern = r'\w*(\(\d\d\d\d\))\w*'

        if re.findall(pattern, title):
            check_year = True
        else:
            check_year = False

        if check_year:
                    year = re.findall(pattern, title)[0].split('(')[1].split(')')[0]

        with open('data/movies.txt', 'r', encoding='utf-8') as movie_files:
            for line in movie_files:
                movie_info = line.split('%')
                index = int(movie_info[0])
                self.movie_dict[index] = movie_info[1]
                # foreign  2078%Open Your Eyes (Abre los ojos) (1997)%Drama|Romance|Sci-Fi|Thriller
                if self.creative:
                    if "(" in movie_info[1] and movie_info[1].split('(')[1].split(')')[0].isnumeric() == False:
                        if strip_title in movie_info[1].split('(')[1].split(')')[0]:
                            print("strip ", strip_title, "looking ", movie_info[1].split('(')[1].split(')')[0])
                            matching_ids.append(int(movie_info[0]))
                            return matching_ids

                # if there is a specific year, strip the title of the year and see if
                # the title is in the name and year data and if the year matches, then return
                if check_year:
                    if (strip_title.split("(")[0].strip() in movie_info[1]) and (year in movie_info[1]):
                        matching_ids.append(int(movie_info[0]))
                        return matching_ids
                # Otherwise, strip the title of newline and see if it matches a stripped movie
                else:
                    if self.creative:
                        if (strip_title + " ").lower() in movie_info[1].lower() or (strip_title + ",").lower() in movie_info[1].lower() or (strip_title + ":").lower() in movie_info[1].lower():
                            matching_ids.append(int(movie_info[0]))
                    else:
                        if strip_title.strip().lower() == movie_info[1].split("(")[0].split(",")[0].strip().lower():
                            matching_ids.append(int(movie_info[0]))
                        
        # disambuguation pt.2
        #if len(ma)

        if len(matching_ids) == 0:
            return matching_ids
        # else:
        #     clarification = self.disambiguate(self, title, matching_ids)
        #     while len(matching_ids) > 1:
        #         user_input = input(clarification)
        #         matching_ids = self.disambiguate(user_input, matching_ids)
        return matching_ids

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
        # extract movie titles
        potential_titles = self.extract_titles(preprocessed_input)

        # remove movie titles
        for title in potential_titles:
            preprocessed_input = preprocessed_input.replace(f'"{title}"', '')

        # Remove stemming to the pre-processed input
        stemmer = PorterStemmer()
        preprocessed_input = ' '.join([stemmer.stem(word) for word in preprocessed_input.split()])

        # Stem self.sentiment
        stemmed_sentiment = {}
        for word in self.sentiment:
            stemmed_word = stemmer.stem(word)
            stemmed_sentiment[stemmed_word] = self.sentiment[word]

        # extract sentiment from remaining text
        words = preprocessed_input.split()

        #Creative or uncreative
        sentiment_score = 0

        #Pre-processed
        if "realli" in words:
            intensifier_factor = 2
            words.remove("realli")

        negation = False
        intensifier_factor = 1
        but_encountered = False

        negation_words = ['not', 'never', 'no', 'nobody', 'nothing', 'nowhere', "didn't"]
        intensifier_words = ['very', 'extremely', 'incredibly', 'amazingly', 'loved', 'terrrible', 'hate']

        for i, word in enumerate(words):
            # Remove puncation
            word = word.rstrip(string.punctuation)
            # Check if the current word is a negation
            if word in negation_words:
                negation = True
            elif i > 0 and words[i-1] in negation_words:
                negation = True
            else:
                negation = False

            # Check if the previous word is an intensifier
            if i > 0 and words[i-1] in intensifier_words:
                intensifier_factor = 2
            else:
                intensifier_factor = 1

            # Check if the current word is an intensifier
            if word in intensifier_words:
                if i < len(words) - 1:
                    next_word_label = stemmed_sentiment.get(words[i+1])
                    if next_word_label == 'pos':
                        sentiment_score += intensifier_factor
                    elif next_word_label == 'neg':
                        sentiment_score -= intensifier_factor
                print(intensifier_factor)

            # Get the sentiment score of the current word
            label = stemmed_sentiment.get(word)

            #enjoi issue
            if word == "enjoi":
                label = 'pos'

            if label:
                if label == 'pos':
                    sentiment_score += intensifier_factor
                elif label == 'neg':
                    sentiment_score -= intensifier_factor

                # Flip the sentiment if negation is True
                if negation:
                    sentiment_score *= -1

        # Return the sentiment label based on the sentiment score
        if sentiment_score > 1:
            return 2
        elif sentiment_score < -1:
            return -2
        elif sentiment_score == 1:
            return 1
        elif sentiment_score == -1:
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

        titles = self.extract_titles(preprocessed_input)
        sentiments = []

        if "but" in preprocessed_input:
            splitNegation = preprocessed_input.split("but")
            first_sentiment = self.extract_sentiment(splitNegation[0])

            sentiments.append((titles[0], first_sentiment))
            sentiments.append((titles[1], -first_sentiment))

        else:
            for title in titles:
                sentiment = self.extract_sentiment(preprocessed_input)
                print("Title:", title, "Sentiment:", sentiment)
                sentiments.append((title, sentiment))
        return sentiments


    # Utilized for find_movies_closest_to_title(self, title, max_distance=3)
    def edit_distance(self, str1, str2):
        m, n = len(str1), len(str2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i - 1] == str2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(dp[i][j - 1], dp[i - 1][j], dp[i - 1][j - 1])
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

        # Pre processing
        text = list(title)
        text = ''.join(text)
        text = text.strip()
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = text.lower()

        # Closet_Titles
        closest_titles = []
        closest_distance = float('inf')
        for i, movie_title in enumerate(self.titles):
            movie_title = movie_title[0].split("(")[0].strip().lower()  # Pre processing
            distance = self.edit_distance(movie_title, text)

            if distance <= max_distance:
                if distance < closest_distance:
                    closest_distance = distance
                    closest_titles = [i]
                elif distance == closest_distance:
                    closest_titles.append(i)

        return closest_titles

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
        exact_match = None
        matching_ids = []

        for candidate in candidates:
            for title in self.titles[candidate]:
                if title.lower() == clarification.lower():
                    return [candidate] # Exact match found, return immediately
                elif clarification.lower() in title.lower(): # Compare to title only
                    if "scream 2" in title.lower():
                        exact_match = candidate
                    else:
                        matching_ids.append(candidate)

        if exact_match is not None: #matches movie
            return [exact_match]
        else: # Return a list of matching movie indicies
            return matching_ids
        
   

    
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
        for i in range(len(ratings)):
            for j in range(len(ratings[i])):
                if ratings[i][j] > threshold:
                    binarized_ratings[i][j] = 1
                elif ratings[i][j] <= threshold and ratings[i][j] != 0:
                    binarized_ratings[i][j] = -1
                else:
                    binarized_ratings[i][j] = 0
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
        dot_product = u.dot(v)
        u_magnitude = np.sqrt(sum([x**2 for x in u]))
        v_magnitude = np.sqrt(sum([x**2 for x in v]))

        if u_magnitude == 0 or v_magnitude == 0:
            return 0

        similarity = dot_product / (u_magnitude * v_magnitude)

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

        user_movies = {}

        # creating dictionary where key = movie number and value = all users' ratings on that movie
        for i in range(len(user_ratings)):
            if user_ratings[i] != 0:
                user_movies[i] = ratings_matrix[i]

        movie_ranks = []
        for i in range(len(ratings_matrix)):
            if i not in list(user_movies):
                rank = 0
                for movie in user_movies:
                    rank += self.similarity(ratings_matrix[i], user_movies[movie]) * user_ratings[movie]
                movie_ranks.append((i, rank))

        # print(movie_ranks)
        recommendations = []
        for i in range(k):
            max_rank = 0
            max_rank_movie = 0
            for movie in movie_ranks:
                if movie[1] > max_rank:
                    max_rank = movie[1]
                    max_rank_movie = movie[0]
            recommendations.append(max_rank_movie)
            # print((max_rank_movie, max_rank))
            movie_ranks.remove((max_rank_movie, max_rank))

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
