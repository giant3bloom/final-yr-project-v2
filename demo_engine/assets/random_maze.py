import numpy as np

def random_maze(seed=None):
    if seed is not None:
        np.random.seed(seed)  # Set the seed for reproducibility
    # Create a 10x10 matrix with random 0s and 1s
    return np.random.randint(0, 2, size=(10, 10))

def expand_with_gaps(matrix):
    # Step 1: Insert zeros between columns
    expanded = np.insert(matrix, range(0, matrix.shape[1]+1), 0, axis=1)
    
    # Step 2: Insert zeros between rows
    expanded = np.insert(expanded, range(0, matrix.shape[0]+1), 0, axis=0)
    
    return expanded

if __name__ == "__main__" : 
    maze = random_maze()
    print(maze)
    print(expand_with_gaps(maze))
