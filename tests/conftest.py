import pytest
import time
from brownie import (
    interface,
    accounts,
    GasStationV2,
    Contract

)
from dotmap import DotMap
import pytest
from bal_addresses import AddrBook


##  Accounts

r = AddrBook("mainnet").flatbook



@pytest.fixture(scope="module")
def deployers():
    return [accounts[0], accounts[1] , accounts[2]]

@pytest.fixture(scope="module")
def bots():
    return [accounts[3], accounts[4]]

@pytest.fixture(scope="module")
def admin():
    return accounts[6]

@pytest.fixture(scope="module")
def upkeep_caller():
    return accounts[7]

@pytest.fixture(scope="module")
def deployer():
    return accounts[8]


@pytest.fixture()
def gas_station(deploy):
    return deploy



@pytest.fixture(scope="module")
def deploy(deployer, admin, upkeep_caller):
    """
    Deploys, vault and test strategy, mock token and wires them up.
    """
    station = GasStationV2.deploy(upkeep_caller, 60, {"from": deployer})
    station.transferOwnership(admin, {"from": deployer})
    station.acceptOwnership({"from": admin})
    return station

