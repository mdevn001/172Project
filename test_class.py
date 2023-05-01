class Node:

        def __init__(self):
            self.parent = None
            self.depth = 0;
            self.url =None;
            
        def assign_parent(self,parent):
            self.parent = parent;
            self.depth = parent.depth+1;

