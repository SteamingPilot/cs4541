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
#define STATUS_READY 3

typedef struct queue_item{
    int philosoper_id;
    int fork_id;
    struct queue_item *next;
} QueueItem;

typedef struct queue{
    QueueItem *head;
    QueueItem *tail;
    int size;
} Queue;

void enque(Queue *queue, int philosopher_id, int fork_id){
    QueueItem *item = (QueueItem *)malloc(sizeof(QueueItem));
    item->philosoper_id = philosopher_id;
    item->fork_id = fork_id;
    item->next = NULL;

    if (queue->size == 0){
        queue->head = item;
        queue->tail = item;
    }else{
        queue->tail->next = item;
        queue->tail = item;
    }
    queue->size++;
}

void add_to_front(Queue *queue, int philosopher_id, int fork_id){
    QueueItem *item = (QueueItem *)malloc(sizeof(QueueItem));
    item->philosoper_id = philosopher_id;
    item->fork_id = fork_id;
    item->next = NULL;

    if (queue->size == 0){
        queue->head = item;
        queue->tail = item;
    }else{
        item->next = queue->head;
        queue->head = item;
    }
    queue->size++;
}

QueueItem * deque(Queue *queue){
    if (queue->size == 0){
        return NULL;
    }
    QueueItem *item = queue->head;
    queue->head = queue->head->next;
    queue->size--;

    return item;
}


int get_front(Queue *queue){
    if (queue->size == 0){
        return -1;
    }
    return queue->head->philosoper_id;
}


void free_queue(Queue *queue){
    while(queue->size != 0){
        QueueItem *item = deque(queue);
        free(item);
    }
    free(queue);
}



typedef struct stack_item{
    int philosoper_id;
    int fork_id;
    struct stack_item *next;
} StackItem;

typedef struct stack{
    StackItem *head;
    StackItem *tail;
    int size;
} Stack;

void push(Stack *stack, int philosopher_id, int fork_id){
    StackItem *item = (StackItem *)malloc(sizeof(StackItem));
    item->philosoper_id = philosopher_id;
    item->fork_id = fork_id;
    item->next = NULL;

    if (stack->size == 0){
        stack->head = item;
        stack->tail = item;
    }else{
        item->next = stack->head;
        stack->head = item;
    }
    stack->size++;
}

StackItem * pop(Stack *stack){
    if (stack->size == 0){
        return NULL;
    }
    StackItem *item = stack->head;
    stack->head = stack->head->next;
    stack->size--;
    return item;
}


void freeStack(Stack *stack){
    while(stack->size != 0){
        StackItem *item = pop(stack);
        free(item);
    }
    free(stack);
}

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
    philosopher->current_time = rand() % philosopher->max_time + 1;
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

    // Setup Queue
    Queue *queue = (Queue *)malloc(sizeof(Queue));
    queue->head = NULL;
    queue->tail = NULL;
    queue->size = 0;

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
                    # pragma omp critical
                    picked_up = pickup_forks(philosopher.id, &forks[philosopher.id], &philosopher, (int) current_time - initial_time);

                    if (picked_up == 0)
                    {
                        // We couldn't pick up the fork, so we need to wait
                        philosopher.status = STATUS_WAITING;
                        enque(queue, philosopher.id, forks[philosopher.id].id);

                        while (philosopher.status != STATUS_READY)
                        {
                            sleep(1);
                            current_time++;
                        }
                        pickup_forks(philosopher.id, &forks[philosopher.id], &philosopher, (int) current_time - initial_time);         

                    } 
                
                    printf("%d Philosopher %d picked up fork %d\n",(int) (current_time - initial_time), philosopher.id, forks[philosopher.id].id);
                        
                    
                    // Delay for 1 second before picking up the right fork, because we need to pickup the forks one at a time
                    sleep(1);
                    current_time++;

                    // Pick up right fork
                    picked_up = 0;
                    #pragma omp critical
                    picked_up = pickup_forks(philosopher.id, &forks[(philosopher.id + 1) % number_of_philosophers], &philosopher, (int) (current_time - initial_time));
                    if (picked_up == 0)
                    {
                        // We couldn't pick up the fork, so we need to wait
                        enque(queue, philosopher.id, forks[(philosopher.id + 1) % number_of_philosophers].id);
                        philosopher.status = STATUS_WAITING;
                        while (philosopher.status != STATUS_READY)
                        {
                            sleep(1);
                            current_time++;
                        }
                        pickup_forks(philosopher.id, &forks[(philosopher.id + 1) % number_of_philosophers], &philosopher, (int) (current_time - initial_time));

                    printf("%d Philosopher %d picked up fork %d\n", (int) (current_time - initial_time), philosopher.id, forks[(philosopher.id + 1) % number_of_philosophers].id);

                    philosopher.status = STATUS_EATING;

                    // Generate a random time for eating
                    int eating_time = rand() % philosopher.max_time + 1;
                    int time_elapsed = current_time - initial_time;

                    printf("%d Philosopher %d is eating for %d seconds\n",time_elapsed, philosopher.id, eating_time);
                    philosopher.current_time = eating_time;
                    sleep(eating_time);
                    current_time += eating_time;

                    // Put down the forks after eating
                    putdown_forks(philosopher.id, &forks[philosopher.id], &philosopher, (int) (current_time - initial_time));
                    
                    // Send Ready signal to whoever is waiting for this fork
                    Stack *stack = (Stack *)malloc(sizeof(Stack));
                    if (queue->size != 0)
                    {
                        QueueItem *head_queue_item;
                        #pragma omp critical
                        head_queue_item = deque(queue);
                        while (head_queue_item->fork_id != forks[philosopher.id].id)
                        {
                            push(stack, head_queue_item->philosoper_id, head_queue_item->fork_id); 

                            free(head_queue_item);
                            #pragma omp critical
                            head_queue_item = deque(queue);
                        }

                        #pragma omp critical
                        philosophers[head_queue_item->philosoper_id].status = STATUS_READY;
                        free(head_queue_item);
                        while(stack->size != 0){
                            StackItem *item = pop(stack);
                            
                            #pragma omp critical
                            enque(queue, item->philosoper_id, item->fork_id);
                            free(item);
                        }
                    }

                    // Put down the left fork after eating
                    putdown_forks(philosopher.id, &forks[philosopher.id], &philosopher, (int) (current_time - initial_time));
                    
                    // Send Ready signal to whoever is waiting for this fork
                    if (queue->size != 0)
                    {
                        QueueItem *head_queue_item;
                        #pragma omp critical
                        head_queue_item = deque(queue);
                        while (head_queue_item->fork_id != forks[philosopher.id].id)
                        {
                            push(stack, head_queue_item->philosoper_id, head_queue_item->fork_id); 

                            free(head_queue_item);
                            #pragma omp critical
                            head_queue_item = deque(queue);
                        }

                        #pragma omp critical
                        philosophers[head_queue_item->philosoper_id].status = STATUS_READY;
                        free(head_queue_item);
                        while(stack->size != 0){
                            StackItem *item = pop(stack);
                            
                            #pragma omp critical
                            enque(queue, item->philosoper_id, item->fork_id);
                            free(item);
                        }
                    }

                    // Put down the right fork after eating
                    putdown_forks(philosopher.id, &forks[(philosopher.id + 1) % number_of_philosophers], &philosopher, (int) (current_time - initial_time));

                    // Send Ready signal to whoever is waiting for this fork
                    if (queue->size != 0)
                    {
                        QueueItem *head_queue_item;
                        #pragma omp critical
                        head_queue_item = deque(queue);
                        while (head_queue_item->fork_id != forks[(philosopher.id + 1) % number_of_philosophers].id)
                        {
                            push(stack, head_queue_item->philosoper_id, head_queue_item->fork_id); 

                            free(head_queue_item);
                            #pragma omp critical
                            head_queue_item = deque(queue);
                        }

                        philosophers[head_queue_item->philosoper_id].status = STATUS_READY;
                        free(head_queue_item);
                        while(stack->size != 0){
                            StackItem *item = pop(stack);
                            
                            #pragma omp critical
                            enque(queue, item->philosoper_id, item->fork_id);
                            free(item);
                        }
                    }

                    // Free the stack
                    freeStack(stack);

                    // Decrement the number of meals
                    #pragma omp critical
                    number_of_meals--;

                    // Think again with a new generated thinking time
                    philosopher.status = STATUS_THINKING;
                    philosopher.current_time = rand() % philosopher.max_time + 1;


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
            
            }
        }
    }





    return 0;
}
















