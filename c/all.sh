#!/bin/bash
clear
g++ -O2 -pthread -o main main.c || exit

for ds in 1 2 3 4 5 6 7 8 9 10 11 12; do
  for job in constant order order-r price-diff; do
    for worker in constant order order-r free-capacity price; do
      for jr in - linear; do
        for wr in - linear; do
          echo "$ds $job $worker $jr $wr"
          ./main $job $worker $jr $wr sets/gap$ds.txt
          echo "------------"
        done
      done
    done
  done
  
  # random
  #for i in `seq 10`; do
    echo "$ds - - rand rand"
    ./main - - rand rand sets/gap$ds.txt
    echo "------------"
   # sleep 2
  #done
done
