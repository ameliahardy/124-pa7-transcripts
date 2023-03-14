# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import numpy as np
from porter_stemmer import PorterStemmer
import re 
import random

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'Suzy the Sassy Sheep'

        self.creative = creative
        self.awaiting_spelling_check = False
        self.spell_check_verified = False
        self.closest_movie = ""
        self.stored_sentiment = -10
        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.movies = util.load_titles('data/movies.txt')
        self.title_number = 0 #  movies input count 
        self.recommend_index = 0 # recommendations count 
        self.sentiment_score = 0 # need to track the sentiment of previous input (for disambiguate dialogue)
        self.disambiguate_track = False # keep track whether the input is about previous input or not (for disambiguate dialogue)
        self.disambiguate_title = [] # keep track of the title 
        self.foreign_articles = ['der', 'den', 'dem', 'des', 'der', 'die', 'das' ,'la', 'le', 'l\'', 'les', 'el', 'los', 'las', 'lo', 'gli', 'i']
        # np array for user raitings 
        self.user_ratings = np.zeros(len(self.titles))
        
        self.arbitrary_list1 = ["This is baaaad, I don't see a movie title! Let's go back to movies, please \n(Use :quit if you're done!)",
                                "Stop wooling around!!! Tell me more about another movie you have seen. \n(Use :quit if you're done!)",
                                "Baaad news, no movie title in sight. Let's stick to movies, please \n(Use :quit if you're done!)",
                                "Are you kidding me? Stop wooling around and tell me more about the movie!! \n(Use :quit if you're done!)",
                                "Oh sheep! No movie detected! Can we just talk about movies? \n(Use :quit if you're done!)",
                                "Baaad situation! Can't find any movie title here...tell me about movies please \n(Use :quit if you're done!)",
                                "No movie detected...Can we please get back on track and chat about movies, wool you? \n(Use :quit if you're done!)",
                                "Baa baa baa. Can you get back to movies please? \n(Use :quit if you're done!)"
                                "How irrelevant. Can you get back to movies? You're starting to sound like a cow. \n(Use :quit if you're done!)"]
        
        self.arbitrary_list2 = ["I'm woolly confused here. Do you want more recommendation or not? \n(Use :quit if you're done!)",
                                "Baaad news, I don't know what you're talking about. Do you want more recommendation? \n(Use :quit if you're done!)",
                                "Stop wooling around! Do you want more recommendations or not? \n(Use :quit if you're done!)",
                                "That's not what we're supposed to be talking about now? Do you want me to keep lamb-splaining more recommendations or not? \n(Use :quit if you're done!)",
                                "Baaa, do you want me to keep ramming more recommendations or are we done here? \n(Use :quit if you're done!)",
                                "Baa baa baa. Irrelevant- almost like your opinion. I'll give you another chance to redeem yourself. \n(Use :quit if you're done!)"
                                "Am I not speaking the language of the humans? What do you not understand about this conversation? Give me a movie please. \n(Use :quit if you're done!)",
                                "Let's count how many sheep care about what you just said... Oh wait there are none. Movies please? \n(Use :quit if you're done!)"]

        self.positive_list = ["Baaaa, great, you liked %s! Tell me about another movie you have seen.", 
                              "Meh, %s was alright. Got any other movies to share, sheep?",
                              "Meh, %s was okay, but glad that you liked it. Do you have any other movies you wanna talk about?",
                              "Baaa, I'm glad you enjoyed %s, but I personally think there are better movies out there. Any other movies you want to share?",
                              "Oh sheep! %s is also one of my favorite movies! Tell me more about movies that you watched recently.",
                              "%s was great, but it's not like it's the greatest sheep movie ever made.So, what else do you have in mind?",
                              "Glad that you liked %s, but that was mid. My wool is practically falling asleep from boredom. Tell me about something else!",
                              "Glad you liked '%s', but let's not pretend it was anything groundbreaking. Got any other movies to chat about, or should I count sheep instead?"]
        
        self.negative_list = ["Bah! You didn't like %s? Can't blame you, counting sheep is better. Anyways, what other movies do you like?",
                              "I'm wooly confused here, %s is one of my favorite movies. So, do you maybe want to talk about any other movies that you watched recently?",
                              "Baaaa, I also hate %s. Counting sheep is much more fun than watching that movie, right? Got any other movies to chat about?",
                              "Didn't like %s? Meh,can't blame you. What other movies do you like?",
                              "You didn't like %s? Eh,I've seen better movies. Got any another movies you wanna talk about?",
                              "Oh sheep!I also saw %s last week and I thought it was horrible! What other movies do you wanna talk about!¥?"]

        self.neutral_list = ["Bahhh i'm having trouble detecting whether you liked %s or not..let's just switch gears and talk about another movie?",
                             "Let's not waste any more time discussing about %s if you don't even know whether you like it or not.Tell me another movie!",
                             "Oh sheep! This is baaad! I still don't know if you like %s or not! Shall we talk about another movie?",
                             "Baaaa, I still don't know whether you like %s or not! Got any other movies to chat about?",
                             "Im wooly confused here, I don't know if you liked %s or not. Got any other movies to chat about?",
                             "Baaa, I'm confused whether you liked %s or not. Shall we talk about a different movie?"]
        
        self.recommendation_list = ["Baaaa, I recommend you watch %s! Trust me, it's one of the best movies ever made! Do you want more recommendations? (enter :quit if you're done!)",
                                    "Baaa, believe me, %s is the cream of the crop! Want more recs of are you ready to say baaaaaa-bye? (enter quit if you're done!)",
                                    "I would like to recommend %s! Do you need more suggestions or are you ready to say baaaaa-bye? (enter quit if you're done!)",
                                    "Honey Lamb, I think you will like %s! One of my favorite movies! Do you want more recommendations or are you ready to quit? (enter quit if you're done!)",
                                    "Oh sheep! I thnk you'll really like %s! Do you want more suggestions or are you ready to count the sheep? (enter quit if you're done!)"]

        with open('data/movies.txt') as file:
            self.movie_dict = {}
            for line in file:
                line = line.rstrip()
                number = line.split("%")[0]
                movie = line.split("%")[1]
                self.movie_dict[number] = movie 

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings, threshold=2.5)
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

        greeting_message = "Hi, I'm Suzy the Sassy Sheep! Since you humans have trash opinoins when it comes to movies, I'm here to give you recommendations on what to watch. Even though your opinions are still probably baaaaad, can you give me a movie you love or hate \n (Use :quit if you're done!)?"

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

        goodbye_message = "Good Riddance! I already know I was super helpful, but you gave me no new information whatsoever- I literally knew every movie you told me. Even still, don't forget to get some good grass for that movie :) \n Baaaaaaaaaaaaaaaaaaaaaa-ye!"

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
            # start the creative mode 

            # extract title  
            input_title = self.extract_titles(line)
            

            # logical fork for answering spell-check
            if self.awaiting_spelling_check:
                self.awaiting_spelling_check = False
                if line.lower() == "yes":
                    input_title.append(str(self.closest_movie))
                elif line.lower() == "no":
                    self.stored_sentiment = -10 #defaults
                    return "Aw ok, tell me about another movie that you've seen"
           
            movie_index = []
            closest = []
            if input_title != []:
                # if creative, swap out
                if len(input_title) > 1 and self.creative: #multiple movies are given
                    movies = self.extract_sentiment_for_movies(line)
                    response = "Wow you've seen so many movies! Have you heard of getting a life? \n"
                    movie_count = 0
                    for movie in movies:
                        if movie_count == len(movies):
                            response += "And Baaaast but not Least,"
                        if movie[1] > 0:
                            response += "You liked " + movie[0] + ".\n"
                        if movie[1] < 0:
                            response += "You didn't like " + movie[0] + ".\n"
                    response += "Here's a Baa for every movie you told me: \n"
                    for movie in movies:
                        response += "Baaaaa! \n"
                    response += "But if you still want recommendations... can you tell me them separately? I'm a sheep- I can only handle so much at once. (Use :quit if you're done!)"
                    return response
                else: #one movie is given and not creative
                    movie_index = self.find_movies_by_title(input_title[0])
                    if not movie_index:
                        closest = self.find_movies_closest_to_title(input_title[0])
                        if not closest:
                            movie_index, store = self.handle_foreign_title(input_title[0])
                            if store: input_title = store

            # dialogue for spell-check
            if not movie_index and closest:
                self.closest_movie = self.movies[closest[0]][0]

                # extracitng title
                if ')' not in self.closest_movie: pass
                else: 
                    op = '(.+) \('
                    temp = re.findall(op, self.closest_movie)
                    self.closest_movie = temp[0]
                response = "I'm sorry, I don't have a movie in my database with that title. Did you mean \"" + self.closest_movie + "\"?"
                self.stored_sentiment = self.extract_sentiment(line)
                # NEED TO STORE SENTIMENT TOO!!
                self.awaiting_spelling_check = True
                # how to get yes??
                return response
            
            # case 1: user asked when the chatbot it still asking for more information 
            if movie_index == [] and self.title_number < 4:
                # ambiguous response 
                if "can" in line.lower():
                    can_response = "Maybe I can and maybe even you can- it doeesn't matter. Can you like stay on topic? \nPlease tell me about another movie so that I can give you baaa-rilliant recommendations?!" 
                    response = can_response
                    return response 
                if "where" in line.lower():
                    where_response = "I'm sorry, I think you'll need to talk to a Shepard about that one. \nPlease tell me aboout another movie that you have seen so that I can give you baaa-rilliant recommendations?!"
                    response = where_response
                    return response 
                if "how" in line.lower():
                    how_response = "Baaaa, the better question is how am I still putting up with you? If you don't stay on topic, I will silence myself. \nPlease tell me about another movie so that I can give you baaa-rilliant recommendations?!"
                    response = how_response
                    return response  
                if "why" in line.lower():
                    why_response = "Baaaa, that's why. Can we go back to what we were discussing previously? \nPlease tell me aboout another movie so that I can give you baaa-rilliant recommendations?!"    
                    response = why_response
                    return response 
                if "who" in line.lower():
                    who_response = "Baaa, why would I care about them in the first place? \nPlease tell me about another movie so that I can give you baaa-rilliant recommendations?!"  
                    response = who_response
                    return response
                if "what" in line.lower():
                    what_response = "The better question is what is keeping the other humans back from using you for a sacrifice? I know sheep are definietly more worthy, but still, you're a waste of wool if I've ever seen one. \n Please tell me aboout another movie so that I can give you baaa-rilliant recommendations?! (Use :quit if you're done!)"
                    response =what_response
                    return response                 
                if self.disambiguate_track == False:
                    chosen = random.choice(self.arbitrary_list1)
                    self.arbitrary_list1.remove(chosen)
                    response = chosen 
                    return response 
                
            # case 2: use asked questions while giving recommendation 
            if movie_index == [] and self.recommend_index != 0:
                if "can" in line.lower():
                    can_response = "Maybe I can and maybe even you can- it doeesn't matter. Can you like stay on topic? \nPlease tell me about another movie so that I can give you baaa-rilliant recommendations?!" 
                    response = can_response
                    return response 
                if "where" in line.lower():
                    where_response = "I'm sorry, I think you'll need to talk to a Shepard about that one. \nPlease tell me aboout another movie that you have seen so that I can give you baaa-rilliant recommendations?!"
                    response = where_response
                    return response 
                if "how" in line.lower():
                    how_response = "Baaaa, the better question is how am I still putting up with you? If you don't stay on topic, I will silence myself. \nPlease tell me about another movie so that I can give you baaa-rilliant recommendations?!"
                    response = how_response
                    return response  
                if "why" in line.lower():
                    why_response = "Baaaa, that's why. Can we go back to what we were discussing previously? \nPlease tell me aboout another movie so that I can give you baaa-rilliant recommendations?!"   
                    response = why_response
                    return response 
                if "who" in line.lower():
                    who_response = "Baaa, why would I care about them in the first place? \nPlease tell me about another movie so that I can give you baaa-rilliant recommendations?!" 
                    response = who_response
                    return response
                if "what" in line.lower():
                    what_response = "The better question is what is keeping the other humans back from using you for a sacrifice? I know sheep are definietly more worthy, but still, you're a waste of wool if I've ever seen one. \n Please tell me aboout another movie so that I can give you baaa-rilliant recommendations?! (Use :quit if you're done!)"
                    return response  

                # random arbitray input  
                else:
                    if "yes" not in line.lower():
                        chosen = random.choice(self.arbitrary_list2)
                        self.arbitrary_list2.remove(chosen)
                        response = chosen 
                        return response 

            
            # keep asking till you get enough information 
            if self.title_number < 4:
                if movie_index != []:
                    self.title_number += 1 
                # dialogue for disambiguation
                if len(movie_index) > 1:
                    title_list = []
                    for index in movie_index:
                        title_list.append(self.movie_dict[str(index)])
                    title_string = ", ".join(title_list)
                    question_return = "Did you mean " +  title_string + "?"
                    self.sentiment_score = self.extract_sentiment(line)
                    response = question_return
                    self.disambiguate_track = True 
                    self.disambiguate_title = movie_index
                    return response

                # when the user responded the clarification
                if self.disambiguate_track == True:
                    clarification = line.lower()
                    final_title = self.disambiguate(str(clarification),self.disambiguate_title)
                   
                    # when disambiguate function was able to return only one movie 
                    if len(final_title) == 1:
                        # if positive sentiment 
                        if self.sentiment_score >= 1 or self.stored_sentiment >=1:
                            if self.sentiment_score:
                                self.user_ratings[movie_index] = self.sentiment_score
                            if self.stored_sentiment:
                                self.user_ratings[movie_index] = self.sentiment_score
                            disambiguate_positive_response = self.return_positive_response(str(self.movie_dict[str(final_title[0])]))
                            self.disambiguate_track = False
                            response = disambiguate_positive_response
                            return response
                        # if negative sentiment 
                        elif self.sentiment_score <= -1 or self.stored_sentiment <=-1:
                            if self.sentiment_score:
                                self.user_ratings[movie_index] = self.sentiment_score
                            if self.stored_sentiment:
                                self.user_ratings[movie_index] = self.sentiment_score
                            disambiguate_negative_response = self.return_negative_response(str(self.movie_dict[str(final_title[0])]))
                            response = disambiguate_negative_response
                            self.disambiguate_track = False
                            return response
                        elif self.sentiment_score == 0 or self.stored_sentiment == 0:
                            self.disambiguate_track = False
                            disambiguate_neutral_response = self.return_neutral_response(str(self.movie_dict[str(final_title[0])]))
                            response = disambiguate_neutral_response 
                            return response 

                    # when disambiguate function could not return just one movie 
                    else:
                        title_list = []
                        for index in final_title:
                            title_list.append(str(self.movie_dict[str(index)]))
                        if not title_list: return "I'm sorry, I did not find a matching movie... Tell me about another one!"
                        title_string = ", ".join(title_list)
                        response = "I am still not sure which movie you are talking about. Did  you mean " + title_string + "?"
                        return response
                
                # if self.disambiguate_track == False (the user response is not related to clarification of the movie)
                else:
                    if self.stored_sentiment != -10:
                        sentiment = self.stored_sentiment

                    else: sentiment = self.extract_sentiment(line)
                    self.stored_sentiment = -10 #set to default after use
                    self.disambiguate_track = False

                    if sentiment == 1:
                        self.user_ratings[movie_index] = 1
                        positive_response = self.return_positive_response(input_title[0])
                        response = positive_response
                        return response
                    elif sentiment == -1:
                        self.user_ratings[movie_index] = -11 
                        negative_response = self.return_negative_response(str(input_title[0]))
                        response = negative_response
                        return response
                    elif sentiment == 0:
                        self.user_ratings[movie_index] = 0
                        neutral_response = self.return_neutral_response(str(input_title[0]))
                        response = neutral_response
                        return response 
                    

            # after you get enough information
            else:
                continue_list = ['yes','keep going','yeah','sure']
                recommendation_list = self.recommend(self.user_ratings,self.ratings,k=10,creative=False)
                recommend_movie_list = []
                
                # if it's clear which movie the user is talking about 
                for index in recommendation_list:
                    title = self.movie_dict[str(index)]
                    recommend_movie_list.append(title)
                enough_information_response = "Baaa, that's enough for me to make a recommendation. I suggest you watch " + recommend_movie_list[self.recommend_index] + ". Do you want more recommendations? (Or enter :quit if you're done.)"
                self.recommend_index += 1 
                if line.lower() not in continue_list and line.lower() != 'quit':
                    response = enough_information_response
                    return response 
                # if continue     
                elif line.lower() in continue_list and self.recommend_index <= 5:
                    movie_rec = self.return_recommendation_response(recommend_movie_list[self.recommend_index])
                    response = movie_rec
                    return response 
                # out of recommendation
                elif line.lower() in continue_list and self.recommend_index >= 6:
                    out_of_index = "I'm out of recommendation now, but I would love to give you more recs! Tell me about a movie you have seen."
                    self.title_number = 0 
                    self.recommend_index = 0 
                    response = out_of_index
                    return response
                # if quit 
                elif line.lower() == 'quit':
                    farewell_message =  "I hope you enjoy watching the movie! Please let me know if you want more recs!"
                    response = farewell_message
                    return response

        # STARTER MODE!!!!!!
        else:
            response = "I processed {} in starter mode!!".format(line)
            movie_index = []
            # extract title  
            input_title = self.extract_titles(line)
            if input_title != []:
                movie_index = self.find_movies_by_title(input_title[0])

            # more than one movie 
            if len(input_title) > 1:
                return "Please tell me about one movie at a time."
            # no title 
            if movie_index == [] and self.title_number < 2:
                return "I don't see a movie title... Please tell me about another movie that you have seen."
            
            # keep asking till you get enough information 
            if self.title_number < 4:
                self.title_number += 1 
                if self.extract_sentiment(line) == 1:
                    self.user_ratings[movie_index] = 1
                    positive_response = self.return_positive_response(str(input_title[0]))
                    return positive_response
                elif self.extract_sentiment(line) == -1:
                    self.user_ratings[movie_index] = -1
                    negative_response = self.return_negative_response(str(input_title[0]))
                    return negative_response
                elif self.extract_sentiment(line) == 0:
                    self.user_ratings[movie_index] = 0
                    neutral_response = self.return_neutral_response(str(input_title[0]))
                    return neutral_response

            # after you get enough information
            else:
                continue_list = ['yes','keep going','yeah','sure', 'ya', 'yee']
                recommendation_list = self.recommend(self.user_ratings,self.ratings,k=10,creative=False)
                recommend_movie_list = []
                for index in recommendation_list:
                    title = self.movie_dict[str(index)]
                    recommend_movie_list.append(title)
                enough_information_response = "That's enough for me to make a recommendation. I suggest you watch " + recommend_movie_list[self.recommend_index] + ". Do you want more recommendations? (Or enter :quit if you're done.)"
                self.recommend_index += 1 
                if line.lower() not in continue_list and line.lower() != 'quit':
                    return enough_information_response
                # if continue     
                elif line.lower() in continue_list and self.recommend_index <= 5:
                    movie_rec = self.return_recommendation_response(recommend_movie_list[self.recommend_index])
                    return movie_rec
                elif line.lower() in continue_list and self.recommend_index >= 6:
                    out_of_index = "I'm out of recommendation now, but I would love to give you more recs! Tell me about a movie you have seen."
                    self.title_number = 0 
                    self.recommend_index = 0 
                    return out_of_index
                # if quit 
                elif line.lower() == 'quit':
                    farewell_message =  "I hope you enjoy watching the movie! Please let me know if you want more recs!"
                    return farewell_message

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################

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

    # helper function (randomly choose positive and negative response)
    def return_positive_response(self,movie_title):
        chosen = random.choice(self.positive_list)
        self.positive_list.remove(chosen)
        response = chosen % movie_title  # Replace %s with the actual movie title
        return response

    def return_negative_response(self,movie_title):
        chosen = random.choice(self.negative_list)
        self.negative_list.remove(chosen)
        response = chosen % movie_title 
        return response 
    
    def return_neutral_response(self,movie_title):
        chosen = random.choice(self.neutral_list)
        self.neutral_list.remove(chosen)
        response = chosen % movie_title
        return response 
    
    def return_recommendation_response(self,movie_title):
        chosen = random.choice(self.recommendation_list)
        self.recommendation_list.remove(chosen)
        response = chosen % movie_title
        return response 

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
        final_output = []
        movie_pattern = '\"(.+?)\"'
        movie_matches = re.finditer(movie_pattern, str(preprocessed_input)) 
        for match in movie_matches:
            final_output.append(match.group(1))
        return final_output 
        


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
                
        final_output = []
        match = []
        title = title.lower()
        # case 1 title with (and without) year 
        year_match = re.search('\(\d{4}\)$',title)
        if year_match:
            movie_title = title
            movie_year = title[-6:] #stored
            has_year = True 
        else:
            movie_title = title 
            has_year = False
        

        # pre-processing by changing order of article
        # case 2 title with A, An, and The -> change the order of the name
        if movie_title[0:2] == "a ": 
            if has_year:
                movie_title = movie_title[2:-6].strip() + ", a " + movie_year
            else: 
                movie_title = movie_title[2:].strip() + ", a"

        if movie_title[0:3] == "an ": 
            if has_year:
                movie_title = movie_title[3:-6].strip() + ", an " + movie_year
            else: 
                movie_title = movie_title[3:].strip() + ", an"
        if movie_title[0:4] == "the ": 
            if has_year:
                movie_title = movie_title[4:-6].strip() + ", the " + movie_year
            else: 
                movie_title = movie_title[4:].strip() + ", the"

        # go through all movies
        for id in range(len(self.movies)):
            cur = self.movies[id]
            if has_year and cur[0].lower() == movie_title.lower():
                final_output.append(id)
                continue
            if not has_year and cur[0][:-7].lower() == movie_title.lower():
                final_output.append(id)
                continue

        if self.creative:
            match = final_output.copy()
            # add other movies that include the same token 
            tokens = movie_title.lower()
            regex_pattern = fr"\b{tokens}\b"
            for num in range(len(self.movies)):
                cur = self.movies[num]
                title = cur[0].lower()
                matches = re.findall(regex_pattern,title)
                for movie in matches:
                    if num not in final_output:
                        match.append(num)
            return match 
        else:
            return final_output
    
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

        movie_title = self.extract_titles(preprocessed_input)
        # create movie_pattern 
        regex_movie_pattern = ""
        for title in movie_title:
            regex_movie_pattern += re.escape(title) + "|"
        regex_movie_pattern = regex_movie_pattern[:-1] # remove the last | 
        # remove the movie title 
        removed_input = re.sub(regex_movie_pattern,' ',str(preprocessed_input))
        list_of_words_lower = removed_input.lower()
        list_of_words_split = list_of_words_lower.split()

        # Stem the words from the input.
        stemmed_words = []
        for word in list_of_words_split:
            stemmed_words.append(PorterStemmer().stem(word))
        
        # Count the positive and negative word occurrences
        positive_count = 0
        negative_count = 0
        
        # make a dictionary that contains all the words and sentiment 
        with open('data/sentiment.txt') as file:
            sentiment_dict = {}
            for line in file:
                line = line.rstrip()
                word = line.split(",")[0]
                sentiment = line.split(",")[1]
                sentiment_dict[PorterStemmer().stem(word)] = sentiment
                
        # count negative words and positive words 
        #includes creative feature for fine grained sentiment
        no_sentiment = True 
        stored = 0
        positive_words = ['love', 'obsessed', 'favorite', 'awesome', 'best', 'magnificent', 'great']
        fine_positive = []
        for word in positive_words:
            fine_positive.append(PorterStemmer().stem(word))
        negative_words = ['hate', 'loathe', 'despise', 'worst', 'terrible', 'atrocious', 'awful', 'abyssmal']
        fine_negative = []
        for word in negative_words:
            fine_negative.append(PorterStemmer().stem(word))
        degree_words = ['really', 'very']
        fine_degree = []
        for word in degree_words:
            fine_degree.append(PorterStemmer().stem(word))
        for word in stemmed_words:
            if word in sentiment_dict:
                no_sentiment = False 
                if sentiment_dict[word] == "pos":
                    positive_count += 1 
                    if word in fine_positive:
                        positive_count += 9 #total 10
                    if stored == 1:
                        positive_count += 5
                        stored = 0
                if sentiment_dict[word] == "neg":
                    negative_count += 1 
                    if word in fine_negative:
                        negative_count += 9 #total 10
                    if stored == 1:
                        negative_count += 5
                        stored = 0
                #compute edit distance to really and if over threshold then use the really function
            if word in fine_degree:
                stored = 1
        # print(stemmed_words)
        # print (negative_count)
        # print('positive: ', positive_count)
        # print('negative: ', negative_count)
        # current_score = 1
        # print(word, positive_count)
        if positive_count > negative_count:
            current_score = 1
            if self.creative and positive_count > 3:
            # if positive_count > 3: #means at least very or strong word was used
                current_score = 2
        elif positive_count  < negative_count:
            current_score = -1 
            if self.creative and negative_count > 3:
            # if negative_count > 3: #means at least very or strong word was used or multiple bad words
                current_score = -2 
        elif positive_count == negative_count:
            current_score = 0
        # print("current_score: ", current_score)
        # handle negation 
        negation_words = ["don't","doesn't","didn't", "couldn't","cannot", "can't", "not", "never", "no", "'nt", "none", "neither", "never"
                         "isn't", "wasn't", "won't", "rarely", "nothing", "nor", "barely", "hardly", "scarcely", "seldom", "rarely",
                         "nobody", "noone", "nowhere"]
        negation_list = []
        for word in negation_words:
            negation_list.append(PorterStemmer().stem(word))
        for word in stemmed_words:
            if word in negation_list:
                current_score *= -1 
        
        # print("current_score", current_score)
        return current_score



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
        titles = self.extract_titles(preprocessed_input)
        split_input = preprocessed_input
        sentiments = []
        alone = [] #holds movies that do not have sentiment yet
        movie_count = 0
        for movie in titles:
            movie_count += 1
            # create movie_pattern 
            regex_movie_pattern = re.escape(movie)
            split = re.split(regex_movie_pattern, split_input)
            beginning = split[0]
            split_input = split[1]
            if movie_count == len(titles): #if last movie then append the rest
                if len(split_input) > 3:
                    beginning += split_input
            list_of_words_lower = beginning.lower()
            list_of_words_split = list_of_words_lower.split()

            # Stem the words from the input.
            stemmed_words = []
            for word in list_of_words_split:
                stemmed_words.append(PorterStemmer().stem(word))
            
            # Count the positive and negative word occurrences
            positive_count = 0
            negative_count = 0
            
            # make a dictionary that contains all the words and sentiment 
            with open('data/sentiment.txt') as file:
                sentiment_dict = {}
                for line in file:
                    line = line.rstrip()
                    word = line.split(",")[0]
                    sentiment = line.split(",")[1]
                    sentiment_dict[PorterStemmer().stem(word)] = sentiment
                    
            # count negative words and positive words 
            #includes creative feature for fine grained sentiment
            no_sentiment = True 
            stored = 0
            for word in stemmed_words:
                if word in sentiment_dict:
                    no_sentiment = False 
                    if sentiment_dict[word] == "pos":
                        positive_count += 1 
                        if re.search("love", word) != None:
                            positive_count += 9 #total 10
                        if stored == 1:
                            positive_count += 5
                            stored = 0
                    if sentiment_dict[word] == "neg":
                        negative_count += 1 
                        if re.search("hate | loathe", word) != None:
                            negative_count+= 9 #total 10
                        if stored == 1:
                            negative_count += 5
                            stored = 0
                    #compute edit distance to really and if over threshold then use the really function
                    if re.search("really | very", word) != None:
                        stored = 1

            if positive_count > negative_count:
                current_score = 1 
                if positive_count > 5: #means at least very or strong word was used
                    current_score = 2
            elif positive_count  < negative_count:
                current_score = -1 
                if negative_count > 5: #means at least very or strong word was used
                    current_score = -2
            elif positive_count == negative_count:
                current_score = 0 

            # handle negation 
            negation_words = ["don't","doesn't","didn't", "couldn't","cannot", "can't", "not", "never", "no", "'nt", "none", "neither", "never"
                         "isn't", "wasn't", "won't", "rarely", "nothing", "nor", "barely", "hardly", "scarcely", "seldom", "rarely",
                         "nobody", "noone", "nowhere"]
            negation_list = []
            for word in negation_words:
                negation_list.append(PorterStemmer().stem(word))
            for word in stemmed_words:
                if word in negation_list:
                    current_score *= -1 
                    if current_score == 0:
                        current_score += -1 

             #END OF SAME EXTRACT SENTIMENT FUNCTION
            if current_score == 0:   #must use sentiment of other movie
                if len(sentiments) > 0:
                    current_score = sentiments[len(sentiments)-1][1]
                else:
                    alone.append(movie) #store movie to be used later
            if (len(alone) > 0) and current_score != 0:
                for loner in alone:
                    sentiments.append = [loner, current_score]
                    alone.remove(loner)
            sentiments.append((movie, current_score))
        return sentiments 

    # helper function: to calculate edit distance
        for movie in preprocessed_input:
            sentiment = self.extract_sentiment(movie)
            sentiments.append((movie, sentiment))
        return sentiments
# helper function: to calculate edit distance
    def edit_distance(self, w1, w2, max_dist):
        w1 = w1.lower().strip()
        w2 = w2.lower().strip()
        n = len(w1)+1
        m = len(w2)+1
        dp = np.zeros((n,m))

        # set up
        for i in range(n):
            dp[i][0] = i
        for j in range(m):
            dp[0][j] = j

        for i in range(1,n):
            for j in range(1,m):
                if w1[i-1] == w2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else: #neq
                    dp[i][j] = min(dp[i-1][j-1]+2, dp[i-1][j]+1,dp[i][j-1]+ 1)

        return dp[n-1][m-1]
    
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
        ret = []
        movie_list = []
        min = 100000

        # go through  movies
        for i in range(len(self.movies)):
            movie = self.movies[i][0].lower()#check this
            #extract title
            if ')' not in movie: continue
            else: 
                op = '(.+) \('
                temp = re.findall(op, movie)
                movie = temp[0]

            dist = self.edit_distance(title, movie, max_distance)
            if dist <= max_distance:
                # only keep those closest to title!!
                if dist < min:
                    min = dist
                    ret = [i]
                    movie_list = [self.movies[i][0]]
                elif dist == min:
                    ret.append(i)
                    print(self.movies[i][0])
                    movie_list.append(self.movies[i][0])
        return ret

    def handle_foreign_title(self, title):
        splits = title.split()
        mod_title = ""
        article = ""
        yr = ""
        
        # store article
        if splits[0] in self.foreign_articles:
            article = splits[0]
            splits.pop(0)
        year = re.search('\(\d{4}\)$',title[-1])
        # store year
        if year:
            yr = title[-1]
            splits.pop()

        # new name
        mod_title = ' '.join(splits)
        if article: mod_title = mod_title + ', ' + article

        for i in range(len(self.movies)):
            movie = self.movies[i]
            aka = re.findall(r"\(a\.k\.a\.(.*)[^\)]", movie[0])
            
            foreign = re.findall(r"\(([^\)]+)\) \(", movie[0])
            
            if aka:
                
                aka = aka[0].strip()
                aka = aka[:-6]
                print(aka)
                if aka.lower().strip() == mod_title.lower().strip():
                   
                    print(matching_movie)
                    return [i], matching_movie
            elif foreign:
                #print(mod_title)
                #print(foreign[0].lower())
                # if re.escape(foreign[0].lower()) == re.escape(mod_title.lower()):
                if foreign[0].lower().strip() == mod_title.lower().strip():
                    matching_movie = re.findall(r"(.*\))", movie[0])
                    return [i], matching_movie
            

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
        final_output = []
        clarification = str(clarification).lower()
        for candidate in candidates:
            movie_index = str(candidate) 
            movie_title = self.movie_dict[movie_index].lower()

            year_match = re.search('\d{4}',clarification)
            # step1: if clarification is year -> return a movie title that includes 1994 
            if year_match:
                if clarification in movie_title:
                    if candidate not in final_output:
                        final_output.append(candidate)

            # step2: if clarification is not a year (example: 2) -> title might inlcude 2 so delete the movie year 
            else:
                year_match2 = re.search('\(\d{4}\)',movie_title)
                if year_match2:
                    movie_title = re.sub(year_match2.group(),' ',movie_title)
                    if clarification in movie_title:
                        if candidate not in final_output:
                            final_output.append(candidate)

        return final_output

            
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
        
        # i = movies j = users 
        # create a copy first 
        temp = np.where((ratings != 0)&(ratings<=2.5), -1, ratings)
        temp2 = np.where(temp>2.5, 1, temp)
        binary_ratings = temp2

        return binary_ratings

        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        #return binarized_ratings

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
        numer = np.dot(u,v)
        denom = np.linalg.norm(u) * np.linalg.norm(v)
        if denom != 0:
            similarity = numer/denom
        else: similarity = 0
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
        #user = self.binarize(user_ratings)
        #ratings = self.binarize(ratings_matrix)
        #for every movie:
            #compute similarity with 
        rated = np.nonzero(user_ratings)[0] #only gives movies that are rated

        for i in range(len(ratings_matrix)):
            if i in rated: 
                # already rated
                continue
            else:
                res = 0
                for s in rated:
                    s_ij = self.similarity(ratings_matrix[s], ratings_matrix[i])
                    r_xj = user_ratings[s]
                    res += s_ij * r_xj
                recommendations.append((i, res))
        
        sort = sorted(recommendations, key=lambda elem:elem[1], reverse=True)
        recommendations = [movie[0] for movie in sort[0:k]] # get top scores
        return recommendations


        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        #return recommendations

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
        return "Suzy the Sassy Sheep is here to give all you stupid humans the right recommendations on movies out there. \n With witty comebacks and stellar (almost computer-like) knowledge, Suzy is for sure a hoot! \nOr rather, a Baaaaaaaa! "
        """
        Your task is to implement the chatbot as detailed in the PA7
        instructions.
        Remember: in the starter mode, movie names will come in quotation marks
        and expressions of sentiment will be simple!
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')

