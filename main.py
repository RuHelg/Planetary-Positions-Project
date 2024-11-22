import requests
import datetime
import numpy as np
import matplotlib.pyplot as plt
from stl import mesh

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
    def scale_data(self):

        position_scale_factor = 40  # Adjusted for appropriate visualization
        diameter_scale_factor = 1 # Adjusted for appropriate visualization

        for body in self.body.values():

            # Scale the position
            pos = body.position
            body.position['X'] = (np.sign(pos['X']) * np.log10(abs(pos['X']) + 1) * position_scale_factor)  # Adding 1 to avoid log(0)
            body.position['Y'] = (np.sign(pos['Y']) * np.log10(abs(pos['Y']) + 1) * position_scale_factor)
            body.position['Z'] = (np.sign(pos['Z']) * np.log10(abs(pos['Z']) + 1) * position_scale_factor)

            # Scale the diameter
            body.diameter = np.log10(body.diameter) * diameter_scale_factor

            # Uncomment for debugging
            # print(f"{planet.name}: X = {planet.position['X']}, Y = {planet.position['Y']}, Z = {planet.position['Z']}")
  
    # Retrieves positions, colors and diameters
    def get_plot_data(self):
        return {
            body.name: {
                'position': body.position,
                'color': body.color,
                'diameter': body.diameter
            }
            for body in self.body.values()
        }

# Plots the positions, size and color of the body in a 3D scatter plot.
def plot_solar_system_3D(solar_system_data, config_parameters):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for body, data in solar_system_data.items():
        pos = data['position']
        color = data['color']
        diameter = data['diameter']

        ax.scatter(pos['X'], pos['Y'], pos['Z'], s=diameter, color=color, edgecolors='black', label=body)
        
        # Uncomment to add text labels for the bodies
        #ax.text(pos['X'] * 1.2, pos['Y'] * 1.2, pos['Z'] * 1.2, body, fontsize=9)

    # Set plot labels and title
    ax.set_xlabel("X [log10(AU)]")
    ax.set_ylabel("Y [log10(AU)]")
    ax.set_zlabel("Z [log10(AU)]")
    ax.set_title(f"Planetary Positions {config_parameters.date}")
    ax.legend()

    # Set equal aspect ratio for all axes
    max_range = max([np.max(np.abs([pos['X'], pos['Y'], pos['Z']])) for pos in [data['position'] for data in solar_system_data.values()]])
    ax.set_xlim([-max_range, max_range])
    ax.set_ylim([-max_range, max_range])
    ax.set_zlim([-max_range, max_range])

    # Save the plot as an EPS file
    plt.savefig("plot_3D.eps", format="eps")
    plt.show()

# Plots the positions, size and color of the body in a 2D plot.
def plot_solar_system_2D(solar_system_data, config_parameters):
    #figure_size_cm = 20  # Set the figure size in cm
    #fig, ax = plt.subplots(figsize=(figure_size_cm/2.54, figure_size_cm/2.54))
    
    fig, ax = plt.subplots()
    
    # Plot each body in the X-Y plane
    for body, data in solar_system_data.items():
        pos = data['position']
        color = data['color']
        diameter = data['diameter']

        # Draw approximate orbit (circle in log scale)
        orbit = np.sqrt(pos['X']**2 + pos['Y']**2) # Radius of the orbit
        orbit = plt.Circle((0, 0), orbit, color='gray', fill=False, linestyle='--', alpha=0.5)
        ax.add_patch(orbit)

        ax.scatter(pos['X'], pos['Y'], s=diameter, color=color, edgecolors='black', label=body)
        
        # Uncomment to add text labels for the bodies
        #ax.text(pos['X'] * 1.2, pos['Y'] * 1.2, body, fontsize=9)

    # Set labels and equal scaling
    ax.set_xlabel("X [log10(AU)]")
    ax.set_ylabel("Y [log10(AU)]")
    ax.set_aspect('equal', 'box')
    ax.set_title(f"XY-plane Planetary Positions {config_parameters.date}")
    ax.legend()

    # Save the plot as an EPS file
    plt.grid(True)
    plt.savefig("plot_2D.eps", format="eps")
    plt.show()


# Create a disc mesh with the specified radius and thickness.
def create_disc(disc_radius, disc_height, disc_resolution):

    #z_top = disc_height / 2
    #z_bottom = -disc_height / 2

    z_top = disc_height
    z_bottom = 0

    # Generate circular points
    angles = np.linspace(0, 2 * np.pi, disc_resolution, endpoint=False)
    circle_top = [(disc_radius * np.cos(a), disc_radius * np.sin(a), z_top) for a in angles]
    circle_bottom = [(disc_radius * np.cos(a), disc_radius * np.sin(a), z_bottom) for a in angles]

    # Central points for top and bottom
    center_top = (0, 0, z_top)
    center_bottom = (0, 0, z_bottom)

    vertices = []
    faces = []

    # Add top surface triangles
    for i in range(disc_resolution):
        next_i = (i + 1) % disc_resolution
        vertices.extend([circle_top[i], circle_top[next_i], center_top])
        faces.append([len(vertices) - 3, len(vertices) - 2, len(vertices) - 1])

    # Add bottom surface triangles
    for i in range(disc_resolution):
        next_i = (i + 1) % disc_resolution
        vertices.extend([circle_bottom[next_i], circle_bottom[i], center_bottom])
        faces.append([len(vertices) - 3, len(vertices) - 2, len(vertices) - 1])

    # Add sidewall triangles
    for i in range(disc_resolution):
        next_i = (i + 1) % disc_resolution
        vertices.extend([
            circle_top[i], circle_bottom[i], circle_top[next_i],  # Triangle 1
            circle_top[next_i], circle_bottom[i], circle_bottom[next_i]  # Triangle 2
        ])
        faces.append([len(vertices) - 6, len(vertices) - 5, len(vertices) - 4])
        faces.append([len(vertices) - 3, len(vertices) - 2, len(vertices) - 1])

    # Convert to numpy arrays
    vertices = np.array(vertices)
    faces = np.array(faces)

    return vertices, faces

# Create a 3D mesh of the orbits with the given radius, width, height and resolution.
def create_orbit(orbit_radius, orbit_width, orbit_height, orbit_resolution):
    
    inner_radius = orbit_radius - orbit_width/2
    outer_radius = orbit_radius + orbit_width/2
    
    # Initialize empty lists to store vertices and faces
    vertices = []
    faces = []

    # Generate vertices for the inner and outer edges of the top and bottom surfaces
    for i in range(orbit_resolution):
        angle = 2 * np.pi * i / orbit_resolution
        # Outer circle vertices
        outer_x = outer_radius * np.cos(angle)
        outer_y = outer_radius * np.sin(angle)
        # Inner circle vertices
        inner_x = inner_radius * np.cos(angle)
        inner_y = inner_radius * np.sin(angle)
        # Top surface
        #vertices.append([outer_x, outer_y, orbit_height / 2])  # Outer top
        #vertices.append([inner_x, inner_y, orbit_height / 2])  # Inner top
        # Bottom surface
        #vertices.append([outer_x, outer_y, -orbit_height / 2])  # Outer bottom
        #vertices.append([inner_x, inner_y, -orbit_height / 2])  # Inner bottom
        # Top surface
        vertices.append([outer_x, outer_y, orbit_height])  # Outer top
        vertices.append([inner_x, inner_y, orbit_height])  # Inner top
        # Bottom surface
        vertices.append([outer_x, outer_y, 0])  # Outer bottom
        vertices.append([inner_x, inner_y, 0])  # Inner bottom

    # Convert vertices to numpy array
    vertices = np.array(vertices)

    # Generate faces for the top surface
    for i in range(orbit_resolution):
        next_i = (i + 1) % orbit_resolution
        faces.append([i * 4, next_i * 4, i * 4 + 1])  # Outer to inner (top surface)
        faces.append([i * 4 + 1, next_i * 4, next_i * 4 + 1])  # Inner to inner (top surface)

    # Generate faces for the bottom surface
    for i in range(orbit_resolution):
        next_i = (i + 1) % orbit_resolution
        faces.append([i * 4 + 2, i * 4 + 3, next_i * 4 + 2])  # Outer to inner (bottom surface)
        faces.append([i * 4 + 3, next_i * 4 + 3, next_i * 4 + 2])  # Inner to inner (bottom surface)

    # Generate faces for the outer wall
    for i in range(orbit_resolution):
        next_i = (i + 1) % orbit_resolution
        faces.append([i * 4, i * 4 + 2, next_i * 4])  # Top to bottom (outer)
        faces.append([i * 4 + 2, next_i * 4 + 2, next_i * 4])  # Bottom to bottom (outer)

    # Generate faces for the inner wall
    for i in range(orbit_resolution):
        next_i = (i + 1) % orbit_resolution
        faces.append([i * 4 + 1, next_i * 4 + 1, i * 4 + 3])  # Top to bottom (inner)
        faces.append([i * 4 + 3, next_i * 4 + 1, next_i * 4 + 3])  # Bottom to bottom (inner)

    # Convert faces to numpy array
    faces = np.array(faces)

    return vertices, faces

# Create a 3D mesh of bodies with the given center and radius.
def create_body(center, radius, body_resolution):

    u = np.linspace(0, np.pi, body_resolution)  # Latitude
    v = np.linspace(0, 2 * np.pi, body_resolution)  # Longitude
    x = center[0] + radius * np.outer(np.sin(u), np.cos(v))
    y = center[1] + radius * np.outer(np.sin(u), np.sin(v))
    z = center[2] + radius * np.outer(np.cos(u), np.ones_like(v))

    vertices = np.array([x.ravel(), y.ravel(), z.ravel()]).T
    faces = []

    # Generate triangular faces for the sphere
    for i in range(body_resolution - 1):
        for j in range(body_resolution - 1):
            p1 = i * body_resolution + j
            p2 = p1 + body_resolution
            p3 = p1 + 1
            p4 = p2 + 1

            faces.append([p1, p2, p3])  # Triangle 1
            faces.append([p3, p2, p4])  # Triangle 2

    return vertices, np.array(faces)

# Add orbits to the disc mesh and return the combined vertices and faces.
def add_orbits_to_disc(disc_vertices, disc_faces, solar_system_data, orbit_width, orbit_height, orbit_resolution):
    
    vertices = disc_vertices.tolist()
    faces = disc_faces.tolist()

    for body, data in solar_system_data.items():
        pos = data['position']
        orbit_radius = np.sqrt(pos['X']**2 + pos['Y']**2)

        orbit_vertices, orbit_faces = create_orbit(orbit_radius, orbit_width=orbit_width, orbit_height=orbit_height, orbit_resolution=orbit_resolution)

        # Offset faces for the new orbit vertices
        offset = len(vertices)
        for face in orbit_faces:
            faces.append([offset + idx for idx in face])

        vertices.extend(orbit_vertices.tolist())

    return np.array(vertices), np.array(faces)

# Add planets to the disc mesh and return the combined vertices and faces.
def add_body_to_disc(orbit_vertices, orbit_faces, solar_system_data, disc_height, body_resolution):

    vertices = orbit_vertices.tolist()
    faces = orbit_faces.tolist()

    for body, data in solar_system_data.items():
        pos = data['position']
        radius = data['diameter'] / 2

        # Position the sphere on top of the disc
        body_center = (pos['X'], pos['Y'], disc_height)  # 3 mm disc thickness
        sphere_vertices, sphere_faces = create_body(body_center, radius, body_resolution=body_resolution)

        # Offset faces for the new sphere vertices
        offset = len(vertices)
        for face in sphere_faces:
            faces.append([offset + idx for idx in face])

        vertices.extend(sphere_vertices.tolist())

    return np.array(vertices), np.array(faces)

# Save the vertices and faces as an STL file.
def save_to_stl(vertices, faces, filename):

    disc_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            disc_mesh.vectors[i][j] = vertices[face[j]]
    disc_mesh.save(filename)
    print(f"STL file saved as {filename}")

# Generate the 3D model of the solar system and save it as an STL file.
def generate_solar_system_stl(solar_system_data):

    # Retrieve the position of Neptune from solar_system_data
    neptune_position = solar_system_data['Neptune']['position']
    
    # Set the disc radius, height and resolution
    disc_radius = np.sqrt(neptune_position['X']**2 + neptune_position['Y']**2) + 20
    disc_height = 4
    disc_resolution = 150

    # Set the orbit width and height
    orbit_width = 1
    orbit_height = 5
    orbit_resolution = 100

    # Set the body resolution
    body_resolution = 40

    # Create the disc
    disc_vertices, disc_faces = create_disc(disc_radius, disc_height, disc_resolution)

    # Add orbits as thin 3D lines with thickness and height
    orbit_vertices, orbit_faces = add_orbits_to_disc(disc_vertices, disc_faces, solar_system_data, orbit_width, orbit_height, orbit_resolution)

    # Add planets as spheres
    vertices, faces = add_body_to_disc(orbit_vertices, orbit_faces, solar_system_data, disc_height, body_resolution)

    # Save the combined mesh to an STL file
    save_to_stl(vertices, faces, filename="solar_system.stl")

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

    # Scale the data for better representation
    solar_system.scale_data()
    
    # Get the relevant data for plotting and 3D model generation
    solar_system_data = solar_system.get_plot_data()

    #Plot the solar system
    #plot_solar_system_3D(solar_system_data, config_parameters)
    #plot_solar_system_2D(solar_system_data, config_parameters)

    # Generate the 3D model of the solar system
    generate_solar_system_stl(solar_system_data)

if __name__ == "__main__":
    main()
