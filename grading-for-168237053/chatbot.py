# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import random
import numpy as np
import re


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'scurvybot'

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
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################
    def tell_joke(self):
        # Pirate jokes sourced from Reader's Digest, https://www.rd.com/article/pirate-jokes-pirate-puns/

        joke_pirate = ["Why don't pirates shower before they walk the plank? Because they'll just wash up on shore later! XD",
                        "What did the pirate wear on Halloween? A pumpkin patch! 🤣",
                        "What's a pirate's favorite type of exercise? The plank! :D",
                        "How much did the pirate pay for his peg and hook? An arm and a leg. 💀💀💀",
                        "Wanna know why pirates are terrible singers? Because they can't hit their high C's! 😂"]
        
        joke_regular = ["Why did the chicken cross the road?? To get to the other side! XD",
                       "What do you call a fake noodle? An Im-pasta! 🤣",
                       "Why do all bears have furry coats?? Fur their protection! 🐻😆",
                       "How do a group of penguins make a house? Igloos them together! 💀🧊",
                       "Why did a scarecrow win a movie award? They were outstanding in their field! 😱"]

        if self.creative:
            return random.choice(joke_pirate)
        else:
            return random.choice(joke_regular)


    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        ########################################################################
        # TODO: Write a short greeting message                                 #
        ########################################################################
        greeting_messages = ["How can I help you?",
                             "Hey! How can I be of assistance?",
                             "What's shaking? Let's hear some of your movie thoughts...",
                             "What's up? Anything I can help you with?",
                             "How can I help you today?",
                             "Anything I can assist you with?",
                             "What do I have the pleasure to work with today?"]

        greeting_pirate = ["Ahoy matey! Allow me to hear ye..."
                           "Sailor! How can thy be served?",
                           "Yo hey ho! Allow a helping hand to thee, will ya?",
                           "I'll be shaken! I've been awakened to service thy!",
                           "Hail the storm, blessed to see ya!",
                           "Holly dolly, skiver on the sea—— Who shall you be to me?"]

        if self.creative:
            return random.choice(greeting_pirate)
        else:
            return random.choice(greeting_messages)
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        ########################################################################
        # TODO: Write a short farewell message                                 #
        ########################################################################

        goodbye_messages = ["Have a great day friend!",
                            "Take care for now!",
                            "See you again!",
                            "Until next time, take care!",
                            "Hasta luego amigo!"]

        goodbye_pirate = ["Safe sailing you ya, matey!",
                          "Allow thy a safe journey back to the sea...",
                          "Enough to make a grown one cry, farewell",
                          "Until next time, we shall part the sea!",
                          "Farewell my fellow sailor, glad I could aid thy in need!",
                          "May the sea stay calm and thy journeys go strong!"]

        if self.creative:
            return random.choice(goodbye_pirate)
        else:
            return random.choice(goodbye_messages)

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################

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

        sentiment_value = self.extract_sentiment(line)
        extracted_title = self.extract_titles(line)
        response = ""
        # need disambiguate since multiple titles can be returned
        # Using five _'s to signify the movie title, which we will use a
        # str.find() and replace function to put the title in with later

        text_tokens = (line.lower()).strip()

        joke_sentiment_words = ["funny", "joke"]
        hello_sentiment_words = ["hello", "hey", "going", "doing"]
        if any(word in text_tokens for word in joke_sentiment_words):
            return self.tell_joke()
        elif any(word in text_tokens for word in hello_sentiment_words):
            return self.greeting()

        if self.creative:
            pirate_good = ["Hear thy! Me hear ye fancy with _____, ye? What others shiver ya?",
                           "Yo ho! Me feel the same, _____ be finest of the sea! Allow me to hear more...",
                           "Finest creator! _____ are of the best me sees! More ye say?",
                           "Ahhhhh _____, great choice thy picks... Hear me some more?",
                           "Poppin popcorn! _____ on a flame, great film! Continue for me mate!",
                           "Alas! _____, yer a good one I say! Count me more..."]
            pirate_bad = ["Davey Jones! What a bad film _____ was! Hear me more...",
                          "Argh! Said film _____ should be off the deck! Bless me more please!"
                          "Blimey! _____ almost gave me scurvy! Finish thy thought please...",
                          "Shiver me timbers! Never a pirate seen _____, never will! Me hearty, finish more!",
                          "Curse _____, no good I say! Allow me to ask again?"]
            
            if sentiment_value > 0: # good
                response = random.choice(pirate_good)
            elif sentiment_value < 0: # bad
                response = random.choice(pirate_bad)

        else:
            good_responses = ["I'm hearing that you liked _____, right? What are some other movies you liked?",
                              "You thought _____ was a good movie? Awesome! Let's hear a few more!",
                              "Okay, so you liked the movie _____? Can I hear more movies you liked?",
                              "Great deal, sounds like you liked _____! How about another movie you liked?",
                              "Interesting movie, heard great things about _____, so I'm glad to hear you enjoyed it! Any other movies?"]
            bad_responses = ["If I understand correctly, you didn't like _____. Tell me more!",
                             "Seems like _____ wasn't a good movie! Let me hear about other movies, please!",
                             "Sorry to hear you didn't enjoy _____! If you give me some more info, I can surely give you a movie you will like!",
                             "_____ was not to your expectations, got it. What else?",
                             "Thanks for the letting me know you thought _____ wasn't good, what are some other thought you have?"]
            if sentiment_value > 0: # good
                response = random.choice(good_responses)
            elif sentiment_value < 0: # bad
                response = random.choice(bad_responses)
            response = response.replace("_____", extracted_title[0]) # CAN BE BUGGY IF NO TITLE
            
        return response
            
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################


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

        # Takes into account capitalization, so will lower-case all and search for that instead
        lowered_input = preprocessed_input.lower()
        titles = re.findall('"(.*?)"', preprocessed_input)
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
        years = re.findall(r'\(([0-9]+)\)', title)

        # cut out year
        words = re.sub(r'(^.+)(\s\(\d+\))', r'\1', title)

        words = words.split()

        # Changed to contain English, Spanish, Italian, French, and German (nomative)
        if words[0] in ["A", "An", "The"]:  # English
            title = ' '.join(words[1:]) + ", " + words[0]
        elif words[0] in ["El", "La", "Los", "Las", "Lo"]:  # Spanish
            title = ' '.join(words[1:]) + ", " + words[0]
        # French with no "la" because it's covered by Spanish
        elif words[0].lower() in ["La", "Le", "L'", "Les"]:
            title = ' '.join(words[1:]) + ", " + words[0]
        elif words[0] in ["Il", "Gli", "I"]:  # Italian with no "lo", "la", "l'", and "le"
            title = ' '.join(words[1:]) + ", " + words[0]
        elif words[0] in ["Ein", "Eine", "Keine"]:  # German
            title = ' '.join(words[1:]) + ", " + words[0]
        else:
            title = ' '.join(words[:])

        # # Previously Changed The Notebook to Notebook, The
        # if words[0] in ["a","an","the"]:
        #     title = ' '.join(words[1:]) + ", " + words[0]
        if len(years) != 0:
            title += " (" + str(years[0]) + ")"
        else:
            title += " ("

        # Titanic (1994)
        # Titanic (1962)
        # We want to search 'Titanic ('
        indices = []
        for i in range(len(self.titles)):
            if title in self.titles[i][0]:
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
        input_no_titles = re.sub(r'"[^"]*"', '', preprocessed_input)
        tokenized = input_no_titles.split()

        if self.creative:
            sum_sentiments = 0
            multiplier = 1
            negated = 1
            for token in tokenized:
                if token.lower() in ["didn't", "never", "not"]:
                    negated *= -1
                if token in ["like", "liked", "enjoy", "enjoyed"]:
                    sum_sentiments += 1 * multiplier
                    multiplier = 1
                if token in ["love", "loved"]:
                    sum_sentiments += 2 * multiplier
                if token in ["really", "very"]:
                    multiplier *= 3
                    

                if token in self.sentiment:
                    word_sentiment = self.sentiment[token]
                    if word_sentiment == 'pos':
                        sum_sentiments += 1 * multiplier
                    else:
                        sum_sentiments -= 1 * multiplier
                    
                    multiplier = 1
            
            sum_sentiments = sum_sentiments * negated
            if sum_sentiments > 1:
                return 2
            elif sum_sentiments == 1:
                return 1
            elif sum_sentiments == -1:
                return -1
            elif sum_sentiments < -1:
                return -2
            return 0

        else:
            sum_sentiments = 0
            negated = 1
            for token in tokenized:
                if token.lower() in ["didn't", "never", "not"]:
                    negated = -1
                if token in ["like", "liked", "love", "loved", "enjoy", "enjoyed", "good", "great"]:
                    sum_sentiments += 2
                if token in self.sentiment:
                    word_sentiment = self.sentiment[token]
                    if word_sentiment == 'pos':
                        sum_sentiments += 1
                    else:
                        sum_sentiments -= 1

            sum_sentiments = sum_sentiments * negated
            if sum_sentiments > 0:
                return 1
            elif sum_sentiments < 0:
                return -1
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

        # Extract movie titles from the preprocessed input
        movie_titles = self.extract_titles(preprocessed_input)
        if not movie_titles:
            return []

        # Create a list to store the tuples of movie titles and their sentiments
        movie_sentiments = []

        # Iterate over the movie titles and extract the sentiment for each movie
        for movie_title in movie_titles:
            # Extract the sentiment for the movie
            sentiment = self.extract_sentiment(preprocessed_input, movie_title)
            # Append the tuple of movie title and its sentiment to the list
            movie_sentiments.append((movie_title, sentiment))

        # Return the list of tuples of movie titles and their sentiments
        return movie_sentiments

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
        possibilities = set()
        tokenized = clarification.lower().split()
        # index = mod10(index(idx[token]))
        indexes = ('first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 
                 'eighth', 'ninth', 'tenth', '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th',
                 '9th', '10th',)
        recent = False
        indx = -1
        for token in tokenized:
            if token in indexes:
                indx = indexes.index(token) % 10
            elif token.isdigit() and int(token) <= len(candidates):
                indx = int(token) - 1

        year = re.search(r'(\(\d{4}(?:-(?:\d{4})?)?\))', clarification)
        if year:
            for i in candidates:
                if year in self.titles[i][0]:
                    possibilities.add(i)
        elif indx != -1:
            possibilities.add(candidates[indx])
        elif 'recent' in clarification or 'latest' in clarification:
            possibilities.add(candidates[-1])

        for i in candidates:
            if clarification in self.titles[i][0]:
                possibilities.add(i)
        return list(possibilities)

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
        dot = np.dot(u, v)
        magnitude = np.linalg.norm(u) * np.linalg.norm(v)

        if magnitude == 0:
            return 0.0
        else:
            return (dot/magnitude)
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################

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

        ratings = []
        rated_idx = np.where(user_ratings != 0)[0]
        unrated_idx = np.where(user_ratings == 0)[0]
        user_ratings_arr = np.array([user_ratings[i] for i in rated_idx])
        for i in unrated_idx:
            sims = []
            r_i = ratings_matrix[i]
            for j in rated_idx:
                r_j = ratings_matrix[j]
                sims.append(self.similarity(r_i, r_j))
            prediction = np.array(sims) @ user_ratings_arr
            ratings.append((i, prediction))

        sorted_recs = sorted(ratings, key=lambda x: x[1])[::-1]
        recommendations = [x[0] for x in sorted_recs[:k]]
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

        if self.creative:
            return "ARRGH! Me name is Jack Sparrow, Cap'n of thee Black Pearl. Critics will say I'm the 'Worst Pirate they'd ever heard of', but to that I say, at least ye heard of me! I'll be yer guide today as I help ye indecisive noggin pick out a movie for yer 'Netflix n Chill' or whatever scurvy ye be up ta. Got questions? Fire Away!"
        else:
            return "Hey there! I'm ChatBot, and I'll be helping you recommend some movies to watch. If you could help me out and give me a few details about movies you liked and did not like, I can tune my recommendations for something I think you might enjoy. Let's start—— What are some movies you wanna talk about?"
        """
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
