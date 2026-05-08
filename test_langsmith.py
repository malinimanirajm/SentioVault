from dotenv import load_dotenv
load_dotenv()

from langsmith import traceable

@traceable
def hello():
    return "hello"

print(hello())