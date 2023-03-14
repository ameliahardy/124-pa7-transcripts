# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import re
import heapq
import numpy as np
import random

import re
from nltk.stem import PorterStemmer
import random


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'JILF_bot'

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
        self.user_ratings = np.zeros((ratings.shape[0], 1))
        self.movies_seen = 0 # num of movies user tells us they have seen 
        self.negations = ["not", "don't", "dislike", "didn't", "never", "won't"]     # list of words that are negations
        self.positives = ["liked", "enjoyed"]
        self.negatives = ["disliked", "didn't like"]
        self.starts = ["Thank you for telling me", "I understand that", "I see that"]
        self.ends = ["Tell me about more movies you've watched! At least 5 so that I can make a recommendation!", "What are some other movies you've seen?", "What about other movies?"]
        self.last_recommended = -1
        self.already_seen = []
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

        greeting_message = "Hello. My name is JILF. I'll help you pick a movie today. If you ever want to leave, just type :quit \n But now, let's find a movie for you. To do so, tell me about movies and TV shows you have seen before and whether you liked them. \n Make sure to put the movie name between quotes. For example, you could say: I hated \"Titanic\" \n Oh, and lastly, just one movie please. Don't say: I loved \"Titanic\" and \"Avatar\""


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

        goodbye_message = "It was an honor to be of service. Enjoy the movie!"

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
            response = ""
            text = self.preprocess(line)
            if line == "yes":
                recommendation = self.recommend(self.user_ratings, self.ratings)
                response = "i would def go for " + self.titles[recommendation[0]][0]
                response += "but i have so many more recommendations!! ahhh do you want another one? just say 'yes' or 'no'"
                return response
            elif line == "no":
                response = "okayyy. I loved helping you pick a new movie fav hehe"
                return response
            titles = self.extract_titles(text)
            if len(titles) == 0:
                # handle arbitrary input

                # check for "Can you" or "Could you"

                if "Can you" in line or "Could you" in line or "could you" in line or "can you" in line:
                    response = "i CAN recommend movies to you! LET'S TALK MOVIES. "
                    response += "okay what have you watched before?"
                    return response
                
                elif "What" in line or "what" in line:
                    response = "excuse me. when you say - " + line + " - i don't like it. "
                    response += "why not just talk about movies. i love movies. "
                    return response

                elif "Why" in line or "why" in line:
                    response = "hmm... " + line + " is a good question. "
                    response += "why... not just talk about movies though lol."
                    return response

                elif "How" in line or "how" in line:
                    response = "hmm... " + line + " is a good question. "
                    response += "a better questions is: how did we get here though? MOVIE TIME. TELL ME MORE."
                    return response

                elif "When" in line or "when" in line:
                    response = "more like when will you talk to me about MOVIES!!! "
                    return response

                emotions = {'angry': (['angry', 'mad', 'annoyed', 'frustrated', 'upset', 'irritated'], "hey hey, I understand that you're ###, but i'm trying my best. take a deeeeeeep breath. let's start again :D."),
                            'sad': (['sad', 'depressed', 'lonely', 'unhappy', 'grieving'], "oh no i'm so sorry that you're ###. maybe a movie will cheer you up hehe. talk to me."),
                            'happy': (['happy', 'excited', 'joyful', 'cheerful', 'thrilled'], "i'm soooo happy to hear that you're ###. LET'S CELEBRATE... with a movie!!!!"),
                            'surprised': (['surprised', 'shocked', 'astonished', 'amazed', 'dumbfounded', 'dumbstruck'], "you know, i was also ### when i first talked to myself *hairflip*. i can do so much more for you. hint: moviesssss."),
                            'disgusted': (['disgusted', 'revolted', 'repulsed', 'appalled', 'repelled', 'repugnant', 'repulsive', 'repugnance', 'repugnancy', 'repugnant'], "feeling ### is the WORST. maybe a movie will help you feel better :)."),
                            'afraid': (['afraid', 'scared', 'terrified', 'frightened', 'petrified', 'alarmed'], "i'm sure everything will be okay. Don't be ###. here, talk to me about a movie and distract yourself."),
                            'neutral': (['neutral', 'indifferent', 'uninterested', 'bored', 'unimpressed', 'unexcited', 'unmoved'], "you're so boring. what are you doing feeling ###? talk to me about a movie instead ;)"),
                            'nervous': (['nervous', 'anxious', 'tense', 'uneasy', 'jittery', 'jumpy'], "Don't be ###. i'm only here to help you :(. let's start talking and i'm sure you'll feel more comfortable hehe.")
                            }

                for emotion in emotions.keys():
                    for word in emotions[emotion][0]:
                        if word in line:
                            response = emotions[emotion][1].replace("###", word)
                            return response

                # else get sentiment
                sentiment = self.extract_sentiment(text)
                sentiment_str = "positive" if sentiment == 1 else "negative"
                response = "listen. i understand that you're feeling " + sentiment_str + ". "
                response += "but, pleaseeeee, tell me about any movie you have watched."
                
            else:
                sentiment = self.extract_sentiment(text)
                if len(titles) > 1:
                    response = "okay okay hold up there. one movie at a time!!!"
                else:
                    title = titles[0]
                    indices = self.find_movies_by_title(title)
                    if len(indices) == 0: 
                        response = "wow, i'm impressed. even i don't know of a movie called "
                        response += '"' + title + '" !'
                        return response
                    elif len(indices) > 1:
                        response = "look at that. i found more than one movie with that title!! can you clarify? which one of these did you mean?: "
                        response += ", ".join([self.titles[index][0] for index in indices])
                        return response
                    else:
                        self.user_ratings[indices[0]][0] = sentiment
                        self.movies_seen += 1
                if self.movies_seen >= 5:   # make sure we have enough to find top k movies
                    recommend = self.recommend(self.user_ratings, self.ratings)
                    response = "FINALLY! i've learned enough about your taste in movies hehe. "
                    response += "i would recommend watching"
                    response += " " + self.titles[recommend[0]][0]
                    response += ". but there are more!! Type 'yes' or 'no' if wanna hear about them!"
                    return response
                else:
                    if sentiment == 1:
                        answer = random.randint(0, 3)
                        if answer == 0:
                            response = "thank you for telling me you liked"
                        if answer == 1:
                            response = "I gather you enjoyed"
                        else:
                            response = "great! thanks for letting me know you appreciated watching"
                    elif sentiment == 0:
                        answer = random.randint(0, 3)
                        if answer == 0:
                            response = "thank you for telling me you were neutral about"
                        if answer == 1:
                            response = "I didn't gather whether you enjoyed"
                        else:
                            response = "thanks for letting me know you didn't have an opinion on"
                    else:
                        answer = random.randint(0, 3)
                        if answer == 0:
                            response = "thank you for telling me you didn't like"
                        if answer == 1:
                            response = "I gather you weren't pleased by"
                        else:
                            response = "thanks for letting me know you didn't enjoy watching"
                    for title in titles:
                        response += ' "' + title + '"'
                    response += "! now talk to me about more movies you've watched :)"
                    return response
        else:
            text = self.preprocess(line)
            if line == "yes":
                print("Generating your recommendation, please standby... (this can take a minute)")
                recommendation = self.recommend(self.user_ratings, self.ratings)
                self.last_recommended += 1
                response = "I recommend watching " + '"' + self.titles[recommendation[self.last_recommended]][0] + '"'
                response += " Would you like another one? Type 'yes' or 'no' (':quit' to exit the program)"
                response += "\n Feel free to tell me about another movie and I'll give you another recommendation if you do!"
                return response
            elif line == "no":
                response = "Thank you for allowing me to help you pick a movie to watch! (':quit' to exit the program)"
                return response
            titles = self.extract_titles(line)
            if len(titles) == 0:
                response = "Please tell me a movie that you have seen! \n"
                response += 'Please put quotations around the title! (ex. "Move Title")'
            else:
                sentiment = self.extract_sentiment(text)
                if len(titles) > 1:
                    response = "Please tell me one movie at a time!"
                    return response
                else:
                    title = titles[0]
                    if title in self.already_seen:
                        response = "You already told me about that movie, tell me about another one!"
                        return response
                    
                    indices = self.find_movies_by_title(title)
                    if len(indices) == 0:
                        answer = random.randint(0, 2)
                        if answer == 0:
                            response = "I have sadly never heard of"
                        else:
                            response = "Sorry, I do not know of a movie called "

                        response += '"' + title + '"! Please tell me about another movie!'
                        return response
                    elif len(indices) > 1:
                        response = "I found more than one movie with that title, can you please clarify?"
                        response += "\nIf there are different versions of the movie, please specify "

                        response += 'which one you have seen by including the year like\n this: "Movie Title (1247)".'
                        response += " Where 1247 would be the year the movie was made. Go ahead!"

                        return response
                    else:
                        if sentiment != 0:
                            self.user_ratings[indices[0]][0] = sentiment
                            self.movies_seen += 1
                if self.movies_seen >= 5:   # make sure we have enough to find top k movies
                    if self.last_recommended == -1:
                        print("The movies you have told me about are enough for me to make a recommendation.")
                    print("Generating your recommendation, please standby... (sorry for the wait!)")
                    recommend = self.recommend(self.user_ratings, self.ratings)
                    response = "Based on movies you've seen, you'd probably like " + '"'
                    self.last_recommended += 1
                    response += self.titles[recommend[self.last_recommended]][0]
                    response += '"' + "! Would you like another recommendation? Type 'yes' or 'no'! (':quit' to exit the program)"
                    response += "\nOr you could also keep telling me about more movies so that I can recommend another!"
                else:
                    start_sentence = self.starts[random.randrange(0, len(self.starts) - 1)]
                    if sentiment == 1:
                        positive_word = self.positives[random.randrange(0, len(self.positives) - 1)]
                        response = start_sentence + " you " + positive_word + ' "'
                    elif sentiment == 0:
                        response = "I'm not sure how you feel about that movie, can you tell me more?"
                        return response
                    else:
                        negative_word = self.negatives[random.randrange(0, len(self.negatives) - 1)]
                        response = start_sentence + " you " + negative_word + ' "'
                    response += titles[0] + '"' + "! " + self.ends[random.randrange(0, len(self.ends) - 1)]
                    self.already_seen.append(titles[0])
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

    def extract_titles(self, unprocessed_input, force_starter=False):
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

        unprocessed_input = ''.join(unprocessed_input)

        # CAREFUL, IN PROCESS FEED IN UNPROCESSED INPUT, NOT PRE-PROCESSED!
        unprocessed_input = unprocessed_input.strip()

        titles_list = []
        if not self.creative or self.creative and force_starter:

            # In non-creative mode, check if string contains exactly two ""
            # @TEAM: do we need to output an error code or print something if not?!
            one_string_pattern = '".*?"'
            if len(re.findall(one_string_pattern, unprocessed_input)) >= 1:

                # Extract Movie title
                movie_title_pattern = '"[^"]+"'
                result = re.findall(movie_title_pattern, unprocessed_input)

                if len(result) == 0:
                    return titles_list
                else:
                    titles_list = [s[1:-1] for s in result]
                    return titles_list

        # @TEAM: Implement creative mode here
        else:
            input_list = unprocessed_input.split()
            for i in range(len(input_list)):
                for j in range(1, min(10, len(input_list) + 1 - i)):
                    possible_title = " ".join(input_list[i:i+j])
                    possible_title = "".join(c for c in possible_title if c not in '\"\',!?.')
                    possible_title = possible_title.title()
                    if len(self.find_movies_by_title(possible_title, force_starter=True)) > 0:
                        if possible_title not in titles_list:
                            titles_list.append(possible_title)
            return titles_list

        return titles_list

    def find_movies_by_title(self, title, force_starter=False):
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

        ##################
        if not self.creative or self.creative and force_starter:
            # FIRST: PROCESS AND REMOVE YEAR, IF PRESENT

            # Identify last word in string "title"
            words_in_title = title.split()
            last_word_in_title = words_in_title[-1]

            # If last word is a year, exclude it from string but save the year separately
            year = None

            # Find out if the last word is a year
            year_match = re.findall('[0-9]{4}', last_word_in_title)
            if len(year_match) == 1:
                year = year_match[0]
                words_in_title = words_in_title[:-1]

            # Reconstruct the title without the year and return it as a string
            title = " ".join(words_in_title)

            ##################
            # SECOND: REMOVE ARTICLES if title starts with an article

            articles = ['a', 'an', 'the', 'A', 'An', 'The', 'AN', 'THE']
            words_in_title = title.split()

            if words_in_title[0] in articles:
                article = words_in_title[0]
                words_in_title[-1] = words_in_title[-1] + ','
                title = ' '.join(words_in_title[1:] + [article])


            ##################
            # THIRD: Now search through movie database.
            # Split title into words
            words_in_title = title.split()
            index_of_match = []

            for i, db_movie_title in enumerate(self.titles):

                # Split titles in database into words
                words_in_db_movie_title = db_movie_title[0].split()
                # print(words_in_db_movie_title)

                match = True
                # Here, compare if it is a match.
                for j in range(len(words_in_title)):
                    if words_in_title[j] != words_in_db_movie_title[j]:
                        match = False
                        break

                # Ensure that e.g. search for "Scream" doesn't return "Scream for Me (1999)"
                if len(words_in_db_movie_title) > len(words_in_title):
                    if not words_in_db_movie_title[len(words_in_title)].startswith('('):
                        match = False

                if match:
                    index_of_match.append(i)

            ##################
            # FOURTH: Now compare years against input

            if year is None:
                return index_of_match

            if len(index_of_match) == 0:
                return index_of_match

            index_year_matches_too = []

            # check each potential element given our list of movie indexes with a matching title
            for i in range(len(index_of_match)):
                movie_at_index = index_of_match[i]

                # movie title and year as extracted from database
                title = self.titles[movie_at_index][0]
                year_form = 0  # single year, 1 is start but no end date, 2 is start and end date
                # db_year = re.findall(r'\(\d{4}(\-\d{4})?\)', title)
                db_year = re.search(r'\(\d{4}(\-)?(\d{4})?\)', title)
                # db_year = re.findall('\([0-9]{4}\)', title)
                db_year = db_year[0]

                if db_year:
                    db_year = db_year.strip('()')

                    year_form = 1 if db_year.endswith('-') else 2 if '-' in db_year else 0
                    # year_form = 2 if '-' in db_year else 1 if db_year.endswith('-') else 0

                match = False

                if year_form == 0 and year == db_year:
                    match = True

                elif year_form == 1:
                    from_year = db_year.split('-')
                    if year >= from_year[0]:
                        match = True

                elif year_form == 2:
                    from_year, to_year = db_year.split('-')
                    if from_year <= year <= to_year:
                        match = True

                if match:
                    index_year_matches_too.append(index_of_match[i])

            return index_year_matches_too

        else:
            # FIRST: PROCESS AND REMOVE YEAR, IF PRESENT

            # Identify last word in string "title"
            words_in_title = title.title().split()
            last_word_in_title = words_in_title[-1]

            # If last word is a year, exclude it from string but save the year separately
            year = None

            # Find out if the last word is a year
            year_match = re.findall('[0-9]{4}', last_word_in_title)
            if len(year_match) == 1:
                year = year_match[0]
                words_in_title = words_in_title[:-1]

            # Reconstruct the title without the year and return it as a string
            title = " ".join(words_in_title)

            ##################
            # SECOND: REMOVE ARTICLES if title starts with an article

            articles = ['a', 'an', 'the', 'A', 'An', 'The', 'AN', 'THE']
            words_in_title = title.title().split()

            if words_in_title[0] in articles:
                article = words_in_title[0]
                words_in_title[-1] = words_in_title[-1] + ','
                title = ' '.join(words_in_title[1:] + [article])

            ##################
            # THIRD: Now search through movie database.
            # Split title into words
            words_in_title = title.title().split()
            index_of_match = []

            for i, db_movie_title in enumerate(self.titles):

                # Split titles in database into words
                words_in_db_movie_title = db_movie_title[0].split()
                # print(words_in_db_movie_title)

                match = True
                # Here, compare if it is a match.
                for j in range(len(words_in_title)):
                    if words_in_title[j].lower() != ''.join(c for c in words_in_db_movie_title[j] if c not in '\'\".!:?').lower():
                        match = False
                        break

                curtitle = " ".join(words_in_db_movie_title)
                if not match and '(' in curtitle:
                    alt_name = curtitle[curtitle.index('(') + 1:curtitle.index(')')]
                    found_alt_match = True
                    for j in range(len(words_in_title)):
                        if words_in_title[j].lower() not in alt_name.lower():
                            found_alt_match = False
                            break
                    match = found_alt_match

                if match:
                    index_of_match.append(i)

            ##################
            # FOURTH: Now compare years against input

            if year is None:
                return index_of_match

            if len(index_of_match) == 0:
                return index_of_match

            index_year_matches_too = []

            # check each potential element given our list of movie indexes with a matching title
            for i in range(len(index_of_match)):
                movie_at_index = index_of_match[i]

                # movie title and year as extracted from database
                title = self.titles[movie_at_index][0]
                year_form = 0  # single year, 1 is start but no end date, 2 is start and end date
                # db_year = re.findall(r'\(\d{4}(\-\d{4})?\)', title)
                db_year = re.search(r'\(\d{4}(\-)?(\d{4})?\)', title.title())
                # db_year = re.findall('\([0-9]{4}\)', title)
                db_year = db_year[0]

                if db_year:
                    db_year = db_year.strip('()')

                    year_form = 1 if db_year.endswith('-') else 2 if '-' in db_year else 0
                    # year_form = 2 if '-' in db_year else 1 if db_year.endswith('-') else 0

                match = False

                if year_form == 0 and year == db_year:
                    match = True

                elif year_form == 1:
                    from_year = db_year.split('-')
                    if year >= from_year[0]:
                        match = True

                elif year_form == 2:
                    from_year, to_year = db_year.split('-')
                    if from_year <= year <= to_year:
                        match = True

                if match:
                    index_year_matches_too.append(index_of_match[i])

            return index_year_matches_too

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
        processed_text = []
        words = preprocessed_input.split()
        title = False
        for word in words:
            if word[0] == '"':
                title = True
            if not title:
                stemmed_word = p.stem(word)
                processed_text.append(stemmed_word)   
            if word[-1] == '"':
                title = False

        sentiment = 0
        last_sentiment = ""
        for word in processed_text:
            if word in self.sentiment:
                if self.sentiment[word] == "pos":
                    sentiment_val = 1
                    last_sentiment = "pos"
                else:
                    sentiment_val = -1
                    last_sentiment = "neg"
                sentiment += sentiment_val
            elif word in self.negations:
                sentiment_val = -3      # negations weigh more negative
                sentiment += sentiment_val
        if sentiment > 0: sentiment = 1 
        elif sentiment < 0: sentiment = -1
        # If sentiments cancelled each other out (sentiment==0), take the last sentiment
        elif last_sentiment == "pos": sentiment = 1
        elif last_sentiment == "neg": sentiment = -1
        return sentiment

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
        # if there are multiple movies, split the input into multiple inputs
        # and call extract_sentiment_for_movies on each of them
        # if the inputs are separated by "and" or "or", then the sentiment is the same
        # if the inputs are separated by "but", then the sentiment is opposite

        separators = ["and", "or"]
        opposites = ["but"]

        list_of_tuples = []

        # check if there are multiple movies using extract_titles
        titles = self.extract_titles(preprocessed_input, force_starter=True)
        if len(titles) == 0:
            return []
        if len(titles) == 1:
            return [(titles[0], self.extract_sentiment(preprocessed_input))]
        else:
            new_input = preprocessed_input.split()
            # turn new_input into a list of words
            
            for i in range(len(new_input)):
                if new_input[i] in separators:
                    list_of_tuples.append((titles[0], self.extract_sentiment(preprocessed_input)))
                    list_of_tuples.append((titles[1], self.extract_sentiment(preprocessed_input)))
                elif new_input[i] in opposites:
                    list_of_tuples.append((titles[0], self.extract_sentiment(" ".join(new_input[:i]))))
                    list_of_tuples.append((titles[1], self.extract_sentiment(" ".join(new_input[i+1:]))))
        # return a list of tuples, where the first item in the tuple is a movie title, and the second is the sentiment in the text toward that movie
        return list_of_tuples


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

        # define a function to get the movie title from the database as one string
        def get_title(i, self):
            # Identify last word in string "title"
            words_in_title = self.titles[i][0].split()
            last_word_in_title = words_in_title[-1]

            # If last word is a year, exclude it from string but save the year separately
            # year = None

            # Find out if the last word is a year
            year_match = re.findall('[0-9]{4}', last_word_in_title)
            if len(year_match) == 1:
                # year = year_match[0]
                words_in_title = words_in_title[:-1]

            # Reconstruct the title without the year and return it as a string
            title = "_".join(words_in_title)
            return title
        
        def turn_title_into_string(title):
            # Identify last word in string "title"
            words_in_title = title.split()
            last_word_in_title = words_in_title[-1]

            # If last word is a year, exclude it from string but save the year separately
            # year = None

            # Find out if the last word is a year
            year_match = re.findall('[0-9]{4}', last_word_in_title)
            if len(year_match) == 1:
                # year = year_match[0]
                words_in_title = words_in_title[:-1]

            # Reconstruct the title without the year and return it as a string
            title = "_".join(words_in_title)
            return title
        

        # compute edit distance between title and all movie titles
        def levenshtein_distance(s1, s2):
            
            # lower case the title
            s1 = s1.lower()
            s2 = s2.lower()
            
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)

            # len(s1) >= len(s2)
            if len(s2) == 0:
                return len(s1)

            # initialize previous row
            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                # calculate current row distances from previous row
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2) 
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row

            return previous_row[-1]


        # # lowercase the title
        # title = title.lower()

        # turn the title into a string
        title = turn_title_into_string(title)


        # find the movies with an edit distance of max_distance or less
        index_matches = []
        for i, movie in enumerate(self.titles):
            
            # get string from self.titles
            movie = get_title(i, self)

            # # lowercase the movie title
            # movie = movie.lower()

            # if movie is empty, skip it
            if movie == "":
                continue
            
            # if title is only two letters, reduce max_distance to 1
            if len(title) <= 2:
                max_distance = 1

            # if the edit distance is less than or equal to max_distance and has at least two letters in common, add the index to the list
            if levenshtein_distance(title, movie) <= max_distance:
                index_matches.append(i)


        # if there are no matches, return an empty list
        if len(index_matches) == 0:
            return []
        
        # if there is only one match, return a list with that index
        elif len(index_matches) == 1:
            return index_matches
        
        # if there are multiple matches, find the closest ones
        else:
            closest = []
            min_dist = 1000
            for i in index_matches:
                dist = levenshtein_distance(title, get_title(i, self))
                if dist < min_dist:
                    min_dist = dist
                    closest = [i]
                elif dist == min_dist:
                    closest.append(i)
            return closest
        

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
        # create a list of strings of the candidates
        candidate_titles = []
        for i in candidates:
            candidate_titles.append(self.titles[i][0])

        # if the clarification is a year, return the movie with that year
        if len(clarification) == 4 and clarification.isdigit():
            for i, title in enumerate(candidate_titles):
                if clarification in title:
                    return [candidates[i]]

        elif clarification.isdigit():
            return [candidates[int(clarification) - 1]]

        # if the clarification is a word, return the movie with that word
        else:
            for i, title in enumerate(candidate_titles):
                if clarification in title:
                    return [candidates[i]]
                else:
                    return candidates

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
        binarized_ratings = np.array(ratings)
        for i in range(len(binarized_ratings)):
            for j in range(len(binarized_ratings[i])):
                if binarized_ratings[i][j] > threshold:
                    binarized_ratings[i][j] = 1
                elif binarized_ratings[i][j] == 0:    # Keep null values as 0
                    continue 
                else:       # the rating is less than threshold
                    binarized_ratings[i][j] = -1

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
        # a [a> 0] = 2* a
        # u[u != 0] = 1/u
        # v[v != 0] = 1/v
        zero_divide = False
        if (u == 0).all():
            zero_divide = True
        if (v == 0).all():
            zero_divide = True

        similarity = 0
        if not zero_divide:
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
        recommendations = []
        ordered_heap = []
        matrix_dimensions = ratings_matrix.shape

        # Populate this list with k movie indices to recommend to the user.
        zero_rated = 0
        heapq.heapify(ordered_heap)

        for index, rating in enumerate(user_ratings):
            if rating == zero_rated:
                scores = []
                rating_updated = 0
                for index2 in range(matrix_dimensions[0]):
                    if not user_ratings[index2] == zero_rated:
                        if not index == index2:
                            similarity = self.similarity(ratings_matrix[index2], ratings_matrix[index])
                            if similarity:
                                rating_updated += (similarity * user_ratings[index2])
                # scores.append((new_rating, i))
                sort_by_lowest = (-1)*rating_updated
                # this uses the first element of the tuple for sorting
                heapq.heappush(ordered_heap, (sort_by_lowest, scores, index, index2))

        # # Sort the movies by recommendation score and take the top k
        # scores_sorted = sorted(scores, key=lambda x: x[0], reverse=True)
        # print(scores_sorted)
        #
        # for i in range(k):
        #     recommendations.append(scores_sorted[i][1])

        while len(ordered_heap) > 0 and 0 < k:
            # Pop the smallest element from ordered_heap and retrieve the index
            smallest_element = heapq.heappop(ordered_heap)
            index = smallest_element[2]
            # Append the index to the recommendations list
            recommendations.append(index)
            k -= 1

        # if recommendations == recommendations1:
        #    print("equal")
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
        return "Hello! I will recommend a movie for you that I think you'll like! To get started, tell me about some movies that you've seen!"


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
