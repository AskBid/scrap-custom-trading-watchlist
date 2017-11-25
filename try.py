def timeFW():
    string ='''
    09:00-09:40
    10:00-10:10
    11:00-11:10
    12:00-12:10
    13:00-13:50
    14:00-14:10
    15:00-15:10
    16:00-20:00
    '''

    string = string.replace(' ','').split('\n')
    string.pop(0)
    string.pop(-1)
    print(string)

timeFW()
