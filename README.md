# Rapport de TP : Agent Intelligent avec LangGraph

**Module :** Systèmes Multi-Agents (SMA) et IAD  
**Formation :** Master SDIA  
**Encadré par :** Prof. RETAL SARA  

---

## Résumé

Ce TP présente la conception d’un agent intelligent basé sur **LangGraph**.

L’agent est capable de :

- raisonner de manière itérative,
- appeler automatiquement des outils externes,
- interrompre son exécution pour validation humaine,
- reprendre après interruption,
- conserver un historique complet de ses états,
- revenir à un ancien état pour explorer d’autres trajectoires d’exécution.

L’objectif principal est de comprendre comment transformer un simple modèle de langage en un **agent structuré, contrôlable et traçable**.

---

## Objectif

Ce TP a pour objectif de découvrir la construction d’agents intelligents avec **LangGraph** en combinant :

- un **LLM local** (Llama 3.2 via Ollama),
- des **tools** (fonctions Python externes),
- un **workflow orienté graphe** (`StateGraph`),
- le mécanisme **HITL (Human-In-The-Loop)** pour la validation humaine,
- la **sauvegarde d’état** (*checkpoints*),
- la **reprise d’exécution** (*time travel*).

---

## Table des matières

1. [Environnement technique](#environnement-technique)
2. [Architecture globale](#architecture-globale)
3. [Partie 1 : LLM local avec outils (Tools)](#partie-1--llm-local-avec-outils-tools)
4. [Partie 2 : Agent comme nœud de LangGraph](#partie-2--agent-comme-nœud-de-langgraph)
5. [Partie 3 : Workflow HITL (Human-In-The-Loop)](#partie-3--workflow-hitl-human-in-the-loop)
6. [Partie 4 : Agent avancé, persistance et forking](#partie-4--agent-avancé-persistance-et-forking)
7. [Résultats obtenus](#résultats-obtenus)
8. [Concepts appris](#concepts-appris)
9. [Conclusion](#conclusion)

---

## Environnement technique

### Technologies utilisées

| Technologie | Rôle |
|---|---|
| Python | Langage principal |
| LangGraph | Orchestration du workflow |
| LangChain | Gestion du LLM et des tools |
| Ollama | Exécution locale du modèle |
| Llama 3.2 | Modèle de langage |
| python-dotenv | Chargement des variables d’environnement |

### Installation

```bash
uv venv
uv pip install langgraph langchain langchain-ollama python-dotenv 
````
### Téléchargement du modèle local

```
ollama pull llama3.2:3b
````
### Architecture globale

L’agent suit le cycle suivant :
```
Utilisateur
   ↓
LLM
   ↓
Décision :
outil nécessaire ?
   ├── Non → réponse finale
   └── Oui
          ↓
      validation humaine
          ↓
      exécution du tool
          ↓
      retour au LLM
```
Cette architecture permet :

* une prise de décision progressive,
* un contrôle humain,
* une traçabilité complète de l’exécution

# Partie 1 — LLM local avec outils (Tools)
Nous définissons les capacités de l’agent dans tools_setup.py.
Les outils sont des fonctions Python pures que le LLM peut invoquer.
```@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b
```
Le modèle est ensuite lié à ces outils via model.bind_tools(tools), 
lui permettant de structurer ses sorties pour appeler ces fonctions.

# Partie 2 — Agent comme nœud de LangGraph
Ici, nous définissons le cœur du système sous forme de StateGraph.

- AgentState : Un dictionnaire qui maintient la mémoire de l'agent (messages) et des métadonnées (compteur d'appels LLM).

- Nœud llm_call : Invoque le LLM avec le contexte actuel.

- Nœud tool_node : Exécute les appels d'outils détectés dans les messages du LLM.

- Cycle : Le graphe utilise des arêtes conditionnelles pour décider s'il doit continuer à utiliser des outils ou s'arrêter.

# Partie 3 — Workflow HITL (Human-In-The-Loop)
Cette partie implémente la sécurité via l'interruption. Le workflow utilise les décorateurs @task et @entrypoint de LangGraph.

* Fonction interrupt() : Met l'exécution en pause et attend une entrée utilisateur.

* Checkpointer : Utilise InMemorySaver() pour sauvegarder l'état du thread, permettant de reprendre l'exécution avec Command(resume=True) sans perdre le contexte.

# Partie 4 — Agent avancé, persistance et forking
La phase finale combine l'autonomie et le contrôle total sur l'historique :

* Persistance des Threads : Chaque conversation possède un thread_id unique.

* Contrôle d'Action : Un nœud approve_node intercepte les intentions du LLM, affiche les outils qu'il souhaite utiliser, et attend un "OK" humain.

* Time Travel & Forking :

   - Nous explorons l'historique via agent.get_state_history(config).

   - Nous pouvons "remonter le temps" vers un état précédent, modifier un message ou une variable, et relancer une nouvelle branche             d'exécution (Fork).
 
* Résultats obtenus
L'agent développé est capable de :

- Gérer des calculs arithmétiques complexes de manière autonome.

- Afficher son raisonnement en streaming (mode updates ou messages).

- Garantir qu'aucune action externe n'est effectuée sans validation humaine.

- Gérer des sessions multiples grâce à la persistance.

## Concepts appris
* Programmation Orientée Graphe : Gérer la logique de l'IA via des nœuds et des arêtes.

* Human-In-The-Loop : Intégrer l'humain comme une étape critique du workflow.

* Gestion d'État (State Management) : Manipuler l'historique et les variables de session de manière immuable.

* Persistance : Sauvegarder et restaurer des états d'agent.

## Conclusion
Ce TP démontre la puissance de LangGraph pour orchestrer des systèmes d'IA complexes. En dépassant le simple chat, nous avons créé un agent capable de collaborer avec l'humain tout en utilisant des outils de manière structurée et sécurisée.
