from io import TextIOWrapper

d = 'inizio'

logfile = TextIOWrapper

print(type(logfile))

print(d)

def func_inizio():
    print('func inizio: ' + d)

def func():
    global d
    d = 'dentro'
    func_inizio()
    print('inside func: ' + d)

if __name__ == '__main__':
    func()

logfile.close()
