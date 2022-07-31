teflo_datarouter_api_plugin
=======================

teflo_datarouter_api_plugin is an importer plugin used by Teflo which allows teflo
to import logs to DataRouter by calling the DataRouter API.

NOTE:
    This plugin is supported only on Python 3 environments.

Based on the input provided by Teflo's `Scenario Descriptor File (SDF) 
<https://teflo.readthedocs.io/en/latest/users/scenario_descriptor.html>`_, 
the teflo_datarouter_api_plugin does the following:

1. Creates access token for the data router API.
2. Send requests to datarouter api.

Please refer Data Router Documentation to get more information.

Install the importer plugin from source
=======================================

Teflo tool gets installed as a part of the plugin installation

.. code-block:: bash

    # for ansible modules requiring selinux, you will need to enable system site packages
    $ virtualenv --system-site-packages droute
    $ source droute/bin/activate
    (droute) $ pip install teflo_datarouter_plugin@git+https://github.com/RedHatQE/teflo_datarouter_api_plugin.git@<tagged_branch>


For more informetion about datarouter api plugin please refer `Here <https://github.com/RedHatQE/teflo_datarouter_api_plugin/blob/master/docs/user.md>`_.

Teflo Compatibility Matrix
===========================

The table below lists out the released Teflo version and supported teflo_datarouter_api_plugin versions.
This matrix will track n and n-2 teflo releases

.. list-table:: Teflo plugin matrix for n and n-1 releases
    :widths: auto
    :header-rows: 1
    :stub-columns: 1

    *   - Teflo Release
        - 2.2.6

    *   - teflo_datarouter_api_plugin
        - 1.0.0

    *   - droute-api
        - 1.0.0

