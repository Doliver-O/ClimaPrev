class User:
    def __init__(self,login):
        self.login = login

    def is_authenticated():
        return True
        
    def is_active(self):
        return True
    
    def is_anonymous():
        return False
    
    def get_id(self):
        return self.login
        
    def get_user(self):
        if self.login != '':
            return self.login
        else:
            return None