from ayesaac.services.common import QueueManager
from ayesaac.utils.logger import get_logger
import re
import json
from datetime import datetime

from ayesaac.services.common.group_6_config_interface import get_value

logger = get_logger(__file__)

class LabelFormatter(object):
	def readDate(self, text):
	# NORMALISING TEXT
		textNormalised = re.sub("[^a-zA-Z\d\n ]", " ", text) # Remove punctuation

		# SEARCHING FOR DATES
		regexDateFormats = [\
			"\d\d \d\d \d\d",\
			"\d\d \d\d \d\d\d\d",\
			"\d\d [a-z][a-z][a-z]",\
			"[a-z][a-z][a-z] \d\d\d\d"\
		]

		# See possible format: https://www.programiz.com/python-programming/datetime/strptime
		dateFormats =[\
			"%d %m %y",\
			"%d %m %Y",\
			"%d %b %Y",\
			"%b %Y"\
		]

		i = 0
		dateList = []
		while i < len(regexDateFormats):
			prevLength = len(dateList)
			dateList = dateList + re.findall(regexDateFormats[i], textNormalised, re.IGNORECASE)

			# FILTERING DATES FOUND
			j = prevLength
			while j < len(dateList):
				# If year is missing (matched  with regex "\d\d [a-z][a-z][a-z]"")...
				if i == 2:
					# ... we assume it is current year
					now = datetime.now()
					dateList[j] = dateList[j] + " " + str(now.year)
					dateFormat = "%d %b %Y" #dd MMM (yyyy)

				# try to convert a date to datetime
				try:
					date = datetime.strptime(dateList[j], dateFormats[i])
					dateList[j] = date
					j = j + 1
					# And discard invalid dates that can't be convert to datetime
				except ValueError:
					dateList.pop(j)
			i = i + 1

	  	# Return none if no date found
		if len(dateList) == 0:
			return None

		# We assume the last date found on the package correspond to expirity date
		return dateList[-1]


	def split_by_keywords(self, text, keywords):
		text = [text]
		regex = '(^.*'
		synonyms_regex = []
		for keyword in keywords:
		  synonyms_regex.append("|".join(synonym for synonym in keywords[keyword]))

		regex += "|".join(synonym_regex for synonym_regex in synonyms_regex)
		regex += ')'
		text = re.split(regex, text[0])
		data = {}
		max_len = -1
		likely_string = None
		for keyword in keywords:
			likely_string = ""
			for i in range(len(text)):
				if (text[i] != ''):
					if (text[i] in keywords[keyword]):
						next_string = text[i+1]
						cur_len = len(next_string)

						# Assume that the longest string after pattern is the one
						if (cur_len > max_len):
							max_len = cur_len
							likely_string = next_string

					data[keyword] = likely_string
		return data

	def find_category(self, text, cat_name, cat_elems):
		matches = []
		for item in cat_elems:
			match = re.search(item, text)
			if (match != None):
				matches.append(item)

		if (len(matches) > 0):
			logger.info("Found matches: " + str(matches) + " for " + cat_name)
		return matches


	def __init__(self):
		self.queue_manager = QueueManager([self.__class__.__name__, "Interpreter"])

	def callback(self, body, **_):
		# Normalize texts array into a string
		text = " ".join(" ".join(t) for t in body["texts"])

		# Replace all whitespaces by single space
		# Keep only alphanumerics, parentheses, commas, asterisks, and percent signs
		text = re.sub('\s+\n', ' ', text).lower()
		text = re.sub('[^a-z0-9(),%*. ]+', '', text)
		print(text)

		# Get keywords to look for from config file
		keywords = get_value("label-keywords")

		# Split label text by keyword and return as json
		body["extracted_label"] = self.split_by_keywords(text, keywords)

		date = self.readDate(text)
		if (date != None):
			body["extracted_label"]["expiry"] = date.strftime("%d %b %Y")
		else:
			logger.info("No expiry date found")

		categories = get_value("categories")
		# logger.info(categories)
		for category in categories.keys():
			body["extracted_label"][category] = self.find_category(text, category, categories[category])

		next_service = body["vision_path"].pop(0)
		self.queue_manager.publish(next_service, body)

		logger.info(f"{self.__class__.__name__} ready")

	def run(self):
		self.queue_manager.start_consuming(self.__class__.__name__, self.callback)

def main():
	lf = LabelFormatter()
	lf.run()


if __name__ == "__main__":
	main()
