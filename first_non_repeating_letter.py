def first_non_repeating_letter(string):
    lowercase_string = string.lower()
    result = []
    for i in lowercase_string:
        if (lowercase_string.count(i) == 1):
            result.append(i)
    if (len(result) == 0): 
        return ""
    else:
        if (string.find(result[0]) == -1 ):
            return result[0].upper()
        else:
            return result[0]

def test_first_non_repeating_letter():
    assert first_non_repeating_letter("stress") == 't' 
    assert first_non_repeating_letter("") == ''
    assert first_non_repeating_letter("aabb") == ''
    assert first_non_repeating_letter("sTreSS") == 'T'
