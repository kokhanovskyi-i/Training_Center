HR Hospital
===========

HR Hospital is an educational Odoo module for managing hospital-related data.

The module allows users to manage patients, doctors, doctor categories, diseases,
appointments, personal doctor history, reports, access rights, translations, and
basic medical workflows.

Features
--------

* Manage patients with personal, contact, and medical information.
* Manage doctors with specialties, categories, mentors, and interns.
* Manage doctor categories.
* Manage disease classifier with hierarchical diseases.
* Manage appointments between patients and doctors.
* Track appointment status: planned, done, and cancelled.
* Track personal doctor assignment history.
* Reassign personal doctors using a wizard.
* Generate visit and disease reports using wizards.
* Generate a printable doctor report in PDF format.
* Use kanban views for doctors.
* Use dedicated HR Hospital security groups and access rules.
* Provide Ukrainian translation for the module and disease classifier.
* Include automated model tests.

Security Groups
---------------

The module provides the following user groups:

* Patient
* Intern
* Doctor
* Manager
* Administrator

Access rights are configured according to the role hierarchy.

Patients can view only their own visits.
Interns can view and edit their own visits.
Doctors can view and edit their own visits and visits of their interns.
Managers can view all visits.
Administrators can delete any data in the module.

Technical Information
---------------------

Module name: ``hr_hospital``

Odoo version: ``19.0``

License: ``OPL-1``

Author
------

Ivan Kokhanovskyi