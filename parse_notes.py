#!/usr/bin/python
# -*- coding: utf-8 -*-

import markdown
import htmlmin
from bs4 import BeautifulSoup
import os
import sys, getopt
import re
import time

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))

file_path= str(sys.argv[1])
input_file= str(sys.argv[2])
export_file= input_file.split('.')[0] + '.html'

# Name input and output files
md_input= file_path + '/' + input_file
html_output= file_path + '/' + export_file

# Define constant to signal end of a question field
END_OF_QUESTION_STRING = '%eq'

# List classes to be removed
REMOVE_ATTRIBUTES = [
  'class', 'alt'
]

# Count h3 and h4 tags to determine num of questions
tag_count = 0


# Return current date formatted as 2020-05-31
def current_date():
    seconds = time.time()
    structured_time = time.localtime(seconds)
    year = structured_time.tm_year
    month = (structured_time.tm_mon
              if len(str(structured_time.tm_mon)) == 2
              else '0{}'.format(structured_time.tm_mon))
    day = (structured_time.tm_mday
            if len(str(structured_time.tm_mday)) == 2
            else '0{}'.format(structured_time.tm_mday))

    return ("%s-%s-%s" % (year, month, day))

def current_time():
  seconds = time.time()
  structured_time= time.localtime(seconds)
  hour = (structured_time.tm_hour
          if len(str(structured_time.tm_hour)) == 2
          else '0{}'.format(structured_time.tm_hour))
  minutes = (structured_time.tm_min
              if len(str(structured_time.tm_min)) == 2
              else '0{}'.format(structured_time.tm_min))
  seconds = (structured_time.tm_sec
              if len(str(structured_time.tm_sec)) == 2
              else '0{}'.format(structured_time.tm_sec))

  return ("%s:%s:%s" % (hour, minutes, seconds))


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

# Get rid of all new lines by minifying html
html_min = htmlmin.minify(str(soup))
# Strip whitespace
html_min = html_min.strip()
# Cook fresh soup
soup = BeautifulSoup(html_min, "html.parser")

# Grab all h3 tags from soup
h3_tags = soup.find_all('h3')

# Identify the end of a question and beginning of an answer:
# add tab after every h3 closing tag (end of a question)
# add quotation mark to identify begin of answer
for h3 in h3_tags:
  h3.insert_after('\t"')

  # Increment no of questions
  # this counts all questions marked with an h3 tag
  tag_count += 1

# Identify the end of an answer and beginning of a question
# add quotation mark to identify the end of an answer
# add new line before h3 openeing tags to identify beginn next question
# Do this except for first h3 tag (first question has no previous answer)
for h3 in h3_tags[1:]:
  h3.insert_before('"\n')


# Workaround for multiple choice questions
##########################################
h4_tags = soup.find_all('h4')

for h4 in h4_tags:
  h4.insert_before('"\n')

# Use string to identify the end of question, instead of closing tag
end_of_question_tags = soup.find_all('p', string=END_OF_QUESTION_STRING)

# Insert a tab after end of question identifier (<p>%eq</p> ->)
# Add quotation mark to identify begin answer (<p>%eq</p> ->")
for end_of_question_tag in end_of_question_tags:
  end_of_question_tag.insert_after('\t"')
  # Remove end of question identifier (->")
  end_of_question_tag.extract()
  
  # Increment tag_count (to count no of questions)
  tag_count += 1

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

print('# No. of questions: ' + str(tag_count) + ' #')

print('#########################')



#################################
# Anki stuff
##############################

# Backup Anki
# backup_folder = current_date() + '-' + current_time() + '-Anki'
# os.system('mkdir /Users/jep/backups/anki/' + backup_folder + '&& cp -r /Users/jep/Library/Application\ Support/Anki2/ /Users/jep/backups/anki/' + backup_folder )



