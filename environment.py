'''
file that contains all functions to define destinations in the 
environment of the simulated world.
'''

import numpy as np
from hospital import Hospital
from school import School
'''
    This class is used to save all environment change operations, 
    such as adding hospitals, adding residences, etc.
'''
class Environment:
    def __init__(self):
        self.building = []

    
    
    #This function could create the building base on the input(building name, *location)
    def create_building(self, building_type, xmin, xmax, ymin, ymax):

        if building_type == 'hospital':
            hospital = Hospital(xmin, xmax, ymin, ymax)
            self.building.append(hospital)
        elif building_type == 'school':
            school = School(xmin, xmax, ymin, ymax)
            self.building.append(school)

    # Drawing the building here
    def building_applied(self, plt, addcross):
        if self.building:
            for building in self.building:
                building.display(plt,addcross)

        


    