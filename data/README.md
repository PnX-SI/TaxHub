A partir de la version 1.9.0 de TaxHub, sa BDD et ses évolutions sont gérés par Alembic dans ``apptax/migrations/``.

Les fichiers de création initiale du schéma ``taxonomie`` n'évoluent plus directement, car ce sont les migrations Alembic qui se chargent des modifications de la BDD.
