## Gas Station Exact V2


This is a contract meant to run as keeper and keep addresses full of eth.

You can read about [Chainlink Automation](https://docs.chain.link/chainlink-automation/introduction)

Reference Deployment [Maxi Gas Station V2](https://etherscan.io/address/0x7fb8f5d04b521b6880158819e69538655aabd5c4#code)

## Setup
The current setup/tests use brownie but you can easily adapt.  Import mappings are in brownie-config.yaml

Using python3.9.  
```bash
pip3.9 install -r requirements.txt
brownie test
```

## Basic Usage Pattern
- Deploy the contract
   - recommend at least 6 hour minMaitSeconds to prevent a recipent from draining the gas station before you can intervene.
   - KeeperRegistry should be set per Chain to the registry address found in the [Chainlinks Docs](https://docs.chain.link/chainlink-automation/supported-networks)
   - Remember to `transferOwnership(owner)`, from deployer and `confirmOwnership()` from the new owner address.
- Add some recipients using `addRecipients(address[] calldata recipients, uint96 minBalanceWei, uint96 topUpToAmountWei)`
  - Must be called by the owner
  - All listed recipients get the same config
  - Use multiple calls to setup different configs per recipient list
- Fund the gas station with enough gas to fund those recipients.
- Register the contract with Chainlink, gas limit can be set to 170,000.
  - Pay in at least 5 or 10 link to make sure that's not a problem
- Spend enough gas and see if you top up.
- Gas station will top up any address that:
  - Is under minBalanceWei.
  - Has waited at least minWaitPeriodSeconds.
  - The gas station has sufficient ETH balance to bring the recipient to `topUpToAmountWei`.

## Checking it works before adding an upkeep
You can call checkUpkeep on the gas station passing in `0x` as call data, it should return true with some data if one of the recipients has balance under it's min amount.

The functions are well documented in the natspec.  you can get a list of recipients by calling  `getRecipientList()`  
The specific parameters for a given recipientsList address can be found by calling `recipientsList(address)` for an address on the recipientsList.  The outputs look like this:
```
[ getAccountInfo(address) method Response ]
  isActive   bool :  true
  minBalanceWei   uint96 :  500000000000000000
  topUpToAmountWei   uint96 :  1000000000000000000
  lastTopUpTimestamp   uint56 :  1676923715
```
**minBalance:** defines the target minimum ETH balance for this address.
**topUpToAmount:** defines the amount of eth that the gas station will top up to.

In the configuration above 0.5 ETH minBalance and it will top up to 1 eth.

