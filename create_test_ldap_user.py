#!/usr/bin/env python
from dataclasses import dataclass
import sys
from django.conf import settings


@dataclass
class User:
    username: str
    first_name: str
    last_name: str


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <username> <password>")
        exit(-1)

    username = sys.argv[1]
    password = sys.argv[2]

    user = User(username=username, first_name=username, last_name="Pirata")
    email = f"{username}@pirata.cat"

    settings.configure()
    from humans import directory

    conn = directory.connect()
    ou, ou_attrs = directory.create_ou(conn, "afiliats")
    user_dn, user_attrs = directory.create_user(conn, user, email)
    directory.set_password(conn, user_dn, password)

    print(f"{user_dn=}\n{password=}\n{user_attrs}")
