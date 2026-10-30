"""Lahore Smog Tracker - a tiny Flask app that shows today's AQI.

Run:  python app.py   then open http://127.0.0.1:5000
Air quality and weather come from Open-Meteo, which needs no API key.
"""
from datetime import date, datetime
from statistics import mean

import requests
from flask import Flask, render_template

app = Flask(__name__)

LAHORE = [31.5204, 74.3587]
TIMEZONE = "Asia/Karachi"
AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
TREND_HOURS = 12

# (upper limit, label, colour class, hex colour, advice)
LEVELS = [
    (50, "Good", "good", "#22c55e", "The air is clean. It's a great time to be outside."),
    (100, "Moderate", "moderate", "#eab308", "Acceptable, but sensitive people should take care."),
    (150, "Unhealthy for sensitive groups", "sensitive", "#f97316", "Children and the elderly should limit time outdoors."),
    (200, "Unhealthy", "unhealthy", "#ef4444", "Go outside only if you need to, and wear a mask."),
    (300, "Very unhealthy", "very-unhealthy", "#a855f7", "Avoid going outside. Wear an N95 mask."),
    (10_000, "Hazardous", "hazardous", "#9f1239", "Stay indoors and keep windows closed."),
]

# Open-Meteo "current" keys -> display names. Values are US AQI sub-indexes, not concentrations.
POLLUTANTS = {
    "us_aqi_pm2_5": "PM2.5",
    "us_aqi_pm10": "PM10",
    "us_aqi_nitrogen_dioxide": "NO₂",
    "us_aqi_ozone": "O₃",
}


def classify(aqi):
    for limit, label, css, color, advice in LEVELS:
        if aqi <= limit:
            return {"label": label, "css": css, "color": color, "advice": advice}


def get_json(url, params):
    return requests.get(url, params={**params, "timezone": TIMEZONE}, timeout=10).json()


def fetch_feed():
    """Return current AQI, pollutants, weather, recent hours and forecast, or None if a call fails."""
    lat, lon = LAHORE
    try:
        air = get_json(AIR_URL, {
            "latitude": lat,
            "longitude": lon,
            "current": ",".join(["us_aqi", *POLLUTANTS]),
            "hourly": "us_aqi",
            "past_days": 1,
            "forecast_days": 7,
        })
        weather = get_json(WEATHER_URL, {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        })
        current = air["current"]
        hours = list(zip(air["hourly"]["time"], air["hourly"]["us_aqi"]))
        return {
            "aqi": int(current["us_aqi"]),
            "measured": datetime.fromisoformat(current["time"]),
            "pollutants": {k: current.get(k) for k in POLLUTANTS},
            "weather": {
                "t": weather["current"]["temperature_2m"],
                "h": weather["current"]["relative_humidity_2m"],
                "w": weather["current"]["wind_speed_10m"],  # km/h
            },
            "history": recent_hours(hours, current["time"]),
            "forecast": daily_forecast(hours),
        }
    except (requests.RequestException, ValueError, KeyError, TypeError):
        return None


def recent_hours(hours, now):
    """The last TREND_HOURS hourly readings, up to and including the current hour."""
    past = [(t, v) for t, v in hours if t <= now and v is not None][-TREND_HOURS:]
    history = [{"time": t[-5:], "aqi": int(v)} for t, v in past]
    if history:
        history[-1]["time"] = "Now"
    return history


def daily_forecast(hours):
    """Average hourly AQI per day, from today onwards."""
    days = {}
    for t, v in hours:
        if v is not None:
            days.setdefault(t[:10], []).append(v)
    today = date.today().isoformat()
    return [{"day": d, "avg": round(mean(vals))} for d, vals in days.items() if d >= today][:7]


@app.route("/")
def index():
    feed = fetch_feed()
    level = classify(feed["aqi"]) if feed else None

    forecast, pollutants, history = [], [], []
    if feed:
        history = feed["history"]
        for key, name in POLLUTANTS.items():
            v = feed["pollutants"].get(key)
            pollutants.append({"name": name, "value": v, "color": classify(v)["color"] if v is not None else None})
        for f in feed["forecast"]:
            day = date.fromisoformat(f["day"])
            label = "Today" if day == date.today() else day.strftime("%a")
            forecast.append({**f, "label": label, "date": day.day, "level": classify(f["avg"])})

    aqis = [h["aqi"] for h in history]
    return render_template(
        "index.html",
        feed=feed,
        geo=LAHORE,
        level=level,
        levels=[{"limit": l, "label": lab, "color": c} for l, lab, _, c, _ in LEVELS],
        pollutants=pollutants,
        forecast=forecast,
        history=history,
        peak=max(aqis, default=None),
        low=min(aqis, default=None),
        measured=feed["measured"].strftime("%d %b %Y, %H:%M") if feed else None,
        now=datetime.now().strftime("%H:%M"),
    )


if __name__ == "__main__":
    app.run(debug=True)
