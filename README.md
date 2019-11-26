# dynaswap
This repository contains the openMRS dynaswap module and other shell scripts which are being utilized in the project.
## dynaswap-omrs
This folder contains the openMRS dynaswap module. The module alows to modify the existing openMRS database and facilitate other customizations as required.
## Shell-scripts
This folder includes all the shell scripts that will be used in the project. Currently includes add users script which add users and their public keys on startup to a VM.
## integration-tests
This folder contains the Gherkin BDD `.feature` file and related pytest files. You can execute the test scripts and get the CVSS score using `pytest -s`
You need to install the following:

 - Firefox web driver using: `sudo apt-get install firefox-geckodriver`. 
 - pytest and pytest-bdd using: `pip install pytest pytest-bdd`
 - selenium using: `pip install selenium`
