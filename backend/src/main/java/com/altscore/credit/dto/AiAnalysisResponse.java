package com.altscore.credit.dto;

public class AiAnalysisResponse {
    private String explanation;
    private String recommendations;
    private double creditScore;
    private String riskLevel;
    private String businessName;

    public AiAnalysisResponse() {}

    public AiAnalysisResponse(String explanation, String recommendations,
                               double creditScore, String riskLevel, String businessName) {
        this.explanation = explanation;
        this.recommendations = recommendations;
        this.creditScore = creditScore;
        this.riskLevel = riskLevel;
        this.businessName = businessName;
    }

    public String getExplanation() { return explanation; }
    public void setExplanation(String explanation) { this.explanation = explanation; }
    public String getRecommendations() { return recommendations; }
    public void setRecommendations(String recommendations) { this.recommendations = recommendations; }
    public double getCreditScore() { return creditScore; }
    public void setCreditScore(double creditScore) { this.creditScore = creditScore; }
    public String getRiskLevel() { return riskLevel; }
    public void setRiskLevel(String riskLevel) { this.riskLevel = riskLevel; }
    public String getBusinessName() { return businessName; }
    public void setBusinessName(String businessName) { this.businessName = businessName; }
}