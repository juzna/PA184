#!/usr/bin/env python

def load_data( filename = "./sets/gap1.txt" ):
    input = open( filename, "r" )
    lines = [ line.replace( "\n", "" ) for line in input.readlines() ]
    input.close()

    number_of_sets = int( lines[0] )
    
    cur_line = 1
    while(lines[cur_line] == ""):
        cur_line += 1

    out_w_price = [[] for i in range( number_of_sets) ]
    out_w_space = [[] for i in range( number_of_sets) ]
    out_w_capacity = [[] for i in range( number_of_sets) ]
    
    for set_id in range( number_of_sets ):        
        # wc: worker_count number of workers
        # jc: job_count number of jobs        
        wc, jc = [ int( number ) for number in lines[ cur_line ].split() ]
        cur_line += 1
        for worker in range( wc ):
            out_w_price[ set_id ].append(
                [ int( number ) for number in lines[cur_line + worker].split() ]
                )
            out_w_space[ set_id ].append(
                [ int( number ) for number in lines[ wc + cur_line + worker].split() ]
                )
        out_w_capacity[ set_id ] = [ int( number ) for number in lines[ 2*wc + cur_line].split() ]
        cur_line += 1 + 2*wc + 1        
        
        while len(lines)-1 > cur_line and lines[cur_line] == "":
            cur_line += 1
    return ( out_w_price, out_w_space, out_w_capacity )

# + loaded_data:
#   output of load_data
# @return number of data sets
def get_number_of_problems( loaded_data ):
    return len(loaded_data[0])
    
# + loaded_data:
#   output of load_data
# ++ index:
#   select which set to use
def select_problem( loaded_data, index = 0 ):
    if index >= len(loaded_data[0]):
        # out of range
        index = 0
    
    w_price = loaded_data[0][index]
    w_space = loaded_data[1][index]
    w_capacity = loaded_data[2][index]
    return w_price, w_space, w_capacity

# if sum of minimal demands of each jobs exceeds maximum capacity of workers
# or
# if demand of one job exceeds all capacities of workers
# @return False and write error code
# otherwise:
# @return True
def trivial_conditions( w_price, w_space, w_capacity ):
    # 1:
    used_cap = 0
    for job_id in range( len ( w_space[0] ) ):
        used_cap += min( [jv[job_id] for jv in w_space] )        
    max_cap = sum( w_capacity )

    if max_cap < used_cap:
        print "the capacity of workers %s is exceeded by demand of jobs %s." % (
            max_cap, used_cap
            )
        return False
    
    # 2:
    for job_id in range( len( w_space[0] ) ):
        fit = False
        for work_id in range( len ( w_capacity ) ):
            if w_space[work_id][job_id] <= w_capacity[work_id]:
                fit = True
        if not fit:
            print "the demand of job %s exceeds all workers capacities." % (            
                str(job_id)
                )
            return False
    return True

# + solution in dictionary
# + price vector
# @return number
def calculate_price( result, w_price ):
    total = 0
    for key in result.keys():
        total += w_price[ result[key] ][ key ]
    return total


# + solution if format dictionary job:worker
# @return string with beautified output
def solution_table( solution ):
    output = "\n"
    output += "\t******************\n"
    output += "\t| Job\t| Worker\n"
    output += "\t******************\n"
    for key in solution.keys():
        output += "\t| %s\t| %s\n" % ( str(key), str(solution[key]) )
    output += "\t******************\n"
    return output