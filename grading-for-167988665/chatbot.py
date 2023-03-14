# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import re
import numpy as np
import random
from porter_stemmer import PorterStemmer
import nltk
from nltk.tokenize import word_tokenize
#from nltk.stem import *
from nltk.stem.porter import *
#stemmer = PorterStemmer

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

        ########################################################################
        # TODO: Binarize the movie ratings matrix. 
        # TODO: DONE!!!                           
        ########################################################################
        self.counter = 0
        self.user_ratings = np.zeros_like(ratings[:, 0]).reshape((-1, 1))
        self.recommendations = []
        self.rec_itr = 0

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings, 2.5)
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        ########################################################################
        # TODO: Write a short greeting message  
        # TODO: DONE!!!                              
        ########################################################################

        greeting_message = "Hi! I'm Chatty! I'm going to recommend a movie to you. First I will ask you about your taste in movies. Tell me about a movie that you have seen."
        if self.creative:
            greeting_message = "H-hewwo! It's Chatty here, and I'd love to like, suggest a movie for you, nya~! B-before we get started though, could you t-tell me a little bit about your movie preferences? Maybe, umm, you could tell me about a movie you've seen before, owo? Then I can like, recommend something that I think you'll really enjoy, heheh~!"
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################
        return greeting_message

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        ########################################################################
        # TODO: Write a short farewell message   
        # TODO: DONE!!!                           
        ########################################################################

        goodbye_message = "Thank you for hanging out with me! Stay in touch! Goodbye!"
        if self.creative:
            goodbye_message = "O-oh my goodness, thank you so much for spending time with me, nya~! It was so much fun chatting with you, and I hope we can like, stay in touch and chat some more soon, owo! Goodbye for now, and take care!"

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
        #if self.creative:
        #    response = "I processed {} in creative mode!!".format(line)
        #else:
        #    response = "I processed {} in starter mode!!".format(line)

        print(self.find_movies_closest_to_title(line))
        if not self.creative:
            if self.recommendations:
                if self.rec_itr == 10:
                    return "Sorry, I have no more movies to recommend. Please type :quit to quit. See you later!"
                curr = self.titles[self.recommendations[self.rec_itr]][0]
                replies3 = [f'You should watch "{curr}".', f'I think you\'ll like "{curr}".', f'Try "{curr}"!']
                self.rec_itr += 1
                reply = "\n" + random.choice(replies3)
                reply += "\n Would you like to hear another recommendation? (Or enter :quit if you're done.)"
                return reply
            movies_input = self.extract_titles(line)
            if len(movies_input) == 0:
                replies = ["I'm sorry, I didn't quite get that. Please tell me about a movie you have seen. Dont't forget quotes around the movie title!", "Apologies, but I don't understand. Tell me about a movie you have seen.", "Sorry, I didn't catch that. Please tell me about a movie you have seen. Don't forget quotes around the title!"]
                return random.choice(replies)
            elif len(movies_input) > 1:
                replies = ["Please tell me about only one movie at a time. Go ahead.", "My apologies, I can only understand input on one movie at a time. Please try again.", "Sorry, I can't understand multiple movies at once! Please try again, but with only one movie this time."]
                return random.choice(replies)
            elif len(movies_input) == 1:
                titles = self.find_movies_by_title(movies_input[0])
                if len(titles) == 0:
                    replies = [f'Sorry, I didn\'t quite get that. "{movies_input[0]}" doesn\'t show up in my database. Please try again.', 'Did you spell that movie title wrong? Please try again.', f'I\'ve never heard of "{movies_input[0]}". Sorry, please tell me about another movie.']
                    return random.choice(replies)
                elif len(titles) > 1:
                    replies = [f'Sorry, I found more than one movie called "{movies_input[0]}". Can you clarify?', f'Could you please specify the movie by its exact title? I found more than one movie called "{movies_input[0]}" in my database.']
                    return random.choice(replies)
                elif len(titles) == 1:
                    sentiment = self.extract_sentiment(line)
                    title = titles[0]
                    index = title
                    if sentiment == 0:
                        replies = [f'Sorry, I can\'t tell what you thought about "{movies_input[0]}". Please try again!', f'Did you like or disklike "{movies_input[0]}"? Please try again and include the movie name like you just did.']
                        return random.choice(replies)
                    elif sentiment == -1:
                        self.counter += 1
                        self.user_ratings[index] = -1
                        if self.counter != 5:
                            replies = [f'Ok, you didn\'t like "{movies_input[0]}". Tell me about another movie.', f'Great! Thanks for telling me you dissaproved of "{movies_input[0]}". Tell me about a new movie!', f'Sorry to hear you didn\'t like "{movies_input[0]}". Tell me about another movie.']
                        if self.counter == 5:
                            replies = [f'Ok, you didn\'t like "{movies_input[0]}".', f'Great! Thanks for telling me you dissaproved of "{movies_input[0]}".', f'Sorry to hear you didn\'t like "{movies_input[0]}".']
                        reply = random.choice(replies)
                        if self.counter == 5:
                            replies2 = ["That's enough for me to make a recommendation.", "Making a movie recommendation for you...", "Recommending a movie now!"]
                            reply += "\n" + random.choice(replies2)
                            self.recommendations = self.recommend(self.user_ratings, self.ratings, k=10, creative=self.creative)
                            curr = self.titles[self.recommendations[self.rec_itr]][0]
                            replies3 = [f'You should watch "{curr}".', f'I think you\'ll like "{curr}".', f'Try "{curr}"!']
                            self.rec_itr += 1
                            reply += "\n" + random.choice(replies3)
                            reply += "\n Would you like to hear another recommendation? (Or enter :quit if you're done.)"
                        return reply
                    elif sentiment == 1:
                        self.counter += 1
                        self.user_ratings[index] = 1
                        if self.counter !=5:
                            replies = [f'Ok, you liked "{movies_input[0]}". Tell me what you thought of another movie.', f'Great! Thanks for telling me you loved "{movies_input[0]}". Tell me about a new movie!', f'I\'m happy to hear you enjoyed "{movies_input[0]}". What is another movie?']
                        if self.counter == 5:
                            replies = [f'Ok, you liked "{movies_input[0]}".', f'Great! Thanks for telling me you loved "{movies_input[0]}".', f'I\'m happy to hear you enjoyed "{movies_input[0]}".']
                        reply = random.choice(replies)
                        if self.counter == 5:
                            replies2 = ["That's enough for me to make a recommendation.", "Making a movie recommendation for you...", "Recommending a movie now!"]
                            reply += "\n" + random.choice(replies2)
                            self.recommendations = self.recommend(self.user_ratings, self.ratings, k=10, creative=self.creative)
                            curr = self.titles[self.recommendations[self.rec_itr]][0]
                            replies3 = [f'You should watch "{curr}".', f'I think you\'ll like "{curr}".', f'Try "{curr}"!']
                            self.rec_itr += 1
                            reply += "\n" + random.choice(replies3)
                            reply += "\n Would you like to hear another recommendation? (Or enter :quit if you're done.)"
                        return reply
            else:
                return "I'm sorry, I didn't get that. Please tell me about a movie you have seen."
        else:
            if self.recommendations:
                if self.rec_itr == 10:
                    return "S-sorry, I'm all out of movie recommendations. To quit, please type :quit. See you later!"
                curr = self.titles[self.recommendations[self.rec_itr]][0]
                replies3 = [f'M-maybe you could try watching "{curr}"? I think it would be really great for you, nya~!', f'I have a feeling that "{curr}" would be just perfect for you, owo!', f'Why not give "{curr}" a try, nya~?']
                self.rec_itr += 1
                reply = "\n" + random.choice(replies3)
                reply += "\n D-do you want to hear another movie suggestion, nya~? O-or if you're all set, you can type :quit to exit, heheh."
                return reply
            movies_input = self.extract_titles(line)
            if len(movies_input) == 0:
                replies = ["Hmmm, that's not really what I want to talk about right now, let's go back to movies pweaase", "Oh no, I'm sorry, I didn't quite understand. Could you like, tell me about a movie you've seen, nya~?", "I'm so sorry, but I'm a little confused. Could you maybe share your thoughts on a movie you've seen before, owo?", "Sorry, I didn't quite catch that. Could you tell me about a movie you've watched, hehe?", "P-please don't give up on me! I just need a little more info before I can recommend a movie to you, nya! Keep talking to me, owo!"]
                return random.choice(replies)
            elif len(movies_input) > 1:
                ### DISAMBIGUATE HERE
                replies = ["Please talk to me about one movie at a time. You can go ahead and tell me about one movie now, nya!", "Oops, I'm sorry, but I can only process information about one movie at a time. Could you please try telling me about one movie again, nya?", "I'm sorry! It looks like I can only understand information about one movie at a time. Can you please try again and tell me about just one movie, OwO?"]
                return random.choice(replies)
            elif len(movies_input) == 1:
                titles = self.find_movies_by_title(movies_input[0])
                if len(titles) == 0:
                    if line.startswith("Can you ") or line.startswith("Could you ") or line.startswith("Would you "):
                        words = line.split()
                        words.pop(0)
                        words.pop(0)
                        line = " ".join(words)
                        if line.endswith("?") or line.endswith("!") or line.endswith("."):
                            line = line[:len(line)-1]
                        line = line.replace(" you ", " I ")
                        line = line.replace(" I ", " you ")
                        line = line.replace(" me ", " you ")
                        apology_message = "I am sowi, I cannot " + line + "."
                        return apology_message
                    if line.startswith("What is ") or line.startswith("What are "):
                        words = line.split()
                        words.pop(0)
                        words.pop(0)
                        line = " ".join(words)
                        if line.endswith("?") or line.endswith("!") or line.endswith("."):
                            line = line[:len(line)-1]
                        line = line.replace(" you ", " I ")
                        line = line.replace(" I ", " you ")
                        line = line.replace(" me ", " you ")
                        apology_message = "I am sowi, I cannot explain " + line + "."
                        return apology_message
                    if line.startswith("How do ") or line.startswith("How does ") or line.startswith("How can "):
                        words = line.split()
                        words.pop(0)
                        words.pop(0)
                        line = " ".join(words)
                        if line.endswith("?") or line.endswith("!") or line.endswith("."):
                            line = line[:len(line)-1]
                        line = line.replace(" you ", " I ")
                        line = line.replace(" I ", " you ")
                        line = line.replace(" me ", " you ")
                        apology_message = "I am sowi, I cannot explain how " + line + "."
                        return apology_message
                    if line.startswith("Who ") or line.startswith("Whose ") or line.startswith("Where ") or line.startswith("When ") or line.startswith("Why ") or line.startswith("Which "):
                        line = line[0].lower() + line[1:]
                        if line.endswith("?") or line.endswith("!") or line.endswith("."):
                            line = line[:len(line)-1]
                        line = line.replace(" you ", " I ")
                        line = line.replace(" I ", " you ")
                        line = line.replace(" me ", " you ")
                        apology_message = "I am sowi, I cannot explain " + line + "."
                        return apology_message
                    if (line.startswith("I")) or (line.startswith("I'm")) or (line.startswith("I've")) or (" I " in line) or (" I'm " in line) or (" I've " in line) or (" me " in line) or (line.endswith("me")) or (line.startswith("Me")):
                        
                        #synonyms for anger, happiness, sadness, and fear were built by asking ChatGPT for synonyms
                        anger_words = ["angry", "irate", "furious", "outraged", "enraged", "livid", "incensed", "wrathful", "vexed", "annoyed", "frustrated", "agitated", "exasperated", "provoked", "resentful"]
                        happiness_words = ["happy", "joyful", "delighted", "pleased", "ecstatic", "elated", "overjoyed", "thrilled", "ecstatic", "content", "gratified", "gleeful", "jovial", "merry", "blissful", "euphoric", "enchanted"]
                        sadness_words = ["sad", "depressed", "unhappy", "miserable", "heartbroken", "sorrowful", "melancholy", "downhearted", "gloomy", "blue", "despondent", "disheartened", "forlorn", "woeful", "crestfallen", "wretched", "dejected", "doleful", "mournful", "pensive"]
                        fear_words = ["fearful", "terrified", "panicked", "anxious", "nervous", "scared", "frightened", "apprehensive", "uneasy", "jittery", "timorous", "agitated", "worried", "alarmed", "horrified", "intimidated", "petrified", "spooked", "terror-stricken", "trepidatious", "daunted", "disquieted", "perturbed"]
                        
                        # each of these sentences were created using ChatGPT. I inputed a string in English and asked to write in uwu voice.
                        for word in line.lower().split():
                            if word in anger_words:
                                return "Oh! Did I make you angwy? I apowogize. OwO"
                            elif word in happiness_words:
                                return "I'm so happy to hear dat you'we feeling happy! UwU"
                            elif word in sadness_words:
                                return "I'm sowwy to heaw dat you'we feeling sad... pwease don't be too sad! ;w;"
                            elif word in fear_words:
                                return "I'm sowwy to heaw dat you'we feeling afwaid... pwease don't be afwaid! I'm hewe for you! OwO"
                    replies = [f'Oh no, I\'m sorry, but I didn\'t quite understand. It seems like "{movies_input[0]}" isn\'t in my movie database, nya. Could you try again or suggest a different movie, owo?', "Um, p-please don't be mad at me, but did you maybe misspell the movie title, nya? Could you please try again, hehe?", f'No way, I\'ve never heard of "{movies_input[0]}" before! I\'m sorry, but I don\'t think I can recommend anything for that movie, nya. Maybe you could tell me about another movie you\'ve watched, owo?']
                    return random.choice(replies)
                elif len(titles) > 1:
                    options = self.find_movies_by_title(movies_input[0])
                    print(options)
                    list_mov = "["
                    for option in options:
                        list_mov += "" + self.titles[option][0] + ", "
                    list_mov = list_mov[:len(list_mov)-1] + "]"
                    replies = [f'Aww, hehe! I\'m sorry to bother you, but it looks like there\'s more than one movie with the title "{movies_input[0]}" in my database, owo! Could you maybe specify which movie you\'re talking about, nya? \n \n Include one of these: {list_mov}^_^', f'Oh my, hehe! I\'m so sorry to ask, but could you please tell me the exact title of the movie you\'re referring to? I found multiple movies with the title "{movies_input[0]}" in my database, and I want to make sure I have the right one, owo! \n \n Include one of these: {list_mov}^_^']
                    return random.choice(replies)
                elif len(titles) == 1: #STOPPED HERE
                    sentiment = self.extract_sentiment(line)
                    title = titles[0]
                    index = title
                    if sentiment == 0:
                        replies = [f'Oh noes, nya! I\'m so sorry, but I couldn\'t quite understand what you thought of "{movies_input[0]}", nya! Could you please try telling me again, nya? I\'m all ears, owo! (=^･ω･^=)', f'Hey hey! Sorry to bother you again, but I\'m not quite sure if you liked or disliked "{movies_input[0]}"! Could you please try telling me again, but make sure to include the name of the movie like you just did? Thank you so much! (＾ω＾)']
                        return random.choice(replies)
                    elif sentiment <= -1:
                        self.counter += 1
                        self.user_ratings[index] = -1
                        if self.counter != 5:
                            replies = [f'Oh! I see you didn\'t quite enjoy "{movies_input[0]}"! No worries, nya! Let\'s talk about another movie! Please tell me the name of another movie you\'d like to discuss, nya! (=^・ω・^=)', f'Yay, hehe! Thank you for letting me know that you didn\'t like "{movies_input[0]}", nya! Now, let\'s move on and talk about something new and exciting, nya! Please tell me the name of a different movie you\'d like to talk about! Thank youuuu! ٩(｡•́‿•̀｡)۶', f'Aww, I\'m sorry to hear that you didn\'t like "{movies_input[0]}", nya! Don\'t worry though, there are plenty of other movies out there to enjoy! Please tell me the name of another movie you\'d like to discuss, nya! (=^・ω・^=)']
                        if self.counter == 5:
                            replies = [f'Oh! I see you didn\'t quite enjoy "{movies_input[0]}"! No worries, nya! (=^・ω・^=)', f'Yay, hehe! Thank you for letting me know that you didn\'t like "{movies_input[0]}", nya! ٩(｡•́‿•̀｡)۶', f'Aww, I\'m sorry to hear that you didn\'t like "{movies_input[0]}", nya! Don\'t worry though, there are plenty of other movies out there to enjoy! (=^・ω・^=)']
                        reply = random.choice(replies)
                        if self.counter == 5:
                            replies2 = ["Understood, meow! It's time for me to recommend a movie just for you, nya!", "Excited to recommend a movie, nya!", "Let's recommend a movie, OwO!!"]
                            reply += "\n" + random.choice(replies2)
                            self.recommendations = self.recommend(self.user_ratings, self.ratings, k=10, creative=self.creative)
                            curr = self.titles[self.recommendations[self.rec_itr]][0]
                            replies3 = [f'You should watch "{curr}", meow! It\'s a great choice, nya! (=^･^=)', f'I have a feeling you\'ll really enjoy "{curr}", hehe! Give it a try, nya! (＾◡＾)', f'Why not check out "{curr}", pawlease? I think you\'ll love it, nya! (✿◠‿◠)']
                            self.rec_itr += 1
                            reply += "\n" + random.choice(replies3)
                            reply += "\n Ready for another suggestion, meow? Type :quit to end. (＾◡＾)"
                        return reply
                    elif sentiment >= 1:
                        self.counter += 1
                        self.user_ratings[index] = 1
                        if self.counter !=5:
                            replies = [f'Great! Let\'s hear about another movie you liked, nya! Any purr-fect picks come to mind? (^・ω・^)', f'Fantastic, nya! Share another favorite movie with me! I\'m all ears... or should I say, paws? ฅ(＾・ω・＾ฅ)', f'Meowvelous! Tell me about another movie that left you feline good, nya! I\'m ready to listen... (=^･^=)']
                        if self.counter == 5:
                            replies = [f'Great! (^・ω・^)', f'Fantastic, nya! ฅ(＾・ω・＾ฅ)', f'Meowvelous! (=^･^=)']
                        reply = random.choice(replies)
                        if self.counter == 5:
                            replies2 = ["Understood, meow! It's time for me to recommend a movie just for you, nya!", "Excited to recommend a movie, nya!", "Let's recommend a movie, OwO!!"]
                            reply += "\n" + random.choice(replies2)
                            self.recommendations = self.recommend(self.user_ratings, self.ratings, k=10, creative=self.creative)
                            curr = self.titles[self.recommendations[self.rec_itr]][0]
                            replies3 = [f'You should watch "{curr}", meow! It\'s a great choice, nya! (=^･^=)', f'I have a feeling you\'ll really enjoy "{curr}", hehe! Give it a try, nya! (＾◡＾)', f'Why not check out "{curr}", pawlease? I think you\'ll love it, nya! (✿◠‿◠)']
                            self.rec_itr += 1
                            reply += "\n" + random.choice(replies3)
                            reply += "\n Ready for another suggestion, meow? Type :quit to end. (＾◡＾)"
                        return reply
            else:
                return "Aww, sowwy! Can you tell me about a movie you've watched, pwease? (=^ ◡ ^=)"
        # response = ""
        # movies_input = self.extract_titles(line)

        # for movie in movies_input:
        #     print("Movie" + movie)
        #     print(self.find_movies_by_title(movie))
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return "Oops"

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
        titles = []

        if self.creative:
            preprocessed_input = preprocessed_input.replace('"', '').replace("'", '')

            #if wanna, add in the case for removing and

            possible_first = [" thought ", " think ", " liked ", " enjoyed ", " like ", " enjoy ", " saw ", " love ", " loved "]
            possible_end = [" was ", " is "]
            punctuaion = [".", "!"]

            start_word = None
            for word in possible_first:
                if word in preprocessed_input:
                    start_word = word
                    break
            
            end_word = None
            for word in possible_end:
                if word in preprocessed_input:
                    end_word = word
                    break

            if start_word and end_word:
                start_index = preprocessed_input.index(start_word) + len(start_word)
                end_index = preprocessed_input.index(end_word)
                substring = preprocessed_input[start_index:end_index].strip()
            elif start_word:
                start_index = preprocessed_input.index(start_word) + len(start_word)
                substring = preprocessed_input[start_index:].strip()
            elif end_word:
                end_index = preprocessed_input.index(end_word)
                substring = preprocessed_input[:end_index].strip()
            else:
                substring = preprocessed_input

            if (substring == "What") or (substring == "Who") or (substring == "Where") or (substring == "Whose") or (substring == "When") or (substring == "Why") or (substring == "Which") or (substring == "Me") or (substring == "I"):
                substring = preprocessed_input
            
            for punt in punctuaion:
                if substring.endswith(punt):
                    substring = substring[:-1]
                    break

            #words = substring.split()
            #capitalized_words = [w.capitalize() for w in words]
            #capitalized_substring = " ".join(capitalized_words)

            #if capitalized_substring not in titles:
                #titles.append(capitalized_substring) 
            if substring not in titles:
                titles.append(substring)
        else:
            #encapsulated in quotes
            first_quote = preprocessed_input.find('\"')
            index = first_quote
            while index != -1:
                new_index = preprocessed_input.find('\"', index + 1)
                titles.append(preprocessed_input[index + 1: new_index])
                index = preprocessed_input.find('\"', new_index + 1)
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
        matching_indices = []
        year = re.search(r'\((\d{4})\)', title)
        title = self.article_handling(title, year)
        #print(title)

        for i, movie_title in enumerate(self.titles):
            movie_title = movie_title[0]
            
            if year:
                movie_title_without_year = movie_title
            else:
                movie_title_without_year = re.sub(r'\s\(\d{4}\)', '', movie_title)
                movie_title_without_year.strip()

            if movie_title_without_year.strip() == title.strip():
                matching_indices.append(i)

            if self.creative:
                punct = [",", ":", ";", ".", "!"]
                translator = str.maketrans("", "", "".join(punct))
                no_punct = movie_title_without_year.translate(translator)
                if (" " + title.strip() + " ") in no_punct.strip():
                    if i not in matching_indices:
                        matching_indices.append(i)
                elif no_punct.strip().startswith(title.strip() + " "):
                    if i not in matching_indices:
                        matching_indices.append(i)
                elif no_punct.strip().endswith(" " + title.strip()):
                    if i not in matching_indices:
                        matching_indices.append(i)
                
                #alternative title
                if "(a.k.a. " in movie_title_without_year:
                    zero_start = movie_title_without_year.find("(a.k.a. ")
                    start_index = zero_start + len("(a.k.a. ")
                    end_index = movie_title_without_year.find(")", start_index)
                    movieEnglish = movie_title_without_year[:zero_start].strip()
                    if year:
                        year_print = year.group(1)
                        movieEnglish += " (" + year_print + ")"
                    foreignMovie = movie_title_without_year[start_index:end_index].strip()

                    movieEnglish = self.article_handling(movieEnglish, year)
                    foreignMovie = self.article_handling(foreignMovie, year)

                    if movieEnglish.strip() == title.strip():
                        if i not in matching_indices:
                            matching_indices.append(i)
                    if foreignMovie.strip() == title.strip():
                        if i not in matching_indices:
                            matching_indices.append(i)
                    movie_title_without_year = movie_title_without_year[:zero_start-1] + movie_title_without_year[end_index+1:]
                
                #title in another language
                movie_title_without_year = re.sub(r'\s\(\d{4}\)', '', movie_title)
                movie_title_without_year.strip()
                start_index = movie_title_without_year.find("(")
                end_index = movie_title_without_year.find(")")
                if start_index != -1 and end_index != -1:
                    foreignMovie = movie_title_without_year[start_index+1:end_index].strip()
                    movieEnglish = movie_title_without_year[:start_index-1].strip()
                    if year:
                        year_print = year.group(1)
                        foreignMovie += " (" + year_print + ")"
                        movieEnglish += " (" + year_print + ")"

                    movieEnglish = self.article_handling(movieEnglish, year)
                    foreignMovie = self.article_handling(foreignMovie, year)
                    
                    if title.strip() == movieEnglish.strip():
                        if i not in matching_indices:
                            matching_indices.append(i)
                    if foreignMovie.strip() == title.strip():
                        if i not in matching_indices:
                            matching_indices.append(i)

                #without correct capitalization 
                if title.strip().lower() == movie_title_without_year.strip().lower():
                    if i not in matching_indices:
                        matching_indices.append(i)

                #disambiguate part 1
                #if title.strip() in movie_title_without_year.strip():
                    #if i not in matching_indices:
                        #matching_indices.append(i)

                

        return matching_indices
    
    def article_handling(self, title, year):
        if year:
            title = re.sub(r'\s\(\d{4}\)', '', title)
            title = title.strip()
        
        if title.startswith("A "):
            title = title[2:]
            title += ", A"
        elif title.startswith("An "):
            title = title[3:]
            title += ", An"
        elif title.startswith("The "):
            title = title[4:]
            title += ", The"

        if self.creative:
            articles = ["el ", "la ", "los ", "las ", "un ", "una ", "uno ", "unos ", "unas ", "il ", "lo ", "gli ", "le ", "les ", "une ", "des ", "der ", "die ", "das ", "die ", "dei ", "delle "]
            words_check = title.split()

            if (words_check[0].lower() + " ") in articles:
                article = words_check.pop(0)
                title = ' '.join(words_check)
                title += (", " + article)

        if year:
            year_print = year.group(1)
            title += " (" + year_print + ")"

        return title

    # def extract_sentiment(self, preprocessed_input):
    #     """Extract a sentiment rating from a line of pre-processed text.

    #     You should return -1 if the sentiment of the text is negative, 0 if the
    #     sentiment of the text is neutral (no sentiment detected), or +1 if the
    #     sentiment of the text is positive.

    #     As an optional creative extension, return -2 if the sentiment of the
    #     text is super negative and +2 if the sentiment of the text is super
    #     positive.

    #     Example:
    #       sentiment = chatbot.extract_sentiment(chatbot.preprocess(
    #                                                 'I liked "The Titanic"'))
    #       print(sentiment) // prints 1

    #     :param preprocessed_input: a user-supplied line of text that has been
    #     pre-processed with preprocess()
    #     :returns: a numerical value for the sentiment of the text
    #     """
    #     bad_words = ["didn't", "not", "won't", "can't", "never", "no", "couldn't"]
    #     flag = 1
    #     all_words = preprocessed_input.split()
    #     removed_movie_words = [word for word in all_words if not '"' in word]

    #     total_sentiment = 0
    #     for word in removed_movie_words:
    #         if word in bad_words:
    #             flag = -1
    #         if word in self.sentiment.keys():
    #             if (self.sentiment[word] == 'neg'):
    #                 total_sentiment += -1
    #             else:
    #                 total_sentiment += 1
        
    #     total_sentiment *= flag
        
    #     if total_sentiment > 0:
    #         return 1
    #     if total_sentiment < 0:
    #         return -1
    #     if total_sentiment == 0:
    #         return 0
    
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
        stemmer = nltk.PorterStemmer()
        #All negative words to consider 
        un_bad_words = ["didn't", "not", "won't", "can't", "never", "no", "couldn't", "n't"]
        bad_words = [stemmer.stem(word) for word in un_bad_words]
        
        un_strong_positive = ["love", "adore"]
        strong_positive = [stemmer.stem(word) for word in un_strong_positive]

        un_strong_negative = ["hate", "terrible", "horrible", "digusting"]
        strong_negative = [stemmer.stem(word) for word in un_strong_negative]
        
        unprocessed_amplify_words = ["really", "very", "reeally", "extremely"] #change this to RE?
        amplify_words = [stemmer.stem(word) for word in unprocessed_amplify_words]
        #print(amplify_words)
        """
        for word in unprocessed_amplify_words:
            amplify_words.append(stemmer.stem(word))
        """
        
        flag = 1
        extreme_neg_flag = 0
        extreme_pos_flag = 0
        amplify_flag = 0

        """
        all_words = preprocessed_input.split()
        removed_movie_words = words = [word for word in words if not ('"' in word)]
        """
        #Remove all movie mentions in the string using helper function
        potential_movies = self.extract_titles(preprocessed_input)
        new_string = preprocessed_input
        for movie in potential_movies:
            new_string = new_string.replace(movie, "")

        #Phrase indicators, start the string after the phrase indicator 
        phrase_words = ["however", "but", "yet"]
        for phrase_word in phrase_words:
            if phrase_word in new_string:
                new_start = new_string.index(phrase_word)
                new_string = new_string[new_start:]

        #remove punctuation
        new_string = new_string.replace(".", "")
        new_string = new_string.replace("!", "")
        new_string = new_string.replace("?", "")

        removed_movie_words = new_string.split()
        #removed_movie_words = nltk.word_tokenize(new_string)
        #print("final string to work", removed_movie_words)
        
        #p = PorterStemmer()
        
        total_sentiment = 0
        for unprocessed_word in removed_movie_words:
            #word = p.stem(unprocessed_word)
            word = stemmer.stem(unprocessed_word)
            #word = unprocessed_word
            #print("stemmed", word)
            if word in bad_words:
                flag = -1
            if word in strong_positive:
                extreme_pos_flag = 1
            if word in strong_negative:
                extreme_neg_flag = 1
            if word in amplify_words:
                amplify_flag = 1
                #print("processed", word)
            if word in self.sentiment.keys():
                if (self.sentiment[word] == 'neg'):
                    
                    total_sentiment += -1
                else:
                    total_sentiment += 1
        
        total_sentiment *= flag
        #neutral
        if self.creative:
            if amplify_flag == 1 or extreme_pos_flag == 1 or extreme_neg_flag == 1:
                if flag == -1:
                    #print("it got here")
                    return 0
                else:
                    if extreme_pos_flag == 1:
                        return 2
                    if extreme_neg_flag == 1:
                        return -2

            if total_sentiment > 0:
                if amplify_flag == 1:
                    return 2
                else:
                    return 1
            if total_sentiment < 0:
                if amplify_flag == 1:
                    return -2
                else:
                    return -1
            if total_sentiment == 0:
                #print("how is it here")
                return 0
        else:
            if total_sentiment > 0:
                return 1
            if total_sentiment < 0:
                return -1
            if total_sentiment == 0:
                return 0


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
        result = []

        phrase_indicators = ["but", "however"]

        strings_to_process = []
        for phrase_indicator in phrase_indicators:
            if phrase_indicator in preprocessed_input:
                break_index = preprocessed_input.index(phrase_indicator)
                strings_to_process.append(preprocessed_input[:break_index - 1])
                strings_to_process.append(preprocessed_input[break_index + 2:])
                break
        if len(strings_to_process) == 0:
            strings_to_process.append(preprocessed_input)
        
        for string in strings_to_process:
            movies = self.extract_titles(string)
            sentiment = self.extract_sentiment(string)

            for movie in movies:
                result.append((str(movie), sentiment))
                #print(string, sentiment)

        return result 


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

        #THE FOLLOWING FOUR FUNCTIONS ARE TAKEN FROM NLTK'S SOURCE CODE, AS SHOWN HERE: https://www.nltk.org/_modules/nltk/metrics/distance.html
        #We take no credit in creating this function(s) to compute edit distance. We cite our sources, as shown here: https://edstem.org/us/courses/20570/discussion/2718996?answer=6240408

        #THIS FUNCTION IS TAKEN FROM NLTK.SOURCE
        def _edit_dist_init(len1, len2):
            lev = []
            for i in range(len1):
                lev.append([0] * len2)  # initialize 2D array to zero
            for i in range(len1):
                lev[i][0] = i  # column 0: 0,1,2,3,4,...
            for j in range(len2):
                lev[0][j] = j  # row 0: 0,1,2,3,4,...
            return lev

        #THIS FUNCTION IS TAKEN FROM NLTK.SOURCE
        def _last_left_t_init(sigma):
            return {c: 0 for c in sigma}

        #THIS FUNCTION IS TAKEN FROM NLTK.SOURCE
        def _edit_dist_step(
            lev, i, j, s1, s2, last_left, last_right, substitution_cost=1, transpositions=False
            ):
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
        #THIS FUNCTION IS TAKEN FROM NLTK.SOURCE
        def edit_distance(s1, s2, substitution_cost=2, transpositions=False):
            """
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
            lev = _edit_dist_init(len1 + 1, len2 + 1)

            # retrieve alphabet
            sigma = set()
            sigma.update(s1)
            sigma.update(s2)

            # set up table to remember positions of last seen occurrence in s1
            last_left_t = _last_left_t_init(sigma)

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
                    _edit_dist_step(
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
        
        #OUR CODE STARTS HERE
        movie_titles = []
        movie_names = []
        lowest_distance = float('Inf')
        for i, movie_title in enumerate(self.titles):
            movie_title = movie_title[0]
            #print(movie_title)
            start = -1
            if "(" in movie_title:
                start = movie_title.index("(")
            if start != -1:
                movie_no_year = movie_title[:start].lower().strip()
            else:
                movie_no_year = movie_title.lower().strip()
            processed_title = title.lower().strip()
            first_letter = processed_title[0]
            distance = edit_distance(processed_title, movie_no_year)
            if distance < lowest_distance:
                lowest_distance = distance
                movie_titles = [] #reset if find new lowest
            if distance <= max_distance and distance <= lowest_distance:
                movie_titles.append(i)
                movie_names.append(movie_title)
        
        return movie_titles


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
        movie_titles = []
        movies_no_year = []
        for candidate in candidates:
            movie = self.titles[candidate][0]
            movie_titles.append(movie)
            start = movie.index("(")
            movies_no_year.append(movie[:start])
        
        result = []
        for i in range(len(candidates)):
            if re.match(r'^\d{4}$', clarification):
                if clarification in movie_titles[i]:
                    result.append(candidates[i])
            else:
                if clarification in movies_no_year[i]:
                    result.append(candidates[i])

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
        # TODO: Binarize the supplied ratings matrix.                          #
        # TODO: DONE!!!                                                                     #
        # WARNING: Do not use self.ratings directly in this function.          #
        ########################################################################

        binarized_ratings = np.where(ratings > 0, 1, 0)
        threshold = 2.5
        above_thresh = np.where(ratings > threshold, 1, 0)
        below_thresh = np.where(ratings <= threshold, -1, 0)
        binarized_ratings = np.multiply(binarized_ratings, above_thresh + below_thresh)

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
        # TODO: Compute cosine similarity between the two vectors.
        # TODO: DONE!!!            
        ########################################################################
        numerator = np.dot(u, v)
        denominator = np.linalg.norm(v) * np.linalg.norm(u) + 0.0001
        similarity = numerator/denominator
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
        seen = np.nonzero(user_ratings.reshape(len(user_ratings),))[0]
        not_seen = np.where(user_ratings.reshape(len(user_ratings),) == 0)[0]
        #print(ratings_matrix)
        #print(user_ratings)
        #print(not_seen)

        sims = []
        for unseen in not_seen:
            sum = 0
            for movie in seen:
                sum += self.similarity(ratings_matrix[movie, :], ratings_matrix[unseen, :]) * user_ratings[movie]
            sims.append((unseen, sum))
        sorted_sims = sorted(sims, key = lambda x: x[1], reverse=True)[:k]
        # NEED TO CHECK IF ALREADY SEEN

        return [x[0] for x in sorted_sims]

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
