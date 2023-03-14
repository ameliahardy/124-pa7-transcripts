# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import numpy as np
import porter_stemmer as ps
import re
import random


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):

        self.name = self.get_bot_name() # look at the method to get the name below

        self.creative = creative
        self.status = 0
        self.num_sim_movies = 0
        self.curr_title = ""
        self.recommendations = []
        self.curr_rec = ""

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.title_list = []
        for i in range(len(self.titles)):
            self.title_list.append(self.titles[i][0].lower())
        for i in range(len(self.title_list)):
            if self.title_list[i].find(", The") != -1:
                div_index = self.title_list[i].find(", The")
                new_title = self.title_list[i][div_index+2:div_index+6] + self.title_list[i][0:div_index] + " " + self.title_list[i][div_index+6:]
                self.title_list[i] = new_title
            elif self.title_list[i].find(", A ") != -1:
                div_index = self.title_list[i].find(", A ")
                new_title = self.title_list[i][div_index+2:div_index+4] + self.title_list[i][0:div_index] + " " + self.title_list[i][div_index+4:]
                self.title_list[i] = new_title
            elif self.title_list[i].find(", An") != -1:
                div_index = self.title_list[i].find(", An")
                new_title = self.title_list[i][div_index+2:div_index+5] + self.title_list[i][0:div_index] + " " + self.title_list[i][div_index+5:]
                self.title_list[i] = new_title
        self.process_title_names()
        self.numratings = 0

        self.user_ratings = np.zeros(len(self.titles))

        # print(self.titles[10][0])
        # print(self.find_movies_by_title("An Affair of Love"))
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        # self.stemmed_sentiment = [ps.stem(word) for word in self.sentiment.keys()]
        newDict = {}
        p = ps.PorterStemmer()
        for word in self.sentiment:
            newDict[p.stem(word)] = self.sentiment[word]

        self.sentiment = newDict
        # self.train(self.titles, ratings, self.sentiment) - to be used for extract_sentiment

        ########################################################################
        # Binarize the movie ratings matrix.  Done by Andrei                           #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix. 
        # - using the static self.binarize method below
        self.ratings = self.binarize(ratings) 
        # print(self.ratings)
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

    def process_title_names(self):
        self.title_list_a = []
        self.years = []
        for i in range(len(self.titles)):
            title = self.titles[i][0].lower()
            if "(" not in title:
                title = self.extract_article(title)
                self.title_list_a.append([title])
                self.years.append(None)
                continue
            
            first = title[:title.find(" (")]
            first = self.extract_article(first)

            altplusyear = re.findall(r' \(([^\(\)]+)\)', title)
            self.title_list_a.append([first])
            self.years.append(None)
            for match in altplusyear:
                if match.isnumeric() and len(match) == 4:
                    self.years[i] = int(match)
                else:
                    match = self.extract_alias(match)
                    match = self.extract_article(match)
                    self.title_list_a[i].append(match)

    @staticmethod
    def extract_alias(title):
        if title.startswith("aka "):
            title = title[4:]
        elif title.startswith("a.k.a. "):
            title = title[7:]
        return title

    @staticmethod
    def extract_article(title):
        if title.endswith(", the"):
            title = "the " + title[:len(title) - 5]
        elif title.endswith(", a"):
            title = "a " + title[:len(title) - 3]
        elif title.endswith(", an"):
            title = "an " + title[:len(title) - 4]
        elif title.endswith(", le"):
            title = "le " + title[:len(title) - 4]
        elif title.endswith(", la"):
            title = "la " + title[:len(title) - 4]
        elif title.endswith(", les"):
            title = "les " + title[:len(title) - 5]
        elif title.endswith(", un"):
            title = "un " + title[:len(title) - 4]
        elif title.endswith(", une"):
            title = "une " + title[:len(title) - 5]
        elif title.endswith(", el"):
            title = "el " + title[:len(title) - 4]
        elif title.endswith(", los"):
            title = "los " + title[:len(title) - 5]
        elif title.endswith(", las"):
            title = "las " + title[:len(title) - 5]
        elif title.endswith(", lo"):
            title = "lo " + title[:len(title) - 4]
        elif title.endswith(", il"):
            title = "il " + title[:len(title) - 4]
        elif title.endswith(", l'"):
            title = "l'" + title[:len(title) - 4]
        elif title.endswith(", i"):
            title = "i " + title[:len(title) - 3]
        elif title.endswith(", der"):
            title = "der " + title[:len(title) - 5]
        elif title.endswith(", die"):
            title = "die " + title[:len(title) - 5]
        elif title.endswith(", das"):
            title = "das " + title[:len(title) - 5]
        return title

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    @staticmethod
    def get_bot_name():
        ########################################################################
        # Andrei wrote this method to extract the chatbot name                 #
        ########################################################################
        names = [ # generated with openai
            "RoboRogue",
            "CogswellPirateBot",
            "BuccaneerBot",
            "SeadogBot",
            "BotOfTheHighSeas",
            "JollyBot",
            "PirateAutomaton",
            "CorsairBot",
            "DreadBotRoberts",
            "Swashbot",
            "SaltyBot",
            "ScallywagBot",
            "MarauderBot",
            "PrivateerBot"
        ]
        ranname = np.random.choice(names)
        return ranname

    @staticmethod
    def get_greetings():
        ########################################################################
        # Andrei wrote this method to simplfy adding/removing greetings        #
        ########################################################################
        greetings = [ # generated with openai
            "Ahoy matey!",
            "Avast ye!",
            "Ahoy there, me hearties!",
            "Shiver me timbers!",
            "Yo ho ho!",
            "Heave ho, me hearties!",
            "Welcome aboard, me hearty!",
            "Hoist the Jolly Roger!",
            "Arrrr, me matey!",
            "Nice to see you!",
        ]
        return greetings

    @staticmethod
    def get_farewells():
        ########################################################################
        # Andrei wrote this method to simplfy adding/removing farewells        #
        ########################################################################
        farewells = [ # generated with openai
            "Farewell, me hearties!",
            "Achors aweigh",
            "Until we meet again, me mateys!",
            "Clear skies and calm seas to ye!",
            "May the wind be at your back!",
            "Avast ye later!",
            "Keep a weather eye open, me hearties!",
            "Happy sailing, me bucko!",
            "May ye find treasure in every port!",
            "Hoist the anchor and set sail!",
            "Goodnight!"
        ]
        return farewells

    def greeting(self): # Andrei did this
        """Return a message that the chatbot uses to greet the user."""
        ########################################################################
        # Write a short greeting message                                 #
        ########################################################################

        greetings = self.get_greetings()
        rangreeting = np.random.choice(greetings)

        greeting_message = "{greeting} My name is {name}. How can I help you?".format(greeting = rangreeting, name = self.name)

        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################
        return greeting_message

    @staticmethod
    def negations():
        words = [  # generated with openai
            "didn't",
            "wouldn't",
            "couldn't",
            "shouldn't",
            "not",
            "never",
            "don't",
            "hasn't",
            "haven't",
            "isn't",
        ]
        p = ps.PorterStemmer()
        return [p.stem(word) for word in words]
    
    @staticmethod
    def very_positive():
        words = [  # generated with openai
            "love", 
            "happy", 
            "amazing", 
            "joy", 
            "bliss", 
            "exciting", 
            "excellent", 
            "fabulous", 
            "gorgeous", 
            "heavenly", 
            "incredible", 
            "marvelous", 
            "perfect", 
            "phenomenal", 
            "radiant", 
            "splendid", 
            "superb", 
            "terrific", 
            "thrilled", 
            "wonderful"
        ]
        p = ps.PorterStemmer()
        return [p.stem(word) for word in words]

    @staticmethod
    def very_negative():
        words = [  # generated with openai
            "hate", 
            "disgusting", 
            "terrible", 
            "awful", 
            "horrible", 
            "disappointing", 
            "unpleasant", 
            "miserable", 
            "dreadful", 
            "grim", 
            "dreary", 
            "gloomy", 
            "depressing", 
            "sad", 
            "bad", 
            "evil", 
            "nasty", 
            "abominable", 
            "offensive", 
            "repugnant"
        ]
        p = ps.PorterStemmer()
        return [p.stem(word) for word in words]

    @staticmethod
    def emphasizers():
        words = [ # generated with openai
            "absolutely", 
            "completely", 
            "totally", 
            "utterly", 
            "entirely", 
            "fully", 
            "wholly", 
            "perfectly", 
            "precisely", 
            "exactly", 
            "definitely", 
            "certainly", 
            "indeed", 
            "positively", 
            "unquestionably", 
            "undoubtedly", 
            "undeniably", 
            "incredibly", 
            "absurdly", 
            "unbelievably",
            "really",
            "truly"
        ]
        p = ps.PorterStemmer()
        return [p.stem(word) for word in words]

    @staticmethod
    def askingfornew():
        words = [
            " Tell me about another movie, matey! ",
            " Arrrgh, Do you have any other thougths about other movies",
            " Would you like to tell me about a different movie, or walk the plank?",
            " Please do tell this Captain about other movies",
            " Have you watched any other movies, yee-hoo!",
            " Let me know about any other movies",
            " I wonder if you have any other movies, my matey"
        ]
        random_word = random.choice(words)
        return random_word

    @staticmethod
    def superposfiller():
        words = [
            ["Arr matey, I'll give \" ", "\" a rating of aye-aye. "],
            ["Shiver me timbers \" ", " \" be a fine treasure! "],
            ["Avast ye \" ", " \" be a sight for sore eyes! "],
            ["Hoist the Jolly Roger \" ", " \" that movie be a swashbuckling good time! "],
            ["Aye \" ", " \" be a cinematic adventure worth its weight in gold doubloons! "],
            ["Ahoy there \" ", " \" be a real booty for the eyes! "],
            ["Arrr \" ", " \" be a film fit for a pirate's parlay! "],
            ["By Blackbeard's beard, \" ", " \" that movie be a rip-roaring success! "],
            ["Avast \" ", "\" be a real barnacle buster! "],
            ["Yo-ho-ho, \" ", "\" be a treasure trove of entertainment! "]
        ]
        random_word = random.choice(words)
        return random_word

    @staticmethod
    def posfiller():
        words = [
            "Yo ho ho! So you liked:  ",
            "Right on bucko, you liked: ",
            "By Blackbeard's beard, you enjoyed: ",
            "Arrrrr, you liked: ",
            "Avast ye, you appreciated:  ",
            "Yo-ho-ho, good to know you were fond of: ",
            "Matey! So you enjoyed: "
        ]
        random_word = random.choice(words)
        return random_word

    @staticmethod
    def negativefillers():
        words = [
            "Blimey, so yer crew didn't like: ",
            "Blow me down! So you weren't delighted by: ",
            "Shiver me timbers! Like a ship with a leak, you didn't enjoy: ",
            "Ahoy, me hearties, so you didn't quite find treasure with: ",
            "Aye me buckos, so you weren't pleased by: ",
            "Avast, so no favor was gained by: ",
            "By Blackbeard's beard, you were disappointed by: "
        ]
        random_word = random.choice(words)
        return random_word

    @staticmethod
    def supernegativefillers():
        words = [
            ["Aye,", "be a disappointment, not at all the treasure we were hoping for! "],
            ["Blow me down,", "be a ship with a leak, letting in a few too many flaws to be seaworthy. "],
            ["Belay,", "be a real hornswoggle, a cheat and a swindle of a film. "],
            ["Ahoy,", "be a real black spot on the reputation of cinema, not worth the salt in me hardtack! "],
            ["Shiver me timbers,", "be a rotting corpse on the high seas of cinema! "],
            ["Arrr,", "be a real barnacle-covered piece of flotsam. "],
            ["Avast, me hearties,", "be a waste of precious booty! "],
            ["ARRGGGH,", "be a real mutiny-inducing disaster of a film. "],
            ["Blow me down matey!", "be a bilge rat of a film, not even worthy of being thrown to the sharks. "],
            ["Shiver me timbers,", "be a cursed thing, not fit for even the lowliest swabbie to watch. "],
            ["Avast,",
             "be a rotting corpse on the high seas of cinema, fit only for the most desperate and cursed of pirates. "],
            ["Belay", "me buckos, it be a blight on the reputation of all pirates and the seven seas! "],
            ["Ahoy, me hearties,",
             "be a black spot on the reputation of all who sailed the seas of cinema, not even worth the salt in me hardtack! "]
        ]
        random_word = random.choice(words)
        return random_word

    @staticmethod
    def neutralfiller():
        words = [
            ["Aye", "it be a fair enough flick!"],
            ["\"", " \" twas a decent enough voyage, but me shipmates and I weren't blown away. "],
            ["Ahoy mateys, \" ", "\" be a middling movie, neither a treasure nor a bilge rat. "],
            ["\"", "\" t'was neither good nor bad, but aye, it be worth a watch if ye have some time to kill. "],
            ["\"", "\" be a fair enough flick, but not one that'll shiver yer timbers "],
            ["\"", "\" is not the best movie on the seven seas, but it ain't the worst either. "],
            ["I reckon \" ", "\" is a passable film, but it won't make ye walk the plank with excitement. "],
            ["\"", "\" be an average adventure, not worth hoarding a chest of doubloons for. "],
            ["Aye, \" ", "\" be a harmless movie, but it won't make ye sing a sea shanty in its honor. "],
            ["Ahoy, me hearties, \"",
             "\" be a movie that'll neither make ye keelhaul the crew nor make ye want to raise the Jolly Roger. "],
            ["\"", "\" be a movie that won't make ye jump for joy, but it also won't make ye jump overboard. "]
        ]
        random_word = random.choice(words)
        return random_word

    @staticmethod
    def recommenders():
        words = [
            "Ahoy matey! Given yer input, me thinks ye might favor: ",
            "Avast ye! From what ye've shared, methinks ye may be partial to: ",
            "Shiver me timbers! Judging by yer words, I reckon ye'd be keen on: ",
            "Yarr! According to yer tale, I be thinkin' ye'd be likin:  ",
            "Yo ho ho! Hear me now, from what ye've spoken, I believe ye'd be fond of: ",
            "Arrr! Based on yer words, it seems to me ye might enjoy: ",
            "Ahoy there, ye scallywag! I gather from yer words that ye'd be interested in: ",
            "Hoist the Jolly Roger! Me ears hear that ye'd be pleased with: ",
            "Ahoy matey! Based on yer words, me thinks ye might fancy: "
        ]
        random_word = random.choice(words)
        return random_word

    @staticmethod
    def morerecs():
        words = [
            "Ye scallywag, do ye have the taste fer another recommendation? ",
            "Fancy ye another suggestion, ye landlubber? ",
            "Arrr, be ye still thirsty fer more recommendations? ",
            "Avast ye, matey! Be ye wantin' another recommendation to watch? ",
            "Ahoy there, me heartie! Do ye care for another suggestion on what to watch? "
        ]
        random_word = random.choice(words)
        return random_word

    @staticmethod
    def nextrec():
        words = [
            "By Blackbeard's beard, I'd also recommend: ",
            "Aye, me hearty, I'd also steer ye towards: ",
            "Batten down the hatches, I'd also suggest: ",
            "Shiver me timbers, I'd also propose: ",
            "Ho there, matey, I think you'd also enjoy: ",
            "Avast ye, I'd also put forth: "
        ]
        random_word = random.choice(words)
        return random_word

    @staticmethod
    def apologies():
        words = [
            ["Ahoy matey, me apologies. I be not sure if ye fancy the film \"",
             "\" .Could ye tell me more about it? "],
            ["Arrr! Me sincerest apologies, me bucko. I be unsure if ye be likin' the flick' \"",
             "\" . Would ye care to enlighten me? "],
            ["Avast ye! I be sorry, me hearty, but I be not sure if \"",
             "\" be to yer taste. Could ye give me more details about yer opinion? "],
            ["By Blackbeard's beard! Me apologies, me hearties. I be uncertain if ye enjoyed the movie \"",
             "\" . Can ye tell me more about yer thoughts on it? "],
            ["Shiver me timbers! Mea culpa, me bucko. I be not sure if ye be a fan of the film \"",
             "\" . Could ye share with me yer feelings about it? "],
            ["Yarr! Me sorry, me matey. I be not sure if \"",
             "\" be yer cup o' tea. Would ye mind tellin' me more 'bout it? "]
        ]
        random_word = random.choice(words)
        return random_word

    @staticmethod
    def saddislike():
        words = [
            "Me apologies, ye scallywag, ye didn't like: ",
            "Forgive me, matey, ye didn't approve of: ",
            "I be sorry for your cinematic misdeeds, ye disliked:  ",
            "Arrr, me hearties, ye did not enjoy: ",
            "Me apologies, me bucko, ye didnt like: ",
        ]
        random_word = random.choice(words)
        return random_word

    @staticmethod
    def cant_find():
        words = [
            ["Blimey! Me apologies, me hearty. I be not familiar with '",
             "'. Could ye tell me 'bout another film ye be fancyin'? "],
            ["Ahoy there! Mea culpa, me matey. I be not aware of ",
             ". Could ye enlighten me 'bout another movie ye enjoyed? "],
            ["Avast ye! Me sorry, me bucko. I be not acquainted with ",
             ". How 'bout ye tell me 'bout another movie that caught yer fancy? "],
            ["Shiver me timbers! Me apologies, me hearties. I be not familiar with ",
             ". Could ye share with me another movie ye be likin'? "],
            ["Yarr! Me sorry, me matey. I be not privy to ",
             ". Can ye tell me 'bout another movie that tickled yer fancy? "],
            ["Arrr! Mea culpa, me hearty. I be not acquainted with ",
             ". How 'bout ye give me a run-down on another movie ye enjoyed, me bucko? "]
        ]
        random_word = random.choice(words)
        return random_word

    @staticmethod
    def pirate_hoorays():
        words = [
            "Shiver me timbers! Huzzah! Ye enjoyed ",
            "Yo ho ho! Hoorah! Ye favored ",
            "Avast ye! Hooray! Ye appreciated ",
            "Yarr! Huzzah, me hearties! Ye took delight in ",
            "By Blackbeard's beard! Hooray! Ye enjoyed ",
            "Ahoy, me buckos! Huzzah! Ye fancied ",
            "Arrr! Hooray, me mateys! Ye took delight in ",
            "Blimey! Huzzah, me hearty! Ye had a grand ole time with ",
            "Hoist the Jolly Roger! Hooray! Ye found mirth and merriment in ",
            "Aye, aye! Huzzah, me lads and lasses! Ye Had a swashbuckling good time with "
        ]
        random_word = random.choice(words)
        return random_word

    @staticmethod
    def offtopic():
        words = [
            "I don't reckon that be the topic I want to discuss at the moment. Can we switch back to movies, ye scurvy dog?",
            "That be not quite what I had in mind. Could we circle back to movies instead, me heartie?",
            "I appreciate yer input, but let's steer the conversation back to movies, if that be okay with ye.",
            "I'm not feelin' particularly interested in that topic right now. Let's refocus on movies, ye landlubber.",
            "I think we may have gotten a bit off track. Let's redirect our conversation to movies, ye matey."
        ]
        random_word = random.choice(words)
        return random_word

    def goodbye(self): # Andrei did this
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        ########################################################################
        # Write a short farewell message                                       #
        ########################################################################

        # Andrei did this
        farewells = self.get_farewells()
        ranfarewell = np.random.choice(farewells)

        # if the user has defined their name, then address them by it
        try: 
            username = ", " + self.username
        except AttributeError:
            username = ""

        goodbye_message = "Of course{name}. {farewell}".format(farewell = ranfarewell, name = username)

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
        # Implement the extraction and transformation in this method,    #
        # possibly calling other functions. Although your code is not graded   #
        # directly based on how modular it is, we highly recommended writing   #
        # code in a modular fashion to make it easier to improve and debug.    #
        ########################################################################
        if self.creative: # python3 repl.py --creative will run in creative mode
            response = "I processed {} in creative mode!!".format(line)
            line = self.preprocess(line)

        else: # no machine learning involved here!
            response = "I processed {} in starter mode!!".format(line)
            line = self.preprocess(line)
        #takes in a list of the titles found in input line
        foundtitles = self.extract_titles(line)
        sentimentarray = self.extract_sentiment_for_movies(line)
        count = 0
        response = ''
        #chatbot theme/persona : PIRATES
        #checks for exit code
        if line[0] == ':quit':
            bye = self.goodbye()
            response += bye
        currtitles = 0
        #make a list of ways to end the process
        if self.status == 0:
            #creative: failing gracefully: no valid titles found, bringing user back to movies
            #responds to arbitrary input
            if len(foundtitles) == 0:
                response = self.offtopic()
            for title in foundtitles:
                currsent = sentimentarray[count][1]
                self.globalsent = currsent
                count += 1
                our_titles = self.find_movies_by_title(title.lower())
                if len(our_titles) == 0: # if not a valid title
                    #creative: dialouge for typo / spellcheck
                    if len(self.find_movies_closest_to_title(title, 3)) > 0: 
                        self.status = 2
                        self.curr_title = title
                        recs = self.find_movies_closest_to_title(title, 3)
                        self.num_sim_movies = len(recs)
                        self.curr_rec = self.title_list[recs[0]].title()
                        #ensures speaking reasonably fluently
                        response += "Did ye mean {}? Yes or no? ".format(self.curr_rec)
                    else:
                        #creative: failing gracefully does not exist sorry, tell me about another movie you liked
                        cant_finds = self.cant_find()
                        choice = cant_finds
                        response += "{front}".format(front = choice[0]) + title.title() + "{end}".format(end = choice[1])

                else:
                    #dialouge for ambigious cases, asking for clarification for which specific movie
                    if len(our_titles) > 1:
                        response += "Arrr I found more than one movie called " + title.title() + ". Can ye clarify?"
                    else:
                        #creative - handles the range of very pos to very neg sentiments
                        # make a list of super positive reference
                        if currsent == 2:
                            self.numratings += 1
                            self.user_ratings[self.find_movies_by_title(title)[0]] = 1
                            super_positives = self.superposfiller()
                            choice = super_positives
                            response += "{front}".format(front = choice[0]) + title.title() + "{end}".format(end = choice[1])

                        elif currsent == 1:
                            self.numratings += 1
                            self.user_ratings[self.find_movies_by_title(title)[0]] = 1
                            positives = self.posfiller()
                            choice = positives
                            response += "{}".format(choice) + title.title() + ". "

                        elif currsent == 0:
                            neutrals = self.neutralfiller()
                            choice = neutrals
                            response += "{front}".format(front = choice[0]) + title.title() + "{end}".format(end = choice[1])
                            # i'm sorry, tell me more
                            apologies = self.apologies()
                            apology_choice = apologies
                            response += "{front}".format(front = apology_choice[0]) + title.title() + "{end}".format(end = apology_choice[1])

                        elif currsent == -1:
                            self.numratings += 1
                            self.user_ratings[self.find_movies_by_title(title)[0]] = -1
                            negatives = self.negativefillers()
                            choice = negatives
                            response += "{}".format(choice) + title.title() + ". "

                        elif currsent == -2:
                            self.numratings += 1
                            self.user_ratings[self.find_movies_by_title(title)[0]] = -1
                            super_negatives = self.supernegativefillers()
                            choice = super_negatives
                            response += "{front}".format(front = choice[0]) + title.title() + "{end}".format(end = choice[1])
                        #making sure we have enough titles to make a recommendation
                        currtitles += 1
                        if self.numratings < 5:
                            # needs more reccomendations to gives a recommendation
                            if currtitles == len(foundtitles):
                                choice = self.askingfornew()
                                response += "\n" + choice
                        else:
                            if currtitles == len(foundtitles):
                                self.recommendations = self.recommend(self.user_ratings, self.ratings)
                                recommendation = self.recommendations[0]
                                front = self.recommenders()
                                askagain = self.morerecs()
                                response += "\n" +  "{first} {rec}. {another} Yes or no?".format(first = front, rec = self.title_list[recommendation].title(), another = askagain)
                                self.recommendations.remove(recommendation)
                                self.status = 1


        # 1 is recommend = If yes: I would also recommend "A Bug's Life (1998)". How about another one?
        elif self.status == 1:
            if line[0].lower() == 'yes':
                if len(self.recommendations) > 0:
                    wouldalsorec = self.nextrec()
                    recommendation = self.recommendations[0]
                    askagain = self.morerecs()
                    response += "{first} {rec}. {another} Yes or no?".format(first = wouldalsorec, rec = self.title_list[recommendation].title(), another = askagain)
                    self.recommendations.remove(recommendation)
                else:
                    response += "Apologies me hearty! Those are all I have. Tell me what ye thought of another movie. (Or enter :quit if yer done.)"
                    self.status = 0
            elif line[0].lower() == 'no':
                self.status = 0
                response += "Aye aye! Tell me what ye thought of another movie. (Or enter :quit if yer done.)"

        # 2 is spellcheck = if yes to correction: great you liked the notebook. then goodbye
        elif self.status == 2:
            #if whatever is yes
            if line[0].lower() == 'yes':
                if self.globalsent == 1 or  self.globalsent == 2:
                    affirms = self.pirate_hoorays()
                    self.numratings += 1
                elif self.globalsent == -1 or self.globalsent == -2:
                    affirms = self.saddislike()
                    self.numratings += 1
                elif self.globalsent == 0:
                    affirms = self.apologies()
                choice = affirms
                response += "{}".format(choice) + self.curr_rec.title() + ". Tell me what ye thought of another movie. (Or enter :quit if yer done.)"
                self.status = 0
                self.curr_title = ""
                self.num_sim_movies = 0
            #if response is no
            elif line[0].lower() == 'no':
                self.num_sim_movies -= 1
                if self.num_sim_movies > 0:
                    new_recs = self.find_movies_closest_to_title(self.curr_title, 3)
                    response += "Hmm... then did ye mean {}? Yes or no?".format(self.title_list[new_recs[len(new_recs) - self.num_sim_movies]])
                else:
                    # does not exist sorry, tell me about another movie you liked 
                    cant_finds = self.cant_find()
                    choice = cant_finds
                    response += "{front}".format(front = choice[0]) + self.curr_title.title() + "{end}".format(end = choice[1]) + "(Or enter :quit if yer done.)"
                    self.status = 0
                    self.curr_title = ""
                    self.num_sim_movies = 0

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
        # NOTE: This method is completely OPTIONAL. If it is not helpful to    #
        # your implementation to do any generic preprocessing, feel free to    #
        # leave this method unmodified.                                        #
        ########################################################################

        arr_of_words = text.split()
        return arr_of_words

        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

        # return text

    def extract_titles(self, input):
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

        combined = ' '.join(map(str, input))
        while combined.endswith("!") or combined.endswith("?"):
            combined=combined[:len(combined) - 1]
        moviegroups = re.findall(r'"([^"]+)"', combined)
        movies = moviegroups

        if len(movies) == 0:
            for i in range(len(input)):
                j = i
                text = ""
                set_of_titles = set(range(len(self.titles)))
                while j < len(input) and j < i + 18:
                    new_set = set()
                    word = input[j].lower()
                    if j == len(input) - 1:
                        word = word.replace("!", "")
                        word = word.replace("?", "")
                    text += word
                    for k in set_of_titles:
                        if text in self.title_list_a[k]:
                            movies.append(text)
                        for tit in self.title_list_a[k]:
                            if tit.startswith(text):
                                new_set.add(k)
                    text += " "
                    set_of_titles = new_set
                    j += 1

        return np.array(movies)

    @staticmethod
    def is_sublist(lst1, lst2):
        if len(lst1) > len(lst2):
            return False
        for i in range(len(lst2) - len(lst1) + 1):
            if lst2[i : i + len(lst1)] == lst1:
                return True
            elif lst2[i : i + len(lst1) - 1] == lst1[:len(lst1) - 1]:
                strcont = lst2[i + len(lst1) - 1]
                str = lst1[len(lst1) - 1]
                return re.match('.*[?.!:;,]$', strcont) is not None and strcont[:len(strcont) - 1] == str
        return False
    
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
        res = []
        title_list = []
        for i in range(len(self.titles)):
            title_list.append(self.titles[i][0])
        for i in range(len(title_list)):
            if title_list[i].find(", The") != -1:
                div_index = title_list[i].find(", The")
                new_title = title_list[i][div_index+2:div_index+6] + title_list[i][0:div_index] + " " + title_list[i][div_index+6:]
                title_list[i] = new_title
            elif title_list[i].find(", A ") != -1:
                div_index = title_list[i].find(", A ")
                new_title = title_list[i][div_index+2:div_index+4] + title_list[i][0:div_index] + " " + title_list[i][div_index+4:]
                title_list[i] = new_title
            elif title_list[i].find(", An") != -1:
                div_index = title_list[i].find(", An")
                new_title = title_list[i][div_index+2:div_index+5] + title_list[i][0:div_index] + " " + title_list[i][div_index+5:]
                title_list[i] = new_title

        for i in range(len(title_list)):
            if title_list[i].lower().startswith(title.lower()) and (title_list[i][len(title):] == "" or title_list[i][len(title):].startswith(" (")):
                res.append(i)
        
        if self.creative:
            res = []
            tokenized = title.split()
            for i in range(len(title_list)):
                if self.is_sublist(tokenized, title_list[i].split()):
                    res.append(i)

        
        if res == []: # creative
            for i in range(len(self.title_list_a)):
                for tit in self.title_list_a[i]:
                    if tit == title.lower():
                        res.append(i)

        return res

    def extract_sentiment(self, preprocessed_input):
        # Uses the implementation specified in 25.6 Using Lexicons for Sentiment Recognition

        """Extract a sentiment rating from a line of pre-processed text.

        You should return -1 if the sentiment of the text is negative, 0 if the
        sentiment of the text is neutral (no sentiment detected), or +1 if the
        sentiment of the text is positive.

        As an optional creative extension, return -2 if the sentiment of the
        text is super negative and +2 if the sentiment of the text is super
        positive.

        Example:
          sentiment = chatbot.extract_sentiment(chatbot.preprocess('I liked "The Titanic"'))
          print(sentiment) // prints 1

        :param preprocessed_input: a user-supplied line of text that has been
        pre-processed with preprocess()
        :returns: a numerical value for the sentiment of the text
        """
        positive_count = 0
        negative_count = 0
        res = 0
        multiplier = 1
        negation_list = self.negations()
        movie = False
        has_sentiment = False

        p = ps.PorterStemmer()
        for word in preprocessed_input:
            if '"' in word:
                if word.count('"') == 1:
                    movie = (not movie)
                continue
            if movie:
                continue

            word = word.replace(".", "")
            word = word.replace(",", "")
            word = word.replace(":", "")
            word = word.replace("?", "")
            word = word.lower()

            stemmed_word = p.stem(word.replace("!", ""))

            if stemmed_word in self.emphasizers():
                multiplier *= 2

            if stemmed_word in self.sentiment:
                has_sentiment = True
                if self.sentiment[stemmed_word] == "pos":
                    if stemmed_word in self.very_positive():
                        if multiplier > 0:
                            positive_count += multiplier * 2
                    elif multiplier > 0:
                        positive_count += multiplier
                    else:
                        negative_count += 1
                    if stemmed_word in self.very_positive():
                        multiplier /= 2
                else:
                    if stemmed_word in self.very_negative():
                        if multiplier > 0:
                            negative_count += multiplier * 2
                    elif multiplier > 0:
                        negative_count += multiplier
                    else:
                        positive_count += 1
            elif stemmed_word in negation_list:
                multiplier *= -1
            
            if "!" in word:
                positive_count *= 2
                negative_count *= 2

        if not has_sentiment and multiplier < 0:
            negative_count += 1      
        
        positive_count += 1
        negative_count += 1

        if positive_count / negative_count > 2:
            res = 2
        elif positive_count / negative_count > 1.25:
            res = 1
        elif negative_count / positive_count > 2:
            res = -2
        elif negative_count / positive_count > 1.25:
            res = -1

        return res

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
        titles_list = self.extract_titles(preprocessed_input)
        output_list = []
        combined = ' '.join(map(str, preprocessed_input))

        for i in range(len(titles_list)):
            title = titles_list[i]

            start_index = 0
            if i > 0:
                prev_title = titles_list[i - 1]
                start_index = combined.find(prev_title) + len(prev_title) + 1
            end_index = combined.find(title)
            
            substr = combined[start_index : end_index]
            sentiment = self.extract_sentiment(self.preprocess(substr))
            if sentiment == 0 and i == len(titles_list) - 1:
                end_index = len(combined)
                substr = combined[start_index : end_index]
                sentiment = self.extract_sentiment(self.preprocess(substr))
            if sentiment == 0 and i > 0:
                sentiment = output_list[i - 1][1]
            
            output_list.append((title, sentiment))

        return output_list

    @staticmethod
    def edit_distance(s1, s2):
        distances = np.zeros((len(s1) + 1, len(s2) + 1))
        for i in range(len(s1) + 1):
            distances[i][0] = i
        for j in range(len(s2) + 1):
            distances[0][j] = j
        for i in range(len(s1)):
            for j in range(len(s2)):
                left = distances[i][j + 1] + 1
                down = distances[i + 1][j] + 1
                diag = distances[i][j] + 2
                if s1[i] == s2[j]:
                    diag -= 2
                distances[i + 1][j + 1] = min(left, down, diag)
        return distances[len(s1)][len(s2)]


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
        res = []
        for i in range(len(self.title_list_a)):
            for tit in self.title_list_a[i]:
                dist1 = self.edit_distance(tit, title.lower())
                if dist1 <= max_distance:
                    res.append((i, dist1))
                    max_distance = dist1
                    continue
        
        res = [i for i, dist in res if dist == max_distance]
                
        return res

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
        title_list = []
        for i in range(len(self.titles)):
            title_list.append(self.titles[i][0])

        for idx in candidates:
            if (" " + clarification + " ") in title_list[idx] or ("(" + clarification + ")") in title_list[idx]:
                result.append(idx)
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
        ########################################################################
        # Binarize the supplied ratings matrix.                          #
        #                                                                      #
        # WARNING: Do not use self.ratings directly in this function.          #
        ########################################################################

        # Andrei did this
        binarized_ratings = np.zeros_like(ratings)
        for i in range(ratings.shape[0]):
            for j in range(ratings.shape[1]):
                if ratings[i][j] != 0:
                    if ratings[i][j] > threshold:
                        binarized_ratings[i][j] = 1
                    else:
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
        # Compute cosine similarity between the two vectors.                   #
        ########################################################################

        # Andrei did this
        normu = np.linalg.norm(u)
        normv = np.linalg.norm(v)
        similarity = np.dot(u, v) / (normu * normv)

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return similarity

    def recommend(self, user_ratings, ratings_matrix, k=10, creative=False):
        # Emma did this
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
        # Implement a recommendation function that takes a vector              #
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
        seen_movies = np.where(user_ratings != 0)[0]
        similarities = {}
        for i in range(len(user_ratings)): 
            if i not in seen_movies:
                similarities[i] = 0
                for j in seen_movies:
                    r_xj = user_ratings[j]
                    if np.linalg.norm(ratings_matrix[i]) != 0 and np.linalg.norm(ratings_matrix[j]) != 0:
                        similarities[i] += self.similarity(ratings_matrix[i], ratings_matrix[j]) * r_xj
        # sort dict by values (similarities) of movies, return as list of descending order tups
        sorted_sims = sorted(similarities.items(), key=lambda x:x[1], reverse=True)
        # returns list of first element (movie index) of each tuple, for the k highest tups
        recommendations = list(list(zip(*sorted_sims))[0])[:k]
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

        - To activate: type (once in the chatbot) ":debug on" ANYWHERE in the
        string. To deactivate: type ":debug off".
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
        Our chatbot is pirate themed and ready to bring you on board. It passes all
         of the starter mode tests along with some additional creative functionality. 
         You can type movies you liked or didn't like, and after 5 movies, the bot 
         will give you a recommendation. Have fun!" 
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
