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

        response = requests.get(link, headers=hdr)
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

    if (tokensInOutput > 30000): #token limit is set below mistralite's inherent limit for safety buffer.
        scrapedtext2 = " ".join(tokenizedtext[:30000])



    fileExists = os.path.isfile(outputfile) #write website output file

    if (fileExists == False):

        with open(outputfile, "w") as file:

            file.write(scrapedtext2)

    else:
        with open(outputfile, "a") as file:

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

    fileExists = os.path.isfile()

    if (fileExists == False):

        with open(outputfile, "w") as file:

            file.write(all_text)

    else:
        with open(outputfile, "a") as file:

            file.write(all_text)


    print(all_text)


def Summarizer(data, targetName, summaryFile, llm): #Use LLM to summarize data from website

    skipSummary = 0 #flag to see if website file exists

    with open(data) as f:
        try:
            rawdata = f.read()
        except FileNotFoundError:
            output = "File not Found"
            skipSummary = 1

    if skipSummary == 0:
        #make sure output does not exceed prompt limit.
        tokenizer = nltk.word_tokenize #nltk appears to be a generic tokenizer so it may not be the most accurate count to determine prompt limits depending on what model is used but is still better than nothing for now.
        tokenizedtext = tokenizer(rawdata)
        tokensInOutput = len(tokenizer(rawdata))

        #iterate through website output in chunks
        beginPart = 0
        endPart = 5000
        leaveTextPartitioningLoop = 0

        while (beginPart <= tokensInOutput):

            if (endPart > tokensInOutput):
                endPart = tokensInOutput
                leaveTextPartitioningLoop = 1

            #summarize chunk
            textPart = " ".join(tokenizedtext[beginPart:endPart])
            textandprompt = "Summarize the following biotech company website text: " + textPart

            messages = [
                {"role": "system",
                 "content": "I am a website summarizer. What website text do you wish me to summarize?"},
                {"role": "user", "content": textandprompt},
            ]

            response = llm.create_chat_completion(messages=messages)

            responsetext = response['choices'][0]['message']['content']

            print(responsetext)

            #write to file
            fileExists = os.path.isfile(summaryFile)

            if (fileExists == False):

                with open(summaryFile, "w") as file:
                    output = targetName + "\n" + responsetext + "\n"
                    file.write(output)

            else:
                with open(summaryFile, "a") as file:
                    output = "\n" + targetName + "\n" + responsetext + "\n"
                    file.write(output)

            if leaveTextPartitioningLoop == 1:
                break

            beginPart = beginPart + 5000
            endPart = endPart + 5000

    if skipSummary == 1:
        with open(summaryFile, "w") as file:
            output = targetName + "\n" + output + "\n"
            file.write(output)







#targetList = sys.argv[0] #get website list from command line input



with open("URLinput.txt") as f:
    websitestocrawl = f.read()

targetList = websitestocrawl.splitlines()


llm = Llama(
      model_path="/home/llama.cpp/models/MistralLite/mistrallite.Q6_K.gguf",
      chat_format="mistrallite",
      n_gpu_layers=-1, # Uncomment to use GPU acceleration
      n_ctx=31000  # Uncomment to increase the context window
)

summaryFile = "summarizedWebsites.txt"


for targetURL in targetList:
    if (('www.' in  targetURL) == False):
        targetURL = targetURL[:8] + 'www.' + targetURL[8:]
    targetURLparts = targetURL.split(".")
    targetName = targetURLparts[1]
    outputFile = targetName + ".txt"
    #targetFolder = targetName + ".com"
    WebsiteDownloader(targetURL, outputFile) #download url


    #fileList = os.listdir(targetFolder)
for targetURL in targetList:
    if (('www.' in targetURL) == False):
        targetURL = targetURL[:8] + 'www.' + targetURL[8:]
    targetURLparts = targetURL.split(".")
    targetName = targetURLparts[1]
    outputFile = targetName + ".txt"
    Summarizer(outputFile, targetName, summaryFile, llm)








