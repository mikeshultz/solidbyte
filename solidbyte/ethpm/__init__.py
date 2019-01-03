""" Install-only Ethereum Package Index library """
import re
import json
import requests
from pathlib import Path
from ..common.logging import getLogger

log = getLogger(__name__)

# Useful for resolving BIP122 URIs
GENESIS_HASHES = {
    '1': 'd4e56740f876aef8c010b86a40d5f56745a118d0906a34e69aec8c0db1cb8fa3',
    '3': '41941023680923e0fe4d74a34bdac8141f2540e3ae90623718e47d66d1ca4a2d',
}

PACKAGE_INDEX_INTERFACE = {
    '3': {
        'address': "0x8011dF4830b4F696Cd81393997E5371b93338878",
        'abi': [{"constant":True,"inputs":[],"name":"getNumReleases","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"name":"newReleaseValidator","type":"address"}],"name":"setReleaseValidator","outputs":[{"name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[{"name":"name","type":"string"},{"name":"offset","type":"uint256"},{"name":"numReleases","type":"uint256"}],"name":"getPackageReleaseHashes","outputs":[{"name":"","type":"bytes32[]"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"name":"newOwner","type":"address"}],"name":"setOwner","outputs":[{"name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[{"name":"name","type":"string"},{"name":"major","type":"uint32"},{"name":"minor","type":"uint32"},{"name":"patch","type":"uint32"},{"name":"preRelease","type":"string"},{"name":"build","type":"string"}],"name":"getReleaseLockfileURI","outputs":[{"name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"getPackageDb","outputs":[{"name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"name":"newPackageDb","type":"address"}],"name":"setPackageDb","outputs":[{"name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[{"name":"name","type":"string"},{"name":"major","type":"uint32"},{"name":"minor","type":"uint32"},{"name":"patch","type":"uint32"},{"name":"preRelease","type":"string"},{"name":"build","type":"string"}],"name":"releaseExists","outputs":[{"name":"","type":"bool"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"getReleaseValidator","outputs":[{"name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"name":"releaseHash","type":"bytes32"}],"name":"getReleaseData","outputs":[{"name":"major","type":"uint32"},{"name":"minor","type":"uint32"},{"name":"patch","type":"uint32"},{"name":"preRelease","type":"string"},{"name":"build","type":"string"},{"name":"releaseLockfileURI","type":"string"},{"name":"createdAt","type":"uint256"},{"name":"updatedAt","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"getAllReleaseHashes","outputs":[{"name":"","type":"bytes32[]"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"name":"name","type":"string"},{"name":"newPackageOwner","type":"address"}],"name":"transferPackageOwner","outputs":[{"name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[{"name":"idx","type":"uint256"}],"name":"getReleaseHash","outputs":[{"name":"","type":"bytes32"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"name":"name","type":"string"},{"name":"major","type":"uint32"},{"name":"minor","type":"uint32"},{"name":"patch","type":"uint32"},{"name":"preRelease","type":"string"},{"name":"build","type":"string"},{"name":"releaseLockfileURI","type":"string"}],"name":"release","outputs":[{"name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"getNumPackages","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"name":"offset","type":"uint256"},{"name":"numReleases","type":"uint256"}],"name":"getReleaseHashes","outputs":[{"name":"","type":"bytes32[]"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"name":"newAuthority","type":"address"}],"name":"setAuthority","outputs":[{"name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[{"name":"name","type":"string"}],"name":"packageExists","outputs":[{"name":"","type":"bool"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"authority","outputs":[{"name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"name":"name","type":"string"}],"name":"getPackageData","outputs":[{"name":"packageOwner","type":"address"},{"name":"createdAt","type":"uint256"},{"name":"numReleases","type":"uint256"},{"name":"updatedAt","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"name":"name","type":"string"}],"name":"getAllPackageReleaseHashes","outputs":[{"name":"","type":"bytes32[]"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"name":"name","type":"string"},{"name":"releaseIdx","type":"uint256"}],"name":"getReleaseHashForPackage","outputs":[{"name":"","type":"bytes32"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"name":"idx","type":"uint256"}],"name":"getPackageName","outputs":[{"name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"name":"newReleaseDb","type":"address"}],"name":"setReleaseDb","outputs":[{"name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"getReleaseDb","outputs":[{"name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"anonymous":False,"inputs":[{"indexed":True,"name":"nameHash","type":"bytes32"},{"indexed":True,"name":"releaseHash","type":"bytes32"}],"name":"PackageRelease","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"name":"oldOwner","type":"address"},{"indexed":True,"name":"newOwner","type":"address"}],"name":"PackageTransfer","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"name":"oldOwner","type":"address"},{"indexed":True,"name":"newOwner","type":"address"}],"name":"OwnerUpdate","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"name":"oldAuthority","type":"address"},{"indexed":True,"name":"newAuthority","type":"address"}],"name":"AuthorityUpdate","type":"event"}], # noqa
    },
}


class EthPMLockfile(object):
    def __init__(self, json_object):
        if type(json_object) == str:
            json_object = json.loads(json_object)
        self._process_lockfile(json_object)

    def _process_lockfile(self, json_object):
        """ Process a JSON-representative object """

        if not json_object:
            raise Exception("json_object is missing")
        if not json_object.get('lockfile_version'):
            raise ValueError("Invalid EthPM Lockfile.  Missing lockfile_version")

        self.lockfile_version = json_object['lockfile_version']

        if self.lockfile_version != '1':
            log.warning("Lockfile version is newer than supported.  This may not go as expected...")

        self.json_object = json_object


class EthPM(object):
    """ A class to interact with Ethereum Package Manager

        Usage
        -----
        epm = EthPM(Web3())
        epm.install('erc223')

        References
        ----------
        https://www.ethpm.com/
        https://www.ethpm.com/docs/integration-guide
        https://github.com/ethpm/ethpm-spec/tree/v1.0.0
        https://github.com/ethereum/EIPs/issues/190

        TODO
        ----
        The IPFS HTTP gateway, as usual, is an issue with timeouts.
    """

    def __init__(self, web3):
        """ Initialize EthPM

        Args:
            web3 (Web3): An instantiated Web3 object with an active connection
        """
        self.web3 = web3
        self.net_id = self.web3.net.chainId or self.web3.net.version
        self._package_index = None

        # EthPM only supports Ropsten
        if not PACKAGE_INDEX_INTERFACE.get(self.net_id):
            raise Exception("EthPM does not support the network(chainID: {}).".format(self.net_id))

        self._init_package_index()

    def _init_package_index(self):
        """ Create the instance of PackageIndex """
        self._package_index = self.web3.eth.contract(
            abi=PACKAGE_INDEX_INTERFACE[self.net_id]['abi'],
            address=PACKAGE_INDEX_INTERFACE[self.net_id]['address']
        )

    def _ipfs_fetch(self, uri, timeout=30):
        """ Retreive an IPFS file using an IPFS URI """
        log.debug("Fetching request for {}.".format(uri))
        uri_pattern = r'^ipfs://(Qm[A-Za-z0-9]{44})$'
        uri_match = re.match(uri_pattern, uri)

        if uri_match is None:
            raise Exception("Invalid IPFS URI")

        qmHash = uri_match.group(1)

        log.info("Fetching {} from IPFS...".format(qmHash))

        resp = None
        try:
            resp = requests.get('https://ipfs.io/ipfs/{}'.format(qmHash,
                                                                 timeout=timeout))
        except requests.exceptions.Timeout as e:
            log.error("Timeout trying to fetch {}".format(uri))
            raise e

        if resp.status_code != 200:
            raise Exception("Invalid reponse from ipfs.io")

        return resp

    def _ipfs_fetch_json(self, uri, timeout=30):
        return self._ipfs_fetch(uri, timeout).json()

    def _ipfs_fetch_text(self, uri, timeout=30):
        return self._ipfs_fetch(uri, timeout).text

    def packageExists(self, pkgname) -> bool:
        """ Check if a package exists in EthPM """
        return self._package_index.functions.packageExists(pkgname).call()

    def getAllPackageReleaseHashes(self, pkgname):
        """ Return release hashes for a package """
        return self._package_index.functions.getAllPackageReleaseHashes(pkgname).call()

    def getReleaseData(self, release_hash) -> dict:
        """ Return release data for a package """

        """ getRelease data returns:
        (major, minor, patch, preRelease, build, releaseLockfileURI, createdAt, updatedAt)
        """
        data = self._package_index.functions.getReleaseData(release_hash).call()

        assert len(data) == 8, "Return data differs from known ABI return values"

        return {
            'major': data[0],
            'minor': data[1],
            'patch': data[2],
            'preRelease': data[3],
            'build': data[4],
            'releaseLockfileURI': data[5],
            'createdAt': data[6],
            'updatedAt': data[7],
        }

    def getLatestReleaseData(self, pkgname):
        """ return the latest release data for a package """
        releases = self.getAllPackageReleaseHashes(pkgname)
        if len(releases) == 0:
            return None
        return releases[-1]

    def getLatestReleaseLockfile(self, pkgname):
        """ return a Release Lockfile for an EthPM package """

        release_hash = self.getLatestReleaseData(pkgname)

        if not release_hash:
            return None

        latest = self.getReleaseData(release_hash)

        lockfile_json = self._ipfs_fetch_json(latest['releaseLockfileURI'])
        if not lockfile_json:
            log.error("Failed to fetch {}".format(latest['releaseLockfileURI']))
            return None
        return EthPMLockfile(lockfile_json)

    def _install_file(self, source, target):
        """ Install a contract from an ipfs source to a filesystem target """
        if len(source) < 8 or source[:4] != 'ipfs':
            raise Exception("Invalid target {}".format(source))
        if type(target) == str:
            target = Path(target)

        source_source = self._ipfs_fetch_text(source)
        if not target.parent.exists():
            log.debug("Creating directory {}".format(target.parent))
            target.parent.mkdir(mode=0o755, parents=True)

        with target.open('x') as openFile:
            openFile.write(source_source)

        log.info("File {} created.".format(target))

    def install(self, pkgname):
        """ Install a package """

        if not self.packageExists(pkgname):
            raise Exception("Package not found")

        lockfile = self.getLatestReleaseLockfile(pkgname)

        if not lockfile:
            raise Exception("Missing lockfile")
        if not lockfile.json_object.get('sources'):
            raise Exception("No sources listed in lockfile")

        for k, v in lockfile.json_object['sources'].items():
            self._install_file(v, k)

        # Handle dependencies
        if lockfile.json_object.get('build_dependencies'):
            for dep_name in lockfile.json_object['build_dependencies'].keys():
                self.install(dep_name)

        log.info("Successfully installed {}.".format(pkgname))

        return True
