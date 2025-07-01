package Day5;

import java.text.SimpleDateFormat;
import java.util.Date;

public class BOJ10699 {
    public static void main(String[] args) {
        Date date = new Date();
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
        System.out.println(date);
        System.out.println(sdf.format(date));
    }
}
