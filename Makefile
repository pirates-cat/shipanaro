IMAGE=shipanaro
VERSION?=latest

init-data:
	./indocker.sh ./manage.py migrate humans
	./indocker.sh ./manage.py migrate

test-user-delete:
	docker-compose run --entrypoint 'ldapdelete -x -H ldap://ldap -D "cn=admin,dc=pirata,dc=cat" -w admin "cn=tester,dc=pirata,dc=cat"' ldap || echo "User doesn't exist"

test-user-create: test-user-delete
	docker-compose run web ./create_ldap_user.py tester tester

shell:
	./indocker.sh ./manage.py shell

clean-data:
	docker-compose down --volumes

lint:
	black .

run: stop
	docker-compose up --build

stop:
	docker-compose down

test: test-user-create
	docker-compose run web ./manage.py test -v2

collected: static
	./indocker.sh ./manage.py collectstatic --noinput

ldap-list:
	docker-compose exec ldap ldapsearch -x -H ldap://localhost -b dc=pirata,dc=cat -D "cn=admin,dc=pirata,dc=cat" -w admin

i18n:
	./indocker.sh ./manage.py makemessages --locale ca
	@echo "Please edit locale/ca/LC_MESSAGES/django.po to add new translations"

i18n-compile:
	./indocker.sh ./manage.py compilemessages --ignore .venv
	docker-compose restart web

package:
	docker build -t ${IMAGE}:${VERSION} .

publish:
	docker tag ${IMAGE}:${VERSION} piratescat/${IMAGE}:${VERSION}
	docker push piratescat/${IMAGE}:${VERSION}

k8s-restart:
	kubectl rollout restart deploy/${IMAGE}

.PHONY: init-data clean-data lint run stop test ldap-test
