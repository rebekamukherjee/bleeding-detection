import csv
import pandas as pd
import re
import spacy
import sys

nlp = spacy.load('en')

TRAINING_METADATA_FILE = './data/notes_metadata_trainingset.csv'
VALIDATION_METADATA_FILE = ''


def extract_phrases(metadata_frame, phrase_length, target_patterns, output_file):
	"""Extracts phrases around target terms indicating bleeding.

	Extracts clinical notes for each unique mrn in the training or validation
	metadata. Uses spacy sentence splitter to extract sentences among these
	notes. If a term indicating a bleeding event is identified in any of these
	sentences, extracts phrases from the clinical notes before and after the
	term, specified by phrase_length.

	Args:
		metadata_frame: The expanded metadata frame containing clinical notes
			for all mrns in the training or validation set.
		phrase_length: The number of phrases to extract when a term indicating
			a bleeding event is found in the clinical notes.
			(e.g. if phrase_length = 5, this function extracts 2 phrases before
			the phrase containing the term, the phrase containting the term,
			and 2 phrases after the phrase containing the term)
		targets_patterns: The regex for extracting terms indicating bleeding.
		output_file: The name of the file where the training or validation data
			will be written, with the extracted notes appended to it.

	Returns:
		None.

	Raises:
		None.
	"""

	output_fieldnames = ['mrn', 'note_date', 'note_ids', 'note', 'targets']
	with open(output_file, 'w') as f:
		writer = csv.writer(f)
		writer.writerow(output_fieldnames)
		count = 0
		mrns = metadata_frame['mrn'].unique()
		for mrn in mrns:
			mrn_frame = metadata_frame[metadata_frame['mrn'] == mrn]
			dates = mrn_frame['note_date'].unique()
			for date in dates:
				notes = list(mrn_frame[mrn_frame['note_date'] == date]['text'])
				note_ids = list(mrn_frame[mrn_frame['note_date'] == date]['noteid'])
				extracted_notes = []
				all_targets = []
				for note in notes:
					if isinstance(note, str):
						doc = nlp(unicode(note, 'utf-8'))
						sentences = [str(i) for i in list(doc.sents)]
						for i in range(len(sentences)):
							targets = []
							for target_pattern in target_patterns:
								targets += re.findall(target_pattern, sentences[i])
								all_targets += re.findall(target_pattern, sentences[i])
							if len(targets) > 0:
								# beginning index
								beg = i - int(phrase_length/2)
								if beg < 0:
									beg = 0
								# ending index
								end = i + phrase_length - int(phrase_length/2)
								if end > len(sentences):
									end = len(sentences)
								extracted_notes += sentences[beg:end]
				extracted_notes = ' '.join(extracted_notes)
				line = [mrn, date, note_ids, extracted_notes, all_targets]
				writer.writerow(line)
			count += 1
			sys.stdout.write('\rCompleted %d of %d, %d%%' % (count, len(mrns), count*100/len(mrns)))
			sys.stdout.flush()


def main():
	"""Main function.

	Reads training or validation metadata, and number of phrases to extract
	when a term indicating a bleeding event is encountered. Calls the function
	to extract notes from the metadata.

	Usage:
	python extract.py [-t | -v] <phrase_length>

	Args:
		-t: Training.
		-v: Validation.
		phrase_length: The number of phrases to extract.

	Example:
	python extract.py -t 3
	"""

	# read CLI arguments
	if len(sys.argv) < 3:
		print 'Insufficient input.'
		exit()

	# read training or validation metadata
	if sys.argv[1] == '-t':
		print 'Reading training metadata file...'
		metadata_frame = pd.read_csv(TRAINING_METADATA_FILE)
		OUTPUT_FILE = ['./data/training']
	elif sys.argv[1] == '-v':
		print 'Reading validation metadata file...'
		metadata_frame = pd.read_csv(VALIDATION_METADATA_FILE)
		OUTPUT_FILE = ['./data/validation']
	else:
		print 'Incorrect input. Enter -t for training data, or -v for validation data.'
		exit()

	# read phrase length
	phrase_length = int(sys.argv[2])
	if phrase_length < 1:
		print 'Phrase length too small. Enter a number between 0 and 5.'
		exit()
	elif phrase_length > 5:
		print 'Phrase length too big. Enter a number between 0 and 5.'
		exit()
	OUTPUT_FILE.append(str(phrase_length) + 'phrases.csv')

	# define regex for bleeding target terms
	bleeding_targets = [r"(?<!non)(?<!non )(?<!non-)(?<!re)(bleed(?!ing)|bleeding(?!\stime))", 
						r"blood loss", 
						r"blood per rectum", 
						r"(?<!non-)(?<!non)(?<!non )bloody", 
						r"brbpr", r"coffee[\- ](ground|grounds)", 
						r"ecchymos[ie]s", 
						r"epistaxis", 
						r"exsanguination", 
						r"\bl?gib\b", 
						r"((\bg|gua?iac)([\-]|\s+)((pos(itive)?)|\+)|guaiac\(\+\))", 
						r"(?<!splinter\s)hem{1,2}or{1,2}h{1,2}age?", 
						r"hematem[a-z]+", 
						r"hematochezia", 
						r"hematoma", 
						r"hematuria", 
						r"hemoperitoneum", 
						r"hemoptysis",
						r"hemothorax",
						r"hemopericardium",
						r"hemarthrosis",
						r"hemarthroses",
						r"hemearthrosis",
						r"sanguineous",
						r"haemorrhage",
						r"diffuse\balveolar\bhemorrhage",
						r"dah",
						r"epidural\bhematoma",
						r"edh",
						r"intracranial\bhemorrhage",
						r"intracranial\bhemhorrage"
						r"intracranial\bhemorrhage"
						r"ich",
						r"\bich", r"mel[ae]n(a|ic)", 
						r"(ng|ngt)\s+lavage\s+((positive)|(pos)|\+)", 
						r"((positive)|(pos)|\+) (ng|ngt) lavage", 
						r"(fecal\s+occult(\s+blood)?|\bob|\bfob)\s+pos(itive)?", 
						r"sah", 
						r"sdh", 
						r"(maroon|red)\s+(stool|bowel\s+movement|bm)", 
						r"vomit[a-z]* blood",
						]

	# extract phrases from notes
	OUTPUT_FILE = '_'.join(OUTPUT_FILE)
	print 'Writing extracted phrases...'
	extract_phrases(metadata_frame = metadata_frame, 
		phrase_length = phrase_length, 
		target_patterns = bleeding_targets, 
		output_file = OUTPUT_FILE)


if __name__ == '__main__':
	main()