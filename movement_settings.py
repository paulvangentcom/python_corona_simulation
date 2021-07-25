class MovementSettings:

    def __init__(self, *args, **kwargs):
        # mean_speed = 0.01 # the mean speed (defined as heading * speed)
        # std_speed = 0.01 / 3 #the standard deviation of the speed parameter
        # the proportion of the population that practices social distancing, simulated
        # by them standing still
        self.proportion_distancing = kwargs.get('proportion_distancing', 0)
        self.speed = kwargs.get('speed', 0.01)  # average speed of population
        # when people have an active destination, the wander range defines the area
        # surrounding the destination they will wander upon arriving
        self.wander_range = kwargs.get('wander_range', 0.05)
        self.wander_factor = kwargs.get('wander_factor', 1)
        self.wander_factor_dest = kwargs.get('wander_factor_dest', 1.5)  # area around destination

    def get(self, key):
        '''gets key value from config'''
        try:
            return self.__dict__[key]
        except:
            raise Exception('key %s not present in config' % key)

    def set(self, key, value):
        '''sets key value in config'''
        self.__dict__[key] = value