import uos


def info(msg):
    file_path = 'log.txt'
    try:
        file_size = uos.stat(file_path)[6]
        if file_size > 1024:
            uos.remove(file_path)
    except OSError:
        pass

    with open(file_path, 'a') as f:
        print(msg)
        print(msg, file=f)
