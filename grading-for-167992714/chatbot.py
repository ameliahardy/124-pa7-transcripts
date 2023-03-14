# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import re
import numpy as np
import string
from porter_stemmer import PorterStemmer
# noinspection PyMethodMayBeStatic

NEGATIVES = {'dont', 'didnt', 'hasnt', 'havent', 'hadnt', 'wont', 'wouldnt', 'shouldnt', 'cant', 'wasnt', 'werent', 'never', 'not', 'cannot', 'neither', 'barely', 'hardly', 'scarcely', 'seldom', 'rarely', 'least'}
STRONG = {'hate', 'love', 'amaze', 'terrible', 'disgust', 'filthy', 'tear', "very", "really", "best", "worst", "favorite", 'wonderful'}
HAPPY = ['happy', 'joy', 'delight', 'pleasure', 'excitement', "enjoy"]
SAD = ['sad', 'upset', 'depressed', 'gloomy', 'miserable', "cry"]
ANGRY = ['useless','angry', 'hate', 'awful', 'irritated', 'frustrated', 'outraged', 'resentful', "mad", "annoyed", "stupid", "dumb"]
FEAR = ['fear', 'anxiety', 'worry', 'nervous', 'scared', "frightened", "shiver", "goosebumps"]
SURPRISE = ['surprised', 'astonished', 'shocked', 'amazed', 'startled']
DISGUST = ['disgusted', 'repelled', 'revolted', 'nauseated', 'abhorred', "vomit"]
### Source: Corpus of Contemporary American English (COCA) #### 
COMMON_WORD =  ["loved", "hated", "one", "two", "three", "four", "five", "six", "food", "thirst", 
                "seven", "eight", "nine", "ten", "look", "hear", "dead", "died", "spoon", "fork",
                'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'I', 
                'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
                'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
                'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
                'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me', 
                'Contact', 'Drive', 'Crash', 'Gravity', 'Heat', 'Frozen', 
                'Speed', 'Jaws', 'Twins', 'Ghost', 'Taken', 'Speed', 'Creed', 
                'Big', 'Rush', 'Doubt', 'Juno', 'Up', 'Focus', 'happy', 'perfect', 'worst', 
                'Spotlight', 'Creed', 'Cars', 'Elf', 'Wanted', 'Room', 'Warrior', 'Ray', "super"]
COMMON_TWO_WORD_PHRASE = ['of the',"please give", 'in the', 'to the', 'on the', 'for the', 'with the', 
                        'at the', 'from the', 'by the', 'about the', 'is a', 'it is', 
                        'in a', 'that the', 'as a', 'to be', 'of a', 'and the', 
                        'at least', 'to a', 'out of', 'in this', 'with a', 'there is', 
                        'as well', 'one of', 'up to', 'such as', 'in order', 'more than', "loved ones", "super happy", 
                        "super joyful", "super mad", "super sad", "super dead", "super scared", "super surprised", 
                        "super astonished", "super shocked", "super awful", "goosebumps", "super annoyed", "super frustrating", 
                        "super nice"]
COMMON_THREE_WORD_PHRASE = ['out of the', 'in order to', 'at the time', 'as well as', 
                            'on the other', 'in front of', 'in the world', 'it is not', 
                            'as a result', 'in terms of', 'in this case', 'in the same', 
                            'there is no', 'in the first', 'it is important', 'at the same', 
                            'the United States', 'it is possible', 'it is also', 'it is necessary', 
                            'it is difficult', 'in the past', 'in the end', 'a lot of', 
                            'in the United', 'it is still', 'it is important to', 'in the next', 
                            'in the middle', 'in the case']


class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'Gordon Ramsey Bot'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        #### ADDED BY ELY BEGIN ####

        # Porter Stemmer
        self.p = PorterStemmer()

        temp = {}
        for k, v in self.sentiment.items():
            new_key = self.p.stem(k)
            temp[k] = new_key

        for old, new in temp.items():
            self.sentiment[new] = self.sentiment.pop(old)

        for word in STRONG.copy():
            STRONG.add(self.p.stem(word))
            if word != self.p.stem(word):
                STRONG.remove(word)

        for i in range(len(HAPPY)):
            HAPPY[i] = self.p.stem(HAPPY[i])
        for i in range(len(SAD)):
            SAD[i] = self.p.stem(SAD[i])
        for i in range(len(ANGRY)):
            ANGRY[i] = self.p.stem(ANGRY[i])
        for i in range(len(FEAR)):
            FEAR[i] = self.p.stem(FEAR[i])
        for i in range(len(SURPRISE)):
            SURPRISE[i] = self.p.stem(SURPRISE[i])
        for i in range(len(DISGUST)):
            DISGUST[i] = self.p.stem(DISGUST[i])

        # user ratings 
        self.user_ratings = np.zeros(len(ratings), 'int')

        # number of movies added by user
        self.user_provided_data_count = 0
        # bool as to whether the chatbot should recommend or not 
        self.bool_recommend = False
        # list of movies to recommend, in order
        self.recommend_list = []
        # index to recommend the next movie 
        self.index_to_recommend = 0
        # bool to turn on when we previously asked user to clarify 
        self.bool_clarify = False 
        self.misspelled_corrected_title = ""
        self.prev_line = ""
        # bool to clarify years 
        self.bool_year_clarify = False
        self.clarify_list = []
        self.prev_line_years = ""
        #### END BY ELY ####
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

        greeting_message = "Hallo, mate! I'm Gordon Ramsey, your trusty movie chef. Give me some ingredients (opinions on movies), and once I have enough ingredients for the perfect dish, I'll whip you up nicely seasoned suggestions."

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

        goodbye_message = "Enjoy your ridiculously good movie dishes!"

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
        response = '' 
        if self.creative:
            ### TO DO: Add on top of basic implementation ###

            # Case 1: recommending 
            if self.bool_recommend:  # in last prompt, already asked user if they want recommendation. YES or NO 
                # response 
                user_response = line.lower().lstrip().rstrip()
                user_response = re.sub(r'\W+', '', user_response)
                # case 1: user wants recommendation
                if user_response == "yes":
                    # if we ran out of movies to recommend / never recommended yet, generate top 20 movies to rec
                    if self.recommend_list == [] or self.index_to_recommend >= len(self.recommend_list):
                        # load 10 new recommendations
                        self.recommend_list = self.recommend(self.user_ratings, self.ratings, 20)
                        # print(self.recommend_list)
                        self.index_to_recommend = 0
                    # recommend movie 
                    movie_choice = self.titles[self.recommend_list[self.index_to_recommend]][0]  # index 1 is genre
                    # update the index
                    self.index_to_recommend += 1
                    # return the response, using random generation 
                    response_options_front = ["Given your ingredients, ", "Cooking up your movie preferences, ", 
                                              "After consulting my recipe book, ", 
                                              "Given your bloody suggestions, ", "I've got a bloody juicy recommendation for ya; "]
                    respnse_options_back = ["Would ya like me to fire up a new recommendation?", "Shall I cook ya something bloody delicious again? ", 
                                            "Would ya like another fresh, non-raw recommendation? ",
                                            "Could I interest you in another perfectly cooked recommendation? ",
                                            "Do ya like where that came from? I've got a gold mine of other recommendations even your mum would love! "]
                    response = np.random.choice(response_options_front) + "Here are the absolutely delicious recommendations; \"{}\"! ".format(movie_choice) + np.random.choice(respnse_options_back)
                    return response  
                # case 2: user does not want recommendation 
                elif user_response == "no":
                    # turn off the boolean to indicate that we are not recommending 
                    self.bool_recommend = False
                    # reset the recommendation list (since user likely to type more data points)
                    self.recommend_list = []
                    self.index_to_recommend = 0
                    # ask the user for an input of data 
                    response = "Bravo! If you have, tell me more about a movie you have opinions on so I can continue cooking!"
                    return response  
                # case 3: user did not enter yes or no
                else:
                    # re-prompt the user
                    response = "Sorry mate, what you said was RAW!... Please answer \"yes\" or \"no\"."
                    return response  
            
            #### Case 2: not recommending ####

            title_list = []
            # MODE: If previous input has misspelling, below is true 
            if self.bool_clarify:
                user_response = line.lower().lstrip().rstrip()
                user_response = re.sub(r'\W+', '', user_response)
                # case 1: misspelled title we proposed was right 
                if user_response == "yes":
                    # print(self.misspelled_corrected_title)
                    title_list = [self.misspelled_corrected_title]
                    # turn off this mode, since we resolved the misspelling ambiguity 
                    self.bool_clarify = False  
                    self.misspelled_corrected_title = ""
                    response = "Got it! "
                # Case 2: out proposed title was not what they were looking for 
                elif user_response == "no":
                    self.bool_clarify = False  
                    self.prev_line = ""
                    self.misspelled_corrected_title = ""
                    response = "Mate, I can't lie to you; what you told me was quite undercooked. Perhaps, if you give me more ingredients (movie opinions), I'll be able to craft something delicious for ya! "
                    return response 
                else:
                    response = "Sorry mate, what you said was RAW!... Please answer \"yes\" or \"no\". "
                    return response 
            else:
                title_list = self.extract_titles(line)

            if self.bool_year_clarify:
                # user response is likely year 
                user_response = line.lower().lstrip().rstrip()
                clarified_list = self.disambiguate(user_response, self.clarify_list)
                # correct output
                if len(clarified_list) == 1:
                    m_index = clarified_list[0]
                    title_list = [self.titles[m_index][0]]
                    # turn off 
                    self.bool_year_clarify = False
                    self.clarify_list = []
                    response = "Got it! "
                # re-ask
                elif len(clarified_list) > 1:
                    self.clarify_list = clarified_list
                    res_list = [self.titles[clarified_list[i]][0] for i in range(len(clarified_list))]
                    response = "Hmm..., there are still multiple titles with similar names. Can you clarify?\n" + str(res_list) 
                    return response
                else:
                    self.bool_year_clarify = False
                    self.prev_line_years = ""
                    self.clarify_list = []
                    response = "I'm sorry... I didn't understand :( Re-type your movie title!"
                    return response 

            # case 1: no titles 
            if len(title_list) == 0:
                # Identify & Respond to emotion, if any
                emotion = self.extract_emotion(line)                
                if emotion: 
                    if emotion == 'happiness':
                        response = "Sensational! Cheers to ya!"
                    elif emotion == 'sadness':
                        response = "Aye, you seem gutted mate... I'm sorry about that, maybe I can cook ya some of my famous Beef Wellington? "
                    elif emotion == 'anger':
                        response = "Aye, it wasn't my intention to get you all riled up. Although I can be daft, I am just a chatbot... :( "
                    elif emotion == 'fear':
                        response = "Blimey, I get scared too! Especially when it's RAW!!!!"
                    elif emotion == 'surprise':
                        response = 'Good grief, it caught me off guard too!'
                    elif emotion == 'disgust':
                        response = "Oy, that's foul!!! But, maybe a good dish (movie) can cheer you up!"
                    return response 
                else:
                    response = "Sorry mate, even a world-class chef can be daft... Tell me about a movie that you have seen and I can get cooking in the kitchen! "

            elif len(title_list) >= 1:
                # more than one title mentioned 

                # all titles 
                matched_title_indexes = []
                # iterate through all title list, only proceed if all inputs exists
                for title in title_list:
                    # find if the movie exists in database 
                    matched_title_index = self.find_movies_by_title(title)
                    # case 1: does not exists    #### WORK ON IT LATER ####
                    if len(matched_title_index) == 0:
                        
                        print("Hmmmm... I don't quite recognize the ingredient (movie) you mentioned. Give me couple seconds to search for the ingredient (movie) with a similar name in the kitchen... (Up to 30 seconds)")
                        # case 1: misspelled
                        potential_misspelled_title = self.find_movies_closest_to_title(title)

                        if len(potential_misspelled_title) > 0:
                            self.misspelled_corrected_title = self.titles[potential_misspelled_title[0]][0]  # potentially misspelled title
                            self.prev_line = line 
                            self.bool_clarify = True   # turn on the clarification mode 
                            response = "Do you mean the movie, \"{}\"?".format(self.misspelled_corrected_title)
                            return response 
                        # too much edit distance
                        else:
                            response = "Sorry mate, even a world-class chef can be daft... Tell me about a movie that you have seen and I can get cooking in the kitchen! "
                            return response 
                        
                    elif len(matched_title_index) > 1:
                        response = "Aye, I found more than one movie called \"{}\".".format(title) + "\nChoices: " + str([self.titles[matched_title_index[i]][0] for i in range(len(matched_title_index))]) + "\nWhich one is it? TYPE THE YEAR (e.g.: 1992)!!! If it's not on the list, re-type it!"
                        self.clarify_list = matched_title_index
                        self.prev_line_years = line 
                        self.bool_year_clarify = True
                        return response
                    else:
                        matched_title_indexes.append(matched_title_index[0])
                # Number of user provided data points (equiv. to number of matched movies identified)
                self.user_provided_data_count += len(matched_title_indexes)
                # if greater than 5 data points, turn on recommendation mode
                if self.user_provided_data_count >= 5:
                    self.bool_recommend = True           

                liked_movies = []
                disliked_movies = []
                liked_string = ''
                unliked_string = ''

                ### EDGE CASE (SINCE "line" is corrupted) ###
                #### DO NOT DELETE THE FOLLOWING LINE OF CODE ####
                if self.prev_line != "":
                    # assumption: only one movie is passed in here 
                    sentiment = self.extract_sentiment(self.prev_line)
                    if sentiment > 0:
                        liked_string = self.titles[matched_title_indexes[0]][0]
                        self.user_ratings[matched_title_indexes[0]] = sentiment
                    elif sentiment < 0:
                        unliked_string = self.titles[matched_title_indexes[0]][0]
                        self.user_ratings[matched_title_indexes[0]] = sentiment 
                    self.prev_line = ""
                elif self.prev_line_years != "":
                    sentiment = self.extract_sentiment(self.prev_line_years)
                    if sentiment > 0:
                        liked_string = self.titles[matched_title_indexes[0]][0]
                        self.user_ratings[matched_title_indexes[0]] = sentiment
                    elif sentiment < 0:
                        unliked_string = self.titles[matched_title_indexes[0]][0]
                        self.user_ratings[matched_title_indexes[0]] = sentiment 
                    self.prev_line_years = ""                    
                else:

                    ### ASSMPTION: Assume that all "movies" in the line input is correct and exists in database                    
                    extracted_sentiment_for_mov = self.extract_sentiment_for_movies(line)

                    cur_m_index = 0  # variable to keep track on which entry we are pointing in "matched_title_indexes"
                    for movie_title_str, sentiment in extracted_sentiment_for_mov:
                        if sentiment > 0:
                            liked_movies.append(movie_title_str)
                            # input the data to user_ratings 
                            self.user_ratings[matched_title_indexes[cur_m_index]] = sentiment
                        elif sentiment < 0:
                            disliked_movies.append(movie_title_str)
                            self.user_ratings[matched_title_indexes[cur_m_index]] = sentiment 

                        cur_m_index += 1
                        if cur_m_index == len(matched_title_indexes):  break 

                if len(liked_movies) >= 1:
                    liked_string = "\"" + liked_movies[0] + "\""
                # from 2nd to n-1th liked movies
                for i in range(1, len(liked_movies) - 1):
                    liked_string += "," + " \"" + liked_movies[i] + "\"" 
                if len(liked_movies) > 1:
                    liked_string += " and " + "\"" + liked_movies[-1] + "\"" 

                if len(disliked_movies) >= 1:
                    unliked_string = "\"" + disliked_movies[0] + "\""
                # from 2nd to n-1th disliked movies
                for i in range(1, len(disliked_movies) - 1):
                    unliked_string += "," + " \"" + disliked_movies[i] + "\"" 
                if len(disliked_movies) > 1:
                    unliked_string += " and " + "\"" + disliked_movies[-1] + "\""

                padding_str_list = ["Aye, ", "Crikey, ", "Interesting, ", "Mm, ", "Gotcha, so ", "Noted, so "]
                if liked_string != '' and unliked_string != '':
                    # choose padding randomly 
                    padding = np.random.choice(padding_str_list)
                    response += padding + 'you like ' + liked_string + "! But you don't like " + unliked_string + ". "
                elif liked_string != '':
                    padding = np.random.choice(padding_str_list)
                    response += padding + 'you like ' + liked_string + "! "      
                elif unliked_string != '':
                    padding = np.random.choice(padding_str_list)
                    response += padding + 'you do not like ' + unliked_string + ". "      
                
                # If more than 5 data points, provide a recommendation  
                if self.bool_recommend:
                    response_options = ["Given your ingredients,, I've got the perfect dish for ya! Would you like to see it?",
                                        "I've got bloody delicious recommendations for you... Wouldn't ya wanna hear it?", 
                                        "Could I interest you in my cooking? I can give you an exquisite recommendation!", 
                                        "Oy mate, I've got a 5-star dish (movie) for you! Do ya want it?"]
                    response = response + np.random.choice(response_options)
                else:
                    response_options = ["Tell me more about a movie you have opinions on so I can get cooking!", "Talk to me about one more movie; we are so close to perfection!", 
                                        "Give me more bloody juicy takes on any movies!", "I'm the chef, you're the customer; tell me more about your movie takes so I can whip up something just right!", 
                                        "You absolutely like movies, right! Tell me more about another movie!", 
                                        "Are there any movies that make you absolutely happy? Tell me one!",
                                        "Do you have a movie hot take? Tell me one so I can continue seasoning this dish!",
                                        "Tell me more about a movie so I can season this dish!!",
                                        "It would be absolutely phenomenal if you could talk to me about one more movie... :)"]
                    response = response + np.random.choice(response_options)
    
        else:
            #### DONE WITH FUNCTIONALITY IMPLEMENTATION. NEED TO MAKE IT MORE NATURAL SOUNDING ####

            # Case 1: recommending 
            if self.bool_recommend:  # in last prompt, already asked user if they want recommendation. YES or NO 
                # response 
                user_response = line.lower().lstrip().rstrip()
                user_response = re.sub(r'\W+', '', user_response)
                # case 1: user wants recommendation
                if user_response == "yes":
                    # if we ran out of movies to recommend / never recommended yet, generate top 10 movies to rec
                    if self.recommend_list == [] or self.index_to_recommend >= len(self.recommend_list):
                        # load 10 new recommendations
                        self.recommend_list = self.recommend(self.user_ratings, self.ratings, 20)
                        # print(self.recommend_list)
                        self.index_to_recommend = 0
                    # recommend movie 
                    movie_choice = self.titles[self.recommend_list[self.index_to_recommend]][0]  # index 1 is genre
                    # update the index
                    self.index_to_recommend += 1
                    # return the response 
                    response_options_front = ["Given your ingredients, ", "Cooking up your movie preferences, ", 
                                              "After consulting my recipe book, ", 
                                              "Given your bloody suggestions, ", "I've got a bloody juicy recommendation for ya; "]
                    respnse_options_back = ["Would ya like me to fire up a new recommendation?", "Shall I cook ya something bloody delicious again?", 
                                            "Would ya like another fresh, non-raw recommendation?",
                                            "Could I interest you in another perfectly cooked recommendation?",
                                            "Do ya like where that came from? I've got a gold mine of other recommendations even your mum would love!"]
                    response = np.random.choice(response_options_front) + "Here are the absolutely delicious recommendations; \"{}\"! ".format(movie_choice) + np.random.choice(respnse_options_back)
                    # return response  
                    # response = "Given the movies you like, I recommend the movie, \"{}\"! Would you like another recommendation?".format(movie_choice)
                    return response  
                # case 2: user does not want recommendation 
                elif user_response == "no":
                    # turn off the boolean to indicate that we are not recommending 
                    self.bool_recommend = False
                    # reset the recommendation list (since user likely to type more data points)
                    self.recommend_list = []
                    self.index_to_recommend = 0
                    # ask the user for an input of data 
                    response = "Gotcha! If you have, tell me more about a movie you have opinions on!"
                    return response  
                # case 3: user did not enter yes or no
                else:
                    # re-prompt the user
                    response = "Sorry mate, what you said was RAW!... Please answer \"yes\" or \"no\". "
                    return response  

            # Case 2: not recommending 
            title_list = self.extract_titles(line)
            # case 1: no titles 
            if len(title_list) == 0:
                response = "Sorry mate, even a world-class chef can be daft... Tell me about a movie that you have seen and I can get cooking in the kitchen! "
            # case 2: more than one title mentioned
            elif len(title_list) > 1:
                response = "Sorry mate, I can't cook multiple ingredients (movies) at a time. A world class chef must deal with them one ingredient at a time. Please tell me about one movie at a time! "
            # case 3: one movie title mentioned
            else:
                title = title_list[0]
                # find if there is a matching movie in our database
                matched_title_indexes = self.find_movies_by_title(title)
                # case 1: no matching titles found
                if len(matched_title_indexes) == 0:
                    response = "I'm sorry mate, this is quite the dodgy ingredient (movie), \"{}\"... but if there is another ingredient (movie) you liked or disliked, let me know!".format(title) 
                # case 2: more than one title matched 
                elif len(matched_title_indexes) > 1:
                    response = "I found more than one ingredient (movie) called \"{}\". Can you clarify before I start the stove?".format(title)
                # case 3: exactly one title matched
                else:

                    # extract sentiment 
                    sentiment = self.extract_sentiment(line)
                    # only update the user_provided_data_count if sentiment is NOT NEUTRAL 
                    if sentiment != 0:
                        # number of user provided data points 
                        self.user_provided_data_count += 1
                        # if greater than 5 data points, turn on recommendation mode
                        if self.user_provided_data_count >= 5:
                            self.bool_recommend = True 

                    # store in user ratings
                    self.user_ratings[matched_title_indexes[0]] = sentiment

                    padding_str_back = ["Tell me more about a movie you have opinions on so I can get cooking!", "Talk to me about one more movie; we are so close to perfection!", 
                                        "Give me more bloody juicy takes on any movies!", "I'm the chef, you're the customer; tell me more about your movie takes so I can whip up something just right!", 
                                        "You absolutely like movies, right! Tell me more about another movie!", 
                                        "Are there any movies that make you absolutely happy? Tell me one!",
                                        "Do you have a movie hot take? Tell me one so I can continue seasoning this dish!",
                                        "Tell me more about a movie so I can season this dish!!",
                                        "It would be absolutely phenomenal if you could talk to me about one more movie... :)"]

                    # case 1: user enjoyed it
                    if sentiment > 0:
                        padding_str_front = ["I'm glad you thought this is gourmet: ", "Good to hear that you liked ", 
                                             "Cheers, so you liked ", "Delicious, so you enjoyed ", 
                                             "It's absolutely nice to hear that you liked ", "Aye, so you liked "]
                        if self.bool_recommend:
                            response = np.random.choice(padding_str_front) + "\"{}\"! ".format(title) + "Given what you had told me, I have a mouth-watering recommendation for you! Would you like to hear it?"
                            # response = "I'm glad you enjoyed \"{}\"! Given what you had told me, I have a recommendation for you! Would you like to hear it?".format(title)
                        else:
                            response = np.random.choice(padding_str_front) + "\"{}\"! ".format(title) + np.random.choice(padding_str_back)
                    # case 2: user is neutral & could not extract sentiment 
                    elif sentiment == 0:
                        padding_str_front = ["Sorry mate, I'm not sure if you liked ",  
                                             "Aye, I can't tell if you enjoyed ", 
                                             "Even a world class chef like me can't tell if you liked the movie ", 
                                             "Blimey, I can't tell if you really liked the movie "]
                        response = np.random.choice(padding_str_front) + "\"{}\"! ".format(title) + "Tell me more about it!"
                    # case 3: user did not enjoy 
                    else:
                        padding_str_front = ["Aye, so you did not like ", "Interesting, so you thought this was raw: ", 
                                             "Crikey, ya didn't like ", "Oy, so you disliked the movie ", 
                                             "Alright, so you weren't the biggest fan of ", "Okay, so this movie was full of bollocks: "]
                        if self.bool_recommend:
                            response = np.random.choice(padding_str_front) + "\"{}\"! ".format(title) + "Given what you had told me, I cooked the perfect recommendation for you! Would you like to hear it, mate?"
                        else:
                            response = np.random.choice(padding_str_front) + "\"{}\"! ".format(title) + np.random.choice(padding_str_back)

                        
                            

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
        # May change in creative mode, but passes basic mode 
        pattern = '(\"[^\"]+\"|\'[^\']+\')'  
        pot_titles = re.findall(pattern, preprocessed_input)
        # remove the quotation marks 
        res = [title[1:-1] for title in pot_titles]

        if self.creative:
            # if no title inside quotation marks is found 
            if len(res) == 0:
                # break title into tokens 
                tokens = preprocessed_input.split(" ")
                # for all possible word combination and size, find if there is matching title
                for i in range(0, len(tokens)):  # lower bound
                    for j in range(i+1, len(tokens)+1):  # upper bound
                        potential_title_1 = " ".join(tokens[i:j])
                        # IF TITLE IS JUST A COMMON PHRASE, SKIP IT 
                        if len(potential_title_1.split(" ")) == 1 and potential_title_1 in COMMON_WORD:
                            continue 
                        elif len(potential_title_1.split(" ")) == 2 and potential_title_1 in COMMON_TWO_WORD_PHRASE:
                            continue 
                        elif len(potential_title_1.split(" ")) == 3 and potential_title_1 in COMMON_THREE_WORD_PHRASE:
                            continue 
                        
                        ### case 1: no punctuation elimination 
                        matching_movies_list_1 = self.find_movies_by_title(potential_title_1)  
                        if len(matching_movies_list_1) > 0:  
                            res.append(potential_title_1)
                        else:

                            ### case 2: punctuation elimination at the end
                            while len(potential_title_1) > 0 and potential_title_1[-1] in string.punctuation:
                                potential_title_1 = potential_title_1[:-1]

                            matching_movies_list_2 = self.find_movies_by_title(potential_title_1)  
                            if len(matching_movies_list_2) > 0:  
                                res.append(potential_title_1)

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
        movie_ids = []            
        title = title.lower()
        edited_title = title  # for now
        has_year = False
        
        title_tokens = title.split(" ")
        # check if tokens have years 
        if re.match("\([0-9][0-9][0-9][0-9]\)", title_tokens[-1]):
            has_year = True

        if len(title_tokens) > 1 and (title_tokens[0] == "a" or 
                                      title_tokens[0] == "the" or 
                                      title_tokens[0] == "an"):
            if has_year:
                has_year = True 
                edited_title = " ".join(title_tokens[1:-1])  # merge, exclude the first and last token 
                edited_title = edited_title + ", " + title_tokens[0] + " " + title_tokens[-1]
            else:
                edited_title = " ".join(title_tokens[1:]) + ", " + title_tokens[0]
        
        # find if the title matches by iterating all possible match
        # print(edited_title)
        for index in range(len(self.titles)):
            pot_match = self.titles[index][0].lower()
            # print(pot_match)
            if has_year:
                if edited_title == pot_match:
                    movie_ids.append(index)
            else:
                if edited_title == pot_match[:-7]:
                    movie_ids.append(index)   

            if self.creative:
                alternate_pattern = ".+\(a.k.a. .+"
                foreign_pattern = ".+\(.+\) ([0-9]{4})"

                if re.match(alternate_pattern, pot_match) or re.match(foreign_pattern, pot_match):
                    alternate_title = re.findall(".+\(a.k.a. (.+)\).+", pot_match)
                    foreign_title = re.findall(".+[\(a.k.a.+\)]? \((.+)\) \([0-9]{4}\)", pot_match)

                    if len(alternate_title) != 0:
                        alternate_title = alternate_title[0]
                    if len(foreign_title) != 0:
                        foreign_title = foreign_title[0]

                    # print(alternate_title, pot_match)
                    # print(foreign_title, pot_match)

                    if edited_title == alternate_title:
                        movie_ids.append(index)
                    elif edited_title == foreign_title:
                        movie_ids.append(index)

        return movie_ids

    def extract_emotion(self, preprocessed_input):
        punctuations = string.punctuation
        preprocessed_input = re.sub(r'"(.*?)"', '', preprocessed_input.lower())
        preprocessed_input = re.sub('[%s]' % re.escape(punctuations), '', preprocessed_input)
        
        # Count occurrences of emotion keywords
        happiness_count = 0
        sadness_count = 0
        anger_count = 0
        fear_count = 0
        surprise_count = 0
        disgust_count = 0
        for i, word in enumerate(preprocessed_input.split()):
            if word in NEGATIVES:
                return None
            word = self.p.stem(word)
            if word in HAPPY:
                happiness_count += 1
            elif word in SAD:
                sadness_count += 1
            elif word in FEAR:
                fear_count += 1
            elif word in ANGRY:
                anger_count += 1
            elif word in SURPRISE:
                surprise_count += 1
            elif word in DISGUST:
                disgust_count += 1
        
        emotions = {
            'happiness': happiness_count,
            'sadness': sadness_count,
            'anger': anger_count,
            'fear': fear_count,
            'surprise': surprise_count,
            'disgust': disgust_count
        }

        dominant_emotion = max(emotions, key=emotions.get)
        if emotions[dominant_emotion] == 0:
            return None
        return dominant_emotion

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
        punctuations = string.punctuation
        sent_score = 0
        super = 0
        input = re.sub(r'"(.*?)"', '', preprocessed_input.lower())
        input = re.sub('[%s]' % re.escape(punctuations), '', input)
        input_words = input.split()

        neg_next = 1
        score = 0
        for i, word in enumerate(input_words):
            if word in NEGATIVES:
                neg_next *= -1
                if i == len(input_words) - 1:
                    sent_score *= neg_next
                continue
            word = self.p.stem(word)            
            if self.creative:
                if word in STRONG:
                    super = 1
            if word in self.sentiment:
                if self.sentiment[word] == 'pos':
                    score = 1
                elif self.sentiment[word] == 'neg':
                    score = -1
                score *= neg_next
                neg_next = 1
                sent_score += score
        
        if sent_score > 0:
            sent_score = 1 + super
        elif sent_score < 0:
            sent_score = -1 - super
        return sent_score

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
        tupleList = []
        split_chars = ["and", "or", "but"]
        for char in split_chars:
            preprocessed_input = preprocessed_input.replace(char, char + "\n")
        lines = preprocessed_input.split("\n")
        lines = [line.strip() for line in lines if line.strip()]
        prev_sentiment = 0
        for line in lines:
            titles = self.extract_titles(line)
            # titles = [self.titles[self.find_movies_by_title(title)[0]][0] for title in titles]
            sentiment = self.extract_sentiment(line)
            if sentiment == 0:
                sentiment = prev_sentiment
            for title in titles:
                tupleList.append((title, sentiment))
            prev_sentiment = sentiment

        return tupleList

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
        #### find title ####  
        title = title.lower()
        close_titles = []
        min_dist_so_far = max_distance + 1

        #### Iterate & Edit All Titles ####
        for index in range(len(self.titles)):
            (p_title, genre) = self.titles[index]
            # lowercased p_title 
            p_title = p_title.lower()
            # extract the title from p_title 
            year_pattern = ".+ \([0-9]{4}\)"
            # find if title has year 
            if re.match(year_pattern, p_title):
                # p_title = re.findall("(.+[^\s]),?\s?\([0-9]{4}\)", p_title)
                p_title = re.findall("(.+)\s.+", p_title)
                p_title = p_title[0]
                p_title_w_eng = re.findall("(.+),\s(the|a|an)[^,]*", p_title)
                if len(p_title_w_eng) != 0:
                    p_title = p_title_w_eng[0][1] + " " + p_title_w_eng[0][0]
            
            #### find the edit distance ####

            # initialize matrix
            D = np.zeros((len(title)+1, len(p_title)+1), 'int')
            for j in range(len(p_title)+1):
                D[0][j] = j
            for i in range(len(title)+1):
                D[i][0] = i

            # recurrence relation 
            for i in range(1, len(title)+1):
                for j in range(1, len(p_title)+1):
                    subst_cost = 2
                    if title[i-1] == p_title[j-1]:
                        subst_cost = 0
                    # update matrix
                    D[i][j] = np.min([D[i-1][j]+1, D[i][j-1]+1, D[i-1][j-1]+subst_cost])
                    
            #### update close titles list ####
            if D[len(title)][len(p_title)] <= max_distance:
                if D[len(title)][len(p_title)] == min_dist_so_far:
                    close_titles.append(index)
                elif D[len(title)][len(p_title)] < min_dist_so_far:
                    min_dist_so_far = D[len(title)][len(p_title)]
                    close_titles = []
                    close_titles.append(index)

        return close_titles

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
        response = []
        for candidate in candidates:
            title = self.titles[candidate][0]
            if clarification in title:
                response.append(candidate)
        return response

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
        # TODO: Compute cosine similarity between the two vectors.             #
        ########################################################################
        norm_u = np.linalg.norm(u)
        norm_v = np.linalg.norm(v)

        if norm_u == 0 or norm_v == 0:  
            return np.dot(u,v)
        similarity = np.dot(u, v) / (norm_u * norm_v)
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

        similarity_matrix = np.zeros((len(user_ratings), len(user_ratings)))
        # only calculate at most (# movies watched) x (# all movies) similarities
        for i in range(len(user_ratings)):
            if user_ratings[i] != 0:
                similarity_matrix[i] = np.array([self.similarity(ratings_matrix[i], ratings_matrix[j]) for j in range(len(user_ratings))])
        # P = similarity_matrix^T * user_ratings
        prediction_vector = np.transpose(similarity_matrix).dot(user_ratings)
        recommendations = np.argsort(prediction_vector)[::-1]
        movie_index_watched = np.nonzero(user_ratings)
        # exclude those watched
        recommendations = [v for v in recommendations if v not in movie_index_watched[0]]

        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        return recommendations[:k]

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
        This is the SUPER MOVIEBOT. This movie bot will ask the user for an input 
        of movies & the user's opinion on it! After 5 or more data inputs, the moviebot
        will automatically ask the user if they want a ~JUICY~ recommendation! Enjoy!
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
