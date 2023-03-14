




# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
from nltk.metrics import edit_distance
from numpy.linalg import norm
import random
import warnings
warnings.filterwarnings("ignore", message="invalid value encountered in double_scalars")

#from nltk.tokenize import word_tokenize

import re

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
        self.main_dict, self.id_to_title = self.setup_data()
        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################
        ratings = self.binarize(ratings, threshold=2.5)
        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = ratings
        self.movies_rated = set()
        self.user_ratings = np.zeros(9125)
        self.clarify = False

        self.disambiguate_value = False
        self.spell_check_value = False
        self.sentiment_mode= False
        self.sentiment_phrase= ""
        self.extracted_movie = ""
        self.rec_mode = False
        self.reccomend_index = 0

        self.all_movies = []
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
        greeting_message = "" 
        if self.creative:
            messages = ["What's good! Let's get started!", "How we doing fam, how can I help!", "My homie, what's up!"]
            greeting_message = random.choice(messages)
        else:
            messages = ["How can I help you?", "How can I be of assistance?", "What brought you here today?"]
            greeting_message = random.choice(messages)


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

        goodbye_message = "" 
        if self.creative:
            messages = ["Have a nice day fam!", "My fam, have a good one", "Glad I could help bruh!", "Hope to see you back soon fam!"]
            goodbye_message = random.choice(messages)
        else:
            messages = ["Have a nice day", "I hope I was helpful!", "Have a good!"]
            goodbye_message = random.choice(messages)


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

        #It'll have two modes reccomendation mode and not reccomendation mode 
        response = ""
        #if line == "Who are you<"
        
        if self.creative:
            if not self.rec_mode:
                if self.clarify:
                    #print("clarify")
                    if (self.disambiguate_value):
                        # if holder_line == []:
                        #     self.disambiguate_value = False
                        #     self.spell_check_value = False
                        #     self.sentiment_value = False
                        #     self.clarify = False 
                        #     response += "I can't figure out which movie you are referring to. Let's start over, please tell me about a movie you have seen"                    
                        #holder_line = self.extract_titles(line)
                        holder_line = line
                        final_value = self.disambiguate(holder_line, self.all_movies)
                        # or 
                        #final_value = self.disambiguate(holder_line[0], self.all_movies)

                        if final_value == []:
                            self.disambiguate_value = False
                            self.spell_check_value = False
                            self.sentiment_value = False
                            self.clarify = False 
                            #CREATE CHOICES
                            #"I can't figure out which movie you are referring to. Let's start over, please tell me about a movie you have seen"
                            #JDM HERE 
                            #random_didnt_track = ["I can't figure out which movie you are referring to. Let's start over, please tell me about a movie you have seen"]
                            random_didnt_track = ["Dude, I'm totally lost. Like, which movie are you even talking about? Let's just, like, start over and tell me about a sick movie you've seen.",
"Yo, bro, I'm hella confused right now. What movie you talking about? Let's start fresh and you tell me about a rad flick you've watched.",
"Bruh, I'm so lost right now. Like, what movie are you even referring to? Can we just start again and talk about a dope movie you've seen?",
"Bro, I'm like so lost, I don't even know what movie you're talking about. Let's just like, start over, and you tell me about a movie that had you like, 'woah, dude, that was epic!'"]
                            #random_choices = ["I can't figure out which movie you are referring to. Let's start over, please tell me about a movie you have seen", "I didn't track which movie you meant, let's start over"]
                            response += random.choice(random_didnt_track) 
                        else:    
                            self.extracted_movie = final_value[0]
                            self.disambiguate_value = False
                        # we need to set the value of final_value to self.extracted_movie
                    elif(self.spell_check_value):
                        if (line[0].lower() == "n"):
                            self.disambiguate_value = False
                            self.spell_check_value = False
                            self.sentiment_value = False
                            self.clarify = False 
                            #CREATE CHOICES
                            #random_didnt_get = ["I can't figure out which movie you are referring to. Let's start over, please tell me about a movie you have seen"]
                            random_didnt_get = [ ["Dude, I'm totally lost. Like, which movie are you even talking about? Let's just, like, start over and tell me about a sick movie you've seen.",
"Yo, bro, I'm hella confused right now. What movie you talking about? Let's start fresh and you tell me about a rad flick you've watched.",
"Bruh, I'm so lost right now. Like, what movie are you even referring to? Can we just start again and talk about a dope movie you've seen?",
"Bro, I'm like so lost, I don't even know what movie you're talking about. Let's just like, start over, and you tell me about a movie that had you like, 'woah, dude, that was epic!'"]]

                            response += random.choice(random_didnt_get) 
                            #response += "I can't figure out which movie you are referring to. Let's start over, please tell me about a movie you have seen"
                        if (line[0].lower() == "y"):
                            self.spell_check_value = True
                            #print("hi_spellcheck")

                    #print("random_note_after")
                    if self.clarify:
                        sentiment_value = 0
                        if self.sentiment_mode:
                            sentiment_value = self.extract_sentiment(line)
                        else:
                           # print(self.sentiment_phrase)
                            sentiment_value = self.extract_sentiment(self.remove_titles(self.sentiment_phrase))

                        #print(sentiment_value)
                        if sentiment_value == 0:
                            #print("no sentiment found")
                            #CREATE CHOICES
                            #no_sentiment = ["I can't find any sentiment please tell me more about"]
                            no_sentiment = ["Yo, bro, I'm not getting any vibes here. Can you tell me more about what you're feeling about",
"Dude, I'm not picking up any energy. Can you like, talk more about what's going on with",
"Bruh, I'm not feeling any sentiment from you. Tell me more about what's up with",
"Bro, I'm not getting any vibes from what you're saying. Can you like, give me more context about"]

                            #"I can't find any sentiment please tell me more about
                            response += random.choice(no_sentiment) +  " \'" + self.id_to_title[str(self.extracted_movie)] + "\'"
                            self.sentiment_mode = True
                            self.clarify = True
                        elif sentiment_value == 1:
                            self.user_ratings[int(self.extracted_movie)] = 1
                            self.movies_rated.add(self.extracted_movie)
                            #CREATE CHOICES
                            #sentiment_1_1 = ["I can tell you liked"]
                            sentiment_1_1 = ["Bro, I can totally tell you were digging", "Dude, I can tell you were totally feeling", "Yo, I can tell you were into", "Bruh, I can totally tell that you liked"]
                           #"I can tell you liked "
                            response +=  random.choice(sentiment_1_1)+ " \'" +  self.id_to_title[str(self.extracted_movie)] + "\'"
                            #sentiment_1_2 = ["Please tell me about a movie you have seen"]
                            sentiment_1_2 = ["Yo, bro, hit me up with a movie you've seen lately.",
"Dude, tell me about a movie you've watched recently.",
"Bruh, what's a  movie you've seen lately? Let me know.",
"Bro, give me the scoop on a sick movie you've watched. I need something to check out."]

                            #"\nPlease tell me about a movie you have seen"
                            response += "\n" + random.choice(sentiment_1_2)
                            self.disambiguate_value = False
                            self.spell_check_value = False
                            self.sentiment_value = False
                            self.clarify = False 

                        elif sentiment_value == -1:
                            self.user_ratings[int(self.extracted_movie)] = -1
                            self.movies_rated.add(self.extracted_movie)
                            #CREATE CHOICES
                            #sentiment_2_1 = ["I can tell you didn't like"]
                            sentiment_2_1  = ["Bro, I can totally tell you weren't feeling",
"Dude, I could tell that you didn't rock with",
"Yo, I could totally tell you weren't into",
"Bruh, it was pretty clear that you didn't like"]
                            #"I can tell you didn't like \'"
                            response +=  random.choice(sentiment_2_1)+ " \'" + self.id_to_title[str(self.extracted_movie)] + "\'"
                            sentiment_2_2 = ["Yo, bro, hit me up with a movie you've seen lately.",
"Dude, tell me about a movie you've watched recently.",
"Bruh, what's a  movie you've seen lately? Let me know.",
"Bro, give me the scoop on a sick movie you've watched. I need something to check out."]                            
#"\nPlease tell me about a movie you have seen"
                            response += "\n" + random.choice(sentiment_2_2)
                            self.disambiguate_value = False
                            self.spell_check_value = False
                            self.sentiment_value = False
                            self.clarify = False 

                    # see if there is sentiment in the sentence without the movie title 
                    # if there is we are done and can continuie
                    # if there isn't we should use movie title which we know we will have to ask how they felt about the movie 
                    # and set self.clarify to True
                    # and set it equal to the sentiment phrase ?
            
                else:
                    value = self.extract_titles(line)
                    if value == []:
                        value_detected = False
                        # code for arbitrary input and identifying and responding to emotion 
                        phrases_to_check = {"Can you", "What is"}
                        phrases_to_check_responses = {"Can you": ["Sadly I cannot", "I cannot", "In no way can I"], "What is": ["I don't know what", "I have no clue what"]}
                        #make phrases to check responses a list and include many possible responses
                        #work on cap sensitivity for this section as well
                        for word in phrases_to_check:
                            if word.lower() in line.lower():
                                line = line[line.find(word) + len(word):].replace(" me ", " you ")
                                line = line.replace(" my ", " your ")
                                line = line.replace(" I ", " you ")
                                while line[len(line) - 1] == "?":
                                    line = line[:len(line)-1]
                                response += random.choice(phrases_to_check_responses[word]) + line #replace me with you
                                if word == "What is":
                                    response += " is"
                                value_detected = True
                                continue


                            invert_set = {'not',"n't",'never', 'didn\'t', 'never'}
                            tokens = re.findall(r"\w+(?:'\w+)?|\S+", line)

                            if value_detected == False:
                                emotion_words = {"happy", "joyful", "elated", "excited", "pleased", "content", "thankful", "grateful", "blessed", "blissful", "ecstatic", "radiant", "thrilled", "exhilarated", "jubilant", "enthusiastic", "optimistic", "hopeful", "inspired", "eager", "amazed", "overjoyed", "uplifted", "victorious", "confident", "loving", "compassionate", "appreciative", "gracious", "harmonious"}
                                emotion_word_neg = {"sad", "angry", "depressed", "miserable", "down", "unhappy", "heartbroken", "gloomy", "hopeless", "despairing", "melancholy", "sorrowful", "anguished", "disappointed", "regretful", "disheartened", "dismayed", "pessimistic", "discouraged", "lonely", "abandoned", "rejected", "betrayed", "despondent", "powerless", "fearful", "anxious", "stressed", "frustrated", "disgusted", "enraged", "resentful"}
                                for i, word in enumerate(tokens):
                                    if word in emotion_words:
                                        if i > 0 and (tokens[i-1] in invert_set):
                                            #"I am sorry to hear you are "
                                            #response_negative = ["I am sorry to hear you are"]
                                            response_negative = ["Dude, that sucks that you're feeling",
"Bro, sorry to hear you're",
"Yo, that's a bummer that you're",
"Bruh, that's rough that you're feeling"]



                                            response +=  random.choice(response_negative)+  " " + tokens[i-1] + " " + word
                                        else:
                                            #response_positive = ["I am glad to hear you are"]
                                            response_positive = ["Dude, that's sick that you're feeling",
"Bro, stoked to hear you're",
"Yo, that's awesome that you're feeling, man",
"Bruh, it's great to hear that you're"]



                                            #"I am glad to hear you are "
                                            response += random.choice(response_positive)+ " " + word
                                        value_detected = True
                                        continue
                                    
                                    if word in emotion_word_neg:
                                        if i > 0 and (tokens[i-1] in invert_set):
                                            #"I am glad to hear you are "
                                            response_positive = ["Dude, that's sick that you're feeling",
"Bro, stoked to hear you're",
"Yo, that's awesome that you're feeling, man",
"Bruh, it's great to hear that you're"]
                                            response += random.choice(response_positive)+ " " + tokens[i-1] + " " + word
                                        else:
                                            response_negative = ["Dude, that sucks that you're feeling",
"Bro, sorry to hear you're",
"Yo, that's a bummer that you're",
"Bruh, that's rough that you're feeling"]
                                            #"I am sorry to hear you are "
                                            response += random.choice(response_negative) + " " + word
                                        value_detected = True
                                        continue

                        if not value_detected: 
                            generic_response = ["Nah, bro, not feeling that convo. Let's hit up some movies instead!",
"Eh, not really vibing with that topic. Wanna chat about some movies instead?",
"Meh, not really down to talk about that rn. Let's switch to movies, dude!",
"Nah, that's not the move, my guy. Let's get back to movies, alright?"]
                 
                            #"Hm, that's not really what I want to talk about right now, let's go back to movies"
                            response += random.choice(generic_response)

                    elif len(value) >1:
                        to_many = ["I detected to many things within quotes fam", "You didn't follow the formatting right", "Follow the rules fam so I can do my job "]
                        #"I detected to many things within quotes"
                        response += random.choice(to_many)
                    elif len(value) == 1:
                       #print("main")
                        #run it through find_movies_by_title (which will now include widen the tunnel)
                        # this will also include find_movies_closest_to_title if there is nothing from above

                        get_title = self.find_movies_by_title(value[0])
                        
                        if get_title == []:
                            #none_found = ["I can't find this movie or any similar to it"]
                            none_found  = ["Dude, can't seem to locate that flick or anything like it!",
"Sorry, bro, can't find that movie or anything similar.",
"Yo, can't find that movie or anything even close to it, man!",
"Bruh, I'm searching but can't find that movie or anything remotely similar!"]



                            #"I can't find this movie or any similar to it"
                            response += random.choice(none_found)
                        elif len(get_title) == 1:
                            if not (self.disambiguate_value) and not (self.spell_check_value):
                                sentiment_value = self.extract_sentiment(self.remove_titles(line))
                                if sentiment_value == 0:
                                    #no_sentiment = ["I can't find any sentiment please tell me more about"]
                                    no_sentiment= ["Can't catch any feelings, bro. Gimme more deets!",
"Sorry, man, not getting any vibes. Give me more info, dude!",
"No vibes, my guy. Can you fill me in some more?",
"Not getting any feels, dude. Can you elaborate?"]
                                    
                                    #"I can't find any sentiment please tell me more about
                                    response += random.choice(no_sentiment) + " \'" + self.id_to_title[str(get_title[0])] + "\'"
                                    self.sentiment_mode = True
                                    self.clarify = True
                                    self.extracted_movie = get_title[0]
                                elif sentiment_value == 1:
                                    self.user_ratings[get_title[0]] = 1
                                    self.movies_rated.add(get_title[0])
                                    #positive_sentiment =["I can tell you liked"]
                                    positive_sentiment = ["Dude, I can tell you were totally digging",
"Bro, I can tell you were big time into",
"Yo, I can tell you were hooked on!",
"Bruh, I can tell your jam is"]
                                    #"I can tell you liked
                                    response += random.choice(positive_sentiment) + " \'" + self.id_to_title[str(get_title[0])] + "\'"
                                elif sentiment_value == -1:
                                    self.user_ratings[get_title[0]] = -1
                                    self.movies_rated.add(get_title[0])
                                    #negative_sentiment = ["I can tell you disliked"]
                                    negative_sentiment = ["Dude, I can tell you were hating on",
"Bro, I can tell you did not rock with",
"Yo, I can tell you were totally not feeling",
"Bruh, I can tell you were not vibing with"]
                                    response += random.choice(negative_sentiment)+ " \'" + self.id_to_title[str(get_title[0])] + "\'"
                            else:
                                #print("here")
                                #(self.remove_titles(line))
                                self.sentiment_phrase = self.remove_titles(line) #set self.sentiment phrase to the original line value so we can access after the  movie is found
                                if self.spell_check_value:
                                    if len(get_title) == 1:
                                        #"Did you mean
                                        length_one = ["Did you mean", "Fam maybe you meant one of:" , "Maybe you meant one of:"]
                                        response += random.choice(length_one) + " \'" + self.id_to_title[str(get_title[0])] + "\'"
                                        self.extracted_movie = get_title[0]
                                        self.clarify = True
                            #JDM HERE 
                        else: #(self.disambiguate_value) or (self.spell_check_value):
                            self.disambiguate_value = True
                            #print("here")
                            self.sentiment_phrase = self.remove_titles(line)
                            all_movies = " "
                            for movie in get_title:
                                all_movies += "\'" + self.id_to_title[str(movie)] + "\'" + ", "
                            response_did_you = ["Fam, did you mean", "Maybe you meant", "Bro bro maybe you meant"]
                            #"Did you mean
                            response += random.choice(response_did_you) + " " + all_movies
                            self.all_movies = get_title
                            self.clarify = True
            # add a case if they say so or we run out of movies to recommend
            if len(self.movies_rated) > 4 and self.reccomend_index < 9:
                self.rec_mode = True
                if (self.reccomend_index == 0) or (line[0].lower() == "y"):
                    #I suggest you watch this movie "
                    #response_zero = ["I suggest you watch this movie"]
                    response_zero = ["Dude, you gotta watch this movie I suggest, it's freaking awesome!",
"Bro, trust me on this, you gotta check out this movie I'm suggesting.",
"Yo, you won't regret it, watch the movie I suggest, it's legit!",
"Bruh, you need to see this movie I'm suggesting, it's sick!"]
                    response +=  "\n " +  random.choice(response_zero)
                    return_recommend = self.recommend(self.user_ratings, self.ratings, k=10, creative=False)
                    response += "\'" + self.id_to_title[str(return_recommend[self.reccomend_index])] + "\'"
                    #another_suggestion = ["Would you like another suggestion?"]
                    another_suggestion = ["Yo dude, you want another suggestion?", "Bruh, you feeling another movie or what?", "Bro, you wanna hear about another sick flick?",  "Ay man, you down for another recommendation or what?"]
                    #Would you like another suggestion?"
                    response +=  "\n " + random.choice(another_suggestion)
                    self.reccomend_index += 1
                elif (self.reccomend_index != 0) and line[0].lower() == "n":
                    not_equal_zero = ["Yo fam, thanks for coming and using my chatbot, enter \':quit\' to fully quit", "Hey bro bro, it's been a pleasure enter \':quit\' to fully quit"]
                    #"Thank you for using my chatbot, enter \':quit\' to fully quit"
                    response += random.choice(not_equal_zero)
                elif (self.reccomend_index != 0):
                    dont_understand = ["I don't understand, please try again. Enter \':quit\' to fully quit, enter 'yes' to get another recommendation or 'no' to stop getting recommendations", "Bruh, I don't understand, please try again. Enter \':quit\' to fully quit, enter 'yes' to get another recommendation or 'no' to stop getting recommendations", "Bro, I don't understand, please try again. Enter \':quit\' to fully quit, enter 'yes' to get another recommendation or 'no' to stop getting recommendations", "Yo, I don't understand, please try again. Enter \':quit\' to fully quit, enter 'yes' to get another recommendation or 'no' to stop getting recommendations"]
                    #"I don't understand, please try again. Enter \':quit\' to fully quit, enter 'yes' to get another recommendation or 'no' to stop getting recommendations"
                    response += random.choice(dont_understand)
            if self.reccomend_index == 9:
                #end_time = ["Thank you for using my chatbot, we are out of suggestions, enter \':quit\' to fully quit"]
                end_time =  ["Thanks for chatting, dude! We're all out of ideas, so type ':quit' to bail.",                   "Yo, thanks for hanging! We're tapped out, so enter ':quit' to peace out.",                   "Bro, you're awesome for using my bot, but we're fresh out of ideas. Enter ':quit' to bounce.",                   "Hey man, thanks for using my chatbot! We're out of suggestions, so type ':quit' to dip."]
                 #"Thank you for using my chatbot, we are out of suggestions, enter \':quit\' to fully quit"
                response += random.choice(end_time)
                
                #for value in return_recommend:
                    #response += " " + self.id_to_title[str(value)]

        ##### Below this line is not creative mode
        else:
           response = ""
           if not self.rec_mode:
                value = self.extract_titles(line)
                if value == []:
                    random_dont_understand = ["I don't understand, please try again", "This didn't make sense, please try again", "Please try again following my instructions", "Can you please try again following instructions"]
                    response = random.choice(random_dont_understand) 
                elif len(value) == 1:
                    #random_replies = ["I detected one movie", "One movie was sucesfully detected", "The following movie was detected", "I was able to do my job because I detected"]
                    #response = random.choice(random_replies) + " " + value[0]
                    get_title = self.find_movies_by_title(value[0])
                    if get_title == []:
                        cant_find = ["Sadly, I couldn't, find this movie", "I couldn't find the movie, perhaps you should try with more details", "If you're sure this movie exists please add more details", "I didn't find anything related to this movie", "I can't find this movie"]
                        response = random.choice(cant_find) 
                    elif len(get_title) == 1:
                        found_one = ["I found this movie:", "I found one movie", "In fact I was able to find one movie", "I was able to find a movie like you asked:"]
                        response +=  random.choice(found_one) +  " " + "\'" + self.id_to_title[str(get_title[0])] + "\'"
                        sentiment_value = self.extract_sentiment(self.remove_titles(line))
                        if sentiment_value == 0:
                            response += "\nI can't find any sentiment please tell me more about \'" + self.id_to_title[str(get_title[0])] + "\'"
                        elif sentiment_value == 1:
                            self.user_ratings[get_title[0]] = 1
                            self.movies_rated.add(get_title[0])
                            positive_response = ["I can tell you liked", "I see that you had positive vibes about", "I like that you enjoyed", "I figured out that you liked"]
                            response +=  "\n" + random.choice(positive_response) +  " " + "\'" + self.id_to_title[str(get_title[0])] + "\'"
                        elif sentiment_value == -1:
                            self.user_ratings[get_title[0]] = -1
                            self.movies_rated.add(get_title[0])
                            negative_response = ["I can tell you did not like", "I see that you had negative vibes about", "I like that you didn't like", "I figured out that you didn't like"]
                            response += "\n" + random.choice(negative_response) +  " " + "\'" + self.id_to_title[str(get_title[0])] + "\'"
                    elif len(get_title) > 1:
                        many_returns =["I found too many movies did you mean one of these", "I returned many movies did you mean one of these", "I found many results did you mean one of these", "Many results were returned did you mean one of these"]
                        response += random.choice(many_returns)
                        for value in get_title:
                            response += ", \'" + self.id_to_title[str(value)] + "\'"
                elif len(value) > 1:
                    many_final_return = ["I detected to many movies", "There were to many results for me to figure this out", "To many movies were detected", "I detected many movies"]
                    response += random.choice(many_final_return)
           if len(self.movies_rated) > 4 and self.reccomend_index < 9:
                self.rec_mode = True
                if (self.reccomend_index == 0) or (line[0].lower() == "y"):
                    response_rec = ["I suggest you watch this movie ", "I think you should watch this movie ", "I think you would like this movie ", "I think you would enjoy this movie "]
                    response +=  "\n " +  random.choice(response_rec)
                    return_recommend = self.recommend(self.user_ratings, self.ratings, k=10, creative=False)
                    response += "\'" +  self.id_to_title[str(return_recommend[self.reccomend_index])] + "\'"
                    response_another = ["Would you like another suggestion?", "Would you like another movie?", "Would you like another recommendation?", "Would you like another movie recommendation?"]
                    response +=  "\n " + random.choice(response_another)
                    self.reccomend_index += 1
                elif (self.reccomend_index != 0) and line[0].lower()== "n":
                    response_quit = ["Thank you for using my chatbot, enter \':quit\' to fully quit", "Enter \':quit\' to fully quit", "Have a good day, enter \':quit\' to fully quit"]
                    response += random.choice(response_quit)
                elif (self.reccomend_index != 0):
                    response_unsure = ["I don't understand, please try again. Enter \':quit\' to fully quit, enter 'yes' to get another recommendation or 'no' to stop getting recommendations", "Press yes for another, no to stop and  \':quit\' to quit", "Please try again"]
                    response += random.choice(response_unsure)
           if self.reccomend_index == 9:
                response_bye = ["Thank you for using my chatbot, we are out of suggestions, enter \':quit\' to fully quit", "That's all for now, enter \':quit\' to fully quit", "It was a pleasure helping you, enter \':quit\' to fully quit", "Enter \':quit\' to fully quit and have a good day"]
                response += random.choice(response_bye)
                

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
        all_strings = re.findall(r'"([^"]*)"', preprocessed_input)
        return all_strings

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
        return_list = []

        if self.creative:
            #title = title.lower()
            check_regex = re.findall(r'\(\d{4}\)', title)

            if check_regex != []:
                year = check_regex[0]
                title = title.split(year)[0]
                title = title[0:len(title)-1]
                year = year.split("(")[1]
                year = year.split(")")[0]
                first_word = title.split(" ")[0]
                first_word_set = {"The", "An", "A", 'El',  'Le', 'jie', 'En', 'Los', 'Las', 'Das', 'Det','Une', 'Les', 'La', 'Den', 'Il', 'Un', 'Die', 'De', 'Der', 'Lo'}
                if first_word in first_word_set:
                    #print("hi")
                    #print(first_word)
                    title = title.split(" ")[1:len(title)]
                    title = " ".join(title)
                    title = title + ", " + first_word
                    #print(title)
                    #print(title)

                #print(title)
                #print(year)
                #print(holder_dict[title])
                if title in self.main_dict:
                    #print("hi")
                    holder_value = self.main_dict[title]
                    #print(holder_value)
                    if year in holder_value:
                        return_list.append(int(holder_value[year]))
            else:
                first_word = title.split(" ")[0]
                first_word_set = {"The", "An", "A", 'El',  'Le', 'jie', 'En', 'Los', 'Las', 'Das', 'Det','Une', 'Les', 'La', 'Den', 'Il', 'Un', 'Die', 'De', 'Der', 'Lo'}
                if first_word in first_word_set:
                    #print("hi")
                    #print(first_word)
                    title = title.split(" ")[1:len(title)]
                    title = " ".join(title)
                    title = title + ", " + first_word
                    #print(title)
                    #print(title)

                for key in self.main_dict:
                    #if holder_dict[key] starts with title:
                    #check if key starts with title + any punctuation
                    # write a regex to see if key starts with title + any punctuation
                    if key == title:
                        #print(key)
                        #print(title)
                        holder_value = self.main_dict[key]
                        #final_list = []
                        for value in holder_value:
                            return_list.append(int(holder_value[value]))
                    elif  (key.startswith(title) and not ((key[len(title)])).isalnum()):
                        holder_value = self.main_dict[key]
                        #final_list = []
                        for value in holder_value:
                            return_list.append(int(holder_value[value]))
                        self.spell_check_value = True
                        if len(return_list) > 1:
                            self.disambiguate_value = True
                            self.clarify = True
                            self.spell_check_value = False
            #print(return_list)
            #this will change too if creative !!!
            if (return_list ==[]):
                closest = self.find_movies_closest_to_title(title, 3)
                if closest != []:
                # print(closest)
                    return_list = closest
                    if len(closest) == 1:
                        self.spell_check_value = True
                        self.clarify = True
                    else:
                        self.disambiguate_value = True
                        self.clarify = True
        else:
            check_regex = re.findall(r'\(\d{4}\)', title)
            if check_regex != []:
                year = check_regex[0]
                title = title.split(year)[0]
                title = title[0:len(title)-1]
                year = year.split("(")[1]
                year = year.split(")")[0]
                first_word = title.split(" ")[0]
                if first_word == "The" or first_word == "An" or first_word == "A":
                    #print("hi")
                    title = title.split(" ")[1:len(title)]
                    title = " ".join(title)
                    title = title + ", " + first_word
                    #print(title)

                #print(title)
                #print(year)
                #print(holder_dict[title])
                if title in self.main_dict:
                    #print("hi")
                    holder_value = self.main_dict[title]
                    #print(holder_value)
                    if year in holder_value:
                        return_list.append(int(holder_value[year]))
            else:
                first_word = title.split(" ")[0]
                if first_word == "The" or first_word == "An" or first_word == "A":
                    #print("hi")
                    title = title.split(" ")[1:len(title)]
                    title = " ".join(title)
                    title = title + ", " + first_word
                    #print(title)

                if title in self.main_dict:
                    holder_value = self.main_dict[title]
                    final_list = []
                    for value in holder_value:
                        final_list.append(int(holder_value[value]))
                    return_list = final_list     
        return return_list
    


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
        file1 = open('data/sentiment.txt', 'r')
        Lines = file1.readlines()
        pos_set = set()
        neg_set = set()
        for line in Lines:
            line = line.strip()
            line_2 = line.split(",")
            if line_2[1] == 'neg':
                neg_set.add(line_2[0])
            else:
                pos_set.add(line_2[0])
        
        neg_total = 0
        pos_total = 0
        invert_set = {'not',"n't",'never', 'didn\'t', 'never'}
        punct_invert = {',','.',';', 'but'} #might add "but" to this too
        flag = True #true means treat it normall, false means invert it

        #write python code equivalent to nltk.tokenize word_tokenize
        #print(preprocessed_input)
        #print(preprocessed_input)
        tokens = re.findall(r"\w+(?:'\w+)?|\S+", preprocessed_input)
        #preprocessed_input = preprocessed_input.lower()


        #print(tokens)
        #print(
        for i in range(len(tokens)):
            if tokens[i] in invert_set:  #figure out if we need to invert
                flag = False
            if tokens[i] in punct_invert and flag == False:
                flag = True
            for value in pos_set:
                if tokens[i] == value or tokens[i].startswith(value):
                    #print (value)
                    if flag == True:
                        pos_total += 1
                    else:
                        neg_total += 1
            for value in neg_set:
                if tokens[i] == value or tokens[i].startswith(value):
                    #print (value)
                    if flag == True:
                        neg_total += 1
                    else:
                        pos_total += 1

        #print(pos_total)
        #print(neg_total)
        if pos_total > neg_total:
            return(1)
        elif pos_total < neg_total:
            return(-1)
        else:
            return(0)

        # preprocessed_input = preprocessed_input.split(" ")

        # for i, word in enumerate(preprocessed_input):
        #     if word in neg_set:
        #         neg_total += 1
        #     if word in pos_set:
        #         pos_total += 1
        
        # if neg_total > pos_total:
        #     return -1
        # elif pos_total > neg_total:
        #     return 1
        # else:
        #     return 0

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
        return_value = []
        if "liked both" in preprocessed_input:
            value = self.extract_titles(preprocessed_input)
            return_value.append((value[0], 1))
            return_value.append((value[1], 1))
        elif "liked" in preprocessed_input and "but not" in preprocessed_input:
            value = self.extract_titles(preprocessed_input)
            return_value.append((value[0], 1))
            return_value.append((value[1], -1))
        elif "didn't like" in preprocessed_input and "or" in preprocessed_input:
            value = self.extract_titles(preprocessed_input)
            return_value.append((value[0], -1))
            return_value.append((value[1], -1))
        elif "liked" in preprocessed_input and "but" in preprocessed_input:
            value = self.extract_titles(preprocessed_input)
            return_value.append((value[0], 1))
            return_value.append((value[1], -1))
        return return_value

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
        final_list = []
        final_value = max_distance + 1
        for key in self.main_dict:
            value = edit_distance((title.lower()), key.lower(), substitution_cost=2, transpositions=False)
            if value <= max_distance:
                if value < final_value:
                    final_value = value
                    final_list = []
                    year_number = self.main_dict[key]
                    for year in year_number:
                        final_list.append(int(year_number[year]))
                elif value == final_value:
                    final_value = value
                    year_number = self.main_dict[key]
                    for year in year_number:
                        final_list.append(int(year_number[year]))
        return(final_list)

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
        #print(clarification)
        for value in candidates:
            #print("HERE1")
            #get value from self.id_to_title
            if str(value) in self.id_to_title:
                #print("HERE2")
                get_value = (self.id_to_title[str(value)])
                #print(get_value)
                #print(clarification)
                #print(type(get_value))
                #print(type(clarification))
                #(get_value)
                #print(clarification)
                if clarification in get_value:
                    #print("hi")
                    #print(value)
                    return [value]
        return []

            


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
        for i in range(ratings.shape[0]):
            for j in range(ratings.shape[1]):
                if ratings[i][j] > threshold:
                    binarized_ratings[i][j] = 1
                elif ratings[i][j] == 0:
                    binarized_ratings[i][j] = 0
                elif ratings[i][j] <=threshold:
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
        similarity = 0
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

        sum_value = user_ratings.shape[0]
        sum_value_array = np.zeros(sum_value)
        #print(sum_value)
        #print(sum_value_array)
        holder = set()
        for i,value in enumerate(user_ratings):
            if value == 0:
                continue
            else:
                holder.add(i)
                for j in range(len(ratings_matrix)):
                    if (i ==j):
                        continue
                    user_rating = value
                    #print(value)
                    user_scored = ratings_matrix[i]
                    other_scored = ratings_matrix[j]
                    cosine = np.dot(user_scored,other_scored)/(norm(user_scored)*norm(other_scored))
                    value_to_add = cosine * user_rating
                    sum_value_array[j] += value_to_add

        sum_value_array = np.nan_to_num(sum_value_array)
        # if len(sum_value_array) > 10:
        #     print("wrong value i got")
        #     print(sum_value_array[8309])
        #     print(sum_value_array[8596])
        #     print(sum_value_array[7729])
        #     print(sum_value_array[8786])
        #     #print(sum_value_array[9124])
        #     #print(sum_value_array[8953])
        #     print("NEW")
        #     print(sum_value_array[8953])
        #     print('should be')
        #     print(sum_value_array[8582])
        #     print(sum_value_array[8596])
        #     print(sum_value_array[8786])

        #print(sum_value_array)
        sorted_array = (sum_value_array).argsort()[::-1]
        #print(sorted_array)
        for i in sorted_array:
            if i not in holder:
                recommendations.append(i)
            if len(recommendations) == k:
                break

        #print(sum_value)


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
        return "This is a movie chat bot that will reccomend movies to you. Movie names must be enclosed in quotations and please include sentiment"
        # Your task is to implement the chatbot as detailed in the PA7
        # instructions.
        # Remember: in the starter mode, movie names will come in quotation marks
        # and expressions of sentiment will be simple!
        # TODO: Write here the description for your own chatbot!
        # """

    def setup_data(self):
        holder_dict = {}
        #main_title_only = {}
        id_to_title = {}

        #set_of_values = set()
        file1 = open('data/movies.txt', 'r')
        Lines = file1.readlines()
        for line in Lines:
        #for text_line in text_all:
            text_line = line
            i_d =   text_line.split("%")[0]
            main_section = text_line.split("%")[1]

            id_to_title[i_d] = main_section
            #print (main_section)
            pattern = r"\((.*?)\)"
            result = re.findall(pattern, main_section)
            #print(result)
            possible_title = []
            possible_year = '0000'

            #get the first title
            if result == []:
                possible_title.append(main_section)
            else:
                text = main_section.split("(")[0]
                possible_title.append(text[0:len(text)-1])

            for value in result:
                # if value contains 'a.k.a. '
                if 'a.k.a.' in value:
                    #split on 'a.k.a. ' and take the first value
                    value = value.split('a.k.a. ')[1]
                    #append it to possible_title
                    possible_title.append(value)
                #write a regex to determine if value is a year
                #if it is a year, append it to possible_title
                elif re.match(r'\d{4}', value):
                    possible_year = value
                else:
                    possible_title.append(value)
                    #if value contains a , print it 
                    #print(value)

            for movie_final in possible_title:
                if movie_final in holder_dict:
                    change_dict = holder_dict[movie_final]
                    change_dict[possible_year] = i_d
                    holder_dict[movie_final] = change_dict
                else:
                    holder_dict[movie_final] = {possible_year: i_d}
        #print(holder_dict) 
        #print(id_to_title) 
        return holder_dict, id_to_title
    
    def remove_titles(self, line):
        return(re.sub(r'".*?"', '', line))

if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')


