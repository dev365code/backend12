package Day3;

import java.util.Scanner;

public class BOJ27433 {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int A = sc.nextInt();

        long tmp = 1;
        for(int i=1; i<=A; i++){
            tmp *= i;
        }
        System.out.println(tmp);
    }
}
