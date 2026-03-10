
import requests
import random

class Rocket:
    def __init__(self, rocket_id, rocket_name, rocket_type):
        self.id = rocket_id
        self.name = rocket_name
        self.type = rocket_type
    def __str__(self):
        return f"{self.name} ({self.type})"

class Astronaut:
    def __init__(self, name, role):
        self.name = name
        self.role = role

class Mission:
    def __init__(self, destination):
        self.destination = destination
        self.rocket = None
        self.crew = []
        self.starlink = []
        self.launch_pad = None
        self.landing_pad = None
        self.launch_name = None
        self.landing_info = None
        self.status = "planning"

    def add_crew_member(self, member):
        if any(a.name == member.name for a in self.crew):
            return
        self.crew.append(member)
        print(f"{member.name} added to the crew.")

    def assign_rocket(self, rocket):
        self.rocket = rocket
        print(f"{rocket.name} assigned to mission.")

    def fetch_landing_info(self, pad_id):
        for pad in landing_pads:
            if pad["id"] == pad_id:
                self.landing_info = pad
                return

    def fetch_starlink(self, launch_id):
        try:
            launch_resp = requests.get(f"https://api.spacexdata.com/v4/launches/{launch_id}")
            if launch_resp.status_code != 200:
                print("Error fetching launch data")
                return
            launch_data = launch_resp.json()
            self.launch_name = launch_data.get("name")
            self.launch_pad = launch_data.get("launchpad")

            starlink_resp = requests.get("https://api.spacexdata.com/v4/starlink")
            if starlink_resp.status_code != 200:
                print("Error fetching Starlink data")
                return

            all_starlink = starlink_resp.json()[:200]
            self.starlink = []
            for sat in all_starlink:
                launch_ref = sat.get("spaceTrack", {}).get("LAUNCH", "")
                if self.launch_pad and self.launch_pad in launch_ref:
                    self.starlink.append(sat)
        except:
            print("Error fetching Starlink satellites")

    def show_mission(self):
        print("\n=== CURRENT MISSION ===")
        print("Status:", self.status)
        print("Destination:", self.destination)
        print("Rocket:", self.rocket if self.rocket else "None")
        print("Launch:", self.launch_name if self.launch_name else "None")
        print("Launch Pad:", self.launch_pad)
        print("Landing Pad:", self.landing_pad)
        if self.crew:
            print("\nCrew:")
            for a in self.crew:
                print("-", a.name)
        else:
            print("Crew: None")

        if self.landing_info:
            print("\nLanding Pad Info")
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
                print("Success Rate:", round((success/attempts)*100, 2), "%")
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
        try: return requests.get("https://api.spacexdata.com/v4/crew").json()
        except: return []
    def get_rockets(self):
        try: return requests.get("https://api.spacexdata.com/v4/rockets").json()
        except: return []
    def get_launches(self):
        try: return requests.get("https://api.spacexdata.com/v4/launches").json()
        except: return []
    def get_landing_pads(self):
        try: return requests.get("https://api.spacexdata.com/v4/landpads").json()
        except: return []
    def get_launch_pads(self):
        try: return requests.get("https://api.spacexdata.com/v4/launchpads").json()
        except: return []

api = SpaceAPI()
astronauts = api.get_crew()
rockets = api.get_rockets()
launches = api.get_launches()
landing_pads = api.get_landing_pads()
launch_pads = api.get_launch_pads()
mission = Mission("Mars")

def show_menu():
    if mission.status in ["in-flight", "completed"]:
        print("\nCurrent mission active. Reset before starting new mission.")
    
    print("\nMISSION MENU")
    print("1 List astronauts")
    print("2 Pick crew")
    print("3 Pick rocket")
    print("4 Random mission")
    print("5 Choose launch and landing pad")
    print("6 Show mission")
    print("7 Mars options")
    print("8 Reset mission")
    print("9 Exit")
    
    while True:
        choice = input("Choose option: ")
        if choice.isdigit() and int(choice) in range(1,10):
            choice = int(choice)
            if mission.status in ["in-flight","completed"] and choice in [2,3,4,5]:
                print("Cannot choose this option during active mission. Reset first.")
                continue
            return choice
        print("Invalid choice")

def list_astronauts():
    print("\nAstronauts:")
    for a in astronauts:
        print("-", a["name"])

def pick_crew():
    if mission.status in ["in-flight","completed"]:
        print("Cannot change crew during active mission.")
        return
    if mission.crew:
        print("Crew already selected")
        return
    mission.add_crew_member(Astronaut("You","Captain"))
    for i in range(2):
        print("\nPick crew member")
        for a in astronauts:
            print("-", a["name"])
        name = input("Enter astronaut name: ").lower()
        for a in astronauts:
            if a["name"].lower() == name:
                mission.add_crew_member(Astronaut(a["name"],"Astronaut"))
                break

def pick_rocket():
    if mission.status in ["in-flight","completed"]:
        print("Cannot change rocket during active mission.")
        return
    print("\nAvailable rockets:")
    for r in rockets:
        print("-", r["name"])
    name = input("Enter rocket name: ").lower()
    for r in rockets:
        if r["name"].lower() == name:
            mission.assign_rocket(Rocket(r["id"], r["name"], r["type"]))
            return
    print("Rocket not found")

def choose_launch():
    if mission.status in ["in-flight","completed"]:
        print("Cannot choose launch during active mission.")
        return
    print("\nLaunch options:")
    for i,l in enumerate(launches[:20]):
        lp_id = l.get("launchpad")
        lp_name = "Unknown"
        for lp in launch_pads:
            if lp["id"] == lp_id: lp_name = lp.get("full_name","Unknown")
        print(f"{i+1}: {l['name']} | Launchpad: {lp_name}")
    choice = int(input("Choose launch number: "))-1
    selected = launches[choice]
    mission.launch_name = selected.get("name")
    mission.launch_pad = selected.get("launchpad")
    
    print("\nLanding pads:")
    for i,pad in enumerate(landing_pads):
        print(f"{i+1}: {pad.get('full_name')} | {pad.get('locality')} - {pad.get('region')}")
    while True:
        land_choice = input("Choose landing pad number: ")
        if land_choice.isdigit() and 1<=int(land_choice)<=len(landing_pads):
            pad = landing_pads[int(land_choice)-1]
            mission.landing_pad = pad["id"]
            mission.fetch_landing_info(pad["id"])
            break
        print("Invalid choice")
    
    mission.fetch_starlink(selected["id"])
    mission.status = "in-flight"
    mission.show_mission()

def random_mission():
    if mission.status in ["in-flight","completed"]:
        print("Cannot start random mission during active mission. Reset first.")
        return
    r = random.choice(rockets)
    mission.assign_rocket(Rocket(r["id"],r["name"],r["type"]))
    mission.add_crew_member(Astronaut("You","Captain"))
    crew = random.sample(astronauts,2)
    for c in crew:
        mission.add_crew_member(Astronaut(c["name"],"Astronaut"))
    l = random.choice(launches)
    mission.launch_name = l.get("name")
    mission.launch_pad = l.get("launchpad")
    pad = random.choice(landing_pads)
    mission.landing_pad = pad["id"]
    mission.fetch_landing_info(pad["id"])
    mission.fetch_starlink(l["id"])
    mission.status = "in-flight"
    mission.show_mission()

def mars_options():
    if mission.status != "in-flight":
        print("Mars options only available during flight.")
        return
    print("\nMars options")
    print("1 Refuel")
    print("2 Return to Earth")
    print("3 Stay on Mars")
    choice = input("Choose: ")
    if choice=="1":
        print("Refueling complete")
        mission.status="completed"
    elif choice=="2":
        mission.destination="Earth"
        print("Returning home")
        mission.status="completed"
    elif choice=="3":
        print("Paused at Mars base")
        mission.status="completed"

def reset_mission():
    if mission.status != "completed":
        print("Mission must be completed before reset.")
        return
    new_dest = input("Enter new destination: ")
    print("1 New mission (reset crew and rocket)")
    print("2 Stay at Novi Space Academy (keep crew and rocket)")
    while True:
        choice = input("Choose 1 or 2: ")
        if choice=="1":
            mission.destination = new_dest
            mission.rocket=None
            mission.crew=[]
            mission.starlink=[]
            mission.launch_pad=None
            mission.landing_pad=None
            mission.launch_name=None
            mission.landing_info=None
            mission.status="planning"
            print(f"New mission started to {mission.destination}")
            return
        elif choice=="2":
            mission.destination="Novi Space Academy"
            mission.launch_pad=None
            mission.landing_pad=None
            mission.launch_name=None
            mission.landing_info=None
            mission.status="planning"
            print("Mission destination set to home base. Crew and rocket retained.")
            return
        print("Invalid choice")

while True:
    choice = show_menu()
    if choice==1: list_astronauts()
    elif choice==2: pick_crew()
    elif choice==3: pick_rocket()
    elif choice==4: random_mission()
    elif choice==5: choose_launch()
    elif choice==6: mission.show_mission()
    elif choice==7: mars_options()
    elif choice==8: reset_mission()
    elif choice==9: break
