import requests
import datetime
import numpy as np
import matplotlib.pyplot as plt

# Class to represent the configuration parameters.
class ConfigParameters:
    def __init__(self, date=None, text=None):
        self.date = date
        self.text = text

    def load_from_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    line = line.strip()  # Remove extra whitespace
                    if line and not line.startswith('#') and ':' in line:  # Skip comments and empty lines
                        key, value = line.split(':', 1)  # Split at the first ':'
                        key = key.strip()
                        value = value.strip().strip("'")  # Remove surrounding quotes
                        if key == "Date":
                            self.date = value
                        elif key == "Text":
                            self.text = value
        except FileNotFoundError:
            print(f"Error: Config file '{file_path}' not found.")
        except Exception as e:
            print(f"Error reading config file: {e}")

# Class to represent a celestial body.
class Body:
    def __init__(self, name, code, diameter, color):
        self.name = name
        self.code = code
        self.diameter = diameter
        self.color = color
        self.position = {'X': None, 'Y': None, 'Z': None}
    
    def set_position(self, x, y, z):
        self.position['X'] = x
        self.position['Y'] = y
        self.position['Z'] = z

# Class to represent the Solar System and its bodies.
class SolarSystem:
    def __init__(self):
        self.body = {
            'Sun':      Body('Sun',      None, 1392684, 'yellow'),
            'Mercury':  Body('Mercury', '199', 4880,    'gray'),
            'Venus':    Body('Venus',   '299', 12104,   'palegoldenrod'),
            'Earth':    Body('Earth',   '399', 12756,   'blue'),
            'Mars':     Body('Mars',    '499', 6792,    'orangered'),
            'Jupiter':  Body('Jupiter', '599', 142984,  'sandybrown'),
            'Saturn':   Body('Saturn',  '699', 120536,  'goldenrod'),
            'Uranus':   Body('Uranus',  '799', 51118,   'lightblue'),
            'Neptune':  Body('Neptune', '899', 49528,   'mediumblue')
        }
    
    # Fetches the positions of the planets relative to the Sun for a given date.
    def get_body_positions(self, date):
        url = "https://ssd.jpl.nasa.gov/api/horizons.api"

        # Define start and stop time for single instance output & convert from "dd.mm.yyyy" to "YYYY-MMM-DD HH:MN"
        start_date_time = datetime.datetime.strptime(date + ' 00:00:00', "%d.%m.%Y %H:%M:%S").strftime("%Y-%b-%d %H:%M:%S")
        stop_date_time = datetime.datetime.strptime(date + ' 00:00:01', "%d.%m.%Y %H:%M:%S").strftime("%Y-%b-%d %H:%M:%S")
        
        # Set the Sun's position to origo
        self.body['Sun'].set_position(0, 0, 0)

        for body in self.body.values():
            if body.code:  # Skip the Sun
                params = {
                    'format': 'json',
                    'COMMAND': body.code,
                    'OBJ_DATA': 'NO',
                    'MAKE_EPHEM': 'YES',
                    'EPHEM_TYPE': 'VECTORS',
                    'CENTER': '500@10',  #  500@10 / 500@sun for sun as the center
                    'OUT_UNITS': 'AU-D',
                    'VEC_TABLE': '1',
                    'CSV_FORMAT': 'YES',
                    'START_TIME': f"'{start_date_time}'",
                    'STOP_TIME': f"'{stop_date_time}'"
                }
                
                response = requests.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.text

                    # Locate the section with $$SOE and $$EOE
                    soe_index = data.find("$$SOE")
                    eoe_index = data.find("$$EOE")
                    
                    # Extract the data within $$SOE and $$EOE
                    if soe_index != -1 and eoe_index != -1:
                        vector_data = data[soe_index + 5:eoe_index].strip()

                        # Split the line by commas to extract X, Y, Z
                        vector_parts = vector_data.split(',')
                        try:
                            x = float(vector_parts[2].strip())
                            y = float(vector_parts[3].strip())
                            z = float(vector_parts[4].strip())
                            body.set_position(x, y, z)
                        except (IndexError, ValueError) as e:
                            print(f"Error parsing position data for {body.name}: {e}")
                    else:
                        print(f"Error: $$SOE or $$EOE markers not found in the response for {body.name}.")
                else:
                    print(f"Error retrieving data for {body.name}: {response.status_code}")
                    print(f"Details: {response.text}")

                    ### Uncomment for debugging (Manually construct the URL with the correct encoding and prit it) ###
                    #query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
                    #full_url = f"{url}?{query_string}"
                    #print(f"Requesting URL: {full_url}")

    # Scale the data of the bodies for visualization
    def log10_scale_data(self):
        for body in self.body.values():

            # Scale the position
            pos = body.position
            body.position['X'] = np.sign(pos['X']) * np.log10(abs(pos['X']) + 1)  # Adding 1 to avoid log(0)
            body.position['Y'] = np.sign(pos['Y']) * np.log10(abs(pos['Y']) + 1)
            body.position['Z'] = np.sign(pos['Z']) * np.log10(abs(pos['Z']) + 1)

            # Scale the diameter
            body.diameter = np.log10(body.diameter)

            # Uncomment for debugging
            # print(f"{planet.name}: X = {planet.position['X']}, Y = {planet.position['Y']}, Z = {planet.position['Z']}")

    # Retrieves the positions of the bodies
    def get_positions(self):
        return {body.name: body.position for body in self.body.values()}
    
    # Retrieves positions, colors and diameters
    def get_data(self):
        return {
            body.name: {
                'position': body.position,
                'color': body.color,
                'diameter': body.diameter
            }
            for body in self.body.values()
        }

# Plots the positions, size and color of the body in a 3D scatter plot.
def plot_solar_system_3D(solar_system_data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for body, data in solar_system_data.items():
        pos = data['position']
        color = data['color']
        diameter = data['diameter']

        ax.scatter(pos['X'], pos['Y'], pos['Z'], s=diameter, color=color, label=body)
        ax.text(pos['X'] * 1.05, pos['Y'] * 1.05, pos['Z'] * 1.05, body, fontsize=9)

    # Set plot labels and title
    ax.set_xlabel("X [log10(AU)]")
    ax.set_ylabel("Y [log10(AU)]")
    ax.set_zlabel("Z [log10(AU)]")
    ax.set_title("Planetary Positions Relative to the Sun")
    ax.legend()

    # Set equal aspect ratio for all axes
    #max_range = max([np.max(np.abs([pos['X'], pos['Y'], pos['Z']])) for pos in [data['position'] for data in solar_system_data.values()]])
    #ax.set_xlim([-max_range, max_range])
    #ax.set_ylim([-max_range, max_range])
    #ax.set_zlim([-max_range, max_range])

    # Save the plot to a file
    #plt.savefig(PlanetaryPositionsPlot.png)
    #print(f"Plot saved as {PlanetaryPositionsPlot.png}")
    plt.show()

# Plots the positions, size and color of the body in a 2D plot.
def plot_solar_system_2D(solar_system_data):
    figure_size_cm = 20  # Set the figure size in cm
    fig, ax = plt.subplots(figsize=(figure_size_cm/2.54, figure_size_cm/2.54))
    
    # Plot each body in the X-Y plane
    for body, data in solar_system_data.items():
        pos = data['position']
        color = data['color']
        diameter = data['diameter']

        ax.scatter(pos['X'], pos['Y'], s=diameter, color=color, label=body)
        ax.text(pos['X'] * 1.05, pos['Y'] * 1.05, body, fontsize=9)

        # Optional: Draw approximate orbit (circle in log scale)
        orbit = np.sqrt(pos['X']**2 + pos['Y']**2) # Radius of the orbit
        orbit = plt.Circle((0, 0), orbit, color='gray', fill=False, linestyle='--', alpha=0.5)
        ax.add_patch(orbit)

    # Set labels and equal scaling
    ax.set_xlabel("X (log10 scaled AU)")
    ax.set_ylabel("Y (log10 scaled AU)")
    ax.set_aspect('equal', 'box')
    ax.set_title("Top-Down View of the Solar System (X-Y Plane)")
    ax.legend()
    plt.grid(True)
    plt.show()

# Main function to execute the planetary positioning project.
def main():
    print("Welcome to the Planetary Positioning Project!")
    
    # Read parameters from the config file
    print("Reading configuration...")
    config_parameters = ConfigParameters()
    config_parameters.load_from_file("config.txt")
    print(f"Using date: {config_parameters.date}")
    print(f"Using text: {config_parameters.text}")

    # Create the Solar System and fetch the body positions
    solar_system = SolarSystem()
    solar_system.get_body_positions(config_parameters.date)
    solar_system.log10_scale_data()
    plot_data = solar_system.get_data()
    plot_solar_system_3D(plot_data)
    plot_solar_system_2D(plot_data)

if __name__ == "__main__":
    main()