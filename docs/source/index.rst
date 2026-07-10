.. clbmtaichi documentation master file, created by
   sphinx-quickstart on Fri Jul  3 21:15:58 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. meta::
   :description: [Taichi-accelerated cumulant LBM simulator]

clbmtaichi documentation
========================

.. admonition:: github repository

   find the project@ `github <https://github.com/hayashi-workshop/clbmtaichi/blob/main/README.md>`_


.. toctree::
   :maxdepth: 1
   :caption: Contents:

   examples
   models/index
   kernels
   nested
   tips
   reference

.. raw:: html

   <br>

.. figure:: https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/nested_vtk.png
   :width: 100%
   :align: center
   :alt: nested.png

Installation
------------
Using anaconda virtual environment is highly recommended. Here, we create a new environment ``taichi_env``: 

.. code-block:: bash

   conda create -n taichi_env python=3.10 -y

Activate ``taichi_env``

.. code-block:: bash

   conda activate taichi_env

Clone the repository onto your local machine. 

.. code-block:: bash

   git clone https://github.com/hayashi-workshop/clbmtaichi.git

Get into the cloned repo. 

.. code-block:: bash

   cd clbmtaichi

Export the current directory path as environment variable for convenience. Not mandatory. 

.. code-block:: bash

   export REPO_PATH=$(pwd)

Install requirements (taichi and some basic packages)

.. code-block:: bash

   pip install -r requirements.txt

You are ready to run ``clbmtaichi``!

.. code-block:: bash

   python main.py run
