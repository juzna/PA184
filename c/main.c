/*
* Very simple Greedy GAP solver
* - findNextJob returns first not assigned job
* - findWorkersForJob orders workers by free capacity (max free capacity goes first)
*/
#include "main.h"


/**
* Worker order functions
*/

// Give all workers same priority
char _gw_constant(Problem *p, int j, int workers[]) {
	for(int w = 0; w < p->wc; w++) workers[w] = 1;
}

// Worker priority as it's number
char _gw_order(Problem *p, int j, int workers[]) {
	for(int w = 0; w < p->wc; w++) workers[w] = p->wc - w;
}

// Worker priority as reverse order number
char _gw_orderr(Problem *p, int j, int workers[]) {
	for(int w = 0; w < p->wc; w++) workers[w] = w;
}

// Workers have priority same as free capacity
char _gw_freeCapacity(Problem *p, int j, int workers[]) {
	for(int w = 0; w < p->wc; w++) workers[w] = p->capacityFree[w];
}

// Workers priority by price of assigning job
char _gw_price(Problem *p, int j, int workers[]) {
	int priceMax = 0;
	
	for(int w = 0; w < p->wc; w++) {
		int space = getSpace(p, w, j); // Space required
		if(p->capacityFree[w] < space) {
			workers[w] = -1; // Worker is full
		}
		else {
			int price = getPrice(p, w, j);
			if(price > priceMax) priceMax = price; // Store maximal price
			workers[w] = price;
		}
	}
	
	// Revert high prices to small priorities
	for(int w = 0; w < p->wc; w++) {
		if(workers[w] > 0) workers[w] = priceMax - workers[w];
	}
}




/**
* Job order functions
*/

// Job priority is constant
char _gj_constant(struct Problem *p, int jobs[]) {
	for(int j = 0; j < p->jc; j++) jobs[j] = 1;
}

// Job priority by order
char _gj_order(struct Problem *p, int jobs[]) {
	for(int j = 0; j < p->jc; j++) jobs[j] = p->jc - j;
}

// Job priority reverse order
char _gj_orderr(struct Problem *p, int jobs[]) {
	for(int j = 0; j < p->jc; j++) jobs[j] = j;
}

// Job priority highest with biggest difference between max- and min-price
char _gj_pricediff(struct Problem *p, int jobs[]) {
	int diff, min = -1, max = -1;
	
	for(int j = 0; j < p->jc; j++) {
		// Find min and max price
		for(int w = 0; w < p->wc; w++) {
			int c = getPrice(p, w, j);
			if(c > max) max = c;
			if(c < min || min == -1) min = c;
		}
		
		// Difference
		diff = max - min;
		jobs[j] = diff;
	}
}







// Callback list: Get worker priority
const GetWorkersPriorityEntry getWorkersPriorityCallbacks[] = {
	{ "constant", _gw_constant },
	{ "order", _gw_order },
	{ "order-r", _gw_orderr },
	{ "free-capacity", _gw_freeCapacity },
	{ "price", _gw_price },
	{ NULL, NULL },
};

// Callback list: Get jobs priority
const GetJobsPriorityEntry getJobPriorityCallbacks[] = {
	{ "constant", _gj_constant },
	{ "order", _gj_order },
	{ "order-r", _gj_orderr },
	{ "price-diff", _gj_pricediff },
	{ NULL, NULL },
};

// Callback list: Randomizers
const RandomizerEntry randomizerCallbacks[] = {
	{ "rand", randomizeTotal},
	{ "linear", randomizeLinear },
	{ "add", randomizeAdd},
	{ NULL, NULL },
};

GetJobsPriority getJobsPriorityCallback(char *name) {
	// Find callbacks
	const GetJobsPriorityEntry *cb = getJobPriorityCallbacks;
	
	for(; cb && cb->name; ++cb) if(!strcmp(cb->name, name)) return cb->cb;
	return NULL;
}

GetWorkersPriority getWorkersPriorityCallback(char *name) {
	// Find callbacks
	const GetWorkersPriorityEntry *cb = getWorkersPriorityCallbacks;
	
	for(; cb && cb->name; ++cb) if(!strcmp(cb->name, name)) return cb->cb;
	return NULL;
}

Randomizer getRandomizerCallback(char *name) {
	// Find callbacks
	const RandomizerEntry *cb = randomizerCallbacks;
	
	for(; cb && cb->name; ++cb) if(!strcmp(cb->name, name)) return cb->cb;
	return NULL;
}

#define DUMP_LIST(TEntry, List) {\
 const TEntry *cb = List;\
 for(; cb && cb->name; ++cb) printf("%s ", cb->name);\
 printf("\n");\
}

void usage(char *file) {
	printf("Usage: %s jobs workers job-randomizer worker-randomizer dataset [set-index]\n", file);

	// Dump Job order cb's
	printf("   Job order funcions: "); DUMP_LIST(GetJobsPriorityEntry, getJobPriorityCallbacks); 
	printf("   Worker order funcions: "); DUMP_LIST(GetWorkersPriorityEntry, getWorkersPriorityCallbacks);
	printf("   Randomizers: "); DUMP_LIST(RandomizerEntry, randomizerCallbacks);
	printf("\n");
	
	printf("Sample: %s order order - - sets/gap1.txt 0 # priorize jobs and workers by it's order, no randomize, dataset gap1.txt, first problem\n", file);
	printf("Sample: %s price-diff free-capacity linear linear sets/gap1.txt 0 # heuristics for jobs and workers, peckish\n", file);
	printf("Sample: %s - - rand rand sets/gap1.txt 0 # no heuristics for jobs and workers, totally random\n", file);
	printf("\n");

	printf("Environment variables:\n  DEBUG=1 - print debug informations\n  SIMPLE=1 - print just problem number, price, used space and time in miliseconds\n");
	printf("  Sample: SIMPLE=1 %s order order - - sets/gap1.txt 0\n", file);
	
	printf("\n");
	exit(1);
}


// Main function
int main(int argc, char**argv) {
	// Find callbacks
	const GetJobsPriorityEntry *cb = getJobPriorityCallbacks;
	
	if(argc < 5) usage(argv[0]);
	
	// Create solver
	Solver solver;
	solver.findJobMethod = Priority;
	solver.getJobsPriority = getJobsPriorityCallback(argv[1]);
	solver.getWorkersPriority = getWorkersPriorityCallback(argv[2]);
	solver.randomizeJobs = getRandomizerCallback(argv[3]);
	solver.randomizeWorkers = getRandomizerCallback(argv[4]);

	//printf("%u %u %u %u\n", solver.getJobsPriority, solver.getWorkersPriority, solver.randomizeJobs, solver.randomizeWorkers);
	
	// Run program
	return main_(&solver, argc - 4, argv + 4);
}
