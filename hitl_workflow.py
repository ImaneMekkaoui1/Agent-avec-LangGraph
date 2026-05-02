import time
import uuid

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint, task
from langgraph.types import interrupt, Command


# -------------------------
# Task : générer un texte
# -------------------------
@task
def write_essay(topic: str) -> str:
    time.sleep(1)
    return f"Essay draft about {topic}"


# -------------------------
# Workflow principal
# -------------------------
@entrypoint(checkpointer=InMemorySaver())
def workflow(topic: str) -> dict:

    # Génération du draft
    draft = write_essay(topic).result()

    # Pause pour validation humaine
    approved = interrupt({
        "draft": draft,
        "action": "approve or reject"
    })

    # Résultat final
    return {
        "draft": draft,
        "approved": approved
    }


# -------------------------
# Exécution
# -------------------------
if __name__ == "__main__":

    thread_id = str(uuid.uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    print("=== Première exécution ===")
    for item in workflow.stream("cats", config):
        print(item)

    print("\n=== Reprise ===")
    for item in workflow.stream(Command(resume=True), config):
        print(item)