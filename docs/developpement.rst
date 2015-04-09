=============
DEVELOPPEMENT
=============

Cette rubrique est destinée aux développeurs qui souhaiteraient...


Routes Symfony
--------------

Les routes sont accessibles dans le fichier ``conf/settings.ini.sample``

Lancer la commande : 

::

    ./install.sh --dev


Bla bla bla
-----------

The most minimal components required to run an instance are :

* PostGIS 2 server
* GDAL, GEOS, libproj
* gettext
* libfreetype
* libxml2, libxslt
* Usual Python dev stuff

A voir : `the list of minimal packages on Debian/Ubuntu <https://github.com/makinacorpus/Geotrek/blob/211cd/install.sh#L136-L148>`_.

.. note::

    En lancant ``env_dev`` et ``update`` is recommended after a pull of new source code,
    but is not mandatory : ``make serve`` is enough most of the time.