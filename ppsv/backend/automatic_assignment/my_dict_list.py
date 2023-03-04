import copy


class MyDictList:
    def __init__(self):
        self.dict = {}

    def __setitem__(self, key, value):
        if key not in self.dict:
            self.dict[key] = value
        else:
            self.dict[key] = value

    def __getitem__(self, key):
        try:
            return self.dict[key]
        except KeyError as e:
            print(e)

    def __len__(self):
        return len(self.dict)

    def __contains__(self, key):
        return key in self.dict

    def __deepcopy__(self, memodict={}):
        new_dict = MyDictList()
        for key, value in self.dict.items():
            new_dict[key] = copy.copy(value)
        return new_dict

    def __str__(self):
        s = ""
        for key, value in self.dict.items():
            s += (str(key) + ": " + str(value)) + "\n"
        return s

    def remove(self, key):
        self.dict.pop(key)

    def keys(self):
        return self.dict.keys()

    def values(self):
        return self.dict.values()

    def items(self):
        return self.dict.items()
