Ymir 1.2 Syntax specification
=============================

Introduction
------------

This document describes the *syntactic structure* of the Ymir programming
language. It is derived from the reference implementation of the syntax visitors
in the Ymir compiler.

The syntax layer is responsible for:
- transforming token streams into syntax trees,
- enforcing grammar rules,
- validating structural correctness,
- producing well-formed AST nodes for semantic analysis.

Structure of the Specification
------------------------------

The syntax is divided into the following components:

1. Global structure and modules
2. Declarations
3. Types (class, record, entity)
4. Traits
5. Enums
6. Unions
7. Def declarations
8. Functions
9. Macros
10. Expressions and instructions

Each section corresponds to a visitor in the implementation.

.. toctree::
   :maxdepth: 1

   global
   type   
   trait
   enum
   union
   def
   function
   macro
   expression
