SHELL := /bin/bash
.DEFAULT_GOAL := help
-include .env
SERIES ?= 3
WINE_VERSION ?= 11
IMAGE ?= ghcr.io/vknmnn/ahnenblatt-docker
BASE_IMAGE ?= ghcr.io/linuxserver/baseimage-selkies:debiantrixie
SOURCE_URL ?= https://github.com/vKnmnn/ahnenblatt-docker
REVISION ?= unknown
CONFIG_DIR ?= ./data/$(SERIES)
export

.PHONY: help check lock lock-all build build-all smoke smoke-all push push-all login up down logs
help:
	@printf '%s\n' \
	  'make lock SERIES=5        Download, verify version and record installer SHA-256' \
	  'make lock-all             Lock all four installers (Python 3 + exiftool required)' \
	  'make check                Static checks; no Docker daemon required' \
	  'make build SERIES=5       Build the image with Wine 11' \
	  'make smoke SERIES=5       Test fresh startup, data mapping and restart in isolation' \
	  'make push SERIES=5 IMAGE=ghcr.io/owner/ahnenblatt  Build, smoke-test, then publish' \
	  'make build-all / smoke-all / push-all' \
	  'make login                Interactive docker login ghcr.io' \
	  'make up / down / logs     Manage the configured Compose instance'
check:
	bash scripts/check.sh
lock:
	python3 scripts/versions.py lock "$(SERIES)"
lock-all:
	python3 scripts/versions.py lock all
build:
	bash scripts/image.sh build
build-all:
	@for series in 2.99 3 4 5; do $(MAKE) build SERIES=$$series || exit $$?; done
smoke:
	bash scripts/smoke.sh "$(IMAGE):$(SERIES)-wine$(WINE_VERSION)"
smoke-all:
	@for series in 2.99 3 4 5; do $(MAKE) smoke SERIES=$$series || exit $$?; done
push:
	bash scripts/image.sh publish
push-all:
	@for series in 2.99 3 4 5; do $(MAKE) push SERIES=$$series || exit $$?; done
login:
	docker login ghcr.io
up:
	docker compose up -d
down:
	docker compose down
logs:
	docker compose logs -f --tail=100
