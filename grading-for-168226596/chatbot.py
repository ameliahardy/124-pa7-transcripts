# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
from porter_stemmer import PorterStemmer
import re
import random


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'moviebot'

        self.creative = creative
        self.stemmer = PorterStemmer()

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.user_ratings = np.zeros(len(self.titles))
        self.user_ratings_count = 0

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
            response = "I processed {} in creative mode!! \n".format(line)
        else:
            response = "I processed {} in starter mode!! \n".format(line)

        # Bank for no sentiment
        no_sentiment = ["I'm sorry, I'm not sure if you liked ", "I didn't quite catch whether you liked or disliked ", "Hmmmmm. I'm confused! Did you like or dislike ",
                        "Human emotions are difficult :( Did you like or dislike "]
        # Bank for positive sentiment
        pos_sentiment = ["Ok, you liked "]
        # Bank for negative sentiment
        neg_sentiment = ["You did not like "]
        # Bank for non-existent movie
        non_existent_movie = ["I've never heard of "]
        # Bank for failing gracefully
        failing_gracefully = [
            "Sorry... Tell me about another movie!", "Sorry, I didn't understand."]
        # Bank for More ratings
        more_ratings = ["Tell me about another movie!", "Tell me about another movie you saw!", "How about you tell me about another movie?", "What's another movie you saw?",
                        "What's another movie you liked/disliked?"]
        question_bank = {"can you": "I'm not sure if I can. ",
                         "what": "I don't know! ", "who are": "I am [INSERT PERSONA HERE]. "}

        for question_phrase in question_bank:
            if line.lower().startswith(question_phrase):
                return response + question_bank[question_phrase] + line + "??" + " Anyway, that's not really what I want to talk about right now. Why don't you tell me something about movies?"

        # Extract possible titles?
        possible_titles = self.extract_titles(line)
        # If no matching title: fail gracefully
        if len(possible_titles) == 0:
            return response + " Sorry I didn't quite catch any movies there. Why don't you tell me something about a movie?"
        # If many possible titles: fail gracefully
        if len(possible_titles) > 1:
            return response + " Sorry I think you're talking about too many movies at once :( Tell me about just one of them!"
        # If one possible title: find movie title:

        movie_titles = self.find_movies_by_title(possible_titles[0])

        # If movie_titles is empty: fail gracefully
        if len(movie_titles) == 0:
            return response + " " + random.choice(non_existent_movie) + " " + possible_titles[0] + ". " + random.choice(more_ratings)
        # If movie_titles has many: disambiguate (ask for clarification)
        if len(movie_titles) > 1 and self.creative:
            # TODO: Fix disambiguation
            return "Seems like you may be talking about a couple of different movies here. Which one do you mean?"
        # If movie_titles has one: get sentiment.
        sentiment = self.extract_sentiment(line)

        # If no sentiment: clarify from bank of no sentiment
        if sentiment == 0:
            return response + " " + random.choice(no_sentiment) + " " + self.titles[movie_titles[0]][0] + ". " + random.choice(more_ratings)
        # If positive/negative: add sentiment to that index in self.user_ratings, increment self.user_ratings_count
        if sentiment >= 1:
            response += "\n" + \
                random.choice(pos_sentiment) + possible_titles[0]
        else:
            response += "\n" + \
                random.choice(neg_sentiment) + possible_titles[0]
        self.user_ratings[movie_titles[0]] = 1 if sentiment >= 1 else -1
        self.user_ratings_count += 1
        # check if self.user_ratings_count < 5: pick from More bank
        if self.user_ratings_count < 5:
            return response + " " + random.choice(more_ratings)
        # else: make a rec -> ask user if they want more
        num_recommendations = 0
        more_recommendation = 'y'

        # while yes: keep making rec
        while more_recommendation[0].lower() == 'y':
            num_recommendations += 1
            recommendation = self.recommend(
                self.user_ratings, self.ratings, num_recommendations, self.creative)
            more_recommendation = input(
                "Would you like another recommendation?")
            print("I think you might like ",
                  self.titles[recommendation[-1]][0])

        # no: pick from More bank
        return response + " " + random.choice(more_ratings)

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

        # Designing this function to create a list of words from the text
        # word_lower = text.lower()
        # re.replace(word_lower, @"[^\w\s\"]", "")

        # return word_list

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

        # Using capture groups to extract the word (movie name) from within the quotations
        titles_list = re.findall(r'\"(.+?)\"', preprocessed_input)
        for title in self.titles:
            if title.lower() in preprocessed_input.lower():
                titles_list.append(title)
        return titles_list

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
        if (self.creative):
            matching_indices_list = []
            title = title.lower()
            title_words = self.process_sentence(title)
            for index, val in enumerate(self.titles):
                movie_title = val[0].lower()
                all_found = True
                for word in title_words:
                    if word not in movie_title:
                        all_found = False
                        break
                if all_found:
                    matching_indices_list.append(index)

            return matching_indices_list

        articles = ["a", "an", "the", "ein", "eine", "keine", "la", "le", "les",
                    "un", "une", "el", "los", "las", "una", "il", "lo", "gli", "uno"]

        matching_indices_list = []
        title = title.lower()
        title_words = title.split()
        year = ""

        # Extract the year
        if title_words[-1][0] == '(':
            year = title_words[-1].strip('(')
            year = year.strip(')')
            del title_words[-1]
            title = ''
            for index, val in enumerate(title_words):
                title += val
                if index != len(title_words) - 1:
                    title += ' '

        # Extract the article
        if title_words[0] in articles:
            title = ''
            for index, val in enumerate(title_words[1::]):
                title += val
                if index + 1 != len(title_words) - 1:
                    title += ' '

            title += ', ' + title_words[0]

        if year != '':
            title += " (" + year + ")"

        for index, val in enumerate(self.titles):
            movie_title = val[0].lower()
            match_title = re.search(r'^{}(?: \(\d{{4}}\))?$'.format(
                re.escape(title)), movie_title)
            if match_title:
                matching_indices_list.append(index)

        return matching_indices_list

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

        stemmed_sentiments = {}
        for word in self.sentiment:
            if self.sentiment[word] == 'pos':
                stemmed_sentiments[self.stemmer.stem(word)] = 1
            else:
                stemmed_sentiments[self.stemmer.stem(word)] = -1

        preprocessed_input = self.remove_titles(preprocessed_input)

        list_of_words = self.process_sentence(preprocessed_input)

        negation_words = ['no', 'not', 'never', 'neither', 'nor', 'none', 'nobody', 'nowhere', 'nothing', 'hardly', 'scarcely', 'barely', 'few', 'little', 'less', 'without',
                          "doesn't", "haven't", "isn't", "couldn't", "don't", "woudln't", "can't", "wasn't", "weren't", "shouldn't", "hasn't", "won't", "hadn't", "cannot", "didn't"]

        strong_positive_words = ["amazing", "awesome", "beautiful", "best", "brilliant", "celebration", "charming", "delightful", "dream", "excellent", "fabulous", "fantastic", "fun",
                                 "glamorous", "gorgeous", "graceful", "great", "happy", "ideal", "incredible", "jolly", "joyful", "love", "luxurious", "marvelous", "outstanding",
                                 "perfect", "pleasant", "pleasure", "remarkable", "sensational", "spectacular", "splendid", "superb", "terrific", "triumph", "unforgettable", "wonderful"]

        strong_negative_words = ["abysmal", "appalling", "atrocious", "awful", "bad", "banal", "barren", "boring", "corrupt", "crappy", "creepy", "dangerous", "defective", "deplorable",
                                 "depressing", "detestable", "disastrous", "disgusting", "dreadful", "dull", "evil", "failed", "filthy", "foul", "frustrating", "ghastly", "grim", "gross",
                                 "hopeless", "horrible", "horrific", "infernal", "insipid", "lousy", "miserable", "pathetic", "poor", "repulsive", "revolting", "shoddy", "sickening",
                                 "terrible", "tragic", "ugly", "unbearable", "unpleasant", "vile", "wicked", "worthless", "hate", ]

        multipliers = ["really", "strongly",
                       "absolutely", "definitely", "reeally"]

        pos_count = 0
        neg_count = 0

        negative_flag = False

        really_multiple = 1

        for word in list_of_words:
            word = word.lower()
            if word in negation_words:
                negative_flag = not negative_flag
            if word in multipliers:
                really_multiple = really_multiple * 2
            stemmed_word = self.stemmer.stem(word)
            if stemmed_word in stemmed_sentiments:
                if negative_flag:
                    if stemmed_sentiments[stemmed_word] == 1:
                        neg_count += 1 * really_multiple if stemmed_word not in strong_positive_words else 2 * really_multiple
                    else:
                        pos_count += 1 * really_multiple if stemmed_word not in strong_negative_words else 2 * really_multiple
                else:
                    if stemmed_sentiments[stemmed_word] == 1:
                        pos_count += 1 * really_multiple if stemmed_word not in strong_positive_words else 2 * really_multiple
                    else:
                        neg_count += 1 * really_multiple if stemmed_word not in strong_negative_words else 2 * really_multiple

        if pos_count > neg_count:
            sentiment = 1
        elif neg_count > pos_count:
            sentiment = -1
        else:
            sentiment = 0

        # TODO: Creative mode: Fine grain sentiment extraction. Haven't tested yet.
        if (self.creative):
            num_total = pos_count + neg_count
            if num_total >= 2 and pos_count >= 2*neg_count:
                sentiment = 2
            elif num_total >= 2 and neg_count >= 2*pos_count:
                sentiment = -2

        return sentiment

    # Helper function to remove titles from sentence
    def remove_titles(self, sentence):
        # Use as extract titles?
        movie_titles = re.findall(r'\"(.+?)\"', sentence)
        # movie_titles = self.extract_titles(sentence)
        for title in movie_titles:
            sentence = sentence.replace('"' + title + '"', "")

        return sentence

    # Convert a single string sentence into a list of strings split by space or punctuation
    def process_sentence(self, sentence):
        sentence = self.remove_titles(sentence)
        sentence_list = re.split(';|,|\s|!+|\?+|\.+', sentence)
        return sentence_list

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
        pass

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
        def editDistDP(str1, str2):
            dp = [[0 for x in range(len(str2) + 1)] for x in range(len(str1) + 1)]
        
            for i in range(len(str1) + 1):
                for j in range(len(str2) + 1):
        
                    if j == 0:
                        dp[i][j] = i   
                    elif i == 0:
                        dp[i][j] = j
                    elif str1[i-1] == str2[j-1]:
                        dp[i][j] = dp[i-1][j-1] 


        
                    else:
                       # dp[i][j] = 1 + min(dp[i][j-1],        # Insert
                       #                 dp[i-1][j],        # Remove
                       #                 dp[i-1][j-1])    
                                        # Replace
                        #dp[i][j] = min( 1 + min(dp[i][j-1],        # Insert
                        #                dp[i-1][j]), 2 + dp[i-1][j-1])
                        dp[i][j] = min(1 + min(dp[i][j-1],	 # Insert
								        dp[i-1][j]),	 # Remove
								        2 + dp[i-1][j-1]) # Replace

        
            return dp[len(str1)][len(str2)]
        matching_indices = []
        title = title.lower().strip()
        min_dist = float('inf')
        #min_dist = 1000
        for i, movie in enumerate(self.titles):
            #movie_title = movie[i][0].lower().strip()
            movie1_title = movie[0].lower()
            movie_title = movie1_title.strip()
            match = re.search(r"^(.*?)\s*\(", movie_title)
            if(match):
                distance = editDistDP(title,match.group(1))
                #print(i,distance)
                if distance <= 3:
                    #print(i)
                    #print(distance)
                    #print(match.group(1))
                    if distance < min_dist:
                        matching_indices = [i]
                        min_dist = distance
                    elif distance == min_dist:
                        matching_indices.append(i)
                    else:
                        continue
        return matching_indices

    # def find_movies_closest_to_title(self, title, max_distance=3):
    #     """Creative Feature: Given a potentially misspelled movie title,
    #     return a list of the movies in the dataset whose titles have the least
    #     edit distance from the provided title, and with edit distance at most
    #     max_distance.

    #     - If no movies have titles within max_distance of the provided title,
    #     return an empty list.
    #     - Otherwise, if there's a movie closer in edit distance to the given
    #     title than all other movies, return a 1-element list containing its
    #     index.
    #     - If there is a tie for closest movie, return a list with the indices
    #     of all movies tying for minimum edit distance to the given movie.

    #     Example:
    #       # should return [1656]
    #       chatbot.find_movies_closest_to_title("Sleeping Beaty")

    #     :param title: a potentially misspelled title
    #     :param max_distance: the maximum edit distance to search for
    #     :returns: a list of movie indices with titles closest to the given title
    #     and within edit distance max_distance
    #     """
    #     def editDistDP(str1, str2, m, n):
    #         # Create a table to store results of subproblems
    #         dp = [[0 for x in range(n + 1)] for x in range(m + 1)]
        
    #         # Fill d[][] in bottom up manner
    #         for i in range(m + 1):
    #             for j in range(n + 1):
        
    #                 # If first string is empty, only option is to
    #                 # insert all characters of second string
    #                 if i == 0:
    #                     dp[i][j] = j    # Min. operations = j
        
    #                 # If second string is empty, only option is to
    #                 # remove all characters of second string
    #                 elif j == 0:
    #                     dp[i][j] = i    # Min. operations = i
        
    #                 # If last characters are same, ignore last char
    #                 # and recur for remaining string
    #                 elif str1[i-1] == str2[j-1]:
    #                     dp[i][j] = dp[i-1][j-1]
        
    #                 # If last character are different, consider all
    #                 # possibilities and find minimum
    #                 else:
    #                    # dp[i][j] = 1 + min(dp[i][j-1],        # Insert
    #                    #                 dp[i-1][j],        # Remove
    #                    #                 dp[i-1][j-1])    
    #                                     # Replace
    #                     #dp[i][j] = min( 1 + min(dp[i][j-1],        # Insert
    #                     #                dp[i-1][j]), 2 + dp[i-1][j-1])
    #                     dp[i][j] = min(1 + min(dp[i][j-1],	 # Insert
	# 							        dp[i-1][j]),	 # Remove
	# 							        2 + dp[i-1][j-1]) # Replace

        
    #         return dp[m][n]
    #     """
    #     lst = "sleeping beauty"
    #     lst1 = "sleeping beaty"
    #     dis = editDistDP(lst,lst1,len(lst),len(lst1))
    #     print(dis)
    #     """
    #     """
    #     lst = "Te"
    #     lst1 = "ed (2002)"
    #     match = re.search(r"^(.*?)\s*\(", lst1)
    #     if(match):
    #         dis = editDistDP(lst,match.group(1),len(lst),len(match.group(1)))
    #         print(dis)
    #         print(match.group(1))
    #     else:
    #         print("L")
    #     """
    #     def editDistance(str1, str2, m, n):
    #     # If first string is empty, the only option is to
    #     # insert all characters of second string into first
    #         if m == 0:
    #             return n
 
    #     # If second string is empty, the only option is to
    #     # remove all characters of first string
    #         if n == 0:
    #             return m
    
    #     # If last characters of two strings are same, nothing
    #     # much to do. Ignore last characters and get count for
    #     # remaining strings.
    #         if str1[m-1] == str2[n-1]:
    #             #print(str1)
    #            # print(str2)
    #             return editDistance(str1, str2, m-1, n-1)

    #         # If last characters are not same, consider all three
    #         # operations on last character of first string, recursively
    #         # compute minimum cost for all three operations and take
    #         # minimum of three values.
    #        #return min(min(1 + min(editDistance(str1, str2, m, n-1),    # Insert
    #        #             editDistance(str1, str2, m-1, n))), 2 +    # Remove
    #        #             editDistance(str1, str2, m-1, n-1)    # Replace
    #        #             )
    #         #print(str1)
    #        # print(str2)
    #         return min((1 + min(editDistance(str1, str2, m, n-1), # Insert
	# 		editDistance(str1, str2, m-1, n))), # Remove
	# 		2 + editDistance(str1, str2, m-1, n-1) # Replace
	# 		)


    #     def edit_distance(title, movie_title):
    #         if len(title) < len(movie_title):
    #             return edit_distance(title, movie_title)
    #         if len(movie_title) == 0:
    #             return len(title)
    #         prev_row = range(len(movie_title) + 1)
    #         for i, c1 in enumerate(title):
    #             curr_row = [i + 1]
    #             for j, c2 in enumerate(movie_title):
    #                 insertions = prev_row[j + 1] + 1
    #                 deletions = curr_row[j] + 1
    #                 substitutions = prev_row[j] + (2 * (c1 != c2))
    #                 curr_row.append(min(insertions, deletions, substitutions))
    #             prev_row = curr_row
    #         return prev_row[-1]
        
    #     def edit_distance1(string1, string2):

    #         if len(string1) > len(string2):
    #             difference = len(string1) - len(string2)
    #             string1[:difference]
    #             for i in range(len(string2)):
    #                 if string1[i] != string2[i]:
    #                     difference += 1


    #         elif len(string2) > len(string1):
    #             difference = len(string2) - len(string1)
    #             string2[:difference]
    #             for i in range(len(string1)):
    #                 if string1[i] != string2[i]:
    #                     difference += 1
    #         else:
    #             difference = 0
    #             for i in range(len(string1)):
    #                 if string1[i] != string2[i]:
    #                     difference += 1

    #         return difference

    #     matching_indices = []
    #     title = title.lower().strip()
    #     min_dist = float('inf')
    #     #min_dist = 1000
    #     for i, movie in enumerate(self.titles):
    #         #movie_title = movie[i][0].lower().strip()
    #         movie1_title = movie[0].lower()
    #         movie_title = movie1_title.strip()
    #         match_title = re.search(r'^{}(?: \(\d{{4}}\))?$'.format(
    #                                 re.escape(title)), movie_title)
    #         #match = re.search(r"^(.*?)\s*\(", movie_title)
    #         match = re.search(r"^(.*?)\s*\(", movie_title)
    #         #pattern = r'^(.*?)(?=\)$)'
    #         #match = re.match(pattern, movie_title)


    #        # print(len(self.titles))
    #        # print(movie_title)
    #         #print(title)
    #         #print(movie_title)
    #         #distance = edit_distance(title, movie_title)
    #         #distance = editDistance(title,movie_title,len(title),len(movie_title))
    #         #distance = editDistDP(title,movie_title,len(title),len(movie_title))
    #         #distance = 2
    #         #distance = edit_distance1(title,movie_title)
    #         #print(distance)
    #         if(match):
    #             distance = editDistDP(title,match.group(1),len(title),len(match.group(1)))
    #             #print(i,distance)
    #             if distance <= 3:
    #                 #print(i)
    #                 #print(distance)
    #                 #print(match.group(1))
    #                 if distance < min_dist:
    #                     matching_indices = [i]
    #                     min_dist = distance
    #                 elif distance == min_dist:
    #                     matching_indices.append(i)
    #                     #matching_indices = matching_indices + [i]
    #                 else:
    #                     i = i
    #     #print(matching_indices)
    #     #print(min_dist)
    #     return matching_indices

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
        ret = []
        plausible_movie_titles = []
        for candidate_index in candidates:
            plausible_movie_titles.append(
                (self.titles[candidate_index][0], candidate_index))
        for movie_title in plausible_movie_titles:
            print(clarification, "\n Actual Title:",  movie_title[0])
            if clarification.lower() in movie_title[0].lower():
                ret.append(movie_title[1])

        return ret

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
        for row_index, row in enumerate(ratings):
            for col, element in enumerate(row):
                if element == 0:
                    binarized_ratings[row_index][col] = 0
                elif element <= threshold:
                    binarized_ratings[row_index][col] = -1
                else:
                    binarized_ratings[row_index][col] = 1
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
        denominator = (np.linalg.norm(u) * np.linalg.norm(v))
        if denominator == 0:
            return 0
        else:
            cosine_sim = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return cosine_sim

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

        # Find out which movies have been rated
        rated_movies = []
        for movie_index, rating in enumerate(user_ratings):
            if rating != 0:
                rated_movies.append(movie_index)

        possible_ratings = {}

        # Find the cosine similarities of each of the movie that have not been rated
        # with the user ratings and then add to list

        for movie_index, rating in enumerate(user_ratings):
            similarities = []
            ratings = []
            if (rating == 0):
                # Find the cosine similarity with each of the other movies

                for rated_movie in rated_movies:
                    cosine = self.similarity(
                        ratings_matrix[movie_index], ratings_matrix[rated_movie])
                    similarities.append(cosine)
                    ratings.append(user_ratings[rated_movie])

            dot_prod = np.dot(np.array(similarities), np.array(ratings))
            possible_ratings[movie_index] = dot_prod

        sorted_ratings = sorted(possible_ratings.items(),
                                key=lambda x: x[1], reverse=True)

        for num in range(k):
            recommendations.append(sorted_ratings[num][0])

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
