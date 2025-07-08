from datetime import datetime

def time_since(timestamp):
    delta = datetime.now() - timestamp
    secs_per_hour = 3600
    secs_per_minute = 60
    if delta.days > 0:
        return "%dd" % (delta.days)
    elif delta.seconds // secs_per_hour > 0:
        return "%dh" % (delta.seconds // secs_per_hour)
    elif delta.seconds // secs_per_minute > 0:
        return "%dm" % (delta.seconds // secs_per_minute)
    else:
        return "just now"