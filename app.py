
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Smart Weather & Disaster Alert System",
    page_icon="🌦️",
    layout="wide"
)

# ==========================================
# WEATHER DESCRIPTION
# ==========================================

def weather_description(code):

    weather_codes = {
        0: "Clear Sky ☀️",
        1: "Mainly Clear 🌤️",
        2: "Partly Cloudy ⛅",
        3: "Overcast ☁️",
        45: "Fog 🌫️",
        48: "Fog 🌫️",
        51: "Light Drizzle 🌦️",
        53: "Moderate Drizzle 🌦️",
        55: "Heavy Drizzle 🌧️",
        61: "Light Rain 🌧️",
        63: "Moderate Rain 🌧️",
        65: "Heavy Rain 🌧️",
        71: "Light Snow ❄️",
        73: "Moderate Snow ❄️",
        75: "Heavy Snow ❄️",
        80: "Rain Showers 🌦️",
        81: "Moderate Rain Showers 🌧️",
        82: "Heavy Rain Showers ⛈️",
        95: "Thunderstorm ⛈️",
        96: "Thunderstorm with Hail ⛈️",
        99: "Heavy Thunderstorm ⛈️"
    }

    return weather_codes.get(code, "Unknown Weather")


# ==========================================
# GET WEATHER DATA
# ==========================================

def get_weather(city):

    geo_url = "https://geocoding-api.open-meteo.com/v1/search"

    geo_params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    geo_response = requests.get(
        geo_url,
        params=geo_params,
        timeout=20
    )

    geo_response.raise_for_status()

    geo_data = geo_response.json()

    if not geo_data.get("results"):
        return None, "City not found. Please enter a valid city."

    location = geo_data["results"][0]

    latitude = location["latitude"]
    longitude = location["longitude"]

    # Weather API

    weather_url = "https://api.open-meteo.com/v1/forecast"

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,

        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "precipitation,"
            "rain,"
            "wind_speed_10m,"
            "weather_code"
        ),

        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max"
        ),

        "forecast_days": 7,
        "timezone": "auto"
    }

    weather_response = requests.get(
        weather_url,
        params=weather_params,
        timeout=20
    )

    weather_response.raise_for_status()

    weather_data = weather_response.json()

    return {
        "location": location,
        "current": weather_data["current"],
        "daily": weather_data["daily"],
        "units": weather_data["current_units"]
    }, None


# ==========================================
# MAIN WEBSITE DESIGN
# ==========================================

st.title("🌦️ Smart Weather & Disaster Alert System")

st.write(
    "Live Weather Monitoring and Disaster Risk Information"
)

st.divider()

# ==========================================
# CITY SEARCH
# ==========================================

st.subheader("📍 Search Weather by City")

city = st.text_input(
    "Enter City Name",
    placeholder="Example: Ahmedabad"
)

if st.button("🌤️ Check Weather", type="primary"):

    if not city.strip():

        st.warning("Please enter a city name.")

    else:

        try:

            with st.spinner("Fetching Live Weather Data..."):

                data, error = get_weather(city.strip())

            if error:

                st.error(error)

            else:

                location = data["location"]
                current = data["current"]
                daily = data["daily"]
                units = data["units"]

                # ==================================
                # LOCATION
                # ==================================

                st.success(
                    f"Weather found for "
                    f"{location['name']}, "
                    f"{location.get('country', '')}"
                )

                st.divider()

                # ==================================
                # CURRENT WEATHER
                # ==================================

                st.subheader("🌤️ Current Weather")

                st.markdown(
                    f"### {weather_description(current['weather_code'])}"
                )

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "🌡️ Temperature",
                    f"{current['temperature_2m']} "
                    f"{units['temperature_2m']}"
                )

                col2.metric(
                    "💧 Humidity",
                    f"{current['relative_humidity_2m']}%"
                )

                col3.metric(
                    "🌬️ Wind Speed",
                    f"{current['wind_speed_10m']} "
                    f"{units['wind_speed_10m']}"
                )

                col4, col5, col6 = st.columns(3)

                col4.metric(
                    "🌡️ Feels Like",
                    f"{current['apparent_temperature']} "
                    f"{units['apparent_temperature']}"
                )

                col5.metric(
                    "🌧️ Rain",
                    f"{current['rain']} {units['rain']}"
                )

                col6.metric(
                    "☔ Precipitation",
                    f"{current['precipitation']} "
                    f"{units['precipitation']}"
                )

                # ==================================
                # 7 DAYS WEATHER FORECAST
                # ==================================

                st.divider()

                st.subheader("📅 7 Days Weather Forecast")

                forecast_df = pd.DataFrame({

                    "Date": daily["time"],

                    "Weather": [
                        weather_description(code)
                        for code in daily["weather_code"]
                    ],

                    "Maximum Temperature (°C)":
                        daily["temperature_2m_max"],

                    "Minimum Temperature (°C)":
                        daily["temperature_2m_min"],

                    "Rain Probability (%)":
                        daily["precipitation_probability_max"]
                })

                st.dataframe(
                    forecast_df,
                    use_container_width=True,
                    hide_index=True
                )

                # ==================================
                # TEMPERATURE GRAPH
                # ==================================

                st.subheader("📊 Weekly Temperature Graph")

                graph_df = pd.DataFrame({

                    "Date": daily["time"],

                    "Maximum Temperature":
                        daily["temperature_2m_max"],

                    "Minimum Temperature":
                        daily["temperature_2m_min"]
                })

                fig = px.line(
                    graph_df,
                    x="Date",
                    y=[
                        "Maximum Temperature",
                        "Minimum Temperature"
                    ],
                    markers=True,
                    title="7 Days Temperature Forecast"
                )

                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Temperature (°C)",
                    template="plotly_dark"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                # ==================================
                # WEATHER RISK ANALYSIS
                # ==================================

                st.divider()

                st.subheader("⚠️ Weather Risk Analysis")

                temperature = current["temperature_2m"]
                wind = current["wind_speed_10m"]
                rain = current["rain"]

                alerts = []

                if temperature >= 40:

                    alerts.append(
                        "High Temperature: Stay hydrated "
                        "and avoid prolonged outdoor exposure."
                    )

                if wind >= 50:

                    alerts.append(
                        "High Wind Speed: Be careful in "
                        "exposed areas."
                    )

                if rain >= 7.5:

                    alerts.append(
                        "Heavy Rain Indicator: Avoid "
                        "waterlogged areas."
                    )

                if alerts:

                    for alert in alerts:

                        st.warning("⚠️ " + alert)

                else:

                    st.success(
                        "No high-risk indicator detected "
                        "by the basic project rules."
                    )

                # ==================================
                # SAFETY INFORMATION
                # ==================================

                st.info(
                    "This project provides educational "
                    "weather risk indicators. These are "
                    "not official disaster warnings. "
                    "Follow government weather alerts "
                    "for safety."
                )

        except requests.exceptions.RequestException as e:

            st.error(
                f"Weather API Connection Error: {e}"
            )

        except (KeyError, ValueError, TypeError) as e:

            st.error(
                f"Weather Data Processing Error: {e}"
            )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "Smart Weather & Disaster Alert System | "
    "Powered by Python, Streamlit and Open-Meteo API"
)
