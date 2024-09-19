import unittest
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
os.environ['RESTAPI_USE_ARCPY'] = 'FALSE'

from test_geohandling import TestGeoHandling

if __name__ == '__main__':
    unittest.main()
