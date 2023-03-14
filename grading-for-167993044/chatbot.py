# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################

import util
from copy import deepcopy
import numpy as np
import re
import random
import porter_stemmer 
p = porter_stemmer.PorterStemmer()

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        self.name = 'Quince'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        
        # This is the dictionary of sentiment {word:sen}
        # add a few past tense
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        pos_past = ['liked', 'loved', 'enjoyed', 'enjoi', 'enjoy', 'happy', 'delighted']
        neg_past = ['hated', 'disliked', 'dislik', 'terribl']
        for word in pos_past:
            self.sentiment[word] = 'pos'
        for word in neg_past:
            self.sentiment[word] = 'neg'

        self.stemmed_sentiment = {}
        for key in self.sentiment.keys():
            value = self.sentiment[key]
            stemmed_key = p.stem(key)
            self.stemmed_sentiment[stemmed_key] = value

        # Binarize the movie ratings before storing the binarized matrix.    
        
        self.ratings = self.binarize(ratings)
        self.count =  0
        self.preferences = {}
        self.continue_rec = False
        self.first_run = True
        self.restart = False
        self.more_than_one = False
        self.more_than_one_indexes = []
        # only for disambiguate
        self.ambiguos = False
        self.ambiguos_indexes = []
        
        
        # possible content filler
        self.okay = ['Okay. ', 'Alrighty~ ', 'Okie~dokey~ ', 'Great!~ ', 'Okay! ', '', '', 'Hummm... ', 'Okay... ', 'All right! ', 'Well... ', 'Ahh... ', 'Aye aye, captain!~', "All good~", "Sounds good!~"]
        self.emojis = ['\(＾▽＾)/', '(＾◡＾)ノシ', '(o^▽^o)', '(=^･^=)', '(･ω･)つ⊂(･ω･)', '(＾◡＾)っ', '(ﾉ´ヮ´)ﾉ*:･ﾟ✧', '(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧', '(ﾉ´ヮ`)ﾉ*: ･ﾟ', '(＾▽＾)ゞ', 
                       '(ﾉ>ω<)ﾉ', '(*´∀`)~♥', 'ξ( ✿＞◡❛)', 'ლ(╹◡╹ლ)', '(◕‿◕✿)', '(づ｡◕‿‿◕｡)づ', '(｡♥‿♥｡)', '(≧◡≦)', '(✿◠‿◠)', '(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧', '(♥ω♥*)', '(＾• ω •＾)']
        self.astonishment = [  'Wow!', 'Aaaahhh', 'Oh!', 'Ohhh... ', 'Ah... ', '', '', '', '(((ﾟДﾟ;)))', 'Σ( ° △ °)', "Wowza! That's amazing~", 
                             "Aaaahhh! I can't believe it~", "Oh my gosh! That's incredible~", "Ohhh... My heart can't take it~", "Ah... My mind is blown~",
                               "Whoa nelly! That's unbelievable~", "Holy cowabunga! That's amazing, dude~", "Golly gee whiz! That's impressive~","Zounds! That's incredible~","That's mind-boggling~"]
        self.confusion = ['hummm... ', 'well... ', '' , 'emmm... ','ummmm... ' , 'okie... ', 'okay... ', '', "('c_`)", "('_ゝ`)",
                           "Huh? I'm confused~",    "Wait, what?",    "Umm... ",  "Eh?",  "Pardon? I'm a bit puzzled~", "Hmm... I'm not following~",
                           '(๑•́ ₃ •̀๑)', '_(┐「ε:)_']
        self.sad = ['(〒︿〒)', 'இдஇ', '(╥﹏╥)', '(☍﹏⁰。)', 'QAQ', '(ಥ_ಥ)', 'T^T', '（。>︿<)', '( ´•̥̥̥ω•̥̥̥` )', '…(•̩̩̩̩＿•̩̩̩̩)', '', '', '', '', '', '', "(╯︵╰,)", "(｡•́︿•̀｡)", "( ˘•́_•̀)っ"]

    def intro(self):
        """Return a string to use as your chatbot's description for the user.

        Consider adding to this description any information about what your
        chatbot can do and how the user can interact with it.
        """
        greetings = ['hello!', 'hi ya~', 'heyyyy!', 'hello!', 'nice to see you!', 'hello~', 'hey!']
        greeting_message = greetings[random.randint(0, len(greetings) - 1)] + self.emojis[random.randint(0, len(self.emojis) - 1)]

        introduction = " I'm Quince (they/them)! I studied film at NYU and I'm a huge fan of French New Wave!"
        description = " I will be your personal movie recommender. I am interactive agent designed to find you a perfect movie."
        detail = " When run in creative mode, I can handle emotions related to film. Just tell me what you liked or disliked to find movies."
        exit_statement = " To exit, just type :quit at any time."
        print(greeting_message)
        return introduction + description + detail + exit_statement

    def greeting(self):
        return "Let's get started! Tell me about some movies you liked or didn't like."

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """

        bye = ['byebye!', 'bye~', 'see ya!', 'have an amazing day!', 'have a nice day~', 'have a nice day!!!']
        goodbye_message = bye[random.randint(0, len(bye) - 1)] + self.emojis[random.randint(0, len(self.emojis) - 1)]

        return goodbye_message

    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################ 
    
    # should only run one time to get all the recs
    def get_all_recommend(self): 
        self.user_rating = np.zeros(len(self.titles))
        replace_index = self.preferences.keys()
        for r in replace_index:   
            self.user_rating[r] = self.preferences[r]

        self.all_recs = self.recommend(self.user_rating, self.ratings)
        
    # run each time user wants a rec, gives new rec every run
    def get_first_recommend(self):
        first_rec = 0
        if len(self.all_recs) != 0:     
            first_rec = self.all_recs.pop(0)
        return first_rec
    
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
        given = [    "With all the details you've shared with me,",    "Based on the lovely information you've given me,",    "In consideration of what you've said, my dear,",    "With all the precious details you've provided,",    "From what you've shared with me so far, cutie,",    "With the lovely information you've given me in mind,",    "In view of the adorable facts you've presented,",    "Given the sweet details you've mentioned, my love,",    "According to what you've told me, dearie,",    "Judging from the precious information you've shared with me,"]
        more = ["Can you share some more movies you like?","What are some other movies you enjoy that you can share with me?","I'm interested in hearing more about your favorite movies. Can you share some other ones you like?","Any other movies you'd like to share with me?","I'd love to hear about more movies you enjoy. Can you share some more recommendations?","What other movies do you like that you'd like to share with me?","Keep sharing your movie suggestions! What else do you enjoy?","I'm always looking for new movies to watch. Can you share some other ones you like?","I'm curious to know what other movies you enjoy. Can you share some more with me?","Tell me about more movies you like. What else would you like to share?"]
        okay_so = ["Oh, so {} is a movie you like. Interesting!", "Ah, I see. {} is a movie you enjoy watching.",  "Okay, got it. {} is a movie you are a fan of.", "Alright, noted. {} is a movie you prefer.", "Oh, I see. {} is a movie you have a liking for.", 
                   "I see, {} is a movie you find enjoyable.", "Ah, I understand. {} is a movie you have a soft spot for.", "Got it, {} is a movie you have an affinity towards.", "Okay, {} is a movie you appreciate.", "Oh, I see. {} is a movie you're fond of watching."]
        yes = [["yes", "okay", "y", "Yes", "sure", "yeah", "yup", "affirmative", "indeed", "absolutely", "roger that", "aye", "correct", "agreed"]]
        response = "Sorry... I didn't quite get that." + " " + more[random.randint(0, len(more) - 1)] + self.emojis[random.randint(0, len(self.emojis) - 1)]
        
        # create dict of movies by titles and index 2288%American Beauty (1999)%Drama|Romance
        movies_dict = {}
        regex_movie_index_title = '([0-9]+)\%(.+)\%'
        list_all_index_titles = []
        
        with open("data/movies.txt", 'r', encoding='utf-8') as f:
            text = f.read()
            list_all_index_titles = re.findall(regex_movie_index_title, text) #(7667, Next Three Days, The (2010))
        
        for index, movie in list_all_index_titles:
            movies_dict[int(index)] = movie


        if self.creative:
    
            # keep recommending movie to user
            if self.continue_rec == True and self.first_run == False: 
                # user want to continue recommending movies
                if line == "yes": 
                    movie_rec = movies_dict[self.get_first_recommend()]
                    return self.okay[random.randint(0, len(self.okay) - 1)] + given[random.randint(0, len(given) - 1)] + "I think you would like {}.".format(movie_rec) + self.emojis[random.randint(0, len(self.emojis) - 1)] + ' ' + 'Would you like more recommendations?'
                #  user doesn't want to continue recommending movies  
                else:
                    self.continue_rec = False
                    self.restart = True
                    return "Is there something else I can help you with?"


            # the firt run, call all recommend only once 
            if self.count == 5 and self.first_run == True: 
                self.first_run = False
                self.get_all_recommend()
                movie_rec = movies_dict[self.get_first_recommend()]
                response = self.okay[random.randint(0, len(self.okay) - 1)] + "Given what you told me, I think you would like {}.".format(movie_rec) + self.emojis[random.randint(0, len(self.emojis) - 1)] + ' ' + 'Would you like more recommendations?'
                self.continue_rec = True
            
        
            # disambiguate, when user say yes
            if self.count < 3 and self.first_run == True and self.more_than_one == True: 
                self.more_than_one = False
                result = self.disambiguate(line, self.more_than_one_indexes)
                self.count +=1
                self.preferences[result[0]] = 1
                # print("pref is", self.preferences)
                return okay_so[random.randint(0, len(okay_so) - 1)].format(movies_dict[result[0]]) + "Hit me up with more movies you like!"
            
            if self.count < 3 and self.first_run == True and self.ambiguos == False: 
    
                # data collection from user
                titles = self.extract_titles(line)
                sentiment = self.extract_sentiment(line)

                # get one title, one sentiment
                if len(titles) != 0 and sentiment != 0: 
                    response_like = "Great, so you like "
                    response_hate = "I'm sorry that you didn't enjoy  " 
                    for title in titles: 
                        
                        title_index = self.find_movies_by_title(title)
                        
                        # title doesn't match in database
                        if len(title_index) == 0: 
                            
                            # couldn't find a title
                            potential_title = self.find_movies_closest_to_title(title, 3)
                            if len(potential_title) > 0:
                                self.count += 1
                                self.preferences[potential_title[0]] = 1 
                                return "You mean {}? Great choice! Tell me more movies you like".format(movies_dict[potential_title[0]])
                            else:
                                return self.confusion[random.randint(0, len(self.confusion) - 1)] + "I've never heard of {}, sorry... Tell me about another movie you like!".format(title)
                        
                        # title match more than one result in database

                        if len(title_index) > 1 and self.more_than_one == False: 
                            self.more_than_one = True
                            self.more_than_one_indexes = title_index
                            response = "I found more than one movie called {}. Which movie did you mean: ".format(title)
                            for movie_index in title_index:
                                movie_name = movies_dict[movie_index]
                                if title_index[-1] == movie_index:
                                    response += movie_name + " ?" + self.emojis[random.randint(0, len(self.emojis) - 1)]  
                                else:
                                    response += movie_name + "or "
    


                        # title match exactly one movie in database
                        if len(title_index) == 1:   
                            # print("titles after", titles) 
                            self.preferences[title_index[0]] = sentiment
                            
                            # if user like the movi 
                            if sentiment > 0:    
                                self.count += 1
                                # print("count is:", self.count)
                                # print("this is preferences:", self.preferences)
                                response_like +=  " " + title + self.emojis[random.randint(0, len(self.emojis) - 1)]   
                                if self.count == 5: 
                                    response = "Fantastic! You have great tastes, do you want me to recommend a movie?" + self.emojis[random.randint(0, len(self.emojis) - 1)] 
                                             
                            if sentiment < 0: 
                                response_hate += title + " " + self.sad[random.randint(0, len(self.sad) - 1)] + "  Can you tell me about another movie you like?"
                    # print("what's the titles", titles)
                    # print("what's the index", title_index)
                    if sentiment > 0 and len(title_index) == 1 and self.count < 3:
                        response = response_like + " Tell me more movies that you like!"
                    if sentiment < 0: 
                        response = response_hate

                # give movie but don't know sentiment
                if len(titles) != 0 and sentiment == 0:
                    response = "I'm sorry, I'm not sure if you like {}. Tell me more about it".format(titles[0])

                # give invalid title 
                # print("what the sentiment, ", sentiment)
                if len(titles) == 0 and sentiment == 0 and self.restart == False:
                    response = self.confusion[random.randint(0, len(self.confusion) - 1)] + "I don't quite get that." + "Tell me about a movie you like!"

                if len(titles) == 0 and sentiment != 0 and self.restart == False:
                    if sentiment > 0:
                        response = "That's so great to hear!" + self.emojis[random.randint(0, len(self.emojis) - 1)] + "You should celebrate by watching a movie. What kind of movie do you want to watch?"
                    if sentiment < 0:
                        response = "I'm sorry you feel that way." + self.sad[random.randint(0, len(self.sad) - 1)] + "Maybe a movie will help cheer you up? What kind of movie do you want to watch?"
            
            if self.first_run == False and self.restart == True:
                    if line in yes:
                        # reset everything as if the first run 
                        self.first_run == True
                        self.count =  0
                        self.preferences = {}
                        self.first_run = True
                        self.continue_rec = False
                        self.restart = False
                        return "Great! What can I help you with?"
                    if line == "no":
                        return "call our goodbye message here"
        
        # non-creative mode
        else:
            
            # keep recommending movie to user
            if self.continue_rec == True and self.first_run == False: 
                # user want to continue recommending movies
                if line == "yes": 
                    movie_rec = movies_dict[self.get_first_recommend()]
                    return self.okay[random.randint(0, len(self.okay) - 1)] + "Given what you told me, I think you would like {}.".format(movie_rec) + self.emojis[random.randint(0, len(self.emojis) - 1)] + ' ' + 'Would you like more recommendations?'
                #  user doesn't want to continue recommending movies  
                else:
                    self.continue_rec = False
                    self.restart = True
                    return "Is there something else I can help you with?"


            # the firt run, call all recommend only once 
            if self.count == 5 and self.first_run == True: 
                self.first_run = False
                self.get_all_recommend()
                movie_rec = movies_dict[self.get_first_recommend()]
                response = self.okay[random.randint(0, len(self.okay) - 1)] + "Given what you told me, I think you would like {}.".format(movie_rec) + self.emojis[random.randint(0, len(self.emojis) - 1)] + ' ' + 'Would you like more recommendations?'
                self.continue_rec = True
                

            # doesn't have enough 5 like movies, keep collecting until count hits 5
            
            if self.count < 5 and self.first_run == True: 
                # data collection from user
                titles = self.extract_titles(line)
                # print(titles, 'is')
                sentiment = self.extract_sentiment(line)

                # get one title, one sentiment
                if len(titles) != 0 and sentiment != 0: 
                    response_like = "Great, so you like "
                    response_hate = "I'm sorry that you didn't enjoy "
                    for title in titles: 
                        
                        title_index = self.find_movies_by_title(title)
                        # print("title index is", title_index)
                        
                        # title doesn't match in database
                        if len(title_index) == 0: 
                            return self.confusion[random.randint(0, len(self.confusion) - 1)] + "I've never heard of {}, sorry... Tell me about another movie you like!".format(title)
                        
                        # title match more than one result in database

                        if len(title_index) > 1:
                            response = self.okay[random.randint(0, len(self.okay) - 1)] + "I found more than one movie called {}. Can you clarify?".format(title) + self.emojis[random.randint(0, len(self.emojis) - 1)]
                        
                        # title match exactly one movie in database
                        if len(title_index) == 1:   
                            # print("titles after", titles) 
                            self.preferences[title_index[0]] = sentiment
                            
                            # if user like the movi 
                            if sentiment == 1:    
                                self.count += 1
                                # print("count is:", self.count)
                                # print("this is preferences:", self.preferences)
                                response_like +=  " " + title + self.emojis[random.randint(0, len(self.emojis) - 1)]   
                                if self.count == 5: 
                                    response = "Fantastic! You have great tastes, do you want me to recommend a movie?" + self.emojis[random.randint(0, len(self.emojis) - 1)] 
                                             
                            if sentiment == -1: 
                                response_hate += title + self.sad[random.randint(0, len(self.sad) - 1)] + "Can you tell me about another movie you like?"
                    print("what's the titles", titles)
                    print("what's the index", title_index)
                    if sentiment == 1 and len(title_index) == 1 and self.count < 3:
                        response = response_like + " Tell me more movies that you like!"
                    if sentiment == -1: 
                        response = response_hate
                # give movie but don't know sentiment
                if len(titles) != 0 and sentiment == 0:
                    response = "I'm sorry, I'm not sure if you like {}. Tell me more about it".format(titles[0])

                # give invalid title 
                if len(titles) == 0 and sentiment == 0 and self.restart == False:
                    response = self.confusion[random.randint(0, len(self.confusion) - 1)] + "I don't quite get that." + "Tell me about a movie you like!"
    
            
            if self.first_run == False and self.restart == True:
                    if line == "yes":
                        # reset everything as if the first run 
                        self.first_run == True
                        self.count =  0
                        self.preferences = {}
                        self.first_run = True
                        self.continue_rec = False
                        self.restart = False
                        return "Great! What can I help you with?"
                    if line == "no":
                        return "call our goodbye message here"
                    
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
        greetings = ['hello', 'hi', 'hello', 'hi', 'hey', 'hey there', 'greetings', 'good morning', 'good afternoon', 'good evening', 'howdy', "what's up", 'yo', 'hiya', 'salutations', 'hola', 'aloha', 'bonjour', 'konnichiwa',              'Shalom', 'Namaste', 'Ahoy', 'Sup', 'Heya', 'Wassup']

        out = re.findall(r'"(.*?)"', preprocessed_input)
        if len(out) != 0:
            return out
        
        out = re.findall(r'\'(.*?)\'', preprocessed_input)
        if len(out) != 0:
            return out

        # lowercase
        else:
            out = re.findall(r'(?:enjoy|enjoyed|love|loved|like|liked|think|thought)\s([\w\s\'\(\)]+)\s(?:was|is)', preprocessed_input)
        if len(out) == 0:
            out = re.findall(r'(?:enjoy|enjoyed|love|loved|like|liked|think|thought)\s([\w\s\'\(\)]+)(?:\.|\!|,|\~|\?|$)', preprocessed_input)
        
        # and
        # if len(out) == 1 and out[0].find('and') != -1:
        #     a1 = re.findall(r'(.+)(?=\sand\s)', out[0])
        #     a2 = re.findall(r'(?:\sand\s)(.+)', out[0])
        #     out = a1 + a2
        if len(out) != 0:
            return out
        
        pro_input = re.sub(r'[,.;@#?!&$]+', ' ', preprocessed_input)
        if self.creative and pro_input.lower() not in greetings:
            index = self.find_movies_by_title(preprocessed_input)
            # if it is not empty then there is a title in the input
            if len(index) != 0:
                return [preprocessed_input]
        return out


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
        # unprocessed: (digit) (digit digit) digit
        unprocessed = re.findall(r'(\s*\(?\d+\)?)\s*$', title)
        # processed: digit
        year = re.findall(r'\(?(\d+)\)?$', title)
        the_ex = 0

        if len(unprocessed) != 0:
            year_com = unprocessed[0]
            i = len(year_com)
            pre = len(title)
            title = title[:pre - i]
        
        # find an, the, a
        the_a_an = re.findall(r'(?:^[Tt]he\s|^[Aa]n\s|^[Aa]\s)([a-zA-Z\s]+)', title)
        if len(the_a_an) != 0:
            words = title.split()
            if words[0].lower() == 'the':
                the_ex = 1
                title = the_a_an[0]
            else:
                title = the_a_an[0]

        # regex
        # there is a year in the title
        if len(unprocessed) != 0 and len(year) != 0:
            year_reg = year[0]
            reg = f'(?i)\d+(?=%{title}.*\({year_reg}\))'
        # there is an, a, or the in the title
        elif len(the_a_an) != 0: # and the_ex == 0
            reg = f'(?i)\d+(?=%{title}\,\s)'

        # otherwise
        else: # exception == 1
            reg = f'(?i)\d+(?=%{title}(?:\s|\W|\:))'

        with open("data/movies.txt", 'r', encoding="utf-8") as f:
            text = f.read()
            movie_list = re.findall(reg, text)
            
            # Try the original title
            if the_ex == 1 and len(movie_list) == 0:
                title = 'the' + ' ' + title
                reg = '(?i)\d+(?=%{title}(?:\s|\W|\:))'
                movie_list = re.findall(reg, text)
        
        out = [int(i) for i in movie_list]
        
        # creative
        if self.creative or len(out) == 1: 
            return out
        
        else:
            reg = f'(?i)\d+(?=%{title}\s\W)'
            movie_list = re.findall(reg, text)
            out = [int(i) for i in movie_list]
            return out


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
        pos = 0
        neg = 0
        multi = 1

        neg_words = ["hasn't", "didn't", "wasn't", "isn't", 'never', "none", "nobody", "noone", "don't", 'not', "can't", 'cannot', "couldn't", 'neither', 'nor', "wouldn't", "shouldn't"]
        strong_word = ['really', 'absolutely', 'favorite', 'hate', 'hated', 'love', 'loved', 'splendid', 'superb', 'amazing', 'outstanding', 'abysmal', 'subpar'
         'exceptional', 'fantastic', 'incredible', 'awesome', 'unacceptable','marvelous','terrific', 'remarkable', 'excellent', 'phenomenal', 'disappointing', 'unsatisfactory',
         'wonderful', 'impressive','terrible', 'awful', 'miserbale', 'pathetic', 'pitiful', 'deplorable', 'offensive', 'unpleasant', 'must', 'unacceptable', 'atrocious'
         'much', 'horrible', 'extremely', 'best', 'worst', 'greatest', 'greatly', 'spectacular', 'brilliant', 'lousy', 'inferior', 'repulsive', 'appalling', 'dreadful']

        # get rid of the title in the sentence to avoid distraction
        title = self.extract_titles(preprocessed_input)
        if len(title) != 0:
            preprocessed_input = preprocessed_input.replace(title[0], '')
        
        # get rid of punctuation marks
        preprocessed_input = re.sub(r'[,.;@#?!&$]+', ' ', preprocessed_input)

        # separate the line into word
        words = preprocessed_input.split()
        pre = ''

        # check whether it is in sentiment
        for i in range(len(words)):
            word = words[i]
            stemmed_word = p.stem(word)

            if i >= 1:
                pre = words[i-1]

            if self.creative and (pre in strong_word or word in strong_word): # and (pre not in neg_words and words[i - 2] not in neg_words)
                multi = 2    

            # check whether a word is a sentiment word
            if word in self.sentiment:
                sen = self.sentiment[word]
            if stemmed_word in self.sentiment:
                sen = self.sentiment[stemmed_word]

                if sen == 'pos':
                    # negation ex: I didn't like | I didn't really like
                    if pre in neg_words or words[i - 2] in neg_words or words[i - 3] in neg_words:
                        neg += 1
                    # normal pos word
                    else: 
                        pos += 1

                elif sen == 'neg':
                    # negation ex: it wasn't bad | it wasn't really awful
                    if pre in neg_words or words[i - 2] in neg_words or words[i - 3] in neg_words:
                        pos += 1
                    # normal neg word
                    else:
                        neg += 1

        if pos == neg:
            return 0
        elif pos > neg: 
            return (1 * multi)
        else: 
            return (-1 * multi)         

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
        out = []
        # Case 1: same sentiment
        # both A and B | both A, and B
        # neither A nor B | either A or B
        sen = 0
        same = '(?:neither|either|both)\s+"?([\w\,]+(?:\s[\w\,]+)*\s*(?:\(.+\))?)"?\s+\,?(?:nor|or|and)\s+"?([\w\,]+(?:\s[\w\,]+)*\s*(?:\(.+\))?)(?:\"|.|\!|$)'
        movies = re.findall(same, preprocessed_input)
        if len(movies) != 0:
            sen =  self.extract_sentiment(preprocessed_input)
            out.append((movies[0][0], sen))
            out.append((movies[0][1], sen))

        # Case 2: different sentiment
        # A, but B | A but B
        # separate the sentence and process each one individually
        dif = '(?:but|though|although|however|despite|oppositely|to the opposite|[oO]n the contrary).*'
        slices = re.findall(dif, preprocessed_input)
        if len(slices) != 0:
            first = preprocessed_input.replace(slices[0], '')
            second = slices[0]
            title_1 = self.extract_titles(first)
            title_2 = self.extract_titles(second)
            sen_1 = 0
            sen_2 = 0
            if len(title_1) == 1:
                sen_1 = self.extract_sentiment(first)
                out.append((title_1[0], sen_1))
            if len(title_2) == 1:
                sen = self.extract_sentiment(second)
                if sen_1 != 0 and sen_2 == 0:
                    sen_2 = sen_1 * -1
                out.append((title_2[0], sen_2))
        return out

    def find_edit_distance(self, str1, str2) -> int:

        distance_matrix = np.zeros((len(str1)+1, len(str2)+1))

        for r in range(distance_matrix.shape[0]):
            distance_matrix[r][0] = r

        for c in range(distance_matrix.shape[1]):
            distance_matrix[0][c] = c

        for r in range(1, distance_matrix.shape[0]):
            for c in range(1, distance_matrix.shape[1]):
                if str1[r-1] == str2[c-1]:
                    distance_matrix[r,c] = distance_matrix[r-1,c-1]
                else:
                    distance_matrix[r,c] = min(distance_matrix[r-1,c] + 1, distance_matrix[r,c-1] + 1, distance_matrix[r-1,c-1] + 2)
                    
        return distance_matrix[len(str1),len(str2)]

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
        regex_movie_index_title = '([0-9]+)\%(.+)\%'
        
        list_all_index_titles = []
        
        with open("data/movies.txt", 'r', encoding="utf-8") as f:
            text = f.read()
            list_all_index_titles = re.findall(regex_movie_index_title, text) #(7667, Next Three Days, The (2010))
        
        movie_dict = {} 
        for index, movie in list_all_index_titles:
            movie_dict[int(index)] = movie

        list_similar_titles = []
        shortest_lengths_list = []
        
        for index, movie in movie_dict.items():
            item_dist = self.find_edit_distance(movie[0:-7].lower(), title.lower())
            if item_dist <= max_distance:
                if len(shortest_lengths_list) == 0:
                    shortest_lengths_list.append(item_dist)
                    list_similar_titles.append(index)
                else:
                    if shortest_lengths_list[-1] == item_dist:
                        shortest_lengths_list.append(item_dist)
                        list_similar_titles.append(index)
                    elif shortest_lengths_list[-1] > item_dist:
                        shortest_lengths_list = [item_dist]
                        list_similar_titles = [index]

        
        return list_similar_titles

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
        regex_movie_index_title = '([0-9]+)\%(.+)\%'
        
        list_all_index_titles = []
        
        with open("data/movies.txt", 'r', encoding="utf-8") as f:
            text = f.read()
            list_all_index_titles = re.findall(regex_movie_index_title, text) #(7667, Next Three Days, The (2010))
        
        movie_dict = {} 
        for index, movie in list_all_index_titles:
            movie_dict[int(index)] = movie

        regex_year = '\([0-9]{4}\)'
        regex_number = '([0-9]+)(?=\s\([0-9]{4}\))'
        regex_title_without_year = '(.+)(?:\s\([0-9]{4}\))'
        
        distances = []

        def longest_common_substring(str1, str2):
            
            len1 = len(str1)
            len2 = len(str2)

            matrix = [[0]*(len2+1) for _ in range(len1+1)]
            longest_substring_length = 0
            longest_substring_end = 0

            for i in range(len1):
                for j in range(len2):
                    if str1[i] == str2[j]:
                        matrix[i+1][j+1] = matrix[i][j] + 1
                        if matrix[i+1][j+1] > longest_substring_length:
                            longest_substring_length = matrix[i+1][j+1]
                            longest_substring_end = i + 1

            longest_substring = str1[longest_substring_end-longest_substring_length: longest_substring_end]

            return longest_substring

        for candidate in candidates:
            title = movie_dict[candidate]
            year = re.findall(regex_year, title) #(1997)
            if year[0].strip("(").strip(")") == clarification.strip("(").strip(")"):
                return [candidate]
            number = re.findall(regex_number, title) #2
            if len(number) > 0 and number[0] == clarification:
                return [candidate]
            subtitle = re.findall(regex_title_without_year, title) #Sorcerer's Stone
            if len(subtitle) <= 0:
                continue
            distance = len(longest_common_substring(subtitle[0].lower(), clarification.lower())) # self.find_edit_distance(subtitle[0].lower(), clarification.lower())
            distances.append(distance)
        
        if "most recent" in clarification:
            years = {
                candidate: int(re.findall(regex_year, movie_dict[candidate])[0].strip("(").strip(")")) for candidate in candidates
            }
            return [sorted(years.items(), key=lambda item: item[1])[-1][0]]


        number_words = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eight", "ninth"]
        for i, nw in enumerate(number_words):
            clarification = clarification.replace(nw, str(i+1))
        num_in_clar = re.findall(r'\d', clarification)
        if len(num_in_clar) > 0:
            return [candidates[int(num_in_clar[0])-1]]
        
        return [candidates[i] for i, dist in enumerate(distances) if dist == max(distances)]

        
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
        

        # The starter code returns a new matrix shaped like ratings but full of
        # zeros.
        binarized_ratings = np.zeros_like(ratings)
        
        for ir, row in enumerate(ratings):
            for ic, col in enumerate(row):
                if ratings[ir, ic] != 0 and ratings[ir, ic] <= threshold:
                    binarized_ratings[ir, ic] = -1
                elif ratings[ir, ic] != 0 and ratings[ir, ic] > threshold:
                    binarized_ratings[ir, ic] = 1
        
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
        denom = np.linalg.norm(u) * np.linalg.norm(v)
        if denom == 0:
            return 0
        similarity = np.dot(u, v) / denom

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
        already_rated = []
        
        already_rated = list(np.where(user_ratings!=0)[0]) #these are the movies that the user already reviewed and they should not be in recommendations

        
        movie_similarities = {}
 
        for r, row in enumerate(ratings_matrix):
            if r not in already_rated:
                similarity_movie = 0
                for index in already_rated:
                    similarity_movie += user_ratings[index] * self.similarity(ratings_matrix[index], ratings_matrix[r])
                    
                movie_similarities[r] = similarity_movie
                
        movie_similarities_list = sorted(movie_similarities.items(), key=lambda elem:elem[1], reverse=True)
        
        count = 0
        for key, val in movie_similarities_list: 
                recommendations.append(key)
                count += 1
                if count == k:
                    break
        
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


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')