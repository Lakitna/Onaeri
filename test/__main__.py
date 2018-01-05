import pytest
import os
import shutil

"""
Create a setting file for the test procedure
"""
folderPath = os.path.dirname(os.path.abspath(__file__))
folderPath = os.path.split(folderPath)[0] + "/settings"

srcfile = folderPath + '/Template.py'
dstfile = folderPath + '/test.py'

shutil.copy(srcfile, dstfile)

"""
Actually run pytest
"""
pytest.main()

"""
Remove the test settings file
"""
os.remove(dstfile)
