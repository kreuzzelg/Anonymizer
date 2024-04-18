"""
Project Name: Anonymizer/emailPstAnonymizer
Description: Import emails from PST file and anonymize them into text file
Author: FAM, kreuzzelg
Date: 18. April 2024

Copyright (c) Year Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

MIT License https://opensource.org/licenses/MIT
"""


from libratom.lib.pff import PffArchive
from email import generator
from pathlib import Path
import re
import spacy
 
 
# Specify the path to your PST file
pst_file_path = r'D:\Work\AI\EmailHandling\Input\itechsupportNov23.pst'
 
# Load the PST file
archive = PffArchive(pst_file_path)
 
# Create a directory to save extracted emails (if it doesn't exist)
#eml_out = Path(Path.cwd() / "emls")
eml_out = Path(r'D:\Work\AI\EmailHandling\Output_6')
if not eml_out.exists():
    eml_out.mkdir()
 
# Load the spaCy Language model
nlp_de = spacy.load("de_core_news_sm")
nlp_multi = spacy.load("xx_ent_wiki_sm")
# import xx_sent_ud_sm
# nlp = xx_sent_ud_sm.load()
 
def remove_names(nlp, text):    
    doc = nlp(text)
    text = " ".join(token.text for token in doc if token.ent_type_ != "PER")
    newString = text
    for e in reversed(doc.ents):
        # print(e.label_)
        if e.label_ == "PER": # Only if the entity is a PERSON
            # print('start:' + newString[e.start_char: e.start_char + len(e.text)]) 
            newString = newString[:e.start_char] + '**PER**' + newString[e.start_char + len(e.text):]
    return newString

def replace_phone_mumber(regex, message):
    text = re.sub(regex, "**PHONE**", message)
    return text
 
""" #This regex validates phone numbers like:
#     +1 123-456-7890
#     555-1234
#     (123) 456 7890
#     +44 20 1234 5678
#     +41 77 777 77 77
#     +41 77 777 7777
"""
phone_pattern_eu = re.compile(r"(?P<country_code>\+\d{1,3})?\s?\(?(?P<area_code>\d{1,4})\)?[\s.-]?(?P<local_number>\d{3}[\s.-]?\d{2,4}[\s.-]?\d{2})")
 
print("Writing messages to .eml files...")
for folder in archive.folders():
    if folder.get_number_of_sub_messages() != 0:
        for message in folder.sub_messages:
            # Generate a filename for the .eml file
            if message.subject:
                name = message.subject.replace(" ", "_")
                name = name.replace("/", "-")
                name = name.replace("?", "[Q]")
                name = name.replace("&", "_n_")
                name = name.replace(":", "¦")
                name = name.replace(",", "_")
                name = name.replace("|", "¦¦")
                name = name.replace("ä", "ae")
                name = name.replace("ö", "oe")
                name = name.replace("ü", "ue")
            else: name = "no_subject"
            filename = eml_out / f"{message.identifier}_{name}.eml"
            print('Writing: ', name)
            # Write the email content to the .eml file
            try:
                formatted_message = archive.format_message(message, with_headers= False)
 
                # Replace email addresses with quotes around them
                nomail_message = re.sub(r'([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})', r'**MAIL**', formatted_message)           
                nophone_message = replace_phone_mumber(phone_pattern_eu, nomail_message)
               
                # Remove named entities (PROPN)
                anon_message = remove_names(nlp_multi, nophone_message)
                anon_message = remove_names(nlp_de, anon_message)
               
                # print(anon_message)
                filename.write_text(anon_message,  encoding="utf-8")
            except OSError:
                print('ERROR:   ', name)
               
            # input("Press Enter to continue...")
print("Extraction complete!")
 


