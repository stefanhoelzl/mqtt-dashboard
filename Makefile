.PHONY: env
env:
	pip install -r requirements.txt --upgrade

.PHONY: ci
ci:
	vue-cli deploy static static app
