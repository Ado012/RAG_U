Retrival Augmented Generation for U, RAG-U is a simple LLM agent / tool that enables automated batch retrival augmented generation (RAG), information distillation, and analysis based on a user specified list of websites and/or text files through local LLMs driven by the llama.cpp interface. Put simply you can 'ask' any question about a given list of websites/or files and the LLM will loop through each one and attempt to answer the question. For example a query of 'are there any jobs available?' with a list of company websites should output an answer for each website.  WARNING: the tool is currently in early development and may not work correctly if set up improperly. The tool also requires lots of VRAM in order to work in a reasonable amount of time. Current parameters are set for 8GB VRAM which takes about 5 minutes or more per entry. Larger amounts of VRAM should reduce this time due to being able to process more text at once. In addition to the option to use a local LLM there is a currently untested option to use Google Gemini with a valid API key. 


#####  Parameters

*prompt* = Specifies the request for the LLM to perform upon the data. ex: "Summarize the following biotech company website text: "<br>
*modelpathParam* = Specifies the location of the LLM model file ex: "/home/sampleuser/modelfile/llama-3.1-8b-instruct.Q4_K.gguf"<br>
*chatformatParam* = llm format ex: "llama-3"<br>
*summarizationEngine* = "local" to use llama.cpp local LLM files. "remote" to use Google Gemini (untested)<br>
*chunkSize* = tokens to process at a time. Larger values will allow more text to be processed and may speed the run time up significantly. However the number may need to be adjusted to fit into the amount of VRAM available as well as the models preexisting context window. Ex. 5000<br>
*remoteQuota* = the amount of requests to make before the tool pauses due to API limits when using a remote LLM like Google Gemini ex. 10<br>
*fragmentationLimit* = Controls how 'fragmented' a RAG/LLM answer can be. In other words how much of the base data the LLM takes into account when making its generation. For example with a very high fragmentationLimit and with a very lengthy datafile the tool is more likely to simply process as much data as is specified to take at a time and make a list of RAGs of the different parts of the file without any context from each other. On the other hand with a fragmentationLimit of 1 the tool will attempt to continuously resummarize the data until it completely fits into one processing cycle making a RAG that takes into account the whole datafile. Lower fragmentationLimits consquently can take much more time. ex 10<br>
*n_gpu_layers*= specifies layers to be offloaded to the GPU ex. -1 (All)<br>
*n_ctx*= context window for model. Along with chunk size can be increased to increase the amount of data the tool can process at a time potentially speeding things up or decreased to fit within available VRAM and the model's inherent capabilities'. ex. 15000<br>


#### Installation

Installation (Linux) <br>

Download and extract directory. <br>

Navigate to directory. <br>

Create a 'datafiles' and 'summarizedfiles' folder in the directory. <br>

Install virtualenv if not yet installed. <br>

*pip install virtualenv* <br>

Create environment folder <br>

*python -m venv venv* <br>



Activate environment <br>


*source venv/bin/activate* <br>


Install requirements <br>

*pip install -r requirements.txt* <br>


Download model: Any llama.cpp compatible model may work with modification but the script is currently set for llama-3.1-8b-instruct.Q4_K.gguf <br>


Set *n_gpu_layers*, *chunkSize*, and *n_ctx* in the script to accomodate the available memory and context window of the model. Currently set for a 8GB nvidia gpu. <br>

Set *modelpathParam* to the path the model is located in. <br>

#### Usage

Set prompt to the instructions you wish to give to the model. <br>

List websites to crawl in the *EntriesInput* file in the format "ht<span>tps://wwww.website.topleveldomain" <br>

Put datafiles to summarize in the *datafiles* folder. <br>

Run the program. <br>

*./python main.py* <br>

Results are output to *summerizedfiles*. <br>
