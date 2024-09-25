"""
Author: Maharshi Patel, 000738366
Date: 24-09-2024
Description: This module contains functions for loading data from text files.
"""
def file_input(filename):
    """
        Loads each line of the file into a list, stripping whitespace, and returns it.
        
        Args:
            filename (str): The path to the file to be read.
        
        Returns:
            list: A list containing each line from the file as a stripped string.
    """
    # Initialize an empty list to store lines from the file.
    lines = []
    with open(filename) as file:
        for line in file:
            # Strip whitespace and append each line to the list.
            lines.append(line.strip())
    return lines