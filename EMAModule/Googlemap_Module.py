import googlemaps


gmaps = googlemaps.Client(key='')

self_location = (33.6466024, -117.8331387)

# reverse_geocode_result = gmaps.reverse_geocode()

places_nearby = gmaps.places_nearby(location=(33.65504549018609, -117.84176834066939), radius=10)

type_count = {}
for place in places_nearby['results']:
    for typ in place['types']:
        if typ in type_count:
            type_count[typ] += 1
        else:
            type_count[typ] = 1

print(type_count)