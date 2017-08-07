def getGlobe():
    globe = {"key1":"","key2":""}
    return globe

def func():
    loc = getGlobe()
    loc["key1"] = "change1"
    loc["key2"] = "change2"
    return loc

print(getGlobe())
print(func())
print(getGlobe())
