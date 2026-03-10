import requests
import random

class Rocket:
    def __init__(self, id, name, type):
        self.id = id
        self.name = name
        self.type = type
    def __str__(self):
        return f"{self.name} ({self.type})"

class CrewMember:
    def __init__(self, name, role):
        self.name = name
        self.role = role

class Journey:
    def __init__(self, destination):
        self.destination = destination
        self.rocket = None
        self.crew = []
        self.starlink = []
        self.launch_platform = None
        self.landing_platform = None
        self.launch_name = None
        self.landing_info = None
        self.status = "planning"

    def add_crew(self, member):
        if any(cm.name == member.name for cm in self.crew):
            return
        self.crew.append(member)
        print(f"{member.name} added to crew.")

    def set_rocket(self, rocket):
        self.rocket = rocket
        print(f"{rocket.name} assigned.")

    def fetch_landing_info(self, landpad_id):
        global landpad_data
        for pad in landpad_data:
            if pad["id"] == landpad_id:
                self.landing_info = pad
                return

    def fetch_starlink_for_launch(self, launch_id):
        try:
            launch_url = f"https://api.spacexdata.com/v4/launches/{launch_id}"
            response = requests.get(launch_url)
            if response.status_code != 200:
                print("Error fetching launch data")
                return
            launch_data = response.json()
            self.launch_name = launch_data.get("name")
            self.launch_platform = launch_data.get("launchpad")
            starlink_resp = requests.get("https://api.spacexdata.com/v4/starlink")
            if starlink_resp.status_code != 200:
                print("Error fetching Starlink data")
                return
            all_starlink = starlink_resp.json()[:200]
            self.starlink = []
            for sat in all_starlink:
                launch_ref = sat.get("spaceTrack", {}).get("LAUNCH", "")
                if self.launch_platform and self.launch_platform in launch_ref:
                    self.starlink.append(sat)
        except:
            print("Error fetching Starlink satellites for launch")

    def show_journey(self):
        print("\n=== SPACE JOURNEY ===")
        print("Status:", self.status)
        print("Destination:", self.destination)
        print("Rocket:", self.rocket if self.rocket else "None")
        print("Launch:", self.launch_name if self.launch_name else "None")
        print("Launch Platform:", self.launch_platform)
        print("Landing Platform:", self.landing_platform)
        if self.crew:
            print("\nCrew:")
            for member in self.crew:
                print("-", member.name)
        else:
            print("Crew: None")
        if self.landing_info:
            print("\nLanding Platform Info")
            print("Name:", self.landing_info.get("name"))
            print("Full Name:", self.landing_info.get("full_name"))
            print("Type:", self.landing_info.get("type"))
            print("Status:", self.landing_info.get("status"))
            print("Location:", self.landing_info.get("locality"), "-", self.landing_info.get("region"))
            print("Latitude:", self.landing_info.get("latitude"))
            print("Longitude:", self.landing_info.get("longitude"))
            attempts = self.landing_info.get("landing_attempts", 0)
            success = self.landing_info.get("landing_successes", 0)
            print("Landing Attempts:", attempts)
            print("Landing Successes:", success)
            if attempts > 0:
                rate = round((success / attempts) * 100, 2)
                print("Success Rate:", rate, "%")
            print("Details:", self.landing_info.get("details"))
        if self.starlink:
            print("\nStarlink Satellites (first 5):")
            for sat in self.starlink[:5]:
                name = sat.get("spaceTrack", {}).get("OBJECT_NAME", "Unknown")
                lat = sat.get("latitude", "N/A")
                lon = sat.get("longitude", "N/A")
                print(f"{name} | Lat: {lat} | Lon: {lon}")
        print()

class SpaceAPI:
    def get_crew(self):
        try:
            return requests.get("https://api.spacexdata.com/v4/crew").json()
        except:
            return []
    def get_rockets(self):
        try:
            return requests.get("https://api.spacexdata.com/v4/rockets").json()
        except:
            return []
    def get_launches(self):
        try:
            return requests.get("https://api.spacexdata.com/v4/launches").json()
        except:
            return []
    def get_landpads(self):
        try:
            return requests.get("https://api.spacexdata.com/v4/landpads").json()
        except:
            return []
    def get_launchpads(self):
        try:
            return requests.get("https://api.spacexdata.com/v4/launchpads").json()
        except:
            return []

api = SpaceAPI()
crew_data = api.get_crew()
rocket_data = api.get_rockets()
launch_data = api.get_launches()
landpad_data = api.get_landpads()
launchpad_data = api.get_launchpads()
journey = Journey("Mars")

def show_menu():
    if journey.status in ["in-flight", "completed"]:
        print("\n=== SPACE MISSION PLANNER ===")
        print(f"Current mission status: {journey.status.upper()}")
        print("To start a new mission (crew, rocket, launch), you must reset first.")
    
    print("\nMISSION PLANNING")
    print("1 List astronauts")
    print("2 Pick crew")
    print("3 Pick rocket")
    print("4 Random journey")
    print("\nLAUNCH")
    print("5 Choose launch and landing pad")
    print("\nMISSION STATUS")
    print("6 Show journey")
    print("\nIN FLIGHT")
    print("7 Mars options")
    print("\nMISSION CONTROL")
    print("8 Reset journey")
    print("\nSYSTEM")
    print("9 Exit")
    
    while True:
        choice = input("Choose option: ")
        if choice.isdigit() and int(choice) in range(1, 10):
            choice = int(choice)
            if journey.status in ["in-flight", "completed"] and choice in [2, 3, 4, 5]:
                print("Cannot choose this option during an active or completed mission. Reset first.")
                continue
            return choice
        print("Invalid option")

def list_astronauts():
    print("\nAstronauts:")
    for member in crew_data:
        print("-", member["name"])

def pick_crew():
    if journey.status in ["in-flight", "completed"]:
        print("Cannot change crew during an active or completed mission. Reset first.")
        return
    if journey.crew:
        print("Crew already selected")
        return
    journey.add_crew(CrewMember("You", "Captain"))
    for i in range(2):
        print("\nPick crew member")
        for member in crew_data:
            print("-", member["name"])
        name = input("Enter astronaut name: ").lower()
        for member in crew_data:
            if member["name"].lower() == name:
                journey.add_crew(CrewMember(member["name"], "Astronaut"))
                break

def choose_rocket():
    if journey.status in ["in-flight", "completed"]:
        print("Cannot change rocket during an active or completed mission. Reset first.")
        return
    print("\nAvailable rockets")
    for rocket in rocket_data:
        print("-", rocket["name"])
    name = input("Enter rocket name: ").lower()
    for rocket in rocket_data:
        if rocket["name"].lower() == name:
            journey.set_rocket(Rocket(rocket["id"], rocket["name"], rocket["type"]))
            return
    print("Rocket not found")

def choose_launch():
    if journey.status in ["in-flight", "completed"]:
        print("Cannot choose launch during an active or completed mission. Reset first.")
        return
    print("\nAvailable launches:")
    for i, launch in enumerate(launch_data[:20]):
        lp_id = launch.get("launchpad")
        lp_name = "Unknown"
        for lp in launchpad_data:
            if lp["id"] == lp_id:
                lp_name = lp.get("full_name","Unknown")
        print(f"{i + 1}: {launch['name']} | Launchpad: {lp_name}")
    
    choice = int(input("Choose launch number: ")) - 1
    selected_launch = launch_data[choice]
    journey.launch_name = selected_launch.get("name")
    journey.launch_platform = selected_launch.get("launchpad")

    print("\nAvailable landing pads:")
    for i, pad in enumerate(landpad_data):
        print(f"{i + 1}: {pad.get('full_name')} | Location: {pad.get('locality')} - {pad.get('region')}")
    
    while True:
        land_choice = input("Choose landing pad number: ")
        if land_choice.isdigit() and 1 <= int(land_choice) <= len(landpad_data):
            selected_pad = landpad_data[int(land_choice)-1]
            journey.landing_platform = selected_pad["id"]
            journey.fetch_landing_info(journey.landing_platform)
            break
        print("Invalid choice, try again.")

    journey.fetch_starlink_for_launch(selected_launch["id"])
    journey.status = "in-flight"
    journey.show_journey()

def random_journey():
    if journey.status in ["in-flight", "completed"]:
        print("Cannot start a random journey during an active or completed mission. Reset first.")
        return
    rocket = random.choice(rocket_data)
    journey.set_rocket(Rocket(rocket["id"], rocket["name"], rocket["type"]))
    journey.add_crew(CrewMember("You", "Captain"))
    crew = random.sample(crew_data, 2)
    for c in crew:
        journey.add_crew(CrewMember(c["name"], "Astronaut"))
    launch = random.choice(launch_data)
    journey.launch_name = launch.get("name")
    journey.launch_platform = launch.get("launchpad")
    landpad = random.choice(landpad_data)
    journey.landing_platform = landpad["id"]
    journey.fetch_landing_info(journey.landing_platform)
    journey.fetch_starlink_for_launch(launch["id"])
    journey.status = "in-flight"
    journey.show_journey()

def mars_options():
    if journey.status != "in-flight":
        print("Mars options are only available during flight.")
        return
    print("\n--- MARS OPTIONS ---")
    print("1 Refuel on Mars")
    print("2 Return to Earth")
    print("3 Stay on Mars")
    choice = input("Choose option: ")
    if choice == "1":
        print("Refueling complete")
        journey.status = "completed"
    elif choice == "2":
        journey.destination = "Earth"
        print("Returning home")
        journey.status = "completed"
    elif choice == "3":
        print("Mission paused at Mars base")
        journey.status = "completed"

def reset_journey():
    if journey.status != "completed":
        print("Mission must be completed before reset.")
        return
    new_dest = input("Enter new destination: ")
    print("Do you want to start a completely new journey or stay at home base?")
    print("1 New journey (reset crew and rocket)")
    print("2 Stay at Novi Space Academy (keep crew and rocket)")
    while True:
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            journey.destination = new_dest
            journey.rocket = None
            journey.crew = []
            journey.starlink = []
            journey.launch_platform = None
            journey.landing_platform = None
            journey.launch_name = None
            journey.landing_info = None
            journey.status = "planning"
            print(f"New journey started to {journey.destination}.")
            return
        elif choice == "2":
            journey.destination = "Novi Space Academy"
            journey.launch_platform = None
            journey.landing_platform = None
            journey.launch_name = None
            journey.landing_info = None
            journey.status = "planning"
            print("Journey destination set to Novi Space Academy. Crew and rocket retained.")
            return
        print("Invalid choice, enter 1 or 2.")

while True:
    choice = show_menu()
    if choice == 1:
        list_astronauts()
    elif choice == 2:
        pick_crew()
    elif choice == 3:
        choose_rocket()
    elif choice == 4:
        random_journey()
    elif choice == 5:
        choose_launch()
    elif choice == 6:
        journey.show_journey()
    elif choice == 7:
        mars_options()
    elif choice == 8:
        reset_journey()
    elif choice == 9:
        print("Mission aborted")
        break
