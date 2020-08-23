from database import create_row, update_row

class Video:
    def __init__(self, id, url, title, status, status_message, dir):
        self.id = id
        self.url = url
        self.title = title
        self.status = status
        self.status_message = status_message
        self.dir = dir

    # A save method can be utilized to update the DB for a single model
    # We are not modifying records via the interface, only from the Queue during processing
    def save(self):
        update_row(self.id, self.url, self.title, self.status, self.status_message, self.dir)

    def toJson(self):
        return {
            'id':self.id,
            'type':'video',
            'attributes': {
                'url':self.url,
                'title':self.title,
                'status':self.status,
                'statusMessage':self.status_message,
                'directory':self.dir
            }
            
        }
    # Could we add other database access methods here?