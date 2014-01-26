import re
def sendToImport(path, fName, lName, score):
    """In order for this to work the user
    must include the names in the export"""
    # Note: everytime you run this program it
    # opens and closes the files
    # this is not the most effiecent use of resources
    textFile = open(path,"r")
    startText = textFile.read()
    textFile.close()

    if fName.lower() not in startText.lower() or lName.lower() not in startText.lower():
        print "ERROR: the name you are looking for is not in the template"
        return False

    score = score.strip().split()[0] #score comes in as "25 / 30"

    newText = startText
    for line in startText.split("\n"):
        if fName.lower() in line.lower() and lName.lower() in line.lower():
            newLine = re.sub(r",\d*?,#",","+str(score)+",#", line) # matches ,,# or ,23343,#
            newText = newText.replace(line,newLine)

    textFile = open(path,"w")
    textFile.write(newText)
    textFile.close()