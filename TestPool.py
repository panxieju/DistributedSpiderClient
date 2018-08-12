import random
import time

import multiprocessing


def wait():
    time.sleep(4)
    return True

if __name__ == '__main__':
    pool = multiprocessing.Pool(10)
    result = pool.map(wait)
    print(result)
