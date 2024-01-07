def anonymous_filter1(ff: str) -> bool:
    ff = ff.lower()
    if ff.count('я')>=23: return True
    else: return False


anonymous_filter = lambda ff: ff.lower().count('я') >= 23


print(anonymous_filter('яяяяяяяяяяяяяяяяяяяяяяяя, яяяяяяяяяяяяяяяя и яяяяяяяя тоже!'))