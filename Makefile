.PHONY: build manjaro


build: manjaro

manjaro:
	@rm -r tmp || true
	@mkdir -p tmp
	@cd tmp

	sudo basestrap -cdGM tmp filesystem pacman
