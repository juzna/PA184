#!/usr/bin/env python
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection, LineCollection
from matplotlib.colors import colorConverter
import matplotlib.pyplot as plt
import numpy as np
import random
import math

"""
Draw 3d graph, green solution are optimal, yellow, orange and red worse.
+ w_price list of lists with price demand for each worker
+ w_space list of lists with space demand for each worker
+ w_capacity list of workers' capacities
+ solution dictionary job:worker
"""
def visualize( w_price, w_space, w_capacity, solution ):
    
    min_price = min( [min(price_list) for price_list in w_price] )
    max_price = max( [max(price_list) for price_list in w_price] )
    
    width_workers = len(w_capacity)
    width_jobs = len(w_price[0])
    
    job_matrice = []
    for job_id in range(width_jobs):
        job_matrice.append(
            [ price[job_id] for price in w_price]
        )
    
    fig = plt.figure()
    ax = Axes3D(fig)    
        
    zs = range(width_jobs)   
    verts = []
    facecolors = []
    for job_id in range( width_jobs ):
        selected_price = float( w_price[ solution[job_id] ][job_id] )
        min_price = float( min( job_matrice[job_id] ) )
        goodness = min_price/selected_price
        
        facecolors.append( colorConverter.to_rgba( (1-(math.pow(goodness,5)), goodness, 0.5), alpha=0.6) )
        verts.append( zip(
            [0] + range(width_workers) + [width_workers-1],
            [0] + job_matrice[job_id] + [0]
            )
        )
    
    import random
    
    poly = PolyCollection(verts, facecolors=facecolors)
    poly.set_alpha(0.2)
    
    ax.add_collection3d(poly, zs=zs, zdir='y')
    
    selected_workers = []
    selected_prices = []
    for job_id in range(width_jobs):
        selected_workers.append( solution[job_id] )
        selected_prices.append( job_matrice[job_id][ solution[job_id] ] )
    

  
    curve_pos = []
    for job_id in range(width_jobs):
        w_x = selected_workers[job_id]
        curve_pos.append( zip(
            [w_x - 0.1, w_x, w_x + 0.1],
            [0, selected_prices[job_id] + 0.1, 0]
            )
        )
    curve = PolyCollection( curve_pos, facecolors=facecolors )
    curve.set_alpha(1)
    
    ax.add_collection3d(curve, zs = [z-0.1 for z in zs], zdir='y') 
    

    
    ax.set_xlim3d(0, width_workers-0.5)
    ax.set_ylim3d(0, width_jobs)
    ax.set_zlim3d(0, max_price)
    
    ax.set_xlabel('Workers')
    ax.set_ylabel('Tasks')
    ax.set_zlabel('Prices')
    
    plt.show()
    

if __name__ == u"__main__":
    w_price = [
        [19, 23, 24, 20, 20, 25, 16, 21, 24, 15, 17, 17, 20, 20, 20],
        [25, 24, 16, 21, 19, 17, 17, 19, 23, 21, 21, 23, 20, 15, 16],
        [16, 21, 25, 22, 24, 24, 16, 17, 15, 18, 15, 17, 18, 24, 18],
        [25, 24, 18, 19, 15, 18, 20, 22, 23, 18, 16, 19, 17, 15, 22],
        [25, 19, 21, 22, 20, 15, 20, 19, 18, 18, 17, 23, 17, 25, 25]
        ]
    w_space = [
        [16, 12, 8, 20, 18, 10, 12, 8, 14, 23, 19, 14, 15, 15, 24],
        [16, 18, 19, 22, 13, 20, 9, 7, 25, 10, 20, 13, 11, 15, 16],
        [6, 20, 20, 5, 14, 12, 6, 15, 22, 18, 13, 23, 23, 18, 25],
        [18, 23, 25, 17, 25, 13, 23, 23, 13, 20, 20, 23, 17, 19, 24],
        [12, 17, 15, 25, 22, 5, 24, 19, 12, 25, 23, 21, 23, 19, 18]
        ]
    w_capacity = [36, 37, 38, 48, 44]
    solution = {0: 3, 1: 0, 2: 4, 3: 2, 4: 2, 5: 4, 6: 2, 7: 0, 8: 3, 9: 1, 10: 2, 11: 4, 12: 1, 13: 0, 14: 1}
    solution = {0: 2, 1: 0, 2: 3, 3: 2, 4: 2, 5: 4, 6: 3, 7: 0, 8: 4, 9: 1, 10: 2, 11: 0, 12: 1, 13: 1, 14: 4}
    visualize(w_price, w_space, w_capacity, solution)
