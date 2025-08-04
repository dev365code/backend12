package Day4;

import java.util.Arrays;
import java.util.Scanner;

public class BOJ10807 {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int[] num = new int[N];

        for(int i=0; i<N; i++){
            num[i] = sc.nextInt();
        }

        int v = sc.nextInt();
        int count = 0;
        for(int i=0; i<N; i++){
            if(num[i] == v){
                count++;
            }
        }
        System.out.println(count);
    }
}
