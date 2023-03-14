# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re, random
import nltk
from nltk.stem import PorterStemmer
import string

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'The Movie Man'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.ratings = ratings #shape (9125, 671)
        # print(np.shape(self.ratings))
        ########################################################################
        self.binarized_matrix = self.binarize(ratings, 2.5)
        self.ratings = self.binarize(ratings,2.5)
        self.movie_count = 0
        self.movies_maybe = []
        self.movieShelf = []
        self.user_ratings = []
        self.movieindexholder = [] #for process to trigger disambiguate

        self.other_opinions = [
        "Do you have any other movie opinions to share?",
        "Would you like to tell me about any other movies you love?",
        "What other movies do you have strong opinions about?",
        "I'm interested in hearing more of your movie opinions. What else comes to mind?",
        "Any other movies you feel passionate about?",
        "Do you have any other movies you want to rave or rant about?",
        "Are there any other movies you want to tell me your thoughts on?",
        "What other movies have you seen that you want to talk about?",
        "Are there any other movies that have stuck with you?",
        "Do you have any other movie recommendations or warnings?"]

        self.reorderTerms = ["The","An","A","Il","La","El","Les","Los","Las","L\'","Le","Der","Das"]
        self.index4pro = 0

        ########################################################################

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

        # greeting_message = "How can I help you?"
        greeting_message = "Tell me about a movie that you have seen."
        if self.creative:
            greeting_message = "Pray, good friend, couldst thou regale me with a tale of a moving picture that hath graced thine eyes? I would fain hear of a movie that thou hast seen, if it doth please thee to share."
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
            goodbye_message = "Mayhap thou hast a day most fair and pleasant!"
        else:
            goodbye_message = "Have a nice day!"

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return goodbye_message

    ############################################################################
    # 1.5. Helper Functions for Process                                        #
    ############################################################################

    def standardResponseGenerator(self, title, sentiment):
        title = self.order_check(title)

        if self.creative:
            PositiveKnownMovieResponses = [
                "I perceive, thou dost enjoy \"{movieTitle}\".",
                "Ah, so \"{movieTitle}\" is to thy liking.",
                "Got it, \"{movieTitle}\" is thy favourite.",
                "Verily, \"{movieTitle}\" is among thy preferred motion pictures.",
                "I doth see, thou hast a fondness for \"{movieTitle}\".",
                "Alright, \"{movieTitle}\" is among thy topmost motion pictures.",
                "So, \"{movieTitle}\" is among thy favourites, I apprehend.",
                "I hearken unto thee, \"{movieTitle}\" is one of thy beloved motion pictures.",
                "Ah, thou art a fan of \"{movieTitle}\".",
                "Understood, \"{movieTitle}\" is one of thy go-to motion pictures."]
            NegativeKnownMovieResponses = [
                "Verily, thou art not a fan of \"{movieTitle}\".",
                "Understood, \"{movieTitle}\" is not to thy liking.",
                "Got it, thou dost not particularly enjoy \"{movieTitle}\".",
                "Alright, \"{movieTitle}\" is not among thy favourites.",
                "I see, \"{movieTitle}\" doth not truly appease thee.",
                "Fair enough, thou art not a great fan of \"{movieTitle}\".",
                "Ah, so \"{movieTitle}\" did not quite hit the mark for thee.",
                "Okay, duly noted that \"{movieTitle}\" did not impress thee.",
                "Thanks for sharing thy thoughts on \"{movieTitle}\", even though thou dost not like it!",
                "Noted, \"{movieTitle}\" is not thy favourite motion picture."]
            UnknownKnownMovieResponses = [
                "I prithee pardon me, but I am not entirely certain whether thou liked or disliked \"{movieTitle}\". Couldst thou please share thy opinion again?",
                "I am not entirely sure whether thou didst enjoy or dislike \"{movieTitle}\", I am afraid. Couldst thou please elaborate?",
                "I beg thy pardon, but I am unsure whether thou hast a positive or negative opinion about \"{movieTitle}\". Couldst thou please try again?",
                "My apologies, but I am not entirely certain whether thou hast a favorable or unfavorable opinion about \"{movieTitle}\". Couldst thou please share thy opinion again?",
                "I prithee pardon me, but I am not sure whether thou liked or didst not like \"{movieTitle}\". Couldst thou please elaborate?",
                "I beg thy pardon, but I am unsure whether thou hast a positive or negative view of \"{movieTitle}\". Couldst thou please try again?",
                "I prithee pardon me, but I am not quite sure if thou enjoyed or disliked \"{movieTitle}\". Couldst thou please share thy opinion again?",
                "I am not entirely certain whether thou hast a positive or negative perspective on \"{movieTitle}\", I am afraid. Couldst thou please elaborate?",
                "My apologies, but I am unsure whether thou hast a favorable or unfavorable perspective on \"{movieTitle}\". Couldst thou please try again?",
                "I prithee pardon me, but I am not entirely certain whether thou liked or didst not like \"{movieTitle}\". Couldst thou please share thy opinion again?"]
            UnknownMovieResponses = [
                "Verily, I prithee pardon, but I am not acquainted with \"{movieTitle}\". Couldst thou checketh the spelling for any typos, or suggesteth a different film?",
                "Prithee pardon, but I am not familiar with \"{movieTitle}\". Please double-checketh the spelling or tryeth another movie.",
                "Verily, I am not acquainted with \"{movieTitle}\". Perhaps thou couldst verify the spelling or suggesteth another movie?",
                "Verily, I am sorry, but I doth not recognize \"{movieTitle}\". Couldst thou please checketh the spelling or suggesteth an alternative?",
                "Prithee pardon, but I am not familiar with \"{movieTitle}\". Please ensure the spelling is correct or recommendeth a different movie.",
                "Verily, I am sorry, but I doth not knoweth \"{movieTitle}\". Canst thou double-checketh the spelling or suggesteth another film?",
                "Prithee pardon, but I am not familiar with \"{movieTitle}\". Wouldst thou mind checking the spelling or proposing a different movie?",
                "Verily, I am not acquainted with \"{movieTitle}\". Please make sure the spelling is accurate or recommendeth a different movie.",
                "Verily, I am sorry, but I doth not recognize \"{movieTitle}\". Couldst thou please checketh the spelling or suggesteth an alternative film?",
                "Prithee pardon, but I am not familiar with \"{movieTitle}\". Perhaps thou couldst verify the spelling or recommendeth another movie?"]
        else:
            PositiveKnownMovieResponses = [
            "I understand, you like \"{movieTitle}\".",
            "Ah, so \"{movieTitle}\" is your cup of tea.",
            "Got it, \"{movieTitle}\" is your favorite.",
            "Okay, so \"{movieTitle}\" is one of your preferred movies.",
            "I see, you have an appreciation for \"{movieTitle}\".",
            "Alright, \"{movieTitle}\" is one of your top movies.",
            "So \"{movieTitle}\" is one of your favorites, I got it.",
            "I hear you, \"{movieTitle}\" is one of your beloved movies.",
            "Ah, you're a fan of \"{movieTitle}\".",
            "Understood, \"{movieTitle}\" is one of your go-to movies."]

            NegativeKnownMovieResponses = [
            "Okay, so you're not a fan of \"{movieTitle}\".",
            "Understood, \"{movieTitle}\" is not your cup of tea.",
            "Got it, you don't particularly enjoy \"{movieTitle}\".",
            "Alright, \"{movieTitle}\" is not one of your favorites.",
            "I see, \"{movieTitle}\" isn't really your thing.",
            "Fair enough, you're not a big fan of \"{movieTitle}\".",
            "Ah, so \"{movieTitle}\" didn't quite hit the mark for you.",
            "Okay, duly noted that \"{movieTitle}\" didn't impress you.",
            "Thanks for sharing your thoughts on \"{movieTitle}\", even though you don't like it!",
            "Noted, \"{movieTitle}\" isn't your favorite film."]

            UnknownKnownMovieResponses = [
            "I'm sorry, but I'm not entirely certain whether you liked or disliked \"{movieTitle}\". Could you please share your opinion again?",
            "I'm not entirely sure whether you enjoyed or disliked \"{movieTitle}\", I'm afraid. Could you please elaborate?",
            "I apologize, but I'm unsure whether you have a positive or negative opinion about \"{movieTitle}\". Could you please try again?",
            "My apologies, but I'm not entirely certain whether you have a favorable or unfavorable opinion about \"{movieTitle}\". Could you please share your opinion again?",
            "I'm sorry, but I'm not sure whether you liked or didn't like \"{movieTitle}\". Could you please elaborate?",
            "I apologize, but I'm unsure whether you have a positive or negative view of \"{movieTitle}\". Could you please try again?",
            "I'm sorry, but I'm not quite sure if you enjoyed or disliked \"{movieTitle}\". Could you please share your opinion again?",
            "I'm not entirely certain whether you have a positive or negative perspective on \"{movieTitle}\", I'm afraid. Could you please elaborate?",
            "My apologies, but I'm unsure whether you have a favorable or unfavorable perspective on \"{movieTitle}\". Could you please try again?",
            "I'm sorry, but I'm not entirely sure whether you liked or didn't like \"{movieTitle}\". Could you please share your opinion again?"]

            UnknownMovieResponses = [
            "I'm sorry, I'm not familiar with \"{movieTitle}\". Could you check the spelling for typos, or suggest a different film?",
            "I'm sorry, but I'm not familiar with \"{movieTitle}\". Please double-check the spelling or try another movie.",
            "I'm sorry, I'm not familiar with \"{movieTitle}\". Perhaps you could verify the spelling or suggest another movie?",
            "I'm sorry, but I don't recognize \"{movieTitle}\". Could you please check the spelling or suggest an alternative?",
            "I'm sorry, I'm not familiar with \"{movieTitle}\". Please ensure the spelling is correct or recommend a different movie.",
            "I'm sorry, but I don't know \"{movieTitle}\". Can you double-check the spelling or suggest another film?",
            "I'm sorry, I'm not familiar with \"{movieTitle}\". Would you mind checking the spelling or proposing a different movie?",
            "I'm sorry, I'm not familiar with \"{movieTitle}\". Please make sure the spelling is accurate or recommend a different movie.",
            "I'm sorry, but I don't recognize \"{movieTitle}\". Could you please check the spelling or suggest an alternative film?",
            "I'm sorry, I'm not familiar with \"{movieTitle}\". Perhaps you could verify the spelling or recommend another movie?"]


        if sentiment == "NA":
            response = str(random.choice(UnknownMovieResponses).format(movieTitle = title))
        elif sentiment >= 1:
            positiveBase = random.choice(PositiveKnownMovieResponses).format(movieTitle = title)
            positivePrompt = random.choice(self.other_opinions)
            self.movie_count += 1
            movie_tuple = (title, 1)
            self.movies_maybe.append(movie_tuple)
            self.movieShelf.append(title)
            response = str(positiveBase + " " + positivePrompt)
        elif sentiment <= -1:
            negativeBase = random.choice(NegativeKnownMovieResponses).format(movieTitle = title)
            negativePrompt = random.choice(self.other_opinions)
            self.movie_count += 1
            movie_tuple = (title, -1)
            self.movies_maybe.append(movie_tuple)
            self.movieShelf.append(title)
            response = str(negativeBase + " " + negativePrompt)
        elif sentiment == 0:
            response = random.choice(UnknownKnownMovieResponses).format(movieTitle = title)
        return response

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
            # print(self.debug(line))
            if line == "no":
                response = "Okay, type ':quit' to exit."
            elif self.movie_count < 4:
                titles = self.extract_titles(line)
                if len(titles) > 1:
                    response = "I'm sorry, I'm only able to handle one movie at a time. Could you please give me your opinions one at a time?"
                if len(titles) == 0: #if no title or clarifying statement basically
                    if self.movieindexholder != []: #trigger disambiguate
                        idk_bruh = self.movieindexholder
                        self.movieindexholder = [] #reset her
                        # print(self.disambiguate(line, idk_bruh))
                        movieTitle = self.titles[self.disambiguate(line, idk_bruh)[0]][0]
                        movieTitle = "\""+movieTitle+"\""
                        response = "Hark! I hath found {}! Pray thee, canst thou give me another motion picture thou hath beheld?".format(movieTitle)
                        self.movie_count += 1
                    else:
                        catchAlls = responses = [
                            "Fair friend, I know not how your words doth pertain to movie recommendations. Pray thee, canst thou tell me of thy film preferences?",
                            "Pray, speak of thy favorite and disliked films, if it please thee.",
                            "Verily, thy words do confound me. Canst thou speaketh of the movies thou dost enjoy or abhor, so that I may better serve thee?",
                            "Prithee, I am but a humble movie recommendation bot. Thy musings provided doth not assist me in my duties. Wilt thou speak of films instead?",
                            "Nay, good friend, thine input doth leave me befuddled. Speaketh thou of movies, and I shall endeavor to aid thee.",
                            "I prithee, good friend, speak of movies, for thy words do not assist me in mine task of recommending them.",
                            "I am perplexed by thy words, fair friend. Canst thou instead tell me of thy film preferences, that I may better serve thee?",
                            "Pray thee, good user, speak of movies. For thy input doth not aid me in my task of recommendation.",
                            "Thy words are curious, dear user. Canst thou tell me of the films thou dost enjoy or disdain, that I may offer thee wise counsel?",
                            "Good friend, thy words do not aid me in the task of recommendation. I implore thee, speak of movies, that I may better serve thee."]
                        response = random.choice(catchAlls)
                elif len(titles) == 1: #1 or more titles
                    title = titles[0]
                    movieIndex = self.find_movies_by_title(title)
                    if movieIndex != []: #if movies indicies arent empty
                        if len(movieIndex) > 1:
                            for idxy in movieIndex:  # loop through movie titles
                                self.movieindexholder.append(idxy) #append them to this list
                            response = "Do not forsake me, but to which motion picture do you refer: {} ?".format(" or ".join(self.titles[elem][0] for elem in self.movieindexholder))
                        else:
                            if title in self.movieShelf:
                                response = "Sorry, you've already expressed an opinion about \"{}\". Could thou provide me a new motion picture opinion?".format(title)
                            else:
                                sentiment = self.extract_sentiment(line)
                                # print(title,sentiment)
                                response = self.standardResponseGenerator(title, sentiment)
                                # print(self.movieShelf)
                    else:
                        response = self.standardResponseGenerator(title, "NA")
            else:
                self.user_ratings = self.builduser(self.movies_maybe)
                recs = self.recommend(self.user_ratings, self.binarized_matrix, k=10, creative=False)
                response = ""
                if self.index4pro == 0:
                    response = "Huzzah, that is sufficient for me to proffer a recommendation! "
                if self.index4pro < len(recs):
                    tittler = self.titles[recs[self.index4pro]][0]
                    movieTitle = self.order_check(tittler)
                    movieTitle = "\""+movieTitle+"\""
                    self.index4pro += 1
                    suggestionDialogues = [ "I doth propose thou shouldst partake in the viewing of {Movie}. Wouldest thou desireth another suggestion? (Enter :quit if thou art finished.)",
                    "I wouldst recommend thee to take pleasure in the spectacle of {Movie}. Wouldst thou care for another counsel? (Enter :quit if thou art content.)", "Methinks thou shouldst watch {Movie}, good friend. Might I offer another counsel? (Enter :quit if thou art done.)", "It is my counsel that thou shouldst indulge in the spectacle of {Movie}. Art thou inclined to hear another recommendation? (Enter :quit if thou art done.)", "Verily, I recommend thee to partake in the viewing of {Movie}. Wouldst thou desire another counsel, good friend? (Enter :quit if thou art finished.)"]
                    response += random.choice(suggestionDialogues).format(Movie=movieTitle)
                else:
                    response = "These are all the recommendations I have! Goodbye!"
        else: #if starter
            # print(self.debug(line))
            if line == "no":
                response = "Okay, type ':quit' to exit."
            elif self.movie_count < 4:
                titles = self.extract_titles(line)
                if len(titles) > 1:
                    response = "I'm sorry, I'm only able to handle one movie at a time. Could you please give me your opinions one at a time?"
                elif len(titles) == 0:
                    response = "Hmm, I didn't detect any movie titles in your sentence. Could you please try again? Make sure your movies appear with proper capitalization and quotation marks, like: \"Shrek 2 (2004)\" or \"Shrek 2\"."
                elif len(titles) == 1:
                    title = titles[0]
                    movieIndex = self.find_movies_by_title(title)
                    if movieIndex != []: #if movies indicies arent empty
                        if len(movieIndex) > 1:
                            response = "I'm sorry, can you be more specific about your request?"
                        else:
                            if title in self.movieShelf:
                                response = "Sorry, you've already expressed an opinion about \"{}\". Could you give me a new movie opinion?".format(title)
                            else:
                                sentiment = self.extract_sentiment(line)
                                response = self.standardResponseGenerator(title, sentiment)
                    else:
                        response = self.standardResponseGenerator(title, "NA")
            else:
                self.user_ratings = self.builduser(self.movies_maybe)
                recs = self.recommend(self.user_ratings, self.binarized_matrix, k=10, creative=False)
                response = ""
                if self.index4pro == 0:
                    response = "Hooray, that is enough for me to make a recommendation! "
                if self.index4pro < len(recs):
                    tittler = self.titles[recs[self.index4pro]][0]
                    movieTitle = self.order_check(tittler)
                    movieTitle = "\""+movieTitle+"\""
                    self.index4pro += 1
                    response = "I suggest you watch {}. Would you like to hear another recommendation? (Enter :quit if you're done.)".format(tittler)
                else:
                    response = "These are all the recommendations I have! Goodbye!"
        return response
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################

    def builduser(self, movies_maybe):
        "build user matrix for use"
        """:param user_ratings: a binarized 1D numpy array of the user's movie
                    ratings
                :param ratings_matrix: a binarized 2D numpy matrix of all ratings, where
                  `ratings_matrix[i, j]` is the rating for movie i by user j
                  ratings_matrix[r, c]` is the rating for movie r by user c"""
        shape_2_rob = self.binarized_matrix[:, 0]
        self.user_ratings = np.zeros_like((shape_2_rob))
        for tuple_movie in movies_maybe:
            indicy = self.find_movies_by_title(tuple_movie[0])
            self.user_ratings[indicy] = tuple_movie[1]
        return self.user_ratings

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
        return text

    def order_check(self, title):
        """Make sure that the order of the title is correct for indexing if the title starts with an article that is moved to the end of the movie title, such as \"the Terminator\""""
        title = title
        titleYear = re.findall(r"\([0-9]{4}\)",title)
        title = re.sub(r" \([0-9]{4}\)",r"",title)
        dieCheck = re.findall(r",\sDie",title)
        title = title.split(" ")
        if title[-1] in self.reorderTerms or dieCheck != []: #check if last word is article
            titleWords = []
            title[-2] = title[-2].strip(',')
            endWord = title.pop(-1) #remove end word which is article
            titleWords.append(endWord) #add it first
            for word in title:
                titleWords.append(word)
            title = titleWords
        if titleYear != []:
            title.append(titleYear[0])
        title = " ".join(title)
        return title


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
        pattern = "(?:\")([^\"]+)(?:\")"
        movie_titles = []
        if re.search(pattern, preprocessed_input):
            titles_found = re.findall(pattern, preprocessed_input)
            for title in titles_found:
                movie_titles.append(title)
        return movie_titles

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
        indicies = []
        split_input = title.split(" ")
        for idx, titles in enumerate(self.titles): # loop through dict titles
            for titley in titles: #loop through possible titles
                strippedTitle = titley
                strippedTitle = re.sub(r" \([0-9]{4}\)",r"",strippedTitle) #remove date from possible titlce
                idk_split = titley.split(" ")
                if self.creative:
                    reorder_strippedtitle = self.order_check(strippedTitle)
                    no_date_input = re.sub(r" \([0-9]{4}\)",r"",title)
                    if title == reorder_strippedtitle:
                        indicies.append(idx)
                    elif no_date_input == reorder_strippedtitle and split_input[-1] == idk_split[-1]:
                        indicies.append(idx)
                    elif re.match(r"\b" + re.escape(title) + r"\b", titley):
                        indicies.append(idx)
                    elif strippedTitle.lower() == title.lower():
                        indicies.append(idx)
                    else:
                        alternateTitles = re.findall(r"\([^\"\(]+\)",strippedTitle)
                        alternateTitlesProcessed = []
                        for item in alternateTitles:
                            item = re.sub(r"a\.k\.a\. ",r"",item)
                            item = re.sub(r"[\(\)]",r"",item)
                            alternateTitlesProcessed.append(item)
                            foreignTitle = self.order_check(item)
                            alternateTitlesProcessed.append(foreignTitle)
                        if title == titley or title == strippedTitle or title in alternateTitlesProcessed: #check if input is same as original or original without date
                            indicies.append(idx)
                else:
                    if title == titley or title == strippedTitle: #check if input is same as original or original without date
                        indicies.append(idx)
                    else:
                        reorder_strippedtitle = self.order_check(strippedTitle)
                        if title == reorder_strippedtitle:
                            indicies.append(idx)
                        else:
                            no_date_input = re.sub(r" \([0-9]{4}\)",r"",title)
                            if no_date_input == reorder_strippedtitle and split_input[-1] == idk_split[-1]:
                                indicies.append(idx)
        return indicies

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
        ps = PorterStemmer()
        pos_count = 0
        neg_count = 0
        sentimenty = {}
        digit = 1
        if self.extract_titles(preprocessed_input) != []:
            titler = self.extract_titles(preprocessed_input)
            input = preprocessed_input.replace(titler[0], " ")
        else:
            input = preprocessed_input
        input = input.translate(input.maketrans('', '', string.punctuation))
        neg_words = ["not", "didn't", "didnt", "never"]
        strong_words = ["really", "hate", "loved", "awful","much", "horrible", "terrible",
        "digusting","love","super","very","much","a lot","hated"]
        for word in self.sentiment:
            stem_keys = ps.stem(word)
            sentimenty[stem_keys] = self.sentiment[word]
        input = input.split(" ")
        for i in range(len(input)):
            word_input = input[i]
            if word_input in neg_words:
                if self.creative:
                    if i != len(input) - 1: #if not the last word
                        next_word = input[input.index(word_input) + 1]
                        if next_word in strong_words:
                            return 0
                        else:
                            return -1
                else:
                    return -1
            if word_input in strong_words:
                if self.creative:
                    digit = 2

            word_stem = ps.stem(word_input)
            if word_stem in sentimenty:
                value = sentimenty[word_stem] # word is the key and the sentiment the value, loop through keys
                # print(word_stem, sentimenty[word_stem])
                if value == "pos":
                    pos_count += 1
                else:
                    neg_count += 1
        else:
            if pos_count < neg_count:
                return -1 * digit
            elif pos_count > neg_count:
                return 1 * digit
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
        listy = []
        both_cunj = ["and", "or"]
        one_conj = ["but"]
        input = preprocessed_input
        input = input.split(" ")
        possible_titles = self.extract_titles(preprocessed_input)
        if len(possible_titles) >= 1:
            for word in input:
                if word in one_conj or word in both_cunj:
                    input = " ".join(input)
                    if word in one_conj:
                        input = input.split(word)
                        for i in range(len(input)):
                            if i != 0:
                                senti = self.extract_sentiment(input[i-1])
                                listy.append(((self.extract_titles(input[i])[0]), senti * -1))
                            else:
                                senti = self.extract_sentiment(input[i])
                                listy.append(((self.extract_titles(input[i])[0]), senti))
                    if word in both_cunj:
                        input = input.split(word)
                        for i in range(len(input)):
                            if i != 0:
                                senti = self.extract_sentiment(input[i-1])
                                listy.append(((self.extract_titles(input[i])[0]), senti))
                            else:
                                senti = self.extract_sentiment(input[i])
                                listy.append(((self.extract_titles(input[i])[0]), senti))
        else:
            listy = self.extract_sentiment(preprocessed_input)
        return listy

    def levenshtein_distance(self, title, possible_title):
        matty = np.zeros((len(title) + 1, len(possible_title) + 1)) # a 2-D matrix of size words
        for cell in range(len(title) + 1): #initialize the first row
            matty[cell][0] = cell
        for cell2 in range(len(possible_title) + 1): #initialize first column
            matty[0][cell2] = cell2
        for cell in range(1, len(title) + 1): # iterate through each cell in the matrix (excluding the first row/column)
            for cell2 in range(1, len(possible_title) + 1):
                 if (title[cell-1] == possible_title[cell2-1]): #f the end characters of the words are equal
                     matty[cell][cell2] = matty[cell - 1][cell2 - 1] #then the distance is equal to the value in the top-left corner
                 else:
                    a = matty[cell][cell2 - 1] #, a is the value of the cell to the left of the current cell
                    b = matty[cell - 1][cell2] #, is the value of the cell above the current cell
                    c = matty[cell - 1][cell2 - 1]  #  is the value of the cell diagonally above and to the left of the current cel

                    if a <= b and a <= c:
                        matty[cell][cell2] = a + 1 #insert
                    elif b <= a and b <= c:
                        matty[cell][cell2] = b + 1 #delete
                    else:
                        matty[cell][cell2] = c + 2 #sub

        return matty[len(title)][len(possible_title)]


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
        smallest_ED = max_distance
        please = []
        placehold = []
        for idx, titles in enumerate(self.titles):
            possible_title = titles[0]
            possible_title = re.sub(r" \([0-9]{4}\)",r"",possible_title) #remove date from possible titlc
            possible_title = possible_title.strip()
            ED = self.levenshtein_distance(title.lower(), possible_title.lower())
            if ED <= max_distance:
                if ED <= smallest_ED:
                    smallest_ED = ED
                    placehold.append((idx,ED))
        placehold.sort(reverse=True)
        for tuple in placehold:
            if tuple[1] <= smallest_ED:
                please.append(tuple[0])
        return please

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
        for possibility in candidates: #search through possibe indicies
            possible_title = self.titles[possibility]
            if clarification in possible_title[0]: #if year in title
                return self.find_movies_by_title(possible_title[0])

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
        for idx, rating in enumerate(ratings):
            condlist = [rating == 0, rating <= threshold, rating > threshold]
            choicelist = [rating, -1, 1]
            binarized_ratings[idx] = np.select(condlist, choicelist)
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
        norm_a = np.linalg.norm(u)
        norm_b = np.linalg.norm(v)
        if norm_a == 0 or norm_b == 0:
            return 0
        similarity = np.dot(u, v) / (norm_a * norm_b)
        return similarity
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
        preReqs = []
        ratedIndices = np.nonzero(user_ratings != 0)
        ratedIndices = ratedIndices[0]
        for idx, array in enumerate(ratings_matrix): #loop through row
            cosum = []
            for movieIndex in ratedIndices: #for movie index in array of user rated movie
                similarity = self.similarity(array,ratings_matrix[movieIndex]) # find similitary between all movie rankings and user movie rating
                useRating = user_ratings[movieIndex]
                subval = similarity * useRating #multiple similarity by user rating
                cosum.append(subval)
            predictedRating = np.sum(cosum)
            preReqs.append((predictedRating,idx))
        preReqs.sort(reverse=True)
        for item in preReqs:
            if item[1] not in ratedIndices:
                recommendations.append(item[1])
        return recommendations[:k]
        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################


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
        # print(self.extract_titles('Ive watched "The Titanic" and "The Notebook" a lot'))
        # print(self.extract_titles('I liked The NoTeBoOk!'))
        # print(self.find_movies_by_title("Scream"))
        # print(self.find_movies_by_title("10 things i HATE about you"))
        # print(self.extract_sentiment("I hated that movie"))
        # print(self.disambiguate("Sorcerer's Stone", [3812, 4325, 5399, 6294, 6735, 7274, 7670, 7842]))
        # print(self.extract_sentiment_for_movies('I liked "Titanic (1997)", but "Ex Machina" was not good.'))
        # print(self.extract_sentiment_for_movies('I didnt like "Titanic (1997)", or "Ex Machina".'))
        # print(self.extract_sentiment_for_movies('I liked "Titanic (1997)", and "Ex Machina".'))
        # print(self.extract_sentiment('I loved "Zootopia"'))
        # print(self.extract_sentiment('"Zootopia" was terrible.'))
        # print(self.extract_sentiment('I really reeally liked "Zootopia"!!!'))
        # print(self.extract_sentiment('I didnt hate "Zootopia"!!!'))
        # print(self.levenshtein_distance("Sleeping Beaty", "Sleeping Beauty"))
        # print(self.levenshtein_distance("Te", "Ted"))
        # print(self.levenshtein_distance("Te", "9"))
        # print(self.find_movies_closest_to_title("Sleeping Beaty", max_distance = 3))
        # print(self.find_movies_closest_to_title("Te", max_distance = 3))
        # print(self.find_movies_closest_to_title("BAT-MAAAN", max_distance = 3))
        # print(self.find_movies_closest_to_title("Blargdeblargh", max_distance = 4))
        pass

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

        if self.creative:
            return """Hear ye, hear ye, good friend! Welcome to our humble abode of cinematic recommendations! I am a chatbot, programmed to assist thee in discovering movies that shall tickle thy fancy. But to perform such a task, I must first get to know thee and thy tastes in movies.

            So I beseech thee, fair user, to provide me with five titles of films that thou hast seen and thy thoughts on them. Pray, ensure that the movies are written in the following format: "{MovieTitle}", where the title of the movie is in quotation marks and properly capitalized. Fear not, for I am well-versed in the language of the modern age and shall understand any such titles.

            Once thou hast given me thy list of movies, I shall use the magic of algorithms and data to suggest other movies that may pique thy interest. Thus, let us begin this journey of cinematic exploration and discover the movies that shall bring thee joy and entertainment!"""
        else:
            return """Hi! I'm MovieBot! I'm going to recommend a movie to you. First I will ask you about your taste in movies, and once you have provided five, I can recommend you some movies!."""


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')


# Notes

## Code makes use of levenshtein distance from https://blog.paperspace.com/implementing-levenshtein-distance-word-autocomplete-autocorrect/
