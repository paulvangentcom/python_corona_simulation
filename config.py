'''
file that contains all configuration related methods and classes
'''

import numpy as np

class config_error(Exception):
    pass


class Configuration():
    def __init__(self, *args, **kwargs):
        #simulation variables
        self.verbose = kwargs.get('verbose', True) #whether to print infections, recoveries and fatalities to the terminal
        self.simulation_steps = kwargs.get('simulation_steps', 10000) #total simulation steps performed
        self.tstep = kwargs.get('tstep', 0) #current simulation timestep
        self.save_data = kwargs.get('save_data', False) #whether to dump data at end of simulation
        self.save_pop = kwargs.get('save_pop', False) #whether to save population matrix every 'save_pop_freq' timesteps
        self.save_pop_freq = kwargs.get('save_pop_freq', 10) #population data will be saved every 'n' timesteps. Default: 10
        self.save_pop_folder = kwargs.get('save_pop_folder', 'pop_data/') #folder to write population timestep data to
        self.endif_no_infections = kwargs.get('endif_no_infections', True) #whether to stop simulation if no infections remain

        #scenario flags
        self.traveling_infects = kwargs.get('traveling_infects', False)
        self.self_isolate = kwargs.get('self_isolate', False)
        self.lockdown = kwargs.get('lockdown', False)
        self.lockdown_percentage = kwargs.get('lockdown_percentage', 0.1) #after this proportion is infected, lock-down begins
        self.lockdown_compliance = kwargs.get('lockdown_compliance', 0.95) #fraction of the population that will obey the lockdown        

        #world variables, defines where population can and cannot roam
        self.xbounds = kwargs.get('xbounds', [0.02, 0.98])
        self.ybounds = kwargs.get('ybounds', [0.02, 0.98])
        
        #visualisation variables
        self.visualise = kwargs.get('visualise', True) #whether to visualise the simulation 
        self.plot_mode = kwargs.get('plot_mode', 'sir') #default or sir
        #size of the simulated world in coordinates
        self.x_plot = kwargs.get('x_plot', [0, 1])
        self.y_plot = kwargs.get('y_plot', [0, 1])
        self.save_plot = kwargs.get('save_plot', False)
        self.plot_path = kwargs.get('plot_path', 'render/') #folder where plots are saved to
        self.plot_style = kwargs.get('plot_style', 'default') #can be default, dark, ...
        self.colorblind_mode = kwargs.get('colorblind_mode', False)
        #if colorblind is enabled, set type of colorblindness
        #available: deuteranopia, protanopia, tritanopia. defauld=deuteranopia
        self.colorblind_type = kwargs.get('colorblind_type', 'deuteranopia')
        
        #population variables
        self.pop_size = kwargs.get('pop_size', 2000)
        self.mean_age = kwargs.get('mean_age', 45)
        self.max_age = kwargs.get('max_age', 105)
        self.age_dependent_risk = kwargs.get('age_dependent_risk', True) #whether risk increases with age
        self.risk_age = kwargs.get('risk_age', 55) #age where mortality risk starts increasing
        self.critical_age = kwargs.get('critical_age', 75) #age at and beyond which mortality risk reaches maximum
        self.critical_mortality_chance = kwargs.get('critical_mortality_chance', 0.1) #maximum mortality risk for older age
        self.risk_increase = kwargs.get('risk_increase', 'quadratic') #whether risk between risk and critical age increases 'linear' or 'quadratic'
        
        #movement variables
        #mean_speed = 0.01 # the mean speed (defined as heading * speed)
        #std_speed = 0.01 / 3 #the standard deviation of the speed parameter
        #the proportion of the population that practices social distancing, simulated
        #by them standing still
        self.proportion_distancing = kwargs.get('proportion_distancing', 0)
        self.speed = kwargs.get('speed', 0.01) #average speed of population
        #when people have an active destination, the wander range defines the area
        #surrounding the destination they will wander upon arriving
        self.wander_range = kwargs.get('wander_range', 0.05)
        self.wander_factor = kwargs.get('wander_factor', 1) 
        self.wander_factor_dest = kwargs.get('wander_factor_dest', 1.5) #area around destination

        #infection variables
        self.infection_range = kwargs.get('infection_range', 0.01) #range surrounding sick patient that infections can take place
        self.infection_chance = kwargs.get('infection_chance', 0.03)   #chance that an infection spreads to nearby healthy people each tick
        self.recovery_duration = kwargs.get('recovery_duration', (200, 500)) #how many ticks it may take to recover from the illness
        self.mortality_chance = kwargs.get('mortality_chance', 0.02) #global baseline chance of dying from the disease

        #healthcare variables
        self.healthcare_capacity = kwargs.get('healthcare_capacity', 300) #capacity of the healthcare system
        self.treatment_factor = kwargs.get('treatment_factor', 0.5) #when in treatment, affect risk by this factor
        self.no_treatment_factor = kwargs.get('no_treatment_factor', 3) #risk increase factor to use if healthcare system is full
        #risk parameters
        self.treatment_dependent_risk = kwargs.get('treatment_dependent_risk', True) #whether risk is affected by treatment

        #self isolation variables
        self.self_isolate_proportion = kwargs.get('self_isolate_proportion', 0.6)
        self.isolation_bounds = kwargs.get('isolation_bounds', [0.02, 0.02, 0.1, 0.98])
        
        #lockdown variables
        self.lockdown_percentage = kwargs.get('lockdown_percentage', 0.1) 
        self.lockdown_vector = kwargs.get('lockdown_vector', [])
        
        
    def get_palette(self):
        '''returns appropriate color palette

        Uses config.plot_style to determine which palette to pick, 
        and changes palette to colorblind mode (config.colorblind_mode)
        and colorblind type (config.colorblind_type) if required.

        Palette colors are based on
        https://venngage.com/blog/color-blind-friendly-palette/
        '''

        #palette colors are: [healthy, infected, immune, dead]
        palettes = {'regular': {'default': ['gray', 'red', 'green', 'black'],
                                'dark': ['#404040', '#ff0000', '#00ff00', '#000000']},
                    'deuteranopia': {'default': ['gray', '#a50f15', '#08519c', 'black'],
                                     'dark': ['#404040', '#fcae91', '#6baed6', '#000000']},
                    'protanopia': {'default': ['gray', '#a50f15', '08519c', 'black'],
                                   'dark': ['#404040', '#fcae91', '#6baed6', '#000000']},
                    'tritanopia': {'default': ['gray', '#a50f15', '08519c', 'black'],
                                   'dark': ['#404040', '#fcae91', '#6baed6', '#000000']}
                    }

        if self.colorblind_mode:
            return palettes[self.colorblind_type.lower()][self.plot_style]
        else:
            return palettes['regular'][self.plot_style]

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
        self.lockdown_percentage = lockdown_percentage
        self.lockdown_vector = np.zeros((self.pop_size,))
        #lockdown vector is 1 for those not complying
        self.lockdown_vector[np.random.uniform(size=(self.pop_size,)) >= lockdown_compliance] = 1


    def set_self_isolation(self, self_isolate_proportion=0.9,
                           isolation_bounds = [0.02, 0.02, 0.09, 0.98],
                           traveling_infects=False):
        '''sets self-isolation scenario to active'''

        self.self_isolate = True
        self.isolation_bounds = isolation_bounds
        self.self_isolate_proportion = self_isolate_proportion
        #set roaming bounds to outside isolated area
        self.xbounds = [0.1, 1.1]
        self.ybounds = [0.02, 0.98]
        #update plot bounds everything is shown
        self.x_plot = [0, 1.1]
        self.y_plot = [0, 1]
        #update whether traveling agents also infect
        self.traveling_infects = traveling_infects


    def set_reduced_interaction(self, speed = 0.001):
        '''sets reduced interaction scenario to active'''

        self.speed = speed


    def set_demo(self, destinations, population):
        #make C
        #first leg
        destinations[:,0][0:100] = 0.05
        destinations[:,1][0:100] = 0.7
        population[:,13][0:100] = 0.01
        population[:,14][0:100] = 0.05

        #Top
        destinations[:,0][100:200] = 0.1
        destinations[:,1][100:200] = 0.75
        population[:,13][100:200] = 0.05
        population[:,14][100:200] = 0.01

        #Bottom
        destinations[:,0][200:300] = 0.1
        destinations[:,1][200:300] = 0.65
        population[:,13][200:300] = 0.05
        population[:,14][200:300] = 0.01


        #make O
        #first leg
        destinations[:,0][300:400] = 0.2
        destinations[:,1][300:400] = 0.7
        population[:,13][300:400] = 0.01
        population[:,14][300:400] = 0.05

        #Top
        destinations[:,0][400:500] = 0.25
        destinations[:,1][400:500] = 0.75
        population[:,13][400:500] = 0.05
        population[:,14][400:500] = 0.01

        #Bottom
        destinations[:,0][500:600] = 0.25
        destinations[:,1][500:600] = 0.65
        population[:,13][500:600] = 0.05
        population[:,14][500:600] = 0.01

        #second leg
        destinations[:,0][600:700] = 0.3
        destinations[:,1][600:700] = 0.7
        population[:,13][600:700] = 0.01
        population[:,14][600:700] = 0.05


        #make V
        #First leg
        destinations[:,0][700:800] = 0.35
        destinations[:,1][700:800] = 0.7
        population[:,13][700:800] = 0.01
        population[:,14][700:800] = 0.05

        #Bottom
        destinations[:,0][800:900] = 0.4
        destinations[:,1][800:900] = 0.65
        population[:,13][800:900] = 0.05
        population[:,14][800:900] = 0.01

        #second leg
        destinations[:,0][900:1000] = 0.45
        destinations[:,1][900:1000] = 0.7
        population[:,13][900:1000] = 0.01
        population[:,14][900:1000] = 0.05

        #Make I
        #leg
        destinations[:,0][1000:1100] = 0.5
        destinations[:,1][1000:1100] = 0.7
        population[:,13][1000:1100] = 0.01
        population[:,14][1000:1100] = 0.05

        #I dot
        destinations[:,0][1100:1200] = 0.5
        destinations[:,1][1100:1200] = 0.8
        population[:,13][1100:1200] = 0.01
        population[:,14][1100:1200] = 0.01

        #make D
        #first leg
        destinations[:,0][1200:1300] = 0.55
        destinations[:,1][1200:1300] = 0.67
        population[:,13][1200:1300] = 0.01
        population[:,14][1200:1300] = 0.03

        #Top
        destinations[:,0][1300:1400] = 0.6
        destinations[:,1][1300:1400] = 0.75
        population[:,13][1300:1400] = 0.05
        population[:,14][1300:1400] = 0.01

        #Bottom
        destinations[:,0][1400:1500] = 0.6
        destinations[:,1][1400:1500] = 0.65
        population[:,13][1400:1500] = 0.05
        population[:,14][1400:1500] = 0.01

        #second leg
        destinations[:,0][1500:1600] = 0.65
        destinations[:,1][1500:1600] = 0.7
        population[:,13][1500:1600] = 0.01
        population[:,14][1500:1600] = 0.05

        #dash
        destinations[:,0][1600:1700] = 0.725
        destinations[:,1][1600:1700] = 0.7
        population[:,13][1600:1700] = 0.03
        population[:,14][1600:1700] = 0.01

        #Make 1
        destinations[:,0][1700:1800] = 0.8
        destinations[:,1][1700:1800] = 0.7
        population[:,13][1700:1800] = 0.01
        population[:,14][1700:1800] = 0.05


        #Make 9
        #right leg
        destinations[:,0][1800:1900] = 0.91
        destinations[:,1][1800:1900] = 0.675
        population[:,13][1800:1900] = 0.01
        population[:,14][1800:1900] = 0.08

        #roof
        destinations[:,0][1900:2000] = 0.88
        destinations[:,1][1900:2000] = 0.75
        population[:,13][1900:2000] = 0.035
        population[:,14][1900:2000] = 0.01

        #middle
        destinations[:,0][2000:2100] = 0.88
        destinations[:,1][2000:2100] = 0.7
        population[:,13][2000:2100] = 0.035
        population[:,14][2000:2100] = 0.01

        #left vertical leg
        destinations[:,0][2100:2200] = 0.86
        destinations[:,1][2100:2200] = 0.72
        population[:,13][2100:2200] = 0.01
        population[:,14][2100:2200] = 0.01

        ###################
        ##### ROW TWO #####
        ###################

        #S
        #first leg
        destinations[:,0][2200:2300] = 0.115
        destinations[:,1][2200:2300] = 0.5
        population[:,13][2200:2300] = 0.01
        population[:,14][2200:2300] = 0.03

        #Top
        destinations[:,0][2300:2400] = 0.15
        destinations[:,1][2300:2400] = 0.55
        population[:,13][2300:2400] = 0.05
        population[:,14][2300:2400] = 0.01

        #second leg
        destinations[:,0][2400:2500] = 0.2
        destinations[:,1][2400:2500] = 0.45
        population[:,13][2400:2500] = 0.01
        population[:,14][2400:2500] = 0.03

        #middle
        destinations[:,0][2500:2600] = 0.15
        destinations[:,1][2500:2600] = 0.48
        population[:,13][2500:2600] = 0.05
        population[:,14][2500:2600] = 0.01

        #bottom
        destinations[:,0][2600:2700] = 0.15
        destinations[:,1][2600:2700] = 0.41
        population[:,13][2600:2700] = 0.05
        population[:,14][2600:2700] = 0.01

        #Make I
        #leg
        destinations[:,0][2700:2800] = 0.25
        destinations[:,1][2700:2800] = 0.45
        population[:,13][2700:2800] = 0.01
        population[:,14][2700:2800] = 0.05

        #I dot
        destinations[:,0][2800:2900] = 0.25
        destinations[:,1][2800:2900] = 0.55
        population[:,13][2800:2900] = 0.01
        population[:,14][2800:2900] = 0.01

        #M
        #Top
        destinations[:,0][2900:3000] = 0.37
        destinations[:,1][2900:3000] = 0.5
        population[:,13][2900:3000] = 0.07
        population[:,14][2900:3000] = 0.01

        #Left leg
        destinations[:,0][3000:3100] = 0.31
        destinations[:,1][3000:3100] = 0.45
        population[:,13][3000:3100] = 0.01
        population[:,14][3000:3100] = 0.05

        #Middle leg
        destinations[:,0][3100:3200] = 0.37
        destinations[:,1][3100:3200] = 0.45
        population[:,13][3100:3200] = 0.01
        population[:,14][3100:3200] = 0.05

        #Right leg
        destinations[:,0][3200:3300] = 0.43
        destinations[:,1][3200:3300] = 0.45
        population[:,13][3200:3300] = 0.01
        population[:,14][3200:3300] = 0.05

        #set all destinations active
        population[:,11] = 1
