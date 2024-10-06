# Le nom
ScEnaRIO ORCHestrator. Voilà.

# Workflow
- Démarrer un project avec `serior init`, ou `serior unravel FICHIER` si reprise d'un scénario existant
- Renseigner tous les records (vues/oc/styles/options) dans le squelette, faire `serior build`, mettre à jour le module
- Continuer le développement, utiliser `serior inject` pour mettre à jour les records en bdd sans mettre à jour le module
- Faire un dernier `serior build`, s'assurer que le scénario passe la màj
- Commit le scénario
