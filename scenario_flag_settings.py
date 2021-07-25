class ScenarioFlagsSettings:

    def __init__(self, *args, **kwargs):
        self.traveling_infects = kwargs.get('traveling_infects', False)
        self.self_isolate = kwargs.get('self_isolate', False)
        self.lockdown = kwargs.get('lockdown', False)
        self.lockdown_percentage = kwargs.get('lockdown_percentage', 0.1)  # after this proportion is infected, lock-down begins
        self.lockdown_compliance = kwargs.get('lockdown_compliance', 0.95)  # fraction of the population that will obey the lockdown

    def get(self, key):
        '''gets key value from config'''
        try:
            return self.__dict__[key]
        except:
            raise Exception('key %s not present in config' % key)

    def set(self, key, value):
        '''sets key value in config'''
        self.__dict__[key] = value