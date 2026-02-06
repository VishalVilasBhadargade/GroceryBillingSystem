package com.grocerystore.billing.repository;

import com.grocerystore.billing.entity.Category;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Category Repository
 * Data access layer for Category entity
 */
@Repository
public interface CategoryRepository extends JpaRepository<Category, Integer> {

    boolean existsByName(String name);

    List<Category> findByIsActiveTrueOrderByName();

    Page<Category> findByIsActiveTrue(Pageable pageable);

    @Query("SELECT c FROM Category c WHERE c.parentCategory.categoryId = :parentId")
    List<Category> findByParentCategoryId(Integer parentId);

    @Query("SELECT c FROM Category c WHERE c.parentCategory IS NULL AND c.isActive = true")
    List<Category> findRootCategories();

    long countByIsActiveTrue();
}
