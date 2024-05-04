CMD_BLACK		:=	black
CMD_ISORT		:=	isort
CMD_PYLINT		:=	pylint

SOURCES			:= \
					"lib" \
					"frankenpest.py" \


.PHONY: help
help:
	@echo "Einfach mal die Presse falten!"
	@echo "------------------------------"
	@echo
	@echo "isort            run isort on code"
	@echo "black            run black on code"
	@echo "pylint           run pylint on code"


.PHONY: isort
isort:
	$(CMD_ISORT) --line-length="79" --profile="black" $(SOURCES)

.PHONY: black
black:
	$(CMD_BLACK) --line-length="79" $(SOURCES)

.PHONY: pylint
pylint:
	$(CMD_PYLINT) \
		--disable="missing-class-docstring" \
		--disable="missing-function-docstring" \
		--disable="missing-module-docstring" \
		--output-format="colorized" \
	$(SOURCES)
