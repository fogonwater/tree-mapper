import csv, json, time
import jinja2
from pprint import pprint as pp
import geocoder

SRC_ADDRESSES = 'data/addresses.csv'
DST_GEOCODED = 'data/geocode.csv'

### UTILITIES

def read_csv(f_path):
    with open(f_path) as f:
        reader = csv.DictReader(f)
        rows = [ row for row in reader]
    return rows

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

### GEOCODING AND DATA CLEANING

def geocode(location):
    g = geocoder.google(location)
    return g.latlng

def contextualise(loc, context='Waiheke Island, NZ'):
    return '{},{}'.format(loc, context)

def clean_lat_lng(coors):
    try:
        return [float(coors[0]), float(coors[1])]
    except IndexError:
        return [None, None]

### GENERATE REPORT

def get_jinja_template(template_file):
    ''' This loads a jinja template file. '''
    loader = jinja2.FileSystemLoader(searchpath=".")
    env = jinja2.Environment(loader=loader)
    return env.get_template(template_file)

def build_report(items, index_template):
    ''' Takes a list of items & builds an HTML page from the template'''
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

### CONTROL THING

def main():
    rows = read_csv(SRC_ADDRESSES)
    items = []
    errors = []
    for i, row in enumerate(rows):
        raw_address = row['Address']
        if not raw_address:
            continue
        #if i >= 3: break
        address = contextualise(raw_address)
        coors = clean_lat_lng( geocode(address) )
        print('{} : {}'.format(address, coors))
        time.sleep(1)
        items.append({
            'address':address,
            'lat':coors[0],
            'lng':coors[1],
            'map':generate_map(coors),
        })

    write_report(items, DST_GEOCODED)
    build_report(items, 'templates/index-template.html')
    print('')
    print('* Errors:')
    pp(errors)

if __name__ == '__main__':
    main()
