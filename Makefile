SHELL := /usr/bin/env bash

.PHONY: help up down restart ps logs smoke evidence build clean

help:
	@echo "VenueOps Cloud Platform"
	@echo "make up        Start local demo"
	@echo "make down      Stop local demo"
	@echo "make restart   Restart local demo"
	@echo "make ps        Show containers"
	@echo "make logs      Follow logs"
	@echo "make smoke     Run smoke test"
	@echo "make evidence  Capture evidence files"
	@echo "make build     Build all containers"
	@echo "make clean     Remove containers and local volumes"

up:
	bash scripts/local-up.sh

down:
	bash scripts/local-down.sh

restart:
	bash scripts/local-down.sh
	bash scripts/local-up.sh

ps:
	docker compose ps

logs:
	docker compose logs -f

smoke:
	bash scripts/smoke-test.sh

evidence:
	bash scripts/generate-evidence.sh

build:
	docker compose build

clean:
	docker compose down -v --remove-orphans
