# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
from numpy.linalg import norm
import re
import porter_stemmer
from operator import itemgetter
import random


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'girlybot'

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
        self.user_movies = np.zeros(len(self.titles))
        self.rated = 0
        self.recommendations = []
        self.recsGiven = 0

        self.clarifying = False
        self.clarifyingIndices = []
        self.clarifiedTitles = "" 
        self.clarifyingLine = ""

        self.clarifyingSpell = False
        self.clarifyingSpellIndices = []
        self.clarifiedSpellTitles = ""
        self.clarifyingSpellLine = ""
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
            greeting_message = "Oh my gosh, hey girl! So like...what's up? I am - like - SO excited you're here. I can totally recommend some movies if you tell me what movies you've liked or disliked!"
        else:
            greeting_message = "Tell me about a movie you liked or disliked."

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
            goodbye_message = "SO good chatting and feel free to hit me up again, like, if you need another rec. Like, any rec. Byeee!"
        else:
            goodbye_message = "Have a nice day!"

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return goodbye_message

    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################


    def checkEmotion(self, line):
        line = line.lower()
        joy_indicators = ["happy", "glad", "content", "good", "silly", "delighted", "excited", "overjoyed", "ecstatic", "merry", "lively", "peaceful", "thrilled"]
        anger_indicators = ["angry", "mad", "angered", "furious", "fuming", "annoyed", "hated"]
        sadness_indicators = ["sad", "disappointed", "sorry", "sorrowful", "down", "uncomfortable"]
        fear_indicators = ["scared", "fearful", "afraid", "concerned", "worried", "embarrassed", "overwhelmed", "stressed"]
        surprise_indicators = ["surprised", "shocked", "astonished"]
        disgust_indicators = ["disgusted", "icked", "grossed out", "queasy", "nauseated"]
            
        for word in line.split():
            if word in joy_indicators:
                return "joy"
            if word in anger_indicators:
                return "anger"
            if word in sadness_indicators:
                return "sadness"
            if word in fear_indicators:
                return "fear"
            if word in surprise_indicators:
                return "surprise"
            if word in disgust_indicators:
                return "disgust"
        return ""
    
    def respondToEmotion(self, emotion):
        emotionalResponse = ""
        if emotion == "joy":
            emotionalResponse += "Yass!! I'm like soooo glad you feel that way."
        elif emotion == "anger":
            emotionalResponse += "Oh! That is totallyyy my bad, like I didn't mean to. I'm sorry."
        elif emotion == "sadness":
            emotionalResponse += "I'm sorry you feel that way, like, really."
        elif emotion == "fear":
            emotionalResponse += "Girl, I know right, it's scary...but it'll be okay."
        elif emotion == "surprise":
            emotionalResponse += "Oh my god! I know, right?"
        elif emotion == "disgust":
            emotionalResponse += "Ugh! That's like, so gross!"
        emotionalResponse += " " + self.gen_prompt()
        return emotionalResponse

    def gather_taste(self, input_titles, line):
        response = ""
        indices = []
        if (self.clarifying == True):
            if line.isdigit() == False:
                return "Ummm... that's not a number. Pick again."
            elif int(line) > len(self.clarifyingIndices) or int(line) < 1:
                return "Yeah, that's not a valid number. Can you pick another?"
            self.clarifiedTitles = self.titles[self.clarifyingIndices[int(line) - 1]][0]
            input_titles = [self.clarifiedTitles]
        if (self.clarifyingSpell == True):
            if (line.lower() == "yes"):
                self.clarifiedSpellTitles = self.titles[self.clarifyingSpellIndices[0]][0]
            else:
                self.clarifyingSpell = False
                return ("Sorry, try to enter a new title.")

        #if len(input_titles) > 1 and (self.clarifying == False and self.clarifyingSpell == False):
            #response += self.gen_response("multiple_titles")
        if len(input_titles) == 0 and (self.clarifying == False and self.clarifyingSpell == False):
            # if in creative mode and there are no quotes in the input, check for emotion phrase:
            if self.creative:
                emotionDisplayed = self.checkEmotion(line)
                firstWord = line.split(" ", 2)[0].lower()
                if emotionDisplayed != "":
                    response += self.respondToEmotion(emotionDisplayed)
                elif line.endswith("?") or firstWord == "what" or firstWord == "how" or firstWord == "why" or firstWord == "who" or firstWord == "when" or firstWord == "can":
                    if firstWord == "what":
                        i = random.randrange(2)
                        responses = ["I don't really know WHAT per se. You should ask someone else... ", 
                            "Well, what do you think??"]
                        response += responses[i]
                    elif firstWord == "how":
                        i = random.randrange(2)
                        responses = ["Girl... you really think I know how?", 
                            "How you'd come to believe I'd know such a thing is crazy."]
                        response += responses[i]
                    elif firstWord == "why":
                        i = random.randrange(2)
                        responses = ["That's crazy you think I'd know why.", "Why don't you look that up!"]
                        response += responses[i]
                    elif firstWord == "who":
                        i = random.randrange(2)
                        responses = ["Not me, that's for sure!", "Not anyone I'd know."]
                        response += responses[i]
                    elif firstWord == "when":
                        i = random.randrange(2)
                        responses = ["It's very 2000s, that's for sure!", "Centuries and centuries ago..."]
                        response += responses[i]
                    elif firstWord == "can":
                        i = random.randrange(2)
                        responses = ["I know YOU can, girl!", "I don't know if that's something I can do, I'm just a chatbot."]
                        response += responses[i]
                    response += " Let's just talk about movies please..."
                else:
                    response += self.general_handling_message()
            else:
                response += self.gen_response("no_quotes")
        elif len(input_titles) == 1: # and (self.clarifying == False and self.clarifyingSpell == False)
            if (self.clarifying == True):
                line = self.clarifyingLine
                input_titles.append(self.clarifiedTitles)
                self.clarifying = False
            if (self.clarifyingSpell == True):
                line = self.clarifyingSpellLine
                input_titles.append(self.clarifiedSpellTitles)
                self.clarifyingSpell = False
            sentiment_val = self.extract_sentiment(line)
            if sentiment_val == 1 or sentiment_val == -1 or sentiment_val == 0:
                indices = self.find_movies_by_title(input_titles[0])
                if len(indices) > 0:
                    self.user_movies[indices[0]] = sentiment_val
                    if sentiment_val != 0:
                        self.rated += 1
            if self.creative and (sentiment_val == 2 or sentiment_val == -2):
                indices = self.find_movies_by_title(input_titles[0])
                if len(indices) > 0:
                    self.user_movies[indices[0]] = sentiment_val
                    if sentiment_val != 0:
                        self.rated += 1

            numMoviesFound = len(indices)
            if numMoviesFound == 0:
                # if we end up not finding any movies and we are in creative mode, 
                # we first check to see if it was a typo
                # if not a typo, then we check if it was a 
                if self.creative:
                    indices = self.find_alt_title(input_titles[0])
                    possibleTitles = self.find_movies_closest_to_title(input_titles[0])

                    if len(indices) > 0:
                        numMoviesFound = len(indices)
                    elif len(possibleTitles) > 0:
                        response += "Did you mean " + self.titles[possibleTitles[0]][0] + "? Please enter \"Yes\" or \"No.\""
                        self.clarifyingSpell = True
                        self.clarifyingSpellIndices = possibleTitles
                        self.clarifyingSpellLine = line
                        # self.rated -= 1
                    else:
                        response += self.gen_response("not_found", input_titles[0])
                else:
                    response += self.gen_response("not_found", input_titles[0])
            
            if numMoviesFound == 1:
                #todo extra pos and neg statements?
                if sentiment_val == 1 or sentiment_val == 2:
                    response += self.gen_response("pos", self.titles[indices[0]][0])
                elif sentiment_val == -1 or sentiment_val == -2:
                    response += self.gen_response("neg", self.titles[indices[0]][0])
                else:
                    response += self.gen_response("neutral", self.titles[indices[0]][0])
            elif numMoviesFound != 0: # need to clarify
                if self.creative:
                    response += "Ok so like...I found more than one movie. Which one are you referring to? Enter a number, 1 - " + str(numMoviesFound) + "\n"
                else:
                    response += "I found more than one movie. Which one are you referring to? Please enter a number, 1 - " + str(numMoviesFound) + "\n"
                for foundMovie in range(numMoviesFound):
                    response += str(foundMovie + 1) + ": " + self.titles[indices[foundMovie]][0] + "\n"
                self.clarifying = True
                self.clarifyingIndices = indices
                self.clarifyingLine = line
                self.rated -= 1
        elif len(input_titles) > 1: # handle multiple input movies
            sentiment_val = self.extract_sentiment(line)
            their_titles = []
            if (sentiment_val == 1 or sentiment_val == -1 or sentiment_val == 0) or (self.creative and (sentiment_val == 2 or sentiment_val == -2)):
                for titles in range(len(input_titles)):
                    #print(input_titles[titles])
                    indices = self.find_movies_by_title(input_titles[titles])
                    #print(indices)
                    if len(indices) > 0:
                        self.user_movies[indices[0]] = sentiment_val
                        if (sentiment_val != 0):
                            self.rated += 1
                        their_titles.append(self.titles[indices[0]][0])
            print(self.rated)
            if sentiment_val == 1 or sentiment_val == 2:
                response += "That's so chill that you enjoyed watching "
                for their_title in range(len(their_titles) - 1):
                    response += "\"" + their_titles[their_title] + "\" and "
                response += "\"" + their_titles[len(their_titles) - 1] + "\"! " + self.gen_prompt()
            elif sentiment_val == -1 or sentiment_val == -2:
                response += "UGH! I also hated watching "
                for their_title in range(len(their_titles) - 1):
                    response += "\"" + their_titles[their_title] + "\" and "
                response += "\"" + their_titles[len(their_titles) - 1] + "\"! " + self.gen_prompt()
            else:
                response += "Ummmm, I can't really tell if you liked watching "
                for their_title in range(len(their_titles) - 1):
                    response += "\"" + their_titles[their_title] + "\" and "
                response += "\"" + their_titles[len(their_titles) - 1] + "\"... Awkward! " + self.gen_prompt()


        return response

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
        response = ""
        if self.creative:
            input_titles = self.extract_titles(line)
            indices = []

            if self.rated < 4:
                response = self.gather_taste(input_titles, line)
            else:
                if self.recsGiven == 0:
                    print("\nOk, so just like, hang tight for a sec... \n")
                    self.user_movies = self.binarize(self.user_movies)
                    self.recommendations = self.recommend(self.user_movies, self.ratings, 50)

                    response += "I TOTALLY recommend you watch " + self.titles[self.recommendations[self.recsGiven]][0] + "\n"
                    self.recsGiven += 1

                    response += "I might have some other movies that - um - you are SO going to fall in love with. Do you want any more recommendations? (or enter :quit if you're done.)"
                else:
                    if (line.lower() != ":quit" and line.lower() != "no" and line.lower() != "n" and line.lower() != "nope"):
                        print(line)
                        response += "You're going to be obsessed with " + self.titles[self.recommendations[self.recsGiven]][0] + "\n"
                        self.recsGiven += 1
                        response += "I might have some other movies that - um - you are SO going to fall in love. Do you want any more recommendations? (Or enter :quit if you're done.)"
                    else:
                        quit()
        else:
            input_titles = self.extract_titles(line)
            indices = []
            
            if self.rated < 4:
                response = self.gather_taste(input_titles, line)
                #print(self.rated)
            else:
                if self.recsGiven == 0:
                    print("\nThat's enough for me to make a recommendation... \n")
                    self.user_movies = self.binarize(self.user_movies)
                    self.recommendations = self.recommend(self.user_movies, self.ratings, 50)

                    response += "I recommend you watch \"" + self.titles[self.recommendations[self.recsGiven]][0] + "\"\n"
                    self.recsGiven += 1

                    response += "Would you like to hear another recommendation? (Or enter :quit if you're done.)"
                else:
                    if (line.lower() != ":quit" and line.lower() != "no" and line.lower() != "n" and line.lower() != "nope"):
                        print(line)
                        response += "I recommend you also watch \"" + self.titles[self.recommendations[self.recsGiven]][0] + "\"\n"
                        self.recsGiven += 1
                        response += "Would you like to hear another recommendation? (Or enter :quit if you're done.)"
                    else:
                        quit()
        return response

    def gen_response(self, mode, title = ""):
        if mode == "pos":
            response = self.gen_pos_response(title)
            response += self.gen_prompt()
        elif mode == "neg":
            response = self.gen_neg_response(title)
            response += self.gen_prompt()
        elif mode == "not_found":
            response = self.gen_not_found_response(title)
            response += self.gen_prompt()
        elif mode == "neutral":
            response = self.gen_neutral_response(title)
        elif mode == "no_quotes":
            response = self.gen_quotes_message()
        elif mode == "multiple_titles":
            response = self.gen_multiple_titles_message()

        return response

    def gen_pos_response(self, title):
        if self.creative:
            i = random.randrange(5)
            responses = ["I'm also obsessed with \"" + title + ".\" ", 
            "You're so right that \"" + title + "\" was a good film. ", 
            "Oh my god, I love that you loved \"" + title + ".\" ", 
            "Ok - like - u enjoyed \"" + title + ".\" ",
            "\"" + title + "\" was like, SO good. "]
            return responses[i]
        
        else:
            i = random.randrange(5)
            responses = ["So you liked the movie \"" + title + ".\" ", 
            "I agree that \"" + title + "\" was a good film. ", 
            "Good to know that you enjoyed \"" + title + ".\" ", 
            "It seems that you have a positive opinion of \"" + title + ".\" ",
            "You have excellent taste! \"" + title + "\" was great. "]
            return responses[i]

    def gen_prompt(self):
        if self.creative:
            i = random.randrange(3)
            responses = ["So like, what else do you like to watch?", 
            "Um sooo what are your movie faves?", 
            "Give me some more hot takes on movies."]
            return responses[i]
        
        else:
            i = random.randrange(5)
            responses = ["What else have you seen?", 
            "What other film did you like or dislike?",
            "Tell me about another movie.",
            "When you can, please give me another film.",
            "Name another film!"]
            return responses[i]

    def gen_neg_response(self, title):
        if self.creative:
            i = random.randrange(5)
            responses = ["Sooo you didn't like \"" + title + "\". ",
            "Yeah, \"" + title + "\" was not it. ",
            "You weren't a fan of \"" + title + ".\" ",
            "Oh my god, \"" + title + "\" was, like, embarrassing! ",
            "Interesting. You were NOT a big fan of \"" + title + "\". "]
            return responses[i]
        else:
            i = random.randrange(5)
            responses = ["You didn't like the film \"" + title + "\". That narrows it down a bit. ",
            "I also thought \"" + title + "\" wasn't very good. ",
            "So you did not enjoy watching \"" + title + ".\" ",
            "It is helpful to know that \"" + title + "\" was not your cup of tea. ",
            "Interesting. You were not a big fan of \"" + title + "\". "]
            return responses[i]

    def gen_not_found_response(self, title):
        if self.creative:
            i = random.randrange(3)
            responses = ["What even is \"" + title + "?\" ",
            "\"" + title + "\"... that like must be indie, I don't know it. ",
            "I have NO clue what \"" + title + ",\" is. Like what?"]
            return responses[i]
        else:
            i = random.randrange(3)
            responses = ["Hmmm... I've never heard of \"" + title + ".\" ",
            "\"" + title + "\"... That must be quite an underground film. I don't know it. ",
            "Sorry, I haven't seen \"" + title + ",\" so I can't make any judgements from that. "]
            return responses[i]

    def gen_neutral_response(self, title):
        if self.creative:
            i = random.randrange(2)
            responses = ["So, like, do you like or not like \"" + title + "?\" I, like, don't get it. ",
            "What you said about \"" + title + "\" is confusing. Can you explain? "]
            return responses[i]
        else:
            i = random.randrange(3)
            responses = ["I can't tell if you liked \"" + title + ".\" Please elaborate. ",
            "Your opinion of \"" + title + "\" is unclear to me. Tell me more. ",
            "I'm not sure what you thought of \"" + title + "\" Can you clarify for me? "]
            return responses[i]

    def gen_quotes_message(self):
        if self.creative:
            i = random.randrange(2)
            responses = ["So like, you have to write the movie in quotes. ",
            "This is kind of annoying, but like, can you write the movie in quotes?"]
            return responses[i]
        else:
            i = random.randrange(3)
            responses = ["Could you please include the title of the movie in quotation marks in your review? ",
            "It is helpful if you state the name of the film in quotes. Tell me agian. ",
            "To make it clear which movie you're referring to, could you state the name in quotes? "]
            return responses[i]

    def gen_multiple_titles_message(self):
        if self.creative:
            i = random.randrange(2)
            responses = ["So ummm. I can only handle one movie at a time. ",
            "It's like impossible to recommend more than one movie at a time. "]
        else:
            i = random.randrange(3)
            responses = ["For the best recommendations, please review only one movie at a time. ",
            "To avoid any confusion, tell me about films one at a time. ",
            "For the sake of clarity, it is best to only review one movie at a time. "]
    
    def general_handling_message(self):
        i = random.randrange(3)
        responses = ["Girl, are we still talking about movies? If so, please babe, put the name in quotes! ",
            "I don’t really want to talk about anything but movies right now... so please, a movie. ",
            "Not to be rude… but you’re being really boring. Let’s talk about movies please. "]
        response = responses[i]
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

        #return re.findall("([\S]+)", text)
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
        #titles = []

        #for word in preprocessed_input: 
        #    print(word)
        #    if word[0] == "\"":
        #        titles += word

        #return re.findall(r'(\"[\w\s]*\")', preprocessed_input)
        if self.creative:
            return preprocessed_input.split('"')[1::2]
        else:
            return preprocessed_input.split('"')[1::2]

    def find_alt_title(self, title):
        indexList = []

        prefixes = ['A ', 'An ', 'The ', 'Le ', 'L\'', 'Les ', 'Die ', 'La ', 'Las ', 'Da ', 'Der ', 'Il ', 'Das ', 'Lo ', 'El ', 'Une ', 'Un ', 'Una ', 'Det ', 'En ', 'Los ', 'I ']

        for index, tit in enumerate(self.titles):
            curTit = tit[0]

            if curTit.count('(') > 1:
                pos_titles = re.findall(r'\(([\w\s,\'.]*)\)', curTit)

                for pos in pos_titles:
                    if pos.startswith("a.k.a. "):
                        pos = pos.lstrip("a.k.a. ")

                    if pos.isdigit() == False:

                        adjustment1 = ""

                        #if pos.count(',') > 0:
                            #print(pos)

                        for prefix in prefixes:
                            if title.startswith(prefix):
                                article = title.split(' ', 1)[0] + ' '
                                adjustment1 += article + pos[:len(pos) - (1 + len(article)):]
            
                        # If title is equal to our current title or any of its adjustments, track the index.
                        if ((title == pos) or (title == adjustment1)): #or (title.startswith(curTit))
                            indexList.append(index)

        return indexList

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
        indexList = []

        # title is the title we want to find
        for index, tit in enumerate(self.titles):
            titleLen = len(title)

            # curTit is the current title we are comparing to. We will run a series of adjustments
            # on this text to determine if this is the title we are looking for.
            curTit = tit[0]
            curTitLen = len(curTit)

            # First adjustment takes into account the fact that the title may not include a year.
            adjustment1 = curTit[:curTitLen - 7:]

            # Second and third adjustments takes into account of articles that may have been moved
            # to the end of the string, as well as if they include years or not.
            adjustment2 = ""
            adjustment3 = ""
            if(title.startswith('A ') or title.startswith('An ') or title.startswith('The ')):
                article = title.split(' ', 1)[0] + ' '
                adjustment2 += article + curTit[:curTitLen - (8 + len(article)):]
                adjustment3 += article + curTit[:curTitLen - (8 + len(article)):] + curTit[curTitLen - 7::]
            
            # If title is equal to our current title or any of its adjustments, track the index.
            if self.creative:
                titleL = title.lower()
                curTit = curTit.lower()
                adjustment1 = adjustment1.lower()
                adjustment2 = adjustment2.lower()
                adjustment3 = adjustment3.lower()

                if ((titleL == curTit) or (titleL == adjustment1) or (titleL == adjustment2) or (titleL == adjustment3) or (curTit.startswith(titleL + " ")) or (curTit.startswith(titleL + ":"))): #or (title.startswith(curTit))
                    indexList.append(index)
            else:
                if ((title == curTit) or (title == adjustment1) or (title == adjustment2) or (title == adjustment3)): #or (title.startswith(curTit))
                    indexList.append(index)

        return indexList


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
        #Find all words that aren't movie titles
        if self.creative:
            wordsandpunc = re.findall(r"[\w']+|[.,!?;]", preprocessed_input)
            pos_words = 1
            neg_words = 1
            negate = False
            emphasis = False
            negation_words = ["not", "didn't", "wasn't", "isn't", "never"]
            p = porter_stemmer.PorterStemmer()
            # Creative: Find emphasis words for fine-grained extraction
            regex = r"r[e]+[a]+lly"
            match = re.search(regex, preprocessed_input)
            if match != None:
                emphasis = True
            emphasis_words = ["!", "super", "extremely"]
            for word in emphasis_words:
                if word in wordsandpunc:
                    emphasis = True
            super_neg_indicators = ["terrible", "worst", "hate", "awful", "horrible"]
            super_pos_indicators = ["love", "best", "amazing", "favorite", "wonderful", "excellent", "incredible", "phenomenal", "splendid"]
            for word in wordsandpunc:
                if word in negation_words:
                    negate = True
                stemmed = p.stem(word)
                # First check my list of super positive and negative words.
                # If negated, it becomes neutral. 
                if word in super_pos_indicators or stemmed in super_pos_indicators:
                    if negate == False:
                        return 2
                elif word in super_neg_indicators or stemmed in super_neg_indicators:
                    if negate == False:
                        return -2
                
                elif word in self.sentiment:
                    if self.sentiment[word] == 'pos':
                        if negate == False:
                            pos_words += 1
                        else:
                            neg_words += 1
                    else :
                        if negate == True:
                            pos_words += 1
                        else:
                            neg_words += 1
                    negate = False
                elif stemmed in self.sentiment:
                    if self.sentiment[stemmed] == 'pos':
                        if negate == False:
                            pos_words += 1
                        else:
                            neg_words += 1
                    else :
                        if negate == True:
                            pos_words += 1
                        else:
                            neg_words += 1
                    negate = False
                elif stemmed == "enjoi":
                    if negate == False:
                        pos_words += 1
                    else:
                        neg_words += 1
                
            score = (pos_words - neg_words)/(pos_words + neg_words + 2)
            if score > 0 :
                if emphasis == True:
                    return 2
                return 1
            elif score < 0:
                if emphasis == True:
                    return -2
                return -1
            else :
                return 0
        else: # not creative
            words = re.findall(r'\b\w+\b(?=(?:[^"]*"[^"]*")*[^"]*$)', preprocessed_input)
            pos_words = 1
            neg_words = 1
            negate = False
            negation_words = ["not", "didn", "wasn", "isn", "never"]

            p = porter_stemmer.PorterStemmer()

            for word in words:
                if word in negation_words:
                    negate = True

                stemmed = p.stem(word)
                if word in self.sentiment:
                    if self.sentiment[word] == 'pos':
                        if negate == False:
                            pos_words += 1
                        else:
                            neg_words += 1
                    else :
                        if negate == True:
                            pos_words += 1
                        else:
                            neg_words += 1
                    negate = False
                elif stemmed in self.sentiment:
                    if self.sentiment[stemmed] == 'pos':
                        if negate == False:
                            pos_words += 1
                        else:
                            neg_words += 1
                    else :
                        if negate == True:
                            pos_words += 1
                        else:
                            neg_words += 1
                    negate = False
                elif stemmed == "enjoi":
                    if negate == False:
                        pos_words += 1
                    else:
                        neg_words += 1


            score = (pos_words - neg_words)/(pos_words + neg_words + 2)
            
            if score > 0 :
                return 1
            elif score < 0:
                return -1
            else :
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
        pass

    def calculateEditDistance(self, curTitle, title):
        # Set both strings to lowercase since case does not count as an edit.
        curTitle = curTitle.lower()
        title = title.lower()
        
        # We want to calculate the Levenshtein distance between these two strings
        curLen = len(curTitle) + 1
        titleLen = len(title) + 1
        levy = np.zeros((curLen, titleLen))

        # Initialization of the matrix
        for i in range(curLen):
            levy[i, 0] = i
        for j in range(titleLen):
            levy[0, j] = j
        
        # Recurrence Relation
        for i in range(1, curLen):
            for j in range(1, titleLen):
                # If X(i) == Y(j)
                if curTitle[i - 1] == title[j - 1]:
                    levy[i, j] = min(levy[i - 1, j] + 1, levy[i, j - 1] + 1, levy[i - 1, j - 1])
                else:  # If X(i) != Y(j)
                    levy[i, j] = min(levy[i - 1, j] + 1, levy[i , j - 1] + 1, levy[i - 1, j - 1] + 2)

        # The total levy for the two strings is in the corner
        return(levy[curLen - 1,titleLen - 1])

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
        newList = [0]
        shortestEditDistance = self.calculateEditDistance("Toy Story", title)

        for curIndex, tit in enumerate(self.titles):
            curTitle = tit[0]
            if (len(curTitle) > 6):
                curTitleAdj = tit[0][:-7]

            # adj2 and adj3 are for articles
            curTitleAdj2 = ""
            curTitleAdj3 = ""

            if(title.startswith('A ') or title.startswith('An ') or title.startswith('The ')):
                article = title.split(' ', 1)[0] + ' '
                curTitleAdj2 += article + curTitle[:len(curTitle) - (8 + len(article)):]
                curTitleAdj3 += article + curTitle[:len(curTitle) - (8 + len(article)):] + curTitle[len(curTitle) - 7::]   

            curEditDistance = self.calculateEditDistance(curTitle, title)
            curEditDistanceAdj = self.calculateEditDistance(curTitleAdj, title)
            curEditDistanceAdj2 = self.calculateEditDistance(curTitleAdj2, title)
            curEditDistanceAdj3 = self.calculateEditDistance(curTitleAdj3, title)

            """ if (curEditDistanceAdj < shortestEditDistance and title == "Sleeping Beaty"):
                print("title", title)
                print("curTitle", curTitle)
                print("curEditDistance", curEditDistance)
                print("curTitleAdj", curTitleAdj)
                print("curEditDistanceAdj", curEditDistanceAdj) """
            
            if curEditDistance < shortestEditDistance:
                newList.clear()
                newList.append(curIndex)
                shortestEditDistance = curEditDistance
            if curEditDistanceAdj < shortestEditDistance:
                newList.clear()
                newList.append(curIndex)
                shortestEditDistance = curEditDistanceAdj

            if curEditDistanceAdj2 < shortestEditDistance:
                newList.clear()
                newList.append(curIndex)
                shortestEditDistance = curEditDistanceAdj2
            if curEditDistanceAdj3 < shortestEditDistance:
                newList.clear()
                newList.append(curIndex)
                shortestEditDistance = curEditDistanceAdj3

            elif curEditDistance == shortestEditDistance:
                newList.append(curIndex)
            elif curEditDistanceAdj == shortestEditDistance:
                newList.append(curIndex)
        
        if(shortestEditDistance <= max_distance):
            return newList

        return []

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

        # Change all non-zero ratings below or at threshold to -1 and all above to 1
        ratings = np.where(np.logical_and(ratings <= threshold, ratings > 0), -1, ratings)
        binarized_ratings = np.where(ratings > threshold, 1, ratings)

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
        # normalize the first vector
        u = np.array(u)
        uLen = np.sqrt(sum(np.square(u)))
        if uLen != 0:
            uNorm = u / uLen
    
        # normalize the second vector
        v = np.array(v)
        vLen = np.sqrt(sum(np.square(v)))
        if vLen != 0:
            vNorm = v / vLen

        if uLen == 0 or vLen == 0:
            return 0
        return np.matmul(uNorm, vNorm)
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        #return similarity

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

        # starter mode:

        # Populate this list with k movie indices to recommend to the user.
        # Unrated movies is a list of indices that the user hasn't watched.
        unratedMovies = np.where(user_ratings == 0)[0]  #.tolist()
        ratedMovies = np.where(user_ratings != 0)[0].tolist()
        simis = dict()

        # iterate through all the unrated movies
        for urMovie in unratedMovies:
            score = 0
            for rMovie in ratedMovies:
                score += (self.similarity(ratings_matrix[urMovie], ratings_matrix[rMovie]) * user_ratings[rMovie])
            simis[urMovie] = score
        
        similaritiesSorted = sorted(simis, key=lambda x:simis[x], reverse = True)
        recommendations = similaritiesSorted[:k]

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
            return """
            Heyyy!! I guess I'm a movie recommendation chatbot, but like, I'm also
            totally not a weird creepy robot. I don't say 'beep boop bop' or anything
            like that. Don't worry.

            So tell me about some movies you've watched and if you totally loved them
            or really hated them. Then I'll give you some movies you def should watch.

            It helps me if you put the movie in quotes, though, like:

            I thought "Toy Story" was super rad. 
            """
        else:
            return """
            Hello! Welcome to the movie recommendation chatbot! Tell me some movies 
            that you like or dislike and I will tell you some movies that you might
            enjoy!!

            Please only review one movie at a time so we really know if you like it 
            or not. When you refer to a movie, place the title in quotes:

            I really enjoyed "Toy Story"

            We hope you like our chatbot!
            """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
