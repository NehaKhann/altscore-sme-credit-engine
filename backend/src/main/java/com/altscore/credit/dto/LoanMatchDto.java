package com.altscore.credit.dto;

import java.util.List;

public class LoanMatchDto {
    private String bankName;
    private String productName;
    private String logoInitials;
    private String color;
    private String maxLoanAmount;
    private String interestRate;
    private String processingTime;
    private String matchStatus;
    private int matchPercentage;
    private List<String> gaps;
    private String highlight;
    private int minScore;

    public LoanMatchDto() {}

    public String getBankName() { return bankName; }
    public void setBankName(String bankName) { this.bankName = bankName; }
    public String getProductName() { return productName; }
    public void setProductName(String productName) { this.productName = productName; }
    public String getLogoInitials() { return logoInitials; }
    public void setLogoInitials(String logoInitials) { this.logoInitials = logoInitials; }
    public String getColor() { return color; }
    public void setColor(String color) { this.color = color; }
    public String getMaxLoanAmount() { return maxLoanAmount; }
    public void setMaxLoanAmount(String maxLoanAmount) { this.maxLoanAmount = maxLoanAmount; }
    public String getInterestRate() { return interestRate; }
    public void setInterestRate(String interestRate) { this.interestRate = interestRate; }
    public String getProcessingTime() { return processingTime; }
    public void setProcessingTime(String processingTime) { this.processingTime = processingTime; }
    public String getMatchStatus() { return matchStatus; }
    public void setMatchStatus(String matchStatus) { this.matchStatus = matchStatus; }
    public int getMatchPercentage() { return matchPercentage; }
    public void setMatchPercentage(int matchPercentage) { this.matchPercentage = matchPercentage; }
    public List<String> getGaps() { return gaps; }
    public void setGaps(List<String> gaps) { this.gaps = gaps; }
    public String getHighlight() { return highlight; }
    public void setHighlight(String highlight) { this.highlight = highlight; }
    public int getMinScore() { return minScore; }
    public void setMinScore(int minScore) { this.minScore = minScore; }
}