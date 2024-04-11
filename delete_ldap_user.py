#!/usr/bin/env python
import sys
from django.conf import settings

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <username>")
        exit(-1)

    username = sys.argv[1]

    settings.configure()
    from humans.directory import Directory

    directory = Directory()
    directory.delete_user(username)

    print(f"User '{username}' deleted from LDAP")
