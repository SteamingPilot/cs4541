#include<stdio.h>

int main(){

    int A[3][5] = {
        {1, 2, 3, 4, 5},
        {1, 2, 3, 4, 5},
        {1, 10, 3, 4, 5}};


    int x = A[2][1] + 15;

    return x;
}