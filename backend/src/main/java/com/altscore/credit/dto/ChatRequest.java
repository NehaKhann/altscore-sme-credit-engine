package com.altscore.credit.dto;

import java.util.List;

public class ChatRequest {
    private Long businessId;
    private String message;
    private List<ChatMessageDto> history;

    public Long getBusinessId() { return businessId; }
    public void setBusinessId(Long businessId) { this.businessId = businessId; }
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
    public List<ChatMessageDto> getHistory() { return history; }
    public void setHistory(List<ChatMessageDto> history) { this.history = history; }
}