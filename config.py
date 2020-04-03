'''
file that contains all configuration related methods and classes
'''

import numpy as np

class config_error(Exception):
    pass

class Configuration():
    def __init__(self, *args, **kwargs):
        #simulation variables
        self.verbose = False #whether to print infections, recoveries and fatalities to the terminal
        self.simulation_steps = 10000 #total simulation steps performed
        self.tstep = 0 #current simulation timestep
        self.save_data = True #whether to dump data
        self.save_timesteps = True #dumps population data every time step
        self.endif_no_infections = True #whether to stop simulation if no infections remain

        #scenario flags
        self.traveling_infects = False
        self.self_isolate = False
        self.lockdown = False
        self.lockdown_percentage = 0.1 #after this proportion is infected, lock-down begins
        self.lockdown_compliance = 0.95 #fraction of the population that will obey the lockdown        

        #world variables, defines where population can and cannot roam
        self.xbounds = [0.02, 0.98]
        self.ybounds = [0.02, 0.98]
        
        #visualisation variables
        self.visualise = False #whether to visualise the simulation 
        self.plot_style = 'default'
        #size of the simulated world in coordinates
        self.x_plot = [0, 1] 
        self.y_plot = [0, 1]
        self.save_plot = False
        
        #population variables
        self.pop_size = 2000
        self.mean_age = 45
        self.max_age = 105
        self.age_dependent_risk = True #whether risk increases with age
        self.risk_age = 55 #age where mortality risk starts increasing
        self.critical_age = 75 #age at and beyond which mortality risk reaches maximum
        self.critical_mortality_chance = 0.1 #maximum mortality risk for older age
        self.risk_increase = 'quadratic' #whether risk between risk and critical age increases 'linear' or 'quadratic'
        
        #movement variables
        mean_speed = 0.01 # the mean speed (defined as heading * speed)
        std_speed = 0.01 / 3 #the standard deviation of the speed parameter
        #the proportion of the population that practices social distancing, simulated
        #by them standing still
        proportion_distancing = 0
        self.speed = 0.01 #TODO: look up wth this is
        #when people have an active destination, the wander range defines the area
        #surrounding the destination they will wander upon arriving
        self.wander_range = 0.05
        self.wander_factor = 1 
        self.wander_factor_dest = 1.5 #area around destination

        #infection variables
        self.infection_range=0.01 #range surrounding sick patient that infections can take place
        self.infection_chance=0.03   #chance that an infection spreads to nearby healthy people each tick
        self.recovery_duration=(200, 500) #how many ticks it may take to recover from the illness
        self.mortality_chance=0.02 #global baseline chance of dying from the disease

        #healthcare variables
        self.healthcare_capacity = 300 #capacity of the healthcare system
        self.treatment_factor = 0.5 #when in treatment, affect risk by this factor
        self.no_treatment_factor = 3 #risk increase factor to use if healthcare system is full
        #risk parameters
        self.treatment_dependent_risk = True #whether risk is affected by treatment

        #self isolation variables
        self.self_isolate_proportion = 0.6
        self.isolation_bounds = [0, 0, 0.1, 0.1]
        
        #lockdown variables
        self.lockdown_percentage = 0.1 
        self.lockdown_vector = []
        
        

    def get(self, key):
        '''gets key value from config'''
        try:
            return self.__dict__[key]
        except:
            raise config_error('key %s not present in config' %key)

    def set(self, key, value):
        '''sets key value in config'''
        self.__dict__[key] = value

    def read_from_file(self, path):
        '''reads config from filename'''
        #TODO: implement
        pass

    def set_lockdown(self, lockdown_percentage=0.1, lockdown_compliance=0.9):
        '''sets lockdown to active'''

        self.lockdown = True

        #fraction of the population that will obey the lockdown
        self.lockdown_compliance = lockdown_compliance
        self.lockdown_vector = np.zeros((pop_size,))
        #lockdown vector is 1 for those not complying
        self.lockdown_vector[np.random.uniform(size=(pop_size,)) >= lockdown_compliance] = 1

