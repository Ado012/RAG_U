import re
import sys
import os
#from playwright.sync_api import sync_playwright, Error

#low profile playwright varient
from patchright.sync_api import sync_playwright, Error

def DeDuplicate(data_list):

    seen = set()
    result = []

    for entry in data_list:
        is_duplicate = False
        for existing_entry in seen: #checks each entry that has been encountered before.
            if entry in existing_entry: #Detects if entry is identical or contained within existing entry. If encountered. Mark for Removal
                is_duplicate = True
                break
        if not is_duplicate:
            result.append(entry)
            seen.add(entry)

    # Now, we need to iterate through the 'result' and remove any entrys
    # that are fully contained within a later entry in 'result'.
    finalResult = []
    indices_to_remove = set()

    for i in range(len(result)): #second pass if longer strings come after the shorter ones contained within
        for j in range(len(result)):
            if i != j and i not in indices_to_remove and j not in indices_to_remove: #exceptions to removal marking
                if result[i] in result[j]: #if a duplicate is deteced
                    indices_to_remove.add(i)

    for i, entry in enumerate(result): #make final entry list
        if i not in indices_to_remove:
            finalResult.append(entry)

    return finalResult

def ScrapeText(url, selector, scraperStance):
  #current_dir = os.getcwd()  # fetch data files
  #subfolder_path = os.path.join(current_dir, "userprofile")

  try:
    with sync_playwright() as p:

      if (scraperStance == 0):
        browser = p.chromium.launch() #choose browser
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

      #page = context.new_page() #create page

      else:
        context = p.chromium.launch_persistent_context(
        user_data_dir="userprofile",
        channel="chromium",
        headless=True,
        no_viewport=True,
        # no custom headers or agents
        )

      page = context.new_page()



      #page = browser.new_page()

      page.goto(url) #go to url
      #page.wait_for_selector(selector) #wait for texts to appear
      #all_visible_text = page.locator("*:visible").all_inner_texts()
      page.wait_for_load_state("networkidle")
      texts = page.locator("p, h1, h2, h3, h4, h5, li, td, strong").all_text_contents() #scrape
      #texts=list(dict.fromkeys(texts)) #remove duplicates. If python 3.7 order preserved. Otherwise might noeed to look into alt solution.
      texts = DeDuplicate(texts) #remove duplicate entries. Including ones contained in other entries
      #browser.close()
      context.close()
      textsCombined = ' '.join(texts) #problem with repeated entries completely contained in others
      return textsCombined
  except Exception as e:
    print(f"An Error occurred: {e}")
    return "ERROR"





def FilterLinks(url, hrefs, linkruleset, linkthresholds, removeExternalLinks):
    hrefs = list(set(hrefs))  # remove duplicates

    if len(linkruleset) > 0:  # Apply link rulesets if available.
        optimizedhrefs = []
        result = 1
        for entry in hrefs:
            # Check if any of the substrings are in the text
            i = 0
            result = 1

            for rule in linkruleset:  # filter scraped text based on rules
                result = FilterRules(entry, rule, linkthresholds[i])
                i = i + 1

                if result == 0:  # if it fails a filter lose the link
                    break

            if result == 1:
                optimizedhrefs.append(entry)

        optimizedhrefs.append(url)
        hrefs = optimizedhrefs

    # remove external links from url scrape if applicable

    if removeExternalLinks == 1:
        urlparts = url.split(".")
        urlName = urlparts[1]

        for entry in hrefs:
            if urlName in entry:
                optimizedhrefs.append(entry)
        hrefs = optimizedhrefs

    return hrefs

from urllib.parse import urljoin

def GetLinks(url, linkdepth, linkruleset, linkthresholds, removeExternalLinks, scraperStance):
    extra_headers = {
        'sec-ch-ua': '\'Not A(Brand\';v=\'99\', \'Google Chrome\';v=\'121\', \'Chromium\';v=\'121\'',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'accept-Language': 'en-US,en;q=0.9'
    }



    #current_dir = os.getcwd()  # fetch data files
    #subfolder_path = os.path.join(current_dir, "userprofile")


    try:
        with sync_playwright() as p:

            if scraperStance == 0:
                browser = p.chromium.launch()
                # intercept the request headers in the browser context
                context = browser.new_context(extra_http_headers=extra_headers)

            else:
                context = p.chromium.launch_persistent_context(
                user_data_dir="userprofile",
                channel="chromium",
                headless=True,
                no_viewport=True,
                # no custom headers or agents
            )

            page = context.new_page()



            page.goto(url)
            links = page.locator("a").all()
            hrefs = []
            for link in links:
                href = link.get_attribute("href")
                if href:
                    absolute_href = urljoin(url, href)  # handles relative and absolute links.
                    hrefs.append(absolute_href)

            hrefs = FilterLinks(url, hrefs, linkruleset, linkthresholds, removeExternalLinks)  # filter links

            links = []  # links was being continously overwritten in earlier bug
            hrefs2 = []

            i = 1

            while i < linkdepth: #crawl links to get additional links according to linkdepth
                for j in hrefs:
                    page.goto(j) #previous bug using hrefs[j] caused skip
                    page.wait_for_load_state("networkidle")
                    linksInPage = page.locator("a").all()
                    for link in linksInPage:
                        href = link.get_attribute("href")
                        if href:
                            absolute_href = urljoin(url, href)  # handles relative and absolute links.
                            hrefs2.append(absolute_href)


                hrefs3 = FilterLinks(url, hrefs2, linkruleset, linkthresholds, removeExternalLinks) #filter links, do additional cycles waste time going thru previous links?
                hrefs.extend(hrefs3)
                i = i + 1

                #hrefs replaced with hrefs3 because it gets more links for some reason. Look into this.
            hrefs = list(set(hrefs))  # remove duplicates
            #browser.close()
            context.close()
            return hrefs
    except Exception as e:
        print(f"An error occurred: {e}")
        return url




def CleanText(scrapedtext):
    # strip out non latin characters
    scrapedtext = re.sub(u'[^\\x00-\\x7F\\x80-\\xFF\\u0100-\\u017F\\u0180-\\u024F\\u1E00-\\u1EFF]', u'', scrapedtext)
    # strip out empty lines
    scrapedtext = scrapedtext.splitlines(True)
    scrapedtext = [string.strip() for string in scrapedtext if string.strip()]

    scrapedtext2 = ""  # rejoin strings into output string

    for line in scrapedtext:
        scrapedtext2 = scrapedtext2 + line + "\n"

    if (scrapedtext2 == ""):
        scrapedtext2: "website cannot be opened"

    words = scrapedtext2.strip().split()  # do a word count and shorten it in case too much is being downloaded?

    wordcount = len(words)

    if wordcount > 100000:
        scrapedtext2 = words[0:100000]

    else:
        scrapedtext2 = words

    processedtext = " ".join(scrapedtext2)

    return processedtext


def WriteFile(link, cleanedtext, filenumber):

    current_dir = os.getcwd() #fetch data file
    subfolder_path = os.path.join(current_dir, "datafiles")
    filenumber =str(filenumber)

    #create unique date file name
    delimiters = r"[./]"
    linkParts = re.split(delimiters, link)
    linkParts = linkParts[2:]
    docName = ""
    docName2 = docName.join(linkParts)

    outputTitle = docName2 + "_" + filenumber + ".txt"

    cleanedtext = link + "\n" + cleanedtext

    data_path = os.path.join(subfolder_path, outputTitle)

    fileExists = os.path.isfile(data_path) #write website output file

    if (fileExists == False):

        with open(data_path, "w", encoding='utf-8') as file: #on windows writing files often defaults to cp1252 which can cause problems

            file.write(cleanedtext)

    else:
        with open(data_path, "a", encoding='utf-8') as file:

            file.write(cleanedtext)


    print(cleanedtext)




def WriteAnswers(summaryData, title):
    current_dir = os.getcwd()  # fetch data files
    summaryFile = "responsesSummary.txt"  # prepare output file

    summary_path = os.path.join(current_dir, summaryFile)

    fileExists = os.path.isfile(summary_path)  # write website output file

    if (fileExists == False):

        with open(summaryFile, "w", encoding='utf-8') as file:
            output = "<<" + title + ">>" + "\n" + summaryData + "\n"
            file.write(output)

    else:
        with open(summaryFile, "a", encoding='utf-8') as file: #omitted title for merged document but needs to include it for 0
            output = "\n" + "<<" + title + ">>" + "\n" + summaryData + "\n"
            file.write(output)




def FilterRules(text, keywords, threshold):
    found_count = 0
    result = 1
    for substring in keywords:
        if substring in text:
            found_count += 1

    if threshold == 0 and found_count > 0:
        result = 0


    if found_count < threshold:
        result = 0

    return result



def WebsiteDownloader(target, collatelinks, linkdepth, linkruleset, linkthresholds, ruleset, thresholds, removeExternalLinks, scraperStance): #download websites


    debug = {'verbose': sys.stderr}

    scrapedtext = target #link to scrape
    textarchive = []
    retrievedLinks = []


    if linkdepth == 0:
        retrievedLinks.append(target)

    if linkdepth > 0:
        retrievedLinks= GetLinks(target,linkdepth, linkruleset,linkthresholds,removeExternalLinks, scraperStance)


    print(retrievedLinks)

    filenumber = 0


    for link in retrievedLinks:

        repeatflag = 0
        badscrape = 0

        #make sure link domain is the same as target domain. Don't want to scrape from another website.
        targetparts = target.split(".")
        targetName = targetparts[1]


        #if you are in another domain. Skip to next link.
        result = targetName in link

        if (result == False):
            continue


        visible_text = ScrapeText(link, ".text", scraperStance)


        if (visible_text == "" or visible_text == "ERROR"): #tried to hanlde ScrapeText fail state. Might need to be reworked
            visible_text = "nothing scraped" #scrape additional tags if website is formatted weirdly
            print(link + " " + "Connection not successful.")
            badscrape = 1

        else:
            print(link + " " + "Connection successful.")


        relevantresult = 1 #filter scraped text based on rules

        if len(ruleset) > 0:
            i = 0

            for rule in ruleset: #filter scraped text based on rules
                relevantresult = FilterRules(visible_text,rule, thresholds[i])
                i = i + 1

                if relevantresult == 0:
                    break

        if relevantresult == 0: #if it fails a filter lose the link
            continue






        if len(textarchive) == 0:
            textarchive.append(visible_text)

        else:
            for line in textarchive: #remove repeat strings extracted from pages
                if visible_text == line:
                    repeatflag = 1
                    continue

        if visible_text != '' and repeatflag == 0 and badscrape == 0:
            textarchive.append(visible_text)

            if collatelinks == 0:
                cleanedtext = CleanText(visible_text)
                WriteFile(link, cleanedtext, filenumber)
                filenumber = filenumber + 1

            elif collatelinks == 1:
                scrapedtext = scrapedtext + "\n" + "<<>>" + "\n" + visible_text





    if collatelinks == 1:
        #cleantext = CleanText(scrapedtext)
        #WriteFile(target, cleantext, filenumber)
        WriteFile(target, scrapedtext, filenumber)












