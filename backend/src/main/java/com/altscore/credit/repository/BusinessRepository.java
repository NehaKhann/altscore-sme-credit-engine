package com.altscore.credit.repository;

import com.altscore.credit.entity.Business;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface BusinessRepository extends JpaRepository<Business, Long> {
}


// This gives you database operations for FREE:
// repository.save(business)        → INSERT into DB
// repository.findAll()             → SELECT * FROM businesses
// repository.findById(1L)          → SELECT * WHERE id = 1
// repository.delete(business)      → DELETE FROM businesses
// No SQL needed — Spring writes it automatically!