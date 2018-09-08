.PHONY: env
env:
	pip install -r requirements.txt --upgrade

.PHONY: ci
ci:
	rm -Rf static
	vue-cli deploy static static app
	touch static/.nojekyll
