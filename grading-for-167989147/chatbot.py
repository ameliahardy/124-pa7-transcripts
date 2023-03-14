# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import re
import numpy as np
import random


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'Movie_Recommender'

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

        self.indexmappingtotitle = {}
        self.indextotitlewodate = {} #index --> title w/o date
        self.indextodate = {} # index --> only title's date
        value = 0
        for i in self.titles:
            self.indexmappingtotitle[value] = i[0]
            self.indextotitlewodate[value] = re.sub('\s\((\d{4})\)$', "" ,i[0])
            self.indextodate[value] = re.sub('[^\((\d{4})\)]',"", i[0])
            value += 1

        self.rated_movies = []

        self.recommended_titles = []

        self.recommend_mode = False 

        self.num_recommended = 0

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

        greeting_message = "Hello! What can I do for you?"

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

        goodbye_message = "I hope you have a nice day!"

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return goodbye_message

    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################

    def tokenize(self,sentence):
        # Define a list of characters to be considered as delimiters
        breaks = [" ", ".", ",", "!", "?", ";", ":", "\n"]
        
        # Tokenize the input string by splitting it based on the delimiters
        tokens = []
        current_token = ""
        for char in sentence:
            if char not in breaks:
                current_token += char
            else:
                if current_token != "":
                    tokens.append(current_token)
                    current_token = ""
        
        # Append the last token if it exists
        if current_token != "":
            tokens.append(current_token)
            
        return tokens
    
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
        
        #Asking questions

        ## Communicate sentiment and movie back to user 

        if self.recommend_mode:
            affirmative_words = ["Yes", "Sure", "Yeah", "Ye", "Ya", "Please", "Great"]
            if line in affirmative_words:
                response_options = ["Sure! I reckon you'd love {} too. Want more?", "No prob! Try {} too. Would you like another recommendation?", "I think {} would be perfect for you! Want more suggestions?"]
                ran_int = random.randint(0,3)
                response = response_options[ran_int].format(self.recommended_titles[self.num_recommended])
                self.num_recommended += 1
            else:
                response = "No problem! You know where I am if you ever want more recommendations!"            
        
        else:
            sentiment = self.extract_sentiment(line)
            extracting_title = self.extract_titles(line)
            user_ratings = np.zeros(len(self.indexmappingtotitle))

            movie_id = self.find_movies_by_title(extracting_title[0]) #list of ids of matching movies 
            if len(movie_id) == 0:
                response = "I've never heard of {}, really sorry! Can you tell me about another movie you liked?".format(extracting_title)
            else: 
                first_movie_id = movie_id[0]
                movie_title = self.indexmappingtotitle[first_movie_id] #list of titles of movies 

                movie_title_wodate = self.indextotitlewodate[first_movie_id] #movie name without date

                if len(movie_id) == 1:
                    if sentiment >= 1:
                        response = "So you liked {} huh? Tell me about another movie you liked!".format(extracting_title[0])
                        user_ratings[first_movie_id] = 1
                    elif sentiment <= -1:
                        response = "So you didn't enjoy {} right? Tell me about movie you did like!".format(movie_title)
                        user_ratings[first_movie_id] = -1
                    elif sentiment == 0: 
                        response = "I'm not sure if you liked {}. Tell me more about it".format(movie_title)
                elif len(movie_id) > 1:
                    response = "I found more than one movie called {}. Can you clarify which one you like?".format(movie_title_wodate)
                
            ## Recommend movies based on what they have told us so far 

                for i in range(len(user_ratings)):
                    if user_ratings[i] != 0:
                        self.rated_movies.append(i)

                print(self.rated_movies)
                
                if len(self.rated_movies) >= 5: 
                    recommendation_ids = self.recommend(user_ratings, self.ratings, k=10)
                    print(recommendation_ids)
                    for i in range(len(recommendation_ids)):
                        recommended_title = self.indexmappingtotitle[recommendation_ids[i]]
                        self.recommended_titles.append(recommended_title)
                    response = "Given what you've told me, I think you would love {}. Would you like more recommendations?".format(self.recommended_titles[self.num_recommended])
                    self.num_recommended += 1
                    self.recommend_mode = True 

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

        if self.creative == False:
            match = re.findall(r'"([^"]*)"',preprocessed_input)
            if match:
                return match
            else:
                return []

        ## Creative task:


        else:
            listofwords = proprocessed_input.lower().strip(".,?!").split()

            
            listofmatches = []
            for start in range(len(listofwords)):
                for end in range(1, len(listofwords) + 1):
                    for movie in self.titles:
                        variable = " ".join(listofwords[start:end])
                        if variable == movie[0].lower():
                            listofmatches.append(variable)
                        else:
                            continue

            return listofmatches           
                
    
        
        

        



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
	    #split the title
        tokens = re.split(r'\s', title)
        reworded_title = title
        year = None
        if bool(re.search("\((\d{4})\)$", tokens[-1])): #if there's a year at the end
            year = tokens[-1]
            if bool(re.search("(?i)^(the|an|a)", tokens[0])): #if there's an article at the beginning:
                first_word_article = tokens[0]
                reworded_list = tokens[1:-1]
                reworded_list.extend([",", first_word_article, year])
                reworded_title = ' '.join(map(str,reworded_list))
                reworded_title = reworded_title.replace(" ,", ",")
        else:
            if bool(re.search("(?i)^(the|an|a)", tokens[0])): #if there's an article at the beginning
                first_word_article = tokens[0]
                reworded_list = tokens[1:]
                reworded_list.extend([",", first_word_article])
                reworded_title = ' '.join(map(str,reworded_list))
                reworded_title = reworded_title.replace(" ,", ",")


        #split the title
        tokens = re.split(r'\s', title)
        reworded_title = title
        year = None
        if bool(re.search("\((\d{4})\)$", tokens[-1])): #if there's a year at the end
            year = tokens[-1]
            if bool(re.search("(?i)^(the|an|a)", tokens[0])): #if there's an article at the beginning:
                first_word_article = tokens[0]
                reworded_list = tokens[1:-1]
                reworded_list.extend([",", first_word_article, year])
                reworded_title = ' '.join(map(str,reworded_list))
                reworded_title = reworded_title.replace(" ,", ",")
        else:
            if bool(re.search("(?i)^(the|an|a)", tokens[0])): #if there's an article at the beginning
                first_word_article = tokens[0]
                reworded_list = tokens[1:]
                reworded_list.extend([",", first_word_article])
                reworded_title = ' '.join(map(str,reworded_list))
                reworded_title = reworded_title.replace(" ,", ",")

        index = 0
        titleindexlist = []
        titleswodate = list(self.indextotitlewodate.values())
        titlesdate = list(self.indextodate.values())
        for i in titleswodate:
            if i in reworded_title:
                if year:
                    if year == titlesdate[index]:        
                        titleindexlist.append(index)
                else:
                    titleindexlist.append(index)
            index += 1
            
        return titleindexlist
    
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
        # Remove movie title and tokenize
        
        
        preprocessed_list = re.sub(r'\".+?\"', '', preprocessed_input)
        text_tokenized = self.tokenize(preprocessed_list)
    
        
        # Set a list of contradiction words
        
        contradictions = ["but"]
        
        # Set a list of negative words
        
        negative = ["n't","don't","didn't","not","never"]
        negation = False
        contradiction_indicator = False
        
        total = 0
        
        for word in text_tokenized:
            # Correct porter stemmer
            if word[-2:] == "ed" and word[-3] == "y":
                word = word[:-2]
            if word[-2:] == "ed" and word[-3] != "y":
                word = word[:-1]
                
            if word in contradictions:
                contradiction_indicator = True
                total = - total
                break
            if word in negative:
                negation = True
            if word in self.sentiment:
                if self.sentiment[word] == 'pos':
                    total +=1
                if self.sentiment[word] == 'neg':
                    total -=1

        if self.creative == False:                            
            if negation == True and contradiction_indicator == False:
                return -1
            elif total > 0:
                return 1
            elif total < 0: 
                return -1
            elif total == 0:
                return 0

        else:
            if negation == True and contradiction_indicator == False:
                return -1
            elif total >= 2:
                return 2
            elif total > 0 and total < 2:
                return 1
            elif total < 0 and total > -2: 
                return -1 
            elif total <= -2: 
                return -2
            elif total == 0:
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
        pass

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
                if ratings[i,j] > threshold:
                    binarized_ratings[i,j] = 1
                elif ratings[i,j] <= threshold and ratings[i,j] != 0:
                    binarized_ratings[i,j] = -1

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
        top = np.dot(u,v)
        bottomfirst = np.sqrt(np.sum(u**2))
        bottomlast = np.sqrt(np.sum(v**2))
        denominator = bottomfirst * bottomlast
        similarity = top/denominator
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

        :param user_ratings: a binarized 1D numpy array of the user's movie ratings
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
    
    
        # APPENDING ALL THE MOVIES INDEX THE USER RATED

        Binarized_user = user_ratings
        Binarized_matrix = ratings_matrix

        
        
    

        listofvalidmovies = []
        for i in range(len(Binarized_user)):
            if Binarized_user[i] != 0:
                listofvalidmovies.append(i)
    
    
        moviedict = {}
        for i in range(len(Binarized_matrix)):
            sums = 0
            for j in listofvalidmovies:
                if i != j and np.sum(Binarized_matrix[j]) != 0 and np.sum(Binarized_matrix[i]) != 0:
                    sums += self.similarity(Binarized_matrix[j], Binarized_matrix[i]) * Binarized_user[j]
            moviedict[i] = sums


        
        listofvalues = []
        for i in moviedict.values():
            listofvalues.append(i)
        
        listofvalues.sort(reverse = True)
        
        listorder = []
        for i in listofvalues:
            for j in moviedict:
                if moviedict[j] == i:
                    listorder.append(j)

        # newlistforlistorder = listorder
        # for i in listorder:
        #     if i in listofvalidmovies:
        #         while listorder.count(i) > 1:
        #             listorder.remove(i)
                
        recommendations = listorder[0:k]
    
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


        """ 
        Your task is to implement the chatbot as detailed in the PA7
        instructions.
        Remember: in the starter mode, movie names will come in quotation marks
        and expressions of sentiment will be simple!
        TODO: Write here the description for your own chatbot!
        """
        return "This chatbot will recommend you movies based on your preferences!"


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
