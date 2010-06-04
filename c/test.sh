#!/bin/bash
clear;g++ -pthread -ggdb3 -o $1 $1.c && valgrind --leak-check=full ./$1 constant constant - - sets/gap8.txt