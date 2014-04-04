#!/usr/bin/env python
from __future__ import print_function
import sys

from django.db import connection
from django_scim.filter import SCIMFilterTransformer

print('Interactive SCIM filter console for Django\'s user database.')
print('Type your query below and press enter.')
print('Example:')
print('  givenName sw "Erik" AND (emails co "zijst" or username sw "e") AND active eq true')

while True:
    sys.stdout.write('scim> ')
    line = sys.stdin.readline()
    if not line:
        break
    try:
        users = list(SCIMFilterTransformer.search(
            line.rstrip().encode('utf-8')))
        print(connection.queries[-1]['sql'])
        for u in users:
            print (u.username)
    except Exception as e:
        print(e)
