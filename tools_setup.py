from langchain.tools import tool
from langchain_ollama import ChatOllama
from dotenv import load_dotenv

# Charger les variables d'environnement (OpenAI, Groq, etc. si utilisé)
load_dotenv()

# Initialisation du modèle Ollama
model = ChatOllama(
    model="llama3.2:3b",  # tu peux changer : mistral, gemma, etc.
)

# ---------------------------
# Définition des tools
# ---------------------------

@tool
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b


@tool
def divide(a: int, b: int) -> float:
    """Divide two integers."""
    return a / b


# ---------------------------
# Préparation des tools
# ---------------------------

tools = [add, multiply, divide]

# dictionnaire pour accès rapide par nom
tools_by_name = {t.name: t for t in tools}

# liaison du modèle avec les tools
model_with_tools = model.bind_tools(tools)

