# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import string
import porter_stemmer
import util
import numpy as np
import re
import random


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'SpongeBot'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        # For Tracking
        #keep track of previous movie and disambiguating
        self.prevMovieMentioned = ""
        self.prevSentiment = 0
        self.prevIndices = []

        self.yetToSuggest = True
        self.bot_prompt = '\001\033[96m\002%s> \001\033[0m\002' % self.name

        #check for clarification, index 0 = mentioned title, need sentiment
        #index 1 : asked them if they want recommendation
        self.isClarification = [0, 0]
        #vector for our specific user
        self.userRatings = np.zeros(len(self.titles))
        self.clean_titles = self.make_clean_titles()
        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################
        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = Chatbot.binarize(ratings)
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
        
        greetings = ["Ahoy there, matey! SpongeBot here, let's talk about movies!", 
                    "Hiya, pal! What's new under the sea? Any movies?",
                    "Good morning, Bikini Bottom! It's a beautiful day to talk about movies.",
                    "Salutations, my fine fishy friend! It's a great day to chat about movies.",
                    "Hey, Spongebuddy! Let's talk about movies!"
                    ]
        greeting_message = random.choice(greetings)

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
        
        goodbyes = ["Well, I guess this is goodbye, Bikini Bottom!",
                    "See ya later, Plankton!",
                    "I'll miss you like a fried Krabby Patty, buddy!",
                    "Goodbye, Gary! Take care of yourself and don't eat too much snail food.",
                    "So long, Patrick! Don't forget to change your underwear!"
                    ]
            
        goodbye_message = random.choice(goodbyes)

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
        response = ""
        #EDGE CASE
        if line == "":
            return self.generateResponses("irrelevant")

        #CREATIVE MODE PART 1
        if self.creative:
            #CHECK FOR QUESTIONS
            if "?" in line:
                return self.checkQuestion(line)

            #CHECK FOR EMOTIONS
            positive_emotions = ["happy", "joyful", "grateful", "ecstatic", "blissful", "confident", "pleased", "peaceful", "delighted",
            "lovestruck", "hopeful", "good", "glad", "great", "wonderful", "fantastic", "cheerful", "cheery", "jolly", "engaged", "excited", "interested",
            "inspired", "curious", "adventerous", "optimistic", "amazed", "bubbly", "positive", "renewed," "healthy", "stoked"]
            negative_emotions = ["sad", "angry", "bored", "dull", "upset", "frustrated", "guilty", "scared", "frightened","afriad", "tired", "sleepy", 
            "exhuasted", "worn out", "worn-out", "hurt", "disappointed", "insulted," "ashamed", "nervous", "embarassed", "weak", "enraged", "speechless", 
            "lonely", "appalled", "depressed", "anxious", "stressed", "impatient", "aggressive", "mad", "furious", "resentful", "hateful", "annoyed",
            "hopeless", "gloomy", "down", "dejected", "heartbroken", "grieving", "mourning", "mean", "negative", "cynical", "shocked,", "unhappy",
            "lost", "troubled", "confused","irritated", "fed up", "bitter"]
            neutral_emotions = ["alright", "meh", "so so", "so-so", "unsure", "not sure", "average", "mid"]
            if "I" in line and '"' not in line:
                for emotion in positive_emotions:
                    if emotion in line:
                        return self.generateResponses("feeling_pos") + emotion + ". "
                    
                for emotion in negative_emotions:
                    if emotion in line:
                        return self.generateResponses("feeling_neg") + emotion + ". "

                for emotion in neutral_emotions:
                    if emotion in line:
                        return self.generateResponses("feeling_neutral") + emotion + ". "
        
        #Check Clarification flags, to distinguish between multiple titles.
        if self.isClarification[0] == 1:
            self.isClarification[0] = 0
            isDate = re.search("\d{4}", line)
            gaveDate = False
            while isDate:
                gaveDate = True
                givenYear = isDate.group(0)
                for index in self.prevIndices:
                    if givenYear == self.clean_titles[index][1]:
                        if self.prevSentiment > 0:
                            self.userRatings[index] = self.prevSentiment
                            response += self.generateResponses("pos_response")
                        elif self.prevSentiment < 0:
                            self.userRatings[index] = self.prevSentiment
                            response += self.generateResponses("neg_response")
                        else:
                            response += self.clarifySentiment(index, self.prevMovieMentioned)
                if response == "":
                    next = input(f"%sHey, that wasn't one of the years I was considering! Which year did you mean out of the ones I mentioned?\n>" % self.bot_prompt)
                    if next == ":quit":
                        exit()
                    isDate = re.search("\d{4}", next)
                else:
                    return response
            else:
                if gaveDate:
                    #"Let's agree to disagree about that one. What movie should we talk about next?"
                    response += self.generateResponses("next_movie_input")
                else:
                    return self.process(line)
            return response


        #Check if want recommendations
        if self.isClarification[1] == 0 and self.wantRec(line, 0) != 0 and np.count_nonzero(self.userRatings) > 4:
            response += self.generateResponses("confirm_recs")
            self.isClarification[1] = 1
            return response

        #process recommendations
        if self.isClarification[1] == 1:
            nRecs = 0
            rec = self.wantRec(line, 1)
            #design decision: we can only recommend relative to how much we know. Here we choose just over half.
            topK = np.count_nonzero(self.userRatings) // 2 + 1
            if rec != -1:
                recIndexes = self.recommend(self.userRatings, self.ratings, topK)
            while rec != -1 and nRecs < len(recIndexes):
                if rec == 1:
                    temp = self.generateRecomendations(self.titles[recIndexes[nRecs]][0])
                    another = input(self.bot_prompt + temp + "\n> ")
                    if another == ":quit":
                            exit()
                    nRecs += 1
                else:
                    another = input(f"%sNot sure if you want another suggestion... you're being a little sandy. Can you be more clear? (Hint: simple yes or no works best)\n> " % self.bot_prompt)
                    if another == ":quit":
                            exit()
                rec = self.wantRec(another, 1)

            if nRecs == topK and rec != -1:
                response += self.generateResponses("no_more_recs")
            elif rec == -1:
                response += self.generateResponses("reject_recs")
            self.isClarification[1] = 0
            return response

        #CREATIVE MODE PART 2        
        if self.creative:
            titles = self.extract_titles(line)
            titles = self.remove_substrings(titles) #remove redundancies
            potTitles = re.findall('"([^"]*)"', line)

            #IF WE CAPTURE TITLES NOT IN QUOTES
            if len(titles) > len(potTitles):
                while True:
                    answer = input(f"%sIt looks like you might not have movies in quotes. Are all your movies in quotes? (Hint: simple yes or no works best)\n> " % (self.bot_prompt))
                    if "y" == answer.lower()[0]:
                        response += self.generateResponses("post_clarify")
                        break
                    if "n" == answer.lower()[0]:
                        return self.generateResponses("reenter_command")
                    elif answer == ":quit":
                        exit()
            titles += potTitles

            #IF WE CAPTURE MOVIE TITLES!
            if len(titles) > 0:
                for title in titles:
                    if line[line.find(title) - 1] != '"':
                        newTitle = '"' + title + '"'
                        line = line.replace(title, newTitle)
                    
                    #FIND THE INDICES
                    indices = self.find_movies_by_title(title)

                    #IF WE CANT FIND THE MOVIE, TRY TO FIND SIMILAR MOVIES (MAYBE TYPO)
                    if len(indices) == 0:
                        candidates = self.find_movies_closest_to_title(title)
                        if len(candidates) == 0:  #IF THE MOVIE JUST HAS NOTHING CLOSE TO IT
                            return "Sandy Cheeks! I couldn't find anything related to %s. Please check your response for typos or tell me about another movie." % title
                        candidatesString = self.indexListToString(candidates)
                        answer = title
                        while True:
                            answer = input(f"%sBarnacles! I couldn't find %s. Which of the following did you mean: %s? (Hint: type one of the choices after the colon)\n> " % (self.bot_prompt, answer, candidatesString))
                            if answer.lower() in candidatesString.lower():
                                response += "Thanks for clarifying!\n"
                                break
                            elif answer == ":quit":
                                exit()
                        line = line.replace('"' + title + '"', '"' + answer + '"')

                # START EXTRACTING MULTIPLE SENTIMENTS
                sentiments = self.extract_sentiment_for_movies(line)
                if len(sentiments) > 0:
                    for sentiment in sentiments:
                        curtitle, rating = sentiment
                        indices = self.find_movies_by_title(curtitle)
                        
                        #UPDATE RATINGS
                        self.userRatings[indices[0]] = rating
                        if rating > 0:
                            response += self.generateResponses("pos_response_creative") + curtitle + ". "
                        elif rating < 0:
                            response += self.generateResponses("neg_response_creative") + curtitle + ". "
                        else:
                            response += self.clarifySentiment(indices[0], curtitle)
                    response += " " + self.generateResponses("next_movie_input")
                else:
                    response = self.generateResponses("feel_request")
            else:
                response = self.generateResponses("irrelevant")
        
        #STARTER MODE
        else:
            #normal inputs
            titles = self.extract_titles(line)
            sentiment = self.extract_sentiment(line)
            #No title detected Branch
            if len(titles) == 0:
                return self.generateResponses("irrelevant")
            #title detected branch
            else:
                #user gave us titles to work with, remember starter mode is only things in quotes
                if len(titles) > 1:
                    #shortcircuit
                    return self.generateResponses("too_many_movies")
                indices = self.find_movies_by_title(titles[0])
                if len(indices) > 0:
                    if len(indices) == 1:
                        if sentiment > 0:
                            ##############
                            response += self.generateResponses("pos_response_creative") + titles[0] + ". " + "Tell me about another movie you've seen."
                            self.userRatings[indices[0]] = sentiment
                        elif sentiment < 0:
                            #you did not like "movie"
                            ######################
                            response += self.generateResponses("neg_response_creative") + titles[0] + ". " + "Tell me about another movie you've seen."
                            self.userRatings[indices[0]] = sentiment
                        else:
                            clarification = input(f"%sI see that you mentioned %s, can you tell me a little more about how you feel about it?\n> " % (self.bot_prompt, titles[0]))
                            if clarification == ":quit":
                                exit()
                            clarification_sentiment = self.extract_sentiment(clarification)
                            if clarification_sentiment == 0:
                                response += self.generateResponses("irrelevant")
                            elif clarification_sentiment < 0:
                                self.userRatings[indices[0]] = clarification_sentiment
                                response += self.response("neg_response")
                            else:
                                self.userRatings[indices[0]] = clarification_sentiment
                                response += self.generateResponses("pos_response")
                    else: #more than one index for a single title
                        #in starter mode, since the title must match, the only difference can be the years, thus we proceed with
                        #that assumption
                        self.isClarification[0] = 1
                        self.prevMovieMentioned = titles[0]
                        self.prevIndices = indices
                        self.prevSentiment = sentiment
                        response += "I found more than one movie called " + titles[0] + ", which year did you mean: "
                        #gather years
                        for i in range(len(indices)):
                            response += str(self.clean_titles[indices[i]][1])
                            if i < len(indices) - 2:
                                result += ", "
                            elif i == len(indices) - 2:
                                response += " or "    #I'm so sorry oxford comma I love you
                        return response + "?"
                else: #weird input
                    response += self.generateResponses("irrelevant_creative") + titles[0] + ". " + "Let's talk about another movie."
        if self.yetToSuggest and np.count_nonzero(self.userRatings) > 4:
            self.yetToSuggest = False
            response += " " + self.generateResponses("offer_recs")
            self.isClarification[1] = 1
            pass
            #woohoo we can recommend

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return response

    def checkQuestion(self, line):
        line = line.lower().strip(",")
        line = line.replace("what's", "what is")
        line = line.replace("why's", "why is")
        line = line.replace("who's", "who is")
        line = line.replace("how's", "how is")
        line = line.replace("when's", "when is")
        line = line.replace("where's", "where is")
        if line == "who are you?":
            return "I am SpongeBot, a chatbot that can recommend you movies after you give me at least 5 movie preferences!"
        response = ""
        positive_response_pool = ["Yes, I", "For sure! I", "Of course! I", "It's Spongebot here! Of course I"]
        negative_response_pool = ["Sorry, I don't think I", "Barnacles! I don't think I", "Oops, I don't think I"]
        indicators1 = ["can you", "may you", "will you", "have you", "are you"]
        for indicator in indicators1:
            if indicator.lower() in line.lower() and "?" in line:
                first_word = indicator.split()[0]
                if line.split()[0] != first_word:
                    break
                start = line.lower().find(indicator.lower()) + len(indicator)
                end = line.find("?")
                response = line[start:end]
                response = response.replace(" my ", " your ")
                response = response.replace(" I ", " you ")
                response = response.replace(" me ", " you ")
                if "movie" in response and ("recommend" in response or "suggest" in response):
                    response = random.choice(positive_response_pool) + first_word + response + "!"
                    return response
                else:
                    if first_word == "are":
                        response = "Sorry, I don't think I am" + response + "!"
                    else:
                        response = random.choice(negative_response_pool) + " " + first_word + response + "!"
                    return response
        indicators2 = ["how", "why", "when", "which"]
        for indicator in indicators2:
            if indicator.lower() in line.lower() and "?" in line:
                first_word = indicator.split()[0]
                if line.split()[0] != first_word:
                    break
                start = line.lower().find(indicator.lower()) + len(indicator)
                end = line.find("?")
                response = line[start:end]
                response = response.replace(" my ", " your ")
                response = response.replace(" I ", " you ")
                response = response.replace(" me", " you")
                response = random.choice(negative_response_pool) + " know " + first_word + response + "!"
                return response
        indicators3 = ["what are", "what is", "what was", "who are", "who is", "who was"]
        for indicator in indicators3:
            if indicator.lower() in line.lower() and "?" in line:
                first_word = indicator.split()[0]
                if line.split()[0] != first_word:
                    break
                last_word = indicator.split()[1]
                start = line.lower().find(indicator.lower()) + len(indicator)
                end = line.find("?")
                response = line[start:end]
                response = response.replace(" my ", " your ")
                response = response.replace(" I ", " you ")
                response = response.replace(" me ", " you ")
                response = random.choice(negative_response_pool) + " know " + first_word + response + " " + last_word + "!"
                return response
        if response == "":
            return random.choice(negative_response_pool) + " know how to answer that question."
    
    def generateRecomendations(self, string):
        responses = ["Woohoo! I think " + string + " would be a fin-tastic fit! How about another suggestion?",
                    "Gotcha, I think you would find " + string + " interesting! How about another suggestion?",
                    "You would be a fan of " + string + "! How about another suggestion?",
                    "I think you will enjoy " + string + "! How about another suggestion?",
                    ]
        return random.choice(responses)

    def generateResponses(self, scenario):
        if scenario == "pos_response":
            responses = ["Nice to know you enjoyed it!",
                         "Gotcha, I also thought it was fantastic!",
                         "Gotcha, you're a fan of it!",
                         "I have to agree with this one!",
                         "Glad to know you liked it!",
                         "Fin-tastic!"]
        elif scenario == "pos_response_creative":
            responses = ["Nice to know you enjoyed ",
                         "Gotcha, you're a fan of ",
                         "It's good to know you liked ",
                         "Fin-tastic! I'm thrilled to know you liked "]
            
        elif scenario == "neg_response":
            responses = ["Sorry you didn't like it.",
                         "Agreed, that movie was fish paste!",
                         "Sorry you didn't enjoy it as much.",
                         "Seriously, barnacles movie!"
                         ]

        elif scenario == "neg_response_creative":
            responses = ["Sorry you didn't like ",
                        "Gotcha, you weren't a fan of ",
                        "Agreed, Squidward also didn't like ",
                        "I'm sorry to hear you didn't enjoy "]

        elif scenario == "neutral_response_creative":
            responses = ["Maybe elaborate more on ",
                        "Maybe tell me more about ",
                        "Tell me how you felt about "]

        elif scenario == "next_movie_input":
            responses = ["Hmm... what movie do you want to talk about next?",
                         "Fin-tastic! Any movies you want to talk about next?",
                         "What other movies have you watched?"]

        elif scenario == "confirm_recs":
            responses = ["Gary says you want recommendations! Is this true?",
                         "Are you ready for clam-tastic recommendations?",
                         "Now, would you like some recommendations?"]

        elif scenario == "offer_recs":
            responses = ["Also, fin-tastic news! I now know enough about your tastes to give some suggestions. Would you like a recommendation?",
                         "Krabby patty time! Are you ready for some recommendations?",
                         "Just making some calculations... PERFECT! Do you want recommendations?"
                         ]
            
        elif scenario == "no_more_recs":
            responses = ["I ran out of recommendations for now! Sea-riously sorry about that, I'll think of some more once we talk about other movies you've watched.",
                         "Woah, I've already given a lot! How about you tell me more about some other movies you've watched?",
                         "Tell me more about some other movies you've watched. Then I can recommend some more!"
                         ]
            
        elif scenario == "reject_recs":
            responses = ["That's alright, I'm always happy as a clam to help, just let me know if need more suggestions.",
                         "Perfect! Just let me know if you need want recommendations!",
                         "Sure, but let me know if you want more suggestions!"
                         ]
            
        elif scenario == "post_clarify":
            responses = ["Aye, thanks for clarifying!",
                         "Thanks for the clarification!",
                         "Fin-tastic! Thanks for clarifying."
                        ]

        elif scenario == "reenter_command":
            responses = ["Aye, just re-enter your command! Make sure to add quotes around your titles.",
                         "Sorry, could you re-enter your command? Please put your titles in quotes!"
                         ]

        elif scenario == "feel_request":
            responses = ["Tell me a little more about how you feel about these movies!",
                         "Hmm... how do you feel about these movies?"
                         ]

        elif scenario == "irrelevant":
            responses = ["Oops! I don't think you mentioned any movies known to Bikini Bottom, let's talk about movies!",
                         "You sound like Patrick! He sometimes doesn't make sense. Let's talk about movies!",
                         "Sorry, didn't quite 'catch' that. Let's talk about or 'fish' some movies!",
                         "Oh my sandy cheeks! Let's just talk about movies!"
                         ]
        
        elif scenario == "irrelevant_creative":
            responses = ["Fish paste! I don't have any information about ",
                         "Oops, I don't understand ",
                         "Barnacles! I don't know information about ",
                         "Sorry, I don't have information on "]
            
        elif scenario == "too_many_movies":
            responses = ["Woah! Looks like you mentioned a fish load of movies, can we discuss them one at a time?",
                         "Barnacles! That's too many movies for me to handle, maybe go one at a time?",
                         "Fish paste! That's quite a lot of movies. How about discuss one at a time?"]
        
        elif scenario == "fail_search":
            responses = ["Sandy Cheeks! I couldn't find anything related to ",
                        "Oops, I didn't find any matches with ",
                        "Barnacles! Couldn't find anything with "]
            
        elif scenario == "feeling_pos":
            responses= ["I am so glad that you are feeling ", 
                        "It's good to hear you're feeling ",
                        "So happy to know that you're feeling ",
                        "Wonderful to hear that you're feeling "]
        
        elif scenario == "feeling_neg":
            responses = ["I am sorry if I made you feel ",
                         "I'm so sorry you feel ",
                         "It's sad to hear that you feel ",
                         "Sorry to hear that you feel "]
        
        elif scenario == "feeling_neutral":
            responses = ["It's ok. I am also feeling ",
                         "Same, I'm feeling pretty "
                         "It's good to hear you're ",
                         "It's reassuring to hear that you are "]

        return random.choice(responses)

    def remove_substrings(self, potentialTitles):
        subStrings = []
        for pT in potentialTitles:
            for other in potentialTitles:
                if pT.lower() == other.lower():
                    continue
                if pT.lower() in other.lower():
                    subStrings.append(pT)
        potentialTitles = list(set(potentialTitles) - set(subStrings))
        return potentialTitles

    def indexListToString(self, indices):
        if len(indices) == 1:
            return self.clean_titles[indices[0]][0][0]
        res = ""
        lastIndex = indices[len(indices) - 1]
        indices = indices[:-1]
        for i in indices:
            title = self.clean_titles[i][0][0]
            res += title + ', '
        lastTitle = self.clean_titles[lastIndex][0][0]
        res += "or " + lastTitle
        return res

    def clarifySentiment(self, index, title):
        response = ""
        clarification = input(f"%sI see that you mentioned %s, can you tell me a little more about how you feel about it?\n> " % (self.bot_prompt, title))
        if clarification == ":quit":
            exit()
        clarification_sentiment = self.extract_sentiment(clarification)
        if clarification_sentiment == 0:
            response += "Didn't quite get that, sorry! Let's talk about something else"
        elif clarification_sentiment < 0:
            self.userRatings[index] = clarification_sentiment
            response += "Gotcha, you weren't a fan."
        else:
            self.userRatings[index] = clarification_sentiment
            response += "Gotcha, I also thought it was fin-tastic!"
        return response
    
    def wantRec(self, line, mode):
        line = line.lower()
        if mode == 1:
            yes_words = ["yes", "absolutely", "definitely", "sure", "of course",]
            no_words = ["no", "not", "never", "negative"]

            ifYes = any(word in line.split() for word in yes_words)
            ifNo = any(word in line.split() for word in no_words)

            if ifYes and not ifNo:
                return 1
            elif not ifYes and ifNo:
                return -1
            elif ifYes and ifNo:
                if no_words[1] in line:
                    return -1
            #ambiguous if it gets here
            return 0
        else:
            rec_words = ["suggest", "recommend"]
            if any(word in line for word in rec_words):
                return 1
            return 0
            

    def movieExists(self, potTitle):
        if self.creative:
            return True #need to fix this
        else:
            potTitle = potTitle.translate(str.maketrans('', '', string.punctuation))
            if self.title_to_index.get(potTitle):
                return True 
            return False

    def make_clean_titles(self):
        res = []
        for movie in self.titles:
            allTitles = []
            title = movie[0]
            yearMatch = re.search("\((\d{4})\)", title)
            year = 0
            #find year
            if yearMatch:
                year = yearMatch.group(1)
            #find all possible titles
            mainTitleMatch = re.search("^(.*?)(?=\([^()]{4,}\))", title)
            if not mainTitleMatch:
                #only edge cases don't contain years, in our dataset also don't contain alternate titles.
                allTitles.append(Chatbot.normalizeTitle(movie[0]))
            else:
                allTitles.append(Chatbot.normalizeTitle(mainTitleMatch.group(0)))

            if year:
                #doing this now bc it helped above
                title = title[:-7]
            
            altTitlesMatch = re.findall("\(([^()]{4,})*\)", title)
            for alt in altTitlesMatch:
                if re.search("a.k.a.", alt):
                    alt = re.sub("a.k.a. ", "", alt)
                allTitles.append(Chatbot.normalizeTitle(alt))
            res.append((allTitles, year))
        return res   
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
        res = []
        if self.creative:
            year = 0
            isYear = re.search("\((\d{4})\)", preprocessed_input)
            if isYear:
                year = isYear.group(1)
            #make lowercase and remove punctuation
            input = preprocessed_input.lower().translate(str.maketrans('', '', string.punctuation))
            for i, movie in enumerate(self.clean_titles):
                for title in movie[0]:
                    if title.lower() in input and all(word in input.split() for word in title.lower().split()):
                        if year and year == movie[1]:
                            res.append(title)
                        elif not year:
                            res.append(title)
        else:
            res = re.findall('"([^"]*)"', preprocessed_input)
        return res

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
        year = 0
        isYear = re.search("\((\d{4})\)", title)
        if isYear:
            year = isYear.group(1)
            title = title[:-7]

        if self.creative:
            potentialTitles = self.extract_titles(title)
            if potentialTitles:
                subStrings = []
            #get rid of titles that are substring titles
                for pT in potentialTitles:
                    for other in potentialTitles:
                        if pT == other:
                            continue
                        if pT in other:
                            subStrings.append(pT)
                potentialTitles = list(set(potentialTitles) - set(subStrings))
            else:
                potentialTitles.append(title)
            for i, movie in enumerate(self.clean_titles):
                for pot in potentialTitles:
                    for alt in movie[0]:
                        alt_parts = set(alt.split())
                        pot_parts = set(pot.split())
                        if pot_parts.issubset(alt_parts):
                            if year and year != movie[1]: #adjust for bad years
                                    continue
                            res.append(i)
                            break
                        
        else:
            title = title.translate(str.maketrans('', '', string.punctuation))
            for i, movie in enumerate(self.clean_titles):
                for name in movie[0]:
                    if title == name:
                        if year and year == movie[1]:
                            res.append(i)
                        elif not year:
                            res.append(i)
        return res

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
        titles = re.findall('"([^"]*)"', preprocessed_input)
        for title in titles:
            preprocessed_input = preprocessed_input.replace('"' + title + '"', "")
        input_list = preprocessed_input.split()
        p = porter_stemmer.PorterStemmer()
        sentiment = ""
        negation_words = ["not", "no", "never", "neither", "nor", "none", "nothing", "nowhere", "nobody", "dislike"]
        self.sentiment = {p.stem(key): self.sentiment[key] for key in self.sentiment}
        neg_words = 0
        pos_words = 0
        negate = False

        strong = False
        strong_words = ["love", "adore", "amazing", "best", "perfect", "stunning", "astounding", "astonishing", "wonderful", "extraordinary", "phenomenal", "hate", "despise", "terrible", "awful", "loath", "detest", "dreadful", "horrible", "atrocious", "repugnant", "vile", "revolting", "repulsive"]
        strong_words = [p.stem(x) for x in strong_words]
        superlative_words = ["really", "very"]
        for word in input_list:
            if word in negation_words or "n't" in word:
                negate = True
            if word in superlative_words or "ly" in word or word.isupper():
                strong = True
            word = word.lower()
            word = p.stem(word)
            if word in strong_words:        
                strong = True
            if word in self.sentiment:
                if self.sentiment[word] == "pos":
                    if negate:
                        neg_words += 1
                        negate = False
                    else:
                        pos_words += 1
                elif self.sentiment[word] == "neg":
                    if negate:
                        pos_words += 1
                        negate = False
                    else:
                        neg_words += 1

        if pos_words > neg_words:
            sentiment = 1
        elif neg_words > pos_words:
            sentiment = -1
        else:
            sentiment = 0

        if self.creative:
            if strong:
                sentiment *= 2
            return sentiment
        else:
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
        res = []
        titles_list = re.findall('"([^"]*)"', preprocessed_input)

        same = ["both", "either", "or", "and"]
        opposite = ["but", "not", "neither", "nor"]
        start = 0
        prev_sentiment = 0
        for title in titles_list:
            index = preprocessed_input.find(title) + len(title) + 1
            subinput = preprocessed_input[start:index]
            subinput_list = subinput.split(" ")
            sentiment = self.extract_sentiment(subinput)
            if sentiment == 0:
                sentiment = prev_sentiment
                for word in subinput_list:
                    if word in same:
                        sentiment = prev_sentiment
                    elif word in opposite:
                        sentiment = prev_sentiment * -1
            res.append((title, sentiment))
            prev_sentiment = sentiment
            start = index + 1
        return res

# TAKEN FROM INTERNET : https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python (6th version)
    # Christopher P. Matthews
    # christophermatthews1985@gmail.com
    # Sacramento, CA, USA
    @staticmethod
    def lev_dist(s, t):
        ''' From Wikipedia article; Iterative with two matrix rows. '''
        if s == t: return 0
        elif len(s) == 0: return len(t)
        elif len(t) == 0: return len(s)
        v0 = [None] * (len(t) + 1)
        v1 = [None] * (len(t) + 1)
        for i in range(len(v0)):
            v0[i] = i
        for i in range(len(s)):
            v1[0] = i + 1
            for j in range(len(t)):
                cost = 0 if s[i] == t[j] else 2
                v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
            for j in range(len(v0)):
                v0[j] = v1[j]
                
        return v1[len(t)]

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
        candidates = []
        title = title.strip().lower()
        for i, data in enumerate(self.clean_titles):
            movies = data[0]
            for movie in movies:
                dist = self.lev_dist(title, movie.lower())
                if dist <= max_distance:
                    candidates.append((i, dist))
                    break
        if candidates == []:
            return res
        candidates = sorted(candidates, key=lambda x:x[1])
        min_dist = candidates[0][1]
        for candidate in candidates:
            if candidate[1] == min_dist:
                res.append(candidate[0])
            else:
                break
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
        ordinals = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eigth", "ninth", "tenth"]
        old = ["old", "older", "oldest"] 
        new = ["new", "newer", "newest", "recent", "most recent"]
        res = []  
        
        # remove "the", "one", and "movie" from clarification (e.g, "the most recent one" -> "most recent")
        clarify = clarification.split(" ")
        if clarify[0].lower() == "the":
            clarify = clarify[1:]
        if clarify[-1].lower() == "movie" or clarify[-1].lower() == "one":
            clarify = clarify[:-1]
        clarification = " ".join(clarify)

        # remove punctuation and capitalization
        clarification = re.sub("[.'!?]", "", clarification).strip()
        clarification = clarification.lower()

        # if clarification is substring of movie title
        for c in candidates:
            titles = self.clean_titles[c][0] #list of alternate titles for movie
            year = self.clean_titles[c][1]
            for title in titles:
                if clarification in title.lower() or clarification == year:
                    res.append(c)
        
        if len(res) == 0 and self.creative:
            # if clarification is ordinal (e.g, first, second, third or 1, 2, 3...)
            if clarification in ordinals:
                res.append(candidates[ordinals.index(clarification)])
            elif clarification.isdigit() and int(clarification) > 0 and int(clarification) <= len(candidates):
                res.append(candidates[int(clarification) - 1])

            # if clarification involves year (e.g, old, new, recent etc)
            else:
                newest = int(self.clean_titles[candidates[0]][1])
                oldest = int(self.clean_titles[candidates[0]][1])
                newest_index = candidates[0]
                oldest_index = candidates[0]
                for c in candidates:
                    if int(self.clean_titles[c][1]) > newest:
                        newest_index = c
                    elif int(self.clean_titles[c][1]) < oldest:
                        oldest_index = c
                if clarification in new:
                    res.append(newest_index)
                elif clarification in old:
                    res.append(oldest_index)

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
        # Binarize the supplied ratings matrix.                                #
        #                                                                      #
        # WARNING: Do not use self.ratings directly in this function.          #
        ########################################################################
        binarized_ratings = np.where(ratings > threshold, 1, -1)
        binarized_ratings = np.where(ratings == 0, 0, binarized_ratings)

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
        # Compute cosine similarity between the two vectors.                    #
        ########################################################################
        u_norm = np.linalg.norm(u)
        v_norm = np.linalg.norm(v)
        if u_norm:
            u = u / u_norm
        if v_norm:
            v = v / v_norm
        similarity = np.dot(u, v)
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
        #find cosine similarity between user vector and columns of the matrix
        scores = []
        relevant_indices = []
        #get rid of spares
        for i in range(len(user_ratings)):
            if user_ratings[i] != 0:
                relevant_indices.append(i)
        #for every movie calculate a rec score
        for i in range(len(ratings_matrix)):
            #ignore movies user has already seen
            if relevant_indices.count(i) > 0:
                continue
            r = 0
            cur = ratings_matrix[i]
            #summation part
            for j in relevant_indices:
                s_ij = self.similarity(cur, ratings_matrix[j])
                r_xj = user_ratings[j]
                r += s_ij * r_xj
            scores.append((r, i))
        
        recommendations = [score[1] for score in sorted(scores, key=lambda x: x[0], reverse=True)[:k]]
        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        return recommendations

    @staticmethod
    def normalizeTitle(input):
        articles = ["A", "An", "The", "L'", "La", "El", "Da"]
        parts = input.strip().split()
        if parts[-1] in articles and "," in parts[-2]:
            #shuffle article around
            art = parts.pop()
            parts.insert(0, art)
        #rejoin correctly ordered parts and get rid of punctuation
        normalizedTitle = " ".join(parts).translate(str.maketrans('', '', string.punctuation))
        return normalizedTitle

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
        description = "SpongeBot is a chatbot that recommends movies to a user based on the user’s input from the MovieLens database. The user can type several movies they liked and disliked. After SpongeBot takes in several inputs, it offers movie recommendations to the user based on his or her likes and dislikes. SpongeBot can account for alternate movie titles, different versions of the same movie (year), and user typos. SpongeBot has a SpongeBob persona!"
        return description
        """
        Your task is to implement the chatbot as detailed in the PA7
        instructions.
        Remember: in the starter mode, movie names will come in quotation marks
        and expressions of sentiment will be simple!
        TODO: Write here the description for your own chatbot!
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')