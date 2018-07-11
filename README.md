# Data Pipeline Templates
This repository contains templates for common AVF data pipeline stages.

New projects should use clones of these templates as a foundation in order to start faster and to help ensure a standard 
data pipeline format across projects. 

## Provided Templates
The standard pipeline being used here takes the format:
```
            /--> fetch messages ------------------------------> messages ------------------------------------\
SMS platform                                                                                                  --> analysis
            \--> fetch surveys --> survey auto code --> Manually code in Coda or CSV --> survey merge coded -/
```
 
To fetch data from an SMS platform, use one of AVF's SMS fetchers (e.g. 
[EchoMobileExperiments](https://github.com/AfricasVoices/EchoMobileExperiments) or
[RapidProExperiments](https://github.com/AfricasVoices/RapidProExperiments)).

This repository contains the templates for the following pipeline stages:

### Messages Pipeline
Reads a list of radio show answers from a serialised TracedData JSON file, cleans the messages, 
and exports to formats suitable for subsequent analysis. 

### Survey Auto Code
Reads a list of survey responses from a serialised TracedData JSON file, cleans the responses, and exports to Coda or 
Coding CSV files for manual verification and coding.

### Survey Merge Coded
Applies manually-assigned codes from Coda or Coding CSV files to a TracedData JSON file.

## Usage
To use one of the provided stage templates in a new project, first clone the relevant sub-directory of this project.
Then, in that directory:

1. Create a virtual environment with `$ pipenv --three`.
2. Synchronise existing dependencies with `$ pipenv sync`.
3. If additional dependencies are required, install them with `$ pipenv install <dependency>`.
4. Modify the python file for that stage by adding project-specific behaviour. 
   Refer to the in-file TODOs for guidance on what to add.
1. Test locally with `$ pipenv run python <file.py> <args>`
1. Update the IMAGE_NAME variable at the top of `docker-run.sh`.
1. If the modifications made in step 4 modified the program arguments for this stage, then update the `CMD` instruction
   in the `Dockerfile` as well as the relevant lines of `docker-run.sh`. 
1. Test in Docker with `$ sh docker-run.sh <args>`
