package Day1;

import java.util.Scanner;

public class BOJ2739 {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();

        for(int i = 1; i <= 9; i++) {
            System.out.printf("%d * %d = " + (N * i), N, i);
            System.out.println();
        }
    }
}
