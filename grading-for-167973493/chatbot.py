# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import porter_stemmer
import random
p = porter_stemmer.PorterStemmer()


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
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        self.process_state = {
            "wait_for_response" : False,
            "wait_for_response's_recs" : [],
            "recs_simplified" : [],
            "prompts" : -1,
            "positive" : [],
            "negative" : [],
            "clarify_sent" : [],
            "clarify_movie" : [],
            "404" : [],
            "confused": [],
            "reccomend" : [],
            "clarify_yes_no" : [],
            "another" : [],
            "exit" : [],
            "ratings" : np.zeros(len(self.titles))
        }

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

        greeting_message = "How can I help you?"

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
        positive = [
            "Can you share your thoughts on a different movie since you enjoyed MOVIE?",
            "Since you enjoyed MOVIE, would you recommend any other movies?",
            "What other movie do you recommend if someone liked MOVIE?",
            "If you are a fan of MOVIE, what other movie would you suggest checking out?",
            "What did you think of MOVIE and do you have any other movie recommendations?",
            "If you enjoyed MOVIE, which other movie would you suggest watching?",
            "I'm ecstatic you have a positive opinion on MOVIE, can you recommend any other movies?",
            "Are there any other movies you'd suggest for someone who enjoyed MOVIE?",
            "What other movies do you think a MOVIE fan would enjoy?",
            "Since you liked MOVIE, would you recommend any other movies in a similar vein?",
            "Could you tell me about another movie you enjoyed?",
            "If you enjoyed MOVIE, which other movies do you think would be worth watching?",
            "Can you think of any other movies that someone who liked MOVIE would enjoy?",
            "What other movies do you think someone who enjoyed MOVIE would like?",
            "Since you enjoyed MOVIE, do you have any suggestions for other movies that might be appealing?",
            "If you're a fan of MOVIE, what other movies would you suggest checking out?",
            "Can you suggest any other movies that someone who enjoyed MOVIE might like?",
            "What other movies would you recommend for someone who liked MOVIE?",


            "I'm pleased to hear you enjoyed MOVIE. Can you share your thoughts on another film?",
            "Your positive feedback about MOVIE is great. How about sharing your thoughts on another movie?",
            "It's great that you liked MOVIE. I'm curious, what are your thoughts on another film?",
            "I'm happy to hear that MOVIE was enjoyable for you. Can you tell me your opinion on another movie?",
            "Your appreciation of MOVIE is noted. What are your thoughts on another film?",
            "I'm glad to hear that you had a good experience with MOVIE. Can you share your thoughts on another movie?",
            "It's good to know that you liked MOVIE. What are your thoughts on another film?",
            "I'm pleased that you enjoyed watching MOVIE. Can you tell me your opinion on another movie?",
            "Your positive reaction to MOVIE is appreciated. How about sharing your thoughts on another film?",
            "I'm happy to hear that you found MOVIE enjoyable. What do you think about another movie?",
            "It's great that you liked MOVIE. Can you share your thoughts on another film?",
            "Your feedback about MOVIE is valued. What are your thoughts on another movie?",
            "I'm glad to hear that you had a good time watching MOVIE. Can you tell me your opinion on another movie?",
            "Your appreciation of MOVIE is well received. How about sharing your thoughts on another film?",
            "It's good to hear that MOVIE was to your liking. What do you think about another movie?"
        ]
        negative = [
            "I'm sorry you didn't like MOVIE. Can you tell me your thoughts on another movies?",
            "I'm sorry that MOVIE wasn't to your liking. Would you care to share your thoughts on another film?",
            "It's a shame that you didn't enjoy MOVIE. Can you tell me your thoughts on a different movie?",
            "If MOVIE didn't meet your expectations, perhaps you'd like to discuss your thoughts on another film?",
            "I'm sorry that you didn't find MOVIE enjoyable. Can you share your opinion on a different movie?",
            "I apologize that MOVIE wasn't what you hoped for. Would you like to share your thoughts on another film?",
            "It's too bad that MOVIE didn't satisfy you. Can you tell me your opinion on another movie?",
            "I'm sorry to hear that you didn't like MOVIE. How about you share your thoughts on a different film?",
            "If MOVIE wasn't your cup of tea, maybe you'd like to discuss your thoughts on another movie?",
            "I'm sorry that MOVIE wasn't up to your expectations. Would you care to share your thoughts on a different film?",
            "It's unfortunate that MOVIE wasn't enjoyable for you. Can you tell me your thoughts on a different movie?",
            "I'm sorry that MOVIE didn't resonate with you. Can you share your opinion on a different film?",
            "If you didn't like MOVIE, perhaps you'd like to discuss your thoughts on another movie?",
            "It's a pity that MOVIE didn't satisfy your taste. Can you tell me your opinion on another film?",
            "I'm sorry that MOVIE wasn't your favorite. How about you share your thoughts on a different movie?",
            "If MOVIE wasn't what you were hoping for, maybe you'd like to discuss your thoughts on another movie?"
        ]

        clarify_sent = [
            "Can you clarify, I am still unsure whether you liked MOVIE",
            "I'm still a bit confused, did you enjoy MOVIE?",
            "Could you elaborate on your feelings towards MOVIE?",
            "I'm not quite sure if you liked MOVIE or not, could you clarify?",
            "I'm getting mixed signals, did you actually like MOVIE?",
            "It's not entirely clear to me whether you liked MOVIE or not, can you explain further?",
            "I'm still a bit uncertain, can you confirm whether you enjoyed MOVIE or not?",
            "I'm not sure if you had a positive or negative experience with MOVIE, could you help me understand?",
            "I'm a bit confused about your feelings towards MOVIE, could you provide more context?",
            "I'm not quite certain if you liked MOVIE or not, could you give me more information?",
            "I'm having trouble determining your opinion of MOVIE, can you help me out?",
            "It's not clear to me whether you liked MOVIE or not, could you please clarify?",
            "I'm still unsure whether you enjoyed MOVIE or not, could you expand on your thoughts?",
            "Can you provide me with more insight into your feelings about MOVIE? I'm not sure if you liked it or not.",
            "I'm not entirely sure whether you had a positive or negative reaction to MOVIE, could you explain further?",
            "I'm a bit confused about whether you enjoyed MOVIE or not, could you give me more information to work with?"
        ]

        clarify_movie = [
            "Can you specify which MOVIE I found more than one movie called MOVIE.",
            "Could you please clarify which specific movie called MOVIE you are referring to?",
            "I'm a bit confused, could you specify which MOVIE you are talking about?",
            "I'm not sure I understand, which MOVIE are you referring to exactly?",
            "Can you be more specific about which MOVIE you're talking about?",
            "Could you provide more information about which MOVIE you're referring to?",
            "I'm having trouble following, can you specify the exact title of the MOVIE you're referring to?",
            "Just to clarify, which specific MOVIE are you talking about?",
            "Can you please tell me the full title of the MOVIE you're referring to?",
            "I want to make sure I understand which MOVIE you're talking about, can you give me more details?",
            "To help me understand better, could you specify which MOVIE you're talking about?",
            "I'm a bit confused, could you provide more context about which MOVIE you're referring to?",
            "Can you specify which MOVIE you're referring to so I can better understand?",
            "I want to make sure I understand correctly, can you tell me which specific MOVIE you're talking about?",
            "Could you please specify which MOVIE you're referring to so we can discuss it further?",
            "Could you please mention the specific MOVIE you are referring to?",
            "I am a bit confused, which MOVIE are you talking about exactly?",
            "To clarify, are you referring to the MOVIE that you liked or a different one?",
            "Just to be sure, could you specify which MOVIE you're referring to?",
            "Sorry to interrupt, but I'm not certain which MOVIE you're talking about. Could you please clarify?"
        ]

        case_404_not_found = [
            "That's funny I have never heard of MOVIE, tell me more about another movie.",
            "I'm not familiar with MOVIE, can you tell me about a different movie you like?",
            "MOVIE is new to me, can you recommend another movie you enjoyed?",
            "I haven't heard of MOVIE, could you share your thoughts on a different movie instead?",
            "I'm not sure I know about the MOVIE you're referring to, what other movie did you like?",
            "MOVIE doesn't ring a bell, can you talk about another movie that you enjoyed?",
            "I'm not familiar with MOVIE, can you tell me about another movie that you liked?",
            "I haven't heard of MOVIE, could you recommend a different movie you enjoyed?",
            "MOVIE is not a movie I know, can you share your thoughts on a different one?",
            "I'm not sure what MOVIE is, can you tell me about a different movie you enjoyed?",
            "I'm not familiar with MOVIE, could you talk about another movie you like?",
            "I haven't heard of MOVIE, can you tell me about a different movie that you enjoyed?",
            "MOVIE is unknown to me, can you recommend a movie you like?",
            "I'm not familiar with MOVIE, can you tell me about a movie that you enjoyed?",
            "I'm not sure I know what MOVIE is, could you share your thoughts on a different movie?",
            "I haven't heard of MOVIE, can you recommend a movie that you liked?"
        ]

        confused = [
            "Wow you stumped me! Can you either simplify or be more explicit?",
            "I'm amazed, you've left me speechless! Could you clarify or provide more detail?",
            "You've got me beat! Would you mind simplifying or elaborating further?",
            "I'm at a loss for words! Can you make it simpler or more clear for me?",
            "I'm impressed, you've got me stuck! Could you simplify or add more details?",
            "You've really got me thinking! Would you mind breaking it down or providing more explanation?",
            "You've got my mind blown! Can you simplify or provide more specifics?",
            "I'm flabbergasted, you've stumped me! Would you mind clarifying or being more detailed?",
            "I'm astonished, you've left me speechless! Can you simplify or provide more information?",
            "You've really thrown me for a loop! Could you elaborate or simplify it for me?",
            "You've got me scratching my head! Can you provide more detail or simplify it?",
            "I'm amazed, you've got me stumped! Would you mind being more explicit or simplifying?",
            "You've really puzzled me! Could you simplify or provide more details?",
            "You've got me completely baffled! Can you make it simpler or add more specifics?",
            "I'm astonished, you've left me flummoxed! Would you mind simplifying or being more explicit?",
            "You've really left me stumped! Can you clarify or provide more information?"
        ]

        recomendations = [
            "If you enjoyed the movie MOVIE, then you might want to consider watching REC, as I found MOVIE to be quite enjoyable.",
            "Based on my personal preference, I found the movie MOVIE to be quite enjoyable, so if you also liked that movie, I would recommend giving REC a watch.",
            "As someone who really enjoyed the movie MOVIE, I would suggest checking out Scream if you're looking for another movie to watch.",
            "In my opinion, MOVIE was a great movie, and if you share my taste in movies, you might want to give REC a try as well.",
            "If you're a fan of MOVIE like I am, then you might want to consider watching REC, as I found both movies to be quite entertaining.",
            "I personally loved the movie MOVIE, so if you're also a fan of that film, you might enjoy checking out REC as well.",
            "As someone who really enjoyed MOVIE, I think REC could be a good movie to watch if you're looking for something similar.",
            "In my view, MOVIE was a fantastic movie, so if you liked it too, you might want to give REC a chance.",
            "Based on my own enjoyment of the movie MOVIE, I would recommend checking out REC if you're looking for a new movie to watch.",
            "If you're a fan of MOVIE, then you might enjoy watching REC, as I found both movies to be quite enjoyable.",
            "I really liked the movie MOVIE, and if you did too, you might want to give REC a try based on my recommendation.",
            "In my personal opinion, MOVIE was a great movie, and if you share my taste in movies, you might want to give REC a chance.",
            "As someone who enjoyed watching MOVIE, I think REC could be a good movie to check out if you're interested.",
            "If you're a fan of MOVIE, then you might want to consider watching REC as well, as I found both movies to be quite good.",
            "I thought MOVIE was a fantastic movie, so if you liked it too, you might enjoy watching REC based on my recommendation.",
            "Based on my own enjoyment of the movie MOVIE, I would suggest giving REC a try if you're looking for something similar.",
            "As someone who really liked MOVIE, I think REC could be a good movie to watch if you're interested in that type of film.",
            "If you enjoyed the movie MOVIE, then you might want to consider watching REC, as I found both movies to be quite enjoyable.",
            "I really enjoyed the movie MOVIE, so if you're a fan of that film, you might want to give REC a chance based on my recommendation.",
            "In my opinion, MOVIE was a great movie, so if you liked it too, you might want to check out REC as well.",
            "If you're a fan of MOVIE like I am, then you might want to consider giving REC a watch, as I found both movies to be quite entertaining.",
        ]

        yes = ["ya", "yes", "ye", "yaa", "yay", "yep"]
        no = ["no", "nah", "naw", "nay", "nope", "nada", "quit", "exit"]

        clarify_yes_no = [
            "I am not sure what you meant by this, can you simplify?",
            "Could you please make it easier to understand what you meant by this?",
            "I'm not quite following your meaning, could you simplify it for me?",
            "Can you clarify or make simpler what you meant by this?",
            "I'm having a hard time understanding what you're saying, could you break it down more simply?",
            "Would you mind simplifying your message, as I'm not entirely sure what you meant by this?",
            "I'm not certain I understood your meaning, could you try to explain it in simpler terms?",
            "Could you possibly make it more straightforward for me to grasp what you meant by this?",
            "Can you simplify your statement so that it's easier for me to understand?",
            "I'm a bit lost, could you try to simplify your answer so that I can follow you better?",
            "Can you simplify your message to make it more accessible for me to understand what you meant by this?"
        ]
        recs_simplified = [
            "Based on your taste in movies I think you would also like MOVIE.",
            "I believe MOVIE would appeal to your movie preferences.",
            "Given your movie taste, I think you'll enjoy MOVIE too.",
            "Your taste in movies suggests that you may appreciate MOVIE as well.",
            "If you're into the kind of movies you like, then MOVIE could be worth checking out.",
            "MOVIE might be something you'd enjoy, based on your taste in movies.",
            "Judging from your movie preferences, I think MOVIE would be up your alley.",
            "Your movie taste indicates that you might find MOVIE to be a good fit.",
            "MOVIE seems like it would be in line with your taste in movies.",
            "Based on your liking for certain movies, I think you might also enjoy MOVIE.",
            "If your movie preferences are any indication, then MOVIE could be a great choice for you."
        ]
        another = [
            "Would you like another recommendation?",
            "Can I suggest another option for you?",
            "Are you open to hearing another recommendation?",
            "Would you be interested in hearing another suggestion?",
            "Might I propose another choice for you?",
            "Do you want me to offer another recommendation?",
            "Shall I give you another suggestion?",
            "Is there any interest in hearing another option?",
            "Would it be helpful if I gave you another recommendation?",
            "Do you want me to suggest something else?",
            "Are you willing to consider another recommendation from me?"
        ]
        exit = [
            "Tell me more about another movie!",
            "Can you provide further details about another movie?",
            "Could you elaborate on another movie?",
            "Would you mind sharing more information about another movie?",
            "I'm interested in hearing more about another movie. Could you please tell me more?",
            "Can you give me more insights into another movie?",
            "Could you expand on another movie?",
            "I would like to know more about another movie. Can you tell me more?",
            "What else can you tell me about another movie?"
        ]
        # hanging state handling: when we are expected to remember information from the last call
        if self.process_state["wait_for_response"]:
            response = line
            response = response.lower()
            response = response.replace(" ", "").replace("!", "").replace("?", "").replace(".", "").replace(",", "")
            if response in yes:
                index = -1
                while index == -1 or index in self.process_state["recs_simplified"]:
                    index = random.choice(range(len(recs_simplified)))
                self.process_state["recs_simplified"].append(index)
                if len(self.process_state["recs_simplified"]) > 5:
                    self.process_sate["recs_simplified"].pop(0)
                str = recs_simplified[index]
                str = str.replace("MOVIE",self.titles[self.process_state["wait_for_response's_recs"][0]][0])
                self.process_state["wait_for_response's_recs"].pop(0)
                # prep for a return here instead of print
                str += "\n"
                index = -1
                while index == -1 or index in self.process_state["another"]:
                    index = random.choice(range(len(another)))
                self.process_state["another"].append(index)
                if len(self.process_state["another"]) > 5:
                    self.process_state["another"].pop(0)
                str += another[index]
                return str
            elif response in no:
                index = -1
                while index == -1 or index in self.process_state["exit"]:
                    index = random.choice(range(len(exit)))
                self.process_state["exit"].append(index)
                if len(self.process_state["exit"]) > 5:
                    self.process_state["exit"].pop(0)
                self.process_state["wait_for_response"] = False # clean up the state
                self.process_state["wait_for_response's_recs"] = []
                return exit[index]
            else:
                index = -1
                while index == -1 or index in self.process_state["clarify_yes_no"]:
                    index = random.choice(range(len(clarify_yes_no)))
                self.process_state["clarify_yes_no"].append(index)
                if len(self.process_state["clarify_yes_no"]) > 5:
                    self.process_state["clarify_yes_no"].pop(0)
                return clarify_yes_no[index]

        # normal state: i.e. nothing needs to be remembered
        titles = self.extract_titles(line)
        if len(titles) != 1: # too many or too litle passed titles
            index = -1
            while index == -1 or index in self.process_state["confused"]:
                index = random.choice(range(len(confused)))
            str = confused[index]
            self.process_state["confused"].append(index)
            if len(self.process_state["confused"]) > 5:
                self.process_state["confused"].pop(0)
            return  str
        movies_by_title = self.find_movies_by_title(titles[0])
        
        sentiment = self.extract_sentiment(line)
        if sentiment > 0 and self.process_state["prompts"] >= 5 and sentiment > 0 and len(movies_by_title) == 1 and len(titles) == 1:  # should recommend
                self.process_state["prompts"] = -1
                self.process_state["ratings"][movies_by_title[0]] = 1
                good_movies = self.recommend(self.process_state["ratings"], self.ratings, k=len(self.titles))
                index = -1
                while index == -1 or index in self.process_state["reccomend"]:
                    index = random.choice(range(len(recomendations)))
                self.process_state["reccomend"].append(index)
                if len(self.process_state["reccomend"]) > 5:
                    self.process_sate["reccomend"].pop(0)
                str = recomendations[index]
                str = str.replace("MOVIE", titles[0])
                str = str.replace("REC", self.titles[good_movies[0]][0])
                good_movies.pop(0)
                # prep for a return here instead of print
                str += "\n"
                index = -1
                while index == -1 or index in self.process_state["another"]:
                    index = random.choice(range(len(another)))
                self.process_state["another"].append(index)
                if len(self.process_state["another"]) > 5:
                    self.process_state["another"].pop(0)
                str += another[index]
                self.process_state["wait_for_response"] = True
                self.process_state["wait_for_response's_recs"] = good_movies
                return str                    
        elif sentiment > 0 and len(movies_by_title) == 1 and len(titles) == 1: # valid positive
            self.process_state["prompts"] += 1
            self.process_state["ratings"][movies_by_title[0]] = 1
            index = -1
            while index == -1 or index in self.process_state["positive"]:
                index = random.choice(range(len(positive)))
            str = positive[index]
            self.process_state["positive"].append(index)
            if len(self.process_state["positive"]) > 5:
                self.process_sate["positive"].pop(0)
            str = str.replace("MOVIE", titles[0])
            return str
        elif sentiment < 0 and len(movies_by_title) == 1 and len(titles) == 1: # valid negative
            self.process_state["prompts"] += 1
            self.process_state["ratings"][movies_by_title[0]] = -1
            index = -1
            while index == -1 or index in self.process_state["negative"]:
                index = random.choice(range(len(negative)))
            str = negative[index]
            self.process_state["negative"].append(index)
            if len(self.process_state["negative"]) > 5:
                self.process_sate["negative"].pop(0)
            str = str.replace("MOVIE", titles[0])
            return str
        elif sentiment == 0 and len(movies_by_title) == 1 and len(titles) == 1: # no sentiment detected
            index = -1
            while index == -1 or index in self.process_state["clarify_sent"]:
                index = random.choice(range(len(clarify_sent)))
            str = clarify_sent[index]
            self.process_state["clarify_sent"].append(index)
            if len(self.process_state["clarify_sent"]) > 5:
                self.process_sate["clarify_sent"].pop(0)
            str = str.replace("MOVIE", titles[0])
            return str
        elif len(movies_by_title) > 1 : # multiple with the same titile
            index = -1
            while index == -1 or index in self.process_state["clarify_movie"]:
                index = random.choice(range(len(clarify_movie)))
            str = clarify_movie[index]
            self.process_state["clarify_movie"].append(index)
            if len(self.process_state["clarify_movie"]) > 5:
                self.process_sate["clarify_movie"].pop(0)
            str = str.replace("MOVIE", titles[0])
            return str
        elif len(movies_by_title) == 0: #404 not found
            index = -1
            while index == -1 or index in self.process_state["404"]:
                index = random.choice(range(len(case_404_not_found)))
            str = case_404_not_found[index]
            self.process_state["404"].append(index)
            if len(self.process_state["404"]) > 5:
                self.process_sate["404"].pop(0)
            str = str.replace("MOVIE", titles[0])
            return str


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
        if not self.creative:
            titles = []
            sections = preprocessed_input.split('\"')
            for i in range(len(sections)):
                if i % 2 == 1:
                    titles.append(sections[i])
            return titles
        else:
            titles = []
            sections = preprocessed_input.split('\"')
            for i in range(len(sections)):
                if i % 2 == 1:
                    titles.append(sections[i])
            return titles
        

    def parse_title(self, title):
        """ Helper function! Given a movie title, return the processed tokens in the title, 
            the tokens in the potential alternate titles, and the year.

        Example:
            title, alt_titles, year = chatbot.parse_title("Quest for Fire (Guerre du feu, La) (1981)")
            print(title) // {'quest', 'for', 'fire'}
            print(alt_titles) // [{'guerre', 'du', 'feu', 'la'}]
            print(year) // 1981 as an integer

        :param title: a string containing a movie title
        :returns: a set of title tokens, a list of sets of alternate title tokens, a year int
        """
        title = title.replace(",", "").replace(".", "").lower()
        if '(' not in title:
            return set(title.split()), [], -1
        segments = title.replace(')', '(').split('(')
        while '' in segments:
            segments.remove('')
        while ' ' in segments:
            segments.remove(' ')
        first_title = set(segments[0].split())
        alt_titles = []
        year = -1
        for i in range(1, len(segments)):
            phrase = segments[i]
            if len(phrase) == 4 and (phrase.isdigit()):
                year = int(phrase)
            else:
                alt_titles.append(set(segments[i].split()))
        return first_title, alt_titles, year


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
        user_title, user_alt_titles, user_year = self.parse_title(title) # assume user only does paren for year
        matches = []  # list of indices
        for movie_i in range(len(self.titles)):
            cmp = self.titles[movie_i][0] # the titles list is a list of lists
            db_title, db_alt_titles, db_year = self.parse_title(cmp)
            in_title = True  # check 1
            in_alt_titles = [True]* len(db_alt_titles)  # check 2
            for token in user_title:
                if in_title and not token in db_title:
                    in_title = False
                for i in range(len(db_alt_titles)):
                    if in_alt_titles[i] and not token in db_alt_titles[i]:
                        in_alt_titles[i] = False
            alt_title_pos = in_alt_titles.index(True) if True in in_alt_titles else -1
            correct_year = True  # check 3
            if user_year != -1 and user_year != db_year:
                correct_year = False
            correct_length = True  # check 4 (disambiguation)
            if not self.creative:
                correct_length = False
                if in_title:
                    correct_length = len(db_title) == len(user_title)
                if alt_title_pos != -1:
                    correct_length = len(db_alt_titles[alt_title_pos]) == len(user_title)
            if (in_title or alt_title_pos != -1) and correct_year and correct_length:
                matches.append(movie_i)
        return matches


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
        # Make negation words and punctuation
        negation_words = ["not", "never", "didn't", "neither", "nor", "don't", "can't"]
        strongly_negative = ['terrible', 'abhorrent', 'appalling', 'atrocious', 'awful', 'deplorable', 'disgusting', 'dreadful', 'evil', 'grotesque', 'hateful', 'heinous', 'horrible', 'horrendous', 'inexcusable', 'infernal', 'loathsome', 'monstrous', 'odious', 'offensive', 'repugnant', 'repulsive', 'revolting', 'shocking', 'terrible', 'unacceptable', 'unforgivable', 'unjustifiable', 'unpardonable', 'vile', 'wicked', 'worthless', 'abhor', 'condemn', 'cursing', 'curse', 'damn', 'deceive', 'destroy', 'disgrace', 'eliminate', 'hate', 'humiliate', 'injure', 'loathe', 'abhorred', 'condemned', 'cursed', 'damned', 'deceived', 'destroyed', 'disgraced', 'eliminated', 'hated', 'humiliated', 'injured', 'loathed', 'abysmally', 'atrociously', 'awfully', 'dreadfully', 'horribly', 'terribly', 'appallingly', 'disgustingly', 'repulsively', 'repugnantly', 'revoltingly', 'vilely', 'deplorably', 'despicably', 'detestably', 'execrably', 'noxiously', 'offensively', 'odiously', 'repellantly', 'abhorrently', 'grossly', 'gruesomely', 'hatefully', 'heinously', 'inhumanly', 'loathsomely', 'nastily', 'obnoxiously', 'sickeningly', 'unpleasantly', 'unsavorily', 'unseemly', 'wretchedly', 'disastrously', 'devastatingly', 'catastrophically']
        strongly_positive = ['amazing', 'awesome', 'beautiful', 'best', 'brilliant', 'celestial', 'cool', 'divine', 'excellent', 'fabulous', 'fantastic', 'great', 'gorgeous', 'heavenly', 'impressive', 'incredible', 'lovely', 'marvelous', 'outstanding', 'perfect', 'phenomenal', 'remarkable', 'splendid', 'stellar', 'stupendous', 'sublime', 'superb', 'terrific', 'top', 'tremendous', 'unbelievable', 'wonderful', 'adore', 'appreciate', 'bless', 'cherish', 'delight', 'enjoy', 'esteem', 'excel', 'fascinate', 'gladden', 'love', 'praise', 'rejoice', 'treasure', 'triumph', 'value', 'venerate', 'amazingly', 'awesomely', 'beautifully', 'brilliantly', 'celestially', 'coolly', 'divinely', 'excellently', 'fabulously', 'fantastically', 'greatly', 'gorgeously', 'heavenly', 'impressively', 'incredibly', 'lovely', 'marvelously', 'outstandingly', 'perfectly', 'phenomenally', 'remarkably', 'splendidly', 'stellarly', 'stupendously', 'sublimely', 'superbly', 'terrifically', 'toply', 'tremendously', 'unbelievably', 'wonderfully']
        new_negative = [p.stem(word) for word in strongly_negative]
        new_positive = [p.stem(word) for word in strongly_positive]
        strongly_negative.extend(new_negative)
        strongly_positive.extend(new_positive)

        # Remove title from input because title should not have impact on sentiment of input
        processed_input = preprocessed_input
        titles = self.extract_titles(processed_input)
        for title in titles:
            processed_input = processed_input.replace(title, "")
        words = processed_input.lower().split(" ")

        # Make stemmed dictionary
        stemmed_dict = {}
        for key in self.sentiment.keys():
            stemmed_key = p.stem(key)
            if stemmed_key not in stemmed_dict:
                stemmed_dict[stemmed_key] = self.sentiment[key]

        # Negate words
        negated_words = []
        negation_flag = False
        double_it = False
        for word in words:
            elem = word
            punc = '!;:,.?'
            for e in word:
                if e in punc:
                    elem = elem.replace(e, "")
            if "!!" in word:
                double_it = True
            if p.stem(elem) in strongly_negative or p.stem(elem) in strongly_positive or elem in strongly_negative or elem in strongly_positive:
                double_it = True

            if negation_flag == True:
                if word.endswith(",") or word.endswith(".") or word.endswith("!") or word.endswith("?"):
                    negated_words.append("NOT_" + word[:len(word) - 1])
                    negation_flag = False
                else:
                    negated_words.append("NOT_" + word)
            else: 
                if word in negation_words:
                    negation_flag = True
                if word.endswith(",") or word.endswith(".") or word.endswith("!") or word.endswith("?"):
                    word = word[:len(word) - 1]
                    negation_flag = False
                negated_words.append(word)

        # Calculate sentiment
        sentiment = 0
        for word in negated_words:
            if "NOT_" in word:
                stem = p.stem(word[4:])
                if stem in stemmed_dict:
                    if stemmed_dict[stem] == 'pos':
                        sentiment -= 1
                    else:
                        sentiment += 1
            else:
                stem = p.stem(word)
                if stem in stemmed_dict:
                    if stemmed_dict[stem] == 'pos':
                        sentiment += 1
                    else:
                        sentiment -= 1

        # Adjust sentiment to correct values
        if sentiment > 0:
            sentiment = 1
        elif sentiment < 0:
            sentiment = -1
        else:
            sentiment = 0

        if self.creative and double_it:
            return sentiment * 2
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
        conjunctions = ["and", "but", "or", "nor"]
        verbs = ["was", "liked", "disliked", "hated", "loved", "failed", "exceeded", "found", "appealed", "sit", "enjoy", "thought", "left", "won", "took", "catch", "fell", "suit", "move", "felt", "find", "click", "like", "hate", "wasn't", "love", "enjoy", "dislike", "fall", "leave", "blow", "is", "isn't"]
        negations = ["not", "never", "didn't", "neither", "nor", "don't", "can't"]
        res = []

        titles = self.extract_titles(preprocessed_input)

        verb_list = []
        words = preprocessed_input.split(" ")
        for i in range(len(words)):
            if words[i] in verbs:
                if words[i - 1] in negations: 
                    verb_list.append(words[i - 1] + " " + words[i])
                else:
                    verb_list.append(words[i])

        compound_flag = False
        if len(verb_list) > 1:
            compound_flag = True
        
        lines = words
        input = " ".join(lines)
        for i in range(len(words)):
            if words[i] in conjunctions:
                if compound_flag == False:
                    if words[i + 1] in negations:
                        lines.insert(i + 2, verb_list[0])
                    else:
                        lines.insert(i + 1, verb_list[0])
                    input = " ".join(lines)
                input = input.split(words[i])

        for i in range(len(input)):
            sentiment = self.extract_sentiment(input[i])
            res.append((titles[i], sentiment))

        return res        
    

    def calc_edit_distance(self, s1, s2):
       """ Return the minimum Levenshtein edit distance between two given strings.
           (non-recursive)
       """
       # https://web.stanford.edu/class/cs124/lec/med.pdf#page=14
       n, m = len(s1), len(s2)
       distances = np.zeros((n+1, m+1))
       # initialization
       for i in range(n+1):
           distances[i][0] = i  # weird cuz the table is flipped (Quadrant 1 not 4)
       for j in range(m+1):
           distances[0][j] = j
       # recurrence relation
       for i in range(1, n+1):
           for j in range(1, m+1):  # i think the pseudocode flips n & m
               insertion = distances[i-1][j] + 1
               deletion = distances[i][j-1] + 1
               substitution = distances[i-1][j-1]
               if s1[i-1] != s2[j-1]:  # string is still zero-indexed
                   substitution += 2
               distances[i][j] = min(insertion, deletion, substitution)
       return distances[n][m]


    def parse_title2(self, title):
       """ Similar to parse_title but doesn't turn titles into sets!
           Use this only for find_movies_closest_to_title since you assume
           no disambiguation combined with spell correct
       """
       title = title.lower()  # punctuation counts for edit distance
       if '(' not in title:
           return title.strip(), [], -1
       segments = title.replace(')', '(').split('(')
       while '' in segments:
           segments.remove('')
       while ' ' in segments:
           segments.remove(' ')
       first_title = segments[0].strip()
       alt_titles = []
       year = -1
       for i in range(1, len(segments)):
           phrase = segments[i]
           if len(phrase) == 4 and (phrase.isdigit()):
               year = int(phrase)
           else:
               alt_titles.append(phrase.strip())
       return first_title, alt_titles, year


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
        # no need for a word by word! assume no disambiguation with spell correct
        user_title, user_alt_titles, user_year = self.parse_title2(title) # assume user only does paren for year
        matches = {}  # key = distance, val = list of indices with that min distance
        for movie_i in range(len(self.titles)):
           cmp = self.titles[movie_i][0] # the titles list is a list of lists
           db_title, db_alt_titles, db_year = self.parse_title2(cmp)
           distance = self.calc_edit_distance(user_title, db_title)
           in_title = distance <= max_distance  # check 1
           in_alt_title = False
           if not in_title:  # check 2
               for i in range(len(db_alt_titles)):
                   distance = self.calc_edit_distance(user_title, db_alt_titles[i])
                   if distance <= max_distance:
                       in_alt_title = True
                       break
           correct_year = True  # check 3
           if user_year != -1 and user_year != db_year:
               correct_year = False
           if (in_title or in_alt_title) and correct_year:
                if distance not in matches.keys():
                    matches[distance] = []
                matches[distance].append(movie_i)
        if len(matches.keys()) == 0:
            return []
        return matches[min(matches.keys())]


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
        indicators = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth", "nineteenth", "twentieth",
        "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th", "13th", "14th", "15th", "16th", "17th", "18th", "19th", "20th",
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]
        stop_words = ['the', 'and', 'a', 'to', 'of', 'in', 'that', 'it', 'for', 'with', 'one']
        year_words = ["recent", "lastest", "earliest", "oldest"]

        clarification_filtered = [elem for elem in clarification.split() if elem not in stop_words]
        narrowed_list = []
        for term in clarification_filtered: 
            if term in indicators:
                return [candidates[((indicators.index(term) + 1) % 20) - 1]]
            if term in year_words:
                ind = year_words.index(term)
                if ind > 1:
                    ind = -1 
                else:
                    ind = 0
                return [candidates[ind]]

        for term in clarification_filtered:
            for candidate in candidates:
                movie_title = self.titles[candidate][0]
                if term in movie_title:
                    narrowed_list.append(candidate)
        return narrowed_list


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
        ratings_reloaded2 = ratings.copy()
        ratings = np.where((ratings > threshold) & (ratings != 0), 1, 0)
        ratings_reloaded2 = np.where((ratings_reloaded2 <= threshold) & (ratings_reloaded2 != 0), -1, 0)
        binarized_ratings = ratings + ratings_reloaded2

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
        similarity = np.dot(u, v)
        normalize = np.linalg.norm(u) * np.linalg.norm(v)
        if normalize != 0:
            similarity /= normalize
        else:
            return 0
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
        already_rated_movies = np.where(user_ratings != 0)[0]  # these are movie indices
        potential_recs = np.where(user_ratings == 0)[0]  # these are also movie indices
        for movie_i in potential_recs:
            # compute item-overlap cosine similarity btwn that movie i row and 
            # the rows of each movie m in user_ratings with a rating
            pred_rating = 0  # predicted user rating of movie i
            for movie_j in already_rated_movies:
                m_weight = self.similarity(ratings_matrix[movie_i], ratings_matrix[movie_j])
                pred_rating += m_weight * user_ratings[movie_j]
            # using formula on https://web.stanford.edu/class/cs124/lec/collaborativefiltering21.pdf#page=43
            recommendations.append((movie_i, pred_rating))
        recommendations = sorted(recommendations, key=lambda m:m[1], reverse=True)[:k]

        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        return [rec[0] for rec in recommendations]

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
