#!/usr/bin/python
# coding=utf-8

import time
import getopt
import os
import sys

from constructive_heuristics import constructive_greedy_heuristic_r
from constructive_heuristics import constructive_peckish_heuristic_r
from constructive_heuristics import constructive_random_heuristic

from process_data import calculate_price
from process_data import get_number_of_problems
from process_data import load_data
from process_data import select_problem
from process_data import solution_table
from process_data import trivial_conditions
    
from local_search import Frame as local_search

# Class to measure speed.
class Stops:
    # Start counting (sec)
    def start_time( self ):
        self.time = time.time()
        return "0.000 sec"
    # Get elapsed time (sec)
    def current_time( self ):
        return str(round((time.time()-self.time), 3)) + " sec"
stops = Stops()

if __name__ == u"__main__":
    input_file_name = "./sets/gap1.txt"
    output_file = None
    task = "deluge"
    visualise = False
    decoration = True
    m_time = False # print start and end time
    
    stats = False # print statistics
    set_demand = [0]
    greedy_goals = ("maxdif","mindif","maxmax","minmax","minmin","maxmin","minavg")


    opts, args = getopt.getopt(
        sys.argv[1:],
        "hi:a:g:d:tvsb",
        ["help","input=","action=","greedygoal=","dataset=","time","visualize","solutions","beautyoff"]
        )
    
    for option in opts:
        if len(option)>0:
            option = (option[0], option[1].replace("=",""))
        if option[0] in ["-i","--input"]:
            # inputFile            
            if os.path.exists(option[1]):
                input_file_name = option[1]
        if option[0] in ["-b","--beautyoff"]:
            decoration = False
        if option[0] in ["-a","--action"]:
            # inputFile
            task = option[1]
            if task not in (
                "c",
                "cgreedy",
                "cpeckish",
                "crandom",
                "iterative",
                "deluge",
                "delugeall",
                "delugerandom",
                "delugegreedy",
                "delugepeckish"):
                    task = "default"
        if option[0] in ["-g","--greedygoal"]:                       
            if option[1] in greedy_goals:
                greedy_goals = [ option[1] ] 
            # default greedy_goals =
            # = ("maxdif","mindif","maxmax","minmax","minmin","maxmin","minavg")
        if option[0] in ["-d","--dataset"]:
            # which test set to select
            if option[1].isdigit():
                set_demand = [ int(option[1]) ]
            else:
                set_demand = "*" # select all            
        if option[0] in ["-v","--visualise"]:
            visualise = True
            try:
                from visualisation import visualize as visualise_sol
            except (Exception), e:
                print e.message()
                visualise = False
        if option[0] in ["-t","--time"]:
            m_time = True
        if option[0] in ["-s","--solutions"]:
            stats = True
        if option[0] in ["-h","--help"]:
            print """
    Python 2.5 or 2.6 is required.

    Call python main.py to run a program.

    "help"
    "input="      main.py -i=opt (--input=opt) path to gap.txt    
    "action="       main.py -a=opt (--action=opt)
        Specify the goal.
        "c", all constructive heuristics
        "cgreedy", constructive greedy heuristic
        "cpeckish", constructive peckish heuristic
        "crandom", constructive random heuristic
        "iterative", iterative local search with random initialisation
        "deluge", great deluge algorithm with random initialisation
        "delugegreedy", great deluge algorithm with greedy initialisation
        "delugepeckish", great deluge algorithm with peckish initialisation
        "delugerandom", great deluge algorithm with random initialisation
        "delugeall", great deluge algorithm with all initialisation
    "greedygoal=" main.py -g=default (--greedygoal=default)
        Use selected greedy criteria:
        "maxdif","mindif","maxmax","minmax","minmin","maxmin","minavg"
    "dataset="    main.py -d=number (--dataset=0) to use selected test set in a file
                  main.py -d=* (--dataset=*) to use all test sets in a file
    "time"        main.py -t (--time) to view start and end time
    "beautyoff"   main.py -b (--beautyoff) strip some text blocks
    "visualise"   main.py -v (--visualise) to run 3D visualization
        Modules matplotlib, numpy and scipy are required!
    "solutions"   main.py -s (--solutions) to view assigment table
                """

    loaded_data = load_data( input_file_name )
    if set_demand == "*":
        set_demand = range( get_number_of_problems(loaded_data) )

    # for each set independently
    for set_id in set_demand:
        w_price, w_space, w_capacity = select_problem( loaded_data, set_id)
        best_sol = 32000
        best_type = None
        if decoration:
            print "\n Processing...\n Filename: %s\n Set: %s" % (input_file_name, set_id)
            print " -------------------------"
        if trivial_conditions( w_price, w_space, w_capacity ):
            # if trivial conditions succed, continue
            
            # test all constructvie heuristics
            if task in ("c", "crandom", "cpeckish", "cgreedy"):
                if task == "c" or task == "crandom":
                    for i in range(8):
                        if m_time:
                            print "@ Start constructive %s h.: %s" % (
                                "random", stops.start_time()
                                )
                        solution = constructive_random_heuristic( w_price, w_space, w_capacity )
                        if m_time:
                            print "@ End constructive %s h.: %s" % (
                                "random", stops.current_time()
                                )
                        temp_price = calculate_price( solution, w_price )
                        if temp_price < best_sol:
                            best_sol = temp_price
                            best_type = "random"
                        print "\t\trandom %s:       %s." % (str(i+1), str(temp_price) )
                if task == "c" or task == "cgreedy":
                    for crit in greedy_goals:
                        if m_time:
                            print "@ Start constructive %s h.: %s" % (
                                "greedy", stops.start_time()
                                )
                        solution = constructive_greedy_heuristic_r( w_price, w_space, w_capacity, crit )
                        if m_time:
                            print "@ End constructive %s h.: %s" % (
                                "greedy", stops.current_time()
                                )
                        temp_price = calculate_price( solution, w_price )
                        if temp_price < best_sol:
                            best_sol = temp_price
                            best_type = "greedy: %s" % (crit)
                        print "\t\tgreedy %s:  %s" % (crit, str(temp_price))
                if task == "c" or task == "cpeckish":                    
                    for crit in greedy_goals:
                        if m_time:
                            print "@ Start constructive %s h.: %s" % (
                                "peckish", stops.start_time()
                                )
                        solution = constructive_peckish_heuristic_r( w_price, w_space, w_capacity, crit )
                        if m_time:
                            print "@ End constructive %s h.: %s" % (
                                "peckish", stops.current_time()
                                )
                        temp_price = calculate_price( solution, w_price )
                        if temp_price < best_sol:
                            best_sol = temp_price
                            best_type = "peckish: %s" % (crit)
                        print "\t\tpeckish %s: %s" % (crit, str(temp_price))
                if stats:
                    print solution_table( solution )
                if visualise:
                    visualise_sol( w_price, w_space, w_capacity, solution )
            # ITERATIVE
            if task == "iterative":
                for i in range(8):
                    if m_time:
                        print "@ Start constructive h.: %s" % (
                            stops.start_time()
                            )
                    init_solution = constructive_random_heuristic(
                        w_price, w_space, w_capacity
                        )
                    if m_time:
                        print "@ Start iterative ls.: %s" % (
                            stops.current_time()
                            )
                    frame = local_search( init_solution, w_price, w_space, w_capacity )
                    solution = frame.run_iteration()
                    temp_price = calculate_price( solution, w_price )
                    if temp_price < best_sol:
                        best_sol = temp_price
                        best_type = "iterative"
                    if m_time:
                        print "@ Finish: %s" % ( stops.current_time() )
                    print "\t\tIterative: %s" % (str(temp_price))
                if stats:
                    print solution_table( solution )
                if visualise:
                    visualise_sol( w_price, w_space, w_capacity, solution )
            # GREAT DELUGE            
            if task in ("deluge", "delugeall", \
                    "delugerandom", "delugegreedy", "delugepeckish"):                
                if task == "deluge":                    
                    todo = ["delugepeckish"]
                if task == "delugeall":
                    todo = ["delugerandom", "delugegreedy", "delugepeckish"]
                if task in ("delugerandom", "delugegreedy", "delugepeckish"):
                    todo = [task]
                for type in todo:
                    if m_time:
                        print "@ Start constructive %s h.: %s" % (
                            type, stops.start_time()
                            )
                    init_solution = None
                    if type == "delugerandom":
                        init_solution = constructive_random_heuristic(
                            w_price, w_space, w_capacity
                        )
                    if type == "delugegreedy":
                        init_solution = constructive_greedy_heuristic_r(
                            w_price, w_space, w_capacity, greedy_goals[0]
                        )
                    if type == "delugepeckish":
                        init_solution = constructive_peckish_heuristic_r(
                            w_price, w_space, w_capacity, greedy_goals[0]
                        )
                    if m_time:
                        print "@ Start deluge ls.: %s" % ( stops.current_time() )
                    frame = local_search( init_solution, w_price, w_space, w_capacity )

                    solution = frame.great_deluge()
                    
                    temp_price = calculate_price( solution, w_price )
                    if temp_price < best_sol:
                        best_sol = temp_price
                        best_type = "deluge: %s" % (type)
                    if m_time:
                        print "@ Finish: %s" % ( stops.current_time() )
                    print "\t\tDeluge %s: %s" % (type, str(temp_price))
                if stats:
                    print solution_table( solution )
                if visualise:
                    visualise_sol( w_price, w_space, w_capacity, solution )
        else:
            print "Set violates trivial constrains!"

        if decoration:
            print """
            Statistics...
            Best: %s
            Heuristic: %s
            -------------------------""" % (str(best_sol), best_type)
                
        
