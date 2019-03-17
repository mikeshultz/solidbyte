pragma solidity >0.4.24 <0.6.0;

import "./ERC20.sol";

/**
 * @title Example ERC20 token implementation
 */
contract MyERC20 is ERC20 {
    constructor(uint256 initialSupply) public
    {
        _mint(msg.sender, initialSupply);
    }
}
