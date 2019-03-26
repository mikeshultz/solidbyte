#######
Install
#######

*******************
System Requirements
*******************

Some system level depenencies are required first for Solidbyte to work.  Python >= 3.6 is required.

=====
Linux
=====

------
Ubuntu
------

.. code-block:: bash

    apt install python3.6 libssl-dev libffi-dev

----------
Arch Linux
----------

.. code-block:: bash

    pacman -S openssl libffi

NOTE: python3 should already be installed on your system.

-----------
REHL/CentOS
-----------

.. code-block:: bash

    yum install openssl-devel libffi-devel

-------
Windows
-------

*TBD.  Please submit a pull request if you figure it out.*

---
OSX
---

*TBD. Please submit a pull request if you figure it out.*


********************
Installing Solidbyte
********************

Install it with system python:

.. code-block:: bash

    pip install --user solidbyte

Or, with a virtual environment:

.. code-block:: bash

    python -m venv ~/virtualenvs/solidbyte
    source ~/virtualenvs/solidbyte/bin/activate
    pip install solidbyte
