class Switcher(object):
    def numbers_to_methods_to_strings(self, argument):

        args = ['try']
        method_name = 'number_' + str(argument)
        method = getattr(self, method_name, lambda: "nothing")

        return method(*args)

    def number_0(self):
        return "zero"

    def number_1(self):
        return "one"

    def number_2(self, string):
        return string

switch = Switcher()

x = switch.numbers_to_methods_to_strings(2)

print(x)
