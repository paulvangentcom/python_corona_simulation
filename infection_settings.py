class InfectionSettings:

    def __init__(self, *args, **kwargs):
        self.infection_range = kwargs.get('infection_range',
                                          0.01)  # range surrounding sick patient that infections can take place
        self.infection_chance = kwargs.get('infection_chance',
                                           0.03)  # chance that an infection spreads to nearby healthy people each tick
        self.recovery_duration = kwargs.get('recovery_duration',
                                            (200, 500))  # how many ticks it may take to recover from the illness
        self.mortality_chance = kwargs.get('mortality_chance', 0.02)  # global baseline chance of dying from the disease

    def get(self, key):
        '''gets key value from config'''
        try:
            return self.__dict__[key]
        except:
            raise Exception('key %s not present in config' % key)

    def set(self, key, value):
        '''sets key value in config'''
        self.__dict__[key] = value