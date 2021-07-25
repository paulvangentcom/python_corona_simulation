
class SimulationSettings:
    def __init__(self, *args, **kwargs):
        #Simulation variables
        self.verbose = kwargs.get('verbose',
                                  True)  # whether to print infections, recoveries and fatalities to the terminal
        self.simulation_steps = kwargs.get('simulation_steps', 10000)  # total simulation steps performed
        self.tstep = kwargs.get('tstep', 0)  # current simulation timestep
        self.save_data = kwargs.get('save_data', False)  # whether to dump data at end of simulation
        self.save_pop = kwargs.get('save_pop',
                                   False)  # whether to save population matrix every 'save_pop_freq' timesteps
        self.save_pop_freq = kwargs.get('save_pop_freq',
                                        10)  # population data will be saved every 'n' timesteps. Default: 10
        self.save_pop_folder = kwargs.get('save_pop_folder', 'pop_data/')  # folder to write population timestep data to
        self.endif_no_infections = kwargs.get('endif_no_infections',
                                              True)  # whether to stop simulation if no infections remain
        self.world_size = kwargs.get('world_size', [2, 2])  # x and y sizes of the world

    def get(self, key):
        '''gets key value from config'''
        try:
            return self.__dict__[key]
        except:
            raise Exception('key %s not present in config' % key)

    def set(self, key, value):
        '''sets key value in config'''
        self.__dict__[key] = value