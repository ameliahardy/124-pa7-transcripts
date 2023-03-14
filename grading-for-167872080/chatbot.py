# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import porter_stemmer as stemmer
import re


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'moviebot'
        self.stemmer = stemmer.PorterStemmer()

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        
        # data structures needed to handle bot recommendation logic. 
        self.user_ratings = np.zeros(ratings.shape[0])
        self.num_user_ratings_added = 0 
        self.supply_recommendations = False
        self.user_recommendations = None
        self.user_recommendations_index = 0

        # data structures for building bot responses. 
        self.response_index = 0 

        # Added response lists that store various generic responses.
        self.no_movie_response = [
            "I'm not sure if I have heard of \"{}\". Maybe it is called something else?",
            "Sorry, I was not able to find \"{}\". Are there any other movies you have seen?",
            "There are no movies called \"{}\" in my database. Perhaps the movie you are thinking of has a different title?",
            "I've never heard of \"{}\", sorry... tell me about another movie you like."
        ]
        self.multiple_matched_titles = [
            "I found more than one movie for \"{}\". Can you clarify?",
            "I seemed to have discovered multiple movies for \"{}\". Can you be more specific.",
            "Hmmm... I found multiple matches for \"{}\". Are you sure that is the right name?",
            "Cool! \"{}\" seems to be a popular title. Can you clarify?"
        ]
        self.neutral_sentiment = [
            "Sorry, I am not sure if you liked \"{}\". Tell me more about it!",
            "Can you be more specific about \"{}\". I'm not sure how you feel.",
            "I'm not sure how you feel about \"{}\". Can you tell me more please?",
            "Interesting.... Can you tell me more about how you feel about \"{}\"."
        ]
        self.positive_sentiment = [
            "Ok, you like \"{}\"! Tell me more.",
            "Great, I see you enjoyed \"{}\". Are there any other movies you have seen?",
            "Nice, I like \"{}\" too. What else?",
            "Cool, I have heard of \"{}\" before. Are there any others?"
        ]
        self.negative_sentiment = [
            "I'm sorry you did not like \"{}\". Tell me about some other movies.",
            "Interesting, I have not seen \"{}\" yet. What else have you seen that you do not like?",
            "I will stay away from \"{}\". Good to know! What else?",
            "Ok, you did not enjoy \"{}\". Are there other movies you have seen?"
        ]

        if self.creative: 
            self.positive_sentiment = [
            "Gotcha. Hypothetically, you've said to have like \"{}\"! Now, please tell me more.",
            "I also know \"{}\". Now, technically, are there any other movies you have seen?",
            "I also know the movie \"{}\". I watched it when I was at Harvard. Now, tell me about some other movies.",
            "Everyone knows \"{}\", well hypothetically at least. What else have you seen?"
            ]
            self.negative_sentiment = [
            "Look. I'm sorry you didn't like \"{}\", but facts don't care about your feelings. So don't waste my time and how about you tell me about some other movies.",
            "Interesting. I've not seen \"{}\" yet, meaning it must be terrible. What else have you seen that you hypothetically do not like?",
            "Wow, okay. I now know that under no circumstances will I watch \"{}\". Now, what else?",
            "Like I said earlier. Facts don't care about your feelings, but it is unfortunate that you didn't like \"{}\". What else?"
            ]
            self.multiple_matched_titles = [
            "Look, I found more than one movie for \"{}\". Please don't waste my time. Hypotetically, could you clarify?",
            "When I was at Harvard, they always taught us to be specific. You did not do that. I found more than one movie for \"{}\". Could you clarify?",
            "You lack the ability to give all the details, and I now have found more than one movie title for \"{}\". Please clarify for me.",
            "According to my calculations, there are several movies with the title \"{}\". Could you clarify for me?",

            ]
            self.no_movie_response = [
            "Look. I went to Harvard and UCLA and have still never heard of \"{}\", so you must be wrong. Is it hypothetically called something else?",
            "According to my calculations, I don't think there is any movies with the title \"{}\". Are there any other movies you have seen?",
            "I know you may think that \"{}\" is a movie, but it is not, and facts don't care about your feelings. What else could it be called?",
            "I really do not think that \"{}\" is a movie title. Now, hypothetically, are there any other movies you have seen?",
            ]
            self.neutral_sentiment = [
            "Look, I don't know what this new language that this new generation speaks with, and I am not sure if you liked \"{}\". Tell me more about it.",
            "Again, this is not somethign I understand. Please rephrase, because I cannot tell if you like  \"{}\".",
            "According to my calculations, I will need you to rephrase this statement because I cannot tell if you like  \"{}\".",
            "I cannot tell if you liked \"{}\". Hypothetically, please reword your statement."
            ]
            
            self.arbitrary_negative_responses = [
                "Look, I am sorry that you are feeling \"{}\", but facts don't care about your feelings.", 
                "It does suck that you are feeling \"{}\", but everyone in the world has problems.",
                "Yeah. I'm sorry to hear that. I have also felt \"{}\" before, but facts don't care about your feelings.",
                "You feel \"{}\"? Hypothetically, that good to hear, and I offer you my deepest condolences."
            ]

            self.arbitrary_postive_responses = [
                "That is great to hear that you're feeling \"{}\". According to my calculations, that means it's been a good day.", 
                "It is always a good thing when you are feeling \"{}\".",
                "I'm glad you feel \"{}\". Just remember that facts don't care about your feelings so don't let that postitive energy carry you away.",
                "Excellent. I'm very happy for you. Your energy is spreading to me, and hypothetically, I'm also feeling \"{}\"."
            ]
            
            self.arbitrary_input_responses = [
                "Look. That's not what we're here to talk about. Please stay on track.",
                "What are you saying? Please, for the sake of the political climate, please return to the subject of movies.",
                "Why are you dodging the question? We're here to talk about movies.",
                "Hypothetically, if you wanted to discuss this matter, there are other forums to do so. Technically, is for movies.",
            ]

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

        greeting_message = "How can I help you?"

        if self.creative: 
            greeting_message = "Hello. I am Ben Shapiro. Aside from my political commentaries, I spend time watching movies. According to my calculations, I'd be able to help you find new movies you might like. Hypothetically, how could I help you?"

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

        if self.creative: 
            goodbye_message = "I hope I could help today. According to my calculations, I'm very busy and must go now. Have a good day."

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
            response = self.processCreativeMode(line)
        else:
            response = self.processStarterMode(line)
        
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return response
    
    def processStarterMode(self, line):
        # Note should we supply title instead of user input title?
        line_movie_titles = self.extract_titles(line)
        line_sentiment = self.extract_sentiment(line)

        # Build up extracted movies list
        matching_movies = []
        for title in line_movie_titles:
            extracted_movie = self.find_movies_by_title(title)
            if extracted_movie:
                matching_movies.append(extracted_movie)
        
        # Case where we are currently supplying user recommendations. 
        if self.supply_recommendations and line.lower() == "no":
            self.supply_recommendations = False 
            self.user_recommendations_index = 0
            self.user_recommendations = None 
            # not sure if we should reset each time the user says no may remove the line below 
            self.num_user_ratings_added = 0 
            response = "Got it. Tell me more above movies you have seen."
            return response 
        if self.supply_recommendations and line.lower() == "yes":
            rec_idx = self.user_recommendations[self.user_recommendations_index]
            rec_title = self.titles[rec_idx][0]
            response = "Given what you have told me, I think you would like {}. Would you like more recommendations?".format(rec_title)
            response += " (enter 'no' to stop and 'yes' to continue)"
            self.user_recommendations_index += 1
            return response
        
        # Case where we are currently supplying movie recs for the first time.
        if self.num_user_ratings_added > 4:
            self.supply_recommendations = True
            self.user_recommendations = self.recommend(self.user_ratings, self.ratings)
            rec_idx = self.user_recommendations[self.user_recommendations_index]
            rec_title = self.titles[rec_idx][0]
            response = "Given what you have told me, I think you would like {}. Would you like more recommendations?".format(rec_title)
            response += " (enter 'no' to stop and 'yes' to continue)"
            self.user_recommendations_index += 1
        # Case where multiple movie titles were supllied in one line.
        elif len(line_movie_titles) > 1:
            response = "Sorry do you mind specifying only one movie at a time? I am not able to handle multiple titles in one line."
        # Case where no movies where extracted from supplied user title. 
        elif len(matching_movies) == 0 and len(line_movie_titles) > 0:
            user_movie = line_movie_titles[0]
            response = self.no_movie_response[self.response_index].format(user_movie)
            self.response_index += 1
        # Case where multiple movies are matched to one title.
        elif len(matching_movies) > 1 and len(line_movie_titles) == 1:
            user_movie = line_movie_titles[0]
            response = self.multiple_matched_titles[self.user_recommendations_index].format(user_movie)
            self.user_recommendations_index += 1
        # Case where line sentiment is neutral for the user and we found a matching movie.
        elif len(matching_movies) > 0 and line_sentiment == 0:
            user_movie = line_movie_titles[0]
            response = self.neutral_sentiment[self.user_recommendations_index].format(user_movie)
            self.user_recommendations_index += 1
        # Case where user supplies some sentiment about a valid movie title.
        elif len(matching_movies) == 1 and line_sentiment != 0:
            user_movie = line_movie_titles[0]
            # Add the rating to current user's ratings.
            movie_idx = matching_movies[0]
            self.user_ratings[movie_idx] = line_sentiment
            self.num_user_ratings_added += 1
            response = self.negative_sentiment[self.response_index] if line_sentiment == -1 else self.positive_sentiment[self.response_index]
            response = response.format(user_movie)
            self.response_index += 1
        else:
            response = "Hmmmm. I am having trouble understanding. Do you mind rephrasing what you are trying to say?"
            
        # reset indicies for bot responses.
        if self.response_index > 3:
            self.response_index = 0

        return response
    
    def processCreativeMode(self, line):
        # Note should we supply title instead of user input title?
        line_movie_titles = self.extract_titles(line)
        line_sentiment = self.extract_sentiment(line)
        has_question_mark = 1 if '?' in line else 0

        # reset indicies for bot responses.
        if self.response_index > 3:
            self.response_index = 0

        if len(line_movie_titles) == 0 and has_question_mark == 0:
            words = line.split()

            sentiment, sentiment_word = 0, 0
            for idx, stem in enumerate(words):
                if stem in self.sentiment:
                    if self.sentiment[stem] =='pos':
                        sentiment = 1
                        sentiment_word = stem
                    else:
                        sentiment = -1
                        sentiment_word = stem

            if sentiment == 1: 
                response = self.arbitrary_postive_responses[self.response_index].format(sentiment_word)
                self.response_index += 1
                return response

            if sentiment == -1:
                response = self.arbitrary_negative_responses[self.response_index].format(sentiment_word)
                self.response_index += 1
                return response

        # Build up extracted movies list
        matching_movies = []
        for title in line_movie_titles:
            extracted_movie = self.find_movies_by_title(title)
            if extracted_movie:
                matching_movies.append(extracted_movie)
        
        # Case where we are currently supplying user recommendations. 
        if self.supply_recommendations and line.lower() == "no":
            self.supply_recommendations = False 
            self.user_recommendations_index = 0
            self.user_recommendations = None 
            # not sure if we should reset each time the user says no may remove the line below 
            self.num_user_ratings_added = 0 
            response = "Technically, I know about that movie. So, hypotetically, what is other movies you like?"
            return response 
        if self.supply_recommendations and line.lower() == "yes":
            rec_idx = self.user_recommendations[self.user_recommendations_index]
            rec_title = self.titles[rec_idx][0]
            response = "Well, according to my calculations, I think you would like {}. Hypothetically, would you want to see more recommendations?".format(rec_title)
            response += " (enter 'no' to stop and 'yes' to continue)"
            self.user_recommendations_index += 1
            return response
        
        # Case where we are currently supplying movie recs for the first time.
        if self.num_user_ratings_added > 4:
            self.supply_recommendations = True
            self.user_recommendations = self.recommend(self.user_ratings, self.ratings)
            rec_idx = self.user_recommendations[self.user_recommendations_index]
            rec_title = self.titles[rec_idx][0]
            # response = "Given what you have told me, I think you would like {}. Would you like more recommendations?".format(rec_title)
            response = "Now look. According to my calculations, if what you have told me is hypothetically true, I think you would like {}. Would you like more recommendations?".format(rec_title)
            response += " (enter 'no' to stop and 'yes' to continue)"
            self.user_recommendations_index += 1
        # Case where multiple movie titles were supllied in one line.
        elif len(line_movie_titles) > 1:
            response = "Sorry do you mind specifying only one movie at a time? I am not able to handle multiple titles in one line."
        # Case where no movies where extracted from supplied user title. 
        elif len(matching_movies) == 0 and len(line_movie_titles) > 0:
            user_movie = line_movie_titles[0]
            response = self.no_movie_response[self.response_index].format(user_movie)
            self.response_index += 1
        # Case where multiple movies are matched to one title.
        elif len(matching_movies) > 1 and len(line_movie_titles) == 1:
            user_movie = line_movie_titles[0]
            response = self.multiple_matched_titles[0].format(user_movie)
        # Case where line sentiment is neutral for the user and we found a matching movie.
        elif len(matching_movies) > 0 and line_sentiment == 0:
            user_movie = line_movie_titles[0]
            response = self.neutral_sentiment[0].format(user_movie)
        # Case where user supplies some sentiment about a valid movie title.
        elif len(matching_movies) == 1 and line_sentiment != 0:
            user_movie = line_movie_titles[0]
            # Add the rating to current user's ratings.
            movie_idx = matching_movies[0]
            self.user_ratings[movie_idx] = line_sentiment
            self.num_user_ratings_added += 1
            response = self.negative_sentiment[self.response_index] if line_sentiment == -1 else self.positive_sentiment[self.response_index]
            response = response.format(user_movie)
            self.response_index += 1
        else:
            # response = "Hmmmm. I am having trouble understanding. Do you mind rephrasing what you are trying to say?"
            # response = "I'm sorry. I do not understand the words you are saying. Hypothetically could you rephrase what you said?"
            lower_line = line.lower()

            if "what is" in lower_line: 
                response = "Now look. I'm a very busy individual. I'm not here to answer your questions."

            elif "can you" in lower_line: 
                response = "Did you just ask me a question? No. Technically, I'm not your personal assistant."
            else: 
                response = self.arbitrary_input_responses[self.response_index]
                self.response_index += 1
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
        pattern = r'"(.*?)"'
        titles = re.findall(pattern, preprocessed_input)

        non_movie_starters = {"i like", "i love", "i am", "i think", "i feel", "i hate", "i dislike"}
        lowered = preprocessed_input.lower()
        
        if len(titles) or not self.creative:
            return titles 
        
        titles = []
        # check if there is a movie without quotes given
        preprocessed_input = preprocessed_input.replace('!', '')
        preprocessed_input = preprocessed_input.lower().split(' ')
        start_index = 0
        if len(titles) == 0:
                if len(preprocessed_input) >= 3: # we only want to check for non-quote titles if the query is >= 3
                    start_index = 0
                    end_index = 1
                    while start_index < len(preprocessed_input) - 1:
                        cur_attempt = preprocessed_input[start_index: end_index + 1]
                        s = ""
                        for word in cur_attempt:
                            s += word + " "
                        s = s[:-1]
                        indices = self.find_movies_by_title(s)  # check if the title we created matches a title in database
                        if len(indices) != 0 and start_index > 1:
                            return [s]
                            # break
                        if end_index + 1 < len(preprocessed_input):
                            end_index += 1
                        else:
                            start_index += 1
                            end_index = start_index + 1

        starts = False
        for phrase in non_movie_starters:
            if lowered.startswith(phrase):
                starts = True

        if self.creative and starts and start_index > 2:
            return []
 
        return titles

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
        movie_indices = []
        stripped = title.replace(',', '').lower()
        parsed_title = stripped.split(' ')
 
        if not self.creative:
            alpha = 1
        else:
            alpha = 6
 
        for i in range(len(self.titles)):
            check = True
            cur_movie = self.titles[i][0].replace(',', '').lower()
            split_cur = cur_movie.split()
  
            if len(split_cur) > len(parsed_title) + alpha:
                continue
 
            for word in parsed_title:
                if word not in split_cur:
                    check = False
                    break
            if check:
                movie_indices.append(i)
               
        return movie_indices

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
        words = preprocessed_input.split()

        # Handle negation word logic 
        negation_words = {"can't", "can not", "did not", "didn't", "not", "never"}
        negation_idxs, opposite = np.zeros(len(words)), False
        for idx, word in enumerate(words):
            if word in negation_words:
                opposite = True
            
            if opposite:
                negation_idxs[idx] = 1

            if word.find(',') != -1:
                opposite = False

        # Stem words for sentiment dictionary
        stemmed_words = [self.stemmer.stem(word) for word in words]

        # Note: had  to hardcode the 'enjoi' stem because of provided stemmer error.
        # Also, in the if statement 'enjoi' must come first otherwise you will get a 
        # key error when indexing the sentiment dictionary.
        sentiment = 0
        for idx, stem in enumerate(stemmed_words):
            if stem in self.sentiment or stem == 'enjoi':
                if negation_idxs[idx]:
                    if  stem == 'enjoi' or self.sentiment[stem] =='pos':
                        sentiment -= 1
                    else:
                        sentiment += 1
                    continue

                if stem == 'enjoi' or self.sentiment[stem] =='pos':
                    sentiment += 1
                else:
                    sentiment -= 1

        # Based on ratio of pos to neg words output final sentiment
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
        sentiment_word_idxs = []
        sentiment_word_values = []

        titles = self.extract_titles(preprocessed_input)
        user_title_has_year = [bool(re.search(r'\(\d+\)', title)) for title in titles]
        matching_movies = [self.find_movies_by_title(title) for title in titles]

        # Stem words for sentiment dictionary
        no_periods = re.sub(r'\.', '', preprocessed_input)
        words = no_periods.split()
        stemmed_words = [self.stemmer.stem(word) for word in words]

        # Handle negation word logic 
        negation_words = {"can't", "can not", "did not", "didn't", "never", "not"}
        negation_idxs, opposite = np.zeros(len(words)), False
        for idx, word in enumerate(words):
            if word in negation_words:
                opposite = True
            
            if opposite:
                negation_idxs[idx] = 1

            if word.find(',') != -1:
                opposite = False

        # Stem words for sentiment dictionary
        stemmed_words = [self.stemmer.stem(word) for word in words]

        # Note: had  to hardcode the 'enjoi' stem because of provided stemmer error.
        # Also, in the if statement 'enjoi' must come first otherwise you will get a 
        # key error when indexing the sentiment dictionary.
        for idx, stem in enumerate(stemmed_words):
            if stem in self.sentiment or stem == 'enjoi' or stem == "not":
                sentiment_word_idxs.append(idx)
                if negation_idxs[idx] and stem != 'not':
                    if stem == 'enjoi' or self.sentiment[stem] =='pos':
                        sentiment_word_values.append(-1)
                    else:
                        sentiment_word_values.append(1)
                    continue

                if stem != 'not' and (stem == 'enjoi' or self.sentiment[stem] =='pos'):
                    sentiment_word_values.append(1)
                else:
                    sentiment_word_values.append(-1)

        res = []

        if len(sentiment_word_idxs) == 0:
            for idx in matching_movies:
                i = idx[0]
                res.append((self.titles[i][0], 0)) 
        
        if len(sentiment_word_idxs) == 1:
            sentiment = sentiment_word_values[0]
            for idx in matching_movies:
                i = idx[0]
                res.append((self.titles[i][0], sentiment))

        # handle more complicated case where there are multiple sentiments. 
        if len(sentiment_word_idxs) > 1:
            for i, idx_list in enumerate(matching_movies):
                sentiment = sentiment_word_values[i] if i < len(sentiment_word_values) else sentiment_word_values[-1] 
                idx = idx_list[0]
                res.append((self.titles[idx][0], sentiment))
        
        # remove years in the movie titles.
        cleaned = []
        for i in range(len(res)):
            title, val = res[i]
            if user_title_has_year[i] == 0:
                cleaned_title = re.sub(r'\s\(\d+\)', '', title)
                cleaned.append((cleaned_title, val))
            else:
                cleaned.append((title, val))
        
        res = cleaned

        return res 

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
        return []
        pass

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
        identified_candidates = []
       
        if len(clarification) == 1 and clarification.isdigit(): # case: just gives a number
            num = int(clarification) - 1
            identified_candidates.append(candidates[num])
            return identified_candidates
       
        if clarification == "most recent":
            identified_candidates.append(candidates[0])
            return identified_candidates

        if "first one" in clarification:
            identified_candidates.append(candidates[0])
            return identified_candidates
       
        if "second one" in clarification:
            identified_candidates.append(candidates[1])
            return identified_candidates

        if "third one" in clarification:
            identified_candidates.append(candidates[2])
            return identified_candidates
       
        if "fourth one" in clarification:
            identified_candidates.append(candidates[3])
            return identified_candidates

        if "fifth one" in clarification:
            identified_candidates.append(candidates[4])
            return identified_candidates
       
        if "sixth one" in clarification:
            identified_candidates.append(candidates[5])
            return identified_candidates

        if "seventh one" in clarification:
            identified_candidates.append(candidates[6])
            return identified_candidates

        if "eigth one" in clarification:
            identified_candidates.append(candidates[7])
            return identified_candidates
       
        if "ninth one" in clarification:
            identified_candidates.append(candidates[8])
            return identified_candidates
       
        if "tenth one" in clarification:
            identified_candidates.append(candidates[9])
            return identified_candidates
       

        for i in range(len(candidates)):
            # looping through all the candidates
            cur_str_index = candidates[i]
            cur_str = self.titles[cur_str_index][0]
            # print(cur_str)
            if clarification in cur_str:
                identified_candidates.append(cur_str_index)

       
        max_count = -1
        for i in range (len(identified_candidates)):
            # get the count of times the substring shows up in the title
            cur_index = identified_candidates[i]
            cur_title = self.titles[cur_index][0]
            # print(cur_title)


        if len(identified_candidates) == 0:
            # we should see which candidate contains the largest number of the words in clarification

            words_in_clarification = clarification.split()

            dict = {}
            # map candidates to count of words that show up in its title
            # key = index IN CANDIDATES
            for i in range(len(candidates)):
                dict[i] = 0
                cur_title = self.titles[candidates[i]][0]
               

                for word in words_in_clarification:
                    if word in cur_title:
                        dict[i] += 1

            # now see which value in dict is the largest
            max_key = max(dict, key=lambda k: dict[k])

            identified_candidates.append(candidates[max_key])

            # or see which words are only in what once

           
        return identified_candidates

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
        binarized_ratings = np.where(ratings > threshold, 1, np.where(ratings == 0, 0, -1))

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
        dots = np.dot(u, v)
        denom = np.linalg.norm(v) * np.linalg.norm(u)
        similarity = dots / denom 
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
        N = len(user_ratings)

        unrated_movies_idxs = set(np.where(user_ratings == 0)[0])
        rated_movies_idxs = np.where(user_ratings != 0)[0]
        movies_matrix = ratings_matrix[rated_movies_idxs]

        ratings = []
        for i in range(N):
            if i not in unrated_movies_idxs:
                continue

            curr_movie = ratings_matrix[i]

            dots = np.dot(movies_matrix, curr_movie)
            curr_mag = np.linalg.norm(curr_movie) 
            denoms = np.linalg.norm(movies_matrix, axis=1) * curr_mag

            sims = np.divide(dots, denoms + 1e-9)

            modified_user_ratings = user_ratings[rated_movies_idxs]
            curr_rating = np.sum(np.dot(sims, modified_user_ratings))

            ratings.append((i,curr_rating))

        sorted_ratings_idxs = sorted(ratings, key = lambda a: a[1]) 
    
        final_ratings = []
        for i in reversed(range(len(ratings))):
            index, _ = sorted_ratings_idxs[i]
            if index in unrated_movies_idxs:
                final_ratings.append(index)
            
            if len(final_ratings) == k:
                break 

        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        return final_ratings

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
