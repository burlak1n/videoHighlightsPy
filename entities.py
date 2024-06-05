from collections import deque

# Дека, в которой хранятся маркеры
class MarkDeq(deque):

    def __init__(self):
        super().__init__()
        self.currI = 0
    # Вставляет v в координатную прямую. Удаляет, если v есть в деке
    def insertV(self, v):
        l = len(self)
        try:
            self.remove(v)
            return
        except ValueError:
            pass
        for i in range(len(self)):
            if self[i] > v:
                self.insert(i, v)
                self.currI = i
                break
        print(i)
        if l == len(self):
            self.append(v)
            self.currI = i+1

    def printDeq(self):
        for i in self:
            print(i)

    def prev(self):
        pass
    def next(self):
        pass
    # side - bool. True - right
    def pos(self, p, side):
        try:
            i = self.index(p)
            return 
            # поменять позицию элемента, стоящего на маркере
        except ValueError:
            pass
    # def changePos(self) -> pos:
    #     return pos
        
# d = MarkDeq()
# d.insertV(10)
# d.insertV(200)
# d.insertV(400)
# d.printDeq()
# Надо почитать о том, как это можно ускорить. Эта либа через ffmpeg делает. Странно, что так долго