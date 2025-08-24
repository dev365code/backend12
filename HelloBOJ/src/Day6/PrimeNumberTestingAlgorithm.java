package Day6;

import java.util.Scanner;

/**
 * 소수 판별 알고리즘 (Prime Number Testing Algorithm)
 * 시간복잡도: O(√n) - 효율적인 소수 판별
 * 공간복잡도: O(1)
 */
public class PrimeNumberTestingAlgorithm {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();  // 소수인지 확인할 숫자 입력받기

        // 소수 판별 결과에 따라 출력
        if (isPrime(n)) {
            System.out.printf("%d is a prime number", n);
        } else {
            System.out.printf("%d is not a prime number", n);
        }
    }

    /**
     * 소수 판별 메소드
     * @param n 판별할 숫자
     * @return 소수면 true, 아니면 false
     */
    public static boolean isPrime(int n) {
        // 1. 2보다 작은 수는 소수가 아님 (0, 1은 소수 아님, 음수도 소수 아님)
        if(n < 2) return false;

        // 2. 2부터 √n까지만 확인하면 충분
        // 이유: 약수는 항상 쌍으로 존재하므로 √n까지만 확인해도 모든 약수를 찾을 수 있음
        for(int i = 2; i * i <= n; i++) {
            // 3. 나누어떨어지면 약수 존재 → 소수 아님
            if(n % i == 0) {
                return false;  // 약수를 찾는 즉시 false 리턴 (조기 종료로 효율성 증대)
            }
        }
        // 4. 모든 검사를 통과하면 소수
        return true;
    }
}
