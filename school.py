from path_planning import set_destination
import numpy as np

'''
        builds School
    
        Defines school, Young people will go to the school at a fixed time, 
        and on the map you can see that the students will move in a normal 
        distribution at a set school location.
        
        Keyword arguments
        -----------------
        xmin : int or float
        xmax : int or float
        ymin : int or float
        ymax : int or float
        location showing below:

        (xmin,ymax)----------(xmax,ymax)
            |                   |
            |      School       |
            |                   |
        (xmin,ymin)----------(xmax,ymin)

        plt : matplotlib.pyplot object
            the plot object to which to append the hospital drawing
            if None, coordinates are returned
            
        Returns
        -------
        None
'''
class School:

    def __init__(self,xmin, xmax, ymin, ymax):
        
        self.destinations_location = []
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
   
    def display(self, plt,addcross):
        #plot walls
        plt.plot([self.xmin, self.xmin], [self.ymin, self.ymax], color = 'black')
        plt.plot([self.xmax, self.xmax], [self.ymin, self.ymax], color = 'black')
        plt.plot([self.xmin, self.xmax], [self.ymin, self.ymin], color = 'black')
        plt.plot([self.xmin, self.xmax], [self.ymax, self.ymax], color = 'black')
        #TODO: setting the hosptial location

    def go_to_school(self, population):
        max_studying_age = 18

        #If popluation exist people who age less than max studying age, then they need
        #go to school.
        if len(population[:7] < max_studying_age) > 0: 
           #some people who infected will go to the hospital
            active_dests = np.unique(population[:,7][population[:,7] < max_studying_age])
            

            #Go to hospital:
            for d in active_dests:
                dest_x = np.random.random(self.xmin,self.xmax)
                dest_y = np.random.random(self.ymin,self.ymax)

                #compute new headings
                head_x = dest_x - population[:,1]
                head_y = dest_y - population[:,2]

                #head_x = head_x / np.sqrt(head_x)
                #head_y = head_y / np.sqrt(head_y)

                #reinsert headings into population of those not at destination yet
                population[:,3][(population[:,11] == d) &
                                (population[:,12] == 0)] = head_x[(population[:,11] == d) &
                                                                    (population[:,12] == 0)]
                population[:,4][(population[:,11] == d) &
                                (population[:,12] == 0)] = head_y[(population[:,11] == d) &
                                                                    (population[:,12] == 0)]
                #set speed to 0.5
                population[:,5][(population[:,11] == d) &
                                (population[:,12] == 0)] = 0.05

        return population
            


        
    

    