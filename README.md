# Rapport de TP : Agent Intelligent avec LangGraph

**Module :** Systèmes Multi-Agents (SMA) et IAD  
**Formation :** Master SDIA  
**Encadré par :** Prof. RETAL SARA  

---

## 🎯 Objectif

Ce TP a pour objectif de découvrir la construction d’agents intelligents avec **LangGraph** en combinant :

- Un **LLM local** (Llama 3.2 via Ollama)
- Des **tools** (fonctions Python externes)
- Un **workflow orienté graphe** (StateGraph)
- Le mécanisme **HITL (Human-In-The-Loop)** pour la validation humaine
- La **sauvegarde d’état** (Checkpoints) et la **reprise d’exécution** (Time Travel)

---

## 📋 Table des matières
1. [Partie 1 : LLM local avec outils (Tools)](#partie-1)
2. [Partie 2 : Agent comme nœud de LangGraph](#partie-2)
3. [Partie 3 : Workflow HITL (Human-In-The-Loop)](#partie-3)
4. [Partie 4 : Agent Avancé, Persistance et Forking](#partie-4)

---

## 🛠 Partie 1 : LLM local avec outils (Tools) <a name="partie-1"></a>

L'étape initiale consiste à définir les capacités de notre agent. Nous utilisons `langchain_ollama` pour piloter un modèle local et `@tool` pour exposer des fonctions arithmétiques.

**Fichier : `tools_setup.py`**
- **Modèle utilisé :** `llama3.2:3b`
- **Outils :** Addition, Multiplication, Division.
- **Principe :** Le modèle est "lié" aux outils via `bind_tools`, ce qui lui permet de générer des requêtes d'appel de fonctions au lieu de simples réponses textuelles.

---

## 🧠 Partie 2 : Agent comme nœud de LangGraph <a name="partie-2"></a>

Ici, nous définissons l'architecture cyclique de l'agent. Contrairement à une chaîne linéaire, l'agent peut boucler sur lui-même tant qu'il estime avoir besoin d'outils.

### Composants clés :
- **AgentState :** Un dictionnaire typé qui maintient l'historique des messages et un compteur `llm_calls`.
- **Nœud `llm_call` :** Appelle le LLM pour décider de la prochaine action.
- **Nœud `tool_node` :** Exécute les fonctions si le LLM a généré des `tool_calls`.
- **Arête conditionnelle `should_continue` :** Détermine si le flux doit aller vers l'exécution d'un outil ou se terminer (`END`).

---

## ⏳ Partie 3 : Workflow HITL (Human-In-The-Loop) <a name="partie-3"></a>

Cette partie introduit la validation humaine dans le workflow. Grâce aux décorateurs `@task` et `@entrypoint`, nous créons un flux capable de s'interrompre.

- **Mécanisme :** La fonction `interrupt()` met le graphe en pause.
- **Persistance :** `InMemorySaver` permet de mémoriser l'état à l'endroit exact de l'interruption.
- **Reprise :** L'exécution reprend via `Command(resume=True)`, permettant à l'humain de valider le contenu généré avant sa finalisation.

---

## 🚀 Partie 4 : Agent Avancé, Persistance et Forking <a name="partie-4"></a>

Le TP final implémente un agent complet capable de gérer des erreurs, des refus humains et des retours dans le passé.

### Fonctionnalités avancées :
1. **Gestionnaire de sauvegarde (Checkpointer) :** Chaque étape est enregistrée sous un `thread_id`. Cela permet de fermer l'application et de reprendre plus tard.
2. **Nœud d'approbation (`approve_node`) :** Une étape de contrôle qui intercepte les appels d'outils avant leur exécution réelle.
3. **Time Travel & Forking :** - Nous récupérons l'historique des états via `get_state_history`.
   - Nous pouvons "forker" (bifurquer) à partir d'un état ancien en utilisant `update_state`, ce qui permet de tester différents scénarios à partir d'un même point de départ.

### Exemple de processus de Forking :
```python
# Récupération d'un checkpoint précédent dans l'historique
history = list(agent.get_state_history(config))
old_state = history[1]

# Création d'une nouvelle branche d'exécution
new_config = agent.update_state(old_state.config, values={"messages": [...]})
agent.invoke(None, new_config)
