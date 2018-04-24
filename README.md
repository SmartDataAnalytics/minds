MINDS
=====

> MINDS - Maths INsiDe SPARQL

Description
-----------

This project provides __MINDS__: a tool which is able to translate
mathematical expressions into [SPARQL
1.1](https://www.w3.org/TR/sparql11-overview/) bindings. In a
nutshell, MINDS provides a python script which is able to parse
mathematical formulae and then translates recursively the discovered
patterns into SPARQL compliant sequences.

Dependencies
------------

The translator has been currently tested with python version
__2.7.12__. In addition, it requires the use of external scripts
(which are all embedded locally inside this repository) for specific
tasks:

- __Lexing__ and __Parsing__ the maths expressions is done using the
  [ply](https://github.com/dabeaz/ply) library.

- __Coloring__ the terminal inside the python-shell is done using
  [colorama](https://github.com/tartley/colorama) which presents the
  advantage of coloring python-shells on multiple platforms!

How-To
------

__MINDS__ provides currently a command-line interface which can be
launched from the terminal.

License
-------

This project is openly shared under the terms of the __Apache License
v2.0__ [here](./LICENSE).


