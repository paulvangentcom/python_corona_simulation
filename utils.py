'''
collection of utility methods shared across files
'''

import os

def check_folder(folder='render/'):
    '''check if folder exists, make if not present'''
    if not os.path.exists(folder):
            os.makedirs(folder)