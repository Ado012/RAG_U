import bs4
import sys
import os
#import pandas as pd
from llama_cpp import Llama
import nltk
nltk.download('punkt')
import requests
import urllib.parse
import urllib.request as urllib2
import re
import regex
from bs4.element import Comment

import google.generativeai as genai
import time

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = bs4(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


def additional_scrapedtext(soup):

    descriptiontextcollated = ""
    ewidgetboxtextcollated = ""

    descriptionboxes = soup.find_all("meta", property="og:description")
    for description in descriptionboxes:
        text = description.get_text(strip=True, separator="\n")  # Extract text, strip whitespace, separate paragraphs
        descriptiontextcollated = descriptiontextcollated + "\n" + text  # Print or store the extracted text as needed

    eb = soup.find_all("div", class_="elementor-widget-container")
    for ewidgetbox in eb:
        text = ewidgetbox.get_text(strip=True, separator="\n")  # Extract text, strip whitespace, separate paragraphs
        ewidgetboxtextcollated = ewidgetboxtextcollated + "\n" + text  # Print or store the extracted text as needed

    additionaltext = descriptiontextcollated + "\n" + ewidgetboxtextcollated + "\n"

    return additionaltext





def crawl(pageurl, depth= 3): #gather urls from website to a certain depth


    hdr2 = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
         'Referer': 'https://cssspritegenerator.com',
         'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
         'Accept-Encoding': 'none',
         'Accept-Language': 'en-US,en;q=0.8',
         'Connection': 'keep-alive'}

    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
        "Accept-Encoding": "none",
        "Accept-Language": "en-US,en;q=0.8",
        "Connection": "keep-alive",
    }


    pages = [pageurl]
    indexed_url = [] # a list for the main and sub-HTML websites in the main website
    for i in range(depth):
        for page in pages:
            if page not in indexed_url:
                indexed_url.append(page)
                try:
                    response = requests.get(page, headers=hdr)
                    html = response.text
                except:
                    print( "Could not open %s" % page)
                    continue
                soup = bs4.BeautifulSoup(html, "html.parser")
                links = soup('a') #finding all the sub_links
                for link in links:
                    if 'href' in dict(link.attrs):
                        url = urllib.parse.urljoin(page, link['href'])
                        if url.find("'") != -1:
                                continue
                        url = url.split('#')[0]
                        if url[0:4] == 'http':
                            indexed_url.append(url)
            pages = indexed_url
    return indexed_url


def WebsiteDownloader(target, outputfile): #download websites

    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
        "Accept-Encoding": "none",
        "Accept-Language": "en-US,en;q=0.8",
        "Connection": "keep-alive",
    }

    debug = {'verbose': sys.stderr}

    scrapedtext = target
    textarchive = []


    retrievedlinks= crawl(target)
    retrievedlinks = list(set(retrievedlinks)) #remove duplicates

    print(retrievedlinks)



    for link in retrievedlinks:

        #response = requests.get(link)
        #html_content = response.content
        #soup2 = bs4.BeautifulSoup(html_content, "html.parser")

        repeatflag = 0

        #make sure link domain is the same as target domain. Don't want to scrape from another website.
        targetparts = target.split(".")
        targetName = targetparts[1]


        #if you are in another domain. Skip to next link.
        result = targetName in link

        if (result == False):
            continue

        try:
            response = requests.get(link, headers=hdr, timeout=5)
        except requests.exceptions.Timeout:
            print(link + " " +"Request timed out.")
            continue
        except requests.exceptions.ConnectionError:
            print(link + " " + "Connection closed.")
            continue

        print(link + " " + "Connection successful.")

        html = response.text

        soup = bs4.BeautifulSoup(html, "html.parser") #read in home

        [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title', 'a'])]
        visible_text = soup.getText()

        if (visible_text == ""):
            additionaltext = additional_scrapedtext(soup)
            visible_text = additionaltext #scrape additional tags if website is formatted weirdly





        if len(textarchive) == 0:
            textarchive.append(visible_text)

        else:
            for line in textarchive: #remove repeat strings extracted from pages
                if visible_text == line:
                    repeatflag = 1
                    break

        if visible_text != '' and repeatflag == 0:
            textarchive.append(visible_text)
            scrapedtext = scrapedtext + "\n" + visible_text

    #strip out non latin characters
    scrapedtext = re.sub(u'[^\\x00-\\x7F\\x80-\\xFF\\u0100-\\u017F\\u0180-\\u024F\\u1E00-\\u1EFF]', u'', scrapedtext)
    #strip out empty lines
    scrapedtext = scrapedtext.splitlines(True)
    scrapedtext = [string.strip() for string in scrapedtext if string.strip()]


    scrapedtext2 = "" #rejoin strings into output string

    for line in scrapedtext:
        scrapedtext2 = scrapedtext2 + line + "\n"



    if (scrapedtext2 == ""):
        scrapedtext2: "website cannot be opened"

    #make sure output does not exceed prompt limit.
    tokenizer = nltk.word_tokenize #nltk appears to be a generic tokenizer so it may not be the most accurate count to determine prompt limits depending on what model is used but is still better than nothing for now.
    tokenizedtext = tokenizer(scrapedtext2)
    tokensInOutput = len(tokenizer(scrapedtext2))

    if (tokensInOutput > 300000): #token limit is set to prevent too much downloading. May remove later
        scrapedtext2 = " ".join(tokenizedtext[:300000])

    current_dir = os.getcwd() #fetch data file
    subfolder_path = os.path.join(current_dir, "datafiles")

    data_path = os.path.join(subfolder_path, outputfile)

    fileExists = os.path.isfile(data_path) #write website output file

    if (fileExists == False):

        with open(data_path, "w") as file:

            file.write(scrapedtext2)

    else:
        with open(data_path, "a") as file:

            file.write(scrapedtext2)


    print(scrapedtext2)

def DocumentReader(datafile, outputfile): #read in html files and convert them to text
    # Load the HTML file
    file = open(datafile, "r")

    lines = file.readlines()
    with  open("datafile") as file:
        soup = bs4.BeautifulSoup(file, 'html.parser') #for some idiotic reason you have to open and load the file in this specific way for beautiful shit.

    all_text = ""
    paragraphs = soup.find_all("p")
    for paragraph in paragraphs:
        all_text += paragraph.get_text().strip() + " "

    current_dir = os.getcwd()
    subfolder_path = os.path.join(current_dir, "datafiles")

    data_path = os.path.join(subfolder_path, outputfile)

    fileExists = os.path.isfile(data_path)

    if (fileExists == False):

        with open(data_path, "w") as file:

            file.write(all_text)

    else:
        with open(data_path, "a") as file:

            file.write(all_text)


    print(all_text)



def DataChecker(data): #checks before preparing data for LLM

    skipSummary = 0

    #current_dir = os.getcwd()
    #subfolder_path = os.path.join(current_dir, "datafiles")

    #data_path = os.path.join(subfolder_path, data)


    try:
        with open(data) as f:  # exception does not seen to work. Look into this later.
            rawdata = f.read()
            if os.stat(data).st_size == 0:  # if file is empty
                skipSummary = 1
    except FileNotFoundError: #if file does not exist
        print("File not Found")
        skipSummary = 1

    skipSummaryStr = str(skipSummary)
    print(data+" "+skipSummaryStr)

    return skipSummary #returns value stating if data is good or not






def DataChunker(data, prompt, chunkSize, llm): # prepares data to feed into LLM in managable chunks

    textandpromptList = []
    skipChunking = 0

    #current_dir = os.getcwd()
    #subfolder_path = os.path.join(current_dir, "datafiles")

    #data_path = os.path.join(subfolder_path, data)

    #fileExists = os.path.isfile(data)  # write website output file

    #make sure output does not exceed prompt limit.
    # tokenizer = nltk.word_tokenize #nltk appears to be a generic tokenizer so it may not be the most accurate count to determine prompt limits depending on what model is used but is still better than nothing for now.
    # tokenizedtext = tokenizer(data)
    # tokensInOutput = len(tokenizer(data))

    #proper tokenization directly using the model.
    bytedata = data.encode('utf-8')
    tokenizedtext = llm.tokenize(bytedata)
    tokensInOutput = len(tokenizedtext)


    #iterate through website output in chunks
    beginPart = 0
    endPart = chunkSize
    leaveTextPartitioningLoop = 0

    while (beginPart <= tokensInOutput):

        if (endPart > tokensInOutput):
            endPart = tokensInOutput
            leaveTextPartitioningLoop = 1

        #take a chunk of the input based on specified size and reconvert back to a string
        tokenizedTextPartList = tokenizedtext[beginPart:endPart]
        byteTextPartList = llm.detokenize(tokenizedTextPartList)
        textPartList = byteTextPartList.decode('utf-8')
        textPart = "".join(textPartList)

        # print("data"+'\n')
        # print(data + '\n')
        # print("processeddata" + '\n')
        # print(textPart + '\n')

        #combine with prompt
        textandprompt = prompt + textPart

        textandpromptList.append(textandprompt)

        beginPart = beginPart + chunkSize
        endPart = endPart + chunkSize

        if leaveTextPartitioningLoop == 1:
            break

    return textandpromptList




def Summarizer(textandpromptChunk, summaryFile, llm, backgroundPrompt, summarizationEngine): #Use LLM to summarize data from website


    if summarizationEngine == "local":
        messages = [
            {"role": "system",
             "content": backgroundPrompt},
            {"role": "user", "content": textandpromptChunk},
        ]

        response = llm.create_chat_completion(messages=messages)


        responsetext = response['choices'][0]['message']['content']

    elif summarizationEngine == "remote":
        responsetext = model.generate_content(textandpromptChunk)


    return responsetext





def RemotePause(remoteRequest, remoteQuota): #Use LLM to summarize data from website

    if summarizationEngine == "remote":  # remote llms sometimes impose limits on requests per minute
        remoteRequest = remoteRequest + 1
        if remoteRequest >= remoteQuota:
            time.sleep(60)
            remoteRequest = 0

    return remoteRequest




#targetList = sys.argv[0] #get website list from command line input


prompt = "Summarize the following biotech company website text: "
backgroundPrompt = "I am a website summarizer. What website text do you wish me to summarize?"
modelpathParam = "/home/sampleuser/modelfile/llama-3.1-8b-instruct.Q4_K.gguf"
chatformatParam = "llama-3"
summarizationEngine = "local"
chunkSize = 5000
remoteQuota = 10
fragmentationLimit = 10




with open("EntriesInput.txt") as f: #open up website/document list
    entriestocrawl = f.read()

entryList = entriestocrawl.splitlines() #split it into a readable format

#set up llm
llm = Llama(
      model_path= modelpathParam,
      chat_format= chatformatParam,
      n_gpu_layers=-1, # Uncomment to use GPU acceleration
      n_ctx=15000  # Uncomment to increase the context window
)

if summarizationEngine == "remote": #load up remote llm if necessary
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')


summaryFile = "summarizedWebsites.txt" #prepare output file



for entry in entryList: #download list of websites
    entryParts = entry.split(".")
    if ('com' in entryParts or 'edu' in entryParts or 'net' in entryParts or 'www' in entryParts ):
        
        domain_values = ['com', 'net', 'edu']

        indices = [i for i, x in enumerate(entryParts) if x in domain_values]
 
        entryFile = entryParts[1] + ".txt"
        targetFolder = "www." + entryParts[1] + "." + entryParts[indices[0]]
        
        
        WebsiteDownloader(entry, entryFile) #download url



current_dir = os.getcwd()  # fetch data files
subfolder_path = os.path.join(current_dir, "datafiles")


remoteRequest = 0 #keep track of remote requests to not time out

for name in os.listdir(subfolder_path): #run summarization engine on list of output files

    entryfilepath = os.path.join(subfolder_path, name)
    root_ext = os.path.splitext(name)
    extensionname = root_ext[1]
    extensionname = extensionname[1:]
    entryResultsFile = root_ext[0] + extensionname + ".txt" #creates file name to hold results of summarization of the file.

    dataExists = DataChecker(entryfilepath) #check if input data is good
    summaryData = []

    if (dataExists==0): #if it is, read it

        with open(entryfilepath) as f:
            try:
                rawdata = f.read()
            except FileNotFoundError:
                output = "File not Found"
                skipChunking = 1

        entryDataList=DataChunker(rawdata, prompt, chunkSize, llm) #chunk data into portions the system can handle
        entryDataList2 = []
        for entryData in entryDataList: #run summarizer on chunked datafile
            summarizedChunk = Summarizer(entryData, entryResultsFile, llm, backgroundPrompt, summarizationEngine) #run summary
            entryDataList2.append(summarizedChunk)
            remoteRequest = (remoteRequest, remoteQuota)

            #condense summary so model can take all of website into account.
            summaryChunks = len(entryDataList2)
            summaryData = ' '.join(entryDataList2)
            while summaryChunks > fragmentationLimit: #condense summary until it reaches a defined number of chunks
                entryDataList = DataChunker(summaryData, prompt, chunkSize, llm)

                for entryData in entryDataList: #resummarize chunked datalist
                    summarizedChunk = Summarizer(entryData, entryResultsFile, llm, backgroundPrompt, summarizationEngine)
                    entryDataList2.append(summarizedChunk)

                    remoteRequest = (remoteRequest,remoteQuota)
                summaryChunks = len(entryDataList2) #measure fragmentation
                summaryData = ' '.join(entryDataList2)


    #write summary file for website or datafile
    fileExists = os.path.isfile(entryResultsFile)

    if (fileExists == False):

        with open(entryResultsFile, "w") as file:
            output = "<<" + ">>" + "\n" + summaryData + "\n"
            file.write(output)

    else:
        with open(entryResultsFile, "a") as file:
            output = "\n" + "<<" + ">>" + "\n" + summaryData + "\n"
            file.write(output)


    current_path = os.path.join(current_dir, entryResultsFile) #move summarized file to summarized folder
    subfolder_path = os.path.join(current_dir, "summarizedfiles")
    subfolder_path_destination = os.path.join(subfolder_path, entryResultsFile)

    os.rename(current_path, subfolder_path_destination)

    current_dir = os.getcwd()  # fetch data files
    subfolder_path = os.path.join(current_dir, "datafiles")



current_dir = os.getcwd()  # fetch data files

#current_path = os.path.join(current_dir, entryResultsFile) #move summarized file to summarized folder
subfolder_path = os.path.join(current_dir, "summarizedfiles")


for name in os.listdir(subfolder_path): #write all entry files to a summary file
    fileExists = os.path.isfile(summaryFile)
    data_path = os.path.join(subfolder_path,name)

    root_ext = os.path.splitext(name)
    entryFileName = root_ext[0] + root_ext[1]

    with open(data_path) as f:  # open up website/document list
        summarizedtext = f.read()


    entryfilepath = os.path.join(subfolder_path, name)


    if (fileExists == False): #write entry into final summary file

        with open(summaryFile, "w") as file:
            output = entryFileName + "\n" + summarizedtext + "\n"
            file.write(output)

    else:
        with open(summaryFile, "a") as file:
            output = entryFileName + "\n" + summarizedtext + "\n"
            file.write(output)





