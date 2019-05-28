import parser
parser.init(csv_file_name = "persons.csv",config_file_name="test")
# parser.parserFile(doc_id = "jdfiks",config_file_name="test", clinical_note_file_name = "/Users/yuanpan/Documents/NLP_project/input/mttest/mtsamples-type-3-sample-343.txt")
# parser.parserFile(doc_id = "djks",config_file_name="test",clinical_note_file_name = "/Users/yuanpan/Documents/NLP_project/input/mttest/mtsamples-type-3-sample-344.txt")
parser.processDocument(docID = "djks",content = "jdkfal")
