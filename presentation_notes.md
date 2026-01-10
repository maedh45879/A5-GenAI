# Fiche de presentation orale - LLM Council Local Deployment

## 1. Introduction orale
- Contexte: projet final, demo live sans support
- Inspiration: base Karpathy LLM Council
- Objectif principal: council de LLMs 100% local et distribue

## 2. Probleme initial et motivation
- Limites d un seul LLM: biais, angle unique, erreurs non corrigees
- Limites cloud: cout, dependance reseau, latence, confidentialite
- Interet council: diversite, auto critique, aggregation
- Pourquoi local distribue: autonomie, reproductibilite, controle

## 3. Presentation generale de l application (vision utilisateur)
- L utilisateur pose une question unique
- Plusieurs LLMs repondent en parallele
- L interface montre les sorties intermediaires
- Le jury verra tout le workflow en direct

## 4. Demonstration live - Workflow officiel du council
- Stage 1 First Opinions
- Soumission de la requete
- Reponses independantes des LLMs
- Inspection rapide des reponses par onglets
- Stage 2 Review and Ranking
- Anonymisation des reponses
- Classement + justification par chaque modele
- Stage 3 Chairman Final Answer
- Chairman separe, synthese finale unique
- Points a faire observer: anonymisation, scores, synthese

## 5. Architecture globale (explication orale, sans schema)
- Separation Council LLMs et Chairman
- Execution locale des modeles (Ollama ou equivalent)
- Communication via REST APIs entre services
- Tout peut tourner sur une seule machine

## 6. Transition vers le code
- Ce que la demo vient de prouver
- On passe a l implementation: services, workflow, orchestration

## 7. Organisation du code
- Backend services
- Gestion des modeles LLM locaux
- Workflow en 3 stages isole et respect strict
- Communication entre services via REST

## 8. Points techniques obligatoires a expliquer
- Suppression des APIs cloud
- Inference locale
- Chairman separe du council
- Workflow end to end respecte
- Inspection des sorties intermediaires

## 9. Choix techniques et decisions de conception
- Choix des modeles: diversite, taille, vitesse
- Architecture distribuee simple et claire
- Compromis: latence vs qualite, ressources locales

## 10. Ameliorations par rapport a Karpathy original
- Retrait dependance OpenRouter
- Execution locale complete
- Ajout REST APIs et separation services
- Meilleure transparence via inspection intermediaire

## 11. Limites actuelles du projet
- Contraintes materiel: RAM, GPU, CPU
- Latence sur certaines questions
- Scalabilite limitee en local

## 12. Pistes d amelioration
- Monitoring et health checks avances
- UI plus riche pour l analyse
- Optimisation perf et caching
- Tracking des performances par modele

## 13. Conclusion orale
- Objectifs des consignes atteints
- Projet montre une architecture distribuee locale
- Apprentissages: orchestration, LLMs locaux, workflow council
