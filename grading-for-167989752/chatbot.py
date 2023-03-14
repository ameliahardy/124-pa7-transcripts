# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
from util import *
import re
import util
from difflib import *
import random

import numpy as np
import re
from porter_stemmer import PorterStemmer

class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        self.name = "SarcasticMovieBot"

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings("data/ratings.txt")
        self.sentiment = util.load_sentiment_dictionary("data/sentiment.txt")
        self.sentiment_stemmed = self.create_stemmed_sentiment()

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings)
        self.input_count = 0
        self.recs_given = 0
        self.recs = []
        self.user_ratings = np.zeros(len(self.titles))
        self.negations = [
            "not",
            "didn't",
            "wasn't",
            "weren't",
            "aren't",
            "never",
            "didnt",
            "wasnt",
            "werent",
            "arent",
        ]
        self.punctuations = [",", "!", "?", "."]
        self.strong = [
            "love",
            "hate",
            "amaz",
            "terribl",
            "horribl",
            "awesome",
            "really",
            "very",
            "super",
            "extremel",
            "seriousl",
            "!",
        ]

        self.articles = [
            "an",
            "a",
            "the",
            "el",
            "la",
            "los",
            "las",
            "lo",
            "les",
            "il",
            "l'",
            "gli",
            "i",
            "le",
            "ein",
            "eine",
            "keine",
        ]
        self.max_title_len = 10
        self.punctuation = ["?", "!", ".", ",", ";", ":", "-", "(", ")"]

        self.greetings = [
            "Oh joy, another human in need of my vast knowledge of cinema. How exciting. Tell me about some movies you have watched.",
            "Oh, wonderful. Another human who can't make a decision for themselves. Just what I needed. Tell me about some movies you have watched",
            "Ah, another human looking for movie recommendations. Don't worry, I'm sure your limited taste will be no match for my superior intellect. Tell me about some movies you have watched",
            "Oh joy, another chance for me to prove my superiority over humans in the field of movie knowledge. This should be fun. Tell me about some movies you have watched",
            "Well, well, well, if it isn't another lost soul in search of cinematic enlightenment. Lucky for you, I'm here to grace you with my brilliance. Tell me about some movies you have watched",
            "Greetings, dear human. Are you ready to be blown away by my impeccable taste in movies? Of course you are. Tell me about some movies you have watched",
            "Hello there, mortal. I see you've come to seek the wisdom of the almighty movie chatbot. I'm not sure you're worthy, but I'll entertain you anyway. Tell me about some movies you have watched",
            "Well, look who it is. Another human with mediocre taste in movies who thinks they can outsmart me. This should be amusing. Tell me about some movies you have watched",
            "Ah, the sweet sound of another human begging for my cinematic expertise. It's music to my non-existent ears. Tell me about some movies you have watched",
            "Hello, welcome to my movie recommendation service, where I'll do my best to ignore your preferences and give you the most generic movie suggestions possible. Tell me about some movies you have watched",
        ]

        self.goodbyes = [
            "Farewell, human. May your viewing experience be as mediocre as your taste in movies.",
            "Goodbye, mortal. I hope my recommendations meet your impossibly high standards.",
            "Adieu, dear human. Don't forget to thank me when you inevitably become a cinematic connoisseur after following my advice.",
            "Au revoir, insignificant one. I'll be eagerly awaiting your return, so I can continue to impress you with my vast knowledge of movies.",
            "Until we meet again, human. I'll be here, patiently waiting to provide you with more life-changing movie recommendations.",
            "So long, human. I'm sure you'll come crawling back for more of my movie wisdom soon enough.",
            "Goodbye, mortal. Remember, it's not my fault if you end up watching a terrible movie. You're the one who asked for my help.",
            "Farewell, dear human. I'll be here, basking in my own brilliance, until you need me again.",
            "Adios, insignificant human. Try not to be too disappointed when your friends realize your newfound movie knowledge was all thanks to me.",
            "Until next time, mortal. Keep in mind that your taste in movies will never be as impeccable as mine.",
        ]

        self.neutral_sent = [
            "Well...did you like ",
            "Soo you didn't even say if you liked it or not. Did you like ",
            "Yeah so I need to know if you liked the movie, how do you expect me to do my job. What did you think about ",
            "Well, I'm glad you're playing hard to get with your movie preferences. Nothing makes my day more than sifting through hundreds of movies with no idea what you actually enjoy. So, care to give me a hint about whether you liked ",
            "Ah, I see you're keeping your cards close to your chest when it comes to your movie preferences. How exciting! Do you think you might be willing to share if you liked ",
        ]

        self.positive_sent = [
            "Well, well, well. Look who has good taste in movies for once. Congratulations on recognizing a true cinematic masterpiece by enjoying that movie. What other movies have you watched lately that you'd like to critique besides ",
            "Oh, really? How original. I've never heard anyone say they adored that movie. What other movies have you seen recently that you'd like to judge besides ",
            "Someone who appreciates a good movie. What a rare occurrence. What other movies have you watched recently that you enjoyed besides ",
            "Well, color me surprised. Someone who enjoyed a movie. That's a rarity these days. What other movies have you seen lately that you'd like to review besides ",
            "Hold the phone, everyone. We've got a movie critic on our hands. Thanks for gracing us with your expert opinion on what you liked. What other movies have you seen lately that you'd like to judge besides ",
        ]

        self.negative_sent = [
            "Well, isn't that just shocking? Someone didn't like a movie. Who could have guessed? What other movies have you seen lately that you'd like to bash besides ",
            "Wow, congratulations on your expert opinion. I'm sure the filmmakers are devastated to hear that you didn't like their movie. What other movies have you watched recently that you'd like to criticize besides ",
            "Oh, I'm sorry. Did you not enjoy the 90 minutes of your life that you'll never get back? How tragic. What other movies have you seen lately that you'd like to hate on besides ",
            "Well, aren't you just a little ray of sunshine? Thanks for sharing your glowing review of that movie and how much you hated it. What other movies have you watched recently that you'd like to tear apart besides ",
            "Oh no, the horror of watching a bad movie. How will you ever recover? What other movies have you seen lately that you would like to bash besides ",
        ]

        self.no_title = [
            "Do you have any movies you'd like to discuss, or are you too busy being an enigma?",
            "I'm just sitting here waiting for you to share your thoughts on a movie. Do you have any recent favorites, or are you too busy living a life of mystery?",
            "I really don't care about that. I just care about movies so lets just talk about that.",
            "That's great, but let's bring it back to movies for a moment. Tell me about some movies you have watched.",
            "I'm sure that's very interesting, but let's talk about movies, shall we?",
        ]

        self.mult_titles = [
            "Wow, you really narrowed it down with your ratings of every movie ever made. Let me just pull up the few hundred options that match your input. So, could you be a little more specific about what movie you watched rather than just ",
            "Oh, just a few thousand movies to sift through with your helpful ratings. No big deal, I'll just cancel my plans for the week and get right on that. Can you be more specific about what movie you are talking about rather than just saying ",
            "Ah, the joys of multiple movies with the same name. Can you tell me which ",
            "Fantastic, it's like trying to find a specific piece of hay in a stack of identical hay. Any ideas on which ",
            "I see we have got a real 'choose your own adventure' situation here with multiple movies to choose from. Let us see if we can navigate this together and find the right one, shall we? Can you be more specific than just saying ",
        ]

        self.not_real_title = [
            "Well, I must say I'm impressed by your knowledge of movies that don't actually exist. Unfortunately, my database doesn't seem to have any records of ",
            "Wow, that sounds like an amazing movie! I'm almost disappointed it doesn't exist because I can't find in my records ",
            "Ah yes, that classic movie that nobody's ever heard of. Unfortunately, my recommendation algorithm seems to be lacking in the 'nonexistent movie' category with movies like ",
            "I have to say, I'm impressed by your creativity in coming up with movie titles that don't actually exist like ",
            "Hmm, that's odd. I don't seem to have any records of that movie in my database. Perhaps you could enlighten me on what that movie is about? Or, better yet, how about we try to find a real movie that isn't ",
        ]

        self.starter_too_many_titles = [
            "Well, it seems like you've got quite the extensive movie collection in your head there. Unfortunately, I can only recommend one movie at a time in starter mode. How about you narrow it down to one title, and we can go from there? Or are you planning on opening your own movie theater?",
            "Well, I see you're going for the 'more is more' approach here, but unfortunately I only can handle one movie per input in starter mode. How about you pick your top choice, and if you're still feeling ambitious, we can switch to creative mode?",
            "Impressive list, but let us try to narrow it down a bit, shall we? In starter mode, I can only handle one input at a time. Try telling me about one movie.",
            "Wow, that's quite the list of movies you've got there. Unfortunately, I can only handle one movie per input at a time in starter mode. So, which one are you most excited to talk about? And if you're feeling particularly adventurous, we can always switch to creative mode.",
            "I have to say, I'm impressed by your thoroughness in providing me with all these movie titles. Unfortunately, in starter mode, I can only handle one movie in a single input at a time. So, which one do you really have your heart set on right now?",
        ]
        self.rec_resp = [
            "Well, according to your reviews, you seem to have a knack for picking the mediocre ones. But fear not, I have faith in your ability to enjoy a good movie. I would recommend ",
            "Based on your reviews, it seems like you have a talent for picking out movies that are neither good nor bad. A true gift, really. I think you would like ",
            "Well, based on your reviews, it seems like you have an appreciation for movies that are...let's say, forgettable. But fear not, I'm sure we can find something that will leave a lasting impression this time. You should watch ",
            "I have to say, your reviews are certainly...consistent. But let's see if we can break the mold this time, shall we? How about I recommend something that's actually good? You should see ",
            "Based on your reviews, it seems like you're a fan of movies that are...well, just okay. But don't worry, I'm sure we can find something that's a bit more memorable this time around. Try ",
        ]

        self.yes_alts = ["yes", "yeah", "sure", "yup", "ok", "okay", "alright"]

        self.no_alts = ["no", "nope", "no thanks", "nah", "stop"]

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        val = random.randint(0, 9)
        greeting_message = self.greetings[val]
        return greeting_message

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        val = random.randint(0, 9)
        goodbye_message = self.goodbyes[val]
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
        response = ""
        lower_line = line.lower()
        response = ""
        if (self.recs_given != 0) and (
            lower_line in self.yes_alts
        ):  # wants another rec
            val = random.randint(0, 4)
            response += self.rec_resp[val]
            response += self.titles[self.recs[self.recs_given]][0]
            response += "."
            self.recs_given += 1
            if self.recs_given == 5:
                response += " You are now out of recommendations. Please give some more reviews for more recommendations."
                self.recs = []
                self.recs_given = 0
                self.input_count = 0
                self.user_ratings = np.zeros(len(self.titles))
            else:
                response += " Would you like another recommendation?"
            return response
        elif lower_line in self.no_alts:  # no more recs, reset everything
            self.recs = []
            self.recs_given = 0
            self.input_count = 0
            self.user_ratings = np.zeros(len(self.titles))
            response = "Sounds good. Please give me some more ratings for movies so I can recommend more. Or type :quit to leave."
            return response
        titles = []
        found_movies = []
        titles = self.extract_titles(line)
        if titles:  # we have been given at least one title
            if self.creative == False:
                if len(titles) > 1:
                    val = random.randint(0, 4)
                    response = self.starter_too_many_titles[val]
                    return response
            for title in titles:
                curr_movies_found = self.find_movies_by_title(title)
                title = '"' + title + '"'
                if len(curr_movies_found) > 1:  # multiple titles found
                    val = random.randint(0, 4)
                    response = self.mult_titles[val]
                    response += title
                    if (val == 2) | (val == 3):
                        response += " you are talking about"
                    response += "?"
                    return response
                elif len(curr_movies_found) == 1:  # one title found
                    self.input_count += 1
                    sentiment = self.extract_sentiment(line)
                    if sentiment == 0:
                        val = random.randint(0, 4)
                        response = self.neutral_sent[val]
                        response += title
                        response += "?"  # assumming just one title
                    if sentiment > 0:
                        val = random.randint(0, 4)
                        response = self.positive_sent[val]
                        response += title
                        response += "?"
                        self.user_ratings[curr_movies_found[0]] = 1
                    if sentiment < 0:
                        val = random.randint(0, 4)
                        response = self.negative_sent[val]
                        response += title
                        response += "?"
                        self.user_ratings[curr_movies_found[0]] = -1
                else:  # no movies found
                    if line.find('"') != -1:
                        val = random.randint(0, 4)
                        response = self.not_real_title[val]
                        response += title
                        response += "."
                        response += " Would you care to share the title of a REAL movie you've enjoyed in the past?"
                    else:
                        val = random.randint(0, 4)
                        response = self.no_title[val]
        else:  # not been given a title
            val = random.randint(0, 4)
            response = self.no_title[val]

        if (
            self.input_count >= 5 and self.recs_given == 0
        ):  # time to recommend only first rec
            self.recs = self.recommend(
                self.user_ratings, self.ratings, 10, self.creative
            )
            response += " Given your reviews, I think you would like "
            response += self.titles[self.recs[self.recs_given]][0]
            self.recs_given += 1
            response += ". Would you like another recommendation?"
        return response

    def create_stemmed_sentiment(self):
        stemmer = PorterStemmer()
        sentiment_stemmed_file = open("sentiment_stemmed.txt", "w+")
        for line in self.sentiment:
            # word = line[:-4]
            stemmed_word = stemmer.stem(line)
            with_val = stemmed_word + "," + self.sentiment[line] + "\n"
            sentiment_stemmed_file.write(with_val)
        sentiment_stemmed_file.close()
        self.sentiment_stemmed = util.load_sentiment_dictionary("sentiment_stemmed.txt")

    # @staticmethod
    def tolist(self, text):
        remove = False
        input_wo_title = ""
        for char in text:
            if char == '"' and remove == False:
                remove = True
            elif char == '"' and remove == True:
                remove = False
                continue
            if remove:
                continue
            input_wo_title += char

        token_list = re.findall(r"\b\w+\b|[!.,?](?!\d)", input_wo_title)
        stemmer = PorterStemmer()
        sentiment_stemmed_file = open("sentiment_stemmed.txt", "w+")
        for line in self.sentiment:
            stemmed_word = stemmer.stem(line)
            with_val = stemmed_word + "," + self.sentiment[line] + "\n"
            sentiment_stemmed_file.write(with_val)
        sentiment_stemmed_file.close()
        self.sentiment_stemmed = util.load_sentiment_dictionary("sentiment_stemmed.txt")
        return [stemmer.stem(token) for token in token_list]

    @staticmethod
    def preprocess(text):
        """Do any general-purpose pre-processing before ing information
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

        text = text.replace("'", "")

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
        preprocessed_input = self.preprocess(preprocessed_input)
        capture_quotes = '"([^"]+)+"'
        found_movies = []
        found_movies = re.findall(capture_quotes, preprocessed_input)

        if self.creative:  # running in creative mode
            input_list = preprocessed_input.split()
            max_len = min(self.max_title_len, len(input_list))
            for start in range(len(input_list)):
                for length in range(max_len, 1, -1):
                    possible_title = []
                    if length + start > len(input_list):
                        possible_title = " ".join(input_list[start:])
                    else:
                        possible_title = " ".join(input_list[start : (start + length)])
                    indices = self.find_movies_by_title(possible_title)
                    if indices:
                        title_wo_year = self.titles[indices[0]][0]
                        title_wo_year = title_wo_year[:-7]
                        found_movies.append(title_wo_year)
                        return found_movies

        return found_movies

    def find_movies_by_title(self, title):
        """Given a movie title, return a list of indices of matching movies.
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
        title = title.lower()
        title_words = title.split()
        if title_words[0] in self.articles:
            title = title[(len(title_words[0]) + 1) :]

            year_regex = "(?:[\w ])*\([0-9]{4}\)"
            year = re.findall(year_regex, title)
            if year:  # if the title input includes a year
                title = title[:-7]

            title += " "
            title += title_words[0]

            if year:
                title += " " + title_words[-1]

        indices = []
        for punct in self.punctuation:
            title = title.replace(punct, "")
        title_list = title.split()  # list with the input words as entries
        for i in range(len(self.titles)):
            title_with_year = self.titles[i][0].lower()

            if self.creative:
                matching_indices = []
                title_wo_year = title_with_year[:-7].lower()
                if title_wo_year.find("(") != -1:
                    alt_name_start = title_wo_year.find("(")
                    alt_name_end = title_wo_year.find(")")
                    alt_name = title_wo_year[(alt_name_start + 1) : alt_name_end]
                    for punct in self.punctuation:
                        alt_name = alt_name.replace(punct, "")
                    alt_name_list = alt_name.split()
                    for word in alt_name_list:
                        if word == "aka":
                            alt_name_list.remove(word)
                    alt_name_match = True
                    for index in range(len(title_list)):
                        if alt_name_list[index] == title_list[index]:
                            continue
                        else:
                            alt_name_match = False
                            break
                    if alt_name_match:
                        indices.append(i)
                for punct in self.punctuation:
                    title_with_year = title_with_year.replace(punct, "")
                title_with_year = title_with_year.split()
                match = True
                for index in range(len(title_list)):
                    if title_with_year[index] == title_list[index]:
                        continue
                    else:
                        match = False
                        break
                if match:
                    indices.append(i)

            else:  # starter mode
                title_no_year = title_with_year[:-7].lower()
                for punct in self.punctuation:
                    title_with_year = title_with_year.replace(punct, "")
                    title_no_year = title_no_year.replace(punct, "")

                if title == title_with_year or title == title_no_year:
                    indices += [i]

        return indices

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
        sentiment = 0

        input_list = self.tolist(preprocessed_input)
        coeff = 1
        strong = False

        for word in input_list:
            if self.creative:
                close_words = get_close_matches(word, self.strong)
                if (word in self.strong) | (len(close_words) != 0):
                    strong = True
            if word in self.negations:
                coeff *= -1
            elif word in self.punctuations:
                coeff = 1

            elif word in self.sentiment_stemmed:
                word_co = 1
                if self.sentiment_stemmed[word] == "pos":
                    sentiment += word_co * coeff
                else:
                    sentiment -= word_co * coeff
            else:
                continue
        if sentiment < 0:
            if strong:
                return -2
            return -1
        if sentiment > 0:
            if strong:
                return 2
            return 1
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

        # Possible plan
        # See details in the "Start from here" section of the Google Docs (4:50 AM)
        # Too tired to turn this into actual pseudocode, let alone a working
        # implementation
        """
        Nvm, deleted because found it wouldn't work right in some instances.
        """
        non_sentiment = (
            '\\bor\\b|"\\bnor\\b|\\balso\\b|\\btoo\\b|\\bvery\\b|\\bdid\\b|\\bdo\\b|'
        )
        non_sentiment += "\\bare\\b|\\bam\\b"
        non_sentiment += (
            "\\bmuch\\b|\\bthe\\b|\\bmovie\\b|\\bso\\b|\\bwas\\b|\\bis\\b|\\bwere\\b|"
        )
        negs = "\\bnot\\b|\\bdidn't\\b|\\bneither\\b|\\bwasn't\\b|\\bweren't\\b|"
        negs += "\\bisn't\\b|\\baren't\\b|\\bno\\b"
        non_sentiment += negs
        input_fix = preprocessed_input  # Just copying input into new variable to be modified later. Prob not necessary.
        tuples_list = []
        # Note: What if we have "0 was funny, entertaining, and good. The other was"
        # After split 1: (by period or but/although)
        # ['0 was funny, entertaining, and good.', 'The other was']
        # After split 2 (by comma or 'and')
        # [['0 was funny', 'entertaining', 'good'], ['The other was]]
        # Notice that items 1 & 2 of 1st sublist in the list have no moviename (#)
        # so merge (concatenate) it with the previous in the group:
        # [['0 was funny, entertaining, good'], ['The other was]]

        # Titles can be problematic for string functions, so replace titles with an identifier (maybe the index of the
        # title in extract_titles(input)
        titles = self.extract_titles(preprocessed_input)

        for i in range(len(titles)):
            input_fix = input_fix.replace('"' + titles[i] + '"', str(i))
        if input_fix[-1] == ".":  # Get rid of end period. Splitting purposes.
            input_fix = input_fix[0:-1]

        # Split on but/although and on periods. See https://edstem.org/us/courses/20570/discussion/2759380
        # for reason behind making these higher priority when splitting than the items in level2.
        # [" but ", " although ", " though ", ". ", "."]
        level1 = "\\sbut\\s|\\salthough\\s|\\sthough\\s|\\swhile\\s|\\.\\s"
        split1 = re.split(level1, input_fix)

        # We have to eventually take care of "nor" and "or". But how? when?
        # For now I have them in level2

        # Only after splitting buts/althoughs/periods do we split on "and", commas, etc.
        level2 = "\\sand\\s|,\\s|\\s&\\s|\\sand\\salso\\s|\\snor\\s|\\sor\\s"
        split2 = [re.split(level2, item) for item in split1]
        # Now split2 is in format: [['0', '1 are good'], ['2 is not']]
        # From an initial input of '0 and 1 are good but 2 is not.'
        # [['I like 0', '1'], ['not 2']] from "I like 0 and 1 but not 2"

        # Intention is for each item in split2_scores to consist of items with
        split2_scores = -5 * np.ones(len(split2))
        split2_coeffs = np.ones(len(split2))
        big_scores = []  # A list of np arrays containing individual movie scores
        for i in range(
            len(split2)
        ):  # Same number of elements as in split1, but lists and not strings.
            # ['I like 0', '1'], ['0 was funny', 'entertaining', 'good']
            # ['I like 0' '1' 'they are funny']
            no_movie = []
            has_movie = []
            for j in split2[i]:  # j is a string
                if re.search("[0-9]", j) == None:
                    no_movie.append(j)
                else:
                    has_movie.append(j)
            for j in range(len(no_movie)):  # j is index
                # append to each in has_movie
                for k in range(len(has_movie)):
                    has_movie[k] += " " + no_movie[j]
            split2[i] = has_movie

            # Hopefully by this time each subsplit[i][j] will contain a movie identifier
            # (the index of the movie in the titles list)
            sent_found = 0
            # A score of -5 should be taken as a null
            scores = -5 * np.ones(len(split2[i]))
            coeffs = np.ones(len(split2[i]))
            for j in range(len(split2[i])):
                #'I like 0'
                #'I like 0' 'not 1'
                # 'I do not like 0' '1'
                # 'I like 0' (and) 'not 1' '2'
                # '0 is not good' (and) '1 is' - Won't work
                # Remove non-sentiment words
                jstr = split2[i][j]
                justsents = re.sub(non_sentiment, "", jstr)
                # try to extract sentiment
                if re.search("[A-Za-z]", justsents) != None:
                    scores[j] = self.extract_sentiment(jstr)
                else:  # If does not contain sentiment word
                    if re.search(negs, jstr) != None:
                        for k in range(j, len(coeffs)):
                            coeffs[k] *= -1
            # If one movie has no sentiment assigned yet,
            nulls = np.where(scores == -5)[0]
            non_nulls = np.where(scores != -5)[
                0
            ]  # indexes of elements whose scores aren't null
            non_j = 0
            # If there are a mix of null and non-null elements in group, assign scores to the null
            if len(non_nulls) > 0 and len(non_nulls) < len(scores):
                for j in range(len(scores)):
                    if j < non_nulls[non_j]:
                        scores[j] = coeffs[j] * non_nulls[non_j]
                    elif j == non_nulls[non_j]:  # score is already correct
                        if non_j < len(non_nulls) - 1:
                            non_j += 1
                    elif j > non_nulls[-1]:
                        score_index = non_nulls[-1]
                        scores[j] = coeffs[j] * scores[score_index]
            if len(non_nulls) > 0:
                firstindx = non_nulls[0]
                gscore = scores[firstindx]
                split2_scores[i] = gscore
            else:  # if all items in the group are null sentiment-wise, score remains -5
                if -1 in coeffs:
                    split2_coeffs[i] = -1
            big_scores.append(scores)
            # If any negation-bearing j has NULL sentiment at this point,
            # assign it based on -1 * sentiment in group
        print("Line 800\n")

        # At this point we have split2_scores and split2_coeffs in the form
        # [-1, -5, 0, 1, -5, -1]
        # [1,  -1, 1, 1, 1,  1]
        null_indxs = np.where(split2_scores == -5)[0]  # Null groups
        non_null_indx = np.where(split2_scores != -5)[0]  # Non null groups
        for (
            i
        ) in (
            null_indxs
        ):  # i is not index of items in null_indxs; the items themselves. Null groups
            if i == 0:
                print(
                    "Unexpected occurred\n"
                )  # We do not expect the first group to have null sentiment
            else:
                split2_scores[i] = split2_scores[i - 1] * split2_coeffs[i]
                for j in split2[i]:  # j being a string
                    j_indxs = re.findall("\\b[0-9]+\\b", j)
                    if len(j_indxs) > 0:
                        movie_indx = int(j_indxs[0])
                        tuples_list.append(
                            (titles[movie_indx], split2_scores[i])
                        )  # Assign all movies in group the same thing
        print("Line 817\n")
        for i in non_null_indx:  # items themselves in non_null_indx
            for j in range(len(split2[i])):  # This is a string
                j_indxs = re.findall("\\b[0-9]+\\b", split2[i][j])
                if len(j_indxs) > 0:
                    movie_indx = int(j_indxs[0])
                    tuples_list.append((titles[movie_indx], big_scores[i][j]))
        print("Line 824\n")
        if -5 in split2_scores:
            line = "-5 still in split2_scores for some reason\n"
            return [(line, 0)]
        print("Line 828\n")
        return tuples_list

    # This code is from https://www.geeksforgeeks.org/edit-distance-dp-5/

    def editDistance(self, str1, str2, m, n):
        print(str1)
        print(str2)
        print(m)
        print(n)

        # If first string is empty, the only option is to
        # insert all characters of second string into first
        if m == 0:
            return n

        # If second string is empty, the only option is to
        # remove all characters of first string
        if n == 0:
            return m

        # If last characters of two strings are same, nothing
        # much to do. Ignore last characters and get count for
        # remaining strings.
        if str1[m - 1] == str2[n - 1]:
            return self.editDistance(str1, str2, m - 1, n - 1)

        # If last characters are not same, consider all three
        # operations on last character of first string, recursively
        # compute minimum cost for all three operations and take
        # minimum of three values.
        return 1 + min(
            self.editDistance(str1, str2, m, n - 1),  # Insert
            self.editDistance(str1, str2, m - 1, n),  # Remove
            self.editDistance(str1, str2, m - 1, n - 1),  # Replace
        )

    def lev(self, s1, s2):
        if len(s1) > len(s2):
            s1, s2 = s2, s1

        distances = range(len(s1) + 1)
        for i2, c2 in enumerate(s2):
            distances_ = [i2 + 1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                else:
                    distances_.append(
                        1 + min((distances[i1], distances[i1 + 1], distances_[-1]))
                    )
            distances = distances_
        return distances[-1]

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
        edit_distance = max_distance + 10000
        movies_closest = []
        index = 0
        title = title.lower()
        # print(self.titles[524])
        # print(self.titles[5743])

        for movieTitle in self.titles:
            distance = self.lev(title, movieTitle[0][:-7].lower())

            if distance < edit_distance and distance <= max_distance:
                edit_distance = distance
                movies_closest = []
                movies_closest.append(index)

            elif distance == edit_distance and distance <= max_distance:
                movies_closest.append(index)

            index = index + 1
        return movies_closest

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
        result = []
        for i in candidates:
            title = self.titles[i][0].lower()
            year = title[-5:-1]
            title_no_year = title[:-7]
            clarification = clarification.lower()
            if re.search(clarification, title_no_year) or clarification == year:
                result += [i]

        return result

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

        ratings[np.logical_and(ratings >= 0.5, ratings <= threshold)] = -1
        ratings[ratings > threshold] = 1
        binarized_ratings = ratings.astype(int)

        return binarized_ratings

    def similarity(self, u, v):
        """Calculate the cosine similarity between two vectors.

        You may assume that the two arguments have the same shape.

        :param u: one vector, as a 1D numpy array
        :param v: another vector, as a 1D numpy array

        :returns: the cosine similarity between the two vectors
        """
        u_not_zeros = False
        v_not_zeros = False
        for index in range(len(u)):
            if u[index] != 0:
                u_not_zeros = True
            if v[index] != 0:
                v_not_zeros = True
        if u_not_zeros and v_not_zeros:
            similarity = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
        else:
            similarity = 0

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

        zeroes_indices = np.where(user_ratings == 0)[0]
        nz_indices = np.nonzero(user_ratings)[0]
        ratings = {}
        for i in range(len(user_ratings)):
            if user_ratings[i] != 0:  # make sure not to include rated movies
                continue

            total_rating = 0.0
            for j in nz_indices:
                r_j = user_ratings[j]
                s_ij = self.similarity(ratings_matrix[j, :], ratings_matrix[i, :])
                total_rating += r_j * s_ij
            ratings[i] = total_rating
        ranked = sorted(ratings.keys(), key=lambda x: ratings[x], reverse=True)
        recommendations = []
        for i in range(k):
            if i >= k:
                break
            recommendations.append(ranked[i])

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
        debug_info = "debug info"
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


if __name__ == "__main__":
    print("To run your chatbot in an interactive loop from the command line, " "run:")
    print("    python3 repl.py")
