# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re
import random
import string

from nltk.stem.porter import *

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'movie_recommend_chatbot'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.titles_no_year = []
        self.titles_no_year_old = [re.sub(r'\([^)]*\)', '', title[0]).strip().lower() for title in self.titles]
        for title in self.titles_no_year_old:
            title_to_add = title
            if ", the" in title:
                title_to_add = "the " + title[:-5]
            if ", an" in title:
                title_to_add = "an "+ title[:-4]
            if ", a" in title:
                title_to_add = "a " + title[:-3]
            title_to_add = title_to_add.replace("*", "\*")
            title_to_add = title_to_add.replace("(", "\(")
            title_to_add = title_to_add.replace(")", "\)")
            title_to_add = title_to_add.replace('\"', '\\"')
            title_to_add = title_to_add.replace('.', '\.')
            title_to_add = title_to_add.replace("\'", "\\'")
            title_to_add = title_to_add.replace('?', '\?')
            title_to_add = title_to_add.replace('$', '\$')
            self.titles_no_year.append(title_to_add)
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.stemmer = PorterStemmer()
        self.titles_pos = []
        self.titles_neg = []
        self.user_ratings = np.zeros(len(self.titles))
        self.recs = []
        self.recs_given = 0
        self.mode = "asking"
        self.clar_cand = []
        self.clar_cand_idx = 0
        self.clar_sentiment = 0
        self.anger_words = ["angry", "annoyed", "frustrated", "bitter", "infuriated", "mad", "insulted", "vengeful"]
        self.anger_words = [self.stemmer.stem(word) for word in self.anger_words]
        self.fear_words = ["afraid", "fear", "worried", "nervous", "anxious", "scared", "panicked", "stressed"]
        self.fear_words = [self.stemmer.stem(word) for word in self.fear_words]
        self.disgust_words = ["disgusted", "offended", "revulsion"]
        self.disgust_words = [self.stemmer.stem(word) for word in self.disgust_words]
        self.lust_words = ["arouse", "desire", "infatuation", "lust", "passion", "longing"]
        self.lust_words = [self.stemmer.stem(word) for word in self.lust_words]
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
        if not self.creative:
            greeting_message = "How can I help you?"
        else:
            greeting_message = "Welcome muggle! Let's try to make some movie magic!"
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
        if not self.creative:
            goodbye_message = "Have a nice day!"
        else:
            goodbye_message = "Farewell Muggle! Hope you enjoy your movies."
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
            choice = random.randint(3,4) #3 possible responses for each situation
        else:
            choice = random.randint(0,2)
        if self.mode == "asking":
            titles = self.extract_titles(line.lower())
            sentiment = self.extract_sentiment(line)
            if sentiment == 2: #user is angry
                if choice == 0:
                    response = "I'm sorry for your frustration. Let's get back to movies."
                elif choice == 1:
                    response = "Let's just take a step back here and come back to movies."
                elif choice == 2:
                    response = "That sounds like an insult, not the name of a movie. Let's get back to the task at hand here."
                elif choice == 3:
                    response = "Muggle! Stop insulting me and give me the name of a movie."
                elif choice == 4:
                    response = "Just give me the name of a movie before I challenge you to a duel"
                return response
            if sentiment == 3:
                if choice == 0:
                    response = "It's gonna be ok. Let's talk about movies to make you feel better."
                elif choice == 1:
                    response = "You know what makes me feel better, talking about my favorite movies!"
                elif choice == 2:
                    response = "Nothing like a good movie to calm you down. Tell me about some of your favorites :)"
                elif choice == 3:
                    response = "Sounds like you need some movie magic. Tell me about your favourite movie"
                elif choice == 4:
                    response = "The magic of the movies will make you feel better. Tell me about some of your favourites"
                return response
            if sentiment == 4:
                if choice == 0:
                    response = "Let's change the mood by talking about some not gross movies."
                elif choice == 1:
                    response = "Sorry you feel that way. Let's get back to talking about movies."
                elif choice == 2:
                    response = "You know what always settles my gut, some popcorn and movies."
                elif choice == 3:
                    response = "I imagine you feel how Ronald Weasley did while he was puking slugs. You need a movie to make you feel better"
                elif choice == 4:
                    response = "Well muggles disgust me. Want a movie to make you feel better?"
                return response
            if sentiment == 5:
                if choice == 0:
                    response = "Hmm... I'm not sure that you know what I'm supposed to do. I'm here to help you find some movies!"
                elif choice == 1:
                    response = "I don't know about that, but I do know a lot about movies."
                elif choice == 2:
                    response = "I'm a movie expert, I wouldn't know about that. What are some of your favorites?"
                elif choice == 3:
                    response = "You've gone off topic muggle. Let's get back to the movies!"
                elif choice == 4:
                    response = "Muggles! Let's stop dilly dallying and get to some movies!"
                return response
            if len(titles) == 0:
                if choice == 0:
                    response = "Sorry, I didn't get that movie. Can you rephrase that?"
                elif choice == 1:
                    response = "Hmm... I couldn't find a movie in what you told me. Please put the movie in quotes."
                elif choice == 2:
                    response = "I didn't quite catch what movie you meant in that sentence. Can you try phrasing that differently?"
                elif choice == 3:
                    response = "I don't know what you're talking about muggle. Rephrase it!"
                elif choice == 4:
                    response = "You're confusing me muggle. Try putting the movie in quotes!"
                return response
            for title in titles:
                idx = self.find_movies_by_title(title)
                if len(idx) == 0:
                    self.clar_cand = self.find_movies_closest_to_title(title)
                    if len(self.clar_cand) == 0:
                        if choice == 0:
                            response = 'Sorry, I could not find "' + title +'". Tell me about another movie you have seen.'
                        elif choice == 1:
                            response = "Hmm... I've never heard about " + title + ". What about a different movie?"
                        elif choice == 2:
                            response = "That doesn't sound like a movie to me. Any other ones that I might know?"
                        elif choice == 3:
                            response = "I couldn't find that in the Hogwarts library. Try a different film."
                        elif choice == 4:
                            response = "Even my father hasn't heard of that movie. Try something else!"
                        return response
                    else:
                        if choice < 3:
                            response = 'Did you mean "' + self.titles[self.clar_cand[0]][0] + '"?'
                        else:
                            response = 'Muggle, were you talking about "' + self.titles[self.clar_cand[0]][0] + '"?'
                        self.clar_cand_idx = 1
                        self.mode = "clarify_close"
                        self.clar_sentiment = sentiment
                        return response
                elif len(idx) > 1:
                    if choice == 0 or choice == 2:
                        response = 'I found more than one movie called "' + title + '". Can you please clarify?'
                    elif choice == 1:
                        response = 'I found multiple movies called "' + title + '". Anything you can give me to narrow it down?'
                    elif choice == 3:
                        response = 'The house elves have found more than one movie called "' + title + '". Any info to help them out?'
                    elif choice == 4:
                        response = 'Hogwats have a couple movies called "' + title + '". Gimme something to narrow it down a bit!'
                    self.mode = "clarify"
                    self.clar_cand = idx
                    self.clar_sentiment = sentiment
                    return response
            else:
                if sentiment == 1:
                    if choice == 0:
                        response = 'Ok, so you liked "'
                        if len(titles) == 1:
                            response += titles[0]
                        else:
                            response += titles[0]
                            for title in titles[1:]:
                                response += '" and "' 
                                response += title
                        response += '". Anything else?'
                    elif choice == 1:
                        response = 'Good to hear that you liked "'
                        if len(titles) == 1:
                            response += titles[0]
                        else:
                            response += titles[0]
                            for title in titles[1:]:
                                response += '" and "' 
                                response += title
                        response += '". Tell me about another movie you have seen.'
                    elif choice == 2:
                        response = 'So happy to hear you enjoyed "'
                        if len(titles) == 1:
                            response += titles[0]
                        else:
                            response += titles[0]
                            for title in titles[1:]:
                                response += '" and "' 
                                response += title
                        response += '". What other movies did you like?'
                    elif choice == 3:
                        response = 'Of course a muggle like you would enjoy "'
                        if len(titles) == 1:
                            response += titles[0]
                        else:
                            response += titles[0]
                            for title in titles[1:]:
                                response += '" and "' 
                                response += title
                        response += '". Maybe something original?'
                    elif choice == 4:
                        response = 'So you like "'
                        if len(titles) == 1:
                            response += titles[0]
                        else:
                            response += titles[0]
                            for title in titles[1:]:
                                response += '" and "' 
                                response += title
                        response += '". Well I guess you will never have the taste of my father and I. Tell me about a movie with some class.'
                elif sentiment == -1:
                    if choice == 0:
                        response = 'Ok, so you did not like "'
                        if len(titles) == 1:
                            response += titles[0]
                        else:
                            response += titles[0]
                            for title in titles[1:]:
                                response += '" and "' 
                                response += title
                        response += '". Anything else?'
                    elif choice == 1:
                        response = 'Sorry to hear you did not like "'
                        if len(titles) == 1:
                            response += titles[0]
                        else:
                            response += titles[0]
                            for title in titles[1:]:
                                response += '" and "' 
                                response += title
                        response += '". Maybe a movie you did like to cheer your spirits?'
                    elif choice == 2:
                        response = 'It is a shame you did not like "'
                        if len(titles) == 1:
                            response += titles[0]
                        else:
                            response += titles[0]
                            for title in titles[1:]:
                                response += '" and "' 
                                response += title
                        response += '". Tell me more about some other movies you have seen.'
                    elif choice == 3:
                        response = 'Only a fool would not like "'
                        if len(titles) == 1:
                            response += titles[0]
                        else:
                            response += titles[0]
                            for title in titles[1:]:
                                response += '" and "' 
                                response += title
                        response += '". Any other wrong opinions?'
                    elif choice == 4:
                        response = 'A muggle that does not like "'
                        if len(titles) == 1:
                            response += titles[0]
                        else:
                            response += titles[0]
                            for title in titles[1:]:
                                response += '" and "' 
                                response += title
                        response += '". I guess there is a first for everything. Maybe you do have some taste...'
                elif sentiment == 0:
                    if choice == 0:
                        response = 'I can not tell if you liked "'
                        if len(titles) == 1:
                            response += titles[0]
                        else:
                            response += titles[0]
                            for title in titles[1:]:
                                response += '" and "' 
                                response += title
                        response += '". Can you rephrase that?'
                    elif choice == 1:
                        response = 'Can you rephrase that? I am not sure how you feel about "'
                        if len(titles) == 1:
                            response += titles[0]
                        else:
                            response += titles[0]
                            for title in titles[1:]:
                                response += '" and "' 
                                response += title
                        response += '".'
                    elif choice == 2:
                        response = 'I am not sure about your preferences for "'
                        if len(titles) == 1:
                            response += titles[0]
                        else:
                            response += titles[0]
                            for title in titles[1:]:
                                response += '" and "' 
                                response += title
                        response += '". Can you tell me more about them?'
                    elif choice == 3:
                        response = 'Muggle I do not know how you feel about "'
                        if len(titles) == 1:
                            response += titles[0]
                        else:
                            response += titles[0]
                            for title in titles[1:]:
                                response += '" and "' 
                                response += title
                        response += '". Maybe phrase it better...'
                    elif choice == 4:
                        response = 'Even my father can not tell how you feel about "'
                        if len(titles) == 1:
                            response += titles[0]
                        else:
                            response += titles[0]
                            for title in titles[1:]:
                                response += '" and "' 
                                response += title
                        response += '". Phrase that in a way that us upper class can understand.'
            if sentiment == 1 and len(titles) > 0:
                for title in titles:
                    idx = self.find_movies_by_title(title)
                    self.titles_pos.append(idx[0])
            elif sentiment == -1 and len(titles) > 0:
                for title in titles:
                    idx = self.find_movies_by_title(title)
                    self.titles_neg.append(idx[0])
            if len(self.titles_neg) + len(self.titles_pos) >= 5:
                for i in self.titles_neg:
                    self.user_ratings[i] = -1
                for i in self.titles_pos:
                    self.user_ratings[i] = 1
                self.recs = self.recommend(self.user_ratings, self.ratings)
                if choice < 3:
                    response = 'Given what you have told me, I think you would like "' + self.titles[self.recs[0]][0] + '". Would you like another recommendation?'
                else:
                    response = 'From what you have told me, the house elves think you would like "' + self.titles[self.recs[0]][0] + '". Maybe another for your binge?'
                self.recs_given += 1
                self.mode = "rec"
        elif self.mode == "rec":
            if line.lower() in ["yes", "yep", "yeah"]:
                if self.recs_given < len(self.recs):
                    if choice == 0:
                        response = 'I also think you would like "' + self.titles[self.recs[self.recs_given]][0] + '". Would you like another?'
                    elif choice == 1:
                        response = 'You should give "' + self.titles[self.recs[self.recs_given]][0] + '" a try. Would you like another recommendation?'
                    elif choice == 2:
                        response = 'I also think you would love"' + self.titles[self.recs[self.recs_given]][0] + '". Want any more recs?'
                    elif choice == 3:
                        response = 'I sent the house elves back and they found "' + self.titles[self.recs[self.recs_given]][0] + '". Do you want another film?'
                    elif choice == 4:
                        response = 'We had "' + self.titles[self.recs[self.recs_given]][0] + '" in the Hogwarts library. Do you want one from the restricted section?'
                    self.recs_given += 1
                else:
                    if choice < 3:
                        response = "Sorry, that's all of the recommendations I have for you. Please type :quit to exit."
                    else:
                        response = "Looks like you've exhausted our whole library. Type :quit to leave."
            elif line.lower() in ["no", "nope", "nah"]:
                if choice < 3:
                    response = "Thank you, and have a wonderful day. Please type :quit to exit."
                else:
                    response = "The whole library and you don't want another? Your loss... Type :quit to leave."
            else:
                if choice < 3:
                    response = "Sorry, I'm not sure if you want another recommendation. Can you please say yes or no?"
                else:
                    response = "Well which one is it muggle, another or not!"
        elif self.mode == "clarify":
            clar = self.disambiguate(line, self.clar_cand)
            if len(clar) == 0:
                if choice < 3:
                    response = "Hmm... I can't find that movie. Let's try a different one."
                else:
                    response = "The Hogwarts libarary didn't have that. Give me something else to look for."
            elif len(clar) > 1:
                if choice < 3:
                    response = "Hmm... That didn't help me too much. Let's try finding a different movie."
                else:
                    response = "Well that doesn't help me narrow it down, does it. Just tell about something else..."
            else:
                if choice < 3:
                    response = "Perfect, I found what you were looking for. Tell me about another movie."
                else:
                    response = "We've found the golden snitch. Maybe we'll be just as lucky with the next one."
                if self.clar_sentiment == 1:
                    self.titles_pos.append(clar[0])
                elif self.clar_sentiment == -1:
                    self.titles_neg.append(clar[0])
            self.mode = "asking"
        elif self.mode == "clarify_close":
            if line.lower() == "yes":
                if choice < 3:
                    response = "Perfect, I found what you were looking for. Tell me about another movie."
                else:
                    response = "Perfect, you've found your movie magic. Now tell me about different movie."
                if self.clar_sentiment == 1:
                    self.titles_pos.append(self.clar_cand[self.clar_cand_idx-1])
                elif self.clar_sentiment == -1:
                    self.titles_neg.append(self.clar_cand[self.clar_cand_idx-1])
                self.mode = "asking"
                return response
            elif line.lower() == "no":
                if self.clar_cand_idx < len(self.clar_cand):
                    if choice < 3:
                        response = 'Ok, did you mean "' + self.titles[self.clar_cand[self.clar_cand_idx]][0] + '"?'
                    else:
                        response = 'Muggle, I am guessing you meant "' + self.titles[self.clar_cand[self.clar_cand_idx]][0] + '"?'
                    self.clar_cand_idx += 1
                else:
                    if choice < 3:
                        response = "Ok, let's try a different one. Tell me about another movie you've seen."
                    else:
                        response = "Huggle the house elves still can't find that. Try a different film that we would actually have..."
                    self.mode = "asking"
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
        res = re.findall(r'\"[^\"]+\"', preprocessed_input)
        if len(res) == 0:
        # regular expression pattern for matching movie titles without quotes
            pattern = r'\b(' + '|'.join(self.titles_no_year) + r')\b'
            res = re.findall(pattern, preprocessed_input.lower())
            result = []
            for s in res:
                result.append(string.capwords(s.lower()))
        else:
            result = []
            for s in res:
                result.append(string.capwords(s[1:-1].lower()))
        return result
            

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
        if self.creative:
            title = string.capwords(title.lower())
        matches = []
        for i in range(len(self.titles)):
            movie_title = re.sub(r'\([^)]*\)', '', self.titles[i][0]).strip()
            year_match = re.search(r"\((\d{4})\)$", self.titles[i][0])
            if year_match:
                year = year_match.group(1)
            words = movie_title.split()
            if len(words) > 1 and words[0] in ['The', 'A', 'An']:
                movie_title = ' '.join(words[1:]) + ', ' + words[0]
            else:
                movie_title = ' '.join(words)
            given_title = re.sub(r'\([^)]*\)', '', title).strip()
            year_match2 = re.search(r"\((\d{4})\)$", title)
            if year_match2:
                year2 = year_match2.group(1)
            given_title = re.sub(r'\(\d{4}\)', '', given_title).strip()
            words2 = given_title.split()
            if len(words2) > 1 and words2[0] in ['The', 'A', 'An']:
                given_title = ' '.join(words2[1:]) + ', ' + words2[0]
            else:
                given_title = ' '.join(words2)
            if year_match2:
                year2 = year_match2.group(1)
                given_title = given_title + " " + year2
                movie_title = movie_title + " " + year
            if given_title == movie_title:
                matches.append(i)
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
        if not self.creative:
            without_title = re.sub(r"\"[\w\s\)\()]+\"", "", preprocessed_input)
            splitted = without_title.split()
            splitted = [self.stemmer.stem(word) for word in splitted]
            '''
            Return 2 if we detect that the user is angry, 3 if the user is afraid,
            4 if the user is disgusted, and 5 if the user is lustful, which we will
            handle as the user being confused.
            ''' 

            for i in self.anger_words:
                if i in splitted:
                    return 2
            for i in self.fear_words:
                if i in splitted:
                    return 3
            for i in self.disgust_words:
                if i in splitted:
                    return 4
            for i in self.lust_words:
                if i in splitted:
                    return 5
            pos_words = 0
            neg_words = 0
            for i, stemmed in enumerate(splitted):
                if stemmed in self.sentiment:
                    if self.sentiment[stemmed] == "pos":
                        if (splitted[i-1] == "didn't" or (i-2 >= 0 and splitted[i-2] == "didn't")) or (splitted[i-1] == "never" or (i-2 >= 0 and splitted[i-2] == "never")) or (splitted[i-1] == "not" or (i-2 >= 0 and splitted[i-2] == "not")):
                            neg_words += 1
                        else:
                            pos_words += 1
                    elif self.sentiment[stemmed] == "neg":
                        neg_words += 1
            if pos_words > neg_words:
                return 1
            elif neg_words > pos_words:
                return -1
            else:
                return 0
        else:
            without_title = re.sub(r"\"[\w\s\)\()]+\"", "", preprocessed_input)
            splitted = without_title.split()
            splitted = [self.stemmer.stem(word) for word in splitted]
            pos_words = 0
            neg_words = 0
            for i, stemmed in enumerate(splitted):
                if stemmed in self.sentiment:
                    if self.sentiment[stemmed] == "pos":
                        if (splitted[i-1] == "didn't" or (i-2 >= 0 and splitted[i-2] == "didn't")) or (splitted[i-1] == "never" or (i-2 >= 0 and splitted[i-2] == "never")) or (splitted[i-1] == "not" or (i-2 >= 0 and splitted[i-2] == "not")):
                            neg_words += 1
                        else:
                            pos_words += 1
                    elif self.sentiment[stemmed] == "neg":
                        neg_words += 1
            if pos_words > neg_words:
                return 1
            elif neg_words > pos_words:
                return -1
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
        return []
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
        matches = []
        min_dist = 100000
        idxs = []
        for i in range(len(self.titles)):
            movie_title = re.sub(r'\([^)]*\)', '', self.titles[i][0]).strip()
            dist = self.edit_distance(title.lower(), movie_title.lower())
            if dist < min_dist:
                min_dist = dist
            if dist <= max_distance:
                matches.append((i,dist))
        for idx, dist in matches:
            if dist == min_dist:
                idxs.append(idx)
        return idxs

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
        res = []
        for i in candidates:
            title = self.titles[i][0]
            if not clarification.isnumeric():
                if clarification in title:
                    res.append(i)
            else:
                if len(clarification) == 4:
                    if clarification in title:
                        res.append(i)
                else:
                    movie_title = re.sub(r'\([^)]*\)', '', self.titles[i][0]).strip()
                    if clarification in movie_title:
                        res.append(i)
        return res

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
        binarized = np.array(ratings)
        binarized[(binarized <= threshold)&(binarized != 0)] = -1
        binarized[binarized > threshold] = 1
        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        return binarized

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
        cosine_sim = np.dot(u,v)/(np.linalg.norm(u)*np.linalg.norm(v))
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
        scores = np.zeros(len(user_ratings))
        if creative == False:
            for i in range(len(user_ratings)):
                if user_ratings[i] == 0:
                    score = 0
                    ratings_i = ratings_matrix[i]
                    for j in range(len(user_ratings)):
                        if user_ratings[j] == 0:
                            continue
                        cosine_sim = 0
                        ratings_j = ratings_matrix[j]
                        i_norm = np.linalg.norm(ratings_i)
                        j_norm = np.linalg.norm(ratings_j)
                        if i_norm == 0 or j_norm == 0:
                            cosine_sim = 0
                        else:
                            cosine_sim = np.dot(ratings_i, ratings_j)/(i_norm*j_norm)
                        score += cosine_sim * user_ratings[j]
                    scores[i]=score
            index_of_scores = list(enumerate(scores))
            sorted_scores = sorted(index_of_scores, key=lambda x: x[1], reverse=True)
            sorted_indexes = [i for i, score in sorted_scores[:k]]

        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        return sorted_indexes

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

        if not self.creative:
            return """
        Hey there! I'm here to help you find some movies to watch based
        on your preferences. Give me some info on your favorite (or not so
        favorite) movies and I'll give you a couple of recs at the end. If
        the movie doesn't pop up when you type it, try putting it in quotes
        to see if I can understand you better. 
        """
        else:
            return """
        Greetings Muggle! I'm Draco Malfoy. I'm here with my house elves waiting to search 
        the Hogwarts library and my Father's private collection for some movies to watch based
        on your preferences. Give me info on your favorite (or not so
        favorite) movies and I'll give you the recommendations that my house elves find. If
        the movie doesn't pop up when you type it then you have failed Muggle, try putting it in quotes
        to see if I can understand you better. 
        
        """
    
    #This function for calculating edit distance was adapted from one by https://python-course.eu/applications-python/levenshtein-distance.php
    def edit_distance(self, s, t, costs=(1, 1, 2)):
        rows = len(s)+1
        cols = len(t)+1
        deletes, inserts, substitutes = costs
        
        dist = [[0 for x in range(cols)] for x in range(rows)]

        # source prefixes can be transformed into empty strings 
        # by deletions:
        for row in range(1, rows):
            dist[row][0] = row * deletes

        # target prefixes can be created from an empty source string
        # by inserting the characters
        for col in range(1, cols):
            dist[0][col] = col * inserts
            
        for col in range(1, cols):
            for row in range(1, rows):
                if s[row-1] == t[col-1]:
                    cost = 0
                else:
                    cost = substitutes
                dist[row][col] = min(dist[row-1][col] + deletes,
                                    dist[row][col-1] + inserts,
                                    dist[row-1][col-1] + cost) # substitution
        
    
        return dist[row][col]


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
