# Installation
Se mettre à la racine du repo, lancer `install.bash`.

Par la suite, le programme est disponible avec le nom `serior`.

# Workflow
- Démarrer un project avec `serior init`, ou `serior unravel FICHIER` si reprise d'un scénario existant
- Renseigner tous les records (vues/oc/styles/options) dans le squelette, faire `serior build`, mettre à jour le module
- Continuer le développement, utiliser `serior inject` pour mettre à jour les records en bdd sans mettre à jour le module
- Faire un dernier `serior build`, s'assurer que le scénario passe la màj
- Commit le scénario

# FAQ
## Le tag autour du fichier de data n'est pas le bon ! ALED !
Faire `serior config` ouvre le fichier de configuration.

Dedans, il faut changer l'entrée `surrounding_tag` par ce que vous voulez.

## Que signifie la clef "quirky" qui apparaît dans certains records ?
Elle indique que le nom/xml_id du record ne contient pas le préfixe du scénario.

Cela permet au programme de les traiter différemment pour prendre cette information en compte

## Le nom de ma vue principale ne contient pas le préfixe du scénario
Il ne faut pas utiliser la clef `main_view`, mais `quirky_main_view` dans ce cas

## Le nom de mon onchange initial ne contient pas le préfixe du scénario
Il ne faut pas utiliser la clef `init_oc`, mais `quirky_init_oc` dans ce cas

## Comment utiliser les xpath ? Quelle est la clef d'une vue où on renseigne la vue sur laquelle appliquer les xpaths ?
La clef est `inherit`

# Le nom
ScEnaRIO ORCHestrator. Voilà.
