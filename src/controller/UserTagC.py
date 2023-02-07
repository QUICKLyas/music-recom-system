class UserTagsController(object):
    def __init__(self, users, tags) -> None:
        self.users = users
        self.tags = tags

    def setUser(self, users):
        self.users = users

    def setTags(self, tags):
        self.tags = tags

    def getUsers(self):
        return self.users

    def getTags(self):
        return self.tags
