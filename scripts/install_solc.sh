#!/bin/sh

SOLC_VERSION="v0.4.25"
SOLC_DOWNLOAD="https://github.com/ethereum/solidity/releases/download/$SOLC_VERSION/solc-static-linux"
SOLC_DEST="$(pwd)/bin/solc"

echo "Downloading the Solidity compiler..."
curl -sL $SOLC_DOWNLOAD --output $SOLC_DEST && chmod +x $SOLC_DEST
echo "Compiler saved to $SOLC_DEST"