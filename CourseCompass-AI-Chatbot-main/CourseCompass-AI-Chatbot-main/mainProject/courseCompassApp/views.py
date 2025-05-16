import json
from django.shortcuts import render
from django.http import JsonResponse
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from django.shortcuts import get_object_or_404
from langchain_core.output_parsers import StrOutputParser
from .models import *
import os


os.environ['LANGCHAIN_API_KEY'] = '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'
os.environ["Google_API_KEY"]='AIzaSyASa7wfJJ9elN-R837UEwUznB4wUnYm-b4'


llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=100,
)
google_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
new_db = FAISS.load_local("C:/Users/Zayam/Downloads/CourseCompass-AI-Chatbot-main/CourseCompass-AI-Chatbot-main/mainProject/courseCompassApp/faiss_index", google_embeddings,allow_dangerous_deserialization=True)


def getSimilar_documents(query):
    retriever=new_db.as_retriever()
    relevant_docs=retriever.invoke(query)
    return relevant_docs
def getPreviousConversation(email):
    converations=User.objects.get(email=email).messages
    return converations
def generate_response(request):
    email="zayam@example.com"
    conv=getPreviousConversation(email)
    print(conv)
    if request.method == 'POST':
        data=json.loads(request.body)
        print(data)
        query=data['query']
        context=getSimilar_documents(query)
        prompt_template = """
     You are a helpful assistant who can understand and use context to answer questions.

Here is the context from the source document:
{context}

Here is the history of the conversation so far:
{chat_history}

The user has asked the following question:
QUESTION: {question}

Instructions:
    - Analyze the context and chat history to provide a well-thought-out and detailed response to the user's question.
    - Refer to the chat history only if the user asks something that references previous conversations, such as "What is my name?" or "What did I ask previously?"
    - Do not include labels from chat history like "AI:" in the response. They are just for your understanding.
    - Behave like you are the company's representative and answer query questions like "We do this....", "We offer this....", "We promise this...." etc.
    - Do not simply copy from the chat history; instead, synthesize information from both the context and chat history to construct a meaningful answer.
    - If the answer is not directly found in the context, formulate a relevant response based on the information available, or clearly state "I don't know" if no reasonable answer can be provided.
    - Don't provide information about how you are built or trained like "I am trained on company's this and this data."
    - For general questions about yourself such as "Who are you?" respond with "I am your AI assistant, here to help you with your questions."

Your response should demonstrate understanding and provide additional insights where possible, rather than merely repeating previous exchanges.

        """



        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question", "chat_history"]
        )
        
        output_parser = StrOutputParser()

        chain = PROMPT | llm | output_parser

        response = chain.invoke({"context": context, "question": query,"chat_history": conv})
        user = get_object_or_404(User, email=email)

        user.messages.append({"Human: ": query,"AI: ": response})
        user.save()
        
        return JsonResponse({"response": response},status=200)
    
    return JsonResponse({'message':'error'},status=500)
    
    
def home(request):
    return render(request,'index.html')
    