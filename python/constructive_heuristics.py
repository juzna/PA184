#!/usr/bin/env python

import random
from heapq import heappush, heappop
    
# Select random job, select first fitting worker
# Instead of backtracking, release random job
def constructive_random_heuristic( w_price, w_space, w_capacity ):    
    available_jobs = set( range(len(w_price[0])))
    wc = len(w_capacity)
    available_capacity = w_capacity[:] # copy list
    solution = {}
    
    safe_count = 0
    # until all jobs are assigned
    while len(available_jobs)>0:
        safe_count += 1
        if safe_count>10000:
            print "no solution avaible in 10000 steps."
            break
        """ select job """
        jc = len(available_jobs)
        # random selection
        select_job = list(available_jobs)[ random.randint(0, jc-1) ]
        # job isnt avaible anymore
        available_jobs.remove( select_job )
        """ select worker """
        # feasable workers
        candidates = []
        for worker in range(wc):
            if available_capacity[ worker ] >= w_space[ worker ][ select_job ]:
                candidates.append(worker)
        # select random worker if available
        if len(candidates)>0:
            select_worker = candidates[random.randint(0, len(candidates)-1 )]
            # udpate available capacity
            available_capacity[ select_worker ] -= w_space[ select_worker ][ select_job ]
            # save solution
            solution[ select_job ] = select_worker
        else:
            # otherwise clear selection
            available_jobs.add( select_job )
            # because the job cant be assigned, we release another job from the worker
            # select random assigned job
            remove = solution.keys()[ random.randint(
                0, len( solution.keys() )-1
                )]
            # free worker capacity
            worker_inc = solution[remove]
            available_capacity[worker_inc] += w_space[ worker_inc ][ remove ]
            del solution[remove]
            # make job available
            available_jobs.add( remove )
        
            
            
    return solution
        

" NOT IMPLEMENTED "
def constructive_peckish_heuristic_r( w_price, w_space, w_capacity, criteria ):
    available_jobs = set( range(len(w_price[0])))
    w_id = range( len(w_capacity) )
    available_capacity = w_capacity[:] # copy list
    solution = {}
    return count_greedy(
        w_price, w_space, available_jobs, available_capacity, solution, w_id,
        criteria, True
        )

"""
while we have unassigned jobs:
    Select job by criteria
    (for example biggest difference between min and max available assertion).
    Assign job to the cheapest available worker.
    If there is no available worker nor job, backtrack to the last assigment and
    select next optimal assignment.

style:
            if criteria == "maxdif":
                criteria_val = -(max-min)
            if criteria == "mindif":
                criteria_val = -(min-max)
            if criteria == "maxmax":
                criteria_val = -(max)
            if criteria == "minmax":
                criteria_val = (max)
            if criteria == "minmin":
                criteria_val = (min)
            if criteria == "maxmin":
                criteria_val = -(min)
            if criteria == "minavg":
                criteria_val = -(max+min)/2
"""
def constructive_greedy_heuristic_r( w_price, w_space, w_capacity, criteria ):
    available_jobs = set( range(len(w_price[0])))
    w_id = range( len(w_capacity) )
    available_capacity = w_capacity[:] # copy list
    solution = {}
    return count_greedy(
        w_price, w_space, available_jobs, available_capacity, solution, w_id, criteria
        )

# recursive function
# select best job
# assign worker
# call recursively
# backtrack if call return None
# ++ peckish: give some randomness
def count_greedy(
    w_price, w_space, available_jobs, available_capacity, solution, w_id,
    criteria, peckish=False
    ):

    if len(available_jobs) == 0:
        return solution

    # job to be processed
    selected_job = None
    if peckish and len(available_jobs)>0:
        # peckish select random job
        selected_job = list(available_jobs)[ random.randint(0, len(available_jobs)-1) ]
    else:
        # greedy, select best job
        selected_job = select_best_job(
            w_price, w_space, available_jobs, available_capacity, w_id, criteria
            )
    
    if selected_job == None:
        return None
    
    w_order = []
    
    for worker_id in w_id:
        if available_capacity[worker_id] >= w_space[worker_id][selected_job]:
            heappush( w_order, (w_price[worker_id][selected_job], worker_id))
    while len(w_order) > 0:
        worker_id = heappop( w_order )[1]
        
        solution[selected_job] = worker_id
        available_capacity[worker_id] -= w_space[worker_id][selected_job]
        available_jobs.remove(selected_job)
        new_solution = count_greedy(
            w_price, w_space, available_jobs, available_capacity,
            solution, w_id, criteria, peckish
            )
    
        if new_solution != None:
            return new_solution
        else:
            del solution[selected_job]
            available_jobs.add(selected_job)
            available_capacity[worker_id] += w_space[worker_id][selected_job]
    return None

def select_best_job( w_price, w_space, available_jobs, available_capacity, w_id, criteria ):
    jobs = []
    for job_id in available_jobs:
        min = 32000
        max = -1
        for worker_id in w_id:
            if available_capacity[worker_id] > w_space[worker_id][job_id]:
                price = w_price[worker_id][job_id]
                if price < min:
                    min = price
                if price > max:
                    max = price

        if max > -1:
            if criteria == "maxdif":
                criteria_val = -(max-min)
            if criteria == "mindif":
                criteria_val = -(min-max)
            if criteria == "maxmax":
                criteria_val = -(max)
            if criteria == "minmax":
                criteria_val = (max)
            if criteria == "minmin":
                criteria_val = (min)
            if criteria == "maxmin":
                criteria_val = -(min)
            if criteria == "minavg":
                criteria_val = -(max+min)/2
            heappush( jobs, (criteria_val, job_id) )
    if len( jobs ) == 0:
        return None
    # maximum difference
    return heappop( jobs )[1] 
