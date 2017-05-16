import os.path
import time

from iterfzf import iterfzf


def iter_pokemon(sleep=0.01):
    filename = os.path.join(os.path.dirname(__file__), 'pokemon.txt')
    with open(filename) as f:
        for l in f:
            yield l.strip()
            time.sleep(sleep)


def main():
    result = iterfzf(iter_pokemon(), multi=True)
    for item in result:
        print(repr(item))


if __name__ == '__main__':
    main()
