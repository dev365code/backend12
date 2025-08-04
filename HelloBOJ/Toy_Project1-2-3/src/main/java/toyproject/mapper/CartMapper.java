package toyproject.mapper;

import toyproject.controller.dto.CartInsertDto;
import toyproject.mapper.queryparam.*;
import toyproject.mapper.result.SizeStockResult;
import toyproject.mapper.result.StockCheckResult;
import toyproject.mapper.result.UserCartPriceResult;
import toyproject.mapper.result.UserCartResult;

import java.util.List;

public interface CartMapper {
    List<SizeStockResult> findAvailableSizesByProductId(int productId);

    int findCartItemsCountByUserId(UserCartByIDQueryParam userCartByIDQueryParam);

    List<UserCartResult> findCartItemsByUserId(UserCartByIDQueryParam userCartByIDQueryParam);

    UserCartPriceResult findCartItemsPriceByUserId(UserCartByIDQueryParam userCartByIDQueryParam);

    Integer findCartItemBySize(UserCartItemQuantityQueryParam userCartItemQuantityQueryParam);

    void updateCartItemQuantity(UserCartUpdateQueryParam userCartUpdateQueryParam);

    void deleteCartItem(UserCartDeleteQueryParam cartDeleteQueryParam);

    void insertCartItem(UserCartUpdateQueryParam cartUpdateQueryParam);

    void insertCartItem(CartInsertDto CartInsertDto);

    List<StockCheckResult> findStocksByProductOptions(List<StockCheckParam> items);
}