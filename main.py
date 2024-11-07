import requests
import datetime

def get_planet_positions(date):
    url = "https://ssd.jpl.nasa.gov/api/horizons.api"
    planets = {
        'Mercury': '199',
        'Venus': '299',
        'Earth': '399',
        'Mars': '499',
        'Jupiter': '599',
        'Saturn': '699',
        'Uranus': '799',
        'Neptune': '899'
    }

    # Define start and stop time for single instance output
    start_date_time = date + ' 00:00:00'
    stop_date_time = date + ' 00:00:01'

    # Convert input date from dd.mm.yyyy to "YYYY-MMM-DD HH:MN"
    start_date_time = datetime.datetime.strptime(start_date_time, "%d.%m.%Y %H:%M:%S").strftime("%Y-%b-%d %H:%M:%S")
    stop_date_time = datetime.datetime.strptime(stop_date_time, "%d.%m.%Y %H:%M:%S").strftime("%Y-%b-%d %H:%M:%S")
    # print(start_date_time)
    # print(stop_date_time)

    planet_positions = {}
    for planet, code in planets.items():
        params = {
            'format': 'json',
            'COMMAND': code,
            'OBJ_DATA': 'NO',
            'MAKE_EPHEM': 'YES',
            'EPHEM_TYPE': 'VECTORS',
            'CENTER': '500@10',  #  500@10 / 500@sun for sun as the center
            'VEC_TABLE': '1',
            'CSV_FORMAT': 'YES',
            'START_TIME': f"'{start_date_time}'",
            'STOP_TIME': f"'{stop_date_time}'"}
        
        response = requests.get(url, params=params)
        # Print the URL with parameters
        # print(f"Requesting URL: {response.url}")
        
        # Manually construct the URL with the correct encoding
        #query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
        #full_url = f"{url}?{query_string}"
        #print(f"Requesting URL: {full_url}")
        #response = requests.get(full_url)


        if response.status_code == 200:
            data = response.text
            # Locate the section with $$SOE and $$EOE
            soe_index = data.find("$$SOE")
            eoe_index = data.find("$$EOE")
            
            if soe_index != -1 and eoe_index != -1:
                # Extract the data within $$SOE and $$EOE
                vector_data = data[soe_index + 5:eoe_index].strip()
                
                # Split the line by commas to extract X, Y, Z
                vector_parts = vector_data.split(',')
                
                try:
                    # Extract X, Y, Z values and convert them to floats
                    x = float(vector_parts[2].strip())
                    y = float(vector_parts[3].strip())
                    z = float(vector_parts[4].strip())
                    planet_positions[planet] = {'X': x, 'Y': y, 'Z': z}
                    #print(f"{planet} position: X = {x}, Y = {y}, Z = {z}")
                except (IndexError, ValueError) as e:
                    print(f"Error parsing position data for {planet}: {e}")
            else:
                print(f"Error: $$SOE or $$EOE markers not found in the response for {planet}.")
        else:
            print(f"Error retrieving data for {planet}: {response.status_code}")
            print(f"Details: {response.text}")

    return planet_positions

def main():
    print("Welcome to the Planetary Positioning Project!")
    date = '19.08.2000'
    planet_positions = get_planet_positions(date)

if __name__ == "__main__":
    main()