package com.demo.controllers;

import com.demo.models.WelcomeDTO;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class WelcomeController {
    @GetMapping("/api/welcome")
    public WelcomeDTO welcome(@RequestParam(value = "name", defaultValue = "...") String name) {
        return new WelcomeDTO("Holasssss, bienvenido " + name + ", esto es un demonio");
    }
}
