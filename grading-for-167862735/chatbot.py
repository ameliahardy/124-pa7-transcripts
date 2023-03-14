# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import porter_stemmer
import random  
import re

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j   
        self.titles, ratings = util.load_ratings('data/ratings.txt')

        # Load sentiment info
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.stem_sentiment_dictionary()
    
        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings)
       
        # Init global variables related to track a user's ratings in conversation
        self.count = 0
        self.user_ratings = np.zeros((len(ratings),1))  # TODO len() gets first dimension (rows) of ratings, so this should work.
        self.rated_movie_indices = []  # list of indices of movies user has rated
        
        # Init global variables to track which reccomendations we've given
        self.recommendations = []
        self.recommendations_used = []

        if not self.creative:
            # The chatbot's default name is `moviebot`.
            self.name = 'Roger'
            # Init global variables that track whether and what we're currently clarifying in the conversation
            self.clarify_sentiment_status = False
            self.titles_to_clarify = []

            self.clarify_title = False
            self.titles_to_remember = list()
            self.last_sentiment = 0 

            # Init global variables to track responses we've used so we don't reuse them
            self.positive_candidates = ["I\'m thrilled to hear you love %s as much as I do!", "That\'s so cool! I'm also a huge fan of %s.", "Really? I'm so glad to hear you like %s too!", "I\'ve been a fan of %s for years,", "Oh, I love %s as well!", "I\'m happy to know that I\'m not the only one who likes %s!", "I\'m glad to hear that you\'re a fan of %s as well!", "It\'s always nice to meet someone else who enjoys %s!", "I share your love for %s!", "I'm a fan of %s too!", "I like %s too!", "Wow, I'm actually a big fan of %s too.", "I loved %s.", "It's great to hear %s is such a good movie!"]
            self.positive_used = []

            self.negative_candidates = ["I was pretty disappointed with %s, too.", "I agree, %s didn't quite live up to the hype.", "I found %s to be a bit underwhelming, to be honest.", "I didn't like %s much either.", "I think %s is a pretty mediocre film, too.", "It's interesting to hear you didn't like %s — it's a classic in the chabot community.", "My bookclub raved about %s, but I didn't like it either."]
            self.negative_used = []

            self.ask_more_candidates = ["Are there any other movies you'd like to share your thoughts on?", "What other movies do you have reviews or ratings for?", "Can you recommend any other movies that you have thoughts about?", "What other films have caught your attention recently?", "What other movies do you have reactions to?", "Any other films you feel strongly about one way or the other?", "Do you have any other movie recommendations or critiques?", "I'm curious, are there other movies you'd like to discuss?", "What's another movie you've seen recently?", "What other movies does it remind you of?", "What's another move you have strong feelings about?"]
            self.ask_more_used = []

            self.no_more_candidates = ["I'm afraid I don't have any more recommendations for you.", "I'm all out of movie recommendations!"]
            self.no_more_used = []

            self.goodbye_candidates = ["It was really great chatting with you. Have a great rest of your day!", "Well it was delightful learning about your movie tastes. Enjoy your day!", "I hope you have a good one! It was great chatting today.","Have a good one! We should totally grab lunch or something soon."]
            self.goodbye_used = []

            self.recommend_candidates = ["I think you'd really like %s.", "Based on what you've told me, I think you would really appreciate %s.", "Hmm. I don't often recommend this one, but I think you would love %s.", "This is so funny—I think you would really love one of my favorite films, %s.", "You should check out %s. You'd really like it.", "I highly recommend you watch %s. It's so good.", "I have a movie rec for you—I think you'd love %s."]
            self.recommend_used = [] 

            self.recommend_another_candidates = ["Would you like another movie recommendation?", "Would you like another movie rec?", "I think I have another recommendation. Do you want to hear it?"]
            self.recommend_another_used = []

            self.not_sure_what_movie_candidates = ["I'm really sorry but I'm not sure what movie you're referring to. Could you elaborate?", "Hmm... I'm not sure what movie you mentioned. Could you repeat it please?", "Really sorry but I don't think I caught that. What movie are you referring to?", "Sorry but I didn't catch the movie you mentioned. What movie was that?"]
            self.not_sure_what_movie_used = []

            self.clarify_title_candidates = ["What movie were you referring to when you said %s?", "I'm not sure I caught that. What movie did you mean by %s?"]
            self.clarify_title_used = []

        else:
            self.creative_titles = []
            for title in self.titles:
                # Initialize vars
                title = title[0]
                paren = title.find("(")
                title_no_date = title[:paren]
                match = title_no_date[0:len(title_no_date ) - 1]
                match = match.lower()
                length = len(match)
                
                # Escape every "*" so regex is happy
                adjust = 0
                for i in range(length):
                    if match[i + adjust] == "*":
                        match = match[0:i + adjust] + "\\" + match[i + adjust:]
                        adjust += 1
                
                match = self.move_articles_to_front(match)

                unit = (title, title_no_date, paren, match)
                self.creative_titles.append(unit)

            # Init global variables that track whether and what we're currently clarifying in the conversation
            self.clarify_sentiment_status = False
            self.titles_to_clarify = []

            self.clarify_title = False
            self.titles_to_remember = list()
            self.last_sentiment = 0 

            self.name = "Dr. Seuss"

            # Init global variables to track responses we've used so we don't reuse them
            self.positive_candidates = ["Oh joy, oh joy, oh me oh my, To hear that you love %s, I can\'t deny! I\'m thrilled, I\'m elated, I\'m bouncing with glee, That you share the same love as me!",
                                        "My heart is aflutter, my spirits are high, To know that you love %s, oh me oh my! I\'m thrilled, I\'m delighted, I\'m tickled pink, That we share this love, don\'t you think?",
                                       "Oh happy day, oh happy day, To hear you love %s, what can I say? I\'m over the moon, I\'m floating on air, That we both have this love to share!",
                                        "Oh my, oh me, oh what a sight, To find a fan of %s so bright! That\'s so cool, that\'s so neat, I love it too, it\'s hard to beat!",
                                        "Oh what a joy, oh what a thrill, To hear %s has such an incredible skill! It\'s great, it\'s fantastic, it\'s simply divine, A movie like that, is worth every dime!",
                                        "How delightful, how splendid, To meet a fan of %s, it never ended! That\'s so cool, that\'s so keen, I\'m a fan too, it\'s like a dream!",
                                        "I\'m beaming with joy, I'm grinning with glee, To hear that %s is loved by you and me! I\'m thrilled, I\'m ecstatic, I can\'t contain, The happiness I feel, it\'s simply insane!"]
            self.positive_used = []

            self.negative_candidates = ["Oh my, oh me, what a blow, To find %s didn\'t quite glow! Disappointed, that\'s how I feel, And it sounds like your disappointment was real!",
                                        "Oh dear, oh dear, it\'s sad to say, That %s left me feeling gray! Underwhelming, that\'s the word, It didn\'t quite hit the right chord!",
                                        "Oh my, oh me, it\'s not too great, To find %s didn\'t quite rate! Underwhelming, that\'s how I found, It didn\'t quite leave me spellbound!", 
                                        "Oh my goodness, oh my dear, That %s didn\'t quite bring the cheer! Underwhelming, that\'s how it felt, It didn\'t quite make my heart melt!",
                                        "I did not fancy %s, no sirree, Not in a house, not in a tree, I did not like it, I must confess, Not in a box, not in a dress.",
                                        "I did not like %s, oh me, Not in a boat or in the sea, I did not like it on a plane, I did not like it, it's just plain."]
            self.negative_used = []

            self.ask_more_candidates = ["Pray tell, my dear, what other flicks do you have thoughts on? Any picks? Let\'s hear your thoughts, let\'s hear your voice, On other films, your heart\'s true choice.", 
                                        "And now, my friend, the time has come, To speak of other films, not just this one. Are there more tales you\'d like to tell? Of movies good, or not so well?",
                                        "What other wondrous films have caught your eye, And left you feeling like you could just fly? Have you seen a tale of love or of war, Or a comedy that left you rolling on the floor?",
                                        "Oh gracious me, what other films have you viewed, That have left you feeling completely renewed? Have you watched a drama that tugged at your heartstrings, Or a thriller that had you on the edge of your seat, like springs?"]
            
            self.ask_more_used = []

            self.no_more_candidates = ["I hate to be so so cruel, but my recommendation engine is out of fuel.", "I wish it weren't, I wish it wasn't this way, but I'm all out of movie titles, I say."]
            self.no_more_used = []

            self.goodbye_candidates = ["Oh me, oh my, it was so delightful, to talk with you about your favorite titles.", "Deary you, deary be, it was my pleasure, talking with you about cinematic treasure."]
            self.goodbye_used = []

            self.recommend_candidates = ["Oh, I've a movie that's just right for you! It's called %s, and it's worth a view!", "A movie you'll fancy, I do decree! %s, the one you should really go see!", "From what you've said, here's my prediction: %s, a movie for your satisfaction!", "From what you've said, from what I've heard, this is the one for you, even if it's a little absurd— %s."]
            self.recommend_used = [] 

            self.recommend_another_candidates = ["Would you fancy a flick suggestion, my friend? Another one to watch, and enjoy 'til the end?", "Would you like to hear another cinematic gem. perhaps?", "May I suggest another movie to view? A new adventure to enjoy, just for you!"]
            self.recommend_another_used = []

            self.not_sure_what_movie_candidates = ["Sorry, can't guess the show you mean. Could you expand on it, dear, or intervene?", "Pardon me, my memory's hazy, which movie was it, my dear daisy?", "Oh dear, my ears must be deceiving! Which movie, my friend, were you speaking?"]
            self.not_sure_what_movie_used = []

            self.clarify_title_candidates = ["When you spoke %s, which flick did you mean? Do tell me quick, I'm quite keen!", "When you spoke %s, did you mean a flick? Pray tell, which one, quick, quick, quick?"]
            self.clarify_title_used = [] 

            
        

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################    
    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
  
        ########################################################################
        # TODO: Write a short greeting message                                 #
        ########################################################################
        if self.creative:
            greeting_message = "Oh me, oh my! What wonderful day! I'm a Dr. Seuss chatbot and I would like to say: do you have a dearest flick, a cinematic pic?"
        else:
            greeting_message = "Hi there! I'm Roger, a chatbot that loves to talk about movies. What' s your favorite movie?"
        # Originally this was "How can I help you?"

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
        if self.creative:
            goodbye_message = "I'm afraid I must, thought it brings me no joy, bid you adieu, as all this was a ploy!"
        else:
            goodbye_message = "Have a nice day!"

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
        
        """
                # If we just asked to clarify the sentiment of something, we don't need to extract titles. Just retrieve them from global memory instead.
                if self.clarify_sentiment_status:
                    titles = self.titles_to_clarify
                    self.clarify_sentiment_status = False
                    
                # If we just asked to clarify bc we couldn't find a title in sentence:
                elif self.clarify_title_no_idea:
                    titles = self.titles_to_remember
                    titles = titles + self.extract_titles(line) 
                
                # If we just asked to clarify because we couldn't disambiguate a title
                elif self.clarify_title_some_idea:
                    candidate_indices = self.candidate_indices_to_disambiguate
                    old_titles = self.titles_to_remember
                    new_titles = self.extract_titles(line)
                    if new_titles == []:
                        new_titles = self.disambiguate(line, candidate_indices)
                    titles = old_titles + new_titles
                
                # If we just intended to clarify a misspelling
                elif self.spellcheck_titles:
                    titles = self.extract_titles(line)
                    if titles == []:
                        titles = self.disambiguate(line, self.possible_mispelled_titles)

                # Otherwise, extract titles. 
                else:
                    # Get a list of titles mentioned by user
                    titles = self.extract_titles(line) 

                # If we didn't successfully extract titles
                if len(titles) == 0:

                    # If we find near-titles
                    possible_mispelled_titles = self.find_movies_closest_to_title(line)
                    if possible_mispelled_titles != []:
                        self.spellcheck_titles = True
                        self.possible_mispelled_titles = possible_mispelled_titles
                        return "Which of the following did you mean %s?"

                    # If we actually found no titles at all
                    else:
                        self.clarify_title_no_idea = True
                        response = self.randomize_response(self.not_sure_what_movie_candidates, self.not_sure_what_movie_used)[0]
                        return response  

                # Get indices of titles mentioned by user 
                movie_indices = []
                for title in titles:
                    indices = self.find_movies_by_title(title)

                    # If find_movies_by_title() returned more than one title, we need to clarify which the user referred to
                    if len(indices) > 1:
                        self.clarify_title_some_idea = True # Update global boolean to reflect we're in a title-clarification stage 
                        titles.remove(title)  # Remove the questionable string so we can save everything else
                        self.titles_to_remember = titles  # Remember all non-confusing titles
                        self.last_sentiment = self.extract_sentiment_for_movies(self.remove_titles(line, titles))  # Remember the sentiment associated with all of these titles
                        
                        # Build a list of candidate titles
                        titles = []
                        for candidate in indices:
                            titles.append(self.titles[candidate][0])
                        concatenated_titles = ""
                        response = self.randomize_response(self.clarify_title_candidates, self.clarify_title_used)[0] % self.concatenate_titles(titles, concatenated_titles, False, True)
                        return response
                    
                    movie_indices.append(indices)  # Get indices of titles mentioend by user from self.title

                # Get sentiment from a line with all punctuation other than quotes stripped 
                # TODO strip punctutation other than quotes on this line before passing into extract_sentiment
                # If we were in a title clarification flow, remember the sentiment from the last line
                if self.clarify_title_some_idea or self.clarify_title_no_idea:
                    sentiments = self.last_sentiment
                    self.clarify_title_some_idea = False
                    self.clarify_title_no_idea = False

                # Otherwise, extract the sentiment from the line
                else:
                    if len(titles) == 1:
                        sentiments = [title, self.extract_sentiment(line)]
                    else:
                        sentiments = self.extract_sentiment_for_movies(line)
                        print(sentiments)
                        # If extract_sentiment_for_movies failed to find sentiment just find a blanket sentiment score
                        if sentiments == []:
                            sentiment = self.extract_sentiment(self.remove_titles(line, titles))
                            for title in titles:
                                sentiments.append((sentiment, title))

                # Handle case where we're not sure what they thought of titles and must clarify.
                # Collect cases of zero sentiment
                zero_sentiments = []
                for sentiment in sentiments:
                    if sentiment[1] == 0:
                        zero_sentiments.append(sentiment)

                # If zero sentiment, clarify sentiment
                if zero_sentiments != []:   
                    print(zero_sentiments)

                    titles = []
                    for sentiment in zero_sentiments:
                        titles.append(sentiment[1])
                    response = self.clarify_sentiment(titles) # TODO WRITE CREATIVE MODE OF THIS
                    return response
                    
                # Udates global user_ratings matrix for each move in movie_indices. Also updates global counter to reflect additions.
                self.update_ratings(movie_indices, sentiments)  # TODO WRITE CREATIVE MODE OF THIS

                # If we don't have enough data, go again
                if self.count < 5:  
                    print(titles)
                    response = self.generate_response(titles, sentiments)

                # If we do have enough data, make a recommendation 
                else:  
                    rec_indices = self.recommend(self.user_ratings, self.ratings, 10, self.creative) 
                    for index in rec_indices:
                        self.recommendations.append(self.titles[index][0])
                      # Convert the indices to strings and save it in a global variable. 
                    # TODO change above line to match the name and parameters of Brandon's function
                    response = self.generate_rec_response(True) # Generate a response that includes a rec 
                     # response = "I processed {} in starter mode!!".format(line)
        """
        ####################
        # STANDARD PROCESS #
        ####################
        self.creative = False
            # Seek more data if we don't yet have enough
        if self.count < 5:
                # If we just asked to clarify something, we don't need to extract titles. Just retrieve them from global memory instead.
                if self.clarify_sentiment_status:
                    titles = self.titles_to_clarify
                    self.clarify_sentiment_status = False
                    
                # If we just asked to clarify what title they were referring to:
                elif self.clarify_title:
                    titles = self.titles_to_remember
                    titles = titles + self.extract_titles(line) 
                    

                # Otherwise, extract titles. 
                else:
                    # Get a list of titles mentioned by user
                    titles = self.extract_titles(line) 

                    
                if len(titles) == 0:
                    response = self.randomize_response(self.not_sure_what_movie_candidates, self.not_sure_what_movie_used)[0]
                    self.clarify_title = True
                    self.titles_to_remember = []
                    self.last_sentiment = self.extract_sentiment(line)
                    return response  

                # Get indices of titles mentioned by user 
                movie_indices = []
                for title in titles:
                    indices = self.find_movies_by_title(title)

                    # If find_movies_by_title() returned more than one title, we need to clarify which the user referred to
                    if len(indices) > 1:
                        self.clarify_title = True # Update global boolean to reflect we're in a title-clarification stage 
                        titles.remove(title)  # Remove the questionable string so we can save everything else
                        self.titles_to_remember = titles  # Remember all non-confusing titles
                        self.last_sentiment = self.extract_sentiment(self.remove_titles(line, titles))  # Remember the sentiment associated with all of these titles
                        return self.randomize_response(self.clarify_title_candidates, self.clarify_title_used)[0] % title
                    
                    movie_indices.append(indices)  # Get indices of titles mentioend by user from self.title

                # Get sentiment from a line with all punctuation other than quotes stripped 
                # TODO strip punctutation other than quotes on this line before passing into extract_sentiment
                # If we were in a title clarification flow, remember the sentiment from the last line
                if self.clarify_title:
                    sentiment = self.last_sentiment
                    self.clarify_title = False

                # Otherwise, extract the sentiment from the line
                else:
                    sentiment = self.extract_sentiment(self.remove_titles(line, titles))

                # Handle case where we're not sure what they thought of titles and must clarify.
                if sentiment == 0:
                    response = self.clarify_sentiment(titles)
                    return response
                    
                # Udates global user_ratings matrix for each move in movie_indices. Also updates global counter to reflect additions.
                self.update_ratings(movie_indices, sentiment)  

                # If we don't have enough data, go again
                if self.count < 5:  
                    response = self.generate_response(titles, sentiment)

                # If we do have enough data, make a recommendation 
                else:  
                    rec_indices = self.recommend(self.user_ratings, self.ratings, 10, self.creative) 
                    for index in rec_indices:
                        self.recommendations.append(self.titles[index][0])
                      # Convert the indices to strings and save it in a global variable. 
                    # TODO change above line to match the name and parameters of Brandon's function
                    response = self.generate_rec_response(True) # Generate a response that includes a rec 
                     # response = "I processed {} in starter mode!!".format(line)
            
            # If count is at least 5, we're already in reccomendation mode and have already recommended something. So, our anticipated inputs are different.
        else:
                line = line.lower()
                line = line.split(" ")
                if "yes" in line or "yeah" in line or "yes." in line or "yeah." in line or "yep" in line or "yep." in line:
                    response = self.generate_rec_response(True)
                else:
                    response = self.generate_rec_response(False)
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
    

    def clarify_sentiment(self, titles):
        # Set globals to reflect we will now try to clarify user sentiment about tiles
        self.clarify_sentiment_status = True
        self.titles_to_clarify = titles 
       
        # Build response that seeks clarification 
        movies = ""
        movies = self.concatenate_titles(titles, movies, 1, False)
        movies = movies[:len(movies) - 1] # Remove last movie end quote so we can put a period before it
        response = 'Hmm. I\'m not sure exactly what you thought of %s." Tell me a little more about what ' % movies
        #TODO make this more random

        # Handle plural vs. singular 
        if len(titles) == 1:
            response += "it "
        else:
            response += "they "

        response += "made you feel."

        return response
    

    def concatenate_titles(self, titles, response, sentiment, question):
        """ Helper function for generate_response(). Concatenates a list of titles with the necessary quotes, commas, and "and"s. """
        num_titles = len(titles)
        for i in range(num_titles):
            if num_titles > 1:
                if num_titles > 2 and i > 0:  # If we're handling a list of more than two titles, add a comma to each title except the last one 
                    response += ","
                if i == num_titles - 1:  # If we've reached the last title, add an "and" before appending
                    if sentiment == 1:
                        if question:
                            response += " or"
                        else:
                            response += " and"
                    else:
                        response += " or"
            if i > 0:
                response += ' "' + titles[i] + '"' 
            else:
                response += '"' + titles[i] + '"' 
        return response
    

    def generate_response(self, titles, sentiment):
        """Generates a response to a user's opinion about a movie. Assumes self.count < 5 so we should 
        try to ingest more data. Assumes sentiment is not 0. """
        # STANDARD MODE #
        if not self.creative:
            # Choose a grounding statement
            if sentiment == 1:
                basic = self.randomize_response(self.positive_candidates, self.positive_used)[0]
            else: 
                basic = self.randomize_response(self.negative_candidates, self.positive_used)[0]
            
            # Piece together response
            movies = ""
            movies = self.concatenate_titles(titles, movies, sentiment, False) 
         
            response = basic % movies
            response += " "

            # Ask for more movies
            response += self.randomize_response(self.ask_more_candidates, self.ask_more_used)[0]
            return response
        
        # CREATIVE MODE # 
        else:
            response = ""

            # Loop through list of tuples of structure ("title", sentiment)
            for movie_titles, sent in sentiment:
                if sent > 0:
                    unit = self.randomize_response(self.positive_candidates, self.positive_used)[0]
                else:
                    unit = self.randomize_response(self.negative_candidates, self.negative_used)[0]
                unit = unit % movie_titles
                response += unit + " " 
            
            # Add an ask more question at the end
            response += self.randomize_response(self.ask_more_candidates, self.ask_more_used)[0]
            return response


    def generate_rec_response(self, more):
        """Generates one of two types of responses. IF more == True, returns a natural language response providing one more reccomendation and then asks if the user would like another.
        If more == False, says bye."""
        # If user wants a reccomendation
        if more and len(self.recommendations) - len(self.recommendations_used) > 0:
            movie, exhausted = self.randomize_response(self.recommendations, self.recommendations_used)
            response = self.randomize_response(self.recommend_candidates, self.recommend_used)[0] % movie
            if not exhausted:
                response += " " + self.randomize_response(self.recommend_another_candidates, self.recommend_another_used)[0]
            else:
                response += self.randomize_response(self.goodbye_candidates, self.goodbye_used)[0]
        
        # User said yes but we don't have any more reviews
        elif len(self.recommendations) - len(self.recommendations_used) == 0:
            response = self.randomize_response(self.no_more_candidates, self.no_more_used)
            response += self.randomize_response(self.goodbye_candidates, self.goodbye_used)[0]
           
        # If the user wants no more recs, we say bye 
        else:
            response = self.randomize_response(self.goodbye_candidates, self.goodbye_used)[0]
        
        return response 


    def randomize_response(self, candidates, candidates_used):
        """For a given list of candidate responses, chooses and returns 1 randomly."""
        # Find an unused candidate
        local_candidates = list(set(candidates) - set(candidates_used))
        candidate = local_candidates[random.randrange(0, len(local_candidates))]
        
        # Updates used list
        candidates_used.append(candidate)
        
        # Init exhausted
        exhausted = False

        # If we've used all candidates
        if len(candidates_used) == len(candidates):

            # If the candidates in question are recommendations, we don't just want to pull from them again. Instead, update exhausted.
            if candidates == self.recommendations:
                exhausted = True

            # Otherwise, remove all candidates but the selected one from candidates_used. I couldn't just say candidates_used = [candidate] because of python's rules on global variables 
            else:
                for can in candidates:
                    candidates_used.remove(can)
                candidates_used.append(candidate)

        return candidate, exhausted

    

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
        if self.creative:
            candidates = []
            self.creative = False
            out = self.extract_titles(preprocessed_input)
            self.creative = True
            candidates += out
            
            line = preprocessed_input.lower()

            for title, title_no_date, paren, match in self.creative_titles:
                # If match is in the line, add it to the list of candidates
                if title_no_date != "" and (len(re.findall(" " + match + "[\s.,\!]", line)) != 0 or len(re.findall(" " + match + "$", line)) != 0 or len(re.findall("^" + match+ "[\s\.,\!]", line)) != 0 or len(re.findall("^" + match+ "$", line)) != 0):
                    if line.find(title_no_date + title[paren:]) != -1:
                        candidates.append(title)
                    else:
                        candidates.append(title_no_date[0:len(title_no_date) - 1])
            
            # Remove all candidates that are subsets of other candidates
            out = candidates
            for title1 in candidates:
                for title2 in candidates:
                    if title1 != title2 and title1 in title2:
                        out.remove(title1)
            
            return out
        
        else: 
            titles = []
            last = 0
            while preprocessed_input.find('"', last) != -1:
                start = preprocessed_input.find('"', last)
                end = preprocessed_input.find('"', start + 1)
                if end != -1:
                    titles.append(preprocessed_input[start + 1:end])
                    last = end + 1
                else:
                    return titles
            return titles


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
        indices = []
        
        title_length = len(title)
        title = self.move_articles(title)
        length = len(self.titles) #self.titles[0] looks like ['Toy Story (1995)', 'Adventure|Animation|Children|Comedy|Fantasy']
        paren_location = title.find("(")

        input_paren = 0
        for char in title:
            if char == '(' or char == ')':
                input_paren += 1

        if self.creative:
            for i in range(length):
                # DISAMBIGUATION PART 1
                print(title)
                print(paren_location)
                if paren_location != -1 and title[paren_location + 1].isnumeric():
                    # year specified, search for title no edits
                    finder = (self.titles[i][0].lower()).find(title.lower()) # handles any capitalization
                    if finder != -1:
                        indices.append(i)
                else:
                    # if there isn't a year specified, search for title with additional space or colon
                    finder = (self.titles[i][0].lower()).find(title.lower() + " ") # handles any capitalization
                    if finder == -1:
                        finder = (self.titles[i][0].lower()).find(title.lower() + ":")
                        if finder != -1:
                            indices.append(i)
                    else:
                        indices.append(i)
        
            # HANDLE ALTERNATE AND FOREIGN
            if len(indices) == 0:
                count_paren = 0

                # BOTH year and alias
                if input_paren == 4:
                    preaka_paren_index = title.find('(')
                    postaka_paren_index = title.find(')')
                    title = title[:preaka_paren_index] + "(a.k.a. " + title[preaka_paren_index + 1:] #+ title[postaka_paren_index:]


                # JUST "ALT (YEAR)" or "MOVIE (ALT)"
                if input_paren == 2:
                    openparen_index = title.find('(')
                    closeparen_index = title.find(')')
                    if title[openparen_index + 1].isnumeric(): # its a "alt (year)"
                        title = title[:openparen_index - 1] + ") " + title[openparen_index:]
                    elif not title[openparen_index + 1].isnumeric(): # its a "movie (alt)"
                        title = title[:openparen_index] + "(a.k.a. " + title[openparen_index + 1:]

                # calc # of paren for all movies, if == 4 then there is an alternative or foreign language
                for i in range(length):
                    for char in self.titles[i][0].lower():
                        if char == '(' or char == ')':
                            count_paren += 1

                    if count_paren == 4:
                        # search
                        finder = (self.titles[i][0].lower()).find(title.lower())
                        if finder != -1:
                            indices.append(i)
                        
                        """
                        TODO implement case for "MOVIE (YEAR)"
                        else: # movie (year)
                            altforeignopen_index = self.titles[i][0].find('(')
                            altforeignclose_index = self.titles[i][0].find(')')
                            alt_foreign = self.titles[i][0][altforeignopen_index + 1 : altforeignclose_index]

                            alt_foreign_omitted = self.titles[i][0][:altforeignopen_index - 1] + self.titles[i][0][altforeignclose_index + 1:]

                            finder = (alt_foreign_omitted.lower()).find(title.lower())
                            if finder != -1:
                                indices.append(i)
                        """
                
                    count_paren = 0


        else:
            for i in range(length):
                finder = (self.titles[i][0]).find(title)
                if finder != -1:
                    indices.append(i)

        return indices
    

    def move_articles(self, title):
        title_as_list = title.split(" ")

        article_present = False

        # Transform title to move preposition ("an", "a", "the")
        if title_as_list[0] == "The" or title_as_list[0] == "An" or title_as_list[0] == "A":
            title = (title.replace(title_as_list[0], '')).strip() # removes whitespace that replaced article will create when using replace() in prev line
            article_present = True

        # Determine whether movie title already has parens
        paren_location = title.find("(")
        
        
        if article_present:
            # If parens exist, add article before the parens
            if paren_location != -1:
                title = title[:paren_location - 1] + ", " + title_as_list[0] + " " + title[paren_location:]
        
            # If not, just add the article at the end
            else: 
                title = title + ", " + title_as_list[0]

        # If there are no parens, add a paren
        if paren_location == -1 and not self.creative:
            title += " ("

        return title
    

    def move_articles_to_front(self, title):
        """Moves articles to front if there is an article is in the title. If no article, returns title unchanged. """
        if ", the" in title.lower() or ", an" in title.lower() or ", a" in title.lower():
            comma = title.find(",")
            title = title[comma + 2:] + " " + title[0:comma]
        return title
    

    def remove_titles(self, line, titles):
         # Remove titles from line
        processed_line = ""
        last = 0
        for title in titles:
            start = line.find(title)

            # If the movies we've asserted are in line aren't in line, it's because we asked the user for a sentiment clarification. In this case, we're happy with the raw line
            if start == -1:
                return line
            processed_line += line[last:start]
            line = line[start + len(title):]
        processed_line += line
        
        return processed_line
    

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
        if self.creative:
                 # TODO: Failing on "I don't know what I think of "Tenet"" (getting -1)
             # Initialize variables
             score = 0
             flip = 1
             negation_words = ["not", "didn't", "never", "don't", "neither", "nor", "isn't", "wasn't", "no"]
             filler_words = ["a", "of", "or", "the", "it", "an"]
             modifier_words = ["pretty", "prettty", "very", "really", "reaally", "so", "soo", "extremely", "slightly", "big", "small", "my", "his", "her", "bit", "their", "such"]
             super_positive_words_unstemmed = ["great", "loved", "fantastic", "amazing", "incredible", "wonderful"]
             super_negative_words_unstemmed = ["awful", "horrible", "terrible", "atrocious"]
             p = porter_stemmer.PorterStemmer()

             super_positive_words = self.stem_list(super_positive_words_unstemmed)
             super_negative_words = self.stem_list(super_negative_words_unstemmed)


             # Init remaining variables
             preprocessed_input = self.strip_punctuation(preprocessed_input)
             words = preprocessed_input.split(" ") 
             length = len(words)

             # Loop through every word in line 
             for i in range(length):
                 if p.stem(words[i]) in self.sentiment:
                     flip = 1
                     # Handle Negation and Fillers
                     cur = i -1
                     while i >= 0 and (words[cur] in modifier_words or words[cur] in filler_words):
                         if words[cur] in modifier_words:
                             flip += 1
                         cur -=1


                     if words[cur] in negation_words:
                         flip *= -1
                     else:
                         flip *= 1 

                     # Add score to scores
                     if self.sentiment[p.stem(words[i])] == "pos":
                         if p.stem(words[i]) in super_positive_words:
                             score += 2 * flip
                         else:
                             score += (1 * flip)
                     else: 
                         if p.stem(words[i]) in super_negative_words:
                             score -= 2 * flip
                         else:
                             score -= (1 * flip)

             # Process raw score
             if score >=2:
                 return 2
             elif score > 0 and score < 2:
                 return 1
             elif score == 0:
                 return 0
             elif score < 0 and score > -2:
                 return -1
             else:
                 return -2
        else:
        # TODO: Failing on "I don't know what I think of "Tenet"" (getting -1)
        # Initialize variables
            score = 0
            flip = 1
            negation_words = ["not", "didn't", "never", "don't", "neither", "nor", "isn't", "wasn't", "no"]
            filler_words = ["a", "of", "or" "so", "the", "it", "an"]
            modifier_words = ["pretty", "very", "really", "so", "extremely", "slightly", "big", "small", "my", "his", "her", "bit", "their"]
            p = porter_stemmer.PorterStemmer()

            # Init remaining variables
            words = preprocessed_input.split(" ") 
            length = len(words)
            
            # Loop through every word in line 
            for i in range(length):
                if p.stem(words[i]) in self.sentiment:
                    # Handle Negation and Fillers
                    cur = i -1
                    while i >= 0 and (words[cur] in modifier_words or words[cur] in filler_words):
                        cur -=1


                    if words[cur] in negation_words:
                        flip = -1
                    else:
                        flip = 1 

                    # Add score to scores
                    if self.sentiment[p.stem(words[i])] == "pos":
                        score += (1 * flip)
                    else: 
                        score -= (1 * flip)

            # Process raw score
            if score > 0:
                return 1
            elif score == 0:
                return 0
            else:
                return -1
        
    def strip_punctuation(self, line):
         line = line.replace(".", "")
         line = line.replace(",", "")
         line = line.replace("!", "")
         line = line.replace(";", "")
         line = line.replace(":", "")
         return line 

    def stem_list(self, input):
         out = []
         p = porter_stemmer.PorterStemmer() 
         for element in input:
             out.append(p.stem(element))

         return out 

    def stem_sentiment_dictionary(self):
        """ Stems every key in sentiment dictionary to enable better sentiment detection"""
        p = porter_stemmer.PorterStemmer()
        for word in list(self.sentiment):
            value = self.sentiment.pop(word)
            self.sentiment[p.stem(word)] = value


    def update_ratings(self, movie_indices, sentiment):
        """Updates global user_ratings array with the user's opinion on movies mentioned in a given line"""
        if not self.creative:
            self.count += len(movie_indices)  # Update global count to reflect that we're adding n movies to the user_ratings
            for movie_index in movie_indices:
                self.user_ratings[movie_index, 0] = sentiment  # Change element from 0 to sentiment in array of length M
                self.rated_movie_indices.append(movie_index)
        else:
            self.count += len(movie_indices)
            for i in range(len(movie_indices)):
                #movie_index = self.find_movies_by_title(movie_name[0])
                self.user_ratings[movie_indices[i], 0] = sentiment[i]
                self.rated_movie_indices.append(movie_index)


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
        words = preprocessed_input.split(" ") 
        titles = self.extract_titles(preprocessed_input)
        conjuction_words = ["and", "or", "but", "nor", "yet"]
        
        if any(item in conjuction_words for item in words) == False and len(titles) == 1:
            sentiment = self.extract_sentiment(preprocessed_input)
            sentiment = [(titles[0], sentiment)]
        elif len(titles) > 1:
            #Split sentence at conjuction to get sentiment of both halves
            sentence_halves = []
            found_conjuction = ""
            for conjuction in conjuction_words:
                if conjuction in words:
                    sentence_halves = preprocessed_input.split(conjuction)
                    found_conjuction = conjuction

            sentiment_one = self.extract_sentiment(sentence_halves[0])
            sentiment_two = self.extract_sentiment(sentence_halves[1])

             #Checking cases where one sentiment is unclear or 0
            if sentiment_one == 0 and sentiment_two != 0:
                if found_conjuction == "but":
                    sentiment_one = -sentiment_two
                else:
                    sentiment_one = sentiment_two

            elif sentiment_one != 0 and sentiment_two == 0:
                if found_conjuction == "but":
                    sentiment_two = -sentiment_one
                else:
                    sentiment_two = sentiment_one   
            sentiment = [(titles[0], sentiment_one), (titles[1], sentiment_two)] 
        else: 
            sentiment = self.extract_titles(preprocessed_input)

        return sentiment          


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
        min_candidate = 100000
        candidate_title = []
        for i in range(len(self.titles)):
            target = self.titles[i][0].lower()
            if title.find("(") == -1:
                paren = target.find("(")
                target = target[:paren - 1]
            dist = self.get_minimum_distance(title.lower(), target)
            
            if dist <= max_distance and dist < min_candidate:
                min_candidate = dist
                candidate_title = [i]
                
            elif dist == min_candidate and dist <= max_distance:
                candidate_title.append(i)
            else:
                pass

        return candidate_title


    def get_minimum_distance(self, source, target):
        n = len(source)
        m = len(target)
        d = np.zeros((n+1, m+1))
        
        
        for i in range(1, n + 1):
            d[i, 0] = d[i-1, 0] + 1
        
        for j in range(1, m + 1):
            d[0, j] = d[0, j - 1] + 1

        for i in range(1, n + 1): 
            for j in range(1, m + 1):
                a = d[i - 1, j] + 1
                b = d[i - 1, j - 1] + self.sub_cost(source[i - 1], target[j - 1])
                c = d[i, j - 1] + 1
                
                min = self.minimum(a, b, c)
                d[i, j] = min
        return d[n, m]
    

    def sub_cost(self, i, j):
        if i.lower() == j.lower():
            return 0
        return 2
    

    def minimum(self, a, b, c):
        if a <= b:
            if a < c:
                return a
            return c
        return b
    

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
        place_to_index = {"first": 0, "1st": 0, "1": 0, "former":0 , "latter":1, "second": 1, "2nd": 1, "2": 1, "third": 2, "3rd": 2, "3": 2, "fourth": 3, "4th": 3, "4":4, "fifth": 4, "5th": 4, "5":5}
        returned_candidates = []

        for word in place_to_index:
            if word in clarification.lower():
                returned_candidates.append(candidates[place_to_index[word]])

        if len(returned_candidates) == 0:
            for candidate in candidates:
                if clarification.lower() in self.titles[candidate][0].lower():
                    returned_candidates.append(candidate)
            
        return returned_candidates

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

        ### NOT SURE IF THIS WORKS YET ###
        binarized_ratings = np.zeros_like(ratings)
        binarize_func = lambda t : 1 if t > threshold else -1 if t > 0.5 else 0
        binarize_vec = np.vectorize(binarize_func)
        binarized_ratings = binarize_vec(ratings)

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
        numerator = np.dot(u, v)
        denominator = ((np.dot(u, u))** (1/2)) * ((np.dot(v, v))** (1/2))
        
        if denominator == 0:
            denominator = 1
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return numerator / denominator


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
        local_rated_movie_indices = []

        # doing this because sanity check is not updating a global user_ratings, so we localize here
        self.user_ratings = user_ratings
        
        # since our implementation depends on global self.rated_movie_indices, which is created in update_ratings(), in order to pass sanity, which doesn't call update_ratings, we need to do this locally
        for i in range(np.shape(user_ratings)[0]):
            if user_ratings[i] == 1 or user_ratings[i] == -1:
                local_rated_movie_indices.append(i)
        

        # loop through all movies
        for i in range(np.shape(ratings_matrix)[0]):
            # make sure we don't calc ranking for movie we have user rating for
            if i not in local_rated_movie_indices:
                synthetic_ranking = 0
                # loop through user's ranked movies (Ri)
                for index in local_rated_movie_indices:
                    synthetic_ranking += self.user_ratings[index] * self.similarity(ratings_matrix[i], ratings_matrix[index])
                
                self.user_ratings[i] = synthetic_ranking
        
        # Set all user-ranked movies to very low number so they aren't selected
        for index in local_rated_movie_indices: 
            self.user_ratings[index] = -1000
        
        rec_indices = []
        # Select top K indices with highest synthetic_ranking and return
        for n in range(k):
            index = np.argmax(self.user_ratings)
        
            self.user_ratings[index] = -10
            rec_indices.append(index)
    
        return rec_indices


        # Get maximum k values from user_ratings 

        
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
        if self.creative:
            message = "Below is an experimental Dr. Seuss chatbot. It understands movie titles in quotes, but you'll probably have to work a bit to understand its responses. That's the joy of Dr. Seuss!"
        else:
            message = "Below is a standard chatbot. Be sure to include movie titles in quotes"
        return message


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, ' 'run:')
    print('    python3 repl.py')
    roger = Chatbot(True)
    print(roger.find_movies_by_title("Scream"))