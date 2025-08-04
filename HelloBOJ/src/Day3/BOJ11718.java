package Day3;

import java.util.Scanner;

public class BOJ11718 {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        while(sc.hasNext()) {
            String text = sc.nextLine().trim();
            if(text.length() > 100) {
                System.out.println("다시 입력하세요");
            } else {
                System.out.println(text);
            }
        }
    }
}
