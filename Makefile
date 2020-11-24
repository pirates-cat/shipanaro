init-data:
	./indocker.sh ./manage.py migrate humans
	./indocker.sh ./manage.py migrate

clean-data:
	docker-compose down --volumes

lint:
	black .

run: stop
	docker-compose up -d # --build

stop:
	docker-compose down

test:
	./indocker.sh ./manage.py test -v2

collected: static
	./indocker.sh ./manage.py collectstatic --noinput

.PHONY: init-data, clean-data, lint, run, stop, test
