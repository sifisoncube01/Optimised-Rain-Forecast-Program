import requests
import datetime
import json
import os

from typing import Dict, Any, Iterator, Generator, Optional, TextIO


class WeatherForecast:

    def __init__(self, cache_file: str = "weather_cache.json") -> None:
        self.cache_file: str = cache_file
        self._data: Dict[str, Any] = self._load_cache()


    def _load_cache(self) -> Dict[str, Any]:
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_cache(self) -> None:
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=4)

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._save_cache()

    def __getitem__(self, key: str) -> Optional[Any]:
        return self._data.get(key)

    def __iter__(self) -> Iterator[str]:
        return iter(self._data.keys())

    def items(self) -> Generator[tuple[str, Any], None, None]:
        for key, value in self._data.items():
            yield key, value

    def fetch_weather(self, lat: str, lon: str, date: str) -> Optional[float]:
        key = f"{date}_{lat}_{lon}"
        if key in self._data:
            return self._data[key]  # Cached result

        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&daily=precipitation_sum&"
            f"timezone=Europe%2FLondon&start_date={date}&end_date={date}"
        )

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            precip = data.get("daily", {}).get("precipitation_sum", [None])[0]
        except requests.RequestException as e:
            print("Network or API error:", e)
            precip = None
        except Exception as e:
            print("Unexpected error:", e)
            precip = None

        self[key] = precip
        return precip

def precipitation_status(value: Optional[float]) -> str:
    if value is None or value < 0:
        return "I don't know"
    elif value == 0:
        return "It will not rain"
    else:
        return f"It will rain ({value} mm)"

def main() -> None:
    weather_forecast = WeatherForecast()


    user_date = input("Enter a date (YYYY-mm-dd) or leave empty for tomorrow: ").strip()
    if not user_date:
        user_date = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()


    try:
        datetime.datetime.strptime(user_date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Please use YYYY-mm-dd.")
        return

    lat = input("Enter latitude (e.g., 51.5074): ").strip()
    lon = input("Enter longitude (e.g., -0.1278): ").strip()

    precip = weather_forecast.fetch_weather(lat, lon, user_date)
    print(precipitation_status(precip))

    print("\nSaved forecasts:")
    for date_key, value in weather_forecast.items():
        print(f"{date_key}: {precipitation_status(value)}")


if __name__ == "__main__":
    main()
