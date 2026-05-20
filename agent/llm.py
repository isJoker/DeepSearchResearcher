import os
import dotenv
from langchain.chat_models import init_chat_model

dotenv.load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
os.environ['OPENAI_BASE_URL'] = os.getenv('OPENAI_BASE_URL')

model = init_chat_model(
    model='gpt-4o-mini'
)