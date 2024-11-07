import requests
import datetime
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Fetches the positions of the planets relative to the Sun for a given date.
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

    planet_positions = {}
    for planet, code in planets.items():
        params = {
            'format': 'json',
            'COMMAND': code,
            'OBJ_DATA': 'NO',
            'MAKE_EPHEM': 'YES',
            'EPHEM_TYPE': 'VECTORS',
            'CENTER': '500@10',  #  500@10 / 500@sun for sun as the center
            'OUT_UNITS': 'AU-D',
            'VEC_TABLE': '1',
            'CSV_FORMAT': 'YES',
            'START_TIME': f"'{start_date_time}'",
            'STOP_TIME': f"'{stop_date_time}'"}
        
        response = requests.get(url, params=params)

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
                    # Extract X, Y, Z values and convert to floats
                    x = float(vector_parts[2].strip())
                    y = float(vector_parts[3].strip())
                    z = float(vector_parts[4].strip())
                    planet_positions[planet] = {'X': x, 'Y': y, 'Z': z}
                    
                except (IndexError, ValueError) as e:
                    print(f"Error parsing position data for {planet}: {e}")
            else:
                print(f"Error: $$SOE or $$EOE markers not found in the response for {planet}.")
        else:
            print(f"Error retrieving data for {planet}: {response.status_code}")
            print(f"Details: {response.text}")

    # Manually construct the URL with the correct encoding
    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
    full_url = f"{url}?{query_string}"
    print(f"Requesting URL: {full_url}")

    return planet_positions

# Plots the positions of the planets in a 3D scatter plot.
def plot_positions(planet_positions):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot each planets position
    for planet, pos in planet_positions.items():

        # Calculate the log10-scaled X and Y coordinates
        log_x = np.sign(pos['X']) * np.log10(abs(pos['X']) + 1)  # Adding 1 to avoid log(0)
        log_y = np.sign(pos['Y']) * np.log10(abs(pos['Y']) + 1)
        log_z = np.sign(pos['Z']) * np.log10(abs(pos['Z']) + 1)

        ax.scatter(log_x, log_y, log_z, label=planet)
        ax.text(log_x, log_y, log_z, planet, fontsize=9)

        #ax.scatter(pos['X'], pos['Y'], pos['Z'], label=planet)
        #ax.text(pos['X'], pos['Y'], pos['Z'], planet, fontsize=9)

    # Plot the Sun at origo
    ax.scatter(0, 0, 0, color='yellow', label='Sun', s=100)

    # Set plot labels and title
    ax.set_xlabel("X (AU)")
    ax.set_ylabel("Y (AU)")
    ax.set_zlabel("Z (AU)")
    ax.set_title("Planetary Positions Relative to the Sun")
    ax.legend()

    # Save the plot to a file
    #plt.savefig(PlanetaryPositionsPlot.png)
    #print(f"Plot saved as {PlanetaryPositionsPlot.png}")
    plt.show()


def plot_solar_system_2d(planet_positions):
    figure_size_cm = 20  # Set the figure size in cm
    fig, ax = plt.subplots(figsize=(figure_size_cm/2.54, figure_size_cm/2.54))

    # Plot the Sun at the center
    ax.plot(0, 0, 'yo', markersize=12, label='Sun')

    # Plot each planet in the X-Y plane
    for planet, pos in planet_positions.items():

        # Calculate the log10-scaled X and Y coordinates
        log_x = np.sign(pos['X']) * np.log10(abs(pos['X']) + 1)  # Adding 1 to avoid log(0)
        log_y = np.sign(pos['Y']) * np.log10(abs(pos['Y']) + 1)
        log_z = np.sign(pos['Z']) * np.log10(abs(pos['Z']) + 1)

        # Plot the planet in the transformed log scale
        ax.plot(log_x, log_y, 'o', label=planet)
        ax.text(log_x * 1.05, log_y * 1.05, planet, fontsize=9)

        # Optional: Draw approximate orbit (circle in log scale)
        distance = np.sqrt(log_x**2 + log_y**2) # Radius of the orbit
        orbit = plt.Circle((0, 0), distance, color='gray', fill=False, linestyle='--', alpha=0.5)
        ax.add_patch(orbit)

        #ax.plot(pos['X'], pos['Y'], 'o', label=planet)
        #ax.text(pos['X'] * 1.05, pos['Y'] * 1.05, planet, fontsize=9)
        
        # Draw a circular representation of orbit path
        #distance = np.sqrt(pos['X']**2 + pos['Y']**2) # Radius of the orbit
        #orbit = plt.Circle((0, 0), distance, color='gray', fill=False, linestyle='--', alpha=0.5)
        #ax.add_patch(orbit)

    # Set labels and equal scaling
    ax.set_xlabel("X (scaled AU)")
    ax.set_ylabel("Y (scaled AU)")
    ax.set_aspect('equal', 'box')
    ax.set_title("Top-Down View of the Solar System (X-Y Plane)")
    ax.legend()
    plt.grid(True)
    plt.show()

    # Example data for demonstration
    # Replace these with actual X, Y values in Astronomical Units (AU) scaled for visualization.
    
# Main function to execute the planetary positioning project.
def main():
    print("Welcome to the Planetary Positioning Project!")
    date = '05.08.2023'
    planet_positions = get_planet_positions(date)
    # plot_positions(planet_positions)
    plot_solar_system_2d(planet_positions)

    ### Prints for debugging ###
    #print(start_date_time)
    #print(stop_date_time)
    #print(f"{planet} position: X = {x}, Y = {y}, Z = {z}")
    
    # Print the URL with parameters
    # print(f"Requesting URL: {response.url}")

if __name__ == "__main__":
    main()