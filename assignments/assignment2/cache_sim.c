#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "queue.h"

#define BASE_10 10
#define BASE_16 16


typedef struct tracker{
    int empty_lines;
    Queue *queue;

} Tracker;

typedef struct{
    int valid;
    int tag;
    // int data[4];
} CacheLine;



void print_error(char *err_text){

    if (strlen(err_text) != 0){
        printf("%s\n", err_text);
    }
        printf("Usage: ./cache_sim [-hv] -s <s> -E <E> -b <b> -t <tracefile>\n");

        printf("-h: Optional help flag that prints usage info\n");
        printf("-v: Optional verbose flag that displays trace info\n");
        printf("-s <s>: Number of set index bits (S = 2 s is the number of sets)\n");
        printf("-E <E>: Associativity (number of lines per set)\n");
        printf("-b <b>: Number of block bits (B = 2 b is the block size)\n");
        printf("-t <tracefile>: Name of the valgrind trace to replay\n");
}

// void print_verbose(char *line, char *status, int is_verbose){
//     if(is_verbose) {
//         line[strlen(line)-1] = '\0';
//         line++;
//         printf("%s %s\n", line, status);
//     }
// }

void print_verbose(char *instruction, long address, char * size, char *status, int is_verbose){
    if(is_verbose) {
        size[strlen(size)-1] = ' ';
        printf("%s %lx,%s%s\n", instruction, address, size, status);
    }
}


void freeCache(CacheLine **cache, int S){
    for (int i = 0; i < S; i++)
    {
        free(cache[i]);
    }
    free(cache);
}

void freeQueue(Queue *queue){
    while (queue->len != 0)
    {
        dequeue(queue);
    }
    free(queue);
}

void freeTrackers(Tracker *trackers, int S){
    for (int i = 0; i < S; i++)
    {
        freeQueue(trackers[i].queue);
    }
    free(trackers);
}




int main(int argc, char **argv){

    if((argc>11) || (argc<2)){
        print_error("");
        return -1;
    }

    long s, E, b, S, hits=0, misses=0, evictions=0;
    int is_verbose=0;

    char *  filename;

    // Looping through the argument list
    for(int i=1; i<argc; i++){
        char *arg = argv[i];
        char *check_string, *value;

        if(!strcmp(arg, "-h") || !strcmp(arg, "-v") || !strcmp(arg, "-E")
        || !strcmp(arg, "-s") || !strcmp(arg, "b") || !strcmp(arg, "-t")){
            // If we end with a valid option, but no option value, it would be an error.
            if((i+1)==argc){
                print_error("");
                return -1;
            }
        }

        if(!strcmp(arg, "-h") || (!strcmp(arg, "-hv"))){
            // If we encounter a "-h" then, we print the usage, and ignore everything
            print_error("");
            return 0;

        } else if(!strcmp(arg, "-v")){
            // Setting verbose bit
            is_verbose = 1;
        } else if(!strcmp(arg, "-s")){
            // Setting value of s
            value = argv[i+1];
            s = strtol(value, &check_string, BASE_10);
            if(*check_string != '\0'){
                print_error("Invalid value of s");
                return -1;
            } else i++;
        } else if(!strcmp(arg, "-E")){
            // We got an E option
            value = argv[i+1];
            E = strtol(value, &check_string, BASE_10);
            if(*check_string != '\0'){
                print_error("Invalid value of E");
                return -1;
            } else i++;
        } else if(!strcmp(arg, "-b")){
            // We got the 'b' value
            value = argv[i+1];
            b = strtol(value, &check_string, BASE_10);
            if(*check_string != '\0'){
                print_error("Invalid value of b");
                return -1;
            } else i++;
        } else if(!strcmp(arg, "-t")){
            // We got the trace file
            filename = argv[i+1];
            i++;
        } else {
            // We can see an option we dont know
            print_error("");
            return -1;
        }
    }


    FILE *filep;
    filep = fopen(filename, "r");

    if(filep == NULL){
        print_error("Bad File Name");
        return -1;
    }



    S = 1 << s;

    // Making the Cache: which is a set of S cache lines
    CacheLine **cache = (CacheLine **)malloc(sizeof(CacheLine *) * S);
    
    for (int i = 0; i < S; i++)
    {
        // For Each Set, we will add E cache lines to each set.
        cache[i] = (CacheLine *)malloc(sizeof(CacheLine) * E);
        for (int j = 0; j < E; j++)
        {
            // Iitialize each cache line values
            cache[i][j].valid = 0;
            cache[i][j].tag = -1;
            // for (int k = 0; k < 4; k++)
            // {
            //     cache[i][j].data[k] = 0;
            // }
        }
    }


    // Making the tracker array which is the set of S trackers.
    Tracker *trackers = (Tracker *)malloc(sizeof(Tracker) * S);
    for (int i = 0; i < S; i++)
    {
        // Initialize each tracker values
        trackers[i].empty_lines = E;
        trackers[i].queue = newQueue();
    }


    // Parsing the trace file
    char *line = NULL;
    size_t len;
    size_t read;
    while((read=getline(&line, &len, filep)) != -1){
        

        // Getting Segmentation fault here
        
        // printf("%c\n", line[0]);
        if (line[0] == 'I'){
            // Ignore this instruction
            continue;
        } else if(line[0] == '\n'){
            continue;
        } else{
            //char line_cpy[strlen(line)];
            // char *x = strcpy(line_cpy, line);

            char *instruction = strtok(line, " ");
            char *address = strtok(NULL, ",");
            char *size = strtok(NULL, ",");

            // Get the Tag and Set bits from the address
            long int address_int = strtol(address, NULL, BASE_16);
            long int tag = address_int >> (s+b);
            long int set = (address_int >> b) & ((1 << s) - 1);

            if(!strcmp(instruction, "L") || !strcmp(instruction, "S") || !strcmp(instruction, "M")){
                int tag_match = 0;
                for (size_t i = 0; i < E; i++)
                {
                    if(cache[set][i].tag == tag){
                        // We have a tag match
                        tag_match = 1;


                        if(cache[set][i].valid == 1){
                            // We have a valid hit
                            hits++;

                            if (!strcmp(instruction, "M"))
                            {
                                hits++;
                                print_verbose(instruction, address_int, size, "hit hit", is_verbose);
                            } else {
                                print_verbose(instruction, address_int, size, "hit", is_verbose);
                            }
                            break;
                        } else {
                            // Miss
                            misses++;
                            if (!strcmp(instruction, "M"))
                            {
                                hits++;
                                print_verbose(instruction, address_int, size, "miss hit", is_verbose);
                            } else {
                                print_verbose(instruction, address_int, size, "miss", is_verbose);
                            }
                            break;
                        }
                    }
                }

                if(!tag_match){
                        // Tag didn't match, so it's a miss

                        // Check if there is an empty line
                        if(trackers[set].empty_lines != 0){
                            // Empy line present
                            int next_line = E - trackers[set].empty_lines;
                            cache[set][next_line].valid = 1;
                            cache[set][next_line].tag = tag;
                            
                            // Decrease Empty line, and add the current line to the queue
                            // so that we can evict it later
                            trackers[set].empty_lines--;
                            enqueue(trackers[set].queue, next_line);

                            misses++;

                            if (!strcmp(instruction, "M"))
                            {
                                hits++;
                                print_verbose(instruction, address_int, size, "miss hit", is_verbose);
                            } else {
                                print_verbose(instruction, address_int, size, "miss", is_verbose);
                            }

                        } else {
                            // No empty line
                            // We need to evict in a FIFO manner
                            
                            // Get the evict line from the front of the queue, and dequeue
                            int evict_line = trackers[set].queue->front->val;
                            dequeue(trackers[set].queue);
                            cache[set][evict_line].tag = tag;
                            cache[set][evict_line].valid = 1;

                            // Add the current line to the end of the queue
                            enqueue(trackers[set].queue, evict_line);

                            misses++;
                            evictions++;

                            if (!strcmp(instruction, "M"))
                            {
                                hits++;
                                print_verbose(instruction, address_int, size, "miss eviction hit", is_verbose);
                            } else {
                                print_verbose(instruction, address_int, size, "miss eviction", is_verbose);
                            }

                        }

                    } 
            }
        }

    }

    printf("hits:%ld misses:%ld evictions:%ld\n", hits, misses, evictions);


    freeCache(cache, S);
    freeTrackers(trackers, S);
    return 0;
}