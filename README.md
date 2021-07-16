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

## Questions

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