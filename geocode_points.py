import csv, time
from pprint import pprint as pp
import geocoder

SRC_ADDRESSES = 'data/addresses.csv'

def read_csv(f_path):
    with open(f_path) as f:
        reader = csv.DictReader(f)
        rows = [ row for row in reader]
    return rows

def geocode(location):
    g = geocoder.google(location)
    return g.latlng


def main():
    rows = read_csv(SRC_ADDRESSES)
    for row in rows:
        loc = row['Address']
        coors = geocode(loc)
        print('{} : {}'.format(loc, coors))
        time.sleep(1)



if __name__ == '__main__':
    main()
