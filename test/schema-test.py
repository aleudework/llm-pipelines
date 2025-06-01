from pydantic import BaseModel
from typing import List
import lmstudio as lms

# Enkelt objekt
class BookSchema(BaseModel):
    title: str
    author: str
    year: int
    stars: int

# Wrapper til en liste af objekter
class BookList(BaseModel):
    books: List[BookSchema]

model = lms.llm("meta-llama-3.1-8b-instruct")


result = model.respond(
    "List 3 famous fantasy books as JSON under the key 'books', each with title, author, year and stars (1–5):",
    response_format=BookList
)

# Gå igennem listen
print(result.parsed['books'][1]['author'])

print('#######')

print(result)