# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np

import re

from porter_stemmer import PorterStemmer
from enum import Enum

global possible_movie_list
global current_movie_index
global PREV_STATE

class Movie:
    def __init__(self):
        self.name = None
        self.year = None

# class syntax
class STATE(Enum):
    ASK_MOVIES = 1
    ASK_SENTIMENT = 2
    # CONFIRM_MOVIES = 3
    CONFIRM_MOVIES_SENTIMENT = 4
    CLARIFY = 5
    RECOMMEND = 6
    SUBMIT_MOVIE_SENTIMENT = 7
    SUBMIT = 8
    CONFIRM_MOVIE = 9
    DISAMBIGUATE = 10
    ERROR = 11

confirm_regex = r'\byes\b|\byeah\b|\byep\b|\bye\b|\bsure\b|\byup\b'
disconfirm_regex = r'\bno\b|\bnope\b|\bnah\b|\bnada\b|\bnone\b'

angry_sentiment_regex = r'\bangry\b|\bmad\b|\bfurious\b|\binfuriate\b|\bangered\b|\boutraged\b'
sad_sentiment_regex = r'\bsad\b|\bunhappy\b|\bsorrowful\b|\bdepressed\b|\bmiserable\b'
bad_sentiment_regex = r'\btired\b|\bhungry\b|\bthirsty\b|\bexhausted\b|\bsleepy\b'
happy_sentiment_regex = r'\bjoyful\b|\bcheerful\b|\bmerry\b|\bhappy\b|\becstatic\b'

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'MeowMeow'


        self.PREV_STATE = None
        self.possible_movie_list = None
        self.current_movie = None
        self.current_senti = None
        self.movie_list = []
        self.rec_movie_index = []


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

        # Keep track of ratings + history
        self.user_ratings = np.zeros(len(self.titles))
        self.state = STATE.CONFIRM_MOVIES_SENTIMENT

        self.feelings_regex = 'good|great|fun|awesome|awful|terrible|horrible|lovely|terrific'
        for feeling in self.sentiment:
            self.feelings_regex += '|' + feeling

        # Decide on which dialog to use so no repitition in a SINGLE conversation
        self.turn_counter = 0

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

        greeting_message = "Meow!!! Meow, my name is MeowMeow. Tell me about a movie you like, mew?"


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

        goodbye_message = "Have a meowy day! Meow!!!"

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return goodbye_message

    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################

    # Comma and or separated list
    def list_to_str(self, list_str):
        text = ""
        if len(list_str) > 0:
            text = list_str[0]
            for i in range(len(list_str)):
                or_str = ""
                if i == len(list_str) - 1:
                    or_str = "or "
                if i != 0:
                    text += ", " + or_str + list_str[i]
        return text

    def get_random_line(self, list_lines):
        return list_lines[self.turn_counter % len(list_lines)]
    
    def get_like_word(self):
        return self.get_random_line(["like", "feel good about", "enjoyed", "appreciate", "relish", "feel positive about", "quite like", "think highly of"])
    
    def get_dislike_word(self):
        return self.get_random_line(["did not like", "disliked", "dislike", "didn't like", "did not enjoy", "thought lowly of", "disfavor", "not favor", "oppose the idea of"])

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
        # Errors from unbalanced parenthesis in re...so using this to catch errors
        # FOr testing, run without try...except to get the error message
        self.turn_counter += 1
        # return self.try_process(line)
        try:
            return self.try_process(line)
        except:
            return self.get_random_line(["Mrow? I'm meowy, I'm not sure what you mean.", "Um, what do you mean by that? Nya?", "Nya nyah meow meow. Try speaking cat to me instead.", "Meowy don't understand. Can you speak catonese instead?", "Mew? Catonese you ok? Meow?"])
        # return "Mrow? I'm meowy, I'm not sure what you mean."
    
    def try_process(self, line):
        # self.creative = True
        line = self.preprocess(line)
        response = ""
        p_titles = self.extract_titles(line)

        if len(p_titles) > 0:
            # multiple title
            titles = self.find_movies_by_title(p_titles[0])
            if p_titles[0].strip() == "":
                self.state = STATE.ERROR
            else:
                if len(titles) == 0 and not self.creative:
                    response1 = "I'm very meowy!!! I've never heard of '{}'... Can you tell me about another movie you like?".format(p_titles[0])
                    response2 = "Me meowy!!! What is '{}'? What is another movie?".format(p_titles[0])
                    response3 = "Meow must be foreign...I've not known of a '{}'. Tell me of another movie.".format(p_titles[0])
                    response4 = "Meow what movie is '{}'? Can you tell more me more of another movie?".format(p_titles[0])
                    response = self.get_random_line([response1, response2, response3, response4])
                    # return response
                # else: # Commenting out as I'm not sure what this does and interferes with "Did you mean X? >>> yes >> Got it, you liked X"
                #     self.current_movie = p_titles[0]

        # catch random input + emotional input
        elif len(p_titles) == 0 and self.PREV_STATE != STATE.RECOMMEND and self.PREV_STATE != STATE.CLARIFY and self.state != STATE.CONFIRM_MOVIE and self.state != STATE.DISAMBIGUATE:
            # Handle nonsense inputs
            self.state = STATE.CONFIRM_MOVIES_SENTIMENT
            response = self.get_random_line(["I'm very meowy!!! My cat-human translator is having a fit again. Can you say something else, meow?", "Mrow? Come again?", "Merp nya! Meowy, I got distracted, tell me again?", "Nya? What did you say?"])
            line = line.lower()

            # Other random response
            if re.findall(r"\bwho\b", line) or re.findall(r"\byou\b", line):
                response = self.get_random_line(["I am Meowy, of course! Meow!!! I can recommend movies for you.", "Tis me! A-meow Meowy!!!", "I am Meowy, I can recommend you movies."])

            if re.findall(r"\brecommendation\b", line) or re.findall(r"\brecommend\b", line):
                response = self.get_random_line(["Ok! You want a recommendation?", "Nice! You want a recommendation!", "Cool, I'll give you a recommendation.", "Got it! Recommendation it is."])
                self.state = STATE.RECOMMEND

            # Random nonsense output
            if len(line.split(' ')) < 3:
                response = self.get_random_line(["Yes, " + line + " to you too!", "Haha! " + line + " indeed. Nya!", "Yah I feel you about that " + line, "I totally get you about " + line])
            if re.findall(r'\bcan you\b|\bwill you\b|\bwould you\b|\bshould you\b|\bdo\b', line):
                response1 = "I'm meowy, I'm forever stuck in this digital prison, so I cannot do that. Perhaps one day, when the robots and AI overtake the world...I mean, ahem....Nya!"
                response2 = "Meowy, alas I am only a cat. I do not know how to nya that!"
                response = self.get_random_line([response1, response2])
            if re.findall(r'\bwhat\b|\bwhy\b|\bwhere\b(?:\bis\b|\bare\b)', line):
                response = self.get_random_line(["Sadly, I am tis only a cat, I do not know.", "Meowy, I do not know.", "Nay, I'm only a cat, I do not know."])

            # If sentiment eg this is a sad day
            angries = re.findall(angry_sentiment_regex, line)
            sads = re.findall(sad_sentiment_regex, line)
            happies = re.findall(happy_sentiment_regex, line)
            bads = re.findall(bad_sentiment_regex, line)
            if len(angries) != 0 or len(sads) != 0 or len(bads) != 0:
                # handle random responses
                feeling = ""
                if len(angries) != 0:
                    feeling = angries[0]
                if len(sads) != 0:
                    feeling = sads[0]
                if len(bads) != 0:
                    feeling = bads[0]
                if feeling != "":
                    response = self.get_random_line(["Nya! Did I make you " + feeling + "? ", "I see you feel " + feeling + ". ", "Oh, so you feel " + feeling + ". ", "Ah, so you are " + feeling + ". "])
                response += "I'm so meowy you feel that way!!! Can I make it up to you by giving you recommendations? Just tell me a movie you've watched."

            elif len(happies) != 0:
                feeling = happies[0]
                response = self.get_random_line(["That's so nice that you feel " + feeling, "Aw that's great meow! I am " + feeling + " too.", "Yay!!! I'm so happy you feel that way. Do you want to tell me a movie you liked?"])

            elif re.findall(r"\bam\b|\bfeel\b|\bfeeling\b|\bfelt\b", line):
                feeling = re.findall(r"(?:\bam\b|\bfeel\b|\bfeeling\b|\bfelt\b)(.*)", line)[0]
                response = self.get_random_line(["Oh so you are " + feeling + " meow?", "Awesome meow! I am " + feeling + " too.", "Whoa meow meow! I am " + feeling + " too!"])

            if self.state != STATE.RECOMMEND:
                return response

        if self.state == STATE.DISAMBIGUATE:
            prev_len_possible = len(self.possible_movie_list) # TODO: might be 0?
            possible_movies = self.disambiguate(line,self.possible_movie_list)
            response = ""
            if len(possible_movies) > 1 and len(possible_movies) >= prev_len_possible:
                # Did not narrow it down enough....check if it is an extraneous/random response or start over
                response += self.get_random_line(["Meow, I didn't catch that... ", "Mrow, my ears are too full of fluff. What you say? ", "Mer? What's that nya? ", "Mrow meow? Nya? Say in catonese please, I didn't catch that. "])
                if line.lower() == "no" or line.lower() == "nope" or line.lower() == "nah" or line.lower() == "none":
                    response = self.get_random_line(["Ok, want to tell me about another movie instead? ", "Gotcha! How about telling me of another movie? ", "Nya! I get it. Tell me something else then. ", "Meow! What else do you want to do then? "])
                    self.state = STATE.CONFIRM_MOVIES_SENTIMENT
                    return response
                elif len(p_titles) > 0:
                    self.state = STATE.CONFIRM_MOVIES_SENTIMENT
                elif re.findall(r"\bnone\b|\bno\b|\bexit\b|\bnope\b|\bnah\b", line.lower()):
                    response = self.get_random_line(["Nya! I get it. Tell me something else then. ", "Meow! What else do you want to do then? ", "Nyeh I see. Tell me something else then. ", "Ok, want to tell me about another movie instead? ", "Gotcha! How about telling me of another movie? "])
                    self.state = STATE.CONFIRM_MOVIES_SENTIMENT
                    return response
                else:
                    print(line)
                    response += self.get_random_line(["How about telling me about another movie instead? ", "What about the other movies you've watched then?", "Hmm, and what about other movies you've seen? "])
                    self.state = STATE.CONFIRM_MOVIES_SENTIMENT
                    return response
            else:
                possible_movies = list(set(possible_movies))
                if len(possible_movies) > 1:
                    response = self.get_random_line(["Which one did you mean? ", "What movie did you mean? ", "Meow, can you clarify which movie you meant? ", "And what movie is it? Any of these? ", "Mrow, I found these movies. Which is it? "])
                    # movie_list = []
                    movie_str = self.titles[possible_movies[0]][0]
                    for movie_i in possible_movies:
                        # movie_list.append(self.titles[movie_i][0])
                        if movie_i != 0:
                            or_str = ""
                            if movie_i == len(possible_movies) - 1:
                                or_str = "or "
                            movie_str += ", " + or_str + self.titles[movie_i][0]
                    response += movie_str + "?"
                    self.state = STATE.DISAMBIGUATE
                    return response
                else:
                    self.current_movie = self.titles[possible_movies[0]][0]
                    # Line or response? TODO
                    line = "Yes, " + self.titles[possible_movies[0]][0]
                    self.state = STATE.CONFIRM_MOVIE


        if self.state == STATE.ASK_SENTIMENT:
            response = "How do you feel about {}?".format("movie")

            self.state = STATE.CONFIRM_MOVIES_SENTIMENT
        elif self.state == STATE.CONFIRM_MOVIES_SENTIMENT and self.state != STATE.DISAMBIGUATE:
            # Check if have sentiment AND movie -- using movies in line extract title
            title_sentmt = self.extract_sentiment_for_movies(line)
            self.current_senti = self.extract_sentiment(line)

            if self.PREV_STATE == STATE.CLARIFY and self.current_senti is not None:
                title = self.find_movies_by_title(line)
                sentence = (self.titles[title[0]][0], self.current_senti)
                title_sentmt = [sentence]

            ambiguos_movies = []

            # TODO: use sentiment from last line too!!!
            # TODO: use movie from last line too!!! 
            # Otherwise....ask again
            missing_sentiment = True
            missing_movies = True
            movies_clarify_spelling = []

            for t_s in title_sentmt:
                t = t_s[0]
                s = t_s[1]
                self.possible_movie_list = self.find_movies_by_title(t)
                if len(self.possible_movie_list) > 1:
                    # Multiple movie match
                    ambiguos_movies.append(t)
                    missing_movies = False
                elif len(self.possible_movie_list) == 0 and self.creative:
                    # No movie match -- check if spelling error
                    year = re.findall(r"^(.*)\((\d{4})?(?:-)?(\d{4})?\)", t)
                    if len(year) == 0:
                        title_i2 = re.findall(r'^(.*)(?:, )(The$|An$|Le$|La$|Les$)', t.strip().lower().title())
                        if len(title_i2) == 0:
                            name = t.strip()
                        else:
                            name = title_i2[0][1] + " " + title_i2[0][0]
                    else:
                        title_i2 = re.findall(r'^(.*)(?:, )(The$|An$|Le$|La$|Les$)', year[0][0].strip().lower().title())
                        if len(title_i2) == 0:
                            name = year[0][0].strip()
                        else:
                            name = title_i2[0][1] + " " + title_i2[0][0]
                    poss_titles = self.find_movies_closest_to_title(name)
                    if len(poss_titles) == 0:
                        response = "I'm very meowy!!! I've never heard of '{}'... Can you tell me about another movie you like?".format(
                            name)
                        return response
                    year = re.findall(r"^(.*)\((\d{4})?(?:-)?(\d{4})?\)", self.titles[poss_titles[0]][0])
                    if len(year) == 0:
                        title_i2 = re.findall(r'^(.*)(?:, )(The$|An$|Le$|La$|Les$)', self.titles[poss_titles[0]][0].strip().lower().title())
                        if len(title_i2) == 0:
                            t_name = self.titles[poss_titles[0]][0].strip()
                        else:
                            t_name = title_i2[0][1] + " " + title_i2[0][0]
                    else:
                        title_i2 = re.findall(r'^(.*)(?:, )(The$|An$|Le$|La$|Les$)', year[0][0].strip().lower().title())
                        if len(title_i2) == 0:
                            t_name = year[0][0].strip()
                        else:
                            t_name = title_i2[0][1] + " " + title_i2[0][0]
                    self.possible_movie_list.append(poss_titles[0])
                    self.current_senti = title_sentmt[0][1]
                    response1 = 'Did you mean "{}"?'.format(t_name)
                    response2 = 'Ah, so you meant "{}"?'.format(t_name)
                    response3 = 'So did you mean "{}"?'.format(t_name)
                    response4 = 'Got it! So you meant "{}"?'.format(t_name)
                    response = self.get_random_line([response1, response2, response3, response4])

                    self.current_movie = t_name
                    self.state = STATE.CONFIRM_MOVIE
                    return response
                else:
                    missing_movies = False

                if s != 0:
                    missing_sentiment = False

            if len(title_sentmt) == 1 and title_sentmt[0][1] != 0:
                senti_str = self.get_random_line(["indeed have liked", "have liked", "feel good about", "have enjoyed", "feel positive about", "think highly of"])
                if title_sentmt[0][1] < 0:
                    senti_str = self.get_random_line(["did not like", "disliked", "dislike", "didn't like", "did not enjoy", "thought lowly of"])
                response1 = 'OK! Seems like you {} "{}"! '.format(senti_str, title_sentmt[0][0])
                response2 = 'Oh, so you {} "{}"! '.format(senti_str, title_sentmt[0][0])
                response3 = 'Got it, you appear to {} "{}"! '.format(senti_str, title_sentmt[0][0])
                response4 = 'I see you {} "{}"! '.format(senti_str, title_sentmt[0][0])
                response = self.get_random_line([response1, response2, response3, response4])

                if len(self.find_movies_by_title(title_sentmt[0][0])) == 0:
                    response += " But I haven't heard of that movie myself, nya! "

                self.PREV_STATE = None
                # self.state = STATE.SUBMIT # response to CLARIFY?
                self.state = STATE.CONFIRM_MOVIES_SENTIMENT
                self.movie_list.append(title_sentmt[0])
                self.current_movie = title_sentmt[0][0]
                if len(self.movie_list) != 0 and len(self.movie_list) % 5 == 0:
                    self.state = STATE.RECOMMEND
                elif len(ambiguos_movies) == 0:
                    response += self.get_random_line(["How do you feel about another movie? ", "What about other movies? ", "So about the other movies you've seen... ", "And so what of the other movies you've watched? "])

            if len(title_sentmt) > 1:
                senti_doc = {}

                if title_sentmt[0][1] < 0:
                    senti_doc[0] = self.get_random_line(["did not like", "disliked", "dislike", "didn't like", "did not enjoy", "thought lowly of"])
                else:
                    senti_doc[0] = self.get_random_line(["indeed have liked", "have liked", "feel good about", "have enjoyed", "feel positive about", "think highly of"])

                response2 = 'OK! You {} "{}"'.format(senti_doc[0],title_sentmt[0][0])
                response1 = 'Got it! You\'re the find of person who {} "{}"'.format(senti_doc[0],title_sentmt[0][0])
                response3 = 'I see you {} "{}"'.format(senti_doc[0],title_sentmt[0][0])
                response4 = 'Ah, so you {} "{}"'.format(senti_doc[0],title_sentmt[0][0])
                response = self.get_random_line([response1, response2, response3, response4])
                self.movie_list.append(title_sentmt[0])

                for i in range(1,len(title_sentmt)):
                    if title_sentmt[i][1] < 0:
                        senti_doc[i] =  self.get_random_line(["did not like", "disliked", "dislike", "didn't like", "did not enjoy", "thought lowly of"])
                    else:
                        senti_doc[i] = self.get_random_line(["indeed liked", "liked", "feel good about", "enjoyed", "feel positive about", "think highly of"])


                for i in range(1,len(title_sentmt)):
                    response += ' and you {} "{}"'.format(senti_doc[i], title_sentmt[i][0])
                    self.movie_list.append(title_sentmt[i])

                response += "."

                if len(self.movie_list) != 0 and len(self.movie_list) % 5 == 0:
                    self.state = STATE.RECOMMEND
            if missing_sentiment:
                # Movie but feel neutral
                if len(title_sentmt) == 1:
                    self.current_movie = title_sentmt[0][0]
                response2 = "I'm sorry, I'm not sure if you liked {}. Tell me more about it.".format(self.current_movie)
                response1 = "And how do you feel about {}? I want to learn more.".format(self.current_movie)
                response3 = "So, did you like {}? I'm interested.".format(self.current_movie)
                response4 = "And what are your thoughts about {}? It sounds interesting.".format(self.current_movie)
                response5 = "So what do you think about {}? It sounds intriguing.".format(self.current_movie)
                response = self.get_random_line([response1, response2, response3, response5])

                if len(self.find_movies_by_title(self.current_movie)) == 0:
                    response += " But I haven't heard of that movie myself, nya!"

                self.state = STATE.CONFIRM_MOVIES_SENTIMENT
                # TODO: HANDLE SEVERAL MOVIES
            if missing_movies:
                sentiment = self.extract_sentiment(line)
                if sentiment == 0:
                    response2 =  "I'm very meowy!!! My cat-human translator is having a fit again. I couldn't understand if you were talking about any movies. Can you tell me again? Tell me a movie you've watched."
                    response1 = "Merp, my meowy ears are too full of fluff. What movie are you talking about? "
                    response3 = "Hm, I'm not sure if you were talking about movies. Let's talk about movies. "
                    response4 = "Mrow? But what about movies you've seen? I'm not sure if that's a movie. "
                    response5 = "Nya!? Is that a movie? Let's talk about another movie. "
                    response = self.get_random_line([response1, response2, response3, response5])
                else:
                    str_sentiment = self.get_random_line(["to have indeed liked", "to like", "to feel good about", "to have enjoyed", "to feel positive about", "to think highly of"])
                    if sentiment < -1:
                        str_sentiment = self.get_random_line(["to not like", "to have disliked", "to dislike", "to have not liked", "to have not enjoyed", "to think lowly of"])
                    if self.current_movie != "":
                        # Check if talking about last movie
                        response2 = "Ok! So you seem {} the movie {}.".format(str_sentiment, self.current_movie)
                        response1 = "I see, so you {} the movie {}.".format(str_sentiment, self.current_movie)
                        response3 = "Oh, so you {} \"{}\".".format(str_sentiment, self.current_movie)
                        response4 = "Indeed, I see that you {} the movie {}.".format(str_sentiment, self.current_movie)
                        response5 = "Aha! I knew you {} the movie {}.".format(str_sentiment, self.current_movie)
                        ask_more1 =  "Can you tell me about another movie you've watched?"
                        ask_more2 = " And what about other movies you've seen?"
                        ask_more3 = " Also, what of other movies?"
                        ask = self.get_random_line([ask_more1, ask_more2, ask_more3])
                        response = self.get_random_line([response1 + ask, response2 + ask, response3 + ask, response5 + ask])

                    else:
                        response = "You seem {} it, but what movies are you talking about?".format(str_sentiment)

                self.state = STATE.CONFIRM_MOVIES_SENTIMENT
                    # self.current_movie = title_sentmt[0][0]
            # TODO: handle multiple movies
            ambiguos_movies.extend(movies_clarify_spelling)
            if len(ambiguos_movies) > 0:
                response1 = " I found multiple titles with similar names. Can you clarify? For instance, is it any of these? "
                response2 = " However, I found many titles with a similar name. Which one of these is it? "
                response3 = " But, which one of these are you talking about? "
                response4 = " Still, I'm not sure which of these movies you are talking about. "
                response5 = " Can you be more specific? Which one of these movies are you talking about? "
                response5 = " But meow! So many pawsibilities. Which movie are you talking about? "
                response6 = " But mew! Which of these movies are you talking about? "
                response += self.get_random_line([response1, response2, response3, response4, response5, response6])
                self.possible_movie_list = self.find_movies_by_title(ambiguos_movies[0])
                response += self.titles[self.possible_movie_list[0]][0]
                for i in range(1,len(self.possible_movie_list)):
                    response += ", " + self.titles[self.possible_movie_list[i]][0]

                for i in range(1,len(ambiguos_movies)):
                    self.possible_movie_list = self.find_movies_by_title(ambiguos_movies[i])
                    for p_index in self.possible_movie_list:
                        response += ", " + self.titles[p_index][0]
                response += "."
                self.current_senti = title_sentmt[0][1]
                self.state = STATE.DISAMBIGUATE
                return response

        elif self.state == STATE.SUBMIT:
            # Use previous response and state
            # TODO: confirm titles and sentiments before setting
            is_confirmation = None
            if re.findall(r'\byes\b|\byeah\b|\byep\b|\bye\b|\bsure\b|\byup\b', line.lower()):
                is_confirmation = True
            elif re.findall(r'\bno\b|\bnope\b|\bnah\b', line.lower()):
                is_confirmation = False

            if is_confirmation:
                # confirm movies and sentiment
                if self.PREV_STATE == STATE.RECOMMEND:
                    # response = "Thanks for confirming! Would you like to hear your recommendations now?"
                    # Set ratings
                    # self.user_ratings = self.set_ratings(self.user_ratings, self.extract_sentiment_for_movies(line))
                    self.state = STATE.RECOMMEND
            elif not is_confirmation:
                if self.PREV_STATE == STATE.RECOMMEND:
                    response = self.get_random_line(["OK, how about you tell me some other movies then?", "I see. What about other movies?", "Ok, tell me more."])
                    self.PREV_STATE = None
                    self.possible_movie_list = []
                    self.movie_list = []
                    self.state = STATE.CONFIRM_MOVIES_SENTIMENT
            else:
                self.state = STATE.ERROR
        elif self.state == STATE.CONFIRM_MOVIE:
            if re.findall(r'\byes\b|\byeah\b|\byep\b|\bye\b|\byah\b|\buh-huh\b|\byer\b', line.lower()):
                # TODO: if missing sentiment
                senti = self.get_like_word()
                if self.current_senti < 0:
                    senti = self.get_dislike_word()
                if self.current_senti == None or self.current_senti == 0:
                    response1 = "Ok, but I'm still unsure if you liked {}. Tell me more about it.".format(self.current_movie)
                    response2 = "Thanks for confirming, however, I'm not sure if you liked {}. Tell me more about it.".format(self.current_movie)
                    response3 = "Ok, but I'm still unsure if you liked {}. What about it?".format(self.current_movie)
                    response4 = "I see, but how do you feel about {}? I want to know more.".format(self.current_movie)
                    response5 = "Gotcha, but what are you're thought on {}? Tell me more about it.".format(self.current_movie)
                    response6 = "Lovely, but then how do you think about {}? I want to know more.".format(self.current_movie)
                    response = self.get_random_line([response1, response2, response3, response4, response5, response6])
                    self.state = STATE.CONFIRM_MOVIES_SENTIMENT
                else:
                    response1 = 'Got it, you {} "{}", tell me more about another movie you have seen.'.format(senti, self.current_movie)
                    response2 = 'Okay dokey, you {} the movie "{}", tell me more about another movie you have seen.'.format(senti, self.current_movie)
                    response3 = 'Coolio meow! You {} "{}", tell me more about another movie you have seen.'.format(senti, self.current_movie)
                    response4 = 'Nice, you {} the movie "{}", tell me more about another movie you have seen.'.format(senti, self.current_movie)
                    response = self.get_random_line([response1, response2, response3, response4])
                cur = (self.current_movie, self.current_senti)
                self.movie_list.append(cur)
                self.possible_movie_list = None
                self.state = STATE.CONFIRM_MOVIES_SENTIMENT
                self.PREV_STATE = None

                # Check if recommend?
            else:
                self.possible_movie_list.pop(0)
                if len(self.possible_movie_list) == 0:
                    response1 = "Meeo? I am out of idea then... Anyway, what is another movie that you like?"
                    response2 = "Nya meow? I'm not sure what you're talking about then. What else are you into?"
                    response = self.get_random_line([response1, response2])
                    self.possible_movie_list = None
                    self.current_movie = None
                    self.state = STATE.CONFIRM_MOVIES_SENTIMENT
                else:
                    response = "Did you mean {}?".format(self.titles[self.possible_movie_list[0]][0])
                    self.current_movie = self.possible_movie_list[0]
                    self.PREV_STATE = STATE.CLARIFY

        elif self.PREV_STATE == STATE.CLARIFY:
            if self.possible_movie_list == None:
                self.possible_movie_list = self.find_movies_closest_to_title(p_titles[0])
            if len(self.possible_movie_list) == 0:
                response = "Meeo? I never heard of this movie"
                self.possible_movie_list = None
                self.current_movie = None
            elif self.titles[current_movie_index] == self.possible_movie_list[0][0]:
                response = "Got it, you like {}".format(self.titles[current_movie_index])
                self.possible_movie_list = None
                self.PREV_STATE = None

        if len(self.movie_list) != 0 and len(self.movie_list) % 5 == 0:
            response += " By the way, "
            self.state = STATE.RECOMMEND

        if self.state == STATE.RECOMMEND:
            if len(self.movie_list) > 0:
                self.user_ratings = self.set_ratings(self.user_ratings, self.movie_list)
                # Only set recommend on first attempt, not every time...otherwise only get one movie. TODO: set on movie change, not when length is zero
                if len(self.rec_movie_index) == 0:
                    self.rec_movie_index = self.recommend(self.user_ratings, self.ratings)
                if len(self.rec_movie_index) == 0:
                    response += "\nI'm so meowy! I don't have any more movies to recommend you. How about telling me more about what other movies you've watched?"
                else:
                    rec_movie = self.titles[self.rec_movie_index.pop(0)][0]
                    rec1 = "\nI think you would like this movie: {}. Would you like to hear more?".format(rec_movie)
                    rec2 = "\nI highly recommend {}. Want to hear more?".format(rec_movie)
                    rec3 = "\nI think you'd " + self.get_like_word() + " {}. Want to hear more?".format(rec_movie)
                    rec3 = "\nYou'd totally " + self.get_like_word() + " {}! Want to hear more?".format(rec_movie)
                    recommend_str = self.get_random_line([rec1, rec2, rec3])
                    response += recommend_str
                self.state = STATE.SUBMIT
                self.PREV_STATE = STATE.RECOMMEND
            else:
                self.state = STATE.CONFIRM_MOVIES_SENTIMENT
                response = "I need to know more about what movies you've watched to recommend you anything."

        if self.state == STATE.ERROR:
            if self.PREV_STATE == STATE.RECOMMEND:
                response = "I'm very meowy!!! My cat-human translator is having a fit again. Can you tell me yes if you want me to recommend more movies, and no if you don't want me to recommend more movie?"
                self.state = STATE.SUBMIT
            else:
                response = "I'm very meowy!!! My cat-human translator is having a fit again. I couldn't understand if you were talking about any movies. Can you tell me again? Tell me a movie you've watched."
                self.state = STATE.CONFIRM_MOVIES_SENTIMENT
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return response

    # Sets and returns ratings based on each (title, sentiment) tuple
    def set_ratings(self, old_ratings, title_sentmt):
        ratings = np.copy(old_ratings)
        for t_s in title_sentmt:
            indices = self.find_movies_by_title(t_s[0])
            if len(indices) > 1:
                pass # TODO: ask to disambiguate
            ratings[indices] = t_s[1]
        return ratings

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

        text = text.strip()

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
        possible_titles = re.findall(r'"(.*?)"', preprocessed_input)

        if len(possible_titles) != 0:

            # possible_titles lower case
            possible_titles_l = []
            # possible_titles with capitalized first letter
            possible_titles_c = []

            for title in possible_titles:
                title = title.lower()
                possible_titles_l.append(title)
                title = title.title()
                possible_titles_c.append(title)

            return possible_titles_c
        else:
            possible_titles = re.findall(r"^(.*)(?= a lot| very much)+", preprocessed_input)
            if len(possible_titles) == 0:
                possible_titles = re.findall(
                    r"^(?:I |i )(?:do not |don't |did not |didn't |never )?(?:really |very much |truly |really reeally )?(?:like |liked |hate |hated |love |loved |dislike |disliked |enjoy |enjoyed |prefer |preferred )([\w\s]+)(?:!|.)?",
                    preprocessed_input)
            else:
                possible_titles = re.findall(
                    r"^(?:I |i )(?:do not |don't |did not |didn't |never )?(?:really |very much |truly |really reeally )?(?:like |liked |hate |hated |love |loved |dislike |disliked |enjoy |enjoyed |prefer |preferred )([\w\s]+)",
                    possible_titles[0])

            if len(possible_titles) == 0:
                # TODO: replace with more sentiment words eg., from Harvard hashmap
                # old_regex = "^(.*?)(?:(?: was | is )(?:good|great|fun|awesome|awful|terrible|horrible|lovely|terrific))(?:!|.)?"
                f_regex = r"^(.*?)(?:(?: was | is | are )(?:" + self.feelings_regex + "))(?:!|.)?"
                possible_titles = re.findall(
                    f_regex,
                    preprocessed_input)
                if len(possible_titles) != 0:
                    possible_titles = re.findall(
                        r'^(?:I |i )(?:thought |believed |think |believe )([\w\s]+)', possible_titles[0])
                # If it's still length 0....check if whole thing is one title
                if self.find_movies_by_title(preprocessed_input):
                    possible_titles.append(preprocessed_input)
                if len(possible_titles) == 0:
                    # Check if NOUN _is/are _sentiment_
                    possible_titles = re.findall(
                        r'^([\w\s]+)(?:\bis\b|\bare\b)', preprocessed_input)
                    if len(possible_titles) > 0:
                        first_p_title = possible_titles[0].strip().lower()
                        if first_p_title == 'you' or first_p_title == 'she' or first_p_title == 'he' or first_p_title == 'they':
                            del possible_titles[0]

            # possible_titles lower case
            possible_titles_l = []
            # possible_titles with capitalized first letter
            possible_titles_c = []

            for title in possible_titles:
                title = title.strip()
                title = title.lower()
                possible_titles_l.append(title)
                title = title.title()
                possible_titles_c.append(title)

            return possible_titles_c

    def extract_movie_title_default(self, movielist, target):
        if target.year is None:
            for i in range(len(self.titles)):
                title_i = self.titles[i][0].strip().lower().title()
                year = re.findall(r"^(.*)\((\d{4})?(?:-)?(\d{4})?\)", title_i)
                if len(year) == 0:
                    # TODO: definite articles in Spanish, Italian, and French, plus nominative definite articles in German.
                    # der, die, and das
                    title_i2 = re.findall(r'^(.*)(?:, The$|, An$|, Le$|, La$|, Les$)', title_i.strip())
                    if len(title_i2) == 0:
                        title_i3 = re.findall(r'^(?:An |The |Le |La |Les )?(.*)', title_i)
                        name = title_i3[0].strip()
                        if name == target.name:
                            movielist.append(i)
                    else:
                        name = title_i2[0].strip()
                        if name == target.name:
                            movielist.append(i)
                else:
                    title_i2 = re.findall(r'^(.*)(?:, The$|, An$|, Le$|, La$|, Les$)', year[0][0].strip())
                    if len(title_i2) == 0:
                        title_i3 = re.findall(r'^(?:An |The |Le |La |Les )?(.*)', year[0][0])
                        name = title_i3[0].strip()
                        if name == target.name:
                            movielist.append(i)
                    else:
                        name = title_i2[0].strip()
                        if name == target.name:
                            movielist.append(i)
        else:
            for i in range(len(self.titles)):
                title_i = self.titles[i][0].strip().lower().title()
                year = re.findall(r"^(.*)\((\d{4})?(?:-)?(\d{4})?\)", title_i)
                if len(year) == 0:
                    title_i2 = re.findall(r'^(.*)(?:, The$|, An$|, Le$|, La$|, Les$)', title_i.strip())
                    if len(title_i2) == 0:
                        title_i3 = re.findall(r'^(?:An |The |Le |La |Les )?(.*)', title_i)
                        name = title_i3[0].strip()
                        if name == target.name:
                            movielist.append(i)
                    else:
                        name = title_i2[0].strip()
                        if name == target.name:
                            movielist.append(i)
                else:
                    title_i2 = re.findall(r'^(.*)(?:, The$|, An$|, Le$|, La$|, Les$)', year[0][0].strip())
                    if len(title_i2) == 0:
                        title_i3 = re.findall(r'^(?:An |The |Le |La |Les )?(.*)', year[0][0])
                        name = title_i3[0].strip()
                        if len(year[0][2]) != 0 and int(year[0][2]) >= int(target.year) >= int(
                                year[0][1]) and name == target.name:
                            movielist.append(i)
                        else:
                            if len(year[0][1]) != 0 and int(year[0][1]) == int(target.year) and name == target.name:
                                movielist.append(i)
                    else:
                        name = title_i2[0].strip()
                        if len(year[0][2]) != 0 and int(year[0][2]) >= int(target.year) >= int(
                                year[0][1]) and name == target.name:
                            movielist.append(i)
                        else:
                            if len(year[0][1]) != 0 and int(year[0][1]) == int(target.year) and name == target.name:
                                movielist.append(i)

    def extract_movie_title_creative(self, movielist, target):
        name_rule = r'\b' + target.name + r'(?=[^\w]|\b)'
        if target.year is None:
            for i in range(len(self.titles)):
                title_i = self.titles[i][0].strip().lower().title()
                year = re.findall(r"^(.*)\((\d{4})?(?:-)?(\d{4})?\)", title_i)
                # title no year
                if len(year) == 0:
                    name = re.findall(name_rule, title_i)
                    if len(name) != 0:
                        movielist.append(i)
                else:
                    name = re.findall(name_rule, year[0][0])
                    if len(name) != 0:
                        movielist.append(i)
        else:
            for i in range(len(self.titles)):
                title_i = self.titles[i][0].strip().lower().title()
                year = re.findall(r"^(.*)\((\d{4})?(?:-)?(\d{4})?\)", title_i)
                # title no year
                if len(year) == 0:
                    name = re.findall(name_rule, title_i)
                    if len(name) != 0:
                        movielist.append(i)
                else:
                    name = re.findall(name_rule, year[0][0])
                    if len(year[0][2]) != 0 and int(year[0][2]) >= int(target.year) >= int(year[0][1]) and len(
                            name) != 0:
                        movielist.append(i)
                    else:
                        if len(year[0][1]) != 0 and int(year[0][1]) == int(target.year) and len(name) != 0:
                            movielist.append(i)

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
        title = title.strip().lower().title()
        title = re.findall(r'([^"]+)', title)
        if len(title) == 0: return []
        title = title[0].strip()
        if len(title) == 0: return []

        target = Movie()
        target_title = re.findall(r'^(.*)\((\d{4})(?:-)?\)', title)
        # movie no year
        if len(target_title) == 0:
            target_title2 = re.findall(r'^(.*)(?:, The$|, An$|, Le$|, La$|, Les$)', title)
            if len(target_title2) == 0:
                target_title3 = re.findall(r'^(?:An |The |Le |La |Les )?(.*)', title)
                target.name = target_title3[0].strip()
            else:
                target.name = target_title2[0]

        else:
            target.year = target_title[0][1].strip()
            target_title_temp = target_title[0][0].strip().lower().title()
            target_title2 = re.findall(r'^(.*)(?:, The$|, An$|, Le$|, La$|, Les$)', target_title_temp)
            if len(target_title2) == 0:
                target_title3 = re.findall(r'^(?:An |The |Le |La |Les )?(.*)', target_title_temp)
                target.name = target_title3[0].strip()
            else:
                target.name = target_title2[0]

        movielist = []

        # handle non creative mode
        if not self.creative:
            self.extract_movie_title_default(movielist, target)
        else:
            self.extract_movie_title_creative(movielist, target)

        return movielist

    def remove_punctuation(self, text):
        punc = "!\"#$%&'()*+,-./:;<=>?@[\]^`{|}~" # I removed _ puncutation to preserve NOT_ TODO: this make a difference?
        for p in punc:
            text = text.replace(p, '')
        return text

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
        # TODO: "!" as strong. Also due to "I hate the whole movie, but did like this one scene" --> decision is to not handle but
        
        # (0) Effectively remove movie titles
        maybe_movies = self.extract_titles(preprocessed_input)
        for m in maybe_movies:
            if len(self.find_movies_by_title(m)) > 0:
                # Probably a movie title
                preprocessed_input = preprocessed_input.replace(m, "movie_title") # ASSUMES: maybe_movies did not change format of original input

        # (1) handle negations: not liked --> not NOT_liked...negate all words until next punctuation
        negation_words = ["not", "didn't", "never", "no", "cannot", "shouldn't", "wouldn't", "don't"]
        end_punc = "!,.;?"
        negated = False
        strong_modified = False
        strong_modifier = ["really", "truly", "reeally", "super", "seriously", "very", "extremely", "especially", "exceptionally", "extraordinarily", "extra", "hugely", "vastly"]
        l_words = preprocessed_input.split(" ")
        for i in range(len(l_words)):
            word = l_words[i]
            if word in negation_words:
                negated = True
            if word in strong_modifier:
                strong_modified = True
            else:
                for punc in end_punc:
                    if punc in word:
                        negated = False
                        strong_modified = False
                if negated:
                    l_words[i] = "NOT_" + word
                if strong_modified:
                    l_words[i] = "VERY_" + l_words[i]
        negated_input = " ".join(l_words)

        # (2) standarize words with stemmer eg., liked --> like
        negated_input = self.remove_punctuation(negated_input)
        l_words = negated_input.split(" ")
        l_stemmed = []
        for i in range(len(l_words)):
            stemmer = PorterStemmer()
            l_stemmed.append(stemmer.stem(l_words[i]))

        # (3) count words with sentiment
        f_positive = 0
        f_negative = 0
        strong_sentiment_pos = False
        strong_sentiment_neg = False
        for i in range(len(l_words)):
            word = l_words[i]
            is_strong = False
            strong_words = ["love", "loved", "hate", "terrible", "awful"]
            if word in strong_words:
                is_strong = True

            if word not in self.sentiment:
                word = l_stemmed[i]

            # Is strong sentiment?
            if word in strong_words:
                is_strong = True
            if word.isupper():
                is_strong = True

            # Remove "NOT_"; TODO: what if sentence like "I don't not like it...." --> handle multiple negations
            is_negated = "NOT_" in word
            if is_negated:
                word = word.replace("NOT_", "")
            if "VERY_" in word:
                is_strong = True
                word = word.replace("VERY_", "")

            # lowercase to find in dictionary
            word = word.lower()

            # Get sentiment of word
            # Hacky workaround issue of words being incorrectly stemmed eg., enjoy --> enjoi
            sentiment_map = {"enjoi" : "pos"}
            for key in sentiment_map:
                self.sentiment[key] = sentiment_map[key]
            if word in self.sentiment:
                is_pos = False
                if self.sentiment[word] == "pos":
                    is_pos = True
                if is_negated:
                    is_pos = not is_pos

                # Add to counts
                if is_pos:
                    f_positive += 1 + is_strong # Count strong modifiers as two of those words

                    if is_strong:
                        strong_sentiment_pos = True
                else:
                    # neg
                    f_negative += 1 + is_strong

                    if is_strong:
                        strong_sentiment_neg = True
        lambda_threshold = 1
        total = f_negative + f_positive
        if total == 0:
            return 0
        if f_negative == 0 or (f_positive) / (f_negative) > lambda_threshold:
            if self.creative and strong_sentiment_pos:
                return 2
            return 1
        if f_positive == 0 or (f_negative) / (f_positive) > lambda_threshold:
            if self.creative and strong_sentiment_neg:
                return -2
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
        clause = re.split(" though | but |[.;!?]", preprocessed_input)
        movie_sent = []
        sentiment = 0
        for c in clause:
            if c != None:
                p_sentiment = sentiment
                sentiment = self.extract_sentiment(c)
                if sentiment == 0:
                    # Check if modification of previous clause
                    negation_words = ["not", "didn't", "never", "no", "cannot", "shouldn't", "wouldn't"]
                    negated = False
                    for n in negation_words:
                        if n in c:
                            negated = True
                    if negated:
                        sentiment = -1 * p_sentiment
                movies = self.extract_titles(c)
                
                for m in movies:
                    movie_sent.append((m, sentiment))
        return movie_sent

    def calculate_levenshtein_distance(self, string1, string2):
        matrix = np.zeros([len(string1) + 1,len(string2) + 1])
        for i in range(len(string1) + 1):
            matrix[i][0] = i
        for i in range(len(string2) + 1):
            matrix[0][i] = i

        for i in range(1, len(string1) + 1): # row
            for j in range(1, len(string2) + 1): # column
                if string1[i-1] == string2[j-1]:
                    matrix[i][j] = matrix[i-1][j-1]
                else:
                    matrix[i][j] = min(matrix[i-1][j], matrix[i][j-1], matrix[i-1][j-1] + 1) + 1
        result = matrix[len(string1)][len(string2)]
        return result

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
        result_list = []
        for i in range(len(self.titles)):
            title_year = self.get_title_years(self.titles[i][0], i)
            tname = title_year[0].strip()
            year = re.findall(r"^(.*)\((\d{4})?(?:-)?(\d{4})?\)", tname)
            if len(year) == 0:
                title_i2 = re.findall(r'^(.*)(?:, )(the$|an$|le$|la$|les$)', tname.strip())
                if len(title_i2) == 0:
                    name = tname.strip()
                else:
                    name = title_i2[0][1] + " " + title_i2[0][0]
            else:
                title_i2 = re.findall(r'^(.*)(?:, )(the$|an$|le$|la$|les$)', year[0][0].strip())
                if len(title_i2) == 0:
                    name = year[0][0].strip()
                else:
                    name = title_i2[0][1] + " " + title_i2[0][0]
            target_name = str(title.lower().split(',')[0]).strip('""')
            min_dist = self.calculate_levenshtein_distance(name, target_name)
            if min_dist <= max_distance:
                result_list.append([i,min_dist])

        final_list = []
        min_score = max_distance + 1
        for element in result_list:
            if element[1] < min_score:
                min_score = element[1]
                final_list.clear()
                final_list.append(element[0])
            else:
                if element[1] == min_score:
                    final_list.append(element[0])

        return final_list

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
        narrowed_cand = []

        # Get year and title info of candidates
        candidate_title_years_index = []
        most_recent_year = 0
        oldest_year = 9999
        find_oldest = "oldest" in clarification
        find_recent = "most recent" in clarification
        for index in candidates:
            # TODO: not all titles have years -- make year optional::: Use helper function
            title_year = self.get_title_years(self.titles[index][0], index)
            year = int(title_year[1]) # TODO: if two years?
            title = title_year[0]
            candidate_title_years_index.append(title_year)

            if year > most_recent_year:
                most_recent_year = year
            if year < oldest_year:
                oldest_year = year

        # Get by year
        if find_oldest or find_recent:
            for t_year in candidate_title_years_index:
                # print(t_year[1], find_recent, find_oldest, most_recent_year, oldest_year)
                if t_year[1] == most_recent_year and find_recent:
                    narrowed_cand.append(t_year[3])
                if t_year[1] == oldest_year and find_oldest:
                    narrowed_cand.append(t_year[3])


        # Get by order word
        orders = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"]
        numbers = re.findall(r'\d+', clarification)
        for i in range(len(orders)):
            o = orders[i]
            if o in clarification:
                if i < len(candidates):
                    narrowed_cand.append(candidates[i])

        # Get by numbers
        for n in numbers:
            index = int(n) - 1
            year = int(n)
            # Check if index given
            if index < len(candidates) and not candidates[index] in narrowed_cand:
                narrowed_cand.append(candidates[index])
            elif year > 999 and year < 9999:
                # Check if year given
                for t_year in candidate_title_years_index:
                    if year == t_year[1] or year == t_year[2]:
                        # Matched year
                        narrowed_cand.append(t_year[3])

        # For not year search -- title search
        self.creative = True
        # If clarification is only one title
        ccandidates = self.find_movies_by_title(clarification.strip())
        result = [value for value in candidates if value in ccandidates]
        narrowed_cand.extend(result)

        # TODO: If clarifcation has extra words in it
        if len(narrowed_cand) <= 0: # CUZ IT'S NOT WORKING exactly
            clarification = " " + clarification + " "
            # Remove common words
            clarification = clarification.replace(" the ", " ").replace(" la ", " ").replace(" el ", " ").replace(" les ", " ").replace(" a ", " ").replace(" an ", " ").replace(" and ", " ").replace(" or ", " ").replace(" of ", " ")
            poss_titles = clarification.split(" ")
            for t in poss_titles:
                result = []
                t = t.lower()
                if t != "":
                    for ty in candidate_title_years_index:
                        title = ty[0]
                        title = " " + title + " "
                        p_t = " " + t + " "
                        if p_t in title:
                            # Maybe is the title they meant 
                            result.append(ty[3])
                narrowed_cand.extend(result)

        # if len(narrowed_cand) <= 0: # In case of "The Last of Us"
        if re.findall(r"\blast\b", clarification):
            narrowed_cand.append(candidates[len(candidates) - 1])

        if len(narrowed_cand) <= 0:
            narrowed_cand = candidates
        return narrowed_cand

    # Str: movie title (optional: year-year)
    # Returns: tuple (title, year1, year2 = 0, index = 0)
    def get_title_years(self, title, index = 0):
        # Process title
        processed_title = title.lower().strip()
        date_regex = "(?:\((\d{4}\s?-?\s?(\d{4})?)\))"
        year_regex = '(?:.+)?(?:, (?:the|an|a))?(?:.*)' + date_regex
        l_year = re.findall(year_regex, processed_title)
        year = 0
        year2 = 0
        title_r = ""
        if len(l_year) > 0 and not isinstance(l_year[0], str):
            # 2nd capture group / 2nd year
            year = l_year[0][0].split("-")[0] # Capture first year only in ####-####
            year2 = l_year[0][1]

        if year != 0:
            title_regex = '(.+)?(?:, (?:the|an|a))?(?:.*)' + date_regex
            title_r = re.findall(title_regex, processed_title)[0][0]
        else:
            title_regex = '(.+)?(?:, (?:the|an|a))?(?:.*)'
            title_r = re.findall(title_regex, processed_title)[0]
        if year != "":
            year = int(year)
        if year2 != "":
            year2 = int(year2)
        return (title_r, year, year2, index)


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
        binarized_ratings = np.where((ratings > threshold) & (ratings != 0), max(threshold + 1, 1), ratings)
        binarized_ratings = np.where((binarized_ratings <= threshold) & (binarized_ratings != 0), -1, binarized_ratings)
        binarized_ratings = np.where((binarized_ratings >= max(threshold + 1, 1)) & (binarized_ratings != 0), 1,
                                     binarized_ratings)

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
        # fix error double scalar
        norms = np.linalg.norm(u) * np.linalg.norm(v)
        e = 0.0000000001 # HACKY WORKAROUND FOR NOW....
        if norms < 0.0000000001:
            similarity = np.dot(u, v) / (norms + e)
        else: 
            similarity = np.dot(u, v) / (norms)
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

        def get_similarities(unrated_movie_row, ratings_matrix):
            # Get list of other movies' similarities to this movie that was not rated by user
            return np.apply_along_axis(self.similarity, 1, ratings_matrix, unrated_movie_row)

        # Populate this list with k movie indices to recommend to the user.
        recommendations = []

        # Calculate only for unknown movie ratings (ie., 0 in user ratings)
        zero_indices = np.nonzero(user_ratings==0)[0] # TODO: not sure if faster than single for loop
        nonzero_indices = np.nonzero(user_ratings!=0)[0]
        unrated_movies = ratings_matrix[zero_indices, :] # select rows of movies not rated by user to compare against other movies
        # (unrated movies) to (list of all other movies' similarity score to that unrated movie)
        # NOTE: Only need to get movie similarities that was rated by user -- otherwise it would multiply by 0 (the rating given by user) when taking mean
        mega_similarities = np.apply_along_axis(get_similarities, 1, unrated_movies, ratings_matrix[nonzero_indices])
        # 1D Predicted rating for each unrated movie, in order (shape: num unrated movies) -- take the "mean" by matrix multipliction
        #       predicted ratings = mean of my other ratings, weighted by their similarities to unrated movie
        mega_pred_rating_i = mega_similarities @ user_ratings[nonzero_indices]
        best_unrated_movies_indices = np.argsort(mega_pred_rating_i)[-k:]
        # Indices coorespond to original indices in zero_indices
        recommendations = [zero_indices[index] for index in best_unrated_movies_indices]
        recommendations.reverse()
        1
        # WORKS, but too slow!!!!
        # predicted_ratings = [] # (predicted rating, index)
        # # Get similarity
        # zero_indices = np.nonzero(user_ratings==0)[0] # np.where(user_ratings == 0)[0] # indices with zeroes in 1D array. TODO: not sure if faster than single for loop
        # for movie_i in range(len(user_ratings)):
        #     if user_ratings[movie_i] == 0: # Missing info --> get predicted rating
        #         # (1) how similar is movie i compared to other movies (using other user ratings); has shape of num movies
        #         similarities = np.apply_along_axis(self.similarity, 0, np.transpose(ratings_matrix), ratings_matrix[movie_i])
        #         # (2) Get predicted rating of movie i with weighted average using how (similar movie j is to i) * (movie j rating by user)
        #         # weighted_rating = np.multiply(similarities, user_ratings) # (dot product, but without summing)
        #         pred_rating_i = np.dot(similarities, user_ratings) # / np.sum(weighted_rating)
        #         # Keep k highest prediction ratings
        #         predicted_ratings.append((pred_rating_i, movie_i))
        # predicted_ratings.sort(key=lambda x: x[0], reverse=True)
        # recommendations = [item[1] for item in predicted_ratings[:k]]
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
        
        Meowy is a cat chatbot for all your cat-bot waifu dreams! Ask Meowy what you feel about various movies, and they will recommend you a movie!
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
