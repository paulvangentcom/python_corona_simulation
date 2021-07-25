class PopulationSettings:

    def __init__(self, *args, **kwargs):
        self.pop_size = kwargs.get('pop_size', 2000)
        self.mean_age = kwargs.get('mean_age', 45)
        self.max_age = kwargs.get('max_age', 105)
        self.age_dependent_risk = kwargs.get('age_dependent_risk', True)  # whether risk increases with age
        self.risk_age = kwargs.get('risk_age', 55)  # age where mortality risk starts increasing
        self.critical_age = kwargs.get('critical_age', 75)  # age at and beyond which mortality risk reaches maximum
        self.critical_mortality_chance = kwargs.get('critical_mortality_chance',
                                                    0.1)  # maximum mortality risk for older age
        self.risk_increase = kwargs.get('risk_increase',
                                        'quadratic')  # whether risk between risk and critical age increases 'linear' or 'quadratic'

    def get(self, key):
        '''gets key value from config'''
        try:
            return self.__dict__[key]
        except:
            raise Exception('key %s not present in config' % key)

    def set(self, key, value):
        '''sets key value in config'''
        self.__dict__[key] = value