package com.altscore.credit.service;

import com.altscore.credit.dto.BusinessRequest;
import com.altscore.credit.dto.BusinessResponse;
import com.altscore.credit.entity.Business;
import com.altscore.credit.repository.BusinessRepository;
import org.springframework.stereotype.Service;
import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class BusinessService {

    private final BusinessRepository repository;
    private final MlServiceClient mlServiceClient;
    private final GroqService groqService;

    public BusinessService(BusinessRepository repository,
                           MlServiceClient mlServiceClient,
                           GroqService groqService) {
        this.repository = repository;
        this.mlServiceClient = mlServiceClient;
        this.groqService = groqService;
    }

    public BusinessResponse createBusiness(BusinessRequest request) {

        // 1. Call ML Service for credit score
        Map<String, Object> mlResult = mlServiceClient.getCreditScore(
            request.getMonthlyRevenue(),
            request.getYearsInOperation(),
            request.getNumTransactions()
        );

        double creditScore = Double.parseDouble(mlResult.get("credit_score").toString());
        String riskLevel = mlResult.get("risk_level").toString();

        // 2. Call Groq AI for combined analysis
        String combined = groqService.generateCombinedAnalysis(
            request.getBusinessName(),
            request.getBusinessType(),
            request.getMonthlyRevenue().doubleValue(),
            request.getYearsInOperation(),
            request.getNumTransactions(),
            creditScore,
            riskLevel
        );

        // 3. Split AI response
        String explanation = "";
        String recommendations = "";

        if (combined.contains("EXPLANATION:") && combined.contains("RECOMMENDATIONS:")) {
            explanation = combined.substring(
                combined.indexOf("EXPLANATION:") + 12,
                combined.indexOf("RECOMMENDATIONS:")
            ).trim();
            recommendations = combined.substring(
                combined.indexOf("RECOMMENDATIONS:") + 16
            ).trim();
        } else {
            explanation = combined;
            recommendations = "Please resubmit to generate recommendations.";
        }

        // 4. Save to DB
        Business business = new Business();
        business.setBusinessName(request.getBusinessName());
        business.setOwnerName(request.getOwnerName());
        business.setBusinessType(request.getBusinessType());
        business.setMonthlyRevenue(request.getMonthlyRevenue());
        business.setYearsInOperation(request.getYearsInOperation());
        business.setNumTransactions(request.getNumTransactions());
        business.setCreditScore(new BigDecimal(creditScore));
        business.setRiskLevel(riskLevel);

        Business saved = repository.save(business);

        // 5. Return response with AI content
        BusinessResponse response = toResponse(saved);
        response.setAiExplanation(explanation);
        response.setAiRecommendations(recommendations);
        return response;
    }

    public List<BusinessResponse> getAllBusinesses() {
        return repository.findAll()
            .stream()
            .map(this::toResponse)
            .collect(Collectors.toList());
    }

    public BusinessResponse getBusinessById(Long id) {
        Business business = repository.findById(id)
            .orElseThrow(() -> new RuntimeException("Business not found"));
        return toResponse(business);
    }

    private BusinessResponse toResponse(Business b) {
        BusinessResponse res = new BusinessResponse();
        res.setId(b.getId());
        res.setBusinessName(b.getBusinessName());
        res.setOwnerName(b.getOwnerName());
        res.setBusinessType(b.getBusinessType());
        res.setMonthlyRevenue(b.getMonthlyRevenue());
        res.setYearsInOperation(b.getYearsInOperation());
        res.setNumTransactions(b.getNumTransactions());
        res.setCreditScore(b.getCreditScore());
        res.setRiskLevel(b.getRiskLevel());
        res.setCreatedAt(b.getCreatedAt());
        return res;
    }
}