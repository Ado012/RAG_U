Retrival Augmented Generation for U, RAG-U is a tool that enables automated batch retrival augmented generation (RAG), information distillation, and analysis based on a user specified list of websites and/or text files through LLMs driven by the llama.cpp interface. Put simply you can 'ask' any question about a given list of websites/or files and the LLM will loop through each one and attempt to answer the question. For example a query of 'are there any jobs available?' with a list of company websites should output an answer for each website.  WARNING: the tool is currently in early development and may not work correctly if set up improperly. The tool also requires lots of VRAM in order to work in a reasonable amount of time. Current parameters are set for 8GB VRAM which takes about 5 minutes or more per entry. Larger amounts of VRAM should reduce this time due to being able to process more text at once. In addition to the option to use a local LLM there is a currently untested option to use Google Gemini with a valid API key. 


Parameters

prompt = Specifies the request for the LLM to perform upon the data. ex: "Summarize the following biotech company website text: "
modelpathParam = Specifies the location of the LLM model file ex: "/home/sampleuser/modelfile/llama-3.1-8b-instruct.Q4_K.gguf"
chatformatParam = llm format ex: "llama-3"
summarizationEngine = "local" to use llama.cpp local LLM files. "remote" to use Google Gemini (untested)
chunkSize = tokens to process at a time. Larger values will allow more text to be processed and may speed the run time up significantly. However the number may need to be adjusted to fit into the amount of VRAM available as well as the models preexisting context window. Ex. 5000
remoteQuota = the amount of requests to make before the tool pauses due to API limits when using a remote LLM like Google Gemini ex. 10
fragmentationLimit = Controls how 'fragmented' a RAG/LLM answer can be. In other words how much of the base data the LLM takes into account when making its generation. For example with a very high fragmentationLimit and with a very lengthy datafile the tool is more likely to simply process as much data as is specified to take at a time and make a list of RAGs of the different parts of the file without any context from each other. On the other hand with a fragmentationLimit of 1 the tool will attempt to continuously resummarize the data until it completely fits into one processing cycle making a RAG that takes into account the whole datafile. Lower fragmentationLimits consquently can take much more time. ex 10
n_gpu_layers= specifies layers to be offloaded to the GPU ex. -1 (All)
n_ctx= context window for model. Along with chunk size can be increased to increase the amount of data the tool can process at a time potentially speeding things up or decreased to fit within available VRAM and the model's inherent capabilities'. ex. 15000


