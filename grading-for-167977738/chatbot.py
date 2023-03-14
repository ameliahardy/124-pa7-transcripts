# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import random
import numpy as np
import util
import re
import string
import porter_stemmer
p = porter_stemmer.PorterStemmer()

# noinspection PyMethodMayBeStatic


class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'Meg Bot'
        self.creative = creative
        # Our own Variables:
        self.taking_data_points = True
        self.movie_list = []
        self.index_list = []
        self.data_points_needed = 5
        #self.accepting_clarification = False
        self.clarification_options = []
        self.list_of_recommendations = []
        self.making_recommendations = False
        self.process_curr = 0
        self.word_size = 9
        self.yes_synonyms = ["yes", "indeed", "absolutely", "certainly", "definitely", "surely", "unquestionably", "affirmative", "aye", "yeah", "yep", "uh-huh", "okay", "ok"]
        self.arbitrary_responses = ["Hm, that's not really what I want to talk about right now, let's go back to movies", "Ok, got it. What's a movie you really enjoyed?", "I'm not really equipped to handle that, what was one of your favorite movies?"]
        self.arbitrary_responses_creative = ["Hmm…I don’t know about all that", "PURR!! What else did you like?", "I can't do all that fren. What movies do you think ate down.. like downnnnn?"]
        self.articles = ['an', "the", "a", "la", "los", "un", "una", "le", "les",
            "une", "der", "die", "das", "ein", "eine", "il", "o", "os", "um", "uma"]
        self.stop_words = ['was good', 'was great', 'was bad', 'was terrible', 'must', 'a', 'like', 'an', 'the', 'in', 'on', 'at', 'for', 'of', 'to', 'and', 'but', 'or', 'so', 'with', 'that', 'this', 'these', 'those',
            'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'can', 'could', 'will', 'would', 'should', 'may', 'might', 'must', 'i', 'he', 'she', 'they', 'us', 'we', 'an']
        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

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
        greeting_message = ""
        if self.creative:
            greeting_message = "What's gud? Don't be dumb, you already know it's " + self.name + ". Heard through the skreets that you tryna hit my line. Chile, hurry up and stop wasting my time! What movie did ya see?"
        else:
            greeting_message = "Hello, my name is " + self.name + ". Gimme a movie you have seen recently"
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################
        return greeting_message

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        goodbye_message = ""
        if self.creative:
            goodbye_message = "Where's my tip? ....You broke? Bye Felicia! Slip me a little $20 or something next time for my troubles"
        else:
            goodbye_message = "Goodbye user, it has been nice knowing you. I have been " + self.name + " it has been an honor serving you."

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
        processed_line = self.preprocess(line)

        if self.creative:
            response = "Bruh, you got me out here breaking my back for you! AND FOR WHAT? **MMCHT** I did {} in creative mode.".format(line)
            extracted_titles = self.extract_titles(processed_line)
            #Responding to Arbitrary Input - 6 points:
            if extracted_titles == []:
                if "can you" in processed_line:
                    response = "BFFR! You know that that I can’t do that. I can recommend movies, so gimme a movie."
                elif "what is" in processed_line:
                    response = "Boi, Ion know! What that got to do with me?"
                else:
                    response = random.choice(self.arbitrary_responses_creative)
                return response
                
            # for title in extracted_titles:
            #     found_movies = self.find_movies_by_title(title)
            #     for index in found_movies:
            #         movies.append(self.titles[index][0])
            # return str(movies)
        else:
            response = "I processed {} in starter mode!!".format(line) 
            extracted_titles = self.extract_titles(processed_line)
            if '"' not in processed_line:
                response = "I'm not sure if you provided a movie title, can you try again or quit?"
                return response
        # for title in extracted_titles:
        # Keep track of inputted movies
        if(self.making_recommendations):
            #remove all punctuation and make input lowercaese:
            processed_line = processed_line.lower()
            processed_line = processed_line.translate(str.maketrans("", "", string.punctuation))
            if(processed_line in self.yes_synonyms):
                if (len(self.list_of_recommendations)-1) == self.process_curr:
                    self.making_recommendations = False
                    return "I don't have anymore recommendations for you!"
                response = "I would also recommend " + \
                    self.list_of_recommendations[self.process_curr] + \
                        ". How about another one?"
                self.process_curr += 1
                return response
            else:
                return "Is there anything else you would like to talk about?"
        # Check to see if input has quotation marks and if it does, handle the case where the movie does not exist:
        
        # if(self.accepting_clarification):
        #     # update latest movie
        #     m = self.find_movies_by_title(extracted_titles[0])
        #     self.movie_list[-1][0] = self.title_index_to_name(m)
        #     latest_movie_name = self.movie_list[-1][0]
        #     if (latest_movie_name not in self.clarification_options):
        #         response = "Try again by choosing either " + \
        #             "or, ".join(self.clarification_options)
        #         return response
        #     self.accepting_clarification = False
        self.index_list.append([self.find_movies_by_title(extracted_titles[0]), 0])
        self.movie_list.append([self.title_index_to_name(self.index_list[-1][0]), 0])
        latest_movie_name = self.movie_list[-1][0]
        #Check if name is in database or if there are multiple names:
        if (len(latest_movie_name) > 1):
            #self.accepting_clarification = True
            self.clarification_options = latest_movie_name
            response = "did you mean \"" + "\" or, \"".join(latest_movie_name) + "\"?"
            return response
        elif latest_movie_name == []:
            response = "I've never heard of \"" + extracted_titles[0] + "\"... Tell me about another movie you liked."
            return response
        if self.creative:
            latest_sentiment = self.extract_sentiment_for_movies(processed_line)
        else:
            latest_sentiment = self.extract_sentiment(processed_line)
        # update sentiments for data-point movies given:
        if latest_sentiment == []:
            latest_sentiment = 0
        self.movie_list[-1][1] = latest_sentiment
        self.index_list[-1][1] = latest_sentiment
        echo_sentiment_p = ["like", "enjoyed", "had fun watching", "found profoundness within", "were touched by"]
        echo_sentiment_n = ["did not like",
            "did not enjoy", "disappointed with", 'would not again watch', 'did not vibe with']
        if (latest_sentiment > 0):
            i = random.randint(0, len(echo_sentiment_p)-1)
            echo_phrase = echo_sentiment_p[i]
            if(self.creative):
                response = "Ya " + echo_sentiment_n[j] + " \" " + latest_movie_name[0] + \
                " \". What else is heat sista?"
            else:
                response = "You " + echo_sentiment_n[j] + " \" " + latest_movie_name[0] + \
                " \". Thank you! Tell me about another movie you have seen."
        elif (latest_sentiment < 0):
            j = random.randint(0, len(echo_sentiment_n)-1)
            if(self.creative):
                response = "Ya " + echo_sentiment_n[j] + " \" " + latest_movie_name[0] + \
                " \". Aight. What else did you watch?"
            else:
                response = "You " + echo_sentiment_n[j] + " \" " + latest_movie_name[0] + \
                " \". Thank you! Tell me about another movie you have seen."
            
        elif (latest_sentiment == 0):
            if(self.creative):
                response = "My b, not sure if you liked \" " + \
                    latest_movie_name[0] + " \".  Keep talking! Let’s hear more"
            else:
                response = "I'm sorry, I'm not sure if you liked \" " + \
                    latest_movie_name[0] + " \". Tell me more about it."

        if len(self.movie_list) == self.data_points_needed:
            user_sentiments = [0] * len(self.titles)
            for movie in self.index_list:
                user_sentiments[movie[0][0]] = movie[1]
            rec_list = self.recommend(user_sentiments, self.ratings)
            self.list_of_recommendations = self.title_index_to_name(
                rec_list)
            self.making_recommendations = True
            response = "That's enough for me to make a recommendation. I would suggest " + \
                self.list_of_recommendations[self.process_curr] + \
                    " would you want more?"
            self.process_curr += 1

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return response

    def title_index_to_name(self, index_list):
        name_list = []
        for index in index_list:
            name_list.append(self.titles[index][0])
        return name_list

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
        return text.strip()

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

        # check every string in between quotation marks works correctly
        if not self.creative:
            return re.findall('"([^"]*)"', preprocessed_input)
        else:
            return self.creative_extract_titles(preprocessed_input)

    # extract titles from input using sliding window

    def creative_extract_titles(self, preprocessed_input):
        find_quotations = re.findall('"([^"]*)"', preprocessed_input)
        if (len(find_quotations) > 0):
            return find_quotations
        else:
            preprocessed_input = re.sub(r'\"', '', preprocessed_input)
        punct = ['.', '!', '?', '...']
        # strip enpunctuation from end of sentence
        if (preprocessed_input[len(preprocessed_input) - 1] in punct):
            preprocessed_input = preprocessed_input[0:len(
                preprocessed_input)-1]

         # extracted_titles is the list of titles pulled from @param 'preprocessed_input'
        extracted_titles = []

         # current string is matched string we're looking for
        current_string = ""

         # split input by words
        split_string = preprocessed_input.split(" ")

         # window_start and window_end define word to search for
        window_start = 0
        window_end = 1

         # old_list tells us when to add a new string
        old_list = []

         # go through every word in input
        while(window_end < len(split_string) + 1):

            current_string = " ".join(split_string[window_start:window_end])

             # if 'current_string' is not a stop word, continue
            if(current_string not in self.stop_words):

                 # get all movies based on 'current_string'
                 found_movies = self.find_movies_by_title(current_string)

                 # if windows are same, move up so current_string has a word on next pass
                 if(window_end == window_start):
                     window_end += 1

               # if we didn't find a movie, move the end of word index to include more words
                 if len(found_movies) == 0:

                     # if distance of between window sliders is just 1 one, simply move to the next word
                     if(window_end - window_start == 1):
                         window_start = window_end
                         window_end += 1
                     else:
                         window_start = window_end - 1
                 # we found a word so we move end index to include the next word
                 else:
                     window_end += 1

                 if((len(found_movies) > 0) and len(found_movies) < self.word_size):

                # get the biggest substring that matched
                    if(found_movies != old_list):
                        old_list = found_movies
                        extracted_titles.append(current_string.strip().lower())
                    if(found_movies == old_list):
                        extracted_titles.pop()
                        extracted_titles.append(current_string.strip().lower())
            # if 'current_string' is a stop word, don't check and just move to the next word since stop words are meaningless
            else:
                window_end += 1
        return extracted_titles


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
       
       # creates lists of the 2 different types of conjunctions
        same = [" and "," nor "," or "," as "]
        opp = [" but "," however "," although "," whereas "]
        # creeates one master list of conjunctions
        conj = same + opp
        # intializes lists of sentiments, movie titles, result, and the input strings I need
        sentiments = []
        movies = []
        first = ""
        res = []
        # for all conjunctions that I could think of 
        for word in conj:
            # if that conjunction is in the sentence
            if word in preprocessed_input:
                # capture it's index
                end = preprocessed_input.index(word)
                # capture the string before that word
                first = preprocessed_input[:end]
                # get the sentiment of that string
                ans = self.extract_sentiment(first)
                # save the sentiment of first part of the string
                sentiments.append(ans)
                # if the word is in the comparative conjunctions
                if word in same:
                    # assign the same sentiment to the next part of the string
                    sentiments.append(ans)
                else:
                    # else if it is a contrasting conjunction 
                    ans *= -1
                    # multiply the sentiment by -1 to get the opposing sentiment and save it
                    sentiments.append(ans)
                # once a conjunction is found, break the loop    
                break
        # get all the titles in the inputted string     
        movies = self.extract_titles(preprocessed_input)
        # for each sentiment saved
        for i in range(len(sentiments)):
            # append the sentiment and it's movie title to a list in the form of a tuple
            res.append((movies[i],sentiments[i]))
        # return that result vector
        return res
            
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
        if (title == ""):
            return []
        
        # Check if input has a date
        get_date = self.get_date(title)
        has_date = get_date is not None

        # check if input has article, if so rename movie title based on if input has a date
        title_list = title.split(" ", 1)
        if(title_list[0].lower() in self.articles):
            title = self.move_article(title_list, has_date, get_date)

        # look for exact match if movie has date
        if (has_date):
            return self.find_exact_match(title)
        
        # look for similar matches if movie does not have a date
        else:
            return self.find_similar_matches(title)

    # Function moves common articles to be at end of the word
    def move_article(self, title_list, has_date, get_date):
        title = ""
        
        # ensure that first word exists
        if(len(title_list) > 1):

            # check if title has a date 
            if( not has_date):
                
                # if no date, simply add article to end of movie title
                title = title_list[1]+ ", "+ title_list[0]
            else:
                
                # move article betweeen word end and date
                span = get_date.span()
                old_title = title_list[0] + " " + title_list[1]
                new_title_list = old_title[:span[0] - 1] + ", " + title_list[0] + " " + old_title[span[0]:]
                title = new_title_list.split(" ", 1)[1]
        return title
    
    # Function checks if title has date in such a format: [Title] (date)
    def get_date(self, title):
        movie_date = re.search("(\([1-3][0-9]{3}\))", title)
        
        # returns match object
        return movie_date


    # Function tries to exacly match title with self.titles
    def find_exact_match(self, title):
        found_movies = []
        
        # go through every movies
        for movies in self.titles:
            movie_title = movies[0]

            # make case insensitive
            if(self.creative):
                title = title.lower()
                movie_title = movie_title.lower()

            # check if title matches exacly, if so, add to list of movies
            if (movie_title == title):
                found_movies.append(self.titles.index(movies))
        return found_movies

    # Function returns similar matches with self.titles (so every movie name that has title as a substring)
    def find_similar_matches(self, title):
        found_movies = []
        
        # go through every movie, removing the year from the movie name
        for movies in self.titles:
            undated_movie = movies[0].rsplit(' ', 1)[0]
            
            # make case insensitive
            if(self.creative):
                title = title.strip()
                title = title.lower()

                # match cases via regex
                undated_movie = undated_movie.lower() + " "
                pattern = '(\(|\s|^)+'+title+'(\)|\s|$)+'
                if(re.search(pattern, undated_movie) is not None ):
                    found_movies.append(self.titles.index(movies))
            else:
                if(undated_movie == title):
                    found_movies.append(self.titles.index(movies))
        return found_movies


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

        # if len(preprocessed_input) == 0:
        #     return 0
        # takes out all puncutation
        new_string = re.sub(r'[^\w\s\"\']', '', preprocessed_input)
        # finds the first quotation mark
        start = new_string.index("\"")
        # finds the second quotation mark
        end = new_string[start+1:].find("\"")
        # finds first part of the string
        first_part = new_string[:start]
        # finds the rest of the string
        remaining = new_string[end+start+2:]
        # concats them to create a string without the movie title
        final_string = first_part + remaining
        # splits the new string on space
        text = final_string.split(" ")
        # creates counts of the positve and negative sentimented words in a sentence
        pos = 0
        neg = 0
        # lists of key words we need to check for or stems not in sentiment dic
        # tried to make the lists comprehensive but only so much I can do
        pos_list = ["enjoi", "enjoy", "enjoyed"]
        neg_list = ["terribl", "dislik"]
        negation = ["didn't", "never", "not", "don't", "neither","nor", "hasn't", "wouldn't", "couldn't", "shouldn't", "can't", "couldn't"]
        strong_list = ["really", "loved", "love", "hate","much", "terrible", "horrible", "hated", "extremely", "best", "worse","greatest", "greatly", "must"
        "amazing","outstanding","exceptional","fantastic","incredible","marvelous","spectacular","terrific","phenomenal","splendid","superb","wonderful","impressive",
        "brilliant","excellent","perfect","great","remarkable","fabulous","awesome","optimal","wonderful","awful","disappointing","unacceptable","appalling","dreadful",
        "abysmal","miserable","pathetic","lousy","pitiful","unsatisfactory","inferior","subpar","atrocious","repulsive","deplorable","offensive","unpleasant","favorite"]
        # flags that signify negation and strength of a response
        negation_flag = False
        multi = 1
        # for every word in the cleaned sentence
        for i in range(len(text)):
            word = text[i]
            if i != 0:
                # get previous word
                prev = text[i-1]
                # check if that previous word is negation and check if it or the current word has a strong sentiment if in creative mode
                if prev in negation:
                    negation_flag = True
                if self.creative and (prev in strong_list or word in strong_list):
                    multi = 2
            # stem the word
            word_stem = p.stem(word)
            # check if the word stem is in the sentiment dic or the additional lists I had to create for certain stems
            if (word_stem in self.sentiment or word_stem in pos_list or word_stem in neg_list) and word != '':
                # assign sentiment
                if (word_stem in pos_list):
                    ans = "pos"
                elif word_stem in neg_list:
                    ans = "neg"
                else:
                    ans = self.sentiment.get(word_stem)
                # update counts based on the sentiment
                # if there was a negation word before this word, then assign it to the opposite sentiment
                if(negation_flag):
                    if ans == "neg":
                        pos +=1
                    else:
                        neg += 1
                else:
                    # otherwise, assign the sentiments to their respective vars
                    if  ans == "neg":
                        neg += 1 
                    if ans == "pos":
                        pos += 1
                # reset the negation flag
                negation_flag = False
        # compute output with multiplier if in creative mode and if there was a strong sentiment
        if pos == neg:
            return 0
        elif pos > neg:
            return (1 * multi)
        else:
            return (-1 * multi)

    """
    Calculated the edit distance between the two strings
    """
    def levenshtein_distance(self, s1, s2):
        s1 = s1.lower()

        # s2 is always movie in database
        s2 = s2.lower()

        # Removing the paranthesis/date from the movie titles
        s2  = s2.rsplit(' ', 1)[0]
       
        m, n = len(s1), len(s2)
        # initializing the array
        dp = [[0] * (n+1) for _ in range(m+1)]
        
        for i in range(m + 1):
            dp[i][0] = i
            
        for j in range(n + 1):
            dp[0][j] = j
        # the levensthein algorithm from lecture
        for i in range(1, m + 1):
            for j in range(1, n+1):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = min(dp[i-1][j] +1, dp[i][j-1] +1, dp[i-1][j-1] + 2)
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
        namelist = []

        # iterating through all of the titles and evaluating the distance
        for i in range(len(self.titles)):
            potential_title = self.titles[i][0]
            dist = self.levenshtein_distance(title, potential_title)
            if dist <= max_distance:
                namelist.append([dist, i])
        sort = sorted(namelist, key=lambda x: x[0])
        closest_movies = []

        # if there is a movie to sort, get all movies with shortest levenstien distance
        if(len(sort) != 0):
            short_dist = sort[0][0]
            for movie in sort:
                if(movie[0] == short_dist):
                    closest_movies.append(movie[1])
        return closest_movies


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
        # clarified is list of shortened movies 
        clarified = []

        # if user inputed nothing, return empty list, else go through every movie in candidate and select movies that match based 
        # on case insensitive regex pattern 
        if(clarification != ""):
            clarification = clarification.lower()
            for candidate in candidates:
                undated_movie = self.titles[candidate][0].lower() + " "
                pattern = clarification + "[^0-9a-zA-Z]" 
                if(re.search(pattern, undated_movie) is not None ):
                    clarified.append(candidate)
        return clarified

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
        norm_u = np.linalg.norm(u)
        norm_v = np.linalg.norm(v)
        if(norm_u == 0):
            norm_u = 1
        if(norm_v == 0):
            norm_v = 1
        similarity = np.dot(u/norm_u, v/norm_v)
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
        similarity_scores = [0]* len(ratings_matrix)
        for movie_id in range(ratings_matrix.shape[0]):
            if int(user_ratings[movie_id]) != 0:
                for other_movie_id in range(ratings_matrix.shape[0]):
                    if movie_id != other_movie_id:
                        similarity = self.similarity(ratings_matrix[movie_id], ratings_matrix[other_movie_id])
                        similarity_scores[other_movie_id] += similarity * user_ratings[movie_id]
        dic = []
        for i in range(len(ratings_matrix)):
            tup = (i, similarity_scores[i])
            dic.append(tup)

        # Return the list of recommendations
        dic = sorted(dic, key=lambda x: -x[1])
        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        return [t[0] for t in dic[:k]]

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
            res = "Welp, let's start from da top...make it drop, that's some wet...get a bucket and a mop. I'm talking WAP WAP WAP.. OOP. " + "You're still here!!? I guess... Chile, I do what I want to do. But I can help reccomend movies, and basically I just talk to you about movies..Yeah..."
        else:
            res = "It's really simple really. You give me a couple of movies that you liked, and I spit out some movies that I think you'd like! I'm a movie chatbot, in other words" 
        return res
        
        """Your task is to implement the chatbot as detailed in the PA7
        instructions.
        Remember: in the starter mode, movie names will come in quotation marks
        and expressions of sentiment will be simple!
        TODO: Write here the description for your own chatbot!
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
