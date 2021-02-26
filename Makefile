IMAGE=shipanaro
VERSION?=latest

init-data:
	./indocker.sh ./manage.py migrate humans
	./indocker.sh ./manage.py migrate

shell:
	./indocker.sh ./manage.py shell

clean-data:
	docker-compose down --volumes

lint:
	black .

run: stop
	docker-compose up --detach --build

stop:
	docker-compose down

test:
	./indocker.sh ./manage.py test -v2

collected: static
	./indocker.sh ./manage.py collectstatic --noinput

ldap-list:
	docker-compose exec ldap ldapsearch -x -H ldap://localhost -b dc=pirata,dc=cat -D "cn=admin,dc=pirata,dc=cat" -w admin

i18n:
	./indocker.sh ./manage.py makemessages --locale ca
	@echo "Please edit locale/ca/LC_MESSAGES/django.po to add new translations"

i18n-compile:
	./indocker.sh ./manage.py compilemessages
	docker-compose restart web

package:
	docker build -t ${IMAGE}:${VERSION} .

publish:
	docker tag ${IMAGE}:${VERSION} piratescat/${IMAGE}:${VERSION}
	docker push piratescat/${IMAGE}:${VERSION}

k8s-restart:
	kubectl rollout restart deploy/${IMAGE}

.PHONY: init-data clean-data lint run stop test ldap-test
