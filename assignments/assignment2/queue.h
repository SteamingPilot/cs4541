#include <stdio.h>
#include <stdlib.h>

typedef struct Queueitem{
	int val;
	struct Queueitem *next;

}QueueItem;


typedef struct{
	int empty_index, len;
    QueueItem *front, *rear;
} Queue;


int isEmpty(Queue *queue){
	if(queue->len == 0){
		return 1;
	} else {
		return 0;

	}
}

void enqueue(Queue *queue, int val){
    if (queue->len == 0)    
    {
        queue->front = (QueueItem *)malloc(sizeof(QueueItem));
        queue->front->val = val;
        queue->front->next = NULL;
        queue->rear = queue->front;
        queue->len++;
    }
    else
    {
        queue->rear->next = (QueueItem *)malloc(sizeof(QueueItem));
        queue->rear->next->val = val;
        queue->rear->next->next = NULL;
        queue->rear = queue->rear->next;
        queue->len++;
    }
}

void dequeue(Queue *queue){
    if (!(queue->len == 0))
    {
        QueueItem *temp = queue->front;
        queue->front = queue->front->next;
        free(temp);
        queue->len--;   
    }
}

Queue * newQueue(){
    Queue *queue = (Queue *)malloc(sizeof(Queue));
    queue->len = 0;
    queue->front = NULL;
    queue->rear = NULL;

    return queue;
}

void printQueue(Queue *queue){
    QueueItem *temp = queue->front;
    while (temp != NULL)
    {
        printf("%d ", temp->val);
        temp = temp->next;
    }
    printf("\n");
}

