import pathlib
import textwrap

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))
# Or use `os.getenv('GOOGLE_API_KEY')` to fetch an environment variable.
import os
os.environ['GOOGLE_API_KEY']=""


genai.configure(api_key="")
model = genai.GenerativeModel('gemini-pro')
def generated_response(query, emailid):
  response = model.generate_content("generate me a reply email for this emailid" + emailid + "and its query in a formal way on the behalf of customerservice.provide our name as contactcenter" +query+".don't leave any [] containing line.[your name] can be contactcenter")
  return response.text

def regenerate_response(query, emailid, prev_response):
  str1= "this was your previous response " + prev_response +"but i need it to be better"
  response = model.generate_content(str1+"generate me a reply email for this emailid" + emailid + "and its query in a formal way on the behalf of customerservice.provide our name as contactcenter" +query)
  return response.text

def write_content(question):
  prompt1 = "you are a assisstant to the customersupport agent and callcenter agent  "
  response = model.generate_content(prompt1 + "generate me a straightforward answer for this question " + question + "asked by the agent to have efficient conversations" )
  return response.text



