down_v:
	docker compose down -v


down:
	docker compose down


up: down
	docker compose up --build -d

rmi:
	docker rmi freedom_hakaton-app freedom_hakaton-add_to_elastic

add_el:
	python3 parse.py --create-index=True