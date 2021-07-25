'''
file that contains all configuration related methods and classes
'''

import numpy as np

from bounds_settings import BoundsSettings
from healthcare_settings import HealthcareSettings
from infection_settings import InfectionSettings
from lock_down_settings import LockDownSetting
from movement_settings import MovementSettings
from population_settings import PopulationSettings
from scenario_flag_settings import ScenarioFlagsSettings
from self_isolation_settings import SelfIsolationSetting
from simulation_settings import SimulationSettings
from visualisation_settings import VisualisationSettings


class config_error(Exception):
    pass


class Configuration:

    config = None

    #Singleton pattern ensuring one instance of Configuration class
    @staticmethod
    def get_instance(*args, **kwargs):
        if Configuration.config is not None:
            return Configuration.config
        Configuration.config = Configuration()
        return Configuration.config

    def __init__(self, *args, **kwargs):
        #Simulation settings
        self.simulation = SimulationSettings(args, kwargs)

        #scenario flags setting
        self.flags = ScenarioFlagsSettings(args, kwargs)
        
        #visualisation variables
        self.visualisation = VisualisationSettings(self.simulation.world_size[0], self.simulation.world_size[1],
                                                   args, kwargs)

        # world variables, defines where population can and cannot roam
        self.bounds = BoundsSettings(self.visualisation.x_plot, self.visualisation.y_plot,
                                     args, kwargs)

        #population variables
        self.population = PopulationSettings(args, kwargs)

        # movement variables
        self.movement = MovementSettings(args, kwargs)

        #infection variables
        self.infections = InfectionSettings(args, kwargs)

        #healthcare variables
        self.healthcare = HealthcareSettings(args, kwargs)

        #self isolation variables
        self.isolation = SelfIsolationSetting(args, kwargs)

        #lockdown variables
        self.lockdown = LockDownSetting(args, kwargs)

        
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

        if self.visualisation.colorblind_mode:
            return palettes[self.visualisation.colorblind_type.lower()][self.visualisation.plot_style]
        else:
            return palettes['regular'][self.visualisation.plot_style]


    def read_from_file(self, path):
        '''reads config from filename'''
        #TODO: implement
        pass


    def set_lockdown(self, lockdown_percentage=0.1, lockdown_compliance=0.9):
        '''sets lockdown to active'''

        self.flags.lockdown = True

        #fraction of the population that will obey the lockdown
        self.flags.lockdown_percentage = lockdown_percentage
        self.lockdown.lockdown_vector = np.zeros((self.pop_size,))
        #lockdown vector is 1 for those not complying
        self.lockdown.lockdown_vector[np.random.uniform(size=(self.population.pop_size,)) >= lockdown_compliance] = 1


    def set_self_isolation(self, self_isolate_proportion=0.9,
                           isolation_bounds = [0.02, 0.02, 0.09, 0.98],
                           traveling_infects=False):
        '''sets self-isolation scenario to active'''

        self.flags.self_isolate = True
        self.isolation.isolation_bounds = isolation_bounds
        self.isolation.self_isolate_proportion = self_isolate_proportion
        #set roaming bounds to outside isolated area
        self.bounds.xbounds = [0.1, 1.1]
        self.bounds.ybounds = [0.02, 0.98]
        #update plot bounds everything is shown
        self.visualisation.x_plot = [0, 1.1]
        self.visualisation.y_plot = [0, 1]
        #update whether traveling agents also infect
        self.flags.traveling_infects = traveling_infects


    def set_reduced_interaction(self, speed = 0.001):
        '''sets reduced interaction scenario to active'''

        self.movement.speed = speed


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

