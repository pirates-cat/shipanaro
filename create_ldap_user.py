#!/usr/bin/env python
import sys
from django.conf import settings

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <username> <password> <uid>")
        exit(-1)

    username = sys.argv[1]
    password = sys.argv[2]
    uid = sys.argv[3]

    settings.configure()
    from humans import directory

    conn = directory.connect()
    user_dn, user_attrs = directory.create_user(conn, username, uid)
    directory.set_password(conn, user_dn, password)

    print(f"{user_dn=}\n{password=}\n{user_attrs}")
