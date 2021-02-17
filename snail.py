def snail(matrix):
    """
    Given a 2 dimensional array with values, size can be anything. You have to give back an array so that 
    you travel the array clockwise and moving like a snail's house.
    """
    length_of_matrix = len(matrix)
    start = 0
    counter = 1
    result = []
    #Check if the array is one dimensional and has one item
    #if so, give it back as a result
    if (length_of_matrix == 1 and len(matrix[0]) == 1):
        result = matrix[0]
    #Check if the input array is empty
    #if so, give back an empty list as result
    elif (length_of_matrix == 1):
        result = []
    else:
        for i in range(length_of_matrix + length_of_matrix):
            #Right
            if (counter == 1):
                for j in range(start,length_of_matrix):
                    result.append(matrix[start][j])
            #Down
            elif (counter == 2):
                for j in range(start + 1, length_of_matrix - 1):
                    result.append(matrix[j][length_of_matrix - 1])
            #Left
            elif (counter == 3):
                for j in range(length_of_matrix - 1, start, -1):
                    result.append(matrix[length_of_matrix - 1][j])
            #Up
            elif (counter == 4):
                for j in range(length_of_matrix - 1, start, -1):
                    result.append(matrix[j][start])
                counter = 0
                start += 1
                length_of_matrix -=1
            counter += 1

    return result

def test_snail():
    assert snail([[1 ,2, 3, 4, 5],[16,17,18,19,6],[15,24,25,20,7],[14,23,22,21,8],[13,12,11,10,9]]) == [1,2,3,4,5,
            6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]
    assert snail([[1,2,3],[4,5,6],[7,8,9]]) == [1,2,3,6,9,8,7,4,5]
