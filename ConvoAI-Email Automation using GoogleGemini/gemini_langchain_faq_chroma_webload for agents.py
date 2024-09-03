

import os
import getpass

os.environ['GOOGLE_API_KEY'] = getpass.getpass('Gemini API Key:')



from langchain import PromptTemplate
from langchain import hub
from langchain.docstore.document import Document
from langchain.document_loaders import WebBaseLoader
from langchain.schema import StrOutputParser
from langchain.schema.prompt_template import format_document
from langchain.schema.runnable import RunnablePassthrough
from langchain.vectorstores import Chroma


loader = WebBaseLoader("https://www.zendesk.com/in/blog/10-best-call-center-etiquette-tips-support-agents/")
docs = loader.load()



# Extract the text from the website data document
text_content = docs[0].page_content

# The text content between the substrings "code, audio, image and video." to
# "Cloud TPU v5p" is relevant for this tutorial. You can use Python's `split()`
# to select the required content.
text_content_1 = text_content.split("code, audio, image and video.",1)[1]
final_text = text_content_1.split("Cloud TPU v5p",1)[0]

# Convert the text to LangChain's `Document` format
docs =  [Document(page_content=final_text, metadata={"source": "local"})]

#Initialize Gemini's embedding model

from langchain_google_genai import GoogleGenerativeAIEmbeddings



gemini_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

"""### Store the data using Chroma

To create a Chroma vector database from the website data, you will use the `from_documents` function of `Chroma`. Under the hood, this function creates embeddings from the documents created by the document loader of LangChain using any specified embedding model and stores them in a Chroma vector database.  

 You have to specify the `docs` you created from the website data using LangChain's `WebBasedLoader` and the `gemini_embeddings` as the embedding model when invoking the `from_documents` function to create the vector database from the website data. You can also specify a directory in the `persist_directory` argument to store the vector store on the disk. If you don't specify a directory, the data will be ephemeral in-memory.

"""

# Save to disk
vectorstore = Chroma.from_documents(
                     documents=docs,                 # Data
                     embedding=gemini_embeddings,    # Embedding model
                     persist_directory="./chroma_db" # Directory to save data
                     )

"""### Create a retriever using Chroma

create a retriever that can retrieve website data embeddings from the newly created Chroma vector store. This retriever can be later used to pass embeddings that provide more context to the LLM for answering user's queries.
You can then invoke the `as_retriever` function of `Chroma` on the vector store to create a retriever.
"""

# Load from disk
vectorstore_disk = Chroma(
                        persist_directory="./chroma_db",       # Directory of db
                        embedding_function=gemini_embeddings   # Embedding model
                   )

retriever = vectorstore_disk.as_retriever(search_kwargs={"k": 1})


print(len(retriever.get_relevant_documents("MMLU")))

# Generator




from langchain_google_genai import ChatGoogleGenerativeAI


llm = ChatGoogleGenerativeAI(model="gemini-pro",
                 temperature=0.7, top_p=0.85)



# Prompt template to query Gemini
llm_prompt_template = """You are an assistant for customersupport agents question-answering tasks.
Use the following context to answer the question.
If you don't know the answer, just say that you don't know.
Use five sentences maximum and keep the answer concise.\n
Question: {question} \nContext: {context} \nAnswer:"""

llm_prompt = PromptTemplate.from_template(llm_prompt_template)

#print(llm_prompt)



# Combine data from documents to readable string format.
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | llm_prompt
    | llm
    | StrOutputParser()
)

"""### Prompt the model

You can now query the LLM by passing any question to the `invoke()` function of the stuff documents chain you created previously.
"""

rag_chain.invoke("What should be the first step?")

