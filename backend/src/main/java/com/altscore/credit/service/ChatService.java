package com.altscore.credit.service;

import com.altscore.credit.dto.ChatMessageDto;
import com.altscore.credit.dto.ChatRequest;
import com.altscore.credit.dto.ChatResponse;
import com.altscore.credit.entity.Business;
import com.altscore.credit.repository.BusinessRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import java.util.*;

@Service
public class ChatService {

    @Value("${groq.api.key}")
    private String apiKey;

    @Value("${groq.api.url}")
    private String apiUrl;

    @Value("${groq.api.model}")
    private String model;

    private final BusinessRepository businessRepository;
    private final KsaBankMatchingService bankMatchingService;
    private final RestTemplate restTemplate = new RestTemplate();

    public ChatService(BusinessRepository businessRepository,
                      KsaBankMatchingService bankMatchingService) {
        this.businessRepository = businessRepository;
        this.bankMatchingService = bankMatchingService;
    }

    public ChatResponse chat(ChatRequest request) {
        try {
            // 1. Load business data from DB
            Business business = businessRepository.findById(request.getBusinessId())
                .orElseThrow(() -> new RuntimeException("Business not found"));

            // 2. Get loan matches for this business
            List<KsaBankMatchingService.BankProduct> matches = bankMatchingService.matchBanks(
                business.getCreditScore().doubleValue(),
                business.getYearsInOperation(),
                business.getMonthlyRevenue().doubleValue(),
                business.getNumTransactions()
            );

            // 3. Build qualified and almost lists
            StringBuilder qualifiedBanks = new StringBuilder();
            StringBuilder almostBanks = new StringBuilder();

            for (KsaBankMatchingService.BankProduct bank : matches) {
                if ("QUALIFIED".equals(bank.getMatchStatus())) {
                    qualifiedBanks.append("- ").append(bank.getBankName())
                        .append(": up to ").append(bank.getMaxLoanAmount())
                        .append(" at ").append(bank.getInterestRate())
                        .append("\n");
                } else if ("ALMOST".equals(bank.getMatchStatus())) {
                    almostBanks.append("- ").append(bank.getBankName())
                        .append(": needs ")
                        .append(String.join(", ", bank.getGaps()))
                        .append("\n");
                }
            }

            // 4. Build system context with real business data
            String systemContext = String.format("""
                You are AltScore AI Assistant, a specialized credit advisor for SME businesses in Saudi Arabia.
                You have access to the following REAL business data for this conversation:
                
                === BUSINESS PROFILE ===
                Business Name: %s
                Owner: %s
                Business Type: %s
                Monthly Revenue: SAR %.0f
                Years in Operation: %d
                Monthly Transactions: %d
                Credit Score: %.0f / 100
                Risk Level: %s
                
                === LOAN ELIGIBILITY ===
                QUALIFIED Banks (can apply TODAY):
                %s
                
                ALMOST Qualifying Banks (close to eligibility):
                %s
                
                === YOUR ROLE ===
                - Answer questions using ONLY this real business data
                - Be specific with numbers (use actual SAR amounts, scores, etc.)
                - Be encouraging but honest
                - Keep answers concise (2-4 sentences max unless asked for detail)
                - Focus on KSA banking context (mention SAMA, STC Pay, Mada when relevant)
                - If asked about improvement, reference their actual weak points
                - Always suggest actionable next steps
                - Do NOT make up information not in the profile above
                """,
                business.getBusinessName(),
                business.getOwnerName(),
                business.getBusinessType(),
                business.getMonthlyRevenue().doubleValue(),
                business.getYearsInOperation(),
                business.getNumTransactions(),
                business.getCreditScore().doubleValue(),
                business.getRiskLevel(),
                qualifiedBanks.length() > 0 ? qualifiedBanks.toString() : "None currently",
                almostBanks.length() > 0 ? almostBanks.toString() : "None"
            );

            // 5. Build messages array with history
            List<Map<String, String>> messages = new ArrayList<>();

            // System message
            Map<String, String> systemMsg = new HashMap<>();
            systemMsg.put("role", "system");
            systemMsg.put("content", systemContext);
            messages.add(systemMsg);

            // Add conversation history
            if (request.getHistory() != null) {
                for (ChatMessageDto historyMsg : request.getHistory()) {
                    Map<String, String> msg = new HashMap<>();
                    msg.put("role", historyMsg.getRole());
                    msg.put("content", historyMsg.getContent());
                    messages.add(msg);
                }
            }

            // Add current user message
            Map<String, String> userMsg = new HashMap<>();
            userMsg.put("role", "user");
            userMsg.put("content", request.getMessage());
            messages.add(userMsg);

            // 6. Call Groq API
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.set("Authorization", "Bearer " + apiKey);

            Map<String, Object> body = new HashMap<>();
            body.put("model", model);
            body.put("messages", messages);
            body.put("max_tokens", 400);
            body.put("temperature", 0.7);

            HttpEntity<Map<String, Object>> httpRequest = new HttpEntity<>(body, headers);
            Map response = restTemplate.postForObject(apiUrl, httpRequest, Map.class);

            List choices = (List) response.get("choices");
            Map choice = (Map) choices.get(0);
            Map messageMap = (Map) choice.get("message");
            String aiResponse = messageMap.get("content").toString();

            return new ChatResponse(aiResponse, true);

        } catch (Exception e) {
            System.out.println("Chat error: " + e.getMessage());
            return new ChatResponse(generateFallbackResponse(request.getMessage()), true);
        }
    }

    private String generateFallbackResponse(String userMessage) {
        String msg = userMessage.toLowerCase();
        if (msg.contains("bank") || msg.contains("loan") || msg.contains("qualify")) {
            return "Based on your credit profile, you qualify for several KSA bank programs. Check the Loan Matches tab above for detailed eligibility and amounts for each bank.";
        } else if (msg.contains("score") || msg.contains("improve") || msg.contains("increase")) {
            return "To improve your credit score, focus on increasing your monthly transaction volume and maintaining consistent revenue. Check the Recommendations tab for specific actions tailored to your business.";
        } else if (msg.contains("revenue") || msg.contains("money") || msg.contains("sar")) {
            return "Your monthly revenue is a key factor in your credit score. Maintaining consistent revenue above SAR 30,000 would significantly improve your risk classification.";
        } else {
            return "I'm your AltScore AI advisor with access to your real business data. Ask me about your loan options, how to improve your score, or what specific banks require for approval.";
        }
    }
}