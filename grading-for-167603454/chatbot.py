# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re
from porter_stemmer import PorterStemmer

import pickle
import random

# noinspection PyMethodMayBeStatic
class Chatbot:
    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'Pycaprio' if not creative else 'JayGatsbyTheBot'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        
        # RATING
        self.ratings = self.binarize(ratings)

        # NLU
        self.movie_title_dict, self.other_title_dict, self.idx_to_movie_dict = self.create_movie_dicts(self.titles)
        self.movie_title_ignorecase = {k.lower(): k for k in self.movie_title_dict.keys()}
        self.other_title_ignorecase = {k.lower(): k for k in self.other_title_dict.keys()}

        self.port_stemmer = PorterStemmer()
        self.sentiment_lexicon_dict = self.create_sentiment_lexicon_dict()
        self.arousal_words = self.load_arousal_words()

        # PERSONA MANAGER
        self.utterances = self.load_utterance_dictionary()
        
        # STATE MANAGER
        self.bot_stage = 'INPUT'
        self.flags = []
        self.soft_flag = []         # [(Flags.xxx, related_data)]
        self.saved_state = {}
        self.prev_question = self.get_randomized_utterance('ask_for_input')
        
        # USER DATA
        self.user_data = {}         # {movie_title : {user_sentiment: ...}, {movie_idx: xx}}
        self.user_ratings = None
        
        # RECOMMENDATION
        self.recommended_movies = []
        
        # DATA
        self.emo_dict = self.load_emotion_dictionary()
        
    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        greeting_message = self.get_randomized_utterance('greeting')
        return greeting_message

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        goodbye_message = self.get_randomized_utterance('goodbye')
        return goodbye_message

    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################

    def process(self, line):
        # RESET FLAGS
        self.reset('flags')


        # FALLBACK
        response = self.get_randomized_utterance('fallback_all')

        # PRELIMINARY NLU
        preprocessed_input = self.preprocess(line)
        response_to_arbitrary_input = self.get_response_to_arbitrary_input(preprocessed_input) if self.creative else ""
        response_to_emotion = self.get_response_to_emotion(preprocessed_input) if self.creative else ""
      
        # HANDLE ARBITRARY INPUT
        if response_to_arbitrary_input and self.creative:
            if self.bot_stage != 'OUTPUT':
                question = self.prev_question
                response = response_to_arbitrary_input + ' ' + question
            else:
                question = self.prev_question
                response = response_to_arbitrary_input + ' ' + question
            self.reset('saved_state')
            
            
        # HANDLE INPUT WITH EMOTION
        elif response_to_emotion and self.creative:
            if self.bot_stage != 'OUTPUT':
                question = self.prev_question
                response = response_to_emotion + ' ' + question
            else:
                question = self.prev_question
                response = response_to_emotion + ' ' + question
            self.reset('saved_state')


        # HANDLE MOVIE INPUT
        elif self.bot_stage == 'INPUT':
        
            # Extract Movie titles mentioned
            input_movie_titles = self.extract_titles(preprocessed_input)
            input_movie_indices = list(map(self.find_movies_by_title, input_movie_titles))
            
            # Add flags: Flags.movie_not_found, Flags.not_exist_in_database, Flags.ambiguous_title
            if not len(input_movie_titles):
                self.flags.append(['Flags.movie_not_found', None])
            for i in range(len(input_movie_titles)):
                if len(input_movie_indices[i]) == 0:
                    self.flags.append(['Flags.not_exist_in_database',input_movie_titles[i]])
                elif len(input_movie_indices[i]) > 1:
                    self.flags.append(['Flags.ambiguous_title', input_movie_titles[i]])
                elif len(input_movie_indices[i]) == 1 and self.check_repetition(input_movie_indices[i][0]):
                    self.soft_flag.append(input_movie_titles[i])

            # Extract user's sentiment towards movies
            input_sentiment = self.extract_sentiment(preprocessed_input)
            self.saved_state['sentiment'] = input_sentiment
            
            # Add flags: Flags.unknown_sentiment
            if input_sentiment == 0:
                self.flags.append(['Flags.unknown_sentiment', input_movie_titles])

            # Output
            if len(self.flags):
                fallback, question = self.get_failing_response()
                self.prev_question = question
                response = fallback + ' ' + question
            else:
                response = self.get_response_to_valid_input(input_movie_titles, input_movie_indices, input_sentiment)
                self.reset('saved_state')
                
                
        # HANDLE TYPO CLARIFICATION INPUT (Can only be triggered in creative mode)
        elif self.bot_stage == 'CLARIFICATION_TYPO':
            if line.lower() in ['yes', 'yeah', 'yea'] : # Accept typo correction
                closest_idx = self.saved_state['closest_movie_idx']
                if 'sentiment' in self.saved_state and self.saved_state['sentiment'] != 0:
                    response = self.get_response_to_valid_input([self.idx_to_movie_dict[closest_idx][0]],
                                                                [[closest_idx]],
                                                                self.saved_state['sentiment'])
                    self.reset('state')
                else:
                    self.flags.append(['Flags.unknown_sentiment', [self.idx_to_movie_dict[closest_idx][0]]])
                    if len(self.flags):
                        fallback, question = self.get_failing_response()
                        self.prev_question = question
                        response = fallback + ' ' + question
            else:
                self.reset('state')
                # DEBUGGING
                # self.print_status_for_debug()
                return self.get_randomized_utterance('fallback_typo') + ' ' + self.get_randomized_utterance('ask_for_input')
        
                    
        # HANDLE TITLE CLARIFICATION INPUT
        elif self.bot_stage == 'CLARIFICATION_TITLE':
            clarification = preprocessed_input
            ambiguous_indices = self.saved_state['ambiguous_cand_indices']
            disambiguated_idx_lst = self.disambiguate(clarification, ambiguous_indices)
            disambiguated_title_lst = [self.idx_to_movie_dict[idx][0] for idx in disambiguated_idx_lst]
            if len(disambiguated_idx_lst) > 1:
                complied_ambiguous_titles = self.compile_movies_mentioned(disambiguated_title_lst, connective='or')
                response = self.get_randomized_utterance('need_clarification_for_title').format(complied_ambiguous_titles)
                self.prev_question = response
                self.saved_state['ambiguous_cand_indices'] = disambiguated_idx_lst
            elif len(disambiguated_idx_lst) == 0:
                question = self.get_randomized_utterance('ask_for_input')
                self.prev_question = question
                response = self.get_randomized_utterance('no_match') + ' ' + self.get_randomized_utterance('ask_for_input')
                self.reset('state')
            elif 'sentiment' in self.saved_state and self.saved_state['sentiment'] != 0:
                response = self.get_response_to_valid_input(disambiguated_title_lst,
                                                            [disambiguated_idx_lst],
                                                            self.saved_state['sentiment'])
                self.reset('state')
            else:
                self.flags.append(['Flags.unknown_sentiment', disambiguated_title_lst])
                if len(self.flags):
                    fallback, question = self.get_failing_response()
                    self.prev_question = question
                    response = fallback + ' ' + question
                    
        
        # HANDLE SENTIMENT CLARIFICATION INPUT (Can only be triggerd when there is no problem with titles)
        elif self.bot_stage == 'CLARIFICATION_SENTIMENT':
            input_movie_titles = self.saved_state['input_movie_titles']
            input_movie_indices = list(map(self.find_movies_by_title, input_movie_titles))
            input_sentiment = self.extract_sentiment(preprocessed_input)
            if input_sentiment == 0:
                self.flags.append(['Flags.unknown_sentiment', input_movie_titles])
                if len(self.flags):
                    fallback, question = self.get_failing_response()
                    self.prev_question = question
                    response = fallback + ' ' + question
            else:
                response = self.get_response_to_valid_input(input_movie_titles,
                                                            input_movie_indices,
                                                            input_sentiment)
                self.reset('state')
                
            
        # GIVE RECOMMENDATION
        elif self.bot_stage == 'OUTPUT':
            if line.lower() == 'yes':
                if len(self.recommended_movies):
                    suggestion = self.generate_recommendation(self.idx_to_movie_dict[self.recommended_movies[0]][0])
                    self.recommended_movies.pop(0)
                    question = self.get_randomized_utterance('ask_if_want_recommendation')
                    self.prev_question = question
                    response = suggestion + ' ' + question
                else:
                    self.flags.append(['Flags.empty_recommend_lst', None])
                    fallback, question = self.get_failing_response()
                    response = fallback + ' ' + question
                    self.prev_question = question
                    self.reset('all')
            else:
                response = self.get_randomized_utterance('ask_for_yes_or_quit')
                self.prev_question = response
                
                
        # DEBUGGING
        # self.print_status_for_debug()
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return response

    @staticmethod
    def preprocess(text):
        return text

    def extract_titles(self, preprocessed_input):
        title_lst = re.findall('(?!\w)"(.*?)"(?!\w)', preprocessed_input)
        if self.creative and not title_lst:
            for movie_title in self.movie_title_ignorecase:
                title_regex = re.compile('(?:^| )(' + re.escape(movie_title) + ')(?:$| |\.|!|\?|:)')
                match = title_regex.search(preprocessed_input.lower())
                if match:
                    title_lst.append(self.movie_title_ignorecase[movie_title])
        return title_lst

    def find_movies_by_title(self, title):
        idx_set = set()
        if self.creative:
            q_title, q_year, _ = self.extract_info_from_raw_title(title)
            q_title = q_title.lower()
            q_main_title_cand_lst = self.get_main_title_candidate_lst(q_title)
            for q_main_title in q_main_title_cand_lst:
                self.find_movies_by_title_helper(q_main_title, q_year, idx_set)
        else:
            q_title, q_year, _ = self.extract_info_from_raw_title(title)
            q_main_title = q_title if q_title in self.movie_title_dict else None
            self.find_movies_by_title_helper(q_main_title, q_year, idx_set)

        idx_lst = list(idx_set)
        return idx_lst

    def extract_sentiment(self, preprocessed_input):
        input_sentences = re.split("[;|\.|\n]|,\sand\s|,\sbut\s", preprocessed_input.lower())
        masked_input_sentences = list(map(self.mask_movie_title, input_sentences))
        input_word_sentences = [s.split(' ') for s in masked_input_sentences]
        preprocessed_word_sentences = [list(map(self.preprocess_words, words)) for words in input_word_sentences]
        negation_sentences = [np.array(self.generate_negation(words)) for words in preprocessed_word_sentences]
        sentence_word_scores = [np.array(list(map(self.get_score, words))) for words in preprocessed_word_sentences]

        if self.creative:
            arousal_sentences = [np.array(self.generate_arousal(words)) for words in preprocessed_word_sentences]
            sentence_sentiments = [np.sum(np.sum(arousal_sentences[i] * negation_sentences[i] * sentence_word_scores[i])) for i in
                                range(len(sentence_word_scores))]
            sentiment = sum(sentence_sentiments)
            
            if '!' in preprocessed_input or ' really ' in preprocessed_input.lower()\
             or ' very ' in preprocessed_input.lower() or ' extremely ' in preprocessed_input.lower():
                sentiment *= 2
                
            if sentiment >= 2:
                return 2
            elif sentiment == 1:
                return 1
            elif sentiment <= -2:
                return -2
            elif sentiment == -1:
                return -1
            else:
                return 0
        else:
            sentence_sentiments = [np.sum(np.dot(negation_sentences[i], sentence_word_scores[i])) for i in
                                range(len(sentence_word_scores))]
            sentiment = sum(sentence_sentiments)
            if sentiment > 0:
                return 1
            elif sentiment < 0:
                return -1
            else:
                return 0

    def extract_sentiment_for_movies(self, preprocessed_input):
        input_sentences = re.split("[;|\.|\n]|,\sand\s|\sbut\s", preprocessed_input.lower())
        masked_input_sentences = list(map(self.mask_movie_title, input_sentences))
        input_word_sentences = [s.split(' ') for s in masked_input_sentences]
        preprocessed_word_sentences = [list(map(self.preprocess_words, words)) for words in input_word_sentences]
        negation_sentences = [np.array(self.generate_negation(words)) for words in preprocessed_word_sentences]
        sentence_word_scores = [np.array(list(map(self.get_score, words))) for words in preprocessed_word_sentences]
        sentence_sentiments = [np.sum(np.dot(negation_sentences[i], sentence_word_scores[i])) for i in
                               range(len(sentence_word_scores))]

        input_sentences_unchanged_case = re.split("[;|\.|\n]|,\sand\s|\sbut\s", preprocessed_input)
        sentence_titles = list(map(self.extract_titles, input_sentences_unchanged_case))

        output = []
        for i in range(len(sentence_titles)):
            for title in sentence_titles[i]:
                if len(input_word_sentences[i]) == 2 and input_word_sentences[i][0] == 'not' \
                        and 'MOVIETITLE' in input_word_sentences[i][1]:
                    sentiment = output[-1][1] * (-1)
                else:
                    sentiment = sentence_sentiments[i]
                    
                if sentiment > 0:
                    output.append((title, 1))
                elif sentiment < 0:
                    output.append((title, -1))
                else:
                    output.append((title, 0))

        return output


    def find_movies_closest_to_title(self, title, max_distance=3):
        closest_movie_lst = []
        minimum_edit_distance = None
        q_title = title.lower()
        for cand_title in self.movie_title_ignorecase:
            diff_len = abs(len(q_title) - len(cand_title))
            if diff_len <= max_distance:
                edit_distance = self.compute_edit_distance(q_title, cand_title)
                if edit_distance <= max_distance:
                    if minimum_edit_distance is None or edit_distance < minimum_edit_distance:
                        cand_main_title = self.movie_title_ignorecase[cand_title]
                        closest_movie_lst = list(self.movie_title_dict[cand_main_title]['year'].values())
                        minimum_edit_distance = edit_distance
                    elif edit_distance == minimum_edit_distance:
                        cand_main_title = self.movie_title_ignorecase[cand_title]
                        closest_movie_lst.extend(list(self.movie_title_dict[cand_main_title]['year'].values()))
        return closest_movie_lst


    def disambiguate(self, clarification, candidates):
        clarification = clarification.lower()
        candidate_titles_lst = [list(map(lambda t: t.lower(), self.idx_to_movie_dict[idx])) for idx in candidates]
        narrow_down_cand_idx_lst = []
        
        clarified_title_lst = re.findall('(?!\w)"(.*?)"(?!\w)', clarification)
        
        clarification_mod = self.modify_clarification(clarification)
        for i, candidate_titles in enumerate(candidate_titles_lst):
            for title in candidate_titles:
                if clarification_mod in title or title in clarified_title_lst:
                    narrow_down_cand_idx_lst.append(candidates[i])
                    break

        return narrow_down_cand_idx_lst

    ############################################################################
    # 3. Movie Recommendation helper functions                                 #
    ############################################################################

    @staticmethod
    def binarize(ratings, threshold=2.5):
        binarized_ratings = np.zeros_like(ratings)
        for x in range(len(binarized_ratings)):
            for y in range(len(binarized_ratings[0])):
                if ratings[x][y] == 0:
                    binarized_ratings[x][y] = 0
                elif ratings[x][y] > threshold:
                    binarized_ratings[x][y] = 1
                else:
                    binarized_ratings[x][y] = -1
        return binarized_ratings

    def similarity(self, u, v):
        norm_u = np.linalg.norm(u)
        norm_v = np.linalg.norm(v)
        similarity = np.dot(u, v) / (norm_u * norm_v) if norm_u and norm_v else 0
        return similarity

    def recommend(self, user_ratings, ratings_matrix, k=10, creative=False):
        recommendations = []
        predicted_ratings = []

        for i in range(len(user_ratings)):
            if (user_ratings[i] == 0):
                predicted_rating = self.predict_rating(ratings_matrix, user_ratings, i)
                predicted_ratings.append(predicted_rating)
            else:
                predicted_ratings.append(-1)
        predicted_ratings = np.array(predicted_ratings)
        top_k_inds = np.argpartition(predicted_ratings, -k)[-k:]
        recommendations = list(top_k_inds[np.argsort(predicted_ratings[top_k_inds])][::-1])

        return recommendations

    ############################################################################
    # 4. Debug info                                                            #
    ############################################################################

    def debug(self, line):
        debug_info = 'debug info'
        return debug_info

    ############################################################################
    # 5. Write a description for your chatbot here!                            #
    ############################################################################
    def intro(self):
        return self.get_randomized_utterance('intro')

    ############################################################################
    # *. Helper function                                                      #
    ############################################################################
    
    def mask_movie_title(self, s):
        s = re.sub('n\'t', ' not', s)  # moved from preprocess_words
        return re.sub('(?!\w)"(.*?)"(?!\w)', 'MOVIETITLE', s)
        
    def process_article(self, title_wo_paren):
        subparts = title_wo_paren.split(', ')
        if len(subparts) == 2:
            if subparts[1] == 'L\'':
                return subparts[1] + subparts[0]
            if subparts != ['I','Robot']:
                return subparts[1] + ' ' + subparts[0]
        return title_wo_paren

    def extract_movie_main_title(self, raw_title):
        left_paren = raw_title.find('(')
        preprocessed_title = raw_title if left_paren == -1 else raw_title[:left_paren - 1]
        preprocessed_title = self.process_article(preprocessed_title)
        return preprocessed_title

    def get_info_from_bracket(self, bracket_str):
        return bracket_str[1:-1]

    def extract_info_from_raw_title(self, raw_title):
        main_title = self.process_article(self.extract_movie_main_title(raw_title))
        year = None
        other_title_lst = []
        paren_lst = re.findall("(\([^\)\(]+\))", raw_title)
        for elem in paren_lst:
            elem = self.get_info_from_bracket(elem)
            if re.match('^\d{4}$', elem):
                year = elem
            elif re.match('^(\d{4})-$', elem):
                year = elem
            elif re.match('^\d{4}-\d{4}$', elem):
                year = elem
            elif elem.startswith('a.k.a.'):
                other_title_lst.append(self.process_article(elem[7:]))
            elif elem.startswith('aka '):
                other_title_lst.append(self.process_article(elem[4:]))
            else:
                other_title_lst.append(self.process_article(elem))
        return main_title, year, other_title_lst

    def add_year_to_title(self, title, year):
        return '{} ({})'.format(title, year) if year else title

    def create_movie_dicts(self, raw_data_lst):
        movie_title_dict = {}
        other_title_dict = {}
        idx_to_movie_dict = {}
        for idx, raw_data in enumerate(raw_data_lst):
            raw_title, genre = raw_data
            genre_lst = genre.split('|')

            main_title, year, other_title_lst = self.extract_info_from_raw_title(raw_title)

            if main_title not in movie_title_dict:
                movie_title_dict[main_title] = {'year': {}, 'genre':genre_lst}
            if year:
                movie_title_dict[main_title]['year'][year] = idx

            for other_title in other_title_lst:
                other_title_dict[other_title] = main_title

            idx_to_movie_dict[idx] = [self.add_year_to_title(main_title, year)]
            idx_to_movie_dict[idx] += [self.add_year_to_title(t, year) for t in other_title_lst]

        return movie_title_dict, other_title_dict, idx_to_movie_dict
        
    def find_movies_by_title_helper(self, q_main_title, q_year, idx_set):
        if q_main_title is not None:
            if q_year is None:
                for idx in self.movie_title_dict[q_main_title]['year'].values():
                    idx_set.add(idx)
            else:
                for valid_year in self.movie_title_dict[q_main_title]['year']:
                    if (
                        (len(valid_year) == 4 and q_year == valid_year)
                        or (len(valid_year) == 5 and int(q_year) >= int(valid_year[:4]))
                        or (len(valid_year) == 9 and int(valid_year[:4]) < int(q_year) and int(q_year < int(valid_year[5:])))
                    ):
                        idx_set.add(self.movie_title_dict[q_main_title]['year'][valid_year])

    def get_main_title_candidate_lst(self, q_title):
        main_title_candidate_set = set()
        title_regex = re.compile('(?:^| )(' + re.escape(q_title) + ')(?:$| |:|-)')
        for cand in self.movie_title_ignorecase:
            match = title_regex.search(cand)
            if match:
                main_title_candidate_set.add(self.movie_title_ignorecase[cand])
        for cand in self.other_title_ignorecase:
            match = title_regex.search(cand)
            if match:
                main_title_candidate_set.add(self.other_title_dict[self.other_title_ignorecase[cand]])
        return list(main_title_candidate_set)
        

    def create_sentiment_lexicon_dict(self):
        sentiment_lexicon_dict = {}
        with open('data/sentiment.txt', 'r') as f:
            for line in f:
                line = line.strip()
                word, sentiment = line.split(',')
                stemmed_word = self.port_stemmer.stem(word, 0, len(word) - 1)
                sentiment_lexicon_dict[stemmed_word] = 1 if sentiment == 'pos' else -1
        return sentiment_lexicon_dict

    def preprocess_words(self, w):
        w = re.sub('[!#\＄%&\(\)\*\+,-\.]', '', w)
        w = self.port_stemmer.stem(w, 0, len(w) - 1)
        return w

    def generate_negation(self, words):
        NEG_WORDS = ['never', 'not']
        negation = []
        neg_status = False
        for w in words:
            negation.append(-1 if neg_status else 1)
            if w in NEG_WORDS:
                neg_status = not neg_status
        return negation

    def get_score(self, w):
        return self.sentiment_lexicon_dict[w] if w in self.sentiment_lexicon_dict else 0

    def load_arousal_words(self):
        with open('deps/arousal.p', 'rb') as pf:
            arousal_words = pickle.load(pf)
        return arousal_words

    def generate_arousal(self, words):
        arousal = []
        for w in words:
            arousal.append(2 if w in self.arousal_words else 1)
        return arousal
        
    def compute_edit_distance(self, source, target):
        def ins_cost(ch):
            return 1
        def del_cost(ch):
            return 1
        def sub_cost(ch_s, ch_t):
            return 2 if ch_s != ch_t else 0

        n = len(source)
        m = len(target)
        D = [[float('inf') for _ in range(m + 1)] for _ in range(n + 1)]
        D[0][0] = 0
        for i in range(1, n + 1):
            D[i][0] = D[i - 1][0] + del_cost(source[i - 1])
        for j in range(1, m + 1):
            D[0][j] = D[0][j - 1] + ins_cost(target[j - 1])
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                D[i][j] = min(D[i - 1][j] + del_cost(source[i - 1]),
                              D[i - 1][j - 1] + sub_cost(source[i - 1], target[j - 1]),
                              D[i][j - 1] + ins_cost(target[j - 1]))

        return D[n][m]
        
    def modify_clarification(self, clarification):
        if clarification.isnumeric():
            if len(clarification) == 1:
                return ' ' + clarification + ' '
            elif len(clarification) == 4:
                return '(' + clarification + ')'
        return clarification
        
    def get_binarized_user_ratings(self):
        binarized_user_ratings = np.zeros(self.ratings.shape[0])
        for movie_title in self.user_data:
            idx = self.user_data[movie_title]['movie_idx']
            binarized_user_ratings[idx] = self.user_data[movie_title]['sentiment']
        return binarized_user_ratings

    def predict_rating(self, ratings_matrix, user_ratings, movie_to_predict_idx):
        movie_movie_rate_lst = []
        for movie_idx in range(len(user_ratings)):
            if movie_idx != movie_to_predict_idx and user_ratings[movie_idx] != 0:
                movie_to_predict_vec = ratings_matrix[movie_to_predict_idx]
                movie_to_comp_vec = ratings_matrix[movie_idx]
                if np.any(movie_to_predict_vec) and np.any(movie_to_comp_vec):
                    movie_similarity = self.similarity(movie_to_predict_vec, movie_to_comp_vec)
                    movie_movie_rate_lst.append((user_ratings[movie_idx], movie_similarity))

        rating = sum([rate * sim for rate, sim in movie_movie_rate_lst])
        return rating
        
    def load_utterance_dictionary(self):
        with open('deps/utterances.p', 'rb') as f:
            mode = 'creative' if self.creative else 'starter'
            raw_utterance_dict = pickle.load(f)
            utterrance_dict = {k: raw_utterance_dict[k][mode] for k in raw_utterance_dict}
        return utterrance_dict
        
    def load_emotion_dictionary(self):
        with open('deps/emotion.p', 'rb') as f:
            emo_dict = pickle.load(f)
        return emo_dict
        
    def get_randomized_utterance(self, key):
        return random.choice(self.utterances[key]) if len(self.utterances[key]) > 1 else self.utterances[key][0]
        
    def reset(self, cond):
        if cond == 'all':
            self.user_data = {}
            self.bot_stage = 'INPUT'
            self.recommended_movies = []
            self.user_ratings = None
            self.saved_state = {}
            self.prev_question = self.get_randomized_utterance('ask_for_input')
        elif cond == 'flags':
            self.flags = []
            self.soft_flag = []
        elif cond == 'state':
            self.bot_stage = 'INPUT'
            self.saved_state = {}
        elif cond == 'saved_state':
            self.saved_state = {}
            
    def update_status(self, input_movie_titles, input_movie_indices, input_sentiment):
        for i in range(len(input_movie_titles)):
            if input_movie_titles[i] not in self.soft_flag and input_movie_indices[i]:
                self.user_data[input_movie_titles[i]] = {'sentiment': input_sentiment,
                                                        'movie_idx': input_movie_indices[0][0]}

    def check_repetition(self, new_movie_idx):
        for movie_name in self.user_data:
            if self.user_data[movie_name]['movie_idx'] == new_movie_idx:
                return True
        return False
        
    def compile_movies_mentioned(self, movie_mentioned_lst, connective='and'):
        compiled_movie_titles = ''
        if movie_mentioned_lst:
            compiled_movie_titles = "\"" + movie_mentioned_lst[-1] + "\""
            if len(movie_mentioned_lst) > 1:
                compiled_movie_titles = "\""
                compiled_movie_titles += "\", \"".join(movie_mentioned_lst[:-1])
                compiled_movie_titles += "\" {} \"".format(connective) + movie_mentioned_lst[-1] + "\""
        return compiled_movie_titles
        
    def get_response_to_arbitrary_input(self, preprocessed_input):
        input_sentences = re.split("[;|\.|\n]|,\sand\s|,\sbut\s", preprocessed_input)
        masked_input_sentences = list(map(self.mask_movie_title, input_sentences))
        for sentence in masked_input_sentences:
            lower = sentence.lower()
            if lower.endswith('?'):
                if lower.startswith('can you') or lower.startswith('what you') or\
                    lower.startswith('would you') or lower.startswith('do you') or\
                    lower.startswith('are you') or lower.startswith('were you'):
                    if lower.startswith('can you') and 'movie' in lower:
                        return self.get_randomized_utterance('fallback_arbitrary')
                    counter = sentence[:-1]
                    counter = ' '.join(counter.split(' ')[2:])
                    return self.get_randomized_utterance('response_to_arbitrary').format(counter)
        return ""
        
    def get_response_to_emotion(self, preprocessed_input):
        positive_emotion = self.emo_dict['positive']
        negative_emotion = self.emo_dict['negative']
        title_lst = re.findall('(?!\w)"(.*?)"(?!\w)', preprocessed_input)
        if not title_lst:
            lower = preprocessed_input.lower()
            if (
                lower.startswith("i'm")
                or lower.startswith("i am")
                or lower.startswith("i was")
                or lower.startswith("i feel")
                or lower.startswith("you make me")
                or lower.startswith("you made me")
            ):
                for emo in positive_emotion:
                    emo_regex = re.compile('(?: )(' + re.escape(emo) + ')(?:$| |\.|!|\?)')
                    match = emo_regex.search(preprocessed_input.lower())
                    if match:
                        return self.get_randomized_utterance('response_to_pos_emo').format(emo)
                for emo in negative_emotion:
                    emo_regex = re.compile('(?: )(' + re.escape(emo) + ')(?:$| |\.|!|\?)')
                    match = emo_regex.search(preprocessed_input.lower())
                    if match:
                        return self.get_randomized_utterance('response_to_neg_emo').format(emo)
        
    def get_failing_response(self):
        movie_not_found = False
        ambiguous_title = None
        not_exist_in_database = None
        unknown_sentiment = None
        for flag_t in self.flags:
            if flag_t[0] == 'Flags.empty_recommend_lst':
                failing_response = self.get_randomized_utterance('empty_recommend_lst_response')
                question = self.get_randomized_utterance('empty_recommend_lst_question')
                return failing_response, question
            elif flag_t[0] == 'Flags.movie_not_found' and not movie_not_found:
                movie_not_found = True
            elif flag_t[0] == 'Flags.ambiguous_title' and ambiguous_title is None:
                ambiguous_title = flag_t[1]
            elif flag_t[0] == 'Flags.not_exist_in_database' and not_exist_in_database is None:
                not_exist_in_database = flag_t[1]
            elif flag_t[0] == 'Flags.unknown_sentiment' and unknown_sentiment is None:
                unknown_sentiment = flag_t[1]

        failing_response = ""
        if movie_not_found:
            failing_response = self.get_randomized_utterance('movie_not_found_response')
            question = self.get_randomized_utterance('ask_for_input')
        elif ambiguous_title is not None:
            failing_response = self.get_randomized_utterance('ambiguous_title_response').format(ambiguous_title)
            ambiguous_indices = self.find_movies_by_title(ambiguous_title)
            ambiguous_titles = [self.idx_to_movie_dict[idx][0] for idx in ambiguous_indices]
            complied_ambiguous_titles = self.compile_movies_mentioned(ambiguous_titles, connective='or')
            question = self.get_randomized_utterance('ambiguous_title_question').format(complied_ambiguous_titles)
            self.bot_stage = 'CLARIFICATION_TITLE'
            self.saved_state['ambiguous_cand_indices'] = ambiguous_indices
        elif not_exist_in_database is not None:
            failing_response = self.get_randomized_utterance('not_exist_in_database_response').format(not_exist_in_database)
            question = self.get_randomized_utterance('not_exist_in_database_question')
            if self.creative:
                closest_ind = self.find_movies_closest_to_title(not_exist_in_database)
                if closest_ind:
                    self.bot_stage = 'CLARIFICATION_TYPO'
                    self.saved_state['closest_movie_idx'] = closest_ind[0]
                    question = self.get_randomized_utterance('correction').format(self.idx_to_movie_dict[closest_ind[0]][0])
        elif unknown_sentiment is not None:
            failing_response = self.get_randomized_utterance('unknown_sentiment_response').format(self.compile_movies_mentioned(unknown_sentiment))
            question = self.get_randomized_utterance('unknown_sentiment_question')
            self.bot_stage = 'CLARIFICATION_SENTIMENT'
            self.saved_state['input_movie_titles'] = unknown_sentiment
        return failing_response, question

    def generate_echo(self, input_movie_indices, input_sentiment):
        movie_titles = []
        for indices_lst in input_movie_indices:
            if len(indices_lst) == 1:
                movie_titles.append(self.idx_to_movie_dict[indices_lst[0]][0])
        compiled_movie_titles = self.compile_movies_mentioned(movie_titles)
        if compiled_movie_titles:
            if input_sentiment > 0:
                return self.get_randomized_utterance('echo_positive').format(compiled_movie_titles)
            elif input_sentiment < 0:
                return self.get_randomized_utterance('echo_negative').format(compiled_movie_titles)
        return compiled_movie_titles
        
    def get_response_to_valid_input(self, input_movie_titles, input_movie_indices, input_sentiment):
        echo = self.generate_echo(input_movie_indices, input_sentiment)
        note = ""
        if self.soft_flag:
            note = self.get_randomized_utterance('dont_repeat')
        self.update_status(input_movie_titles, input_movie_indices, input_sentiment)
        if len(self.user_data) < 5:
            question = self.get_randomized_utterance('ask_for_input')
            self.prev_question = question
            response = echo + ' ' + question + ' ' + note if note else echo + ' ' + question
            self.bot_stage = 'INPUT'
        else:
            self.bot_stage = 'OUTPUT'
            ending = self.get_randomized_utterance('ending_for_input')

            self.user_ratings = self.get_binarized_user_ratings()
            self.recommended_movies = self.recommend(self.user_ratings, self.ratings)
            if len(self.recommended_movies) == 0:
                self.reset('all')
                self.creative = False
                self.name = "BackUpBot"
                response = self.get_randomized_utterance('backup_init') + " ... " + self.get_randomized_utterance('backup_greeting')
            else:
                suggestion = self.generate_recommendation(self.idx_to_movie_dict[self.recommended_movies[0]][0])
                self.recommended_movies.pop(0)
                question = self.get_randomized_utterance('ask_if_want_recommendation')
                self.prev_question = question
                response = echo + ' ' + ending + ' ' + suggestion + ' ' + question

        return response
        
    def generate_recommendation(self, recommended_movie):
        return self.get_randomized_utterance('recommendation').format(recommended_movie)
    
    def print_status_for_debug(self):
        print('self.user_data = {}'.format(self.user_data))
        print('self.bot_stage = {}, self.flags = {}'.format(self.bot_stage, self.flags, self.soft_flag))
        print('self.recommended_movies = {}'.format(self.recommended_movies))
        print('self.saved_state = {}'.format(self.saved_state))
        print('self.prev_question = {}'.format(self.prev_question))


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
