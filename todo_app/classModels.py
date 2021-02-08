import datetime

class ViewModel:
        def __init__(self, items):
            self._items = items
            self._ToDo = items
            self._Doing = items
            self._Done = items
            self._recentDone = items
            self._olderDone = items
        
        @property
        def items(self):
            return self._items

        @property
        def statusToDo(self):
            updated_items = []
            for val in self._items:
                if (val['status']== "To Do"):
                    item = { 'id': val["id"], 'title': val["title"], 'status': "To Do", 'DateUpdated':val["DateUpdated"] }
                    updated_items.append(item)
            self._ToDo = updated_items
            return self._ToDo
        
        @property
        def statusDoing(self):
            updated_items2 = []
            for val in self._items:
                if (val['status']== "Doing"):
                    item = { 'id': val["id"], 'title': val["title"], 'status': "Doing", 'DateUpdated':val["DateUpdated"] }
                    updated_items2.append(item)
            self._Doing = updated_items2
            return self._Doing 
        
        @property
        def show_all_done_items(self):
            updated_items3 = []
            for val in self._items:
                if (val['status']== "Done"):
                    item = { 'id': val["id"], 'title': val["title"], 'status': "Done", 'DateUpdated':val["DateUpdated"] }
                    updated_items3.append(item)
            self._Done = updated_items3
            
            if len(self._Done) < 5:
                return self._Done
            else:
                updated_items3 = []
                updated_items4 = []
                present = datetime.now()
                for val in self._items:
                    value = datetime.strptime(val['DateUpdated'], "%d/%m/%Y")
                    item = { 'id': val["id"], 'title': val["title"], 'status': "Done", 'DateUpdated':val["DateUpdated"] }
                    if (value.date() == present.date()):
                        updated_items3.append(item)
                    else:
                        updated_items4.append(item)
                        self._olderDone = updated_items4
                        self._recentDone = updated_items3
                return self._recentDone

        @property
        def recent_done_items(self): 
                return self._recentDone 
        
        @property
        def older_done_items(self): 
            return self._olderDone