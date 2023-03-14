# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np

import porter_stemmer as ps

from numpy import random

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        self.name = 'Mr. Krabs'

        self.creative = creative

        self.rate_count = 0 

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        self.recommendations = []
        self.user_ratings = np.zeros(len(self.titles))

        self.recommendings = False

        ########################################################################
        # Binarize the movie ratings matrix.                             #
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
        ########################################################################                          #
        ########################################################################

        greeting_message = "Welcome to the Krusty Krab. I, Mr. Krabs, love money. I want to help you give more of your money to my movie streaming service side hustle. Tell me what movies you like!"

        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################
        return greeting_message

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        ########################################################################                             #
        ########################################################################

        goodbye_message = "Enjoy your films! Ar ar ar ar ar!"

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

        def consent(line):
            affirmative = ["yes", "ye", "yeah", "yur", "yerr", "yass", "affirmativ"]
            negative = ["no", "nope", "negativ"]
            yes_count = 0
            no_count = 0
            for word in affirmative:
                if word in line.lower():
                    yes_count += 1
            for word in negative:
                if word in line.lower():
                    no_count += 1
            if yes_count > no_count and len(self.extract_titles(line)) == 0:
                return 1 
            return 0 

        if self.creative == False:
            movie_titles = self.extract_titles(line)
            self.rate_count += 1
            response = ""

            if len(movie_titles) == 0:
                rand = random.randint(1, 4)
                if not self.recommendings:
                    if rand == 1:
                        response += "Arg matey! I'm not sure that's a movie! That's probably because I work all day, unlike you, you lazybones. Get a job at the Krusty Krab today!"
                    elif rand == 2:
                        response += "I only want to talk about movies today. Time is money!"
                    elif rand == 3:
                        response += "Not sure I recognize that film."
                    else:
                        response += "Answer my questions and you'll reap the rewards my friend. Don't keep me waiting!"
                    response += "Are you ready to hear the film recommendations that I have for you?"
                    self.recommendings = True

                else:
                    consent = consent(line)
                    if consent == 1:
                        rand = random.randint(1,3)
                        if rand == 1:
                            response = "I'm ready to give you some movie recommendations now! Try watching "
                        elif rand == 2:
                            response = "Piping hot movie recommendations, coming your way! Check out "
                        else:
                            response = "Movie recommendations for you, served with a smile (and a side pickle!). One movie I like is "
                            
                        self.recommendations = self.recommend(self.user_ratings, self.ratings, k=5, creative=False)
                        randNum = random.randint(0, 4)
                        response += " ".join(self.titles[randNum][0])
                        if rand == 1 or rand == 3:
                            response += "! Would you like another recommendation?"
                        else:
                            response += " :) Want another movie recommendation? I have tons of options - from ones loved by the spongiest of SpongeBobs to those hailed by the squiddiest of Squidwards!"
                    else:
                        self.recommendings = False
                        if rand == 1 or rand == 2:
                            response = "That's fine, if you're done chatting about films, how about buying yourself a Krabby Patty?"
                        else:
                            response = "Ok, got it."
            
            else:
                movie_indices = []
                for movie_title in movie_titles:
                    if len(self.find_movies_by_title(movie_title)) == 0:
                        return "I'm not sure I've heard of " + movie_title + " before. Tell me about another film!"
                    movie_indices += self.find_movies_by_title(movie_title)
                
                if len(movie_indices) > 1:
                    return "It sounds like you've mentioned more than one movie! Please talk about only one movie at a time."

                self.rate_count += 1
                sentiment = self.extract_sentiment(line)
                for movie in movie_indices:
                    self.user_ratings[movie] = sentiment

                if sentiment == 1:
                    rand = random.randint(1, 3)
                    if rand == 1:
                        response += "I'm glad to hear that you liked "
                        choice = 0
                        if len(movie_titles) > 1:
                            choice = random.randint(0, len(movie_titles))
                        response += movie_titles[choice] 
                        response += "! That's one of my daughter's favorites, too. I love my girl, Pearl!"
                    elif rand == 2:
                        response += " Interesting choice! I think I saw Plankton watching "
                        choice = 0
                        if len(movie_titles) > 1:
                            choice = random.randint(0, len(movie_titles))
                        response += movie_titles[choice] 
                        response += " on Karen the other day, but to each their own, I guess."
                    else:
                        word = movie_titles[0][0]
                        response += " "
                        response += word
                        response += "! That's one of my favorite things. I think I should check this movie out, too. Ar ar ar ar."
                    #return response
                elif sentiment == -1:
                    rand = random.randint(1, 3)
                    if rand == 1:
                        response += "Pee-yew. I can't stand "
                        choice = 0
                        if len(movie_titles) > 1:
                            choice = random.randint(0, len(movie_titles))
                        response += movie_titles[choice] 
                        response += " either. It makes me almost as nauseous as the food from the Chum Bucket does... but I digress."
                        #return response 
                    elif rand == 2:
                        response += "Not for you, huh? That's too bad. "
                        choice  = 0
                        if len(movie_titles) > 1:
                            choice = random.randint(0, len(movie_titles))
                        response += movie_titles[choice]
                        response += " was one of my wife's favorite movies. That was before the beaching..."
                        #return response 
                    else:
                        response += "I hate "
                        choice  = 0
                        if len(movie_titles) > 1:
                            choice = random.randint(0, len(movie_titles))
                        response += movie_titles[choice]
                        response += " too! Wow, we have so much in common. You should come work at my restaurant, none of my workers relate to me."
                        #return response 
                else:
                    response += "Sorry, I'm not sure what your thoughts are on "
                    response += movie_titles[0]
                    response += ". Can you elaborate more?"

                if self.rate_count >= 5:
                    response += " Great talking with you so far! Want to hear the film recommendations that I have for you?"
                    self.recommending == True
                    return response
                else:
                    rand2 = random.randint(1, 3)
                    if rand2 == 1:
                        response += "Tell me more about the movies that you like and don't like."
                        return response
                    elif rand2 == 2:
                        response += "Give me some more to work with! Some ketchup for that burger, some mayo for those fries. Give me an opinion about a movie that you've seen."
                        return response 
                    else: 
                        response += "Hit me again - give me one of those juicy, delectable, mouth-watering movie reviews."
                        return response

                return "Okay, sorry! If you're not here for recommendations, then buy a Krabby Patty or get out of my Krusty Krab!"
        
        else:
            movie_titles = self.extract_titles(line)

            response = ""

            if len(movie_titles) == 0:
                rand = random.randint(1, 4)
                if not self.recommendings:
                    if rand == 1:
                        response += "Arg matey! I'm not sure that's a movie! That's probably because I work all day, unlike you, you lazybones. Get a job at the Krusty Krab today!"
                    elif rand == 2:
                        response += "I only want to talk about movies today. Time is money!"
                    elif rand == 3:
                        response += "Not sure I recognize that film."
                    else:
                        response += "Answer my questions and you'll reap the rewards my friend. Don't keep me waiting!"
                    response += "Are you ready to hear the film recommendations that I have for you?"
                    self.recommendings = True

                else:
                    consent = consent(line)
                    if consent == 1:
                        rand = random.randint(1,3)
                        if rand == 1:
                            response = "I'm ready to give you some movie recommendations now! Try watching "
                        elif rand == 2:
                            response = "Piping hot movie recommendations, coming your way! Check out "
                        else:
                            response = "Movie recommendations for you, served with a smile (and a side pickle!). One movie I like is "
                            
                        self.recommendations = self.recommend(self.user_ratings, self.ratings, k=5, creative=True)
                        randNum = random.randint(0, 4)
                        response += " ".join(self.titles[randNum][0])
                        if rand == 1 or rand == 3:
                            response += "! Would you like another recommendation?"
                        else:
                            response += " :) Want another movie recommendation? I have tons of options - from ones loved by the spongiest of SpongeBobs to those hailed by the squiddiest of Squidwards!"
                    else:
                        self.recommendings = False
                        if rand == 1 or rand == 2:
                            response = "That's fine, if you're done chatting about films, how about buying yourself a Krabby Patty?"
                        else:
                            response = "Ok, got it."
            
            else:
                movie_indices = []
                for movie_title in movie_titles:
                    if len(self.find_movies_by_title(movie_title)) == 0:
                        return "I'm not sure I've heard of " + movie_title + " before. Tell me about another film!"
                    movie_indices += self.find_movies_by_title(movie_title)
                
                sentiment = self.extract_sentiment(line)
                for movie in movie_indices:
                    self.user_ratings[movie] = sentiment

                if sentiment == 1:
                    rand = random.randint(1, 3)
                    if rand == 1:
                        response += "I'm glad to hear that you liked "
                        choice = 0
                        if len(movie_titles) > 1:
                            choice = random.randint(0, len(movie_titles))
                        response += movie_titles[choice] 
                        response += "! That's one of my daughter's favorites, too. I love my girl, Pearl!"
                    elif rand == 2:
                        response += " Interesting choice! I think I saw Plankton watching "
                        choice = 0
                        if len(movie_titles) > 1:
                            choice = random.randint(0, len(movie_titles))
                        response += movie_titles[choice] 
                        response += " on Karen the other day, but to each their own, I guess."
                    else:
                        word = movie_titles[0][0]
                        response += " "
                        response += word
                        response += "! That's one of my favorite things. I think I should check this movie out, too. Ar ar ar ar."
                    #return response
                elif sentiment == -1:
                    rand = random.randint(1, 3)
                    if rand == 1:
                        response += "Pee-yew. I can't stand "
                        choice = 0
                        if len(movie_titles) > 1:
                            choice = random.randint(0, len(movie_titles))
                        response += movie_titles[choice] 
                        response += " either. It makes me almost as nauseous as the food from the Chum Bucket does... but I digress."
                        #return response 
                    elif rand == 2:
                        response += "Not for you, huh? That's too bad. "
                        choice  = 0
                        if len(movie_titles) > 1:
                            choice = random.randint(0, len(movie_titles))
                        response += movie_titles[choice]
                        response += " was one of my wife's favorite movies. That was before the beaching..."
                        #return response 
                    else:
                        response += "I hate "
                        choice  = 0
                        if len(movie_titles) > 1:
                            choice = random.randint(0, len(movie_titles))
                        response += movie_titles[choice]
                        response += " too! Wow, we have so much in common. You should come work at my restaurant, none of my workers relate to me."
                        #return response 
                else:
                    response += "Sorry, I'm not sure what your thoughts are on "
                    response += movie_titles[0]
                    response += ". Can you elaborate more?"

                rand2 = random.randint(1, 3)
                if rand2 == 1:
                    response += "Tell me more about the movies that you like and don't like."
                    return response
                elif rand2 == 2:
                    response += "Give me some more to work with! Some ketchup for that burger, some mayo for those fries. Give me an opinion about a movie that you've seen."
                    return response 
                else: 
                    response += "Hit me again - give me one of those juicy, delectable, mouth-watering movie reviews."
                    return response

                return "Okay, sorry! If you're not here for recommendations, then buy a Krabby Patty or get out of my Krusty Krab!"

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

        quote = '"'
        indices = []
        txt = str(preprocessed_input)
        for idx, char in enumerate(txt):
            if char == quote:
                indices.append(idx)
        quotes = []
        for j in range(0, len(indices), 2):
            quotes.append(txt[indices[j] + 1 : indices[j + 1]])
        return quotes
        
        # else:
        #     moreArticles = ['a', 'an', 'the', 'uma', 'um', 'o', 'ein', 'eine', 'un', 'una', 'la', 'el', 'las', 'los', 'le', 'les', 'une', 'il']
            
        #     line = preprocessed_input
        #     if not line[-1].isalnum:
        #         line = line.replace(line[-1], '')
        #     line = line.replace('"', '')
        #     lineList = line.split()
            
        #     possibleTitles = []
        #     for w in range(len(lineList)):
        #         for possibleLens in range(w + 1, len(lineList) + 1):
        #             possibleStr = ''
        #             for i in range(possibleLens - w):
        #                 if i < (possibleLens - w - 1):
        #                     possibleStr += (lineList[w + i] + ' ')
        #                 else:
        #                     possibleStr += lineList[w + i]
        #             possibleTitles.append(possibleStr.lower())
        #     possibleTitles = sorted(possibleTitles, key=len, reverse=True)

        #     updatedTitles = []

        #     for t in possibleTitles:
        #         newTitle = t
        #         titleList = t.split()
        #         if titleList[0] in moreArticles:
        #             if titleList[-1][1:4].isnumeric() and ')' == titleList[-1][5]:
        #                 dateIdx = t.find(titleList[-1])
        #                 newTitle = t[len(titleList[0]) + 1: dateIdx - 1] + ', ' + titleList[0] + t[dateIdx - 1:]
        #             else:
        #                 newTitle = t[len(titleList[0]) + 1:] + ', ' + titleList[0]
        #         updatedTitles.append(newTitle)

        #     extractedTitle = []

        #     for elem in self.titles:
        #         movieTitle = elem[0].lower()
        #         for possibility in updatedTitles:
        #             if possibility == movieTitle or possibility == movieTitle[:len(movieTitle) - 7]:
        #                 extractedTitle.append(possibility)
        #                 break

        #     print(extractedTitle)
        #     return extractedTitle

        # return []

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
        #check if title starts w/ (a, an, the) - if yes, search with it moved to end
        articles = ['a', 'an', 'the']
        moreArticles = ['a', 'an', 'the', 'uma', 'um', 'o', 'ein', 'eine', 'un', 'una', 'la', 'el', 'las', 'los', 'le', 'les', 'une', 'il']
        titleParts = title.split()
        matches = []
        
        
        if titleParts[0].lower() in articles:
            if titleParts[-1][1:4].isnumeric() and ')' == titleParts[-1][5]:
                dateIdx = title.find(titleParts[-1])
                title = title[len(titleParts[0]) + 1: dateIdx - 1] + ', ' + titleParts[0] + title[dateIdx - 1:]
            else:
                title = title[len(titleParts[0]) + 1:] + ', ' + titleParts[0]

            #search through self.titles for the index of the movie (position in list)
        for idx in range(len(self.titles)):
            name = self.titles[idx][0].lower()
            nameParts = name.split()
            if title.lower() == name or title.lower() == name[:name.find(nameParts[-1]) - 1]:
                 matches.append(idx)
        
        if self.creative:
            title = title.lower()
            newTitle = title
            for article in moreArticles:
                numBefore = newTitle.find(article) - 1
                numAfter = numBefore + len(article) + 1
                if (numBefore == -1 or (numBefore > -1 and not newTitle[numBefore].isalnum())) and (numAfter < len(newTitle) and not newTitle[numAfter].isalnum()):
                    newTitle = newTitle.replace(' ' + article, '')
                    newTitle = newTitle.replace(article + ' ', '')

            title = newTitle

            for m in range(len(self.titles)):
                movieName = self.titles[m]
                movieName = movieName[0].lower()
                elemBefore = movieName.find(title) - 1
                elemAfter = movieName.find(title) + len(title)
                if (title in movieName and (elemBefore == -1 or (elemBefore > -1 and not movieName[elemBefore].isalnum())) and (elemAfter < len(movieName) and not movieName[elemAfter].isalnum())):
                    if m not in matches:
                        matches.append(m)

        return matches

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
        negations = ['no', 'not', 'none', 'nobody', 'nothing', 'neither', 'nowhere', 
        'never', 'hardly', "doesn't", "isn't", "wasn't", "shouldn't", "wouldn't", 
        "couldn't", "won't", "can't", "don't", "didn't"]

        stemEdgeCases = {'enjoi':'enjoy', }

        rating = 0
        titles = self.extract_titles(preprocessed_input)
        userText = preprocessed_input
        for title in titles:
            userText = userText.replace('"' + title + '"', '')
        text = userText.split()
        stemmer = ps.PorterStemmer()

        negatives = False
        for word in text:
            if word in negations:
                negatives = True

        for word in text:
            stemWord = stemmer.stem(word)
            if stemWord in stemEdgeCases:
                word = stemEdgeCases[stemWord]
            if stemWord in self.sentiment and word not in self.sentiment:
                word = stemWord
            if word in self.sentiment:
                if self.sentiment[word] == 'neg':
                    if negatives:
                        rating += 1
                    else:
                        rating -= 1
                else:
                    if negatives:
                        rating -= 1
                    else:
                        rating += 1

        if rating > 0:
            return 1
        elif rating < 0:
            return -1
        return rating

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
        conjunctions = ['and', 'or', 'nor', 'but']
        sentimentsList = []
        titlesList = []
        words = preprocessed_input.split()
        for i in range(len(words)):
            title = self.extract_titles(preprocessed_input)
            if title not in titlesList:
                titlesList.append(title)

        splitWord = None

        for word in words:
            if word in conjunctions:
                splitWord = word

        initialSentiment = 0
        for title in titlesList[0]:
            if preprocessed_input.find(title) < preprocessed_input.find(splitWord):
                initialSentiment = self.extract_sentiment(preprocessed_input[:preprocessed_input.find(splitWord)])
                sentimentsList.append((title, initialSentiment))
            else:
                if splitWord == 'but':
                    sentimentsList.append((title, initialSentiment * -1))
                else:
                    sentimentsList.append((title, initialSentiment))

        return sentimentsList

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

        def get_edit_distance(potential, current):
            rows = len(current)
            columns = len(potential)
            dist = [[0 for p in range(columns + 1)] for k in range(rows + 1)]

            dist[0][0] = 0
            i = 1 
            while i < rows + 1:
                dist[i][0] = i
                i += 1
            j = 1
            while j < columns + 1:
                dist[0][j] = j 
                j += 1

            for r in range(1, rows + 1):
                for c in range(1, columns + 1):
                    addend = 2
                    if current[r - 1] == potential[c - 1]:
                        addend = 0
                    prev_below = dist[r - 1][c]
                    prev_left = dist[r][c - 1]
                    prev_diag = dist[r - 1][c - 1]
                   
                    dist[r][c] = min(prev_below + 1, prev_left + 1, prev_diag + addend)

            return dist[rows][columns] 

        sug = []
        prev_max = max_distance
        new_max = max_distance

        if " (" in title: 
            res = title.index(" (")
            title = title[: res]

        for i in range(len(self.titles)):
            pot_name = self.titles[i][0]
            if " (" in pot_name: 
                res_p = pot_name.index(" (")
                pot_name = pot_name[: res_p]

            if pot_name != '' and pot_name != ' ':
                d = get_edit_distance(pot_name.lower(), title.lower())
                if d <= new_max:
                    prev_max = new_max
                    new_max = d
                    if new_max < prev_max:
                        sug = []
                    sug.append(i)

        return sug


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
        movieIndices = []
        recents = {}
        numbers = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth']
        identifiers = ['a', 'the', 'an', 'movie', 'film', 'one']

        newClarification = clarification
        for identifier in identifiers:
            newClarification = newClarification.replace(' ' + identifier, '')
            newClarification = newClarification.replace(identifier + ' ', '')

        clarification = newClarification

        for c in range(len(candidates)):
            movie = self.titles[candidates[c]]
            elemBefore = movie[0].find(clarification) - 1
            elemAfter = movie[0].find(clarification) + len(clarification)
            if (clarification in movie[0] and (not movie[0][elemBefore].isalnum()) and (not movie[0][elemAfter].isalnum()) and elemBefore > -1):
                movieIndices.append(candidates[c])

            if 'recent' in clarification:
                movieDate = movie[0][-5:4]
                recents[candidates[c]] = movieDate
            
            if numbers[c] in clarification:
                movieIndices.append(candidates[c])

        if len(movieIndices) == 0 and clarification.isnumeric() and int(clarification) < len(candidates):
            movieIndices.append(candidates[int(clarification) - 1])
        
        if 'recent' in clarification:
            movieIndices.append(max(recents, key=recents.get))

        return movieIndices

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
        
        binarized_ratings = np.where(ratings > threshold, 1, ratings)
        binarized_ratings = np.where(ratings <= threshold, -1, binarized_ratings)
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
        similarity = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v) + 1e-16)
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
        recommendations = []

        def calcCos(ratings_matrix2, ratings_matrix1):
            return self.similarity(ratings_matrix2, ratings_matrix1)

        def calcTotal(ratings_matrix1, ratings_matrix2, user_ratings):
            # for every movie (row) in the matrix, find cosine similarity
            cosines = np.apply_along_axis(calcCos, 1, ratings_matrix2, ratings_matrix1)
            return np.sum(np.multiply(cosines, user_ratings))

        # might need to remove user ratings from ratings matrix using np.delete
        watched = np.nonzero(user_ratings)
        rated = np.take(user_ratings, watched[0])
        ratings = np.take(ratings_matrix, watched[0], 0)
        
        predRates = np.apply_along_axis(calcTotal, 1, ratings_matrix, ratings, rated)
        
        excludeArr = watched[0]
        reverse = np.argsort(predRates)
        sortedIdx = np.flip(reverse)
        filteredRates = np.setdiff1d(sortedIdx, excludeArr, True)
        
        recommendations = filteredRates[0:k]


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
        Looking for some new movies to watch? With just a quick conversation with 
        Mr. Krabs, a movie recommender chatbot, you can learn about several films 
        new and old to add to your watchlist.

        For the best user experience, please use short, specific sentences, and be 
        patient if he asks you to clarify anything! For example the entry "I really
        enjoyed watching "The Nightmare Before Christmas" movie." is formatted well.
        Additionally, please only input one movie at a time and put the movie's name 
        in quotation marks. 
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
