package toyproject.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import toyproject.controller.dto.*;
import toyproject.mapper.CartMapper;
import toyproject.mapper.queryparam.*;
import toyproject.mapper.result.SizeStockResult;
import toyproject.mapper.result.StockCheckResult;
import toyproject.mapper.result.UserCartResult;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@Slf4j
@RequiredArgsConstructor
public class CartService {
    private final CartMapper cartMapper;

    public CartResponseDto searchCart(CartRequestDto requestDto) {

        log.info("CartService_searchCart 진입");

        UserCartByIDQueryParam userCartByIDQueryParam = UserCartByIDQueryParam.builder()
                .userId(requestDto.getUserId())
                .build();

        List<UserCartResult> userUserCartResultList = cartMapper.findCartItemsByUserId(userCartByIDQueryParam);

        List<CartInfoDto> userCartInfoList = userUserCartResultList.stream().map(userCartResult -> CartInfoDto
                .builder().productId(userCartResult.getProductId())
                .productImg(userCartResult.getProductImg())
                .productName(userCartResult.getProductName())
                .size(userCartResult.getSize())
                .cartProductQuantity(userCartResult.getCartProductQuantity())
                .stockQuantity(userCartResult.getStockQuantity())
                .productPrice(userCartResult.getProductPrice()).build()
        ).toList();

        return CartResponseDto.builder()
                .cartItems(userCartInfoList)
                .build();
    }

    public List<SizeResponseDto> getSizesByProductId(SizeRequestDto sizeRequestDto) {

        log.info("CartService_getSizesByProductId 진입");

        List<SizeStockResult> availableSizes = cartMapper.findAvailableSizesByProductId(sizeRequestDto.getProductId());

        log.info("availableSizes" + availableSizes);

        List<SizeResponseDto> sizeResponseDtoList = availableSizes.stream().map(result -> SizeResponseDto.builder().size(result.getSize()).stockQuantity(result.getStockQuantity()).build()).toList();

        return sizeResponseDtoList;
    }

    @Transactional
    public void updateCartOption(String userId, CartUpdateRequestDto dto) {

        if (dto.getPrevSize() != dto.getNewSize()) {
            UserCartDeleteQueryParam userCartDeleteQueryParam = UserCartDeleteQueryParam
                    .builder()
                    .userId(userId)
                    .productId(dto.getProductId())
                    .size(dto.getPrevSize())
                    .build();

            cartMapper.deleteCartItem(userCartDeleteQueryParam);

            UserCartItemQuantityQueryParam userCartItemQuantityQueryParam = UserCartItemQuantityQueryParam.builder()
                    .userId(userId)
                    .productId(dto.getProductId())
                    .size(dto.getNewSize())
                    .build();

            // 존재하면 cart 옵션 수량 업데이트 , 존재하지 않으면 cart 옵션 수량 insert

            Integer sizeItemQuantity = cartMapper.findCartItemBySize(userCartItemQuantityQueryParam);

            UserCartUpdateQueryParam userCartUpdateQueryParam = UserCartUpdateQueryParam
                    .builder()
                    .userId(userId)
                    .productId(dto.getProductId())
                    .size(dto.getNewSize())
                    .productQuantity(dto.getNewQuantity())
                    .build();

            if (sizeItemQuantity == null) {
                cartMapper.insertCartItem(userCartUpdateQueryParam);
            } else {
                userCartUpdateQueryParam.setQuantityToCartItem(sizeItemQuantity + dto.getNewQuantity());
                cartMapper.updateCartItemQuantity(userCartUpdateQueryParam);
            }

        } else {
            UserCartUpdateQueryParam userCartUpdateQueryParam = UserCartUpdateQueryParam
                    .builder()
                    .userId(userId)
                    .productId(dto.getProductId())
                    .size(dto.getNewSize())
                    .productQuantity(dto.getNewQuantity())
                    .build();

            cartMapper.updateCartItemQuantity(userCartUpdateQueryParam);
        }
    }

    @Transactional
    public void deleteCartItems(String userId, CartDeleteRequestDto deleteRequestDto) {
        for (CartOption item : deleteRequestDto.getItems()) {
            UserCartDeleteQueryParam param = UserCartDeleteQueryParam.builder()
                    .userId(userId)
                    .productId(item.getProductId())
                    .size(item.getSize())
                    .build();

            cartMapper.deleteCartItem(param);
        }
    }

    public List<CartItemStockInfo> findStockIssues(List<CartStockCheckRequestDto> items) {

        List<StockCheckParam> params = items.stream()
                .map(result -> StockCheckParam.builder()
                        .productId(result.getProductId())
                        .size(result.getSize())
                        .build())
                .toList();

        List<StockCheckResult> inventoryList = cartMapper.findStocksByProductOptions(params);

        Map<String, StockCheckResult> stockMap = inventoryList.stream()
                .collect(Collectors.toMap(
                        i -> i.getProductId() + "_" + i.getSize(),
                        i -> i
                ));

        List<CartItemStockInfo> result = new ArrayList<>();

        for (CartStockCheckRequestDto item : items) {
            String key = item.getProductId() + "_" + item.getSize();
            StockCheckResult stockInfo = stockMap.get(key);

            CartItemStockInfo.CartItemStockInfoBuilder builder = CartItemStockInfo.builder()
                    .productId(item.getProductId())
                    .size(item.getSize());

            if (stockInfo == null) {
                // 상품 자체를 못 찾은 경우
                builder.stock(0)
                        .productName("알 수 없는 상품")
                        .issueType(IssueType.UNKNOWN_PRODUCT);
            } else if (stockInfo.getStock() == 0) {
                // 재고가 0개인 경우
                builder.stock(0)
                        .productName(stockInfo.getProductName())
                        .issueType(IssueType.OUT_OF_STOCK);
            } else if (stockInfo.getStock() < item.getQuantity()) {
                // 수량보다 재고가 부족한 경우
                builder.stock(stockInfo.getStock())
                        .productName(stockInfo.getProductName())
                        .issueType(IssueType.NOT_ENOUGH_STOCK);
            } else {
                // 문제가 없으면 응답에 포함하지 않음
                continue;
            }
            result.add(builder.build());
        }
        return result;
    }
    public void insertCartItem(CartInsertDto dto) {
        cartMapper.insertCartItem(dto);
    }
}