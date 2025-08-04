package toyproject.config;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.EnableWebMvc;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import org.springframework.web.servlet.view.InternalResourceViewResolver;
import toyproject.interceptor.LoginCheckInterceptor;

@Configuration
@EnableWebMvc
@ComponentScan(basePackages = "toyproject")
@MapperScan("toyproject.mapper")
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        // 정적 리소스(css, js 등) 경로 매핑
        registry.addResourceHandler("/publish/**")
                .addResourceLocations("/publish/");

        // 이미지 경로 추가
        registry.addResourceHandler("/image/**")
                .addResourceLocations("/image/");

    }
    @Bean
    public InternalResourceViewResolver viewResolver() {
        InternalResourceViewResolver resolver = new InternalResourceViewResolver();
        resolver.setPrefix("/WEB-INF/views/");
        resolver.setSuffix(".jsp");
        resolver.setCache(false); // 인코딩 문제 해결을 위한 설정 추가(by 홍성훈)
        return resolver;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new LoginCheckInterceptor())
                .order(1)
                .addPathPatterns("/cart/**",  "/board/inquiry/**") // 로그인 필요한 경로
                .excludePathPatterns("/", "/login", "/css/**", "/js/**", "/images/**"); // 예외
    }
}