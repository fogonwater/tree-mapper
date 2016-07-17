import csv, json, time
import jinja2
from pprint import pprint as pp
import geocoder

SRC_ADDRESSES = 'data/addresses.csv'
DST_GEOCODED = 'data/geocode.csv'
COUNT_FIELDS = ["Plums ","Frank's Early ","Wilson's Early ","Black Doris "]


class Location:
    def __init__(self, loc_string, fields=[], row_dic={}, verbose=True):
        self.loc_string = contextualise(loc_string)
        self.properties = {'name':loc_string}
        self.read_properties(fields, row_dic)
        self.located = False
        self.verbose = verbose
        self.geocode()

    def read_properties(self, fields, row_dic):
        for field in fields:
            key = clean_key(field)
            if row_dic[field]:
                self.properties[key] = int(row_dic[field])
            else:
                self.properties[key] = 0

    def geocode(self):
        time.sleep(1)
        g = geocoder.google(self.loc_string)
        coors = g.latlng
        try:
            self.lat, self.lng = float(coors[0]), float(coors[1])
            self.located = True
        except IndexError:
            self.lat, self.lng = None, None
            self.located = False
        if self.verbose:
            print('{} -> {}, {}'.format(self.loc_string, self.lat, self.lng))

    def geojson(self):
        if not self.located:
            return None
        return {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [self.lng, self.lat],
            },
            'properties':self.properties
        }


### UTILITIES

def read_csv(f_path):
    with open(f_path) as f:
        reader = csv.DictReader(f)
        rows = [ row for row in reader]
    return rows

def write_json(data, f_path):
    with open(f_path, 'w') as outfile:
        json.dump(
            data,
            outfile,
            indent=2,
            sort_keys=True
        )
    print('{} written.'.format(f_path))

def clean_key(s):
    key = s.strip()
    key = key.replace(' ', '_')
    key = key.replace("'", '')
    return key.lower()

def contextualise(loc, context='Waiheke Island, NZ'):
    return '{}, {}'.format(loc, context.strip())




### CONTROL THING

def main():
    rows = read_csv(SRC_ADDRESSES)
    features = {'type': 'FeatureCollection', 'features':[]}
    for row in rows:
        raw_address = row['Address']
        if not raw_address:
            continue
        loc = Location(raw_address, fields=COUNT_FIELDS, row_dic=row)
        if loc.located:
            features['features'].append(loc.geojson())
        else:
            print('* UNABLE TO GEOCODE: {}'.format(raw_address))

    write_json(features, 'data/geocode.json')

    '''
    write_report(items, DST_GEOCODED)
    build_report(items, 'templates/index-template.html')
    print('')
    print('* Errors:')
    pp(errors)
    '''

if __name__ == '__main__':
    main()

'''

def safe_int(s):
    try:
        return int(s)
    except ValueError:
        return 0

def write_report(items, f_path):
    headers = items[0].keys()
    headers.sort()
    rows = [headers]
    for item in items:
        row = []
        for header in headers:
            row.append(item[header])
        rows.append(row)
    with open(f_path, 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print('Wrote {}.'.format(f_path))


### GENERATE REPORT

def get_jinja_template(template_file):
    # This loads a jinja template file. #
    loader = jinja2.FileSystemLoader(searchpath=".")
    env = jinja2.Environment(loader=loader)
    return env.get_template(template_file)

def build_report(items, index_template):
    # Takes a list of items & builds an HTML page from the template#
    template = get_jinja_template(index_template)
    doc = template.render({
        'items':items
    })
    with open('index.html', 'w') as f:
        f.write(doc)

def generate_map(coors, width=150, height=150, zoom=12):
    loc = "{},{}".format(coors[0], coors[1])
    return ''.join([
        "http://maps.googleapis.com/maps/api/staticmap?center=",
        loc,
        "&zoom=",
        str(zoom),
        "&scale=false&size=",
        str(width),
        "x",
        str(height),
        "&maptype=roadmap&format=png&visual_refresh=true"
        "&markers=size:mid%7Ccolor:0xff0000%7Clabel:%7C",
        loc,
    ])
'''
