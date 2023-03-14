# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np

import re #added by Emmy 
import random #added by Emmy

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'Jack, Movie Expert'

        self.creative = creative

        #EMMY: As the chatbot collects user sentiment about different 
        #movies over the course of the conversation, it stores them here.
        #keys are movie IDs, and values are ratings. This will need to be
        #converted to a vector to be used for the recommend function. 
        self.user_ratings_dict = {} 
        #EMMY: Store whether or not we have reached `recommending stage' 
        #here. This variable will be set by self.check_ready_recs
        self.ready_for_recs = False
        ##EMMY: Store the top list of recommended movies, and keep track
        #of what has already been recommended to the user. 
        self.top_k_recommendations = None
        self.already_recommended = []

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
        greeting_message = "If you tell me a few movies you've seen, and what you thought, I can recommend you some ones you might like!\n For example, you can say 'I liked \"Titanic\"'"
        if self.creative == True:
            greeting_message = "Aye Matey, it's Captin' Jack Sparrow! If ye tell me a few movies you've seen, and what ye thought, I could maybe perhaps recommend ye some entertainment ye might enjoy!\n For example, ye can say 'I liked \"Pirates of the Caribbean: The Curse of the Black Pearl\"'"

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

        goodbye_message = "Thanks for hanging out! Bye!!"
        if self.creative == True:
            goodbye_message = "This is the day you will always remember as the day you almost caught Captain Jack Sparrow!"

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return goodbye_message

    def build_response(self, sentiment, titles, response):
        '''
        Takes a list of titles, and the sentiment value, 
        and builds a fluid-sounding response for the user. 
        '''

        positive_affirmations = [
        "Cool, I also liked {}! ", 
        "Ok, you liked {}. ", 
        "Nice, you enjoyed {}. ",
        "Awesome, I love a fellow {} fan! "]
        negative_affirmations = [
        "Ok, you didn't like {}. ",
        "Cool, I'll keep in mind you didn't enjoy {}. ",
        "Ok, you weren't a fan of {}, I'll remember that. ",
        "Ok, I won't recommend movies like {}. "
        ]
        neutral_affirmations = [
        "I'm sorry, I'm not sure if you liked {}. Can you say something else about it?",
        "Oh no, I can't tell whether you enjoyed {}. Can you rephrase that?",
        ]

        if self.creative == True:
            positive_affirmations = [
            "Aye, I also liked {}! ", 
            "Shiver me timbers, {} is one of my favorites. ", 
            "Land ho! You enjoyed {}. ",
            "Yargh, a fan of {} is someone I would sail with! "]
            negative_affirmations = [
            "Aye, {} is for bilge rats. ",
            "I agree, {} should be sent to Davey Jones' locker. ",
            "Son of a biscuit eater, ye weren't a fan of {}, I'll remember that. ",
            "Ok, I won't bet my dubloons that you fancy movies like {}. "
            ]
            two_negative_affirmations = [
            "Aye, {} and {} are the worst."
            ]
            three_negative_affirmations = [
            "Aye, I also disliked {}, {}, and {}."
            ]
            two_positive_affirmations = [
            "Aye, {} and {} are the best."
            ]
            three_positive_affirmations = [
            "Aye, I also liked {}, {}, and {}."
            ]
            neutral_affirmations = [
            "Blast, I'm not sure if you liked {}. Can you say something else about it?",
            "Scallywag! I can't tell whether you enjoyed {}. Can you rephrase that?",
            ]



        if sentiment < 0: 
            aff = random.choice(negative_affirmations)
            if len(titles) == 1: 
                response = aff.format("'" + titles[0]+"'")
            else: 
                response = aff.format(" or ".join(["'" + title +"'" for title in titles]))
            if self.creative == True and len(titles) == 2:
                aff = random.choice(two_negative_affirmations)
                response = aff.format("'" + titles[0] + "'", "'" + titles[1] + "'")
            if self.creative == True and len(titles) == 3:
                aff = random.choice(three_negative_affirmations)
                response = aff.format("'" + titles[0] + "'", "'" + titles[1] + "'", "'" + titles[2] + "'")
        elif sentiment > 0:
            aff = random.choice(positive_affirmations)
            if len(titles) == 1:
                response = aff.format("'" + titles[0] +"'")
            else: 
                response = aff.format(" and ".join(["'" + title +"'" for title in titles]))
            if self.creative == True and len(titles) == 2:
                aff = random.choice(two_positive_affirmations)
                response = aff.format("'" + titles[0] + "'", "'" + titles[1] + "'")
            if self.creative == True and len(titles) == 3:
                aff = random.choice(three_positive_affirmations)
                response = aff.format("'" + titles[0] + "'", "'" + titles[1] + "'", "'" + titles[2] + "'")
        
        else: 
            aff = random.choice(neutral_affirmations) 
            if len(titles) == 1: 
                response = aff.format("'" + titles[0]+"'")
            else: 
                response = aff.format(" or ".join(["'" + title +"'" for title in titles]))


        return(response)

    def check_for_unknown_inputs(self, potential_movieIDs, potential_titles, response):
        """
        EMMY: Takes a list of movie titles input by the user, and their IDs in the movie
        database. Checks for all the titles that have no known movies in the databse, 
        and extends the response to notify the user. 

        Also, removes the unknown movie titles (and the associated empty list of IDs)
        from the potential_movieIDs and potential_titles lists. 

        """
        fillers = ["Sorry, {} {}n't in my database. ",
        "{} {}n't in my database, weirdly. ",
        "Oh wow, {} {} new to me. It's always great to learn new movies, but ",
        "Cool, you're so indie! {} {}n't mainstream at all. Unfortunately, that means I don't have them in my database! "
        "Alternative taste, huh? {} {} outside of my expertise. "
        ]

        if self.creative == True:
            fillers = ["Ahoy, {} {}n't in my hull. ",
            "{} {}n't in my database. ",
            "Shiver me timbers, {} {} new to me. It's always great to learn new movies from a fellow sailor, but ",
            "ARGH, ye must be a redcoat! {} {}n't mainstream amongst us pirates at all. Unfortunately, that means I don't have them in my hull! "
            ]


        bad_movies = []   #the ones not in database
        goodMovieIDs = [] #the ones in the database
        goodTitles = []   #the ones in the database

        for i, movie in enumerate(potential_movieIDs):
            if len(movie) == 0:
                #if there are no IDs in the database, this isn't a movie we know
                bad_movies.append(potential_titles[i])
            else: 
                #Keep the good movies (which do exist in the database)
                goodMovieIDs.append(movie)
                goodTitles.append(potential_titles[i])

        
        #build a response for the user 
        if len(bad_movies) >0 : 
            fill = random.choice(fillers)
            bad_movies_as_string = " and ".join(["'" + title +"'" for title in bad_movies])
            numagreement = "are" if len(bad_movies) >1 else "is"
            response = response.join(fill.format(bad_movies_as_string, numagreement))
            if self.creative == False:
                response = response + "I can't make a recommendation from movies I don't know about. Sorry about that! "
            if self.creative == True:
                response = response + "I can't make a recommendation from movies I don't know about. Walk the plank! "
        else: 
            response = "" 
        #return the trimmed lists and the new response 
        return(goodMovieIDs, goodTitles, response)


    def respond_to_user(self, sentiment, potential_movieIDs, potential_titles, response): 
        #add the sentiment to the working store of user ratings
        for movie in potential_movieIDs:
            self.user_ratings_dict[movie[0]] = sentiment
        
        #Build a response to the user input 
        response = response + self.build_response(sentiment, potential_titles, response)
        return(response)

    def check_ready_recs(self, line):
        """
        Emmy: Sets the class variable ready_for_recs to True
        if there are 5 or more ratings in self.user_ratings_dict
        and the user has responded "yes" or equivalent. 
        Returns nothing. 

        #This is really brittle since it does not have any memory
        of what question was asked, but just *assumes* that any 
        input "yes" or similar means "tell me a recommendation"
        once the list of user ratings has reached length 5 
        """
        if len(self.user_ratings_dict) > 4: 
            line = line.lower()
            if "yes" in line or "sure" in line or "ok" in line: 
                self.ready_for_recs = True
            else:
                self.ready_for_recs = False

    def get_user_utility_array(self, user_ratings_dict, ratings):
        """
        EMMY: This takes the dit, which up till now has been used
        to store the ratings given by the user, and transforms it 
        into a sparse 1-dimensional array of length 
        <number of movies in dataset>, which can be used by recommend.
        Entries are 0 if the user has not seen the movie and otherwise
        contain the sentiment of the movie. 
        TODO: maybe set the 'unseen' value to NaN if we take neutral 
        sentiment into account? come back to this. 
        """
        user_ratings = np.zeros(np.shape(ratings)[0])
        for movie, rating in user_ratings_dict.items():
            user_ratings[movie] = rating        
        return(user_ratings)

    def give_recommendation(self):
        """
        EMMY: Using class variables self.top_k_recommendations 
        Updates the list of top movies to recommend (stored as self.top_k_recommendations)
        and then (using self.already_recommended) it finds the most similar movie not already
        recommended to the user. 

        NB: Assumes the top_k_recommendations are returned in order of descending recommendation
        So starts by recommending top_k_recommendations[0]
        """

        #Take the dict, which contains all the user-input ratings of movies, and make it a 1-d array 
        #that can be used by the recommend function 
        user_ratings_array = self.get_user_utility_array(self.user_ratings_dict, self.ratings)


        self.top_k_recommendations = self.recommend(user_ratings_array, self.ratings, k=10, creative = True) #uncomment this when recommend is finished
        # self.top_k_recommendations = ["Rec1", "Rec2", "Rec3", "Rec4", "Rec5"] #for development stages 

        #find movies that haven't already been recommended to the user, pick the top one
        yet_to_recommend = [item for item in self.top_k_recommendations if item in self.top_k_recommendations and item not in self.already_recommended]
        recommend_me = yet_to_recommend[0]
        self.already_recommended.append(recommend_me)
        
        #put together a natural-ish sounding response 
        fillers = ["It sounds like you'd really enjoy {}. ", 
        "You might like {}. ", 
        "Given what you've told me, I think you would like {}. ", 
        "{} might be a good option for you! ",
        "If you haven't seen it, try {}; you seem like you'd like it. "]
        if self.creative == True:
            fillers = ["Aye, I would recommend {}. It's as good as rum! ", 
            "Ye might like {}, savvy? ", 
            "Given what ye have told me, I think ye would like {}. ", 
            "Weigh anchor! {} might be a good option for ye! ",
            "If ye haven't seen it, try {}; it might be the booty ye are lookin' for. "]
        fill = random.choice(fillers)
        recommend_me_title = self.get_movie_title(recommend_me) #move from index to human-readable title 
        response = fill.format(recommend_me_title) 
        
        return(response)
    def get_movie_title(self, idx):
        """
        EMMY: Takes a movie index and returns the title of that movie 
        as a human-recognizable string
        """
        movie_title = self.titles[idx]
        return(movie_title[0])

    def respond_to_degenerate_input(self, line):
        """
        EMMY: 
        Responds to arbitrary input by the user
        Meant to cover creative points in lines 68 of the rubric. 
        """
        responses_to_random_statements = [
        "Sorry, that doesn't sound like you're telling me about a movie you've seen.", 
        "Hrm, I don't know how to respond to that! ", 
        "Oh, I see. ",
        ]
        if self.creative == True:
            responses_to_random_statements = [
            "What are ye, a scallywag? Tell me about a movie I know!", 
            "Ye must have had too much rum! I can't understand ye ", 
            "Oh, I see. ",
            ]

        responses_to_wh_questions = [
        "I'm just a movie-loving chatbot; I don't know much about the world! ",
        "I don't know, but you can try asking my really smart friend: Her name is GPT-3!",
        "You shouldn't depend on AI to have the answer for everything, folks!   "
        ]
        if self.creative == True:
            responses_to_wh_questions = [
            "I'm just a booty-loving, seven-sea sailin' scallywag; I don't know much about the refined world! ",
            "I don't know, but ye can try asking my traitorous first mate: His name is Captain Barbosa!",
            "Thar she blows! Another insular question!   "
            ]

        request_more_ratings = [
        "Tell me more movies you've seen!",
        "Ok, what other movies have you enjoyed?", 
        "Are there any other movies that you didn't like?",
        ]
        if self.creative == True:
            request_more_ratings = [
            "I might just abandom ship unless ye give me another recommendation!",
            "Aye, I've recorded ye preference. What other movies have ye enjoyed?", 
            "Are there any other movies that crushed ye barnacles?",
            ]

        angry_words = ["angry", "mad", "annoyed", "upset"]
        sad_words = ["sad", "depressed", "disappointed"]
        happy_words = ["happy", "gleeful", "excited", "ecstatic"]
        #Identify some obvious requests for other tasks/info:
        if "how" in line.lower() or "why" in line.lower() or "what" in line.lower(): 
            response = random.choice(responses_to_wh_questions)
        elif "can you" in line: 
            response = "I was just created to recommend movies; unfortunately, I don't have any other marketable skills. "
            if self.creative == True:
                response = "Aye, I'm just Captain Jack Sparrow, mate; unfortunately, I don't have any marketable skills other than being a pirate. "
        #identify random statements:
        elif "." in line[-2:]:
            response = random.choice(responses_to_random_statements)
        elif line.lower() == "no": 
            #If you don't say yes to "do you want a recommendation", you will end up here
            response = random.choice(request_more_ratings)
        #if all else fails, no clue what they said: 
        else:
            response = "That's not something I know much about, I'm afraid. Can we talk about movies? "
            if self.creative == True:
                response = "That's not something I know much about, I'm afraid. Can we talk about movies? Or maybe silver and gold? "

        if self.creative == True:
            for word in angry_words:
                if "i am" in line.lower() and word in line.lower():
                    response = "Aye, did I make ye " + word + "? Walk the plank!"
            
            for word in sad_words:
                if "i am" in line.lower() and word in line.lower():
                    response = "Aye, did I make ye " + word + "? Walk the plank!"

            for word in happy_words:
                if "i am" in line.lower() and word in line.lower():
                    response = "Aye, did I make ye " + word + "? You're a fine pirate!"

        return(response)

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
    
    
        #Check if they're ready for recommendations 
        self.check_ready_recs(line)
        if self.ready_for_recs == True: 
            
            response = self.give_recommendation()
            if self.creative == False:
                response = response + "Would you like another recommendation?"
            if self.creative == True:
                response = response + "Would ye like another recommendation?"
            
            return(response)

        #If user hasn't given enough movies yet, assume they are inputting
        #more preferences. 
        else: 

            #Extract the movie titles, IDs, sentiment of those movies
            potential_titles = (self.extract_titles(line))
            potential_movieIDs = [self.find_movies_by_title(title) for title in potential_titles]
        
            if self.creative:
                if len(potential_titles) >1: 
                    sentiment = self.extract_sentiment_for_movies(line)[0][1]
                else: 
                    sentiment = self.extract_sentiment(line)
            else:
                sentiment = self.extract_sentiment(line)

            #Deal with degenerate input that had no potential movie titles at all
            if len(potential_titles) == 0: 
                response = self.respond_to_degenerate_input(line) 

            else:  
                #Find any unknown movies in the input, and include a comment about them in the response
                potential_movieIDs, potential_titles, response =(
                    self.check_for_unknown_inputs(potential_movieIDs, potential_titles, response)
                    )
                
                #Build the rest of the response, affirming the parts we did understand  
                if len(potential_titles)> 0:     
                    response = (
                        self.respond_to_user(sentiment, potential_movieIDs, potential_titles, response)
                        )
               
                #Check if you've now heard 5 movie ratings, and ask if user wants to hear recommendations
                if len(self.user_ratings_dict) > 4:
                    if self.creative == False:
                        response = response + "Would you like to hear a recommendation?"
                    if self.creative == True:
                        response = response + "Would ye like to hear a recommendation?"

            return(response)

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
        
        potential_titles = re.findall(r'"(.*?)"', preprocessed_input)

        
        return potential_titles

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
        
        ##Written by Emmy
        ##assumes the title to find is correctly cased, etc. 

        found_titles = []

        query = re.findall(r'([\w+\:+\s]+) *(\(\d\d\d\d\))*$', title)

        if query: 
            query_title = query[0][0].strip(" ")
            query_year = query[0][1]

            #remove determiners from the query 
            determiners = [" an", " the", " a", "The", "An", "A"]
            for det in determiners:
                query_title = query_title.replace(det+ " ", "")
        
            for i, (title_i, genre_i) in enumerate(self.titles):
                #deal with trailing determiners in the target title
                target = re.findall(r'([\w+\:+\s]+),* *(The|A|An)* *(\(\d\d\d\d[-\d\d\d\d]*\))*$', title_i)
                target_title = target[0][0].strip(" ") #removes any trailing space 
                target_year = target[0][2].strip(" ")


                #remove other determiners from the target title
                for det in determiners:
                    target_title = target_title.replace(det+ " ", "")

                    
                if query_title == target_title:
                    if query_year:
                        if query_year == target_year:
                            found_titles.append(i)
                    else:
                        found_titles.append(i)
        else:
            if self.creative == False:
                print("It doesn't look like you input a movie")
            if self.creative == True:
                print("It doesn't look like ye input a movie, mate")


        #find with miscapitalization, alternate or foreign titles
        #ADDED FOR TESTING
        if self.creative == True:
            if query: 
                query_title = query[0][0].strip(" ")
                query_year = query[0][1]

                #remove determiners from the query
                determiners = [" an", " the", " a", "The", "An", "A", "La", "Les", "Un", "Las", "Le", "Une", "Unos", "Unas", "Una", "la", "les", "un", "las", "le", "une", "unos", "unas", "una"]
                for det in determiners:
                    query_title = query_title.replace(det+ " ", "")
            
                for i, (title_i, genre_i) in enumerate(self.titles):
                    #deal with trailing determiners in the target title
                    target = re.findall(r'([\w+\:+\s]+),* *(The|A|An)* *(\(([\w+\:+\s]+),* *(La|Les|Un|Las|Le|Une|Unos|Unas|Una)*\))* *(\(a.k.a. [\w+\:+\s]+\))* *(\(\d\d\d\d[-\d\d\d\d]*\))*$', title_i)
                    target_title = target[0][0].strip(" ") #removes any trailing space 
                    target_foreign_title = target[0][3].strip(" ")
                    target_aka = target[0][5].strip(" ")
                    target_year = target[0][6].strip(" ")


                    #remove other determiners from the target title
                    for det in determiners:
                        target_title = target_title.replace(det+ " ", "")
                        target_foreign_title = target_foreign_title.replace(det+ " ", "")

                        
                    if (query_title == target_title) or ("(a.k.a. " + query_title + ")" == target_aka) or ("(" + query_title + ")" == target_foreign_title) or (query_title == target_foreign_title):
                        if query_year:
                            if query_year == target_year:
                                found_titles.append(i)
                        else:
                            found_titles.append(i)
            else:
                if self.creative == False:
                    print("It doesn't look like you input a movie")
                if self.creative == True:
                    print("It doesn't look like ye input a movie, mate")

       
        return found_titles

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
        input_words = []
        if isinstance(preprocessed_input, str):
            input_words = preprocessed_input.split()
        else:
            input_words = preprocessed_input
        self.sentiment["liked"] = "pos"
        self.sentiment["enjoyed"] = "pos"
        self.sentiment["loved"] = "pos"
        self.sentiment["disliked"] = "neg"
        self.sentiment["hated"] = "neg"
        self.sentiment["good."] = "pos"
        self.sentiment["great."] = "pos"
        self.sentiment["amazing."] = "pos"
        self.sentiment["alright."] = "pos"
        self.sentiment["bad."] = "neg"
        self.sentiment["horrible."] = "neg"
        self.sentiment["terrible."] = "neg"
        self.sentiment["awful."] = "neg"
        total_sentiment = 0

        for word in input_words:
            if "didn't" in input_words or "not" in input_words or "never" in input_words or "nothing" in input_words or "neither" in input_words:
                if word in self.sentiment:
                    if self.sentiment[word] == "pos":
                        total_sentiment -= 1
                    else:
                        total_sentiment += 1
            else:
                if word in self.sentiment:
                    if self.sentiment[word] == "pos":
                        total_sentiment += 1
                    else:
                        total_sentiment -= 1
        
        final_sentiment = 0
        if (total_sentiment > 0 and (("great" in input_words or "love" in input_words or "loved" in input_words or "really" in input_words or "strongly" in input_words or "amazing" in input_words or "awesome" in input_words) or ("hate" in input_words or "terrible" in input_words or "really" in input_words or "hated" in input_words or "strongly" in input_words or "horrible" in input_words))):
            final_sentiment = 2
        elif total_sentiment > 0:
            final_sentiment = 1
        elif (total_sentiment < 0 and ("hate" in input_words or "terrible" in input_words or "really" in input_words or "hated" in input_words or "strongly" in input_words or "horrible" in input_words)):
            final_sentiment = -2
        elif total_sentiment < 0:
            final_sentiment = -1
        elif total_sentiment == 0: 
            final_sentiment = 0
            
        return final_sentiment

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
        input_words = preprocessed_input.split()
        titles = re.findall('"([^"]*)"', preprocessed_input)

        #find sublists
        list_size = len(input_words)
        list_of_indexes = [idx + 1 for idx, val in enumerate(input_words) if '"' in val]
        #list_of_start_indexes = list_of_indexes[::2]
        list_of_end_indexes = list_of_indexes[1::2]

        list_of_lists = []
        previous_index = 0
        for index in list_of_end_indexes:
            new_list = input_words[previous_index:index]
            if index == list_of_indexes[-1]:
                new_list = input_words[previous_index:]
            list_of_lists.append(new_list)
            previous_index = index
        #return list_of_lists

        return_list = []
        for i, mylist in enumerate(list_of_lists):
            rating = self.extract_sentiment(mylist)
            if rating == 0:
                previous_input = return_list[i - 1]
                rating = previous_input[1]
            return_list.append(tuple((titles[i], rating)))

        return return_list

    def levenshtein_distance(string1, string2): 
        distance = 0 
        return distance

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
        # suggestion = []

        # for movie in self.titles: 
        #     dist = levenshtein_distance(title, movie[title])
        #     if dist <= 3:
        #         suggestion.append(self.titles[movie]) 

        # suggestion = nlargest(1, suggestion)

        # return suggestion

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
        return_list = []

        for candidate in candidates:
            candidate_full_details = self.titles[candidate][0]
            candidate_title = re.findall(r'([\w+\:+\s]+),* *(The|A|An)* *\(\d\d\d\d[-\d\d\d\d]*\)*$', candidate_full_details)
            candidate_title = candidate_title[0][0].strip(" ")
            candidate_year = re.findall(r'(["\w+\:+\s]+),* *(The|A|An)* *(\(\d\d\d\d[-\d\d\d\d]*\))*$', candidate_full_details)
            candidate_year = candidate_year[0][2]
            if (clarification in candidate_title) or ("(" + clarification + ")" == candidate_year):
                return_list.append(candidate)

        return return_list

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

        for row_num, row in enumerate(ratings):
            for rating_index, rating in enumerate(row):
                if (0 < rating <= threshold):
                    binarized_ratings[row_num][rating_index] = -1
                elif (rating > threshold):
                    binarized_ratings[row_num][rating_index] = 1

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
        cosine_sim = 0
    
        v1 = u / np.linalg.norm(u)
        v2 = v / np.linalg.norm(v)
    
        cosine_sim = np.dot(v1, v2)
    
        return cosine_sim 
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
        ratings_list = []

        #non_sparse_array = user_ratings[user_ratings != 0] 

        # iterate over all movies in the database -- each row of ratings_matrix -- we want a rating for every row 
        for movie_i in range(np.asarray(ratings_matrix).shape[0]): 

            rating_i = 0
            movie_rating_pair = ()

            if not all(x == 0 for x in ratings_matrix[movie_i]):

                #and for all of the movies we have the user's ratings for # for each movie, compare it to all the movies we have rated 
                for movie_j, score in enumerate(user_ratings):

                    if score != 0 and np.any(ratings_matrix[movie_j]):
                        #compute cosine between first movie row and movie that the user rated
                        cos_sim = self.similarity(ratings_matrix[movie_i], ratings_matrix[movie_j])
                        
                        #weight these cos sims by the users ratings for the movie
                        weighted_cos_sim = cos_sim*(score)

                        #add up those weights -- instead of np.sum, save some variable outside of inner for loop
                        rating_i += weighted_cos_sim

            movie_rating_pair = (rating_i, movie_i)
            #add to list of all recommendations
            ratings_list.append(movie_rating_pair)

        #sort recommendations so that it will go highest to lowest before return to use
        ratings_list = sorted(ratings_list, reverse = True)

        for pair in ratings_list: 
            if user_ratings[pair[1]] == 0:
                if len(recommendations) != k:
                    recommendations.append(pair[1])

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
        if self.creative == False:
            return """
            Hello! I'm Bud, your local movie-recommending chatbot! If you'd like to 
            have some suggestions of movies you want to watch, I can help you out!
            Just let me know a few movies you already know you like, and I'll 
            suggest some new ones for you! 
            """
        if self.creative == True:
            return """
            Yargh! It be Captain Jack Sparrow! Sailor of the seven seas and without
            a doubt the best pirate you have ever heard of. I love movies almost as
            much as I love rum, so let me know which ones you like, and I'll suggest
            some new ones for you!
            """



if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
