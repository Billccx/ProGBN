import sys
import getopt


def site():
    name = None
    url = None

    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, "n:u:")  # 短选项模式

    except:
        print("Error")

    for opt, arg in opts:
        if opt in ['-n']:
            name = arg
        elif opt in ['-u']:
            url = arg

    print(name + " " + url)


site()