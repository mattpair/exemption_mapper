# exemption_mapper
Recreate MLS tool using census data and public tax portal to find potentially under-valued properties

Census data taken from https://openaddresses.io/
exemptions.py runs each Chicago address through Cook County Tax Portal: http://www.cookcountypropertyinfo.com/
mapper.py will plot each property with exemptions and will be searchable.

Requires pipenv and selenium webdriver for Chrome
