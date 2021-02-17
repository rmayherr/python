from datetime import datetime as dt
from datetime import timedelta as td

def time_delta(t1, t2):
    tmp1, tmp2 = td, td
    tmp1 = dt.strptime(t1[4:], '%d %b %Y %H:%M:%S %z')
    tmp2 = dt.strptime(t2[4:], '%d %b %Y %H:%M:%S %z') 
    return f"{int(abs(tmp1 - tmp2).total_seconds())}"

def test_time_delta():
    assert time_delta("Sun 10 May 2015 13:54:36 -0700","Sun 10 May 2015 13:54:36 -0000") == '25200'
    assert time_delta("Sat 02 May 2015 19:54:36 +0530","Fri 01 May 2015 13:54:36 -0000") == '88200'
    assert time_delta("Fri 11 Feb 2078 00:05:21 +0400","Mon 29 Dec 2064 03:33:48 -1100") == '413962293'
