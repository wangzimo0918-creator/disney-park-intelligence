import requests
import streamlit as st


st.set_page_config(
    page_title="Disney Wait-Time Dashboard",
    page_icon="🏰",
    layout="wide"
)

st.title("🏰 Disney World Park Intelligence")
st.subheader("Magic Kingdom Attraction Wait-Time Dashboard")

st.write(
    "Explore current attraction wait times at Magic Kingdom. "
    "Use the filters to find attractions that fit your plans."
)


API_URL = "https://queue-times.com/parks/6/queue_times.json"


@st.cache_data(ttl=60)
def get_ride_data():
    response = requests.get(API_URL, timeout=15)
    response.raise_for_status()

    data = response.json()

    rides = []

    for land in data["lands"]:
        land_name = land["name"]

        for ride in land["rides"]:
            rides.append({
                "Attraction": ride["name"],
                "Land": land_name,
                "Open": ride["is_open"],
                "Wait Time": ride["wait_time"],
                "Last Updated": ride["last_updated"]
            })

    for ride in data.get("rides", []):
        rides.append({
            "Attraction": ride["name"],
            "Land": "Other",
            "Open": ride["is_open"],
            "Wait Time": ride["wait_time"],
            "Last Updated": ride["last_updated"]
        })

    return rides


try:
    rides = get_ride_data()

except requests.exceptions.RequestException:
    st.error("Unable to connect to the Queue-Times API. Please try again later.")
    st.stop()

except (KeyError, ValueError, TypeError):
    st.error("The API returned data in an unexpected format.")
    st.stop()


if len(rides) == 0:
    st.warning("No attraction data is currently available.")
    st.stop()


st.header("Explore Attractions")

lands = ["All Lands"] + sorted(set(ride["Land"] for ride in rides))

selected_land = st.selectbox(
    "Choose a themed land:",
    lands
)

max_wait = st.slider(
    "Maximum acceptable wait time (minutes):",
    min_value=0,
    max_value=180,
    value=60,
    step=5
)



filtered_rides = []

for ride in rides:
    if selected_land == "All Lands" or ride["Land"] == selected_land:
        if ride["Open"] and ride["Wait Time"] <= max_wait:
            filtered_rides.append(ride)

# Sort attractions from shortest to longest wait
filtered_rides.sort(key=lambda ride: ride["Wait Time"])



st.header("Your Results")

col1, col2, col3 = st.columns(3)

col1.metric("Total Attractions", len(rides))

col2.metric(
    "Open Attractions",
    sum(1 for ride in rides if ride["Open"])
)

col3.metric("Matching Attractions", len(filtered_rides))

st.divider()


st.subheader("📊 Attraction Wait-Time Comparison")

if filtered_rides:
    wait_chart = {
        ride["Attraction"]: ride["Wait Time"]
        for ride in filtered_rides
    }

    st.bar_chart(wait_chart)

else:
    st.info("No open attractions match your selected filters.")


st.subheader("⏱️ Wait-Time Distribution")

wait_categories = {
    "0–15 min": 0,
    "16–30 min": 0,
    "31–60 min": 0,
    "61+ min": 0
}

for ride in filtered_rides:
    wait = ride["Wait Time"]

    if wait <= 15:
        wait_categories["0–15 min"] += 1
    elif wait <= 30:
        wait_categories["16–30 min"] += 1
    elif wait <= 60:
        wait_categories["31–60 min"] += 1
    else:
        wait_categories["61+ min"] += 1

st.bar_chart(wait_categories)


st.subheader("🎢 Matching Attractions")

if filtered_rides:
    st.dataframe(
        filtered_rides,
        use_container_width=True,
        hide_index=True
    )

else:
    st.write("Try selecting another land or increasing your maximum wait time.")



st.divider()

st.markdown(
    "Data provided by [Queue-Times.com](https://queue-times.com/)."
)

st.caption(
    "Wait times are live estimates and may change. "
    "Queue-Times updates its real-time API approximately every five minutes."
)

