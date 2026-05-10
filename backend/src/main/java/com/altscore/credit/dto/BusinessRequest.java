package com.altscore.credit.dto;

import java.math.BigDecimal;

public class BusinessRequest {
    private String businessName;
    private String ownerName;
    private String businessType;
    private BigDecimal monthlyRevenue;
    private Integer yearsInOperation;
    private Integer numTransactions;

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
}


// Two DTOs:
// BusinessRequest  → data coming IN  (from frontend form)
// BusinessResponse → data going OUT  (to frontend display)
// Why not just use the Entity directly?
// Entity has ALL database fields including internal ones
// DTO has ONLY what you want to send/receive

// Example:
// Entity has: id, createdAt, updatedAt, internalFlags...
// Request DTO has: only businessName, revenue, etc. (what user fills)
// Response DTO has: only what frontend needs to display