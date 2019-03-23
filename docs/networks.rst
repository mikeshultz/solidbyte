############
networks.yml
############

:code:`networks.yml` is the `YAML <http://yaml.org>`_ file you use to configure
connections to Ethereum JSON-RPC providers and nodes.  Some templates may 
provide some pre-configured connections.

************
Example File
************

.. code-block:: yaml

    # networks.yml
    ---
    dev:
      type: auto

    infura-mainnet:
      type: websocket
      url: wss://mainnet.infura.io/ws

    geth:
      type: ipc
      file: ~/.ethereum/geth.ipc

    test:
      type: eth_tester
      autodeploy_allowed: true
      use_default_account: true

Each root-level node is the network name you will use to reference the
configuration.  For instance using the above file, if you want to connect to
your local go-ethereum IPC endpoint: `sb console geth`

*********************
Connection Parameters
*********************

============
:code:`type`
============

The available connection types are:

* :code:`auto` - Setting the connection to `auto` will allow web3.py to
  automagically try common configurations for a connection.
* :code:`websocket` - Connect to a Web socket JSON-RPC provider
* :code:`http` - Connect to a plain HTTP(or HTTPS) JSON-RPC provider
* :code:`ipc` - Use the local IPC socket to connect to a local node
* :code:`eth_tester` - A virtual ephemeral chain to test against.  Very useful
  for running unit tests. **NOTE**: eth_tester is in alpha and has been known
  to show bugs.

===========
:code:`url`
===========

The URL endpoint to connect to.  Only available for :code:`http` and
:code:`websocket`.

============
:code:`file`
============

The IPC socket to connect to.  Only available for type :code:`ipc`.

==========================
:code:`autodeploy_allowed`
==========================

This is a per-network setting that allows Solidbyte to automatically deploy your contracts if it
needs to use this network.  This is great for test backends, but use at your own risk on public
networks.  This defaults to :code:`false`.

===========================
:code:`use_default_account`
===========================

This allows the network to use the account set as default for deployment and testing. This defaults
to :code:`false` for safety.
