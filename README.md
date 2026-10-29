# Lahore Smog Tracker

A dashboard that shows how clean (or polluted) Lahore's air is at a glance: today's AQI, what it means, a smog map, a 7-day forecast and a chart of recent readings.

## Problem

Every winter Lahore's smog gets serious, but most AQI websites are cluttered. I only wanted an answer to one question: "Is it safe to go outside today?"

## Features

- Live US AQI for Lahore from Open-Meteo (no API key needed)
- Simple health advice for every level, from Good to Hazardous
- Smog map, temperature, humidity, wind and pollutant breakdown
- AQI trend for the last 12 hours
- 7-day AQI forecast

## Run

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

## Data source

Air quality and weather come from [Open-Meteo](https://open-meteo.com/), which is free and needs no key. The AQI is model-based (Copernicus CAMS), so it covers Lahore even though there's no public monitoring station with current readings.

## Project structure

```
smog-tracker/
├── app.py              # Flask app and Open-Meteo calls
├── templates/index.html
├── static/style.css
└── requirements.txt
```

## Roadmap

- [x] Live Lahore data
- [ ] Hourly forecast for the next 24 hours
- [ ] Telegram alert when AQI goes above 200
- [ ] More cities (Karachi, Islamabad)
- [ ] Deploy (Render / PythonAnywhere)
