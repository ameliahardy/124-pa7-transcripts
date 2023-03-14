# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np

import re
import nltk
from collections import defaultdict
from numpy import random

# all phrases are a combination of Artie, ChatGPT, google translate, and 
# artie's friend's daughter (who is two and unnamed as a minor), special
# shout out to nintendo for making mario in the first place
def say_stuff(movie, label):

    never_heard = ["Sorry-a, I don't-a know about \"" + movie + "\"... Can you-a tell me about another movie you enjoyed?", 
    "Mamma mia! \"" + movie + "\" is-a not something I'm familiar with. How about another movie you-a liked?", 
    "Oh no! I've-a never heard of \"" + movie + "\" before. But that's okay, tell me about another movie you enjoyed.", 
    "Oh boy, \"" + movie + "\" doesn't-a sound familiar. Can you-a talk about another movie you liked?", 
    "Whoa! \"" + movie + "\" is-a not a movie I know. But don't-a worry, let's-a hear about another one you liked.", 
    "I'm-a sorry, I don't-a recognize \"" + movie + "\". Can you-a share another movie you enjoyed?", 
    "Hmm, \"" + movie + "\" is-a not ringing any bells. Can you-a talk about another movie you liked instead?", 
    "Mama-mia! \"" + movie + "\" is-a not in my vocabulary. How about another movie you-a enjoyed?", 
    "Oh no, I've-a never heard of \"" + movie + "\". But don't-a worry, tell me about another movie you liked.", 
    "It's-a me, Mario, and I'm-a sorry I don't-a know \"" + movie + "\". Can you-a tell me about another movie you enjoyed?"]

    narrow = ["Mamma mia! I'm-a sorry, I couldn't-a figure out which movie you're-a talking about. The possible movies are-a ",
    "Oh boy, it's-a tough to figure out, but here are the possible movies:",
    "Mamma mia! I couldn't-a quite catch which movie you're-a talking about. The possible movies are-a ",
    "That's-a a tricky one, but here are the possible movies I think you're-a referring to:",
    "Yahoo! I'm-a sorry, I couldn't-a figure out which movie you're-a talking about. The possiblilities are-a",
    "Oh boy, I'm-a sorry, I couldn't-a quite understand which movie you're-a talking about. The possible movies are-a "]

    not_movie = ["Thank you! Hmm, I'm-a not quite getting it. Can-a you tell-a me about a movie you enjoyed or didn't enjoy?",
    "Thanks! Sorry about that, I'm-a not sure what you mean. Can-a you tell-a me about a movie you liked or didn't like?",
    "Many thanks! Oh boy, it seems like I'm-a not following you. Can-a you share with me a movie you enjoyed or didn't enjoy?",
    "Thank you kindly! Mamma mia, it looks like we're not on the same page. Can-a you tell-a me about a movie you liked or didn't like?",
    "Thank you! I'm-a sorry, but I'm not understanding you. Can-a you tell-a me about a movie you enjoyed or didn't enjoy instead?"]

    too_many = ["Oh my! It looks like you mentioned more than one movie. Can-a you tell-a me about one at a time, please? Thank you-a so much!",
    "Whoa there! It seems like you're talking about multiple movies. Can-a you share them one at a time? Thank you-a very much!",
    "Hold on a moment! It appears that you mentioned more than one movie. Can-a you tell-a me about one movie at a time, please? Thanks-a bunch!",
    "Mamma mia! It looks like you're talking about more than one movie. Can-a you tell-a me about them one at a time, please? Thank you-a so much!",
    "Oh no! It seems like you mentioned multiple movies. Can-a you share them one at a time, please? Grazie mille!"]

    like = ["\n" + "A-ha! Looks like you're-a quite the fan of: " + movie + ".",
    "\n" + "Well, well, well! It seems like you're-a really into: " + movie + ".", 
    "\n" + "Oh ho! I see you have great taste in movies. You like: " + movie + ".",
    "\n" + "Mamma mia! You really know how to pick 'em! You're-a into: " + movie + ".",
    "\n" + "I like-a what I see! You're-a clearly a big fan of: " + movie + "."]

    dislike = ["\n" + "Oh no! Looks like you're-a not a fan of: " + movie + ".",
    "\n" + "Mamma mia, that's-a too bad! It looks like you don't really care for: " + movie + ".",
    "\n" + "Aw, shucks! I see you're not too keen on: " + movie + ".",
    "\n" + "Oh boy, that's-a disappointing! It seems like you're not really into: " + movie + ".",
    "\n" + "Yikes, that's-a rough! It looks like you're not a big fan of: " + movie + "."]

    recommend_time = ["Here we go! I highly recommend for you: \"" + movie + "\". Do you want me to-a recommend another movie? I've got a whole list of great ones!",
    "Yahoo! I think you're really going to enjoy: \"" + movie + "\". I've got a few more movies up my sleeve! Would you like to hear?",
    "It's-a me, Mario! A great movie to watch is \"" + movie + "\". Would-a you like more movies?",
    "Let's-a go! I have a recommendation for you: \"" + movie + "\". Do you want me to keep going with the recommendations?",
    "Yahoo! I think you'll enjoy \"" + movie + "\". Would you like more, friend?"]

    unsure_vibes = ["Uh-oh! It seems like I'm-a not sure if you liked-a \"" + movie + "\". Can-a you try rephrasing that, please?",
    "Mamma mia! I'm-a having trouble telling if you enjoyed-a \"" + movie + "\". Can-a you say that another way, please?",
    "Oh boy! It's-a hard for me to tell if you liked-a \"" + movie + "\". Can-a you try saying that differently, please?",
    "Oops-a-daisy! I'm-a having a hard time figuring out if you enjoyed-a \"" + movie + "\". Can-a you rephrase that, please?",
    "Oh dear! It looks like I'm-a not sure if you liked-a \"" + movie + "\". Can-a you try saying that in another way, please?"]

    quit = ["Toad-a-ly understand if you need to go, just type ':quit' and you're-a outta here!"
    "So long-a, friend! Just type ':quit' and you're-a on your way to your next adventure!",
    "Wahoo! If you need to go, just type ':quit' and you're-a free to go-a!",
    "Mamma mia! If you're-a ready to go, just type ':quit' and you're-a good to go!",
    "It's-a me, Mario! If you need to leave, just type ':quit' and you're-a free to go do something else!"]


    if label == 'never_heard':
        return never_heard[random.randint(0,9)]
    if label == 'narrow':
        return narrow[random.randint(0,5)]
    if label == 'not_movie':
        return not_movie[random.randint(0,4)]
    if label == 'too_many':
        return too_many[random.randint(0,4)]
    if label == 'dislike':
        return dislike[random.randint(0,4)]
    if label == 'recommend_time':
        return recommend_time[random.randint(0,4)]
    if label == 'like':
        return like[random.randint(0,4)]
    if label == 'quit':
        return quit[random.randint(0,4)]
    if label == 'unsure_vibes':
        return unsure_vibes[random.randint(0,4)]

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'moviebot'

        self.creative = creative
        
        self.porter_stemmer = nltk.stem.PorterStemmer()
        
        self.articles_list_foriegn = ['el', 'la', 'las', 'il', 'le', 'l', 'das', 'der', 'das', 'det', 'les', 'die']
        self.articles_list = ['the', 'a', 'an']
        self.negations_list = ["no", "not", "neither", "nor", "doesnt", "isnt", "wasnt", "shouldnt", "wouldnt", "hardly", "barely",
                               "couldnt", "wont", "cant", "dont", "didnt", "werent", "never", "none", "nobody", "nothing", "scarcely"]
        self.super_sentiments = set(['amaz', 'astound', 'bloodi', 'dread', 'coloss', 'especi', 'except', 'excess', 'extrem',
                    'extraordinari', 'fantast', 'fright', 'incredib', 'insan', 'outrag', 'phenomen', 'quit',
                    'radic', 'rather', 'real', 'realli', 'remarkab', 'ridicul', 'so', 'strikingli', 'super',
                    'suprem', 'terribl', 'terrif', 'too', 'total', 'unusu', 'veri', 'wick'])
        """ Citation: Obtained additional emotion words from thesaurus.com and with chatgpt!
        """
        self.anger = ['angri', 'piss', 'furiou', 'enrag', 'frustrat', 'irrit', 'outrag', 'mad', 'fume', 
                      'wrath', 'seeth', 'aggrav', 'vex', 'cross', 'infuri', 'annoy', 'resent', 'bitter', 
                      'hostil', 'indign', 'tempestu', 'upset', 'stormi', 'testi', 'huffi', 'explos', 'steam']

        self.sad = ['sad', 'blue', 'gloomi', 'somber', 'melanchol', 'depress', 'despond', 'sorrow', 'unhappi', 'downcast', 'deject', 'crestfallen', 'low', 'dishearten', 'discourag', 'dispirit', 'forlorn', 'melancholi', 'mourn', 'woeful', 'glum', 'down', 'heartbroken', 'heavyheart', 'joyless', 'low-spirit', 'moros', 'sadden', 'sorrow', 'teari', 'unhappi', 'wist']

        self.happy = ['happi', 'content', 'excit', 'joy', 'glad', 'elat', 'pleas', 'delight', 'ecstat', 'euphor', 'overjoy', 'thrill', 'cheer', 'exult', 'bliss', 'exuber', 'gleeful', 'grate', 'jubil', 'merri', 'radiant', 'satisfi', 'sunni', 'tickl', 'upbeat', 'buoyant', 'chirpi', 'chipper', 'gratifi', 'jolli', 'mirth', 'raptur', 'vivaci']

        self.fear = ['fear', 'anxiou', 'terrifi', 'dread', 'frighten', 'horrifi', 'panick', 'alarm', 'uneasi', 'trepidati', 'phobic', 'disquiet', 'apprehens', 'concern', 'angsti', 'jitteri', 'nervou', 'scare', 'agit', 'constern', 'hesit', 'panicki', 'queasi', 'edgi', 'spook', 'timid', 'worri', 'dismay', 'trembl', 'shiveri', 'startl']

        self.disgust = ['disgust', 'repuls', 'revolt', 'nauseat', 'sicken', 'offend', 'queasi', 'displeas', 'grossed-out', 'appal', 'turned-off', 'abhor', 'avers', 'detest', 'disench', 'disapprov', 'disdain', 'disinterest', 'dislik', 'loath', 'nauseou', 'repugn', 'sickli', 'squeamish', 'unsettl', 'unsatisfi', 'abomin', 'antipathet', 'nauseou']

        self.emotions = [self.anger, self.sad, self.happy, self.fear, self.disgust]

 

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.stem_sentiment = util.load_sentiment_dictionary('deps/stemmed_sentiments.txt')

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings)
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

        # Added for process

        # Keep track of how many movies have been rated
        self.num_of_movies = 0
        # Keep track of recommendations
        self.recommendations = []
        #Keep track of how many movies have been recommended so far
        self.n = 0
        self.k = 0
        # Keep track of user ratings
        self.user_ratings = np.zeros((self.ratings.shape[0], 1))
        # CREATIVE Keeps track of candidates for disamigation
        self.candidates = []
        # CREATIVE
        self.unsure = -1
        self.llist = []
        self.movie_index = 0
    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################






    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        ########################################################################
        ########################################################################

        """ Citation: Obtained phrases from chatgpt, mario videos, google translate, and Artie's 
        friend's two year old daughter who will remain unnamed because she's a minor. Phrases 
        were edited by Artie. The Italian may be incorrect.
        """
        messages = ["Buongiorno! It's-a me, Mario!", 
        "Ciao, come stai? Everything's-a good? Time to watch-a movie!", 
        "Salve! Let's-a find a movie!", 
        "Benvenuto! What brings you here today?", 
        "Saluti, amico mio! How can I-a help you?", 
        "Hola! Come va? Ready for-a some recommendations?", 
        "Buondì! It's-a time to play!", 
        "Ehilà! Let's-a jump right in!", 
        "Salve a tutti! Ready for-a some movies?", 
        "Hey, ascolta! Let's-a go on an movie-finding adventure!"]



        message_pick = random.randint(0, 9)
        greeting_message = messages[message_pick]

        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################
        return greeting_message

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        ########################################################################
        ########################################################################

        """ Citation: Obtained phrases from chatgpt, mario videos, google translate, and Artie's 
        friend's two year old daughter who will remain unnamed because she's a minor. Phrases 
        were edited by Artie. The Italian may be incorrect.
        """
        messages = ["Bye-bye! See you later!",
        "Ciao for now! It's-a time to go!",
        "It was-a great-a seeing you! Bye!",
        "I'll-a catch you on the flip side!",
        "So long, partner! Until-a we meet again!",
        "Arrivederci! Keep-a smiling!",
        "Farewell! Don't-a forget to eat-a your mushrooms!",
        "Take-a care! Don't-a fall down any pits!",
        "Later gator! Or should I say-a, later-a crocodile!",
        "Goodbye, my-a friend! You'll-a always be in my-a heart!" ]
        message_pick = random.randint(0, 9)
        goodbye_message = messages[message_pick]

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
            if self.unsure != -1:
                prev = self.candidates
                self.candidates = self.disambiguate(line, self.candidates)
                if len(self.candidates) != 1:
                    if len(self.candidates) == 0: self.candidates = prev
                    response = say_stuff('', 'narrow')
                    for i in range(len(self.candidates)):
                        if i == len(self.candidates) - 1:
                            response += 'and ' + self.titles[self.candidates[i]][0] + '.'
                        else:
                            response += self.titles[self.candidates[i]][0] + ', '
                    return response
                else:
                    self.llist[self.unsure][0] = self.titles[self.candidates[0]][0]
                    self.unsure = -2
            if self.num_of_movies < 5:
                if self.unsure != -2:
                    self.llist = [list(x) for x in self.extract_sentiment_for_movies(line)]
                if len(self.llist) == 0:
                    
                    response = say_stuff('', 'not_movie')
                else:
                    for item in self.llist:
                        titles = self.find_movies_by_title(item[0])
                        if len(titles) > 1 or len(titles) == 0:
                            titles = [self.find_movies_by_title(x) for x in self.extract_titles(item[0])]
                            temp = []
                            for t in titles:
                                for a in t:
                                    temp.append(a)
                            titles = list(set(temp))
                            if len(titles) == 0:
                                if self.unsure != -2:
                                    return say_stuff(item[0], 'never_heard')
                                else:
                                    response += "\n" + say_stuff(item[0], 'never_heard')
                            elif len(titles) > 1:
                                self.unsure = self.llist.index(item)
                                self.candidates = titles
                                response = say_stuff('', 'narrow')
                                for i in range(len(self.candidates)):
                                    if i == len(self.candidates) - 1:
                                        response += 'and ' + self.titles[self.candidates[i]][0] + '.'
                                    else:
                                        response += self.titles[self.candidates[i]][0] + ', '
                                response += " Can-a you please clarify?"
                                return response

                        title = item[0]
                        if len(titles) == 1:
                            sentiment = item[1]
                            index = titles  # returns list of movie indices, like [1356, 2347]
                            self.user_ratings[index] = sentiment
                            if sentiment >= 1:
                                response += say_stuff(title, 'like')
                                self.num_of_movies += 1
                            if sentiment < 0:
                                response += say_stuff(title, 'dislike')
                                self.num_of_movies += 1
                            if sentiment == 0:
                                response += "\n" + say_stuff(title, 'unsure_vibes')  #Chatbot unclear

                    self.unsure = -1
            else:
                if line == "yes" or line == "Yes" or line == "YES":
                    self.movie_index += 1
                elif line == "no" or line == "No" or line == "No":
                    if self.num_of_movies == 5:
                        # Restart Variables
                        self.num_of_movies = 0
                        self.recommendations = []
                        self.user_ratings = np.zeros((self.ratings.shape[0], 1))
                        self.movie_index = 0
                    return say_stuff('', 'quit')
                if self.num_of_movies >= 5:
                    ratings_indices = self.recommend(self.user_ratings, self.ratings, self.movie_index+1, False) 
                    response = say_stuff(self.titles[ratings_indices[-1]][0], 'recommend_time') + "(yes/no)"
            if self.num_of_movies == 5 and self.movie_index == 0:
                return response + "\nI will now recommend movies for you. Enter yes (or anything) to continue!\n"
        
        
        
        
        else:
            if self.num_of_movies < 5:
                titles = self.extract_titles(line)
                if len(titles) == 1:
                    extracted_movie = titles[0]
                elif len(titles) > 1:
                    return say_stuff('', 'too_many')
                else:
                    extracted_movie = ''
                movie_list = self.find_movies_by_title(extracted_movie)
                if len(movie_list) == 1:
                    sentiment = self.extract_sentiment(line)
                    index = movie_list  # returns list of movie indices, like [1356, 2347]
                    self.user_ratings[index] = sentiment
                    if sentiment == 1:
                        response = say_stuff(extracted_movie, 'like')
                        self.num_of_movies += 1
                    if sentiment == -1:
                        response = say_stuff(extracted_movie, 'dislike')
                        self.num_of_movies += 1
                    if sentiment == 0:
                        response = say_stuff(extracted_movie, 'unsure_vibes')  #Chatbot unclear
                elif len(movie_list) > 1:
                    response = 'I found more than one movie called-a \"' + extracted_movie + '\". Can you clarify by either being more specific or providing the year after the movie in parenthesis? Yahoo!'
                # user didn't mention input
                elif len(movie_list) == 0:
                    if extracted_movie != '':
                        response = say_stuff(extracted_movie, 'never_heard')
                    else:
                        response = say_stuff('', 'not_movie')

            else:
                if line == "yes" or line == "Yes" or line == "YES":
                    self.movie_index += 1
                elif line == "no" or line == "No" or line == "No":
                    if self.num_of_movies == 5:
                        # Restart Variables
                        self.num_of_movies = 0
                        self.recommendations = []
                        self.user_ratings = np.zeros((self.ratings.shape[0], 1))
                        self.movie_index = 0
                    return say_stuff('', 'quit')
                if self.num_of_movies >= 5:
                    ratings_indices = self.recommend(self.user_ratings, self.ratings, self.movie_index+1, False) 
                    response = say_stuff(self.titles[ratings_indices[-1]][0], 'recommend_time') + "(yes/no)"
            if self.num_of_movies == 5 and self.movie_index == 0:
                return response + "\nI will now recommend movies for you. Enter yes (or anything) to continue!\n"
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
        if self.creative:
            def helper(preprocessed_input):
                extracted_titles = set()
                words = preprocessed_input.split(' ')
                for i in range(len(words)):
                    for j in range(i, len(words)+1):
                        word = ' '.join(words[i:j])
                        if word != '':
                            extracted_titles.add(word)
    
                return extracted_titles
            # updated to move redundant titles-Artie
            extracted_titles = set(list(helper(preprocessed_input)) + list(helper(re.sub(r'[^\w\s-]', '',     preprocessed_input))))
            extracted_titles = [x for x in extracted_titles if self.find_movies_by_title(x, cr=False)!= []]
            return extracted_titles
        else:
            regex = r'"(.*?)"'
            extracted_titles = re.findall(regex, preprocessed_input)

        return extracted_titles

    def find_movies_by_title(self, title, cr=True):
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
        if cr == False:
            self.creative = False
        movie_indices = []
        title = title.lower()
        split_title = title.split(' ')

        regex = r'\([0-9]{4}\)'
        specifies_year = re.fullmatch(regex, split_title[-1])


        if specifies_year:
            if split_title[0] in self.articles_list:
                title = ''
                for i in range(1, len(split_title) - 1):
                    title = title + split_title[i] + ' ' if i < len(split_title) - 2 else title + split_title[i]
                title += ', ' + split_title[0] + ' ' + split_title[-1]
            for i in range(len(self.titles)):
                if title == self.titles[i][0].lower():
                    movie_indices += [i]
        else:
            # Added by Cristobal (aka titles don't move articles)
            if self.creative:
                title_with_articles = title
                title_with_articles_split = title_with_articles.split(' ')
                title_f = title_with_articles
                if title_with_articles_split[0] in self.articles_list_foriegn:
                    title_f = ''
                    for i in range(1, len(title_with_articles_split)):
                        title_f = title_f + title_with_articles_split[i] + ' ' if i < len(title_with_articles_split) - 1 else title_f + title_with_articles_split[i]
                    title_f += ', ' + title_with_articles_split[0]
            # ---------------------------
            if split_title[0] in self.articles_list:
                title = ''
                for i in range(1, len(split_title)):
                    title = title + split_title[i] + ' ' if i < len(split_title) - 1 else title + split_title[i]
                title += ', ' + split_title[0]
            for i in range(len(self.titles)):
                movie_without_year = self.titles[i][0].lower().split(' (')[0]

                # Added by Cristobal
                if self.creative:
                    movie_alt_title = self.titles[i][0].lower().split(' (a.k.a. ')
                    if len(movie_alt_title) > 1:
                        for j in range(1, len(movie_alt_title)):
                            movie_alt_title_cpy = movie_alt_title[j].split(')')
                            if title_with_articles == movie_alt_title_cpy[0]:
                                movie_indices += [i]

                    movie_foriegn_title = self.titles[i][0].lower().split(' (')
                    movie_foriegn_title = [x[:-1] for x in movie_foriegn_title[1:] if x[0:6] != 'a.k.a.' and re.sub(r'^[0-9]{4}', '', x[:-1]) != '']
                    for t in movie_foriegn_title:
                        if title_f == t:
                            movie_indices += [i]
                #-------------------
                if title == movie_without_year:
                    movie_indices += [i]
                if self.creative:
                    movie_split = movie_without_year.split(' ')
                    if title == ' '.join(movie_split[:2]) or title == ' '.join(movie_split[:2])[:-1]:
                        movie_indices += [i]
                    elif title == movie_split[0] or title == str(movie_split[0])[:-1]:
                            movie_indices += [i]

        if cr == False:
            self.creative = True
        return list(set(movie_indices))

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
        regex = r'"(.*?(\s)*?)*?"'
        quoteless_text = re.sub(regex, '', preprocessed_input)
        punctuationless_text = re.sub(r'[^\w\s-]', '', quoteless_text)
        words = [self.porter_stemmer.stem(word) for word in nltk.wordpunct_tokenize(punctuationless_text)]

        sentiments = []
        has_negation = False
        has_super_seniment = False
        for i in range(len(words)):
            word = words[i]
            if self.creative:
                    if word in self.super_sentiments: has_super_seniment = True
            if word in self.negations_list:
                has_negation = True

            # TODO: How to account for sentence like 'I did not like "Titanic", but I did enjoy "Avatar".'
            elif word in self.stem_sentiment:
                word_sentiment = 1 if self.stem_sentiment[word] == 'pos' else -1
                phrase_sentiment = (word_sentiment * -1) if has_negation else word_sentiment
                has_negation = False
                sentiments += [phrase_sentiment]

        total_sentiment = np.sum(sentiments)



        # if self.creative:
        #     if (total_sentiment > 0) and (total_sentiment < .5):
        #         return 1
        #     elif total_sentiment == 0:
        #         return 0
        #     elif (total_sentiment < 0) and (total_sentiment > -.5):
        #         return -1
        #     elif total_sentiment > 0:
        #         return 2
        #     elif total_sentiment < 0:
        #         return -2
        # else:
        #     return 1 if total_sentiment > 0 else 0 if total_sentiment == 0 else -1
        if has_super_seniment:
            return 2 if total_sentiment > 0 else 0 if total_sentiment == 0 else -2
        
        return 1 if total_sentiment > 0 else 0 if total_sentiment == 0 else -1
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

        def helper(x):
            quoteless_text = ''
            bad = False
            for char in x:
                if char == '\"':
                    bad = not bad
                if bad == False and char != '"':
                    quoteless_text += char
            #quoteless_text = re.sub(r'"(.*?(\s)*?)*?"', '', x)
            punctuationless_text = re.sub(r'[^\w\s-]', '', quoteless_text)
            words = [self.porter_stemmer.stem(word) for word in nltk.wordpunct_tokenize(punctuationless_text)]

            sentiments = []
            has_negation = False
            for i in range(len(words)):
                word = words[i]
                if word in self.negations_list:
                    has_negation = True

                # TODO: How to account for sentence like 'I did not like "Titanic", but I did enjoy "Avatar".'
                elif word in self.stem_sentiment:
                    word_sentiment = 1 if self.stem_sentiment[word] == 'pos' else -1
                    phrase_sentiment = (word_sentiment * -1) if has_negation else word_sentiment
                    has_negation = False
                    sentiments += [phrase_sentiment]

            total_sentiment = np.sum(sentiments)

            return 1 if total_sentiment > 0 else 0 if total_sentiment == 0 else -1

            return 0


        sentiment_arr = []
        movies = re.split(r"\"[ ,]", preprocessed_input)
        m_name = ""
        if movies[0][-1] == '"':
            m_name = movies[0]
        else:
            m_name = movies[0] + '"'
        g = re.search(r'".+"', m_name)
        if g != None:
            name = re.sub('"', '', g.group())
            sentiment_arr.append((name, helper(movies[0])))

        for i in range(1, len(movies)):
            cur_split = movies[i].split(" ")
            cur = 0
            if cur_split[0:3].count("and") or cur_split[0:3].count("And") or cur_split[0:3].count("or") or cur_split[0:3].count("Or") :
                cur = sentiment_arr[i-1][1]
            elif cur_split[0:3].count("But") or cur_split[0:3].count("but"):
                cur = sentiment_arr[i-1][1] * -1
            else:
                if i+1 != len(movies):
                    cur = helper(movies[i+1])
                else:
                    cur = helper(movies[i])
            if i != len(movies) - 1:
                if movies[i][-1] == '"':
                    m_name = movies[i]
                else:
                    m_name = movies[i] + '"'
            else:
                m_name = movies[i]

            g = re.search(r'".+"', m_name)
            if g != None:
                name = re.sub('"', '', g.group())
                sentiment_arr.append((name, cur))

        return sentiment_arr

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
        dict = {} #{'movie title' : edit dist, 'movie title' : edit dist, etc}
        list = []

        for i in range(len(self.titles)):
            option = self.titles[i]

            #find edit distance between user input and title
            if len(title) > len(option):
                dist = len(title) - len(option)
                title[:dist]

            elif len(option) > len(title):
                dif = len(option) - len(title)
                option[:dist]

            else:
                dist = 0

            for i in range(len(title)):
                if title[i] != option[i]:
                    dist += 1

            #if edit distance is <= max distance, put movie title : edit distance into dict
            if dist <= max_distance:
                dict[i] = dist #index : dist

        if not dict: #if dict is empty
            return []

        #sort dict by value, least to greatest
        sort_dict = sorted(dict.items(), key=lambda x: x[1], reverse=False) #returns a list of tuples

        #navigate to distance for first element in tuple bc thats the smallest distance
        least = sort_dict[0][1]

        for movie in sort_dict:
            if movie[1] == least:
                list.append(i)

        return list
        dict = {} #{'movie title' : edit dist, 'movie title' : edit dist, etc}
        list = []

        for i in range(len(self.titles)):
            option = self.titles[i]

   #find edit distance between user input and title
            if len(title) > len(option):
                dist = len(title) - len(option)
                title[:dist]

            elif len(option) > len(title):
                dif = len(option) - len(title)
                option[:dist]

            else:
                dist = 0

            for i in range(len(title)):
                if title[i] != option[i]:
                    dist += 1

   #if edit distance is <= max distance, put movie title : edit distance into dict
            if dist <= max_distance:
                dict[i] = dist #index : dist

        if not dict: #if dict is empty
            return []

#sort dict by value, least to greatest
        sort_dict = sorted(dict.items(), key=lambda x: x[1], reverse=False) #returns a list of tuples

#navigate to distance for first element in tuple bc thats the smallest distance
        least = sort_dict[0][1]

        for movie in sort_dict:
            if movie[1] == least:
                list.append(i)

        return list


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
        candidates_names = []
        updated_candidates = []
        for c in candidates:
            candidates_names.append((' '.join(self.titles[c]), c))

        # print(candidates_names)
        for val in candidates_names:
            if val[0].lower().count(str(clarification).lower() + ' ') or val[0].count('(' + str(clarification) + ')') or (val[0].count(str(clarification)[1:-1]) and str(clarification)[1:-1] != ''):
                updated_candidates.append(val[1])

        if updated_candidates == []:
            clarification_without_one = re.sub(" one *", '', clarification)
            for val in candidates_names:
                if val[0].lower().count(' ' + str(clarification_without_one).lower() + ' ') or val[0].count('(' + str(clarification) + ')'):
                    updated_candidates.append(val[1])

        numbers = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'eleventh', 'twelfth', 'thirteenth']
        for i in range(len(numbers)):
            if updated_candidates == []:
                if clarification.count(' ' + numbers[i] + ' '):
                        updated_candidates.append(candidates[i])
            else:
                break

        if updated_candidates == []:
            if clarification == 'most recent' or clarification == 'recent' or clarification == 'Most Recent':
                updated_candidates.append(candidates[0])

        if updated_candidates == [] and re.sub(r'[^\d]','', clarification[:2]) != '':
            temp = ''
            for c in clarification:
                if temp == '' and c != '0':
                    temp += c
            clarification = temp
            if len(clarification) < 3 and int(clarification[:2]) < 10 and len(candidates) > int(clarification[:2]):
                updated_candidates.append(candidates[int(clarification[:2]) - 1])

        return updated_candidates

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
        # binarized_ratings = np.zeros_like(ratings)
        
        ratings_array = np.array(ratings)
        
        # if the rating is greater than the threshold, set it to 10
        binarized_ratings = np.where(ratings_array > threshold, 10, ratings_array)
        
        # if the rating is zero, set it to 5
        binarized_ratings = np.where(binarized_ratings == 0, 6, binarized_ratings)
        
        # all ratings at or below threshold are guarunteed to be non-zero, so they
        # are set to -1
        binarized_ratings = np.where(binarized_ratings <= threshold, -1, binarized_ratings)
        
        # all ratings with a value of 5 are guarunteed to have originally been zero,
        # so they are now set appropriately
        binarized_ratings = np.where(binarized_ratings == 6, 0, binarized_ratings)
        
        # all ratings with a value of 10 are guarunteed to have originally been above
        # the threshold, so they are now set to 1
        binarized_ratings = np.where(binarized_ratings == 10, 1, binarized_ratings)

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
        # checks for zero-vectors
        if (not np.any(u)) or (not np.any(v)):
            return 0
        
        similarity = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
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
        recommendations = [0 for i in range(k)]
        seen_movies = []
        
        for i in range(np.size(user_ratings)):
            if user_ratings[i] != 0:
                seen_movies += [i]
        
        numerators = np.zeros(np.size(user_ratings))
        for i in range(np.size(user_ratings)):
            # unwatched movie
            if user_ratings[i] == 0:
                sum = 0
                for j in seen_movies:
                    rxj = user_ratings[j]
                    sij = self.similarity(ratings_matrix[i], ratings_matrix[j])
                    sum += rxj * sij
                    
                numerators[i] = sum
        
        dic = {}
        for i in range(np.size(numerators)):
            dic[i] = numerators[i]
        
        sorted_dic = sorted(((v,k) for (k,v) in dic.items()), reverse = True)
        for i in range(k):
            recommendations[i] = sorted_dic[i][1]

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

        This chatbot takes on the persona of Mario, a video game character, and
        offers movie recommendations based on knowing what you like. Feel free
        to chat with him casually, and he'll do his best to find a movie that 
        you'll enjoy. You can ask for multiple recommendations by continuing to 
        request more, exit using ":quit" and even discuss your emotions. Disclaimer: 
        We are doing this purely for an assignment and are not receiving monetary 
        compensation. Nintendo, if you see this, please don't sue us.
    
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')

