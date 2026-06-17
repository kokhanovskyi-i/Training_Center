Training Center
===========

Training Center is an educational Odoo module for managing hospital-related data.

The module allows users to manage students, teachers, teacher categories, subjects,
lessons, main teacher history, reports, access rights, translations, and
basic medical workflows.

Features
--------

* Manage students with personal, contact, and medical information.
* Manage teachers with specialties, categories, mentors, and assistants.
* Manage teacher categories.
* Manage subject classifier with hierarchical subjects.
* Manage lessons between students and teachers.
* Track lesson status: planned, done, and cancelled.
* Track main teacher assignment history.
* Reassign main teachers using a wizard.
* Generate lesson and subject reports using wizards.
* Generate a printable teacher report in PDF format.
* Use kanban views for teachers.
* Use dedicated Training Center security groups and access rules.
* Provide Ukrainian translation for the module and subject classifier.
* Include automated model tests.

Security Groups
---------------

The module provides the following user groups:

* Student
* Assistant
* Teacher
* Manager
* Administrator

Access rights are configured according to the role hierarchy.

Students can view only their own lessons.
Assistants can view and edit their own lessons.
Teachers can view and edit their own lessons and lessons of their assistants.
Managers can view all lessons.
Administrators can delete any data in the module.

Technical Information
---------------------

Module name: ``training_center``

Odoo version: ``19.0``

License: ``OPL-1``

Author
------

Ivan Kokhanovskyi