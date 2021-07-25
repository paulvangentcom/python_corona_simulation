class HealthcareSettings:

    def __init__(self, *args, **kwargs):
        self.healthcare_capacity = kwargs.get('healthcare_capacity', 300)  # capacity of the healthcare system
        self.treatment_factor = kwargs.get('treatment_factor', 0.5)  # when in treatment, affect risk by this factor
        self.no_treatment_factor = kwargs.get('no_treatment_factor',
                                              3)  # risk increase factor to use if healthcare system is full
        # risk parameters
        self.treatment_dependent_risk = kwargs.get('treatment_dependent_risk',
                                                   True)  # whether risk is affected by treatment

    def get(self, key):
        '''gets key value from config'''
        try:
            return self.__dict__[key]
        except:
            raise Exception('key %s not present in config' % key)

    def set(self, key, value):
        '''sets key value in config'''
        self.__dict__[key] = value