import parser
# parser.init(csv_file_name = "persons.csv",config_file_name="test")
# parser.parserFile(doc_id = "ID0000", clinical_note_file_name = "/Users/yuanpan/Documents/NLP_project/input/mttest/mtsamples-type-3-sample-343.txt")
# parser.parserFile(doc_id = "ID0001",clinical_note_file_name = "/Users/yuanpan/Documents/NLP_project/input/mttest/mtsamples-type-3-sample-344.txt")
# parser.processDocument(docID = "djks",content = "jdkfal")

parser.init(csv_file_name = "persons.csv",config_file_name="test_drugs.yaml")
parser.parserFile(doc_id = "41-2280", clinical_note_file_name = "/Users/yuanpan/Documents/NLP_project/input/mttest/mtsamples-type-41-sample-2280.txt")
parser.parserFile(doc_id = "91-1439",clinical_note_file_name = "/Users/yuanpan/Documents/NLP_project/input/mttest/mtsamples-type-91-sample-1439.txt")
parser.parserFile(doc_id = "95-520",clinical_note_file_name = "/Users/yuanpan/Documents/NLP_project/input/mttest/mtsamples-type-95-sample-520.txt")



#
# import nltk
# from nltk.tokenize import regexp
# word_tokenizer = regexp.WhitespaceTokenizer()
#
# import re
# re.search(r"\b12\b", "12 23 45 6y").start()
#
#
# #
# # for i in re.finditer('[0-9]+',"12 23 45 6y"):
# #     print(i.start())
#
#
