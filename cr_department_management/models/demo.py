# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from datetime import timedelta, datetime

today = datetime.today().date()
date1 = datetime(2025, 6, 11).date()

print(today)
before_30_days = today - timedelta(days=30)
print(before_30_days)

print(date1 > (today - timedelta(days=30)))
