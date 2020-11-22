import random
import numpy as np

def get_random_ages(n):
    probabilities = [
        0.08790890062535199,
        0.09554494604383408,
        0.09764393164843278,
        0.11804435810521348,
        0.1581454497526682,
        0.15567451717963607,
        0.11750413048003026,
        0.09882497758080205,
        0.0707087885840311
    ]
    
    ages = [a for i, p in enumerate(probabilities) for a in list(range(i * 10, i * 10 + 10))]
    weights = [p for i, p in enumerate(probabilities) for a in list(range(i * 10, i * 10 + 10))]
    
    return random.choices(population=ages, weights=weights, k=n)