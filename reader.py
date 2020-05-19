__author__ = 'Dasha'
from tika import parser
import re

'''
    distill_file is the main function. Call it from CMD (windows) with: 
    python -c "import reader; reader.distill_file('du_bois_off_print.pdf', 'Synthese')" 
    It should work on a Mac terminal too, just replace double quotes with single quotes. 

    Requires Java install and Java in PATH variable.
'''


def distill_file(fileName, journalName):
    """
      This function opens the specified pdf file and prints (to the console) the distilled version of
      the text, i.e., without the superfluous information at the top and bottom of pages, without
      citations, without the content before the abstract, and without references. The output text
      can then be read with the audio reader of your choice, e.g. Word.
      Parameters:
        fileName (string): name of the pdf file to distill
            (e.g., "du_bois_democratic_defence_of_the_value_free_ideal_off_print.pdf").
        journalName (string): name of the article's journal name (e.g., "Synthese").
    """

    #Words that, if they fully make up a line, indicate the line has no content and should be skipped
    stopwords = {"author", "author's", "personal", "copy", "copyright", "page", "of"}
    stopwords.add(journalName.lower())

    #TODO: Currently there's unicode encoding issues so I'm just printing to the console,
    # but in the future it would be good to print to a file instead.
    #outputFileName = fileName[:-4] + "_distilled.txt"
    #f = open(outputFileName, 'w')
    outputText = ""

    # Get raw data using tika parser. 'raw' contains a dictionary with the content (text)
    #   and the metadata (info like author name, year, etc.)
    raw = parser.from_file(fileName)
    fileContents = "" + raw['content']
    metadata = raw['metadata']

    #TODO: not every paper has this metadata. May have to extract author and title data another way.
    if "meta:author" in metadata.keys():
        author = metadata["meta:author"]
        authorNames = author.split()
        for name in authorNames:
            stopwords.add(name.lower())

    if "dc:title" in metadata.keys():
        title = metadata["dc:title"]
        titleWords = title.split()
        for titleWord in titleWords:
            stopwords.add(titleWord.lower())
        #Document starts with title and author name, strips everything before abstract
        print(title + "\n by " + author + "\n")

    lineNum = 0

    #Keep track of whether there's been "abstract" or "introduction". Only start collecting text after that.
    abstractFound = False
    #Flag when multiple new lines are encountered, indicating a new page or other unnecessary whitespace
    multipleNewLines = False
    loopCount = 0

    while not abstractFound:
        #If we went through the doc already and found no abstract, this message gets printed
        if loopCount > 0:
            print("Warning: This article has no abstract or introduction.")
            abstractFound = True

        for line in fileContents.splitlines():
            lowercaseLine = line.lower()
            #line = line.decode("utf-8")
            # Ignore everything until keyword 'Abstract' or 'Introduction'
            if not abstractFound:
                if lowercaseLine.startswith("abstract") or lowercaseLine.startswith("introduction"):
                    abstractFound = True
                else:
                    continue

            #Once we hit reference, we're done.
            if lowercaseLine.startswith("references") and len(line) < 12:
                break

            #Handles different scenarios with superfluous white space at the bottom of pages
            if len(line) < 1 or line.isspace():
                #Asterisk is a flag indicating a white space line. Seeing another whitespace line means
                #the previous whitespace line should be stripped instead of kept as a newline.
                if outputText[len(outputText)-1] == '*':
                    outputText = outputText[:-1]
                    multipleNewLines = True
                #If there's no asterisk flag and no previous newline, append a newline and mark that we've
                #   seen a white space line.
                elif not multipleNewLines and outputText[len(outputText)-1] != '\n':
                    outputText += '\n'
                    multipleNewLines = True
                #If we've seen a whitespace line already and we've appended a newline, that means
                #   it was appended by mistake, so the previous whitespace line should be stripped
                elif multipleNewLines and outputText[len(outputText)-1] == '\n' \
                        and not outputText.rstrip().endswith('.'):
                    outputText = outputText[:-1]
                continue
            else:
                multipleNewLines = False

            #Call helper function to ignore garbage and clean up lines
            line = cleanUp(line, stopwords)
            outputText += line
        loopCount += 1

    #Get rid of citations in final result (it's easier to do this at the end because
    #   sometimes citations span multiple lines)
    outputText = stripParentheticalCitations(outputText)
    print(outputText)

    #f.write(outputText)


#TODO how does this handle latex pdfs?
#TODO why do some words get glued together - is it the Tika parser or something I'm doing?


def cleanUp(line, stopwords):
    """
      This function determines if the given line has content worth keeping.
      Parameters:
      line (string): a line of the document
      stopwords (set): a set of garbage words indicating that a line has no content

      Returns:
          If the line has no content, returns '*' flag for parent function to handle.
          Otherwise, returns the line with the relevant white space added.
    """

    #Lines with urls are typically garbage and should be ignored
    if containsURL(line):
        return '*'

    #Get the words in the line of the pdf. rstrip and lstrip remove whitespace at front and back.
    wordsInLine = line.lstrip().rstrip().split()

    #Lines starting with numbers or stopwords are suspect, but check that they have no content before discarding
    if line[0].isdigit() or wordsInLine[0].lower() in stopwords:
        hasContent = False
        for word in wordsInLine:
            #If there's a contentful word, err on the side of safety and keep the line
            if word.lower() not in stopwords and word.isalpha():
                hasContent = True
                break
        #Otherwise, ignore the line
        if not hasContent:
            return '*'

    #TODO deal with footnotes?

    #Lines ending with dashes are usually individual words split up over multiple lines, so remove the dash
    if line.endswith('-'):
        return line[:-1]
    else:
        return line + ' '


def containsURL(line):
    """
          This helper function determines if the given line contains a URL
          Parameters:
          line (string): a line of the document

          Returns:
              True if there is a URL, false otherwise
        """

    #urlRegex = "https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
    urlRegex = "https?:\/\/.*\s*"
    return len(re.sub(urlRegex, "", line)) < len(line)


#TODO make this journal-specific.
def stripParentheticalCitations(line):
    """
          This helper function gets rid of parenthetical citations. e.g.,
              In Bright (2004), he argues...               ->  In Bright, he argues...
              In Bright (2004) (and others), he argues...  ->  In Bright (and others), he argues...
              Such and such (Bright, 2004).                ->  Such and such.
              Such and such (Bright, 2004, p. 25-26).      ->  Such and such.

          Parameters:
          line (string): a line of the document

          Returns:
              The line stripped of parenthetical citations.
        """
    return re.sub("\s*\(([^\)]*)(\d{4})[^\)]*\)", "", line)


#TODO: special characters causing issues. Better solution?
# http://stackoverflow.com/questions/5419/python-unicode-and-the-windows-console/32176732#32176732 ;
# http://stackoverflow.com/questions/878972/windows-cmd-encoding-change-causes-python-crash/3259271
# try:
#     f.write(value.lower() + '\n')
# except UnicodeEncodeError:
#     if sys.version_info >= (3,):
#         f.write(value.encode('utf8').decode(sys.stdout.encoding).lower() + '\n')
#     else:
#         f.write(value.encode('utf8').lower() + '\n')