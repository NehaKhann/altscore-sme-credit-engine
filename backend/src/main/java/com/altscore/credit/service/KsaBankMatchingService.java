package com.altscore.credit.service;

import org.springframework.stereotype.Service;
import java.util.*;

@Service
public class KsaBankMatchingService {

    public static class BankProduct {
        private String bankName;
        private String productName;
        private String logoInitials;
        private String color;
        private int minScore;
        private int minYears;
        private double minMonthlyRevenue;
        private int minTransactions;
        private String maxLoanAmount;
        private String interestRate;
        private String processingTime;
        private String matchStatus; // QUALIFIED, ALMOST, NOT_ELIGIBLE
        private int matchPercentage;
        private List<String> gaps;
        private String highlight;

        public BankProduct(String bankName, String productName, String logoInitials,
                          String color, int minScore, int minYears,
                          double minMonthlyRevenue, int minTransactions,
                          String maxLoanAmount, String interestRate,
                          String processingTime, String highlight) {
            this.bankName = bankName;
            this.productName = productName;
            this.logoInitials = logoInitials;
            this.color = color;
            this.minScore = minScore;
            this.minYears = minYears;
            this.minMonthlyRevenue = minMonthlyRevenue;
            this.minTransactions = minTransactions;
            this.maxLoanAmount = maxLoanAmount;
            this.interestRate = interestRate;
            this.processingTime = processingTime;
            this.highlight = highlight;
            this.gaps = new ArrayList<>();
        }

        // Getters
        public String getBankName() { return bankName; }
        public String getProductName() { return productName; }
        public String getLogoInitials() { return logoInitials; }
        public String getColor() { return color; }
        public int getMinScore() { return minScore; }
        public String getMaxLoanAmount() { return maxLoanAmount; }
        public String getInterestRate() { return interestRate; }
        public String getProcessingTime() { return processingTime; }
        public String getMatchStatus() { return matchStatus; }
        public void setMatchStatus(String matchStatus) { this.matchStatus = matchStatus; }
        public int getMatchPercentage() { return matchPercentage; }
        public void setMatchPercentage(int matchPercentage) { this.matchPercentage = matchPercentage; }
        public List<String> getGaps() { return gaps; }
        public void setGaps(List<String> gaps) { this.gaps = gaps; }
        public String getHighlight() { return highlight; }
        public int getMinYears() { return minYears; }
        public double getMinMonthlyRevenue() { return minMonthlyRevenue; }
        public int getMinTransactions() { return minTransactions; }
    }

    private List<BankProduct> getKsaBankProducts() {
        return Arrays.asList(
            new BankProduct(
                "Social Development Bank",
                "Numuw SME Program",
                "SDB",
                "#16a34a",
                40, 0, 5000, 10,
                "SAR 300,000",
                "0% (Government)",
                "2-4 weeks",
                "Best for early-stage businesses"
            ),
            new BankProduct(
                "Monsha'at",
                "Kafalah Guarantee Program",
                "MN",
                "#0891b2",
                45, 1, 8000, 15,
                "SAR 500,000",
                "Subsidized Rate",
                "3-5 weeks",
                "Government-backed guarantee"
            ),
            new BankProduct(
                "Al Rajhi Bank",
                "Business Finance",
                "AR",
                "#dc2626",
                60, 1, 15000, 30,
                "SAR 500,000",
                "Starting 4.5%",
                "1-2 weeks",
                "Fastest approval in KSA"
            ),
            new BankProduct(
                "Saudi National Bank",
                "SME Business Loan",
                "SNB",
                "#1d4ed8",
                65, 2, 20000, 40,
                "SAR 1,000,000",
                "Starting 5.0%",
                "2-3 weeks",
                "Largest loan amounts"
            ),
            new BankProduct(
                "Riyad Bank",
                "Tayseer SME Finance",
                "RB",
                "#7c3aed",
                65, 2, 18000, 35,
                "SAR 750,000",
                "Starting 4.8%",
                "1-2 weeks",
                "Flexible repayment terms"
            ),
            new BankProduct(
                "Bank Albilad",
                "Albilad Business Finance",
                "AB",
                "#b45309",
                70, 2, 20000, 40,
                "SAR 600,000",
                "Starting 4.9%",
                "2-3 weeks",
                "Sharia-compliant financing"
            ),
            new BankProduct(
                "Saudi Fransi Bank",
                "Fransi Business Plus",
                "SF",
                "#0f766e",
                75, 3, 30000, 60,
                "SAR 2,000,000",
                "Starting 5.2%",
                "2-4 weeks",
                "Premium business banking"
            ),
            new BankProduct(
                "Arab National Bank",
                "ANB SME Finance",
                "ANB",
                "#9333ea",
                70, 3, 25000, 50,
                "SAR 1,500,000",
                "Starting 5.0%",
                "2-3 weeks",
                "Dedicated SME relationship manager"
            )
        );
    }

    public List<BankProduct> matchBanks(double creditScore, int yearsInOperation,
                                         double monthlyRevenue, int numTransactions) {
        List<BankProduct> products = getKsaBankProducts();

        for (BankProduct product : products) {
            List<String> gaps = new ArrayList<>();
            int metCriteria = 0;
            int totalCriteria = 4;

            // Check score
            if (creditScore >= product.getMinScore()) {
                metCriteria++;
            } else {
                gaps.add("Need " + (product.getMinScore() - (int)creditScore) + " more credit score points");
            }

            // Check years
            if (yearsInOperation >= product.getMinYears()) {
                metCriteria++;
            } else {
                int yearsNeeded = product.getMinYears() - yearsInOperation;
                gaps.add("Need " + yearsNeeded + " more year(s) of operation");
            }

            // Check revenue
            if (monthlyRevenue >= product.getMinMonthlyRevenue()) {
                metCriteria++;
            } else {
                double revenueNeeded = product.getMinMonthlyRevenue() - monthlyRevenue;
                gaps.add("Need SAR " + String.format("%.0f", revenueNeeded) + " more monthly revenue");
            }

            // Check transactions
            if (numTransactions >= product.getMinTransactions()) {
                metCriteria++;
            } else {
                int transNeeded = product.getMinTransactions() - numTransactions;
                gaps.add("Need " + transNeeded + " more monthly transactions");
            }

            // Calculate match percentage and status
            int matchPct = (metCriteria * 100) / totalCriteria;
            product.setMatchPercentage(matchPct);
            product.setGaps(gaps);

            if (matchPct == 100) {
                product.setMatchStatus("QUALIFIED");
            } else if (matchPct >= 50) {
                product.setMatchStatus("ALMOST");
            } else {
                product.setMatchStatus("NOT_ELIGIBLE");
            }
        }

        // Sort: QUALIFIED first, then ALMOST, then NOT_ELIGIBLE
        products.sort((a, b) -> {
            Map<String, Integer> order = Map.of(
                "QUALIFIED", 0, "ALMOST", 1, "NOT_ELIGIBLE", 2
            );
            int statusCompare = order.get(a.getMatchStatus())
                    .compareTo(order.get(b.getMatchStatus()));
            if (statusCompare != 0) return statusCompare;
            return b.getMatchPercentage() - a.getMatchPercentage();
        });

        return products;
    }
}