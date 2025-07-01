package CardGame;

import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

//딜러역할 카드를 나눠주고, 평가 호출, 결과 정리
public class DeckTest {
    public static void main(String[] args) {
        List<Player> players = new ArrayList<>();               // 플레이어 리스트
        Scanner sc = new Scanner(System.in);                    // 플레이어 이름 입력을 위한 스캐너 생성
        for (int i = 1; i <= 4; i++) {                          // 플레이어 생성 이름 입력
            String name;
            while (true) {
                System.out.println("플레이어 " + i + " 의 닉네임을 입력하세요 : ");
                name = sc.nextLine();
                if (name.length() <= 20) { break; }
                System.out.println(" 닉네임은 20자 이하여야 합니다.");
            }
            players.add(new Player(name));
        }

        int totalGames = 100;

        //게임 시작
        for (int game = 1; game <= totalGames; game++) {
//            System.out.println("==== " + game + "번째 게임 ====");
            Deck d = new Deck();
            d.shuffle();
            int cardOwn = 0;
            for (Player p : players) {                          // 각플레이어에게 5장씩 순서대로 카드를 나누어줌
                List<Card> hand = new ArrayList<>();
                for (int i = 0; i < 5; i++) {
                    hand.add(d.pick(cardOwn++));                // 카드 소유카운트가 올라가면서 20장까지 중복없이 나누어줌
                }
                p.setHand(hand);
            }

            //플레이어가 가진 카드를 점수로 환산
            for (Player p : players) {
                int score = PokerRule.evaluate(p.getHand());
                p.setScore(score);
//                System.out.println(p.getNickname() + "의 점수: " + score);
            }

            //플레이어중 가장 높은 점수를 받은애 계산
            int maxScore = -1;
            Player winner = null;
            for (Player p : players) {
                if (p.getScore() > maxScore) {
                    maxScore = p.getScore();
                    winner = p;
                }
            }

            if (winner != null) {
                for (Player p : players) {
                    if (p == winner) {
                        p.addWin();
                        p.addMoney(100);
//                        System.out.println("이번 게임의 승자: " + p.getNickname() + " (점수: " + p.getScore() + ")");
                    } else {
                        p.addLose();
                    }
                }
            }
        }

        System.out.println("===== 최종 결과 =====");
        for (Player p : players) {
            System.out.println(p.getNickname() + " | 총 승: " + p.getWin() + " | 총 패: " + p.getLose() + " | 최종 보유금: " + p.getMoney());
        }
    }
}
