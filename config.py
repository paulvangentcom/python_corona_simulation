'''
file that contains all configuration related methods and classes
'''

import numpy as np

class config_error(Exception):
    pass


class Configuration():
    def __init__(self, *args, **kwargs):
        #simulation variables
        self.__verbose = kwargs.get('verbose', True) #whether to print infections, recoveries and fatalities to the terminal
        self.__simulation_steps = kwargs.get('simulation_steps', 10000) #total simulation steps performed
        self.__tstep = kwargs.get('tstep', 0) #current simulation timestep
        self.__save_data = kwargs.get('save_data', False) #whether to dump data at end of simulation
        self.__save_pop = kwargs.get('save_pop', False) #whether to save population matrix every 'save_pop_freq' timesteps
        self.__save_pop_freq = kwargs.get('save_pop_freq', 10) #population data will be saved every 'n' timesteps. Default: 10
        self.__save_pop_folder = kwargs.get('save_pop_folder', 'pop_data/') #folder to write population timestep data to
        self.__endif_no_infections = kwargs.get('endif_no_infections', True) #whether to stop simulation if no infections remain
        self.__world_size = kwargs.get('world_size', [2, 2]) #x and y sizes of the world


        #scenario flags
        self.__traveling_infects = kwargs.get('traveling_infects', False)
        self.__self_isolate = kwargs.get('self_isolate', False)
        self.__lockdown = kwargs.get('lockdown', False)

        #visualisation variables
        self.__visualise = kwargs.get('visualise', True) #whether to visualise the simulation
        self.__plot_mode = kwargs.get('plot_mode', 'sir') #default or sir
        #size of the simulated world in coordinates
        self.__x_plot = kwargs.get('x_plot', [0, self.__world_size[0]])
        self.__y_plot = kwargs.get('y_plot', [0, self.__world_size[1]])
        self.__save_plot = kwargs.get('save_plot', False)
        self.__plot_path = kwargs.get('plot_path', 'render/') #folder where plots are saved to
        self.__plot_style = kwargs.get('plot_style', 'default') #can be default, dark, ...
        self.__colorblind_mode = kwargs.get('colorblind_mode', False)
        #if colorblind is enabled, set type of colorblindness
        #available: deuteranopia, protanopia, tritanopia. defauld=deuteranopia
        self.__colorblind_type = kwargs.get('colorblind_type', 'deuteranopia')
        
        #world variables, defines where population can and cannot roam
        self.__xbounds = kwargs.get('xbounds', [self.__x_plot[0] + 0.02, self.__x_plot[1] - 0.02])
        self.__ybounds = kwargs.get('ybounds', [self.__y_plot[0] + 0.02, self.__y_plot[1] - 0.02])
    
        #population variables
        self.__pop_size = kwargs.get('pop_size', 2000)
        self.__mean_age = kwargs.get('mean_age', 45)
        self.__max_age = kwargs.get('max_age', 105)
        self.__age_dependent_risk = kwargs.get('age_dependent_risk', True) #whether risk increases with age
        self.__risk_age = kwargs.get('risk_age', 55) #age where mortality risk starts increasing
        self.__critical_age = kwargs.get('critical_age', 75) #age at and beyond which mortality risk reaches maximum
        self.__critical_mortality_chance = kwargs.get('critical_mortality_chance', 0.1) #maximum mortality risk for older age
        self.__risk_increase = kwargs.get('risk_increase', 'quadratic') #whether risk between risk and critical age increases 'linear' or 'quadratic'
        
        #movement variables
        #mean_speed = 0.01 # the mean speed (defined as heading * speed)
        #std_speed = 0.01 / 3 #the standard deviation of the speed parameter
        #the proportion of the population that practices social distancing, simulated
        #by them standing still
        self.__proportion_distancing = kwargs.get('proportion_distancing', 0)
        self.__speed = kwargs.get('speed', 0.01) #average speed of population
        #when people have an active destination, the wander range defines the area
        #surrounding the destination they will wander upon arriving
        self.__wander_range = kwargs.get('wander_range', 0.05)
        self.__wander_factor = kwargs.get('wander_factor', 1)
        self.__wander_factor_dest = kwargs.get('wander_factor_dest', 1.5) #area around destination

        #infection variables
        self.__infection_range = kwargs.get('infection_range', 0.01) #range surrounding sick patient that infections can take place
        self.__infection_chance = kwargs.get('infection_chance', 0.03)   #chance that an infection spreads to nearby healthy people each tick
        self.__recovery_duration = kwargs.get('recovery_duration', (200, 500)) #how many ticks it may take to recover from the illness
        self.__mortality_chance = kwargs.get('mortality_chance', 0.02) #global baseline chance of dying from the disease

        #healthcare variables
        self.__healthcare_capacity = kwargs.get('healthcare_capacity', 300) #capacity of the healthcare system
        self.__treatment_factor = kwargs.get('treatment_factor', 0.5) #when in treatment, affect risk by this factor
        self.__no_treatment_factor = kwargs.get('no_treatment_factor', 3) #risk increase factor to use if healthcare system is full
        #risk parameters
        self.__treatment_dependent_risk = kwargs.get('treatment_dependent_risk', True) #whether risk is affected by treatment

        #self isolation variables
        self.__self_isolate_proportion = kwargs.get('self_isolate_proportion', 0.6)
        self.__isolation_bounds = kwargs.get('isolation_bounds', [0.02, 0.02, 0.1, 0.98])
        
        #lockdown variables
        self.__lockdown_percentage = kwargs.get('lockdown_percentage', 0.1)
        self.__lockdown_vector = kwargs.get('lockdown_vector', [])
        self.__lockdown_compliance = kwargs.get('lockdown_compliance', 0.95) #fraction of the population that will obey the lockdown

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

        if self.__colorblind_mode:
            return palettes[self.__colorblind_type.lower()][self.__plot_style]
        else:
            return palettes['regular'][self.__plot_style]

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

    #set & set funtions
    #simulation variables
    def get_verbose(self):
        return self.__verbose

    def set_simulation_steps(self, steps):
        self.__simulation_steps = steps

    def get_simulation_steps(self):
        return self.__simulation_steps

    def get_save_data(self):
        return self.__save_data
    def get_save_pop(self):
        return self.__save_pop

    def get_save_pop_freq(self):
        return self.__save_pop_freq

    def get_save_pop_folder(self):
        return self.__save_pop_folder

    def get_endif_no_infections(self):
        return self.__endif_no_infections

    #scenario flags
    def get_traveling_infects(self):
        return self.__traveling_infects

    def set_self_isolation(self, self_isolate_proportion=0.9,
                           isolation_bounds = [0.02, 0.02, 0.09, 0.98],
                           traveling_infects=False):
        '''sets self-isolation scenario to active'''

        self.__self_isolate = True
        self.__isolation_bounds = isolation_bounds
        self.__self_isolate_proportion = self_isolate_proportion
        #set roaming bounds to outside isolated area
        self.__xbounds = [0.1, 1.1]
        self.__ybounds = [0.02, 0.98]
        #update plot bounds everything is shown
        self.__x_plot = [0, 1.1]
        self.__y_plot = [0, 1]
        #update whether traveling agents also infect
        self.__traveling_infects = traveling_infects

    def get_self_isolate(self):
        return self.__self_isolate

    def set_lockdown(self, lockdown_percentage=0.1, lockdown_compliance=0.9):
        '''sets lockdown to active'''

        self.__lockdown = True

        # fraction of the population that will obey the lockdown
        self.__lockdown_percentage = lockdown_percentage
        self.__lockdown_vector = np.zeros((self.__pop_size,))
        # lockdown vector is 1 for those not complying
        self.__lockdown_vector[np.random.uniform(size=(self.__pop_size,)) >= lockdown_compliance] = 1

    def get_lockdown(self):
        return self.__lockdown

    def set_reduced_interaction(self, speed = 0.001):
        '''sets reduced interaction scenario to active'''

        self.__speed = speed

    #visualisation variables
    def get_visualise(self):
        return self.__visualise

    def get_plot_mode(self):
        return self.__plot_mode

    #size of the simulated world in coordinates
    def get_x_plot(self):
        return self.__x_plot

    def get_y_plot(self):
        return self.__y_plot

    def get_save_plot(self):
        return self.__save_plot

    def set_plot_style(self, style = 'default'):
        self.__plot_style = style

    def get_plot_style(self):
        return self.__plot_style

    #if colorblind is enabled, set type of colorblindness
    #available: deuteranopia, protanopia, tritanopia
    def set_colorblind(self, mode = False, type = 'deuteranopia'):
        self.__colorblind_mode = mode
        self.__colorblind_type = type

    #world variables
    def get_xbounds(self):
        return self.__xbounds

    def get_ybounds(self):
        return self.__ybounds

    #population variables
    def get_pop_size(self):
        return self.__pop_size

    def get_mean_age(self):
        return self.__mean_age

    def get_max_age(self):
        return self.__max_age

    def get_age_dependent_risk(self):
        return self.__age_dependent_risk

    def get_risk_age(self):
        return self.__risk_age

    def get_critical_age(self):
        return self.__critical_age

    #movement variables
    def get_speed(self):
        return self.__speed

    def get_wander_factor(self):
        return self.__wander_factor

    def get_wander_factor_dest(self):
        return self.__wander_factor_dest

    #infection variables
    def get_infection_range(self):
        return self.__infection_range

    def get_infection_chance(self):
        return self.__infection_chance

    def get_recovery_duration(self):
        return self.__recovery_duration

    def get_mortality_chance(self):
        return self.__mortality_chance

    #healthcare variables
    def get_healthcare_capacity(self):
        return self.__healthcare_capacity

    def get_no_treatment_factor(self):
        return self.__no_treatment_factor

    def get_treatment_dependent_risk(self):
        return self.__treatment_dependent_risk

    #risk parameters
    def get_self_isolate_proportion(self):
        return self.__self_isolate_proportion

    def get_isolation_bounds(self):
        return self.__isolation_bounds

    #self isolation variables

    #lockdown variables
    def get_lockdown_percentage(self):
        return self.__lockdown_percentage

    def get_lockdown_vector(self):
        return self.__lockdown_vector


    #demo
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
