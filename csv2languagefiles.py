# inloop/csv2languagefiles
# apache2 license
# author: Martin Olesnanik (http://nixone.sk)

import sys, csv, os, getopt

def printUsageAndQuit():
	print("usage: python "+sys.argv[0]+" [options] <csvfile>")
	print("Options:")
	print("    --android-variant-suffix <suffix> Suffix for flavor named folders, e.g. app/src/flavorXYZ/...")
	print("    --help                            Prints this help")
	sys.exit(2)

# Let' just parse command line options and if necessary print the usage
androidVariantSuffix = ""

try:
	optsArgs, leftArguments = getopt.getopt(sys.argv[1:], "", ['help', 'android-variant-suffix='])

	if len(leftArguments) != 1:
		print("Apart from options, exactly one argument <csvfile> is required")
		printUsageAndQuit()

	for opt, arg in optsArgs:
		if opt in ["-h", "--help"]:
			printUsageAndQuit()
		if opt == "--android-variant-suffix":
			androidVariantSuffix = arg

except getopt.GetoptError as err:
		print(str(err))
		printUsageAndQuit()

# Support for iteration over dictionary in python 2 and 3
def iterateDictionary(dict):
	if (sys.version_info >= (3, 0)):
		return dict.items()
	return dict.iteritems()

keyIndex = 0
variantIndex = 1
iOSApplicableIndex = 2
androidApplicableIndex = 3
languageStartIndex = 4

# If the file doesn't exist, bug off
filepath = leftArguments[0]
if not os.path.exists(filepath):
	print("File "+filepath+" not found")
	sys.exit(2)

# Let's start working with the file
with open(filepath) as csvFile:
	isFirst = True

	variantNamesDict = {}
	variantCount = 0
	languageCount = 0
	languageNames = []

	rowsToProcess = []

	counter = 0

	# Gather metadata, variants, variant names, language info, etc. and prepare rows with data to process
	for row in csv.reader(csvFile):
		if isFirst:
			isFirst = False
		
			for languageIndex in range(languageStartIndex, len(row)):
				languageCount += 1
				languageNames.append(row[languageIndex])
		else:
			rowsToProcess.append(row)
			if row[variantIndex] not in variantNamesDict:
				variantNamesDict[row[variantIndex]] = len(variantNamesDict)

	# Prepare multidimensional matrices for mapping data by variant index, language index, and then key in dictionary
	iOSByVariantAndLanguage = [[{} for i in range(0, languageCount)] for i in range(0, len(variantNamesDict))]
	androidByVariantAndLanguage = [[{} for i in range(0, languageCount)] for i in range(0, len(variantNamesDict))]

	# Process all rows and fill the appropriate matrices
	for row in rowsToProcess:
		variant = row[variantIndex]
		iOSApplicable = len(row[iOSApplicableIndex]) > 0
		androidApplicable = len(row[androidApplicableIndex]) > 0
		key = row[keyIndex]

		for l in range(0, languageCount):
			if iOSApplicable:
				# We want iOS data to have the default variant present everywhere as default
				if variant == '':
					for v, variantIndex in iterateDictionary(variantNamesDict):
						if key not in iOSByVariantAndLanguage[variantIndex][l]:
							iOSByVariantAndLanguage[variantIndex][l][key] = row[languageStartIndex]
				else:
					iOSByVariantAndLanguage[variantIndex][l][key] = row[languageStartIndex+l]
			if androidApplicable:
				androidByVariantAndLanguage[variantNamesDict[variant]][l][key] = row[languageStartIndex+l]

	# We first iterate over every variant and then in every language
	for variant, variantIndex in iterateDictionary(variantNamesDict):
		for languageIndex in range(0, languageCount):

			# Here comes android

			# Empty variant will be in android "main" folder, any other variant will be in "anyOtherLook" folder
			variantPath = ""
			if variant == '':
				variantPath = "main"
			else:
				variantPath = variant + androidVariantSuffix
			dirsToWrite = ["android/src/"+variantPath+"/res/values-"+languageNames[languageIndex]]

			# If we are processing first language, we want to use it also as default (values/strings.xml)
			if languageIndex == 0:
				dirsToWrite.append("android/src/"+variantPath+"/res/values")
			for dirToWrite in dirsToWrite:
				if not os.path.exists(dirToWrite):
					os.makedirs(dirToWrite)
				with open(dirToWrite+"/strings.xml", "w") as xmlFile:
					xmlFile.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
					xmlFile.write("<!-- THIS FILE IS GENERATED, MODIFY ONLY IF YOU ARE SURE WHAT YOU ARE DOING -->\n")
					xmlFile.write("<resources>\n")
					for key, value in iterateDictionary(androidByVariantAndLanguage[variantIndex][languageIndex]):

						# We first write a comment, value from first language as a hint for other translations
						xmlFile.write("\n    <!-- "+androidByVariantAndLanguage[variantIndex][0][key]+" -->\n")

						# Then we preformat the value and write the <string> record itself
						notFormatted = False
						if "{string}" in value:
							notFormatted = True
							value = value.replace("{string}", "%s")
						if "{float}" in value:
							notFormatted = True
							value = value.replace("{float}", "%f")
						if "{integer}" in value:
							notFormatted = True
							value = value.replace("{integer}", "%d")

						if "<font" in value or "{cdata}" in value:
							value = value.replace("{cdata}", "")
							value = "<![CDATA[ "+value+"]]>"

						xmlFile.write("    <string name=\""+key+"\"")
						if notFormatted:
							xmlFile.write(" formatted=\"false\"")
						xmlFile.write(">"+value+"</string>\n")
					xmlFile.write("</resources>")

			# Here comes iOS
	
			if not os.path.exists("ios"):
				os.makedirs("ios")
			with open("ios/Localizable"+variant+languageNames[languageIndex]+".strings", "w") as stringsFile:
				stringsFile.write("/* THIS FILE IS GENERATED, MODIFY ONLY IF YOU ARE SURE WHAT YOU ARE DOING */\n")

				for key, value in iterateDictionary(iOSByVariantAndLanguage[variantIndex][languageIndex]):

					# We first write a comment, value from first language as a hint for other translations
					stringsFile.write("\n/* "+iOSByVariantAndLanguage[variantIndex][0][key]+" */\n")

					# Then we preformat the value and write the <string> record itself
					if "{string}" in value:
						value = value.replace("{string}", "%@")
					if "{float}" in value:
						value = value.replace("{float}", "%f")
					if "{integer}" in value:
						value = value.replace("{integer}", "%d")

					stringsFile.write("\""+key+"\" = \""+value+"\";\n")