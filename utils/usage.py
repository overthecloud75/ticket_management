import psutil

def get_usage():

    mem_per=psutil.virtual_memory().percent
    cpu_per=psutil.cpu_percent()

    return {'mem': mem_per, 'cpu': cpu_per}