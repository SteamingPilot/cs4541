#include<stdio.h>

int main(){


	// Problem 1
	float p1 = 2.5;

	printf("Problem 1: %.10f\n", p1);

	// Problem 2
	float p2 = -1.0/10.0;
	printf("Problem 2: %.10f\n", p2);
	

	// Problem 3
	double p3 = 1/3;
	printf("Problem 3a: %lf\n", p3);
	
	p3 = 1.0/3.0;
	printf("Problem 3b: %lf\n", p3);

	// Problem 4
	double p4 = 9999999.3399999999;
	printf("Problem 4a: %lf\n", p4);
	printf("Problem 4b: %f\n", (float) p4);
	

	// Problem 5
	int p5 = 30000 * 30000;
	printf("Problem 5a: %d\n", p5);

	p5 = 40000*40000;
	printf("Problem 5b: %d\n", p5);

	p5 = 50000*50000;
	printf("Problem 5c: %d\n", p5);

	p5 = 60000*60000;
	printf("Problem 5d: %d\n", p5);

	p5 = 70000*70000;
	printf("Problem 5e: %d\n", p5);



	// Problem 6
	float p6 = 1e20;
	printf("Problem 6a: %f\n", p6);

	p6 = 1e20 + 3500000000;
	printf("Problem 6b: %f\n", p6);

	p6 = 1e20 + (3500000000 * 1000000000);
	printf("Problem 6c: %f\n", p6);

	p6 = 1e20;

	for (int i = 0; i < 1000000000 ; i++)
	{
		p6 = p6 + 3500000000;
	}

	printf("Problem 6d: %f\n", p6);

	






















	return 0;
}

