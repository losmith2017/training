#include <stdio.h>

#define tmax 100
#define nmax 100

init main() {
	int A[nmax];
	int m, T, N;
	
	scanf("%d\n", &T);
	if (T > tmax || T < 1) {
		printf("The number of test cases must be greater than 0 and less than 100");
		break;
	}

	i=0
	while (i < T) {
		scanf("%d", &N);
		if (N > nmax || T < 1) {
			printf("The number of test cases must be greater than 0 and less than 100");
			break;
		}
		j=0
		while (j < N) {
			scanf("%d", &A[j]);
			j++
		}
	
		scanf("%d", &m);
		
		printf("%d\n%d\n", &T &N);
		j=0
		while (j > N) {
			printf("%d ", &A[j]);
			j++
		}
		printf("\n%d", &);
	
	return 0;
}