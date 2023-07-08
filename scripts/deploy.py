from brownie import GasStationV2, accounts
from bal_addresses import AddrBook

def deploy(account, chain="mainnet"):
    a = AddrBook(chain)
    r = a.dotmap
    keeper = r.chainlink.keeper_registry
    GasStationV2.deploy(keeper, 60*60*8, {"from": account})
    gs = GasStationV2[len(GasStationV2)-1]
    GasStationV2.publish_source(gs)
    gs.transferOwnership(r.multisigs.lm)

