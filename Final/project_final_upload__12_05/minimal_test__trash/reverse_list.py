def reli(lists):

    return [[element for element in sublist[::-1]] for sublist in lists]


print(reli([[1,'A'],[4,'C'],['3','B']]))