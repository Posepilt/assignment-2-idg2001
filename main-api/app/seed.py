"""Loads the Kaggle CSV into the database."""
import os
import pandas as pd
from app.database import SessionLocal
from app.models.olympic_event import OlympicEvent


def seed_database():
    """Seed the olympic_events table from the CSV file."""
    db = SessionLocal()
    try:
        count = db.query(OlympicEvent).count()
        if count > 0:
            print(f"Database already seeded ({count} records). Skipping.")
            return

        csv_path = os.path.join(
            os.path.dirname(__file__), "data", "athlete_events.csv"
        )
        if not os.path.exists(csv_path):
            print("CSV not found in data/ folder!")
            return

        print("Seeding database... this may take a moment.")
        csv_data = pd.read_csv(csv_path)

        records = []
        for _, csv_row in csv_data.iterrows():
            record = OlympicEvent(
                name=csv_row.get("Name"),
                sex=csv_row.get("Sex"),
                age=clean_float(csv_row.get("Age")),
                height=clean_float(csv_row.get("Height")),
                weight=clean_float(csv_row.get("Weight")),
                team=csv_row.get("Team"),
                noc=csv_row.get("NOC"),
                games=csv_row.get("Games"),
                year=clean_int(csv_row.get("Year")),
                season=csv_row.get("Season"),
                city=csv_row.get("City"),
                sport=csv_row.get("Sport"),
                event=csv_row.get("Event"),
                medal=clean_str(csv_row.get("Medal")),
            )
            records.append(record)

        chunk_size = 5000  # insert in chunks, doing it all at once uses too much memory
        for i in range(0, len(records), chunk_size):
            db.bulk_save_objects(records[i:i + chunk_size])
            db.commit()
            records_inserted = min(i + chunk_size, len(records))
            print(f"  Inserted {records_inserted}/{len(records)}")

        print("Seeding complete!")
    finally:
        db.close()


def clean_float(val):
    """Convert a value to float, returning None for NaN or missing."""
    try:
        float_value = float(val)
        if pd.isna(float_value):
            return None
        return float_value
    except (ValueError, TypeError):
        return None


def clean_int(val):
    """Convert a value to int, returning None for NaN or missing."""
    float_value = clean_float(val)
    if float_value is not None:
        return int(float_value)
    return None


def clean_str(val):
    """Convert a value to string, returning None for NaN or missing."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    cleaned_string = str(val).strip()
    if cleaned_string and cleaned_string.lower() != "nan":
        return cleaned_string
    return None
