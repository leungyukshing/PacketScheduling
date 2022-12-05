# CS7260 Final Project: Queuing-Algorithms

# File Structure

```
├── README.md
├── WFQ
│   ├── destination.py
│   ├── router.py
│   └── source.py
├── WF2Q
│   ├── destination.py
│   ├── router.py
│   └── source.py
├── WF2Q+
│   ├── destination.py
│   ├── router.py
│   └── source.py
├── QFQ
│   ├── destination.py
│   ├── router.py
│   └── source.py
└── DRR
    ├── destination.py
    ├── router.py
    └── source.py
```

# How to run?

Run each of the following command on a new terminal for each scheduling algorithm

```bash
$ python router.py
$ python destination.py
$ python source.py 0
$ python source.py 1
$ python source.py 2
```
# Result
|       | Average Throughput | Average Latency (ms) |         |         | Worst-case Latency (ms) |          |          |
|:-----:|:------------------:|:--------------------:|:-------:|:-------:|:-----------------------:|:--------:|:--------:|
|       |                    |        Flow 0        |  Flow 1 |  Flow 2 |          Flow 0         |  Flow 1  |  Flow 2  |
|  WFQ  |       0.60849      |        5.50887       | 5.77361 | 5.34764 |         10.97530        | 10.40571 | 10.44194 |
|  WF2Q |       0.60997      |        5.44373       | 4.37278 | 6.26225 |         10.37029        |  9.27594 | 10.92013 |
| WF2Q+ |       0.93343      |        5.0748        | 5.84614 |  10.397 |         9.26937         |  5.12817 |  9.86658 |
|  DRR  |       0.97722      |        0.0372        | 0.01148 | 0.04069 |         0.68941         |  0.02891 |  0.34967 |

# Reference:
[Github Ref](https://github.com/varshit97/Weighted-Fair-Queuing)

