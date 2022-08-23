# developer scripts

This is a collection of random scripts that are helpful to developing on TVM's CI. As one-off scripts these do not conform to the usual TVM quality standards which is why they are stored out of tree.

## `determine_shards.py`

Given a goal runtime for each test shard and a Jenkins job, print out the number of shards that should be used for each step.

```bash
# print out number of shards per test step
python determine_shards.py --runtime-goal-m 90 --branch PR-12473

# see bottleneck steps individually
python determine_shards.py --runtime-goal-m 90 --branch PR-12473 --list-steps
```