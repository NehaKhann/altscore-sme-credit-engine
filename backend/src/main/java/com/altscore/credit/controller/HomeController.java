package com.altscore.credit.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HomeController {

    @GetMapping("/")
    public String home() {
        return """
                <h1>✅ Altscore Backend is Running Successfully!</h1>
                <h3>Available Endpoints:</h3>
                <ul>
                    <li><a href="/api/v1/businesses">GET /api/v1/businesses</a> - List all businesses</li>
                    <li><a href="/health">GET /health</a> - Health Check</li>
                </ul>
                """;
    }

    @GetMapping("/health")
    public String health() {
        return "OK - " + java.time.LocalDateTime.now();
    }
}