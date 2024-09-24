"""Loads each line of the file into a list and returns it."""

def file_input(filename):
    lines = []
    with open(filename) as file:
        for line in file:
            lines.append(line.strip())
    return lines