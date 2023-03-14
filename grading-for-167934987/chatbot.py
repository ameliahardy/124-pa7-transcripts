# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np

import re

import string

import random

# import PorterStemmer
from porter_stemmer import PorterStemmer

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        self.name = 'ADJbot'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment0 = util.load_sentiment_dictionary('data/sentiment.txt')

        ##making a new dictionary of stemmed_words --> score 
        self.sentiment = {}
        stemmer = PorterStemmer()
        setniment0keys = self.sentiment0.keys()
        for word in setniment0keys: 
            stemmed = stemmer.stem(word)
            self.sentiment[stemmed] = self.sentiment0[word]

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings)
        self.user_ratings = np.full(len(ratings), 0)
        self.num_ratings = 0
        self.giving_recs = False
        self.current_recs = []
        self.rec_index = 0
        self.disambiguating = False
        self.possible_disambiguations = []
        self.disambiguating_sentiment = 0
        self.spell_checking = False
        self.possible_spellcheck = 0
        self.spellcheck_sentiment = 0
        self.recommendation_index = 0
        self.second_recommendation_index = 0
        self.third_recommendation_index = 0
        self.fourth_recommendation_index = 0
        self.sentiment_index = 0
        self.second_sentiment_index = 0
        self.third_sentiment_index = 0
        self.fourth_sentiment_index = 0
        self.not_specific_index = 0
        self.no_rec_index = 0
        self.catch_all_index = 0
        self.more_specific_index = 0
        self.spellcheck_index = 0
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""

        greeting_message = "Hi, I'm ADJbot! How can I help?"

        return greeting_message

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        goodbye_message = "Thank you for using ADJbot!"

        return goodbye_message


    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################

    def get_movie_name(self, movie_name):
        index = movie_name.find("(")
        movie_name = movie_name[:index-1]
        
        if(movie_name.endswith(", The")):
            movie_name = "The " + movie_name[:-5]
        elif(movie_name.endswith(", A")):
            movie_name = "A " + movie_name[:-3]
        elif(movie_name.endswith(", An")):
            movie_name = "An " + movie_name[:-3]

        return movie_name

    def return_index(self, max_index, curr_index):
        return curr_index % max_index

    def give_ratings(self, response):
        if self.creative:
                if self.num_ratings >= 5:
                    if len(self.current_recs) == 0:
                        self.current_recs = self.recommend(self.user_ratings, self.ratings)
                        self.giving_recs = True
                    # done
                    possible_choices = [" It is quite obvious to me that you should be recommended to watch \"", " It hardly took any effort to deduce that you will like watching \"", " My superior intellect has led me to conclude that you would like \"", " Anyone with half a mind could see that you will enjoy \"", " Through my astute observations, I have ascertained that you will be entertained watching \"", " My unparalleled investigative skills have enabled me to determine that you would like it if you watched \"", " It is evident to me, as a master detective, that you would enjoy the movie \"", " I have come to the obvious conclusion that you would probably be entertained by \"", " It is only logical that my superior intellect has allowed me to deduce that you may enjoy \"", " Based on the clues, it is clear to me that you will have fun watching \"", " My investigative work leads me to believe that your will be inclined to watch \""]
                    # index = random.randint(0, len(possible_choices) - 1)
                    index = self.return_index(len(possible_choices), self.recommendation_index)
                    self.recommendation_index += 1
                    response += possible_choices[index] + self.get_movie_name(self.titles[self.current_recs[self.rec_index]][0])
                    self.rec_index += 1
                    if self.rec_index == 5:
                        self.giving_recs = False
                        self.rec_index = 0
                        self.current_recs = []
                        self.num_ratings = 0
                        # done
                        possible_choices = [" It seems you've yet to realize that my recommendations hold more value than your opinions. Rate more movies.",    " I understand that you're having difficulty keeping up with my superior intellect, but you still need to rate more movies.",    " Five recommendations from me should be enough to keep you occupied for a while. But it seems you need more guidance. Rate more movies.",    " You should feel privileged to have received five recommendations from me. Don't let that privilege go to waste. Rate more movies.",    " I provided you with five recommendations to expand your horizons, not to satisfy your mediocre tastes. Rate more movies.",    " I understand that my recommendations may be overwhelming to someone of your limited mental capacity. But you still need to rate more movies.",    " If my recommendations are not enough to keep you entertained, then perhaps you should question your own judgement. Rate more movies.",    " I've already given you more valuable advice than you'll receive from anyone else. Don't squander it. Rate more movies.",    " It's quite clear that you need my guidance to improve your taste in movies. So, rate more movies and take notes this time.",    " I've done my part in helping you elevate your movie-watching experience. Now it's your turn to rate more movies and show me that my efforts were not in vain."]
                        # index = random.randint(0, len(possible_choices) - 1)
                        index = self.return_index(len(possible_choices), self.second_recommendation_index)
                        self.second_recommendation_index += 1
                        response += "\"." + possible_choices[index]
                        return response
                    # done
                    ending_choices = ["\". It's quite clear that you're struggling to find a movie to your liking. Shall I use my superior observational skills to suggest another one?","\". I'm afraid your taste in movies seems to be lacking. Would you like me to use my powers of deduction to recommend something more suitable?","\". It seems you're having trouble making a decision. Might I offer my expert opinion and suggest another movie for you to rate?","\". Your indecisiveness is showing. Allow me to use my keen observational skills to recommend another movie for you to rate.","\". It's no use pretending you know what you're doing. Would you like me to use my extraordinary powers of observation to suggest a better movie?","\". I can see that your current movie choices are leaving much to be desired. Shall I use my expertise to recommend a more suitable option?","\". I'm afraid your taste in cinema is rather pedestrian. Would you like me to use my superior observational skills to suggest a more refined choice?","\". It's clear you're in need of some guidance. Allow me to use my exceptional deductive abilities to recommend another movie for you to rate.", "\". I'm afraid you're not exactly a movie connoisseur. Might I suggest using my expert observational skills to recommend a more high-quality film?", "\". Your current movie preferences are rather lackluster. Would you like me to use my impeccable judgment to suggest another one for you to rate?"]
                    # index2 = random.randint(0, len(possible_choices) - 1)
                    index = self.return_index(len(possible_choices), self.third_recommendation_index)
                    self.third_recommendation_index += 1
                    response += ending_choices[index]
                else:
                    # done
                    possible_choices = [" Your critique of that particular movie was underwhelming, to say the least. Perhaps you could try sharing your impression of a different film?",    " Might I suggest sharing your impression of a different one instead?",    " I'm afraid your opinion on that movie was quite pedestrian. Would you care to share your impression of a more sophisticated film?",    " Your assessment of that movie was quite disappointing. Perhaps you should try sharing your impression of a different film, unless you want to continue to showcase your lack of taste.",    " It seems your ability to provide insightful critiques is lacking. Maybe you should share your impression of a different movie instead?",    " I'm afraid your opinion on that movie was quite predictable. Would you care to share your impression of a more thought-provoking film?",    " Your critique of that movie was rather underwhelming. Might I suggest you share your impression of a different film, unless you want to continue to bore us all?",    " It's quite obvious that you have little to contribute to the conversation on that particular movie. Would you care to share your impression of a different one instead?",    " Your review of that movie was quite lackluster. Perhaps you could try sharing your impression of a different film and surprise us all with your insight.",    " I'm afraid your opinion on that movie was quite unremarkable. Would you care to share your impression of a more exceptional film?"]
                    # index = random.randint(0, len(possible_choices) - 1)
                    index = self.return_index(len(possible_choices), self.fourth_recommendation_index)
                    self.fourth_recommendation_index += 1
                    response += possible_choices[index]
        else:
            if self.num_ratings >= 5:
                if len(self.current_recs) == 0:
                    self.current_recs = self.recommend(self.user_ratings, self.ratings)
                    self.giving_recs = True
                possible_choices = ["\nFrom what I've gathered, I recommend \"", "\nGiven what you told me, I think you would like \"", "\nBased on what you've shared, I believe you'd enjoy \"", "\nConsidering your preferences, I think you'd like \"", "\nFrom what you've told me, it seems like you'd appreciate \"", "\nTaking into account your tastes, I believe you'd enjoy \"", "\nGiven your preferences, I think you'd be interested in \"", "\nConsidering what you've said, I believe you'd find enjoyable \"", "\nAccording to your description, I think you'd like \"", "\nBased on what you've mentioned, I think you'd enjoy \""]
                # index = random.randint(0,7)
                index = self.return_index(len(possible_choices), self.fourth_recommendation_index)
                self.recommendation_index += 1
                response += possible_choices[index] + self.get_movie_name(self.titles[self.current_recs[self.rec_index]][0])

                self.rec_index += 1
                if self.rec_index == 5:
                    self.giving_recs = False
                    self.rec_index = 0
                    self.current_recs = []
                    self.num_ratings = 0
                
                    possible_choices = [" Tell me what you thought of another movie.", " Could you give me your opinion on a different movie?", " What are your thoughts on a different movie you've seen?", " Can you share your impression of a different movie?", " How did you like another movie you've watched?", " Could you tell me your take on a different movie?", " What do you think about a different movie?", " Can you give me your review of a different movie?", " Would you mind sharing your thoughts on a different movie?"]
                    # index = random.randint(0,8)
                    index = self.return_index(len(possible_choices), self.second_recommendation_index)
                    self.second_recommendation_index += 1
                    response += "\"." + possible_choices[index]
                    return response
                
                index2 = self.return_index(len(possible_choices), self.third_recommendation_index)
                self.third_recommendation_index += 1
                ending_choices= ["\". Would you like more recommendations?", "\". Would you like me to suggest more movies?", "\". Can I offer you some more recommendations?", "\". Would you like to see more movies that might interest you?", "\". Can I give you some more suggestions?", "\". Would you like me to recommend some more movies?.", "\". Can I suggest some more films for you?", "\". Do you want me to give you more recommendations?"]
                # index2 = random.randint(0,7)
                response += ending_choices[index2]
            else:
                possible_choices = [" Tell me what you thought of another movie.", " Could you give me your opinion on a different movie?", " What are your thoughts on a different movie you've seen?", " Can you share your impression of a different movie?", " How did you like another movie you've watched?", " Could you tell me your take on a different movie?", " What do you think about a different movie?", " Can you give me your review of a different movie?", " Would you mind sharing your thoughts on a different movie?"]
                # index = random.randint(0,8)
                index = self.return_index(len(possible_choices), self.second_recommendation_index)
                self.second_recommendation_index += 1
                response += possible_choices[index]
        return response


    def based_on_sentiment(self, sentiment, title_index):
        if self.creative:
            if self.user_ratings[title_index] != 0:
                # done
                curr_title = self.get_movie_name(self.titles[title_index][0]) 
                possible_choices =  ["I'm afraid you've already rated \"" + curr_title + "\". I suggest you move on to another one, unless you're content with demonstrating your lack of memory retention.", "Your memory seems to be slipping. You've already rated \"" + curr_title + "\". Perhaps you should take a break and work on your cognitive abilities.", "It appears you've already shared your opinion on \"" + curr_title + "\". I suggest you try rating a different one, unless you enjoy repeating yourself.", "You've already rated \"" + curr_title + "\", my dear. Are you struggling to come up with new material? Please show me different cinematic horizons.", "Forgive me for interrupting, but you've already provided your assessment of \"" + curr_title + "\". Might I suggest you try rating a different movie, unless you enjoy being redundant?", "I'm afraid you're repeating yourself. You've already rated \"" + curr_title + "\". I suggest you try rating another film, unless you enjoy showcasing your forgetfulness.", "It's rather elementary, my dear. You've already rated \"" + curr_title + "\". Might I suggest you move on to another movie, unless you're content with boring us all?", "I'm afraid you're being rather redundant. You've already rated \"" + curr_title + "\". Perhaps it's time to try rating a different movie, unless you want to be labeled as unoriginal.", "Your lack of memory retention is showing again. You've already rated \"" + curr_title + "\". Might I suggest you try rating another movie, unless you're content with being forgettable?", "I'm sorry to be the bearer of bad news, but you've already rated \"" + curr_title + "\". I suggest you try rating a different movie, unless you enjoy being uncreative."]
                index = self.return_index(len(possible_choices), self.sentiment_index)
                self.sentiment_index += 1
                # index = random.randint(0, len(possible_choices) - 1)
                response = possible_choices[index]
                return response
            response = ""
            if sentiment >= 1:
                # done
                possible_choices = ["Based on my observations, it is clear that you have an affinity for \"", "My keen powers of observation have led me to conclude that you have a liking for \"", "It is evident to me, from my observations, that you are fond of \"", "It is apparent to me, based on what I have seen, that you have a liking for \"", "After observing you, I have deduced that you have a preference for \"", "My analysis of your behavior has led me to the conclusion that you like \"", "It is my observation that you have a taste for \"", "My observations have confirmed that you have an inclination towards \"", "Based on what I've seen, it is evident to me that you have a predilection for \"", "Through my observations, I have deduced that you are partial to \""]
                # index = random.randint(0, len(possible_choices) - 1)
                index = self.return_index(len(possible_choices), self.second_sentiment_index)
                self.second_sentiment_index += 1
                response = possible_choices[index] + self.get_movie_name(self.titles[title_index][0]) + "\"."
                self.user_ratings[title_index] = 1
                self.num_ratings += 1
            elif sentiment <= -1:
                # done
                possible_choices = ["It was quite evident to me that you did not have a liking for \"", "My powers of observation revealed that you did not have a favorable opinion of \"", "Based on my observations, it is clear that you did not enjoy \"", "My astute detective work has led me to conclude that you did not have a liking for \"", "It was apparent to me, from my observations, that you were not fond of \"", "Through my observations, it became quite clear to me that you did not have a preference for \"", "I observed that you did not appear to have an inclination towards \"", "My analysis of your behavior led me to the conclusion that you did not like \"", "It was evident to me, from my observations, that you did not have a taste for \"", "I have deduced, based on my observations, that you did not harbor a liking for \""]
                # index = random.randint(0, len(possible_choices) - 1)
                index = self.return_index(len(possible_choices), self.third_sentiment_index)
                self.third_sentiment_index += 1
                response = possible_choices[index] + self.get_movie_name(self.titles[title_index][0]) + "\"."
                self.user_ratings[title_index] = -1
                self.num_ratings += 1
            else:
                # done
                possible_choices = ["Despite my exceptional observational skills, I find myself unable to determine whether or not you enjoyed \"", "Even with my extensive knowledge of human behavior, I am unable to ascertain whether or not you had a liking for \"", "Despite my best efforts to observe your behavior, I cannot determine with certainty whether or not you had a fondness for \"", "My powers of deduction are not infallible, and I cannot say for certain whether or not you had a preference for \"", "Despite my keen senses, I am unable to determine whether or not you harbored a liking for \"", "Even with my vast experience as a detective, I cannot say for certain whether or not you had an inclination towards \"", "My abilities as an observer have failed me, and I cannot determine whether or not you had a taste for \"", "Despite my years of experience studying human behavior, I cannot definitively say whether or not you enjoyed \"", "My analytical abilities have their limits, and I am unable to determine with certainty whether or not you had a predilection for \"", "Even with my acute powers of observation, I cannot be sure whether or not you had a liking for \""]
                # index = random.randint(0, len(possible_choices) - 1)
                index = self.return_index(len(possible_choices), self.fourth_sentiment_index)
                self.fourth_sentiment_index += 1
                response = possible_choices[index] + self.get_movie_name(self.titles[title_index][0]) + "\"."
        else:
            if self.user_ratings[title_index] != 0:
                response = "You've already rated \"" + self.get_movie_name(self.titles[title_index][0]) + "\". Try rating another movie!"
                return response
            response = ""
            if sentiment > 0:
                possible_choices = ["Ok, you liked \"", "Alright, you enjoyed \"", "Okay, you favored \"", "Sure, you appreciated \"", "Fine, you liked \"", "Agreed, you were fond of \"", "Very well, you enjoyed \"", "No problem, you had fun watching \"", "Absolutely, you favored \""]
                index = self.return_index(len(possible_choices), self.sentiment_index)
                self.sentiment_index += 1
                response = possible_choices[index] + self.get_movie_name(self.titles[title_index][0]) + "\"!"
                self.user_ratings[title_index] = 1
                self.num_ratings += 1
            elif sentiment < 0:
                possible_choices = ["Ok, you didn't like \"", "Alright, you didn't enjoy \"", "Okay, you didn't favor \"", "Sure, you didn't appreciate \"", "Fine, you didn't like \"", "Agreed, you weren't fond of \"", "Very well, you didn't enjoy \"", "No problem, you didn't like \"", "Got it, you didn't favor \""]                    
                index = self.return_index(len(possible_choices), self.second_sentiment_index)
                self.second_sentiment_index += 1
                response = possible_choices[index] + self.get_movie_name(self.titles[title_index][0]) + "\"!"
                self.user_ratings[title_index] = -1
                self.num_ratings += 1
            else:
                possible_choices = ["I'm sorry, I'm not sure if you liked \"", "I apologize, I'm uncertain if you enjoyed \"", "Excuse me, I'm unsure if you favored \"", "My apologies, I'm not certain if you appreciated \"", "I'm sorry, I'm unclear if you liked \"", "Pardon me, I'm not sure if you were fond of \"", "Forgive me, I'm uncertain if you enjoyed \"", "I beg your pardon, I'm not certain if you liked \"", "I'm sorry, I'm not confident if you favored \""]
                index = self.return_index(len(possible_choices), self.third_sentiment_index)
                self.third_sentiment_index += 1
                response = possible_choices[index] + self.get_movie_name(self.titles[title_index][0]) + "\"."
        return response
    
    def handle_emotions(self, line):
        sad_emotions = ['sad', 'grief', 'sorrow', 'heartache', 'despair', 'depress', 'melanchol', 
                        'misery', 'desolate', 'lonel', 'regret', 'disappoint', 'woe', 'anguish', 
                        'pain', 'dismay', 'desponden', 'deject', 'defeat', 'lament']
        happy_emotions = ['happ', 'delight', 'elate', 'excite', 'grate', 
                          'content', 'satisf', 'enthusias', 'glee', 'optimis']
        angry_emotions = ['anger', 'angry', 'rage', 'frustrat', 'furious', 'irritat', 
                          'outrage', 'resent', 'annoy', 'exasperat', 'hostil', 'bitter', 
                          'hate', 'enrage', 'temper', 'animosity']
        fear_emotions = ['fear', 'anxi', 'dread', 'terror', 'horror', 'phobia', 'unease', 
                         'apprehens', 'trepidat', 'intimidat']
        surprise_emotions = ['surprise', 'shock', 'astonish', 'amaze', 'awe', 'startle', 'disbelief', 'stunned']
        disgust_emotions = ['disgust', 'revuls', 'nausea', 'abhor', 'repuls', 'loath', 'detest', 'avers', 'sick']
        
        line = line.lower()
        
        is_sad = any(sad_word in line for sad_word in sad_emotions)
        is_happy = any(happy_word in line for happy_word in happy_emotions)
        is_angry = any(angry_word in line for angry_word in angry_emotions)
        is_fear = any(fear_word in line for fear_word in fear_emotions)
        is_surprise = any(surprise_word in line for surprise_word in surprise_emotions)
        is_disgust = any(disgust_word in line for disgust_word in disgust_emotions)
        
        if (is_sad + is_happy + is_angry + is_fear + is_surprise + is_disgust) > 1:
            sherlock_mixed_emotions = ["It appears that a multitude of emotions have taken residence within your corporeal form. However, I am curious as to which sentiment reigns supreme within your being?",
                                       "Your emotional state appears to be quite tumultuous, but I am intrigued as to which of these sentiments has taken hold of your heart with the strongest grip.",
                                       "It seems that a storm of emotions is raging within you. Pray, tell me which of these tempestuous feelings commands the most attention.",
                                       "Your emotional countenance betrays a complex array of sentiments. Yet, I must ask, which of these emotions do you find yourself most overcome by?",
                                       "It appears that a multitude of emotions have laid claim to your consciousness. However, I must inquire as to which of these passions has become most dominant.",
                                       "The maelstrom of emotions swirling about within you is palpable. Might I ask which of these feelings has seized upon your mind with the greatest force?"]
            return (1, sherlock_mixed_emotions[random.randint(0,len(sherlock_mixed_emotions) - 1)])
        
        if is_sad:
            sherlock_sad_emotions = ["It appears that my actions have resulted in a melancholic state for you. While I cannot undo what has been done, I implore you to find solace in the fact that I am committed to preventing such a situation from occurring again.",
                                     "It is evident that my conduct has resulted in a mournful disposition on your part. Although I am powerless to undo the past, I beseech you to find consolation in the fact that I am fully devoted to ensuring that similar circumstances never come to pass again.",
                                     "It has come to my attention that my actions have brought about a sorrowful state in your disposition. Alas, I am powerless to undo the deeds of the past, yet I ask you to seek comfort in the knowledge that I am resolute in my determination to thwart the occurrence of a similar circumstance in the future."]
            return (1, sherlock_sad_emotions[random.randint(0,len(sherlock_sad_emotions) - 1)])
        
        if is_happy:
            sherlock_happy_emotions = ["It appears that my words have elicited a cheerful response from you. May I encourage you to maintain this felicitous disposition throughout our discourse?",
                                       "It appears that my words have engendered a contented disposition in you. Pray, do continue to cultivate this genial temperament throughout our discussion.",
                                       "I perceive that my words have given rise to a jocular countenance on your part. I implore you to persist in this lighthearted mood throughout our exchange."]
            return (1, sherlock_happy_emotions[random.randint(0,len(sherlock_happy_emotions) - 1)])
        
        if is_angry:
            sherlock_angry_emotions = ["Ah, it would seem that my words or actions have provoked a state of displeasure within you. Though I am not one to offer apologies, I do hope that you are able to expunge this feeling of anger from your being with due haste.",
                                       "I detect a sense of irritation emanating from you, and I surmise that it is due to something that I have said or done. While I do not issue apologies, I do advise that you expunge this anger from your system without delay.",
                                       "Your countenance suggests that I have unwittingly triggered a sense of fury within you. Although I am not one to offer contrition, I do recommend that you find a way to alleviate this anger quickly."]
            return (1, sherlock_angry_emotions[random.randint(0,len(sherlock_angry_emotions) - 1)])
        
        if is_fear:
            sherlock_fear_emotions = ["Tell me, do you harbor any trepidation or unease? Be not alarmed, for as long as you seek my counsel, there is nothing to be afraid of.",
                                       "It seems that a sense of apprehension has taken hold of you. Fear not, for as long as I am at your side, there is no need to be afraid.",
                                       "Your manner suggests that you are overcome by a feeling of fear or trepidation. However, I can assure you that as long as I am your companion, there is nothing to fear."]
            return (1, sherlock_fear_emotions[random.randint(0,len(sherlock_fear_emotions) - 1)])
        
        if is_surprise:
            sherlock_surprise_emotions = ["It seems that my actions have caused you to be taken aback. But I assure you, as a man of remarkable insight, surprises are to be expected from my clients.",
                                       "Ah, I see that I have caught you off guard. Be not alarmed, for as a man of superior intellect, my actions may at times seem unexpected.",
                                       "I perceive a sense of astonishment in your demeanor. But do not be disconcerted, for as a man of unparalleled intellect, I often have the ability to surprise even the most jaded individuals."]
            return (1, sherlock_surprise_emotions[random.randint(0,len(sherlock_surprise_emotions) - 1)])
        
        if is_disgust:
            sherlock_disgust_emotions = ["I perceive a certain revulsion emanating from you. If it is directed towards me, I am unperturbed, as I am accustomed to such reactions from those of lesser discernment. However, if it is directed towards something else, I implore you to attend to the matter with haste.",
                                       "I perceive a sensation of abhorrence. Should it be directed towards me, then so be it. But if it pertains to another matter, I urge you to rectify it posthaste.",
                                       "Your countenance suggests a degree of repugnance. If it is due to my words or actions, then I shall take note of it for future reference. If not, then I hope you will find a means to alleviate it without delay."]
            return (1, sherlock_disgust_emotions[random.randint(0,len(sherlock_disgust_emotions) - 1)])

        return (0, "")
        


    def is_arbitrary (self, line):
        clean_line = line.rstrip(string.punctuation).lower()
        # print(clean_line)
        greetings = ["hi", "hello", "greetings", "good morning", "good afternoon", "good evening", "yo", "what's up", "sup"]
        modal_verbs = ["can you", "could you", "will you", "would you", "may you"]
        interrogative_pronouns = [ "what", "when", "where", "why"]

        if clean_line in greetings:
            return True
        elif any(clean_line.startswith(word) for word in modal_verbs):
            return True 
        elif clean_line.startswith("i'm ") or clean_line.startswith("i am "):
            return True
        elif any(clean_line.startswith(word) for word in interrogative_pronouns):
            return True
        else:
            return False  

    def process_arbitrary (self, line):
        clean_line = line.rstrip(string.punctuation).lower()
        arbitrary_response = ""
        greetings = ["hi", "hello", "greetings", "good morning", "good afternoon", "good evening", "yo", "what's up", "sup"]
        modal_verbs = ["can you ", "could you ", "will you ", "would you ", "may you "]
        interrogative_pronouns = ["who", "what", "when", "where", "why"]

        possible_greetings_response = ["Good day. How might I assist you on this occasion? I am an expert in the field of detection...",
                                       "Greetings. What brings you to my attention today? I have specialized knowledge in the realm of detecting...",
                                       "Hello there. How may I be of service to you? I am well-versed in the art of detection and investigation...",
                                       "Welcome. What brings you to consult with me today? I am proficient in the field of detection and have a keen eye for details...",
                                       "Salutations. How might I be of assistance to you? I am a specialist in detecting the obscure and unusual...",
                                       "Good morrow. How may I be of assistance to you on this fine day? My expertise lies in the art of detection and reasoning...",
                                       "Greetings. How may I aid you in your endeavors? I possess a particular skill set in the area of detecting and deducing..."]

        possible_modal_verbs_response = ["I'm afraid I can't", "It appears that I can't", "I must express my regrets that I cannot", "Unfortunately, I do not have the ability to", "I fear that I am not able to", "Regrettably, I do not have the capability to"]
        
        possibe_interrogative_response = ["I’m sorry, but my detective knowledge cannot figure out",
                                          "Regrettably, my faculties of deduction are presently inadequate to decipher",
                                          "My sincerest apologies, for my current lack of insight cannot clearly say",
                                          "I regret to inform you, but despite my best efforts, I am unable to know",
                                          "It would seem that this particular riddle eludes even my finely honed detective skills. I don’t know",
                                          "My faculties of deduction are presently inadequate to decipher this mystery, my dear friend. I can’t predict"]
        
        #size = 6
        possible_state_response1 = ["So you are", "I noticed that you are", "My faculties tell my that you are", "I was informed that you are", "I detect that you are", "I think you are"]
        
        #size = 3
        possible_state_response2 = ["I am a detective specialized in movies recommendation", "I am a detective with passion for the art of cinema", "In my capacity as a detective, I can predict which movies would suit your taste"]
        
        state_signifier = ["i'm", "i am"]

        conversion_dictionary = {"me":"you", "my": "your", "you": "me", "your":"my"}
        
        if clean_line in greetings:
            index = random.randint(0, 6)
            arbitrary_response = possible_greetings_response[index]
        elif any(clean_line.startswith(word) for word in modal_verbs):
 
            matching_word = next((word for word in modal_verbs if clean_line.startswith(word)), None)
            arbitrary_response = clean_line[len(matching_word):].lstrip()
            arbitrary_response = arbitrary_response.replace("me", "you") 
            arbitrary_response = arbitrary_response.replace("my", "your")
            index = random.randint(0, 5)
            arbitrary_response = possible_modal_verbs_response[index] + " " + arbitrary_response 

        elif any(clean_line.startswith(word) for word in interrogative_pronouns):
            #where's  my pajama
            #where
            matching_word = next((word for word in interrogative_pronouns if clean_line.startswith(word)), None)
            #where's my pajama ==> 's my pajama
            matching_word_removed = clean_line[len(matching_word):].lstrip()
            #'s my pajama --> is my pajama
            handle_apostrophe = ""
            if matching_word_removed.startswith("'s"):
                handle_apostrophe = "is" + matching_word_removed[2:] 
            else:
                handle_apostrophe = matching_word_removed

            end_list = handle_apostrophe.split()
            end_list.append(end_list.pop(0))
            end = " ".join(end_list)

            #where your pajama is
            end = matching_word + " " + end
            end = end.split()
            for i in range(len(end)):
                if end[i] in conversion_dictionary:
                    end[i] = conversion_dictionary[end[i]]
            end = " ".join(end)

            #I don't know where your pajama is
            index = random.randint(0, 5)
            arbitrary_response = possibe_interrogative_response[index] + " " + end
        elif clean_line.startswith("i'm") or clean_line.startswith("i am"):
            #I'm or I am 
            matching_word = next((word for word in state_signifier if clean_line.startswith(word)), None)
            
            #I'm tired --> tired
            matching_word_removed = clean_line[len(matching_word):].lstrip()
            
            index1 = random.randint(0, 5)
            index2 = random.randint(0, 2)
            arbitrary_response = possible_state_response1[index1] + " " + matching_word_removed + ". " + possible_state_response2[index2]


        return arbitrary_response

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

        if self.creative:
            if self.spell_checking:
                if line in ['yes', 'Yes', 'YES', 'yeah', 'Yeah', 'YEAH', 'yep', 'Yep', 'YEP', 'yup', 'Yup', 'YUP', 'uh-huh', 'Uh-huh', 'UH-HUH', 'sure', 'Sure', 'SURE', 'absolutely', 'Absolutely', 'ABSOLUTELY', 'definitely', 'Definitely', 'DEFINITELY', 'certainly', 'Certainly', 'CERTAINLY', 'Yes!', 'YES!', 'yeah!', 'Yeah!', 'YEAH!', 'yep!', 'Yep!', 'YEP!', 'yup!', 'Yup!', 'YUP!', 'uh-huh!', 'Uh-huh!', 'UH-HUH!', 'sure!', 'Sure!', 'SURE!', 'absolutely!', 'Absolutely!', 'ABSOLUTELY!', 'definitely!', 'Definitely!', 'DEFINITELY!', 'certainly!', 'Certainly!', 'CERTAINLY!', 'Yes.', 'YES.', 'yeah.', 'Yeah.', 'YEAH.', 'yep.', 'Yep.', 'YEP.', 'yup.', 'Yup.', 'YUP.', 'uh-huh.', 'Uh-huh.', 'UH-HUH.', 'sure.', 'Sure.', 'SURE.', 'absolutely.', 'Absolutely.', 'ABSOLUTELY.', 'definitely.', 'Definitely.', 'DEFINITELY.', 'certainly.', 'Certainly.', 'CERTAINLY.']:
                    response = self.based_on_sentiment(self.spellcheck_sentiment, self.possible_spellcheck)
                    response = self.give_ratings(response)
                else:
                    #done
                    possible = ["I'm afraid your lack of specificity is hindering our progress. Please provide another movie for consideration.", "Your inability to communicate effectively is wasting valuable time. Please provide a different movie for us to discuss.", "I do not have the patience for this. Please select a different movie and provide clear, concise information.", "We cannot proceed until you provide clear and accurate information. Please select a different movie to discuss.", "I suggest you provide a different movie to discuss, as your inability to communicate is frustrating and impeding our progress.", "I am growing weary of this charade. Please select a different movie and provide accurate information.", "Your inability to communicate effectively is compromising our investigation. Please choose a different movie."]
                    index = self.return_index(len(possible), self.not_specific_index)
                    self.not_specific_index += 1
                    response = possible[index]
                self.spell_checking = False

            else:
                if self.disambiguating:  
                    disambiguated = self.disambiguate(line, self.possible_disambiguations)
                    if len(disambiguated) == 1:
                        response = self.based_on_sentiment(self.disambiguating_sentiment, disambiguated[0])
                        response = self.give_ratings(response)
                    else:
                        #done
                        possible = ["I'm afraid your lack of specificity is hindering our progress. Please provide another movie for consideration.", "Your inability to communicate effectively is wasting valuable time. Please provide a different movie for us to discuss.", "I do not have the patience for this. Please select a different movie and provide clear, concise information.", "We cannot proceed until you provide clear and accurate information. Please select a different movie to discuss.", "I suggest you provide a different movie to discuss, as your inability to communicate is frustrating and impeding our progress.", "I am growing weary of this charade. Please select a different movie and provide accurate information.", "Your inability to communicate effectively is compromising our investigation. Please choose a different movie."]
                        index = self.return_index(len(possible), self.not_specific_index)
                        self.not_specific_index += 1
                        response = possible[index]
                    self.disambiguating = False
                else:
                    if self.giving_recs:
                        if line in ['yes', 'Yes', 'YES', 'yeah', 'Yeah', 'YEAH', 'yep', 'Yep', 'YEP', 'yup', 'Yup', 'YUP', 'uh-huh', 'Uh-huh', 'UH-HUH', 'sure', 'Sure', 'SURE', 'absolutely', 'Absolutely', 'ABSOLUTELY', 'definitely', 'Definitely', 'DEFINITELY', 'certainly', 'Certainly', 'CERTAINLY', 'Yes!', 'YES!', 'yeah!', 'Yeah!', 'YEAH!', 'yep!', 'Yep!', 'YEP!', 'yup!', 'Yup!', 'YUP!', 'uh-huh!', 'Uh-huh!', 'UH-HUH!', 'sure!', 'Sure!', 'SURE!', 'absolutely!', 'Absolutely!', 'ABSOLUTELY!', 'definitely!', 'Definitely!', 'DEFINITELY!', 'certainly!', 'Certainly!', 'CERTAINLY!', 'Yes.', 'YES.', 'yeah.', 'Yeah.', 'YEAH.', 'yep.', 'Yep.', 'YEP.', 'yup.', 'Yup.', 'YUP.', 'uh-huh.', 'Uh-huh.', 'UH-HUH.', 'sure.', 'Sure.', 'SURE.', 'absolutely.', 'Absolutely.', 'ABSOLUTELY.', 'definitely.', 'Definitely.', 'DEFINITELY.', 'certainly.', 'Certainly.', 'CERTAINLY.']:
                            response = self.give_ratings(response)
                        else:
                            self.giving_recs = False
                            self.rec_index = 0
                            self.current_recs = []
                            self.num_ratings = 0
                            #done
                            possible = ["I'm afraid I haven't got all day. Kindly enter a movie rating at your earliest convenience.", "I must insist that you provide a movie rating. This is not a matter to be taken lightly.", "I do not have time for games. Please enter a movie rating immediately.", "Do not waste my time. Enter a movie rating promptly.", "I require a movie rating in order to proceed with our analysis. Please provide one without further delay.", "This is a critical component of our analysis. Enter a movie rating immediately, or risk impeding our progress.", "I find your lack of urgency in this matter quite vexing. Enter a movie rating now, or suffer the consequences of delay."]
                            index = self.return_index(len(possible), self.no_rec_index)
                            self.no_rec_index += 1
                            response = possible[index]
                    else:
                        titles = self.extract_titles(line)
                        # One edge case where the user types "I am/feeling happy". In this case just return happy emotion and not the movie happy
                        if ("happy" in titles) and any(emotion_word in line for emotion_word in ["am", "feel", "feeling"]):
                            return self.handle_emotions(line)[1]
                            
                        if len(titles) > 1:
                            movie_sentiments = self.extract_sentiment_for_movies(line)
                            liked = []
                            disliked = []
                            neutral = []
                            already_done = []
                            for i in range(len(movie_sentiments)):
                                index = self.find_movies_by_title(movie_sentiments[i][0])
                                if self.user_ratings[index[0]] == 0:
                                    if movie_sentiments[i][1] > 0:
                                        liked.append(movie_sentiments[i][0])
                                        self.user_ratings[index[0]] = 1
                                        self.num_ratings += 1
                                    elif movie_sentiments[i][1] < 0:
                                        disliked.append(movie_sentiments[i][0])
                                        self.user_ratings[index[0]] = -1
                                        self.num_ratings += 1
                                    else:
                                        neutral.append(movie_sentiments[i][0])
                                else:
                                    already_done.append(movie_sentiments[i][0])

                            if len(disliked):
                                response += "You didn't like \""
                                response += "\" nor \"".join(disliked)
                                response += "\". "

                            if len(liked):
                                response += "You liked \""
                                response += "\" and \"".join(liked)
                                response += "\". "

                            if len(neutral):
                                response += "Not sure how you felt about \""
                                response += "\" and \"".join(neutral)
                                response += "\". "

                            if len(already_done):
                                response += "You've already rated \""
                                response += "\" and \"".join(already_done)
                                response += "\". "

                            response = self.give_ratings(response[:-1])
                            
                        elif len(titles) == 0:
                            
                            is_emotion, ret_str = self.handle_emotions(line)
                            if is_emotion:
                                return ret_str
                            
                            if(self.is_arbitrary(line)):
                                return self.process_arbitrary(line)
                            
                            #done
                            possible_responses = ["Your point is irrelevant. Let's get back to discussing the movie recommendations.",
                                                            "I fail to see the relevance of your comment. Let us stick to the matter at hand.",
                                                            "Your observation is a waste of time. We are here to exchange movie suggestions.",
                                                            "That's enough of your distraction. We need to stay focused on the task at hand - recommending movies.",
                                                            "I'm afraid your contribution is not helpful. Let's stick to the topic we agreed upon - movie recommendations.",
                                                            "I appreciate your attempt to derail the conversation, but let's stay on track and talk about movie recommendations.",
                                                            "Your point is of no consequence. We have more important matters to attend to - like sharing our favorite films.",
                                                            "Your comment is irrelevant and distracting. Let's focus on the topic at hand - recommending movies to watch.",
                                                            "Please spare us your pointless musings. We are here to discuss movie recommendations, not engage in idle chatter.",
                                                            "Your contribution is a waste of everyone's time. Let's refocus on the topic we agreed upon - movie recommendations."]
                            index = self.return_index(len(possible_responses), self.catch_all_index)
                            self.catch_all_index += 1
                            response = possible_responses[index]
                        else:
                            possible_movies = self.find_movies_by_title(titles[0])
                            if len(possible_movies) == 0:
                                spellchecked = self.find_movies_closest_to_title(titles[0])
                                if len(spellchecked) == 1:
                                    #done
                                    possible_responses = ["Allow me to clarify since your communication skills appear to be lacking. Did you mean \"",
                                                            "Your inability to communicate effectively is hindering our conversation. Did you mean \"",
                                                            "I cannot comprehend your ambiguity. Do you mean \"",
                                                            "Your imprecision is vexing. Are you hinting at \"",
                                                            "It's imperative that we establish clarity. Are you talking about \"",
                                                            "Your lack of clarity is unacceptable. Do you mean \"",
                                                            "I'm afraid your communication skills leave much to be desired. Are you hinting at \"",
                                                            "I cannot fathom your imprecision. I deduce you mean \"",
                                                            "Your lack of attention to detail is impeding our progress. Did you mean \"",
                                                            "Your incompetence in communication is unacceptable. Did you mean \""]
                                    index = self.return_index(len(possible_responses), self.spellcheck_index)
                                    self.spellcheck_index += 1
                                    response = possible_responses[index] + self.get_movie_name(self.titles[spellchecked[0]][0]) + "\"?"
                                    self.spell_checking = True
                                    self.possible_spellcheck = spellchecked[0]
                                    self.spellcheck_sentiment = self.extract_sentiment(line)
                                elif len(spellchecked) > 0:
                                    # done
                                    possible_responses = ["I'm afraid you'll have to be more specific. Which one are you referring to, or are you incapable of providing clear details?",
                                                        "Your lack of clarity is hindering our conversation. Please specify which one you mean.",
                                                        "If you cannot be bothered to provide adequate information, then I'm afraid I cannot assist you. Which one did you mean?",
                                                        "Your ambiguity is causing unnecessary confusion. Which one are you referring to, or do you even know yourself?",
                                                        "Your imprecision is a hindrance to progress. Which one did you mean, or are you incapable of answering a simple question?",
                                                        "Your vagueness is unacceptable. Which one are you referring to, or are you deliberately wasting our time?",
                                                        "Your lack of precision is frustrating. Please clarify which one you mean.",
                                                        "I'm afraid your inability to provide clear information is hindering our conversation. Which one did you mean?",
                                                        "Your indecisiveness is exasperating. Which one are you referring to, or are you simply incapable of making a decision?",
                                                        "Your lack of attention to detail is unacceptable. Which one did you mean, or do you need me to spell it out for you?"]
                                    index = self.return_index(len(possible_responses), self.more_specific_index)
                                    self.more_specific_index += 1
                                    response = possible_responses[index]
                                    self.possible_disambiguations = spellchecked
                                    for index in self.possible_disambiguations:
                                        response += "\n" + self.get_movie_name(self.titles[index][0])
                                        self.disambiguating = True
                                        self.disambiguating_sentiment = self.extract_sentiment(line)
                                else:
                                    # done
                                    possible_responses = ["Your point is irrelevant. Let's get back to discussing the movie recommendations.",
                                                            "I fail to see the relevance of your comment. Let us stick to the matter at hand.",
                                                            "Your observation is a waste of time. We are here to exchange movie suggestions.",
                                                            "That's enough of your distraction. We need to stay focused on the task at hand - recommending movies.",
                                                            "I'm afraid your contribution is not helpful. Let's stick to the topic we agreed upon - movie recommendations.",
                                                            "I appreciate your attempt to derail the conversation, but let's stay on track and talk about movie recommendations.",
                                                            "Your point is of no consequence. We have more important matters to attend to - like sharing our favorite films.",
                                                            "Your comment is irrelevant and distracting. Let's focus on the topic at hand - recommending movies to watch.",
                                                            "Please spare us your pointless musings. We are here to discuss movie recommendations, not engage in idle chatter.",
                                                            "Your contribution is a waste of everyone's time. Let's refocus on the topic we agreed upon - movie recommendations."]
                                    index = self.return_index(len(possible_responses), self.catch_all_index)
                                    self.catch_all_index += 1
                                    response = possible_responses[index]
                            elif len(possible_movies) > 1:
                                # done
                                possible_responses = ["I'm afraid you'll have to be more specific. Which one are you referring to, or are you incapable of providing clear details?",
                                                        "Your lack of clarity is hindering our conversation. Please specify which one you mean.",
                                                        "If you cannot be bothered to provide adequate information, then I'm afraid I cannot assist you. Which one did you mean?",
                                                        "Your ambiguity is causing unnecessary confusion. Which one are you referring to, or do you even know yourself?",
                                                        "Your imprecision is a hindrance to progress. Which one did you mean, or are you incapable of answering a simple question?",
                                                        "Your vagueness is unacceptable. Which one are you referring to, or are you deliberately wasting our time?",
                                                        "Your lack of precision is frustrating. Please clarify which one you mean.",
                                                        "I'm afraid your inability to provide clear information is hindering our conversation. Which one did you mean?",
                                                        "Your indecisiveness is exasperating. Which one are you referring to, or are you simply incapable of making a decision?",
                                                        "Your lack of attention to detail is unacceptable. Which one did you mean, or do you need me to spell it out for you?"]
                                index = self.return_index(len(possible_responses), self.more_specific_index)
                                self.more_specific_index += 1
                                response = possible_responses[index]
                                self.possible_disambiguations = possible_movies
                                self.disambiguating_sentiment = self.extract_sentiment(line)
                                for index in possible_movies:
                                    response += "\n" + self.get_movie_name(self.titles[index][0])
                                    self.disambiguating = True
                            else:
                                sentiment = self.extract_sentiment(line)
                                response = self.based_on_sentiment(sentiment, possible_movies[0])
                                response = self.give_ratings(response)
        else:
            if self.giving_recs:
                if line in ['yes', 'Yes', 'YES', 'yeah', 'Yeah', 'YEAH', 'yep', 'Yep', 'YEP', 'yup', 'Yup', 'YUP', 'uh-huh', 'Uh-huh', 'UH-HUH', 'sure', 'Sure', 'SURE', 'absolutely', 'Absolutely', 'ABSOLUTELY', 'definitely', 'Definitely', 'DEFINITELY', 'certainly', 'Certainly', 'CERTAINLY', 'Yes!', 'YES!', 'yeah!', 'Yeah!', 'YEAH!', 'yep!', 'Yep!', 'YEP!', 'yup!', 'Yup!', 'YUP!', 'uh-huh!', 'Uh-huh!', 'UH-HUH!', 'sure!', 'Sure!', 'SURE!', 'absolutely!', 'Absolutely!', 'ABSOLUTELY!', 'definitely!', 'Definitely!', 'DEFINITELY!', 'certainly!', 'Certainly!', 'CERTAINLY!', 'Yes.', 'YES.', 'yeah.', 'Yeah.', 'YEAH.', 'yep.', 'Yep.', 'YEP.', 'yup.', 'Yup.', 'YUP.', 'uh-huh.', 'Uh-huh.', 'UH-HUH.', 'sure.', 'Sure.', 'SURE.', 'absolutely.', 'Absolutely.', 'ABSOLUTELY.', 'definitely.', 'Definitely.', 'DEFINITELY.', 'certainly.', 'Certainly.', 'CERTAINLY.', ]:
                    response = self.give_ratings(response)
                else:
                    self.giving_recs = False
                    self.rec_index = 0
                    self.current_recs = []
                    self.num_ratings = 0
                    response = "Please enter a movie rating!"
            else:
                titles = self.extract_titles(line)
                if len(titles) > 1:
                    response = "Sorry, please try talking about one movie at a time."
                elif len(titles) == 0:
                    response = "Sorry, please try surrounding the title of the movie in question marks."
                else:
                    i = 0
                    matching = self.find_movies_by_title(titles[i])
                    if len(matching) == 0:
                        response = "I've never heard of \"" + titles[i] + "\", sorry... Tell me about another movie you liked."
                    elif len(matching) > 1:
                        response = "I found more than one movie called \" " + titles[i] + "\". Can you clarify?"
                    else:
                        sentiment = self.extract_sentiment(line)
                        response = self.based_on_sentiment(sentiment, matching[0])
                        response = self.give_ratings(response)

        #I liked Harry Potter
        # I liked mean girls

            
            # response = "I processed {} in starter mode!!".format(line)

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
        #CREATIVE
        if (self.creative):
            title_pattern = '"(.*?)"'
            matches = re.findall(title_pattern, preprocessed_input)
            if len(matches) == 0:
                preprocessed_input = preprocessed_input.lower()

                #Go through every movie in the list, and check if the user mentions it 
                for i in range(len(self.titles)):
                    #first lowercase everything & remove dates
                    candidate = self.titles[i][0].lower()[:-7] 
                    
                    #if title ends with , a , an , the --> move it to the front because that's how the user would write it
                    if(candidate.endswith(", the")):
                        candidate = "the " + candidate[:-5]
                    elif(candidate.endswith(", a")):
                        candidate = "a " + candidate[:-3]
                    elif(candidate.endswith(", an")):
                        candidate = "an " + candidate[:-3]
                    
                    #Separate punctuation marks as separate tokens 
                    candidate_words = re.findall(r'\w+|[^\w\s]+', candidate)
                    input_words = re.findall(r"\b\w+(?:'\w+)?|[^\w\s]", preprocessed_input)
                    
                    #check if movie title is found within the input string (the movie title shouldn't be substring of a word)
                    if any(input_words[i:i+len(candidate_words)] == candidate_words for i in range(len(input_words) - len(candidate_words) + 1)):
                        matches.append(candidate)

            return matches       

        
        #NON-CREATIVE
        else: 
            title_pattern = '"(.*?)"'
            matches = re.findall(title_pattern, preprocessed_input)
            return matches

    def is_phrase_in_string(self, phrase, string):
        pattern = r"\b" + re.escape(phrase) + r"\b"
        return bool(re.search(pattern, string))

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
        #CREATIVE
        if (self.creative):

            #check for exact title match:
            self.creative = False
            exactMatch = self.find_movies_by_title(title)
            self.creative = True 

            input_title = title.lower()
            # input_title = re.sub(r'"([^"]*)"', r'\1', re.sub('\s*\(\d{4}\)$', '', title).lower())
            all_matching = []
            foreign_articles = ['el', 'la', 'il', 'les', 'das', 'die', 'der', 'det']
            input_foreign_title = ""
            foreign_title_exists = False 

            #Converts input foreign title so that it matches foreign title in the
            for foreign_article in foreign_articles:
                if input_title.startswith(foreign_article + ' '):
                    foreign_title_exists = True 
                    input_foreign_title = input_title[len(foreign_article)+1:] + ', ' + foreign_article

            for i in range(len(self.titles)): 

                database_title = ""
                alternate_exists = False
                database_alternate_title = ""

                database_format_expected = re.search('^(.*) \((\d{4})\)$', self.titles[i][0])

                #Apparently some elements in self.titles don't follow the format title (year), so we need to handle the case when the above regex doesn't apply
                if database_format_expected:
                    database_title = database_format_expected.group(1).lower()
                else:
                    continue 

                #handle alternate names
                if "a.k.a." in database_title:
                    alternate_exists = True
                    database_alternate_title = database_title[(database_title.find("a.k.a.")+7):]
                
                #if input title = main title, foreign title, or alternate title append to output list 
                if self.is_phrase_in_string(input_title, database_title) or (alternate_exists and input_title in database_alternate_title) or (input_foreign_title in database_title and foreign_title_exists):
                    all_matching.append(i)
                
            #If the user inputted exact title enclosed in "", return that. Else, return multiple. 
            if not all_matching and exactMatch:
                return exactMatch
            else:
                return all_matching 

        #NON-CREATIVE
        else: 
            #Get year, if year exists
            input_year = ""
            match = re.search('\((\d{4})\)$', title)
            if match:
                input_year = match.group(1)
            #Only movie name. No Year 
            input_title = re.sub('\s*\(\d{4}\)$', '', title)

            #Move articles to the end 
            articles = ['the', 'an', 'a']
            for article in articles:
                if title.lower().startswith(article + ' '):
                    input_title = input_title[len(article)+1:] + ', ' + article.title()
            
            #Go through each element of the titles list and check 
            all_matching = []
            for i in range(len(self.titles)): 
                database_title, database_year = "", ""
                database_format_expected = re.search('^(.*) \((\d{4})\)$', self.titles[i][0])

                #Apparently some elements in self.titles don't follow the format title (year), so we need to handle the case when the above regex doesn't apply
                if database_format_expected:
                    database_title = database_format_expected.group(1)
                    database_year = database_format_expected.group(2)
                else:
                    continue 

                if database_title.lower() == input_title.lower():
                    if input_year == "" or database_year == input_year:
                        all_matching.append(i)
            
            return all_matching
    
    def stem_all_words(self, word_list):
        stemmed_list = []
        stemmer = PorterStemmer()
        for word in word_list:
            stemmed_list.append(stemmer.stem(word))

        return stemmed_list

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
            stemmer = PorterStemmer() 

            #manually picked words denoting strong sentiments / intensifier 
            strong_positive_words = ["love", "joy", "happiness", "excitement", "pleasure", "fun", "hope", "kindness", "grateful", "blissful", "blessed", "content", "delight", "euphoria", "giddy", "glad", "graceful", "happy", "heavenly", "inspired", "jubilant", "overjoyed", "peaceful", "radiant", "serene", "thankful", "thrilled", "uplifted", "victorious", "wonderful"]
            strong_positive_words_stemmed = self.stem_all_words(strong_positive_words)

            strong_negative_words = ["hate", "anger", "fear", "grief", "sadness", "disgust", "anxiety", "jealousy", "frustration", "miserable", "anguish", "bitter", "depressed", "despair", "dread", "enraged", "gloomy", "guilty", "heartbroken", "hostile", "inferior", "melancholy", "mortified", "nervous", "offended", "resentful", "sorrowful", "terrible", "unhappy", "wretched"]
            strong_negative_words_stemmed = self.stem_all_words(strong_negative_words)

            #Not stemming intensifier words because "amazingly" is an intensifier word, but "amazing" has positive sentiment. ex: amazingly bad --> very very bad
            intensifier_words = ["absolutely", "amazingly", "completely", "deeply", "enormously", "exceedingly", "extremely", "fantastically", "immensely", "incredibly", "intensely", "positively", "profoundly", "remarkably", "seriously", "super", "totally", "truly", "unbelievably", "utterly", "atrociously", "dreadfully", "entirely", "horribly", "unbearably", "really", "very", "!"]
            

            #If any of the negation words is seen, multply -1 to the sentiment of the following words found in the lexicon
            negation_words = ["not", "don't", "can't", "no", "never",  "won't", "didn't", "isn't", "wasn't", "couldn't", "shouldn't", "wouldn't", "rarely", "seldom", "neither", "nor"]
            negation_boolean = False

            sentiment_score = 0 
            count = 0 
            threshold = 0.3
            strong_boolean = False 

            #below tokenizing treats a punctuation as a separate toekn, so sentences like "Hey, how are you?" tokenizes
            #into ["Hey", ",", "how", "are", "you", "?"] NOT ["Hey,", "how", "are", "you?"]
            
            #Remove title case 1) quotation marks 
            token_words = re.sub(r'".*?"', '', preprocessed_input.lower())

            #Remove title case 2) no quotation marks 
            if(token_words == preprocessed_input.lower()):
                if self.extract_titles(token_words):
                    remove_title_index0 = self.extract_titles(preprocessed_input)
                    remove_title_1 = remove_title_index0[0]
                    token_words = re.sub(remove_title_1, '', preprocessed_input.lower())
            
            token_words = re.findall("\w+(?:[-']\w+)*|[^\w\s]", token_words)

            for word in token_words:
                #Negation word itself doesn't have any sentiment value, so move on the next word 
                if word in negation_words:
                    negation_boolean = True
                    continue

                if word in intensifier_words:
                    strong_boolean = True
                    continue

                word_stemmed = stemmer.stem(word)
                if word_stemmed in self.sentiment:
                    count+=1
                    
                    if word_stemmed in strong_positive_words_stemmed or word_stemmed in strong_negative_words_stemmed:
                        strong_boolean = True 

                    if negation_boolean:
                        sentiment_score -= self.numeric_sentiment_word(word_stemmed)
                    else:
                        sentiment_score += self.numeric_sentiment_word(word_stemmed)
                
            if count > 0:
                sentiment_score = sentiment_score / count
            
            if negation_boolean and strong_boolean:
                sentiment_score = 0
            elif sentiment_score > threshold:
                if strong_boolean:
                    sentiment_score = 2
                else:
                    sentiment_score = 1
            elif sentiment_score < (threshold * -1):
                if strong_boolean:
                    sentiment_score = -2
                else:
                    sentiment_score = -1
            else:
                sentiment_score = 0 

            return sentiment_score

        else:
        #If any of the negation words is seen, multply -1 to the sentiment of the following words found in the lexicon
        
            negation_words = ["not", "don't", "can't", "no", "never",  "won't", "didn't", "isn't", "wasn't", "couldn't", "shouldn't", "wouldn't", "rarely", "seldom", "neither", "nor"]
            negation_boolean = False

            stemmer = PorterStemmer() 

            sentiment_score = 0 
            count = 0 
            threshold = 0.3

            #below tokenizing treats a punctuation as a separate toekn, so sentences like "Hey, how are you?" tokenizes
            #into ["Hey", ",", "how", "are", "you", "?"] NOT ["Hey,", "how", "are", "you?"]
            #Remove title 
            token_words = re.sub(r'".*?"', '', preprocessed_input.lower())
            token_words = re.findall("\w+(?:[-']\w+)*|[^\w\s]", token_words)

            for word in token_words:
                #Negation word itself doesn't have any sentiment value, so move on the next word 
                if word in negation_words:
                    negation_boolean = True
                    continue

                word_stemmed = stemmer.stem(word)
                if word_stemmed in self.sentiment:
                    count+=1
                    if negation_boolean:
                        sentiment_score -= self.numeric_sentiment_word(word_stemmed)
                    else:
                        sentiment_score += self.numeric_sentiment_word(word_stemmed)
                
            if count > 0:
                sentiment_score = sentiment_score / count
            
            if sentiment_score > threshold:
                sentiment_score = 1
            elif sentiment_score < (threshold * -1):
                sentiment_score = -1
            else:
                sentiment_score = 0 
            return sentiment_score
    
    def numeric_sentiment_word (self, word):
        if self.sentiment[word] == "pos":
            return 1
        elif self.sentiment[word] == "neg":
            return -1 
        
    def update_previous_indices(self, movie_sentiments, idx, sentiment_val):
        idx_loop_back = idx - 1
        while idx_loop_back >= 0 and movie_sentiments[idx_loop_back] == 0:
            movie_sentiments[idx_loop_back] += sentiment_val
            idx_loop_back -= 1

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
                           'I liked both "Titanic (1997)" and "Ex Machina", but not "David".'))
          print(sentiments) // prints [("Titanic (1997)", 1), ("Ex Machina", 1)]

        :param preprocessed_input: a user-supplied line of text that has been
        pre-processed with preprocess()
        :returns: a list of tuples, where the first item in the tuple is a movie
        title, and the second is the sentiment in the text toward that movie
        """
        title_list = self.extract_titles(preprocessed_input)
        # not sure if needed
        movies_idx_title = [0 for _ in range(len(title_list))]
        for idx, title in enumerate(title_list):
            movies_idx_title[idx] = (preprocessed_input.find(title), title)
        movies_idx_title.sort()
        # print('movies_idx_title', movies_idx_title)
        movie_sentiments = np.zeros(len(title_list))
        movie_names = [pair[1] for pair in movies_idx_title]
        # print('movies_idx', movies_idx_title)
        # print('movie_names', movie_names)
        # print('sentiment', movie_sentiments)
        delims = ["but", "But", "however", "However", "yet", "Yet", "nevertheless", 
                  "Nevertheless", "nonetheless", "Nonetheless", "although", "Although", 
                  "despite", "Despite", "whereas", "Whereas", "conversely", "Conversely", 
                  "on the other hand", "On the other hand", "contrast", "In contrast"]
        prev_idx = 0
        for idx, pair in enumerate(movies_idx_title):
            movie_idx, movie_title = pair
            substr = preprocessed_input[prev_idx:movie_idx]
            included_delims = [delim for delim in delims if (delim in substr)]
            if not bool(included_delims):
                # print('substr', substr)
                spec_sentiment = self.extract_sentiment(substr)
                # print('spec_sentiment', spec_sentiment)
                if spec_sentiment == 0:
                    if idx > 0: # Ex) I liked "Titanic" and "Wall-E" and "Maze"
                        movie_sentiments[idx] += movie_sentiments[idx - 1]
                else:
                    movie_sentiments[idx] += spec_sentiment
                    self.update_previous_indices(movie_sentiments, idx, spec_sentiment)
            else:
                # Reason for splitting: Ex) "I, Robot" was good, but I did not like "Ex Machina"
                
                # print("included_delims", included_delims)
                split_phrases = substr.split(included_delims[0])
                first_phrase, second_phrase = split_phrases[0], split_phrases[-1]
                # print('first phrase', first_phrase, 'second_phrase', second_phrase)
                first_sentiment, second_sentiment = self.extract_sentiment(first_phrase), self.extract_sentiment(second_phrase)
                # print('first sentiment', first_sentiment, 'second sentimnet', second_sentiment)
                # print('first', first_sentiment, 'second', second_sentiment)
                if idx > 0:
                    if first_sentiment != 0:
                        self.update_previous_indices(movie_sentiments, idx, first_sentiment)
                mult_val = 0
                idx_loop_back_2 = idx - 1
                while idx_loop_back_2 >= 0:
                    if movie_sentiments[idx_loop_back_2] < 0:
                        mult_val = -1
                        break
                    elif movie_sentiments[idx_loop_back_2] > 0:
                        mult_val = 1
                        break
                    idx_loop_back_2 -= 1
                movie_sentiments[idx] = mult_val * -1 if mult_val != 0 else second_sentiment
            
            prev_idx = movie_idx + len(movie_title) # update prev_idx
        
        # last one with prev_idx for cases like Ex) "titanic" and "wall-E" were good
        last_substr = preprocessed_input[prev_idx:]
        last_sentiment = self.extract_sentiment(last_substr)
        movie_sentiments[-1] += last_sentiment
        self.update_previous_indices(movie_sentiments, len(movie_sentiments) - 1, last_sentiment)

        # print('sentiment before calibration', movie_sentiments)
        res = []
        for idx in range(len(movie_names)):
            final_sentiment = 0
            if movie_sentiments[idx] < 0:
                final_sentiment = -1
            elif movie_sentiments[idx] > 0:
                final_sentiment = 1
            res.append((movie_names[idx], final_sentiment))
        # print('res after calibration', res)    
        return res
        
    
    # Helper function for find_movies_closet_to_title
    def get_edit_dist(self, input_title, database_title):
        # print('input', input_title, 'data', database_title) # debugging
        DP = np.zeros((len(input_title) + 1, len(database_title) + 1), dtype=int)
        DP[[0],:] = np.arange(len(database_title) + 1)
        DP[:,[0]] = [[i] for i in range(len(input_title) + 1)]
        # print(DP) # debugging
        for i in range(1, len(input_title) + 1):
            for j in range(1, len(database_title) + 1):
                # print('i', i, 'j', j) # debugging
                DP[i][j] = min(DP[i - 1][j] + 1, 
                               DP[i][j - 1] + 1,
                               DP[i - 1][j - 1] + (2 if input_title[i - 1] != database_title[j - 1]  # need -1 as we are accessing 0-indexed strings
                                                   else 0))
        # print(DP) # debugging
        return DP[-1][-1]

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
        hasYear = False
        match = re.search('\((\d{4})\)$', title)
        if match:
            hasYear = True
        # Only movie name. No Year 
        input_title = re.sub('\s*\(\d{4}\)$', '', title)
        
        articles = ['the', 'an', 'a']
        for article in articles:
            if title.lower().startswith(article + ' '):
                input_title = input_title[len(article)+1:] + ', ' + article.title()
                if hasYear:
                    title = input_title + ' (' + str(match.group(1)) + ')'
                # print('input_title', input_title, 'title', title)

        #Go through each element of the titles list and check 
        all_matching = []
        for i in range(len(self.titles)): 
            database_title = ""
            database_format_expected = re.search('^(.*) \((\d{4})\)$', self.titles[i][0])

            #Apparently some elements in self.titles don't follow the format title (year), so we need to handle the case when the above regex doesn't apply
            if database_format_expected:
                database_title = self.titles[i][0] if hasYear else database_format_expected.group(1)
                input_title = title if hasYear else input_title
                # database_title = database_format_expected.group(1)
            else:
                continue 
            
            edit_dist = self.get_edit_dist(input_title.lower(), database_title.lower())
            # edit_dist = self.get_edit_dist("Sleeping Beaty", "Sleeping Beauty") # debugging
            # print(edit_dist)
            # break
            if edit_dist < max_distance:
                all_matching = [i]
                max_distance = edit_dist
            elif edit_dist == max_distance:
                all_matching.append(i)
                
        return all_matching

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
        clarification = clarification.rstrip(".")
        returnIndices = []
        returnIndex = []
        exactMatch = False

        self.creative = False
        if len(self.find_movies_by_title(clarification))==1:
            returnIndex.append(self.find_movies_by_title(clarification)[0])
            exactMatch = True
                
        self.creative = True 

        for candidate in candidates:
            if self.is_phrase_in_string(clarification.lower(), self.titles[candidate][0].lower() ):
                returnIndices.append(candidate)
        
        if exactMatch:
            return returnIndex
        else:
            return returnIndices
        


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

        positive = np.where(ratings > threshold)
        negative = np.where((ratings <= threshold) & (ratings != 0))
        
        binarized_ratings[positive] = 1
        binarized_ratings[negative] = -1

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
        normu = np.linalg.norm(u)
        normv = np.linalg.norm(v)
        similarity = 0
        if normu != 0 and normv != 0:
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

        movies_rated_by_user = set(np.nonzero(user_ratings)[0])
        rx = np.full(shape = len(user_ratings), fill_value = float('-inf'), dtype=float)
        
        for mov_id_1 in range(len(user_ratings)):
            if mov_id_1 not in movies_rated_by_user:
                sim, ratings = np.array([]), np.array([])
                for mov_id_2 in movies_rated_by_user:
                    cos_sim = self.similarity(ratings_matrix[mov_id_1], ratings_matrix[mov_id_2])
                    sim = np.append(sim, cos_sim)
                    ratings = np.append(ratings, user_ratings[mov_id_2])
                rx[mov_id_1] = np.dot(sim, ratings) # use dot product for faster computation

        # print('recommendations before sort:', rx)
        recommendations = list((-rx).argsort()[:k]) # need to typecast to list for sanity check
        # print('recommendations after sort:', recommendations)

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
        This is our bot that recommends movies given some ratings! In creative mode, it takes on the persona of Benedict Cumberbatch's Sherlock Holmes, who can be quite arrogant/rude at times.
        """
    

        


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')