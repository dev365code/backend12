package CardGame;

import java.util.*;

//카드 5장을 받아 점수 계산
public class PokerRule {

//    	      •evaluate(List<Card> hand): int
//             → 5장의 카드를 받아 점수를 반환
//            •예: 원페어 = 10점, 투페어 = 20점 … 이렇게 설계 시작

    public static int evaluate(List<Card> hand) {
        // 각 카드의 랭크(rank)를 세기 위한 맵 생성 (예: "A", "K", "5" 등)
        Map<String, Integer> rankCount = new HashMap<>();

        // hand에 있는 5장의 카드에서 랭크별 개수를 맵에 저장
        for (Card card : hand) {
            String rank = card.getRank();
            rankCount.put(rank, rankCount.getOrDefault(rank, 0) + 1);
        }

        // 페어, 트리플, 포카드 여부를 저장할 변수 선언
        int pairs = 0;
        boolean threeOfKind = false;
        boolean fourOfKind = false;

        // 맵에 저장된 랭크별 개수를 기반으로 페어, 트리플, 포카드 판별
        for (int count : rankCount.values()) {
            if (count == 2) pairs++;             // 같은 랭크가 2개면 페어
            else if (count == 3) threeOfKind = true; // 같은 랭크가 3개면 트리플
            else if (count == 4) fourOfKind = true;  // 같은 랭크가 4개면 포카드
        }

        // 점수 반환: 높은 조합일수록 점수도 높게 반환
        if (fourOfKind) return 70;               // 포카드
        if (threeOfKind && pairs == 1) return 60; // 풀하우스
        if (threeOfKind) return 50;              // 트리플
        if (pairs == 2) return 40;               // 투페어
        if (pairs == 1) return 30;               // 원페어

        return 10; // 아무 조합도 없는 하이카드
    }
}
