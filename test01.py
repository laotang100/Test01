import re
from decimal import Decimal
from datetime import date,datetime

r = 'w+'

v = re.match(r,'aabbcc',re.M)

a = Decimal('0.1')

d = date.today()