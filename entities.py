from collections import deque

arrSide = {'>': True, '<': False}
bookmarkM = {}
# Дека, в которой хранятся маркеры
class MarkDeq(deque):

    def __init__(self):
        super().__init__()
        # self.currI = 0

    # Вставляет v в координатную прямую. Удаляет, если v есть в деке
    # True - added / False - deleted
    def insertV(self, v):
        i=0
        l = len(self)
        try:
            self.remove(v)
            return False
        except ValueError:
            pass
        for i in range(l):
            if self[i] > v:
                self.insert(i, v)
                # self.currI = i
                break 
        if l == len(self):
            self.append(v)
            # self.currI = i+1
        return True

    def printDeq(self):
        for i in self:
            print(i)

    def prev(self, i):
        print(i,self)
        if len(self) == 1:
            return self[0]
        return self[i-1]
    
    def next(self, i):
        i+=1
        if len(self) == i: i=0
        return self[i]
    
    # side - bool. True - right
    def pos(self, value, side):

        # бинарный поиск
        low = 0
        l = len(self)
        if l == 0:
            return False
        high = l - 1
        mid = l // 2
        while self[mid] != value and low <= high:
            if value > self[mid]:
                low = mid + 1
            else:
                high = mid - 1
            mid = (low + high) // 2
        
        print(value-self[high])
        if low > high:
            # элемент должен быть между high и low
            if side:
                return self.next(high)
            if value-self[high]<2000:
                return self.prev(high)
            return self[high]
        else:
            if side:
                return self.next(mid)
            return self.prev(mid)
    
    def pairs(self):
        l = len(self)
        if l%2 != 0:
            return False
        d_slice = [self[i]/1000 for i in range(l)]
        return [d_slice[i:i + 2] for i in range(0, len(d_slice), 2)]
    # def changePos(self) -> pos:
    #     return pos
        
# d = MarkDeq()
# d.insertV(10)
# d.insertV(200)
# d.insertV(400)
# d.insertV(23)
# # print(d.prev())
# d.printDeq()
# print("---")
# print(d.pos(9, False))
# print(d.currI)
