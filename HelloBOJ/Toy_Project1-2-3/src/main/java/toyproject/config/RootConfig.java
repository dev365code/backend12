package toyproject.config;

import org.springframework.context.annotation.*;
import org.springframework.context.support.PropertySourcesPlaceholderConfigurer;

@Configuration
@PropertySource("classpath:application.properties")
@ComponentScan(basePackages = {"toyproject.config","toyproject.service","toyproject.mapper"})
@Import({
    DataSourceConfig.class,  // DB 커넥션 관련
    TxConfig.class,          // 트랜잭션 설정
    WebConfig.class,         // 정적 리소스, 뷰 설정
})
public class RootConfig {

    @Bean
    public static PropertySourcesPlaceholderConfigurer propertyConfigInDev() {
        return new PropertySourcesPlaceholderConfigurer();
    }
}