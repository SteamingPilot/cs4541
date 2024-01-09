/* 
    Bonus Assignment 1
    The Diningin Philosophers Problem
    Author: Md Abiruzzaman Palok
    Date: 12/14/2023

*/



#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <time.h>
#include <unistd.h>

#define STATUS_THINKING 0
#define STATUS_EATING 1
#define STATUS_WAITING 2


// The Diningin Philosophers Problem Simulation

struct Philosopher{
    int id;
    int status;
    int max_time;
    // int *blocktime;
    // int *blockstarting;
    int current_time;
};

struct Fork{
    int id;
    int is_available;
};


int init_philosopher(struct Philosopher *philosopher, int id, int max_time, time_t initial_time){ 
    philosopher->id = id;
    philosopher->status = STATUS_THINKING;
    philosopher->max_time = max_time;

    // Hand coding the thinking time to simulate blocking
    philosopher->current_time = 1;
    int current_time = time(NULL);
    int time_elapsed = current_time - initial_time;
    printf("%d Philosopher %d is thinking for %d seconds\n", time_elapsed, philosopher->id, philosopher->current_time);
    return 1;
}

int pickup_forks(int philosopher_id, struct Fork *fork, struct Philosopher *philosopher, int time){
    if (fork->is_available == 1){
        fork->is_available = 0;
        // printf("Philosopher %d picked up fork %d\n", philosopher_id, fork->id);
        return 1;
    }
    else{
        printf("%d Philosopher %d is waiting for fork %d\n", time, philosopher_id, fork->id);
        // philosopher->status = STATUS_WAITING;
        return 0;
    }
}

int putdown_forks(int philosopher_id, struct Fork *fork, struct Philosopher *philosopher, time_t initial_time){
    fork->is_available = 1;
    time_t current_time = time(NULL);
    int time_elapsed = current_time - initial_time;
    printf("%d Philosopher %d put down fork %d\n", time_elapsed, philosopher_id, fork->id);

    return 1;
}


int main(int argc, char **argv){

    if(argc != 3){
        printf("Usage: ./main <number_of_philosophers> <max_time>\n");
        return 0;
    }

    int number_of_philosophers = atoi(argv[1]);
    int max_time = atoi(argv[2]);

    struct Philosopher *philosophers = (struct Philosopher *)malloc(sizeof(struct Philosopher) * number_of_philosophers);
    struct Fork *forks = (struct Fork *)malloc(sizeof(struct Fork) * number_of_philosophers);

    #pragma omp parallel for
    for(int i = 0; i < number_of_philosophers; i++){
        forks[i].id = i;
        forks[i].is_available = 1;

        init_philosopher(&philosophers[i], i, max_time, time(NULL));

    }

    int number_of_meals = 5;
    time_t initial_time = time(NULL);
    int my_rank, picked_up;


    # pragma omp parallel num_threads(number_of_philosophers)
    {
        time_t current_time;
        my_rank = omp_get_thread_num();
        struct Philosopher philosopher  = philosophers[my_rank];
        while(number_of_meals != 0){
            current_time = time(NULL);
            if (philosopher.status == STATUS_THINKING)
            {
                if(philosopher.current_time == 0){
                    // Pick up left fork
                    picked_up = 0;
                    while(picked_up != 1){
                        # pragma omp critical
                        picked_up = pickup_forks(philosopher.id, &forks[philosopher.id], &philosopher, (int) current_time - initial_time);

                        if (picked_up == 0)
                        {
                            // Try again to pick up the left fork after 1 second
                            sleep(1);
                            current_time++;
                        } else {
                            printf("%d Philosopher %d picked up fork %d\n",(int) (current_time - initial_time), philosopher.id, forks[philosopher.id].id);
                        }
                        
                    }

                    
                    // Delay for 1 second before picking up the right fork, because we need to pickup the forks one at a time
                    sleep(1);
                    current_time++;

                    // Pick up right fork
                    picked_up = 0;
                    while (picked_up != 1){
                        #pragma omp critical
                        picked_up = pickup_forks(philosopher.id, &forks[(philosopher.id + 1) % number_of_philosophers], &philosopher, (int) (current_time - initial_time));
                        if (picked_up == 0)
                        {
                            // Try again to pick up the left fork after 1 second
                            sleep(1);
                            current_time++;
                        } else{
                            printf("%d Philosopher %d picked up fork %d\n", (int) (current_time - initial_time), philosopher.id, forks[(philosopher.id + 1) % number_of_philosophers].id);
                        }
                    }

                    philosopher.status = STATUS_EATING;

                    // Generate a random time for eating
                    int eating_time = rand() % philosopher.max_time + 1;
                    int time_elapsed = current_time - initial_time;

                    printf("%d Philosopher %d is eating for %d seconds\n",time_elapsed, philosopher.id, eating_time);
                    philosopher.current_time = eating_time;
                    sleep(eating_time);
                }else{
                    // I should think
                    sleep(philosopher.current_time);
                    philosopher.current_time = 0;
                }
            }
            else if (philosopher.status == STATUS_EATING)
            {

            }
            else if (philosopher.status == STATUS_WAITING)
            {
                /* code */
            }
            
        };
    }





    return 0;
}
















