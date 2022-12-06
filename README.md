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

[1] Jon CR Bennett and Hui Zhang. 1997. Hierarchical packet fair queueing algorithms. IEEE/ACM Transactions on networking 5,5 (1997), 675–689. 
<br>
[2] Fabio Checconi, Luigi Rizzo, and Paolo Valente. 2012. QFQ:
Efficient packet scheduling with tight guarantees. IEEE/ACM
Transactions on Networking 21, 3 (2012), 802–816.
<br>
[3] Abhay K Parekh and Robert G Gallager. 1993. A generalized
processor sharing approach to flow control in integrated ser-
vices networks: the single-node case. IEEE/ACM transactions
on networking 1, 3 (1993), 344–357.
<br>
[4] Sriram Ramabhadran and Joseph Pasquale. 2003. Stratified
round robin: A low complexity packet scheduler with band-
width fairness and bounded delay. In Proceedings of the 2003
conference on applications, technologies, architectures, and pro-
tocols for computer communications. 239–250.
<br>
[5] George N Rouskas and Zyad Dwekat. 2007. A practical and
efficient implementation of WF 2 Q+. In 2007 IEEE International
Conference on Communications. IEEE, 172–176.
<br>
[6] Madhavapeddi Shreedhar and George Varghese. 1995. Effi-
cient fair queueing using deficit round robin. In Proceedings of 
the conference on Applications, technologies, architectures, and
protocols for computer communication. 231–242.
<br>
[7] Google Techtalk. [n. d.]. New Developments in Link Emulation
and packet Scheduling in FreeBSD, Linux, and Windows. <https://www.youtube.com/watch?v=r8vBmybeKlE>.
<br>
[8] Hui Zhang and Jon CR Bennett. 1996. WF2Q: worst-case fair
weighted fair queueing. In IEEE INFOCOM, Vol. 96. 120–128.
