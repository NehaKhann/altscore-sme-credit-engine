package com.altscore.credit.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "businesses")
public class Business {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "business_name", nullable = false)
    private String businessName;

    @Column(name = "owner_name", nullable = false)
    private String ownerName;

    @Column(name = "business_type", nullable = false)
    private String businessType;

    @Column(name = "monthly_revenue", nullable = false)
    private BigDecimal monthlyRevenue;

    @Column(name = "years_in_operation", nullable = false)
    private Integer yearsInOperation;

    @Column(name = "num_transactions", nullable = false)
    private Integer numTransactions;

    @Column(name = "credit_score")
    private BigDecimal creditScore;

    @Column(name = "risk_level")
    private String riskLevel;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

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
    public LocalDateTime getUpdatedAt() { return updatedAt; }
}
