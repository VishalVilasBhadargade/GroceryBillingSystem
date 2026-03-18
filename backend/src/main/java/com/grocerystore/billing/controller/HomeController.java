package com.grocerystore.billing.controller;

@org.springframework.web.bind.annotation.RestController
public class HomeController {

    @org.springframework.web.bind.annotation.GetMapping("/")
    public String home() {
        return "App Running Successfully";
    }
}
