class LockDownSetting:
    def __init__(self, *args, **kwargs):
        self.lockdown_percentage = kwargs.get('lockdown_percentage', 0.1)
        self.lockdown_vector = kwargs.get('lockdown_vector', [])

    def get(self, key):
        '''gets key value from config'''
        try:
            return self.__dict__[key]
        except:
            raise Exception('key %s not present in config' % key)

    def set(self, key, value):
        '''sets key value in config'''
        self.__dict__[key] = value