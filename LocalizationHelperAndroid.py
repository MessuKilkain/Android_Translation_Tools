
from bs4 import BeautifulSoup
from bs4 import element
import csv
from future.utils import iteritems

FIELDNAME_KEY = u'Key'

def splitLocalizationWithPlural(localization):
	splittedDict = dict()
	for (key, value) in iteritems(localization):
		# print( '- ', key, type(key) )
		# print( '\t- ', value, type(value) )
		if type(value) is type(str()):
			splittedDict[key] = value
		elif type(value) is type(dict()):
			for (pluralKey, pluralValue) in iteritems(value):
				splittedDict[str(key)+u"/"+str(pluralKey)] = str(pluralValue)
		else:
			raise TypeError(u"value("+str(value)+u") of key("+str(key)+u") is not a string neither a dictionary", [{u'key':key, u'value':value}])
	return splittedDict

def joinLocalizationWithPlural(localization):
	joinedDict = dict()
	for (key, value) in iteritems(localization):
		# print( '- ', key, type(key) )
		# print( '\t- ', value, type(value) )
		if type(key) is type(str()):
			if "/" in key :
				splitted = key.split(sep="/",maxsplit=1)
				trueKey = splitted[0]
				pluralKey = splitted[1]
				if trueKey in joinedDict:
					if type(joinedDict[trueKey]) is not type(dict()):
						raise TypeError(u"key("+str(key)+u") with value("+str(value)+u") has already a non-plural value joined", [{u'key':key, u'value':value, u'joinedDict':joinedDict}])
				else:
					joinedDict[trueKey] = dict()
				joinedDict[trueKey][pluralKey] = value
			else:
				joinedDict[key] = value
		else:
			raise TypeError(u"key("+str(key)+u") with value("+str(value)+u") is not a string", [{u'key':key, u'value':value}])
	return joinedDict

def parseFilePathToLocalizedStringsDictionary(filePath,output=None):
	localizedStringsDictionary = dict()
	with open(filePath, 'r', encoding='utf-8') as infile:
		soup = BeautifulSoup(infile, 'html.parser')
		# print(soup.prettify(),file=output)
		# print(str(soup.contents),file=output)
		# print(str(len(soup.contents)),file=output)
		for content in soup.children:
			if type(content) is element.Tag:
				# print(content.name,file=output)
				for resource in content.children:
					# print(resource,file=output)
					# print(resource.prettify(),file=output)
					if type(resource) is element.Tag:
						True
						print("NAME : "+str(resource.name)+" ( name : "+str(resource['name'])+" )",file=output)
						key = None
						value = None
						if 'string' == resource.name:
							if resource['name'] and resource.string:
								True
								key = str(resource['name'])
								value = str(resource.string)
								# print("-> "+resource.string,file=output)
						elif 'plurals' == resource.name:
							True
							print("Plurals : "+resource.name+" ( name : "+str(resource['name'])+" )",file=output)
							print(resource.prettify(),file=output)
							key = str(resource['name'])
							value = dict()
							for pluralsItem in resource.children:
								if (
								type(pluralsItem) is element.Tag
								and 'item' == pluralsItem.name
								and pluralsItem['quantity']
								and pluralsItem['quantity'] not in value ):
									value.setdefault(str(pluralsItem['quantity']),str(pluralsItem.string))
						else:
							print("NAME : "+resource.name+" ( name : "+str(resource['name'])+" )",file=output)
						# print(resource.prettify(),file=output)
						if key and value:
							if key in localizedStringsDictionary:
								# Error : key should not be present
								print("ERROR : key("+key+") is already present in localizedStringsDictionary (values : "+localizedStringsDictionary[str(key)]+" ; "+str(value)+")",file=output)
							else:
								localizedStringsDictionary.setdefault(str(key), value)
						else:
							True
							print("key("+str(key)+") or value("+str(value)+") is invalid",file=output)
					elif type(resource) is element.NavigableString:
						if resource.strip():
							print("STRING : "+str(resource),file=output)
					elif type(resource) is element.Comment:
						if resource.strip():
							True
							# print("COMMENT : "+resource,file=output)
					# else:
					# 	print("line break",file=output)
			elif type(content) is element.NavigableString:
				True
				if content != '\n':
					print("navigable string : "+content,file=output)
			elif type(content) is element.ProcessingInstruction:
				True
				# Do nothing
				print(content,file=output)
			else:
				print("TYPE : "+str(type(content)),file=output)
				print(content,file=output)
	return localizedStringsDictionary

def formatAndCompleteLocalizationFile(sourceLocalizationFilePath,destinationLocalizationFilePath):
	indentOffsetString = "    "
	destinationLocalizedStringsDictionary = parseFilePathToLocalizedStringsDictionary(destinationLocalizationFilePath)
	with open(sourceLocalizationFilePath, 'r', encoding='utf-8') as infile,open(destinationLocalizationFilePath, 'w', encoding='utf-8') as outfile:
		soup = BeautifulSoup(infile, 'html.parser')
		for content in soup.children:
			if type(content) is element.Tag and "resources" == content.name:
				print("<resources>",file=outfile)
				insideCommentBlock = False
				stringAddedOutsideCommentBlock = False
				for resource in content.children:
					if type(resource) is element.Tag \
						and ( "string" == resource.name or "plurals" == resource.name ):
						if resource.get(key='translatable',default='true') == "false":
							True
							# print("Translatable false : "+str(resource))
							# print nothing
						else:
							if not insideCommentBlock and not stringAddedOutsideCommentBlock:
								stringAddedOutsideCommentBlock = True
								print(file=outfile)
							if 'string' == resource.name:
								# print("string resource : "+str(resource))
								if resource['name'] and resource.string:
									# print("resource to print : "+str(resource))
									key = resource['name']
									value = resource.string
									newItemTag = soup.new_tag('string')
									newItemTag['name'] = key
									if key in destinationLocalizedStringsDictionary and destinationLocalizedStringsDictionary[key]:
										newItemTag.string = destinationLocalizedStringsDictionary[key]
										print(indentOffsetString+str(newItemTag),file=outfile)
										destinationLocalizedStringsDictionary.pop(key)
									else:
										print(indentOffsetString+str(newItemTag),end='',file=outfile)
										print("<!-- TODO : translate -->",file=outfile)
								else:
									print("ERROR : resource['name']("+str(resource['name'])+") or resource.string("+str(resource.string)+") is invalid")
							elif 'plurals' == resource.name:
								key = resource['name']
								# print("resource key : "+str(key))
								if key in destinationLocalizedStringsDictionary \
									and destinationLocalizedStringsDictionary.get(key) \
									and type(destinationLocalizedStringsDictionary.get(key)) is dict:
									print(indentOffsetString+"<plurals name=\""+key+"\">",file=outfile)
									for itemKey, itemValue in destinationLocalizedStringsDictionary[key].items():
										newItemTag = soup.new_tag('item', quantity=itemKey)
										newItemTag.append(itemValue)
										print(indentOffsetString+indentOffsetString+str(newItemTag),file=outfile)
									print(indentOffsetString+"</plurals>",file=outfile)
									destinationLocalizedStringsDictionary.pop(key)
								else:
									newPluralsTag = soup.new_tag('plurals')
									newPluralsTag['name'] = key
									newPluralsTag.append(element.Comment(" TODO : translate "))
									print(indentOffsetString+str(newPluralsTag),file=outfile)
					# elif type(resource) is element.NavigableString:
					# 	print(resource,end='',file=outfile)
					elif type(resource) is element.Comment:
						if resource.string.strip().startswith('/') and -1 == resource.string.find('->'):
							insideCommentBlock = False
							stringAddedOutsideCommentBlock = False
						elif not insideCommentBlock:
							print(file=outfile)
							insideCommentBlock = True
						print(indentOffsetString+"<!--"+resource+"-->",file=outfile)
					# else:
					# 	print("OTHER : "+str(resource))
					# 	print(resource,end='',file=outfile)
				# TODO : print translated keys not present in source file
				print("destinationLocalizedStringsDictionary : "+str(destinationLocalizedStringsDictionary))
				if len(destinationLocalizedStringsDictionary) > 0:
					print(file=outfile)
					print(indentOffsetString+"<!-- The followings are not in original file. The keys have probably been deleted. -->",file=outfile)
					for remainingKey, remainingValue in destinationLocalizedStringsDictionary.items():
						if type(remainingValue) is dict:
							print(indentOffsetString+"<plurals name=\""+remainingKey+"\">",file=outfile)
							for itemKey, itemValue in remainingValue.items():
								newItemTag = soup.new_tag('item', quantity=itemKey)
								newItemTag.append(itemValue)
								print(indentOffsetString+indentOffsetString+str(newItemTag),file=outfile)
							print(indentOffsetString+"</plurals>",file=outfile)
						else:
							newItemTag = soup.new_tag('string')
							newItemTag['name'] = remainingKey
							newItemTag.append(str(remainingValue))
							print(indentOffsetString+str(newItemTag),file=outfile)
					print()
				print("</resources>",file=outfile)
			elif type(content) is element.Tag:
				print(content,end='',file=outfile)
			elif type(content) is element.NavigableString:
				print(content,end='',file=outfile)
			elif type(content) is element.Comment:
				print("<!--"+content+"-->",end='',file=outfile)
			elif type(content) is element.ProcessingInstruction:
				print("<?"+content+">",end='',file=outfile)
			else:
				# WARNING :
				print("TYPE : "+str(type(content)))
				print(content)
	return

def exportLocalizationToAndroidStringFile(destinationLocalizationFilePath,localization,encoding=u"utf-8",):
	indentOffsetString = "    "
	with open(destinationLocalizationFilePath, 'w', encoding='utf-8') as outfile:
		soup = BeautifulSoup("<b></b>", 'html.parser')
		print("<resources>",file=outfile)
		for key, value in localization.items():
			if type(value) is dict:
				print(indentOffsetString+"<plurals name=\""+key+"\">",file=outfile)
				for itemKey, itemValue in value.items():
					newItemTag = soup.new_tag(name=u'item', quantity=itemKey)
					newItemTag.append(itemValue)
					print(indentOffsetString+indentOffsetString+str(newItemTag),file=outfile)
				print(indentOffsetString+"</plurals>",file=outfile)
			else:
				newItemTag = soup.new_tag(name=u'string')
				newItemTag['name'] = key
				newItemTag.append(str(value))
				print(indentOffsetString+str(newItemTag),file=outfile)
		print("</resources>",file=outfile)
	return

class NullPrint:
	def write(self,string):
		return

def exportLocalizationToCsvFile(outputFileName,keys,localization,encoding=u"utf-8"):
	'''
	Write localization to a CSV file.

	:param str outputFileName: The path to csv file to export to
	:param list keys: The list of localization key
	:param dict localization: The dictionary of dictionries of localized texts, first level key being the language or 'Comment', second level key being the localization key for the translated text or the comment
	:param str encoding: Encoding used for open (optional)
	:return: void
	:rtype: None
	:raises ValueError: if 'Key' is present in the csv fieldnames
	'''
	fieldnames = list(localization)
	if FIELDNAME_KEY in fieldnames:
		raise ValueError(FIELDNAME_KEY + u" is expected to be absent from fieldnames")
	with open( outputFileName, u"w", encoding=encoding ) as fileTo:
		csvFieldnames = list(fieldnames)
		csvFieldnames.insert(0,FIELDNAME_KEY)
		writer = csv.DictWriter(fileTo, fieldnames=csvFieldnames)
		writer.writeheader()
		for key in keys:
			rowToWrite = {FIELDNAME_KEY:key}
			for fieldname in fieldnames:
				if key in localization[fieldname]:
					rowToWrite[fieldname] = localization[fieldname][key]
			writer.writerow(rowToWrite)
	return



def importLocalizationFromCsvFile(inputFileName,encoding=u"utf-8"):
	'''
	Parse and return localization from a CSV file.

	:param str inputFileName: The path to csv file to import from
	:param str encoding: Encoding used for open (optional)
	:return: The list of localization keys and the dictionary of dictionaries of localized texts, first level key being the language or 'Comment', second level key being the localization key for the translated text or the comment
	:rtype: (list,dict)
	:raises ValueError: if 'Key' is not present in the csv fieldnames
	'''
	extractedValues = dict()
	extractedKeys = list()

	with open( inputFileName, u"r", encoding=encoding ) as csvfile:
		reader = csv.DictReader(csvfile)
		csvFieldnames = list(reader.fieldnames)
		if not FIELDNAME_KEY in csvFieldnames:
			raise ValueError(FIELDNAME_KEY + u" is not present as a fieldname in csv.")
		else:
			csvFieldnames.remove(FIELDNAME_KEY)
			for fieldname in csvFieldnames:
				extractedValues[fieldname] = dict()
			for row in reader:
				key = row[FIELDNAME_KEY]
				extractedKeys.append(key)
				for fieldname in csvFieldnames:
					extractedValues[fieldname][key] = row[fieldname]
	return (extractedKeys, extractedValues)
