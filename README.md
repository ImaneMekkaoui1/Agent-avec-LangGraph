Rapport de TP : Agent Intelligent avec LangGraph
Module : Systèmes Multi-Agents (SMA) et IAD

Formation : Master SDIA

Encadré par : Prof. RETAL SARA

🎯 Objectif du TP
Ce travail pratique a pour objectif de concevoir un agent intelligent capable de raisonnement autonome en utilisant LangGraph. L'accent est mis sur la transition d'un modèle de langage passif vers un système dynamique capable de :

Interagir avec des outils externes (Tools).

Gérer un état conversationnel complexe via un graphe d'états.

Intégrer une validation humaine avant action (Human-In-The-Loop).

Gérer la persistance, la reprise après interruption et le "Time Travel" (modification d'états passés).

📋 Table des matières
Configuration du LLM local et des Outils

Construction de l'Agent comme Graphe

Workflow avec Validation Humaine (HITL)

Agent Avancé : Persistance, Interruption et Forking

🛠 Partie 1 : LLM local avec outils (Tools) 
Dans cette étape, nous configurons un modèle Llama 3.2 via Ollama et définissons des outils mathématiques simples que le modèle pourra appeler.

Points clés :

Utilisation du décorateur @tool pour transformer des fonctions Python en outils exploitables par le LLM.

Liaison des outils au modèle via model.bind_tools().

Python
# Extrait du fichier tools_setup.py
@tool
def add(a: int, b: int) -> int:
    """Ajoute deux entiers."""
    return a + b

tools = [add, multiply, divide]
model_with_tools = model.bind_tools(tools)
🧠 Partie 2 : Agent comme nœud de LangGraph 
L'agent est ici structuré comme un StateGraph. Contrairement à une simple chaîne, le graphe permet des cycles (boucles de réflexion).

Structure de l'État (AgentState)
L'état est l'objet qui circule entre les nœuds. Il contient :

messages : L'historique des échanges (avec concaténation automatique via Annotated[list, add]).

llm_calls : Un compteur pour suivre l'activité du modèle.

Les Nœuds du Graphe
llm_call : Le cerveau de l'agent qui décide s'il faut répondre ou appeler un outil.

tool_node : L'exécuteur qui traite les demandes d'outils et renvoie les résultats.

should_continue : La logique conditionnelle qui oriente le flux.

⏳ Partie 3 : Workflow avec Validation Humaine (HITL) 
Cette partie introduit le concept de Human-In-The-Loop. Le workflow s'arrête (interrupt) pour permettre à un humain d'approuver ou de rejeter une action.

@task : Isole une unité d'exécution.

@entrypoint : Définit le point d'entrée du workflow avec un gestionnaire de sauvegarde (checkpointer).

Python
@entrypoint(checkpointer=InMemorySaver())
def workflow(topic: str) -> dict:
    draft = write_essay(topic).result()
    # Le graphe s'arrête ici et attend une action externe
    approved = interrupt({"draft": draft, "action": "approve or reject"})
    return {"draft": draft, "approved": approved}
🚀 Partie 4 : Agent Avancé (Persistance et Time Travel) 
La dernière partie combine toutes les fonctionnalités pour créer un agent robuste capable de gérer des scénarios de production.

Fonctionnalités implémentées :
Persistance (Checkpointer) : Utilisation de InMemorySaver pour sauvegarder chaque étape du graphe dans un thread_id.

Interruption Systématique : L'agent s'arrête avant chaque exécution d'outil (approve_node) pour demander une confirmation.

Reprise d'exécution : Utilisation de Command(resume=True/False) pour relancer le graphe après une interruption.

Modification d'état (Forking) : Capacité de récupérer un état passé (get_state_history), de le modifier (update_state) et de relancer l'agent à partir de cette nouvelle branche.

Exemple de processus de Forking :
Python
# Récupération d'un checkpoint précédent
history = list(agent.get_state_history(config_reject))
picked = history[1]

# Création d'un nouvel état modifié (Fork)
new_config = agent.update_state(picked.config, values={"messages": [...]})
forked = agent.invoke(None, new_config)
🧪 Comment tester le projet
Prérequis :

Installer Ollama et télécharger Llama 3.2 (ollama run llama3.2).

Installer les dépendances : pip install langgraph langchain_ollama.

Exécution :

Lancer les scripts pour observer le streaming des messages.

Tester l'interruption en fournissant une réponse à l'agent lorsqu'il est en pause.

Consulter l'historique des checkpoints pour vérifier la persistance.

📌 Conclusion
Ce TP a permis de comprendre que le développement d'agents ne se limite pas à l'envoi de prompts. Grâce à LangGraph, nous avons pu implémenter une logique de contrôle fine, garantissant la fiabilité des agents via la persistance et l'intervention humaine, éléments essentiels pour des systèmes d'IA distribués et robustes.
