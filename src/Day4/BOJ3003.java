package Day4;

import java.util.Scanner;

public class BOJ3003 {
    public static void main(String[] args) {
        int[] black = {1,1,2,2,2,8};
        Scanner sc = new Scanner(System.in);

        for(int i=0; i<black.length;i++) {
            System.out.print(black[i] - sc.nextInt() + " ");
        }
    }
}