package com.demo.controllers;

import com.demo.models.WelcomeDTO;
import org.springframework.web.bind.annotation.*;

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

    // ⚠ Logger mal usado con datos sensibles
    private static final Logger logger = Logger.getLogger(WelcomeController.class.getName());

    // ⚠ Hardcoded secret (clave embebida)
    private static final String DB_PASSWORD = "SuperSecreta123!";
    private static final String API_KEY = "ABC123-TOKEN-INSEGURO";

    // XSS
    @GetMapping("/api/welcome")
    public WelcomeDTO welcome(@RequestParam(value = "name", defaultValue = "...") String name) {
        return new WelcomeDTO("Hola, bienvenido " + name + ", esto es un demo");
    }

    // Stacktrace expuesto
    @GetMapping("/api/error")
    public String error() {
        try {
            int a = 1 / 0;
            return "OK";
        } catch (Exception e) {
            return e.toString(); // ⚠ Devuelve detalles internos
        }
    }
}