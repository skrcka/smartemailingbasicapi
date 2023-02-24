class ContactList:
    def __init__(self, name, publicname, sendername, senderemail, replyto=None, id=None):
        self.id = id
        self.name = name
        self.publicname = publicname
        self.sendername = sendername
        self.senderemail = senderemail
        self.replyto = replyto if replyto else senderemail
        