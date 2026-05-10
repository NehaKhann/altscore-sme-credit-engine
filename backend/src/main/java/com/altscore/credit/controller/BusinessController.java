package com.altscore.credit.controller;

import com.altscore.credit.dto.BusinessRequest;
import com.altscore.credit.dto.BusinessResponse;
import com.altscore.credit.service.BusinessService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/v1/businesses")
@CrossOrigin(origins = "*")
public class BusinessController {

    private final BusinessService service;

    public BusinessController(BusinessService service) {
        this.service = service;
    }

    @PostMapping
    public ResponseEntity<BusinessResponse> createBusiness(@RequestBody BusinessRequest request) {
        return ResponseEntity.ok(service.createBusiness(request));
    }

    @GetMapping
    public ResponseEntity<List<BusinessResponse>> getAllBusinesses() {
        return ResponseEntity.ok(service.getAllBusinesses());
    }

    @GetMapping("/{id}")
    public ResponseEntity<BusinessResponse> getBusinessById(@PathVariable Long id) {
        return ResponseEntity.ok(service.getBusinessById(id));
    }
}
