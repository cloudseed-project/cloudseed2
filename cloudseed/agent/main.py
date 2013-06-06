from multiprocessing import Process
from .utils import daemonize
from .agent import worker
from .agent import agent


def main():
    daemonize()
    Process(name='cloudseed worker', target=worker).start()
    Process(name='cloudseed agent', target=agent).start()

if __name__ == '__main__':
    main()
