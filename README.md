# Description-Audit
This repository contains tools and other files used as part of a project to audit archival metadata in Duke's Rubenstein Library for potentially harmful (e.g. racist, sexist, ableist, colonialist) language. These tools are available to archivists and librarians from other institutions and any other interested parties to enable quick, computer-aided identification and categorization of harmful language use in archival description. The description_audit search tool can be run from the command line as a Python script or as a stand-alone application (OS-dependent). The application can be downloaded and run without any programming expertise.
## What Does This Do? How?
The audit search tool searches EAD and MARC data (in .xml file format) for the presence of defined harmful terms or phrases using BeautifulSoup as an XML parser and a [SpaCy rule-based matcher](https://spacy.io/usage/rule-based-matching) to identify these terms. Matches are recorded in CSV output files that include the collection title, call number, user-designated harmful language category, and context for the term's use. These reports are intended a starting point for human analysis and additional categorization (whose structure at the Rubenstein is outlined in a document in the reports folder). The automated CSV reports and human analysis are used as a basis for prioritizing remediation work across archival data.
## Our Audit
The archival description audit at Rubenstein Library has two primary goals:
1. To surface, analyze, and remediate harmful language in our descriptive outputs (e.g. finding aids and catalog records) that is racist, sexist, ableist, colonialist, aggrandizing, white-supremacist or otherwise harmful in some way. 
2. To identify collections where BIPOC voices and experiences have been ignored, undervalued, or misrepresented and to prioritize those collections for re-processing / remediation.
The description audit is part of a larger, multi-year effort outlined in the Rubenstein's [Anti-Racist Roadmap](https://blogs.library.duke.edu/rubenstein/2020/12/03/reckoning-with-our-past-and-present/).
## Repository Contents
- **/lexicons** - Lists of harmful terms or phrases organized into broad categories (e.g. terms of aggrandizement, race euphemisms, terms related to enslavement, etc.).

- **/reports** - Sample CSV reports indicating presence, context, and location of potentially harmful language in archival materials. Organization system used by the Rubenstein library for manual parsing of these computerized results is included as well, along with examples. (Samples ONLY included in public repository)

- **/scripts** -  Python scripts that use Beautiful Soup for parsing XML and the [spaCy NLP](https://spacy.io/) library to search and report out term and phrase matches in MARCXML and EAD inputs

- **/source_data** - Although most source data has been removed publicly for the sake of repository storage and distribution, we have provided examples of an EAD record (.xml file) and an excerpt of our single-file MARC record (.xml file) to demonstrate the archive formats that this program is able to work over.

- **/dist** - Operating system-dependent PyInstaller executable versions of the Python scripts used to inventory instances, context, and other relevant information about each time potentially harmful terms appears in given metadata. Using one of these executables, no dependencies are required, even Python itself.
## Installation/Distribution
There are multiple ways to access these tools, varying in required skills and levels of flexibility.
### Least Flexible, Non-Technical Installation:
Not a developer? Just want to use the program as it currently exists and see if it works for your archives? This is for you!
Click [here](https://gitlab.oit.duke.edu/dul-rubenstein/description-audit/-/blob/master/dist/description_audit.exe) to download the executable for Windows computers. Click on the download to run the program, input the needed information on the setup screen, and wait approximately ten minutes for the program to search your data. After this, you should see a CSV file(s) in the folder you chose on the setup screen containing your results.
### Clone the Repository:
This requires you to have git, a GitHub account, Python 3.8, and some kind of package or environment manager (e.g. pip, homebrew, conda).
First, fork the repository so any changes you make don't impact the main version or anyone else's changes. Then, copy the project fork's SSH key or HTTPS key (depending on your git configuration), navigate via command line to the directory where you want this repository to be stored on your computer, and clone the repository using the key.

    git clone <ssh or https key>
Once your forked version of the repository is cloned to your local environment, install dependencies from the requirements.txt file. It is recommended to install these dependencies to a virtual environment of your choice. For example, to use Python's built-in venv system and pip, with Python installed along your system path on Windows:

    C:\> python -m venv c:\path\to\myenv #relative or absolute
    C:\> <venv>\Scripts\activate.bat #activate virtual env
    C:\> pip install -r requirements.txt
Once all dependencies are installed, the main audit search program can be run with (on Windows):

    python ./description_audit.py
This command will launch the program with the GUI active. To input your setup parameters (such as file paths) from the command line, use the flag --nogui and refer to description_audit_driver.py function in the scripts folder to see the contents and parameters of the command line parser if needed.
About 10 minutes after the parameters are given, the process should be completed, with matches to the given lexicons stored in the chosen folder as CSV files.
## Contributions
Suggestions and contributions are welcome! In particular, we are looking for someone who is able to create executables for a wider variety of operating systems. Even if you run the script from the command line, if you have a non-Windows OS, please consider using your programming skills and the instructions in create_executable_instructions.txt in the repository main folder to create an executable version to help other users with your operating system.

For bugs or usability issues, please raise an issue on GitHub. For new feature implementations, expansions, or any larger changes that you might make, we'd love if you made a pull/merge request to share that information with us.
## Refactoring TODO's & Expansion Ideas:
*Expansion ideas on this project are not in active development; formal development through the Rubenstein Library has ended, so interested parties are invited to contribute to making new features a reality!*

Opportunities for further refactoring/restructuring include improving the performance bottleneck of accessing archival records and transforming them into BeautifulSoup objects (potentially using SoupStrainer from BS4?), adding functionality to better identify locations of lexicon matches within the archival entry (using ArchiveSpace ID's for example), and making CSV writing function more elegant.

Opportunities for expansion include analyzing match data to highlight distributions of matches (most common lexicons, locations of matches, etc.) and presenting this via visualizations/summary statistics in the GUI to allow for easy strategizing for remediation.
## Credits
This project was started by Noah Huffman at the Rubenstein Library, and expanded by [Miriam Shams-Rainey](https://www.linkedin.com/in/mshamsrainey/), a CS and Linguistics undergrad at Duke. 

This project was inspired by many other librarians and archivists who have written, presented, or otherwise shared their expertise, strategies, and tools for promoting more inclusive archival description practices. In particular, we'd like to acknowledge work by Archives for Black Lives in Philadelphia (find their [GitHub here](https://github.com/a4blip/A4BLiP)), [Jarrett Drake](https://medium.com/on-archivy/radtech-meets-radarch-towards-a-new-principle-for-archives-and-archival-description-568f133e4325), [Michele Caswell](https://doi.org/10.1086/692299), and [Dorothy Berry](https://youtu.be/XGCTtDgNty4) just to name a few. Many of the lexicon terms and phrases in this project were borrowed from Kelly Bolding of Princeton University ([GitHub](https://github.com/kellybolding/scripts)) (thanks, Kelly!). The initial Python / spaCy reporting framework was heavily influenced by Kayla Heslin's work ([Github](https://github.com/kheslin0420/kheslin0420.github.io/tree/master/Legacy_Description_Audit)) at the University of Pittsburgh.
