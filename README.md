# community-garmin-route-planner
A simple, open-source desktop application that allows you to manually draw routes on an interactive map and send them directly to your Garmin sports watch. This project was built to provide Linux and Windows users with a fast, lightweight alternative to the official Garmin Express desktop software.

## ✨ Features

* **Interactive Map:** Easily click points on the map to design a route (track) live on your screen.
* **Direct via USB:** Saves the route directly into the correct watch folder (`Garmin/NewFiles`) when your device is connected via cable. Works universally on both Windows and Linux.
* **☁️ Wireless via Garmin Cloud:** Securely log in with your own Garmin Connect account and upload your route wirelessly to the cloud using a clever open-source workaround.
* **Privacy Friendly:** Your login credentials are not stored anywhere and are only used to communicate directly with the official Garmin servers.

---

## 🚀 How to Install and Run

To run this application locally, you need **Python** installed on your computer. Follow these simple steps:

### 1. Install Dependencies

Open your terminal (or Command Prompt/PowerShell on Windows) and run the following command to install the required building blocks:

```bash
pip install tkintermapview gpxpy garminconnect
2. Start the Application
Download the code (app.py), navigate to the folder where it is saved in your terminal, and launch the program:

Bash
python app.py
🗺️ How the Cloud Upload Works
Since Garmin has restricted their official Route API to enterprise partners, this app uses a smart open-source workaround. The app uploads your route as an "activity" with fake timestamps. Follow these simple steps to convert it into a route on your watch:

Plot your route on the map (use at least 4 to 5 points for the best results).

Log in on the right panel and click Verstuur draadloos (Cloud).

Open the Garmin Connect app on your phone (or log into the website).

Open the newly added activity, click the three dots in the top right corner, and select "Create Course".

Save the course and select "Send to Device" to sync it to your watch.

Optional: You can now safely delete the original fake activity from your logbook; the course will remain safely stored on your watch!

🛠️ Roadmap
[ ] Package the application as an official Flatpak for distribution on Flathub (Linux App Store).

[ ] Implement automatic activity-to-course conversion within the interface (if supported by the API).

[ ] Add the ability to import existing .gpx files and push them directly to the watch.

🤝 Contributing
This is a project built for and by the community! If you have ideas to improve the code, enhance the interface, or fix a bug, feel free to submit a Pull Request or open an Issue.

Built with love using the open-source libraries garminconnect, tkintermapview, and gpxpy.
