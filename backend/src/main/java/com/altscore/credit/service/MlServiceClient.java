package com.altscore.credit.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;

@Service
public class MlServiceClient {

    @Value("${ml.service.url}")
    private String mlServiceUrl;

    private final RestTemplate restTemplate = new RestTemplate();

    public Map<String, Object> getCreditScore(BigDecimal monthlyRevenue,
                                               Integer yearsInOperation,
                                               Integer numTransactions) {
        try {
            Map<String, Object> request = new HashMap<>();
            request.put("monthly_revenue", monthlyRevenue);
            request.put("years_in_operation", yearsInOperation);
            request.put("num_transactions", numTransactions);

            Map response = restTemplate.postForObject(
                mlServiceUrl + "/api/v1/predict", // call ML service URL
                request,  // send this data
                Map.class  // expect this back
            );
            return response;
        } catch (Exception e) {
            // Fallback if ML service unavailable
            Map<String, Object> fallback = new HashMap<>();
            fallback.put("credit_score", 65.0);
            fallback.put("risk_level", "MEDIUM");
            return fallback;
        }
    }
}
