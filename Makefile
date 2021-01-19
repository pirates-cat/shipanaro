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


.PHONY: init-data clean-data lint run stop test ldap-test
