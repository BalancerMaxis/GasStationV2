import brownie
import time
from brownie import chain
import pytest


def drain_addresses(to_drain, dest):
    for account in to_drain:
        account.transfer(dest, account.balance())
        
    
def test_everything(admin, gas_station, upkeep_caller, deployers, bots):\
    ## Drain recipients
    drain_addresses(deployers, admin.address)
    drain_addresses(bots, admin.address)
    ### Setup values
    deploy_min = 0.25e18
    deploy_topup = 1e18
    bot_min = 0.5e18
    bot_topup = 1.5e18
    ### Calculate stuff
    full_topup = (deploy_topup*len(deployers)) + (bot_topup*len(bots))
    ###  stuf
    gas_station.addRecipients(deployers, deploy_min, deploy_topup, {"from": admin})
    gas_station.addRecipients(bots, bot_min, bot_topup, {"from": admin})
    assert len(gas_station.getRecipients()) == len(bots) + len(deployers), "Watch list is wrong length"
    (ready, recipients) = gas_station.checkUpkeep(0)
    assert not ready, "Ready with no gas"
    admin.transfer(gas_station.address, full_topup*2)
    (ready, recipients) = gas_station.checkUpkeep(0)
    assert ready, "Everything setup, but not ready"
    gas_station.performUpkeep(recipients, {"from": upkeep_caller})
    assert gas_station.balance() == full_topup, "Unexpected amount of gas left in station"
    for bot in bots:
        assert bot.balance() == bot_topup, f"{bot} has unexpected balance {bot.balance}"
    for deployer in deployers:
        assert deployer.balance() == deploy_topup, f"{deployer} has unexpected balance {deployer.balance}"
    # At this point we have topped all the empty addresses up to full

    ### Test second topup at threshold
    chain.sleep(gas_station.MinWaitPeriodSeconds() + 1)
    chain.mine()
    (ready, recipients) = gas_station.checkUpkeep(0)
    assert not ready, "Reports ready with no gas spend"
    # test thresholds
    bots[0].transfer(admin.address, bot_topup - bot_min)
    (ready, recipients) = gas_station.checkUpkeep(0)
    assert not ready, "Ready at boundry, should need 1 less wei"
    bots[0].transfer(admin.address, 1)
    (ready, recipients) = gas_station.checkUpkeep(0)
    assert ready, "Not ready when recipient needs gas"
    tx = gas_station.performUpkeep(recipients, {"from": upkeep_caller})
    assert bots[0].balance() == bot_topup, "Bot should have been topped up but does not have topup balance"

    # Test min wait period

    bots[0].transfer(admin.address, bots[0].balance())
    (ready, recipients) = gas_station.checkUpkeep(0)
    assert not ready, "Ready with no minWait"
    gas_station.performUpkeep(recipients, {"from": upkeep_caller})
    (ready, recipients) = gas_station.checkUpkeep(0)
    assert not ready, "reports ready before minwait"
    tx = gas_station.performUpkeep(recipients, {"from": upkeep_caller})
    assert dict(tx.events) == {}, "Perform upkeep did something when it shouldn't have"
    assert bots[0].balance() == 0, "wallet has  balance"
    ## get ready for next run
    chain.sleep(gas_station.MinWaitPeriodSeconds()+1)
    chain.mine()

    ## test multiple
    deployers[0].transfer(admin, .8e18)
    deployers[1].transfer(admin, .76e18)
    deployers[2].transfer(admin, .9e18)
    bots[1].transfer(admin, (1.0001e18))
    (ready, recipients) = gas_station.checkUpkeep(0)
    assert ready, "Multiple recipents need gas and keeper not ready"
    tx = gas_station.performUpkeep(recipients, {"from": upkeep_caller})
    for bot in bots:
        assert bot.balance() == bot_topup, f"{bot.address} has unexpected balance {bot.balance()}"
    for deployer in deployers:
        assert deployer.balance() == deploy_topup, f"{deployer.address} has unexpected balance {deployer.balance()}"
