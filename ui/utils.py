
def milliseconds_to_time_string(milliseconds):
    minutes = (milliseconds // 1000) // 60
    seconds = (milliseconds // 1000) % 60
    decimal_point = milliseconds % 1000

    return "{:0=2}\'{:0=2}\"{:0=3}".format(minutes, seconds, decimal_point)
