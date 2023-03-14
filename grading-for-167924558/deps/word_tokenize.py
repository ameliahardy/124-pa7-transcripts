def word_tokenize(line):
    punctuation = {'"', "'", ':', ';', ',', '.', '?', '!'}
    tokens = line.split(' ')
    res = []
    for token in tokens:
        start = 0
        while start < len(token) and token[start] in punctuation:
            start += 1
        if start > 0:
            for i in range(start):
                res.append(token[i])
        
        end = -1
        while len(token) + end > 0 and token[end] in punctuation:
            end -= 1
        
        if end < -1:
            res.append(token[start:end + 1])
        else:
            res.append(token[start:])

        if end < -1:
            for i in range(len(token) + end + 1, len(token)):
                res.append(token[i])
    return res