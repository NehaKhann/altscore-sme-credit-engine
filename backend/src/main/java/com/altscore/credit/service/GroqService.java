package com.altscore.credit.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;
import java.util.*;

@Service
public class GroqService {

    @Value("${groq.api.key}")
    private String apiKey;

    @Value("${groq.api.url}")
    private String apiUrl;

    @Value("${groq.api.model}")
    private String model;

    private final RestTemplate restTemplate = new RestTemplate();

    public String generateCombinedAnalysis(String businessName, String businessType,
                                            double monthlyRevenue, int yearsInOperation,
                                            int numTransactions, double creditScore,
                                            String riskLevel) {
        String prompt = String.format("""
                You are an expert credit analyst for SME businesses in Saudi Arabia.
                
                Business Profile:
                - Name: %s
                - Type: %s
                - Monthly Revenue: SAR %.0f
                - Years in Operation: %d
                - Monthly Transactions: %d
                - Credit Score: %.0f / 100
                - Risk Level: %s
                
                Respond in this EXACT format with these exact headers:
                
                EXPLANATION:
                [Write 2-3 sentences explaining why this business received this score,
                what it means for their loan eligibility in KSA banking context]
                
                RECOMMENDATIONS:
                1. [Specific actionable recommendation] | Impact: +X to +Y points | Timeline: X months
                2. [Specific actionable recommendation] | Impact: +X to +Y points | Timeline: X months
                3. [Specific actionable recommendation] | Impact: +X to +Y points | Timeline: X months
                """,
                businessName, businessType, monthlyRevenue,
                yearsInOperation, numTransactions, creditScore, riskLevel);

        String result = callGroq(prompt);

        if (result == null) {
            return generateFallbackAnalysis(businessName, businessType,
                    creditScore, riskLevel, monthlyRevenue,
                    yearsInOperation, numTransactions);
        }
        return result;
    }

    private String callGroq(String prompt) {
        try {
            System.out.println("=== GROQ API CALL ===");
            System.out.println("Model: " + model);
            System.out.println("Key starts with: " + apiKey.substring(0, 10));

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.set("Authorization", "Bearer " + apiKey);

            Map<String, Object> message = new HashMap<>();
            message.put("role", "user");
            message.put("content", prompt);

            Map<String, Object> body = new HashMap<>();
            body.put("model", model);
            body.put("messages", List.of(message));
            body.put("max_tokens", 500);
            body.put("temperature", 0.7);

            HttpEntity<Map<String, Object>> request = new HttpEntity<>(body, headers);

            Map response = restTemplate.postForObject(apiUrl, request, Map.class);
            System.out.println("=== GROQ RESPONSE RECEIVED ===");

            List choices = (List) response.get("choices");
            Map choice = (Map) choices.get(0);
            Map messageMap = (Map) choice.get("message");
            String result = messageMap.get("content").toString();

            System.out.println("=== AI TEXT LENGTH: " + result.length() + " chars ===");
            return result;

        } catch (Exception e) {
            System.out.println("=== GROQ ERROR: " + e.getMessage() + " ===");
            System.out.println("=== USING SMART FALLBACK ===");
            return null;
        }
    }

    private String generateFallbackAnalysis(String businessName, String businessType,
                                             double creditScore, String riskLevel,
                                             double monthlyRevenue, int yearsInOperation,
                                             int numTransactions) {
        String explanation;
        String recommendations;

        if (creditScore >= 80) {
            explanation = businessName + " demonstrates excellent creditworthiness with strong performance across all key metrics. " +
                    "The high transaction volume of " + numTransactions + " monthly transactions combined with SAR " +
                    String.format("%.0f", monthlyRevenue) + " monthly revenue shows a financially healthy " +
                    businessType.toLowerCase() + " business. This business is highly eligible for SME financing " +
                    "and should qualify for competitive loan rates from most KSA banks.";
            recommendations =
                    "1. Apply for a business expansion loan up to SAR 500,000 at favorable rates | Impact: Business growth | Timeline: 1-2 months\n" +
                    "2. Register with SAMA open banking to strengthen your credit profile further | Impact: +3 to +5 points | Timeline: 2-4 weeks\n" +
                    "3. Diversify revenue streams to maintain excellent score long-term | Impact: +2 to +4 points | Timeline: 3-6 months";

        } else if (creditScore >= 60) {
            explanation = businessName + " shows a solid credit profile with good fundamentals in the " +
                    businessType.toLowerCase() + " sector. With " + yearsInOperation + " year(s) of operation " +
                    "and SAR " + String.format("%.0f", monthlyRevenue) + " monthly revenue, the business has " +
                    "demonstrated stability. This business qualifies for SME loans with standard conditions.";
            recommendations =
                    "1. Increase monthly transactions from " + numTransactions + " to above 100 by accepting STC Pay and Mada | Impact: +8 to +12 points | Timeline: 2-3 months\n" +
                    "2. Maintain consistent revenue above SAR " + String.format("%.0f", monthlyRevenue * 1.2) + " for 3 consecutive months | Impact: +5 to +8 points | Timeline: 3 months\n" +
                    "3. Register with Monsha'at SME portal for additional credibility signals | Impact: +4 to +6 points | Timeline: 2-4 weeks";

        } else if (creditScore >= 40) {
            explanation = businessName + " has a developing credit profile with " + yearsInOperation +
                    " year(s) of operation in the " + businessType.toLowerCase() + " sector. " +
                    "Current monthly revenue of SAR " + String.format("%.0f", monthlyRevenue) +
                    " and " + numTransactions + " transactions show early-stage business activity. " +
                    "Focused improvements over 3-6 months can significantly boost loan eligibility.";
            recommendations =
                    "1. Increase monthly revenue to above SAR 20,000 through expanded sales channels | Impact: +10 to +15 points | Timeline: 3-6 months\n" +
                    "2. Boost transaction frequency by enabling all digital payment methods | Impact: +8 to +12 points | Timeline: 1-2 months\n" +
                    "3. Open a dedicated business bank account and route all revenue through it | Impact: +7 to +10 points | Timeline: 1 month";

        } else {
            explanation = businessName + " is in the early stages of building a credit profile. " +
                    "The current metrics reflect limited financial history which is common for newer " +
                    businessType.toLowerCase() + " businesses. " +
                    "Consider microfinance options through Social Development Bank (SDB) as a starting point.";
            recommendations =
                    "1. Register business officially with Ministry of Commerce (CR number) | Impact: +15 points | Timeline: 2-4 weeks\n" +
                    "2. Process all sales digitally for 3 months to build transaction history | Impact: +12 to +15 points | Timeline: 3 months\n" +
                    "3. Apply for Monsha'at startup support program for SME seed financing | Impact: Qualifies for SAR 50,000-200,000 | Timeline: 4-6 weeks";
        }

        return "EXPLANATION:\n" + explanation + "\n\nRECOMMENDATIONS:\n" + recommendations;
    }
}