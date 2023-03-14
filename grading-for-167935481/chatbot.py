# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import itertools
import os
import signal
import sys
import time

import util

import numpy as np
import re
import porter_stemmer
import random


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        self.name = 'motbot'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.supersentiment = util.load_sentiment_dictionary('deps/fgsentiment.txt')
        # p = porter_stemmer.PorterStemmer()
        # for word in self.sentiment:
        #     clean = p.stem(word)
        #     print(clean + "," + self.sentiment[word])

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings)
        self.rec_count = 0
        self.given_movies_count = 0
        self.user_rs = np.zeros(len(self.ratings))
        self.top_recs = []
        self.added_words = [" Slayyy!", " Yassss!", " Queen!", " Mmm yuh...", " Big slay...", " (That's questionable :| )",
                            " If that floats your boat!"]
        self.add = ""
        self.emotions = ["anger", "fear", "happi", "disgust", "sad", "surpris", "angry", "angri", "mad", "depress",
                         "ecstat", "furiou", "silli", "annoi", "worri", "fear", "optimist", "hope", "jubil", "anxiou",
                         "stress"]
        self.clarify = (False, "", "", [])

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

        greeting_message = "Hi! What movie would you like to talk about?"

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

        goodbye_message = "Byeeeeeee bestie!"

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
        line = line.strip()
        if self.creative:
            self.add = random.choice(self.added_words)
            # print(self.given_movies_count, self.clarify[0])
            if self.given_movies_count < 4 or self.clarify[0]:
                if self.clarify[0]:
                    old_title = self.clarify[1]
                    poss_indices = self.clarify[3]
                    old_line = self.clarify[2]
                    self.clarify = (False, "", "", [])
                    titles = self.extract_titles(line)
                    if len(titles) == 0:
                        return "Girl, you gave me no continuing movie title. Let's start over and give me the full movie name this time."
                    elif len(titles) > 1:
                        # IF WE WANT TO PROCESS SENTIMENT OF MULTIPLE MOVIES
                        if self.creative:
                            # get the sentiments of all the movies the user listed
                            all_sentiments = self.extract_sentiment_for_movies(line)
                            response = "Bestie that's a lot of tea. One sec . . . so, you "
                            for i in range(len(all_sentiments)):
                                # the movie we're looking at this iteration
                                one_movie = all_sentiments[i]
                                # craft response based on the sentiment assigned to that movie
                                if one_movie[1] == 0:
                                    response += "felt neutrally about "
                                    response += str(one_movie[0])
                                elif one_movie[1] == 1:
                                    response += "liked "
                                elif one_movie[1] == 2:
                                    response += "really liked "
                                    response += str(one_movie[0])
                                elif one_movie[1] == -1:
                                    response += "disliked "
                                    response += str(one_movie[0])
                                else:
                                    response += "really disliked "
                                    response += str(one_movie[0])
                                # check how to end/continue the sentence
                                if i == len(all_sentiments) - 1:
                                    response += "! Tell me about a different movie."
                                else:
                                    response += ", and you "
                            return response
                        else:
                            return "Girl, you gave me too many continuing movie titles! Let's start over and give me the full movie name this time."
                    else:
                        clarify_title = titles[0].strip()
                        indices = self.disambiguate(clarify_title, poss_indices)
                        if len(indices) == 0:
                            return "TBH, I've never heard of movies that have " + old_title + " and " + clarify_title + ". Let's start over."
                        if len(indices) > 1:
                            return "Bestie there are so many movies that have " + old_title + " and " + clarify_title + "! You didn't clarify enough, let's start over."
                        index = indices[0]
                        self.given_movies_count += 1
                        line = self.preprocess(line)
                        sent = self.extract_sentiment(old_line + " " + line)
                        self.user_rs[index] = sent
                        response = "Ok, you "
                        if sent == 0:
                            return "Babe did you like " + self.titles[index][0] + " or not?? Tell me more about it."
                        elif sent == 1:
                            response += "liked "
                        elif sent == 2:
                            response += "really liked "
                        elif sent == -1:
                            response += "disliked "
                        else:
                            response += "really disliked "
                        response += self.titles[index][0]
                        response += "!" + self.add + " Tell me about a different movie."
                        return response
                og_line = line
                line2 = self.preprocess(line)
                titles = self.extract_titles(line2)
                if len(titles) == 0:
                    remove_title = re.compile(r'\"(.+?)\"')
                    review_without_quotes = re.sub(remove_title, '', line).lower()
                    processed_review_without_quotes = self.preprocess(review_without_quotes)
                    review_without_quotes = review_without_quotes.split()
                    processed_review_without_quotes = processed_review_without_quotes.split()
                    for wordi in range(len(processed_review_without_quotes)):
                        if processed_review_without_quotes[wordi] in self.emotions:
                            return "Oh bestie! Did I make you " + review_without_quotes[
                                wordi] + "?" + " Sorry for getting off track, let's go back to movies."
                    return "Ugh bae I must be having a bad day... " \
                           "That's not really what I want to talk about about right now, tell me about a " \
                           "specific movie using quotation marks around the title."
                self.add = random.choice(self.added_words)
                line = og_line

                line = self.preprocess(line)
                # print(line)
                titles = self.extract_titles(line)

                if len(titles) == 0:  # fail gracefully
                    return "Ugh bae I must be having a bad day... I can't tell if you gave me a movie title. Tell me about a " \
                           "specific movie using quotation marks around the title."
                if len(titles) > 1:
                    if not self.creative:
                        response = "Whoa whoa whoa, slow dowwwn, bestie. Can you give me one movie, so"
                        response += " or ".join(titles) + "?"
                        return response
                    if self.creative:
                        # IF WE WANT TO PROCESS SENTIMENT OF MULTIPLE MOVIES
                        # get the sentiments of all the movies the user listed
                        all_sentiments = self.extract_sentiment_for_movies(line)
                        response = "Bestie that's a lot of tea. One sec . . . so, you "
                        # print(all_sentiments)
                        for i in range(len(all_sentiments)):
                            # the movie we're looking at this iteration
                            one_movie = all_sentiments[i]
                            # print(one_movie)
                            # craft response based on the sentiment assigned to that movie
                            if one_movie[1] == 0:
                                response += "felt neutrally about "
                                response += str(one_movie[0])
                            elif one_movie[1] == 1:
                                response += "liked "
                                response += str(one_movie[0])
                            elif one_movie[1] == 2:
                                response += "really liked "
                                response += str(one_movie[0])
                            elif one_movie[1] == -1:
                                response += "disliked "
                                response += str(one_movie[0])
                            else:
                                response += "really disliked "
                                response += str(one_movie[0])
                            # check how to end/continue the sentence
                            if i == len(all_sentiments) - 1:
                                response += "! Tell me about a different movie."
                            else:
                                response += ", and you "
                        return response
                # user only gave us one title
                title = titles[0]
                sent = self.extract_sentiment(line)
                indices = self.find_movies_by_title(title)
                if len(indices) == 0:
                    return "TBH, I've never heard of " + title + ". Tell me about another movie."
                if len(indices) > 1:
                    self.clarify = (True, title, line, indices)
                    pos_titles = []
                    for i in indices:
                        pos_titles.append(self.titles[i][0])
                    pos_titles = " or ".join(pos_titles).strip()
                    return "Bestie there are so many movies called " + title + ". Can you give me one movie, so " \
                           + pos_titles + "? Clarify!"
                index = indices[0]
                self.given_movies_count += 1
                self.user_rs[index] = sent
                response = "Ok, you "
                if sent == 0:
                    return "Babe did you like " + self.titles[index][0] + " or not?? Tell me more about it."
                elif sent == 1:
                    response += "liked "
                else:
                    response += "disliked "
                response += self.titles[index][0]
                response += "!" + self.add + " Tell me about a different movie."
                return response
            else:
                self.clarify = (False, "", "", [])
                if self.rec_count % 10 == 0:
                    print("Ok! Based on these, let me think of a movie for you. Give me one sec...")
                    # Fire up a loading spinner
                    pid = os.fork()
                    if pid > 0:
                        # parent
                        self.top_recs = self.recommend(self.user_rs, self.ratings, self.rec_count + 10)
                        os.kill(pid, signal.SIGTERM)
                        sys.stdout.write('\b')

                    else:
                        # child
                        load_spinner = itertools.cycle(['-', '/', '|', '\\'])
                        while True:
                            sys.stdout.write(next(load_spinner))
                            time.sleep(.15)  # brief pause
                            sys.stdout.flush()  # clear
                            sys.stdout.write('\b')  # remove last
                if self.rec_count > 0 and line.lower() not in ["no", "nah", "yes", "ya", "yuh", "naur", "nope", "stop", "ok", "y", "n"]:
                    return "Girl!! You gotta give me a yes or a no."
                if self.rec_count > 0 and line.lower() in ["no", "nah", "naur", "nope", "stop", "n"]:
                    response = "Alright bestie boo! Tell me about a movie."
                    self.given_movies_count = 0
                    self.rec_count = 0
                    return response
                response = "I think you would love "
                response += self.titles[self.top_recs[self.rec_count]][0]
                response += "! You want some more recommendations? (respond yes/no)"
                self.rec_count += 1
                return response

        else:
            if self.given_movies_count < 4:
                line = self.preprocess(line)
                titles = self.extract_titles(line)

                if len(titles) == 0:  # fail gracefully
                    return "Ugh bae I must be having a bad day... I can't tell if you gave me a movie title. Tell me about a " \
                           "specific movie using quotation marks around the title."
                if len(titles) > 1:
                    return "Whoa whoa whoa, slow dowwwn, bestie. Tell me about one movie at a time."
                title = titles[0]
                sent = self.extract_sentiment(line)
                indices = self.find_movies_by_title(title)
                print(indices)
                if len(indices) == 0:
                    return "TBH, I've never heard of " + title + ". Tell me about another movie."
                if len(indices) > 1:
                    return "Bestie there are so many movies called " + title + ". Clarify!"
                index = indices[0]
                self.given_movies_count += 1
                self.user_rs[index] = sent
                response = "Ok, you "
                if sent == 0:
                    return "Babe did you like " + title + " or not?? Tell me more about it."
                elif sent == 1:
                    response += "liked "
                else:
                    response += "disliked "
                response += title + "! Tell me about a different movie."
            else:
                if self.rec_count % 10 == 0:
                    print("Ok! Let me generate some, give me one sec...")
                    self.top_recs = self.recommend(self.user_rs, self.ratings, self.rec_count + 10)
                if line.lower() not in ["no", "nah", "yes", "ya", "yuh", "naur", "nope", "stop", "ok", "y", "n"]:
                    return "Girl!! You gotta give me a yes or a no."
                if self.rec_count > 0 and line.lower() in ["no", "nah", "naur", "nope", "stop", "n"]:
                    response = "Alright bestie boo! Tell me about a movie."
                    self.given_movies_count = 0
                    self.rec_count = 0
                    return response
                response = "I think you would love "
                response += self.titles[self.top_recs[self.rec_count]][0]
                response += "! You want some more recommendations? (respond yes or no)"
                self.rec_count += 1

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
        p = porter_stemmer.PorterStemmer()

        right_titles = re.findall(r'"(.*?)"', text)
        words = text.split()
        cleaned_line = []
        for word in words:
            cleaned_word = p.stem(word)
            cleaned_line.append(cleaned_word)
        cleaned_line = " ".join(cleaned_line)

        wrong_titles = re.findall(r'"(.*?)"', cleaned_line)

        for i in range(len(wrong_titles)):
            cleaned_line = cleaned_line.replace('"' + wrong_titles[i] + '"', '"' + right_titles[i] + '"')

        return cleaned_line

        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

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
        return re.findall(r'"(.*?)"', preprocessed_input)

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
        res = set()
        years = set(re.findall(r'\(([0-9][0-9][0-9][0-9]?)\)', title))

        if len(years) > 0:
            for i in range(len(self.titles)):
                curtitle_arr = self.titles[i]
                curtitle = curtitle_arr[0]
                articles = curtitle.split(", ")
                if len(articles) > 1:
                    article_year = articles[-1].split()
                    if article_year[0] in ["The", "An", "A", "the", "a", "an"]:
                        curtitle = article_year[0] + " " + articles[0] + " " + article_year[1]

                if self.creative:
                    # ctitle = title.split()
                    # ccurtitle = curtitle.split()
                    # if not set(ctitle).isdisjoint(set(ccurtitle)):
                    #     res.append(i)
                    regex = r'\bspecial_string_to_check\W'
                    # print(title, cur_title)
                    if re.search(regex.replace('special_string_to_check', title), curtitle_arr[0]):
                        res.add(i)

                if title == curtitle:
                    res.add(i)
                    break
        else:
            for i in range(len(self.titles)):
                curtitle_arr = self.titles[i]
                curtitle = curtitle_arr[0]
                articles = curtitle.split(", ")
                if len(articles) > 1:
                    article_year = articles[-1].split()
                    if article_year[0] in ["The", "An", "A", "the", "a", "an"]:
                        curtitle = article_year[0] + " " + articles[0] + " " + article_year[1]

                title_info = curtitle.split("(")
                cur_title = title_info[0].strip()
                if self.creative:
                    # ctitle = title.split()
                    # ccurtitle = curtitle.split()
                    # if not set(ctitle).isdisjoint(set(ccurtitle)):
                    #     res.append(i)
                    regex = r'\bspecial_string_to_check\W'
                    # print(title, cur_title)
                    if re.search(regex.replace('special_string_to_check', title), curtitle_arr[0]) or title == cur_title:
                        res.add(i)

                    # Alt Titles
                    alt_names = set(re.findall(r'\(a\.k\.a\.\s[\w\s]+\)', curtitle_arr[0]))

                    for alt in alt_names:           # alt = "(a.k.a. The Bicycle Thief)"
                        parts = alt.split()
                        alt_name = " ".join(parts[1:])
                        alt_name = alt_name[:-1]
                        if alt_name == title:
                            res.add(i)
                            break

                    # Foreign Titles
                    foreign_titles = set(re.findall(r'\(.+\)\s', curtitle_arr[0]))
                    foreign_titles = foreign_titles.difference(years)
                    foreign_titles = foreign_titles.difference(alt_names)
                    for foreign_t in foreign_titles:
                        foreign_t = foreign_t.strip()
                        # if cur_title == "Quest for Fire":
                        #     print(foreign_t)
                        foreign_t = foreign_t[1:-1]
                        if foreign_t == title:
                            res.add(i)
                            break
                        # Foreign Articles
                        parts = foreign_t.split(', ')
                        rearranged_t = " ".join(parts[:-1])
                        rearranged_t = parts[-1] + " " + rearranged_t
                        if rearranged_t == title:
                            res.add(i)
                            break

                else:
                    if title == cur_title:
                        res.add(i)

        return list(res)

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
        good_count = 0
        bad_count = 0

        remove_title = re.compile(r'\"(.+?)\"')
        review_without_quotes = (re.sub(remove_title, '', preprocessed_input)).lower()

        # negation words: don't, didn't, not, no, never, can't, shouldn't, won't
        negations = ["don't", "didn't", "not", "no", "never", "can't", "shouldn't", "won't"]

        split_string = re.split(r'[,!;.:?]', review_without_quotes)
        if not self.creative:
            for clause in split_string:
                was_negation = False
                words = clause.split()
                for word in words:
                    y_word = word[:-1] + "y"
                    if word in self.sentiment or y_word in self.sentiment:
                        wrd = ""
                        if word in self.sentiment:
                            wrd = word
                        else:
                            wrd = y_word
                        sent = self.sentiment[wrd]
                        if sent == "pos":
                            if was_negation:
                                bad_count += 1
                            else:
                                good_count += 1
                        if sent == "neg":
                            if was_negation:
                                good_count += 1
                            else:
                                bad_count += 1

                    if word in negations:
                        was_negation = True

            if good_count > bad_count:
                return 1
            if good_count == bad_count:
                return 0
            else:
                return -1
        else:   # creative mode
            good_count = 0
            bad_count = 0
            remove_title = re.compile(r'\"(.+?)\"')
            review_without_quotes = (re.sub(remove_title, '', preprocessed_input)).lower()
            # negation words: don’t, didn’t, not, no, never, can’t, shouldn’t, won’t
            negations = ["don't", "didn't", "not", "no", "never", "can't", "shouldn't", "won't"]
            split_string = re.split(r'[,!;.:?]', review_without_quotes)
            for clause in split_string:
                was_negation = False
                words = clause.split()
                for word in words:
                    y_word = word[:-1] + "y"
                    if word in self.supersentiment or y_word in self.supersentiment:
                        if word in self.supersentiment:
                            wrd = word
                        else:
                            wrd = y_word
                        wrd = wrd.strip()
                        sent = self.supersentiment[wrd]
                        if sent == "vpos":
                            if was_negation:
                                bad_count += 2
                            else:
                                good_count += 2
                        elif sent == "pos":
                            if was_negation:
                                bad_count += 1
                            else:
                                good_count += 1
                        elif sent == "neg":
                            if was_negation:
                                good_count += 1
                            else:
                                bad_count += 1
                        elif sent == "vneg":
                            if was_negation:
                                good_count += 2
                            else:
                                bad_count += 2
                    word = word.strip()
                    if word in negations:
                        was_negation = True
            # greater positive sentiment than negative
            if good_count > bad_count:
                # super positive threshold
                if (good_count >= (2 * bad_count)) and self.creative:
                    return 2
                # regular positive threshold
                else:
                    return 1
            # neutral sentiment
            elif good_count == bad_count:
                return 0
            # greater negative sentiment than positive
            else:
                # super negative threshold
                if (bad_count >= (2 * good_count)) and self.creative:
                    return -2
                # regular negative threshold
                else:
                    return -1

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
        movie_sentiments = {}

        parts = re.split(r'(but|however|yet)', preprocessed_input)
        sentiment_segments = []

        for i in range(len(parts)):
            if i % 2 == 0:
                sentiment_segments.append(parts[i])

        for review in sentiment_segments:
            movie_titles = set(re.findall('"([^"]*)"', review))
            for movie in movie_titles:
                movie_sentiment = self.extract_sentiment(review)
                if not self.creative:
                    if movie_sentiment > 0:
                        movie_sentiments[movie] = 1
                    elif movie_sentiment < 0:
                        movie_sentiments[movie] = -1
                    else:
                        movie_sentiments[movie] = 0
                if self.creative:
                    movie_sentiments[movie] = movie_sentiment
        return list(movie_sentiments.items())

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
        res = set()
        for c in candidates:
            curtitle_arr = self.titles[c]
            curtitle = curtitle_arr[0]
            articles = curtitle.split(", ")
            if len(articles) > 1:
                article_year = articles[-1].split()
                if article_year[0] in ["The", "An", "A", "the", "a", "an"]:
                    curtitle = article_year[0] + " " + articles[0] + " " + article_year[1]
            title_info = curtitle.split("(")
            cur_title = title_info[0].strip()
            regex = r'\bspecial_string_to_check\W'
            if re.search(regex.replace('special_string_to_check', clarification), curtitle_arr[0]) or re.search(
                    regex.replace('special_string_to_check', clarification), cur_title) or clarification == cur_title:
                res.add(c)
            else:
                clarification = "(" + clarification + ")"
                if re.search(regex.replace('special_string_to_check', clarification), curtitle_arr[0]) or re.search(
                        regex.replace('special_string_to_check', clarification),
                        cur_title) or clarification == cur_title:
                    res.add(c)

        return list(res)

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

        binarized_ratings[(ratings > threshold) & (ratings != 0)] = 1
        binarized_ratings[(ratings <= threshold) & (ratings != 0)] = -1

        return binarized_ratings

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
        u = np.array(u)
        v = np.array(v)
        len1 = np.sqrt(sum(np.square(u)))
        len2 = np.sqrt(sum(np.square(v)))
        if len1 == 0 or len2 == 0:
            return 0
        if len1 != 0:
            one = u / np.sqrt(sum(np.square(u)))
        if len2 != 0:
            two = v / np.sqrt(sum(np.square(v)))
        similarity = np.matmul(one, two)
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

        unrated = []
        rated = []
        for i in range(len(user_ratings)):
            user_r = user_ratings[i]
            if user_r == 0:
                unrated.append(i)
            else:
                rated.append(i)
        predicted_ratings = dict()
        for mi in unrated:
            total = 0
            for mr in rated:
                sim = self.similarity(ratings_matrix[mi], ratings_matrix[mr])
                total += (sim * user_ratings[mr])
            predicted_ratings[mi] = total

        sorted_ratings = sorted(predicted_ratings, key=lambda x: predicted_ratings[x], reverse=True)

        recommendations = sorted_ratings[:k]
        return recommendations
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
        Greetings! This is motbot. Remember: in the starter and creative modes, movie names
        must be in quotation marks! Please beware... my creators made me yassified so don't be
        too hurt if I slay you too hard <3
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')