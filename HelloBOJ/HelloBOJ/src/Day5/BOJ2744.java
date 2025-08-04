package Day5;

import java.util.Scanner;

public class BOJ2744 {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        char[] ch = sc.nextLine().toCharArray();

        for(int i = 0; i < ch.length; i++){
            int tmp = ch[i];
            if( 65 <= tmp && tmp <= 96){
                System.out.print((char)(tmp+32));
            } else {
                System.out.print((char)(tmp-32));
            }
        }
    }
}

//대문자면 +32 / 소문자면 -32

//Scanner sc = new Scanner(System.in);
//String str = sc.nextLine();
//char tmp = 0;
//// A=65 대문자에서 32를 더하면 소문자가 된다.
//// a=97 소문자에서 32를 빼면 대문자가 되고
//        for(int i=0; i<str.length();i++){
//char ch = str.charAt(i);
//            if (ch >= 'A' && ch <= 'Z') {
//tmp = (char)(ch + 32);
//        } else if (ch >= 'a' && ch <= 'z') {
//tmp = (char)(ch - 32);
//        }
//        System.out.print(tmp);
//        }