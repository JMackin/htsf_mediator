import os
from dir_nav import dirs


class Navver:

    # rorl == 1: remote, rorl == 0: local
    def __init__(self, rorl: int = 0):
        self.rorl = rorl if (rorl == 1) or (rorl == 0) else 0
        self.base = [os.getcwd(), '']
        self.cwd = [os.getcwd(), '']
        self.prev = ['', '']
        self.saved = [{"base": os.fspath(os.getcwd())}, {"base": ''}]
        self.use_rorl = lambda rl: self.rorl if rl is None else rl
        self.verify = lambda path: os.path.exists(os.fspath(path))
        self.resolve = lambda sym: ('',
                                    lambda: self.getbase(),
                                    lambda: self.getcwd(),
                                    lambda: os.fspath('/'.join(self.getcwd().split('/')[:-1]))
                                    if len(self.getcwd().split('/')) > 2 else os.fspath('/')
                                    )[len(sym.split('.'))]() \
            if (sym == '.' or sym == '..' or sym == '~') \
            else os.fspath(sym)

    # dir_tup = (base, cwd, prev, (*optional_adds.))

    def est_dirs(self, dir_tup: tuple, rorl: int = None):
        rorl = self.use_rorl(rorl)

        self.base[rorl] = dir_tup[0]
        self.cwd[rorl] = dir_tup[1]
        self.prev[rorl] = dir_tup[2]

        if len(dir_tup) > 3:
            for i in dir_tup[3]:
                # (key, path, rorl) || (key, path) || path
                self.savepath(i[0], i[1], (rorl if len(i) < 3 else i[2])) \
                    if type(i) == tuple \
                    else self.savepath(key=None, path=i, rorl=rorl)
        self.export()

    def getcwd(self, rorl: int = None):

        rorl = self.use_rorl(rorl)
        return self.cwd[rorl]

    def getdirname(self, rorl: int = None):
        rorl = self.use_rorl(rorl)
        return self.cwd[rorl].split('/')[-1]

    def getprev(self, rorl: int = None):
        rorl = self.use_rorl(rorl)
        return self.prev[rorl]

    def getbase(self, rorl: int = None):
        rorl = self.use_rorl(rorl)
        return self.base[rorl]

    def move(self, path: str = None, rorl: int = None):
        rorl = self.use_rorl(rorl)

        if path is not None:
            path = os.path.join(self.getcwd(), path) if path[0] != '/' else path

            if rorl == 0 and not self.verify(path):
                print(f"\nInvalid path: {path}\n CWD: {self.getcwd(rorl)}")
                return None

            else:
                self.prev[rorl] = self.cwd[rorl]
                self.cwd[rorl] = self.resolve(path)

        else:
            self.prev[rorl] = self.cwd[rorl]
            self.cwd[rorl] = self.resolve('..') if self.cwd[rorl] != os.fspath('/') else os.fspath('/')

        return self.cwd[rorl]

    def savepath(self, key: str = None, path: str = None, rorl: int = None):
        rorl = self.use_rorl(rorl)
        key = os.getcwd().split('/')[-1] if key is None else key
        path = os.fspath(path) if path is not None else os.getcwd()
        self.saved[rorl][key] = path
        return path

    def recall(self, key, rorl: int = None):
        try:
            rorl = self.use_rorl(rorl)
            recalled = os.fspath(self.saved[rorl][key])

        except KeyError as k:
            print(f"\nNothing saved under key: {key}\n")
            return None

        return recalled

    def goback(self, rorl: int = None):
        rorl = self.use_rorl(rorl)

        tmp = self.getcwd(rorl)
        self.cwd[rorl] = self.getprev(rorl)
        self.prev[rorl] = tmp

    def flip_rorl(self):
        self.rorl = not self.rorl
        rorl_dict = {0: 'local', 1: 'remote'}
        print(f"\n{rorl_dict[(not self.rorl)]} -> {rorl_dict[self.rorl]}\n")
        return self.rorl

    def am_rorl(self):
        print("local" if self.rorl == 0 else "remote\n")
        return self.rorl

    def export(self):
        l_dir_vals = (self.base[0], self.cwd[0], self.prev[0])
        r_dir_vals = (self.base[1], self.cwd[1], self.prev[1])
        x = 0

        for i in dirs.local.keys():
            dirs.local[i] = l_dir_vals[x]
            dirs.remote[i] = r_dir_vals[x]
            x += 1

        for k, v in self.saved[0].items():
            dirs.local[k] = v
        for k, v in self.saved[1].items():
            dirs.remote[k] = v
