#!/usr/bin/env python
from dataclasses import dataclass
import sys
from django.conf import settings


@dataclass
class User:
    username: str
    first_name: str
    last_name: str
    email: str


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <username> <password>")
        exit(-1)

    username = sys.argv[1]
    password = sys.argv[2]
    create_ou = len(sys.argv) > 3 and sys.argv[3] == "--create-ou"

    user = User(
        username=username,
        first_name=username,
        last_name="Pirata",
        email=f"{username}@pirata.cat",
    )

    settings.configure()
    from humans.directory import Directory

    directory = Directory()

    if create_ou:
        ou, ou_attrs = directory.create_ou("afiliats")

    user_dn, user_attrs = directory.create_user(user)
    directory.set_password(user_dn, password)

    print(f"{user_dn=}\n{password=}\n{user_attrs}")
