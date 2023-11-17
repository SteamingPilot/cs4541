Date: 11/04/2023
Class: CS4541
Assignment: Cache Simulator
Author(s): Md Abiruzzaman Palok

Instruction:
1.To compile the program, use the following command
    gcc -std=c99 -Wall -o cache_sim cache_sim.c

    NOTE: make sure the queue.h header file is in the same folder as the cache_sim.c

2. To run cache simulator in a trace file use the following command:
    ./cache_sim [-hv] -s <s> -E <E> -b <b> -t <tracefile>

    NOTE:
        -h: Optional help flag that prints usage info
        -v: Optional verbose flag that displays trace info
        -s <s>: Number of set index bits (S = 2 s is the number of sets)
        -E <E>: Associativity (number of lines per set)
        -b <b>: Number of block bits (B = 2 b is the block size)
        -t <tracefile>: Name of the valgrind trace to replay (include path)

    Example:
        To run a dave.trace file in the traces folder you would do something like:

            ./cache_sim -v -s 4 -E 2 -b 3 -t ./traces/dave.trace

