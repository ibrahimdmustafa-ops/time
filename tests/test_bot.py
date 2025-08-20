import pytest
import pytz
from datetime import datetime
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path to import bot modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot_enhanced import get_local_time, build_keyboard, CITY_TIMEZONES


class TestTimezoneBot:
    """Test suite for the Telegram timezone bot."""

    def test_get_local_time_valid_city(self):
        """Test getting time for a valid city."""
        result = get_local_time("New York")
        assert "❌" not in result
        assert ":" in result  # Should contain time format
        assert "AM" in result or "PM" in result

    def test_get_local_time_invalid_city(self):
        """Test getting time for an invalid city."""
        result = get_local_time("Invalid City")
        assert "❌ Timezone not found." in result

    def test_build_keyboard_first_page(self):
        """Test building keyboard for first page."""
        keyboard = build_keyboard(0)
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) > 0

    def test_build_keyboard_pagination(self):
        """Test keyboard pagination."""
        # Test that we have enough cities to paginate
        total_cities = len(CITY_TIMEZONES)
        assert total_cities > 6  # Should have more than one page

        keyboard = build_keyboard(0)
        # Should have navigation if more than 6 cities
        has_next = any("Next" in str(button) for row in keyboard.inline_keyboard for button in row)
        assert has_next

    def test_city_timezones_validity(self):
        """Test that all city timezones are valid."""
        invalid_timezones = []
        for city, tz_name in CITY_TIMEZONES.items():
            try:
                pytz.timezone(tz_name)
            except pytz.exceptions.UnknownTimeZoneError:
                invalid_timezones.append((city, tz_name))
        
        assert len(invalid_timezones) == 0, f"Invalid timezones found: {invalid_timezones}"

    def test_time_format(self):
        """Test that time format is consistent."""
        result = get_local_time("Toronto")
        lines = result.split('\n')
        
        # Should have at least 2 lines (time and date)
        assert len(lines) >= 2
        
        # First line should contain time with AM/PM
        time_line = lines[0]
        assert "AM" in time_line or "PM" in time_line
        assert ":" in time_line

    @patch('bot_enhanced.datetime')
    def test_timezone_conversion(self, mock_datetime):
        """Test timezone conversion accuracy."""
        # Mock a specific datetime
        mock_now = datetime(2025, 1, 15, 12, 0, 0)  # Noon UTC
        mock_datetime.now.return_value = mock_now
        
        # This test would need more sophisticated mocking
        # to properly test timezone conversion
        pass

    def test_cities_coverage(self):
        """Test that we have good coverage of major cities."""
        us_cities = [city for city, tz in CITY_TIMEZONES.items() 
                    if tz.startswith("America/") and not any(canadian in city.lower() 
                    for canadian in ["toronto", "montreal", "vancouver", "calgary", "ottawa"])]
        
        canadian_cities = [city for city, tz in CITY_TIMEZONES.items() 
                          if any(canadian in tz.lower() 
                          for canadian in ["toronto", "vancouver", "edmonton", "winnipeg", "halifax", "regina", "st_johns"])]
        
        assert len(us_cities) >= 40  # Should have at least 40 US cities
        assert len(canadian_cities) >= 40  # Should have at least 40 Canadian cities


if __name__ == "__main__":
    pytest.main([__file__, "-v"])