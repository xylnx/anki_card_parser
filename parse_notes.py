#!/usr/bin/python
# -*- coding: utf-8 -*-

import markdown
import htmlmin
from bs4 import BeautifulSoup
import os
import sys, getopt
import re
import time

# Anki's library folder
# ANKI_LIB_DIR='${HOME}/.local/share/Anki2/User\ 1/collection.media'
ANKI_LIB_DIR='${HOME}/Library/Application\ Support/Anki2/User\ 1/collection.media'

# Image folder location
IMG_DIR='/img/'

# HTML folder location
HTML_DIR='/html/'

# Define constants to signal begin and end of a question
BEGINN_QUESTION = 'h3'
END_QUESTION = '%eq'

# HANDLE ARGUMENTS
# print('Number of arguments:', len(sys.argv), 'arguments.')
# print('Argument List:', str(sys.argv))
file_path= str(sys.argv[1])
input_file= str(sys.argv[2])
export_file= HTML_DIR + input_file.split('.')[0] + '.html'

# Name input and output files
md_input= file_path + '/' + input_file
html_output= file_path + '/' + export_file

# Count questions
question_count = 0

# Open markdown file
with open(md_input, "r", encoding="utf-8") as input_file:
    markd = input_file.read()

# Parse markdown
html = markdown.markdown(markd, extensions=['fenced_code'])

# Parse html
soup = BeautifulSoup(html, "html.parser")


##################
# Clean up html #
################

# List tags for removal
REMOVE_TAGS = ['h1', 'h2', 'hr']
# List classes to be removed
REMOVE_ATTRIBUTES = ['class', 'alt']
# List quotation marks to be replace with html entity
QUOT_SYMBOLS= ['„', '“', '"']

# Remove attributes
def remove_attrs(attrs):
  for attribute in attrs:
    for tag in soup.find_all(attrs={attribute: True}):
      del tag[attribute]

def remove_tags(tags):
  for tag in tags:
    for tag in soup.select(tag):
      tag.extract()

# Replace strings in the whole file
def replace_strings(string_array, replacement_str):
  for str in string_array:
    # Find strings
    result = soup.find_all(string=re.compile(str))
    # Replace strings
    for item in result:
      new_str= item.replace(str, replacement_str)
      item.replace_with(new_str)

# Replace strings in a subset made from particular tags
def replace_strings_sub(strg, replacement_str, tag):
    result = soup.find_all(tag)
    # Replace strings
    for item in result:
      new_str= str(item).replace(strg, replacement_str)
      item.replace_with(new_str)
      # print(new_str)

def clean_html():
  # Remove unnecessary html tags and attributes
  remove_tags(REMOVE_TAGS)
  remove_attrs(REMOVE_ATTRIBUTES)
  # Replace quotation marks with html entity
  replace_strings(QUOT_SYMBOLS, '&quot;')
  # Replace double quotes with single quotes in image src attributes
  # Double quotes cause errors when importing to Anki
  replace_strings_sub('"',"'","img")

clean_html()

#######################################################################
# Format quesetions and answers so it can be read by Anki's importer #
#####################################################################

# Ankis importer reads text files and excepts HTML in them.
# Here we use a simple card layout: 2 Fields --> front (question) and back (answer)
# Anki distinguishes fields through a separator (semicolon, comma etc.)
# Here we use a tab as separator
# Also: A new line is needed to signal the beginning of a new card
# And: Every question and every answer is wrapped in quotes
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
# False : insert answer/question-separator directly after begin_tag
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
    # Increment no of questions
    question_count += 1

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
  question_count += 1

  # Remove end of question identifier
  end_tag.extract()

# Mark end of last question
# get all tags
tags = soup.findAll()
# get last html element
t = tags[-1]

# Find last closing tag
# Problem: html elements are nested
# Thus: the last closing tag might actually be the penultimate tag
# Solution: get last parent of last element before the root
while (t.parent.name != "[document]"):
  t = t.parent

# insert quote after last parent of last element
t.insert_after('"')


  #######################
 # save file           #
########################

## Write anki optimized soup to file
with open(html_output, "w", encoding="utf-8", errors="xmlcharrefreplace") as output_file:
  output_file.write(soup.decode(formatter=None))

# Copy all image files to Anki
os.system('cd ' + file_path + IMG_DIR + ' && cp *.jpg ' +  ANKI_LIB_DIR)


# Print content of tags
# for string in soup.strings:
#   print(string)

# Print number of questions
print('#########################')

print('# No. of questions: ' + str(question_count) + ' #')

print('#########################')



#################################
# Anki stuff
##############################

# Backup Anki
# backup_folder = current_date() + '-' + current_time() + '-Anki'
# os.system('mkdir /Users/xy/backups/anki/' + backup_folder + '&& cp -r
# /Users/xy/Library/Application\ Support/Anki2/ /Users/xy/backups/anki/' + backup_folder )



