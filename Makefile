# OpenTCAM Root
OPENTCAM_ROOT = $(shell git rev-parse --show-toplevel)

# ------------------------------------------ PATHS
include ./scripts/setup_paths.sh

# ------------------------------------------ VARIABLES
include ./scripts/setup_vars.sh

# ------------------------------------------ TARGETS
default: help

loadpaths:
	$(info DIR_COMPILER:		$(DIR_COMPILER))
	$(info DIR_COMP_CONFIGS:	$(DIR_COMP_CONFIGS))
	$(info DIR_COMP_LIB:		$(DIR_COMP_LIB))
	$(info DIR_COMP_SRC:		$(DIR_COMP_SRC))
	$(info DIR_COMP_TESTS:		$(DIR_COMP_TESTS))
	$(info DIR_SCRIPTS:		$(DIR_SCRIPTS))
	$(info DIR_VENV:		$(DIR_VENV))
	$(info DIR_DOCS:		$(DIR_DOCS))
	$(info DIR_IMAGES:		$(DIR_IMAGES))

install_dependencies:
	@ clear
	@ echo ----------------------- Installing basic dependencies ----------------------
	@ sudo apt install git make python3 python3-pip python3-venv
	@ sudo python3 -m pip install --user virtualenv
	@ echo ------------------------------------ DONE ----------------------------------
	@ echo " "

opentcam_venv:
	clear
	@ echo ------------------- Creating OpenTCAM Virtual Environment ------------------
	@ echo " "
	@ bash ${DIR_SCRIPTS}/setup_venv.sh
	@ echo ------------------------------------ DONE ----------------------------------
	@ echo " "

tablemap:
	@ echo " "
	@ echo --------------------------------- OpenTCAM ---------------------------------
	@ python3 $(DIR_COMP_SRC)/main.py \
	--tcamConfig $(TCAMCONFIG) \
	-excel $(EXCEL) -html $(HTML) -json $(JSON) -txt $(TXT) \
	--debug $(DEBUG) --verbose $(VERBOSE)
	@ echo ------------------------------------ DONE ----------------------------------
	@ echo " "

rununittest:
	@ echo " "
	@ echo --------------------------- OpenTCAM Unit Test -----------------------------
	@ python3 -m pytest -v -m ${MARKER} compiler/tests/*.py
	@ echo ------------------------------------ DONE ----------------------------------
	@ echo " "
# run single test using test_class_name and test_name
# @ python3 -m pytest -v compiler/tests/${TESTCLASS}.pytepy::${TESTCLASS}::${TESTNAME}

runregression:
	@ echo " "
	@ echo --------------------------- OpenTCAM Unit Tests ----------------------------
	@ python3 -m pytest -v -s --ff --cache-clear ${DIR_COMP_TESTS}/*.py
	@ echo ------------------------------------ DONE ----------------------------------
	@ echo " "

testmarkers:
	@ echo " "
	@ echo -------------------------- OpenTCAM Test Markers ---------------------------
	@ pytest --markers
	@ echo ------------------------------------ DONE ----------------------------------
	@ echo " "

coverage:
	@ echo " "
	@ echo -------------------------- OpenTCAM Test Coverage --------------------------
	@ coverage erase
	@ echo " "
	@ coverage run --branch -m pytest -v --ff --cache-clear ${DIR_COMP_TESTS}/*.py
	@ echo " "
	@ coverage report -m
	@ echo " "
	@ coverage html --precision=4 --title=${COV_TITLE} -d ${COV_FOLDER}
	@ echo ------------------------------------ DONE ----------------------------------
	@ echo " "

runpylint:
	@ echo " "
	@ echo ------------------------------ Running PyLint ------------------------------
	pylint ${DIR_COMP_SRC}/*.py --output-format=parseable:./logs/pylint.log,colorized \
	--msg-template='{path:s}: (Ln {line:d}, Col {column}) -- {obj} -- {msg_id} -- {msg}' \
	--rcfile=${OPENTCAM_ROOT}/.pylintrc
	@ echo ------------------------------------ DONE ----------------------------------
	@ echo " "

runblack:
	@ echo " "
	@ echo ------------------------------ Running Black ------------------------------
	@ black --check --target-version=py35 ${DIR_COMP_SRC}/*.py
	@ echo " "
	@ black --target-version=py35 ${DIR_COMP_SRC}/.py
	@ echo ---------------------------------- DONE -----------------------------------
	@ echo " "

install_iverilog:
	@ echo " "
	@ echo ------------------------- INSTALLING Icarus Verilog ------------------------
	@ bash ${DIR_SCRIPTS}/install_iverilog.sh
	@ echo ----------------------------------- DONE -----------------------------------
	@ echo " "

install_yosys:
	@ echo " "
	@ echo ------------------- INSTALLING Yosys Open SYnthesis Suite ------------------
	@ bash ${DIR_SCRIPTS}/install_yosys.sh
	@ echo ----------------------------------- DONE -----------------------------------
	@ echo " "

cleanvenv:
	@ echo " "
	@ echo ------------------- Deleting Python Virtual Environment/s ------------------
	@ echo " "
	@ rm -rf .py*
	@ echo ------------------------------------ DONE ----------------------------------
	@ echo " "

cleanlogs:
	@ echo " "
	@ echo --------------------------- Deleting Log File/s ----------------------------
	@ rm -rf logs
	@ echo ------------------------------------ DONE ----------------------------------
	@ echo " "

cleansramtables:
	@ echo " "
	@ echo ---------------------- Deleting SRAM Table Map File/s ----------------------
	@ rm -rf sramTables
	@ echo ------------------------------------ DONE ----------------------------------
	@ echo " "

cleantests:
	@ echo " "
	@ echo --------------------------- Deleting Test Cache ----------------------------
	@ rm -rf ${DIR_COMP_TESTS}/.test_cache
	@ echo ------------------------------------ DONE ----------------------------------
	@ echo " "

cleancoverage:
	@ echo " "
	@ echo ------------------------- Deleting Coverage File/s -------------------------
	@ rm -rf coverage* htmlcov .coverage
	@ echo ------------------------------------ DONE ----------------------------------
	@ echo " "

cleanall: 
	@ make cleanlogs 
	@ make cleansramtables 
	@ make cleantests 
	@ make cleancoverage

deepclean:
	clear
	@ echo " "
	@ echo ------------------------- Deep Cleaning Environment ------------------------
	@ echo " "
	@ make cleanvenv
	@ make cleanall
	@ echo ------------------------------------ DONE ----------------------------------
	@ echo " "

help:
	clear
	@ echo " "
	@ echo ---------------------------- Targets in Makefile ---------------------------
	@ echo ----------------------------------------------------------------------------
	@ echo " "
	@ echo " loadpaths:		display various loaded file paths"
	@ echo " setupvenv:		create a virtual environemnt with all necessary dependencies"
	@ echo " "
	@ echo " runopentcam:		simulate openTCAM"
	@ echo " 	TCAMCONFIG=tcamTableX	tcam table config name"
	@ echo " 	DEBUG=1/0		debugging on/off"
	@ echo " 	VERBOSE=1/0		verbosity on/off"
	@ echo " "
	@ echo " cleanvenv:		remove the virtual env"
	@ echo " cleanlogs:		remove all .log files"
	@ echo " cleandumpfiles:	removes all files generated"
	@ echo " "
	@ echo " deepclean:		delete everything (cleandumpfiles + cleanvenv)"
	@ echo " "
	@ echo " help:			humble people ask for help :)"
	@ echo ----------------------------------------------------------------------------
	@ echo " "

