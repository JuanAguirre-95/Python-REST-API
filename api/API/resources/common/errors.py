class DbCreateError(Exception):
    def __init__(self,message):
        self.message = message

class DbReadError(Exception):
    def __init__(self,message):
        self.message = message

class DbUpdateError(Exception):
    def __init__(self,message):
        self.message = message

class DbDeleteError(Exception):
    def __init__(self,message):
        self.message = message

class DbListError(Exception):
    def __init__(self,message):
        self.message = message