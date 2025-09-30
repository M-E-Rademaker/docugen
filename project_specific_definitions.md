# Project-Specific Definitions

## Project Definition

### What
<!-- Clear definition of what the project is -->
- Project purpose and scope
    - Provide a CLI that takes an .sql or .python .r file or folder of files and docuement the code according to predefined documentation standards.
      saving the file afterwards 
- Core functionality description
    - The tool takes a file or folder containing files and does the following
      1. It checks the file endings for .sql, .py. or .r.
      1. It checks for existing documentation in these files
        a. If an existing documentation is found it checks if the documentation is compliant with the specific language documentation standard
        b. If no existing documentation is found it creates a documentation using the specific language documentation standard
    - Depending on the file type, the following documentation standards are used
      - for .sql: use markdown-style syntax
      - for .py: use numpy/scipy-style docstring 
      - for .r: use roxygen2
    - Once edited it safes a modified version of the file using the orginal file name with the *__cli_dcreate_modified* suffix added a file name is given as the the second argument.
- Target audience
    - Data scientists and data engeineers
- Key features and capabilities
    - Works in Windows PowerShell and Linux Bash
    - Requires Python 3.11.0 for .py file documentation
    - Requires R for .r file documentation

### Why
<!-- Justification and motivation for the project -->
- Problem statement
  Code documentation is a notoriously neglected topic in code development.
- Business case or need
  Missing code documentation can make code maintance harder or even impossible. This is particulary problematic for business critical code in smaller business where 
  the number of people familiar with the code is typically very small or even just one. 
- Benefits and value proposition
  A CLI tool is code and can thus be seamlessly integrated in code development pipelines. This makes code documentation creation fully automatic and reduces the documentation
  process to post-controll and 

### How
<!-- High-level approach and methodology -->
- Technical approach and implementation strategy
  The tool is written in Python 3.11.0. It uses the argparse libary to provide a user interface.

## Version control
- Use git for version control

## CLI Usage Examples

dcreate my_py_file.py # defaults to saving the file as *my_py_file__cli_dcreate_modified.py*
dcreate my_py_file.py --my_py_file_documented.py 

### Primary Use Cases
<!-- Main scenarios where the project will be used -->
- Use case 1: [dbt model]
  - Description
    A new dbt model 
  - User story
  - Expected outcome
- Use case 2: [Title]
  - Description
  - User story
  - Expected outcome

## (Sub)Agent Definitions

### Key Agents for the Project
<!-- Define the main agents/components -->

#### Agent 1: [python_god]
- Purpose and responsibility:
  xxx
- Input/output specifications
- Dependencies
- Configuration requirements

#### Agent 2: [testing_god]
- Purpose and responsibility
- Input/output specifications
- Dependencies
- Configuration requirements

#### Agent 2: [project_coordinator]
- Purpose and responsibility
- Input/output specifications
- Dependencies
- Configuration requirements