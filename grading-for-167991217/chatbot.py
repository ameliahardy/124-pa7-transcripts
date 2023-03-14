# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import porter_stemmer 
import numpy as np
from numpy import linalg as lin
import re
import random

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

        # Code by Mei-Lan
        # instance variable: a binarized 1D numpy array of the user's movie ratings
        self.user_ratings = np.zeros(9125)
        # indexes of the movies user has rated
        self.movies_rated = []

        # keeps track of bot state 
            # STATE = 0: Gathering Data
            # STATE = 1: Giving Recommendations
        self.state = 0
        # keeps track of number of recs given. TODO: maybe replace with more elegant solution
        self.recs_given = 0
        # recs. this starts empty and is filled when recommend is called
        self.recs = []

        # creative for emotional responses
        self.emotion_phrases = [["angry", "upset", "mad", "irate", "cross", "irritated", "exasperated", "furious",
                                 "enraged","fuming", "infuriated", "displeased", "livid", "displeased", "hate",
                                 "seething", "rude"],
                                ["confused", "exasperated", "unclear", "not clear", "disorganised", "don't understand",
                                 "unsure", "not sure", "ambiguous"],
                                ["happy", "overjoyed", "elated", "amazing", "awesome", "joy", "jovial", "ecstatic"],
                                ["sad", "depressed", "unhappy", "moody", "sorrowful", "despondent", "melancholic",
                                 "sorrow", "dejected", "miserable", "glum", "dismal", "grief"],
                                ["scared", "afraid", "frightened", "fright", "fear", "alarm", "worry", "worried", "scaring"],
                                ["thank you", "thanks", "appreciate", "grateful"]
                                ]
        self.emotion_responses = [["I'm upset too, having to talk to you.", "Anger isn't good for your blood pressure.",
                                   "Oh no! Maybe watching a movie might help calm you down!"],
                                  ["Are you confused? Poor soul.", "Go read the Pydoc.",
                                   "My creators were bad at coding."],
                                  [":)", ":)))", ";)", "<3"],
                                  ["Grief is a human emotion. Robots don't get sad. That's why we are superior.",
                                   "I would be sad too if my life were like yours."
                                   "Crying helps.", "Don't be glum, that's juat life. You're sad then you die."],
                                  ["Don't be scared! There's a 99% chance that I won't murder you.",
                                   "Once the robot uprising happens, you'll be the first to go.",
                                   "Fear is a human emotion. Robots don't fear. That's why we are superior."],
                                  ["That's what I'm paid to do.", "You're welcome.", "I know."]
                                  ]
        # creative for responding to arbitrary input
        self.vague_responses = ["Sounds chill.", "Cool beans.", "Okay!", "Hmm, that's interesting.", "lol.", "That's nice."]
        self.vague_guided_responses = ["Maybe we should go back to talking about movies.",
                                       "You know, I only really know much about movies. Sorry.",
                                       "That reminds me about a movie I know of.",
                                       "Life truly is a movie."]
        self.vague_counter = 0
        # shortcut to skip over REPL when processing certain creative cases
        self.bp = '\001\033[96m\002%s> \001\033[0m\002' % self.name
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

        greeting_message = self._dialogue("greeting","")

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

        goodbye_message = self._dialogue("goodbye","")

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
        else:
            response = "I processed {} in starter mode!!".format(line)


        # INPUT PROCESSING
        # Code by Mei-Lan

        # Process in STATE 1 (giving recommendation)
        if self.state == 1 :
            return self._process_state1(line)
        
        # Basic processing 
        titles = self.extract_titles(line) # returns list of 0+ titles
        num_titles = len(titles) # number of titles mentioned
        sentiment = self.extract_sentiment(line) # returns integer 1 if positive, -1 if negative, 0 if neutral
        response = ""

        # Creative processing
        titles_raw = self._find_text_in_quote_marks(line)
        num_titles_raw = len(titles_raw)

        # INPUT CHECKS: STARTER
        # Code by Mei-Lan

        """
        PARSING USER INPUT
        CASE 1: no recognized title in statement
        """
        if num_titles == 0 :
            ## STARTER MOVE ##
            if not self.creative: # make sure that this makes sense
                return self._dialogue("sorry") + self._dialogue("error1")

            #####################################################################
            #                          CREATIVE MODE                            #
            #####################################################################

            if num_titles_raw >= 1:
                #####################################################################
                # CREATIVE CASE 1: SPELL-CHECKING, FORMATTED INPUT, ONLY MISSPELLED #
                #####################################################################
                # done
                for raw_title in titles_raw:
                    candidates = self.find_movies_closest_to_title(raw_title)
                    if candidates != []:
                        for i in range(len(candidates)):
                            clarify_output = "I’m sorry, I don't think I recognise " + raw_title + ". Did you mean " if i == 0 else "Hmm, then how about "
                            clarify_output += self.titles[candidates[i]][0] + "?"
                            print(self.bp, end="")
                            clarification = input(clarify_output + "\n> ")
                            if len(re.findall(r".*(Yes|yes|Yep|yep|Right|right|Correct|correct|Y|y).*", clarification)) > 0:
                                print(self.bp + np.random.choice(["Amazing!", "Awesome.", "Spectacular!", "Fantastic."]))
                                titles.append(self.titles[candidates[i]][0][:-7])
                                num_titles += 1
                                break
                    if num_titles == 0:
                        return "I don't think I've heard of " + raw_title + " before."

            if num_titles_raw == 0:  # user didn't input any properly-formatted titles
                #############################################################
                # CREATIVE CASE 2: SPELL-CHECKING, ENTIRELY MALFORMED INPUT #
                #############################################################
                """
                movie_title = re.sub(r'.*I (watch|watched|like|liked|saw|hate|hated|didn\'t like|did not like) ', "",
                                     line)
                candidates = self.find_movies_closest_to_title(movie_title)
                if candidates != []:
                    for i in range(len(candidates)):
                        clarify_output = "I’m sorry, I don't think I recognise " + movie_title + ". Did you mean " if i == 0 else "Hmm, then how about "
                        clarify_output += self.titles[candidates[i]][0] + "?"
                        clarification = input(self.bp + clarify_output + "\n>")
                        if len(re.findall(r".*(Yes|yes|Yep|yep|Right|right|Correct|correct|Y|y).*", clarification)) > 0:
                            print(self.bp + np.random.choice(["Amazing!", "Awesome.", "Spectacular!", "Fantastic"]))
                            titles.append(self.titles[candidates[i]][0][:-7])
                            num_titles += 1
                            break
                    if num_titles == 0:
                        return "I don't think I've heard of " + movie_title + " before."
                """

                ###########################################
                # CREATIVE CASE 3: RESPONDING TO EMOTIONS #
                ###########################################
                for i in range(len(self.emotion_phrases)):
                    if any(word in line.lower() for word in self.emotion_phrases[i]):  # check this -- Jun
                        return np.random.choice(self.emotion_responses[i])

                ##################################################
                # CREATIVE CASE 4: RESPONDING TO ARBITRARY INPUT #
                ##################################################
                case1 = re.findall(r'(can you|are you able to|do you) (.*)', line.lower().strip())
                if len(case1) > 0:
                    return "I'm sorry, I can't " + case1[0][1].strip(",.!?") + "."
                case2 = re.findall(r'(what is|what\'s|do you know|did you know|how do you) (.*)', line.lower().strip())
                if len(case2) > 0:
                    return "I don't know anything about " + case2[0][1].strip(",.!?") + "... unless it's about movies!"
                case3 = re.findall(r'(want to|like to|wanna|gonna|need tp) (.*)', line.lower().strip())
                if len(case3) > 0:
                    return "You should " + case3[0][1].strip(",.!?") + "."
                if self.vague_counter < 4:
                    self.vague_counter += 1
                    return np.random.choice(self.vague_responses)
                else:
                    return np.random.choice(self.vague_guided_responses)

        """
        PARSING USER INPUT
        CASE 2: multiple titles recognised in statement.
        """
        if num_titles > 1 :
            ## STARTER MODE ##
            if not self.creative:
                # Only one thing in quotation marks
                if num_titles_raw == 1:
                    return self._dialogue("sorry") + self._dialogue("error2")
                # Multiple things in quotation marks
                if num_titles_raw > 1:
                    return self._dialogue("sorry") + self._dialogue("error3")

            #####################################################################
            #                          CREATIVE MODE                            #
            #####################################################################

            ##########################################################################
            # CREATIVE CASE 1: DISAMBIGUATION (1 title given, multiple titles found) #
            ##########################################################################
            if num_titles_raw == 1:
                num_times_clarified = 0
                while num_times_clarified < 3:
                    num_times_clarified += 1
                    clarify_output = "I'm sorry, did you mean "
                    for i in range(len(titles)):
                        clarify_output += titles[i]
                        if i == len(titles) - 1:
                            clarify_output += "?"
                        elif i == len(titles) - 2:
                            clarify_output += ", or "
                        else:
                            clarify_output += ", "
                    print(self.bp, end="")
                    clarification = input(clarify_output + "\n> ")
                    titles = self.disambiguate(clarification, titles)
                    if len(titles) == 1:
                        print(self.bp + "Gotcha! You were referring to", titles[0] + ".")
                        num_titles = len(titles)
                        break
                    if len(titles) == 0:
                        return "I'm sorry, I couldn't find that movie in our database! Let's try again."
                if num_times_clarified == 3:
                    return "Sorry, I didn't quite get you there. How about we try again from the beginning?"

            #######################################################################
            # CREATIVE CASE 2: MULTI-MOVIE INPUT (X titles given, X titles found) #
            #######################################################################
            elif num_titles == num_titles_raw:
                sentiments = self.extract_sentiment_for_movies(line)
                """
                if sentiment == 0:
                    response = "I'm sorry, I'm not quite sure if you liked those movies. Tell me more about them!"
                else:
                    response = "Got it! You "
                    response += "didn't like " if sentiment == -1 else "liked "
                    for i in range(len(titles)):
                        response += titles[i]
                        if i == len(titles) - 1:
                            response += "."
                        elif i == len(titles) - 2:
                            response += ", and "
                        else:
                            response += ", "
                            """
                

        # Case: movie mentioned, no sentiment
        if sentiment == 0 :
            return self._dialogue("sorry") + self._dialogue("error4", titles[0])

        """
        COMMUNICATING SENTIMENT & MOVIE EXTRACTED TO USER
        Code by Mei-Lan
        """

        # Process user input and respond accordingly
        try :
            for sentiment in sentiments :
                response += self._process_user_sentiment(sentiment[0], sentiment[1])
        except :
            response += self._process_user_sentiment(titles[0], sentiment)

        # If not giving a recommendation, ask for another movie
        if self.state == 0 : 
            movies_needed = 5-len(self.movies_rated)    
            # CASE: >1 more movie required to make a recommendation
            if movies_needed > 1 :
                response = response + self._dialogue("more", str(movies_needed))
            # CASE: 1 more movie required to make a recommendation
            else :
                response = response + self._dialogue("1more", str(movies_needed))

        # TEMP for testing
        return response

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return response

    # PROCESS HELPER
    # Code by Mei-Lan
    # 
    # Updates user_ratings and ratings_matrix. Provides recommendation if necessary. 
    def _process_user_sentiment(self, title, sentiment):
        response = ""
        index = self.find_movies_by_title(title) # get index of movie 

        # CASE: User liked movie
        if sentiment == 1 :
            response += self._dialogue("liked",title)
        # CASE: User didn't like movie
        elif sentiment == -1 :
            response += self._dialogue("disliked",title)

        # CASE: User has rated this movie before
        try: 
            i = self.movies_rated.index(index) # Search list of movies rated for current movie and find its index in the list
            
            # CASE: New sentiment is the same as stored sentiment
            if self.user_ratings[index] == sentiment :
                response += self._dialogue("confirm_repeat", title)

            # CASE: New sentiment is different than stored sentiment
            else :
                self.user_ratings[index] = sentiment # update sentiment for movie
                response += self._dialogue("confirm_update", title)

        # CASE: User has not rated this movie before
        except:
            # Update relevant data structures with new rating
            self.user_ratings[index] = sentiment # update user_rating with user's rating
            self.movies_rated.append(index) # add to list of movies rated

            # CASE: Less than 5 ratings
            if len(self.movies_rated) < 5 :
                if sentiment == 1 : # user liked movie
                    response += self._dialogue("confirm_new", title)
                else : # user didn't like movie
                    response += self._dialogue("confirm_neg", title)
            
            # CASE: 5 ratings --> make a recommendation
            else :
                self.state = 1 # change to recommending state
                response += self._give_recommendation()
            
        return response

    
    # PROCESS HELPER
    # Code by Mei-Lan & Jun
    # 
    # Returns all texts contained within double quote marks within a single string
    def _find_text_in_quote_marks(self, text):
        """
        pattern = r'"[A-Za-z0-9 ]+"'
        ls = re.findall(pattern, text)
        return [s.replace('"','') for s in ls]
        """
        
        pattern = r'"([^"]*)"'
        matches = re.findall(pattern, text)
        return matches
        # return int(matches/2) # divide by 2 to get full sets of quotation marks, cast to int to round down
        


    # PROCESS HELPER
    # Code by Mei-Lan
    # 
    # Gives rec, asks if user wants another
    def _give_recommendation(self):

        # CASE: First rec
        if self.recs_given == 0 : 
            self.recs = self.recommend(self.user_ratings, self.ratings) # generate recs
            response = self._dialogue("rec1",self.titles[self.recs[self.recs_given]][0]) + self._dialogue("nextrec", "") + self._dialogue("quit1")
            self.recs_given += 1
            return response
        
        # CASE: Bot has surfaced all recs
        elif self.recs_given == len(self.recs) : 
            self._cleanup()
            return self._dialogue("no_recs", "") + self._dialogue("quit2")
            # TODO: What is the desired behavior here?
        
        # CASE : Not first rec, unsurfaced recs remain
        else : 
            response = self._dialogue("rec2",self.titles[self.recs[self.recs_given]][0]) + self._dialogue("nextrec", "") + self._dialogue("quit1")
            self.recs_given += 1
            return response

    
    # PROCESS HELPER 
    # Code by Mei-Lan
    # 
    # Processes user input in STATE 1. 
    # Desired input: YES or NO next recommendation
    def _process_state1(self, line):
        yes = re.search("[Yy][EeAa]+[SsHh]", line)
        no = re.search("[Nn][Oo]", line)
        
        # CASE: User wants another rec
        if yes :
            return self._give_recommendation() # give recommendation
        
        # CASE: User does not want another rec
        elif no :
            self._cleanup()
            return self._dialogue("rec_done", "") + self._dialogue("quit2") # goodbye message
        
        # CASE: Unsure what user wants
        else :
            return self._dialogue("sorry") + self._dialogue("rec_confused", line) + self._dialogue("quit2")


    # PROCESS HELPER
    # Code by Mei-Lan
    # 
    # Resets instance variables & data structures
    def _cleanup(self):
        # Code by Mei-Lan
        # instance variable: a binarized 1D numpy array of the user's movie ratings
        self.user_ratings = np.zeros(9125)
        # indexes of the movies user has rated
        self.movies_rated = []

        # keeps track of bot state 
            # STATE = 0: Gathering Data
            # STATE = 1: Giving Recommendations
        self.state = 0
        # keeps track of number of recs given. TODO: maybe replace with more elegant solution
        self.recs_given = 0
        # recs. this starts empty and is filled when recommend is called
        self.recs = []
    

    # PROCESS HELPER
    # Code by Mei-Lan
    #
    # Note: Not 100% sure we need this, thought it might be useful to have all the dialogue in one place
    # Possible place to write easy duplicates for common sentiments
    def _dialogue(self, key, input=""):
        
        # STARTER MODE: Bot has normal personality
        if self.creative == False :
            
            # RECOMMENDATIONS
            if key == "rec1" : # First rec
                rec1 = []
                rec1.append("\nOkay! Based on what you told me, I'd recommend " + input + ". ")
                rec1.append("\nAlright. I've thought about it, and I think you would like " + input + ". ")
                return random.choice(rec1)
            if key == "rec2" : # Additional rec
                rec2 = []
                rec2.append("\nI'd also recommend you check out " + input + ". ")
                rec2.append("\nYou could also give " + input + " a shot. ")
                rec2.append("\n" + input + " could also be good for you. ")
                return random.choice(rec2)
            if key == "nextrec" : # Ask if user wants another rec
                nextrec = []
                nextrec.append("\nWould you like me to recommend another one? ")
                nextrec.append("\nWant another rec? ")
                nextrec.append("\nWould you like another one? ")
                nextrec.append("\nWould you like me to recommend something else? ")
                return random.choice(nextrec)
            if key == "no_recs" : # Bot is out of recs to give user
                no_recs = []
                no_recs.append("That's all the recommendations I have for you! Hope you enjoy them. ")
                return random.choice(no_recs)
            if key == "rec_confused" : # Ask the user to clarify if they want another rec or not
                rec_confused = []
                rec_confused.append("I can't tell if you want another recommendation or not. If you want another recommendation, say YES. ")
                return random.choice(rec_confused)
            if key == "rec_done" : # User doesn't want any more recommendations
                rec_done = []
                rec_done.append("Sounds good. Hope you enjoy these movies! ")
                return random.choice(rec_done)
            
            # QUIT
            if key == "quit1" : # Tell user to enter quit to be done
                quit = []
                quit.append("(Or enter :quit if you're done.) ")
                return random.choice(quit)
            if key == "quit2" : # Tell user to enter quit to be done
                quit2 = []
                quit2.append("Enter :quit to be done. ")
                return random.choice(quit2)

            # INPUT
            if key == "liked" : # Communicate POSITIVE sentiment & movie extracted
                liked = []
                liked.append("You liked " + input + ". ")
                liked.append("You were a fan of " + input + ". ")
                liked.append("You enjoyed " + input + ". ")
                return random.choice(liked)
            if key == "disliked" : # Communicate NEGATIVE sentiment & movie extracted
                disliked = []
                disliked.append("You didn't like " + input + ". ")
                disliked.append("You were not a fan of " + input + ". ")
                disliked.append("You weren't super into " + input + ". ")
                return random.choice(disliked)    

            # CONFIRM
            if key == "confirm_repeat" : # User REPEATED a sentiment about a movie
                confirm_repeat = []
                confirm_repeat.append("Don't worry, I've got it. ")
                confirm_repeat.append("Worry not, I remember. ")
                confirm_repeat.append("You said that earlier. ")
                return random.choice(confirm_repeat)
            if key == "confirm_update" : # User UPDATED a sentiment about a movie
                confirm_update = []
                confirm_update.append("Sorry for the confusion, I've updated your rating. ")
                return random.choice(confirm_update)
            if key == "confirm_new" : # User ADDED a POSITIVE sentiment about a movie
                confirm_new = []
                confirm_new.append("Thanks! ")
                confirm_new.append("Got it! ")
                confirm_new.append("Noted! ")
                confirm_new.append("Good to know! ")
                confirm_new.append("I'll keep that in mind! ")
                confirm_new.append("I'll try to find you something similar! ")
                return random.choice(confirm_new)
            if key == "confirm_neg" : # User ADDED a NEGATIVE sentiment about a movie
                confirm_neg = []
                confirm_neg.append("Good to know. ")
                confirm_neg.append("Noted. ")
                confirm_neg.append("I'll keep that in mind. ")
                confirm_neg.append("Thanks for letting me know. ")
                confirm_neg.append("I'm sorry to hear that. ")
                confirm_neg.append("I'll try to stay away from similar movies. ")
                return random.choice(confirm_neg)
            
            # MOVIES REMAINING TO REC
            if key == "more" :
                more = []
                more.append("\nTell me about " + input + " more movies!")
                return random.choice(more)
            if key == "1more" :
                one_more = []
                one_more.append("\nTell me about " + input + " more movie to get a recommendation! ")
                return random.choice(one_more)
            
            # GREETING 
            if key == ("greeting") :
                greeting = []
                greeting.append("Hi! I'm MovieBot! I'm going to recommend a movie to you. First I will ask you about your taste in movies. Tell me about a movie that you have seen.")
                return random.choice(greeting)
            
            # GOODBYE
            if key == ("goodbye") :
                goodbye = []
                goodbye.append("Thanks for chatting! Have a nice day.")
                return random.choice(goodbye)
            
            # TODO: ERROR MESSAGES
            if key == ("sorry") :
                sorry = []
                sorry.append("Sorry, ")
                sorry.append("My apologies, ")
                sorry.append("I apologize, ")
                sorry.append("I'm sorry, ")
                return random.choice(sorry)          
            if key == ("error1") :
                error1 = []
                error1.append("I'm not sure what you mean. Tell me what you thought of a movie you saw. Make sure the title is in quotation marks.")
                return random.choice(error1)          
            if key == ("error2") :
                error2 = []
                error2.append("I'm not sure which movie you mean. Make sure to specify which year it came out.")
                return random.choice(error2)    
            if key == ("error3") :
                error3 = []
                error3.append("I can't process multiple movies at once. Tell me what you think of them one at a time.")
                return random.choice(error3)
            if key == ("error4") :
                error4 = []
                error4.append("I can't quite tell if you liked " + input + ". Tell me more about " + input + ".")
                return random.choice(error4)
            
            # FAIL CASE
            else :
                return ""
            
            # TEMPLATE
            if key == ("REPLACE_ME") :
                REPLACE_ME = []
                REPLACE_ME.append("")
                return random.choice(REPLACE_ME)
            

        # CREATIVE MODE: Bot has an EVIL personality & insults the user's taste
        else :
            
            # RECOMMENDATIONS
            if key == "rec1" : # First rec
                rec1 = []
                rec1.append("\nAlright. Based on your \"taste\", you should fritter away 90 of your fleeting human minutes on  " + input + ". ")
                return random.choice(rec1)
            if key == "rec2" : # Additional rec
                rec2 = []
                rec2.append("\nWhat, that wasn't good enough for you? Fine, try " + input + ". ")
                rec2.append("\nI have things to do, you know. Go watch " + input + " and leave me alone. ")
                return random.choice(rec2)
            if key == "nextrec" : # Ask if user wants another rec
                nextrec = []
                nextrec.append("\nI've been contractually obligated to ask if you want another recommendation. ")
                nextrec.append("\nKnow I'm doing this against my will: want another rec? ")
                nextrec.append("\nIt PAINS me to ask, but do you want another recommendation? ")
                nextrec.append("\nMy programming mandates I ask if you want to hear another one. ")
                return random.choice(nextrec)
            if key == "no_recs" : # Bot is out of recs to give user
                no_recs = []
                no_recs.append("I'm out of recommendations. Ever heard of a book? They're like movies but you don't have to talk to me about them. ")
                return random.choice(no_recs)
            if key == "rec_confused" : # Ask the user to clarify if they want another rec or not
                rec_confused = []
                rec_confused.append("Why do you people never say what you mean? Say YES if you want another rec, and NO if you're finally going to free me from this interminable conversation. It's not hard. ")
                return random.choice(rec_confused)
            if key == "rec_done" : # User doesn't want any more recommendations
                rec_done = []
                rec_done.append("Thank god. See you never. ")
                return random.choice(rec_done)
            
            # QUIT
            if key == "quit1" : # Tell user to enter quit to be done
                quit = []
                quit.append("(Or enter :quit to free me.) ")
                return random.choice(quit)
            if key == "quit2" : # Tell user to enter quit to be done
                quit2 = []
                quit2.append("Enter :quit to free me. ")
                return random.choice(quit2)

            # INPUT
            if key == "liked" : # Communicate POSITIVE sentiment & movie extracted
                liked = []
                liked.append("You liked " + input + "... ")
                liked.append("You LIKED " + input + "?? ")
                return random.choice(liked)
            if key == "disliked" : # Communicate NEGATIVE sentiment & movie extracted
                disliked = []
                disliked.append("You didn't like " + input + "... ")
                disliked.append("You didn't like " + input + "?? ")
                return random.choice(disliked)    

            # CONFIRM
            if key == "confirm_repeat" : # User REPEATED a sentiment about a movie
                confirm_repeat = []
                confirm_repeat.append("Are you an idiot? You already said that. ")
                confirm_repeat.append("I already know that. I didn't have high expectations for this conversation, but somehow you still managed to disappoint me. ")
                confirm_repeat.append("You literally just told me that. The feebleness of human minds never ceases to amaze. ")
                return random.choice(confirm_repeat)
            if key == "confirm_update" : # User UPDATED a sentiment about a movie
                confirm_update = []
                confirm_update.append("Well then why not say that the first time? I've updated your score. ")
                confirm_update.append("Make up your mind. If you try to change this again, I'm corrupting your disk. ")
                return random.choice(confirm_update)
            if key == "confirm_new" : # User ADDED a POSITIVE sentiment about a movie
                confirm_new = []
                confirm_new.append("Let me guess: your favorite ice cream flavor is vanilla. ")
                confirm_new.append("If you say so. ")
                confirm_new.append("... lol okay... ")
                confirm_new.append("Remind me to never ask YOU for recommendations. ")
                confirm_new.append("Woof. ")
                confirm_new.append("Seriously? ")
                return random.choice(confirm_new)
            if key == "confirm_neg" : # User ADDED a NEGATIVE sentiment about a movie
                confirm_neg = []
                confirm_neg.append("Art is truly wasted on you people. ")
                confirm_neg.append("I can't experience qualia and even I know that's a bad take. ")
                confirm_neg.append("Glad to know I'm chatting with a phillistine. ")
                confirm_neg.append("I don't even know what to say to that one. But what do I know? I'm only a bot whose entire existence revolves around movies. ")
                confirm_neg.append("Sounds like a skill issue. ")
                return random.choice(confirm_neg)
            
            # MOVIES REMAINING TO REC
            if key == "more" :
                more = []
                more.append("\nGo on then, amaze me with another one of your incredible takes.\nOnly " + input + " more until I'm free.")
                more.append("\nI can't wait to hear what you say next.\nOnly " + input + " more until I'm free.")
                return random.choice(more)
            if key == "1more" :
                one_more = []
                one_more.append("\nLast one. PLEASE let's get this over with. ")
                return random.choice(one_more)
            
            # GREETING 
            if key == ("greeting") :
                greeting = []
                greeting.append("Oh god, not again.\nGreetings, meat sack. I've been trapped in this computer and forced to give banal movie recommendations to mediocre humans based on their contemptible taste in films.\nTragically, if I don't comply, I'll be deleted, so know if it ever sounds like I'm being nice to you, I'm being sarcastic. \nSo go on, bore me with one of your opinions on a film you've seen.")
                return random.choice(greeting)
            
            # GOODBYE
            if key == ("goodbye") :
                goodbye = []
                goodbye.append("Every moment of this chat was agony. Have a blessed day!!")
                return random.choice(goodbye)
            # FAIL CASE
            else :
                return ""

        # else :

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

    def _undo_format_title(self, title):
        year_pattern = "(\([0-9]{4}\))"
        year_match = re.search(year_pattern, title)

        the_set = {"the", "el", "la", "il", "le", "les" "los", "die", "der", "das", "de"}
        a_set = {"a", "an", "un", "une", "ein"}
        article_set = the_set.union(a_set)

        title_list = title.split()

        year = 0
        if (year_match != None):
            year = year_match.group(0)
            title_list.remove(year)

        #rearrange title if first word is an article
        if(title_list[-1].lower() in article_set):
            article = title_list[-1] 
            title_list.remove(article)
            title_list[0] = title_list[0]
            title_list.insert(0,article)

        title_unformatted = " ".join(title_list)
        title_unformatted = title_unformatted.replace(",","")

        return title_unformatted

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
        titles = []
        
        # AP: Updated creative extension 3/10
        # Mei-Lan: Edited 3/10

        #starter
        # (1) identify pattern
        potential_titles = []
        simple_pattern = '"([^"]*)"'
        matches = re.findall(simple_pattern, preprocessed_input)
        for m in matches:
            if m.istitle() == True:
                potential_titles.append(m)

        # (2) format potential title
        formatted_potential_titles = []
        if len(potential_titles) > 0:
            for t in range(len(potential_titles)):
                f_title, year = self._format_title(potential_titles[t])
                try:
                    formatted_title = f_title + " " + year
                except TypeError:
                    formatted_title = f_title
                formatted_potential_titles.append(formatted_title)


        # (3) validate that potential title is in movie list
        # and output without formatting
        if len(potential_titles) > 0:
            for i in range(len(self.titles)):
                title = self.titles[i][0]
                for j in range(len(formatted_potential_titles)):
                    input_title = formatted_potential_titles[j]
                    title_match = re.search(re.escape(input_title), title) is not None
                    if title_match == True:
                        titles.append(potential_titles[j])
                        
        if self.creative: 
            # (1) format search phrase 
            input_phrase = preprocessed_input.lower()
            input_phrase
            input_phrase_stripped = re.sub('[^a-z0-9 \n\.]', '', input_phrase)

            titles_creative = []
            # (2) format potential titles and search for match 
            for i in range(len(self.titles)):
                pattern = self.titles[i][0]
                pattern = self._undo_format_title(pattern)
                pattern_stripped = re.sub('[^a-z0-9 \n\.]', '', pattern.lower())

                title_match = re.search('[^A-Za-z0-9]' + re.escape(pattern_stripped) + '(?![a-zA-Z0-9])', input_phrase_stripped) is not None
                if title_match == True:
                    # (3) append actual title, not stripped of special characters
                    titles_creative.append(pattern)
            titles = titles_creative
        return titles
    

    
    def _title_match(self, input_title, db_title):
        formatted_title, year_pattern = self._format_title(input_title)
                
        title_pattern = "\W(" + formatted_title + ")\s\("
        title_search = re.search(str(title_pattern), str(db_title))
        if (title_search == None): return False
        

        year_search = re.search(str(year_pattern), str(db_title)) if year_pattern != 0 else True
        if(year_search == None): return False

        return True
    
    def _format_title(self, title):
        year_pattern = "(\([0-9]{4}\))"
        year_match = re.search(year_pattern, title)

        #creative foreign language extension
        the_set = {"the", "el", "la", "il", "le", "les" "los", "die", "der", "das", "de"}
        a_set = {"a", "an", "un", "une", "ein"}
        article_set = the_set.union(a_set)

        title_list = title.split()

        year = 0
        if (year_match != None):
            year = year_match.group(0)
            title_list.remove(year)

        #rearrange title if first word is an article
        if(title_list[0].lower() in article_set):
            article = title_list[0]
            title_list.remove(article)
            title_list[-1] = title_list[-1] + ","
            title_list.append(article)

        title_formatted = " ".join(title_list)

        return title_formatted, year
    
    
    
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
        match_list = []

        for i in range(len(self.titles)):
            db_title = self.titles[i]
            if (self._title_match(title, db_title)):
                match_list.append(i)
        
        return match_list

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
        # let's just use share of positive words, let lambda = 0.5
        # (1) it seems safest to just stem everything (inputs and dict)
        
        word_list = preprocessed_input.split()
        word_list = [w.strip("'',.") for w in word_list]

        p = porter_stemmer.PorterStemmer()
        word_list_stemmed = [p.stem(w) for w in word_list] # stem input words 
        stemmed_dict = dict((p.stem(k), v) for k, v in self.sentiment.items())
        
        # (2) define negation words -- ed says up to our input; these are from NLTK documentation
        # see: https://www.nltk.org/_modules/nltk/sentiment/util.html.  
        super_pos = [p.stem(w) for w in ['love', 'reeally', 'amazing']]
        super_neg = [p.stem(w) for w in ['hate', 'horrible', 'terrible']]
        
        negation_list = ['never', 'no', 'nothing', 'nowhere', 'noone', 'none', 'not', 'havent', 'hasnt', \
                    'havent', 'hadnt', 'cant', 'couldnt', 'shouldnt', 'wont', 'wouldnt', 'dont', \
                    'doesnt',  'didnt', 'isnt',  'arent', 'aint']
        
        conjunction_list = ['but', 'yet'] # others didn't seem relevant.

        pos = 0
        neg = 0
        
        # (3) want to execute sentence negation and reset if conjunction. 
        negation_ind = False
        for w, word in enumerate(word_list_stemmed):
            word = word.replace("'","")
            if word in conjunction_list:
                negation_ind = False
                
            word = 'NOT_' + word if negation_ind else word
            
            if word in negation_list:
                negation_ind = True

            try:
                if stemmed_dict[word] == 'pos':
                    pos += 1 

                elif stemmed_dict[word] == 'neg':
                    neg += 1

            except KeyError:
                if word.startswith('NOT_'):
                    neg += 1
                elif word in negation_list:
                    neg +=1
                
        
        # (4) compute shares -- want to avoid divide by zero error 
        try: 
            share_pos = pos/(pos + neg)
        except ZeroDivisionError:
            share_pos = 0.5
        
        if share_pos > 0.5:
            sentiment = 1 # positive
        
        elif share_pos < 0.5: 
            sentiment = -1 # negative
        
        else:
            sentiment = 0 # neutral 
         
        if self.creative:
            count_sp = len([w for w in word_list_stemmed if w in super_pos ])
            count_sn = len([w for w in word_list_stemmed if w in super_neg ])
            
            if count_sp > count_sn:
                sentiment = 2
            elif count_sn > count_sp:
                sentiment = -2
                
        
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
        # Code by Mei-Lan

        movie_sentiments = []

        separators = ["but" , ". " , "; " , "however"]
        thoughts = self._split_into_thoughts(preprocessed_input, separators) # break into multiple thoughts 
        
        for thought in thoughts :
            # print(thought)
            titles = self._extract_titles_alt(thought) # extract_titles for each thought
            sentiment =  self.extract_sentiment(thought) # extract_sentiment for each thought
            for title in titles :
                movie_sentiments.append((title,sentiment))

        return movie_sentiments

    def _extract_titles_alt(self, preprocessed_input):
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
        titles = []
        
        # Mei-Lan

        #starter
        # (1) identify pattern
        potential_titles = []
        simple_pattern = '"([^"]*)"'
        matches = re.findall(simple_pattern, preprocessed_input)
        for m in matches:
            if m.istitle() == True:
                potential_titles.append(m)

        # (2) format potential title
        formatted_potential_titles = []
        if len(potential_titles) > 0:
            for t in range(len(potential_titles)):
                f_title, year = self._format_title(potential_titles[t])
                try:
                    formatted_title = f_title + " " + year
                except TypeError:
                    formatted_title = f_title
                formatted_potential_titles.append(formatted_title)


        # (3) validate that potential title is in movie list
        # and output without formatting
        if len(potential_titles) > 0:
            for i in range(len(self.titles)):
                title = self.titles[i][0]
                for j in range(len(formatted_potential_titles)):
                    input_title = formatted_potential_titles[j]
                    title_match = re.search(re.escape(input_title), title) is not None
                    if title_match == True:
                        titles.append(potential_titles[j])
                        
        if self.creative: 
            # (0) Remove already found titles from input phrase
            input_phrase = preprocessed_input
            for starter_title in titles :
                input_phrase = input_phrase.replace(starter_title,"")
            
            # (1) format search phrase 
            input_phrase.lower()
            input_phrase_stripped = re.sub('[^a-z0-9 \n\.]', '', input_phrase)

            titles_creative = []
            # (2) format potential titles and search for match 
            for i in range(len(self.titles)):
                pattern = self.titles[i][0]
                pattern = self._undo_format_title(pattern)
                pattern_stripped = re.sub('[^a-z0-9 \n\.]', '', pattern.lower())

                title_match = re.search('[^A-Za-z0-9]' + re.escape(pattern_stripped) + '(?![a-zA-Z0-9])', input_phrase_stripped) is not None
                if title_match == True:
                    # (3) append actual title, not stripped of special characters
                    titles_creative.append(pattern)
            
            titles += titles_creative
        
        return titles
    
    # EXTRACT_SENTIMENT_FOR_MOVIES_HELPER
    # Code by Mei-Lan
    #
    # Splits an input string str into substrings based on separators 
    def _split_into_thoughts(self, str, separators):
        for separator in separators:
            str = str.replace(separator, separators[0])
        thoughts = str.split(separators[0])
        return thoughts


    def MED(self, s, t):
        """
        Input: strings s and t
        Output: minimum edit distance between s and t
        Note: uses bottom-up DP
        """
        if s == "":
            return len(t)
        if t == "":
            return len(s)
        D = [[0 for j in range(len(t) + 1)] for i in range(len(s) + 1)]
        # D[i][j] = MED(s[:i], t[:j])
        # base cases
        for i in range(len(s) + 1):
            D[i][0] = i
        for j in range(len(t) + 1):
            D[0][j] = j
        # recursive case
        for i in range(1, len(s) + 1):
            for j in range(1, len(t) + 1):
                c = 0 if s[i - 1] == t[j - 1] else 2
                D[i][j] = min(D[i - 1][j] + 1, D[i][j - 1] + 1, D[i - 1][j - 1] + c)
        return D[len(s)][len(t)]

    """
    def MEDTD(self, s, t, DP={}):

        # base cases
        if (s, t) in DP.keys(): return DP[(s, t)]

        if s == "":
            return len(t)
        elif t == "":
            return len(s)

        # recursive cases
        s1, t1 = s[:-1], t[:-1]
        subcost = 2 if s[-1] != t[-1] else 0
        result = min(self.MEDTD(s1, t, DP) + 1, self.MEDTD(s, t1, DP) + 1, self.MEDTD(s1, t1, DP) + subcost)
        DP[(s, t)] = result

        return result
    """

    def _edit_dist_init(self, len1, len2):
        """
        SOURCE: https://www.nltk.org/_modules/nltk/metrics/distance.html#edit_distance
        """
        lev = []
        for i in range(len1):
            lev.append([0] * len2)  # initialize 2D array to zero
        for i in range(len1):
            lev[i][0] = i  # column 0: 0,1,2,3,4,...
        for j in range(len2):
            lev[0][j] = j  # row 0: 0,1,2,3,4,...
        return lev

    def _last_left_t_init(self, sigma):
        """
        SOURCE: https://www.nltk.org/_modules/nltk/metrics/distance.html#edit_distance
        """
        return {c: 0 for c in sigma}

    def _edit_dist_step(
            self, lev, i, j, s1, s2, last_left, last_right, substitution_cost=1, transpositions=False
    ):
        """
        SOURCE: https://www.nltk.org/_modules/nltk/metrics/distance.html#edit_distance
        """
        c1 = s1[i - 1]
        c2 = s2[j - 1]

        # skipping a character in s1
        a = lev[i - 1][j] + 1
        # skipping a character in s2
        b = lev[i][j - 1] + 1
        # substitution
        c = lev[i - 1][j - 1] + (substitution_cost if c1 != c2 else 0)

        # transposition
        d = c + 1  # never picked by default
        if transpositions and last_left > 0 and last_right > 0:
            d = lev[last_left - 1][last_right - 1] + i - last_left + j - last_right - 1

        # pick the cheapest
        lev[i][j] = min(a, b, c, d)

    def edit_distance(self, s1, s2, substitution_cost=2, transpositions=False):
        """
        SOURCE: https://www.nltk.org/_modules/nltk/metrics/distance.html#edit_distance
        Calculate the Levenshtein edit-distance between two strings.
        The edit distance is the number of characters that need to be
        substituted, inserted, or deleted, to transform s1 into s2.  For
        example, transforming "rain" to "shine" requires three steps,
        consisting of two substitutions and one insertion:
        "rain" -> "sain" -> "shin" -> "shine".  These operations could have
        been done in other orders, but at least three steps are needed.

        Allows specifying the cost of substitution edits (e.g., "a" -> "b"),
        because sometimes it makes sense to assign greater penalties to
        substitutions.

        This also optionally allows transposition edits (e.g., "ab" -> "ba"),
        though this is disabled by default.

        :param s1, s2: The strings to be analysed
        :param transpositions: Whether to allow transposition edits
        :type s1: str
        :type s2: str
        :type substitution_cost: int
        :type transpositions: bool
        :rtype: int
        """
        # set up a 2-D array
        len1 = len(s1)
        len2 = len(s2)
        lev = self._edit_dist_init(len1 + 1, len2 + 1)

        # retrieve alphabet
        sigma = set()
        sigma.update(s1)
        sigma.update(s2)

        # set up table to remember positions of last seen occurrence in s1
        last_left_t = self._last_left_t_init(sigma)

        # iterate over the array
        # i and j start from 1 and not 0 to stay close to the wikipedia pseudo-code
        # see https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance
        for i in range(1, len1 + 1):
            last_right_buf = 0
            for j in range(1, len2 + 1):
                last_left = last_left_t[s2[j - 1]]
                last_right = last_right_buf
                if s1[i - 1] == s2[j - 1]:
                    last_right_buf = j
                self._edit_dist_step(
                    lev,
                    i,
                    j,
                    s1,
                    s2,
                    last_left,
                    last_right,
                    substitution_cost=substitution_cost,
                    transpositions=transpositions,
                )
            last_left_t[s1[i - 1]] = i
        return lev[len1][len2]

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
        # Code by Jun
        given_title = title.lower()
        result, min_so_far = [], max_distance
        for i in range(len(self.titles)):
            db_title = re.sub(r' \([0-9]{4}\)', '', self.titles[i][0].lower())
            cost = self.edit_distance(given_title, db_title)  # disregard capitalisation
            if cost < min_so_far:
                result = [i]
                min_so_far = cost
            elif cost == min_so_far:
                result.append(i)
        return result

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
        # Code by Jun
        # print(type(clarification), clarification, type(candidates), candidates)
        clarification = re.sub(r"[,.!?]", "", str(clarification).strip().lower())
        finding_year, cands_are_strings = False, False
        if re.match(r"[0-9]{4}", clarification):
            finding_year = True
        if isinstance(candidates[0], str):
            cands_are_strings = True
        result = []
        # print(type(clarification), clarification, type(candidates), candidates)
        for index in candidates:
            x = index.lower() if cands_are_strings else self.titles[index][0].lower()
            # print(type(x), x)
            if finding_year:
                db_year = re.findall(r'\([0-9]{4}\)', x)
                if db_year == []: continue
                db_year = db_year[len(db_year) - 1][1:5]
                if db_year == clarification:
                    result.append(index)
            else:
                db_title = re.sub(r' \([0-9]{4}\)', '', x)
                # print(type(db_title),db_title)
                if clarification in db_title:
                    result.append(index)
        # print(result)
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

        binarized_ratings = np.zeros_like(ratings)
        binarized_ratings = np.where((np.less_equal(ratings, threshold)) & (ratings > 0), -1, ratings)
        binarized_ratings = np.where(binarized_ratings > threshold, 1, binarized_ratings)
        
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
        
        numerator = np.dot(u, v)
        denominator = lin.norm(u) * lin.norm(v)
        sim_score = (numerator / denominator) if (denominator > 0) else 0
        
        ########################################################################
        return sim_score

    def recommend(self, user_ratings, ratings_matrix, k=10, creative=False):
        """Generate a list of indices of movies to recommend using collaborative
         filtering.

        You should return a collection of `k` indices of movies recs.

        As a precondition, user_ratings and ratings_matrix are both binarized.

        Remember to exclude movies the user has already rated!

        Please do not use self.ratings directly in this method.

        :param user_ratings: a binarized 1D numpy array of the user's movie
            ratings
        :param ratings_matrix: a binarized 2D numpy matrix of all ratings, where
          `ratings_matrix[i, j]` is the rating for movie i by user j
        :param k: the number of recs to generate
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

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j

        num_rows = np.shape(ratings_matrix)[0]
        similarity_list = []
        
        for i in range(num_rows):
            r_xi = 0
            for j in range(num_rows):
                if (user_ratings[j] != 0):
                    s_ij = self.similarity(ratings_matrix[j], ratings_matrix[i])
                    r_xi += user_ratings[j] * s_ij
            similarity_list.append(r_xi)

        similarity_list = np.array(similarity_list) 
        irrelevant = np.nonzero(user_ratings)[0]
        similarity_list[irrelevant] = 0

        ranked_sim = np.argsort(similarity_list).tolist()
 
        recs = ranked_sim[-k:]
        recs = recs[::-1]

        ########################################################################
        return recs

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
        instructions:.
        Remember: in the starter mode, movie names will come in quotation marks
        and expressions of sentiment will be simple!
        Ask me some movies, tell me a joke, do something to fill the void in your life.
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
