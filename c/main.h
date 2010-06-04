/*
* Greedy GAP solver
*
* This file is not much like C++ header file look like, but it's made for simplicity.
* Here are defines basic functions for several Greedy GAP solvers invoked from other files
*
* You can use functions:
*  - loadData(char* file) - loads set of problems from text file defined in PA184
*  - dumpProblem(Problem *p) - dump problem definition for users
*  - dumpProblem2(Problem *p) - dump problem definition in loadData() format
*  - dumpResult(Problem *p)   - dump results of solved problem
*  - solveGreedy(Problem *p)  - tries to solve the problem
*  - solveGreedyAndDump(...)  - try to solve problem and dump results
*  - main_(...)               - run program with given solver
*
* Check main.c for example solver solution.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <unistd.h>

#define DIE(x) { printf("%s\n", x); exit(1); }
#define ROTATE(x) (x) = (x)
#define microtime ((int)((clock())*1E3/CLOCKS_PER_SEC))

char debug = 0; // Show debug info
char simple = 0; // Simple output
char quit = 0; // Quitting

struct Problem;
struct Solver;
struct WorkerWithProblem;
struct JobWithProblem;

enum FindJobMethod {
	Callback = 1,
	Priority = 2,
};

typedef char (* GetJobsPriority)(struct Problem *p, int jobs[]);
typedef char (* GetWorkersPriority)(struct Problem *p, int job, int workers[]); // Callback to order jobs
typedef char (* Randomizer)(struct Problem *p, int num, int items[]);
typedef int (* FindNextJob)(struct Problem *p);

// Solver info -> defines solver callbacks
struct Solver {
	enum FindJobMethod findJobMethod; // What method is used to find job
	FindNextJob findNextJob;
	GetJobsPriority getJobsPriority; // Callback to order jobs
	GetWorkersPriority getWorkersPriority;
	Randomizer randomizeJobs;
	Randomizer randomizeWorkers;
};

struct GetJobsPriorityEntry {
	char *name;
	GetJobsPriority cb;
};

struct GetWorkersPriorityEntry {
	char *name;
	GetWorkersPriority cb;
};

struct RandomizerEntry {
	char *name;
	Randomizer cb;
};

struct Problem {
	// Settings
	int index;
	int wc;
	int jc;
	int *price;
	int *space;
	int *capacity;
	
	// Calculations
	int *assignments; // Assignment job to worker
	int *capacityFree; // Free capacity for each worker
	
	// Solver
	struct Solver *solver;
	int actualJob;
	void *solverData; // Any kind of data solver would like to associate with this problem
	JobWithProblem *jobList;
	char solved;
	
};

// Touple of worker and associated problem (used for sorting, because qsort not accepts scope parameter)
struct WorkerWithProblem{
	Problem *problem;
	int worker;
	long int priority;
};

// Touple of job and associated problem (used for sorting, because qsort not accepts scope parameter)
struct JobWithProblem{
	Problem *problem;
	int job;
	long int priority;
};


// Get price for worker and job
inline int getPrice(Problem *problem, int w, int j) {
	return (w >= problem->wc || j >= problem->jc) ? -1 : problem->price[w * problem->jc + j];
}

// Get space for worker and job
inline int getSpace(Problem *problem, int w, int j) {
	return (w >= problem->wc || j >= problem->jc) ? -1 : problem->space[w * problem->jc + j];
}

// Get capacity for worker
inline int getCapacity(Problem *problem, int w) {
	return (w >= problem->wc) ? -1 : problem->capacity[w];
}

// Create new problem data space
Problem *createProblem(int wc, int jc) {
	Problem *problem = (Problem *) malloc(sizeof(Problem));
	problem->wc = wc;
	problem->jc = jc;
	
	problem->price = (int *) malloc(sizeof(int) * wc * jc);
	problem->space = (int *) malloc(sizeof(int) * wc * jc);
	problem->capacity = (int *) malloc(sizeof(int) * wc);
	problem->assignments = (int *) malloc(sizeof(int) * jc);
	problem->capacityFree = (int *) malloc(sizeof(int) * wc);
	memset(problem->assignments, -1, sizeof(int) * jc); // Clear assignments

	problem->solved = 0;
	
	return problem;
}

// Deallocate
void removeProblem(Problem *problem) {
	free(problem->price);
	free(problem->space);
	free(problem->capacity);
	free(problem->assignments);
	free(problem->capacityFree);
	free(problem);
}

// Load data from file
Problem** loadData(char *file) {
	FILE *fp = fopen(file, "r");
	if(!fp) DIE("Unable to open file");
	
	int numSets = 0;
	if(fscanf(fp, "%d", &numSets) != 1 || numSets < 1) DIE("Wrong data set number");
	
	// Allocate problem list
	Problem **problems = (Problem**) malloc(sizeof(Problem *) * (numSets + 1)); // List of pointers to Problem
	problems[numSets] = 0;
	
	for(int i = 0; i < numSets; i++) {
		int wc, jc, *p;
		if(fscanf(fp, "%d %d", &wc, &jc) != 2) DIE("Wrong data: wc/jc");
		
		if(debug) printf("Loading data set %d\n", i);
		
		// Allocate space
		problems[i] = createProblem(wc, jc);
		problems[i]->index = i;
		
		// Load prices
		p = problems[i]->price;
		for(int w = 0; w < wc; w++) {
			for(int j = 0; j < jc; j++) {
				fscanf(fp, "%d", p);
				ROTATE(*p);
				p++;
			}
		}
		
		// Load spaces
		p = problems[i]->space;
		for(int w = 0; w < wc; w++) {
			for(int j = 0; j < jc; j++) {
				fscanf(fp, "%d", p);
				p++;
			}
		}
		
		// Load capacities
		p = problems[i]->capacity;
		for(int w = 0; w < wc; w++) {
			fscanf(fp, "%d", p);
			p++;
		}
	}
	
	return problems;
}

// Dump problem
void dumpProblem(Problem *problem) {
	printf("Workers: %d, jobs: %d\n", problem->wc, problem->jc);
	
	printf("Prices:\n");
	for(int w = 0; w < problem->wc; w++) {
		printf("W%3d: ", w + 1);
		for(int j = 0; j < problem->jc; j++) printf("%4d", getPrice(problem, w, j));
		printf("\n");
	}
	
	printf("Spaces:\n");
	for(int w = 0; w < problem->wc; w++) {
		printf("W%3d: ", w + 1);
		for(int j = 0; j < problem->jc; j++) printf("%4d", getSpace(problem, w, j));
		printf("\n");
	}
	
	printf("Capacities:\n");
	for(int w = 0; w < problem->wc; w++) {
		printf("W%3d: %d\n", w + 1, problem->capacity[w]);
	}
}

// Dump problem
void dumpProblem2(Problem *problem) {
	printf("%d %d\n", problem->wc, problem->jc);
	for(int w = 0; w < problem->wc; w++) {
		for(int j = 0; j < problem->jc; j++) printf("%4d", getPrice(problem, w, j));
		printf("\n");
	}
	
	for(int w = 0; w < problem->wc; w++) {
		for(int j = 0; j < problem->jc; j++) printf("%4d", getSpace(problem, w, j));
		printf("\n");
	}
	
	for(int w = 0; w < problem->wc; w++) {
		printf("%4d", problem->capacity[w]);
	}
	
	printf("\n\n");
}

// Dump result of a problem
void dumpResult(Problem *problem) {
	int w, j, p, s;
	int price = 0, space = 0; // Used price and space
	
	printf("Assignments:\n");
	for(j = 0; j < problem->jc; j++) {
		w = problem->assignments[j];
		printf("Job %3d: worker %3d (price %4d, space %3d)\n", j + 1, w + 1, p = getPrice(problem, w, j), s = getSpace(problem, w, j));
		price += p; space += s;
	}

	printf("Capacities:\n");
	for(int w = 0; w < problem->wc; w++) {
		printf("W%3d: total %4d, free %4d\n", w + 1, problem->capacity[w], problem->capacityFree[w]);
	}
	
	printf("Price: %d, used space: %d\n", price, space);
}

// Get price of solution
int getProblemPrice(Problem *problem, int *retSpace) {
	int w, j, p, s;
	int price = 0, space = 0; // Used price and space
	
	for(j = 0; j < problem->jc; j++) {
		w = problem->assignments[j];
		price += getPrice(problem, w, j); space += getSpace(problem, w, j);
	}
	
	if(retSpace) *retSpace = space;
	return price;
}

// Find next job by priority
int findNextJobByPriority(Problem *p) {
	for(int ji = 0; ji < p->jc; ji++) {
		int j = p->jobList[ji].job;
		if(p->assignments[j] == -1) return j;
	}
	
	return -1;
}

// Compare two workers
int compareWorkersByPriority(const void *a, const void *b) {
	WorkerWithProblem *A = (WorkerWithProblem*) a, *B = (WorkerWithProblem *) b;
	return (B->priority - A->priority);
}

// Compare two jobs
int compareJobsByPriority(const void *a, const void *b) {
	JobWithProblem *A = (JobWithProblem*) a, *B = (JobWithProblem *) b;
	return (B->priority - A->priority);
}


// Greedy solver
// return negative value if failed, positive if sucessful
char solveGreedy_(Problem *p, int jr) {
	if(quit) return 0;
	
	// Find what job we would solve
	int j = p->solver->findNextJob(p);
	if(j < 0 || j >= p->jc) throw "INVALID JOB ID";
	if(debug) printf("[%d] will assign job %d\n", p->jc - jr, j);
	
	// Get workers priority
	int workerList_[p->wc];
	if(p->solver->getWorkersPriority) {
		if(!p->solver->getWorkersPriority(p, j, workerList_)) {
			if(debug) printf("[%d] no workers available\n", p->jc - jr);
			return -1;
		}
	}
	
	// Randomizer
	if(p->solver->randomizeWorkers) p->solver->randomizeWorkers(p, p->wc, workerList_);
	
	// Order workers
	int wc = 0;
	WorkerWithProblem workerList[p->wc];
	for(int i = 0; i < p->wc; i++) {
		if(workerList_[i] <= 0) continue;
		
		workerList[wc].problem = p;
		workerList[wc].worker = i;
		workerList[wc].priority = workerList_[i];
		wc++;
	}
	
	// Sort workers
	qsort(workerList, wc, sizeof(WorkerWithProblem), compareWorkersByPriority);
	
	if(debug) {
		printf("[%d] workers ordered: ", p->jc - jr);
		for(int wi = 0; wi < wc; wi++) {
			int w = workerList[wi].worker; // Get worker ID
			printf("%d (%d)\t", w, workerList[wi].priority);
		}
		printf("\n");
	}
	
	// Try workers
	for(int wi = 0; wi < wc; wi++) {
		int w = workerList[wi].worker; // Get worker ID
		int s = getSpace(p, w, j); // Space required
		
		if(p->capacityFree[w] < s) continue; // Not possible -> continue with another worker
		
		// Try to assign this job
		if(debug) printf("[%d] assigning %d to %d with price %d and space %d\n", p->jc - jr, j, w, s, getPrice(p, w, j));
		p->assignments[j] = w;
		p->capacityFree[w] -= s;
		
		// Recursion
		if(jr <= 1 || solveGreedy_(p, jr - 1) > 0) return 1;
		
		// Deassign
		p->assignments[j] = -1;
		p->capacityFree[w] += s;
	}
	
	if(debug) printf("bt \n");
	return -1;
}

// Slove problem using greedy algorithm, return price
// returns 1 is OK, 0 if notfound
int solveGreedy(Problem *p) {
	// Clear assignments
	memset(p->assignments, -1, sizeof(int) * p->jc);
	memcpy(p->capacityFree, p->capacity, sizeof(int) * p->wc);
	
	// Prepare priority queue of jobs
	if(p->solver->findJobMethod == Priority) {
		int jobList[p->jc];
		if(p->solver->getJobsPriority) p->solver->getJobsPriority(p, jobList);
		
		// Randomizer
		if(p->solver->randomizeJobs) p->solver->randomizeJobs(p, p->jc, jobList);
		
		// Generate touple list
		JobWithProblem jobList2[p->jc];
		for(int i = 0; i < p->jc; i++) {
			jobList2[i].problem = p;
			jobList2[i].job = i;
			jobList2[i].priority = jobList[i];
		}
		
		// Order jobs
		qsort(jobList2, p->jc, sizeof(JobWithProblem), compareJobsByPriority);
		
		p->jobList = jobList2;
		p->solver->findNextJob = &findNextJobByPriority;
		
		return (solveGreedy_(p, p->jc) > 0) ? 1 : 0;
	}
	
	// Get next job using callback
	else {
		return (solveGreedy_(p, p->jc) > 0) ? 1 : 0;
	}
}

// Solve problem and dump result
// return nonzero if successful
char solveGreedyAndDump(Solver *s, Problem *p) {
	if(!simple) dumpProblem(p);
	
	// Assign solver
	p->solver = s;
	
	// Solve first problem
	try {
		int tstart = microtime;
		char found = solveGreedy(p);
		int tend = microtime, tduration = tend - tstart;
		if(found) {
			if(simple) {
				int space, price = getProblemPrice(p, &space);
				printf("%d\t%d\t%d\t%d\n", p->index, price, space, tduration);
			}
			else {
				printf("Solution found\n");
				dumpResult(p);
			}
		}
		else {
			if(simple) printf("-\n");
			else printf("Solution not found\n");
		}
		p->solved = 1;
		return found;
	}
	catch(char *err) {
		printf("Exception: %s\n", err);
		p->solved = 2;
		return 0;
	}
}

void *solveGreedyAndDump_(void *p_) {
	Problem *p = (Problem *) p_;
	if(!simple) printf("Solving problem %d\n", p->index);
	solveGreedyAndDump(p->solver, p);
}


// Usual main function with given solver
int main_(Solver *solver, int argc, char**argv) {
	if(argc < 2) DIE("Enter input file name");
	char *file = argv[1];
	srand(time(NULL));
	
	// Load data
	Problem **problems = loadData(file);
	Problem *p = problems[0];
	
	char *deb = getenv("DEBUG");
	char *simple_ = getenv("SIMPLE");	
	if(deb) debug = atol(deb);
	if(simple_) simple = atol(simple_);
	
	
	// Print out the source
	//dumpProblem2(p);
	
	// Print out source info
	//dumpProblem(p);
	
	// Just one problem
	if(argc == 3) {
		int pi = atol(argv[2]);
		solveGreedyAndDump(solver, problems[pi]);
	}
	
	// All problems
	else {
		int cnt = 0; // Count problems
		for(; problems[cnt] != NULL; cnt++);
		
		pthread_t threads[cnt];
		for(int i = 0; i < cnt; i++) {
			problems[i]->solver = solver;
			pthread_create(&threads[i], NULL, solveGreedyAndDump_, problems[i]);
		}
		
		// Wait for all threads
		int tlimit = time(NULL) + 600;
		while(time(NULL) < tlimit) {
			int numSolved = 0;
			for(int i = 0; i < cnt; i++) if(problems[i]->solved) numSolved++;
			
			if(numSolved == cnt) break;
			else {
				//printf("sleeping\n");
				usleep(10000);
			}
		}
		
		printf("# all solved\n");
		
		// Join threads
		quit = 1;
		for(int i = 0; i < cnt; i++) {
			pthread_join(threads[i], NULL);
		}
	}
	
	// Deallocate data sets
	for(int i = 0; problems[i] != NULL; i++) removeProblem(problems[i]);
	free(problems);
	
	return 0;
}

// Linear randomize
char randomizeLinear(struct Problem *p, int num, int items[]) {
	for(int i = 0; i < num; i++) items[i] *= (rand() % 100);
}

char randomizeTotal(struct Problem *p, int num, int items[]) {
	for(int i = 0; i < num; i++) items[i] = (rand() % 100);
}

char randomizeAdd(struct Problem *p, int num, int items[]) {
	for(int i = 0; i < num; i++) items[i] += (rand() % 100);
}
