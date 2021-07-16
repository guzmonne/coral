from __future__ import annotations
from dataclasses import dataclass
from typing import List, Literal, Union, Callable


@dataclass
class Order:
    """
    Represents an order entered by a user. It specifies the number of
    shares that have to be bought/sold and its maximum/minimum prices.

    Attributes
    ----------
    user_id : str
        unique identifier of a user
    order_type : Literal["BUY"|"SELL"]
        type of order [BUY|SELL]
    q : float
        quantity of shares
    p : float
        maximum share price when buying and minimum price when selling
    """
    user_id: str
    order_type: Literal['BUY', 'SELL']
    q: float
    p: float


@dataclass
class AuctionResult:
    """
    Holds the result of running an auction.

    Attributes
    ----------
    q_max : float
        Maximum number of shares that could be sold/bought between all users
    p_min : float
        The mimimum value of the range at which all the transactions can take place
    p_max : float
        The maximum value of the range at which all the transactions can take place
    """
    q_max: float
    p_min: Union[float, None]
    p_max: Union[float, None]


@dataclass
class AuctionOrder(object):
    """
    Aggregates multiple Orders with the same price and quantity and handles share
    allocation.

    Attributes
    ----------
    q : float
        the number of shares to buy/sell
    p : float
        the max/min price to buy/sell shares
    order_type : Literal["BUY", "SELL"]
        auction order type
    orders : List[Order]
        the aggregated list of orders
    allocated : float
        the number of allocated shares for these orders

    Methods
    -------
    compared_to(other_order: Order) -> int:
        Checks if another user is more willing to buy than itself.
    compared_to(other_order: Order) -> int:
        Checks if another user is more willing to sell than itself.
    """
    q: float
    p: float
    order_type: Literal['BUY', 'SELL']
    orders: List[Order]
    allocated: float = 0

    @property
    def fulfilled(self) -> bool:
        return self.allocated == self.q_total

    @property
    def q_total(self) -> float:
        return self.q * len(self.orders)

    @property
    def q_to_allocate(self) -> float:
        return self.q_total - self.allocated

    def compared_to(self, other: Order) -> int:
        """
        Compares itself to another Order, indicating if better (1), worst(-1), or equal(0)

        :param other - `order` to compare against.
        """
        if self.order_type == "BUY":
            if self.p != other.p:
                return 1 if self.p > other.p else -1
            else:
                if self.q == other.q:
                    return 0
                else:
                    return 1 if self.q > other.q else -1
        elif self.order_type == "SELL":
            if self.p != other.p:
                return 1 if self.p < other.p else -1
            else:
                if self.q == other.q:
                    return 0
                else:
                    return 1 if self.q > other.q else -1


class AuctionManager(object):
    """
    Handles the entire auction process.

    Holds all buy/sell orders, grouping those with equal characteristics.
    It exposes methods to conduct the auction and get back the results.

    Attributes
    ----------
    buy_orders : List[AuctionOrder]
        list of "BUY" orders for the auction
    sell_orders : List[AuctionOrder]
        list of "SELL" orders for the auction
    allocated : float
        total number of allocated stocks
    p_min : float
        minimum price at which the shares can be exchanged
    p_max : float
        maximum price at which the shares can be exchanged.
    buy_index : int
        internal index pointing to the last evaluated "BUY" order
    sell_index : int
        internal index pointing to the last evaluated "SELL" order

    Methods
    -------
    next_buy_order():
        Returns the next unallocated buy order or `None`.
    next_sell_order():
        Returns the next unallocated sell order or `None`.
    match_orders(buy_order: AuctionOrder, sell_order: AuctionOrder):
        Tries to see if there is a match between the buy and sell order.
    allocate_orders():
        Runs the auction with the current buy/sell orders.
    append_to_buy_orders():
        Adds an order to the `buy_orders` list, sorted according to the user's willingness to buy.
    append_to_sell_orders():
        Adds an order to the `sell_orders` list, sorted according to the user's willingness to sell.
    """
    buy_orders: List[AuctionOrder]
    sell_orders: List[AuctionOrder]
    allocated: float = 0
    p_min: float = None
    p_max: float = None
    buy_index: int = 0
    sell_index: int = 0

    def __init__(self, orders: List[Order]):
        """
        Constructs an AuctionManger according to the provided orders.

        All the orders will be sorted into the `buy_orders` and `sell_orders`. For each order
        an equivalent `AuctionOrder` will be created, grouping those orders with equal properties.

        Parameters
        ----------
        orders : List[Orders]
            list of orders that the class should handle

        Returns
        -------
        None
        """
        self.buy_orders = []
        self.sell_orders = []
        for order in orders:
            if order.order_type == "BUY":
                self.append_to_buy_orders(order)
            else:
                self.append_to_sell_orders(order)

    def next_buy_order(self) -> Union[AuctionOrder, None]:
        """
        Returns the next unallocated buy unallocated order or `None`.

        Returns
        -------
        buy_order : AuctionOrder | None
            The next unallocated buy order or `None`
        """
        try:
            buy_order = self.buy_orders[self.buy_index]
            if buy_order.fulfilled:
                self.buy_index += 1
                return self.next_buy_order()
            return buy_order
        except IndexError:
            return None

    def next_sell_order(self) -> Union[AuctionOrder, None]:
        """
        Returns the next unallocated sell unallocated order or `None`.

        Returns
        -------
        sell_order : AuctionOrder | None
            The next unallocated sell order or `None`
        """
        try:
            sell_order = self.sell_orders[self.sell_index]
            if sell_order.fulfilled:
                self.sell_index += 1
                return self.next_sell_order()
            return sell_order
        except IndexError:
            return None

    def match_orders(self, buy_order: AuctionOrder, sell_order: AuctionOrder) -> bool:
        """
        Tries to see if there is a match between the buy and sell order.

        Parameters
        ----------
        buy_order : AuctionOrder
            Buy order to match
        sell_order : AuctionOrder
            Sell order to match

        Returns
        -------
        result : boolean
            A flag indicating if the orders matched.
        """
        if buy_order.p < sell_order.p:
            return False
        q_buy = buy_order.q_to_allocate
        q_sell = sell_order.q_to_allocate
        if q_buy <= q_sell:
            q = q_buy
        else:
            q = q_sell
        # Allocate shares
        self.allocated += q
        buy_order.allocated += q
        sell_order.allocated += q
        # Update price range
        if self.p_max is None:
            self.p_max = buy_order.p
        self.p_min = sell_order.p

        return True

    def allocate_orders(self):
        """
        Runs the auction with the current buy/sell orders.

        Returns
        -------
        None
        """
        buy_order = self.next_buy_order()
        sell_order = self.next_sell_order()
        if buy_order == None or sell_order == None:
            return
        # If an order can't be allocated we stop the process.
        if self.match_orders(buy_order, sell_order):
            self.allocate_orders()

    def append_to_buy_orders(self, buy_order: Order) -> None:
        """
        Adds an order to the `buy_orders` list, sorted according to the user's willingness to buy.

        Parameters
        ----------
        buy_order : AuctionOrder
            Buy order to store

        Returns
        -------
        None
        """
        for index, auction_order in enumerate(self.buy_orders):
            more_willing = auction_order.compared_to(
                buy_order)
            if more_willing == -1:
                self.buy_orders.insert(index, AuctionOrder(
                    orders=[buy_order],
                    p=buy_order.p,
                    q=buy_order.q,
                    order_type="BUY"
                ))
                return
            elif more_willing == 0:
                self.buy_orders[index].orders.append(buy_order)
                return
        self.buy_orders.append(AuctionOrder(
            orders=[buy_order],
            p=buy_order.p,
            q=buy_order.q,
            order_type="BUY"
        ))

    def append_to_sell_orders(self, sell_order: Order) -> None:
        """
        Adds an order to the `sell_orders` list, sorted according to the user's willingness to sell.

        Parameters
        ----------
        sell_order : AuctionOrder
            Buy order to store

        Returns
        -------
        None
        """
        for index, auction_order in enumerate(self.sell_orders):
            more_willing = auction_order.compared_to(
                sell_order)
            if more_willing == -1:
                self.sell_orders.insert(index, AuctionOrder(
                    orders=[sell_order],
                    p=sell_order.p,
                    q=sell_order.q,
                    order_type="SELL"
                ))
                return
            elif more_willing == 0:
                self.sell_orders[index].orders.append(sell_order)
                return
        self.sell_orders.append(AuctionOrder(
            orders=[sell_order],
            p=sell_order.p,
            q=sell_order.q,
            order_type="SELL"
        ))


def run_auction(orders: List[Order]) -> AuctionResult:
    manager = AuctionManager(orders)
    manager.allocate_orders()
    return AuctionResult(q_max=manager.allocated, p_max=manager.p_max, p_min=manager.p_min)
