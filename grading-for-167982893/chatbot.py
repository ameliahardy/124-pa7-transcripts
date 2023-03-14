# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import re
import porter_stemmer
p = porter_stemmer.PorterStemmer()
import numpy as np
import random


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""
    def __init__(self, creative=True):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'krash <3'
        self.creative = creative
        self.data_points = []
        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.more_recs = False
        self.need_to_disambiguate = False
        self.movies_to_disambiguate = []
        self.temp_line = ""
        self.reccs = []
        self.idx = 0

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = ratings
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

        greeting_message = "heyyyy bae :P i'm krash <3 (kieran, regina, ari, & sexy helena). i love 2 watch movies, and i love to help my friends find movies 2 watch !! so, let's find some movie recs 4 u shall we? tell me about a movie u've liked or didn't like!"

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

        goodbye_message = "noooo don't leave :(((((. jk hehe i had so much fun talking to u! cant wait 2 see u next time :). TTYLXOX"

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
        ########################################################################\
        title = ""
        list_arbitrary = ["hmmmmm. that's a littttttle off topic tbh. so, tell me about a movie u like or don't like?", "ummmmmmmm awk. i didnt get that. can u try again? tell me about a movie you liked or didnt like.", "sry girlie pop that totes cool but idk about that :/ can u tell me more abt ur fav movies :()", "LOL wait i'm confused :/ let's talk about movies. can u tell me about a movie u like or don't like?"]
        list_disambiguate = [("woahhhhh! i know more than one movie that matches the title", "like all of these:", "can u clarify which one u mean and if u liked it?"), ("that's cray!!! i found more than one movie named ", ":0 these are all of them: ", "can u tell me which 1 u mean and if u like it :D"), ("thank u for the input slaybot :] i know maaany movies called ", ". which of these movies did u mean luver :{}?? ", " andddd did u like it??"), ("oh em gee :[] i found 2 many with the title ", "!!! which 1 of these did u mean: ", "and lmk if u like it baee")]
        # list_generate_titles = []
        list_unknown_movie = [("yikes. is that a new one? i've never heard of ", "! can you tell me about another movie?"), ("hmmmmm im not sure ik ", " :/ can u b more specific bae or tell me ant a new movie"), ("OMG im so silly!! wuts ", "? ive never heard of it b4 ;'( can we talk abt a dif movie pls???")]
        # list_multiple_movies = [MULTIPLE MOVES IN CREATIVE]
        list_too_many_movies = ["ummmmmmmm awk. too many movies to keep track of! can u try again? tell me about ONE movie u liked or didnt like.", "wo0000ah!!! thats 2 many movies 4 me :0. can u tell me abt 1 movie u like or h8", "oh em gee im confused :/ can we talk abt 1 movie at a time and if u liked it or h8ed it!!!"]
        list_positive_sent = [("o.m.g. i <3 ", " 2! thanks for the info, bae."), ("r u serious?!?!?! i luv ", " sm <33333 ty for the info slayer ") , ("thats cray bc ", " is literally my fav movie ever!!! great minds think alike mamas :0. ty for the info")]           
        list_negative_sent = [("u don't have 2 tell me twice ... tbh i didn't really like ", " either :/ low key flopped."), ("noted. if im being so real... i didn't like ", " either."), ("so valid of u queen. i totessssss agree that ", " was NOT it."), ("tbh my myspace moots posted the samzies about ", ", thats cray. i see u, and i hear u. ty for lmk <3")]
        list_clarify_sentiment = [("so, i hear that u watched ", " but... did u like it??? that's the real question! can u pls tell me again which movie andddd if u liked it?"), ("im totes confused rn! the movie ", "... did u like it or not?!?!?"), ("good news, bad news...i get what movie u mean. its ", " right? but idk if you like it or not :0. can u clarify wht movie it was and if u luved it!!!")]
        list_elicit_responses = ["this is gr8 intel! tell me about another movie u've liked or didn't like", "logged. let's keep going ;) tell me another movie if u loved or not.", "i so get u. tell me another movie and if u liked it or not!", "yaaasssssss. that's so slay. thx for letting me know bae. time 4 another one! tell me another movie u liked luver"]
        list_disam_mult = ["lolz thats 222 many movies 444 me :( can u try giving me telling me if u liked or h8ed a more specific title?!?! <33333", "omg that's cray i cant keep track of all these movies!!! can u try giving me telling me if u liked or h8ed a more specific title?!?! <33333"]
         
        # creative mode
        if self.creative:
            response = "I processed {} in creative mode!!".format(line)
            exact_title = ""
            if self.more_recs:
                if line == "YES":
                    self.idx += 1
                    if self.idx == 5:
                        self.more_recs = False
                        response = "oopsie! im gonna need some more info b4 i can give u another rec :'). tell me abt another movie u liked or didnt like"
                        self.data_points = []
                        self.idx = 0
                    else:
                        response = "lets get u another rec!! i think ur gonna like this one baeeee. its called "
                        movie = self.titles[self.reccs[self.idx]][0]
                        response += movie
                        response += " just like before, type YES if u want another rec <33333. type NO if ur done hehe"
                if line == "NO":
                    response = "thats ok bae!! thx 4 hanging out w me :)))). u can leave using :quit and enjoy the rest of ur day!!!"
                    self.data_points = []
                    self.idx = 0
                    self.more_recs = False 
                else:
                    result = "ummm das not what i asked u girl lmao... do u want more reccs?? " 
                    result += "type YES or NO :))))"
                    return result
            
            
            elif len(self.data_points) < 5:
                titlez = []
                if self.need_to_disambiguate:
                    #chatbot.disambiguate("1997", [1359, 2716]) should return [1359]  
                    indexes = self.disambiguate(line, self.movies_to_disambiguate)
                    print(indexes)
                    if len(indexes) == 0:
                        return "waittt... that's not one of the options! can you try clarifying which one of those movies again? thank uu :)"
                    titlez = [self.titles[idx][0] for idx in indexes]
                    if len(indexes) == 1:
                        self.movies_to_disambiguate = []
                        self.need_to_disambiguate = False
                        exact_title = titlez[0]
                        print("yay!! got your clarification. u want: ", exact_title)
                        line = self.temp_line
                    elif len(titlez) > 1:
                        self.need_to_disambiguate = True
                        self.movies_to_disambiguate = indexes
                        rand_index = random.randrange(0, len(list_disambiguate))
                        response = "ur clarification narrows it down to these titles: "
                        for i in range(len(indexes)):
                            response += self.titles[indexes[i]][0]
                            if i != len(indexes) - 1:
                                response += ", "
                            else:
                                response += ". \n"
                        response += "can u b a lillllll bit more specific pretty plz? <3"
                        return response
                else:
                    titlez = self.extract_titles(line)
                    self.temp_line = line
                # if we found no titles, raise error
                if len(titlez) == 0:
                    rand_index = random.randrange(0, len(list_arbitrary))
                    response = list_arbitrary[rand_index - 1]
                    return response
                
                for title in titlez:
                    movies = self.find_movies_by_title(title)
                    # if a title given does not match any of our movies
                    if len(movies) < 1:
                        rand_index = random.randrange(0, len(list_unknown_movie))
                        response = list_unknown_movie[rand_index - 1][0] + title 
                        response += list_unknown_movie[rand_index - 1][1]
                        return response

                    # if matches too many titles
                    if len(titlez) == 1 and len(movies) > 1:
                        # I liked "Twilight" -> would disambiguate
                        # I liked "Twilight" and "Cars" -> would NOT disambiguate
                        self.need_to_disambiguate = True
                        self.movies_to_disambiguate = movies
                        rand_index = random.randrange(0, len(list_disambiguate))
                        response = list_disambiguate[rand_index - 1][0] + title 
                        response += list_disambiguate[rand_index - 1][1]
                        for i in range(len(movies)):
                            response += self.titles[movies[i]][0]
                            if i != len(movies) - 1:
                                response += ", "
                            else:
                                response += ". \n"
                        response += list_disambiguate[rand_index - 1][2]
                        return response
                    
                    elif len(movies) > 1:
                        # too many movies, too much info
                        rand_index = random.randrange(0, 2)
                        if rand_index == 1:
                            response = title + " is not specific enfuff :((( can u try giving me the whole title or year and if u liked it or not :()"
                        else:
                            response = "there's a lot of titles close to " + title + ":[] can u give me the WHOLE title or its year &&& if u luved it or not?!?!?!"
                        return response


                sentis = self.extract_sentiment_for_movies(self.temp_line)
                print("made it to checkpoint, sentis are: ", sentis)
                sentis_clean = []

                for i in range(len(sentis)):
                    tple = sentis[i]
                    if exact_title == "":
                        exact_title = tple[0]
                    idx = self.find_movies_by_title(exact_title)[0]
                    senti = tple[1]
                    sentis_clean.append((idx, senti))
                    
                    if i == 0:
                        response = "mmmmmm. i hear that you "
                    if senti == 0:
                        rand_index = random.randrange(0, len(list_clarify_sentiment))
                        response = list_clarify_sentiment[rand_index - 1][0] + title 
                        response += list_clarify_sentiment[rand_index - 1][1]
                        return response
                    else:
                        if senti == 1:
                            response += "loved " + title 
                        elif senti == -1:
                            response += "did not luv " + title
                        if i != len(sentis) - 1:
                            response += ", "
                        else:
                            response += ". "

                self.data_points += sentis_clean
                if len(self.data_points) >= 5:
                    response += " amazing. it seems we have enough movies to find u a recommendation!!!"
                    response += " let's work some magic now ;) *magic sounds* here is your recommendation: "
                    user_ratings = self.make_user_ratings(self.data_points)
                    self.reccs = self.recommend(user_ratings, self.ratings, k=5, creative=False)
                    response += self.titles[self.reccs[0]][0]
                    response += " hope u like it babe!! let me know if u want more recs and ill give u more ;)))). type YES if u want more. if ur #done and #overit & dont want more recs thats totes ok :p! type NO"
                    self.more_recs = True
                else:
                    response += "this is gr8 intel! i need a bit moreeee. tell me about other movies u've liked or didn't like"


        # starter mode
        else:
            if self.more_recs:
                if line == "YES":
                    self.idx += 1
                    if self.idx == 5:
                        self.more_recs = False
                        response = "oopsie! im gonna need some more info b4 i can give u another rec :'). tell me abt another movie u liked or didnt like"
                        self.data_points = []
                        self.idx = 0
                    else:
                        response = "lets get u another rec!! i think ur gonna like this one baeeee. its called "
                        movie = self.titles[self.reccs[self.idx]][0]
                        response += movie
                        response += " just like before, type YES if u want another rec <33333. type NO if ur done hehe"
                if line == "NO":
                    response = "thats ok bae!! thx 4 hanging out w me :)))). u can leave using :quit and enjoy the rest of ur day!!!"
                    self.data_points = []
                    self.idx = 0
                    self.more_recs = False       
            elif len(self.data_points) < 5:
                titlez = self.extract_titles(line)
                if len(titlez) == 0:
                    rand_index = random.randrange(0, len(list_arbitrary))
                    response = list_arbitrary[rand_index - 1]
                    return response
                elif len(titlez) > 1:
                    rand_index = random.randrange(0, len(list_too_many_movies))
                    response = list_too_many_movies[rand_index - 1]
                    return response
                title = titlez[0]
                movies = self.find_movies_by_title(title)
                if len(movies) == 0: 
                    # ADD TITLE
                    rand_index = random.randrange(0, len(list_unknown_movie))
                    response = list_unknown_movie[rand_index - 1][0] + title + list_unknown_movie[rand_index - 1][1]
                    return response
                elif len(movies) > 1: 
                    rand_index = random.randrange(0, len(list_disambiguate))
                    response = list_disambiguate[rand_index - 1][0] + title + list_disambiguate[rand_index - 1][1]
                    for i in range(len(movies)):
                        response += self.titles[movies[i]][0]
                        if i != len(movies) - 1:
                            response += ", "
                        else:
                            response += ". \n"
                    response += list_disambiguate[rand_index - 1][2]
                    return response

                movie = movies[0]
                senti = self.extract_sentiment(line)
                if senti == 0:
                    rand_index = random.randrange(0, len(list_clarify_sentiment))
                    response = list_clarify_sentiment[rand_index - 1][0] + title + list_clarify_sentiment[rand_index - 1][1]
                    return response
                elif senti == 1:
                    rand_index = random.randrange(0, len(list_positive_sent))
                    response = list_positive_sent[rand_index - 1][0] + title + list_positive_sent[rand_index - 1][1]
                elif senti == -1:
                    rand_index = random.randrange(0, len(list_negative_sent))
                    response = list_negative_sent[rand_index - 1][0] + title + list_negative_sent[rand_index - 1][1]
                self.data_points.append((movie, senti))
                if len(self.data_points) == 5:
                    response += " amazing. it seems we have enough movies to find u a recommendation!!!"
                    response += " let's work some magic now ;) *magic sounds* here is your recommendation: "
                    user_ratings = self.make_user_ratings(self.data_points)
                    self.reccs = self.recommend(user_ratings, self.ratings, k=5, creative=False)
                    response += self.titles[self.reccs[0]][0]
                    response += " hope u like it babe!! let me know if u want more recs and ill give u more ;)))). type YES if u want more. if ur #done and #overit & dont want more recs thats totes ok :p! type NO"
                    self.more_recs = True
                else:
                    response += " this is gr8 intel! tell me about another movie u've liked or didn't like"
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
    
    # PARAMS:
    # words is a list with all the words in this potential movie
    def match_exact_title(self, words_notlow):
        #print('THIS IS THE WORD: ', words_notlow)
        # If title starts with article, remove it!
        articles = ["the", "a", "an"]
        words = [word.lower() for word in words_notlow]
        first_word = words[0]
        last_word = words[len(words) - 1]
        title_withyear = ""
        title_noyear = ""
        
        if first_word in articles:
            if ')' in last_word:
                # move the article to the second to last word 
                # aka "the notebook (2004)" -> "notebook, the (2004)"
                updated_words = words[1:len(words) - 1] 
                for i in range(updated_words):
                    title_withyear += updated_words[i]
                    if i != (len(updated_words) - 1):
                        title_withyear += ' '
                title_withyear += ", " + first_word + " " + last_word
            else:
                for i in range(len(words)):
                    if i != 0:
                        title_noyear += words[i]
                    if i != (len(words) - 1):
                        title_noyear += " "
                title_withyear += ", " + first_word
                
        # or make title_noyear
        else:
            for i in range(len(words)):
                title_noyear += words[i]
                if i != (len(words) - 1):
                    title_noyear += " "
        
        title_withyear = title_withyear.lower()
        title_noyear = title_noyear.lower()
        movies = self.titles
        
        res = []
        for i in range(len(movies)):
            movie = movies[i][0].lower()
            if title_withyear == movie:
                res.append(movie)
            elif title_noyear == movie[:len(movie) - 7]:
                res.append(movie)
        return res
    
    #data_points is a list of tuples. tuples look like (index, sentiment)
    def make_user_ratings(self, data_points):
        user_ratings = np.zeros(self.ratings.shape[0])
        for idx in data_points:
            user_ratings[idx[0]] = idx[1]
        return user_ratings
    
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
        # The simple pattern
        simple_pattern = r'"([^"]+)"'
        matches = re.findall(simple_pattern, preprocessed_input)
        return matches
    
    
    # PARAMS:
    # words is a list with all the words in this potential movie
    def match_exact_title(self, words_notlow):
        # If title starts with article, remove it!
        articles = ["the", "a", "an"]
        words = [word.lower() for word in words]
        first_word = words[0]
        last_word = words[len(words) - 1]
        title_withyear = ""
        title_noyear = ""
        
        if first_word in articles:
            if ')' in last_word:
                # move the article to the second to last word 
                # aka "the notebook (2004)" -> "notebook, the (2004)"
                updated_words = words[1:len(words) - 1] 
                for i in range(updated_words):
                    title_withyear += updated_words[i]
                    if i != (len(updated_words) - 1):
                        title_withyear += ' '
                title_withyear += ", " + first_word + " " + last_word
            else:
                for i in range(len(words)):
                    if i != 0:
                        title_noyear += words[i]
                    if i != (len(words) - 1):
                        title_noyear += " "
                title_withyear += ", " + first_word
                
        # or make title_noyear
        else:
            for i in range(len(words)):
                title_noyear += words[i]
                if i != (len(words) - 1):
                    title_noyear += " "
        
        title = title.lower()
        movies = self.titles
        
        res = []
        for i in range(len(movies)):
            movie = movies[i][0].lower()
            if title_withyear == movie:
                res.append(movie)
            elif title_noyear == movie[:len(movie) - 7]:
                res.append(movie)
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
        #return self.find_movies_by_title_wrap(title, self.titles)
        result = []
        res = self.find_movies_by_title_wrap(title, self.titles)
        print(res)
        if self.creative:
            resres = []
            for elem in res:
                title2 = self.titles[elem][0]
                title3 = title2.split()
                if title.lower() == title3[0].lower():
                    resres.append(elem)
            return resres
        
        low = title.lower()
        
        # Restructure search term if it starts with an article
        articles = "(?:[Aa][Nn] |[Tt][Hh][Ee] |[Aa] )"
        find_articles = re.match(articles, title)
        if find_articles is not None:
            open_paren = title.find('(')
            if open_paren != -1:
                begin = title[len(find_articles.group(0)):open_paren - 1]
                begin += ", " + find_articles.group(0) + title[open_paren:]
                title = begin
            else:
                title = title[len(find_articles.group(0)):] + ", " + find_articles.group(0)
        title_low = (title.lower()).strip()
        
        for idx in res:
            movie_name = (self.titles[idx][0]).lower()
            open_paren = movie_name.find('(')
            title_open_paren = title_low.find('(')
            if title_open_paren == -1:
                movie_without_year = movie_name[:open_paren - 1]
                if movie_without_year == title_low:
                    result.append(idx)
            else:
                result.append(idx)
                          
        return result
            
    def find_movies_by_title_wrap(self, title, candidates):
        res = []
        movies = candidates 
        movie_titles = '' # string that will hold all movie titles in the database alongside their idx
        
        # Restructure search term if it starts with an article
        articles = '(?:[Aa][Nn] |[Tt][Hh][Ee] |[Aa] )'
        find_articles = re.match(articles, title)
        if find_articles is not None:
            open_paren = title.find('(')
            if open_paren != -1:
                begin = title[len(find_articles.group(0)):open_paren - 1]
                begin += ', ' + find_articles.group(0) + title[open_paren:]
                title = begin
            else:
                title = title[len(find_articles.group(0)):]
        pattern = '\d+-'
   
        # Add search term chars to regex pattern (not case sensitive)
        for ch in title:
            low = ch.lower()
            pattern += '[' + low + ch.upper() + ']'
        
        # Find all movie titles that match search term
        for i in range(len(movies)):
            movie_genre = movies[i]
            movie_titles += str(i) + '-' + movie_genre[0] # add index as last entry in move title
        matches = re.findall(pattern, movie_titles)
        
        # Extract index from each match, add to result list
        for match in matches:
            dash = match.find('-')
            idx = match[:dash]
            res.append(int(idx))
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
        count_pos = 0
        count_neg = 0
        
        # remove movie names from the list
        text = preprocessed_input.lower()
        current_titles = self.extract_titles(preprocessed_input)
        for title in current_titles:
            title = title.lower()
            idx = text.index(title)
            text = text[:idx] + text[idx + len(title):]
        
        # EXAMPLE IS 'I didn't enjoy "Titanic (1997)".'
        
        negation_words = ["not", "no", "didn", "don", "never", "barely", "hardly"]
        words_unstemmed = re.findall(r'\w+', text)
        words = [p.stem(word) for word in words_unstemmed]
        prev = None
        negated = False
        for i in range(len(words)):
            word = words[i]
            if word[len(word) - 1] == 'i':
                word = word[:len(word) - 1] + 'y'
            if prev in negation_words:
                negated = True
            if word in self.sentiment:
                if self.sentiment[word] == "pos":
                    if negated:
                        count_neg += 1
                        negated = False
                    else:
                        count_pos += 1
                elif self.sentiment[word] == "neg":
                    if negated:
                        count_pos += 1
                        negated = False
                    else:
                        count_neg += 1
            prev = word
        
        if count_pos > count_neg:
            return 1
        if count_neg > count_pos:
            return -1
        else:
            return 0
        
    def split_clauses(self, text, conjunctions):
        # input "I liked "Superman", but I did not like "As you like it""
        # returns [I liked "Superman", "but I did not like "As you like it"]
        clauses = []
        words = re.findall(r'\w+', text)
        start = 0
        for i in range(len(words)):
            word = words[i]
            if word.lower() in conjunctions:
                idx = text.find(word, start)
                clauses.append(text[start:idx + len(word)])
                start = idx + len(word)
            elif i == len(words) - 1:
                clauses.append(text[start:])
        return clauses
            
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
        sentiments = []
        conjunctions = ["but", "however", "yet"]
        clauses = self.split_clauses(preprocessed_input, conjunctions)
        last_senti = None
        negation_words = ["not", "no", "didn", "don", "never", "barely", "hardly"]
        for clause in clauses:
            movies = self.extract_titles(clause)
            movie_senti = self.extract_sentiment(clause)
            if (movie_senti == 0) and (last_senti != None) and (last_senti != 0):
                for negation_word in negation_words:
                    if negation_word in clause:
                        movie_senti = last_senti * -1
            for movie in movies:
                sentiments.append((movie, movie_senti))
            last_senti = movie_senti
        return sentiments
        

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

    # helper for disambiguate
    def find_substring(self, movies, title):
        low = title.lower()   
        for i in range(len(movies)):
            title_lower = movies[i][0].lower()
            if low in title_lower:
                return True
        return False       
        

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
        res = []
        movies = []
        low = clarification.lower()
        for candidate in candidates:
            movie_name = self.titles[candidate][0]
            if low in movie_name:
                res.append(candidate)
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
        # TODO: Binarize the supplied ratings matrix.                          #
        #                                                                      #
        # WARNING: Do not use self.ratings directly in this function.          #
        ########################################################################

        # The starter code returns a new matrix shaped like ratings but full of
        # zeros.
        # The starter code returns a new matrix shaped like ratings but full of
        # zeros.
        binarized_ratings = np.where(ratings > threshold, 1, -1) * np.where(ratings == 0, 0, 1)
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
        similarity = np.dot(u, v) / (np.sqrt(np.sum(u * u)) * np.sqrt(np.sum(v * v)))
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return similarity

    # Determines whether any user has rated this movie or not
    def rated_movie(self, ratings):
        for rating in ratings:
            if rating != 0:
                return True
        return False
    
    # Helper function that determines which movies already have ratings or not
    def indices_to_compare(self, user_ratings, ratings_matrix):
        known_items = []
        unknown_items = []
        unknown_item_indices = []
        known_ratings = []
        for i in range(user_ratings.shape[0]):
            if user_ratings[i] == 0:
                if self.rated_movie(ratings_matrix[i]):
                    unknown_items.append(ratings_matrix[i])
                    unknown_item_indices.append(i)
            else:
                known_ratings.append(user_ratings[i])
                known_items.append(ratings_matrix[i])
        return known_items, unknown_items, unknown_item_indices, known_ratings
  
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
        similarities = {} # Dictionary where key is index, value is weighted cosine similarity
        #concatenated = np.concatenate([ratings_matrix, user_ratings.reshape(user_ratings.shape[0], 1)], axis=1)
        known_items, unknown_items, unknown_item_indices, known_ratings = self.indices_to_compare(user_ratings, ratings_matrix)
        for i in range(len(unknown_items)):
            cur_item = unknown_items[i]
            sum = 0
            for j in range(len(known_items)):
                sum += known_ratings[j] * self.similarity(known_items[j], cur_item)
            similarities[unknown_item_indices[i]] = sum
                
        dict_items = similarities.items()
        similarities = sorted(dict_items, key=lambda x: x[1], reverse=True)
        lst = [tup[0] for tup in similarities]
        recommendations = lst[:k]
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
********************************************************************************        
             __   ___  _______   _______   _______   __   __   __
            |  | /  / |       | |   _   | |       | |  | |  | |  |
            |  |/  /  |    _  | |  |_|  |  \   ___| |  |_|  | |  |
            |     /   |   |_| | |       |   \  \    |       | |  |
            |   _  \  |      _| |       |  __\  \   |       | |__|
            |  | \  \ |   |  \  |   _   | |      \  |   _   |  __
            |__|  \__\|___|\__\ |__| |__| |_______| |__| |__| |__|

        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
