SHELL := /bin/bash
install:
	pip install poetry==1.8.3 poeblix==0.10.0
	cd src; poetry install
