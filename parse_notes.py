#!/usr/bin/python
# -*- coding: utf-8 -*-

import markdown
import htmlmin
from bs4 import BeautifulSoup
import os
import sys, getopt
import re
import time

# print('Number of arguments:', len(sys.argv), 'arguments.')
# print('Argument List:', str(sys.argv))

file_path= str(sys.argv[1])
input_file= str(sys.argv[2])
export_file= input_file.split('.')[0] + '.html'

# Name input and output files
md_input= file_path + '/' + input_file
html_output= file_path + '/' + export_file

# Define constant to signal end of a question field
BEGINN_QUESTION = 'h3'
END_QUESTION = '%eq'

# List classes to be removed
REMOVE_ATTRIBUTES = [
  'class', 'alt'
]

# Count questions
qestion_count = 0

# Open markdown file
with open(md_input, "r", encoding="utf-8") as input_file:
    text = input_file.read()

# Parse markdown
html = markdown.markdown(text, extensions=['fenced_code'])

# Parse html
soup = BeautifulSoup(html, "html.parser")


##################
# Clean up html #
################

# Delete tags
tags = ['h1', 'h2', 'hr']
for item in tags:
  for tag in soup.select(item):
    tag.extract()

# Remove classes
for attribute in REMOVE_ATTRIBUTES:
  for tag in soup.find_all(attrs={attribute: True}):
    del tag[attribute]

# Replace quotation marks with html entity
quot_symbols= ['„', '“', '"']

for quot_symbol in quot_symbols:
  result= soup.find_all(string=re.compile(quot_symbol))

  for item in result:
    new_item= item.replace(quot_symbol, '&quot;')
    item.replace_with(new_item)

# Replace tabs with spaces
# tabs= ['	']

# for tab in tabs:
#   result= soup.find_all(string=re.compile(tab))

#   for item in result:
#     new_item= item.replace(tab, '  ')
#     item.replace_with(new_item)

#####################################################
# Format html so it can be read by Anki's importer #
###################################################

# Ankis importer reads text files and excepts HTML in them.
# Here we use a simple card layout: 2 Fields --> front (question) and back (answer)
# Anki distinguishes fields through a separator (semicolon, comma etc.)
# Here we use a tab as separator
# A new line is needed to signal the beginning of a new card
# Every question and every answer is wrapped in quotes
# This allows for multi line questions and answers (and new lines in questions and answers, which would otherwise be identified as beginnings of new cards)


# Get rid of all new lines by minifying html
html_min = htmlmin.minify(str(soup))
# Strip whitespace
html_min = html_min.strip()
# Cook fresh soup
soup = BeautifulSoup(html_min, "html.parser")


# Grab all begin and end tags from soup
begin_tags = soup.find_all(BEGINN_QUESTION)

# Determine if there is an end_tag in between two begin_tags
# If true: no action required
# False : insert answer and question separator directly after begin_tag
is_end_tag = False

for begin_tag in begin_tags:
  loop_variable = begin_tag
  while (loop_variable.find_next_sibling() and loop_variable.find_next_sibling().name != 'h3'):
    if (loop_variable.find_next_sibling().text == END_QUESTION):
      is_end_tag = True
      break
      loop_variable = loop_variable.find_next_sibling()
    else:
      loop_variable = loop_variable.find_next_sibling()
  
  if (not is_end_tag):
    begin_tag.insert_after('"\t"')
    print('insert after begin_tag')
    qestion_count += 1
  
  is_end_tag = False

end_tags = soup.find_all('p', string=END_QUESTION)
# paragraphs = soup.find_all('p')

# Mark beginning of a question
# no new line for first question
begin_tags[0].insert_before('"')

# Close answer from previous question (")
# Mark beging of next question (\t)
# Start wrapping the question(")
for begin_tag in begin_tags[1:]:
  begin_tag.insert_before('"\n"')

# Close question (")
# Insert tab separator (\t)
# Start wrapping answer ("")
for end_tag in end_tags:
  end_tag.insert_before('"\t"')
  # Increment no of questions
  qestion_count += 1

  # Remove end of question identifier
  end_tag.extract()

# Mark end of last question
# get all tags
tags = soup.findAll()
# get last html element
t = tags[-1]

# Problem: html elements are nested
# Solution: get last parent of last element before root
while (t.parent.name != "[document]"):
  t = t.parent

# insert quote after last parent of last element
t.insert_after('"')



    

# if (tags[-1].name == 'code'):
#   pass

# tags[-1].insert_after('"')



# Identify the end of an answer and beginning of a question
# add quotation mark to identify the end of an answer
# add new line before h3 openeing tags to identify beginn next question
# Do this except for first h3 tag (first question has no previous answer)



# Workaround for multiple choice questions
##########################################
# h4_tags = soup.find_all('h4')

# for h4 in h4_tags:
#   h4.insert_before('"\n')

# # Use string to identify the end of question, instead of closing tag
# end_of_question_tags = soup.find_all('p', string=END_QUESTION)

# # Insert a tab after end of question identifier (<p>%eq</p> ->)
# # Add quotation mark to identify begin answer (<p>%eq</p> ->")
# for end_of_question_tag in end_of_question_tags:
#   end_of_question_tag.insert_after('\t"')
#   # Remove end of question identifier (->")
#   end_of_question_tag.extract()
  
#   # Increment qestion_count (to count no of questions)
#   qestion_count += 1

###################################
###################################

## Write anki optimized soup to file
with open(html_output, "w", encoding="utf-8", errors="xmlcharrefreplace") as output_file:
  output_file.write(soup.decode(formatter=None))

# Copy all image files to Anki
os.system('cd ' + file_path + ' && cp *.jpg /Users/jep/Library/Application\ Support/Anki2/User\ 1/collection.media/')


# Print content of tags
# for string in soup.strings:
#   print(string)

# Print number of questions
print('#########################')

print('# No. of questions: ' + str(qestion_count) + ' #')

print('#########################')



#################################
# Anki stuff
##############################

# Backup Anki
# backup_folder = current_date() + '-' + current_time() + '-Anki'
# os.system('mkdir /Users/jep/backups/anki/' + backup_folder + '&& cp -r /Users/jep/Library/Application\ Support/Anki2/ /Users/jep/backups/anki/' + backup_folder )



