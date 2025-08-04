package CardGame;
import java.util.ArrayList;
import java.util.List;

public class Player {

    String nickname;
    public Player(String nickname) {
        this.nickname = nickname;
    }

    int money = 10000;
    int winCount, loseCount;

    //받은 카드 리스트
    List<Card> hand = new ArrayList<>();
    void receiveCards(List<Card> cards) {
        hand.clear();      // 이전 게임 카드 제거
        hand.addAll(cards);
    }

    //카드 초기화
    void resetHand() {
        hand.clear();
    }

    //승패 기록
    void addWin() {
        winCount++;
        money += 100; // 상금 룰에 따라 증가
    }
    void addLose() {
        loseCount++;
    }

    void setHand(List<Card> hand) {
        this.hand = new ArrayList<>(hand);      // 카드를 받아서 담는 객체
    }

//    //카드 출력
//    void showHand() {
//        System.out.println(nickname + "의 카드:");
//        for (Card card : hand) {
//            System.out.println(card);
//        }
//    }


//	•	List<Card> hand
//	•	resetHand()
//	•	addWin(), addLose()

    // 현재 손에 든 카드 반환
    public List<Card> getHand() {
        return new ArrayList<>(hand); // 외부에서 수정 못하게 복사본 반환
    }

    // 승리 횟수 반환
    public int getWin() {
        return winCount;
    }

    // 패배 횟수 반환
    public int getLose() {
        return loseCount;
    }

    // 플레이어의 현재 머니 반환
    public int getMoney() {
        return money;
    }

    // 플레이어의 이름 반환
    public String getNickname() {
        return nickname;
    }

    // 점수 저장용 (게임 중 계산 결과 저장용)
    private int score;

    // 점수 설정
    public void setScore(int score) {
        this.score = score;
    }

    // 점수 조회
    public int getScore() {
        return score;
    }
    public void addMoney(int amount) {
        this.money += amount;
    }
}
