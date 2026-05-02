apport de TP : Systèmes Multi-Agents (SMA) & IAD
Master SDIA | Année Universitaire 2025-2026 Professeur : Mme RETAL SARA

📌 Présentation du Projet
Ce TP porte sur la conception et l'implémentation d'agents intelligents en utilisant la bibliothèque LangGraph. L'objectif est de passer d'un simple appel à un modèle de langage (LLM) vers un système capable de raisonnement cyclique, d'utilisation d'outils (Tools), et d'intégration d'une validation humaine dans la boucle (Human-in-the-loop).

Technologies utilisées
LangGraph : Framework pour orchestrer des agents sous forme de graphes d'états.

LangChain : Interface pour la manipulation des LLMs et des outils.

Ollama (Llama 3.2:3b) : Exécution locale du modèle de langage.

Python 3.10+

🛠 Configuration de l'environnement
Avant de commencer, assurez-vous d'avoir installé les dépendances nécessaires :

Bash
pip install langchain_ollama langgraph python-dotenv typing_extensions
🗂 Structure du TP
PARTIE 1 : LLM local avec outils (Tools)
Dans cette phase, nous configurons le modèle de base et définissons des fonctions Python atomiques que le LLM pourra appeler dynamiquement.

Fichier : tools_setup.py

Définition des outils arithmétiques : add, multiply, divide.

Binding des outils au modèle via model.bind_tools(tools).

PARTIE 2 : Agent comme nœud de LangGraph
Nous transformons le LLM en un agent réactif au sein d'un graphe. Le graphe gère un état (AgentState) qui contient l'historique des messages et un compteur d'appels.

Architecture du Graphe
Node llm_call : Le LLM analyse la requête et décide s'il a besoin d'un outil.

Node tool_node : Exécute physiquement la fonction Python demandée.

Edge should_continue : Une fonction de contrôle qui oriente le flux vers la fin ou vers l'exécution d'un outil.

PARTIE 3 : Workflow avec Validation Humaine (HITL)
Cette section introduit le concept de Human-In-The-Loop. Le workflow génère une ébauche (draft) mais suspend son exécution via la fonction interrupt(), attendant une commande de validation (approve ou reject) de l'utilisateur avant de finaliser.

PARTIE 4 : TP Final - Agent Avancé
C'est la partie la plus complexe, intégrant la persistance et la gestion des états.

Fonctionnalités implémentées :
Checkpointer (InMemorySaver) : Permet de sauvegarder l'état du graphe à chaque étape.

Interruption Manuelle : Le graphe s'arrête systématiquement avant l'exécution d'un outil pour demander l'autorisation.

Time Travel (Forking) : Capacité de revenir sur un état précédent du graphe, de modifier les données et de relancer l'exécution depuis ce point.

🚀 Utilisation et Tests
Exécution de l'agent avec outils
Python
# Exemple de commande
result = agent.invoke({"messages": [HumanMessage(content="Add 3 and 4.")], "llm_calls": 0})
Gestion de l'interruption (Partie 4)
Lorsqu'un agent demande l'exécution d'un outil, il entre en état de pause.

Pour valider : Envoyer Command(resume=True).

Pour rejeter : Envoyer Command(resume=False).

Exploration de l'historique
Le code permet de visualiser les points de sauvegarde (checkpoints) :

Python
history = list(agent.get_state_history(config))
print(f"Nombre de points de sauvegarde : {len(history)}")
📝 Conclusion
Ce TP démontre la puissance de LangGraph pour transformer un LLM passif en un agent autonome et contrôlable. Nous avons appris à :

Orchestrer des cycles de réflexion (Reasoning loops).

Gérer un état persistant pour permettre la reprise après erreur.

Implémenter des barrières de sécurité via l'intervention humaine.

Note : Ce projet a été réalisé dans le cadre du module SMA & IAD sous la supervision de Prof. RETAL SARA.

Instructions pour le rendu
Clonez ce dépôt.

Assurez-vous que votre instance Ollama est active avec le modèle llama3.2.

Lancez le script principal pour observer les sorties dans la console.
