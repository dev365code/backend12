package toyproject.config;

import org.apache.ibatis.session.SqlSessionFactory;
import org.mybatis.spring.SqlSessionFactoryBean;
import org.mybatis.spring.annotation.MapperScan;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import javax.sql.DataSource;

@Configuration
@MapperScan(basePackages = "toyproject.mapper")
public class MyBatisConfig {

    @Bean
    public SqlSessionFactory sqlSessionFactory(DataSource dataSource) throws Exception {
        SqlSessionFactoryBean factory = new SqlSessionFactoryBean();
        factory.setDataSource(dataSource);
        factory.setTypeAliasesPackage("toyproject.mapper, toyproject.controller.dto");

        org.apache.ibatis.session.Configuration config = new org.apache.ibatis.session.Configuration();
        config.setMapUnderscoreToCamelCase(true);
        config.setCacheEnabled(true);
        config.setLazyLoadingEnabled(true);
        config.setMultipleResultSetsEnabled(true);
        config.setCallSettersOnNulls(true);
        config.setLogImpl(org.apache.ibatis.logging.slf4j.Slf4jImpl.class); // log4jdbc 대응용 logImpl
        factory.setConfiguration(config);
        factory.setMapperLocations(
                new PathMatchingResourcePatternResolver()
                        .getResources("classpath:/mapper/**/*.xml")
        );

        return factory.getObject();
    }
}