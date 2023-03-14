# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import numpy as np
import re
import random

import util
from porter_stemmer import PorterStemmer


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'Nikaphtina'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.article_list = ["An", "A", "The", "La", "Il", "L\'", "El", "Los", "Las", "Le", "Les", "Das", "Det"]

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings, 2.5)

        # ADDITIONAL OWN CODE
        self.user_ratings = np.zeros(len(self.titles))
        self.numMoviesGivenByUser = 0
        self.recs = []
        self.indexOfRecsBeingGiven = 0

        self.isClarifyingFromSpellCheck = False
        self.spellCheckMovieIndices = []
        self.currSpellCheckMovieIndex = None
        self.lineToUseForSentimentSpellCheck = None
        self.randIndexGivingRecs = 0

        self.isDisambiguating = False
        self.disambiguationMovieIndices = []
        self.lineToUseForDisambiguation = None

        self.randIndexArbitrary = 0
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
            greeting_message = "Hola! Soy Dora! Today our puzzle is to see what movies you'd like!"
        else:
            greeting_message = "Hi nice to talk to you!"

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
            goodbye_message = "Adios! Gracias for your help!"
        else:
            goodbye_message = "Bye bye!"

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
            response = "I processed {} in creative mode!!".format(line)
            randNum = random.random()  # random number between 0 and 1

            # take care of specific arbitrary input cases
            lowerLine = line.lower()
            if "can you" in lowerLine:
                indexOfCanYou = lowerLine.find("can you")
                actionBeingAskedToDo = line[indexOfCanYou + len("can you"):]
                actionBeingAskedToDoTokens = actionBeingAskedToDo.split(" ")
                for i in range(len(actionBeingAskedToDoTokens)):
                    if actionBeingAskedToDoTokens[i] == "you":
                        actionBeingAskedToDoTokens[i] = "me"
                    elif actionBeingAskedToDoTokens[i] == "me":
                        actionBeingAskedToDoTokens[i] = "you"
                    elif actionBeingAskedToDoTokens[i] == "my":
                        actionBeingAskedToDoTokens[i] = "your"
                    elif actionBeingAskedToDoTokens[i] == "your":
                        actionBeingAskedToDoTokens[i] = "my"
                actionBeingAskedToDo = " ".join(actionBeingAskedToDoTokens)
                actionBeingAskedToDo = re.sub(r'[^\w\s]', '', actionBeingAskedToDo)
                response = "Sorry, I just know about movies and adventures! I can't" + actionBeingAskedToDo + "."
                return response
            elif "what is" in lowerLine:
                indexOfWhatIs = lowerLine.find("what is")
                itemAfterWhatIs = line[indexOfWhatIs + len("what is"):]
                itemAfterWhatIsTokens = itemAfterWhatIs.split(" ")
                for i in range(len(itemAfterWhatIsTokens)):
                    if itemAfterWhatIsTokens[i] == "you":
                        itemAfterWhatIsTokens[i] = "me"
                    elif itemAfterWhatIsTokens[i] == "me":
                        itemAfterWhatIsTokens[i] = "you"
                    elif itemAfterWhatIsTokens[i] == "my":
                        itemAfterWhatIsTokens[i] = "your"
                    elif itemAfterWhatIsTokens[i] == "your":
                        itemAfterWhatIsTokens[i] = "my"
                itemAfterWhatIs = " ".join(itemAfterWhatIsTokens)
                itemAfterWhatIs = re.sub(r'[^\w\s]', '', itemAfterWhatIs)
                response = "Great question! Why don't you tell me what is" + itemAfterWhatIs + "? You can do it!"
                return response
            elif "what's" in lowerLine:
                indexOfWhatIs = lowerLine.find("what's")
                itemAfterWhatIs = line[indexOfWhatIs + len("what's"):]
                itemAfterWhatIsTokens = itemAfterWhatIs.split(" ")
                for i in range(len(itemAfterWhatIsTokens)):
                    if itemAfterWhatIsTokens[i] == "you":
                        itemAfterWhatIsTokens[i] = "me"
                    elif itemAfterWhatIsTokens[i] == "me":
                        itemAfterWhatIsTokens[i] = "you"
                    elif itemAfterWhatIsTokens[i] == "my":
                        itemAfterWhatIsTokens[i] = "your"
                    elif itemAfterWhatIsTokens[i] == "your":
                        itemAfterWhatIsTokens[i] = "my"
                itemAfterWhatIs = " ".join(itemAfterWhatIsTokens)
                itemAfterWhatIs = re.sub(r'[^\w\s]', '', itemAfterWhatIs)
                response = "Great question! Why don't you tell me what's" + itemAfterWhatIs + "? You can do it!"
                return response

            # see if we are in the process of recommending
            if self.numMoviesGivenByUser >= 5:  # we're in the recommending process
                if self.indexOfRecsBeingGiven >= len(self.recs):  # no more recs to give
                    if randNum < 0.5:
                        response = "That's all the information in my backpack. Feel free to start a new adventure!"
                    else:
                        response = "Even Swiper doesn't have more movie ideas. See you on the next adventure!"
                    return response
                else:  # more recs to give
                    # see if user even wants more recs
                    loweredLine = line.lower()
                    if "yes" in loweredLine or "yeah" in loweredLine or "sure" in loweredLine or "ok" in "loweredLine":
                        if randNum < 0.3:
                            response = "Boots suggests " + \
                                       self.titles[self.recs[self.indexOfRecsBeingGiven]][0] + \
                                       ". How about another one?"
                            self.indexOfRecsBeingGiven += 1
                        elif randNum < 0.6:
                            response = self.titles[self.recs[self.indexOfRecsBeingGiven]][0] + \
                                       " would be a good movie for you. Want more ideas?"
                            self.indexOfRecsBeingGiven += 1
                        else:
                            response = "Diego says to check out " + \
                                       self.titles[self.recs[self.indexOfRecsBeingGiven]][0] + \
                                       ". Do you want more recommendations?"
                            self.indexOfRecsBeingGiven += 1
                        return response
                    elif "no" in loweredLine or "not" in loweredLine or "nah" in loweredLine:
                        if randNum < 0.5:
                            response = "Oh no, you cut short our adventure!"
                        else:
                            response = "I guess you have a map of where to go next already! I won't help you more!"
                        return response
                    else:
                        if self.randIndexArbitrary == 0:
                            response = "Hm, that's not related to our expedition, let's go " \
                                       "back to recommendations! Vamos!"
                        elif self.randIndexArbitrary == 1:
                            response = "Ok, got it! Dora and Boots are excited to give you more " \
                                       "recommendations, do you want them?"
                        elif self.randIndexArbitrary == 2:
                            response = "I see! Let's stay on track for our adventure! Do you want more recommendations?"
                        elif self.randIndexArbitrary == 3:
                            response = "Thanks for telling me! Why don't we continue on our expedition about movies?"
                        else:
                            response = "Wow, you're a great writer! I want to keep talking about movies!"
                        self.randIndexArbitrary += 1
                        return response

            else:  # We are in the data-seeking process
                id = None
                title = None

                if self.isClarifyingFromSpellCheck:  # already has ids in mind
                    lowerLine = line.lower()
                    if "yes" in lowerLine or "yeah" in lowerLine:
                        id = self.currSpellCheckMovieIndex
                        title = self.titles[id][0]
                        self.isClarifyingFromSpellCheck = False
                        self.spellCheckMovieIndices = []
                        self.currSpellCheckMovieIndex = None
                        line = self.lineToUseForSentimentSpellCheck
                        self.lineToUseForSentimentSpellCheck = None
                    elif "no" in lowerLine or "nope" in lowerLine:
                        if len(self.spellCheckMovieIndices) == 0:  # no more movies from spellcheck list left to guess
                            response = "I'm giving up! Diego and I don't know which movie you wanted! " \
                                       "Please tell me again then."
                            self.isClarifyingFromSpellCheck = False
                            self.spellCheckMovieIndices = []
                            self.lineToUseForSentimentSpellCheck = None
                        else:
                            response = "Boots is wondering if you meant " + \
                                       self.titles[self.spellCheckMovieIndices[0]][0] \
                                       + "?"
                            self.currSpellCheckMovieIndex = self.spellCheckMovieIndices[0]
                            self.spellCheckMovieIndices.pop(0)
                            self.isClarifyingFromSpellCheck = True
                        return response
                    else:
                        response = "Yikes, you didn't tell me if my guess was correct! Please just try again " \
                                   "and tell me about a movie!"
                        self.isClarifyingFromSpellCheck = False
                        self.spellCheckMovieIndices = []
                        self.currSpellCheckMovieIndex = None
                        self.lineToUseForSentimentSpellCheck = None
                        return response

                elif self.isDisambiguating:
                    narrowedDownIndices = self.disambiguate(line, self.disambiguationMovieIndices)
                    if len(narrowedDownIndices) == 0:
                        response = "I'm giving up! Now there's no movies in my backpack that match what you said! Try " \
                                   "telling me about a movie again."
                        self.isDisambiguating = False
                        self.disambiguationMovieIndices = []
                        self.lineToUseForDisambiguation = None
                        return response
                    elif len(narrowedDownIndices) > 1:
                        response = "Ok, the backpack is on its way to getting smaller! Which of these movies were you" \
                                   " talking about?"
                        for movie_id in narrowedDownIndices:
                            response += "\n" + self.titles[movie_id][0]
                        self.isDisambiguating = True
                        self.disambiguationMovieIndices = narrowedDownIndices
                        return response
                    else:  # only one left, woohoo
                        self.isDisambiguating = False
                        id = narrowedDownIndices[0]
                        title = self.titles[id][0]
                        line = self.lineToUseForDisambiguation


                else:  # needs to acquire id from scratch
                    titles = self.extract_titles(line)
                    # see if no title was found
                    if len(titles) == 0:
                        if self.randIndexArbitrary == 0:
                            response = "Hm, I don't know what you're talking about, let's go " \
                                       "back to movies! Make sure to say them loudly and clearly! Vamos!"
                        elif self.randIndexArbitrary == 1:
                            response = "Ok, got it! But Boots and I are excited to explore your favorite movies, " \
                                       "and you must say it loudly and clearly! " \
                                       "You didn't say anything about a movie Boots or I know. Please talk about a movie!"
                        elif self.randIndexArbitrary == 2:
                            response = "I see! We need to continue on our adventure, " \
                                       "so please tell me about a movie " \
                                       "that Boots and I know about!"
                        else:
                            response = "Thanks for telling me, pal, but you need to tell me about a movie and " \
                                       "be super clear about it! We need to solve our puzzle!"
                        self.randIndexArbitrary += 1
                        return response

                    # see if more than one title was found
                    if len(titles) > 1:
                        if randNum < 0.5:
                            response = "Slow down, PBS kid!. Only talk about 1 movie at a time!"
                        else:
                            response = "You're going even faster than Diego! Just talk about 1 movie and wait for me!"
                        return response

                    # Get the ids
                    movie_ids = self.find_movies_by_title(titles[0])

                    # If no id was found, say it wasn't found
                    if len(movie_ids) == 0:
                        # try to do spell check
                        indicesOfMoviesClosestToTitle = self.find_movies_closest_to_title(titles[0])
                        # check if spell check returned nothing
                        if len(indicesOfMoviesClosestToTitle) == 0:
                            if randNum < 0.5:
                                response = "I've never heard of " + titles[
                                    0] + ", it's not in my backpack! Tell me about" \
                                         " another movie you liked or disliked."
                            else:
                                response = titles[0] + " isn't even on my map! Try another movie."
                        # check if spell check returned just one or multiple
                        else:
                            response = "Boots is wondering if you meant " + \
                                       self.titles[indicesOfMoviesClosestToTitle[0]][0] \
                                       + "?"
                            self.spellCheckMovieIndices = indicesOfMoviesClosestToTitle
                            self.currSpellCheckMovieIndex = indicesOfMoviesClosestToTitle[0]
                            self.spellCheckMovieIndices.pop(0)
                            self.isClarifyingFromSpellCheck = True
                            self.lineToUseForSentimentSpellCheck = line
                        return response

                    # if too many ids were found, asked for clarification
                    if len(movie_ids) > 1:
                        # try to disambiguate
                        response = "Ay ay! In my brainy backpack, I found more than one movie " \
                                   "called " + titles[0] + ". Can you clarify which one you meant out of these?"
                        for movie_id in movie_ids:
                            response += "\n" + self.titles[movie_id][0]
                        self.isDisambiguating = True
                        self.disambiguationMovieIndices = movie_ids
                        self.lineToUseForDisambiguation = line
                        return response

                    id = movie_ids[0]
                    title = titles[0]

                # See if it's a movie we've been told about before
                if self.user_ratings[id] != 0:
                    response = title + " is already in my backpack of movies you like or dislike! Add another item " \
                                       "and tell me about a new movie!"
                    return response

                # Try extracting the sentiment
                sentimentForMovie = self.extract_sentiment(line)

                # if sentiment is 0, say that you're not sure if user liked it
                if sentimentForMovie == 0:
                    if randNum < 0.5:
                        response = "Boots isn't sure if you liked " + title + ". Tell us more about it."
                    else:
                        response = "Can you please tell Boots more about " + title + \
                                   "? I'm not sure what you thought!"
                    return response

                # Got past all the failure cases!

                # Update the user ratings, as well as number of movies given by user
                self.user_ratings[id] = sentimentForMovie
                self.numMoviesGivenByUser += 1

                # Check if less than 5 recommendations have been given as of now, meaning we need to ask for more
                if self.numMoviesGivenByUser < 5:
                    if sentimentForMovie > 0:
                        if randNum < 0.3:
                            response = "Fantastico, you liked " + title + "! Tell Boots and I what you " \
                                                                          "thought of another movie."
                        elif randNum < 0.6:
                            response = "Excelente, glad to know you enjoyed " + title + ". What about another one?"
                        else:
                            response = "Gracias! It's great that " + title + \
                                       " was fun for you. Why don't you also talk about a different movie?"
                        return response
                    else:
                        if randNum < 0.3:
                            response = "AHHH, you didn't like " + title + \
                                       ". Boots loves that one. Tell me what you thought " \
                                       "of another movie."
                        elif randNum < 0.6:
                            response = "Swiper would be angry to hear you weren't a fan of " + title + \
                                       ". Any other movies you do actually like?"
                        else:
                            response = "It's a jungle-sized disaster that " + title + \
                                       " didn't go well with you. Why don't you talk about another movie?"
                        return response

                # We reached our fifth movie, time to start recommending
                elif self.numMoviesGivenByUser == 5:
                    self.recs = self.recommend(self.binarize(self.user_ratings), self.ratings)
                    self.indexOfRecsBeingGiven = 0
                    if sentimentForMovie > 0:
                        response = "We've solved it! We've solved it! I see that you liked " + title + \
                                   ". We'd recommend " + \
                                   self.titles[self.recs[self.indexOfRecsBeingGiven]][0] + \
                                   ". Would you like more recommendations?"
                    else:
                        response = "We've solved it! We've solved it! I see that you disliked " + title + \
                                   ". We'd recommend " + \
                                   self.titles[self.recs[self.indexOfRecsBeingGiven]][0] + \
                                   ". Would you like more recommendations?"
                    self.indexOfRecsBeingGiven += 1
                    return response


        ####################################################################################### STARTER MODE PROCESS #######################################################################################
        else:
            response = "I processed {} in starter mode!!".format(line)
            randNum = random.random()  # random number between 0 and 1

            # see if we are in the process of recommending
            if self.numMoviesGivenByUser >= 5:  # we're in the recommending process
                if self.indexOfRecsBeingGiven >= len(self.recs):  # no more recs to give
                    if randNum < 0.5:
                        response = "Unfortunately, that's all the recommendations I have. Feel free to restart me!"
                    else:
                        response = "That's the extent of my recommendations. We can restart if you want!"
                    return response
                else:  # more recs to give
                    # see if user even wants more recs
                    loweredLine = line.lower()
                    if "yes" in loweredLine or "yeah" in loweredLine or "sure" in loweredLine or "ok" in "loweredLine":
                        if self.randIndexGivingRecs == 0:
                            response = "We'd also recommend " + \
                                       self.titles[self.recs[self.indexOfRecsBeingGiven]][0] + \
                                       ". How about another one?"
                            self.indexOfRecsBeingGiven += 1
                        elif self.randIndexGivingRecs == 1:
                            response = self.titles[self.recs[self.indexOfRecsBeingGiven]][0] + \
                                       " would be a good movie for you. Would you like more recommendations?"
                            self.indexOfRecsBeingGiven += 1
                        elif self.randIndexGivingRecs == 2:
                            response = "Surely check out " + self.titles[self.recs[self.indexOfRecsBeingGiven]][0] + \
                                       ". Do you want more recommendations?"
                            self.indexOfRecsBeingGiven += 1
                        elif self.randIndexGivingRecs == 3:
                            response = "Definitely watch " + self.titles[self.recs[self.indexOfRecsBeingGiven]][0] + \
                                       ". Want more?"
                            self.indexOfRecsBeingGiven += 1
                        elif self.randIndexGivingRecs == 4:
                            response = "Why not watch " + self.titles[self.recs[self.indexOfRecsBeingGiven]][0] + \
                                       "? Do you want any more recs?"
                            self.indexOfRecsBeingGiven += 1
                        elif self.randIndexGivingRecs == 5:
                            response = "Sure, go see " + self.titles[self.recs[self.indexOfRecsBeingGiven]][0] + \
                                       "? Do you think another rec would be nice?"
                            self.indexOfRecsBeingGiven += 1
                        elif self.randIndexGivingRecs == 6:
                            response = "You have to see " + self.titles[self.recs[self.indexOfRecsBeingGiven]][0] + \
                                       "? I have some more recommendations if you want?"
                            self.indexOfRecsBeingGiven += 1
                        elif self.randIndexGivingRecs == 7:
                            response = "Seeing " + self.titles[self.recs[self.indexOfRecsBeingGiven]][0] + \
                                       " is a must do. Tell me if you want more!"
                            self.indexOfRecsBeingGiven += 1
                        elif self.randIndexGivingRecs == 8:
                            response = "You better watch " + self.titles[self.recs[self.indexOfRecsBeingGiven]][0] + \
                                       ". Would another recommendation be helpful?"
                            self.indexOfRecsBeingGiven += 1
                        elif self.randIndexGivingRecs == 8:
                            response = "Next movie rec is " + self.titles[self.recs[self.indexOfRecsBeingGiven]][0] + \
                                       ". Need more recs?"
                            self.indexOfRecsBeingGiven += 1
                        elif self.randIndexGivingRecs >= 9:
                            response = "Ok, go watch " + self.titles[self.recs[self.indexOfRecsBeingGiven]][0] + \
                                       ". Let me know if you want more."
                            self.indexOfRecsBeingGiven += 1
                        self.randIndexGivingRecs += 1
                        return response
                    elif "no" in loweredLine or "not" in loweredLine or "nah" in loweredLine:
                        if randNum < 0.5:
                            response = "Ok, I won't give any more recommendations!"
                        else:
                            response = "All right, no more recommendations for you!"
                        return response
                    else:
                        if randNum < 0.5:
                            response = "I can't tell if you want more recommendations. Can you be more explicit?"
                        else:
                            response = "Hmm, I'm not sure whether you're seeking additional recommendations."
                        return response

            else:  # We are in the data-seeking process
                titles = self.extract_titles(line)

                # see if no title was found
                if len(titles) == 0:
                    if randNum < 0.5:
                        response = "Unfortunately, I couldn't identify any movie in what you just said. " \
                                   "Can you try telling me " \
                                   "about a movie and your opinion on it? Also, please put the movie in quotes."
                    else:
                        response = "There doesn't seem to be a movie in what you just said. " \
                                   "Please tell me " \
                                   "about a movie and your opinion about it, and put the movie in quotes!"
                    return response

                # see if more than one title was found
                if len(titles) > 1:
                    if randNum < 0.5:
                        response = "I'm sorry, you're talking about more than one movie at a time. Can " \
                                   "you only discuss one and wait for me to reply?"
                    else:
                        response = "Unfortunately, you should only talk about one movie at a time."
                    return response

                # Get the ids
                movie_ids = self.find_movies_by_title(titles[0])

                # If no id was found, say it wasn't found
                if len(movie_ids) == 0:
                    if randNum < 0.5:
                        response = "I've never heard of " + titles[0] + ", sorry... Tell me about " \
                                                                        "another movie you liked or disliked."
                    else:
                        response = titles[0] + " isn't a movie I know. Try another movie."
                    return response

                # if too many ids were found, asked for clarification
                if len(movie_ids) > 1:
                    if randNum < 0.5:
                        response = "I found more than one movie called " + titles[0] + ". Can you clarify?"
                    else:
                        response = "There are multiple movies with the name " + titles[0] + \
                                   ". Please give a clarification."
                    return response

                id = movie_ids[0]

                # See if it's a movie we've been told about before
                if self.user_ratings[id] != 0:
                    response = titles[0] + " is already one you've told me about. Tell me about a new movie!"
                    return response

                # Try extracting the sentiment
                sentimentForMovie = self.extract_sentiment(line)

                # if sentiment is 0, say that you're not sure if user liked it
                if sentimentForMovie == 0:
                    if randNum < 0.5:
                        response = "I'm not sure if you liked " + titles[0] + ". Tell me more about it."
                    else:
                        response = "Can you please tell me more about " + titles[0] + \
                                   "? I'm not sure about your opinion on it."
                    return response

                # Got past all the failure cases

                # Update the user ratings, as well as number of movies given by user
                self.user_ratings[id] = sentimentForMovie
                self.numMoviesGivenByUser += 1

                # Check if less than 5 recommendations have been given as of now, meaning we need to ask for more
                # or if 5 have been shared, just tell them you understood their opinion
                if self.numMoviesGivenByUser <= 5:
                    if sentimentForMovie > 0:
                        if self.numMoviesGivenByUser == 1:
                            response = "Ok, you liked " + titles[0] + "! Tell me what you thought of another movie."
                        elif self.numMoviesGivenByUser == 2:
                            response = "Glad to know you enjoyed " + titles[0] + ". What about another one?"
                        elif self.numMoviesGivenByUser == 3:
                            response = "It's great that " + titles[0] + \
                                       " went well with you. Why don't you also talk about a different movie?"
                        elif self.numMoviesGivenByUser == 3:
                            response = "So thrilled to hear that " + titles[0] + \
                                       " was good. Can't wait to hear about another movie!"
                        elif self.numMoviesGivenByUser == 4:
                            response = "Got it, I see that you had a good time watching " + titles[0] + \
                                       ". Can you let me know about another movie too?"
                        elif self.numMoviesGivenByUser == 5:
                            response = "Awesome news that you enjoyed " + titles[0] + \
                                       "!"
                    else:
                        if self.numMoviesGivenByUser == 1:
                            response = "Oh, you didn't like " + titles[0] + ". Tell me what you thought " \
                                                                            "of another movie."
                        elif self.numMoviesGivenByUser == 2:
                            response = "Sorry to hear you weren't a fan of " + titles[0] + \
                                       ". Any other movies you have opinions on?"
                        elif self.numMoviesGivenByUser == 3:
                            response = "It's unfortunate that " + titles[0] + \
                                       " didn't go well with you. Why don't you talk about another movie?"
                        elif self.numMoviesGivenByUser == 4:
                            response = "I'm sad that " + titles[0] + \
                                       " wasn't really in your aisle. Could you share another movie opinion?"
                        elif self.numMoviesGivenByUser == 5:
                            response = "Disheartening news that " + titles[0] + \
                                       " wasn't one you liked."

                # We reached our fifth movie, time to start recommending
                if self.numMoviesGivenByUser == 5:
                    self.recs = self.recommend(self.binarize(self.user_ratings), self.ratings)
                    self.indexOfRecsBeingGiven = 0
                    response += " Given what you told me, we'd recommend " + \
                                self.titles[self.recs[self.indexOfRecsBeingGiven]][0] + \
                                ". Would you like more recommendations?"
                    self.indexOfRecsBeingGiven += 1
                    return response

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
        # text = text.lower()
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
        if self.creative:
            titles = re.findall(r'"(.*?)"', preprocessed_input)
            if len(titles) > 0:
                return titles
            titles = re.findall(r'"(.*?)"', preprocessed_input.lower())
            if len(titles) > 0:
                return titles
            preceding_list = ["like", "enjoy", "enjoi", "saw", "rent", "see", "love", "in", "\"", "thought", "think",
                              "and", "hate"]
            end_list = [")", "\"", ".", "?", "!", "was", "is", "did"]
            succeeding_list = ["was", "is", "did"]
            word_ends_in = [")", "\"", "\'"]

            # stem every word as we go thru
            inputTokens = re.split('[".,!?;&: ]', preprocessed_input.lower())
            p = PorterStemmer()
            i = 0
            # I liked The Notebook
            while i < len(inputTokens):
                stemmedWord = p.stem(inputTokens[i])
                i += 1
                if stemmedWord in preceding_list:
                    possible_title = ""

                    # break when you encounter a word in succeeding list
                    while i < len(inputTokens) and inputTokens[i] not in end_list:
                        if inputTokens[i] != " ":
                            possible_title += inputTokens[i] + " "
                            # len(inputTokens[i]) > 0 and
                            if len(inputTokens[i]) > 0 and inputTokens[i][-1] in word_ends_in:
                                i += 1
                                break
                            i += 1

                    if len(possible_title) > 0 and possible_title.strip() not in titles:
                        titles.append(possible_title.strip())

            j = len(inputTokens) - 1
            while j >= 0:
                stemmedWord = p.stem(inputTokens[j])
                j -= 1
                if stemmedWord in succeeding_list:
                    possible_title = ""

                    # break when you encounter a word in succeeding list
                    while j >= 0 and inputTokens[j] not in preceding_list:
                        if inputTokens[j] != " ":
                            possible_title = inputTokens[j] + " " + possible_title
                            j -= 1

                    if len(possible_title) > 0:
                        titles.append(possible_title.strip())

            return titles
        return re.findall(r'"(.*?)"', preprocessed_input)

    def find_movies_by_title(self, title):
        """ Given a movie title, return a list of indices of matching movies.

        - If no movies are found that match the given title, return an empty
        list.
        - If multiple movies are found that match the given title, return a list
        containing all of the indices of these matching movies.
        - If exactly one movie is found that matches the given title, return a
        list that contains the index of that matching movie.

        Example:
          ids = chatbot.find_movies_by_title('Titanic')
          print(ids) // prints [1359, 2716]

        :param title: a string containing a movie title
        :returns: a list of indices of matching movies
        """
        matching_movies = []

        # normal-- remove articles and check if current title begins with queried title
        for i in range(len(self.titles)):
            row_title = self.titles[i][0]
            if self.check_title_single(self.remove_lead_articles(title), self.remove_trail_articles(row_title)):
                matching_movies.append(i)

        if self.creative:
            # Without capitalization
            title = title.lower()
            titleTokens = re.split('[.,!?;&: ]', title)

            # Disambiguation 1 - widening the funnel
            for i in range(len(self.titles)):
                allTokensLists = []
                possibleTitle = self.titles[i][0].lower()

                possibleTitleTokens = re.split('[.,!?;&: ]', possibleTitle)
                # for tokenList in possibleTitleTokens:
                if self.titleSublistOfPossibleTitle(titleTokens, possibleTitleTokens) and i not in matching_movies:
                    matching_movies.append(i)
                    # break
                # Foreign/alt titles
                foreignTitles = re.findall(r'(?<=\(a.k.a.).*?(?=\) \()|(?<=\().*?(?=\) \()', possibleTitle)

                for foreignTitle in foreignTitles:
                    # if i == 28: print(self.remove_lead_articles(title), self.remove_trail_articles(foreignTitle))
                    if self.remove_lead_articles(title) in self.remove_trail_articles(foreignTitle):
                        matching_movies.append(i)

        return matching_movies

    # helper function to check if title tokens are sublist of a possible title's tokens
    def titleSublistOfPossibleTitle(self, titleTokens, possibleTitleTokens):
        lenTitleTokens = len(titleTokens)
        lenPossibleTitleTokens = len(possibleTitleTokens)
        if lenTitleTokens > lenPossibleTitleTokens:
            return False
        for start in range(lenPossibleTitleTokens):
            if start + lenTitleTokens > lenPossibleTitleTokens:
                break
            if titleTokens == possibleTitleTokens[start: start + lenTitleTokens]:
                return True
        return False

    # Titanic (1887)
    # Titanic (1887)

    # helper function to check if title is single standing
    def check_title_single(self, title, database_title):
        # print(title, database_title)
        if database_title.startswith(title):
            if database_title[len(title):].startswith(" (") or (len(database_title) == len(title)):
                # print(database_title[len(title):])
                return True
        return False

    # helper function to remove articles like a, an, the
    def remove_trail_articles(self, database_title):
        for article in self.article_list:
            article_str = ", " + article
            database_title = database_title.replace(article_str, "")
            article_str = ", " + article.lower()
            database_title = database_title.replace(article_str, "")
        return database_title

    # helper function to remove leading articles in input titles
    def remove_lead_articles(self, query_title):
        for article in self.article_list:
            article_str = article + " "
            if query_title.startswith(article_str):
                query_title = query_title.replace(article_str, "")
            article_str = article.lower() + " "
            if query_title.startswith(article_str):
                query_title = query_title.replace(article_str, "")
        return query_title

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
        p = PorterStemmer()
        sentimentDict = util.load_sentiment_dictionary('data/sentiment.txt')
        sentimentDictStemmed = {}
        for word in sentimentDict:
            stemmedWord = p.stem(word)
            stemmedWord = re.sub(r'[^\w\s]', '', stemmedWord)
            sentimentDictStemmed[stemmedWord] = sentimentDict[word]

        negationWords = ["didnt", "not", "never", "nothing"]
        amplifiers = ["really", "reeally", "absolutely", "extremely", "very", "so", "much", "must"]
        superPositiveWords = ["love", "adore", "thrill"]
        superNegativeWords = ["hate", "detest", "terrible"]
        sentiment = 0
        amplifierCount = 0

        preprocessed_input_no_movies = re.sub(r'"(.*?)"', " ", preprocessed_input)
        preprocessed_input_list = preprocessed_input_no_movies.split(" ")

        negationMultiplier = 1
        if self.creative:
            for origWord in preprocessed_input_list:
                unpuncWord = re.sub(r'[^\w\s]', '', origWord)
                stemmedWord = p.stem(unpuncWord)  # stemmed
                if origWord in negationWords or unpuncWord in negationWords or stemmedWord in negationWords:
                    negationMultiplier *= -1
                    sentiment -= 1
                elif origWord in superNegativeWords or unpuncWord in superNegativeWords or stemmedWord in superNegativeWords:
                    if negationMultiplier == 1:
                        amplifierCount += 1
                elif origWord in superPositiveWords or unpuncWord in superPositiveWords or stemmedWord in superPositiveWords:
                    if negationMultiplier == 1:
                        amplifierCount += 1
                elif origWord in amplifiers or unpuncWord in amplifiers or stemmedWord in amplifiers or '!' in origWord:
                    if negationMultiplier == 1:
                        amplifierCount += 1
                if stemmedWord in sentimentDictStemmed:  # check if stemmed is
                    if sentimentDictStemmed[stemmedWord] == "pos":
                        sentiment += (1 * negationMultiplier)
                    else:
                        sentiment -= (1 * negationMultiplier)

            toReturn = None
            if sentiment == 0:
                toReturn = 0
            elif sentiment > 0 and amplifierCount == 0:
                toReturn = 1
            elif sentiment > 0 and amplifierCount > 0:
                toReturn = 2
            elif sentiment < 0 and amplifierCount == 0:
                toReturn = -1
            elif sentiment < 0 and amplifierCount > 0:
                toReturn = -2
            return toReturn
        else:
            for origWord in preprocessed_input_list:
                unpuncWord = re.sub(r'[^\w\s]', '', origWord)
                stemmedWord = p.stem(unpuncWord)  # stemmed
                if origWord in negationWords or unpuncWord in negationWords or stemmedWord in negationWords:
                    sentiment -= 2
                if stemmedWord in sentimentDictStemmed:
                    if sentimentDictStemmed[stemmedWord] == "pos":
                        sentiment += 1
                    else:
                        sentiment -= 1
            if sentiment == 0:
                return 0
            elif sentiment < 0:
                return -1
            else:
                return 1

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

        tuple_list = []
        turn_phrases = ["but", "however", "although", ". "]
        splits = [preprocessed_input]
        sents = []
        turn_phrase = False
        list_titles = []

        # list_titles = self.extract_titles(preprocessed_input)
        for phrase in turn_phrases:
            if phrase in preprocessed_input:
                turn_phrase = True
                splits = preprocessed_input.split(phrase)

        for split in splits:
            list_titles.append(self.extract_titles(split))
            sents.append(self.extract_sentiment(split))

        i = 0
        for split in list_titles:
            if turn_phrase == False:
                i = 0
            for title in split:
                tuple_list.append((title, sents[i]))
            i += 1

        return tuple_list

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
        # convert to database movie title format based on articles and years
        hasYear = False
        if title.find("(") == -1:  # does not have year in parenthesis
            if title.startswith("The "):
                title = title[4:] + ", The"
            elif title.startswith("A "):
                title = title[2:] + ", A"
            elif title.startswith("An "):
                title = title[3:] + ", An"
        else:  # does have year in parenthesis
            hasYear = True
            indexOfOpenParenthesis = title.find("(")
            if title.startswith("The "):
                title = title[4:indexOfOpenParenthesis] + ", The " + title[indexOfOpenParenthesis:]
            elif title.startswith("A "):
                title = title[2:indexOfOpenParenthesis] + ", A " + title[indexOfOpenParenthesis:]
            elif title.startswith("An "):
                title = title[3:indexOfOpenParenthesis] + ", An " + title[indexOfOpenParenthesis:]

        # do edit distance calculations
        currMinEditDistance = None
        listOfPossibleIndices = []
        listOfPossibleTitles = []
        for i in range(len(self.titles)):
            possibleTitle = self.titles[i][0]
            if not hasYear:
                indexOfSpaceOpenParenthesisInPossibleTitle = possibleTitle.find(" (")
                possibleTitle = possibleTitle[:indexOfSpaceOpenParenthesisInPossibleTitle]
            editDistance = self.edit_distance_helper(title.lower(), possibleTitle.lower())
            if editDistance > max_distance:
                continue
            if currMinEditDistance is None:
                currMinEditDistance = editDistance
                listOfPossibleIndices.append(i)
                listOfPossibleTitles.append(possibleTitle)
            elif editDistance < currMinEditDistance:
                currMinEditDistance = editDistance
                listOfPossibleIndices = [i]
                listOfPossibleTitles = [possibleTitle]
            elif editDistance == currMinEditDistance:
                listOfPossibleIndices.append(i)
                listOfPossibleTitles.append(possibleTitle)

        return listOfPossibleIndices

    # helper function to find edit distance b/w 2 strings
    def edit_distance_helper(self, title1, title2):
        m = len(title1)
        n = len(title2)
        dp = [[0 for i in range(n + 1)] for j in range(m + 1)]

        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0:
                    dp[i][j] = j
                elif j == 0:
                    dp[i][j] = i
                elif title1[i - 1] == title2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = min(dp[i][j - 1] + 1, dp[i - 1][j] + 1, dp[i - 1][j - 1] + 2)

        return dp[m][n]

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
        candidateInfo = []
        for candidateIndex in candidates:
            candidateMovie = self.titles[candidateIndex][0]
            # indexOfOpenParenthesis = candidateMovie.find("(")
            # indexOfClosedParenthesis = candidateMovie.find(")")
            candidateYear = int(candidateMovie[len(candidateMovie) - 5:len(candidateMovie) - 1])
            candidateInfo.append((candidateIndex, candidateMovie, candidateYear))

        candidateInfo = sorted(candidateInfo, key=lambda tup: tup[2])

        narrowedDownIndices = []

        clarificationSub = re.sub(r'[^\w\s]', '', clarification)

        if clarification.isdigit() and int(
                clarification) < 10:  # something like 2 corresponding to Scream 2 or 2 meaning the second one
            # like scream 2 case
            case1found = False
            clarification = " " + clarification + " "
            for candidateIndex, candidateMovie, candidateYear in candidateInfo:
                if candidateMovie.find(clarification) != -1:
                    narrowedDownIndices.append(candidateIndex)
                    case1found = True
            # meaning the second one case
            if not case1found:
                narrowedDownIndices.append(candidateInfo[int(clarification) - 1][0])

        elif clarification.isdigit() and 1000 < int(clarification) < 3000:  # corresponding to the year
            for candidateIndex, candidateMovie, candidateYear in candidateInfo:
                if candidateYear == int(clarification):
                    narrowedDownIndices.append(candidateIndex)

        elif "most recent" in clarification or "latest" in clarification:  # for ones like most recent
            narrowedDownIndices.append(candidateInfo[len(candidateInfo) - 1][0])
        elif "least recent" in clarification or "oldest" in clarification:  # own addition for possible test case
            narrowedDownIndices.append(candidateInfo[0][0])

        elif "first one" in clarification or "1st one" in clarification and len(candidates) >= 1:
            narrowedDownIndices.append(candidates[0])
        elif "second one" in clarification or "2nd one" in clarification and len(candidates) >= 2:
            narrowedDownIndices.append(candidates[1])
        elif "third one" in clarification or "3rd one" in clarification and len(candidates) >= 3:
            narrowedDownIndices.append(candidates[2])

        elif 0 <= clarification.find("the ") <= clarification.find(" one"):  # for cases like "the Goblet of Fire one"
            clarification = clarification[clarification.find("the ") + 4: clarification.find(" one")]
            for candidateIndex, candidateMovie, candidateYear in candidateInfo:
                if candidateMovie.find(clarification) != -1 or candidateMovie.find(clarificationSub) != -1:
                    narrowedDownIndices.append(candidateIndex)

        else:  # search term case like "Sorcerer's Stone"
            for candidateIndex, candidateMovie, candidateYear in candidateInfo:
                if candidateMovie.find(clarification) != -1 or candidateMovie.find(clarificationSub) != -1:
                    narrowedDownIndices.append(candidateIndex)

        return narrowedDownIndices

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
        binarized_ratings = np.where((ratings <= 2.5) * (ratings != 0), -1, ratings)
        binarized_ratings = np.where((binarized_ratings > 2.5) * (binarized_ratings != 0), 1, binarized_ratings)

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
        if np.count_nonzero(u) == 0 or np.count_nonzero(v) == 0:
            return np.NaN
        similarity = 0
        similarity = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
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
        userRatings = []
        for userMovieIndex in range(len(user_ratings)):
            if user_ratings[userMovieIndex] != 0:
                continue
            else:  # user hasn't rated yet
                ratingToCalculate = 0
                for sumUserMovieIndex in range(len(user_ratings)):
                    if user_ratings[sumUserMovieIndex] != 0:  # user already rated
                        similarity = self.similarity(ratings_matrix[userMovieIndex],
                                                     ratings_matrix[sumUserMovieIndex])
                        ratingToCalculate += similarity * user_ratings[sumUserMovieIndex]
                if not np.isnan(ratingToCalculate):
                    userRatings.append((userMovieIndex, ratingToCalculate))

        sortedUserRatings = sorted(userRatings, key=lambda tup: tup[1], reverse=True)
        sortedUserRatingsOnlyMovieIndices = list(map(lambda tup: tup[0], sortedUserRatings))
        topK = sortedUserRatingsOnlyMovieIndices[:k]
        recommendations = topK

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
        return "Hello! This chatbot is for recommending movies to you based on the movies you have liked or " \
               "disliked in the past. In starter mode, be sure to give your movie name in quotation marks. " \
               "In creative mode, I'll be Dora the Explorer! I'll be keeping track of how strongly " \
               "you feel about certain movies and we'll be able to interact in case you make any typos, or " \
               "want to clarify a movie you mentioned. After I've heard about five of your " \
               "movie tastes, I'll give you movie " \
               "recommendations one after the other! Let's get started on our movie adventure!"


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')