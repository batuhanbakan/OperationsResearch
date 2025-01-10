class Knapsack:

  def __init__(self, values, weights, capacity):

    self.values = values
    self.weigths = weights
    self.capacity = capacity

    self.n = len(self.values)

  def greedy(self):

    self.ratios = []
    for i in range(self.n):
      self.ratios.append(self.values[i] / self.weigths[i])

    self.selection = []
    for i in range(self.n):
      self.selection.append(0)

    self.currentValue = 0
    self.currentCapacity = 0

    self.index = self.ratios.index(max(self.ratios))

    while (self.currentCapacity + self.weigths[self.index]) <= self.capacity:

      self.selection[self.index] = 1
      self.currentCapacity += self.weigths[self.index]
      self.currentValue += self.values[self.index]
      self.ratios[self.index] = 0

      self.index = self.ratios.index(max(self.ratios))

  def solve(self):

    self.greedy()

    return f"Objective Value is: {self.currentValue}"

"""
Description:

    Solves the knapsack problem.


Arguments:

- values: Values of items.
- weights: Weights of items.
- capacity: Capacity of the knapsack.

Returns:

    A Knapsack object.

Example:

```
values = [20, 10, 35, 55, 60]
weights = [1, 2, 3, 4, 5]
capacity = 10

k = Knapsack(values, weights, capacity)
k.solve()
```
"""