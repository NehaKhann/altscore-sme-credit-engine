// Step 1: Receive business data from controller
// Step 2: Call ML Service → get credit score
// Step 3: Save business + score to database
// Step 4: Return response to frontend
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

    public BusinessService(BusinessRepository repository, MlServiceClient mlServiceClient) {
        this.repository = repository;
        this.mlServiceClient = mlServiceClient;
    }

    public BusinessResponse createBusiness(BusinessRequest request) {
        // 1. Call ML Service for credit score
        Map<String, Object> mlResult = mlServiceClient.getCreditScore(
            request.getMonthlyRevenue(),
            request.getYearsInOperation(),
            request.getNumTransactions()
        );

        // 2. Save to DB
        Business business = new Business();
        business.setBusinessName(request.getBusinessName());
        business.setOwnerName(request.getOwnerName());
        business.setBusinessType(request.getBusinessType());
        business.setMonthlyRevenue(request.getMonthlyRevenue());
        business.setYearsInOperation(request.getYearsInOperation());
        business.setNumTransactions(request.getNumTransactions());
        business.setCreditScore(new BigDecimal(mlResult.get("credit_score").toString()));
        business.setRiskLevel(mlResult.get("risk_level").toString());

        Business saved = repository.save(business);
        return toResponse(saved);
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
