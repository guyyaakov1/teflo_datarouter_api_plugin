teflo_datarouter_api_plugin
=======================

teflo_datarouter_api_plugin is an importer plugin used by Teflo which allows teflo
to import xunit files and logs to DataRouter by calling the DataRouter API.

NOTE:
    This plugin is supported only on Python 3.9 and above.

Please refer Data Router Documentation to get more information.

Install the importer plugin from source
=======================================

Teflo tool gets installed as a part of the plugin installation

.. code-block:: bash

    # for ansible modules requiring selinux, you will need to enable system site packages
    $ virtualenv --system-site-packages droute
    $ source droute/bin/activate
    (droute) $ pip install teflo_datarouter_plugin@git+https://github.com/RedHatQE/teflo_datarouter_api_plugin.git@<tagged_branch>


For more information about datarouter api plugin please refer `User Guide <https://github.com/RedHatQE/teflo_datarouter_api_plugin/blob/master/docs/user.md>`_.

