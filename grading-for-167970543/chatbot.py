# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
from ast import Return
import util

import numpy as np
import random

import re
import nltk

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        if creative:
            self.name = 'yodabot'
        else:
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

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings, 2.5)
        self.user_ratings = np.zeros(len(self.titles))
        self.user_ratings_count = 0
        self.reviewed_movies = []
        
        self.disambiguate_flag = False
        self.disambiguate_indices = []
        self.disambiguated_line = ""
        
        self.recommendations = []
        self.recommendations_count = 0
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
            greeting_message = "Greetings, young padawan. For you what can Yoda do, hmm?"
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
            goodbye_message = "No more help do you require. Already know you, that which you need."
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
        titles = []
        affirmatives = ["yes", "yes!", "yeah", "yeah!", "yes please", "yes please!", "yeh", "yah!", "yah", "ya", "ya!", "yep", "yep!", "yup!", "yup", "y", "ye", "mhm"]
        negatives = ["no", "no.", "no!", "no thanks", "no thanks.", "no thanks!", "no thank you", "no thank you.", "no thank you!", "nope", "nope!", "nah", "n"]
        liked_movie = ["I'm glad you enjoyed ", "Got it, so you liked ", "I see that you liked ", "Awesome, you enjoyed "]
        disliked_movie = ["I'm sorry to hear that you didn't like ", "Okay, you didn't like ", "Got it, you did not like ", "Thanks for letting me know you didn't like "]
        question_words = ["can", "what", "where", "when", "why"]
        recommendations = ["I would also recommend ", "I think you would also like ", "Based on your taste, I bet you would enjoy ", "You should try watching "]
        want_more = ["Would you like another recommendation?", "Want another one?", "How about another recommendation?", "Should I give you another recommendation?"]
        too_many_inputs = ["Sorry, I can only process one movie at a time.", "Could you tell me about each of those movies individually?"]
        
        arbitrary_input_yoda = ["Of movies, you speak not. Speak only of movies, I must.", "Not talking of movies you are. To talk of movies I want.", "More interesting, movies are. About movies I want to hear."]
        liked_movie_yoda = ["glad you enjoyed, I am.", "hrmmm? Like this movie you did, yes.", "you liked. Happy to hear this, Yoda is."]
        disliked_movie_yoda = ["you did not like, hrmm?", "Yoda enjoys. Feel the same way, you do not.", "you did not like."]
        want_more_yoda = ["More movies you want?", "Another recommendation you want?", "One more movie you want?"]
        recommend_yoda = ["also think you'd like, Yoda does. ", "recommends Yoda. ", "Yoda thinks you will enjoy. ", "Yoda suggests. A great movie for you, it is. "]
        i_statements = ["i want", "i need", "i can't", "i will", "i hope", "i don't"]
        i_response_yoda = ["Often talk of your desires and limitations, you do. Talk of movies instead.", "To me for recommendations you come. Yet what you do or don't want, you tell to Yoda."]
        transition_yoda = [" And also, ", " See also I can, ", " Understood I did, "]


        # establishing emotion keywords and respective responses
        anger_keywords = ["frustrated", "mad", "angry", "livid", "upset", "pissed", "stupid"]
        anger_response_yoda = ["A path to the dark side, anger is.", "Control your anger, you must.", "Calm like Yoda, you must be."]
        sadness_keywords = ["sad", "depressed", "depressing", "melancholy", "gloomy", "sadness"]
        sadness_response_yoda = ["Sorry you are sad, Yoda is.", "Feel sad you do, hrmm?", "Feel sad you must not, young padawan"]
        offended_keywords = ["offended", "outraged", "offensive", "outrageous", "distasteful"]
        offended_response_yoda = ["Upset you, Yoda did not mean to.", "Sorry, Yoda is. Feel upset you must not.", "Offend you, Yoda did not mean to."]
        bored_keywords = ["bored", "boring", "lame", "yawn"]
        bored_response_yoda = ["Bored you are, hrmm? Sorry, Yoda is", "Bore you, Yoda did not mean to.", "More interesting, I will try to be."]
        fear_keywords = ["scary", "fearful", "scared", "horrified", "terrified", "afraid", "horrific"]
        fear_response_yoda = ["Scare you, Yoda did not mean to.", "Overcome your fear, you must.", "Fear not, young padawan."]
        happy_keywords = ["happy", "glad", "thrilled", "overjoyed", "ecstatic"]
        happy_response_yoda = ["Glad Yoda is, that you are glad.", "Glad you are happy, Yoda is.", "Like that you are happy, I do."]
           
        # Ensure that there is only one movie in the input line
        titles = self.extract_titles(line)
        
        if self.creative:            
            # disambiguation
            if self.disambiguate_flag:
                new_matches = self.disambiguate(line, self.disambiguate_indices)
                # if we need more specificity
                if len(new_matches) > 1:
                    response = "More than one movie I still find. More can you clarify? The movie is "
                    self.disambiguate_flag = True
                    self.disambiguate_indices = new_matches
                    for i in range(len(new_matches)):
                        if i == len(new_matches) - 1:
                            response += ", or " + self.titles[new_matches[i]][0] + "?"
                        if i == 0:
                            response += self.titles[new_matches[i]][0]
                        else:
                            response += ", " + self.titles[new_matches[i]][0]
                    return response
                elif len(new_matches) == 0:
                    response = "No movies by that name I find. Still, more can you clarify?"
                    self.disambiguate_flag = True
                    return response
                else:
                    titles = [self.titles[new_matches[0]][0]]
                    line = self.disambiguated_line
                    self.disambiguate_flag = False
            
            if self.user_ratings_count >= 5 and self.recommendations_count < len(self.recommendations):
                if line.lower().strip() in affirmatives:
                    if self.recommendations_count == 0:
                        response = self.titles[self.recommendations[self.recommendations_count]][0] + ", you should watch, thinks I. " + random.choice(want_more_yoda)
                    elif self.recommendations_count == len(self.recommendations) - 1:
                        response = random.choice(recommendations) + self.titles[self.recommendations[self.recommendations_count]][0] + ". All the recommendations I have, that is!"
                    else:
                        response = self.titles[self.recommendations[self.recommendations_count]][0] + ", " + random.choice(recommend_yoda) + random.choice(want_more_yoda)
                    self.recommendations_count += 1
                    return response
                elif line.lower() in negatives:
                    if self.recommendations_count == 0:
                        response = "No recommendations to you I will give. Hmm."
                    else:
                        response = "Yoda's recommendations, I hope you enjoy."
                        return response
                else:
                    response = "Another recommendation you want? More clearly, you must speak."
                    return response
            
            # edited for multiple sentiment extraction
            if len(titles) > 1:
                response = ""
                sentiment_array = self.extract_sentiment_for_movies(line)
                for i, sentiment in enumerate(sentiment_array):
                    matching_indices = self.find_movies_by_title(sentiment[0])
                    if sentiment[1] == 0:
                        response += "Sure if you liked \"{}\", I am not. More about it could you tell me?".format(sentiment[0])
                    elif sentiment[1] < 0:
                        response += sentiment[0] + ", " + random.choice(disliked_movie_yoda)
                    else:
                        response += sentiment[0] + ", " + random.choice(liked_movie_yoda)
                    if matching_indices[0] not in self.reviewed_movies and sentiment[1] != 0:
                        self.reviewed_movies.append(matching_indices[0])
                        self.user_ratings_count += 1
                    if i < len(sentiment_array) - 1:
                        response += random.choice(transition_yoda)  
                    self.user_ratings[matching_indices[0]] = sentiment[1]
                return response

            # handling arbitrary inputs / emotions
            elif len(titles) == 0:
                tokens = line.split()
                for token in tokens:
                    stripped_token = re.sub(r'[^\w\s]', '', token)
                    if stripped_token in anger_keywords:
                        return random.choice(anger_response_yoda)
                    if stripped_token in sadness_keywords:
                        return random.choice(sadness_response_yoda)
                    if stripped_token in offended_keywords:
                        return random.choice(offended_response_yoda)
                    if stripped_token in bored_keywords:
                        return random.choice(bored_response_yoda)
                    if stripped_token in fear_keywords:
                        return random.choice(fear_response_yoda)
                    if stripped_token in happy_keywords:
                        return random.choice(happy_response_yoda)
                
                # more arbitrary responses for questions words and I statements
                if tokens[0].lower() in question_words:
                    return "Answer this question, I cannot. Talk about movies, we must."
                if len(tokens) > 1:
                    first_two_words = tokens[0] + " " + tokens[1]
                    if first_two_words.lower() in i_statements:
                        return random.choice(i_response_yoda)
                    # general uncaught arbitrary responses
                return random.choice(arbitrary_input_yoda)
            
            else:

                # Ensure that there is only one movie corresponding to the input
                matching_indices = self.find_movies_by_title(titles[0])
                
                if len(matching_indices) > 1:
                    response = "More than one movie titled \"{}\", I found. You mean which one?".format(titles[0])
                    self.disambiguated_line = line
                    self.disambiguate_flag = True
                    self.disambiguate_indices = matching_indices
                    for i in range(len(matching_indices)):
                        if i == len(matching_indices) - 1:
                            response += ", or " + self.titles[matching_indices[i]][0] + "?"
                        elif i == 0:
                            response += " " + self.titles[matching_indices[i]][0]
                        else:
                            response += ", " + self.titles[matching_indices[i]][0]
                    return response
                
                if len(matching_indices) == 0:
                    response = "\"{}\", heard of I have not. About another movie you must tell me.".format(titles[0])
                
                else:
                    # Extract sentiment and populate user preference matrix
                    sentiment = self.extract_sentiment(line)
                    self.user_ratings[matching_indices[0]] = sentiment
                    if sentiment == 0:
                        response = "Sure if you liked \"{}\", I am not. More about it could you tell me?".format(titles[0])
                        return response
                    if matching_indices[0] not in self.reviewed_movies:
                        self.reviewed_movies.append(matching_indices[0])
                        self.user_ratings_count += 1
                    if sentiment < 0:
                        response = titles[0] + ", " + random.choice(disliked_movie_yoda)
                    else:
                        response = titles[0] + ", " + random.choice(liked_movie_yoda)
                    if self.user_ratings_count >= 5:
                        self.recommendations = self.recommend(self.user_ratings, self.ratings)
                        response += " Know you well, Yoda now does. A recommendation from Master Yoda you want, hrmm?"
                        self.recommendations_count = 0
                    else:
                        response +=  " About another movie, you must tell me."
        
        
        ### standard mode: DO NOT CHANGE ###
        else:

            # Ensure that there is only one movie in the input line
            titles = self.extract_titles(line)
            
            if self.user_ratings_count >= 5 and self.recommendations_count < len(self.recommendations):
                if line.lower().strip() in affirmatives:
                    if self.recommendations_count == 0:
                        response = "I think you should watch " + self.titles[self.recommendations[self.recommendations_count]][0] + ". " + random.choice(want_more)
                    elif self.recommendations_count == len(self.recommendations) - 1:
                        response = random.choice(recommendations) + self.titles[self.recommendations[self.recommendations_count]][0] + ". That's all the movies I have to recommend!"
                    else:
                        response = random.choice(recommendations) + self.titles[self.recommendations[self.recommendations_count]][0] + ". " + random.choice(want_more)
                    self.recommendations_count += 1
                    return response
                elif line.lower() in negatives:
                    if self.recommendations_count == 0:
                        response = "Okay, I won't give you any recommendations :("
                    else:
                        response = "Okay, I hope you like my recommendations!"
                        return response
                else:
                    response = "Sorry, I can't tell if you want another recommendation. Do you want one?"
                    return response
                
            if len(titles) > 1:
                response = random.choice(too_many_inputs)
            
            # handling non-movie inputs
            elif len(titles) == 0:
                return "Sorry, let's get back to talking about movies."
            
            else:

                # Ensure that there is only one movie corresponding to the input
                matching_indices = self.find_movies_by_title(titles[0])
                if len(matching_indices) > 1:
                    response = "I found more than one movie titled \"{}\". Could you be more specific? ".format(titles[0])
                    return response
                if len(matching_indices) == 0:
                    response = "I've never heard of \"{}\". Could you tell me about another movie?".format(titles[0])
                else:

                    # Extract sentiment and populate user preference matrix
                    sentiment = self.extract_sentiment(line)
                    self.user_ratings[matching_indices[0]] = sentiment
                    if sentiment == 0:
                        response = "I'm sorry, but I'm not sure if you liked \"{}\". Could you tell me more about it?".format(titles[0])
                        return response
                    if matching_indices[0] not in self.reviewed_movies:
                        self.reviewed_movies.append(matching_indices[0])
                        self.user_ratings_count += 1
                    if sentiment < 0:
                        response = random.choice(disliked_movie) + titles[0] + "."
                    else:
                        response = random.choice(liked_movie) + titles[0] + "."
                    if self.user_ratings_count >= 5:
                        self.recommendations = self.recommend(self.user_ratings, self.ratings)
                        response += " I've learned enough about your taste to recommend new movies. Would you like a recommendation?"
                        self.recommendations_count = 0
                    else:
                        response += " Tell me about another movie you've seen."
                        
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
        
        matches = re.findall('"(.*?)"', preprocessed_input)
        
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
        matching_indices = []
        year = re.search(r'\(\d{4}\)', title)
        if year:
            title_without_year = title[:len(title) - 7]
            year = year[0]
        else:
            title_without_year = title
            
        # Move any article (a, an, the) to the end of the movie title
        article_match = re.search(r'^(a|an|the)\s+', title_without_year, re.IGNORECASE)
        if article_match:
            article = article_match.group(0)
            title_without_year = title_without_year.replace(article, '') + ', ' + article.title()
            title_without_year = title_without_year.strip() 
        processed_title = title_without_year     
        
        if year:
            processed_title = processed_title + ' ' + year    
        if self.creative:
            title_length = len(processed_title)
            for i, movie in enumerate(self.titles):
                if processed_title == movie[0][:title_length]:
                    matching_indices.append(i)
        else:            
            for i, movie in enumerate(self.titles):
                if year:
                    if processed_title == movie[0]:
                        matching_indices.append(i)
                else:
                    processed_search = re.sub(r'\(\d+\)', '', movie[0]).strip()
                    if processed_search == processed_title:
                        matching_indices.append(i)
            
            
        return matching_indices

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
        sentiment_score = 0
        
        words = preprocessed_input.split()
        negatives = ['not', "didn't", "never"]
        negation_flag = False
        emphasis = ['v[e]+[r]+[y]+', 'r[e]+[a]+l[l]+[y]+', 'supe[r]+', 'incredibl[e]+', 'ter[r]+ibl[e]+', 
                    'worst', 'best', '[\w]+[!]+', 'extremely', 'absolutely', 'awfu[l]+', 'atrocious', 'incredibl[ey]',
                    'totally', 'hate[d]*', 'detest[ed]*', 'despise[d]*', 'adore[d]*', 'love[d]*']
        emphasis_multiplier = 1
        
        for word in words:
            for expression in emphasis:
                if re.match(expression, word):
                    emphasis_multiplier = 2
            if word in negatives:
                negation_flag = True
            if word.endswith('d'):
                word = re.sub('d$', '', word)
            if word not in self.sentiment:
                if word.endswith('e'):
                    word = re.sub('e$', '', word)
            if word in self.sentiment:
                if self.sentiment[word] == 'neg':
                    if negation_flag:
                        sentiment_score += 1
                        negation_flag = False
                    else:
                        sentiment_score -= 1
                else:
                    if negation_flag:
                        sentiment_score -= 1
                        negation_flag = False
                    else:
                        sentiment_score += 1
            
        if sentiment_score > 0:
            return emphasis_multiplier
        elif sentiment_score < 0:
            return -1 * emphasis_multiplier
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
        senti = []
        input_sentence = preprocessed_input.split(".")
        for sentence in input_sentence:
            titles = self.extract_titles(sentence)
            but = sentence.find("but")
            if but == -1: # same sentiment
                for title in titles:
                    id_ = self.find_movies_by_title(title)
                    sentiment = self.extract_sentiment(sentence)
                    if len(id_) != 0:
                        senti.append((title, sentiment))
            else:
                sentences = sentence.split("but")
                titles1 = self.extract_titles(sentences[0])
                titles2 = self.extract_titles(sentences[1])
                senti1 = self.extract_sentiment(sentences[0])
                senti2 = self.extract_sentiment(sentences[1])
                if senti1 != 0 and senti2 == 0:
                    senti2 = senti1 * (-1)
                for title in titles1:
                    id_ = self.find_movies_by_title(title)
                    if len(id_) != 0:
                        senti.append((title, senti1))
                for title in titles2:
                    id_ = self.find_movies_by_title(title)
                    if len(id_) != 0:
                        senti.append((title, senti2))
        return senti

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

        def remove_year(title):
            if re.search(r'\(\d{4}\)', title):
                title = title[:len(title) - 7]
            return title
        title = title.lower()
        closest_movies = []
        min_distance = max_distance + 1
        for i, movie in enumerate(self.titles):
            movie_title = remove_year(movie[0]).lower()
            distance = nltk.edit_distance(title, movie_title)
            if distance < min_distance:
                min_distance = distance
                closest_movies = [i]
            elif distance == min_distance:
                closest_movies.append(i)
        return closest_movies

    def disambiguate(self, clarification: str, candidates):
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

        def get_year(title):
            match = re.findall(r'\((\d{4})\)', title)
            return match[0] if len(match) == 1 else "9999"

        def remove_year(title):
            if re.search(r'\(\d{4}\)', title):
                title = title[:len(title) - 7]
            return title

        clarification = clarification.lower().strip()
        clarification = re.sub(r'[^\w\s\'\,]', '', clarification)

        ret = []
        if clarification.isnumeric():
            if len(clarification) == 4:
                # match year
                ret.extend([i for i in candidates if get_year(self.titles[i][0]) == clarification])
            else:
                if int(clarification) <= len(candidates):
                    ret.append(candidates[int(clarification)-1])
            return ret

        if clarification[-4:] == " one":
            clarification = clarification[:-4]

        if clarification == "most recent":
            tmp = [(get_year(self.titles[i][0]),i) for i in candidates]
            recent = sorted(tmp, key=lambda x: -int(x[0]) )[0][0]
            return [i for i in candidates if get_year(self.titles[i][0]) == recent]

        ordinal_numbers = ["first", "second", "third", "third", "fifth", "sixth", \
                "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth", \
                "thirteenth", "fourteenth", "fourteenth", "sixteenth", "seventeenth", \
                "seventeenth", "seventeenth", "twentieth"]

        clar_split = clarification.split()
        if len(clar_split) == 2 and clar_split[0] == "the" and clar_split[1] in ordinal_numbers:
            idx = ordinal_numbers.index(clar_split[1])
            if idx < len(candidates):
                return [candidates[idx]]

        for i in candidates:
            movie_title = remove_year(self.titles[i][0]).lower()
            if clarification in movie_title:
                ret.append(i)
        
        return list(set(ret))

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
        # binarized_ratings = np.zeros_like(ratings)
        binarized_ratings = np.empty_like(ratings)
        binarized_ratings[ratings <= threshold] = -1
        binarized_ratings[ratings > threshold] = 1
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
        similarity = 0
        norm_u_v = np.sqrt(np.dot(u, u) * np.dot(v, v))
        if norm_u_v != 0:
            similarity = np.dot(u, v) / norm_u_v

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

        senti_dict = {}
 

        for id in range(len(user_ratings)):
            senti_dict[id] = user_ratings[id]

        # find movies that users rated
        movie_rated = set() #id
        for id in senti_dict:
            if senti_dict[id] != 0:
                movie_rated.add(id)
        rating = {}
        for i in range(len(user_ratings)):
            similarity = np.array([])
            ratings = np.array([])

            if i not in movie_rated:
                for movie in movie_rated:
                    cos_sim = self.similarity(ratings_matrix[i], ratings_matrix[movie])
                    similarity = np.append(similarity, cos_sim)
                    ratings = np.append(ratings, senti_dict[movie])
            rating[i] = np.dot(similarity, ratings)

        sorted_movies = sorted(rating.items(), key=lambda x: (-x[1], x[0]))
        recommendations = [movie[0] for movie in sorted_movies[:k]]


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
