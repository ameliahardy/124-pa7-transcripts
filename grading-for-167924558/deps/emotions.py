# negative emotions from: https://www.berkeleywellbeing.com/negative-emotions.html
negative_emotions = {
    'annoi', 'unnerv', 'nervou', 'sullen', 'gloomi', 'jealousi', 'possess', 'restless', 'melancholi', 'uncertainti', 'weak', 'homesick', 'loopi', 'cowardli', 'shock', 'grumpi', 'miserli', 'self-doubt', 'disgruntl', 'shame', 'unhappi', 'furi', 'ruthless', 'bore', 'offend', 'rattl', 'mad', 'indign', 'lone', 'perplex', 'dismai', 'agit', 'agoni', 'self-consci', 'submiss', 'dispirit', 'hate', 'vulner', 'afraid', 'upset', 'torment', 'unsur', 'irrit', 'miser', 'bitter', 'apathi', 'revuls', 'aggress', 'pessim', 'contempt', 'panick', 'disturb', 'disgust', 'dislik', 'self-crit', 'envi', 'demor', 'remors', 'bewild', 'neg', 'stubborn', 'numb', 'loath', 'ennui', 'reject', 'glum', 'distress', 'dumbstruck', 'exasper', 'humili', 'undermin', 'hopeless', 'lazi', 'terror', 'nasti', 'fright', 'confus', 'veng', 'discombobul', 'sad', 'resent', 'guilt', 'long', 'displeasur', 'suspici', 'mortifi', 'obstin', 'fear', 'grief', 'vigil', 'coerciv', 'helpless', 'insecur', 'claustrophob', 'brood', 'stuck', 'depress', 'tire', 'greed', 'nauseat', 'alarm', 'frustrat', 'scare', 'spite', 'viciou', 'dishearten', 'insult', 'suffer', 'discontent', 'piti', 'disappoint', 'hysteria', 'self-piti', 'sorrow', 'reluct', 'discomfort', 'unsettl', 'moodi', 'stress', 'impati', 'regret', 'overwhelm', 'self-loath', 'dread', 'anguish', 'despair', 'rage', 'paranoid', 'hurt', 'doubt', 'uneasi', 'anxiou', 'embarrass', 'infuri', 'isol', 'daze', 'outrag', 'avers', 'wrath', 'neglect', 'anger', 'apprehens', 'horrifi', 'puzzl', 'troubl', 'grouchi', 'woe', 'worri', 'deject', 'scorn', 'baffl', 'powerless', 'smug', 'mixed up', 'tension', 'resign', 'disori', 'alien', 'cruel'
}

# positive emotions from: https://www.berkeleywellbeing.com/positive-emotions.html

positive_emotions = {
'lust', 'nostalg', 'relax', 'modesti', 'cheer', 'anticip', 'enjoy', 'seren', 'cynic', 'interest', 'amus', 'euphoria', 'Schadenfreud', 'excit', 'self-compassion', 'strong', 'intrigu', 'surpris', 'self-confid', 'friendli', 'affect', 'satisfact', 'joi', 'determin', 'glee', 'calm', 'pride', 'like', 'mystifi', 'happi', 'hope', 'delight', 'trust', 'enchant', 'attract', 'pleasur', 'driven', 'courag', 'self-car', 'pleas', 'kind', 'love', 'care', 'posit', 'fascin', 'amaz', 'empathi', 'reliev', 'optimist', 'epiphani', 'insight', 'self-motiv', 'domin', 'carefre', 'jubil', 'focus', 'eager', 'cheeki', 'sympathi', 'thrill', 'enthusiasm', 'accept', 'ador', 'jovial', 'expect', 'triumphant', 'sentiment', 'self-understand', 'aw', 'assert', 'fond', 'ecstasi', 'gratitud', 'curios', 'elat', 'content', 'comfort', 'attent', 'self-respect', 'admir', 'humil', 'worthi', 'bliss', 'infatu', 'passion', 'confid', 'brazen', 'thank', 'enlighten', 'tender'
}

def is_negative_emotion(token):
    return token in negative_emotions

def is_positive_emotion(token):
    return token in positive_emotions