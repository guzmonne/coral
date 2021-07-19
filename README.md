# Coral - Take Home Exercise

Implementation of "Two-sided Single-Price Auctions".

## Test

Install the project dependencies by running:

```bash
pip install -r requirements.txt
```

Install package in `editable` mode.

```bash
pip install -e .
```

Run the tests using `pytest`:

```bash
pytest
```

## Documentation

The module documentation can be found at the `docs/` directory.

It is generated with [`pdoc`](https://pdoc3.github.io/pdoc/).

To generate if from the source install `pdoc` with `pip` and run:

```bash
pdoc --html coral --output-dir docs
```

Or if you want to start an HTTP server to read the documentation without
building it you can run:

```bash
pdoc --html : coral
```

And then go to [`http://localhost:8080`].

## Design Model Questions

**How do we identify a user more willing to buy or sell than other?**

One way could be to just focuse on the max/min price, disregarding the amount
of shares. For example, an offer to sell with `p=500,q=10` would be idententified
as more willing to sell than one with `p=501,q=1000`. Even though the amount of
shares that the second user wants to sell it's much higher, and the price difference
is minimal.

Another way could be considering the total value of the offer: `p * q`. But this
can also produce undesired edge cases when there is too much asymetry between
variables.

The current code uses a mix of the last two examples: It first evaluates orders
regarding its `p` value but, if they are equal, it uses the value of `q` to
determine which is best. If more than one offer have the same values of `p` and
`q`, then they are grouped together, and the shares allocations are divided
between them.

**Can shares be fractioned?**

If we need to allocate 100 shares between 3 users, does it make sense to split
one share in thirds an allocate one third to each user?

**How do you describe an order that is completed?**

Meaning a buy/sell order in which all the shares have been allocated.

**How do you describe an order that is better than other?**

Is it that a user is more willing to buy/sell or that the offer is just better.

**How do you call the action of having the auction?**

On my code I describe it as `allocate_orders` since what I did was match the
orders according to the user's willingness to buy or sell shares, and allocate
them. I believe a more descriptive term for the action can be used to align the
code to the design model.