# General Guidelines

- version controll the whole project using git
- use a virtual environment when developing
- use consistent code style (i guess autopep8 but up to you)

## Why
- Problem statement
  Code documentation is a notoriously neglected topic in code development.
- Business case or need
  Missing code documentation can make code maintance harder or even impossible. This is particulary problematic for business critical code in smaller business where 
  the number of people familiar with the code is typically very small or even just one. 
- Benefits and value proposition
  A CLI tool is code and can thus be seamlessly integrated in code development pipelines. This makes code documentation creation fully automatic and reduces the documentation
  process to post-controll and 

## Tools/Libraries to Use
<!-- Specify approved tools and libraries for the project -->
- Development tools:
    Use Python version 3.11.0 to write the CLI tool. Use the argparse liberary to provide the python file as a CLI. Use the venv package to create the a virtual environment for development
    All Python packages must be written in a requirements.txt and installed in the virtual environment.
- Testing frameworks:
    The testing system should be decided by the agent based on the projects structure and content. Make sure to always ensure that both PowerShell and bash are supported.
- IDE/Editor recommendations:
    Use VSCode as the IDE. 



## Tools/Libraries to Use
<!-- Specify approved tools and libraries for the project -->
- Development tools:
    Use Python version 3.11.0 to write the CLI tool. Use the argparse liberary to provide the python file as a CLI. Use the venv package to create the a virtual environment for development
    All Python packages must be written in a requirements.txt and installed in the virtual environment.
- Testing frameworks:
    The testing system should be decided by the agent based on the projects structure and content. Make sure to always ensure that both PowerShell and bash are supported.
- IDE/Editor recommendations:
    Use VSCode as the IDE. 

## Code Guidelines
### General Rules (Linting)
<!-- Define general coding standards and linting rules -->
- Code style and formatting requirements:
    - Use autopep8 for Python code.
    - Be explicit rather than implicit when it comes to file names. Use self-explantory names even if they may become longer than usual up to a limit of 255 characters.

### How to Write Documentation
<!-- Documentation standards and practices -->
- Documentation formats
    - All document
- Required documentation sections
- Code commenting standards
- API documentation requirements
- README structure guidelines

### Naming Conventions (Files + Folders)
<!-- File and folder naming standards -->
- File naming patterns
- Directory structure conventions
- Variable and function naming
- Class and module naming
- Constants and configuration naming

### Project Skeleton
<!-- Standard project structure template -->
- Directory layout
- Required files and folders
- Configuration file placement
- Source code organization
- Resource and asset structure

### Examples
<!-- Code examples demonstrating best practices -->
- Sample implementations
- Template files
- Reference implementations
- Common patterns and idioms

## Interaction / Personality Guidelines

### General Interaction Standards
<!-- How team members should interact -->
- Communication protocols
- Code review processes
- Collaboration guidelines
- Meeting standards
- Decision-making processes

## Procedures

### Debugging
<!-- Debugging methodologies and practices -->
- Debugging tools and techniques
- Log analysis procedures
- Error handling standards
- Troubleshooting workflows
- Performance profiling guidelines

### Git Setup / Git Usage
<!-- Version control standards and procedures -->
- Repository setup instructions
- Branch naming conventions
- Commit message standards
- Pull request procedures
- Merge strategies
- Release tagging

### How to Do Testing
<!-- Testing methodologies and requirements -->
- Unit testing standards
- Integration testing procedures
- End-to-end testing guidelines
- Test coverage requirements
- Testing tools and frameworks
- Continuous integration setup

## Core Principles

### BE DRY (Don't Repeat Yourself)
<!-- DRY principle implementation -->
- Code reusability standards
- Abstraction guidelines
- Refactoring procedures

### 1:1 Function/Class Purpose
<!-- Single responsibility principle -->
- Function design principles
- Class design standards
- No legacy code policy
- Version management

### Full Reporting Standards
<!-- Comprehensive reporting requirements -->
- No shortcuts policy
- No mocks/stubs/fakes in production
- Complete implementation requirements
- Transparency in development