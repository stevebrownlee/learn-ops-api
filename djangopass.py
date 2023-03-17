import sys
from django.contrib.auth.hashers import make_password

print(make_password(sys.argv[1]))
sys.exit(0)
