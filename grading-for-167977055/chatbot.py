# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
from datetime import date
import util
import porter_stemmer
p = porter_stemmer.PorterStemmer()
import numpy as np
import random
import re


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'Alto'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        #stem the dictionary of words/sentiments
        self.stemmed_sentiment = {}
        for key in self.sentiment:
            key_stem = p.stem(key, 0, len(key)-1)
            self.stemmed_sentiment[key_stem] = self.sentiment[key]

        # create dicts for find_movies_by_title()
        self.titles_without_date = {}
        self.titles_only_date = {}
        self.reg_title_key = 'regular'
        self.alt_title_key = 'alternate'
        date_regex = "(\d{4})"
        date_regex_paren = "([(]\d{4}[)])"
        alternate_title_regex = "([(][^()]*[)])"
        aka_regex = "(a\.*k\.*a\.*\s)"

        for i in range(len(self.titles)):
            title_dic = {}
            title_entry = self.titles[i][0].lower()
            if re.search(date_regex_paren, title_entry):
                title_entry = title_entry.replace(' ' + re.search(date_regex_paren, self.titles[i][0]).group(1), '')
                self.titles_only_date[i] = re.search(date_regex_paren, self.titles[i][0]).group(1)
            elif re.search(date_regex, self.titles[i][0]):
                title_entry = title_entry.replace(' ' + re.search(date_regex, self.titles[i][0]).group(1), '')
                self.titles_only_date[i] = re.search(date_regex, self.titles[i][0]).group(1)
            else:
                self.titles_only_date[i] = ""
        
            
            if re.findall(alternate_title_regex, title_entry):
                regular_title = title_entry
                for match in re.findall(alternate_title_regex, title_entry):
                    if re.search(aka_regex, match):
                        match = match.replace(re.search(aka_regex, match).group(1), '')
                    regular_title = regular_title.replace(' ' + re.search(alternate_title_regex, regular_title).group(1), '')
                    alternate_title = match[1:-1]
                    title_dic[self.alt_title_key] = alternate_title
                title_dic[self.reg_title_key] = regular_title
            else:
                title_dic[self.reg_title_key] = title_entry
                title_dic[self.alt_title_key] = ""
            
            self.titles_without_date[i] = title_dic
                

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings, threshold=2.5)

        self.unsure_check = False
        self.unsure = ""
        self.liked = []
        self.disliked = []
        self.rec = False
        self.rec_already = []
        self.rec_index = 0
        self.rec_k = 10
        
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
        greeting_message = ""
        if self.creative:
            greeting_message = "Well, well, well, darling! It's Edna Mode. How lovely to see you again. Now, let's talk about movies, shall we? I'm going to recommend a movie to you, but first, I simply must ask about your taste in films. So, do tell me, darling, about a movie that you have seen and what you thought of it. Remember, darling, honesty is always in style!"
        else:
            greeting_message = "Hi! I'm " + self.name + " I'm going to recommend a movie to you. First I will ask you about your taste in movies. Tell me about a movie that you have seen."

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
        goodbye_message = ""
        if self.creative:
            goodbye_message = "It was lovely chatting with you, darling! Have a fabulous day!"
        else:
            goodbye_message = "Nice talking to you! Have a nice day!"

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return goodbye_message

    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################

    def res_random(self, options):
        response = random.choice(options)
        return response

    def res_make_rec(self):
        user_ratings = np.zeros(len(self.titles))
        for like in self.liked:
            user_ratings[like] = 1
        for dislike in self.disliked:
            user_ratings[dislike] = -1
        if (self.rec_index > self.rec_k):
            self.rec_k += 10
        recs = self.recommend(user_ratings, self.ratings, k=self.rec_k, creative=False)
        suggest_options = []
        if self.creative:
            suggest_options = [
                "I strongly advise that you feast your eyes upon \"{}\", darling!",
                "It would behoove you to witness the brilliance of this film called \"{}\", my dear!",
                "Do yourself a favor and indulge in the splendor of the motion picture that is \"{}\"!",
                "It is imperative that you experience the sheer magnificence of this movie called \"{}\", my dear!",
                "I insist that you partake in the spectacle of \"{}\", darling!",
                "Trust me, darling, you simply must see this cinematic masterpiece by the name \"{}\"!",
                "You would be remiss to miss out on the brilliance of \"{}\", my dear!",
                "I wholeheartedly recommend that you bask in the glory of \"{}\", darling!",
                "It is absolutely crucial that you feast your eyes upon this cinematic delight called \"{}\", my dear!",
                "Believe me, darling, you won't regret immersing yourself in the wonder of the film \"{}\"!"]

        else:
            suggest_options = [
                "I suggest you watch \"{}\".",
                "I'd reccomend the movie \"{}\".",
                "You might want to check out \"{}\".",
                "\"{}\" is a solid new movie choice.",
                "I think \"{}\" might interest you.",
                "I think you'd like \"{}\".",
                "\"{}\" might be worth your time!"
            ]
        suggest = self.res_random(suggest_options)
        response = suggest.format(self.titles[recs[self.rec_index]][0])
        self.rec_index += 1
        another_options = []
        if self.creative:
            another_options = ["Are you ready for another dose of cinematic excellence, darling?",
            "Shall I delight you with yet another recommendation?",
            "Can I interest you in another cinematic masterpiece?",
            "May I suggest another exquisite movie for your viewing pleasure, my dear?",
            "Would you care to indulge in another magnificent film, darling?",
            "Are you eager for another recommendation from yours truly?",
            "Shall I bestow upon you another gem of the silver screen?",
            "Can I tempt you with another marvelous motion picture, my dear?",
            "Darling, would you like to experience another breathtaking film?",
            "May I present to you another spectacular suggestion for your cinematic enjoyment?"]
        else:
            another_options = [
                "Would you like to hear another recommendation?",
                "Would you be interested in hearing about another movie?",
                "Do you want to hear about another movie?",
                "Do you want to hear another suggestion?",
                "Can I give another reccomendatioin?",
                "Want to hear another movie reccomendation?"
            ]
        another = self.res_random(another_options)
        response += " " + another + "(Or enter :quit if you're done.)"
        return response

    def res_cont_rec(self, line):
        line = line.lower()
        line = line.strip('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')
        yes = ["yes", "yeah", "yup", "y", "sure", "ok", "okay"]
        if (line in yes):
            response = self.res_make_rec()
            return response
        else:
            unsure_options = []
            if self.creative:
                unsure_options = [
                    "I'm afraid I didn't quite catch that, darling.",
                    "Pardon me, my dear, but I'm not quite certain what you meant.",
                    "I must apologize, darling, but I didn't quite understand what you said.",
                    "Could you please repeat that, my dear? I'm afraid I didn't quite grasp it.",
                    "I'm not quite sure I followed you there, darling. Could you please clarify?",
                    "Forgive me, my dear, but I'm not entirely certain I understood what you were saying.",
                    "I'm afraid I'm a bit confused, darling. Could you please repeat yourself?",
                    "I beg your pardon, my dear, but I'm not quite sure I heard you correctly.",
                    "I must confess, darling, that I'm a bit puzzled by what you said.",
                    "I'm afraid I didn't quite get the gist of what you were saying, my dear."]
            else:
                unsure_options = [
                    "I'm not quite sure what you said.",
                    "I'm sorry, I didn't catch that.",
                    "I didn't quite understand what you said.",
                    "I'm having trouble understanding what you said.",
                    "Sorry, I'm not sure what you said."
                ]
            unsure = self.res_random(unsure_options)
            another_options = []
            if self.creative:
                another_options =  [
                    "Are you ready for another dose of cinematic excellence, darling?",
                    "Shall I delight you with yet another recommendation?",
                    "Can I interest you in another cinematic masterpiece?",
                    "May I suggest another exquisite movie for your viewing pleasure, my dear?",
                    "Would you care to indulge in another magnificent film, darling?",
                    "Are you eager for another recommendation from yours truly?",
                    "Shall I bestow upon you another gem of the silver screen?",
                    "Can I tempt you with another marvelous motion picture, my dear?",
                    "Darling, would you like to experience another breathtaking film?",
                    "May I present to you another spectacular suggestion for your cinematic enjoyment?"]
            else:
                another_options = [
                    "Would you like to hear another recommendation?",
                    "Would you be interested in hearing about another movie?",
                    "Do you want to hear about another movie?",
                    "Do you want to hear another suggestion?",
                    "Can I give another reccomendatioin?",
                    "Want to hear another movie reccomendation?",
                ]
            another = self.res_random(another_options)
            response = unsure + " " + another  + " Remember to enter :quit if you're done."
            return response
    
    def res_sentiment(self, line, movie, id):
        sentiment = self.extract_sentiment(self.preprocess(line))
        if sentiment > 0:
            liked_options = []
            if self.creative:
                liked_options = [
                    "You liked \"{}\"? How splendid, darling!",
                    "My dear, you have exquisite taste in films. \"{}\" is a marvel.",
                    "How marvelous, my dear! \"{}\" is truly a cinematic delight.",
                    "I see you're enjoying the brilliance of \"{}\", darling. A wise choice.",
                    "You enjoyed \"{}}\"? I approve, my dear.",
                    "It sounds like you enjoyed \"{}\"? A brilliant choice, darling.",
                    "How delightful, my dear! You're savoring the magnificence of \"{}\".",
                    "It seems like you liked \"{}\"? You never cease to impress me, darling.",
                    "\"{}}\"? Excellent movie to enjoy. Indulge away, my dear.",
                    "\"{}\"? I loved it as well. An inspired selection, darling."
                    ]
            else:
                liked_options = [
                    "It sounds like you liked \"{}\". Thank you!",
                    "Glad you enjoyed \"{}\".",
                    "Sounds like you thought \"{}\" was a great movie. Thank you!",
                    "You liked \"{}\". Thank you!",
                    "Ok, you liked \"{}\".",
                    "I'm hearing that you enjoyed \"{}\"."
                ]
            liked = self.res_random(liked_options)
            response = liked.format(movie)
            if id not in self.liked:
                self.liked.append(id)
            self.unsure_check = False
        elif sentiment < 0:
            disliked_options = []
            if self.creative:
                disliked_options = [
                    "You didn't like \"{}\"? How unfortunate, darling.",
                    "It seems \"{}\" didn't quite hit the mark, my dear.",
                    "How disappointing that \"{}\" didn't live up to your expectations, my dear.",
                    "I see that \"{}\" wasn't quite your style, darling.",
                    "It sounds like you didn't like \"{}\". Not quite your cup of tea, I take it, my dear?",
                    "Alas, \"{}\" failed to impress you, darling.",
                    "\"{}\" wasn't very good? A swing and a miss, it appears, my dear.",
                    "Regrettable, my dear, that \"{}\" didn't suit your taste.",
                    "It seems that \"{}\" wasn't for you, my dear.",
                    "You didn't enjoy\"{}\" ? A pity it didn't meet your standards, darling."
                    ]
            else:
                disliked_options = [
                    "It sounds like you did not like \"{}\". Thank you!",
                    "Sorry you didn't enjoy \"{}\".",
                    "Sounds \"{}\" wasn't really your cup of tea. Thank you!",
                    "You did not liked \"{}\". Thank you!",
                    "Ok, you didn't like watching \"{}\".",
                    "I'm hearing that you didn't like \"{}\".",
                    "It seems like \"{}\" wasn't really a movie you liked."
                ]
            disliked = self.res_random(disliked_options)
            response = disliked.format(movie)
            if id not in self.disliked:
                self.disliked.append(id)
            self.unsure_check = False
        else:
            unsure_options = []
            if self.creative:
                unsure_options = [
                    "My apologies, dear, I'm not quite certain if \"{}\" met your approval.",
                    "I'm afraid I'm not quite sure if you enjoyed \"{}\", darling.",
                    "Pardon me, my dear, but I'm not entirely sure if you found \"{}\" to your liking.",
                    "I'm sorry, darling, but I'm not certain if \"{}\" was your cup of tea.",
                    "I see that you watched \"{}\", but I'm not quite sure if you liked it, my dear.",
                    "My apologies, my dear, but I'm uncertain if \"{}\" was to your taste.",
                    "I'm afraid I'm not quite sure if you were satisfied with \"{}\", darling.",
                    "I'm sorry, my dear, but I'm not quite sure if \"{}\" met your expectations.",
                    "I see that you watched \"{}\", but forgive me if I'm mistaken in thinking you didn't enjoy it, my dear.",
                    "Pardon me, darling, but I'm not quite sure if you were pleased with \"{}\"."
                    ]
            else: 
                unsure_options = [
                    "I'm sorry, I'm not quite sure if you liked \"{}\".",
                    "I'm not sure if you enjoyed \"{}\".",
                    "Sorry, I'm not entirely clear on your feelings about \"{}\".",
                    "Hmmm I'm having diffficulty determining if you liked \"{}\".",
                    "Hmmm I'm having trouble discerning \"{}\" was a movie you liked or disliked.",
                    "Sorry, its unclear to me if you liked \"{}\".",
                    "Sorry, I'm not so sure whether or not \"{}\" was a movie you liked. "
                ]
            unsure = self.res_random(unsure_options)
            response = unsure.format(movie)
            clarify_options = []
            if self.creative:
                clarify_options = [
                        "Tell me, dear, more about \"{}\"?",
                        "\"{}\" has stirred you. Share more?",
                        "\"{}\" caught your attention. Elaborate?",
                        "Speak up, darling! Thoughts on \"{}\"?",
                        "Expand on your thoughts about \"{}\", my dear.",
                        "\"{}\" sparked a reaction. Tell me more.",
                        "I sense there's more to \"{}\". Do elaborate!",
                        "Thoughts on \"{}\"? I'm all ears, darling.",
                        "More about \"{}\", please, my dear.",
                        "\"{}\" left an impression. Care to share?"
                    ]
            else:
                clarify_options = [
                    "Tell me more about \"{}\".",
                    "Could you elaborate on your feelings about \"{}\"?",
                    "I'd love to here more on how you felt watching \"{}\".",
                    "Maybe you could clarify if you liked watching \"{}\"?",
                    "Lets here more about your feelings watching \"{}\".",
                    "How did feel watching \"{}\"?"
                ]
            clarify = self.res_random(clarify_options)
            response += " " + clarify.format(movie)
            self.unsure = id
            self.unsure_check = True
        return response
    
    def res_check_line_for_title(self, line_titles, line):
        if (line_titles == []):
            if self.creative:
                # identifying and responding to emotions
                emotions_dict = {
                    "Darling, pray tell, have I aroused your ire? If so, I offer my sincerest apologies!" : ['angry', 'anger', 'mad', 'infuriated', 'outraged', 'outrage', 'fuming', 'furious', 'seething', 'frustrated'],
                    "My dear, I regret to hear that you're feeling blue. Perhaps, a cinematic suggestion from me shall uplift your spirits!" : ['sad', 'melancholy', 'depressed', 'unhappy', 'miserable', 'upset', 'blue'],
                    "Oh, what a delight! Learning of your joy brings me tremendous pleasure as well!" : ['happy', 'joyful', 'cheerful', 'content', 'overjoyed', 'exuberant', 'jolly', 'excited', 'delighted'],
                    "My dear, stress is simply not becoming of your flawless complexion. I implore you to take a break, unwind, and indulge in some well-deserved relaxation." : ['stress', 'stressed', 'burnt', 'anxious'],
                    "My dear, the sole entity that deserves your apprehension is fear itself." : ['fear', 'fearful', 'scared', 'frightened', 'petrified', 'terrified', 'apprehensive']
                }
                for key, value in emotions_dict.items():
                    for emotion_synonym in value:
                        if emotion_synonym in line.lower():
                            return key
                
                # responding to arbitrary input
                arbitary_input_dict = {
                    "can you" : "Dearest, being a chatbot, I'm incapable of \"{}\" or suggesting anything beyond films. However, if you desire a recommendation, kindly enlighten me on your cinematic preferences, what pleases or displeases you?",
                    "what is" : "Alas, my dear, being a chatbot limits me to offering nothing beyond cinematic recommendations. I cannot enlighten you with any information on \"{}\".",
                    "what was" : "Alas, my dear, being a chatbot limits me to offering nothing beyond cinematic recommendations. I cannot enlighten you with any information on \"{}\".",
                    "what did" : "Alas, my dear, being a chatbot limits me to offering nothing beyond cinematic recommendations. I cannot enlighten you with any information on \"{}\".",
                    "explain" : "I yearn to elucidate \"{}\" for you, darling. However, I must remind you that I'm merely a chatbot! Why don't you ask me for some movie suggestions instead?",
                    "when is" : "Alas, my dear, I'm oblivious to the timeframe of \"{}\". My sense of time is limited to the release dates of certain movies!",
                    "when was" : "Alas, my dear, I'm oblivious to the timeframe of \"{}\". My sense of time is limited to the release dates of certain movies!",
                    "when did" : "Alas, my dear, I'm oblivious to the timeframe of \"{}\". My sense of time is limited to the release dates of certain movies!"
                }
                for key, value in arbitary_input_dict.items():
                    if line.lower().startswith(key):
                        return value.format(line.lower())
            misunderstand_options = []
            if self.creative:
                misunderstand_options = [
                    "I'm afraid I didn't quite catch that, darling.",
                    "Pardon me, my dear, but I'm not quite certain what you meant.",
                    "I must apologize, darling, but I didn't quite understand what you said.",
                    "Could you please repeat that, my dear? I'm afraid I didn't quite grasp it.",
                    "I'm not quite sure I followed you there, darling. Could you please clarify?",
                    "Forgive me, my dear, but I'm not entirely certain I understood what you were saying.",
                    "I'm afraid I'm a bit confused, darling. Could you please repeat yourself?",
                    "I beg your pardon, my dear, but I'm not quite sure I heard you correctly.",
                    "I must confess, darling, that I'm a bit puzzled by what you said.",
                    "I'm afraid I didn't quite get the gist of what you were saying, my dear."]
            else:
                misunderstand_options = [
                    "I'm not quite sure what you said.",
                    "I'm sorry, I didn't catch that.",
                    "I didn't quite understand what you said.",
                    "I'm having trouble understanding what you said.",
                    "Sorry, I'm not sure what you said.",
                    "Sorry, I don't understand.",
                    "Hmmm I'm a bit lost...."
                ]
            misunderstand = self.res_random(misunderstand_options)
            tell_options = []
            if self.creative:
                tell_options = ["Share with me, darling, a movie you've witnessed?",
                    "I need to hear about a movie you've seen, my dear.",
                    "Speak up, my dear! Which movie has caught your eye?",
                    "Tell me about a film you've witnessed, darling.",
                    "Which movie left a lasting impression on you, my dear?",
                    "I demand to know, darling, tell me about a movie you've seen",
                    "Share with me a film you've witnessed, darling. I insist!",
                    "Don't keep me waiting, my dear. Tell me of a movie you've seen."]
            else:
                tell_options = [
                    "Tell me about a movie you've seen.",
                    "Can you describe a movie that you recently watched?",
                    "Have you seen any movies lately? Tell me about one.",
                    "What was the last movie you saw? Could you tell me about it?",
                    "I'm curious, could you share your thoughts on a movie you've seen recently?",
                    "Could you talk about a movie that you have seen?",
                    "Have you seen any movies that have really stood out to you? Can you tell me about one of them?",
                ]
            tell = self.res_random(tell_options)
            response = misunderstand + " " + tell

            return response
        elif (len(line_titles) > 1):
            limit_options = []
            if self.creative:
                limit_options = ["Oh, darling, let's not get ahead of ourselves. One movie at a time, please!",
                "Let's stay on track, my dear. One movie at a time, please proceed.",
                "Focus, darling, one movie at a time. Please share your thoughts.",
                "One movie at a time, my dear. Let's not overwhelm ourselves.",
                "Steady now, my dear. One movie at a time, please proceed.",
                "Let's not lose sight of our objective, darling. One movie at a time, please!",
                "Don't rush, my dear. One movie at a time, let's stay focused.",
                "One movie at a time, my dear. Please proceed with your thoughts.",
                "Patience, darling, let's not bite off more than we can chew. One movie at a time, please!",
                "Let's maintain our focus, my dear. One movie at a time, please proceed."]
            else:
                limit_options = [
                    "One movie at a time, please. Maybe talk about the first",
                    "Let's focus on one movie at a time. Go ahead.",
                    "Can we talk about one movie at a time?",
                    "We'll go one by one. Maybe with the first movie, please.",
                    "Let's take it one movie at a time. What's one movie you have thoughts on?",
                    "Please tell me about one movie at a time. Go ahead",
                    "We'll go through them all, but one at a time. Let's hear about one first!",
                    "I'm interested in all of them, but let's focus on one at a time. You can start with the first that comes to mind",
                    "I'd love to hear about all of the movies, but lets start with one at a time. Go ahead"
                ]
            limit = self.res_random(limit_options)
            response = limit
            return response
        return ""
    
    def res_check_title_for_movie(self, movie_pre, ids):
        if (ids == []):
            unknown_options = []
            if self.creative:
                unknown_options = [
                    "I'm terribly sorry, darling, but I haven't had watched \"{}\". Could you tell me about another movie you've seen?",
                    "Oh dear, I'm not familiar with \"{}\". Can you please tell me about a different movie you watched?",
                    "I'm afraid I'm not acquainted with \"{}\". Can you elaborate on another movie you've seen?",
                    "My apologies, darling, but I'm not familiar with \"{}\". Please tell me about a different movie you've watched.",
                    "Darling, I'm not quite sure what \"{}\" is. Could you share a different movie you've seen?",
                    "I'm sorry, I haven't had the pleasure of watching \"{}\". Can you tell me about another movie you enjoyed?",
                    "Oh dear, I'm not familiar with that one. Could you perhaps share your thoughts on a different movie?",
                    "I'm afraid I haven't seen \"{}\" yet. Can you please tell me about another movie you've watched?",
                    "My apologies, I'm not acquainted with that movie. Please share your thoughts on a different one.",
                    "I'm sorry, darling, but I haven't seen \"{}\". Could you please tell me about another movie you've seen?"
                    ]
            else:
                unknown_options = [
                    "Oh....  I'm not familiar with \"{}\". Could you tell me about a different movie you watched?",
                    "I'm sorry, I haven't heard of \"{}\" before. Can you tell me about a different one?",
                    "I'm not familiar with \"{}\". How about telling me about another movie you've seen?",
                    "I'm sorry, I don't know \"{}\". Can you recommend another movie you liked or disliked?",
                    "I've never heard of that \"{}\". Can you share your thoughts on another movie you one?",
                    "Hmm... I don't recognize \"{}\". Could you tell me about a different movie you found interesting?",
                    "I'm not familiar with \"{}\", sorry. How about telling me about another movie?",
                    "I'm sorry, I haven't seen \"{}\". Can you tell me about another movie?"
                ]
            unknown = self.res_random(unknown_options)
            response = unknown.format(movie_pre)
            return response
        elif (len(ids) > 1):
            multiple_options = []
            if self.creative:
                multiple_options = [
                        "Darling, I need a bit of clarification. There are multiple movies called \"{}\". Can you specify which one you mean?",
                        "I'm afraid there are several movies called \"{}\". Which one are you referring to?",
                        "Oh dear, there are a few movies under \"{}\". Could you specify which one you mean?",
                        "Hmm, I need a bit more information. There are multiple movies called \"{}\". Can you be more specific?",
                        "Multiple movies called \"{}\", darling. Could you clarify which one you're referring to?",
                        "Dear, there are a few movies under \"{}\". Can you specify which one you're talking about?",
                        "I'm sorry, there are a few films that go by \"{}\". Could you please clarify which one you're referring to?",
                        "Multiple movies called \"{}\", I'm afraid. Could you be more specific?"
                        ]
            else:
                multiple_options = [
                    "I see there are multiple movies called \"{}\". Can you tell me which you're referring to?",
                    "Hmm... There are a few movies that go by \"{}\". Can you specify which one you mean?",
                    "I found multiple movies called \"{}\". Can you clarify which one you're talking about?",
                    "There are a couple of movies under \"{}\". Could you tell me which one you're referring to?",
                    "Oh no, I found more than one movie called \"{}\". Can you specify which one you're talking about?",
                    "There are a few movies that share the \"{}\". Can you tell me which one you're referring to?",
                ]
            multiple = self.res_random(multiple_options)
            response = multiple.format(movie_pre)
            return response
        return ""
    
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
        if False:
            response = "I processed {} in creative mode!!".format(line)
        else: # starter mode
            id = 0
            #RECCOMEND STAGE
            if self.rec:
                return self.res_cont_rec(line)
            elif self.unsure_check:
                id = self.unsure
            else:
                # GET TITLE FROM LINE
                line_titles = self.extract_titles(line)
                response = self.res_check_line_for_title(line_titles, line)
                if response != "" : # If you can't find a title, or too many
                    return response
        
                # GET MOVIE FROM TITLE
                movie_pre = line_titles[0]
                ids = self.find_movies_by_title(movie_pre)
                response = self.res_check_title_for_movie(movie_pre, ids)
                if response != "" : # If you can't find a movie, or too many
                    return response
                id = ids[0] # id of the movie
            
            # SENTIMENT
            movie = self.titles[id][0]
            # add to sentiment counts
            # build response based off sentiment
            response = self.res_sentiment(line, movie, id)
            if (self.unsure_check):
                return response
            
            # MAKING RECCOMENDATION
            if (len(self.liked) + len(self.disliked) >= 5):
                self.rec = True
                if self.creative:
                    enough_options = ["Ah, splendid! Based on your information, I have just the movie in mind!",
                    "Marvelous, my dear! I believe I have the perfect movie for you based on your input.",
                    "Fantastic, darling! I have just the movie recommendation for you based on the information provided.",
                    "Brilliant, my dear! I have enough information to suggest the perfect movie for you.",
                    "Excellent, darling! Based on your input, I can confidently recommend the ideal movie for you.",
                    "Amazing, my dear! I have just the movie in mind based on the information provided.",
                    "Stupendous, darling! With the information you've given me, I can suggest the perfect movie for you.",
                    "Fabulous, my dear! I have enough information to make a solid movie recommendation.",
                    "Superb, darling! Based on your input, I can confidently suggest the ideal movie for you.",
                    "Outstanding, my dear! With the information you've given me, I have just the movie in mind to recommend."]
                else:
                    enough_options = [
                        "Given the information you provided, I can suggest a movie.",
                        "Based on what you've told me, I can recommend a movie.",
                        "From what you've shared, I have a movie suggestion.",
                        "That's enough information for me to recommend a movie.",
                        "Given your preferences, I have a movie in mind.",
                        "Thanks to your input, I can suggest a movie for you.",
                        "Your input has given me enough information to suggest a movie.",
                        "With the information you've given me, I can make a movie recommendation.",
                        "Based on your preferences, I have a movie suggestion for you.",
                        "Your feedback has given me enough to make a movie recommendation."
                    ]
                enough = self.res_random(enough_options)
                response += enough + " "
                response += self.res_make_rec()
                return response
            tell_options = []
            if self.creative:
                tell_options = ["Share with me, darling, a movie you've witnessed?",
                    "I need to hear about a movie you've seen, my dear.",
                    "Speak up, my dear! Which movie has caught your eye?",
                    "Tell me about a film you've witnessed, darling.",
                    "Which movie left a lasting impression on you, my dear?",
                    "I demand to know, darling, tell me about a movie you've seen",
                    "Share with me a film you've witnessed, darling. I insist!",
                    "Don't keep me waiting, my dear. Tell me of a movie you've seen."]
            else:
                tell_options = [
                    "Tell me about a movie you've seen.",
                    "Can you describe a movie that you recently watched?",
                    "Have you seen any movies lately? Tell me about one.",
                    "What was the last movie you saw? Could you tell me about it?",
                    "I'm curious, could you share your thoughts on a movie you've seen recently?",
                    "Could you talk about a movie that you have seen?",
                    "Have you seen any movies that have really stood out to you? Can you tell me about one of them?",
                ]
            tell = self.res_random(tell_options)
            response += " " + tell

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
        if self.creative:
            potential_titles = re.findall('"([^"]+)"', preprocessed_input)
            if (potential_titles == []):
                
                potential_titles = re.findall('[liked |enjoyed |thought |hated |saw |loved |like |enjoy |hate |watch |watched ] ([^"]+) [was|is]', preprocessed_input)
                potential_titles += re.findall('[liked |enjoyed |thought |hated |saw |loved |like |enjoy |hate |watch |watched ] (.+)[.|!|!!]', preprocessed_input)
        else: 
            potential_titles = re.findall('"([^"]+)"', preprocessed_input)

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
        indices = []
        date_exists = False
        title_lowercase = title.lower()
        title_without_date = title_lowercase
        
        date_regex = "(\d{4})"
        date_regex_paren = "([(]\d{4}[)])"
        if re.search(date_regex_paren, title_lowercase):
            date_exists = True
            date = re.search(date_regex_paren, title_lowercase).group(1)
            title_without_date = title_lowercase.replace(' ' + date, '')
        elif re.search(date_regex, title_lowercase):
            date_exists = True
            date = re.search(date_regex, title_lowercase).group(1)
            title_without_date = title_lowercase.replace(' ' + date, '')

        if len(title_without_date.split()) > 1:
            first_word = title_without_date.split()[0]
            first_query_case = title_without_date.replace(first_word + ' ', '', 1) + ', ' + first_word
            indices = [k for k, v in self.titles_without_date.items() if any(first_query_case in l for l in v.values()) or any(title_without_date == l for l in v.values())]
        else:
            if self.creative:
                indices = [k for k, v in self.titles_without_date.items() if any(title_without_date in l.split() for l in v.values())]
            else:
                indices = [k for k, v in self.titles_without_date.items() if any(title_without_date == l for l in v.values())]

        
        if date_exists:
            for possible_index in indices:
                if self.titles_only_date[possible_index] != date:
                    indices.remove(possible_index)
                
        return indices

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
            print(preprocessed_input)
            negatives = ["don't", "never", "didn't", "not"]
            #list of extreme words for creative
            extreme_positive = ['Amazing', 'Awesome', 'Beautiful', 'Blissful', 'Brilliant', 'Delightful', 'Ecstatic', 'Enchanting', 'Excellent', 'Fabulous', 'Fantastic', 'Glorious', 'Heavenly', 'Incredible', 'Magnificent', 'Marvelous', 'Outstanding', 'Phenomenal', 'Splendid', 'Superb', 'Terrific', 'Wonderful', "Loved"]
            extreme_negative = ['Abysmal', 'Appalling', 'Atrocious', 'Awful', 'Deplorable', 'Disastrous', 'Dreadful', 'Horrendous', 'Horrible', 'Infernal', 'Miserable', 'Pathetic', 'Terrible', 'Tragic', 'Traumatic', 'Unbearable', 'Unforgivable', 'Unpleasant', 'Upsetting', 'Vile', 'Wretched', "Hated"]
            #lets stem this words
            stemmed_extreme_positive = []
            for w in extreme_positive:
                stemmed_extreme_positive.append(p.stem(w, 0, len(w)-1).lower())
            stemmed_extreme_negative = []
            for w in extreme_negative:
                stemmed_extreme_negative.append(p.stem(w, 0, len(w)-1).lower())
        
            #Remove titles
            new_input = preprocessed_input
            for word in Chatbot.extract_titles(self, preprocessed_input):
                if word in preprocessed_input:
                    new_input = preprocessed_input.replace('"' + word + '"', "")
            #this is a list of the words in the input with the title removed
            input_list = new_input.split()

            #stem the words in the input list
            stemmed_words = []
            for w in input_list:
                stemmed_words.append(p.stem(w, 0, len(w)-1))

            #classify sentiment
            sentiment_count = 0
            negate = 1
            for word in stemmed_words:
                if word in self.stemmed_sentiment:
                    if self.stemmed_sentiment[word] == "neg":
                        sentiment_count = sentiment_count - 1
                    if self.stemmed_sentiment[word] == "pos":
                        sentiment_count = sentiment_count + 1
                    if p.stem(word, 0, len(word)-1) in stemmed_extreme_negative:
                        print(-2)
                        return -2 
                    if p.stem(word, 0, len(word)-1) in stemmed_extreme_positive:
                        print(2)
                        return 2
                if word.lower() in negatives:
                    negate = negate * -1
            sentiment_count = sentiment_count * negate

            #here we assume that if someone desribes a movie with multiple adjectives, that means they liked it a lot more or less. 
            sentiment = 0
            if sentiment_count > 1:
                sentiment = 2
            if sentiment_count == 1:
                sentiment = 1
            if sentiment_count == -1:
                sentiment = -1
            if sentiment_count < -1:
                sentiment = -2

            #if someone says really or ever, then we should make it extreme.
            extreme = 1
            for word in input_list:
                if re.findall("r+e+a+l+y+", word) or re.findall("e+v+e+r+", word):
                    extreme = 2
            sentiment = sentiment * extreme
            
            print(sentiment)
            return sentiment


        else:
            negatives = ["don't", "never", "didn't", "not"]
            for word in Chatbot.extract_titles(self, preprocessed_input):
                if word in preprocessed_input:
                    new_input = preprocessed_input.replace('"' + word + '"', "")
            #this is a list of the words in the input with the title removed
            input_list = new_input.split()
            stemmed_words = []
            for w in input_list:
                stemmed_words.append(p.stem(w, 0, len(w)-1))

            sentiment_count = 0
            negate = 1
            for word in stemmed_words:
                if word in self.stemmed_sentiment:
                    if self.stemmed_sentiment[word] == "neg":
                        sentiment_count = sentiment_count - 1
                    if self.stemmed_sentiment[word] == "pos":
                        sentiment_count = sentiment_count + 1
                if word.lower() in negatives:
                    negate = -1
            sentiment_count = sentiment_count * negate

            sentiment = 0
            if sentiment_count > 0:
                sentiment = 1
            if sentiment_count < 0:
                sentiment = -1
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
        # split input by conjuction
        # for each string
        # get the title
        # get sentitment
            # if there's no sentiment then get the prevous one
        but_split = preprocessed_input.split("but ")
        for i in range(len(but_split)):
            if (i > 0):
                but_split[i] = "but " + but_split[i]

        titles_sent = []
        for p in range(len(but_split)):
            titles = self.extract_titles(but_split[p])
            sentiment = self.extract_sentiment(self.preprocess(but_split[p]))
            for i in range(len(titles)):
                title_ids = self.find_movies_by_title(titles[i])
                if (len(title_ids) > 0):
                    id = title_ids[0]
                    if (p >= 1):
                        sentiment = prev_sentiment * -1
                    titles_sent.append((titles[i], sentiment))
            prev_sentiment = sentiment
        return titles_sent

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
        def edit_distance(str1, str2):
            m = len(str1)
            n = len(str2)

            table = [[0 for x in range(n+1)] for x in range(m+1)]

            for i in range(m+1):
                for j in range(n+1):
                    if i == 0:
                        table[i][j] = j
                    elif j == 0:
                        table[i][j] = i
                    elif str1[i-1] == str2[j-1]:
                        table[i][j] = table[i-1][j-1]
                    else:
                        table[i][j] = 2 + min(table[i][j-1],
                                        table[i-1][j],
                                        table[i-1][j-1])
            return table[m][n]
        
    


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
        for candidate in candidates:
            for title_option in self.titles_without_date[candidate]:
                if clarification in title_option:
                    res.append(candidate)
            if clarification in self.titles_only_date[candidate]:
                res.append(candidate)
        return list(set(res))

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
        binarized_ratings[ratings > threshold] = 1
        binarized_ratings[(ratings <= threshold) & (ratings != 0)] = -1
        #print(ratings)

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
        num = np.dot(u, v)
        den = (np.linalg.norm(u) * np.linalg.norm(v))
        if (den == 0):
            similarity = 0
        else:
            similarity = num / den
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return similarity

    def func_b(self, b, a):
        num = np.dot(a[:-1], b[:-1])
        den = (np.linalg.norm(a[:-1]) * np.linalg.norm(b[:-1]))
        if (den == 0):
            return 0
        return (num / den) * b[-1]

    def func_a(self, a, nonzero):
        s = np.apply_along_axis(self.func_b, 1, nonzero, a)
        return np.sum(s)

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
        # item item collab with cosine similarity
        
        # indices of nonrated movies
        nonrated = np.array(np.nonzero(user_ratings == 0))[0]

        updated = np.c_[ratings_matrix, user_ratings]
        nonzero = updated[np.nonzero(user_ratings), :][0]

        nonrated_updated = updated[np.nonzero(user_ratings == 0), :][0]
        #print(updated)

        rx = np.apply_along_axis(self.func_a, 1, nonrated_updated, nonzero)
        #unseen = rx[np.nonzero(user_ratings == 0)]

        rx_index = np.c_[rx, nonrated]
        rx_index_sorted = rx_index[rx_index[:, 0].argsort()]

        recommendations = (rx_index_sorted[:, 1])[-k:]
        rec = list(recommendations.astype(int))
        rec.reverse()

        #print(rec)
        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        return rec

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
