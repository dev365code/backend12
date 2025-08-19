package Day6;

import java.util.Scanner;

public class EuclideanAlgorithm {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();  // 첫 번째 수
        int m = sc.nextInt();  // 두 번째 수
        
        // 유클리드 호제법으로 최대공약수 구하기
        int gcd = getGCD(n, m);
        int lcm = getLCM(n, m, gcd);  // 최소공배수도 함께 구하기
        
        System.out.println("최대공약수: " + gcd);
        System.out.println("최소공배수: " + lcm);
    }
    
    // 유클리드 호제법으로 최대공약수 구하는 메소드
    public static int getGCD(int a, int b) {
        // GCD(a, b) = GCD(b, a % b)
        // b가 0이 될 때까지 반복
        while(b != 0) {
            int temp = b;      // b를 임시 저장
            b = a % b;         // 나머지를 새로운 b로
            a = temp;          // 기존 b를 새로운 a로
        }
        return a;  // b가 0이 되면 a가 최대공약수
    }
    
    // 최소공배수 구하는 메소드 (공식: a × b ÷ 최대공약수)
    public static int getLCM(int a, int b, int gcd) {
        return a * b / gcd;
    }
}
