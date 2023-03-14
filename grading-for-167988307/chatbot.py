# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)

######################################################################
import util
import re
import numpy as np
from numpy.linalg import norm


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
        
        # Our additions
        self.userRatings = np.zeros(np.array(self.titles).shape[0])
        self.gaveRecs = False
        self.Recs = []
        self.recIndex = 0
        self.moreDetail = False

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

        greeting_message = "Hi, I'm a movie reccomendation chatbot. To get started please tell me about some movies you've seen."

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
        
        response = ""
        if self.creative:
            pass
        else:
            if self.gaveRecs:
                yes_list = ["yes", "yup", "yeah", "absolutely", "indeed", "certainly", "affirmative", "roger that", "for sure", "definitely", "okay", "OK", "right", "correct", "agreed", "you bet", "no problem", "sure thing", "aye", "very well", "totally", "without a doubt", "of course", "by all means", "gladly", "positively", "OK, I'm in", "uh-huh", "yep", "surely", "exactly", "precisely", "that's right", "that's correct"]
                no_list = ["no", "nope", "nah", "not at all", "negative", "never", "no way", "I don't think so", "not really", "definitely not", "sorry", "unfortunately", "regrettably", "denied", "vetoed", "I disagree", "I object", "not a chance", "absolutely not", "by no means", "no siree", "no thanks", "hard pass", "I'm afraid not", "not on your life", "not for anything", "not in a million years", "no can do", "I'm not up for it", "I'm not interested", "not worth it", "not my thing"]
                if line.lower() in yes_list:
                    response = "{} is another movie I believe you would like. Do you want another recommendation?".format(self.titles[self.Recs[self.recIndex]][0])
                    self.recIndex += 1
                elif line.lower() in no_list:
                    response = "Sounds good! If you would like tell me about more movies for a better recommendation. To quit the application type ':quit'."
                    self.gaveRecs = False
                    self.recIndex = 0
                else:
                    response = "I don't quite understand that response. Please try again..."
            elif self.moreDetail:
                self.moreDetail = False
                sentiment = self.extract_sentiment(line)
                if sentiment == 0:
                    response = "I couldn't tell if you liked {}. Tell me more about it.".format(self.possMovies[0])
                    self.moreDetail = True
                else: 
                    indicies = self.find_movies_by_title(self.possMovies[0])
                    self.userRatings[indicies[0]] = sentiment
                    if len(np.nonzero(self.userRatings)[0]) >= 5:
                        self.gaveRecs = True
                        self.Recs = self.recommend(self.userRatings, self.ratings)
                        response = "Based on what you've told me I think you would really enjoy {}. Would you like another recommendation?".format(self.titles[self.recIndex][0])
                        self.recIndex += 1
                    elif sentiment == 1:
                        response = "So you liked {}. Tell me about another movie you've seen!".format(self.possMovies[0])
                    elif sentiment == -1:
                        response = "So you didn't like {}. Tell me about another movie you've seen!".format(self.possMovies[0])
            else:
                possMovies = self.extract_titles(line)
                if len(possMovies) == 0:
                    response = "I'm sorry. I'm not sure how this relates to movies."
                elif len(possMovies) > 1:
                    response = "Woah there, only one movie at a time."
                else:
                    indicies = self.find_movies_by_title(possMovies[0])
                    if len(indicies) == 0:
                        response = "Huh? I've never heard of that one. Have you watched any other movies?"
                    elif len(indicies) > 1:
                        response = "I found more than one movie called {}. Could you be more specific?".format(possMovies[0])
                        response += " The movies I found are "
                        for index in indicies:
                            response += self.titles[index][0] + ", "
                        response = response[:-2] + "."
                    else:
                        sentiment = self.extract_sentiment(line)
                        if sentiment == 0:
                            response = "I couldn't tell if you liked {}. Tell me more about it.".format(possMovies[0])
                            self.moreDetail = True
                            self.possMovies = possMovies
                        else:    
                            self.userRatings[indicies[0]] = sentiment
                            if len(np.nonzero(self.userRatings)[0]) >= 5:
                                self.gaveRecs = True
                                self.Recs = self.recommend(self.userRatings, self.ratings)
                                response = "Based on what you've told me I think you would really enjoy {}. Would you like another recommendation?".format(self.titles[self.recIndex][0])
                                self.recIndex += 1
                            elif sentiment == 1:
                                response = "So you liked {}. Tell me about another movie you've seen!".format(possMovies[0])
                            elif sentiment == -1:
                                response = "So you didn't like {}. Tell me about another movie you've seen!".format(possMovies[0])
                            
        
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
        def tempComb(wordList):
            returnList = []
            curSize = len(wordList)
            while curSize != 0:
                for j in range(len(wordList)):
                    end = curSize + j
                    if  end <= len(wordList):
                        returnList.append(" ".join(wordList[j:end]))
                curSize -= 1
            return returnList      
        
        quotedTitles = re.findall(r'"([^"]*)"', preprocessed_input)
        if self.creative == False and len(quotedTitles) == 0:
            preprocessed_input = re.sub(r'[^\w\s]', '', preprocessed_input)
            for title in tempComb(preprocessed_input.split(" ")):
                titleText = getUserInputTitle(title).lower()
                titleYear = getDateFromSelfTitles(title)
                for i in range(len(self.titles)):
                    matchText = getTitlefromSelfTitles(self.titles[i][0]).lower()
                    matchYear = getDateFromSelfTitles(self.titles[i][0])
                    if titleText == matchText and (titleYear == matchYear or titleYear == None):
                        return [matchText]
        return quotedTitles
            


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
        index = []
        def findSpecialSelfTitles(SelfTitles):
            res = []
            for i in range(len(SelfTitles)):
                returnStr = re.search(r'\([a-zA-Z0-9_ ]*[a-zA-Z_, ]+[a-zA-Z0-9_ ]*\)\s\(', SelfTitles[i][0])
                if returnStr != None:
                    res.append((SelfTitles[i], i))
            return res

        def getTitlefromSpecialSelfTitles(curTitle):
            returnStr = re.findall(r'\([a-zA-Z0-9_ ]*[a-zA-Z_, ]+[a-zA-Z0-9_ ]*\)', curTitle)
            return returnStr


        titleText = getUserInputTitle(title).lower()
        titleYear = getDateFromSelfTitles(title)

        for i in range(len(self.titles)):
            matchText = getTitlefromSelfTitles(self.titles[i][0]).lower()
            matchYear = getDateFromSelfTitles(self.titles[i][0])
            if self.creative == False:
                if (titleText == matchText) and (titleYear == matchYear or titleYear == None):
                    index.append(i)
            if self.creative == True:
                matchTextTemp = '(' + matchText + ')'
                if ((titleText == matchText) or ((' ' + titleText + ' ') in matchText) or ((' ' + titleText + ')') in matchTextTemp) or (('(' + titleText + ' ') in matchTextTemp)) and (titleYear == matchYear or titleYear == None):
                    index.append(i)

        if index == []:
            specialSelfTitles = findSpecialSelfTitles(self.titles)
            # print(specialSelfTitles)
                
            targets = []
            for i in range(len(specialSelfTitles)):
                targets = getTitlefromSpecialSelfTitles(specialSelfTitles[i][0][0])
                for target in targets:
                    new_target = target.replace("(", "" ).replace(")", "")
                    addList = [', Il', ', Lo', ', Det', ', Le', ', Un', ', Den', ', The', ', A', ', Der', ', Das', ', jie', ', Die', ', I', ', Une', ', Las', ', Los', ', La', ', Les', ', El']
                    # addList = [', a', ', A', ', an', ', An',', the',', The',', la',', La', ', el', ', El', ', una', ', Una', ', uno', ', Uno', ', un', ', Un', ', il', ', Il', ', le', ', Le', ', los', ', Los', ', las', ', Las', ', une', ', Une', ', ein', ', Ein', ', eina', ', Eina', ', die', ', Die', ', der', ', Der', ', den', ', Den', ', um', ', uma', ', Um', ', Uma', ', o', ', O', ', os', ', Os', ', I', 'le', 'i', 'Le']
                    for word in addList:
                        if word == new_target[len(new_target) - len(word):]:
                            new_target = word[2:len(word)] + ' ' + new_target[0:len(new_target) - len(word)]
                            break
                    if new_target.lower() == title.lower():
                    # titleText = title.lower() 
                    # matchText = new_target.lower()
                    # matchTextTemp = '(' + matchText + ')'
                    # if ((titleText == matchText) or ((' ' + titleText + ' ') in matchText) or ((' ' + titleText + ')') in matchTextTemp) or (('(' + titleText + ' ') in matchTextTemp)):
                        index.append((specialSelfTitles[i][1]))
                        
        return index

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
        negCount, posCount, flip, word = 0, 0, False, ""
        oppositeWords = ["didn't", "never", "not", "don't"]
        for letter in preprocessed_input:
            if letter.isalnum() or letter == "'":
                word += letter
                if word in self.sentiment.keys():
                    if self.sentiment[word] == 'pos':
                        if flip == True:
                            negCount += 1
                        else: 
                            posCount += 1
                    else:
                        if flip == True:
                            posCount += 1
                        else: 
                            negCount += 1
            else:
                if word in oppositeWords:
                    flip = True
                word = ""
        if posCount > negCount:
            return 1
        elif posCount < negCount:
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
        change_word = -1
        change_word_size = 0
        res = []
        titles = self.extract_titles(preprocessed_input)
        indices = []
        for title in titles:
            indices.append(preprocessed_input.lower().find(title.lower()))

        change_words = ['but', 'however', 'although']
        for word in change_words:
            if word in preprocessed_input.lower():
                change_word = preprocessed_input.lower().find(word)
                change_word_size = len(word)
        start = 0
        if change_word != -1:
            sentiment_before = self.extract_sentiment(preprocessed_input[:change_word + change_word_size])
            sentiment_after = 0
            if sentiment_before == 1:
                sentiment_after = -1
            if sentiment_before == -1:
                sentiment_after = 1
            # sentiment_after = self.extract_sentiment(preprocessed_input[change_word + change_word_size:])
            for title in titles:
                if preprocessed_input.lower().find(title.lower()) < change_word:
                    res.append((title, sentiment_before))
                else:
                    res.append((title, sentiment_after))
        else:
            sentiment = self.extract_sentiment(preprocessed_input)
            for title in titles:
                res.append((title, sentiment))
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
        editDist = []
        for i in range(len(self.titles)):
            editDist.append((nltk_edit_distance(title.lower(), getTitlefromSelfTitles(self.titles[i][0].lower())), i))
        
        editDist.sort()
        returnList = []
        if editDist[0][0] > max_distance:
            return []
        for entry in editDist:
            if entry[0] == editDist[0][0]:
                returnList.append(entry[1])
            else: 
                break
        return returnList
        

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
        numList = []
        if clarification.isdigit():
            if len(clarification) == 4:
                for index in candidates:
                    if clarification in self.titles[index]:
                        numList.append(index)
                if len(numList) == 1:
                    return numList
            if int(clarification) <= len(candidates):
                for index in candidates:
                    if clarification in self.titles[index]:
                        numList.append(index)           
                if len(numList) == 0:
                    return [candidates[int(clarification) - 1]] 
                if len(numList) == 1:
                    return numList    
        if " recent" in clarification or 'newest' in clarification:
            retIndex, date = 0, float('-inf')
            for index in candidates:
                possDate = re.search(r'[0-9]{4}', self.titles[index][0]).group()
                if possDate != None and int(possDate) > date:
                    date = int(possDate)
                    retIndex = index
                return [retIndex]
        if " oldest " in clarification:
            retIndex, date = 0, float('inf')
            for index in candidates:
                possDate = re.search(r'[0-9]{4}', self.titles[index][0]).group()
                if possDate != None and int(possDate) < date:
                    date = int(possDate)
                    retIndex = index
                return [retIndex]

        subList = []
        for index in candidates:
            if clarification.lower() in self.titles[index][0].lower():
                subList.append(index)
        if len(subList) == 1:
            return subList
        
        mergeList = [item for item in numList if item in subList]
        if len(mergeList) == 1:
            return mergeList
        
        distList = []
        for index in candidates:
            distList.append((nltk_edit_distance(clarification.lower(), self.titles[index][0].lower()), index))
        distList.sort()
        temp = []
        for entry in distList:
            if entry[0] == distList[0][0]:
                temp.append(entry[1])
            else: 
                break
        distList = temp
        if len(numList) > 0 and distList > 0:
            newList = [item for item in numList if item in distList]
            if len(newList) > 0:
                return newList
        if len(numList) > 0:
            return numList
        return distList

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
        binarized_ratings = np.where(ratings == 0, 0, np.where(ratings > threshold, 1, np.where(ratings <= threshold, -1, 0)))

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
        denom = np.linalg.norm(u) * np.linalg.norm(v)
        if denom == 0:
            return 0
        similarity = np.dot(u,v)/denom
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
        #ratings_matrix = self.binarize(ratings_matrix) # include this line in sanitycheck

        recommendations = []
        def getRating(i):
            ratingsList = []
            curRow = ratings_matrix[i]
            j = 0
            for row in ratings_matrix:
                if user_ratings[j] != 0:       
                    ratingsList.append(self.similarity(row, curRow))
                else:
                    ratingsList.append(0)
                j += 1
                # ratingsList.append(np.dot(row, curRow)) # for some reason, doing this instead of the if/else statement above makes our implementation wrong
            return np.dot(ratingsList, user_ratings)

        newRatings = []
        for i in range(len(user_ratings)):
            if user_ratings[i] == 0:
                newRatings.append((getRating(i), i))
            else:
                if user_ratings[i] != 0:
                    newRatings.append((float('-inf'), i))
        newRatings.sort(reverse=True)
        recommendations = [entry[1] for entry in newRatings[:k]]
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
    
#########################################
# Self Written Helper Functions Section #
#########################################

def getDateFromSelfTitles(curTitle):
    returnStr = re.search(r'[0-9]{4}', curTitle)
    if returnStr == None:
        return None
    returnStr = returnStr.group().strip()
    returnStr = returnStr.replace("(", "").replace(")", "")
    return returnStr

def getUserInputTitle(curTitle):
    returnStr = re.search(r'^([^\(]*)', curTitle)
    if returnStr == None:
        return None
    return returnStr.group().strip()

def getTitlefromSelfTitles(curTitle):
    returnStr = re.search(r'^([^\(]*)', curTitle)
    if returnStr == None:
        return None
    returnStr = returnStr.group().strip()
    returnList = [' a', ' A', ' an', ' An', ' the', ' The']
    for word in returnList:
        if returnStr.endswith(word):
            returnStr = word[1:] + ' ' + returnStr[:-(len(word)+1)]
    return returnStr

def myComb(text):
    wordList = text.split(" ")
    returnList = []
    curSize = len(wordList)
    while curSize != 0:
        for j in range(len(wordList)):
            end = curSize + j
            if  end <= len(wordList):
                returnList.append(" ".join(wordList[j:end]))
        curSize -= 1
    return returnList
    
def runRubric():
    myChat = Chatbot()
    print(np.array([0,1,1,0,-1,0]))
    print(np.array([[1, 1, 1, 0],
                   [1, -1, 0, 1],
                   [1, 1, 1, 0],
                   [0, 1, 1, -1],
                   [0, -1, 1, -1],
                   [-1, -1, -1, 0]]))
    myChat.recommend(np.array([0,1,1,0,-1,0]), np.array([[1, 1, 1, 0],[1, -1, 0, 1],[1, 1, 1, 0],[0, 1, 1, -1],[0, -1, 1, -1],[-1, -1, -1, 0]]))
    print('--------------------------')
    inputs = ['I liked "The Notebook".', "You are a great bot!", 'I enjoyed "Titanic (1997)" and "Scream 2 (1997)"', "I liked The NoTeBoOk!", "I thought 10 things i hate about you was great"]
    print("extract_titles(input))")
    for i in range(len(inputs)):
        print("Input: " + str(inputs[i]) + "  -->  Output: " + str(myChat.extract_titles(inputs[i])))
    print()
    
##############################
# Imported Functions Section # 
##############################  
"""
This is the ntlk.edit_distance() function. We did not write this function and pulled 
it from the online nltk libraries. As per ed discussion post #1464 and #1652 we can copy and import function as long it is explicitly cited as done above.
"""
def nltk_edit_distance(s1, s2, transpositions=False):
    def _edit_dist_step(lev, i, j, s1, s2, transpositions=False):
        c1 = s1[i - 1]
        c2 = s2[j - 1]
        a = lev[i - 1][j] + 1
        b = lev[i][j - 1] + 1
        c = lev[i - 1][j - 1] + (c1 != c2)
        d = c + 1
        if transpositions and i > 1 and j > 1:
            if s1[i - 2] == c2 and s2[j - 2] == c1:
                d = lev[i - 2][j - 2] + 1
        lev[i][j] = min(a, b, c, d)
    def _edit_dist_init(len1, len2):
        lev = []
        for i in range(len1):
            lev.append([0] * len2)
        for i in range(len1):
            lev[i][0] = i
        for j in range(len2):
            lev[0][j] = j
        return lev
    len1 = len(s1)
    len2 = len(s2)
    lev = _edit_dist_init(len1 + 1, len2 + 1)
    for i in range(len1):
        for j in range(len2):
            _edit_dist_step(lev, i + 1, j + 1, s1, s2, transpositions=transpositions)
    return lev[len1][len2]

if __name__ == '__main__':
    runRubric()
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')