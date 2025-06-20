import bs4
import os
import re
#import pandas as pd
from llama_cpp import Llama
import nltk
nltk.download('punkt')

from webcrawl import WebsiteDownloader
from webcrawl import WriteAnswers

from haystack import Document, Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.components.readers import ExtractiveReader


from haystack.components.converters import TextFileToDocument
from haystack.components.preprocessors import DocumentCleaner
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter


from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

from haystack_integrations.components.generators.llama_cpp import LlamaCppChatGenerator

#targetList = sys.argv[0] #get website list from command line input


#PARAMETERS

prompt = "Summarize the following biotech company website text: "
backgroundPrompt = "I am a website summarizer. What website text do you wish me to summarize?"

fragmentationLimit = 10
collatelinks = 1 #1: links from a website are scraped into one text file.
linkdepth = 2
mergeddocuments = 0 #1: all documents are merged together and run in the pipeline. 0: all documents are run seperately through pipeline-recommended for running through multiple websites
llmoption = 1 #1 openai remote model
linkruleset = [['job','career','recruit','opening','about','aboutus', 'apply', 'join'],['indeed', 'linkedin', '@']]
linkthresolds = [1,0]
ruleset = [['ioinformatic', 'omputational', 'enomics', 'enetic', 'olecular', ' cell ', ' Cell ', 'iology', 'machine learning', 'Machine Learning', 'iostatistic', ' AI ', ' ML ', 'ellular']]
thresholds = [1]
removeExternalLinks = 0
scraperStance = 1


#WEBSCRAPE PART


with open("EntriesInput.txt", encoding='utf-8') as f: #open up website/document list
    entriestocrawl = f.read()

entryList = entriestocrawl.splitlines() #split it into a readable format
delimiters = r"[./]"

for entry in entryList: #download list of websites
    entryParts = re.split(delimiters, entry)
    if ('com' in entryParts or 'net' in entryParts or 'edu' in entryParts or 'ai' in entryParts or 'www' in entryParts ):

        domain_values = ['com', 'net', 'edu', 'ai']

        indices = [i for i, x in enumerate(entryParts) if x in domain_values]


        WebsiteDownloader(entry, collatelinks, linkdepth, linkruleset, linkthresolds, ruleset, thresholds, removeExternalLinks, scraperStance) #download url. Will output list of files of websites or website individual paged depending on collatelinks




#RAG Part


current_dir = os.getcwd()  # fetch data files
subfolder_path = os.path.join(current_dir, "datafiles")

#construct indexing pipeline

documentpathlist = []


if (mergeddocuments == 1):
    for name in os.listdir(subfolder_path): #run summarization engine on list of output files

        nameParts = name.split(".")
        if ('txt' in nameParts or 'edu' in nameParts):

            try:
                data_path = os.path.join(subfolder_path, name)
                with open(data_path) as f:  # exception does not seen to work. Look into this later.
                    rawdata = f.read()
                    if os.stat(data_path).st_size == 0:  # if file is empty
                        continue
                    else:
                        documentpathlist.append(data_path)

            except FileNotFoundError:  # if file does not exist
                print("File not Found")
                continue



#set up document indexing pipeline
document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

pipeline = Pipeline()
pipeline.add_component("converter", TextFileToDocument())
pipeline.add_component("cleaner", DocumentCleaner())
pipeline.add_component("splitter", DocumentSplitter(split_by="sentence", split_length=10))
pipeline.add_component("docembed", SentenceTransformersDocumentEmbedder())
pipeline.add_component("writer", DocumentWriter(document_store=document_store))

pipeline.connect("converter", "cleaner")
pipeline.connect("cleaner", "splitter")
pipeline.connect("splitter", "docembed")
pipeline.connect("docembed", "writer")




num_documents = document_store.count_documents()

remoteRequest = 0 #keep track of remote requests to not time out



# chat template

template = [
    ChatMessage.from_user(
        """
Given the following information scraped from webpages, answer the question.

Context:
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: {{question}}
Answer:
"""
    )
]

prompt_builder = ChatPromptBuilder(template=template)




if llmoption == 1: #remote OPENAI generator
    chat_generator = OpenAIChatGenerator(api_key=Secret.from_env_var("OPENAI_API_KEY"), model="gpt-4o-mini")

else: #or local generator
    chat_generator = LlamaCppChatGenerator(
        model="/home/samplemodel.gguf",
        n_ctx=15000,
        n_batch=128,
        model_kwargs={"n_gpu_layers": -1},
        generation_kwargs={"max_tokens": 128, "temperature": 0.1},
    )









#set query pipeline
query_pipeline = Pipeline()
query_pipeline.add_component("text_embedder", SentenceTransformersTextEmbedder())
query_pipeline.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store))
query_pipeline.add_component("prompt_builder", prompt_builder)
query_pipeline.add_component("llm", chat_generator)

query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
query_pipeline.connect("retriever", "prompt_builder")
query_pipeline.connect("prompt_builder.prompt", "llm.messages")



#set retriever pipeline
retriever_pipeline = Pipeline()
retriever_pipeline.add_component("text_embedder", SentenceTransformersTextEmbedder())
retriever_pipeline.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store))
retriever_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")





#question = "Is this a bioinformatics or computational biology related job posting that was opened March 2025 or later and if so what is its job number?"

question = "List the job postings related to bioinformatics, computational biology, software development, data science, molecular biology, cell biology, genetics, and genomics in the text."



#run pipeline on full document list
if mergeddocuments == 1:
    pipeline.run({"converter": {"sources": documentpathlist}})
    response = query_pipeline.run({"text_embedder": {"text": question}, "prompt_builder": {"question": question}})
    print(response["llm"]["replies"][0].text)
    WriteAnswers(response["llm"]["replies"][0].text, "summary")

    # Run the pipeline
    response2 = retriever_pipeline.run({"text_embedder": {"text": question}})


    retrieved_documentsfromstore = response2["retriever"]

    iter = 0
    while (iter <= 9):
        singleresponse = response2['retriever']['documents'][iter]
        print(singleresponse.content)
        print('\n' + '\n')
        iter = iter + 1
    print("wow")
#run pipeline on individual files
else:
    for name in os.listdir(subfolder_path):  # run summarization engine on list of output files

        documentpathlist = []
        #clean out documents from last loop
        all_documents = document_store.filter_documents()
        document_ids_to_delete = [doc.id for doc in all_documents]
        document_store.delete_documents(document_ids=document_ids_to_delete)

        try:
            data_path = os.path.join(subfolder_path, name)
            with open(data_path , encoding='utf-8') as f:  # exception does not seen to work. Look into this later.
                rawdata = f.read() #length check only...doesn't actually process this scraping instance
                if os.stat(data_path).st_size == 0:  # if file is empty
                    continue
                else:
                    documentpathlist.append(data_path)
                    product = pipeline.run({"converter": {"sources": documentpathlist}})
                    response = query_pipeline.run({"text_embedder": {"text": question}, "prompt_builder": {"question": question}})
                    print(response["llm"]["replies"][0].text)
                    WriteAnswers(response["llm"]["replies"][0].text, name)

        except FileNotFoundError:  # if file does not exist
            print("File not Found")
            continue























