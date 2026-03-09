
#//maak een menu
#// request van api gebruik 2 endpoints 
# maak een switch statement om meerdere condities the controleren
# verwerk 3 functionaliteiten in het menu
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

    def add_crew(self, member):
        if any(cm.name == member.name for cm in self.crew):
            return
        self.crew.append(member)
        print(f"{member.name} added to the crew for {self.destination}.")

    def set_rocket(self, rocket):
        self.rocket = rocket
        print(f"{rocket.name} assigned to {self.destination}.")

    def reset_journey(self, new_destination):
        self.destination = new_destination
        self.rocket = None
        self.crew = []
        self.starlink = []
        self.launch_platform = None
        self.landing_platform = None
        self.launch_name = None
        print(f"Journey reset. New destination: {self.destination}")

    def fetch_starlink_for_launch(self, launch_id):
        try:
            launch_url = f"https://api.spacexdata.com/v4/launches/{launch_id}"
            response = requests.get(launch_url)
            if response.status_code != 200:
                print("Error fetching launch data")
                return
            launch_data = response.json()
            self.launch_name = launch_data.get("name", "Unknown Launch")
            self.launch_platform = launch_data.get("launchpad", "")
            cores = launch_data.get("cores", [])
            if cores:
                self.landing_platform = cores[0].get("landpad", "")
            starlink_url = "https://api.spacexdata.com/v4/starlink"
            starlink_resp = requests.get(starlink_url)
            if starlink_resp.status_code != 200:
                print("Error fetching Starlink data")
                return
            all_starlink = starlink_resp.json()
            self.starlink = []
            for sat in all_starlink:
                launch_ref = sat.get("spaceTrack", {}).get("LAUNCH", "")
                land_ref = sat.get("spaceTrack", {}).get("LAND", "")
                if self.launch_platform and self.launch_platform in launch_ref:
                    self.starlink.append(sat)
                elif self.landing_platform and self.landing_platform in land_ref:
                    self.starlink.append(sat)
            print(f"{len(self.starlink)} Starlink satellites linked to {self.launch_name}")
        except:
            print("Error fetching Starlink satellites for launch")

    def show_journey(self):
        print("\nYOUR SPACE JOURNEY")
        print("Destination:", self.destination)
        print("Rocket:", self.rocket if self.rocket else "None")
        print("Launch:", self.launch_name if self.launch_name else "None")
        print("Launch Platform:", self.launch_platform if self.launch_platform else "None")
        print("Landing Platform:", self.landing_platform if self.landing_platform else "None")
        if self.crew:
            print("Crew:")
            for member in self.crew:
                print("-", member.name)
        else:
            print("Crew: None")
        if self.starlink:
            print("\nStarlink satellites linked to this journey (first 10):")
            for sat in self.starlink[:10]:
                name = sat.get("spaceTrack", {}).get("OBJECT_NAME", "Unknown")
                version = sat.get("version", "Unknown")
                lat = sat.get("latitude", "N/A")
                lon = sat.get("longitude", "N/A")
                alt = sat.get("altitude_km", "N/A")
                print(f"{name} | Version: {version} | Lat: {lat} | Lon: {lon} | Alt: {alt} km")
        print()

class SpaceAPI:
    def get_crew(self):
        try:
            response = requests.get("https://api.spacexdata.com/v4/crew")
            return response.json() if response.status_code == 200 else []
        except:
            return []

    def get_rockets(self):
        try:
            response = requests.get("https://api.spacexdata.com/v4/rockets")
            return response.json() if response.status_code == 200 else []
        except:
            return []

    def get_launches(self):
        try:
            response = requests.get("https://api.spacexdata.com/v4/launches")
            return response.json() if response.status_code == 200 else []
        except:
            return []

    def get_landpads(self):
        try:
            response = requests.get("https://api.spacexdata.com/v4/landpads")
            return response.json() if response.status_code == 200 else []
        except:
            return []

api = SpaceAPI()
crew_data = api.get_crew()
rocket_data = api.get_rockets()
launch_data = api.get_launches()
landpad_data = api.get_landpads()
journey = Journey("Mars")

def show_menu():
    print("\n=== SPACE MISSION PLANNER ===")
    print("CREW:")
    print("1. List astronauts")
    print("2. Pick your crew (2 NoviNauts + YOU as Captain)")
    print("ROCKET:")
    print("3. Pick a rocket")
    print("JOURNEY:")
    print("4. Show your journey")
    print("5. Random journey")
    print("6. Reset journey")
    print("LAUNCH & LANDING:")
    print("7. Choose a launch and landing platform")
    print("MARS OPTIONS:")
    print("9. Mars options (Refuel / Return / Stay)")
    print("EXIT:")
    print("8. Exit")
    while True:
        choice = input("Choose an option: ")
        if choice.isdigit() and int(choice) in [1,2,3,4,5,6,7,8,9]:
            return int(choice)
        print("Please enter a valid option.")

def list_astronauts():
    if not crew_data:
        print("No crew data available.")
        return
    print("\nAstronauts:")
    for member in crew_data:
        print("-", member["name"])

def pick_crew_members_with_captain(captain_name="You"):
    if not crew_data:
        print("No crew data available.")
        return
    if journey.crew:
        print(f"Crew already assigned to {journey.destination}. Reset journey first to pick new crew.")
        return
    captain = CrewMember(captain_name, "Captain")
    journey.add_crew(captain)
    print(f"{captain_name} assigned as captain.")
    selected_count = 0
    max_members = 2
    while selected_count < max_members:
        print(f"\nPick crew member {selected_count + 1} of {max_members}:")
        for member in crew_data:
            print("-", member["name"])
        name_input = input("Enter astronaut name: ").strip().lower()
        found = False
        for member in crew_data:
            if "name" in member and member["name"].strip().lower() == name_input:
                if any(cm.name.lower() == member["name"].strip().lower() for cm in journey.crew):
                    print("Astronaut already selected, choose another.")
                    found = True
                    break
                crew_member = CrewMember(member["name"], member.get("agency", "Unknown"))
                journey.add_crew(crew_member)
                found = True
                selected_count += 1
                break
        if not found:
            print("Astronaut not found. Try again.")

def choose_rocket():
    if not rocket_data:
        print("No rocket data available.")
        return
    print("\nAvailable Rockets:")
    for rocket in rocket_data:
        print("-", rocket["name"])
    name_input = input("Enter rocket name to pick: ").strip().lower()
    found = False
    for rocket_info in rocket_data:
        if "name" in rocket_info and rocket_info["name"].strip().lower() == name_input:
            rocket = Rocket(rocket_info["id"], rocket_info["name"], rocket_info["type"])
            journey.set_rocket(rocket)
            found = True
            break
    if not found:
        print("Rocket not found. Please check the name or try again.")

def random_journey():
    if not crew_data or not rocket_data or not launch_data:
        print("Not enough data for a random journey.")
        return
    if journey.crew or journey.rocket:
        print(f"A crew and/or rocket is already assigned to {journey.destination}. Reset first.")
        return
    rocket_info = random.choice(rocket_data)
    crew_info = random.sample(crew_data, 2)
    rocket = Rocket(rocket_info["id"], rocket_info["name"], rocket_info["type"])
    journey.set_rocket(rocket)
    journey.add_crew(CrewMember("You", "Captain"))
    for c in crew_info:
        journey.add_crew(CrewMember(c["name"], c.get("agency","Unknown")))
    launch = random.choice(launch_data)
    journey.fetch_starlink_for_launch(launch["id"])
    journey.show_journey()

def choose_launch():
    if not launch_data:
        print("No launch data available.")
        return
    print("\nAvailable Launches:")
    for i, launch in enumerate(launch_data[:20]):
        print(f"{i + 1}: {launch.get('name')} | Date: {launch.get('date_utc')}")
    while True:
        choice = input("Pick a launch number: ")
        if choice.isdigit():
            choice = int(choice) - 1
            if 0 <= choice < len(launch_data[:20]):
                selected_launch = launch_data[choice]
                journey.launch_name = selected_launch.get("name")
                journey.launch_platform = selected_launch.get("launchpad", "")
                cores = selected_launch.get("cores", [])
                available_landpads = [core.get("landpad") for core in cores if core.get("landpad")]
                if not available_landpads:
                    available_landpads = [lp['id'] for lp in landpad_data]
                print("\nAvailable landing platforms:")
                for idx, pad in enumerate(available_landpads):
                    pad_name = pad
                    for lp in landpad_data:
                        if lp['id'] == pad:
                            pad_name = lp.get('name', pad)
                    print(f"{idx + 1}: {pad_name}")
                while True:
                    landing_choice = input("Pick a landing platform number: ")
                    if landing_choice.isdigit():
                        landing_choice = int(landing_choice) - 1
                        if 0 <= landing_choice < len(available_landpads):
                            journey.landing_platform = available_landpads[landing_choice]
                            break
                    print("Invalid choice, try again.")
                journey.fetch_starlink_for_launch(selected_launch["id"])
                journey.show_journey()
                return
        print("Invalid choice, try again.")

def mars_options():
    if journey.destination.lower() != "mars":
        print("Mars options are only available for a journey to Mars.")
        return
    print("\n--- MARS OPTIONS ---")
    print("1. Refuel on Mars")
    print("2. Return early to Novi Space Academy")
    print("3. Stay at Novi Hub")
    while True:
        choice = input("Make a choice: ")
        if choice == "1":
            print("Crew is refueling on Mars... resources replenished!")
            break
        elif choice == "2":
            journey.destination = "Novi Space Academy"
            print("Journey terminated early. Returning to Novi Space Academy with current rocket, crew, and landing platform.")
            journey.show_journey()
            break
        elif choice == "3":
            print("Staying at Novi Hub. Mission paused.")
            break
        else:
            print("Invalid choice, try again.")

while True:
    choice = show_menu()
    if choice == 1:
        list_astronauts()
    elif choice == 2:
        pick_crew_members_with_captain()
    elif choice == 3:
        choose_rocket()
    elif choice == 4:
        journey.show_journey()
    elif choice == 5:
        random_journey()
    elif choice == 6:
        new_dest = input("Enter new destination for the journey: ")
        journey.reset_journey(new_dest)
    elif choice == 7:
        choose_launch()
    elif choice == 8:
        print("Mission aborted")
        break
    elif choice == 9:
        mars_options()
