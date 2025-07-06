package com.demo.controllers;

import com.demo.models.WelcomeDTO;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.util.HtmlUtils;

import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;
import java.io.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.sql.*;
import java.util.Base64;
import java.util.logging.Logger;

@RestController
public class WelcomeController {


    // XSS
    @GetMapping("/api/welcome")
    public WelcomeDTO welcome(@RequestParam(value = "name", defaultValue = "...") String name) {
        
        // 2. Escapar la entrada del usuario para neutralizar cualquier script malicioso.
        String sanitizedName = HtmlUtils.htmlEscape(name); 
        
        return new WelcomeDTO("Hola, bienvenido " + sanitizedName + ", esto es un demo");
    }

}