from coral.core import run_auction, Order, AuctionResult, AuctionManager, AuctionOrder


def test_auction_order():
    # #fulfilled()
    order = Order(user_id="U1", order_type="BUY", q=100, p=500)
    auction_order = AuctionOrder(
        orders=[order], q=order.q, p=order.p, order_type=order.order_type)
    assert auction_order.fulfilled == False
    auction_order.allocated = order.q
    assert auction_order.fulfilled == True
    auction_order.allocated = 1
    assert auction_order.fulfilled == False
    auction_order = AuctionOrder(
        orders=[order, order], q=order.q, p=order.p, order_type=order.order_type)
    assert auction_order.fulfilled == False
    auction_order.allocated = order.q
    assert auction_order.fulfilled == False
    auction_order.allocated = order.q * 2
    assert auction_order.fulfilled == True


def test_auction_manager():
    # Buy orders are inverted
    order_1 = Order(user_id="U1", order_type="BUY", q=100, p=500)
    order_2 = Order(user_id="U2", order_type="BUY", q=100, p=600)
    auction_order_1 = AuctionOrder(
        orders=[order_1], q=order_1.q, p=order_1.p, order_type=order_1.order_type)
    auction_order_2 = AuctionOrder(
        orders=[order_2], q=order_2.q, p=order_2.p, order_type=order_2.order_type)
    orders = [order_1, order_2]
    assert AuctionManager(orders).buy_orders == [
        auction_order_2, auction_order_1]
    # Buy orders are already sorted
    orders = [order_2, order_1]
    assert AuctionManager(orders).buy_orders == [
        auction_order_2, auction_order_1]
    # Two buy orders with same price but different quantities
    order_3 = Order(user_id="U3", order_type="BUY", q=50, p=600)
    auction_order_3 = AuctionOrder(
        orders=[order_3], q=order_3.q, p=order_3.p, order_type=order_3.order_type)
    orders = [order_1, order_2, order_3]
    assert AuctionManager(orders).buy_orders == [
        auction_order_2, auction_order_3, auction_order_1]
    # Sell orders are already sorted
    order_4 = Order(user_id="U4", order_type="SELL", q=100, p=500)
    order_5 = Order(user_id="U5", order_type="SELL", q=100, p=600)
    auction_order_4 = AuctionOrder(
        orders=[order_4], q=order_4.q, p=order_4.p, order_type=order_4.order_type)
    auction_order_5 = AuctionOrder(
        orders=[order_5], q=order_5.q, p=order_5.p, order_type=order_5.order_type)
    orders = [order_4, order_5]
    assert AuctionManager(orders).sell_orders == [
        auction_order_4, auction_order_5]
    # Sell orders are inverted
    orders = [order_5, order_4]
    assert AuctionManager(orders).sell_orders == [
        auction_order_4, auction_order_5]
    # Two sell orders with same price buy different quantities
    order_6 = Order(user_id="U6", order_type="SELL", q=50, p=500)
    auction_order_6 = AuctionOrder(
        orders=[order_6], q=order_6.q, p=order_6.p, order_type=order_6.order_type)
    orders = [order_4, order_5, order_6]
    assert AuctionManager(orders).sell_orders == [
        auction_order_4, auction_order_6, auction_order_5]
    # Multiple buy orders with the same price and quantity
    order_7 = Order(user_id="U7", order_type="BUY", q=100, p=500)
    orders = [order_1, order_7]
    auction_order_7 = AuctionOrder(
        orders=[order_1, order_7], q=order_7.q, p=order_7.p, order_type=order_7.order_type)
    assert AuctionManager(orders).buy_orders == [auction_order_7]
    # Multiple sell orders with the same price and quantity
    order_8 = Order(user_id="U8", order_type="SELL", q=100, p=500)
    orders = [order_4, order_8]
    auction_order_8 = AuctionOrder(
        orders=[order_4, order_8], q=order_8.q, p=order_8.p, order_type=order_8.order_type)
    assert AuctionManager(orders).sell_orders == [auction_order_8]
    # #next_buy_order()
    order_1 = Order(user_id="U1", order_type="BUY", q=100, p=600)
    order_2 = Order(user_id="U2", order_type="BUY", q=100, p=500)
    auction_order_1 = AuctionOrder(
        orders=[order_1], q=order_1.q, p=order_1.p, order_type=order_1.order_type)
    auction_order_2 = AuctionOrder(
        orders=[order_2], q=order_2.q, p=order_2.p, order_type=order_2.order_type)
    manager = AuctionManager([order_1, order_2])
    assert manager.next_buy_order() == auction_order_1
    manager.buy_index += 1
    assert manager.next_buy_order() == auction_order_2
    manager.buy_index += 1
    assert manager.next_buy_order() == None
    # #next_sell_order()
    order_1 = Order(user_id="U1", order_type="SELL", q=100, p=500)
    order_2 = Order(user_id="U2", order_type="SELL", q=100, p=600)
    auction_order_1 = AuctionOrder(
        orders=[order_1], q=order_1.q, p=order_1.p, order_type=order_1.order_type)
    auction_order_2 = AuctionOrder(
        orders=[order_2], q=order_2.q, p=order_2.p, order_type=order_2.order_type)
    manager = AuctionManager([order_1, order_2])
    assert manager.next_sell_order() == auction_order_1
    manager.sell_index += 1
    assert manager.next_sell_order() == auction_order_2
    manager.sell_index += 1
    assert manager.next_sell_order() == None
    # #match_orders()
    # If the buy and sell shares match they should be completely allocated
    shares = 500
    buy_order = Order(user_id="U1", order_type="BUY",  q=shares, p=500)
    sell_order = Order(user_id="U2", order_type="SELL", q=shares, p=500)
    auction_buy_order = AuctionOrder(
        orders=[buy_order], q=buy_order.q, p=buy_order.p, order_type=buy_order.order_type)
    auction_sell_order = AuctionOrder(
        orders=[sell_order], q=sell_order.q, p=sell_order.p, order_type=sell_order.order_type)
    manager = AuctionManager([buy_order, sell_order])
    assert manager.match_orders(
        auction_buy_order, auction_sell_order) == True
    assert manager.allocated == shares
    assert manager.p_max == 500
    assert manager.p_min == 500
    assert auction_buy_order.fulfilled == True
    assert auction_sell_order.fulfilled == True
    # If there are more shares to sell than to buy then the buy order should
    # be fulfilled and the sell order should be partially fulfilled.
    buy_shares = 500
    sell_shares = 300
    buy_order = Order(user_id="U1", order_type="BUY",  q=buy_shares, p=500)
    sell_order_1 = Order(user_id="U2", order_type="SELL", q=sell_shares, p=500)
    sell_order_2 = Order(user_id="U2", order_type="SELL", q=sell_shares, p=500)
    auction_buy_order = AuctionOrder(
        orders=[buy_order], q=buy_order.q, p=buy_order.p, order_type=buy_order.order_type)
    auction_sell_order = AuctionOrder(
        orders=[sell_order_1, sell_order_2], q=sell_order_1.q, p=sell_order_1.p, order_type=sell_order_1.order_type)
    manager = AuctionManager([buy_order, sell_order_1, sell_order_2])
    assert manager.match_orders(
        auction_buy_order, auction_sell_order) == True
    assert manager.allocated == buy_shares
    assert manager.p_max == 500
    assert manager.p_min == 500
    assert auction_buy_order.fulfilled == True
    assert auction_sell_order.fulfilled == False
    # If there are more shares to buy than to sell then the sell order should
    # be fulfilled and the buy order should be partially fulfilled.
    buy_shares = 500
    sell_shares = 200
    buy_order = Order(user_id="U1", order_type="BUY",  q=buy_shares, p=500)
    sell_order_1 = Order(user_id="U2", order_type="SELL", q=sell_shares, p=500)
    sell_order_2 = Order(user_id="U2", order_type="SELL", q=sell_shares, p=500)
    auction_buy_order = AuctionOrder(
        orders=[buy_order], q=buy_order.q, p=buy_order.p, order_type=buy_order.order_type)
    auction_sell_order = AuctionOrder(
        orders=[sell_order_1, sell_order_2], q=sell_order_1.q, p=sell_order_1.p, order_type=sell_order_1.order_type)
    manager = AuctionManager([buy_order, sell_order_1, sell_order_2])
    assert manager.match_orders(
        auction_buy_order, auction_sell_order) == True
    assert manager.allocated == sell_shares * 2
    assert manager.p_max == 500
    assert manager.p_min == 500
    assert auction_buy_order.fulfilled == False
    assert auction_sell_order.fulfilled == True
    # #allocate_orders()
    order_1 = Order(user_id="U1", order_type="BUY",  q=100, p=100)
    order_2 = Order(user_id="U2", order_type="BUY",  q=50, p=200)
    order_3 = Order(user_id="U3", order_type="SELL",  q=100, p=200)
    order_4 = Order(user_id="U4", order_type="SELL",  q=50, p=100)
    # If there are no buy orders it should do nothing
    manager = AuctionManager([order_3, order_4])
    manager.allocate_orders()
    assert manager.p_max == None
    assert manager.p_min == None
    assert manager.allocated == 0
    # If there are no sell orders it should do nothing
    manager = AuctionManager([order_1, order_2])
    manager.allocate_orders()
    assert manager.p_max == None
    assert manager.p_min == None
    assert manager.allocated == 0
    # It should allocate all the orders
    manager = AuctionManager([order_1, order_2, order_3, order_4])
    manager.allocate_orders()
    assert manager.allocated == 50
    assert manager.p_max == 200
    assert manager.p_min == 100


def test_no_buy_orders():
    order_1 = Order(user_id="U1", order_type="SELL", q=100, p=500)
    order_2 = Order(user_id="U2", order_type="SELL", q=60, p=40)
    orders = [order_1, order_2]

    expected = AuctionResult(q_max=0, p_min=None, p_max=None)
    actual = run_auction(orders)

    assert actual == expected


def test_no_sell_orders():
    order_1 = Order(user_id="U1", order_type="BUY", q=100, p=500)
    order_2 = Order(user_id="U2", order_type="BUY", q=60, p=40)
    orders = [order_1, order_2]

    expected = AuctionResult(q_max=0, p_min=None, p_max=None)
    actual = run_auction(orders)

    assert actual == expected


def test_simple_example_1():
    order_1 = Order(user_id="U1", order_type="BUY", q=100, p=500)
    order_2 = Order(user_id="U2", order_type="SELL", q=60, p=400)
    orders = [order_1, order_2]

    expected = AuctionResult(q_max=60, p_min=400, p_max=500)
    actual = run_auction(orders)

    assert actual == expected


def test_simple_example_2():
    order_1 = Order(user_id="U1", order_type="BUY", q=100, p=200)
    order_2 = Order(user_id="U2", order_type="SELL", q=50, p=300)
    orders = [order_1, order_2]

    expected = AuctionResult(q_max=0, p_min=None, p_max=None)
    actual = run_auction(orders)

    assert actual == expected


def test_simple_example_3():
    order_1 = Order(user_id="U1", order_type="BUY", q=50, p=200)
    order_2 = Order(user_id="U2", order_type="SELL", q=50, p=200)
    orders = [order_1, order_2]

    expected = AuctionResult(q_max=50, p_min=200, p_max=200)
    actual = run_auction(orders)

    assert actual == expected


def test_complex_example_1():
    order_1 = Order(user_id="U1", order_type="BUY", q=100, p=300)
    order_2 = Order(user_id="U2", order_type="SELL", q=50, p=200)
    order_3 = Order(user_id="U3", order_type="SELL", q=25, p=250)
    orders = [order_1, order_2, order_3]

    expected = AuctionResult(q_max=75, p_min=250, p_max=300)
    actual = run_auction(orders)

    assert actual == expected


def test_complex_example_2():
    order_1 = Order(user_id="U1", order_type="BUY", q=50, p=300)
    order_2 = Order(user_id="U2", order_type="SELL", q=100, p=200)
    order_3 = Order(user_id="U3", order_type="SELL", q=100, p=250)
    orders = [order_1, order_2, order_3]

    expected = AuctionResult(q_max=50, p_min=200, p_max=300)
    actual = run_auction(orders)

    assert actual == expected


def test_custom_complex_example():
    order_1 = Order(user_id="U1", order_type="BUY", q=50, p=300)
    order_2 = Order(user_id="U2", order_type="SELL", q=100, p=200)
    order_3 = Order(user_id="U3", order_type="SELL", q=100, p=200)
    orders = [order_1, order_2, order_3]

    expected = AuctionResult(q_max=50, p_min=200, p_max=300)
    actual = run_auction(orders)

    assert actual == expected
