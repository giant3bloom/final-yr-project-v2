import numpy as np 


def replace_negatives(mat1, mat2) :
    """
    Replace -1 in mat2 with opposite of mat1:
    0 in mat1 -> 1 in mat2
    1 in mat1 -> 0 in mat2
    """
    mat2_fixed = mat2.copy()
    mask = mat2_fixed == -1
    mat2_fixed[mask] = 1 - mat1[mask]  # replace -1 with opposite of mat1
    return mat2_fixed


def strink_matrix(mat) :
    """
    Takes a 21x21 matrix and removes even-index rows and columns,
    returning a 10x10 matrix.
    """
    return mat[1::2, 1::2]

def accuracy(orgin_mat, discovered) : 
    """
    Takes two 10x10 matrices, computes absolute difference per element,
    sums them, divides by 100, and returns the result.
    """
    discovered = replace_negatives(orgin_mat, discovered)

    diff = np.abs(orgin_mat - discovered)       # element-wise absolute difference
    total_diff = np.sum(diff)                   # sum of all differences
    score = total_diff / 100.0                  # normalize
    return 1 - score

def move_accuracy(steps_taken, max_steps = 420) :
    """
    Takes no.of steps taken with the max_steps 
    returns a value between 0->1 as efficiency score
    """ 
    
    return  1 - (steps_taken / max_steps)

def absolute_accuracy(orgin_mat, discovered, steps_taken, max_steps=450, x=7, y=3):
    """
    Combines base accuracy and step efficiency into a single score.
    Returns a value between 0 and 1.
    """
    base_accuracy = accuracy(orgin_mat, discovered)
    step_score = move_accuracy(steps_taken, max_steps)

    abs_acc = (x * base_accuracy + y * step_score) / (x + y)
    
    return abs_acc