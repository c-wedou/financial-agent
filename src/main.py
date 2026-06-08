from langchain_core.messages import HumanMessage
from src.agent import app
import uuid
from config import MAX_ITERATIONS
question = input("Je suis à votre dispostion pour générer n'importe quel rapport financier d'une entreprise.\n\n\n\n\n Quelle est l'entreprise sur laquelle veux-tu faire un rapport :\t")
thread_id = str(uuid.uuid4())
result = app.invoke({
    "messages" : [HumanMessage(content=question)]},
    {"configurable" :{"thread_id" : thread_id}, "recursion_limit": MAX_ITERATIONS}
)

print(result["messages"][-1].content)