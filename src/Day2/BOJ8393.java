package Day2;

import java.util.Scanner;

public class BOJ8393 {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        int tmp = 0;
        for(int i = n; i >= 1; i--) {
            tmp += i;
        }
        System.out.println(tmp);
    }
}
