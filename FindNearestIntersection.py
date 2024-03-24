from bs4 import BeautifulSoup
import requests


def findDist(c1, c2):
    return ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2) ** 0.5


def giveNearestAddress(lat, lng, lat2, lng2, maxRows, radius):
    usr = "marc"
    url = f"http://api.geonames.org/findNearestIntersectionJSON?lat={lat}&lng={lng}&maxRows={maxRows}&radius={radius}&username={usr}"
    print(url)

    res = requests.get(url)
    soup = BeautifulSoup(res.content, "lxml")

    raw_data = soup.find("p").contents[0].split("{")

    finalAddress = ""
    coord = [0, 0]
    dist = 0
    res = [lat, lng]

    for intersections in raw_data:
        address = ""
        for ele in intersections.split(","):
            if "\"street1\"" in ele:
                address += ele[11:-1] + " & "
            if "\"street2\"" in ele:
                address += ele[11:-1]
            if "lng" in ele:
                coord[1] = float(ele[7:-1])
            if "lat" in ele:
                coord[0] = float(ele[7:-4])
            if "distance" in ele:
                dist = float(ele[12:-1])

        if findDist(coord, (lat2, lng2)) < findDist(res, (lat2, lng2)):
            res = [] + coord
            finalAddress = address
            print(coord, findDist(coord, (lat2, lng2)))
            print("HERE:" + str(res))

    print("|||" + str(res))
    return res, finalAddress

# giveNearestAddress(41.792279, -87.599954, 41.7845895, -87.6003179, 1000, 0.9052359626420613)
