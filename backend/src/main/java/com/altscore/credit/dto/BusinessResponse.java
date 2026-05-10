package com.altscore.credit.dto;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public class BusinessResponse {
    private Long id;
    private String businessName;
    private String ownerName;
    private String businessType;
    private BigDecimal monthlyRevenue;
    private Integer yearsInOperation;
    private Integer numTransactions;
    private BigDecimal creditScore;
    private String riskLevel;
    private LocalDateTime createdAt;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getBusinessName() { return businessName; }
    public void setBusinessName(String businessName) { this.businessName = businessName; }
    public String getOwnerName() { return ownerName; }
    public void setOwnerName(String ownerName) { this.ownerName = ownerName; }
    public String getBusinessType() { return businessType; }
    public void setBusinessType(String businessType) { this.businessType = businessType; }
    public BigDecimal getMonthlyRevenue() { return monthlyRevenue; }
    public void setMonthlyRevenue(BigDecimal monthlyRevenue) { this.monthlyRevenue = monthlyRevenue; }
    public Integer getYearsInOperation() { return yearsInOperation; }
    public void setYearsInOperation(Integer yearsInOperation) { this.yearsInOperation = yearsInOperation; }
    public Integer getNumTransactions() { return numTransactions; }
    public void setNumTransactions(Integer numTransactions) { this.numTransactions = numTransactions; }
    public BigDecimal getCreditScore() { return creditScore; }
    public void setCreditScore(BigDecimal creditScore) { this.creditScore = creditScore; }
    public String getRiskLevel() { return riskLevel; }
    public void setRiskLevel(String riskLevel) { this.riskLevel = riskLevel; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
