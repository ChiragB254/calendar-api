import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from icalendar import Calendar, Event
from datetime import datetime
from io import BytesIO
from pydantic import BaseModel
import os

app = FastAPI()

# Directory to save .ics files
ICS_DIR = "ics_files"
os.makedirs(ICS_DIR, exist_ok=True)

# Request model
class FlightDetails(BaseModel):
    outbound_flight_number: str
    outbound_departure_airport: str
    outbound_arrival_airport: str
    outbound_departure_time: str
    outbound_arrival_time: str
    inbound_flight_number: str
    inbound_departure_airport: str
    inbound_arrival_airport: str
    inbound_departure_time: str
    inbound_arrival_time: str

@app.post("/generate-ics")
async def generate_ics(flight_data: FlightDetails):
    try:
        # Parse datetime strings
        outbound_departure_time = datetime.strptime(flight_data.outbound_departure_time, "%Y-%m-%d %H:%M")
        outbound_arrival_time = datetime.strptime(flight_data.outbound_arrival_time, "%Y-%m-%d %H:%M")
        inbound_departure_time = datetime.strptime(flight_data.inbound_departure_time, "%Y-%m-%d %H:%M")
        inbound_arrival_time = datetime.strptime(flight_data.inbound_arrival_time, "%Y-%m-%d %H:%M")
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD HH:MM."}
    
    # Create a new calendar
    cal = Calendar()
    
    # Create outbound event
    outbound_event = Event()
    outbound_event.add('summary', f'Flight {flight_data.outbound_flight_number} from {flight_data.outbound_departure_airport} to {flight_data.outbound_arrival_airport}')
    outbound_event.add('dtstart', outbound_departure_time)
    outbound_event.add('dtend', outbound_arrival_time)
    outbound_event.add('dtstamp', datetime.now())
    outbound_event.add('location', f'{flight_data.outbound_departure_airport} to {flight_data.outbound_arrival_airport}')
    cal.add_component(outbound_event)

    # Create inbound event
    inbound_event = Event()
    inbound_event.add('summary', f'Flight {flight_data.inbound_flight_number} from {flight_data.inbound_departure_airport} to {flight_data.inbound_arrival_airport}')
    inbound_event.add('dtstart', inbound_departure_time)
    inbound_event.add('dtend', inbound_arrival_time)
    inbound_event.add('dtstamp', datetime.now())
    inbound_event.add('location', f'{flight_data.inbound_departure_airport} to {flight_data.inbound_arrival_airport}')
    cal.add_component(inbound_event)
    
    # Save to file
    ics_filename = f"{ICS_DIR}/flight_schedule.ics"
    with open(ics_filename, "wb") as f:
        f.write(cal.to_ical())

    return {"message": "ICS file generated successfully!", "download_url": "/download-ics"}

@app.get("/download-ics")
async def download_ics():
    ics_filename = f"{ICS_DIR}/flight_schedule.ics"
    return FileResponse(ics_filename, media_type="text/calendar", filename="flight_schedule.ics")

# Run the API
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
