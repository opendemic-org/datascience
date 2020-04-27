from unittest import TestCase

import opendemic.data as odd


class TestRegionData(TestCase):
    """Test the RegionData class tailored on the usa data"""

    def test_check_fetch_is_implemented(self):
        """Test if the .fetch(...) method is implemented."""
        odd.USARegionData.fetch(state='NY')
        odd.USARegionData.fetch(county=1001)
