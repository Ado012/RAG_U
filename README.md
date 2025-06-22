Retrival Augmented Generation for U, RAG-U is a simple LLM tool built on the Haystack framework that enables automated batch retrival augmented generation (RAG), information distillation, and analysis based on a user specified list of websites and/or text files through an OpenAI interface. Put simply you can 'ask' any question about a given list of websites/or files and the LLM will loop through each one and attempt to answer the question. For example a query of 'are there any jobs available?' with a list of company websites would ideally output an answer for each website. The scraper can also be used on its own by changing the parameters as desired and examining the raw datafiles. 


WARNING: the tool is currently just an experimental casual project. Although tested and working in certain instances it may not work correctly or as expected if set up improperly or even if set up properly for other cases and expectations. Challenges remain with getting the webscraper to extract from a wide variety of websites as well as more effective use of the LLM. It is mostly designed to work on simple sites for small and midsized organizations and cannot currently process complicated structures like large job posting sites for very large corporations. Certain sites cannot be retrieved from. 



#####  Parameters

The parameters of the program can be set up differently depending on purpose. 


*question* = Specifies the request for the LLM to perform upon the data. ex: "Summarize the following biotech company website text: <br>
*backgroundPrompt*: sets the background prompt: ex:  "I am a website summarizer. What website text do you wish me to summarize?" <br>
*collatelinks* = 1: links from a website are scraped into one text file. 0: Links will be scraped into different text files <br>
*linkdepth* = 1 : How deep will the scraper crawl. Larger numbers crawl deeper. <br>
*mergeddocuments*: 0: Documents are processed by the LLM individually, 1: all documents are merged together and run in the pipeline   <br>
*llmoption* = 1 : openai remote model  <br>
*linkruleset* = [['job','career','recruit','opening','about','aboutus', 'apply', 'join'],['indeed', 'linkedin', '@']] : rules for link scraping. Specifies which groups of keywords to determine which links to crawl and which to discard.  <br>
*linkthresolds* = [1,0] : determines how the group of keywords in linkruleset are used. 1 specifices that at least 1 keyword in the group must be in the link. 0 specifies that no keyword should be in the link. <br>
*ruleset* = [['ioinformatic', 'omputational', 'enomics', 'enetic', 'olecular', ' cell ', ' Cell ', 'iology', 'machine learning', 'Machine Learning', 'iostatistic', ' AI ', ' ML ', 'ellular'],['March','April','May','June'],['2024', 'Professor']] : rules for text scraping. Specifies which groups of keywords to determine which text to scrape and which to discard.<br>
*thresholds* = [1,1,0] : determines how the group of keywords in ruleset are used. 1 specifices that at least 1 keyword in the group must be in the text. 0 specifies that no keyword should be in the text. <br>
*removeExternalLinks* = 0 : removes external links <br>
*scraperStance* = 0 : ordinary operation. 1: low profile mode. Better at retrieving web info but may take more time  <br>
*headless* = True : Set to False for slightly better scraping efficiency with a visible browser popup. 

#####  Operation

The tool consists of two parts. A webscraper and a Haystack based AI module requiring an OpenAI key set as an environmental variable. The webscraper obtains text based on the websites specified in the EntriesInput file and the rules specified in ruleset and linkruleset. Based upon parameter settings the text is processed into a vector representation than relevant portions are retrieved and processed by the LLM. 



#####  Differences between previous versions

The previous version of this tool utilized llama-cpp or alternatively Gemini to analyze text through looping summaries. The current version uses haystack, vectorization, and targeted retrieval to process information much more quickly. 




#### Installation 


NOTE: Requires Sentence Transformers which can take up a fair amount of space. Be sure to have at least 7GB of free space if installing through venv. 


**Installation (Linux)** <br>

Download and extract directory. <br>

Navigate to directory. <br>

Create a 'datafiles' and 'userprofile' folder in the directory. <br>

Install virtualenv if not yet installed. <br>

*pip install virtualenv* in terminal <br>

Set the *ragureqs_linux.sh* installation file to be executable in its properties. <br>

Run *ragureqs_linux.sh* in the terminal to install the requirements. <br>

If unable to use sh files. Run the lines within manually in the terminal in the correct directory. <br>

Set the OPENAI_API_KEY environment variable in your .bashrc file adding the line: export OPENAI_API_KEY = valid OpenAI key (Ensure that your quota will be sufficient for use)


**Installation (Windows)**

NOTE: May need to set execution policy to allow script running through set-executionpolicy remotesigned as administrator <br>

NOTE: May need to install Microsoft C++ Build Tools for llama-cpp integration (Desktop development with C++) <br>


Open Powershell <br>

Navigate to directory. <br>

Create a 'datafiles' and 'userprofile' folder in the directory. <br>

Install python if it is not already installed. <br>


Create the venv folder: python -m venv venv <br>

Activate the environment: venv\Scripts\activate <br>

Install requirements: pip install -r requirements.txt <br>

Install the browser driver: patchright install chromium <br>

Set environmental variable OPENAI_API_KEY to a valid OpenAI key (Ensure that your quota will be sufficient for use)<br>


#### Usage 

**Usage (Linux)** <br>

Set *question* to the instructions you wish to give to the model in *main.py*. <br>

List websites to crawl in the *EntriesInput* file in the format "ht<span>tps://wwww.website.topleveldomain" <br>

For best results ensure past files in the *datafiles* folder and past responseSummary files are cleared. <br>

The tool currently is primarily designed around pulling and analyzing data from websites. But additional text files can be added to analyze with the proper settings in the *datafiles* folder. <br>

Activate environment <br>

*source venv/bin/activate* <br>

Run the program. <br>

*./python main.py* <br>

Results are output to *responsesSummary*. <br>




**Usage (Windows)** <br> 

Open Powershell <br>

Navigate to directory in Powershell. <br>

For best results ensure past files in the *datafiles* folder and past responseSummary files are cleared. <br>

The tool currently is primarily designed around pulling and analyzing data from websites. But additional text files can be added to analyze with the proper settings in the *datafiles* folder. <br>

Set *question* to the instructions you wish to give to the model in *main.py*. <br>

List websites to crawl in the *EntriesInput* file in the format "ht<span>tps://wwww.website.topleveldomain" <br>

Activate the environment venv\Scripts\activate <br>

Run the program python main.py <br>



#### Example Use Cases


**Search list of websites for List the job postings related to bioinformatics, computational biology, software development, data science, molecular biology, cell biology, genetics, and genomics**

Run with default configuration with the sample EntriesInput file. NOTE: A couple of the sites on the sample list cannot be read by the scraper and are simply included as an example. 


**Search UCSD Recruit for nonprofessorial listings for bioinformatics, molecular biology, and computational science related jobs posted on or after March 2025 as of May 2025**

Put ``https://apol-recruit.ucsd.edu/apply`` as the sole address in EntriesInput. <br>
Change the default configuration in the following manner:  <br>
*question*= 'List the nonprofessorial job postings that are bioinformatics, molecular biology, and computational science related'<br>
*mergeddocuments*: = 1 <br>
ruleset = [['ioinformatic', 'omputational', 'enomics', 'enetic', 'olecular', ' cell ', ' Cell ', 'iology', 'machine learning', 'Machine Learning', 'iostatistic', ' AI ', 'ellular'],['March','April','May'],['rofessor','2024']] <br>
thresholds = [1,1,0] <br>

run the program <br>





