# networks.yml

`networks.yml` is the [YAML](http://yaml.org) file you use to configure
connections to Ethereum JSON-RPC providers and nodes.  Some templates may 
provide some pre-configured connections.

## Example File

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

Each root-level node is the network name you will use to reference the
configuration.  For instance using the above file, if you want to connect to
your local go-ethereum instance: `sb console geth`

## Connection Types

The available connection types are:

 - `auto` - Setting the connection to `auto` will allow web3.py to automagically try common configurations for a connection.
 - `websocket` - Connect to a Web socket JSON-RPC provider
 - `http` - Connect to a plain HTTP(or HTTPS) JSON-RPC provider
 - `ipc` - Use the local IPC socket to connect to a local node
 - `eth_tester` - A virtual ephemeral chain to test against.  Very useful for running unit tests. **NOTE**: eth_tester is in alpha and has been known to show bugs.

 ## `autodeploy_allowed`

 This is a per-network setting that allows Solidbyte to automatically deploy your contracts if it
 needs to use this network.  This is great for test backends, but use at your own risk on public
 networks.  This defaults to `false`.
 