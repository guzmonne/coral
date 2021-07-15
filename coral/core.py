from dataclasses import dataclass
from types import List, Literal, Union

@dataclass
class Order:
    user_id: str
    order_type: Literal['BUY', 'SELL']
    q: float
    p: float

@dataclass
class AuctionResult:
    q_max: float
    p_min: Union[float, None]
    p_max: Union[float, None]


def run_auction(orders: List[Order]) -> AuctionResult:
    pass




