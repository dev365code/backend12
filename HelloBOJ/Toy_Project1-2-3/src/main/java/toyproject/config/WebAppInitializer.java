package toyproject.config;

import org.springframework.web.WebApplicationInitializer;
import org.springframework.web.context.ContextLoaderListener;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;
import org.springframework.web.filter.CharacterEncodingFilter;
import org.springframework.web.servlet.DispatcherServlet;

import javax.servlet.FilterRegistration;
import javax.servlet.ServletContext;
import javax.servlet.ServletException;
import javax.servlet.ServletRegistration;

public class WebAppInitializer implements WebApplicationInitializer {

    @Override
    public void onStartup(ServletContext servletContext) throws ServletException {
        // 루트 설정
        AnnotationConfigWebApplicationContext rootContext = new AnnotationConfigWebApplicationContext();
            rootContext.register(
        toyproject.config.DataSourceConfig.class,
        toyproject.config.MyBatisConfig.class,
        toyproject.config.TxConfig.class,
        toyproject.config.CacheConfig.class
    );
        servletContext.addListener(new ContextLoaderListener(rootContext));

        // 서블릿 설정
        AnnotationConfigWebApplicationContext servletContextConfig = new AnnotationConfigWebApplicationContext();
        servletContextConfig.register(WebConfig.class);

        ServletRegistration.Dynamic dispatcher =
            servletContext.addServlet("dispatcher", new DispatcherServlet(servletContextConfig));
        dispatcher.setLoadOnStartup(1);
        dispatcher.addMapping("/");

        // 인코딩 문제 해결을 위한 설정 추가(by 홍성훈)
        CharacterEncodingFilter encodingFilter = new CharacterEncodingFilter();
        encodingFilter.setEncoding("UTF-8");
        encodingFilter.setForceEncoding(true);

        FilterRegistration.Dynamic encoding = servletContext.addFilter("encodingFilter", encodingFilter);
        encoding.addMappingForUrlPatterns(null, false, "/*");
    }
}